from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import torch
from safetensors.torch import load_file
from src.lncrfm import get_lncrfm, get_tokenizer

def check_loading(checkpoint: Path, device):
    options = json.loads((checkpoint / 'model_config.json').read_text())['factory_kwargs']
    tokenizer = get_tokenizer(tokenizer_file=str(checkpoint / 'tokenizer.json'), max_length=options['max_length'])
    model = get_lncrfm(**options, tokenizer=tokenizer, from_pretrained=str(checkpoint), device=device, dtype=torch.float32)
    weights = load_file(str(checkpoint / 'model.safetensors'), device='cpu')
    state = model.state_dict()
    if set(state) != set(weights) or not all((torch.equal(state[name].cpu(), value) for name, value in weights.items())):
        raise AssertionError('Loaded weights differ from checkpoint tensors')
    if any((parameter.device.type != device for parameter in model.parameters())):
        raise AssertionError('Model parameters are on different devices')
    print(f'PASS: architecture and {len(weights)} checkpoint tensors match')
    return (model, tokenizer)

def check_forward(model, tokenizer, device):
    model = model.to(device).eval()
    inputs = tokenizer('[CLS] A U G [MASK] C [SEP]', return_tensors='pt').to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
    if logits.shape != (*inputs.input_ids.shape, len(tokenizer)) or not torch.isfinite(logits).all():
        raise AssertionError('Invalid model output')
    print('PASS: pretrained-model forward pass')

def check_training(model, tokenizer, device):
    torch.manual_seed(42)
    model = model.to(device).train()
    inputs = tokenizer(['[CLS] A U [MASK] C G [SEP]', '[CLS] C G [MASK] A U [SEP]'], padding=True, return_tensors='pt').to(device)
    labels = torch.full_like(inputs.input_ids, -100)
    labels[inputs.input_ids == tokenizer.mask_token_id] = torch.tensor(tokenizer.convert_tokens_to_ids(['G', 'C']), device=device)
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-06)
    before = model.lm_head.decoder.weight.detach().clone()
    loss = model(**inputs, labels=labels, connects=torch.zeros_like(inputs.input_ids)).loss
    if not torch.isfinite(loss):
        raise AssertionError('Non-finite training loss')
    loss.backward()
    if not all((torch.isfinite(parameter.grad).all() for parameter in model.parameters() if parameter.grad is not None)):
        raise AssertionError('Non-finite training gradients')
    optimizer.step()
    if torch.equal(before, model.lm_head.decoder.weight):
        raise AssertionError('Optimizer step did not update model parameters')
    print(f'PASS: pretrained-model training step on synthetic RNA, loss={loss.item():.4f}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=Path, default=Path(os.getenv('LNCRFM_CHECKPOINT', Path(__file__).resolve().parent / 'checkpoints/lncrfm_pretrained')))
    parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    parser.add_argument('--train-step', action='store_true')
    args = parser.parse_args()
    if args.train_step and args.device != 'cuda':
        parser.error('--train-step requires --device cuda')
    if args.device == 'cuda' and (not torch.cuda.is_available()):
        parser.error('CUDA is required for forward and training checks')
    model, tokenizer = check_loading(args.checkpoint, args.device)
    if args.device == 'cuda':
        check_forward(model, tokenizer, args.device)
    if args.train_step:
        check_training(model, tokenizer, args.device)
if __name__ == '__main__':
    main()
