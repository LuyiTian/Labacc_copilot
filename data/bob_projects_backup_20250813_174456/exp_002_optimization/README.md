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
5. **Low viability** (76% vs target >80%)

**Root Cause**: Standard 45-minute warm digestion protocol over-digests fragile lung adenocarcinoma epithelial cells while preserving resistant immune cells.

## Key Question

**How can we optimize dissociation kinetics to preserve epithelial cells while maintaining efficient single-cell suspension?**

## Proposed Protocol Modifications

### Primary Changes from exp_001:

#### 1. **Cold Pre-digestion Step** 🧊
- **15 minutes at 4°C** with reduced enzyme concentration
- Allows longer digestion without heat-shock stress response
- Should release cells gently without inducing FOS/JUN/HSP upregulation

#### 2. **Shortened Warm Digestion** ⏱️
- **Reduce to 20-25 minutes at 37°C** (vs previous 45 min)
- Stop immediately when microscopy shows adequate single-cell release
- Prioritize epithelial cell survival over complete dissociation

#### 3. **Enhanced Mechanical Disruption** ⚙️
- **Additional gentleMACS cycles** with "soft" program first
- **Manual pipetting** between enzyme steps 
- More frequent agitation during digestion

#### 4. **Real-time Monitoring** 🔬
- **Check every 10 minutes** with microscopy
- **Viability assessment** at each time point
- **Photo documentation** for optimization record

#### 5. **Debris Cleanup** 🧹  
- **DNase I treatment** to reduce ambient RNA
- **Dead cell removal kit** (Miltenyi) post-digestion
- **OptiPrep gradient** if high debris persists

## Detailed Protocol Draft

### Sample Preparation (Same as exp_001)
- Fresh lung adenocarcinoma tissue
- 2-3mm pieces with scalpel
- Keep on ice until processing

### Step 1: Initial Mechanical Disruption
- gentleMACS "soft_01" program (NEW)
- Check tissue breakdown under microscope

### Step 2: Cold Pre-digestion ❄️ (NEW STEP)
- **4°C for 15 minutes**
- 50% enzyme concentration (Enzyme D, R reduced)
- Gentle rotation, no shaking
- Monitor for early cell release

### Step 3: Warm Digestion (MODIFIED)
- **37°C for 20-25 minutes** (reduced from 45 min)
- Full enzyme concentration
- **Check at 10, 15, 20 minutes**
- Stop when clumps resolve (don't wait for timer)

### Step 4: Enhanced Mechanical (NEW)
- Additional gentleMACS "medium_02" if needed
- Manual pipetting 10x with 5mL pipette
- Check single-cell suspension

### Step 5: Cleanup (ENHANCED)
- **DNase I treatment**: 5 minutes at room temp
- **70μm + 40μm straining** (same as before)
- **Dead cell removal** (Miltenyi kit)
- Check debris level under microscope

### Step 6: QC and Loading
- Viability check (target >80%)
- Cell concentration for 10X loading
- Photo documentation of final suspension

## Expected Improvements

### Cell Recovery Targets:
| Cell Type | exp_001 Result | exp_002 Target | Improvement Strategy |
|-----------|----------------|----------------|---------------------|
| **Tumor Epithelial** | 8% | **25-35%** | Gentle digestion, preserve fragile cells |
| **Immune Total** | 65% | **35-45%** | Reduce over-representation |  
| **Fibroblasts** | 7% | **15-20%** | Better clump disruption |
| **Viability** | 76% | **>85%** | Reduced digestion stress |

### Quality Improvements:
- **Mitochondrial %**: <12% (vs 16.8%)
- **Median genes/cell**: >1,500 (vs 1,247)
- **Ambient RNA**: <0.10 (vs 0.23)
- **Cell stress markers**: Reduced FOS/JUN expression

## Risk Mitigation

### Potential Issues:
1. **Incomplete dissociation**: Cold digestion may be too gentle
   - **Mitigation**: Extend warm phase if needed (max 30 min)

2. **Low cell yield**: Gentle protocol may reduce total recovery  
   - **Mitigation**: Accept lower yield for better quality

3. **Still see clumping**: Some tissue may be very fibrotic
   - **Mitigation**: Additional mechanical disruption steps

4. **Increased processing time**: More steps = longer protocol
   - **Mitigation**: Pre-optimize timing, parallel processing

## Success Criteria

### Primary Endpoints:
✅ **Tumor epithelial cells: >20%** (vs 8% in exp_001)  
✅ **Cell viability: >80%** (vs 76% in exp_001)  
✅ **Mitochondrial %: <15%** (vs 16.8% in exp_001)

### Secondary Endpoints:
- Immune cell proportion normalized to 35-45%
- Reduced ambient RNA contamination  
- Improved fibroblast representation
- Clear single-cell suspension (minimal clumps)

## Timeline

- **Week 1**: Finalize protocol details, order reagents
- **Week 2**: **Execute exp_002** with next patient sample (LC-002)
- **Week 3**: Data analysis and protocol assessment
- **Week 4**: Decision on exp_003 protocol or further optimization

## Required Materials

### New Reagents Needed:
- [ ] **Cold digestion enzymes** (Miltenyi cold-active collagenase)
- [ ] **DNase I** (Sigma cat# DN25, 2000 units)  
- [ ] **Dead Cell Removal Kit** (Miltenyi cat# 130-090-101)
- [ ] **OptiPrep gradient medium** (if needed for debris)

### Equipment Ready:
- ✅ gentleMACS Octo Dissociator
- ✅ Cold room access for 4°C digestion
- ✅ Microscopy setup for monitoring
- ✅ Cell counting equipment

## Questions for Team Discussion

1. **Should we test even gentler conditions?** (e.g., 15min total warm digestion)
2. **Alternative mechanical disruption?** (ultrasonication, different gentleMACS programs)
3. **Control experiment?** Run both old and new protocol side-by-side?
4. **Backup plan?** What if optimization still shows epithelial bias?

## References for Protocol Design

1. **van den Brink et al. Nature Protocols 2017** - Cold digestion methods
2. **Denisenko et al. Genome Biology 2020** - scRNAseq protocol optimization  
3. **10X Genomics Technical Note CG000206** - Tissue dissociation best practices
4. **Lambrechts et al. Nature Medicine 2018** - Lung cancer dissociation protocols

## Next Actions

- [ ] **Literature review**: Check latest lung scRNAseq protocols (2024-2025)
- [ ] **Order reagents**: Cold digestion and cleanup kits
- [ ] **Protocol dry-run**: Test timing and logistics without sample
- [ ] **Patient scheduling**: Coordinate with surgical team for LC-002

---
**Experiment Status**: 📋 **READY FOR EXECUTION** pending reagent arrival  
**Key Hypothesis**: Cold pre-digestion + shortened warm digestion will preserve epithelial cells  
**Decision Point**: Based on exp_002 results, finalize protocol for remaining 6 patients