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
from LncDowntask.finetune_lncrna_hm_reference import ClassWeights, add_finetune_scheme_args, build_class_weights, evaluate, should_build_scheme_encoder
TASK_NAME_TO_KEY = {'donor': 'splice_site_donor', 'acceptor': 'splice_site_acceptor'}
from LncDowntask.data_paths import checkpoint_path, data_path
DEFAULT_SPLICE_SITE_DIR = Path(data_path('RiNALMo-Splice.parquet'))
DEFAULT_LNCRFM_CKPT = checkpoint_path()
DEFAULT_LNCRFM_MOTIF_CKPT = os.environ.get('LNCRFM_MOTIF_DEFAULT_CKPT', checkpoint_path())
DEFAULT_CHECKPOINT_DIR = checkpoint_path()

def _reference_module():
    return importlib.import_module('LncDowntask.finetune_lnc_binary_reference')

def task_key_for_name(task_name: str) -> str:
    try:
        return TASK_NAME_TO_KEY[task_name]
    except KeyError as exc:
        raise ValueError(f'unknown splice-site task_name: {task_name}') from exc

def load_split_records(data_dir: Path, task_name: str, split: str) -> List[Dict]:
    task_key_for_name(task_name)
    return load_task_records(data_dir, target='label_id', site=task_name)[split]

def load_all_split_records(data_dir: Path, task_name: str) -> Dict[str, List[Dict]]:
    task_key_for_name(task_name)
    return load_task_records(data_dir, target='label_id', site=task_name)

def select_validation_metric(val_metrics: Dict[str, float]) -> Dict[str, float | str | bool]:
    return {'metric': 'val_f1', 'value': float(val_metrics['f1']), 'used_fallback': False}

def train(args: argparse.Namespace) -> None:
    ref = _reference_module()
    torch = ref.torch
    DataLoader = ref.DataLoader
    RandomSampler = ref.RandomSampler
    task_key = task_key_for_name(args.task_name)
    task_identity = f'splice_site_{args.task_name}_reference'
    ref.set_seed(args.seed)
    device = torch.device(args.device if args.device else 'cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer, effective_max_length = ref.build_tokenizer(args)
    split_records = load_all_split_records(args.data_dir, args.task_name)
    print({'split_sizes': {name: len(rows) for name, rows in split_records.items()}}, flush=True)
    train_dataset = ref.LNCBinaryDataset(split_records['train'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    val_dataset = ref.LNCBinaryDataset(split_records['val'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    test_dataset = ref.LNCBinaryDataset(split_records['test'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    collator = ref.LNCBinaryCollator(tokenizer)
    train_sampler = None
    if args.n_samples_per_epoch > 0:
        train_sampler = RandomSampler(train_dataset, replacement=True, num_samples=args.n_samples_per_epoch)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=train_sampler is None, sampler=train_sampler, collate_fn=collator)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    encoder, hidden_size = ref.build_encoder(args, tokenizer, device)
    scheme_encoder = None
    if should_build_scheme_encoder(args):
        scheme_encoder = ref.build_sequence_scheme_encoder(hidden_size, args)
    if args.mode == 'finetune':
        model = ref.FineTuneClassifier(encoder, hidden_size, args.probe_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    else:
        model = ref.ProbeClassifier(encoder, hidden_size, args.probe_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    if args.freeze_encoder:
        for param in model.encoder.parameters():
            param.requires_grad = False
        trainable = ref.count_initialized_parameters(model, trainable_only=True)
        total = ref.count_initialized_parameters(model)
        print(f'[Freeze] encoder frozen, trainable: {trainable:,}/{total:,} ({100 * trainable / total:.1f}%)', flush=True)
    optimizer = torch.optim.Adam([param for param in model.parameters() if param.requires_grad], lr=args.lr if args.warmup_steps <= 0 else 0.0, weight_decay=args.weight_decay)
    warmup_steps = args.warmup_steps
    global_step = 0
    class_weights = build_class_weights(split_records['train']) if args.weighted_loss else ClassWeights(1.0, 1.0)
    os.makedirs(args.output_dir, exist_ok=True)
    best_selection_value = -math.inf
    best_selection_metric = 'val_f1'
    best_val_roc_auc = float('nan')
    best_val_f1 = float('nan')
    best_epoch = 0
    epochs_without_improvement = 0
    best_path = os.path.join(args.output_dir, 'best_model.pt')
    history: List[Dict] = []
    print({'task': task_identity, 'task_key': task_key, 'mode': args.mode, 'model_backend': args.model_backend, 'num_train': len(train_dataset), 'num_val': len(val_dataset), 'num_test': len(test_dataset), 'freeze_base': args.freeze_base, 'freeze_encoder': args.freeze_encoder, 'from_pretrained': args.from_pretrained, 'effective_max_length': effective_max_length, 'long_seq_strategy': args.long_seq_strategy, 'window_overlap': args.window_overlap, 'finetune_scheme': args.finetune_scheme, 'n_samples_per_epoch': args.n_samples_per_epoch, 'weighted_loss': args.weighted_loss, 'class_weights': {'negative': round(class_weights.negative, 6), 'positive': round(class_weights.positive, 6)}, 'selection_metric': 'val_f1', 'reported_metrics': ['loss', 'accuracy', 'precision', 'recall', 'f1', 'roc_auc']}, flush=True)
    for epoch in range(1, args.epoch + 1):
        model.train()
        total_loss = 0.0
        total_items = 0
        skipped_batches = 0
        accum_steps = 0
        optimizer.zero_grad(set_to_none=True)
        for batch_idx, batch in enumerate(train_loader, start=1):
            batch = ref.move_batch_to_device(batch, device)
            logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], token_mask=batch['token_mask'])
            message = ref.describe_nonfinite('train_logits', logits, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
            if message is not None:
                print(message + ' [Action] skipping batch before backward.', flush=True)
                skipped_batches += 1
                continue
            loss = ref.compute_weighted_bce_loss(logits, batch['labels'], class_weights)
            message = ref.describe_nonfinite('train_loss', loss, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
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
                    bad_grad_message = ref.describe_nonfinite(f'grad[{name}]', param.grad, epoch=epoch, batch_idx=batch_idx, args=args, sample_ids=batch['sample_ids'])
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
        metric_selection = select_validation_metric(val_metrics)
        epoch_record = {'epoch': epoch, 'train_loss': train_loss, 'skipped_batches': skipped_batches, **{f'val_{key}': value for key, value in val_metrics.items()}, 'selection_metric': metric_selection['metric'], 'selection_value': metric_selection['value'], 'selection_used_fallback': metric_selection['used_fallback']}
        if args.eval_test_each_epoch:
            test_metrics = evaluate(model, test_loader, device, class_weights, args.threshold)
            epoch_record.update({f'test_{key}': value for key, value in test_metrics.items()})
        history.append(epoch_record)
        print(epoch_record, flush=True)
        if args.save_every_epochs > 0 and epoch % args.save_every_epochs == 0:
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'epoch': epoch, 'class_weights': {'negative': class_weights.negative, 'positive': class_weights.positive}}, os.path.join(args.output_dir, f'checkpoint_epoch_{epoch}.pt'))
        selection_value = float(metric_selection['value'])
        if selection_value > best_selection_value + args.early_stop_min_delta:
            best_selection_value = selection_value
            best_selection_metric = str(metric_selection['metric'])
            best_val_roc_auc = float(val_metrics['roc_auc'])
            best_val_f1 = float(val_metrics['f1'])
            best_epoch = epoch
            epochs_without_improvement = 0
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_roc_auc': best_val_roc_auc, 'best_val_f1': best_val_f1, 'best_epoch': best_epoch, 'class_weights': {'negative': class_weights.negative, 'positive': class_weights.positive}}, best_path)
        else:
            epochs_without_improvement += 1
        if args.early_stop_patience > 0 and epoch >= args.early_stop_min_epochs and (epochs_without_improvement >= args.early_stop_patience):
            print({'early_stop': True, 'epoch': epoch, 'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_roc_auc': best_val_roc_auc, 'best_val_f1': best_val_f1, 'best_epoch': best_epoch, 'epochs_without_improvement': epochs_without_improvement, 'early_stop_patience': args.early_stop_patience, 'early_stop_min_epochs': args.early_stop_min_epochs, 'early_stop_min_delta': args.early_stop_min_delta}, flush=True)
            break
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    final_test = evaluate(model, test_loader, device, class_weights, args.threshold)
    print({'best_selection_metric': best_selection_metric, 'best_selection_value': best_selection_value, 'best_val_f1': best_val_f1, 'best_epoch': best_epoch, 'best_val_roc_auc': best_val_roc_auc, **{f'final_test_{key}': value for key, value in final_test.items()}}, flush=True)
    with open(os.path.join(args.output_dir, 'history.json'), 'w', encoding='utf-8') as fout:
        json.dump(history, fout, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Reference-style fine-tuning/probing for splice-site classification.')
    parser.add_argument('--task_name', choices=sorted(TASK_NAME_TO_KEY), default='donor')
    parser.add_argument('--mode', choices=['finetune', 'probing'], default='finetune')
    parser.add_argument('--model_backend', choices=['lncrfm'], default='lncrfm')
    parser.add_argument('--from_pretrained', type=str, default=DEFAULT_LNCRFM_CKPT)
    parser.add_argument('--data_dir', '--data_file', type=str, default=data_path('RiNALMo-Splice.parquet'))
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_length', type=int, default=2050)
    parser.add_argument('--dim', type=int, default=768)
    parser.add_argument('--layer', type=int, default=12)
    parser.add_argument('--dropout', type=float, default=0.0)
    parser.add_argument('--probe_hidden_size', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--epoch', type=int, default=100)
    parser.add_argument('--n_samples_per_epoch', type=int, default=0)
    parser.add_argument('--lr', type=float, default=1e-05)
    parser.add_argument('--warmup_steps', type=int, default=0)
    parser.add_argument('--freeze_encoder', action='store_true')
    parser.add_argument('--weight_decay', type=float, default=0.0)
    parser.add_argument('--max_grad_norm', type=float, default=1.0)
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
