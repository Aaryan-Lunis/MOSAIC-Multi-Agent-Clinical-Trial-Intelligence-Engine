# Innovative_Trial-s_LLM

## Basic Information

- **Title:** Insights into the adoption of innovative clinical trials across therapeutic areas using clinical trials registry data and large Language models
- **Authors:** Danila Azzolina, Vittorio Scisciola, Luca Vedovelli, Domenico Iervolino, Mohd Rashid Khan, Rosanna Irene Comoretto, Martino Belvederi Murri, Dario Gregori
- **Year:** 2025
- **Venue:** Scientific Reports (Nature Portfolio), Volume 15, Article 35075
- **DOI:** 10.1038/s41598-025-18488-8
- **Official DOI Link:** https://doi.org/10.1038/s41598-025-18488-8
- **Official Publisher Link:** www.nature.com/scientificreports (Scientific Reports, Nature Portfolio)
- **GitHub Repository:** Not reported (no code repository mentioned in the paper)
- **Dataset(s) Used:**
  - ClinicalTrials.gov: Yes (primary data source — full CSV export of all interventional trials, June 27, 2024)
  - AACT: Not reported (paper uses a direct CSV export from ClinicalTrials.gov rather than the AACT database, though AACT is cited as a reference for database structure, ref. 25)
  - PubMed: No
  - PubMed eUtils: No
  - Other: None additional; ChatGPT 4.0/4o used as an LLM classification tool applied to the ClinicalTrials.gov "condition" field

## Research Category

- Data Sources & Knowledge
- Clinical NLP (LLM-based free-text classification)
- Evaluation
- Core Clinical Trial Intelligence

## Research Problem

Innovative clinical trial designs (Adaptive and Bayesian methodologies) have gained traction as solutions to rising costs and regulatory complexity in traditional trials, but comprehensive evaluation of their adoption and impact across therapeutic areas — outside the well-studied fields of oncology and hematology — is lacking. Additionally, manually classifying hundreds of thousands of trials into therapeutic areas based on free-text "condition" fields is labor-intensive, so it is unclear whether an LLM-assisted classification approach can feasibly and accurately support large-scale, automated monitoring of trial design trends by therapeutic area.

## Motivation

Clinical trials increasingly face high costs and complex regulatory requirements, motivating adoption of innovative (adaptive/Bayesian) trial designs that can improve efficiency, flexibility, and ethical standards (e.g., stopping early for futility, incorporating prior knowledge). However, most existing evaluations of adaptive/Bayesian trial adoption focus narrowly on oncology; a significant gap exists in understanding adoption patterns, characteristics, and outcomes (e.g., termination risk) of innovative trial designs in other fields such as neuroscience, psychiatry, and rare diseases. Separately, ClinicalTrials.gov is a large but underutilized resource because its free-text fields (e.g., "condition") are not structured by therapeutic area, and manual classification does not scale — motivating exploration of LLMs (e.g., ChatGPT) for automated, scalable therapeutic-area classification.

## Objective

Two primary objectives: (1) Quantify the adoption of innovative clinical trial designs (adaptive and Bayesian approaches) using ClinicalTrials.gov registry data from 2005–2024, and characterize how adoption varies by population, recruitment status, duration, funding source, geography, and especially therapeutic area (with particular focus on neuroscience/psychiatry). (2) Assess the performance/accuracy of an LLM (ChatGPT 4.0/4o)-assisted classification system for assigning trials to therapeutic areas based on free-text "condition" fields, to determine whether such tools can support scalable, real-time monitoring of trial design innovation.

## Proposed Method

**Study design:** Retrospective, registry-based study using a full CSV export of ClinicalTrials.gov interventional trials registered 2005–June 2024 (n = 348,818 trials with study description field, after exclusions per PRISMA-style flow diagram, Fig. 1).

**Objective 1 — Innovative trial classification (keyword-based, not LLM-based):**
- Trials were classified as "Innovative" if their "study description" field contained at least one of 42 predefined keywords referencing adaptive or Bayesian design elements (e.g., "adaptive design," "Bayesian adaptive," "response-adaptive," "group sequential," "biomarker adaptive," "sample size re-estimation," "phase II/III," etc.), derived from a prior published keyword list. All other trials were classified as "Traditional." This is a deterministic keyword/string-search algorithm, not an LLM classifier.
- Statistical analysis: descriptive statistics (frequencies for categorical, medians/IQR for quantitative variables), univariable logistic regression (Odds Ratios with 95% CI) comparing innovative vs. traditional trials across characteristics (year, status, sex, pediatric/elderly focus, phase, funding, continent, duration, results posting).
- Survival analysis: Kaplan–Meier curves and log-rank test comparing termination-free survival between innovative and traditional trials; Cox proportional hazards model with interaction terms between trial design (Innovative/Traditional) and therapeutic area, adjusted for funder type, initiation year, sex, pediatric/elderly population, phase, enrollment size, and continent.
- Focused sub-analysis: multivariable logistic regression specifically for neuroscience trials (Neurology/Neurosurgery vs. Psychiatry/Substance Abuse/Mental Health) to assess odds of innovative design adoption by year and sub-specialty.

**Objective 2 — LLM-based therapeutic area classification:**
- ChatGPT 4.0 (elsewhere referred to as "ChatGPT 4o") was applied to each trial's free-text "condition" field to classify it into one of a predetermined list of 29 therapeutic areas (author-curated list based on a prior published taxonomy, integrated with cross-cutting fields like Public Health/Geriatrics/Nutrition and specialized areas like Pediatrics/Women's Health/Rare Diseases and Genetics/Health Informatics).
- Validation: a manually classified random sample of 2,000 trials (sample size powered for 95% accuracy ± 2% CI) was independently reviewed by two reviewers (with a third adjudicating disagreements) and compared against the LLM's classification to compute accuracy, F1, precision, and recall with 95% CIs. Mid-P Clopper-Pearson approach used for confidence intervals on proportions.

**Models/Inference:** No custom model training — this is prompting/inference-only application of ChatGPT (4.0/4o) as a zero-shot-style free-text classifier assigning each trial's "condition" text to one of a fixed taxonomy of therapeutic areas.

## Datasets Used

- **ClinicalTrials.gov full export (CSV):** 499,740 total records initially identified (June 27, 2024); after excluding non-interventional studies (n=116,505) and trials published before 2005 (n=31,522) and trials missing the study description field (n=2,895), the final analytic sample was 348,818 interventional trials registered 2005–2024 (Fig. 1 PRISMA-style flow). Of these, 5,827 trials were classified as Innovative via the keyword algorithm and 342,991 as Traditional.
- **Manual validation subsample:** A random sample of 2,000 trials (drawn before LLM classification) manually classified by two independent reviewers (third reviewer adjudicated disagreements) into the 29 predefined therapeutic areas, used as ground truth to evaluate LLM classification accuracy.
- **Preprocessing:** Derivation of time-to-event intervals (first posted date, start date, completion date, last update date) for survival analysis; trials terminated before completion coded as events, all other statuses (excluding withdrawn, which were excluded from survival analysis) coded as censored.

## Models / Technologies

- ChatGPT 4.0 / ChatGPT 4o (OpenAI LLM used for free-text therapeutic-area classification of the "condition" field)
- Keyword-based string-matching algorithm (42 predefined keywords) for innovative-vs-traditional trial classification — a rule-based method, not a machine learning model
- R (version 3.4.2, R Core Team) for statistical analysis and data extraction
- Cox proportional hazards regression, Kaplan–Meier estimation, log-rank test, univariable/multivariable logistic regression (standard biostatistical methods, not deep learning)
- No RAG, no vector database, no Knowledge Graph, no PubMed eUtils/ClinicalTrials.gov API integration beyond the initial bulk CSV export; no FAISS or embeddings-based retrieval used

## Experimental Setup

- **Training:** None — ChatGPT was used purely at inference time (prompted classification), no fine-tuning performed.
- **Evaluation (Objective 1):** Descriptive statistics + inferential statistics (logistic regression ORs, Cox proportional hazards, Kaplan-Meier/log-rank) on the full 348,818-trial dataset and sub-analyses on neuroscience-specific trials (n=48,665).
- **Evaluation (Objective 2):** Accuracy, F1, precision, recall computed against the 2,000-trial manually labeled validation sample, with 95% confidence intervals (mid-P Clopper-Pearson approach). Sample size (2,000, rounded up from a calculated minimum of 1,865) was powered to detect 95% accuracy ± 2% CI.
- **Hardware:** Not reported.
- **Software:** R version 3.4.2 (R Core Team, 2015) for all statistical analyses and data extraction.

## Results

- Of 348,818 interventional trials analyzed (2005–2024), 5,827 (1.67%) were classified as Innovative and 342,991 as Traditional.
- Innovative trial adoption increased markedly from 2011 onward; Innovative trials were more likely to be Active, more likely pediatric-focused, more early-phase (I–II), more likely NIH- or network-funded, more concentrated in the Americas/Europe/Oceania (vs. Africa/Asia), more likely to post results publicly, and had significantly longer durations than Traditional trials.
- By therapeutic area, Hematology and Oncology had the highest share of Innovative trials (33% of innovative trials vs. 17% of traditional trials); Psychiatry/Substance Abuse/Mental Health rose from 6.1% (traditional) to 12% (innovative) share; Neurology and Neurosurgery similarly overrepresented among innovative trials (9.9% vs. 7.7%) (Table 1).
- Kaplan-Meier survival analysis: statistically significant difference in termination-free survival between Innovative and Traditional trials (log-rank p = 0.021), with Innovative trials generally remaining active longer.
- Cox model (Panel B, Table 2): the overall main effect of Innovative design on termination risk was not statistically significant (HR 0.97, 95% CI 0.79–1.20, p = 0.767) after adjustment, but several therapeutic areas had significantly lower termination hazards regardless of design (e.g., Hematology/Oncology HR 0.57, p<0.001; Neurology/Neurosurgery HR 0.79, p<0.001; Rare Diseases/Genetics HR 0.83, p=0.014). A significant interaction was found for Innovative × Neurology/Neurosurgery (HR 0.50, 95% CI 0.26–0.98, p=0.042), indicating innovative designs specifically reduced early-termination risk in that field.
- Neuroscience-specific analysis: within neuroscience, Psychiatry/Substance Abuse/Mental Health trials had significantly higher odds of being innovative than Neurology/Neurosurgery trials (OR 1.50, 95% CI 1.34–1.68, p<0.001; Table 3). Multivariable model: trials initiated 2011–2024 had nearly double the odds of adopting innovative design vs. earlier (OR 1.97, 95% CI 1.66–2.34, p<0.001), and Psychiatry/Substance Abuse/Mental Health area had higher odds than other neuroscience areas (OR 1.50, 95% CI 1.34–1.67, p<0.001) (Table 4).
- LLM validation: ChatGPT's therapeutic-area classification accuracy on the manually labeled 2,000-trial sample was 94.6% (95% CI 93.6%–95.5%). Radiology/Diagnostic Imaging and Dental/Otolaryngology/Rare Diseases and Genetics fields showed higher misclassification rates (underrepresented, harder-to-classify categories), while Neurology and Neurosurgery (well-represented) had no misclassifications in the manual sample.

## Strengths

- Very large-scale, real-world validation dataset (348,818 trials) directly from ClinicalTrials.gov, providing strong external validity for MOSAIC's target data source.
- Rigorous LLM validation methodology (independent dual-reviewer manual labeling, third-reviewer adjudication, power-calculated sample size, accuracy/F1/precision/recall with CIs) that can serve as a template for validating MOSAIC's own LLM-based classification or extraction components.
- Directly demonstrates that a general-purpose LLM (ChatGPT) can achieve high (94.6%) accuracy in free-text therapeutic-area classification of ClinicalTrials.gov "condition" fields — direct evidence supporting feasibility of LLM-based structuring of ClinicalTrials.gov free text for MOSAIC.
- Provides a concrete, reusable list of 42 adaptive/Bayesian design keywords and a 29-category therapeutic-area taxonomy, both of which are directly transferable assets.
- Combines classical biostatistical rigor (Cox models, Kaplan-Meier, logistic regression with adjustment) with LLM classification, illustrating a hybrid statistical + LLM pipeline architecture.
- Explicitly documents where LLM misclassification is more likely (underrepresented/overlapping categories like Rare Diseases and Genetics, Radiology), which is directly relevant to MOSAIC's expected failure modes.

## Limitations

- The "innovative trial" classification itself is keyword/rule-based (42-term string search on free text), not LLM-based or semantic — likely to miss synonyms/paraphrases and may over- or under-count depending on exact phrasing in the study description field; some keywords (e.g., "interim analysis," "group sequential") are noted by the authors as already standard in some confirmatory trial fields, potentially blurring the innovative/traditional boundary.
- LLM classification accuracy (94.6%) is high but imperfect; the authors note higher misclassification specifically in underrepresented/overlapping categories (Radiology and Diagnostic Imaging, Dental and Otolaryngology, Rare Diseases and Genetics) — a systematic weakness for rare/niche category classification.
- The study does not evaluate compliance with methodological/regulatory standards of the innovative trials identified — only whether keyword-flagged "innovative" language appears in the description, not whether the trial design was executed rigorously.
- No code/software repository provided, limiting direct reproducibility of the exact classification pipeline (though methodology is described narratively).
- Retrospective, single-timepoint dataset (June 2024 export); does not capture real-time/streaming updates to ClinicalTrials.gov.
- Some therapeutic areas (e.g., Rare Diseases and Genetics) are underrepresented in the training/validation sample, limiting confidence in classification performance for those specific areas — directly relevant caution for MOSAIC if targeting rare-disease trial matching.

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** Primarily the Data Sources & Knowledge module (ClinicalTrials.gov ingestion and structuring) and the Clinical NLP / Eligibility Extraction module, since this paper directly demonstrates LLM-based structuring of ClinicalTrials.gov free-text fields at scale.

**Exactly what we should implement:**
1. **LLM-based therapeutic-area / condition classification pipeline:** Directly adapt the paper's approach — apply an LLM (e.g., GPT-4-class model) to the free-text "condition" field of each ClinicalTrials.gov record to assign a therapeutic-area label from a fixed, curated taxonomy (the paper's 29-category list, Table 1, can be reused or adapted as MOSAIC's initial therapeutic-area ontology).
2. **Validation protocol:** Replicate the paper's validation methodology for any MOSAIC LLM classification component: draw a power-calculated random sample (e.g., ~2,000 records for ±2% CI at 95% expected accuracy), have independent human reviewers (with adjudication for disagreement) manually label a ground-truth subset, then compute accuracy/F1/precision/recall with confidence intervals before deploying the classifier at scale.
3. **Keyword list as a feature/heuristic layer:** Reuse the 42-keyword adaptive/Bayesian-design list as a rule-based pre-filter or feature input (not a replacement) for any MOSAIC module that needs to flag "innovative design" trials — e.g., as an auxiliary signal alongside LLM-based semantic classification, or for identifying trials relevant to methodologically flexible eligibility criteria.
4. **Data pipeline structure:** Reuse the PRISMA-style trial identification/exclusion flow (Fig. 1: total records → exclude non-interventional → exclude pre-cutoff-date → exclude missing key field → final analytic sample) as the template for MOSAIC's ClinicalTrials.gov ingestion/cleaning pipeline.
5. **Survival/termination-risk modeling as a downstream analytics feature:** If MOSAIC includes any trial-quality or trial-stability scoring feature (e.g., predicting likelihood a matched trial stays open/active), the Cox proportional hazards approach with therapeutic-area interaction terms is directly reusable as a modeling template.

**What should NOT be copied:**
- The specific innovative-vs-traditional keyword list and 29-category therapeutic taxonomy are domain-specific artifacts from this paper's authors' own prior work; MOSAIC should adapt/expand rather than treat them as an immutable standard, especially since the authors themselves note ambiguity in some keywords.
- The clinical/statistical conclusions about innovative trial adoption trends (e.g., specific odds ratios, hazard ratios) are epidemiological findings about the trial landscape, not techniques to implement in MOSAIC — they should be cited as motivating background context only, not re-derived or embedded as system logic.
- Do not assume 94.6% accuracy generalizes to all classification tasks MOSAIC might need (e.g., fine-grained eligibility criterion extraction is a different and likely harder task than coarse therapeutic-area assignment); MOSAIC needs its own validation per the protocol above.

**Possible improvements:**
- Where this paper used a single LLM call to assign one therapeutic-area label, MOSAIC could extend this into a multi-agent pipeline (informed by MDAgents' and MetaGPT's approaches) — e.g., a specialist "Rare Disease Classifier" agent invoked specifically when confidence in the general classifier is low or the case falls into the categories flagged in this paper as high-misclassification-risk (Radiology, Rare Diseases/Genetics).
- Replace the purely rule-based innovative-design keyword search with a hybrid LLM + keyword ensemble, potentially improving recall for paraphrased adaptive/Bayesian design descriptions that the 42-term list would miss.
- Incorporate confidence scores from the LLM classifier (not just a single label) to support MOSAIC's downstream trial-matching ranking, flagging low-confidence therapeutic-area assignments for human/agent review rather than treating classification as always deterministic.

## Personal Notes

