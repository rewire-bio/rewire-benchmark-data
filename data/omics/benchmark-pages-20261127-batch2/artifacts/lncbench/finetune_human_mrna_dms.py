from __future__ import annotations
from lncbench_data import load_task_records
import argparse
import json
import math
import os
from typing import Dict, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from finetune_schemes.runtime import add_finetune_scheme_args, build_token_scheme_encoder, count_initialized_parameters
from human_mrna_task_common import build_encoder, build_tokenizer, encode_sequence, move_batch_to_device, pearson_corr, sanitize_sequence, set_seed, split_sequence_into_windows
from LncDowntask.data_paths import checkpoint_path, data_path
DEFAULT_LNCRFM_MOTIF_CKPT = os.environ.get('LNCRFM_MOTIF_DEFAULT_CKPT', checkpoint_path())

class HumanMRNADMSDataset(Dataset):

    def __init__(self, records: List[Dict], tokenizer, max_length: int, model_backend: str, long_seq_strategy: str, window_overlap: int) -> None:
        self.records = records
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.model_backend = model_backend
        self.nt_max_length = max_length - 2
        self.long_seq_strategy = long_seq_strategy
        self.window_overlap = window_overlap

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Dict:
        record = self.records[idx]
        full_sequence = sanitize_sequence(record['sequence'])
        full_values = list(record['dms'][:len(full_sequence)])
        if self.long_seq_strategy == 'sliding_window':
            windows = split_sequence_into_windows(full_sequence, self.nt_max_length, self.window_overlap)
            spans = []
            start = 0
            stride = max(1, self.nt_max_length - max(0, min(self.window_overlap, self.nt_max_length - 1)))
            for window in windows:
                end = start + len(window)
                spans.append((start, end))
                if end >= len(full_sequence):
                    break
                start += stride
            encoded_windows = [encode_sequence(window, self.tokenizer, self.max_length, self.model_backend) for window in windows]
            return {'sequence': full_sequence, 'input_ids': [item['input_ids'] for item in encoded_windows], 'attention_mask': [item['attention_mask'] for item in encoded_windows], 'dms': [full_values[start:end] for start, end in spans], 'window_starts': [start for start, _ in spans], 'sample_id': record['sample_id']}
        sequence = full_sequence[:self.nt_max_length]
        values = list(full_values[:len(sequence)])
        encoded = encode_sequence(sequence, self.tokenizer, self.max_length, self.model_backend)
        return {'sequence': sequence, 'input_ids': encoded['input_ids'], 'attention_mask': encoded['attention_mask'], 'dms': values, 'sample_id': record['sample_id']}

class DMSCollator:

    def __init__(self, tokenizer) -> None:
        self.tokenizer = tokenizer

    def __call__(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        first_input_ids = batch[0]['input_ids']
        if isinstance(first_input_ids, list) and first_input_ids and isinstance(first_input_ids[0], list):
            return self._collate_windowed(batch)
        features = [{'input_ids': item['input_ids'], 'attention_mask': item['attention_mask']} for item in batch]
        padded = self.tokenizer.pad(features, return_tensors='pt')
        batch_size, padded_len = padded['input_ids'].shape
        labels = torch.zeros(batch_size, padded_len, dtype=torch.float32)
        label_mask = torch.zeros(batch_size, padded_len, dtype=torch.bool)
        nt_lens = torch.zeros(batch_size, dtype=torch.long)
        for index, item in enumerate(batch):
            nt_len = len(item['sequence'])
            nt_lens[index] = nt_len
            for pos, value in enumerate(item['dms']):
                token_pos = pos + 1
                if token_pos >= padded_len or value <= -999:
                    continue
                labels[index, token_pos] = float(value)
                label_mask[index, token_pos] = True
        padded['labels'] = labels
        padded['label_mask'] = label_mask
        padded['nt_lens'] = nt_lens
        padded['sample_ids'] = [item['sample_id'] for item in batch]
        return padded

    def _collate_windowed(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        batch_size = len(batch)
        max_windows = max((len(item['input_ids']) for item in batch))
        pad_token_id = int(getattr(self.tokenizer, 'pad_token_id', 0) or 0)
        flat_features = []
        flat_window_lengths = []
        flat_window_starts = []
        for item in batch:
            num_windows = len(item['input_ids'])
            for input_ids, attention_mask, dms_values, window_start in zip(item['input_ids'], item['attention_mask'], item['dms'], item['window_starts']):
                flat_features.append({'input_ids': input_ids, 'attention_mask': attention_mask})
                flat_window_lengths.append(len(dms_values))
                flat_window_starts.append(int(window_start))
            for _ in range(max_windows - num_windows):
                flat_features.append({'input_ids': [pad_token_id], 'attention_mask': [0]})
                flat_window_lengths.append(0)
                flat_window_starts.append(-1)
        padded = self.tokenizer.pad(flat_features, return_tensors='pt')
        _, padded_len = padded['input_ids'].shape
        input_ids = padded['input_ids'].view(batch_size, max_windows, padded_len)
        attention_mask = padded['attention_mask'].view(batch_size, max_windows, padded_len)
        labels = torch.zeros(batch_size, max_windows, padded_len, dtype=torch.float32)
        label_mask = torch.zeros(batch_size, max_windows, padded_len, dtype=torch.bool)
        global_positions = torch.full((batch_size, max_windows, padded_len), -1, dtype=torch.long)
        nt_lens = torch.tensor([len(item['sequence']) for item in batch], dtype=torch.long)
        window_mask = torch.zeros(batch_size, max_windows, dtype=torch.bool)
        for batch_index, item in enumerate(batch):
            for window_index, (dms_values, window_start) in enumerate(zip(item['dms'], item['window_starts'])):
                window_mask[batch_index, window_index] = True
                for pos, value in enumerate(dms_values):
                    token_pos = pos + 1
                    if token_pos >= padded_len:
                        continue
                    global_positions[batch_index, window_index, token_pos] = int(window_start) + pos
                    if value <= -999:
                        continue
                    labels[batch_index, window_index, token_pos] = float(value)
                    label_mask[batch_index, window_index, token_pos] = True
        return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': labels, 'label_mask': label_mask, 'global_positions': global_positions, 'window_mask': window_mask, 'nt_lens': nt_lens, 'sample_ids': [item['sample_id'] for item in batch]}

class DMSRegressionModel(nn.Module):

    def __init__(self, encoder: nn.Module, hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder: nn.Module | None=None) -> None:
        super().__init__()
        self.encoder = encoder
        self.finetune_scheme = finetune_scheme
        self.scheme_encoder = scheme_encoder
        self.head = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.GELU(), nn.LayerNorm(hidden_size), nn.Dropout(dropout), nn.Linear(hidden_size, 1))

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        if self.scheme_encoder is None:
            if input_ids.dim() == 3:
                batch_size, num_windows, seq_len = input_ids.shape
                flat_input_ids = input_ids.reshape(batch_size * num_windows, seq_len)
                flat_attention_mask = attention_mask.reshape(batch_size * num_windows, seq_len)
                token_embeddings = self.encoder(input_ids=flat_input_ids, attention_mask=flat_attention_mask)
                logits = self.head(token_embeddings).squeeze(-1)
                return logits.view(batch_size, num_windows, seq_len)
            token_embeddings = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
            return self.head(token_embeddings).squeeze(-1)
        token_embeddings = self.scheme_encoder(self.encoder, input_ids, attention_mask)
        if token_embeddings.dim() == 4:
            batch_size, num_windows, seq_len, hidden_size = token_embeddings.shape
            logits = self.head(token_embeddings.view(batch_size * num_windows, seq_len, hidden_size)).squeeze(-1)
            return logits.view(batch_size, num_windows, seq_len)
        return self.head(token_embeddings).squeeze(-1)

def load_split_records(data_dir: str) -> Dict[str, List[Dict]]:
    return load_task_records(data_dir, target='dms')

def compute_masked_mse(logits: torch.Tensor, labels: torch.Tensor, label_mask: torch.Tensor) -> torch.Tensor:
    preds = logits[label_mask]
    targets = labels[label_mask]
    if preds.numel() == 0:
        return logits.sum() * 0.0
    return torch.mean((preds - targets) ** 2)

def aggregate_windowed_dms_predictions(logits: torch.Tensor, labels: torch.Tensor, label_mask: torch.Tensor, global_positions: torch.Tensor | None, nt_lens: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if global_positions is None:
        return (logits, labels, label_mask)
    batch_size = logits.size(0)
    max_nt_len = int(nt_lens.max().item())
    pred_sums = logits.new_zeros((batch_size, max_nt_len))
    pred_counts = logits.new_zeros((batch_size, max_nt_len))
    target_sums = labels.new_zeros((batch_size, max_nt_len))
    target_counts = labels.new_zeros((batch_size, max_nt_len))
    for batch_index in range(batch_size):
        valid_positions = global_positions[batch_index] >= 0
        if not valid_positions.any():
            continue
        batch_global = global_positions[batch_index][valid_positions]
        batch_preds = logits[batch_index][valid_positions]
        pred_sums[batch_index].index_add_(0, batch_global, batch_preds)
        pred_counts[batch_index].index_add_(0, batch_global, torch.ones_like(batch_preds))
        batch_label_positions = label_mask[batch_index] & valid_positions
        if batch_label_positions.any():
            label_global = global_positions[batch_index][batch_label_positions]
            batch_targets = labels[batch_index][batch_label_positions]
            target_sums[batch_index].index_add_(0, label_global, batch_targets)
            target_counts[batch_index].index_add_(0, label_global, torch.ones_like(batch_targets))
    aggregated_preds = pred_sums / pred_counts.clamp_min(1.0)
    aggregated_targets = target_sums / target_counts.clamp_min(1.0)
    aggregated_mask = target_counts > 0
    return (aggregated_preds, aggregated_targets, aggregated_mask)

def describe_nonfinite(name: str, tensor: torch.Tensor, *, epoch: int | None=None, batch_idx: int | None=None, args=None, sample_ids: List[str] | None=None) -> str | None:
    if torch.isfinite(tensor).all():
        return None
    details = [f'{name} became non-finite']
    if epoch is not None:
        details.append(f'epoch={epoch}')
    if batch_idx is not None:
        details.append(f'batch={batch_idx}')
    if args is not None:
        details.append(f'model_backend={args.model_backend}')
        details.append(f'checkpoint={args.from_pretrained}')
    if sample_ids:
        details.append(f'sample_ids={sample_ids}')
    finite_mask = torch.isfinite(tensor)
    finite_values = tensor[finite_mask]
    if finite_values.numel():
        details.append(f'finite_min={float(finite_values.min().item()):.6g}')
        details.append(f'finite_max={float(finite_values.max().item()):.6g}')
    details.append(f'nan_count={int(torch.isnan(tensor).sum().item())}')
    details.append(f'inf_count={int(torch.isinf(tensor).sum().item())}')
    return '[Numerics] ' + ', '.join(details)

@torch.no_grad()
def evaluate(model: nn.Module, data_loader: DataLoader, device: torch.device) -> Dict[str, float]:
    model.eval()
    total_squared_error = 0.0
    total_absolute_error = 0.0
    total_count = 0
    preds_all = []
    targets_all = []
    for batch_idx, batch in enumerate(data_loader, start=1):
        batch = move_batch_to_device(batch, device)
        logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
        global_positions = batch.get('global_positions')
        message = describe_nonfinite('eval_logits', logits, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
        if message is not None:
            raise RuntimeError(message)
        aggregated_preds, aggregated_targets, aggregated_mask = aggregate_windowed_dms_predictions(logits, batch['labels'], batch['label_mask'], global_positions, batch['nt_lens'])
        preds = aggregated_preds[aggregated_mask]
        targets = aggregated_targets[aggregated_mask]
        if preds.numel() == 0:
            continue
        total_squared_error += torch.sum((preds - targets) ** 2).item()
        total_absolute_error += torch.sum(torch.abs(preds - targets)).item()
        total_count += preds.numel()
        preds_all.append(preds.detach().cpu())
        targets_all.append(targets.detach().cpu())
    if total_count == 0:
        return {'loss': 0.0, 'mae': 0.0, 'pearson': 0.0}
    stacked_preds = torch.cat(preds_all, dim=0)
    stacked_targets = torch.cat(targets_all, dim=0)
    return {'loss': total_squared_error / total_count, 'mae': total_absolute_error / total_count, 'pearson': pearson_corr(stacked_preds, stacked_targets)}

def train(args: argparse.Namespace) -> None:
    set_seed(args.seed)
    device = torch.device(args.device if args.device else 'cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer, effective_max_length = build_tokenizer(args)
    split_records = load_split_records(args.data_dir)
    print({'split_sizes': {name: len(rows) for name, rows in split_records.items()}}, flush=True)
    train_dataset = HumanMRNADMSDataset(split_records['train'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    val_dataset = HumanMRNADMSDataset(split_records['val'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    test_dataset = HumanMRNADMSDataset(split_records['test'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    collator = DMSCollator(tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collator)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    encoder, hidden_size = build_encoder(args, tokenizer, device)
    scheme_encoder = build_token_scheme_encoder(hidden_size, args)
    model = DMSRegressionModel(encoder, hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    if args.freeze_encoder:
        for param in model.encoder.parameters():
            param.requires_grad = False
        trainable = count_initialized_parameters(model, trainable_only=True)
        total = count_initialized_parameters(model)
        print(f'[Freeze] encoder frozen, trainable: {trainable:,}/{total:,} ({100 * trainable / total:.1f}%)', flush=True)
    optimizer = torch.optim.AdamW([param for param in model.parameters() if param.requires_grad], lr=args.lr if args.warmup_steps <= 0 else 0.0, weight_decay=args.weight_decay)
    warmup_steps = args.warmup_steps
    global_step = 0
    os.makedirs(args.output_dir, exist_ok=True)
    best_metric = -math.inf
    epochs_without_improvement = 0
    best_path = os.path.join(args.output_dir, 'best_model.pt')
    history = []
    print({'task': 'human_mRNA_dms_specialized', 'model_backend': args.model_backend, 'num_train': len(train_dataset), 'num_val': len(val_dataset), 'num_test': len(test_dataset), 'freeze_base': args.freeze_base, 'from_pretrained': args.from_pretrained, 'effective_max_length': effective_max_length, 'long_seq_strategy': args.long_seq_strategy, 'window_overlap': args.window_overlap, 'finetune_scheme': args.finetune_scheme}, flush=True)
    for epoch in range(1, args.epoch + 1):
        model.train()
        total_loss = 0.0
        total_items = 0
        skipped_batches = 0
        accum_steps = 0
        optimizer.zero_grad(set_to_none=True)
        for batch_idx, batch in enumerate(train_loader, start=1):
            batch = move_batch_to_device(batch, device)
            logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
            message = describe_nonfinite('train_logits', logits, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            aggregated_preds, aggregated_targets, aggregated_mask = aggregate_windowed_dms_predictions(logits, batch['labels'], batch['label_mask'], batch.get('global_positions'), batch['nt_lens'])
            loss = compute_masked_mse(aggregated_preds, aggregated_targets, aggregated_mask)
            message = describe_nonfinite('train_loss', loss, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            (loss / args.grad_accum_steps).backward()
            accum_steps += 1
            should_step = accum_steps == args.grad_accum_steps or batch_idx == len(train_loader)
            if should_step and args.max_grad_norm > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
            bad_grad_message = None
            for name, param in model.named_parameters():
                if param.grad is not None:
                    bad_grad_message = describe_nonfinite(f'grad[{name}]', param.grad, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
                    if bad_grad_message is not None:
                        break
            if bad_grad_message is not None:
                optimizer.zero_grad(set_to_none=True)
                accum_steps = 0
                print(bad_grad_message + ' [Action] skipping optimizer step for this batch.', flush=True)
                skipped_batches += 1
                continue
            if should_step:
                optimizer.step()
                global_step += 1
                if warmup_steps > 0 and global_step <= warmup_steps:
                    for pg in optimizer.param_groups:
                        pg['lr'] = args.lr * global_step / warmup_steps
                optimizer.zero_grad(set_to_none=True)
                accum_steps = 0
            batch_size = batch['input_ids'].size(0)
            total_loss += loss.item() * batch_size
            total_items += batch_size
        train_loss = total_loss / max(total_items, 1) if total_items > 0 else float('nan')
        val_metrics = evaluate(model, val_loader, device)
        epoch_record = {'epoch': epoch, 'train_loss': train_loss, 'skipped_batches': skipped_batches, **{f'val_{key}': value for key, value in val_metrics.items()}}
        if args.eval_test_each_epoch:
            test_metrics = evaluate(model, test_loader, device)
            epoch_record.update({f'test_{key}': value for key, value in test_metrics.items()})
        history.append(epoch_record)
        print(epoch_record, flush=True)
        if args.save_every_epochs > 0 and epoch % args.save_every_epochs == 0:
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'epoch': epoch}, os.path.join(args.output_dir, f'checkpoint_epoch_{epoch}.pt'))
        if val_metrics['pearson'] > best_metric + args.early_stop_min_delta:
            best_metric = val_metrics['pearson']
            epochs_without_improvement = 0
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'best_val_pearson': best_metric}, best_path)
        else:
            epochs_without_improvement += 1
        if args.early_stop_patience > 0 and epoch >= args.early_stop_min_epochs and (epochs_without_improvement >= args.early_stop_patience):
            print({'early_stop': True, 'epoch': epoch, 'best_val_pearson': best_metric, 'epochs_without_improvement': epochs_without_improvement, 'early_stop_patience': args.early_stop_patience, 'early_stop_min_epochs': args.early_stop_min_epochs, 'early_stop_min_delta': args.early_stop_min_delta}, flush=True)
            break
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    final_test = evaluate(model, test_loader, device)
    print({'best_val_pearson': best_metric, **{f'final_test_{key}': value for key, value in final_test.items()}}, flush=True)
    with open(os.path.join(args.output_dir, 'history.json'), 'w') as fout:
        json.dump(history, fout, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Specialized finetuning for the human mRNA DMS task.')
    parser.add_argument('--model_backend', choices=['lncrfm'], default='lncrfm')
    parser.add_argument('--from_pretrained', type=str, default=checkpoint_path())
    parser.add_argument('--data_dir', '--data_file', type=str, default=data_path('mRNA-DMS.parquet'))
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_length', type=int, default=2050)
    parser.add_argument('--dim', type=int, default=768)
    parser.add_argument('--layer', type=int, default=12)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--batch_size', type=int, default=2)
    parser.add_argument('--epoch', type=int, default=50)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--warmup_steps', type=int, default=0)
    parser.add_argument('--freeze_encoder', action='store_true')
    parser.add_argument('--weight_decay', type=float, default=0.01)
    parser.add_argument('--max_grad_norm', type=float, default=0.5)
    parser.add_argument('--grad_accum_steps', type=int, default=1)
    parser.add_argument('--save_every_epochs', type=int, default=0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--device', type=str, default=None)
    parser.add_argument('--long_seq_strategy', choices=['truncation', 'sliding_window'], default='truncation')
    parser.add_argument('--window_overlap', type=int, default=256)
    parser.add_argument('--early_stop_patience', type=int, default=10)
    parser.add_argument('--early_stop_min_epochs', type=int, default=15)
    parser.add_argument('--early_stop_min_delta', type=float, default=0.001)
    add_finetune_scheme_args(parser)
    parser.add_argument('--freeze_base', action='store_true')
    parser.add_argument('--eval_test_each_epoch', dest='eval_test_each_epoch', action='store_true')
    parser.add_argument('--no_eval_test_each_epoch', dest='eval_test_each_epoch', action='store_false')
    parser.set_defaults(eval_test_each_epoch=True)
    args = parser.parse_args()
    args.grad_accum_steps = max(1, args.grad_accum_steps)
    if args.model_backend == 'lncrfm' and args.from_pretrained == checkpoint_path():
        args.from_pretrained = DEFAULT_LNCRFM_MOTIF_CKPT
    return args
if __name__ == '__main__':
    train(parse_args())
