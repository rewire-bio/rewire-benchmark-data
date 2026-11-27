# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:19:49 2025

@author: blivesey
"""

# Script to reproduce the data structures needed to plot Figures 1 and 2.
# The files required are at: 10.6084/m9.figshare.28295198 or bundled with this script.

import re, os
import pandas as pd
import numpy as np
from tqdm import tqdm as tq
from scipy.stats import spearmanr

# Folder where the DMS and VEP prediction files are stored
DMS_dir = '/path/to/prediction/files/'
# Path to the file containing VEP (re)naming rules.
rename_path = 'rename.csv'
# Path to the file with score inversion rules.
invert_path = 'invert.xlsx'
# Path the the DMS summary file
DMS_summary_path = 'dms_summary.csv'
# Clinvar variants file path
clinvar_path = 'clinvar_variants.csv'
# gnomAD variants file path
gnomad_path = 'gnomad_variants.csv'

# All DMS datasets to be used
final_DMS_list = ['P07550','P45381','P0DP23','Q9BXL7','P42574','P55210','P35520',
'P11712','P30793','P35557','P31150','P08397','P04035','P01112','P01116','Q5SW96',
'P28482','P43246','P42898','Q9NV35','P26367','Q14432','P37231','O15297','O60260',
'P60484','P05121','Q9UQ13','P37840','P12931','P63165','P04637','Q9H3S4','P51580',
'P63279','Q9BQB6']

# List of VEPs to exclude from the calculations
exclude_VEPs = ['MutationTaster','COSMIS','MOIpred_dominant','MOIpred_recesive','Maverick_dominant',
                'Maverick_recesive','NetDiseaseSNP','ESM-IF1','MIF-ST','ProteinMPNN','PonPS','PAPI','S3D-PROF',
               'meta','Unnamed: 79','LINSIGHT']

# list of population-free VEPs
n_pop = ['MSA_Transformer','Wavenet','RITA','Unirep_evotune','GEMME','TranceptEVE','ProGen2','Tranception',
               'ESM-1b','DeMaSk','sequence_unet','CPT-1','mutationTCN','ESM-1v','EVE','EVmutation_independent',
               'EVmutation_epistatic','phastCons','phyloP','fitCons','LRT','SIFT4G','Envision','SIFT','DeepSequence',
               'SiPhy','GERP++','BLOSUM62','Grantham','PROVEAN','meta','CARP','ProtGPT2','ESM2','SaProt',
               'ProtGPT2','MutationAssessor','PANTHER','ESCOTT','iGEMME','PHACT','ProGen2']

# list of clinical-trained VEPs
pop = ['MutScore','VESPA','SNPred','COSMIS','Rhapsody','MISTIC','CAPICE',
             'InMeRF','MOIpred_benign','gMVP','DeepSAV','VESPAl','SNPs&GO','PhD_SNP','VARITY_R',
             'VARITY_ER','ClinPred','BayesDel','BayesDel_noAF','MetaRNN','GenoCanyon','Eigen','fathmm-MKL','DANN','CADD_1.6',
             'MPC','MVP','MutPred','MetaLR','MetaSVM','REVEL','CONDEL','DEOGEN2','SNPs&GO3D','PhD-SNPg',
             'M-CAP','SuSPect','FathmmXF','VEST4','SNAP2','PonP2','FATHMM','PolyPhen2_HumVar','PolyPhen2_HumDiv','SIGMA',
             'SPRI','MutFormer','AlphScore','Maverick_benign','mvPPT','PHACTboost','CADD_1.7',
      '3Cnet']

# List of population-tuned VEPs
tuned = ["AlphaMissense","UNEECON","LASSIE","popEVE","LIST-S2","PrimateAI"]

# Dictionary with any DMS that VEPs are trained with.
VEP_TRAINING_DATA = {'VARITY_R':['UBE2I','SUMO1','CALM1','TPK1','NCS1','GDI1','TECR','MTHFR','CBS','BRCA1','PTEN','TPMT'],
'VARITY_ER':['UBE2I','SUMO1','CALM1','TPK1','NCS1','GDI1','TECR','MTHFR','CBS','BRCA1','PTEN','TPMT'],
'CPT-1':['CALM1','MTHFR','SUMO1','UBE2I','TPK1'],
'DeMaSk':['MAPK1','P53','CCR5','CXCR4','CALM1','SUMO1','TPK1','UBE2I'],
'Envision':['BRCA1']}

# Criteria used to select the DMS assays as 'cannonical'
criteria = 'median'

with open(rename_path,'r') as ifile:
    rename_dict = {x.split(',')[0].strip():x.split(',')[1].strip() for x in ifile}
# Function to dynamically rename VEPs based on rules in the rename file
def rename(x):
    keys = list(rename_dict.keys())
    convert_array = [bool(re.match(z,x)) for z in keys]
    if any(convert_array):
        return rename_dict[keys[convert_array.index(1)]]
    else:
        return x

uniprot_gene_dict = {}
with open(DMS_summary_path,'r') as ifile:
    for line in ifile:
        line = line.split(',')
        uniprot_gene_dict[line[0]] = line[1]

gene_uniprot_dict = {i:j for j,i in uniprot_gene_dict.items()}

invert = pd.read_excel(invert_path,index_col='score')
invert = invert.to_dict(orient='index')
invert = {i:list(j.values())[0] for i,j in invert.items()}

# Exclude all variants in ClinVar, gnomAD and HGMD from a prediction frame
def exclude_variants(frame,uniprot):
    exclude_clinvar = pd.read_csv(clinvar_path)
    exclude_clinvar = exclude_clinvar[~exclude_clinvar['clinsig'].isin(['Uncertain_significance','Conflicting_classifications_of_pathogenicity',
                                                                      ])]
    exclude_clinvar = exclude_clinvar[~exclude_clinvar['revstat'].str.contains('no_assertion_criteria_provided')]
    exclude_targets = list(set(exclude_clinvar[exclude_clinvar['uniprot_id']==uniprot]['variant']))
    
    exclude_gnomad = pd.read_csv(gnomad_path)
    exclude_targets = list(set(exclude_targets + list(set(exclude_gnomad[exclude_gnomad['uniprot_id']==uniprot]['variant']))))
    
    #exclude_hgmd = pd.read_csv(r'C:\Users\blivesey\Documents\FULL_DMS_VEP_PIPELINE\exclude variants\hgmd_variants.csv')
    #exclude_hgmd['variant'] = exclude_hgmd['hgmd_hgvs'].apply(lambda x:x.split('.')[-1])
    #exclude_targets = list(set(exclude_targets+list(set(exclude_hgmd[exclude_hgmd['hgmd_uniprot']==uniprot]['variant']))))
    
    allowed_variants = [i for i in frame.index if i not in exclude_targets]
    frame_mod = frame.loc[allowed_variants]
    return frame_mod

###########################################################################

# Calculte the integrity of the prediction result files
# This is used to exclude proteins / VEPs that do not meed the coverage criteria

# minimum coverage before a column is classed as missing data
minimum_coverage = 0.1

files = [i for i in os.listdir(DMS_dir) if '.csv' in i and i.split('.')[0] in final_DMS_list]

filematrix = pd.DataFrame(index=files)

for file in tq(files):
    data = pd.read_csv(DMS_dir+'%s' % (file), index_col='variant')
    for column in data.columns:
        if 'DMS' in column:
            continue
        column_rename = rename(column)
        
        if column_rename not in filematrix.columns:
            filematrix[column_rename] = [0]*len(filematrix)
        if len(data[column].dropna()) >= len(data)*minimum_coverage:
            filematrix[column_rename][file] = 1
            
filematrix.to_csv('DMS_integrity_matrix.csv')

integrity_matrix = pd.read_csv('DMS_integrity_matrix.csv',index_col='Unnamed: 0')
# Remove DMS that is present for <50% of the the DMS datasets.
integrity_matrix['total'] = integrity_matrix.sum(axis=1)
total_veps = len(integrity_matrix.columns)
vep_subset = integrity_matrix[integrity_matrix['total']<total_veps/2]
exclude_proteins = list(set([i.split('.')[0] for i in vep_subset.index]))

integrity_matrix=integrity_matrix.T
integrity_matrix['total'] = integrity_matrix.sum(axis=1)
total_dms = len(integrity_matrix.columns)
dms_subset = integrity_matrix[integrity_matrix['total']<total_dms/2]
exclude_VEPs = list(set(exclude_VEPs + list(dms_subset.index)))


# Calculate the mean, median and maximum DMS correlations with each VEP column
minimum_coverage = 1000

files = [i for i in os.listdir(DMS_dir) if '.csv' in i and i.split('.')[0] in final_DMS_list]
cor_dict = {}

pbar = tq(files)
for file in pbar:
    pbar.set_description(file)
    protein_name = file[:-4]
    if protein_name in exclude_proteins:
        continue
    data = pd.read_csv(DMS_dir+'%s' % (file), index_col='variant')
    
    data = data[[i for i in data.columns if rename(i) not in exclude_VEPs]]
    dms_sets = [i for i in data.columns if 'DMS' in i]
    for dset in dms_sets:
        cor_list = []
        for column in data.columns:
            subset = data[[dset,column]].dropna()
            if 'DMS' not in column and len(subset) >= minimum_coverage:
                cor_list.append(abs(spearmanr(subset[dset],subset[column])[0]))
            else:
                continue
        
        if len(cor_list) == 0:
            cor_dict[protein_name+'_'+dset] = [protein_name,dset,np.nan,np.nan,np.nan]
        else:
            cor_dict[protein_name+'_'+dset] = [protein_name,dset,np.mean(cor_list),np.median(cor_list),np.max(cor_list)]

all_cor_results = pd.DataFrame.from_dict(cor_dict,orient='index')
all_cor_results.columns = ['protein','DMS_set','mean_correlation','median_correlation','max_correlation']
all_cor_results.to_csv('average_DMS_VEP_correlations.csv',index=None)

# Compile the data used to plot figure 1

hframe = pd.DataFrame()
selected_DMS_data = pd.read_csv('average_DMS_VEP_correlations.csv')

unique_proteins = list(set(selected_DMS_data['protein']))

for protein in tq(unique_proteins):
    selected = list(selected_DMS_data[selected_DMS_data['protein']==protein].dropna(subset=['%s_correlation' % (criteria)]).sort_values('%s_correlation' % (criteria),ascending=False)['DMS_set'])[0]
    hframe[protein] = np.NAN
    data = pd.read_csv(DMS_dir+'%s.csv' % (protein), index_col='variant')
    
    data = exclude_variants(data,protein)
    
    data.columns = [rename(i) for i in data.columns]
    
    data = data[[i for i in data.columns if i not in exclude_VEPs]]
    
    
    for col in data.columns:
        if 'DMS' not in col:
            if col not in hframe.index:
                hframe.loc[col] = np.NAN
            subset = data[[col,selected]].dropna()
            cor = spearmanr(subset[col],subset[selected])
            hframe[protein][col] = cor[0]
            

figure_1_data = abs(hframe)
figure_1_data.to_csv('Figure_1_data.csv')

################################################################################

# Perform the amin paired ranking analysis.

all_protein_frames = []
files = [i for i in os.listdir(DMS_dir) if '.csv' in i and i.split('.')[0] in final_DMS_list]
final_VEP_list = []
for counter, file in enumerate(tq(files)):
    protein = file[:-4]
    if protein in exclude_proteins:
        continue
    data = pd.read_csv(DMS_dir+'%s' % (file), index_col='variant')
    
    data = exclude_variants(data,protein)
    
    data.columns = [rename(i) for i in data.columns]
    all_VEPs = [i for i in data.columns if 'DMS' not in i]
    all_VEPs = [i for i in all_VEPs if i not in exclude_VEPs]
    
    training_exclude = []
    for k, v in VEP_TRAINING_DATA.items():
        if uniprot_gene_dict[protein] in v:
            training_exclude.append(k)
    all_VEPs = [i for i in all_VEPs if i not in training_exclude]
    
    protein_specific_frame = pd.DataFrame(columns=all_VEPs,index=all_VEPs)
    top_result = list(selected_DMS_data[selected_DMS_data['protein']==protein].sort_values('%s_correlation' % (criteria),ascending=False)['median_correlation'])[0]
    if np.isnan(top_result):
        continue
    selected = list(selected_DMS_data[selected_DMS_data['protein']==protein].sort_values('%s_correlation' % (criteria),ascending=False)['DMS_set'])[0]
    for p1 in all_VEPs:
        if p1 not in final_VEP_list:
            final_VEP_list.append(p1)
        for p2 in all_VEPs:
            if p1 == p2:
                continue
            subset = data[[p1,p2,selected]].dropna()
            corr_1 = abs(spearmanr(subset[p1],subset[selected])[0])
            corr_2 = abs(spearmanr(subset[p2],subset[selected])[0])
            try:
                if corr_1 > corr_2:
                    protein_specific_frame[p1][p2] = 1
                    protein_specific_frame[p2][p1] = 0
                elif corr_1 == corr_2:
                    protein_specific_frame[p1][p2] = 0
                    protein_specific_frame[p1][p2] = 0
            except:
                protein_specific_frame[p1][p2] = 0
                protein_specific_frame[p1][p2] = 0
    all_protein_frames.append(protein_specific_frame)

final_frame_wins = pd.DataFrame(columns=final_VEP_list,index=final_VEP_list).fillna(0)
final_frame_totals = pd.DataFrame(columns=final_VEP_list,index=final_VEP_list).fillna(0)
protein_frame = pd.DataFrame(index=final_VEP_list,columns=['proteins']).fillna(0).astype(int)
for frame in tq(all_protein_frames):
    for v1 in final_VEP_list:
        if v1 in frame.columns:
            protein_frame['proteins'][v1] += 1
        for v2 in final_VEP_list:
            if v1 in frame.columns and v2 in frame.columns and frame[v1][v2] is not np.nan:
                final_frame_wins[v2][v1] += frame[v1][v2]
                final_frame_totals[v2][v1]+=1
                
final_final_frame = (final_frame_wins / final_frame_totals) * 100

rank_score_list = []
for i, row in final_final_frame.iterrows():
    total = 0
    for j, v in zip(row.index,row):
        if j != i:
            total+=v
    total = total / (len(row)-1)
    rank_score_list.append(total)
final_final_frame['rank_score'] = rank_score_list
final_final_frame.sort_values('rank_score',ascending=False,inplace=True)
final_final_frame = pd.merge(final_final_frame,protein_frame,how='left',left_index=True,right_index=True)
final_final_frame_heatmap = final_final_frame[list(final_final_frame.index)]
np.fill_diagonal(final_final_frame_heatmap.values,50)
final_final_frame.to_csv('Figure_2_data.csv')