from __future__ import annotations
from lncbench_data import load_task_records
import argparse
import importlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
for _path in (PROJECT_ROOT, SCRIPT_DIR):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)
TASK_KEY = '5utr_mrl'
TASK_NAME = '5utr_mrl_reference'
from LncDowntask.data_paths import checkpoint_path, data_path
DEFAULT_5UTR_MRL_DIR = Path(data_path('5UTR-MRL.parquet'))
DEFAULT_LNCRFM_CKPT = checkpoint_path()
DEFAULT_LNCRFM_MOTIF_CKPT = os.environ.get('LNCRFM_MOTIF_DEFAULT_CKPT', checkpoint_path())
DEFAULT_CHECKPOINT_DIR = checkpoint_path()

def _runtime_modules() -> Dict[str, object]:
    torch = importlib.import_module('torch')
    nn = importlib.import_module('torch.nn')
    data = importlib.import_module('torch.utils.data')
    common = importlib.import_module('LncDowntask.human_mrna_task_common')
    schemes = importlib.import_module('LncDowntask.finetune_schemes.runtime')
    return {'torch': torch, 'nn': nn, 'DataLoader': data.DataLoader, 'RandomSampler': data.RandomSampler, 'add_finetune_scheme_args': schemes.add_finetune_scheme_args, 'build_sequence_scheme_encoder': schemes.build_sequence_scheme_encoder, 'count_initialized_parameters': schemes.count_initialized_parameters, 'build_encoder': common.build_encoder, 'build_tokenizer': common.build_tokenizer, 'collate_sequence_batch': common.collate_sequence_batch, 'move_batch_to_device': common.move_batch_to_device, 'pearson_corr': common.pearson_corr, 'pooled_sequence_features': common.pooled_sequence_features, 'prepare_sequence_batch_item': common.prepare_sequence_batch_item, 'sanitize_sequence': common.sanitize_sequence, 'set_seed': common.set_seed}

def add_finetune_scheme_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--finetune_scheme', choices=['baseline', 'adapter'], default='baseline')
    parser.add_argument('--scheme_dropout', type=float, default=-1.0)
    parser.add_argument('--scheme_bottleneck_size', type=int, default=192)
    parser.add_argument('--router_hidden_size', type=int, default=128)
    parser.add_argument('--routing_temperature', type=float, default=1.0)
    parser.add_argument('--scheme_kernel_sizes', type=str, default='3,5,7')
    parser.add_argument('--scheme_structure_dilations', type=str, default='2,4')
    parser.add_argument('--adapter_residual_scale', type=float, default=1.0)

def should_build_scheme_encoder(args: argparse.Namespace) -> bool:
    return args.mode == 'probing' or args.freeze_base or args.finetune_scheme != 'baseline'

def load_split_records(data_dir: Path, split: str) -> List[Dict]:
    return load_task_records(data_dir, target='target')[split]

def load_all_split_records(data_dir: Path) -> Dict[str, List[Dict]]:
    return load_task_records(data_dir, target='target')

def select_validation_metric(val_metrics: Dict[str, float]) -> Dict[str, float | str | bool]:
    return {'metric': 'val_pearson_r2', 'value': float(val_metrics['pearson_r2']), 'used_fallback': False}

def should_update_best_checkpoint(*, best_epoch: int, selection_value: float, best_selection_value: float, min_delta: float) -> bool:
    return best_epoch == 0 or selection_value > best_selection_value + min_delta

def run_final_evaluations(model, best_path: str, test_loader, device, runtime: Dict[str, object]) -> Dict[str, Dict[str, float]]:
    torch = runtime['torch']
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    reports = {'test': evaluate(model, test_loader, device, runtime)}
    return reports

def describe_nonfinite(torch, name: str, tensor, *, epoch: int | None=None, batch_idx: int | None=None, args=None, sample_ids: List[str] | None=None) -> str | None:
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

class UTRMRLDataset:

    def __init__(self, records: List[Dict], tokenizer, max_length: int, model_backend: str, long_seq_strategy: str, window_overlap: int, runtime: Dict[str, object]) -> None:
        self.records = records
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.model_backend = model_backend
        self.long_seq_strategy = long_seq_strategy
        self.window_overlap = window_overlap
        self.prepare_sequence_batch_item = runtime['prepare_sequence_batch_item']
        self.sanitize_sequence = runtime['sanitize_sequence']

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Dict:
        record = self.records[idx]
        sequence = self.sanitize_sequence(record['sequence'])
        encoded = self.prepare_sequence_batch_item(sequence, self.tokenizer, self.max_length, self.model_backend, long_seq_strategy=self.long_seq_strategy, window_overlap=self.window_overlap)
        return {'input_ids': encoded['input_ids'], 'attention_mask': encoded['attention_mask'], 'special_tokens_mask': encoded.get('special_tokens_mask'), 'label': float(record['label']), 'nt_len': encoded['nt_len'], 'sample_id': record['sample_id']}

class RegressionCollator:

    def __init__(self, tokenizer, runtime: Dict[str, object]) -> None:
        self.tokenizer = tokenizer
        self.torch = runtime['torch']
        self.collate_sequence_batch = runtime['collate_sequence_batch']

    def __call__(self, batch: List[Dict]) -> Dict:
        padded = self.collate_sequence_batch(self.tokenizer, batch)
        padded['labels'] = self.torch.tensor([item['label'] for item in batch], dtype=self.torch.float32).unsqueeze(-1)
        padded['sample_ids'] = [item['sample_id'] for item in batch]
        return padded

def build_regressor_classes(runtime: Dict[str, object]):
    nn = runtime['nn']
    pooled_sequence_features = runtime['pooled_sequence_features']

    class FineTuneRegressor(nn.Module):

        def __init__(self, encoder, hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder=None) -> None:
            super().__init__()
            self.encoder = encoder
            self.finetune_scheme = finetune_scheme
            self.scheme_encoder = scheme_encoder
            self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden_size, hidden_size), nn.GELU(), nn.Dropout(dropout), nn.Linear(hidden_size, 1))

        def forward(self, input_ids, attention_mask, token_mask):
            if self.scheme_encoder is None:
                cls_feature = pooled_sequence_features(self.encoder, input_ids, attention_mask, token_mask, pooling='cls')
            else:
                cls_feature = self.scheme_encoder(self.encoder, input_ids, attention_mask, token_mask, pooling='cls')
            return self.head(cls_feature)

    class ProbeRegressor(nn.Module):

        def __init__(self, encoder, hidden_size: int, probe_hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder=None) -> None:
            super().__init__()
            self.encoder = encoder
            self.finetune_scheme = finetune_scheme
            self.scheme_encoder = scheme_encoder
            self.head = nn.Sequential(nn.Linear(hidden_size, probe_hidden_size), nn.GELU(), nn.Dropout(dropout), nn.Linear(probe_hidden_size, 1))

        def forward(self, input_ids, attention_mask, token_mask):
            if self.scheme_encoder is None:
                pooled = pooled_sequence_features(self.encoder, input_ids, attention_mask, token_mask, pooling='mean')
            else:
                pooled = self.scheme_encoder(self.encoder, input_ids, attention_mask, token_mask, pooling='mean')
            return self.head(pooled)
    return (FineTuneRegressor, ProbeRegressor)

def evaluate(model, data_loader, device, runtime: Dict[str, object]) -> Dict[str, float]:
    torch = runtime['torch']
    nn = runtime['nn']
    move_batch_to_device = runtime['move_batch_to_device']
    pearson_corr = runtime['pearson_corr']
    model.eval()
    total_squared_error = 0.0
    total_absolute_error = 0.0
    total_items = 0
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for batch_idx, batch in enumerate(data_loader, start=1):
            batch = move_batch_to_device(batch, device)
            logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], token_mask=batch['token_mask'])
            message = describe_nonfinite(torch, 'eval_logits', logits, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
            if message is not None:
                raise RuntimeError(message)
            preds = logits.view(-1)
            targets = batch['labels'].view(-1)
            loss = nn.functional.mse_loss(preds, targets, reduction='sum')
            message = describe_nonfinite(torch, 'eval_loss', loss, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
            if message is not None:
                raise RuntimeError(message)
            total_squared_error += float(loss.item())
            total_absolute_error += float(torch.sum(torch.abs(preds - targets)).item())
            total_items += int(targets.numel())
            all_preds.append(preds.detach().cpu())
            all_targets.append(targets.detach().cpu())
    if total_items == 0:
        return {'loss': 0.0, 'mae': 0.0, 'pearson': 0.0, 'pearson_r2': 0.0}
    stacked_preds = torch.cat(all_preds, dim=0)
    stacked_targets = torch.cat(all_targets, dim=0)
    pearson = float(pearson_corr(stacked_preds, stacked_targets))
    pearson_r2 = pearson * pearson if math.isfinite(pearson) else float('nan')
    return {'loss': total_squared_error / total_items, 'mae': total_absolute_error / total_items, 'pearson': pearson, 'pearson_r2': pearson_r2}

def train(args: argparse.Namespace) -> None:
    runtime = _runtime_modules()
    torch = runtime['torch']
    nn = runtime['nn']
    DataLoader = runtime['DataLoader']
    RandomSampler = runtime['RandomSampler']
    runtime['set_seed'](args.seed)
    device = torch.device(args.device if args.device else 'cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer, effective_max_length = runtime['build_tokenizer'](args)
    split_records = load_all_split_records(args.data_dir)
    print({'split_sizes': {name: len(rows) for name, rows in split_records.items()}}, flush=True)
    train_dataset = UTRMRLDataset(split_records['train'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap, runtime)
    val_dataset = UTRMRLDataset(split_records['val'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap, runtime)
    test_dataset = UTRMRLDataset(split_records['test'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap, runtime)
    collator = RegressionCollator(tokenizer, runtime)
    train_sampler = None
    if args.n_samples_per_epoch > 0:
        train_sampler = RandomSampler(train_dataset, replacement=True, num_samples=args.n_samples_per_epoch)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=train_sampler is None, sampler=train_sampler, collate_fn=collator)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    encoder, hidden_size = runtime['build_encoder'](args, tokenizer, device)
    scheme_encoder = None
    if should_build_scheme_encoder(args):
        scheme_encoder = runtime['build_sequence_scheme_encoder'](hidden_size, args)
    FineTuneRegressor, ProbeRegressor = build_regressor_classes(runtime)
    if args.mode == 'finetune':
        model = FineTuneRegressor(encoder, hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    else:
        model = ProbeRegressor(encoder, hidden_size, args.probe_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    if args.freeze_encoder:
        for param in model.encoder.parameters():
            param.requires_grad = False
        trainable = runtime['count_initialized_parameters'](model, trainable_only=True)
        total = runtime['count_initialized_parameters'](model)
        print(f'[Freeze] encoder frozen, trainable: {trainable:,}/{total:,} ({100 * trainable / total:.1f}%)', flush=True)
    optimizer = torch.optim.AdamW([param for param in model.parameters() if param.requires_grad], lr=args.lr if args.warmup_steps <= 0 else 0.0, weight_decay=args.weight_decay)
    warmup_steps = args.warmup_steps
    global_step = 0
    os.makedirs(args.output_dir, exist_ok=True)
    best_selection_value = -math.inf
    best_selection_metric = 'val_pearson_r2'
    best_val_pearson = float('nan')
    best_val_pearson_r2 = float('nan')
    best_epoch = 0
    epochs_without_improvement = 0
    best_path = os.path.join(args.output_dir, 'best_model.pt')
    history: List[Dict[str, float]] = []
    print({'task': TASK_NAME, 'task_key': TASK_KEY, 'mode': args.mode, 'model_backend': args.model_backend, 'num_train': len(train_dataset), 'num_val': len(val_dataset), 'num_test': len(test_dataset), 'freeze_base': args.freeze_base, 'freeze_encoder': args.freeze_encoder, 'from_pretrained': args.from_pretrained, 'effective_max_length': effective_max_length, 'long_seq_strategy': args.long_seq_strategy, 'window_overlap': args.window_overlap, 'finetune_scheme': args.finetune_scheme, 'n_samples_per_epoch': args.n_samples_per_epoch, 'selection_metric': 'val_pearson_r2', 'reported_metrics': ['loss', 'mae', 'pearson', 'pearson_r2']}, flush=True)
    for epoch in range(1, args.epoch + 1):
        model.train()
        total_loss = 0.0
        total_items = 0
        skipped_batches = 0
        accum_steps = 0
        optimizer.zero_grad(set_to_none=True)
        for batch_idx, batch in enumerate(train_loader, start=1):
            batch = runtime['move_batch_to_device'](batch, device)
            logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], token_mask=batch['token_mask'])
            message = describe_nonfinite(torch, 'train_logits', logits, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            preds = logits.view(-1)
            targets = batch['labels'].view(-1)
            loss = nn.functional.mse_loss(preds, targets)
            message = describe_nonfinite(torch, 'train_loss', loss, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
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
                    bad_grad_message = describe_nonfinite(torch, f'grad[{name}]', param.grad, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
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
        val_metrics = evaluate(model, val_loader, device, runtime)
        metric_selection = select_validation_metric(val_metrics)
        epoch_record = {'epoch': epoch, 'train_loss': train_loss, 'skipped_batches': skipped_batches, **{f'val_{key}': value for key, value in val_metrics.items()}, 'selection_metric': metric_selection['metric'], 'selection_value': metric_selection['value'], 'selection_used_fallback': metric_selection['used_fallback']}
        if args.eval_test_each_epoch:
            test_metrics = evaluate(model, test_loader, device, runtime)
            epoch_record.update({f'test_{key}': value for key, value in test_metrics.items()})
        history.append(epoch_record)
        print(epoch_record, flush=True)
        if args.save_every_epochs > 0 and epoch % args.save_every_epochs == 0:
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'epoch': epoch}, os.path.join(args.output_dir, f'checkpoint_epoch_{epoch}.pt'))
        selection_value = float(metric_selection['value'])
        should_update_best = should_update_best_checkpoint(best_epoch=best_epoch, selection_value=selection_value, best_selection_value=best_selection_value, min_delta=args.early_stop_min_delta)
        if should_update_best:
            best_selection_value = selection_value
            best_selection_metric = str(metric_selection['metric'])
            best_val_pearson = float(val_metrics['pearson'])
            best_val_pearson_r2 = float(val_metrics['pearson_r2'])
            best_epoch = epoch
            epochs_without_improvement = 0
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_pearson': best_val_pearson, 'best_val_pearson_r2': best_val_pearson_r2, 'best_epoch': best_epoch}, best_path)
        else:
            epochs_without_improvement += 1
        if args.early_stop_patience > 0 and epoch >= args.early_stop_min_epochs and (epochs_without_improvement >= args.early_stop_patience):
            print({'early_stop': True, 'epoch': epoch, 'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_pearson': best_val_pearson, 'best_val_pearson_r2': best_val_pearson_r2, 'best_epoch': best_epoch, 'epochs_without_improvement': epochs_without_improvement, 'early_stop_patience': args.early_stop_patience, 'early_stop_min_epochs': args.early_stop_min_epochs, 'early_stop_min_delta': args.early_stop_min_delta}, flush=True)
            break
    final_evaluations = run_final_evaluations(model, best_path, test_loader, device, runtime)
    final_test = final_evaluations['test']
    final_report = {'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_pearson': best_val_pearson, 'best_val_pearson_r2': best_val_pearson_r2, 'best_epoch': best_epoch, **{f'final_test_{key}': value for key, value in final_test.items()}}
    print(final_report, flush=True)
    with open(os.path.join(args.output_dir, 'history.json'), 'w', encoding='utf-8') as fout:
        json.dump(history, fout, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Reference-style fine-tuning/probing for 5utr_mrl regression.')
    parser.add_argument('--mode', choices=['finetune', 'probing'], default='finetune')
    parser.add_argument('--model_backend', choices=['lncrfm'], default='lncrfm')
    parser.add_argument('--from_pretrained', type=str, default=DEFAULT_LNCRFM_CKPT)
    parser.add_argument('--data_dir', '--data_file', type=str, default=data_path('5UTR-MRL.parquet'))
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_length', type=int, default=2050)
    parser.add_argument('--dim', type=int, default=768)
    parser.add_argument('--layer', type=int, default=12)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--probe_hidden_size', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--epoch', type=int, default=100)
    parser.add_argument('--n_samples_per_epoch', type=int, default=0)
    parser.add_argument('--lr', type=float, default=1e-05)
    parser.add_argument('--warmup_steps', type=int, default=0)
    parser.add_argument('--freeze_encoder', action='store_true')
    parser.add_argument('--weight_decay', type=float, default=0.01)
    parser.add_argument('--max_grad_norm', type=float, default=1.0)
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
    parser.set_defaults(eval_test_each_epoch=False)
    from_pretrained_provided = any((arg == '--from_pretrained' or arg.startswith('--from_pretrained=') for arg in sys.argv[1:]))
    args = parser.parse_args()
    args.grad_accum_steps = max(1, args.grad_accum_steps)
    if args.model_backend == 'lncrfm' and (not from_pretrained_provided) and (args.from_pretrained == DEFAULT_LNCRFM_CKPT):
        args.from_pretrained = DEFAULT_LNCRFM_MOTIF_CKPT
    if args.mode == 'probing':
        args.freeze_base = True
        if args.lr == 1e-05:
            args.lr = 0.0001
    return args
if __name__ == '__main__':
    train(parse_args())
