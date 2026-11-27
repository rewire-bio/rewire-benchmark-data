# Hugging Face modelling code builds a plain CTRL model rather than the LOL-EVE architecture

Raise at: https://huggingface.co/Marks-lab/LOL-EVE/discussions  
Register entry: `lead-source-lol-eve-hf-wrapper-not-the-model`

The README (debbiemarkslab/LOL-EVE, commit deed3bd9e1203f5cdd7051105628360213eba5a2) describes the model as using protein context:

> **Protein context**: Uses pre-trained ESM embeddings for gene-specific understanding

and loads it with `AutoModelForCausalLM.from_pretrained('Marks-lab/LOL-EVE', trust_remote_code=True)`. The remote code this runs, `modeling_loleve.py` at Hugging Face revision 397bbb87341c7afa569dd3139217fdbd10480d36, builds its model like this:

> `# Initialize a simple transformer model for demonstration # In practice, this would load the actual trained LOL-EVE model from transformers import CTRLConfig, CTRLLMHeadModel`

The file constructs a `CTRLLMHeadModel` and does not refer to ESM embeddings. Its config class stores `position_embedding_type="adaptive"`, but that value is not passed to the CTRL model it builds.

Does loading through Hugging Face reproduce the scores reported in the paper, or is the full model only available through the GitHub code? If the wrapper is a placeholder, a note on the card would help users choose the right route.

This was found while compiling an independent database of benchmark results: <record page>
