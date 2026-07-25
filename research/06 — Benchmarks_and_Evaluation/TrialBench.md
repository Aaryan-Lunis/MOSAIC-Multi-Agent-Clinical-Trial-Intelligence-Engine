# File: TrialBench.md

# TrialBench

## Basic Information

- **Title:** TrialBench: Multi-Modal AI-Ready Datasets for Clinical Trial Prediction
- **Authors:** Jintai Chen, Yaojun Hu, Mingchen Cai, Yingzhou Lu, Yue Wang, Xu Cao, Miao Lin, Hongxia Xu, Jian Wu, Xiao Cao, Jimeng Sun, Yuqiang Li, Lucas Glass, Kexin Huang, Marinka Zitnik, Tianfan Fu (Jintai Chen and Yaojun Hu contributed equally)
- **Year:** 2025
- **Venue:** Scientific Data (Nature), Vol. 12, Article 1564
- **DOI:** 10.1038/s41597-025-05680-8
- **Official DOI Link:** https://doi.org/10.1038/s41597-025-05680-8
- **Official Publisher Link:** https://www.nature.com/articles/s41597-025-05680-8 (www.nature.com/scientificdata)
- **GitHub Repository (if available):** https://github.com/ML2Health/ML2ClinicalTrials/tree/main/Trialbench (code to reproduce Table 6 results); dataset/documentation site: https://huyjj.github.io/Trialbench/ ; Python/R packages available via the `trialbench` package
- **Dataset(s) Used:**
  - ClinicalTrials.gov — Yes (primary raw data source; >420,000 clinical trial XML records as of Feb 2024, covering trials registered before Feb 16, 2024)
  - AACT — Not reported (paper uses ClinicalTrials.gov XML records directly, not the AACT relational database specifically)
  - PubMed — Not a direct data source for dataset curation, but explicitly recommended as an external knowledge source for downstream AI model development (e.g., for the drug dose finding task)
  - PubMed eUtils — Not reported
  - Other — DrugBank (drug molecular structures/SMILES, pharmaceutical properties), TrialTrove (trial approval/outcome ground truth, public/released subset), ICD-10-CM coding system (via Clinical Table Search Service API and CCS codes), OpenAI ChatGPT API / GPT-4.0 (used for automated data annotation/labeling of failure reasons and drug dosage categories)

## Research Category

- Data Sources & Knowledge (benchmark dataset creation)
- Core Clinical Trial Intelligence
- Clinical NLP (eligibility criteria, multi-modal feature processing)
- Evaluation (baseline models and metrics for 8 clinical trial prediction tasks)

## Research Problem

Despite ClinicalTrials.gov providing a vast, publicly accessible repository of clinical trial data (480,000+ trials, 221 countries), there was no comprehensive, standardized, AI-ready benchmark that converted this complex, hierarchical, multi-modal XML data into clean tabular datasets with clearly defined prediction targets for the range of clinical trial design challenges that matter in practice (duration, dropout, adverse events, mortality, approval, failure reason, eligibility criteria design, drug dosing). Identifying the right AI-solvable tasks and selecting appropriate variables for each requires a blend of deep medical knowledge and AI expertise that most data scientists lack, which has hindered broad AI involvement in clinical trial research.

## Motivation

Clinical trials are extremely costly and risky: Phase 1–3 development programs typically span 7–11 years, cost ~$2 billion on average, and achieve only ~15% approval rates. AI is well suited to reduce this risk by identifying patterns in the vast (but complex, multi-modal, XML-hierarchical) data clinical trials generate — but the complexity of the raw data and the medical domain knowledge required to define meaningful prediction tasks has kept most AI/ML researchers from fully exploiting it. No prior open, standardized, multi-task, multi-modal benchmark existed to lower this barrier and let AI experts without deep clinical background contribute models and comparisons on a shared, well-defined footing.

## Objective

To curate and publicly release a comprehensive suite of AI-ready datasets — TrialBench — spanning 8 well-defined, clinically meaningful prediction tasks and 23 corresponding datasets derived from ClinicalTrials.gov (enriched with DrugBank and TrialTrove), each with clearly specified input features, prediction targets, evaluation metrics, and baseline multi-modal deep learning models, to catalyze broader AI/ML research on clinical trial design and outcome prediction.

## Proposed Method

### Overview
TrialBench is fundamentally a **dataset/benchmark contribution** (not a novel predictive algorithm), but it includes a reference multi-modal baseline pipeline used for technical validation of dataset quality. The pipeline:

1. **Data Acquisition:** Raw clinical trial records pulled from ClinicalTrials.gov XML files (trials registered before Feb 16, 2024; 420,000+ records, 50 US states + 221 countries). Each trial's NCT ID, disease names, associated drugs, title, summary, phase, eligibility criteria, and statistical results are extracted. Enrichment sources: DrugBank (drug molecular structure/SMILES, pharmaceutical properties), TrialTrove (trial outcome/approval ground truth, from the public HINT-released subset), and ICD-10-CM (disease codes, via Clinical Table Search Service API, then mapped to CCS codes).

2. **Dataset Curation & Feature Organization:** XML hierarchy flattened into tabular format; only features available *before trial start* are retained (to avoid label leakage); features with identical/null values across trials removed; task-specific selection filters applied (e.g., trial duration capped at ≤10 years to remove outliers; only trials with realistic completion dates used for duration prediction; only completed trials used for eligibility criteria design; only Phase II trials with drug dosage info used for drug dose finding). Certain XML nodes (e.g., `ipd_info_type`, `study_design_info/masking`, `arm_group_type`, `intervention_type`) are one-hot/binary-encoded into multiple tabular columns.

3. **Data Annotation:** Labels derived per task — e.g., trial duration = completion date − start date; dropout rate = dropout patients / enrolled patients; adverse event / mortality event = binarized from reported ClinicalTrials.gov results; trial approval labels sourced from HINT/TrialTrove plus ClinicalTrials.gov "why stopped" termination reasons as negative samples; **trial failure reason** (4-category: success, poor enrollment, safety issue, lack of efficacy) and **drug dosage category** (4-class: <1, 1–10, 10–100, >100 mg/kg) both labeled via **OpenAI ChatGPT API prompting** on the raw "why stopped" / dosage text (10 trials batched per prompt).

4. **Data Partitioning:** Random 80/20 train/test split by default; stratified sampling for classification tasks (to preserve class balance), random splitting for regression tasks. Authors also suggest temporal splits, 5-fold CV, and location-based splits as alternatives for robustness/generalizability testing.

5. **Baseline Multi-Modal Deep Neural Network (technical validation model):**
   - **Drug molecule (SMILES → 2D molecular graph):** Message Passing Neural Network (MPNN) — node/edge feature updates over L iterations, aggregated via readout function for graph-level embedding.
   - **Disease code (ICD-10):** Graph-based Attention Model (GRAM) — represents each disease code as an attention-weighted average of its own and its ancestors' basic embeddings in the ICD-10 hierarchy.
   - **Text (eligibility criteria, trial summary):** Bio-BERT (a BERT variant pretrained on biomedical literature).
   - **MeSH terms:** Pretrained MeSH-Embedding layer (node2vec-based); new terms get a parametric embedding learned from scratch.
   - **Categorical/numerical tabular features:** DANets (stacked lightweight "basic block" modules) → 50-dimensional embedding.
   - **Representation Fusion:** All modality embeddings (size 100 each) concatenated and fed into an MLP; sigmoid output for binary classification, softmax for multi-class classification, no activation for regression. Cross-entropy loss for classification, MSE for regression.
   - **Eligibility criteria design (generation task):** Uses the OpenAI ChatGPT API directly (prompted) rather than the fusion MLP, since output is natural-language text.

## Datasets Used

TrialBench provides **23 datasets across 8 tasks**, all derived from ClinicalTrials.gov (+ DrugBank + TrialTrove + ICD-10). Per-task statistics (from Table 1 / Table 3 of the paper):

| Task | AI Task Type | # Data (records) | # Trials (I/II/III/IV) | Input Modalities |
|---|---|---|---|---|
| Trial duration prediction | Regression | 141,940 | 143.8K (13.5K/13.4K/9.2K/7.1K) | All 5 modalities |
| Patient dropout prediction | Classification + Regression | 62,058 | 62.1K (4.2K/15.8K/11.5K/6.9K) | All 5 modalities |
| Serious adverse event prediction | Classification | 31,306 | 31.3K (2.0K/8.1K/4.8K/2.9K) | All 5 modalities |
| Mortality event prediction | Classification | 31,306 | 31.3K (2.0K/8.1K/4.8K/2.9K) | All 5 modalities |
| Trial approval prediction | Classification | 43,202 | 43.2K (4.5K/12.5K/9.2K/4.5K) | All 5 modalities |
| Trial failure reason identification | Classification (4-class) | 41,369 | 41.4K (4.3K/8.8K/4.2K/3.5K) | All 5 modalities |
| Eligibility criteria design | Generation | 136,443 | 136.4K (19.4K/14.2K/10.8K/10.6K) | MeSH, SMILES, ICD-10, Texts |
| Drug dose finding | Classification (4-class, ordinal) | 12,790 | 12.8K (0/12.8K/0/0) | SMILES, MeSH |

**The 5 modalities** referenced throughout: (1) drug molecule structure (SMILES string), (2) disease code (ICD-10), (3) free text (trial summary, eligibility criteria), (4) categorical/numerical features (e.g., patient gender, blood pressure), (5) MeSH (Medical Subject Headings).

**Source datasets/databases:**
- **ClinicalTrials.gov:** >420,000–480,000 trial records (NLM/NIH), XML format, covering all 50 US states and 221 countries.
- **DrugBank:** Drug molecular structures (SMILES) and pharmaceutical properties; free for academic/non-profit research and educational use.
- **TrialTrove:** Trial outcome/approval ground truth; public/released subset (from Fu et al.'s HINT study) available for non-commercial use.
- **ICD-10-CM:** Disease coding via Clinical Table Search Service API (clinicaltables.nlm.nih.gov), further mapped to CCS codes.

**Preprocessing:** XML → tabular flattening; feature selection restricted to pre-trial-start-available variables only; removal of constant/null features; task-specific filters (see Proposed Method above); multi-hot/binary encoding for multi-valued categorical XML nodes; disease names mapped to ICD-10 hierarchy; drug names mapped to SMILES/molecular graphs via DrugBank.

## Models / Technologies

- Message Passing Neural Network (MPNN) — for drug molecule (SMILES/graph) representation
- GRAM (Graph-based Attention Model) — for ICD-10 disease code hierarchy representation
- Bio-BERT — for free-text features (eligibility criteria, trial summaries)
- MeSH-Embedding (node2vec-based, pretrained) — for MeSH term representation
- DANets (Deep Abstract Networks) — for categorical/numerical tabular feature processing
- Multi-Layer Perceptron (MLP) — for multi-modal representation fusion and final prediction
- OpenAI ChatGPT API / GPT-4.0 — for automated data annotation (failure reason, drug dosage) and for the eligibility criteria generation baseline
- ClinicalTrials.gov API/XML records, DrugBank, TrialTrove, ICD-10-CM coding system — core data infrastructure
- Adam optimizer (lr = 1e-3, zero weight decay) — training optimizer for the baseline models
- `trialbench` Python/R package — for dataset download and loading (PyTorch DataLoader or pandas DataFrame format)

## Experimental Setup

- **Implementation:** Python 3.8, PyTorch for all deep learning models; GPT-4.0 used specifically for data annotation and the eligibility-criteria generation task.
- **Training:** Embedding size = 100 for all modality representations; Adam optimizer, initial learning rate 1e-3, zero weight decay; batch size = 64; maximum training epochs = 20.
- **Evaluation metrics:**
  - Classification: Accuracy, PR-AUC, F1, Precision, Recall, Specificity, ROC-AUC
  - Regression: RMSE, MAE, Concordance Index, Pearson Correlation
  - Generation (eligibility criteria design): text-embedding cosine similarity, informativeness, redundancy (semantic metrics; detailed in Supplementary Information)
- **Hardware:** NVIDIA GeForce RTX 3090 GPU, Intel(R) Xeon(R) CPU, 50GB RAM (single server used for all empirical experiments).
- **Data partitioning:** 80/20 default split; stratified for classification, random for regression; alternative splitting strategies (temporal, 5-fold CV, location-based) suggested for robustness/generalizability testing.

## Results

Reference results using the multi-modal baseline (Table 6 of the paper), by phase where applicable:

- **Patient dropout prediction (classification):** F1 ranged 0.7138 (Phase I) to 0.9455 (Phase III); ROC-AUC 0.6516–0.7610 across phases.
- **Patient dropout prediction (regression):** MAE ~0.40–0.45, R² 0.22–0.63 across phases.
- **Adverse event prediction (classification):** F1 0.8038–0.9297, ROC-AUC 0.7952–0.8913 across Phases I–III.
- **Mortality event prediction (classification):** F1 0.6825–0.7695, ROC-AUC 0.8144–0.9093 across Phases I–III.
- **Trial approval prediction (classification):** F1 0.5172–0.6724, ROC-AUC 0.6052–0.7649 across Phases I–IV (Phase I highest ROC-AUC at 0.7649; Phase IV weakest, F1 0.5797, ROC-AUC 0.6052).
- **Drug dose finding (classification, Phase II & III):** F1 0.4938, ROC-AUC 0.7586, PR-AUC 0.5341.
- **Trial failure reason identification (classification, 4-class):** F1 only 0.1499–0.1993 across phases (notably weak — near chance for a 4-class task), ROC-AUC 0.4751–0.5692.
- **Trial duration prediction (regression):** MAE 0.83–1.44 years, R² 0.31–0.65 across Phases I–III.
- **Eligibility criteria design (generation, all phases):** cosine similarity 0.6988, informativeness 0.6518, redundancy 0.1181.
- **Overall finding:** Across the 14 binary classification datasets (dropout, adverse event, mortality, approval), the baseline achieves ≥0.7 F1 on 11 of them, and reasonable performance on regression/generation tasks, which the authors interpret as validating the AI-readiness and quality of the curated datasets (not as claiming state-of-the-art predictive performance).

## Strengths

- Largest and most comprehensive open-access, standardized, multi-modal benchmark suite for clinical trial AI to date at time of publication: 23 datasets across 8 clinically meaningful tasks.
- Explicit leakage-avoidance design: only pre-trial-start-available features are retained for prediction tasks.
- True multi-modality: combines SMILES/molecular graphs, ICD-10 codes, MeSH terms, free text, and categorical/numerical tabular features — supporting a wide range of downstream architectures.
- Provides reference baseline models, evaluation metrics, and validation results for every task, lowering the barrier to entry for AI researchers without deep clinical domain expertise.
- Transparent documentation of dataset curation criteria, annotation methodology (including exact ChatGPT prompts used for labeling), and licensing/ethics considerations.
- Publicly available with accompanying Python and R packages (`trialbench`) for easy download and integration into ML pipelines (PyTorch DataLoader or pandas DataFrame formats).
- Covers the full clinical trial lifecycle relevant to AI: design (eligibility criteria, dosing), conduct (dropout, adverse events, mortality), and outcome (approval, failure reason, duration).

## Limitations

- The paper explicitly states TrialBench is an "ongoing effort" — important tasks/datasets are not yet included, and AI for clinical trials is described as a vast, fast-growing field where the benchmark will continue to expand.
- Trial failure reason identification and trial approval prediction (Phase IV especially) show notably weak baseline performance (e.g., F1 as low as 0.15–0.20 for failure reason), suggesting these tasks remain genuinely difficult, or that available features are insufficient.
- Reliance on GPT-based automated annotation (ChatGPT API) for two label sets (failure reason, drug dosage category) introduces potential annotation noise/bias, since these labels were not manually verified against ground truth by domain experts (only prompted/extracted by an LLM).
- TrialTrove data is a "released/public subset" only (non-commercial use), so full reproduction of trial approval ground truth may require access the general public/most academics may not have.
- DrugBank-derived features are free for academic/non-profit use only, not unrestricted commercial use — a licensing constraint for downstream applications.
- Business-decision-driven trial failures (e.g., funding, strategic pipeline changes) are explicitly excluded from the failure-reason dataset as "not predictable," meaning the failure-reason task captures only 3 of the real-world failure categories plus success.
- Baseline models are simple fusion-MLP architectures intended for dataset validation, not optimized/state-of-the-art predictive models — actual task-specific performance ceilings are likely higher than reported.

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:**
TrialBench is the foundational **Data Sources & Knowledge** and **Evaluation** backbone for MOSAIC. It directly supplies (a) the standardized task definitions, features, and labels MOSAIC's **Clinical Trial Matching / Outcome Prediction** module should target, (b) the multi-modal feature engineering blueprint (SMILES, ICD-10, MeSH, free text, tabular) for MOSAIC's **Knowledge Graph** and **Medical Retrieval** modules, and (c) a ready-made, pre-validated benchmark against which MOSAIC's own models (including any AutoCT-style agent pipeline) can be trained and evaluated.

**Exactly what we should implement:**
- Directly consume the **`trialbench` package** (Python/R) to download and load MOSAIC's training/evaluation data for trial approval, dropout, adverse event, mortality, and duration prediction tasks — avoiding re-implementing ClinicalTrials.gov XML parsing from scratch.
- Adopt TrialBench's **pre-trial-start feature-availability filter** as a hard rule anywhere MOSAIC builds predictive features from ClinicalTrials.gov data, to prevent label leakage.
- Reuse the **5-modality feature taxonomy** (SMILES, ICD-10, free text, categorical/numerical, MeSH) as the schema for MOSAIC's internal multi-modal trial representation / knowledge graph nodes.
- Reuse the **GRAM-style hierarchical disease-code embedding** approach for MOSAIC's disease/knowledge-graph component, since ICD-10 hierarchy-awareness is directly relevant to eligibility matching and retrieval.
- Reuse TrialBench's **task definitions and evaluation metrics** (ROC-AUC, PR-AUC, F1, etc., per task) as MOSAIC's standard evaluation harness for any new model MOSAIC develops (including AutoCT-style agents), enabling apples-to-apples benchmarking against TrialBench's published baselines (and against AutoCT's reported numbers on the same benchmark).
- Consider TrialBench's **eligibility criteria design (generation)** dataset as ground truth / training data for MOSAIC's Eligibility Extraction / criteria-generation module.

**What should NOT be copied:**
- The baseline fusion-MLP predictive model itself should not be treated as MOSAIC's final production model — it is explicitly a dataset-validation baseline, not a competitive SOTA architecture (see AutoCT and other more advanced methods, e.g., HINT/SPOT, for stronger performance references).
- The ChatGPT-based auto-labeling for failure reason / drug dosage should not be blindly trusted as ground truth if MOSAIC needs high-precision labels — MOSAIC should consider human-verified subsets or additional QA if these labels feed high-stakes decisions.
- The exclusion of business-decision failure trials should not be silently inherited without documenting the limitation to MOSAIC's own users, since it means the "poor enrollment / safety / efficacy" failure-reason model cannot explain all real-world trial terminations.

**Possible improvements:**
- Combine TrialBench's large-scale, pre-curated multi-modal features with AutoCT's LLM-agent-driven feature construction to enrich features beyond TrialBench's fixed schema (e.g., dynamically research additional PubMed-grounded features per trial) while keeping TrialBench's leakage-safe, pre-trial-start filtering discipline.
- Replace/augment the DANets + GRAM + Bio-BERT + MPNN fusion baseline with more modern architectures (e.g., LLM-based feature extraction as in AutoCT, or graph neural networks over a MOSAIC-built knowledge graph) to raise the weak-performing tasks (trial failure reason identification, Phase IV approval) above baseline levels.
- Extend the temporal/location-based splitting strategies TrialBench merely suggests into MOSAIC's standard evaluation protocol, to better assess real-world deployment robustness (e.g., predicting for trials in geographies/time periods not seen in training).

## Personal Notes

