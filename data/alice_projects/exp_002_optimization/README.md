# Experiment 002: Protocol Optimization 

## Overview

**Experiment ID**: exp_002_optimization  
**Date**: **PLANNED** - Not yet executed  
**Operator**: Bob Chen, Jennifer Liu  
**Status**: 🔄 **IN PLANNING** - Awaiting protocol finalization  

**Objective**: Optimize tissue dissociation protocol based on exp_001 findings to improve tumor epithelial cell recovery and reduce immune cell bias.

## Motivation

**Critical Issues from exp_001**:
1. **Only 8% tumor epithelial cells captured** (expected 25-40%)
2. **65% immune cells** vs expected 25-35% - severe bias
3. **High cell stress** (16.8% mitochondrial genes)  
4. **Cell clumping** during dissociation
5. **Low viability** (76% vs target

### Primary Changes from exp_001:

#### 1. **Cold Pre‑digestion Step** 🧊
- **15 minutes at 4 °C** with reduced enzyme concentration  
- Allows longer digestion without heat‑shock stress response  
- Should release cells gently without inducing FOS/JUN/HSP up‑regulation  

#### 2. **Shortened Warm Digestion** ⏱️
- **Reduce to 20‑25 minutes at 37 °C** (vs previous 45 min)  
- Stop immediately when microscopy shows adequate single‑cell release  
- Prioritize epithelial cell survival over complete dissociation  

#### 3. **Enhanced Mechanical Disruption** ⚙️
- **Additional gentleMACS cycles** with “soft” program first  
- **Manual pipetting** between enzyme steps  
- More frequent agitation during digestion  

#### 4. **Real‑time Monitoring** 🔬
- **Check every 10 minutes** with microscopy  
- **Viability assessment** at each time point  
- **Photo documentation** for optimization record  

#### 5. **Debris Cleanup** 🧹  
- **DNase I treatment** to reduce ambient RNA  
- **Dead cell removal kit** (Miltenyi) post‑digestion  
- **OptiPrep gradient** if high debris persists  

## Detailed Protocol Draft

### Sample Preparation (Same as exp_001)
- Fresh lung adenocarcinoma tissue  
- 2‑3 mm pieces with scalpel  
- Keep on ice until processing  

### Step 1: Initial Mechanical Disruption
- gentleMACS **“soft_01”** program (NEW)  
- Check tissue breakdown under microscope  

### Step 2: Cold Pre‑digestion ❄️ (NEW STEP)
- **4 °C for 15 minutes**  
- 50 % enzyme concentration (Enzyme D, R reduced)  
- Gentle rotation, no shaking  
- Monitor, 20 minutes**  
- Stop when clumps resolve (don’t wait for timer)  

### Step 4: Enhanced Mechanical (NEW)
- Additional gentleMACS **“medium_02”** if needed  
- Manual pipetting 10× with 5 mL pipette  
- Check single‑cell suspension  

### Step 5: Cleanup (ENHANCED)
- **DNase I treatment**: 5 minutes at room temp  
- **70 µm + 40 µm straining** (same as before)  
- **Dead cell removal** (Miltenyi kit)  
- Check debris level under microscope  

### Step 6: QC and Loading
- Viability check (target > 80 %)  
- Cell concentration for 10X loading  
- Photo documentation of final suspension  

## Expected Improvements

### Cell Recovery Targets:
| Cell Type | exp_001 Result | exp_002 Target | Improvement Strategy |
|-----------|----------------|----------------|----------------------|
| **Tumor Epithelial** | 8 % | **25‑35 %** | Gentle digestion, preserve fragile cells |
| **Immune Total** | 65 % | **35‑45 %** | Reduce over‑representation |
| **Fibroblasts** | 7 % | **15‑20 %** | Better clump disruption |
| **Viability** | 76 % | **> 85 %** | Reduced digestion stress |

### Quality Improvements:
- **Mitochondrial %**: < 12 % (vs 16.8 %)  
- **Median genes/cell**: > 1,500 (vs 1,247)  
- **Ambient RNA**: < 0.10 (vs 0.23)  
- **Cell stress markers**: Reduced FOS/JUN expression  

## Risk Mitigation

### Potential Issues:
1. **Incomplete dissociation** – Cold digestion may be too gentle  
   - **Mitigation**: Extend warm phase if needed (max 30 min)  

2. **Low cell yield** – Gentle protocol may reduce total recovery  
   - **Mitigation**: Accept lower yield for better quality  

3. **Still see clumping** – Some tissue may be very fibrotic  
   - **Mitigation**: Additional mechanical disruption steps  

4. **Increased processing time** – More steps = longer protocol  
   - **Mitigation**: Pre‑optimize timing, parallel processing  

## Success Criteria

### Primary Endpoints:
✅ **Tumor epithelial cells: > 20 %** (vs 8 % in exp_001)  
✅ **Cell viability: > 80 %** (vs 76 % in exp_001)  
✅ **Mitochondrial %: < 15 %** (vs 16.8 % in exp_001)  

### Secondary Endpoints:
- Immune cell proportion normalized to 35‑45 %  
- Reduced ambient RNA contamination  
- Improved fibroblast representation  
- Clear single‑cell suspension (minimal clumps)  

## Timeline

- **Week 1**: Finalize protocol details, order reagents  
- **Week 2**: **Execute exp_002** with next patient sample (LC‑002)  
- **Week 3**: Data analysis and protocol assessment  
- **Week 4**: Decision on exp_003 protocol or further optimization  

## Required Materials

### New Reagents Needed:
- [ ] **Cold digestion enzymes** (Miltenyi cold‑active collagenase)  
- [ ] **DNase I** (Sigma cat# DN25, 2000 units)  
- [ ] **Dead Cell Removal Kit** (Miltenyi cat# 130‑090‑101)  
- [ ] **OptiPrep gradient medium** (if needed for debris)  

### Equipment Ready:
- ✅ gentleMACS Octo Dissociator  
- ✅ Cold room access for 4 °C digestion  
- ✅ Microscopy setup for monitoring  
- ✅ Cell counting equipment  

## Questions for Team Discussion

1. **Should we test even gentler conditions?** (e.g., 15 min total warm digestion)  
2. **Alternative mechanical disruption?** (ultrasonication, different gentleMACS programs)  
3. **Control experiment?** Run both old and new protocol side‑by‑side?  
4. **Backup plan?** What if optimization still shows epithelial bias?  

## References for Protocol Design

1. **van den Brink et al. Nature Protocols 2017** – Cold digestion methods  
2. **Denisenko et al. Genome Biology 2020** – scRNA‑seq protocol optimization  
3. **10X Genomics Technical Note CG000206** – TissueFor lung cancer tissue dissociation.md`)  

**Key Findings from the Document (2025‑08‑16):**  

- **Digestion time is a critical determinant** of cell viability, transcriptional stress, and cell‑type composition in lung cancer tissue dissociation for scRNA‑seq.  
- **Over‑digestion** (excessively long warm incubation) leads to loss of fragile tumor epithelial cells, activation of a conserved stress transcriptional program (FOS, JUN, HSPs, MHC‑I), skewed proportions toward resistant myeloid/fibroblast populations, and increased ambient RNA from dead cells.  
- **Under‑digestion** (excessively short warm incubation) yields low overall cell numbers, persistent clumps, and a suspension enriched for easily released immune cells while under‑representing epithelial and stromal cells.  
- **Practical recommendations** (directly incorporated into exp_002):  
  - Sample the suspension **every 10–15 minutes** for microscopic assessment.  
  - Target a **“just enough” warm digestion window of ≈ 25–45 minutes at 37 °C**, adjusting based on tissue hardness.  
  - **Optional cold‑protease digestion (≈ 6 °C)** can mitigate heat‑shock artifacts when longer digestions are required.  
  - Perform **DNase I washes** and debris removal (dead‑cell kits, OptiPrep) to limit ambient RNA.  

**Integration with exp_002:**  
- The protocol adopts the **cold‑protease pre‑digestion** (4 °C, 15 min) and shortens the warm digestion to **20‑25 minutes** as recommended for balancing yield, viability, and transcriptomic fidelity.  
- Real‑time monitoring every 10 minutes follows the document’s guidance to stop the reaction as soon as adequate single‑cell release is observed, thereby preventing over‑digestion‑induced stress.  

## Next Actions

- [ ] **Literature review**: Check latest lung scRNA‑seq protocols (2024‑2025)  
- [ ] **Order reagents**: Cold digestion and cleanup kits  
- [ ] **Protocol dry‑run**: Test timing and logistics without sample  
- [ ] **Patient scheduling**: Coordinate with surgical team for LC‑002  

---
**Experiment Status**: 📋 **READY FOR EXECUTION** pending reagent arrival  
**Key Hypothesis**: Cold pre‑digestion + shortened warm digestion will preserve epithelial cells  
**Decision Point**: Based on exp_002 results, finalize protocol for remaining 6 patients