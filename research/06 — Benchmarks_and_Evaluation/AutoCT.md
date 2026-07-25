# File: AutoCT.md

# AutoCT

## Basic Information

- **Title:** AutoCT: Automating Interpretable Clinical Trial Prediction with LLM Agents
- **Authors:** Fengze Liu, Haoyu Wang, Joonhyuk Cho, Dan Roth, Andrew W. Lo
- **Year:** 2025
- **Venue:** Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP 2025), Suzhou, China (pages 30945–30970)
- **DOI:** 10.18653/v1/2025.emnlp-main.1575
- **Official DOI Link:** https://doi.org/10.18653/v1/2025.emnlp-main.1575
- **Official Publisher Link:** https://aclanthology.org/2025.emnlp-main.1575/
- **GitHub Repository (if available):** Not reported (no repository link given in the paper or its official ACL Anthology / arXiv pages)
- **Dataset(s) Used:**
  - ClinicalTrials.gov — Yes (used both as the retrieval knowledge base "NCT DB" and as the source of trial identifiers/labels via the TrialBench-derived task datasets)
  - AACT — Not reported (paper references ClinicalTrials.gov directly, not the AACT database specifically)
  - PubMed — Yes (used as the retrieval knowledge base "PubMed DB" for feature research, embedded with PubMedBERT-based embeddings)
  - PubMed eUtils — Not reported (paper does not specify eUtils; it describes a locally embedded PubMed corpus rather than live eUtils API calls)
  - Other — TrialBench benchmark datasets (Chen et al., 2024) for Trial Approval Prediction, Patient Dropout Prediction, Mortality Prediction, and Adverse Event Prediction tasks

## Research Category

- Core Clinical Trial Intelligence
- Multi-Agent Architecture
- Medical Retrieval (RAG over PubMed and ClinicalTrials.gov)
- Clinical NLP / Automated Feature Engineering (AutoML)
- Evaluation (clinical trial outcome prediction benchmarking)

## Research Problem

Clinical trial outcome prediction models fall into two camps: (1) classical machine learning on expert-curated tabular features, which achieves interpretable but manually-bottlenecked performance, and (2) deep learning models that integrate diverse/unstructured data sources but act as uninterpretable "black boxes" and are prone to label leakage when pulling from external databases without a knowledge cutoff. The paper's problem is to design a system that can automatically construct informative, interpretable tabular features for clinical trial prediction directly from public biomedical data sources (ClinicalTrials.gov, PubMed), using only a trial identifier and outcome label, without manual feature engineering, while avoiding label leakage and preserving the interpretability of classical ML models.

## Motivation

Drug development is extremely costly (paper cites ~US$2.6 billion average cost, >10 years, <10% clinical success rate) so accurate early prediction of trial outcomes can meaningfully reduce cost and risk. Existing approaches force a tradeoff: expert-curated tabular ML is interpretable but not scalable/manual; deep learning models scale but are opaque and can leak information from post-hoc data. There was a gap for a system that emulates how a biomedical expert would research a trial (reading PubMed literature, related trials, drug/disease context) to construct meaningful features — automatically, at scale, and without compromising interpretability or violating temporal/label-leakage constraints.

## Objective

To build an end-to-end, fully automated framework (AutoCT) that uses LLM agents to autonomously propose, plan, build, and iteratively refine tabular features for clinical trial outcome prediction from only a trial identifier (NCT ID) and outcome label — training interpretable classical ML models (Logistic Regression, Random Forest, XGBoost) on these LLM-derived features and optimizing the feature set via Monte Carlo Tree Search (MCTS), achieving performance competitive with SOTA deep learning baselines while remaining interpretable (e.g., via SHAP).

## Proposed Method

### Architecture / Pipeline Overview
AutoCT is a multi-agent LLM pipeline (backbone LLM: gpt-4o-mini, temperature 0) with the following components, orchestrated inside a Monte Carlo Tree Search loop:

1. **Retrieval Tools (§3.1):** Two local knowledge bases built with PubMedBERT-based embeddings:
   - **PubMed DB** — embedded PubMed articles.
   - **NCT DB** — embedded ClinicalTrials.gov trial records.
   Retrieval uses hybrid search (BM25 + embedding similarity). A **publication-date filter** enforces that only documents/trials published/started before the target trial's start date are retrievable, explicitly preventing label leakage from post-hoc trial results or later publications.

2. **Feature Proposer (§3.2):** Generates conceptual feature ideas.
   - *Initializing Proposer* (first iteration only), combining:
     - **Zero-Shot Proposer** — CoT-prompted LLM suggests generic features from parametric knowledge only (task description as input).
     - **Factor-Based Proposer** — ReAct-based LLM examines individual labeled training examples (3 positive + 3 negative samples) and queries retrieval tools to propose sample-grounded features.
     - Outputs from both are merged/summarized by a CoT LLM summarizer into a unified feature set.
   - *Iterative Proposer* (runs every MCTS iteration): given an Evaluator suggestion, outputs a single **Add / Refine / Remove** feature action.

3. **Feature Planner (§3.3):** CoT LLM converts each conceptual feature idea into an executable, structured plan: explicit JSON schema (feature type: integer/float/boolean/categorical/multicategorical), data sources, example values, possible values, and unambiguous construction instructions.

4. **Feature Builder (§3.4):** Executes the plans.
   - *Feature Grouper* clusters conceptually related/dependent features to share research context and save context-window budget.
   - *Feature Researcher* — ReAct agent that queries PubMed DB / NCT DB to gather raw evidence per feature group.
   - *Feature Builder* — CoT agent converts retrieved evidence into structured feature values per the JSON schema (returns "None" for missing/uncertain/insufficient data, with an explanation).

5. **Model Builder (§3.5):** A non-LLM function call that trains three classical ML models on the constructed tabular features: **Logistic Regression, Random Forest, and XGBoost**.

6. **Evaluator (§3.6):** Assesses model performance and produces improvement proposals (≤2–3 suggestions), aggregated into a candidate list for the next Iterative Proposer round.
   - *Model-Based Evaluator* — CoT LLM given ROC-AUC, feature importances, and feature plans; suggests additions/refinements/removals.
   - *Error-Based Evaluator* — ReAct LLM given the same info plus one misclassified validation example per iteration; investigates via retrieval why the model erred and proposes a corrective feature change.

7. **Monte Carlo Tree Search (§3.7):** Each tree node = a distinct feature set/state; each edge = an Add/Refine/Remove action suggested by the Evaluator. Node selection uses the UCT formula:
   `UCT(x) = q(x)/n(x) + α * sqrt(ln(n(x_parent)) / n(x))`
   where q(x) = cumulative reward, n(x) = visit count, α = exploration weight (set to 1.0). The search runs up to a configured number of rollouts (10 for the main Trial Approval task, 5 for the secondary tasks) and max depth 10; final output is the feature set/model with best validation performance.

### Full Algorithm (Algorithm 1, as described in the paper)
- Initialize: `F0 = FeatureBuilder(FeaturePlanner(InitializingProposer(D, sampled train subset)))`; train `M0`; score `s0 = Evaluate(M0)` on validation subset; initialize search tree with root `(F0, s0)`.
- For each of N iterations: for each Evaluator-generated suggestion g, run `IterativeProposer(g) → FeaturePlanner → FeatureBuilder → UpdateFeatures → ModelBuilder → Evaluate`; add resulting `(F', s')` as a new tree node; select the best child to continue the search.
- Return the best-performing feature set/model found.

### Inference / Cost Notes
Each MCTS run over 100 training / 100 validation samples costs approximately **$150** in LLM API usage (dominated by Feature Builder's retrieval/reasoning cost). No hyperparameter optimization is performed (explicitly out of scope — proof-of-concept focus).

## Datasets Used

- **TrialBench (Chen et al., 2024)** — Source of all four evaluation tasks used in this paper:
  - *Trial Approval Prediction* (primary task): 24,468 training / 6,215 test samples in the full benchmark. For AutoCT's experiments, **stratified sampling** (by label distribution) reduced this to 100 training, 100 validation, and 100 test samples due to LLM API cost constraints.
  - *Patient Dropout, Mortality Event, Adverse Event Prediction* (secondary tasks, Phase I trials only): same stratified-sampling strategy (100/100/100), with MCTS capped at 5 rollouts (vs. 10 for the main task) to manage compute cost.
  - Although TrialBench provides base features (e.g., SMILES, ICD-10 disease codes), **AutoCT is given only the NCT ID** for each trial and must independently determine and construct its own feature set.
- **PubMed** (via PubMed DB) — Embedded corpus of academic articles, used as a retrieval source for the Feature Researcher and Evaluator agents; filtered by publication date to avoid leakage.
- **ClinicalTrials.gov** (via NCT DB) — Embedded corpus of trial records, similarly used as a retrieval source with a trial-start-date leakage filter.
- **Preprocessing:** PubMedBERT-based embeddings used to build both local knowledge bases; hybrid retrieval (BM25 + embedding similarity) at query time; explicit date-based filtering to exclude any document/trial published/started after the target trial's start date.

## Models / Technologies

- **gpt-4o-mini** — backbone LLM for all agent roles (Proposer, Planner, Builder, Evaluator), temperature = 0
- **PubMedBERT-based embeddings** — for building the PubMed DB and NCT DB retrieval indices
- **BM25** — sparse lexical retrieval, combined with embedding similarity for hybrid retrieval
- **Chain-of-Thought (CoT) prompting** — used in Zero-Shot Proposer, Feature Planner, Feature Builder, Model-Based Evaluator
- **ReAct (Reasoning + Acting) framework** — used in Factor-Based Proposer, Feature Researcher, Error-Based Evaluator, for tool-augmented reasoning
- **Monte Carlo Tree Search (MCTS)** with UCT selection — for iterative feature-set optimization
- **Classical ML models:** Logistic Regression, Random Forest, XGBoost (trained by the Model Builder)
- **SHAP (SHapley Additive exPlanations)** — used post-hoc for model interpretability/case studies
- **ClinicalTrials.gov** and **PubMed** — external public data sources (accessed via the local embedded knowledge bases, not live APIs/eUtils)
- Retrieval-Augmented Generation (RAG)-style architecture (explicitly compared to RAG in the paper)

## Experimental Setup

- **Backbone LLM:** gpt-4o-mini, temperature 0
- **Initializing Proposer sampling:** 3 positive + 3 negative training samples fed to the Factor-Based Proposer
- **Evaluator sampling:** 3 misclassified validation samples per iteration fed to the Error-Based Evaluator
- **MCTS parameters:** exploration weight α = 1.0 in the UCT formula; up to 10 rollouts and max depth 10 for the Trial Approval task; up to 5 rollouts for the three secondary tasks (Patient Dropout, Mortality, Adverse Event), with early termination once reasonable performance is reached
- **Primary tuning metric:** ROC-AUC (consistent with prior benchmark work: Lo et al. 2019; Siah et al. 2021; Fu et al. 2022; Chen et al. 2024)
- **Sample sizes (due to LLM cost constraints):** 100 training / 100 validation / 100 test samples per task, via stratified sampling on label distribution
- **Cost:** ~$150 per MCTS run on 100 train + 100 validation samples
- **Hardware:** Not reported (no GPU/CPU/cloud specification given; compute cost is reported only in LLM API dollar terms)
- **No hyperparameter optimization performed** for the classical ML models (explicit limitation/design choice)

## Results

**Trial Approval Prediction (Table 1 — ROC-AUC on Phase I / II / III test sets):**
- AutoCT: **0.753 (Phase I)**, **0.639 (Phase II)**, **0.702 (Phase III)**
- Comparable strong baselines: HINT (0.576 / 0.645 / 0.723), SPOT (0.660 / 0.630 / 0.711), MMFusion/TrialBench baseline (0.782 / 0.771 / 0.741)
- AutoCT's Phase I ROC-AUC (0.753) and PR-AUC (0.710) exceed all listed baselines including SPOT and MMFusion on Phase I; performance is more mixed/lower on Phase II and III (e.g., F1 of 0.386 on Phase II, notably lower than deep learning baselines), reflecting the effect of the very small (100-sample) evaluation set and dataset/task difficulty.

**Secondary tasks, Phase I only (Table 2 — AutoCT vs. MMFusion):**
- Patient Dropout: AutoCT PR-AUC 0.795 vs. MMFusion 0.691; F1 0.718 (tie); ROC-AUC 0.711 vs. 0.723
- Mortality: AutoCT PR-AUC 0.560 vs. MMFusion 0.610; F1 0.732 vs. 0.745; ROC-AUC 0.852 vs. 0.900
- Adverse Event: AutoCT PR-AUC 0.796 vs. MMFusion 0.726; F1 0.731 vs. 0.793; ROC-AUC 0.831 vs. 0.874
- Overall: performance is comparable to MMFusion across all three secondary tasks, supporting generalizability of the framework beyond trial approval prediction, despite using far fewer training samples and no hand-crafted features.

**Effect of MCTS rollouts:** Increasing the maximum rollout count generally improves average test ROC-AUC (top-5 models), though gains plateau, plausibly due to the very small (100/100) sample sizes limiting the model's ability to generalize across diverse trial/disease types.

**Case studies (SHAP-based interpretability, §4.5.1):** Three individual trial predictions are explained via SHAP — e.g., NCT00035360 (Phase III PEG-Intron/HIV trial) predicted 0.244 approval probability, driven mainly by primary outcome measure and treatment duration; NCT00628680 (Phase III catheter infection trial) predicted 0.895, driven by treatment duration and inclusion-criteria count; NCT02698176 (Phase I oncology trial) predicted 0.197, driven by trial design, geography, route of administration, and eligibility strictness.

**Feature-set evolution case study (§4.5.2):** Traces one MCTS search path showing the Evaluator recommending an **Add** (adverse event rate, sourced from ClinicalTrials.gov/PubMed), a **Refine** (trial design elements — randomization/blinding/control group specificity, prompted by an Example-Based Evaluator finding a quadruple-masking trial), and a **Remove** (intervention type, dropped for low feature importance since most curated trials are drug trials).

## Strengths

- Fully automated end-to-end pipeline requiring only an NCT ID and outcome label — no manual feature engineering or domain-expert annotation needed.
- Explicitly engineers against label leakage via a publication/trial-start-date filter on all retrieval — a documented weakness of prior deep-learning approaches (per Fu et al., 2022).
- Retains full interpretability by using classical ML (LR/RF/XGBoost) as the final predictor, enabling SHAP-based explanation of individual predictions — directly addressing the black-box critique of deep learning baselines.
- Demonstrates competitive or superior performance vs. strong published baselines (HINT, SPOT, COMPOSE, DeepEnroll, MMFusion) on Phase I trial approval prediction with drastically fewer labeled samples (100 vs. tens of thousands).
- Generalizes across four distinct clinical prediction tasks (approval, dropout, mortality, adverse event) without task-specific redesign.
- Transparent, reusable multi-agent design (Proposer / Planner / Builder / Evaluator) with MCTS providing a principled way to balance exploration vs. exploitation of the feature space.
- Detailed, reproducible prompts and example agent outputs are provided in the Appendix (Zero-Shot Proposer, Factor-Based Proposer, Feature Planner, Feature Builder, Model-Based/Example-Based Evaluators).

## Limitations

- Retrieval restricted to only two data sources (PubMed and ClinicalTrials.gov) due to knowledge-cutoff/label-leakage concerns, potentially limiting feature richness (explicitly acknowledged by the authors).
- No hyperparameter optimization was performed for the classical ML models — a deliberate proof-of-concept scope limitation, not a fully tuned system.
- Evaluated on very small sample sizes (100 train/100 val/100 test) due to LLM API cost (~$150 per run), which limits statistical robustness and generalization, especially evident in performance plateaus and Phase II/III weaker results.
- MCTS is currently constrained to exploring only the feature-proposal space; the Evaluator cannot yet attribute underperformance to specific pipeline components (e.g., Feature Researcher reasoning error vs. Feature Builder execution error), limiting the precision of automated debugging/refinement.
- Secondary-task evaluation (dropout, mortality, adverse event) restricted to Phase I trials only, leaving generalizability to other phases for these tasks unexamined.
- No GitHub/code repository link is provided in the paper, limiting reproducibility for external users at this time.
- Comparisons to baselines trained on different dataset vintages (e.g., Fu et al. 2022 baselines trained on the older TOP dataset vs. AutoCT/TrialBench on Chen et al. 2024's updated dataset) introduce some baseline-comparability caveats, which the authors flag explicitly.

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:**
This paper is the most directly relevant blueprint for MOSAIC's **Multi-Agent Architecture** and **Eligibility/Feature Extraction** modules, and for any MOSAIC component doing **RAG-based clinical trial reasoning** over ClinicalTrials.gov and PubMed. It also directly informs the **Clinical Trial Matching / Outcome Prediction** capability MOSAIC is likely to expose (trial approval, dropout, adverse event, mortality prediction), and provides a validated architecture for a MOSAIC "Feature/Insight Agent" pipeline.

**Exactly what we should implement:**
- The **four-role agent decomposition** (Proposer → Planner → Builder → Evaluator) as a reusable MOSAIC agent pattern for any task requiring structured extraction from unstructured biomedical text (not just outcome prediction — e.g., eligibility criteria structuring).
- The **dual local knowledge-base design** (PubMed DB + NCT DB with PubMedBERT embeddings and hybrid BM25 + embedding retrieval) as a template for MOSAIC's own RAG layer over ClinicalTrials.gov/PubMed data.
- The **publication/trial-date leakage filter** — a critical, easily-overlooked design pattern MOSAIC's RAG/retrieval layer should adopt whenever building temporally-sensitive predictive features, to avoid contaminating any MOSAIC prediction or matching task with future/outcome information.
- The **MCTS-driven iterative refinement loop** (Add/Refine/Remove actions guided by Evaluator feedback) as a candidate optimization strategy for MOSAIC's feature or prompt-refinement subsystems, particularly where automated, cost-bounded self-improvement is desired.
- The **interpretable-by-design final layer** (LLM for feature construction, classical ML — not an LLM — for final prediction, with SHAP explanations) as the recommended pattern anywhere MOSAIC needs clinically defensible, explainable predictions rather than opaque LLM-only outputs.
- The explicit JSON **feature schema format** (feature_name, feature_type, data_sources, example_values, possible_values, feature_instructions) as a reusable structured-output contract between MOSAIC's planning and extraction agents.

**What should NOT be copied:**
- The very small evaluation sample sizes (100/100/100) — a cost-driven compromise in the original paper, not a design choice MOSAIC should inherit; MOSAIC should validate at TrialBench's full scale wherever feasible.
- The lack of hyperparameter optimization — MOSAIC's production pipeline should tune its downstream classical ML models rather than treating this as out of scope.
- Reliance on a single backbone LLM (gpt-4o-mini) without model-selection experimentation — MOSAIC should benchmark across available models rather than fixing this choice.
- The narrow two-source retrieval scope — while the *leakage-filtering principle* should be kept, MOSAIC can and should expand retrieval sources (e.g., FDA labels, DrugBank, AACT) beyond just PubMed/ClinicalTrials.gov.

**Possible improvements MOSAIC could make:**
- Extend the Evaluator to attribute errors to specific pipeline stages (a limitation the authors themselves flag), enabling more targeted self-repair in MOSAIC's agent loop.
- Combine AutoCT's feature-construction agents with TrialBench's larger, already-curated multi-modal datasets (SMILES, ICD-10, MeSH) rather than starting purely from NCT IDs, to reduce cost while retaining interpretability.
- Add a knowledge-graph layer (aligning with MOSAIC's KG component) to store and reuse AutoCT-style constructed features across trials, avoiding redundant LLM calls for similar trials/diseases.
- Explore replacing/augmenting MCTS with a cheaper heuristic or bandit-based search to reduce the ~$150/100-sample cost, making the approach more viable at MOSAIC's intended scale.

## Personal Notes

