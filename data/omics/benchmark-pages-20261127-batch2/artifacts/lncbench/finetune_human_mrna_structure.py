from __future__ import annotations
from lncbench_data import load_task_records
import argparse
import json
import math
import os
from typing import Dict, List, Sequence, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from finetune_schemes.runtime import add_finetune_scheme_args, build_structure_scheme_encoder, count_initialized_parameters
from human_mrna_task_common import build_default_thresholds, build_encoder, build_tokenizer, can_form_canonical_pair, encode_sequence, move_batch_to_device, precision_recall_f1, sanitize_sequence, set_seed, split_sequence_into_windows
from LncDowntask.data_paths import checkpoint_path, data_path
DEFAULT_LNCRFM_MOTIF_CKPT = os.environ.get('LNCRFM_MOTIF_DEFAULT_CKPT', checkpoint_path())

class HumanMRNAStructureDataset(Dataset):

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
            pairs = []
            nt_len = len(full_sequence)
            for left, right in record['pairs']:
                if 0 <= left < nt_len and 0 <= right < nt_len and (left != right):
                    a, b = sorted((int(left), int(right)))
                    pairs.append((a, b))
            return {'sequence': full_sequence, 'input_ids': [item['input_ids'] for item in encoded_windows], 'attention_mask': [item['attention_mask'] for item in encoded_windows], 'special_tokens_mask': [item.get('special_tokens_mask') for item in encoded_windows], 'window_starts': [start for start, _ in spans], 'window_lengths': [end - start for start, end in spans], 'pairs': pairs, 'sample_id': record['sample_id']}
        sequence = full_sequence[:self.nt_max_length]
        nt_len = len(sequence)
        pairs = []
        for left, right in record['pairs']:
            if 0 <= left < nt_len and 0 <= right < nt_len and (left != right):
                a, b = sorted((int(left), int(right)))
                pairs.append((a, b))
        encoded = encode_sequence(sequence, self.tokenizer, self.max_length, self.model_backend)
        return {'sequence': sequence, 'input_ids': encoded['input_ids'], 'attention_mask': encoded['attention_mask'], 'special_tokens_mask': encoded.get('special_tokens_mask'), 'pairs': pairs, 'sample_id': record['sample_id']}

class StructureCollator:

    def __init__(self, tokenizer, min_loop_length: int, canonical_only: bool, allow_wobble: bool) -> None:
        self.tokenizer = tokenizer
        self.min_loop_length = min_loop_length
        self.canonical_only = canonical_only
        self.allow_wobble = allow_wobble

    def __call__(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        first_input_ids = batch[0]['input_ids']
        if isinstance(first_input_ids, list) and first_input_ids and isinstance(first_input_ids[0], list):
            return self._collate_windowed(batch)
        features = [{'input_ids': item['input_ids'], 'attention_mask': item['attention_mask'], 'special_tokens_mask': item.get('special_tokens_mask')} for item in batch]
        padded = self.tokenizer.pad(features, return_tensors='pt')
        batch_size, padded_len = padded['input_ids'].shape
        special_tokens_mask = padded.get('special_tokens_mask')
        if special_tokens_mask is None:
            special_tokens_mask = torch.zeros_like(padded['attention_mask'])
        original_nt_lens = torch.tensor([len(item['sequence']) for item in batch], dtype=torch.long)
        max_nt_len = int(original_nt_lens.max().item())
        labels = torch.zeros(batch_size, max_nt_len, max_nt_len, dtype=torch.float32)
        label_mask = torch.zeros(batch_size, max_nt_len, max_nt_len, dtype=torch.bool)
        nt_lens = torch.zeros(batch_size, dtype=torch.long)
        global_positions = torch.full((batch_size, padded_len), -1, dtype=torch.long)
        for batch_index, item in enumerate(batch):
            sequence = item['sequence']
            nt_len = len(sequence)
            token_positions = torch.nonzero(padded['attention_mask'][batch_index].bool() & ~special_tokens_mask[batch_index].bool(), as_tuple=False).squeeze(-1)
            effective_nt_len = min(nt_len, int(token_positions.numel()))
            nt_lens[batch_index] = effective_nt_len
            positive_pairs = set(item['pairs'])
            global_positions[batch_index, token_positions[:effective_nt_len]] = torch.arange(effective_nt_len, dtype=torch.long)
            for left, right in positive_pairs:
                if left < effective_nt_len and right < effective_nt_len:
                    labels[batch_index, left, right] = 1.0
                    label_mask[batch_index, left, right] = True
            for left in range(effective_nt_len):
                start = left + self.min_loop_length + 1
                if start >= effective_nt_len:
                    continue
                left_base = sequence[left]
                for right in range(start, effective_nt_len):
                    if (left, right) in positive_pairs:
                        continue
                    if self.canonical_only and (not can_form_canonical_pair(left_base, sequence[right], self.allow_wobble)):
                        continue
                    label_mask[batch_index, left, right] = True
        padded['labels'] = labels
        padded['label_mask'] = label_mask
        padded['nt_lens'] = nt_lens
        padded['global_positions'] = global_positions
        padded['sample_ids'] = [item['sample_id'] for item in batch]
        return padded

    def _collate_windowed(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        batch_size = len(batch)
        max_windows = max((len(item['input_ids']) for item in batch))
        pad_token_id = int(getattr(self.tokenizer, 'pad_token_id', 0) or 0)
        flat_features = []
        flat_window_starts = []
        flat_window_lengths = []
        for item in batch:
            num_windows = len(item['input_ids'])
            for input_ids, attention_mask, special_tokens_mask, window_start, window_length in zip(item['input_ids'], item['attention_mask'], item['special_tokens_mask'], item['window_starts'], item['window_lengths']):
                flat_features.append({'input_ids': input_ids, 'attention_mask': attention_mask, 'special_tokens_mask': special_tokens_mask})
                flat_window_starts.append(int(window_start))
                flat_window_lengths.append(int(window_length))
            for _ in range(max_windows - num_windows):
                flat_features.append({'input_ids': [pad_token_id], 'attention_mask': [0], 'special_tokens_mask': [0]})
                flat_window_starts.append(-1)
                flat_window_lengths.append(0)
        padded = self.tokenizer.pad(flat_features, return_tensors='pt')
        _, padded_len = padded['input_ids'].shape
        input_ids = padded['input_ids'].view(batch_size, max_windows, padded_len)
        attention_mask = padded['attention_mask'].view(batch_size, max_windows, padded_len)
        special_tokens_mask = padded.get('special_tokens_mask')
        if special_tokens_mask is None:
            special_tokens_mask = torch.zeros_like(padded['attention_mask'])
        special_tokens_mask = special_tokens_mask.view(batch_size, max_windows, padded_len)
        nt_lens = torch.tensor([len(item['sequence']) for item in batch], dtype=torch.long)
        max_nt_len = int(nt_lens.max().item())
        labels = torch.zeros(batch_size, max_nt_len, max_nt_len, dtype=torch.float32)
        label_mask = torch.zeros(batch_size, max_nt_len, max_nt_len, dtype=torch.bool)
        global_positions = torch.full((batch_size, max_windows, padded_len), -1, dtype=torch.long)
        window_mask = torch.zeros(batch_size, max_windows, dtype=torch.bool)
        for batch_index, item in enumerate(batch):
            sequence = item['sequence']
            nt_len = len(sequence)
            positive_pairs = set(item['pairs'])
            for left, right in positive_pairs:
                if left < max_nt_len and right < max_nt_len:
                    labels[batch_index, left, right] = 1.0
                    label_mask[batch_index, left, right] = True
            for left in range(nt_len):
                start = left + self.min_loop_length + 1
                if start >= nt_len:
                    continue
                left_base = sequence[left]
                for right in range(start, nt_len):
                    if (left, right) in positive_pairs:
                        continue
                    if self.canonical_only and (not can_form_canonical_pair(left_base, sequence[right], self.allow_wobble)):
                        continue
                    label_mask[batch_index, left, right] = True
            for window_index, (window_start, window_length) in enumerate(zip(item['window_starts'], item['window_lengths'])):
                window_mask[batch_index, window_index] = True
                if window_length <= 0:
                    continue
                token_positions = torch.nonzero(attention_mask[batch_index, window_index].bool() & ~special_tokens_mask[batch_index, window_index].bool(), as_tuple=False).squeeze(-1)
                effective_window_length = min(int(window_length), int(token_positions.numel()))
                global_positions[batch_index, window_index, token_positions[:effective_window_length]] = torch.arange(int(window_start), int(window_start) + effective_window_length, dtype=torch.long)
        return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': labels, 'label_mask': label_mask, 'nt_lens': nt_lens, 'global_positions': global_positions, 'window_mask': window_mask, 'sample_ids': [item['sample_id'] for item in batch]}

class StructureContactModel(nn.Module):

    def __init__(self, encoder: nn.Module, hidden_size: int, pair_hidden_size: int, dropout: float, *, finetune_scheme: str='baseline', scheme_encoder: nn.Module | None=None) -> None:
        super().__init__()
        self.encoder = encoder
        self.finetune_scheme = finetune_scheme
        self.scheme_encoder = scheme_encoder
        self.norm = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.query = nn.Linear(hidden_size, pair_hidden_size)
        self.key = nn.Linear(hidden_size, pair_hidden_size)
        self.unary = nn.Linear(hidden_size, 1)
        self.scale = math.sqrt(pair_hidden_size)
        self.pairwise_head = None

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        if self.scheme_encoder is None:
            if input_ids.dim() == 3:
                batch_size, num_windows, seq_len = input_ids.shape
                flat_input_ids = input_ids.reshape(batch_size * num_windows, seq_len)
                flat_attention_mask = attention_mask.reshape(batch_size * num_windows, seq_len)
                token_embeddings = self.encoder(input_ids=flat_input_ids, attention_mask=flat_attention_mask)
                token_embeddings = self.dropout(self.norm(token_embeddings))
                query = self.query(token_embeddings)
                key = self.key(token_embeddings)
                logits = torch.matmul(query, key.transpose(1, 2)) / self.scale
                unary_bias = self.unary(token_embeddings).squeeze(-1)
                logits = logits + unary_bias.unsqueeze(1) + unary_bias.unsqueeze(2)
                logits = 0.5 * (logits + logits.transpose(1, 2))
                return logits.view(batch_size, num_windows, seq_len, seq_len)
            token_embeddings = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
            token_embeddings = self.dropout(self.norm(token_embeddings))
            query = self.query(token_embeddings)
            key = self.key(token_embeddings)
            logits = torch.matmul(query, key.transpose(1, 2)) / self.scale
            unary_bias = self.unary(token_embeddings).squeeze(-1)
            logits = logits + unary_bias.unsqueeze(1) + unary_bias.unsqueeze(2)
            return 0.5 * (logits + logits.transpose(1, 2))
        token_embeddings, pairwise_features = self.scheme_encoder(self.encoder, input_ids, attention_mask)
        if pairwise_features is not None:
            if pairwise_features.dim() == 5:
                batch_size, num_windows, seq_len, _, pair_hidden_size = pairwise_features.shape
                logits = self.pairwise_head(pairwise_features.view(batch_size * num_windows, seq_len, seq_len, pair_hidden_size)).squeeze(-1)
                logits = 0.5 * (logits + logits.transpose(1, 2))
                return logits.view(batch_size, num_windows, seq_len, seq_len)
            logits = self.pairwise_head(pairwise_features).squeeze(-1)
            return 0.5 * (logits + logits.transpose(1, 2))
        assert token_embeddings is not None
        if token_embeddings.dim() == 4:
            batch_size, num_windows, seq_len, hidden_size = token_embeddings.shape
            token_embeddings = token_embeddings.view(batch_size * num_windows, seq_len, hidden_size)
            token_embeddings = self.dropout(self.norm(token_embeddings))
            query = self.query(token_embeddings)
            key = self.key(token_embeddings)
            logits = torch.matmul(query, key.transpose(1, 2)) / self.scale
            unary_bias = self.unary(token_embeddings).squeeze(-1)
            logits = logits + unary_bias.unsqueeze(1) + unary_bias.unsqueeze(2)
            logits = 0.5 * (logits + logits.transpose(1, 2))
            return logits.view(batch_size, num_windows, seq_len, seq_len)
        token_embeddings = self.dropout(self.norm(token_embeddings))
        query = self.query(token_embeddings)
        key = self.key(token_embeddings)
        logits = torch.matmul(query, key.transpose(1, 2)) / self.scale
        unary_bias = self.unary(token_embeddings).squeeze(-1)
        logits = logits + unary_bias.unsqueeze(1) + unary_bias.unsqueeze(2)
        return 0.5 * (logits + logits.transpose(1, 2))

def load_split_records(data_dir: str) -> Dict[str, List[Dict]]:
    return load_task_records(data_dir, target='pairs')

def compute_structure_pos_weight(records: Sequence[Dict], max_length: int, min_loop_length: int, canonical_only: bool, allow_wobble: bool, max_pos_weight: float) -> Tuple[float, int, int]:
    nt_max_length = max_length - 2
    total_positive = 0
    total_candidate = 0
    for record in records:
        sequence = sanitize_sequence(record['sequence'])[:nt_max_length]
        nt_len = len(sequence)
        positive_pairs = set()
        for left, right in record['pairs']:
            if 0 <= left < nt_len and 0 <= right < nt_len and (left != right):
                positive_pairs.add(tuple(sorted((int(left), int(right)))))
        total_positive += len(positive_pairs)
        total_candidate += len(positive_pairs)
        for left in range(nt_len):
            start = left + min_loop_length + 1
            if start >= nt_len:
                continue
            left_base = sequence[left]
            for right in range(start, nt_len):
                if (left, right) in positive_pairs:
                    continue
                if canonical_only and (not can_form_canonical_pair(left_base, sequence[right], allow_wobble)):
                    continue
                total_candidate += 1
    total_negative = max(total_candidate - total_positive, 0)
    if total_positive == 0:
        return (1.0, total_positive, total_negative)
    raw_pos_weight = float(total_negative) / float(total_positive)
    return (min(raw_pos_weight, max_pos_weight), total_positive, total_negative)

def upsample_logits_to_label_mask(logits: torch.Tensor, label_mask: torch.Tensor) -> torch.Tensor:
    if logits.shape == label_mask.shape:
        return logits
    _, logit_h, logit_w = logits.shape
    _, mask_h, mask_w = label_mask.shape
    kmer_h = mask_h // logit_h
    kmer_w = mask_w // logit_w
    if kmer_h >= 1 and kmer_w >= 1 and (mask_h % logit_h == 0) and (mask_w % logit_w == 0):
        return logits.repeat_interleave(kmer_h, dim=1).repeat_interleave(kmer_w, dim=2)
    return F.interpolate(logits.unsqueeze(1), size=(mask_h, mask_w), mode='bicubic', align_corners=False).squeeze(1)

def compute_loss(logits: torch.Tensor, labels: torch.Tensor, label_mask: torch.Tensor, criterion: nn.Module) -> torch.Tensor:
    masked_logits = logits[label_mask]
    masked_labels = labels[label_mask]
    if masked_logits.numel() == 0:
        return logits.sum() * 0.0
    return criterion(masked_logits, masked_labels)

def aggregate_structure_logits(logits: torch.Tensor, global_positions: torch.Tensor, nt_lens: torch.Tensor) -> torch.Tensor:
    if logits.dim() == 3:
        logits = logits.unsqueeze(1)
        global_positions = global_positions.unsqueeze(1)
    batch_size, _, _, _ = logits.shape
    max_nt_len = int(nt_lens.max().item())
    aggregated = logits.new_zeros((batch_size, max_nt_len, max_nt_len))
    counts = logits.new_zeros((batch_size, max_nt_len, max_nt_len))
    for batch_index in range(batch_size):
        for window_index in range(logits.size(1)):
            window_positions = global_positions[batch_index, window_index]
            valid = window_positions >= 0
            if not valid.any():
                continue
            nt_indices = window_positions[valid]
            window_logits = logits[batch_index, window_index][valid][:, valid]
            row_index = nt_indices[:, None].expand(-1, nt_indices.numel())
            col_index = nt_indices[None, :].expand(nt_indices.numel(), -1)
            aggregated[batch_index].index_put_((row_index, col_index), window_logits, accumulate=True)
            counts[batch_index].index_put_((row_index, col_index), torch.ones_like(window_logits), accumulate=True)
    return aggregated / counts.clamp_min(1.0)

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
def evaluate(model: nn.Module, data_loader: DataLoader, device: torch.device, criterion: nn.Module, thresholds: Sequence[float]) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    total_pairs = 0
    total_positive = 0
    total_predicted_prob = 0.0
    stats = {float(threshold): {'tp': 0.0, 'fp': 0.0, 'fn': 0.0} for threshold in thresholds}
    for batch_idx, batch in enumerate(data_loader, start=1):
        batch = move_batch_to_device(batch, device)
        logits = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
        message = describe_nonfinite('eval_logits', logits, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
        if message is not None:
            raise RuntimeError(message)
        aggregated_logits = aggregate_structure_logits(logits, batch['global_positions'], batch['nt_lens'])
        aggregated_logits = upsample_logits_to_label_mask(aggregated_logits, batch['label_mask'])
        masked_logits = aggregated_logits[batch['label_mask']]
        masked_labels = batch['labels'][batch['label_mask']]
        if masked_logits.numel() == 0:
            continue
        loss = criterion(masked_logits, masked_labels)
        message = describe_nonfinite('eval_loss', loss, batch_idx=batch_idx, sample_ids=batch['sample_ids'])
        if message is not None:
            raise RuntimeError(message)
        total_loss += loss.item() * masked_logits.numel()
        total_pairs += masked_logits.numel()
        probs = torch.sigmoid(masked_logits).detach().cpu()
        targets = masked_labels.detach().cpu() > 0.5
        total_positive += int(targets.sum().item())
        total_predicted_prob += float(probs.sum().item())
        for threshold in thresholds:
            preds = probs >= float(threshold)
            tp = float(((preds == 1) & (targets == 1)).sum().item())
            fp = float(((preds == 1) & (targets == 0)).sum().item())
            fn = float(((preds == 0) & (targets == 1)).sum().item())
            stats[float(threshold)]['tp'] += tp
            stats[float(threshold)]['fp'] += fp
            stats[float(threshold)]['fn'] += fn
    if total_pairs == 0:
        return {'loss': 0.0, 'threshold': float(thresholds[0]) if thresholds else 0.5, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0, 'positive_rate': 0.0, 'mean_probability': 0.0}
    best_threshold = float(thresholds[0])
    best_metrics = (0.0, 0.0, 0.0)
    best_f1 = -1.0
    for threshold in thresholds:
        tp = stats[float(threshold)]['tp']
        fp = stats[float(threshold)]['fp']
        fn = stats[float(threshold)]['fn']
        precision, recall, f1 = precision_recall_f1(tp, fp, fn)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)
            best_metrics = (precision, recall, f1)
    return {'loss': total_loss / total_pairs, 'threshold': best_threshold, 'precision': best_metrics[0], 'recall': best_metrics[1], 'f1': best_metrics[2], 'positive_rate': float(total_positive) / float(total_pairs), 'mean_probability': total_predicted_prob / float(total_pairs)}

def train(args: argparse.Namespace) -> None:
    set_seed(args.seed)
    device = torch.device(args.device if args.device else 'cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer, effective_max_length = build_tokenizer(args)
    split_records = load_split_records(args.data_dir)
    print({'split_sizes': {name: len(rows) for name, rows in split_records.items()}}, flush=True)
    train_dataset = HumanMRNAStructureDataset(split_records['train'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    val_dataset = HumanMRNAStructureDataset(split_records['val'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    test_dataset = HumanMRNAStructureDataset(split_records['test'], tokenizer, effective_max_length, args.model_backend, args.long_seq_strategy, args.window_overlap)
    collator = StructureCollator(tokenizer=tokenizer, min_loop_length=args.min_loop_length, canonical_only=args.canonical_only, allow_wobble=args.allow_wobble)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collator)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    encoder, hidden_size = build_encoder(args, tokenizer, device)
    scheme_encoder = build_structure_scheme_encoder(hidden_size, args.pair_hidden_size, args)
    model = StructureContactModel(encoder, hidden_size, args.pair_hidden_size, args.dropout, finetune_scheme=args.finetune_scheme, scheme_encoder=scheme_encoder).to(device)
    if args.pos_weight > 0:
        pos_weight_value = args.pos_weight
        total_positive = -1
        total_negative = -1
    else:
        pos_weight_value, total_positive, total_negative = compute_structure_pos_weight(split_records['train'], effective_max_length, args.min_loop_length, args.canonical_only, args.allow_wobble, args.max_pos_weight)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight_value, device=device))
    if args.freeze_encoder:
        for param in model.encoder.parameters():
            param.requires_grad = False
        trainable = count_initialized_parameters(model, trainable_only=True)
        total = count_initialized_parameters(model)
        print(f'[Freeze] encoder frozen, trainable: {trainable:,}/{total:,} ({100 * trainable / total:.1f}%)', flush=True)
    optimizer = torch.optim.AdamW([param for param in model.parameters() if param.requires_grad], lr=args.lr if args.warmup_steps <= 0 else 0.0, weight_decay=args.weight_decay)
    warmup_steps = args.warmup_steps
    global_step = 0
    thresholds = build_default_thresholds() if not args.thresholds else [float(value) for value in args.thresholds.split(',')]
    os.makedirs(args.output_dir, exist_ok=True)
    best_metric = -math.inf
    epochs_without_improvement = 0
    best_path = os.path.join(args.output_dir, 'best_model.pt')
    history = []
    print({'task': 'human_mRNA_structure_specialized', 'model_backend': args.model_backend, 'num_train': len(train_dataset), 'num_val': len(val_dataset), 'num_test': len(test_dataset), 'freeze_base': args.freeze_base, 'from_pretrained': args.from_pretrained, 'effective_max_length': effective_max_length, 'long_seq_strategy': args.long_seq_strategy, 'window_overlap': args.window_overlap, 'finetune_scheme': args.finetune_scheme, 'min_loop_length': args.min_loop_length, 'canonical_only': args.canonical_only, 'allow_wobble': args.allow_wobble, 'pos_weight': pos_weight_value, 'train_positive_pairs': total_positive, 'train_negative_pairs': total_negative}, flush=True)
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
            aggregated_logits = aggregate_structure_logits(logits, batch['global_positions'], batch['nt_lens'])
            aggregated_logits = upsample_logits_to_label_mask(aggregated_logits, batch['label_mask'])
            loss = compute_loss(aggregated_logits, batch['labels'], batch['label_mask'], criterion)
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
        val_metrics = evaluate(model, val_loader, device, criterion, thresholds)
        epoch_record = {'epoch': epoch, 'train_loss': train_loss, 'skipped_batches': skipped_batches, **{f'val_{key}': value for key, value in val_metrics.items()}}
        if args.eval_test_each_epoch:
            test_metrics = evaluate(model, test_loader, device, criterion, [val_metrics['threshold']])
            epoch_record.update({f'test_{key}': value for key, value in test_metrics.items()})
        history.append(epoch_record)
        print(epoch_record, flush=True)
        if args.save_every_epochs > 0 and epoch % args.save_every_epochs == 0:
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'epoch': epoch, 'best_threshold': val_metrics['threshold']}, os.path.join(args.output_dir, f'checkpoint_epoch_{epoch}.pt'))
        if val_metrics['f1'] > best_metric + args.early_stop_min_delta:
            best_metric = val_metrics['f1']
            epochs_without_improvement = 0
            torch.save({'model_state_dict': model.state_dict(), 'args': vars(args), 'best_val_f1': best_metric, 'best_threshold': val_metrics['threshold'], 'pos_weight': pos_weight_value}, best_path)
        else:
            epochs_without_improvement += 1
        if args.early_stop_patience > 0 and epoch >= args.early_stop_min_epochs and (epochs_without_improvement >= args.early_stop_patience):
            print({'early_stop': True, 'epoch': epoch, 'best_val_f1': best_metric, 'epochs_without_improvement': epochs_without_improvement, 'early_stop_patience': args.early_stop_patience, 'early_stop_min_epochs': args.early_stop_min_epochs, 'early_stop_min_delta': args.early_stop_min_delta}, flush=True)
            break
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    final_test = evaluate(model, test_loader, device, criterion, [float(checkpoint['best_threshold'])])
    print({'best_val_f1': best_metric, 'best_threshold': float(checkpoint['best_threshold']), **{f'final_test_{key}': value for key, value in final_test.items()}}, flush=True)
    with open(os.path.join(args.output_dir, 'history.json'), 'w') as fout:
        json.dump(history, fout, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Specialized finetuning for the human mRNA structure task.')
    parser.add_argument('--model_backend', choices=['lncrfm'], default='lncrfm')
    parser.add_argument('--from_pretrained', type=str, default=checkpoint_path())
    parser.add_argument('--data_dir', '--data_file', type=str, default=data_path('mRNA-Structure.parquet'))
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_length', type=int, default=2050)
    parser.add_argument('--dim', type=int, default=768)
    parser.add_argument('--layer', type=int, default=12)
    parser.add_argument('--pair_hidden_size', type=int, default=256)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--epoch', type=int, default=50)
    parser.add_argument('--lr', type=float, default=5e-05)
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
    parser.add_argument('--min_loop_length', type=int, default=3)
    parser.add_argument('--canonical_only', dest='canonical_only', action='store_true')
    parser.add_argument('--no_canonical_only', dest='canonical_only', action='store_false')
    parser.set_defaults(canonical_only=True)
    parser.add_argument('--allow_wobble', dest='allow_wobble', action='store_true')
    parser.add_argument('--no_allow_wobble', dest='allow_wobble', action='store_false')
    parser.set_defaults(allow_wobble=True)
    parser.add_argument('--pos_weight', type=float, default=0.0)
    parser.add_argument('--max_pos_weight', type=float, default=200.0)
    parser.add_argument('--thresholds', type=str, default='')
    parser.set_defaults(eval_test_each_epoch=True)
    args = parser.parse_args()
    args.grad_accum_steps = max(1, args.grad_accum_steps)
    if args.model_backend == 'lncrfm' and args.from_pretrained == checkpoint_path():
        args.from_pretrained = DEFAULT_LNCRFM_MOTIF_CKPT
    return args
if __name__ == '__main__':
    train(parse_args())
