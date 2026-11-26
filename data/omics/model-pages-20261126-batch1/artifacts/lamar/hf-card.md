---
license: mit
tags:
- biology
---
# LAMAR
LAMAR is a Foundation **La**nguage **M**odel for RN**A** **R**egulation, which achieves better or comparable performance compared to baseline models in various 
RNA regulation tasks, helping to decipher the rules of RNA regulation. LAMAR was developed by Rnasys Lab and Bio-Med Big Data Center, Shanghai Institute of Nutrition 
and Health (SINH), Chinese Academy of Sciences (CAS).      

This repository contains pretrained and fine-tuned weights for RNA foundation language model **LAMAR**.  

![image](./ReadMe/overview.png)

## Scripts

The scripts for pretraining and fine-tuning LAMAR are deposited in Github (https://github.com/zhw-e8/LAMAR).  

## Model weights

LAMAR is pretrained on approximately 15 million sequences from both genome and transcriptome of 225 mammals and 1569 viruses, and further fine-tuned with labeled 
datasets for various tasks. Considering the sequence length of genes/transcripts and the available computational resources, we pretrain two models with the contextual 
length of up to 2048 and 4096 tokens, named LAMAR-2k and LAMAR-4k.
* mammalian80D_2048len1mer1sw_80M: Pretrained weights of LAMAR-2k  
* mammalian80D_4096len1mer1sw_80M: Pretrained weights of LAMAR-4k

LAMAR is fine-tuned to predict the splice site, mRNA translation efficiency, mRNA degradation rate and internal ribosome entry site (IRES).
* SpliceSitePred: Weight of fine-tuned LAMAR predict splice site of pre-mRNA  
* UTR5TEPred: Weight of fine-tuned LAMAR predict translation efficiency of mRNA based on 5' UTR  
* UTR3DegPred: Weight of fine-tuned LAMAR predict degradation rate of mRNA based on 3' UTR  
* IRESPred: Weight of fine-tuned LAMAR predicting internal ribosome entry site (IRES)  

## Citation
https://www.biorxiv.org/content/10.1101/2024.10.12.617732v2
 