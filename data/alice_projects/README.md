# Lung Cancer scRNAseq Project - Bob's Lab

## Project Overview

**Principal Investigator**: Bob Chen  
**Project Start**: 2025-01-15  
**Study Type**: Single-cell RNA sequencing analysis of lung adenocarcinoma  
**Technology**: 10X Genomics Chromium Single Cell 3' v3 kit  
**Sample Source**: Primary lung adenocarcinoma tissue from surgical resections

## Research Objectives

### Primary Aim
Characterize the cellular heterogeneity within lung adenocarcinoma tumor microenvironment, with focus on:
- Tumor epithelial cell subpopulations
- Immune cell infiltration patterns  
- Stromal cell composition and activation states
- Cell-cell communication networks

### Secondary Aims
1. Identify biomarkers associated with immune infiltration
2. Map transcriptional programs in tumor vs. normal adjacent tissue
3. Characterize therapy resistance mechanisms at single-cell level

## Sample Information

**Patient Cohort**: Stage II-III lung adenocarcinoma patients (n=8 planned)
- Age range: 55-72 years
- Smoking history: Mixed (4 former smokers, 2 never-smokers, 2 current)
- Treatment naive (no prior chemotherapy/radiation)

**Tissue Processing**:
- Fresh surgical specimens transported on ice within 30 min
- Tumor regions identified by pathologist
- Target: 70%+ tumor content areas
- Normal adjacent lung collected as control

## Experimental Design

### Phase 1: Protocol Development (exp_001 - exp_002)
- **exp_001**: Initial protocol test with standard dissociation
- **exp_002**: Optimized dissociation protocol (based on exp_001 findings)

### Phase 2: Full Cohort Analysis (exp_003 onwards)
- Process remaining patient samples with optimized protocol
- Include matched normal adjacent tissue controls

## Key Challenges Identified

### Issue from exp_001:
1. **Low tumor epithelial cell recovery** - Only 8% epithelial cells captured
2. **Immune cell enrichment** - 65% immune cells (expected ~30-40%)
3. **Cell clumping observed** - Incomplete tissue dissociation
4. **High ambient RNA** - Suggesting over-digestion or cell lysis

### Root Cause Analysis:
Current protocol may have **suboptimal digestion kinetics**:
- Fragile tumor epithelial cells lysed during extended warm digestion
- Resistant immune cells preferentially survived
- Incomplete mechanical dissociation left stromal clumps

## Technical Specifications

**Equipment**:
- 10X Genomics Chromium Controller
- gentleMACS Octo Dissociator (Miltenyi Biotec)
- Inverted microscope for real-time monitoring
- Cell counters: Luna-FL automated cell counter

**Key Reagents**:
- Tumor Dissociation Kit (Miltenyi Biotec, cat# 130-095-929)
- Collagenase IV (Worthington, cat# LS004188)
- DNase I (Sigma, cat# DN25)
- 10X Genomics Single Cell 3' Reagent Kit v3

## Success Metrics

**Quality Control Targets**:
- Cell viability: >80%
- Doublet rate: <10% 
- Genes/cell: >1500 (epithelial), >800 (immune)
- Mitochondrial gene %: <15%
- Tumor epithelial representation: >20%

**Expected Cell Composition** (based on literature):
- Tumor epithelial: 20-40%
- Immune cells: 25-35% (T cells, macrophages, NK)
- Stromal cells: 15-25% (fibroblasts, endothelial)
- Normal epithelial: 5-15%

## Current Status

- ✅ **exp_001**: Completed - revealed protocol issues
- 🔄 **exp_002**: In planning - optimization experiment  
- ⏳ **exp_003-008**: Pending optimization results

## Key References

1. Lambrechts et al. Nature Medicine 2018 - Lung cancer scRNAseq atlas
2. Kim et al. Cell 2020 - Comprehensive lung cancer TME analysis  
3. Zilionis et al. Immunity 2019 - Immune landscape of lung cancer
4. 10X Genomics Technical Note: "Tissue Dissociation for Single Cell Applications"

## Contact Information

**Primary Contact**: Bob Chen (bob.chen@university.edu)  
**Collaborators**: 
- Dr. Sarah Park (Pathology) - Tissue processing
- Dr. Mike Zhang (Bioinformatics) - Data analysis
- Jennifer Liu (Research Tech) - scRNAseq execution

---
*Last updated: 2025-01-15*  
*Project folder: `/data/bob_projects/`*