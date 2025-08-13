# exp_002 Protocol Draft - Cold Pre-digestion Method

**Version**: 2.1  
**Date**: 2025-01-16  
**Based on**: exp_001 analysis and literature review

## OVERVIEW
**Goal**: Preserve fragile tumor epithelial cells while achieving complete tissue dissociation  
**Key Innovation**: Cold pre-digestion step to reduce warm digestion time

---

## REAGENT PREPARATION

### Cold Digestion Mix (NEW)
- **Enzyme D**: 50μL (half strength)
- **Enzyme R**: 25μL (half strength)  
- **Enzyme A**: 10μL (half strength)
- **Buffer**: 2.4mL RPMI + 10% FBS
- **Keep on ice until use**

### Warm Digestion Mix  
- **Enzyme D**: 100μL (full strength)
- **Enzyme R**: 50μL (full strength)
- **Enzyme A**: 20μL (full strength) 
- **Buffer**: 2.3mL RPMI + 10% FBS

### DNase Mix (NEW)
- **DNase I**: 20μL (2000 units/mL)
- **MgCl2**: 10μL (100mM)
- **Buffer**: 2.5mL PBS

---

## STEP-BY-STEP PROTOCOL

### Step 1: Sample Prep (0-15 min)
1. **Receive tissue on ice** - process within 30 min of resection
2. **Pathology review** - confirm tumor content >50%
3. **Weigh tissue** - target 1-3g for optimal processing  
4. **Dice tissue** - 2-3mm pieces with sterile scalpel
5. **Transfer to gentleMACS C tube** - keep on ice

**✅ Checkpoint**: Tissue pieces uniform size, minimal necrosis

---

### Step 2: Initial Mechanical (15-20 min)
1. **gentleMACS program**: "37C_h_TDK_1" (soft program)
2. **Check under microscope**: Tissue breakdown without over-disruption
3. **Photos**: Document initial mechanical disruption

**✅ Checkpoint**: Tissue broken down but epithelial clumps still visible

---

### Step 3: Cold Pre-digestion ❄️ (20-35 min) 
🆕 **NEW STEP**

1. **Add cold digestion mix** (2.5mL, pre-chilled to 4°C)
2. **Incubate at 4°C for 15 minutes** with gentle rotation
3. **No shaking** - just slow rotation to prevent mechanical stress
4. **Check at 10 min**: Sample aliquot under microscope
   - Look for: Early cell release, epithelial viability
   - Expect: Some single cells, intact clumps still present

**✅ Checkpoint**: Gentle cell release without debris accumulation

---

### Step 4: Warm Digestion (35-60 min)
🔄 **MODIFIED - Shorter duration**

1. **Add warm digestion mix** (2.5mL at 37°C)  
2. **Incubate 37°C with gentle shaking**
3. **Monitor every 10 minutes**:

   **10 min check**:
   - Sample 50μL for microscopy
   - Count: single cells vs clumps ratio
   - Viability: Trypan blue exclusion
   - **Decision**: Continue if clumps >50%

   **20 min check**:
   - Repeat assessment
   - **STOP HERE if**:
     - Single cells >70% 
     - Viability dropping below 85%
     - High debris visible

   **25 min check** (MAXIMUM):
   - **Mandatory stop** regardless of clumps
   - Prioritize cell health over complete dissociation

4. **Photo documentation** at each time point

**✅ Checkpoint**: Adequate single cells without over-digestion

---

### Step 5: Enhanced Mechanical (60-70 min)
🆕 **ADDITIONAL STEP**

1. **gentleMACS program**: "37C_m_TDK_2" 
2. **Manual pipetting**: 10x with 5mL serological pipette
   - Gentle up/down motion
   - Avoid foaming
3. **Check suspension**: Should be mostly single cells now
4. **Final mechanical**: gentleMACS "37C_h_TDK_3" if clumps persist

**✅ Checkpoint**: Single cell suspension achieved

---

### Step 6: Cleanup & Purification (70-90 min)
🆕 **ENHANCED CLEANUP**

1. **DNase treatment**:
   - Add 100μL DNase mix
   - Incubate 5 min room temperature  
   - Mix by gentle inversion

2. **Straining**:
   - 70μm filter first (catch remaining clumps)
   - 40μm filter second (final cleanup)
   - Collect flow-through

3. **Dead cell removal**:
   - Miltenyi Dead Cell Removal Kit
   - Follow manufacturer protocol
   - Should reduce debris significantly

4. **Final assessment**:
   - Cell count and viability
   - Microscopy photos
   - Debris level evaluation

**✅ Checkpoint**: Clean single cell suspension, >80% viability

---

### Step 7: 10X Preparation (90-120 min)

1. **Cell concentration**: Dilute to 1,000 cells/μL
2. **Final count**: Automated counter + manual verification  
3. **Load volume**: 50μL for ~5,000 recovered cells target
4. **QC photos**: Document final suspension quality

---

## DECISION POINTS

### Early Stop Criteria:
- **Viability drops <80%** - stop digestion immediately
- **Heavy debris visible** - proceed to cleanup  
- **Good single cells at 15min** - skip to 20min check

### Extension Criteria:  
- **Heavy clumps at 20min** - continue to 25min maximum
- **Tough/fibrotic tissue** - may need additional mechanical

---

## TROUBLESHOOTING

| Problem | Cause | Solution |
|---------|-------|----------|
| **High clumps at 20min** | Fibrotic tissue | Additional gentleMACS, extend to 25min max |
| **Low viability early** | Tissue quality | Reduce digestion time, increase cold phase |
| **High debris** | Over-digestion | Stop early, enhance cleanup steps |
| **Low yield** | Under-digestion | Slight increase in warm phase next time |

---

## SUCCESS METRICS

**Primary Goals**:
- Tumor epithelial cells: >20%
- Overall viability: >80%  
- Mitochondrial %: <15%

**Secondary Goals**:
- Immune cells: 35-45% (vs 65% in exp_001)
- Fibroblasts: 15-20% (vs 7% in exp_001)  
- Clean single cell suspension
- Reduced ambient RNA

---

## NOTES FOR EXECUTION

**Critical Timing**:
- Cold digestion: Exactly 15 minutes (don't extend)
- Warm digestion: 20min default, 25min maximum  
- Monitor continuously - don't rely on timers alone

**Team Coordination**:
- Bob: Primary operator and decision maker
- Jennifer: Microscopy monitoring and documentation  
- Both: QC assessment at each checkpoint

**Backup Plans**:
- If protocol fails: Save aliquots for method comparison
- If low yield: Accept quality over quantity
- If high clumps: Additional mechanical disruption acceptable

---
**Protocol Status**: 📋 Ready for execution  
**Expected Duration**: ~2 hours total (vs 1.5hr for exp_001)  
**Key Success**: Epithelial cell preservation through cold pre-digestion