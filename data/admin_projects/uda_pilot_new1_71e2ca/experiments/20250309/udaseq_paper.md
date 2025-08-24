https://doi.org/10.1038/s41592-024-02586-y

UDA-seq: universal droplet
microfluidics-based combinatorial indexing
for massive-scale multimodal single-cell
sequencing

Received: 24 June 2024

Accepted: 15 December 2024

Published online: 20 January 2025

 Check for updates

  4,22, Yanling Fan1,2,22, Jun Ping5,22,

  1,2,3,22, Lubin Xu

  1,2,3,22, Zheng Huang

  1,2, Yanjie Chen1,2,3,6, Chengwei Yu

Yun Li
  1,2,3,7, Qifei Wang1,2,3,
Guochao Li
Turun Song8,9, Tao Lin8,9, Mengmeng Liu1,2,3, Yangqing Xu1,2,3, Na Ai1,2,3,
  1,2,3, Qin Qiao1,2, Hongbin Ji3,10,11,12, Zhen Qin10, Shuo Jin13,14,
Xini Meng
  1,2,3, Shaokun Shu
  13,14, Minxian Wang
Nan Jiang
, Feng Zhang
  4
  3,16,17,18,19,20,21
Weiqi Zhang
Lan Jiang

  15
, Limeng Chen

  1,2,3
  1,2,3,6,7

, Guang-Hui Liu

,

  5
 &

The use of single-cell combinatorial indexing sequencing via droplet
microfluidics presents an attractive approach for balancing cost, scalability,
robustness and accessibility. However, existing methods often require
tailored protocols for individual modalities, limiting their automation
potential and clinical applicability. To address this, we introduce UDA-seq,
a universal workflow that integrates a post-indexing step to enhance
throughput and systematically adapt existing droplet-based single-cell
multimodal methods. UDA-seq was benchmarked across various tissue
and cell types, enabling several common multimodal analyses, including
single-cell co-assay of RNA and VDJ, RNA and chromatin, and RNA and
CRISPR perturbation. Notably, UDA-seq facilitated the efficient generation
of over 100,000 high-quality single-cell datasets from three dozen frozen
clinical biopsy specimens within a single-channel droplet microfluidics
experiment. Downstream analysis demonstrated the robustness of this
approach in identifying rare cell subpopulations associated with clinical
phenotypes and exploring the vulnerability of cancer cells.

Single-cell RNA sequencing (scRNA-seq) has greatly enhanced our under-
standing of intricate biological systems and has provided groundbreaking
insights into human genetics and clinical research1,2. Despite its capability
to uncover novel cell types and states within heterogeneous tissues, tran-
scriptomics alone often falls short in distinguishing molecularly similar
yet functionally distinct cell categories3. The concurrent assessment of
additional modalities, which offer distinct and complementary informa-
tion from the same cell, is crucial not only for enhancing our capacity to

identify cell types and states but also for gaining new insights into the
interaction of different components within the cell that define cellular
function4,5. However, the majority of multimodal single-cell sequenc-
ing methods remain expensive and have low throughput. Therefore,
advanced multimodal single-cell sequencing technology is urgently
needed to facilitate fundamental discoveries in biology and medicine.
With the efforts of international consortiums such as the Human
Cell Atlas, the data size of scRNA-seq has grown exponentially, reaching

A full list of affiliations appears at the end of the paper.
ghliu@ioz.ac.cn; chenlimeng@pumch.cn; jiangl@big.ac.cn

 e-mail: shaokun_shu@bjmu.edu.cn; fengzhang@wmu.edu.cn; zhangwq@big.ac.cn;

Nature Methods | Volume 22 | June 2025 | 1199–1212

1199

nature methodsArticle
hundreds of millions of cells. Gene expression values, which can be
considered as ‘tokens’, scale to the order of trillions, which is equivalent
to the amount of natural language text used to train large language
models such as the generative pretrained transformer. Pretrained
large-scale foundation models for deciphering the ‘language’ of cells
have been successfully constructed and are expected to promote
biomedical research6. However, these models are limited to single-cell
transcriptomes. If multimodal single-cell sequencing technology con-
tinues to advance and becomes as widely used as current scRNA-seq,
an additional benefit is that a more robust foundational model, which
takes large-scale multimodal single-cell data as input, could provide a
better understanding of gene regulatory mechanisms and the ability
to predict cellular responses to perturbations.

We have developed UDA-seq, a general workflow for single-cell
multimodal sequencing that connects droplet microfluidics with com-
binatorial indexing. This approach is a versatile strategy that can be
seamlessly integrated with current droplet-based multimodal methods
to enhance throughput. To validate the capabilities of UDA-seq, we
conducted experiments involving various single-cell co-assay tasks,
such as RNA and chromatin, RNA and variable, diversity and joining
(VDJ), and RNA and CRISPR interference across different tissues and
cell types. UDA-seq achieves extremely high throughput with data
quality similar to that of standard droplet microfluidic procedures. We
have also established efficient sample preparation and correspond-
ing computational pipelines to facilitate UDA-seq analysis of clini-
cal liquid or needle biopsy specimens. Our results demonstrate that
UDA-seq can identify age-related ITGB1 + PREX1 + CD4 naive T cells,
proteinuria-related podocyte (POD) cells and kidney injury-related
glomerular capillaries endothelial cells (EC-GCs). Additionally, we show
that UDA-seq can perform hundreds of CRISPR interferences in genes
containing bromodomains, revealing the different vulnerabilities of
existing subpopulations in the SNU16 cancer cell line.

Results
Theory and design of UDA-seq
In droplet microfluidics systems, single cells are encapsulated using
low-density cell suspensions to minimize collisions. Typically, only 1–10%
of the total droplets contain cells or nuclei, following a Poisson distribu-
tion. To enhance cell droplet utilization and reduce costs, new methods
involving two rounds of combinatorial indexing have been developed7–10.
These methods combine droplet microfluidics and pre-indexing strate-
gies to increase cell throughput and sample multiplexing. Although
these approaches allow the overloading of droplets and effective
use of data from multiplets, current pre-indexing methods require
specific protocols for each modality and involve time-consuming
operations, which may impact the stability of data quality owing to
potential degradation and loss of target nucleic acid molecules.

In this Article, we propose a straightforward two-round combina-
torial indexing experimental workflow called UDA-seq. It uses droplet
microfluidics-based techniques for the first round of cell indexing, fol-
lowed by a second round of cell indexing after they are released from
droplets. While the microfluidic droplets do not isolate single cells,
they function as physical compartments similar to ‘wells’ in classical
combinatorial indexing approaches such as single-cell combinatorial
indexing RNA sequencing (sci-RNA-seq)11 and split-pool ligation-based
transcriptome sequencing (SPLiT-seq)12. As a result, most droplets
contain multiple cells or nuclei.

To get started (Fig. 1a and Extended Data Fig. 1), the following
steps are carried out: (1) Hundreds of thousands of cells or nuclei are
fixed and permeabilized before being encapsulated using a standard
microfluidics device. Different single-cell modalities are achieved by
using the appropriate reagents and chips. In the case of single-cell assay
for transposase-accessible chromatin (ATAC) and RNA sequencing
Multiome analysis, the nuclei are subjected to in situ Tn5 tagmentation
before loading to the microfluidics chip. (2) Inside these overloaded

droplets, targeted transcripts (for example, 3′-RNA and 5′-RNA) and
DNA (for example, open chromatin regions and specific histone modi-
fication region) are labeled with a droplet-specific barcode (round 1).
(3) The droplet emulsion is then broken to release the cells or nuclei,
which remain intact (Extended Data Fig. 2). (4) The nuclei or cells are
randomly mixed and aliquoted into 96/384-well PCR plates for a second
round of indexing by well-specific index PCR. (5) The PCR amplifica-
tion products from the two rounds of barcoding are pooled together
for purification and further library construction for sequencing. After
sequencing, the combination of the droplet- and well-specific barcodes
allows for the unique identification of targeted nucleic acid fragments
from the same single cell.

With  the  post-indexing  strategy,  we  can  smoothly  incorpo-
rate an additional round of barcoding through index PCR in the
well-established droplet-based single-cell method.

UDA-seq validation
Theoretically, employing two rounds of combinatorial barcoding has
the potential to generate between 9,600,000 and 38,000,000 bar-
code combinations. This entails one round of barcoding in droplets
followed by a subsequent round involving 96/384 well-specific bar-
coding. Notably, even when loading 500,000 cells, the collision rate
remains exceedingly low, and it can be reduced further to almost zero by
increasing the number of post-index barcodes (Extended Data Fig. 3a).
To assess the capability of UDA-seq for generating uniquely bar-
coded cells, we conducted species-mixing experiments. We utilized
the 10x Genomics Chromium droplet generator for droplet barcoding
owing to its widespread availability. Initially, we verified the feasibility
of 3′-RNA UDA-seq in fixed whole cells by mixing human Hela and mouse
NIH 3T3 cell lines in a 1:1 ratio. We loaded a total of 10,000 cells on the
10x Genomics Chromium system, followed by 96-well post-indexing.
We successfully obtained 6,245 high-quality single-cell transcriptomes,
representing 62% of the loaded cells. The majority of cells, each with
a unique two-round barcode, were identified as belonging to a sin-
gle species. The collision rate was only 1.23% (Fig. 1b), notably lower
than the expected rate of 6.29% when using the round 1 barcode only
(Extended Data Fig. 3b).

We also conducted UDA-seq testing using formaldehyde-fixed
nuclei with a loading nuclei number of 10,000. This included a com-
bination of human Hela, mouse NIH 3T3 and locust brain nuclei for
3′-RNA in a ratio of 1:1:1, or an equal mix of human Hela and mouse NIH
3T3 nuclei for Multiome. The cell recovery rates were approximately
57% for 3′-RNA and 37% for Multiome. Despite using only 16 barcodes in
the second round of labeling, the collision rates were very low, at 2.11%
for 3′-RNA and 0.67% for Multiome (Fig. 1c,d). The collision rates are
markedly lower than those observed when using the round 1 barcode
alone (Extended Data Fig. 3c,d). For the 3′-RNA UDA-seq experiments
involving three species, all three species were distinguished on the basis
of their transcriptomes (Extended Data Fig. 3e). In species-mixture
experiments for Multiome UDA-seq, human and mouse nuclei can be
effectively defined using either transcriptome or chromatin profiles
(Fig. 1d and Extended Data Fig. 3f).

UDA-seq performance and scalability
We evaluated UDA-seq to assess its practicality and ability to gener-
ate high-quality data in various primary tissues and clinical samples,
as well as to understand how its performance varies across different
modalities. Initially, we applied the Multiome (RNA and ATAC) UDA-seq
workflow to frozen cell lines and human clinical samples, including chol-
angiocarcinoma, lung cancer, pancreatic cancer, coronary artery and
kidney biopsy tissues (Extended Data Fig. 3g). When randomly taking
1/12 of cells as a sublibrary based on post-index and downsampling the
read depth to 20,000 reads per cell, the data obtained from Multiome
UDA-seq demonstrated quality comparable to that of the standard 10x
Multiome procedure within the same cell line or tissue type (Fig. 1e).

Nature Methods | Volume 22 | June 2025 | 1199–1212

1200

Articlehttps://doi.org/10.1038/s41592-024-02586-ya

b

Droplet barcoding (round 1)

Well-specific barcoding (round 2)

3’

Barcoded beads

1 2 3 4 5

6

7 8

9

10

11 12

Cells/nuclei

Partitioning oil

A
B
C
D
E
F
G
H

Fixed cells/nuclei
(10,000–1,000,000)

Droplet
emulsion

Release
cells

c

UDA (3’-RNA)
Whole cell (96 post-index)

UDA (3’-RNA)
Nuclei (16 post-index)

Human (52.86%)
Mouse (45.91%)
Multiplets (1.23%)

L
o
c
u

st U
MIs

MIs
n U
a
m
u
H

Mouse UMIs

0

10k

20k

30k

hg38 UMIs per cell

l
l
e
c
r
e
p
s
I
M
U
0
1
m
m

30k

20k

10k

0

Human
(37.52%)

Mouse
(28.05%)

Locust
(32.32%)

Multiplets
(2.11%)

h

Single-cell Multiome ATAC and RNA-seq

5’

Single-cell 5’-RNA-seq

V D J

Single-cell VDJ-seq

3’

Single-cell 3’-RNA-seq

gRNA

CRISPR screening gRNA-seq

UDA (Multiome)
Nuclei (16 post-index)

Human (56.76%)
Mouse (42.57%)
Multiplets (0.67%)

d

o
i
t
a
r

s
I
M
U
A
N
R
8
3
g
h

1.00

0.75

0.50

0.25

0

0

0.25

0.50

0.75

1.00

hg38 ATAC fragments ratio

PBMC (UDA, GEM-X 5′ Kit v3)

1,252

1,924

9,326 2,198

Tissue
6,872 9,199

1,598

1,738

1,316

1,873

1,971

2,180

1,069

1,622

Method

e

Cells

3,372

Cell line
4,961

0
1
g
o

l

)
s
e
n
e
g
d
e
t
c
e
t
e
d
(

0
1
g
o

l

)
k
a
e
p
n

i

s
d
a
e
r
(

3,076

2,386

3.7

3.0

2.2

1.5
4.6

3.0

1.5

0

150,018 cells

NK_BNC2+

NK_AOAH+

NK_CD56+

NK_CD56+_Cycling

T_CD4_Activated_CTL

T_CD8_EMRA

T_G/D_CM

B_Switched_Memory

Lymphoid_Progenitor

T_CD8_EM

Hematopoietic_Progenitor_CD34+/CD38+

T_G/D_EM

T_CD8_EMRA_Cycling

T_CD8_CM

B_Non−Switched_Memory

Plasma_Cell

T_CD8_CTL

T_Double_Negative

T_G/D_Immature_RTE

T_CD4_EM

T_MAI_Activated

T_MAI

T_CD4_Helper_1

UDA-seq

B_Naive_AFF3+

10x

T_CD8_Activated_CTL_Cycling
cDC2

T_CD4_Naive_IFN_stim

Monocyte_CD14+

T_Reg_EM

B_Naive_FCRL1+

T_CD4_Naive_Activated_ICOS+CD28+

B_Naive_COL19A1+

pDC

T_Reg_CM

T_CD8_Naive

T_CD4_Helper_2

T_CD4_Helper_0

T_CD4_CM

T_CD4_Follicular_Helper

T_CD4_Naive_TSHZ2+_ICOS+

T_CD4_Naive_IL7R+

Monocyte_CD16+

T_CD4_Naive_NELL2+_LEF1+

T_CD4_Naive_TSHZ2+_PLCL1+

2
P
A
M
U

UMAP1

i

NIH3T3

Hela

Kidney biopsy

Lung cancer Pancreatic cancer

Multiome

f

Frozen
(2 years)

Frozen
(6 months)

Fresh
frozen

11,309 4,311

1,429

2,180

Method

UDA-seq

10x

Cells

11,943 8,488

1,089

1,588

)
s
e
n
e
g
d
e
t
c
e
t
e
d
(

0
1
g
o

l

3.5

3.0

2.5

2.0

g

o
i
t
a
r
n
o
i
t
c
e
t
e
D

1.00

0.75

0.50

0.25

0

BCR

TCR

0.98

0.93

0.92

0.8

0.6

0.45

Method

UDA-seq

10x

NK_CD56+_Cycling

Lymphoid_Progenitor

Hematopoietic_Progenitor_CD34+/CD38+

T_CD8_Activated_CTL_Cycling

Kit_v2

Kit_v2

Kit_v1

Kit_v2

PBMC (5’-RNA)

Kit_v2

Kit_v3

Kit_v2

Kit_v2

Kit_v3

Kit_v2

PBMC (VDJ)

2
P
A
M
U

UMAP1

Fig. 1 | The workflow of UDA-seq and its performance across diverse modalities
and samples. a, The UDA-seq workflow involves two rounds of barcoding.
b–d, Species-mixing experiments by using single-cell 3′-RNA UDA-seq with
96-well post-indexing (b), single-nucleus 3′-RNA UDA-seq with 16 well post-
indexing (c) and single-nucleus scMultiome UDA-seq with 16 well post-indexing
(d). e,f, Violin plots showing the distribution of genes (RNA) and peak reads
(ATAC) detected by UDA-seq scMultiome and 10x Genomics (e) as well as UDA-seq
sc5′-RNA (f). Box plots show the interquartile range with the median marked.

The whiskers extend up to 1.5 times the interquartile range; the outliers are not
displayed. The median number of genes detected is shown at the top of each
violin plot. g, A comparison between UDA and 10x Genomics for scVDJ-seq. The
T-cell receptor (TCR) and B-cell receptor (BCR) detection ratio for UDA with
Next GEM (Kit_v2) and GEM-X (Kit_v3), and the 10x Next GEM. h, The ultrahigh-
throughput 5′-scRNA UDA-seq analysis of over 150,000 cells from a single donor,
identifying 44 distinct cell types. The UMAP plot is color-coded to represent
these cell types. j, Rare cell types, identified with cell type labels.

Nature Methods | Volume 22 | June 2025 | 1199–1212

1201

Articlehttps://doi.org/10.1038/s41592-024-02586-y

We performed single-cell 5′-RNA and VDJ UDA-seq on fixed whole
cells of peripheral blood mononuclear cells (PBMCs). Upon down-
sampling the depth to 50k reads per cell, we detected a median of
1,089 genes per cell in PBMCs frozen for 2 years and 1,588 genes per
cell in PBMCs frozen for 6 months. These results are slightly lower
and comparable to the standard procedure for the same kit version
of 10x Genomics (Fig. 1f). Furthermore, we detected approximately
45% T cells with either T cell receptor (TCR)α or TCRβ chains and 80%
B cells with either heavy or light chains. These percentages are slightly
lower than the standard procedure but still highly informative (Fig. 1g).
The relatively lower detection of the TCR in UDA-seq may be a result
of its low expression level or specific RNA structural features. Further
optimization of fixation conditions and reverse transcription (RT)
reagents or selection of a longer sequencing read length may enhance
the detection.

We  evaluated  scalability  by  upgrading  our  reagents  to  the
10x Genomics GEM-X Reagent Kits v3 and instrumentation to the
Chromium X, doubling the droplet numbers compared with the pre-
vious system. We conducted a large-scale single-cell UDA-seq 5′-RNA
and VDJ with GEM-X (v3) reagents by loading 300,000 methanol-fixed
PBMCs frozen for 2 years into a single channel followed by 96-well
post-indexing. A total of 170,000 cells were recovered, of which 150,018
cells met the quality control criteria. When downsampling the read
depth to 50,000 reads per cell, we observed a median of 1,296 genes
per cell (Extended Data Fig. 3h). A sublibrary, representing 1/12 cells of
the entire library, was subjected to deep sequencing to achieve read
coverage of 178,000 reads per cell. We identified a median of 3,589
unique molecular identifiers (UMIs) and 1,822 genes per cell (Extended
Data Fig. 3i), a median of 60.3% T cells with TCRα and TCRβ chains, and
93.4% B cells with heavy and light chains (Fig. 1g). This indicates that
optimizing the reagent and increasing the number of droplets can be
directly integrated into the existing UDA-seq workflow without addi-
tional configuration. The enhanced cellular recovery enables a more
thorough analysis of cell populations. Reference mapping identified 44
distinct cell states (Fig. 1h), including some rare populations account-
ing for less than 0.1% of the sample. These uncommon cell states, such
as activated T-cell states, cycling cell states and progenitor cell types,
may be overlooked when using methods that have lower cell through-
put (Fig. 1i and Extended Data Fig. 3j).

These results demonstrate that plate-based post-indexing is com-
patible with droplet-based barcoding. They also show that UDA-seq is
reliable when used with whole cells or nuclei, fresh cell lines or frozen
complex tissue, and that it is compatible with co-assaying of different
single-cell modalities.

Multiome UDA-seq analysis on kidney frozen biopsy
After successfully confirming the feasibility and scalability of UDA-seq,
we proceeded to assess its potential for increasing sample throughput
and utilization in a large-scale cohort study. We employed Multiome
UDA-seq to study chromatin accessibility and gene expression in
kidney diseases. We collected 35 frozen human samples, including
10 time-zero transplant biopsies from healthy donors and 25 biopsies
from patients with over 10 different diagnoses (Supplementary Table 1).

These diseases were categorized on the basis of their underlying patho-
physiological mechanisms, covering immune-mediated glomerulopa-
thies (12 donors), metabolic-related renal diseases (5 donors) and other
types (8 donors). Additionally, we assessed the samples on the basis of
clinical symptoms, such as the presence of massive proteinuria (≥3.5 g
per 24 h) and impaired kidney function (Fig. 2a).

We addressed the challenge of working with ultralow start-
ing materials by pooling 35 samples to isolate and fix nuclei. Each
disease sample, equivalent to around one-fifth of a 16G or 18G needle
biopsy (approximately 2–3 mm in length), was sourced from the
tissue remaining after diagnostic procedures. Subsequently, the
nuclei suspension underwent two channels of Multiome UDA-seq with
96 barcodes in post-indexing in a single batch (Fig. 2b). Sample demulti-
plexing was carried out using natural genetic variation13. As a result,
we obtained a total of 207,789 cells that met high-quality criteria for
both single-nucleus RNA sequencing (snRNA-seq) and single-nucleus
ATAC sequencing (snATAC-seq) readouts, with a median of 1,707 and
1,518 genes per cell, and 9,881 and 7,163 fragments in peak per cell for
patients and healthy controls, respectively. These results are compa-
rable to the data quality from the standard 10x Multiome procedure
(Figs. 1e and 2c and Extended Data Fig. 4a).

The data from the two channels shows a high degree of consistency
(Extended Data Fig. 4b–d). After unsupervised clustering, a total of 60
cell clusters for the snRNA-seq and 68 cell clusters for the snATAC-seq
were identified (Fig. 2d). These clusters were then categorized into 54
subclasses by leveraging a well-annotated human kidney scRNA-seq
reference dataset14 (detailed cell types provided in Methods ‘Kidney
snRNA-seq part analysis’ section). The specificity of our snRNA-seq
data was demonstrated using previously characterized cell markers
(Fig. 2e; for detailed genes, see Supplementary Table 2), and specific
peaks were identified in the snATAC-seq within these cells (Fig. 2f).
Subsequent integrative analysis of both modalities using the weighted
nearest neighbor3 method revealed a more refined pattern of cell
clustering (a total of 253 cell clusters) as identified by the aforemen-
tioned single-modality analysis (Fig. 2g). Furthermore, employing
an orthogonal approach, ArchR15, by combining co-accessibility and
RNA integration, allowed the identification of 98,698 Peak2Gene links.
These links show a strong correlation between chromatin accessibility
and target gene expression, resulting in 25 unique modules across all
cell types (Fig. 2h), which confirms the high quality of the data.

Key cells and regulators linked to massive proteinuria
Massive proteinuria corresponds to protein of more than 3.5 g in 24 h
urine. Our data include measurements of the extent of proteinuria
for each donor and matched single-cell profiling of primary tissue.
With a sample size of 35, this cohort enables us to determine which
specific cellular subpopulation is most relevant to the clinical signs
observed in proteinuric kidney diseases. To address this question, we
modified an algorithm called Scissor16, which is a method for identify-
ing subpopulations of cells associated with specific phenotypes from
single-cell data. Surprisingly, Scissor identified podocytes (POD) as
the highest-ranking candidate, and the signal seems quite unique and
specific (Fig. 3a). Notably, the number of PODs represented less than

Fig. 2 | Single-nucleus RNA and ATAC joint profiling from human kidney
mini biopsies. a, A total of 25 renal biopsy samples from patients with kidney
disease and 10 healthy control samples from kidney transplantation donors were
utilized for Multiome UDA-seq analysis. b, A schematic of the joint snATAC-seq
and snRNA-seq analysis for kidney biopsy samples. c, The data quality of the
Multiome UDA-seq, showing the distributions of gene number per cell (top left)
and FiRP per cell (top right) for patients with disease (n = 25) and healthy control
donors (n = 10). Box plots show interquartile range with the median marked.
The whiskers extend up to 1.5 times the interquartile range, and the outliers are
not displayed. Bottom left: normalized insertion profile around transcriptional
start sites for patients with disease and healthy donors. Bottom right: the length

distribution of fragments from patients with disease and healthy donors.
d, UMAP plots with cells colored by clusters, defined by snRNA-seq alone (top)
or snATAC-seq alone (bottom). e, A dot plot showing differentially expressed
genes across the major cell types. f, A track plot showing differentially accessible
regions across the major cell types. g, UMAP plots with cells colored by clusters,
defined by weighted nearest network joint analysis of snRNA-seq and snATAC-
seq. h, Peak2Gene links (P2GLinks) in kidney snRNA-seq and snATAC-seq profiles
shown in a heat map with 25 modules. Each row represented a single cell, grouped
by its cell type. Panel b was created using BioRender.com. Full names for all
abbreviations of cell types in panels d–h can be found in the Methods.

Nature Methods | Volume 22 | June 2025 | 1199–1212

1202

Articlehttps://doi.org/10.1038/s41592-024-02586-yb

c

Cells

83,243

124,546

a

d

× 10

× 25

Control

Kidney diseases

~1/5 biopsy
(2–3 mm)

Immune
(n = 12)

Metabolic
(n = 5)

Other
(n = 8)

n = 35

Pool

Impairment
(24 h proteinuria ≥3.5 g)

No Impairment

UDA-seq
Round 2 (96 index)
Two channels

sn3’-RNA-seq
+
snATAC-seq

3k

2k

1k

r
e
b
m
u
n
e
n
e
G

d
e
z
i
l
a
m
r
o
N

e
l
i
f
o
r
p
n
o
i
t
r
e
s
n

i

12

8

4

0

With
disease

Healthy

With
disease
Healthy

124,546

Cells 83,243
0.8
0.7
0.6
0.5
0.4
0.3

i

P
R
F

With
disease

Healthy

With
disease
Healthy

f
o
e
g
a
t
n
e
c
r
e
P

s
t
n
e
m
g
a
r
f

0.6

0.4

0.2

0

−2k −1k

0 1k

2k

200 400 600

Distance
from center (bp)

ATAC-seq
fragment size (bp)

2.5
e
x
2.0
p
1.5
r
e
1.0
s
0.5
s
i
0
o
n−0.5

A
v
e
r
a
g
e

25
50
75

e
x
p
r
e
s
s
e
d

P
e
r
c
e
n
t

e

PEC
DTL
PC
VSM/P
IMM
FIB
EC
DCT
CNT
IC
POD
PT
TAL

f

h

RNA profile (207,789 cells)

EC−LYM

cycEC

EC−AEA

EC−DVR
EC−GC

EC−AVR

MYOF

aFIB

M−FIB

EC−PTC

MDC
cycMNP

REN

MAC−M2

MC

FIB
VSMC/P

VSMC

M−TAL

C−TAL

MD

cDC

ncMON

B

PL

T

SC/NEU

PEC

POD

dPT

ATL

DTL3

PT−S3

aTAL1

DTL1

DTL2

DCT1

DCT2

CNT

IMCD

cycCNT

cycPT

CCD−PC

CNT−PC

OMCD−PC

PT−S2

PT−S1

aPT

tPC−IC

CNT−IC−A

dC−IC−A

OMCD−IC−A

CCD−IC−A

IC−B

2
P
A
M
U

UMAP1

ATAC profile (207,789 cells)

dC−IC−A

IC−B

CCD−IC−A

OMCD−IC−A

CNT−IC−A

EC−AEA

EC−DVR
cycEC

EC−GC

EC−PTC

EC−AVR

EC−LYM

tPC−IC

DCT1

M−TAL

C−TAL

MD

ATL

aFIB

FIB

M−FIB

POD

ncMON

DCT2
CNT

aTAL1
cycCNT

CNT−PC
CCD−PC

IMCD
OMCD−PC

DTL3

PT−S1

PT−S2
PT−S3

dPT

aPT

cycPT

PEC

DTL1

DTL2

2
P
A
M
U

g

MDC
MAC−M2

cycMNP
B

cDC

PL

T

UMAP1

ATAC + RNA profile (207,789 cells)

CCD−IC−A

CNT−IC−A
OMCD−IC−A

dC−IC−A

EC−GC

PL

aFIB
FIB

cycEC

EC−PTC
EC−AVR

B

T

EC−AEA

M−FIB

EC−LYM

EC−DVR

dPT

PT−S3

PT−S1

tPC−IC

VSMC

OMCD−PC

REN
MC

IMCD

CCD−PC

CNT−PC

cycCNT

DCT1

DCT2

CNT

ncMON

PT−S2

aTAL1

POD

aPT

DTL3

ATL

MD

cycMNP
MDC
MAC−M2

cDC

IC−B

cycPT

DTL2

DTL1

2
P
A
M
U

UMAP1

SC/NEU

PEC

C−TAL

M−TAL

2
P
R
L

D
O
M
U

N
B
U
C

O
R
P
T
P

Q
R
P
T
P

K
N
L
C

1
A
2
1
C
L
S

7
A
6
2
C
L
S

1
G
T
N
S

1
A
8
C
L
S

3
A
2
1
C
L
S

7
C

6
M
P
R
T

2
B
D
L

N
C
M
E

1
R
G
E
N

5
1
P
A
G
H
R
A

C
R
P
T
P

C
1
A
N
C
A
C

1

O
B
O
R

B
1
R
P
M
B

4
A
Y
E

2
P
X
O
F

H
F
C

5
A
4
4
C
L
S

2
A
1
H
D
L
A

CNT (n = 10,587)
DCT (n = 17,419)
DTL (n = 3,741)
EC (n = 13,660)
FIB (n = 3,482)
IC (n = 10,680)
IMM (n = 9,232)
PC (n = 7,736)
PEC (n = 2,085)
POD (n = 1,239)
PT (n = 74,696)
TAL (n = 51,073)
VSM/P (n = 2,041)

25

2324

22

2021

19

18

17

16

15

14

13

12

1011

23456789

1 groupBy

ATAC Z scores
98,698 P2GLinks

−2
2
RNA Z scores
98,698 P2GLinks

−2

aFIB
aPT
aTAL1
B
C−TAL
CCD−IC−A
CCD−PC
cDC
CNT
CNT−PC
cycPT
DCT1
DCT2
dPT
DTL1
DTL2
EC−AEA
EC−AVR
EC−DVR
EC−GC
EC−LYM
EC−PTC

2
FIB
IC−B
M−FIB
M−TAL
MAC−M2
MC
MD
MDC
MYOF
ncMON
OMCD−IC−A
OMCD−PC
PEC
PL
POD
PT−S1
PT−S2
PT−S3
T
VSMC
VSMC/P

Nature Methods | Volume 22 | June 2025 | 1199–1212

1203

Articlehttps://doi.org/10.1038/s41592-024-02586-yCLSTN2SLC12A3MGAT3PTPRBLRIT1RGRDMRT2ZNF683SEMG2KIRREL3PTPRQCYP4A11GP2UMODSPEG

0.6% of our data (Fig. 3b). Moreover, cells positively associated with
proteinuria (proteinuria positive cells) identified by Scissor were
notably  enriched  in  donors  with  proteinuria  greater  than  3.5 g
(Fig. 3c). Genes differentially expressed in proteinuria positive cells
were employed as a proteinuria-associated signature (for detailed
genes, see Supplementary Table 3), which was positively correlated
with the magnitude of proteinuria in the donors (Fig. 3d). These
results further demonstrate that UDA-seq is very reliable in depicting
the population scale of a complex cellular system.

Podocytes (PODs) are specialized cells that are crucial for estab-
lishing and maintaining the glomerular filtration barrier17–19. Our
research findings support previous studies on the important role
of podocyte injury in massive proteinuria. We delved into the het-
erogeneous subpopulations of PODs involved in this process, as well
as the underlying molecular mechanisms and regulatory networks.
Through unsupervised reclustering, we identified six distinct sub-
clusters of PODs (Fig. 3e). Notably, subcluster 1 emerged as a crucial
contributor to proteinuria by Scissor analysis (Fig. 3f and Extended
Data Fig. 5a). We found that the highly expressed genes in subcluster
1 were intricately linked to the activation of the transforming growth
factor-beta signaling pathway (Fig. 3g). This observation aligns with
earlier findings indicating that transforming growth factor-beta acti-
vation triggers a dedifferentiation process of podocytes resembling
the epithelial-to-mesenchymal transition, which may contribute to
glomerular fibrosis20–22.

A better understanding of the molecular regulatory networks of
POD dysfunction could help in developing podocyte-targeted thera-
peutic approaches. We used SCENIC+23 to infer enhancer-driven gene
regulatory networks for proteinuria-associated POD subpopulations.
SCENIC+ identified 17 activator eRegulons and 7 repressor eRegulons,
including transcription factors (TFs) known to be associated with
kidney disease (Extended Data Fig. 5b). For example, LMX1B muta-
tions may cause glomerulopathy17,24,25, and high expression of E2F3 has
been linked to worse pathological characteristics in renal cancer17,26,27.
SCENIC+ then constructed a putative regulatory network, demonstrat-
ing the cooperative relationship between E2F3, ZNF398 and PLAG1
(Fig. 3h). Upregulation of DAAM2, MYLK3 and SCGB2B2 by transcrip-
tion factor E2F3 was observed in massive proteinuria-associated POD
(Extended Data Fig. 5c).

We used CellChat28 to analyze cell-to-cell communication and
found that patients with massive proteinuria had increased commu-
nication between podocytes (as a source of signals) and EC-GCs (as
a receiver of signals) compared with healthy controls (Fig. 3i). Addi-
tionally, we observed enhanced communication of the FGF signaling
pathway and reduced communication of the VEGF signaling pathway
in these patients (Fig. 3j). These results are consistent with previous
reports indicating the importance of podocyte-derived VEGF signaling

for the survival and function of EC-GCs29, as well as clinical observations
that VEGF inhibition leads to endothelial swelling and thrombotic
microangiopathy30.

Key cells and regulators linked to renal function impairment
Chronic kidney disease (CKD) and acute kidney injury (AKI) are increas-
ingly understood as closely linked syndromes31–35. Thus, we grouped
patients with AKI and CKD together as having ‘renal impairment’ to
study the types of cells most impacted. We employed the Scissor
algorithm-based approach to determine the cell types associated
with kidney function impairment. The analysis showed that the top
four most affected cell types in both immune-associated renal injury
and metabolism-associated renal injury were all different endothelial
cells. The top-ranking cell type was EC-GCs (Fig. 4a,b), a critical part of
the glomerular filtration barrier. Additionally, the ‘renal impairment’
signature (for detailed genes, see Supplementary Table 4) calculated by
Scissors displayed a negative correlation with the patient’s glomerular
filtration rate (eGFR), a crucial negative indicator of renal filtration
capacity, confirming the accuracy of our calculation (Fig. 4c,d). Upon
reclustering of EC-GCs, six subclusters with specific marker genes were
identified (Fig. 4e,f). Interestingly, cells of metabolic-related injury
were predominantly found in subcluster 0 (Fig. 4g), while those of
immune-related injury were enriched in subcluster 3 (Fig. 4h).

In our analysis using SCENIC+, we effectively examined the
eRegulon of EC-GC subpopulations associated with renal impairment
(Fig. 4i) and successfully constructed gene regulatory networks (GRNs).
Our investigation revealed a collaborative relationship between
RARB and KLF9 in immune injury positive cells (Fig. 4j). Notably, abnormal
levels of CCND336–39 and PKT2840, the target genes of KLF9, have been
previously linked to immune regulation and immune-mediated dis-
eases. These compelling findings (Fig. 4k) suggest that these genes hold
potential therapeutic targets for immune-mediated glomerulopathy.
In  summary,  we  have  effectively  generated  top-quality
pan-nephropathy scMultiome data using UDA-Seq, leading to a remark-
able 8- to 9-fold reduction in the cost of library construction per cell
or 15- to 20-fold per sample (aiming for approximately 5,000 cells
per sample). See Extended Data Figs. 6 and 7 for a more detailed cost
comparison. In addition, it is worth noting that the enhanced cellular
and sample throughput make pooling of tiny samples feasible and
multimodal data from rare cell types meaningful.

RNA and VDJ UDA-seq of frozen PBMCs from human aging
cohort
We proceeded to apply UDA-seq to the study of paired gene expression
and adaptive immune receptor repertoire from the same cell, also
referred to as FIPRESCI-seq210. We gathered and applied single-cell
RNA and VDJ UDA-seq to PBMCs from 38 female donors aged 20–65

Fig. 3 | Rare cell subpopulations associated with proteinuria identified using
UDA-seq. a, A violin plot displaying the distribution of positive proteinuria
signature scores across different cell types. Box plots show the interquartile
range with the median marked. The whiskers extend up to 1.5 times the
interquartile range, and the outliers are not displayed. b. Left: the anatomical
structure of the glomerulus, with arrows indicating a podocyte and EC-GC.
Right: UMAP embedding, colored by positive proteinuria signature score,
highlighting the enrichment of the proteinuria signature in the podocyte. c, A
heatmap providing a visual representation of the enrichment of cells related to
proteinuria positivity or negativity across different donors. The colors in the
heatmap correspond to the enrichment scores. Donors were categorized into
three groups: healthy, those with 24 h urinary protein levels ≥3.5 g and those with
levels <3.5 g. d, A box plot depicting donors’ positive proteinuria signature scores
across the control (n = 10), low proteinuria (n = 19) and high proteinuria (n = 6)
group. The box plots show the interquartile range with the median marked. The
whiskers extend up to 1.5 times the interquartile range. P values were calculated
using the two-sided t test. *Bonferroni-adjusted P < 0.05. **Bonferroni-adjusted

P < 0.01. e. Podocyte reclustering, revealing six subclusters. f, UMAP embedding,
colored to indicate cells positively related to proteinuria. g, A Volcano plot
showing marker genes of subcluster 1 for podocytes. P values were calculated by
the two-sided Wilcoxon rank sum test. The vertical dashed lines represented −1
or 1 log2FC value, the horizontal dashed line represented p-value = 0.05. h, The
key eRegulon identified by SCENIC+. Bold and enlarged gene symbols represent
transcription factors (TFs), squares represent peak regions and gene symbols
at the graph’s edges represent regulated genes. i, A heatmap illustrating the
differential cell–cell communication strength of proteinuria donors compared
with healthy control donors. j, A bar plot illustrating that the podocyte-to-EC-GC
communication changes between donors with proteinuria and healthy control
donors in the fibroblast growth factor (FGF), vascular endothelial growth factor
(VEGF), neuregulins (NRG) and platelet-derived growth factor (PDGF) signaling
pathway. The FGF signaling pathway exhibits an increase in proteinuria donors.
Panel b was created using BioRender.com. Full names for all abbreviations of cell
types in panels a,b,i can be found in the Methods.

Nature Methods | Volume 22 | June 2025 | 1199–1212

1204

Articlehttps://doi.org/10.1038/s41592-024-02586-ya

e
r
o
c
s
e
r
u
t
a
n
g
i
s
a
i
r
u
n
e
t
o
r
P

i

1.5

1.0

0.5

0

c

b

Proteinuria signature score

2
P
A
M
U

UMAP1

EC-GC

POD (<0.6%)

e

POD

1

1.5

1.0

0.5

0

0

1

2

3

4

5

)
6
3
3
=
n
(
B
I
F
a

)
9
3
2
,
1

=
n
(

D
O
P

)
5
8
0
,
2
=
n
(

C
E
P

)
9
5
3
=
n
(
B
I
F
−
M

)
4
2
6
,
2
=
n
(
B
I
F

)
9
4
9
,
1

=
n
(

D
M

)
9
7
4
=
n
(

C
M
S
V

)
2
9
2
,
6
1

=
n
(

1
T
C
D

)

0
0
8
=
n
(

C
M

)
2
6
7

=
n
(
P
/
C
M
S
V

)
2
2
4
=
n
(

A
E
A
−
C
E

)
7
2
1
,
1

=
n
(
2
T
C
D

,

)
1
5
3
5
=
n
(

1
L
A
T
a

)
1
2
9
=
n
(
2
L
T
D

)
3
3
0
,
1

=
n
(
R
V
D
−
C
E

,

)
1
6
6
8
=
n
(
T
N
C

)
6
2
5
,
1

=
n
(
R
V
A
−
C
E

)
6
2
9
,
1

=
n
(

C
P
−
T
N
C

)
4
0
2
,
4
=
n
(

C
P
−
D
C
M
O

)

0
6
4
9
1

,

=
n
(
T
P
a

)
8
6
1
,
1

=
n
(

C
G
−
C
E

,

)
2
3
5
3
=
n
(

C
P
−
D
C
C

,

)
2
2
3
9
=
n
(

C
T
P
−
C
E

)

0
2
8
,
2
=
n
(

1
L
T
D

)
1
9
7
,
2
=
n
(
B
−
C

I

)
8
2
5
=
n
(
T
P
d

,

)
7
1
0
3
3
=
n
(
L
A
T
−
C

)
6
5
7
,
0
1

=
n
(
L
A
T
−
M

)
6
3
9
=
n
(
2
M
−
C
A
M

)
5
3
2
,
5
1

=
n
(
3
S
−
T
P

)
7
0
3
,
7

=
n
(

A
−
C
I
−
D
C
C

)
2
8
5
=
n
(

A
−
C
I
−
D
C
M
O

,

)
8
5
8
4
=
n
(
T

)
5
1
6
,
1

=
n
(
B

)
8
5
7

=
n
(
L
P

)
2
8
7

=
n
(

C
D
M

,

)
7
9
8
8
=
n
(
2
S
−
T
P

,

)
3
1
5
0
3
=
n
(

1
S
−
T
P

*

**

d

0.12

e
r
u
t
a
n
g
i
s
a
i
r
u
n
e
t
o
r
P

i

0.09

0.06

0.03

Enrichment
Score

4
2
0
−2
−4

24 h proteinuria

<3 g
≥3 g
Control

f

PB456
PB263
PB350
PB462
PB481
PB242
PB231
PB341
PB234
PB354
PB346
PB458
PB233
PB449
PB430
PB465
PB197
PB235
PB262
PB238
PB448
PB203
PB334
PB457
PB373
WB51
WB48
WB42
WB44
WB45
WB47
WB49
WB43
WB50
WB46

Proteinuria positive
Background

Proteinuria negative
24 h proteinuria

h

LRRC8A

ZFYVE28

DOCK3

SCGB2B2

CYB5B

KLHL29

PXK

IQSEC1

DAAM2

PLAG1

E2F3

FAM89A

USP33

ZNF398

TEAD4

B3GALNT2

DNAJC9

EHD4

MYLK3

GABRA2

NAB1

GRIK4

Low proteinuria
Control

High proteinuria

Proteinuria positive

2
P
A
M
U

UMAP1

g

Cluster1 marker genes

NS

log2 FC

P value

P value and log2 FC

Total of 3,488 variables

P
0
1
g
o
l
–

20

10

0

Background

Proteinuria positive

RYR2

FRAS1

COL4A1

PDE1A

HNRNPF
KAZN

GPC6

PTPRQ

ARRDC4

LINC02006
DOCK3

AL356124.1
PLCB4

FAM153CP
CENPP
AF235103.3
EOGT

G3BP2

AC022126.1
PDGFA

CDH12

2
P
A
M
U

UMAP1

i

Differential interaction strength

0.8
0.6
0.4
0.2
0

B

)
r
e
d
n
e
s
(

s
e
c
r
u
o
S

EC−AEA

EC−AVR

EC−DVR

EC−GC

EC−LYM

EC−PTC

POD

T

B

EC−AVR
EC−DVR
EC−AEA

EC−LYM
EC−GC
EC−PTC

POD T

−2.5

0

2.5

log2 fold change

j

FGF

VEGF

NRG

PDGF

e
u
l
a
v
e
v
i
t
a
l
e
R

4

2

0

−2

−4

0

.

5
0

0
.
1

24 h UP ≥3.5 g

Control

0

2.5

5.0

7.5

Information flow

Nature Methods | Volume 22 | June 2025 | 1199–1212

1205

Articlehttps://doi.org/10.1038/s41592-024-02586-y

Immune-related impairment signature

)
3
3
6
=
n
(

C
M

)
1
2
6
,
1

=
n
(
B
I
F

)
3
6
9
=
n
(
R
V
A
−
C
E

)
3
0
3
=
n
(

A
E
A
−
C
E

)
1
3
7

=
n
(
R
V
D
−
C
E

)
6
1
9
=
n
(

C
G
−
C
E

,

)
5
0
3
6
=
n
(

C
T
P
−
C
E

)

0
5
5
=
n
(
P
/
C
M
S
V

)
7
4
8
,
2
=
n
(

C
P
−
D
C
C

)
6
0
7
,
2
=
n
(

C
P
−
D
C
M
O

)
5
1
2
=
n
(
B
I
F
a

)
7
6
3
=
n
(

C
M
S
V

)
4
9
2
=
n
(
B
I
F
−
M

)
1
6
4
,
1

=
n
(

C
P
−
T
N
C

)
3
7
0
3
1

,

=
n
(
3
S
−
T
P

)
9
0
4
=
n
(
B

)
5
9
2
,
1

=
n
(
T

)
1
3
3
=
n
(

C
D
M

)

0
7
5
=
n
(
2
M
−
C
A
M

)
1
7
8
=
n
(

D
O
P

)
1
9
5
,
1

=
n
(

C
E
P

)
3
9
2
,
5
=
n
(
T
N
C

)
3
4
1
,
1

=
n
(

D
M

)
3
3
2
=
n
(
L
P

)
8
5
2
=
n
(
T
P
d

)
8
9
8
,
2
=
n
(

1
L
A
T
a

)
2
9
7

=
n
(
2
L
T
D

)
3
3
5
0
1

,

=
n
(
T
P
a

)
5
8
2
,
2
=
n
(

1
L
T
D

)
1
5
7
,
6
=
n
(
2
S
−
T
P

)
4
1
5
=
n
(

A
−
C
I
−
D
C
M
O

)
2
7
8
=
n
(
2
T
C
D

)
5
2
1
,
2
=
n
(
B
−
C

I

)
2
2
6
,
2
1

=
n
(

1
T
C
D

)

0
6
1
,
4
2
=
n
(

1
S
−
T
P

,

)
6
3
5
6
2
=
n
(
L
A
T
−
C

)
2
9
4
0
1

,

=
n
(
L
A
T
−
M

)
9
2
1
,
5
=
n
(

A
−
C
I
−
D
C
C

Metabolic-related impairment signature

a

e
r
o
c
s
e
r
u
t
a
n
g
S

i

1.0

0.5

0

b

e
r
o
c
s
e
r
u
t
a
n
g
S

i

0.75

0.50

0.25

0

−0.25

)
8
9
3
=
n
(
R
V
D
−
C
E

)
4
1
7

=
n
(
R
V
A
−
C
E

)
2
0
4
=
n
(

C
G
−
C
E

,

)
3
5
0
3
=
n
(

C
T
P
−
C
E

)
7
1
2
,
3
=
n
(

A
−
C
I
−
D
C
C

)
7
6
4
=
n
(

A
−
C
I
−
D
C
M
O

)

0
6
6
=
n
(

C
P
−
T
N
C

)
1
4
4
,
2
=
n
(

C
P
−
D
C
C

)
8
9
2
,
1

=
n
(

C
P
−
D
C
M
O

)
4
9
2
=
n
(

C
M

,

)
6
3
3
3
=
n
(
T
N
C

)
6
7
5
,
1

=
n
(
B
−
C

I

)
2
8
3
=
n
(
P
/
C
M
S
V

)

0
9
2
=
n
(
B
I
F
−
M

)
9
5
2
=
n
(

C
M
S
V

)
2
9
3
,
1

=
n
(
B
I
F

)
1
9
5
=
n
(
2
T
C
D

)
6
5
1

=
n
(

C
D
M

)
7
5
3
=
n
(

D
O
P

)

0
8
3
=
n
(
2
M
−
C
A
M

)
1
4
7

=
n
(
T

)
8
5
2
=
n
(
B

)

0
8
1

=
n
(
L
P

)
4
3
0
,
1

=
n
(

C
E
P

,

)
5
6
6
8
=
n
(

1
T
C
D

)
8
9
0
,
1

=
n
(

1
L
A
T
a

)
1
3
8
=
n
(

D
M

)
5
5
1

=
n
(
T
P
d

)
3
7
7

=
n
(
2
L
T
D

)
9
2
2
,
2
=
n
(

1
L
T
D

,

)
5
3
9
5
=
n
(
T
P
a

)
7
4
1
,
9
1

=
n
(
L
A
T
−
C

,

)
2
9
8
9
=
n
(
L
A
T
−
M

,

)
6
8
5
8
=
n
(
3
S
−
T
P

)
5
3
6
,
7
1

=
n
(

1
S
−
T
P

)
1
4
1
,
4
=
n
(
2
S
−
T
P

3

2

0

1

4

5

Metabolic positive
Other

Immune positive
Other

Cluster 0

h

r
e
t
s
u
C

l

3

1

2

0

4

−3

Cluster 3

0

−2

1
−1
Immune impairment
enrichment score

EPS15L1

PALD1

TIMP3

OSBPL5

SLC6A6

SYNE1

MRPL33

WNK1

TACC1

OTUD7A

GFOD1

LRRFIP1

ABLIM2

ZBTB46

KLF9

RARB

ITGA9

RXFP1

FKBP5

PTK2B

GALNT14 CCND3
PLAT

j

Scaled TF
expression

1

0.75

0.50

0.25

0

Scaled target
region enrich

0
0.25
0.50
0.75
1

−4

−1

−2

−3

1
Metabolic impairment
enrichment score

0

ZNF704_+_(55r)
TCF7L2_extended_+_(2r)
SNAPC4_extended_+_(4r)
AHR_+_(32r)
ZGPAT_+_(28r)
RARB_+_(121r)
KLF9_+_(265r)
CREB5_+_(17r)
SREBF2_+_(5r)
SOX5_extended_+_(13r)
MEF2A_+_(7r)
KLF12_+_(213r)
PBX1_+_(9r)

ZNF704_-_(17r)
AHR_-_(6r)
ZGPAT_-_(38r)
RARB_-_(12r)
KLF9_-_(33r)
CREB5_-_(4r)
SREBF2_-_(2r)
SOX5_extended_-_(4r)
MEF2A_-_(1r)
KLF12_-_(50r)
PBX1_extended_-_(4r)

A
c
t
i
v
a
t
o
r

R
e
p
r
e
s
s
o
r

0
r
e
t
s
u
l
c

1

r
e
t
s
u
l
c

2
r
e
t
s
u
l
c

3
r
e
t
s
u
l
c

4
r
e
t
s
u
l
c

5
r
e
t
s
u
l
c

e

g

i

2
P
A
M
U

UMAP1

r
e
t
s
u
C

l

0

2

4

1

3

c

e
r
o
c
s

t
n
e
m

r
i
a
p
m

i

e
n
u
m
m

I

d

e
r
o
c
s

t
n
e
m

r
i
a
p
m

i

c
i
l

o
b
a
t
e
M

f

Immune impairment

0.06

PB233

r = –0.908. P = 4.47 × 10

–5

0.03

PB456

PB197

PB262

PB448

0

−0.03

−0.06

PB341

PB234

PB346

PB263

PB354

PB462

PB449

25

50

75

100

125

eGFR

Metabolic impairment

PB235

0.05

PB350

PB203

r = –0.99, P = 0.00125

0

PB465

PB458

25

50

75

100

eGFR

−0.05

r
e
t
s
u
C

l

5

4

3

2

1

0

1
P
I
L
I
F

4
N
T
N

3
T
I
L
S

1
B
T
N
S

2
O
T
E
N

3
A
3
1
P
T
A

3
F
F
A

2
1
F
L
K

C
F
G
E
V

6
A
6
C
L
S

1
L
1
D
H
K
P

5
P
B
K
F

2
M
I
L
B
A

3
R
A
C
B

2
S
O
N

K
P
N
R
N
H

2
F
L
S

6
D
A
M
S

5
P
A
K
C
N

8
2
P
A
G
H
R
A

3
V
A
N

2
T
R
L
F

2
C
S
A

I

2
G
P
S
H

1
G
E
R
T
E
R

2
A
2
P
A

9
1
2
M
E
M
T

1
.
8
1
5
0
9
0
C
A

Average
expression
−1012

Percent
expressed
0 25 50 75 100

ABLIM2

OTUD7A

3

2

1

0

0 1 2 3 4 5

0 1 2 3 4 5

OSBPL5

PTK2B

3

2

1

0

0 1 2 3 4 5

0 1 2 3 4 5

Cluster

k

n
o
i
s
s
e
r
p
x
E

l
e
v
e
l

n
o
i
s
s
e
r
p
x
E

l
e
v
e
l

3

2

1

0

3

2

1

0

Nature Methods | Volume 22 | June 2025 | 1199–1212

1206

Articlehttps://doi.org/10.1038/s41592-024-02586-y

Fig. 4 | Rare cell subpopulations associated with impairment identified
using UDA-seq. a,b, A violin plot displaying the distribution of single-cell
level immune-related impairment (a) and metabolic-related impairment (b)
signature scores across different cell types, with the y-axis representing the
immune-related signature score and the x-axis representing cell types. Box plots
show the interquartile range with the median marked. The whiskers extend up
to 1.5 times the interquartile range, and the outliers are not displayed. c,d, The
median score of the immune-related impairment (c) and metabolic-related
impairment (d) signature across all cells from an individual donor, exhibiting a
negative correlation with the eGFR (Pearson’s r = 0.908 and 0.99, respectively).
The shaded area around the regression line represents the 95% confidence
interval. e, Left: EC-GC reclustering, revealing six subclusters in UMAP. Middle:
UMAP embedding, colored by metabolic impairment positive cells. Right: UMAP
embedding, colored by immune impairment positive cells. f, Marker genes

identified for the six subclusters. The dot size indicates the gene expression
percentage of a cluster, while the color represents the scaled average gene
expression within a cluster. g, A bar plot showing that subcluster 0 was enriched
with cells that are positively related to metabolic impairment. h, A bar plot
displaying that subcluster 3 was enriched with cells that are positively related
to immune impairment. i, Important eRegulons identified by SCENIC+ in the six
subclusters. The colors of the heatmap represent scaled TF gene expression, and
the dot size indicates scaled target region enrichment. j, GRNs revealed the key
eRegulons of subcluster 3, which consists of immune impairment-related cells.
Transcription factors are denoted in bold with enlarged gene symbols, peak
regions are represented by squares and regulated genes are shown at the edge of
the graphs. k, The representative genes regulated by the transcription factor in j
are highly expressed in subcluster 3.

years, constituting a female natural aging cohort. The frozen PBMCs
were thawed and then divided into two pools, one comprising 10 donor
PBMCs and the other comprising 28. Following fixation with methanol,
each pool of cells was loaded with one channel and underwent 96-well
post-indexing for library construction (Fig. 5a). A total of 152,357 cells
were recovered from the two channels. After conducting quality control
and sample demultiplexing using natural genetic variation similar to
mux-seq13, 132,712 cells remained for downstream analysis. On average,
3,112 cells and 1,149 genes per cell were identified for each individual
(Extended Data Fig. 8a,b). We integrated our data and annotated them
using a high-quality reference dataset3. We retained 126,616 cells with
high prediction scores, which led to the identification of 27 major cell
types (Fig. 5b).

In our investigation into the correlation between cell type and
age, we employed the SCIPAC algorithm41, which offers a quantitative
assessment of the link between single cells and a specific phenotype.
Through the use of matched single-cell RNA-seq and phenotype data,
cells were categorized into three distinct groups: phenotype+ cells,
phenotype− cells and null cells. Our analysis revealed that natural killer
(NK) cells, CD8+ T effector memory (TEM) and γδT cells are among the
top three cell types positively correlated with aging. Furthermore,
CD8+ naive, CD4+ naive and CD4+ T central nemory (TCM) cells were
identified as the top three cell types negatively correlated with aging
(Fig. 5c,d and Extended Data Fig. 8c). The findings described align
with prior research on single-cell transcriptomic data of PBMC in
independent aging human cohorts42,43. It is worth noting that γδT cells
constitute only a small portion of the PBMCs (0.36%), yet they dem-
onstrate a positive association with senescence. As anticipated, genes
differentially expressed between age positively correlated cells and
age-independent cells serve as aging-related signatures and display
a positive correlation with age (Fig. 5e; for detailed genes, see Sup-
plementary Table 5). These signatures are linked to NK cell sensitivity
and activation (Fig. 5f).

Further unsupervised reclustering of CD4+ naive cells resulted
in the identification of nine subclusters (Fig. 5g). Although a negative

correlation between CD4 naive cells and aging was found through
SCIPAC analysis, there was a cumulative increase in subcluster 2 of CD4
naive cells with aging (Fig. 5h). Previous studies have suggested that a
specific group of CD4+ naive cells (CD4+, CD31−) increase with age44. The
subcluster 2 of CD4 naive cells that we identified is probably a subset
of the previously reported CD4+ CD31− cells (Extended Data Fig. 8d,e).
However, we can now redefine this aging-negatively correlated cell
subpopulation as ITGB1 + PREX1 + CD4 naive cells, on the basis of the
positive molecular markers (Fig. 5i).

We conducted an analysis to understand the adaptive immune
properties associated with aging. Using nested PCR, we enriched TCR/
BCR (B-cell receptor) molecules from the cDNA of 5′-RNA UDA-seq
libraries. As a result, we obtained 34,784 cells with gene expression and
TCR data and 32,958 cells with gene expression and BCR data (Extended
Data Fig. 8f). Our analysis focused on examining the relationship of
clonal expansion among individual T cells and the usage of V(D)J genes
across different age groups. The findings showed that age notably
affected TCR clonotype diversity. There was a noticeable decrease in
richness, meaning fewer different TCR clonotypes, and an increase
in clonality, indicating a higher abundance of specific clonotypes in
older individuals (Fig. 5j).

This advancement enables cohort studies to pinpoint rare sub-
populations relevant to various phenotypes, such as aging, and offers
fresh insights into the clonal expansion dynamics of immune cells.

UDA-seq enables analysis of CRISPR-mediated perturbations
In addition to cohort studies, an important application scenario that
necessitates ultrahigh throughput is pooled CRISPR screening with
single-cell transcriptome as readout. We conducted an assessment
of the knockout impact of bromodomain-containing genes on human
gastric cancer SNU16 cell lines by employing the combined use of
CRISPR droplet sequencing (CROP-seq)45 and UDA-seq. SNU16 cells
expressing Cas9 were transduced with lentiviral constructs that encode
255 single guide RNAs (sgRNAs) targeting 46 genes within the bromo-
domain and extra-terminal domain (BET) family proteins. Each gene was

Fig. 5 | Investigating the PBMC characteristics in an aging female cohort.
a, A flowchart depicting the multimodality experimental design carried out
on PBMCs obtained from a female aging cohort, consisting of two batches
of donors totaling 10 and 28 individuals, respectively. b, UMAP embedding
of 126,616 5′-scRNA-seq profiled PBMC cells, encompassing 27 distinct cell
types. c, Aging-related cells detected using SCIPAC with a UMAP visualization
with cells color-coded on the basis of the significance of the association, with
a red P value indicating a positive association and a blue P value indicating a
negative association. The P values were calculated by the SCIPAC nonparametric
bootstrap strategy. d, Pie charts showing cell type proportions in age-associated
cell groups. Top: age positively associated groups. Bottom: age-negatively
associated groups. e, Box plots displaying age-related gene signature scores
across different age ranges, indicating a positive association with aging. Box
plots show interquartile range with the median marked. The whiskers extend up

to 1.5 times the interquartile range. The number of cells for different age ranges
is shown at the top of each box plot. f, GO enrichment analysis performed on the
gene set forming the age-associated signature. The length of the bars indicates
the gene counts for corresponding GO terms, while the colors represent the
adjusted P value of enrichment. The P value for GO terms was calculated by
the two-sided hypergeometric test and adjusted by the Benjamini–Hochberg
method. g, Reclustering of CD4 naive cells, revealing nine subclusters. h, The
proportion of CD4 naive subcluster 2 increases with age. i, A stacked violin
plot depicting the positive marker genes of subcluster 2 within the CD4 naive
population. j, Box plots depicting the TCR clonal diversity across age groups
(n = 5, 2, 8, 13 and 10), with each dot representing a donor’s diversity calculated by
the inverse Simpson index. The box plots show the interquartile range with the
median marked. The whiskers extend up to 1.5 times the interquartile range.

Nature Methods | Volume 22 | June 2025 | 1199–1212

1207

Articlehttps://doi.org/10.1038/s41592-024-02586-ytargeted with at least five sgRNAs, and ten sgRNAs were used as negative
controls (for detailed genes and sgRNA, see Supplementary Table 6).
After 7 days of infection, cells were subjected to 3′-RNA UDA-seq. A total

of 50,000 methanol-fixed cells were loaded in one channel, followed
by 96-well post-indexing. Guide RNA with single-cell barcodes was
enriched from UDA-seq cDNA products (Fig. 6a). Subsequent single-cell

a

Natural aging cohort
(n = 38; age 20–65 years)

b

PBMC (n = 126,616 cells)

…

Pool

n = 10

n = 28

UDA-seq
Round 2 (96 index)
(Two channels)

sc5’-RNA-seq
+
scVDJ-seq

c

Aging associated cells

d

SCIPAC positive cell types

B intermediate
B memory
B naive
CD4 naive
CD4 TCM
CD4 TEM
CD8 naive
CD8 TCM
CD8 TEM
CD14 mono
CD16 mono
HSPC
ILC

MAIT
NK
NK proliferating
NK CD56bright

Plasmablast
Platelet
Treg
cDC1
cDC2
dnT
gdT
pDC

2
P
A
M
U

UMAP1

P value

≤0.001
≤0.001

0.01

0.05

0.01

0.05

CD8 TEM
(59.57%)

NK
(39.66%)
gdT
(0.49%)

Other
(0.28%)

CD8 naive
(68.5%)

CD4 naive
(25.09%)

CD4 TCM
(1.91%)

Other
(4.5%)

NK

CD8 TEM

SCIPAC negative cell types

CD4 naive

CD8 naive

g

GO term of age positive signature genes

Leukocyte mediated immunity

Leukocyte mediated
cytotoxicity

Natural killer cell mediated
immunity

Lymphocyte mediated immunity

Natural killer cell activation

Natural killer cell mediated
cytotoxicity

Cell killing

Regulation of natural killer
cell mediated immunity

Regulation of immune
effector process

Regulation of leukocyte
mediated cytotoxicity

i

4

3

3

3

l
e
v
e
l

n
o
i
s
s
e
r
p
x
E

CD4 naive

3

0

7

1

6

8

2

4

Adjusted
P value

2.5 × 10−10
5.0 × 10−10
7.5 × 10−10

5

2
P
A
M
U

UMAP1

0

10

20

30

40

Count

Clonetype diversity

IL7R

CCR7

ITGB1

PREX1

C
D
4
n
a
v
e
T

i

S
u
b
c
l
u
s
t
e
r
2

j

25.0

22.5

20.0

17.5

UMAP1

Cells

12,422

10,781 29,228

55,272 18,913

f

0.2

0

−0.2

[20−30)

[30−40)

[40−50)

[50−60)

≥60

Age stage (years)

Proportion of cluster 2

2
P
A
M
U

e

e
r
o
c
s
e
r
u
t
a
n
g
i
s
e
v
i
t
i
s
o
p
e
g
A

h

0.3

0.2

0.1

0

n
o
i
t
r
o
p
o
r
P

[20−30)

[30−40)

[40−50)

[50−60)

≥60

Age stage (years)

0

1

2

3

4

5

6

7

8

Cluster

[20−30)

[30−40)

[40−50)

[50−60)

≥60

Age stage (years)

Nature Methods | Volume 22 | June 2025 | 1199–1212

1208

Articlehttps://doi.org/10.1038/s41592-024-02586-y

a

255 gRNAs

b

l
e
v
e
l

n
o
i
s
s
e
r
p
x
E

3

2

1

0

SNU16–Cas9

Control

Pertubed cells

UDA-seq
Round 2 (96 index)
(One channel)

sc3’-RNA-seq
+
gRNA enrichment

c

P
0
1
g
o
l
–

4

3

2

1

0

e

SNU16 cell gene expression

BRD7

EP300

d

FOXP1 selection plot

l
e
v
e
l

n
o
i
s
s
e
r
p
x
E

3

2

1

0

Other

EP300−sgRNA11
EP300−sgRNA17
Control

Other

BRD7−sgRNA14

BRD7−sgRNA15

BRD7

FAR2

Total of 1,732 variables

VDAC1

LRRK1

NDUFS5

PRKG1

TOM1L2

UMAD1

USP15
HS6ST2

CA8

FOXP1

FGD4

NS

Log2 FC

P value

P value and log2 FC

−5.0

−2.5

0

2.5

5.0

FGFR2

f

l
e
v
e
l

n
o
i
s
s
e
r
p
x
E

8

6

4

2

0

Group 1
Group 2

A
N
R
g
s

A
N
R
g
s

KAT2B
RB1
BRD7
BAZ1B
ARID1A
BAZ1A
NF1
SP100
KMT2A
ATAD2B
SP140L
BAZ2B
BAZ2A
BPTF
TRIM66
CECR2
BRD9
KAT2A
BRWD1
BRWD3
TAF1
BRD3
BRD2
BRD8
TRIM28
ZMYND8
ASH1L
BRPF1
BRDT
PBRM1
SMARCA4
KIAA2026
BRD4
ATAD2
TRIM24
BRD1
EP300
ZMYND11
SP110
TAF1L
posCtrl
BRPF3
PHIP
NF2
SP140
CREBBP
TRIM33
SMARCA2
NegCtrl

FDR

≤0.05

Other

−0.1 0

0.1 0.2

LR score

VDAC1 selection plot

ZMYND8
ASH1L
NegCtrl
BRPF3
SP140L
SP140
TRIM66
RB1
ATAD2
BRD8
KIAA2026
TRIM33
EP300
BRD4
BRD2
BRD9
SP110
BAZ2B
posCtrl
BRWD1
NF2
KAT2A
SMARCA4
BPTF
PBRM1
BRPF1
PHIP
BRD1
BRWD3
BRD3
SMARCA2
BAZ2A
KAT2B
SP100
ARID1A
BAZ1B
ATAD2B
BAZ1A
NF1
TAF1L
TRIM28
KMT2A
CECR2
ZMYND11
CREBBP
BRDT
TRIM24
TAF1
BRD7

FDR

≤0.05

Other

−0.2

−0.1
0
LR score

Group 2

Group 1

Group 2

Group 1

Group 2

i

Group 1

Control

Control

BAZ2A
CECR2

BRD1
BRD4
BAZ2A
BRD8

Target
gene

Control

Target
gene

Control

*

* *

*

BRD1

BRD4

BAZ2A

BRD8

Control

e
l
c
y
c
l
l
e
C

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
B
b
r
E

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
K
P
A
M

e
c
n
e
c
s
e
n
e
s

r
a
l
u

l
l
e
C

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s

t
n
W

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s

t
k
A
−
K
3
P

I

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
o
p
p
H

i

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
a
t
e
b
−
F
G
T

C
s
i
t
i
t
a
p
e
H

B
s
i
t
i
t
a
p
e
H

n
o
i
t
c
e
f
n

i

a
l
l
e
n
o
m
l
a
S

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
T
A
T
S
−
K
A
J

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
e
n
o
m
r
o
h
d
o
r
y
h
T

i

r
e
c
n
a
c
n

i

s
n
a
c
y
l
g
o
e
t
o
r
P

n
o
i
t
c
e
f
n

i

s
u
r
i
v
r
r
a
B
−
n
e
t
s
p
E

i

r
e
c
n
a
c
n

i

n
o
i
t
a
l
u
g
e
r
s
i
m

l
a
n
o
i
t
p
i
r
c
s
n
a
r
T

n
o
i
t
c
e
f
n

i

s
u
r
i
v
o
l
a
g
e
m
o
t
y
c
n
a
m
u
H

n
o
i
t
c
e
f
n

i

1

i

s
u
r
i
v
a
m
e
k
u
e
l

l
l
e
c
T
n
a
m
u
H

n
o
i
t
c
e
f
n

i

s
u
r
i
v
s
e
p
r
e
h
d
e
t
a
c
o
s
s
a
-
a
m
o
c
r
a
s

i

i
s
o
p
a
K

s
l
l
e
c
m
e
t
s

f
o
y
c
n
e
t
o
p
i
r
u
p
g
n
i
t
a
l
u
g
e
r

l

s
y
a
w
h
t
a
p
g
n

i
l
a
n
g
S

i

r
e
c
n
a
c
n

i

s
A
N
R
o
r
c
M

i

n
o
i
t
a
v
i
t
c
a
r
o
t
p
e
c
e
r

−

i

s
i
s
e
n
e
g
o
n
c
r
a
c
l
a
c
m
e
h
C

i

e
l
c
y
c
l
l
e
C

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
B
b
r
E

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
K
P
A
M

e
c
n
e
c
s
e
n
e
s

r
a
l
u

l
l
e
C

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s

t
n
W

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s

t
k
A
−
K
3
P

I

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
o
p
p
H

i

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
a
t
e
b
−
F
G
T

C
s
i
t
i
t
a
p
e
H

B
s
i
t
i
t
a
p
e
H

n
o
i
t
c
e
f
n

i

a
l
l
e
n
o
m
l
a
S

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
T
A
T
S
−
K
A
J

y
a
w
h
t
a
p
g
n

i
l
a
n
g
i
s
e
n
o
m
r
o
h
d
o
r
y
h
T

i

r
e
c
n
a
c
n

i

s
n
a
c
y
l
g
o
e
t
o
r
P

n
o
i
t
c
e
f
n

i

s
u
r
i
v
r
r
a
B
−
n
e
t
s
p
E

i

r
e
c
n
a
c
n

i

n
o
i
t
a
l
u
g
e
r
s
i
m

l
a
n
o
i
t
p
i
r
c
s
n
a
r
T

n
o
i
t
c
e
f
n

i

s
u
r
i
v
o
l
a
g
e
m
o
t
y
c
n
a
m
u
H

n
o
i
t
c
e
f
n

i

1

i

s
u
r
i
v
a
m
e
k
u
e
l

l
l
e
c
T
n
a
m
u
H

n
o
i
t
c
e
f
n

i

s
u
r
i
v
s
e
p
r
e
h
d
e
t
a
c
o
s
s
a
-
a
m
o
c
r
a
s

i

i
s
o
p
a
K

s
l
l
e
c
m
e
t
s

f
o
y
c
n
e
t
o
p
i
r
u
p
g
n
i
t
a
l
u
g
e
r

l

s
y
a
w
h
t
a
p
g
n

i
l
a
n
g
S

i

r
e
c
n
a
c
n

i

s
A
N
R
o
r
c
M

i

n
o
i
t
a
v
i
t
c
a
r
o
t
p
e
c
e
r

−

i

s
i
s
e
n
e
g
o
n
c
r
a
c
l
a
c
m
e
h
C

i

2
C
P

PC 1

0.40

0.35

0.30

0.25

0.20

0.15

g

l
e
v
e
l

n
o
i
s
s
e
r
p
x
e
C
Y
M

h

l
e
v
e
l

n
o
i
s
s
e
r
p
x
e
C
Y
M

0.6

0.4

0.2

0

BAZ2A
BRD4
BRD8
BRD1
BRPF1
SP110
TRIM66
SP140L
NF1
SMARCA4
BRWD3
posCtrl
SMARCA2
KMT2A
BRD2
PBRM1
ARID1A
PHIP
BRD9
CECR2
BRD7
ATAD2B
TRIM24
KAT2A
EP300
TAF1
TRIM28
BAZ1B
SP100
ZMYND8
BRPF3
TRIM33
BRD3
BRDT
BRWD1
TAF1L
BAZ1A
BAZ2B
RB1
BPTF
SP140
NF2
ASH1L
CREBBP
ATAD2
KAT2B
KIAA2026
ZMYND11

T
a
r
g
e
t
g
e
n
e

4
3
2
1
0

E
n
r
i
c
h
m
e
n
t

s
c
o
r
e

Nature Methods | Volume 22 | June 2025 | 1199–1212

1209

Articlehttps://doi.org/10.1038/s41592-024-02586-y

Fig. 6 | UDA-seq enables pooled CRISPR screening with single-cell
transcriptome readout. a, A flowchart of the UDA CRISPR screening on the
SNU16 cell line. Cells were transduced with 255 different gRNAs overall. b, A violin
plot illustrating the absence of expression of the targeted genes BRD7 and EP300.
c, The genes that exhibit differential expression in cells subjected to interference
targeting BRD7 as compared with those targeted by the negative control sgRNA.
The vertical dashed lines represented −1 or 1 log2FC value, the horizontal dashed
line represented p-value = 0.05. d, The degree of perturbations of the genes of
interest, estimated by the scMAGeCK-LR module. An LR_score >0 represents
upregulation by the corresponding target genes, while an LR_score <0 represents
downregulation. FDR means adjusted p-value calculated from ScMAGeCK.
e, Unsupervised clustering of the single-cell transcriptome, revealing two
distinct groups (group 1 with n = 3,880 and group 2 with n = 8,707) of SUN16 cells
in the PCA space defined by PC1 and PC2. f, A violin plot indicating that the gene
expression of FGFR2 was higher in group 2. The box plots show the interquartile
range with the median marked. The whiskers extend up to 1.5 times the

interquartile range, and the outliers are not displayed. g, The average expression
(dots) of the MYC gene within cells grouped by perturbation. The calculations
for the target gene versus control and group 1 versus group 2 were performed
separately. h, The expression of the MYC gene was notably reduced in cells
subjected to interference targeting BRD1 (n = 5), BRD4 (n = 5), BAZ2A (n = 5)
and BRD8 (n = 5) compared with the control (n = 10). The box plots show the
interquartile range with the median marked. The whiskers extend up to 1.5 times
the interquartile range, and the outliers are not displayed. P values were
calculated using the two-sided t test. *Hochberg-adjusted P value <0.05 (adjusted
P values of 0.039, 0.039, 0.047 and 0.022, respectively). i. The downregulated
genes identified for each target gene separately in group 1 and group 2 cells. The
enrichment of these downregulated genes per target on MYC-related pathways
from the KEGG database is illustrated by − log10(P value). The P values for the
KEGG pathway were calculated by the two-sided hypergeometric test and
adjusted by the Benjamini–Hochberg method.

transcriptomic analysis revealed that 38,000 cells were recovered.
After quality control, 31,487 cells with sgRNA were retained (Extended
Data Fig. 9a,b).

UDA-seq’s ultrahigh throughput simplifies downstream analysis.
Even with stringent thresholds requiring cells with a single sgRNA or
cells with more than one sgRNA but with a dominant one, we were able
to identify 12,644 cells. This results in a mean library coverage of 44 cells
per sgRNA and 233 cells per target gene, meeting typical requirements.
A median of 1,745 genes and 2,497 UMIs are detected per cell in the
final dataset (Extended Data Fig. 9c). We verified that targeted genes
no longer express in the corresponding sgRNA-perturbed cells, such
as BRD7 and EP300 (Fig. 6b). To systematically uncover gene regula-
tion relationships, we used both differential expression gene analysis
and ScMAGeCK46 analysis tailored for single-cell perturbation data
and found consistent results from both analyses. For example, both
analyses indicated that BRD7 is a potential repressor of FOXP1 and
an activator of VDAC1 (Fig. 6c,d). These observations (Fig. 6b–d and
Extended Data Fig. 9d,e) validate the successful use of CRISPR interfer-
ence and the high quality of UDA-seq.

The analysis of scRNA-seq data showed that there are two distinct
groups of SNU16 cells (Fig. 6e). These groups exhibit different levels of
FGFR2 gene expression, with group 2 showing higher levels (Fig. 6f).
Both groups contain cells with negative sgRNA and other target sgRNA
(Extended Data Fig. 9f), suggesting that the observed differences
between the groups are not due to CRISPR perturbation. Previous
research has indicated that SNU16 cells display variability, with dif-
fering levels of FGFR2 amplification leading to varying responses to
drugs47–49.

The bromodomain family of proteins are crucial epigenetic
‘readers’50,51. BET inhibitors52,53 have proven to rapidly suppress key
proto-oncogenes such as MYC52–55. Our data support that perturbing
these target genes has resulted in a notable decrease in MYC expression
in comparison with control groups (Fig. 6g,h and Extended Data Fig. 9g).
To better understand the influence of different Bromodomain
family genes on SNU16, we compared the correlation of differentially
expressed genes with MYC-related pathways in two groups of SNU16
cells after depleting each target gene. We found that various Bromo-
domain family genes have differing effects on the MYC pathway in the
two groups of SNU16 cells (Fig. 6i). The depletion of BAZ2A, BRD4 and
BRD8 adversely affected the differentiation, proliferation, apoptosis
and migration-related signaling pathways in group 1 cells. BAZ2A also
inhibits those pathways in group 2 cells, suggesting its crucial role in
maintaining cell growth and proliferation in both groups. Additionally,
the depletion of SP140L, NF1 and SMARCA4 inhibited infection and
metabolic pathways specifically in group 2 cells.

We anticipate that the extensive use of UDA-seq will pave the way
for a thorough exploration of regulatory processes and support the
creation of foundational models in single-cell perturbation modeling.

Discussion
We introduce UDA-seq, a single-cell multimodal sequencing method
offering versatility, affordability and reliability for analyzing fresh
and fixed cells or nuclei. UDA-seq achieves a 10- to 20-fold increase
in throughput while remarkably reducing doublets. Its workflow and
data quality are on par with the commercial 10x Genomics kit. We
validated UDA-seq on a variety of frozen clinical samples, including
PBMCs, kidney biopsies and multiple cancer samples, demonstrating
its effectiveness for large-scale single-cell population cohort analysis.
The increased sample size and deeper cellular coverage enable the iden-
tification of rare cell types associated with specific phenotypes, such
as age-associated γδT cells and proteinuria-associated POD cells, even
when these cell types constitute fewer than 5 in 1,000 cells. Moreover,
UDA-seq can minimize experimental batch bias and variation, especially
with limited starting material, making it a valuable tool for researchers
conducting high-throughput, large-scale studies.

Some early pioneering work introduced the concept of combi-
natorial indexing in droplet microfluidics7,8. However, most initial
studies primarily supported single modalities, often requiring tailored
additional steps to enable multimodality, thus rendering the approach
nonuniversal. In contrast, our work provides a universal solution to
greatly enhance the throughput of existing single-cell multimodal
omics technologies. This method can be readily expanded to augment
other multimodality assays, such as cellular indexing of transcrip-
tomes and epitopes by sequencing (CITE-seq)56, Droplet Pair-Tag57,
single-nucleus m6A-CUT&Tag (sn-m6A-CT)58, and numerous others.
Importantly, updates from the manufacturer can be seamlessly
and synergistically integrated into the UDA-seq workflow. For exam-
ple, transitioning from the Chromium Controller to Chromium X or
updating reagents from Next GEM to GEM-X requires no additional
configuration, leading to improved recovery rates and other benefits
(Fig. 1g,h). UDA-seq is specifically compatible with 10x Genomics and
similar methods that rely on the conditional dissolution of gel beads or
photolysis to release barcoded oligonucleotides. However, platforms
that require cell lysis within droplets for barcoding are not compatible
with UDA-seq.

UDA-seq demonstrates the feasibility of achieving high through-
puts for cells and real-world clinical samples by combining combina-
torial indexing with droplet microfluidics through a post-indexing
approach. Unlike pre-indexing strategies such as single-cell combi-
natorial fluidic indexing (scifi)-RNA-seq8, the post-indexing method
does not inherently provide built-in sample multiplexing capabilities.
To address this, we utilized genetic variation for donor deconvolu-
tion in this study, minimizing the preprocessing handling time. It
is important to note that UDA-seq is compatible with established
sample multiplexing methods, such as DNA-labeled antibodies59 and
lipids60. This compatibility is particularly valuable in scenarios where
SNP-based deconvolution is not applicable, as seen in longitudinal

Nature Methods | Volume 22 | June 2025 | 1199–1212

1210

Articlehttps://doi.org/10.1038/s41592-024-02586-ystudies of the same donor. We have noticed that an independent
method known as Overloading And unpacKing (OAK)-seq61 employs
a barcoding strategy similar to UDA-seq. However, OAK-seq primarily
focuses on in vitro systems. It nicely complements our work by show-
casing the potential of capturing lineage information and its compat-
ibility with Cell Hashing, which uses barcoded antibodies for sample
multiplexing.

In conclusion, UDA-seq’s ultrahigh throughput makes it ideal for
large-scale single-cell, multisample studies such as large-scale disease
cohorts or cellular atlas constructions, as well as high-throughput
CRISPR and drug screening, driving advancements in single-cell
technology.

Online content
Any methods, additional references, Nature Portfolio reporting sum-
maries, source data, extended data, supplementary information,
acknowledgements, peer review information; details of author contri-
butions and competing interests; and statements of data and code avail-
ability are available at https://doi.org/10.1038/s41592-024-02586-y.

References
1.  Cuomo, A. S. E., Nathan, A., Raychaudhuri, S., MacArthur, D. G.

18.  D’Agati, V. D. et al. Obesity-related glomerulopathy: clinical and
pathologic characteristics and pathogenesis. Nat. Rev. Nephrol.
12, 453–471 (2016).

19.  Fornoni, A., Merscher, S. & Kopp, J. B. Lipid biology of the

podocyte–new perspectives offer new opportunities. Nat. Rev.
Nephrol. 10, 379–388 (2014).

20.  Li, Y. et al. Epithelial-to-mesenchymal transition is a potential

pathway leading to podocyte dysfunction and proteinuria. Am. J.
Pathol. 172, 299–308 (2008).

21.  Ghayur, A. & Margetts, P. J. Transforming growth factor-beta and
the glomerular filtration barrier. Kidney Res. Clin. Pract. 32, 3–10
(2013).

22.  Wang, D., Dai, C., Li, Y. & Liu, Y. Canonical Wnt/beta-catenin
signaling mediates transforming growth factor-beta1-driven
podocyte injury and proteinuria. Kidney Int. 80, 1159–1169 (2011).

23.  Bravo Gonzalez-Blas, C. et al. SCENIC+: single-cell multiomic

inference of enhancers and gene regulatory networks. Nat. Methods
20, 1355–1367 (2023).

24.  Edwards, N. et al. A novel LMX1B mutation in a family with

end-stage renal disease of unknown cause. Clin. Kidney J. 8,
113–119 (2015).

25.  Negrisolo, S. et al. Could the interaction between LMX1B and

& Powell, J. E. Single-cell genomics meets human genetics. Nat.
Rev. Genet. 24, 535–549 (2023).

PAX2 influence the severity of renal symptoms? Eur. J. Hum.
Genet. 26, 1708–1712 (2018).

2.  Lim, J. et al. Transitioning single-cell genomics into the clinic. Nat.

Rev. Genet. 24, 573–584 (2023).

3.  Hao, Y. et al. Integrated analysis of multimodal single-cell data.

Cell 184, 3573–3587 e3529 (2021).

26.  Liang, B., Zhao, J. & Wang, X. Clinical performance of E2Fs 1–3
in kidney clear cell renal cancer, evidence from bioinformatics
analysis. Genes Cancer 8, 600–607 (2017).

27.  Chen, R. et al. Identification of the expression and clinical

4.  Baysoy, A., Bai, Z., Satija, R. & Fan, R. The technological landscape
and applications of single-cell multi-omics. Nat. Rev. Mol. Cell Biol.
24, 695–713 (2023).

significance of E2F family in clear cell renal Cell carcinoma. Int. J.
Gen. Med. 15, 1193–1212 (2022).

28.  Jin, S. et al. Inference and analysis of cell-cell communication

5.  Vandereyken, K., Sifrim, A., Thienpont, B. & Voet, T. Methods and

using CellChat. Nat. Commun. 12, 1088 (2021).

applications for single-cell and spatial multi-omics. Nat. Rev. Genet.
24, 494–515 (2023).

7.

6.  Hao, M. et al. Large-scale foundation model on single-cell
transcriptomics. Nat. Methods 21, 1481–1491 (2024).
Lareau, C. A. et al. Droplet-based combinatorial indexing for
massive-scale single-cell chromatin accessibility. Nat. Biotechnol.
37, 916–924 (2019).

8.  Datlinger, P. et al. Ultra-high-throughput single-cell RNA

sequencing and perturbation screening with combinatorial fluidic
indexing. Nat. Methods 18, 635–642 (2021).

9.  Hwang, B. et al. SCITO-seq: single-cell combinatorial indexed
cytometry sequencing. Nat. Methods 18, 903–911 (2021).
10.  Li, Y. et al. FIPRESCI: droplet microfluidics based combinatorial
indexing for massive-scale 5'-end single-cell RNA sequencing.
Genome Biol. 24, 70 (2023).

29.  Eremina, V. et al. Glomerular-specific alterations of VEGF-A

expression lead to distinct congenital and acquired renal
diseases. J. Clin. Invest. 111, 707–716 (2003).

30.  Eremina, V. et al. VEGF inhibition and renal thrombotic

microangiopathy. N. Engl. J. Med. 358, 1129–1136 (2008).
31.  Okusa, M. D., Chertow, G. M., Portilla, D. & Acute Kidney Injury

Advisory Group of the American Society of Nephrology The nexus
of acute kidney injury, chronic kidney disease, and World Kidney
Day 2009. Clin. J. Am. Soc. Nephrol. 4, 520–522 (2009).

32.  Guo, R. et al. The road from AKI to CKD: molecular mechanisms

and therapeutic targets of ferroptosis. Cell. Death Dis. 14, 426
(2023).

33.  Chawla, L. S. & Kimmel, P. L. Acute kidney injury and chronic

kidney disease: an integrated clinical syndrome. Kidney Int. 82,
516–524 (2012).

11.  Cao, J. Y. et al. Comprehensive single-cell transcriptional profiling

34.  Hsu, R. K. & Hsu, C. Y. The role of acute kidney injury in chronic

of a multicellular organism. Science 357, 661–667 (2017).
12.  Rosenberg, A. B. et al. Single-cell profiling of the developing

kidney disease. Semin. Nephrol. 36, 283–292 (2016).

35.  Chawla, L. S., Eggers, P. W., Star, R. A. & Kimmel, P. L. Acute kidney

mouse brain and spinal cord with split-pool barcoding. Science
360, 176–182 (2018).

injury and chronic kidney disease as interconnected syndromes.
N. Engl. J. Med. 371, 58–66 (2014).

13.  Kang, H. M. et al. Multiplexed droplet single-cell RNA-sequencing
using natural genetic variation. Nat. Biotechnol. 36, 89–94 (2018).

14.  Lake, B. B. et al. An atlas of healthy and injured cell states and
niches in the human kidney. Nature 619, 585–594 (2023).

15.  Granja, J. M. et al. ArchR is a scalable software package for

integrative single-cell chromatin accessibility analysis. Nat. Genet.
53, 403–411 (2021).

16.  Sun, D. et al. Identifying phenotype-associated subpopulations by
integrating bulk and single-cell sequencing data. Nat. Biotechnol.
40, 527–538 (2022).

17.  Meliambro, K., He, J. C. & Campbell, N. N. Podocyte-targeted

therapies—progress and future directions. Nat. Rev. Nephrol. 20,
643–658 (2024).

36.  Peng, L. et al. The emerging roles of CCN3 protein in immune-
related diseases. Mediators Inflamm. 2021, 5576059 (2021).
37.  de la Vega Gallardo, N., Dittmer, M., Dombrowski, Y. & Fitzgerald,
D. C. Regenerating CNS myelin: emerging roles of regulatory
T cells and CCN proteins. Neurochem. Int. 130, 104349 (2019).
38.  Li, R. et al. Association between endothelin-1 and systemic lupus

erythematosus: insights from a case–control study. Sci Rep. 13,
15970 (2023).

39.  Ketzer, F. et al. CCND3 is indispensable for the maintenance of
B-cell acute lymphoblastic leukemia. Oncogenesis 11, 1 (2022).
40.  Zhou, G. et al. PTK2B regulates immune responses of neutrophils
and protects mucosal inflammation in ulcerative colitis. FASEB J.
37, e22967 (2023).

Nature Methods | Volume 22 | June 2025 | 1199–1212

1211

Articlehttps://doi.org/10.1038/s41592-024-02586-y41.  Gan, D., Zhu, Y., Lu, X. & Li, J. SCIPAC: quantitative estimation of
cell-phenotype associations. Genome Biol. 25, 119 (2024).
42.  Terekhova, M. et al. Single-cell atlas of healthy human blood
unveils age-related loss of NKG2C(+)GZMB(-)CD8(+) memory
T cells and accumulation of type 2 memory T cells. Immunity 56,
2836–2854 e2839 (2023).

43.  Zhu, H. et al. Human PBMC scRNA-seq-based aging clocks reveal
ribosome to inflammation balance as a single-cell aging hallmark
and super longevity. Sci. Adv. 9, eabq7599 (2023).

44.  van den Broek, T., Borghans, J. A. M. & van Wijk, F. The full spectrum
of human naive T cells. Nat. Rev. Immunol. 18, 363–373 (2018).

45.  Datlinger, P. et al. Pooled CRISPR screening with single-cell
transcriptome readout. Nat. Methods 14, 297–301 (2017).
46.  Yang, L. et al. scMAGeCK links genotypes with multiple

56.  Stoeckius, M. et al. Simultaneous epitope and transcriptome

measurement in single cells. Nat. Methods 14, 865–868 (2017).
57.  Xie, Y. et al. Droplet-based single-cell joint profiling of histone

modifications and transcriptomes. Nat. Struct. Mol. Biol. 30,
1428–1433 (2023).

58.  Hamashima, K. et al. Single-nucleus multiomic mapping of m(6)
A methylomes and transcriptomes in native populations of cells
with sn-m6A-CT. Mol Cell. 83, 3205–3216.e5 (2023).

59.  Stoeckius, M. et al. Cell Hashing with barcoded antibodies
enables multiplexing and doublet detection for single cell
genomics. Genome Biol. 19, 224 (2018).

60.  McGinnis, C. S. et al. MULTI-seq: sample multiplexing for

single-cell RNA sequencing using lipid-tagged indices. Nat.
Methods 16, 619–626 (2019).

phenotypes in single-cell CRISPR screens. Genome Biol. 21, 19
(2020).

47.  Hung, K. L. et al. ecDNA hubs drive cooperative intermolecular

61.  Wu, B. et al. Overloading And unpacKing (OAK)–droplet-based
combinatorial indexing for ultra-high throughput single-cell
multiomic profiling. Nat Commun. 15, 9146 (2024).

oncogene expression. Nature 600, 731–736 (2021).

48.  Grygielewicz, P. et al. Epithelial-mesenchymal transition confers
resistance to selective FGFR inhibitors in SNU-16 gastric cancer
cells. Gastric Cancer 19, 53–62 (2016).

Publisher’s note Springer Nature remains neutral with regard
to jurisdictional claims in published maps and institutional
affiliations.

49.  Xie, L. et al. FGFR2 gene amplification in gastric cancer predicts

sensitivity to the selective FGFR inhibitor AZD4547. Clin. Cancer Res.
19, 2572–2583 (2013).

50.  Sanchez, R. & Zhou, M. M. The role of human bromodomains
in chromatin biology and gene transcription. Curr. Opin. Drug
Discov. Devel. 12, 659–665 (2009).

51.  Josling, G. A., Selvarajah, S. A., Petter, M. & Duffy, M. F. The role
of bromodomain proteins in regulating gene expression. Genes
(Basel) 3, 320–343 (2012).

52.  Muhar, M. et al. SLAM-seq defines direct gene-regulatory

functions of the BRD4-MYC axis. Science 360, 800–805 (2018).
53.  Devaiah, B. N. et al. MYC protein stability is negatively regulated
by BRD4. Proc. Natl Acad. Sci. USA 117, 13457–13467 (2020).

54.  Graziani, V. et al. Metabolic rewiring in MYC-driven medulloblastoma

by BET-bromodomain inhibition. Sci. Rep. 13, 1273 (2023).

55.  Dawson, M. A. et al. Inhibition of BET recruitment to chromatin
as an effective treatment for MLL-fusion leukaemia. Nature 478,
529–533 (2011).

Open Access This article is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International License,
which permits any non-commercial use, sharing, distribution and
reproduction in any medium or format, as long as you give appropriate
credit to the original author(s) and the source, provide a link to the
Creative Commons licence, and indicate if you modified the licensed
material. You do not have permission under this licence to share
adapted material derived from this article or parts of it. The images
or other third party material in this article are included in the article’s
Creative Commons licence, unless indicated otherwise in a credit
line to the material. If material is not included in the article’s Creative
Commons licence and your intended use is not permitted by statutory
regulation or exceeds the permitted use, you will need to obtain
permission directly from the copyright holder. To view a copy of this
licence, visit http://creativecommons.org/licenses/by-nc-nd/4.0/.

© The Author(s) 2025

1China National Center for Bioinformation, Beijing, China. 2Beijing Institute of Genomics, Chinese Academy of Sciences, Beijing, China. 3University of
Chinese Academy of Sciences, Beijing, China. 4Department of Nephrology, State Key Laboratory of Complex Severe and Rare Diseases, Peking Union
Medical College Hospital, Chinese Academy of Medical Science and Peking Union Medical College, Beijing, China. 5Department of Respiratory and
Critical Care, Joint Innovation Center for Engineering in Medicine, Quzhou Affiliated Hospital of Wenzhou Medical University, Quzhou, China. 6Sino–
Danish College, University of Chinese Academy of Sciences, Beijing, China. 7College of Future Technology College, University of Chinese Academy of
Sciences, Beijing, China. 8Department of Urology/Institute of Urology, West China Hospital, Sichuan University, Chengdu, China. 9Kidney Transplantation
Center, West China Hospital, Sichuan University, Chengdu, China. 10Key Laboratory of Multi-Cell Systems, Shanghai Institute of Biochemistry and Cell
Biology, Center for Excellence in Molecular Cell Science, Chinese Academy of Sciences, Shanghai, China. 11School of Life Science and Technology,
Shanghai Tech University, Shanghai, China. 12School of Life Science, Hangzhou Institute for Advanced Study, University of Chinese Academy of Sciences,
Hangzhou, China. 13Hepato-pancreato-biliary Center, Beijing Tsinghua Changgung Hospital, School of Clinical Medicine, Tsinghua University, Beijing,
China. 14Research Unit of Precision Hepatobiliary Surgery Paradigm, Chinese Academy of Medical Sciences, Beijing, China. 15State Key Laboratory of
Molecular Oncology, Peking University Cancer Hospital & Institute, Peking University International Cancer Institute, Peking University-Yunnan Baiyao
International Medical Research Center, Beijing, China. 16State Key Laboratory of Membrane Biology, Institute of Zoology, Chinese Academy of Sciences,
Beijing, China. 17Institute for Stem Cell and Regeneration, Chinese Academy of Sciences, Beijing, China. 18Beijing Institute for Stem Cell and Regenerative
Medicine, Beijing, China. 19Advanced Innovation Center for Human Brain Protection and National Clinical Research Center for Geriatric Disorders, Xuanwu
Hospital Capital Medical University, Beijing, China. 20Aging Translational Medicine Center, International Center for Aging and Cancer, Beijing Municipal
Geriatric Medical Research Center, Xuanwu Hospital, Capital Medical University, Beijing, China. 21Aging Biomarker Consortium, Beijing, China. 22These
authors contributed equally: Yun Li, Zheng Huang, Lubin Xu, Yanling Fan, Jun Ping.
zhangwq@big.ac.cn; ghliu@ioz.ac.cn; chenlimeng@pumch.cn; jiangl@big.ac.cn

 e-mail: shaokun_shu@bjmu.edu.cn; fengzhang@wmu.edu.cn;

Nature Methods | Volume 22 | June 2025 | 1199–1212

1212

Articlehttps://doi.org/10.1038/s41592-024-02586-yMethods
Cell culture
All established cell lines NIH-3T3 (SCSP-515), HeLa (SCSP-504), and
SNU16 (TCHu243) were purchased from the National Collection of
Authenticated Cell Cultures (Shanghai, China). Cells were cultured
at 37 °C in an atmosphere of 5% (v:v) carbon dioxide in DMEM (Gibco,
catalog no. 11965092) or RPMI (Gibco, catalog no. 11875093) medium
(SNU16) supplemented with 10% fetal bovine serum, and digested with
0.25% Trypsin (catalog no. 25200056; Gibco) for preparing single-cell
suspension.

Human specimen sampling
The study was approved by the Ethics Committee of the Beijing Institute
of Genomics, Chinese Academy of Sciences/China National Center for
Bioinformation (2024H013 and 2023H001), Peking Union Medical
College Hospital (I-23PJ739) and West China Hospital of Sichuan
University (2024-170) and was conducted following the Declaration
of Helsinki. All the patients in this study provided written informed
consent. Participants were not compensated.

Human PBMCs
The peripheral blood samples of healthy women were from the Quzhou
Affiliated Hospital of Wenzhou Medical University. All the patients in
this study provided written informed consent. The fresh peripheral
blood was collected in EDTA anticoagulant tubes and processed
immediately. PBMCs were isolated according to the manufacturer’s
instructions for Ficoll-Paque PLUS (17-1440-02; GE Healthcare). Iso-
lated PBMCs were gently suspended in cryopreservation medium
CELLBANKER2 (11891; AMSBIO), and stored in liquid nitrogen before
further processing. After thawing, dead cells were removed using the
Dead Cell Removal Kit (catalog no. 130-090-101; Miltenyi Biotec). For
the human aging cohort study, equal numbers of live cells were pooled
for 10 and 28 samples per pool. Cells were fixed, permeabilized and
immediately subjected to sc5′-RNA and VDJ-seq UDA-seq. After fixation,
100,000 cells (for 10 donors) and 250,000 cells (for 28 donors) were
subjected to two channels of UDA followed by 96-well post-indexing.

Human kidney biopsy
A total of 35 human kidney samples were obtained for this study:
25 from nephritic patients from the Peking Union Medical College
Hospital (PUMCH) and 10 time-zero transplantation biopsy samples
from the West China Hospital of Sichuan University, under institu-
tional review board-approved protocols. All samples were dissected
from excess tissue from needle biopsy samples used for diagnostic
purposes. Each patient biopsy was approximately 2–3 mm (equivalent
to around one-fifth of a 16G or 18G needle biopsy). Samples were from
18 male and 17 female participants. All specimens were snap frozen
with liquid nitrogen immediately after sampling and stored in liquid
nitrogen before processing. The metadata for the samples are given
in Supplementary Table 1. On the day of the experiment, all 35 human
kidney samples were combined to isolate nuclei, and two channels of
Multiome (single-nuclear (sn)3′-RNA and ATAC-seq) UDA-seq were
performed. Each channel was loaded with 300,000 nuclei and then
subjected to 96-well post-indexing.

Human lung cancer, cholangiocarcinoma, pancreatic cancer
and heart (coronary artery) samples
Human lung cancer samples were obtained from the Fudan University
Shanghai Cancer Center Hospital. Cholangiocarcinoma samples were
obtained from the Beijing Tsinghua Changgung Hospital. Human
pancreatic cancer samples were obtained from the Beijing Cancer
Hospital. Human heart samples were obtained from the Wuhan Uni-
versity Zhongnan Hospital. All samples were obtained from patients’
leftover surgical tumor tissue and stored at −80 °C before processing.
These samples were combined in equal mass to isolate the nuclei.

Nature Methods

A total of 300,000 nuclei were then subjected to Multiome (sc3′-RNA
and ATAC-seq) UDA-seq, followed by 96-well post-indexing.

CRISPR screening cell lines
We cloned 255 guide RNA cassettes into the CROP-seq-Guide-Puro plas-
mid (catalog no. 86,708; Addgene), targeting 46 genes of the human
bromodomain family with at least five guide RNAs each and including
ten nontargeting controls (sequences are provided in Supplementary
Table 6). SNU16 cells were transduced with lentiCas9-Blast (catalog no.
52,962; Addgene) and selected with 25 µg ml−1 blasticidin (catalog no.
ant-bl-5; InvivoGen) to achieve stable expression of Cas9. Then, SNU16
cells expressing Cas9 were transduced with lentiviral constructs encod-
ing 255 guide RNAs. Following overnight incubation at 37 °C and 5%
CO2, the medium was exchanged to select for the guide RNA construct
(RPMI, 10% FCS, penicillin–streptomycin, 25 µg ml blasticidin, 2 µg ml−1
puromycin, catalog no. A1113803; Thermo Fisher Scientific). The
selective medium was renewed every 2–3 days for a duration of 7 days
to allow for efficient genome editing. Seven days after transfection,
the cells after perturbation were collected to apply UDA-seq (3′-RNA),
followed by 96-well post-indexing.

Preparation for UDA-seq
Cell fixation and permeabilization. A total of 1 million live cells (NIH
3T3, Hela, PBMCs or SNU16) were fixed and permeabilized by sus-
pending in 100 µl of 1× PBS and 900 µl of ice-cold methanol (cata-
log no. M116121; Aladdin) at −20 °C for 10 min. After two additional
washes (centrifugation at 300g for 5 min at 4 °C) with 1 ml of chilled
PBS-BSA-RNase inhibitor (1× PBS supplemented with 1% w/v BSA, A1933;
Sigma) and 1 U µl−1 RNase inhibitor (3335399001; Sigma), fixed and per-
meabilized cells were resuspended in 40 µl PBS-BSA-RNase inhibitor,
placed on ice and then immediately sent for UDA-seq.

Isolation of nuclei from human tissues. For single nucleus isola-
tion, all steps were completed on ice. Frozen tissues were placed into
a 1.5 ml microcentrifuge tube with 0.5 ml of chilled 0.1× lysis buffer
(10 mM Tris–HCl pH 7.4 (catalog no. T2194; Sigma-Aldrich), 10 mM NaCl
(catalog no. 59222C; Sigma-Aldrich), 3 mM MgCl2 (catalog no. M1028;
Sigma-Aldrich), 0.1% Tween-20 (catalog no. 28320; Thermo Fisher),
0.01% NP40 (catalog no. 59222C; Sigma-Aldrich), 0.001% digitonin
(catalog no. BN2006; Thermo Fisher), 1 mM DTT (catalog no. 646563;
Sigma-Aldrich), 1% BSA (catalog no. A1933; Sigma-Aldrich) and 1 U µl−1
RNase inhibitor (catalog no. N2615; Promega)), and large tissues (such
as lung cancer, cholangiocarcinoma, coronary artery and pancreatic
cancer) were quickly minced into small pieces (~0.1 mm) on ice using
scissors, then immediately homogenized 15 times using a pellet pestle.
After incubation for 5 min on ice, the mix was pipetted 10 times with a
wide-bore pipette tip then incubated for 10 min on ice before adding
1 ml chilled wash buffer (10 mM Tris–HCl pH 7.4, 10 mM NaCl, 3 mM
MgCl2, 0.1% Tween-20, 1 mM DTT, 1% BSA and 1 U µl−1 RNase inhibitor) to
the lysed sample. The mix was pipetted five times, and the suspension
was passed through a 70 µm Flowmi cell strainer before being filtered
through a 40 µm Flowmi cell strainer into a new 1.5 ml tube, then centri-
fuged at 500g for 5 min at 4 °C. The supernatant was removed without
disrupting the nuclei pellet, then the pellet was resuspended in chilled
PBS-RNase inhibitor (1× PBS supplemented with 1 U µl−1 RNase inhibitor
(3335399001; Sigma)). If cell debris and large clumps were observed,
it was passed through a 40 µm cell strainer again.

Isolation of nuclei from cell lines. Cells (100,000–3,000,000)
were  washed  with  2 ml  ice-cold  1×  DPBS  (catalog  no.  14190144;
Gibco) and centrifuged at 300g for 5 min at 4 °C. The cell pellets were
resuspended  in  200 µl  chilled  1×  lysis  buffer  (10 mM  Tris–HCl
pH  7.4,  catalog  no.  T2194;  Sigma-Aldrich),  10 mM  NaCl  (cata-
log no. 59222C; Sigma-Aldrich), 3 mM MgCl2 (catalog no. M1028;
Sigma-Aldrich), 0.1% Tween-20 (catalog no. 28320; Thermo Fisher),

Articlehttps://doi.org/10.1038/s41592-024-02586-y0.1% NP40 (catalog no. 59222C; Sigma-Aldrich), 0.01% digitonin (cat-
alog no. BN2006; Thermo Fisher), 1 mM DTT (catalog no. 646563;
Sigma-Aldrich), 1% BSA (catalog no. A1933; Sigma-Aldrich) and 1 U µl−1
RNase inhibitor (catalog no. N2615; Promega)), and the mix was pipet-
ted ten times. After incubation for 3–5 min on ice, 1 ml chilled wash
buffer (10 mM Tris–HCl, pH 7.4, 10 mM NaCl, 3 mM MgCl2, 0.1% Tween-
20 and 1% BSA) was added to the lysed cells. The mix was pipetted five
times then centrifuged at 500g for 5 min at 4 °C and resuspended in
ice-cold PBS-RNase inhibitor.

Fixation of nuclei. Nuclei were fixed by adding formaldehyde (catalog
no. F8775; Sigma-Aldrich, at a final concentration of 1% for cell lines or
1.5% for primary tissues) and incubated at room temperature for 10 min,
then centrifuged at 600g for 5 min at 4 °C to remove supernatant. All
centrifugations were performed on a swing bucket centrifuge. Then,
the cell pellet was washed twice with 1 ml PBS-BSA-RNase inhibitor and
centrifuged at 500g for 5 min at 4 °C. The supernatant was removed
without disrupting the nuclei pellet, after which the pellet was resus-
pended in chilled diluted nuclei buffer (PN-2000153, 10x Genomics)
and placed on ice. Subsequently, we immediately proceeded with the
UDA-seq.

i7-only Tn5 transposome assembly. i7-only Tn5 transposome was
assembled for UDA-seq transcriptome library construction. In detail,
the assembly of the i7-only Tn5 transposome was performed accord-
ing to the manufacturer’s instructions for TruePrep Tagment Enzyme
(catalog no. S601-01; Vazyme) reagent. Tn5-top_ME and TN5_R2_index
(sequences are provided in Supplementary Table 7) were synthe-
sized and purified by high-performance liquid chromatography
(Sangon Biotech, Shanghai) and dissolved into the annealing buffer
at a final stock concentration of 10 µM. For the annealing reaction,
oligonucleotides were mixed at a 1:1 molar ratio at 10 µM and mixed
thoroughly. The samples were annealed using the following ther-
mocycling parameters: 75 °C for 15 min, 60 °C for 10 min, 50 °C for
10 min, 40 °C for 10 min and 25 °C for 30 min. After this step, the
oligonucleotide cassette can be aliquoted and frozen at −20 °C for
future transposome assemblies. To assemble the Tn5 transposase,
we mixed 14 µl of oligonucleotide cassette from the previous step
with 8 µl of TruePrep Tagment Enzyme and 78 µl coupling buffer,
mixed well and then incubated for 1 h at 30 °C in a thermocycler. The
resulting 100 µl of assembled transposome can be stored at −20 °C
for at least 1 month.

sc3′-RNA-seq and sc5′-RNA-seq UDA-seq
For the step-by-step protocol for scRNA UDA-seq, see ref. 62.

Microfluidics droplet barcoding. Fixed whole cells or nuclei were
counted by using a LUNA automated cell counter (Luna-FL). A certain
number of cells were partitioned and barcoded using the 10x Genomics
Chromium Controller (10x Genomics) and the Single Cell 3′ Library and
Gel Bead Kit (10x Genomics; PN-PN-1000268) or Single Cell 5′ Library
and Gel Bead Kit (10x Genomics; PN-1000263), or upgraded instrumen-
tation (Chromium X, which can generate twice the number of droplets)
and upgraded 10x Genomics reagents (Chromium GEM-X Single Cell
5′ Reagent Kits v3) according to the manufacturer’s recommended
protocol. After the generation of single-cell gel bead-in-emulsions
(GEMs), in situ reverse transcription reaction was performed at 53 °C
for 45 min with a 4 °C hold.

Release of cells from droplets and splitting. Recovery agent (125 µl)
was added to the GEMs immediately following the completion of the RT
reaction, to release cells. The recovery agent/partitioning oil (pink) was
slowly removed from the bottom of the tube and and discarded. PBS
(120 µl) was added to the remaining aqueous phase (80 µl), mixed thor-
oughly and then the liquid was dispensed evenly into a 96-well plate,

Nature Methods

with each well receiving 2 µl. After brief centrifugation, the products
were incubated in a thermomixer with 85 °C for 5 min and a 4 °C hold.

Cell purification. The subsequent purification step can be accom-
plished in three distinct ways. (1) The first method is direct PCR, as
the amount of liquid added to each well after the preceding reaction
step is minimal and has a limited impact on the PCR reaction system.
(2) The second method entails enzymatic digestion to remove the
excess oligos, followed by PCR. In brief, 2 µl of ExoSAP-IT (catalog no.
78201.1.ML; Applied Biosystems) was added to each well. After brief
centrifugation, the products were incubated in a thermomixer at 37 °C
for 30 min and 80 °C for 25 min. This method is capable of detecting
15% more genes than the first method. (3) The third method employs
the Dynabeads SILANE genomic DNA kit (catalog no. 37012D; Invit-
rogen) to purify the products according to the manufacturer, after
which PCR is performed. This method detects a comparable number
of genes to the second method, but the procedure is more intricate.
Consequently, the second approach is the optimal choice in terms of
data quality and ease of use.

Post-indexing PCR and purification. Next, index PCR mix (1× KAPA
HiFi HotStart Ready Mix (catalog no. KK2602; KAPA), 0.5 µM partial
template switch oligo (TSO)/IS primer and 0.5 µM Truseq-i5 index
primer (oligo sequences are provided in Supplementary Table 7)) was
added to each well (note that the Truseq-i5 index primer is unique in
each well) in a final volume of 20 µl. After brief centrifugation, the PCR
mix was incubated in a thermomixer to perform enrichment index
PCR with 98 °C for 3 min, then 10 or 11 cycles of 98 °C for 15 s, 63 °C
for 20 s and 72 °C for 1 min, and finally 72 °C for 1 min. All indexed PCR
products in one 96-well plate were pooled and purified with 0.6× XP
beads (catalog no. A63881; Beckman Coulter), eluting in 40 µl of EB
buffer (catalog no. 19,086; Qiagen).

sc-RNA-seq library construction. cDNA products (50 ng) were mixed
with 15 µl i7-only TN5 Tagmentation Mix (5 µl self-assembly i7-only TN5,
prepared as described above) and 10 µl 5× reaction buffer (catalog no.
S601-01; Vazyme) in a final volume of 50 µl. Tagmentation reactions
were incubated at 55 °C for 10 min, followed by purification with 0.8×
XP beads, eluting in 40 µl of EB buffer. Then, fragmented cDNA was
mixed with 60 µl of library enrichment mix (50 µl NEBNext Ultra II
Q5 Master Mix (catalog no. M0544L; NEB), 5 µl 10 µM Partial P5 and
5 µl 10 µM Nextare-i7 index primer). The reaction was amplified in a
thermocycler at 72 °C for 5 min, 98 °C for 45 s, eight or nine cycles of
98 °C for 20 s, 60 °C for 30 s and 72 °C for 1 min, and finally 72 °C for
5 min, with storage at 4 °C. Libraries were size-selected with 0.6–0.8×
XP beads and eluted in 25.5 µl EB. The final libraries were quantified
using a Bioanalyzer high-sensitivity DNA chip (50674626; Agilent) and
Qubit HS assay (Q32854; Thermo Fisher Scientific) and then sequenced
in MGISeq-T7 (MGI Tech Co., Ltd.) with a 150 bp paired-end read length,
targeting a depth of 10,000–50,000 reads per cell.

Single-cell VDJ enrichment from UDA-seq (sc5′-RNA-seq). VDJ
libraries were enriched from the PBMC cDNA product of UDA-seq
(sc5′-RNA-seq) by using two consecutive nested PCRs and VDJ library
preparation according to the manufacturer’s protocol (Chromium
Single Cell V(D)J Reagent Kits, 10x Genomics). The final libraries were
sequenced in MGISeq-T7 (MGI Tech Co., Ltd.) with a 150 bp paired-end
read length, targeting a depth of 5,000 reads per cell.

Multiome (sn3′-RNA and ATAC-seq) UDA-seq
For a step-by-step protocol of Multiome UDA-seq, see ref. 63.

Chromatin tagmentation. A certain number of fixed nuclei (5 µl) were
resuspended in transposition mix (7 µl ATAC buffer B, 3 µl ATAC enzyme
B, PN-1000283; 10x Genomics) and incubated at 37 °C for 60 min.

Articlehttps://doi.org/10.1038/s41592-024-02586-yMicrofluidics droplet barcoding. After chromatin tagmentation,
nuclei were partitioned and barcoded using the Chromium Controller
(10x Genomics) and the Chromium Next GEM Single Cell Multiome
ATAC + Gene Expression (PN-1000283; 10x Genomics) according to
the manufacturer’s recommended protocol. After the generation of
single-cell GEMs, in situ RT reaction and ligation reaction were per-
formed at 37 °C for 45 min and 25 °C for 30 min with a 4 °C hold.

Release of cells from droplets and splitting. The operation of
releasing nuclei and spilling to 96-well plates is the same as UDA-seq
(sc3′-RNA-seq and sc5′-RNA-seq). Then, 1 µl of proteinase K (catalog no.
W9527; Tiangen) and 5 µl of EB buffer were added to each well (with 2 µl
of products), followed by thorough vortexing. After brief centrifuga-
tion, products were incubated in a thermomixer with 55 °C for 10 min
and 85 °C for 5 min and a 4 °C hold.

Purification of nuclei. Dynabeads SILANE genomic DNA kit (catalog
no. 37012D; Invitrogen) was employed to purify the products according
to the manufacturer. A final 10 µl of EB buffer for each well was used
to elute the beads.

Post-indexing PCR for both modality and purification. Next, 20 µl
of index PCR mix (15 µl NEBNext Ultra II Q5 Master Mix (catalog no.
M0544L; NEB), 0.5 µM Partial TSO/IS, 0.5 µM Truseq-i5 index primer,
0.5 µM P5 primer and 0.5 µM Nextare-i7 index primer) (Sangon Biotech;
oligo sequences are provided in Supplementary Table 7) was added to
each well (note that the Truseq-i5 index primer and Nextare-i7 index
primer are unique in each well), each of which already contained the
nuclei purification products. After brief centrifugation, index PCR
reaction was performed at 72 °C for 5 min, 98 °C for 3 min, then seven
cycles of 98 °C for 20 s, 63 °C for 30 s and 72 °C for 1 min, and finally
72 °C for 1 min. Then, half of the indexed PCR products in one 96-well
plate were pooled and purified with 1.6× XP beads, eluting in 160 µl
of EB buffer.

sc-ATAC-seq library construction. The post-indexing product (40 µl)
was mixed with 60 µl of ATAC-seq enrichment mix (50 µlx KAPA HiFi
HotStart Ready Mix, 5 µl of 10 µM Partial P5 and 5 µl of 10 µM P7 primer).
The reaction was amplified in a thermocycler at 98 °C for 45 s, then
seven to nine cycles of 98 °C for 20 s, 67 °C for 30 s and 72 °C for 20 s,
and finally 72 °C for 1 min. Libraries were size-selected with 0.5–1.4×
XP beads and eluted in 25.5 µl EB. The final libraries were sequenced in
MGISeq-T7 (MGI Tech Co., Ltd.) with a 100 bp paired-end read length,
targeting a depth of 10,000–50,000 reads per cell.

cDNA enrichment. The post-indexing product (40 µl) was mixed with
60 µl of cDNA enrichment mix (50 µlx KAPA HiFi HotStart Ready Mix,
5 µl of 10 µM Partial P5 and 5 µl of 10 µM Bio-Tso/ISPCR). The reaction
was amplified in a thermocycler at 98 °C for 3 min, then four or five
cycles of 98 °C for 15 s, 63 °C for 20 s and 72 °C for 1 min, and finally
72 °C for 1 min. The product was then purified with Dynabeads MyOne
Streptavidin C1 (catalog no. 65,001; Invitrogen). In brief, 10 µl of Dyna-
beads MyOne Streptavidin C1 was washed twice with 1× B&W buffer
(5 mM Tris pH 8.0, 1 M NaCl, 0.5 mM EDTA). After washing, the beads
were resuspended in 100 µl of 2× B&W buffer (10 mM Tris pH 8.0, 2 M
NaCl, 1 mM EDTA) and mixed with the sample. The mixture was rotated
on an end-to-end rotator at 10 rpm for 60 min at room temperature.
The lysate was put on a magnetic stand to separate the supernatant
and beads, then the beads were washed with 100 µl 1× B&W buffer,
and 100 µl EB buffer again. Finally, beads were resuspended in 40 µl
nuclease-free water. Enriched cDNA products (40 µl) (with C1 beads)
were then mixed with cDNA amplifaction mix (50 µlx KAPA HiFi Hot-
Start Ready Mix, 5 µl of 10 µM Partial P5, 5 µl of 10 µM Tso/ISPCR). The
reaction was amplified in a thermocycler at 98 °C for 3 min, then four
or five cycles of 98 °C for 15 s, 63 °C for 20 s and 72 °C for 1 min, then

Nature Methods

finally 72 °C for 1 min. Amplified cDNA was then purified with 0.6× XP
beads and eluted in 40 µl EB.

sc-RNA-seq library construction. cDNA products (50 ng) were taken
for further library construction, the same as for UDA-seq (sc3′-RNA-seq
and  sc5′-RNA-seq).  The  final  libraries  were  then  sequenced  in
MGISeq-T7 with a 150 bp paired-end read length, targeting a depth of
10,000–50,000 reads per cell.

UDA-seq collision rate estimate
The collision rate estimation followed the single-cell combinatorial
indexed cytometry sequencing (SCITO-seq) formula with the 10x
Genomics Chromium parameters setting.

Species mixture analysis
For the two-species mixture (human and mouse cell line) scRNA-seq,
sequencing data were mapped to a human and mouse mixture genome
reference (hg38+mm10), and mapped and quantified by using the Cell
Ranger Single Cell software suite (version 6.0.2). We defined a cell as a
mouse cell if its mm10 UMI ratio was greater than 0.85. A cell was con-
sidered to be a human cell if its hg38 UMI ratio was greater than 0.85.

For the three-species mixture (human cell line, mouse cell line and
locust tissue) scRNA-seq, sequencing data were mapped to a human,
mouse and locust ref. 64 by using the Cell Ranger Single Cell software
suite (version 6.0.2). Similarly, a cell was determined to be a locust cell
if its locust UMI count number was two fold greater than other species’
UMI count number, and similarly for mouse and human cell species
determination.

For the two-species (human and cell line) Multiome analysis,
sequencing data were mapped to a human and mouse mixture genome
reference by using Cell Ranger ARC (version 2.0.1). For the scRNA-seq
part, the determination of a cell’s species was the same as the scRNA-seq
species mixture analysis described above. For the scRNA-seq and
scATAC-seq paired profiled part, a cell was considered to be a human
cell if its hg38 UMI ratio was greater than 0.85 or if its hg38 ATAC-seq
fragment ratio was greater than 0.85.

GEM-X PBMC scRNA-seq cell state annotation
To infer the detailed cell states within a single PBMC sample profiled
using UDA-seq with GEM-X reagents, we conducted Seurat v4 reference
mapping to align our query data to the highly detailed cell state anno-
tation presented in the Human Severe Acute Respiratory Syndrome
Coronavirus 2 challenge study65, in which 83 cell states from multiple
PBMC samples collected under different coronavirus disease 2019
infection conditions were annotated, leveraging both RNA expres-
sion and surface protein (CITE-seq) measurements. We annotated our
query cells on the basis of the predicted cell state assignments and
manual curation. We further leveraged the reference data to infer the
imputed surface protein levels for the query cells. Finally, we calculated
a weighted nearest neighbor (WNN) graph to integrate a weighted
combination of the RNA assay and predicted_ADT assay, and further
used this graph to generate the uniform manifold approximation and
projection (UMAP) visualization.

Basic quality comparison of the sequencing data
We extensively tested the single-cell Multiome to compare data qual-
ity. Our testing involved various cell lines, such as mouse NIH 3T3 and
human Hela cells, as well as multiple human tissue samples, including
kidney biopsy, lung cancer and pancreatic cancer. Different tissue
types have an impact on the quality of single-cell data. To make com-
parisons, we downloaded raw data from publicly available datasets
generated using the standard 10x Multiome kit for the NIH 3T3 cell line
and the corresponding tissue samples. We applied consistent quality
control criteria to all datasets, keeping only cells with more than 200
detected genes and less than 10% mitochondrial percentage, to ensure

Articlehttps://doi.org/10.1038/s41592-024-02586-yconsistency. Initially, we processed all data using cellranger-arc 2.0.1
with a 10x-provided reference genome to obtain the exact number of
high-quality cells in each dataset. Then, we uniformly downsampled the
raw data to 20,000 read pairs per cell for ATAC data and 20,000 reads
per cell for RNA data. After downsampling, we reran the cellranger-arc
process to generate the final output matrices. These matrices were then
used to evaluate the data quality across different samples. For samples
with original sequencing depths higher than 20,000 reads per cell, we
also conducted comparisons at multiple sequencing depths.

The public datasets used in this comparison were sourced as
follows: the scMultiome data for NIH 3T3 cells were obtained from
PRJEB50424, the kidney biopsy data from the GSE220251 dataset, the
lung cancer data from the GSE241468 dataset and the pancreatic cancer
data from the GSE241895 dataset.

For the comparison of 5′ scRNA-seq, we selected three datasets
from the 10x Genomics website. These datasets utilized different chem-
istry versions and were compared with UDA-seq data. To ensure con-
sistency, we downsampled datasets with more than 50,000 reads and
recalculated matrices. The quality control followed uniform criteria,
retaining all cells with mitochondrial counts below 5%.

For 5′ scRNA-seq, scVDJ-seq and surface protein data, the following

sources were used for comparison:

 (1)  For comparing scRNA-seq and scVDU-seq, ref. 66 (Kit_v1)
 (2)  For comparing scRNA-seq, ref. 67 (Kit_v2)
 (3)  For comparing scRNA-seq, ref. 68 (Kit_v3)

To calculate the TCR and BCR detection ratios, T cells were identi-
fied by the surface protein CD3-UCHT1, while B cells were identified by
the surface protein CD19-HIB19. The TCR detection percentage was
calculated as (number of cells with TCR)/(total T cell number), and
the BCR detection percentage was calculated as (number of cells with
BCR)/(total B cell number).

Female aging PBMC scRNA-seq and VDJ-seq data
preprocessing
For sequencing data mapping and quantifying, in UDA-seq, 10x bar-
codes were round 1 barcodes, and post-index were round 2 barcodes.
FASTQ files were firstly grouped by post-index (index 1–96 in the human
kidney case). For each post-index, the Cell Ranger (version 7.0.0) ‘count’
command was applied to map and quantify the scRNA-seq part of the
data. The Cell Ranger (version 7.0.0) ‘vdj’ command was applied to
map and quantify paired scVDJ-seq data. Finally, a cell barcode was
formed by the combination of the 10x barcode (round 1 barcode)
and post-index (round 2 barcode). The quantified matrix (UMI count
matrix) was aggregated by cell barcode. Demuxlet (version 2) was
applied to scRNA-seq mapping results (bam files) and each donor’s
imputed (by minimac369) Illumine Infinium Asian screening array SNP
file SNP sequencing results (VCF file, processed by Plink2 v2.070 to
assign the cell barcode to a specific donor). Droplets containing two
or more cells were excluded using Demuxlet and Scrublet71 (version
0.2.3). scVDJ-seq mapping results were paired with scRNA-seq by cor-
responding paired cell barcodes using scRepertoire72.

Female aging PBMC cohort analysis
For quality control and annotation of scRNA-seq, firstly, cells with
fewer than 200 genes and mitochondria percentage <5% were filtered
out. Then, the batch effect was removed by using Harmony (version
1.0)73 and unsupervised clustering by Seurat, and cells from clusters
4, 9 and12 were filtered out since those clusters had low UMI content.
For the remaining cells, batch effects were removed again by Harmony
and reclustering by the Seurat pipeline. After that, label transfer was
performed from the PBMC CITE-seq data3 by using Seurat (with the
FindTransferAnchors and MapQuery functions). Visualization was
done by using Scanpy74 (version 1.9.1). For scVDJ-seq data, quality con-
trol was done by scRepertoire with default parameters. Moreover, cells

Nature Methods

from scVDJ-seq that were not successfully annotated by scRNA-seq
(using the annotation procedure described above) were filtered out.
For  age  positively  related  gene  signature  analysis,  firstly,  a
pseudo-bulk RNA-seq profiled donor was formed by aggregating
the expression values from a group of cells from the same donor.
Secondly, (1) age as a continuous phenotype with (2) the pseudo-bulk
RNA-seq profile and (3) the snRNA-seq profile were used as co-inputs,
and SCIPAC (version 1.0.0) was applied to efficiently find cell types
associated with age. Age positively related cells were defined by a SCI-
PAC association >0 and a corresponding SCIPAC significance P value
below 0.05. The age positively related signature gene set was selected
by differentially expressed gene between age positively-associated
cells and non-associated cells with a log2 fold change of average expres-
sion >1 and Bonferroni-adjusted P value of <0.05. Gene Ontology (GO)
analysis of the age positively associated genes was performed by using
clusterProfiler75 (version 4.8.1).

For the analysis of the subgroup of CD4 naive cells, unsuper-
vised reclustering was performed on CD4 naive scRNA-seq data by
using the Seurat pipeline, as follows: (1) normalization of raw UMI
counts matrix by using the NormalizeData function with default
parameters, (2) finding the top 2,000 highly variable genes by using
the FindVariableFeatures function with default parameters, (3) prin-
ciple component analysis (PCA) performed by using the ScaleData
and RunPCA functions with default parameters, (4) removing the
batch effect by the Harmony73 method, (5) applying unsupervised
clustering by using the FindNeighbors (parameters: dims = 1:20, reduc-
tion = “harmony”) and FindClusters (parameters: resolution = 0.5 and
other default parameters), functions and (6) UMAP performed by the
RunUMAP function, using the top 20 Harmony-corrected principle
components (PCs). The protein expression level was imputed by using
PBMC CITE-seq data with Seurat. Marker genes of cluster 2 in CD4 naive
cells were found by comparison of cluster 2 with other CD4 naive cells.

Human kidney sequencing data preprocessing
For sequencing data mapping and quantifying, 10x barcodes were
round 1 barcodes and post-index were round 2 barcodes. Multiome
sequencing data FASTQ files were firstly grouped by post-index (in this
case, index 1–96 from two channels). For each post-index, Cell Ranger
ARC (version 2.0.1) was applied for mapping and quantification. A cell
barcode was formed by the combination of the 10x barcode (round 1
barcode) and post-index (round 2 barcode). Demuxlet was applied on
both the snRNA-seq and snATAC-seq mapping results (bam format files)
and each donor’s imputed (by Michigan Imputation Server; https://
imputationserver.sph.umich.edu/) Illumine Infinium Asian screen-
ing array SNP file (VCF format file, processed by Plink2 version 2.0) to
assign the cell barcode to a specific donor. Doublets with multidonor
assignments were removed.

For data quality control, for snRNA-seq data, cells whose gene
number was greater than 200 and mitochondria gene percentage was
<5% survived. For snATAC-seq data, cells whose transcriptional start
side (TSS) enrichment score was >4 and fragment number was >1,000
survived. Cells that survived both snRNA-seq and snATAC-seq quality
control procedures were used in downstream analysis.

Kidney snRNA-seq part analysis. After data quality control, unsuper-
vised clustering and visualization were carried out by using the Seurat
pipeline, as follows: (1) normalization of the raw UMI count matrix by
using the NormalizeData function with default parameters, (2) finding
the top 2,000 highly variable genes by using the FindVariableFeatures
function with default parameters, (3) PCA by using the ScaleData and
RunPCA functions with default parameters, (4) unsupervised clustering
by using the FindNeighbors (with parameter dims = 1:20 and others at
default) and FindClusters (with parameter resolution = 2.5 and others
at default) functions and (5) UMAP performed by using the function
RunUMAP with the top 20 PCs.

Articlehttps://doi.org/10.1038/s41592-024-02586-yAnnotation of kidney snRNA-seq results was achieved by using
Seurat label transfer procedures. Labels of kidney cell type annota-
tions (subclass.l2) were transferred from a kidney atlas76 to snRNA-seq
data in this study with the Seurat FindTransferAnchors (parameter
dums = 1:30) and TransferData (with default parameters) functions.
Cells with prediction score ≤0.4 were filtered out. Abbreviations and full
names for all cell types can be found on https://github.com/yyt1010/
UDA_seq_Kindey_Cell_full_name/tree/main.

Kidney snATAC-seq part analysis
After mapping, we obtained 96 sublibrary fragment files for two
channels, respectively. On the basis of the cell barcodes, more than
200,000 cells paired with high-quality snRNA-data were selected
from 96 × 2 = 196 scATAC fragment files. New fragment files for 44
donors (one file per donor) were rebuilt with these cells for subse-
quent analysis. First, ArchR (version 1.0.2) was used to create arrow
files (filtering on TSS ≥4 and filterFrags ≥1,000) with the addition of
TileMatrix and GeneScoreMatrix. After cell annotation in snRNA-seq,
cells that were both high quality in snATAC-seq and annotated on
snRNA-seq data remained. In summary, we obtained 207,671 cells
with a median TSS enrichment score of of 10.6 and 8,116 fragments.
Quality control plots were visualized for TSS enrichment, fragments
and fragments in peak (FRiP), grouped by states (health or disease) or
donors, respectively. Secondly, dimensionality reduction was applied
by using iterative latent semantic indexing based on TileMatrix (with
default parameters plus iterations = 2 and dimsToUse = 1:30), followed
by cell clustering with the addClusters function (with resolution = 2
and maxClusters = 50). In this step, 42 clusters were identified. The
visualization by UMAP was thus finished (with default parameters of
nNeighbors = 30 and minDist = 0.5). Thirdly, cell types with <50 cells
were filtered out. Then, addGroupCoverages, addReproduciblePeakSet
and addPeakMatrix with default parameters were used for peak calling.
After peak calling, marker peaks and marker genes in each cell type were
obtained by using getMarkerFeatures with PeakMatrix and GeneScore-
Matrix, respectively. For the visualization of cell type-specific marker
peaks located on the promoter of marker genes, the scaled matrix was
obtained by using plotMarkerHeatmap(seMarker = markerGenes, cut-
Off = “FDR < = 0.1 & Log2FC ≥ 2”, transpose = T, returnMatrix = T). The
marker genes with marker peaks for each cell type were selected from
the matrix by using the following cutoff: a value of one cell type of 2, all
values of other cell types of <−1 and a standard deviation of other cell
types’ values of <0.3. Then, getGroupBW(groupby = “cell_type”, nor-
mMethod = “None”) was used to obtain bigwig files for each cell type,
followed by IGV visualization of selected marker genes as mentioned
above. MotifMatrix was obtained by using the addDeviationsMatrix
function. Adding the gene expression matrix to the ArchR project by
using addGeneExpressionMatrix, peak to gene links were calculated
by using addPeak2GeneLinks.

Human kidney proteinuria positive-related cell type analysis.
In this study, we regarded donors with 24 h urinary protein ≥3.5 g as
having massive proteinuria and as nonproteinuria donors otherwise.
A pseudo-bulk RNA-seq profiled donor was formed by aggregating the
expression values (UMI counts) from a group of cells from the same
donor. Cells annotated as altered states were not taken into considera-
tion. Three types of data, viz. (1) binary phenotype data for each donor:
proteinuria or nonproteinuria, (2) pseudo-bulk RNA-seq profiled data
and (3) snRNA-seq profiled data, were used as inputs (using randomly
selected half of the cells, for computational efficiency) for Scissor
(version 2.0.0) with parameter α = 0.8 to identify the proteinuria
positively related cell subpopulation (Scissor+ cells).

For proteinuria positive signature analysis, differential gene
expression was performed between proteinuria positively related cells
(Scissor+ cells) and other cells by using the R package Seurat (version
4.9) FindMarkers (with parameter max.cells.per.ident = 500 and others

Nature Methods

at default) function. Highly expressed genes in proteinuria positively
related cells were selected for Bonferroni-adjusted P value <0.01, log2
fold change of average expression of >1 and non-gender-related genes.
The single-cell-level proteinuria positive signature score was calcu-
lated with those highly expressed genes by using the Seurat function
AddModuleScore with default parameters. The donor-level proteinuria
signature score was calculated as the median value of single all cells’
signature scores from that donor. The differential significance between
each group of the donor was calculated by using the R package rstatix
(version 0.7.0).

To characterize cell–cell communication differences between
immune cells, EC-type cells and podocytes between proteinuria greater
than or equal to 3.5 g per 24 h and healthy human controls, the CellChat
(version 1.6.1) package was used to identify major signal strength dif-
ferences in a given signaling network and predict critical information
flows for specific cell types.

Human kidney podocyte proteinuria positive-related cell
subcluster analysis
Firstly, only podocytes from the Scissor outputs were selected with
unsupervised reclustering on podocyte snRNA-seq data by using the
Seurat pipeline, as follows: (1) normalization of the raw UMI count
matrix by using the NormalizeData function with default parameters,
(2) finding the top 2,000 highly variable genes by using the FindVari-
ableFeatures function with default parameters, (3) PCA by using the
ScaleData and RunPCA functions with default parameters, (4) unsu-
pervised clustering by applying the FindNeighbors (with parameter
dims = 1:20 and the others at default) and FindClusters (with para-
meters resolution = 0.8 and others at default) functions and (5) UMAP
by using the RunUMAP function with the top 20 PCs.

For proteinuria phenotype enrichment analysis, the proteinuria
phenotype enrichment score of cluster i was calculated by using the
formula

Enrichmenti = log2 (

Pi
Exi

+ pseudo_value) ,

(1)

where Pi is the proportion of cluster i in the proteinuria positive-related
cells identified by Scissor (Scissor+ cells), Exi is the expected proportion
of cluster i in proteinuria positive-related cells, while setting pseudo_
value to 0.000001, to avoid meaningless operations. The podocyte
subcluster whose enrichment score was highest and greater than 0 was
regarded as a proteinuria phenotype-enriched subcluster.

For eRegulon identification in podocytes, firstly, the ATAC-seq
peak matrix (obtained from the ArchR version 1.0.2 peak caller) was sub-
setted according to the podocyte’s cell barcode. Peaks that were open in
fewer than five cells were filtered. The top 100,000 highly variable open
peaks identified by the Seurat function FindVariableFeatures (with
parameters selection.method = “disp” and nfeatures = 1,000,000) were
retained for downstream analysis. Secondly, a set of genes differentially
expressed between cluster 1 and other clusters (except cluster 0, since
it had a small value of positive enrichment of proteinuria phenotype)
was selected based on having a log2 fold change of average expres-
sion greater than 0.5. Only these genes were retained for downstream
analysis. Thirdly, an snATAC-seq topic-based model was built by using
the Cis-topic77 algorithm with the Python package pycisTopic (ver-
sion 1.0.3) run_cgs_models function (with parameters n_topics = 10,
randon_state = 555, alpha = 50, alpha_by_topic = True, eta = 0.1 and
eta_by_topic = False). The methods used for the binarization of each
topic were Otsu and ntop (nTop = 3,000) with the binarize_topics
function. The accessibility of regions was imputed and normalized
by using the impute_accessibility (parameter scale_factor = 10**6)
and normalize_scores (parameter scale_factor = 10**4) functions.
Peaks from Otsu and the top 3,000 for each topic were selected as
candidate enhancers for downstream analysis. Then, motif enrichment

Articlehttps://doi.org/10.1038/s41592-024-02586-yanalysis was performed by using pycistarget.motif_enrichment_dem
and pycistarget.motif_enrichment_cistarget. Utilizing Scenicplus
(version 1.0.1), an RNA and ATAC paired scenicplus object was cre-
ated. The gene regulatory network was built by using the scenicplus
function build_grn (with parameters quantiles = c(0.85,0.90,0.95),
order_regions_to_gene_by = “importance”, rho_threshold = 0.02 and
keep_extended_motif_annot = True). After the gene regulatory network
was built, we set rho to −0.05 and 0.05 for negative correlated and
positive correlated, respectively. Important eRegulons were selected
on the basis of the regulon specificity score (RSS).

Human kidney impairment positive related cell type analysis
AKI and CKD were diagnosed by nephrologists according to Kidney
Disease: Improving Global Outcomes guidelines. Impairment was
classified into three types: immune mediated, metabolic mediated
and other. Similar to the proteinuria analysis, a pseudo-bulk RNA-seq
profiled donor was formed by aggregating the expression values (UMI
counts) from a group of cells from the same donor. Cells annotated as
altered states were not included. Three types of data, viz. (1) a binary
phenotype for each donor: impairment or non-impairment, (2) the
pseudo-bulk RNA-seq profile and (3) the snRNA-seq profile, were used
as inputs (using a randomly selected half of cells, for computational
efficiency) for Scissor (version 2.0.0) with parameter α = 0.05 for
immune-mediated impairment and α = 0.5 for metabolic-mediated
impairment, to identify the impairment related cell subpopulation
(Scissor+ cells).

For  immune-mediated  impairment  signature  and
metabolic-mediated impairment analysis, the way to select the sig-
nature gene set and calculate the signature score was the same as for
the proteinuria signature analysis described above. For human kidney
EC-GC impairment positive related cell subcluster analysis, firstly, only
EC-GCs were selected from the Scissor output (both immune medi-
ated and metabolic mediated), then unsupervised reclustering was
performed on the EC-GC snRNA-seq data by using the Seurat pipeline,
as follows: (1) normalization of the raw UMI count matrix by using the
NormalizeData function with default parameters, (2) finding the top
2,000 highly variable genes by using the FindVariableFeatures function
with default parameters, (3) PCA by using the ScaleData and RunPCA
functions with default parameters, (4) unsupervised clustering by
using the FindNeighbors (with parameter dims = 1:20 and others as
default) and FindClusters (with parameter resolution = 0.8 and others
as default) functions and (5) UMAP performed by using the RunUMAP
function with the top 20 PCs.

For proteinuria phenotype enrichment analysis, cluster 5 was
filtered out since its cell number was less than 50. The impairment
phenotype enrichment score for cluster i was calculated by using equa-
tion (1) above, but with  Pi being the the proportion of cluster i in the
immune-mediated or metabolic-mediated phenotype positive related
cells identified by Scissor (Scissor+ cells) and  Exi being the expected
proportion of cluster i in the injury positive related cells, setting
pseudo_value to 0.000001 to avoid meaningless operations. The EC-GC
subcluster whose enrichment score was highest and greater than 0 was
regarded as the immune-mediated or metabolic-mediated impairment
phenotype enriched subcluster.

For eRegulon identification in EC-GCs, the methods used were the
same as for eRegulon identification in podocytes, except the parameter
nTop was set at 8,000 in the binarize_topics function.

Analysis of UDA CRISPER screen data
The preprocessing of the UDA CRISPER sequencing data was the same
as for the PBMC cohort RNA-seq part. In quality control of the UDA
CRISPER screen, unsupervised clustering based on the single-cell RNA
profile showed that cluster 11 had an extremely low UMI content, while
clusters 4 and 7 had relatively higher sgRNA numbers than other clus-
ters. Thus, clusters 4, 7 and 11 were filtered out. For sgRNA assignment,

Nature Methods

we assigned the most dominant sgRNA (where the sgRNA UMI content
exceeded the sum of all other sgRNA UMI contents within a cell) to the
cell. Finally, only uniquely assigned cells survived.

For the analysis of two groups of cells, single-cell RNA profiled
SNU16 cells were subject to unsupervised clustering by using the Seurat
pipeline. In the PCA analysis, two groups of cells were clearly observed
along two dimensions (PC1 and PC2) in the visualization. Cluster 9
was removed as it had the lowest cell number and was scattered. We
grouped clusters 8, 0 and 7 into group 1 and the other clusters into
group 2.

For MYC-related pathway analysis, the MYC-related pathways were
downloaded from the Kyoto Encyclopedia of Genes and Genomes
database (KEGG)78. Within each group of SNU16 cells, perturbed upreg-
ulated or downregulated genes for each target gene were defined as
highly upregulated genes in comparison with cells with the target gene
and negative control cells by using the Seurat differential expression
gene pipeline, with the R package clusterProfiler (version 4.8.1) to do
the KEGG pathway enrichment and restrict the enrichment results on
MYC-related pathways. The enrichment score was −log10( p_value) .
Pathways specific to a single cancer in MYC-related pathways were not
taken into consideration. The heatmap was plotted by using the R
package ComplexHeatmap (version 2.10.0)79.

For genotype to multiple phenotypes analysis. We implemented
the scMAGeCK (version 1.6.0) function scmageck_lr, setting the param-
eter NEGCTRL to negative control sgRNAs and PERMUTATION to 100.

Reporting summary
Further information on research design is available in the Nature
Portfolio Reporting Summary linked to this article.

Data availability
The raw sequence data reported in this paper have been deposited in the
Genome Sequence Archive in the National Genomics Data Center, Beijing
Institute of Genomics (China National Center for Bioinformation) of
CAS under accession no. PRJCA025219 at https://ngdc.cncb.ac.cn/
gsa-human. This includes the raw data for the cell line (HRA007205,
HRA009268) as well as for the kidney and PBMCs (HRA007355). The
processed datasets can be accessed from the OMIX, China National
Center for Bioinformation/Beijing Institute of Genomics, Chinese Acad-
emy of Sciences at https://ngdc.cncb.ac.cn/omix/release/OMIX007175.
Supplementary Table 8 contains a detailed annotation for the datasets
generated by UDA-seq in this paper. According to the Ministry of Sci-
ence and Technology of the People’s Republic of China, the data related
to human genetics will be available under controlled access. Source
data are provided with this paper.

Code availability
The code used for the data processing and analysis mentioned in
the Methods section is available via GitHub at https://github.com/
lanjiangbig/UDA-seq-analysis.

References
62.  Li, Y. UDA-5′RNA-protocol. Protocols.io https://doi.org/10.17504/

protocols.io.n2bvjne15gk5/v1 (2024).

63.  Li, Y. UDA-Multiome-protocol. Protocols.io https://doi.org/

10.17504/protocols.io.5qpvokd4xl4o/v1 (2024).

64.  Wang, X. et al. The locust genome provides insight into swarm

formation and long-distance flight. Nat. Commun. 5, 2957 (2014).

65.  Lindeboom, R. G. H. et al. Human SARS-CoV-2 challenge uncovers
local and systemic response dynamics. Nature 631, 189–198
(2024).

66.  10x Genomics. hPBMCs of a Healthy Donor (Next GEM v1.1).
10x Genomics https://www.10xgenomics.com/datasets/
pbm-cs-of-a-healthy-donor-next-gem-v-1-1-1-1-standard-3-1-0
(2024).

Articlehttps://doi.org/10.1038/s41592-024-02586-y67.  10x Genomics. 5k human PBMCs stained with TotalSeq™-C

human TBNK cocktail, Chromium NextGEM single cell 5′.
10x Genomics https://www.10xgenomics.com/datasets/5k-human-
pbmcs-stained-with-totalseq-C-human-TBNK-cocktail-NextGEM
(2024).

68.  10x Genomics. 10k human PBMCs stained with TotalSeq™-C

human TBNK cocktail, Chromium GEM-X single cell 5′. 10x
Genomics https://www.10xgenomics.com/datasets/10k-human-
pbmcs-stained-with-totalseq-C-human-TBNK-cocktail-GEM-X
(2024).

69.  Das, S. et al. Next-generation genotype imputation service and

methods. Nat. Genet. 48, 1284–1287 (2016).

70.  Chang, C. C. et al. Second-generation PLINK: rising to the

challenge of larger and richer datasets. Gigascience 4, 7 (2015).

71.  Wolock, S. L., Lopez, R. & Klein, A. M. Scrublet: computational

identification of cell doublets in single-cell transcriptomic data.
Cell Syst 8, 281–291 e289 (2019).

72.  Borcherding, N., Bormann, N. L. & Kraus, G. scRepertoire:

an R-based toolkit for single-cell immune receptor analysis.
F1000Res 9, 47 (2020).

73.  Korsunsky, I. et al. Fast, sensitive and accurate integration of

single-cell data with Harmony. Nat. Methods 16, 1289–1296 (2019).
74.  Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell

gene expression data analysis. Genome Biol. 19, 15 (2018).
75.  Wu, T. et al. clusterProfiler 4.0: a universal enrichment tool for

interpreting omics data. Innovation (Camb) 2, 100141 (2021).
76.  Lake, B. B. et al. Single-nucleus RNA-seq of the Adult Human
Kidney (Version 1.0). Kidney Precision Medicine Project (KPMP)
Consortium https://datasets.cellxgene.cziscience.com/
a7445ac6-93ca-43af-810a-3809c9e4d82e.rds (2023).
77.  Bravo Gonzalez-Blas, C. et al. cisTopic: cis-regulatory topic

modeling on single-cell ATAC-seq data. Nat. Methods 16, 397–400
(2019).

78.  Kanehisa, M. & Goto, S. KEGG: kyoto encyclopedia of genes and

genomes. Nucleic Acids Res. 28, 27–30 (2000).

79.  Gu, Z., Eils, R. & Schlesner, M. Complex heatmaps reveal

patterns and correlations in multidimensional genomic data.
Bioinformatics 32, 2847–2849 (2016).

Acknowledgements
This research was supported by grants from the National Key Research
and Development Program of China (grant no. 2019YFA0801702
to L.J.), the Strategic Priority Research Program of the Chinese
Academy of Sciences (grant no. XDB38020500 to L.J.), the
National Key Research and Development Program of China (grant
no. 2023YFC3402703 to L.J.), the NSFC (grant nos. 92374104 and
31970760 to L.J., 32100479 to G.L., 81921006, 82488301, 92168201,
92149301, 82330044 and 32341001 to G.-H.L. and 32121001 and
82361148131 to W.Z.), the CAS Youth Interdisciplinary Team, the
International Partnership Program of the Chinese Academy of
Sciences (grant no. 153F11KYSB20210006 to L.J.), the CAS Project
for Young Scientists in Basic Research (grant no. YSBR-076 to G.-H.L.
and YSBR-012 to W.Z.), the national funded postdoctoral researcher

program (grant no. GZC20232568 to Y.L.), the National Key Research
and Development Program of China (grant no. 2020YFA0804000 to
G.-H.L. and 2022YFA1103700 to W.Z.), the National High Level Hospital
Clinical Research Funding (grant no. 2022-PUMCH-B-019 to L.C.),
the New Cornerstone Science Foundation (grant no. XPLORERPRIZE
2021-1045 to G.-H.L.), the Program of the Beijing Natural Science
Foundation (grant no. 724018 to G.-H.L., JQ24044 to W.Z. and 5242024
to Y.F.) and the Quzhou Technology Projects (grant no. 2022K46 to
W.Z.). Some icons in Extended Data Fig. 1 were created with BioRender.
com. The funders had no role in study design, data collection and
analysis, the decision to publish or the preparation of the manuscript.
This publication is part of the Human Cell Atlas (https://www.
humancellatlas.org/).

Author contributions
L.J. and Y.L. conceived the study and developed the UDA-seq
methods. Y.L. performed all the UDA-seq experiments. Z.H. led
the bioinformatics analyses. Z.H., Y.C., G.L., C.Y., Q.W., Y.L. and N.A.
prepared the figures. Y.X. and M.L. helped with experiments. X.M.
helped with data processing. L.X., T.L. and T.S. contributed to the
human kidney sampling. Y.F., J.P. and Q.Q. contributed to the human
PBMC sampling. Z.Q. contributed to the human lung cancer sampling.
N.J. contributed to the human cholangiocarcinoma sampling. L.J.,
L.C., G.-H.L. and W.Z. acquired the funding. L.J., L.C., G.-H.L., W.Z., F.Z.,
S.S., H.J., M.W. and S.J. obtained resources. L.J., L.C., G.-H.L., W.Z. and
S.S. supervised the study. The manuscript was written by Y.L. and L.J.
All authors read and approved the manuscript.

Competing interests
L.J., Y.L. and Z.H. are inventors on a patent application describing the
UDA-seq method. The patent does not restrict the use of the method
for educational, research or nonprofit purposes. The other authors
declare no competing interests.

Additional information
Extended data is available for this paper at
https://doi.org/10.1038/s41592-024-02586-y.

Supplementary information The online version
contains supplementary material available at
https://doi.org/10.1038/s41592-024-02586-y.

Correspondence and requests for materials should be addressed to
Shaokun Shu, Feng Zhang, Weiqi Zhang, Guang-Hui Liu, Limeng Chen
or Lan Jiang.

Peer review information Nature Methods thanks Xi Chen, Kun Zhang
and the other, anonymous, reviewer(s) for their contribution to
the peer review of this work. Primary Handling Editor: Lei Tang,
in collaboration with the Nature Methods team.

Reprints and permissions information is available at
www.nature.com/reprints.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 1 | The detailed workflow of UDA-seq. The comprehensive workflow of UDA-seq is depicted in a schematic view, illustrating its compatibility with
various libraries.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 2 | See next page for caption.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 2 | Integrity of cells after completing round 1 barcoding
in droplet. a-d. Representative AO (green)/PI (red) cell counting images of live
SNU16 cells (a), fixed SNU16 cells (b), fixed SNU16 cells released from microfluidic
droplets after completed round 1 barcoding subjected by 10x Genomics
3'-RNA-seq kits and chip (c), and fixed kidney nuclei released from droplets
after completed round 1 barcoding subjected by 10x Genomics Multiome kit
and chip (d). The images showing fixed cells/nuclei released from a microfluidic

droplet remaining intact after the first round of barcoding. Scale bar, 100 µm.
e. Representative microscopy images of droplets showing the fixed cells/nuclei
in microfluidic droplet remaining intact after the first round of barcoding.
Scale bar, 50 µm. f. Microscopy bright field images showing the fixed cells/
nuclei release from microfluidic droplet remaining intact after the first round of
barcoding. Scale bar, 30 µm.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 3 | See next page for caption.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 3 | Theoretical estimation and experimental validation.
a. The relationship between the number of loaded cells and the collision rate
is being plotted across various post-index numbers. The collision rate is being
calculated using a formula derived from SCITO-seq. b-d. Collison rates of
single-cell 3′-RNA species mixing (b), single-nuclei 3′-RNA three species (c) and
single-nuclei multiome species mixing (d) basis of the round1 barcode alone.
e. Single-nuclei 3′-RNA UDA-seq was performed on a three-species mixture
consisting of human Hela, mouse NIH3T3, and locust brain tissue. The resulting
UMAP embedding of the cells was color-coded to denote their respective species.
f. The Multiome UDA-seq was employed to analyze a mixed cell population of
two species, human HeLa and mouse NIH3T3. g. Date quality of the UDA-seq
multiome. The plots show gene number distribution for snRNA-seq and read in
peak distribution for snATAC-seq. Box plots show interquartile range with the
median marked. The whiskers extend up to 1.5 times the interquartile range,

the outliers are not displayed. The cell number for each samples, n = 3,372;
207,789; 455; 10,232; 6,735; 1,971). h. A comparison was made between UDA-
seq (n = 13,905) and 10x Genomics (n = 9,010) for reagent v3 (GEM-X). Median
numbers of detected genes are shown at the top of each column. Box plots show
interquartile range with the median marked. The whiskers extend up to 1.5 times
the interquartile range, the outliers are not displayed. i. The violin plot showed
the gene number detected for a sub-library (representing 1/12 of the entire
library) of PBMC constructed by UDA-seq (5′-RNA) using GEM-X reagents at a read
depth of 500,000 reads per cell. j. The dot plot displayed differentially expressed
genes across the PBMC uncommon cell states, generated by 5′-RNA and VDJ
UDA-seq using GEM-X reagents. Left panel: the gene expression level. Right panel:
the imputed protein expression level. The imputation is from the CITE-seq PBMC
atlas.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 4 | See next page for caption.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 4 | Data quality of kidney disease cohort. a. The violin
plot illustrates the distribution of gene numbers per cell (top) and FRiP per
cell (middle) across donors in the kidney disease cohort. The bottom panel
showing the number of cells corresponding to each donor. Box plots show
interquartile range with the median marked. The whiskers extend up to 1.5 times
the interquartile range, the outliers are not displayed. b. Violin plot displaying

the distribution of TSS (Transcriptional Start Sites) enrichment scores per cell
across donors in each channel. Box plots show interquartile range with the
median marked. The whiskers extend up to 1.5 times the interquartile range, the
outliers are not displayed. c. A violin plot illustrating the distribution of fragment
numbers (base 10 logarithms) per cell across donors in each channel. d. UMAP
embedding color-coded by channel.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 5 | Proteinuria positively related podocyte sub-clusters.
a. Proteinuria positively related cells enriched in podocyte sub-clusters 1. b.
Important eRegulons identified by SCENIC+ in sub-cluster 1. The heatmap colors

represent scaled TF gene expression, and the dot size represents scaled target
region enrichment. The violin plot displayed highly expressed genes in sub-
cluster 1. c. The violin plot displayed highly expressed genes in sub-cluster 1.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 6 | Cost efficiency for UDA-seq and 10x Genomics (sequencing by MGI-T7). The comprehensive cost comparison between UDA-seq and 10x
Genomics (sequencing by MGI-T7).

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 7 | Cost efficiency for UDA-seq and 10x Genomics (sequencing by illumina). The comprehensive cost comparison between UDA-seq and 10x
Genomics (sequencing by illumina).

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 8 | See next page for caption.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 8 | Data quality of PBMCs from human aging cohort.
a. The violin plot shows the distribution of gene numbers per cell across donors
in the cohort. The number of cells per donor showing in (b). Box plots show
interquartile range with the median marked. The whiskers extend up to 1.5 times
the interquartile range, the outliers are not displayed. b. The bar plot shows the
number of cells per donor in the cohort. c. Aging-associated cells are displayed
in the UMAP plot, with colors indicating the strength of the association. Positive

and negative numbers represent positive and negative associations, respectively.
d. Imputed CD31 protein expression is shown across CD4 Naïve sub-clusters.
The imputation is from the CITE-seq PBMC atlas. e. The gene expression level of
PECAM1 across CD4 Naïve sub-clusters is displayed. The PECAM1 gene encodes
the CD31 protein. f. The percentage of BCR and TCR detection in scVDJ-seq is
shown in this cohort.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 9 | See next page for caption.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-yExtended Data Fig. 9 | UDA-seq is compatible with CRISPR Screening. a. Pie
plot displaying 38000 cells’s sgRNA detection rate. b. Sankey diagram showing
sgRNA number distribution out of 31,487 cells. c. Distribution of gene and
UMI numbers per cell in single-cell transcriptome (n = 12,644). Box plots show
interquartile range with the median marked. The whiskers extend up to 1.5
times the interquartile range, the outliers are not displayed. d. The genes that
exhibit differential expression in cells subjected to interference targeting EP300
as compared to those targeted by the negative control sgRNA. P values were
calculated by two-sided Wilcoxon Rank Sum test. e. The scMAGeCK-LR module

estimated the degree of perturbations of the interested genes (FAR2 in the left
panel and NDUFS5 in the right panel). An LR_score >0 represented up-regulation
by the corresponding target genes, while an LR_score <0 represented down-
regulation. f. PCA analysis showed that cells transduced with negative control
sgRNAs were evenly distributed within group 1 and group 2 SUN16 cells. g. The
expression of the MYC gene was notably reduced in cells (n = 5) subjected to each
interference targeting genes compared to the control (n = 10) in group 2 cells.
Box plots show interquartile range with the median marked. The whiskers extend
up to 1.5 times the interquartile range.

Nature Methods

Articlehttps://doi.org/10.1038/s41592-024-02586-y