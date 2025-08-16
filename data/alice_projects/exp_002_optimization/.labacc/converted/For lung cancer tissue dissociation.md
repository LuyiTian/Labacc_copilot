For lung cancer tissue dissociation, digestion time is one of the most critical variables

affecting both cell yield and the biological quality of your scRNA-seq data. The

consequences of going too long or too short differ, and the trade-offs are particularly

important for lung because of its high immune infiltration, mucin content, and

heterogeneous matrix composition.

1. If digestion time is too long

a. Cell viability loss

•  Extended exposure to collagenase, dispase, or proteases will damage cell

membranes.

•  Epithelial cells, especially tumor epithelial cells, are more fragile and will lyse

first, reducing the representation of tumor cells.

b. Transcriptional artifacts

•  Prolonged warm digestion (37 °C) induces a conserved enzymatic dissociation

stress program (FOS, JUN, HSPs, MHC-I upregulation) in many cell types.

•  This makes cells from different samples more similar in the “stress” dimension,

masking true biological differences.

c. Shift in cell composition

•  More resistant populations (e.g., myeloid cells, fibroblasts) become enriched as

fragile cells die.

•  This biases downstream cell type proportion analysis.

d. Increased debris and ambient RNA

•  Dead and lysed cells release RNA into the supernatant, increasing ambient RNA

contamination in 10x data.

•

Leads to higher background gene counts and “soup” effect in all barcodes.

2. If digestion time is too short

a. Low cell yield

•  Tissue remains in chunks, trapping cells inside.

•  You may get disproportionately high immune cell content (since they are easier

to release) and under-representation of tumor epithelial and stromal cells.

b. Incomplete dissociation → clumps

•  Clumps cannot be loaded efficiently into the 10x microfluidics system, causing:

o  Reduced actual cell recovery.

o  Higher multiplet rate if clumps partially enter droplets.

c. Biased composition

•

Large stromal and epithelial clusters remain trapped, so the single-cell

suspension skews toward smaller, more easily liberated cells (T cells,

macrophages).

3. Practical recommendations for lung cancer

1.  Monitor dissociation in real time

Every 10–15 min, pipette a small aliquot, dilute, and check under a microscope

for:

o  Proportion of single cells vs. clumps.

o  Presence of intact epithelial-like cells.

o  Dead cell debris.

2.  Stop at “just enough”

For lung tumors, 25–45 min at 37 °C with gentleMACS (Miltenyi “medium”

program) is typical, but adjust:

o  Softer/more necrotic tissue → shorter time.

o  Very fibrotic tissue → slightly longer but watch viability.

3.

If aiming to preserve native transcriptomes

Use cold protease (6 °C) to allow longer digestion without inducing heat-shock

transcripts.

This allows you to extend time for tough tumor matrix while limiting stress

artifacts.

4.  Post-dissociation cleanup

If you suspect over-digestion or high debris, include a DNase wash and possibly

a debris removal step to reduce ambient RNA before 10x.

If you want, I can prepare a time–outcome matrix specifically for lung cancer scRNA-

seq, showing the trade-offs in yield, viability, cell type bias, and transcriptional artifacts

at different digestion durations for both warm and cold protocols. This makes it easier

to optimize your digestion window empirically.

