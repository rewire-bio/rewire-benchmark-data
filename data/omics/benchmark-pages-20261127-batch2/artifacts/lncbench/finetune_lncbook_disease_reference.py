from __future__ import annotations
from lncbench_data import load_task_records
import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, RandomSampler
from finetune_schemes.runtime import add_finetune_scheme_args, build_sequence_scheme_encoder, count_initialized_parameters
from human_mrna_task_common import collate_sequence_batch, build_encoder, build_tokenizer, move_batch_to_device, pooled_sequence_features, precision_recall_f1, prepare_sequence_batch_item, sanitize_sequence, set_seed
from LncDowntask.data_paths import data_path, checkpoint_path
DEFAULT_LNCBOOK_DISEASE_DIR = data_path('Disease.parquet')
DEFAULT_LNCRFM_CKPT = checkpoint_path()
DEFAULT_LNCRFM_MOTIF_CKPT = os.environ.get('LNCRFM_MOTIF_DEFAULT_CKPT', checkpoint_path())

@dataclass
class ClassWeights:
    negative: float
    positive: float

class LNCBookDiseaseDataset(Dataset):

    def __init__(self, records: List[Dict], tokenizer, max_length: int, model_backend: str, long_seq_strategy: str, window_overlap: int) -> None:
        self.records = records
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.model_backend = model_backend
        self.long_seq_strategy = long_seq_strategy
        self.window_overlap = window_overlap

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Dict:
        record = self.records[idx]
        sequence = sanitize_sequence(record['sequence'])
        encoded = prepare_sequence_batch_item(sequence, self.tokenizer, self.max_length, self.model_backend, long_seq_strategy=self.long_seq_strategy, window_overlap=self.window_overlap)
        return {'input_ids': encoded['input_ids'], 'attention_mask': encoded['attention_mask'], 'special_tokens_mask': encoded.get('special_tokens_mask'), 'label': float(record['label']), 'nt_len': encoded['nt_len'], 'sample_id': record['sample_id']}

class DiseaseCollator:

    def __init__(self, tokenizer) -> None:
        self.tokenizer = tokenizer

    def __call__(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        padded = collate_sequence_batch(self.tokenizer, batch)
        padded['labels'] = torch.tensor([item['label'] for item in batch], dtype=torch.float32).unsqueeze(-1)
        padded['sample_ids'] = [item['sample_id'] for item in batch]
        return padded

class FineTuneClassifier(nn.Module):

    def __init__(self, encoder: nn.Module, hidden_size: int, probe_hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder: nn.Module | None=None) -> None:
        super().__init__()
        self.encoder = encoder
        self.finetune_scheme = finetune_scheme
        self.scheme_encoder = scheme_encoder
        self.output = nn.Sequential(nn.Linear(hidden_size, probe_hidden_size), nn.ReLU(), nn.Dropout(dropout), nn.Linear(probe_hidden_size, 1))

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, token_mask: torch.Tensor) -> torch.Tensor:
        if self.scheme_encoder is None:
            cls_feature = pooled_sequence_features(self.encoder, input_ids, attention_mask, token_mask, pooling='cls')
        else:
            cls_feature = self.scheme_encoder(self.encoder, input_ids, attention_mask, token_mask, pooling='cls')
        return self.output(cls_feature)

class ProbeClassifier(nn.Module):

    def __init__(self, encoder: nn.Module, hidden_size: int, probe_hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder: nn.Module | None=None) -> None:
        super().__init__()
        self.encoder = encoder
        self.finetune_scheme = finetune_scheme
        self.scheme_encoder = scheme_encoder
        self.probe = nn.Sequential(nn.Linear(hidden_size, probe_hidden_size), nn.ReLU(), nn.Dropout(dropout), nn.Linear(probe_hidden_size, 1))

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, token_mask: torch.Tensor) -> torch.Tensor:
        if self.scheme_encoder is None:
            pooled = pooled_sequence_features(self.encoder, input_ids, attention_mask, token_mask, pooling='mean')
        else:
            pooled = self.scheme_encoder(self.encoder, input_ids, attention_mask, token_mask, pooling='mean')
        return self.probe(pooled)

def load_split_records(data_dir: str) -> Dict[str, List[Dict]]:
    return load_task_records(data_dir, target='label_id')

def build_class_weights(records: List[Dict]) -> ClassWeights:
    positives = sum((int(float(record['label']) >= 0.5) for record in records))
    negatives = len(records) - positives
    if positives == 0 or negatives == 0:
        return ClassWeights(negative=1.0, positive=1.0)
    neg_weight = 1.0 / negatives
    pos_weight = 1.0 / positives
    avg_weight = (neg_weight * negatives + pos_weight * positives) / (negatives + positives)
    return ClassWeights(negative=neg_weight / avg_weight, positive=pos_weight / avg_weight)

def compute_weighted_bce_loss(logits: torch.Tensor, labels: torch.Tensor, class_weights: ClassWeights) -> torch.Tensor:
    labels = labels.float()
    sample_weights = torch.where(labels >= 0.5, class_weights.positive, class_weights.negative)
    loss = nn.functional.binary_cross_entropy_with_logits(logits, labels, reduction='none')
    return torch.mean(loss * sample_weights)

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
def evaluate(model: nn.Module, data_loader: DataLoader, device: torch.device, class_weights: ClassWeights, threshold: float) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    total_items = 0
    all_probs = []
    all_targets = []
    for batch_idx, batch in enumerate(data_loader, start=1):
        batch = move_batch_to_device(batch, device)
        logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], token_mask=batch['token_mask'])
        message = describe_nonfinite('eval_logits', logits, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
        if message is not None:
            raise RuntimeError(message)
        loss = compute_weighted_bce_loss(logits, batch['labels'], class_weights)
        message = describe_nonfinite('eval_loss', loss, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
        if message is not None:
            raise RuntimeError(message)
        batch_size = batch['labels'].size(0)
        total_loss += float(loss.item()) * batch_size
        total_items += batch_size
        all_probs.append(torch.sigmoid(logits).detach().cpu().view(-1))
        all_targets.append(batch['labels'].detach().cpu().view(-1))
    probs = torch.cat(all_probs) if all_probs else torch.zeros(0)
    targets = torch.cat(all_targets).int() if all_targets else torch.zeros(0, dtype=torch.int32)
    preds = (probs >= threshold).int()
    tp = int(((preds == 1) & (targets == 1)).sum().item())
    fp = int(((preds == 1) & (targets == 0)).sum().item())
    fn = int(((preds == 0) & (targets == 1)).sum().item())
    precision, recall, f1 = precision_recall_f1(tp, fp, fn)
    accuracy = float((preds == targets).float().mean().item()) if targets.numel() else 0.0
    return {'loss': total_loss / max(total_items, 1), 'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1, 'threshold': threshold}

def train(args: argparse.Namespace) -> None:
    set_seed(args.seed)
    device = torch.device(args.device if args.device else 'cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer, effective_max_length = build_tokenizer(args)
    split_records = load_split_records(args.data_dir)
    print({'split_sizes': {name: len(rows) for name, rows in split_records.items()}}, flush=True)
    train_dataset = LNCBookDiseaseDataset(split_records['train'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    val_dataset = LNCBookDiseaseDataset(split_records['val'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    test_dataset = LNCBookDiseaseDataset(split_records['test'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    collator = DiseaseCollator(tokenizer)
    train_sampler = None
    if args.n_samples_per_epoch > 0:
        train_sampler = RandomSampler(train_dataset, replacement=True, num_samples=args.n_samples_per_epoch)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=train_sampler is None, sampler=train_sampler, collate_fn=collator)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    encoder, hidden_size = build_encoder(args, tokenizer, device)
    scheme_encoder = build_sequence_scheme_encoder(hidden_size, args)
    if args.mode == 'finetune':
        model = FineTuneClassifier(encoder, hidden_size, args.probe_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    else:
        model = ProbeClassifier(encoder, hidden_size, args.probe_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    if args.freeze_encoder:
        for param in model.encoder.parameters():
            param.requires_grad = False
        trainable = count_initialized_parameters(model, trainable_only=True)
        total = count_initialized_parameters(model)
        print(f'[Freeze] encoder frozen, trainable: {trainable:,}/{total:,} ({100 * trainable / total:.1f}%)', flush=True)
    optimizer = torch.optim.Adam([param for param in model.parameters() if param.requires_grad], lr=args.lr if args.warmup_steps <= 0 else 0.0, weight_decay=args.weight_decay)
    warmup_steps = args.warmup_steps
    global_step = 0
    class_weights = build_class_weights(split_records['train']) if args.weighted_loss else ClassWeights(1.0, 1.0)
    os.makedirs(args.output_dir, exist_ok=True)
    best_metric = -math.inf
    epochs_without_improvement = 0
    best_path = os.path.join(args.output_dir, 'best_model.pt')
    history: List[Dict[str, float]] = []
    print({'task': 'lncbook_disease_reference', 'mode': args.mode, 'model_backend': args.model_backend, 'num_train': len(train_dataset), 'num_val': len(val_dataset), 'num_test': len(test_dataset), 'freeze_base': args.freeze_base, 'from_pretrained': args.from_pretrained, 'effective_max_length': effective_max_length, 'long_seq_strategy': args.long_seq_strategy, 'window_overlap': args.window_overlap, 'finetune_scheme': args.finetune_scheme, 'n_samples_per_epoch': args.n_samples_per_epoch, 'weighted_loss': args.weighted_loss, 'class_weights': {'negative': round(class_weights.negative, 6), 'positive': round(class_weights.positive, 6)}}, flush=True)
    for epoch in range(1, args.epoch + 1):
        model.train()
        total_loss = 0.0
        total_items = 0
        skipped_batches = 0
        accum_steps = 0
        optimizer.zero_grad(set_to_none=True)
        for batch_idx, batch in enumerate(train_loader, start=1):
            batch = move_batch_to_device(batch, device)
            logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], token_mask=batch['token_mask'])
            message = describe_nonfinite('train_logits', logits, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            loss = compute_weighted_bce_loss(logits, batch['labels'], class_weights)
            message = describe_nonfinite('train_loss', loss, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            (loss / args.grad_accum_steps).backward()
            accum_steps += 1
            should_step = accum_steps == args.grad_accum_steps or batch_idx == len(train_loader)
            bad_grad_message = None
            if should_step and args.max_grad_norm > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
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
            batch_size = batch['labels'].size(0)
            total_loss += float(loss.item()) * batch_size
            total_items += batch_size
        train_loss = total_loss / max(total_items, 1) if total_items > 0 else float('nan')
        val_metrics = evaluate(model, val_loader, device, class_weights, args.threshold)
        epoch_record = {'epoch': epoch, 'train_loss': train_loss, 'skipped_batches': skipped_batches, **{f'val_{key}': value for key, value in val_metrics.items()}}
        if args.eval_test_each_epoch:
            test_metrics = evaluate(model, test_loader, device, class_weights, args.threshold)
            epoch_record.update({f'test_{key}': value for key, value in test_metrics.items()})
        history.append(epoch_record)
        print(epoch_record, flush=True)
        if args.save_every_epochs > 0 and epoch % args.save_every_epochs == 0:
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'epoch': epoch, 'class_weights': {'negative': class_weights.negative, 'positive': class_weights.positive}}, os.path.join(args.output_dir, f'checkpoint_epoch_{epoch}.pt'))
        if val_metrics['f1'] > best_metric + args.early_stop_min_delta:
            best_metric = val_metrics['f1']
            epochs_without_improvement = 0
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'best_val_f1': best_metric, 'class_weights': {'negative': class_weights.negative, 'positive': class_weights.positive}}, best_path)
        else:
            epochs_without_improvement += 1
        if args.early_stop_patience > 0 and epoch >= args.early_stop_min_epochs and (epochs_without_improvement >= args.early_stop_patience):
            print({'early_stop': True, 'epoch': epoch, 'best_val_f1': best_metric, 'epochs_without_improvement': epochs_without_improvement, 'early_stop_patience': args.early_stop_patience, 'early_stop_min_epochs': args.early_stop_min_epochs, 'early_stop_min_delta': args.early_stop_min_delta}, flush=True)
            break
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    final_test = evaluate(model, test_loader, device, class_weights, args.threshold)
    print({'best_val_f1': best_metric, **{f'final_test_{key}': value for key, value in final_test.items()}}, flush=True)
    with open(os.path.join(args.output_dir, 'history.json'), 'w') as fout:
        json.dump(history, fout, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Reference-style fine-tuning/probing for lncbook_disease.')
    parser.add_argument('--mode', choices=['finetune', 'probing'], default='finetune')
    parser.add_argument('--model_backend', choices=['lncrfm'], default='lncrfm')
    parser.add_argument('--from_pretrained', type=str, default=DEFAULT_LNCRFM_CKPT)
    parser.add_argument('--data_dir', '--data_file', type=str, default=data_path('Disease.parquet'))
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_length', type=int, default=2050)
    parser.add_argument('--dim', type=int, default=768)
    parser.add_argument('--layer', type=int, default=12)
    parser.add_argument('--dropout', type=float, default=0.0)
    parser.add_argument('--probe_hidden_size', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--epoch', type=int, default=100)
    parser.add_argument('--n_samples_per_epoch', type=int, default=10000)
    parser.add_argument('--lr', type=float, default=1e-05)
    parser.add_argument('--warmup_steps', type=int, default=0)
    parser.add_argument('--freeze_encoder', action='store_true')
    parser.add_argument('--weight_decay', type=float, default=0.0)
    parser.add_argument('--max_grad_norm', type=float, default=0.5)
    parser.add_argument('--grad_accum_steps', type=int, default=1)
    parser.add_argument('--save_every_epochs', type=int, default=0)
    parser.add_argument('--threshold', type=float, default=0.5)
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
    parser.add_argument('--weighted_loss', dest='weighted_loss', action='store_true')
    parser.add_argument('--no_weighted_loss', dest='weighted_loss', action='store_false')
    parser.set_defaults(weighted_loss=True)
    parser.set_defaults(eval_test_each_epoch=True)
    args = parser.parse_args()
    args.grad_accum_steps = max(1, args.grad_accum_steps)
    if args.model_backend == 'lncrfm' and args.from_pretrained == DEFAULT_LNCRFM_CKPT:
        args.from_pretrained = DEFAULT_LNCRFM_MOTIF_CKPT
    if args.mode == 'probing':
        args.freeze_base = True
        if args.lr == 1e-05:
            args.lr = 0.0001
    return args
if __name__ == '__main__':
    train(parse_args())
