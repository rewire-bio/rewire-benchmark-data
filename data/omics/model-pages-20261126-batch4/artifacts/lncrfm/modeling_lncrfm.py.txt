from pathlib import Path
import torch
import torch.nn as nn
from safetensors.torch import load_file as safe_load
from transformers.modeling_outputs import MaskedLMOutput
from .backbone import LncRFMConfig, LncRFMBackbone
DEFAULT_SSM_CFG = {'d_state': 64, 'd_conv': 7, 'expand': 2, 'headdim': 64, 'ngroups': 1, 'learnable_init_states': False, 'bias': False, 'conv_bias': True, 'chunk_size': 256, 'use_mem_eff_path': False}

class ConvMotifStem(nn.Module):

    def __init__(self, d_model, kernel_sizes=(3, 7), dropout=0.1, use_gate=False, gate_init=1.0):
        super().__init__()
        if not kernel_sizes:
            raise ValueError('kernel_sizes must not be empty')
        self.use_gate = use_gate
        self.branches = nn.ModuleList([nn.Sequential(nn.Conv1d(d_model, d_model, kernel_size=k, padding=k // 2, groups=d_model), nn.Conv1d(d_model, d_model, kernel_size=1), nn.GELU()) for k in kernel_sizes])
        self.proj = nn.Linear(d_model * len(kernel_sizes), d_model)
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        self.motif_gate = nn.Parameter(torch.tensor(float(gate_init)))

    def forward(self, hidden_states, attention_mask=None):
        mask = None
        if attention_mask is not None:
            mask = attention_mask.to(device=hidden_states.device, dtype=hidden_states.dtype).unsqueeze(-1)
            hidden_states = hidden_states * mask
        x = hidden_states.transpose(1, 2)
        feats = [branch(x).transpose(1, 2) for branch in self.branches]
        motif_states = torch.cat(feats, dim=-1)
        motif_states = self.proj(motif_states)
        if mask is not None:
            motif_states = motif_states * mask
        motif_states = self.dropout(motif_states)
        motif_states = motif_states * self.motif_gate.to(dtype=motif_states.dtype)
        fused = self.norm(hidden_states + motif_states)
        if mask is not None:
            fused = fused * mask
        return fused

class SimpleMLMHead(nn.Module):

    def __init__(self, d_model, vocab_size):
        super().__init__()
        self.dense = nn.Linear(d_model, d_model)
        self.act = nn.GELU()
        self.layer_norm = nn.LayerNorm(d_model)
        self.decoder = nn.Linear(d_model, vocab_size)

    def forward(self, hidden_states):
        hidden_states = hidden_states.to(self.dense.weight.dtype)
        x = self.dense(hidden_states)
        x = self.act(x)
        x = self.layer_norm(x)
        x = self.decoder(x)
        return x

    @property
    def device(self):
        return next(self.parameters()).device

class LncRFMForMaskedLM(nn.Module):

    def __init__(self, config: LncRFMConfig, from_pretrained=None, device=None, dtype=torch.float32, use_motif_stem=True, motif_kernel_sizes=(3, 7), motif_dropout=0.1, use_motif_gate=True, motif_gate_init=0.0):
        super().__init__()
        self.config = config
        self.vocab_size = config.vocab_size
        self.backbone = LncRFMBackbone(config=self.config, device=device, dtype=dtype)
        self.use_motif_stem = use_motif_stem
        self.motif_stem = None
        if self.use_motif_stem:
            backbone_param = next(self.backbone.parameters())
            self.motif_stem = ConvMotifStem(d_model=config.d_model, kernel_sizes=tuple(motif_kernel_sizes), dropout=motif_dropout, use_gate=use_motif_gate, gate_init=motif_gate_init).to(device=backbone_param.device, dtype=backbone_param.dtype)
        self.lm_head = SimpleMLMHead(config.d_model, config.vocab_size).to(self.backbone.device)
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
        if from_pretrained:
            model_file = Path(from_pretrained) / 'model.safetensors'
            state_dict = safe_load(str(model_file), device=str(device or 'cpu'))
            self.load_state_dict(state_dict, strict=True)

    def forward(self, input_ids, attention_mask=None, labels=None, output_hidden_states=True, connects=None, **kwargs):
        B, L = input_ids.shape
        device = input_ids.device
        assert L <= self.config.max_position_embeddings, f'Input length {L} exceeds max_position_embeddings {self.config.max_position_embeddings}'
        structure_mask = None
        if connects is not None:
            structure_mask = (connects != 0).float()
        position_ids = torch.arange(L, device=device).unsqueeze(0).expand(B, L)
        token_embeds = self.backbone.embedding(input_ids=input_ids, position_ids=position_ids)
        token_embeds = self.motif_stem(token_embeds, attention_mask=attention_mask)
        backbone_outputs = self.backbone(inputs_embeds=token_embeds, attention_mask=attention_mask, position_ids=position_ids, inference_params=None, structure_mask=structure_mask)
        sequence_output = backbone_outputs[0]
        hidden_states = backbone_outputs[2] if len(backbone_outputs) > 2 else None
        attentions = backbone_outputs[3] if len(backbone_outputs) > 3 else None
        if attention_mask is not None:
            sequence_output = sequence_output * attention_mask.to(dtype=sequence_output.dtype).unsqueeze(-1)
        prediction_scores = self.lm_head(sequence_output)
        mlm_loss = None
        loss = None
        if labels is not None:
            mlm_loss = self.loss_fn(prediction_scores.view(-1, self.config.vocab_size), labels.view(-1))
            loss = mlm_loss
        return MaskedLMOutput(loss=loss, logits=prediction_scores, hidden_states=hidden_states if output_hidden_states else None, attentions=attentions)

    @property
    def device(self):
        return next(self.parameters()).device

def get_lncrfm(dim=768, layer=12, vocab_size=None, attn_layer_idx=None, attn_cfg=None, from_pretrained=None, max_length=2050, ssm_cfg=None, rms_norm=True, fused_add_norm=True, residual_in_fp32=True, tokenizer=None, device=None, dtype=torch.float32, use_motif_stem=True, motif_kernel_sizes=(3, 7), motif_dropout=0.1, use_motif_gate=True, motif_gate_init=0.0, position_embedding_type='none', use_bidirectional_mixer=True, pair_aware_fusion=True, bidirectional_strategy='mean', bidirectional_weight_tie=False):
    if not (use_motif_stem and use_motif_gate and use_bidirectional_mixer and pair_aware_fusion):
        raise ValueError('LncRFM requires its motif stem, motif gate and pair-aware bidirectional mixer')
    if position_embedding_type != 'none' or bidirectional_strategy != 'mean' or bidirectional_weight_tie:
        raise ValueError('Unsupported LncRFM architecture configuration')
    if attn_layer_idx is None:
        attn_layer_idx = [5, 11]
    if attn_cfg is None:
        attn_cfg = {'num_heads': 12, 'dropout': 0.0, 'use_masked_attention': True}
    if tokenizer is None:
        from ..data.tokenizer import get_mlm_tokenizer
        tokenizer = get_mlm_tokenizer(max_length=max_length)
    if vocab_size is None:
        assert tokenizer is not None
        vocab_size = len(tokenizer)
    config = LncRFMConfig(d_model=dim, n_layer=layer, vocab_size=vocab_size, max_position_embeddings=max_length, ssm_cfg=ssm_cfg or dict(DEFAULT_SSM_CFG), rms_norm=rms_norm, fused_add_norm=fused_add_norm, residual_in_fp32=residual_in_fp32, attn_layer_idx=attn_layer_idx, attn_cfg=attn_cfg, position_embedding_type=position_embedding_type, use_bidirectional_mixer=use_bidirectional_mixer, pair_aware_fusion=pair_aware_fusion, bidirectional_strategy=bidirectional_strategy, bidirectional_weight_tie=bidirectional_weight_tie)
    return LncRFMForMaskedLM(config=config, from_pretrained=from_pretrained, device=device, dtype=dtype, use_motif_stem=use_motif_stem, motif_kernel_sizes=motif_kernel_sizes, motif_dropout=motif_dropout, use_motif_gate=use_motif_gate, motif_gate_init=motif_gate_init)
