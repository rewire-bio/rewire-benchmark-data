from pathlib import Path
import pyarrow.parquet as pq
SPLITS = {'train': 'train', 'validation': 'val', 'val': 'val', 'test': 'test'}

def load_lncbench(path, sequence_columns=('sequence',)):
    source = pq.ParquetFile(path)
    columns = [*sequence_columns, 'label', 'split']
    missing = set(columns) - set(source.schema_arrow.names)
    if missing:
        raise ValueError(f'Missing Parquet columns: {sorted(missing)}')
    partitions = {'train': [], 'val': [], 'test': []}
    index = 0
    for batch in source.iter_batches(columns=columns):
        for row in batch.to_pylist():
            split = SPLITS.get(row['split'])
            if split is None:
                raise ValueError(f"Unknown split at row {index}: {row['split']!r}")
            if any((not isinstance(row[column], str) or not row[column] for column in sequence_columns)) or row['label'] is None:
                raise ValueError(f'Missing sequence or label at row {index}')
            partitions[split].append({**row, 'split': split, 'sample_id': f'{Path(path).stem}:{index}'})
            index += 1
    if index == 0:
        raise ValueError('Empty Parquet dataset')
    return partitions

def load_task_records(path, target='label', site=None):
    if site is not None and site not in {'donor', 'acceptor'}:
        raise ValueError('Splice site must be donor or acceptor')
    partitions = load_lncbench(path)
    for split, rows in partitions.items():
        records = []
        for row in rows:
            value = row['label']
            if site is not None:
                if not isinstance(value, dict) or value.get('site') not in {'donor', 'acceptor'}:
                    raise ValueError('Splice labels must contain site and value')
                if value['site'] != site:
                    continue
                value = value['value']
            record = dict(row)
            record['label'] = value
            if target == 'pairs':
                record['pairs'] = [tuple(pair) for pair in value]
            elif target != 'label':
                record[target] = value
            if target == 'label_id' or site is not None:
                if value not in (0, 1):
                    raise ValueError('Binary labels must be 0 or 1')
                record['label_id'] = int(value)
            records.append(record)
        partitions[split] = records
    return partitions

def load_localization_records(path):
    partitions = load_lncbench(path)
    labels = sorted({label.strip() for rows in partitions.values() for row in rows for label in row['label'].split(';') if label.strip()})
    if not labels:
        raise ValueError('Empty localization label vocabulary')
    label_to_id = {label: index for index, label in enumerate(labels)}
    for rows in partitions.values():
        for row in rows:
            target = [0.0] * len(labels)
            for label in row['label'].split(';'):
                if label.strip():
                    target[label_to_id[label.strip()]] = 1.0
            row['label'] = target
    return (partitions, dict(enumerate(labels)))
