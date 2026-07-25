# TrialGPT

## Basic Information

- **Title**: Matching patients to clinical trials with large language models
- **Authors**: Qiao Jin, Zifeng Wang, Charalampos S. Floudas, Fangyuan Chen, Changlin Gong, Dara Bracken-Clarke, Elisabetta Xue, Yifan Yang, Jimeng Sun, Zhiyong Lu
- **Year**: 2024
- **Venue**: Nature Communications, 15:9074
- **DOI**: 10.1038/s41467-024-53081-z
- **Official DOI Link**: https://doi.org/10.1038/s41467-024-53081-z
- **Official Publisher Link**: https://doi.org/10.1038/s41467-024-53081-z (Nature Communications)
- **GitHub Repository**: https://github.com/ncbi-nlp/TrialGPT
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Indirectly — candidate trials pooled from SIGIR/TREC cohorts, which are sourced from clinical trial registries
  - AACT: Not reported
  - PubMed: Not reported (not the primary data source; trial and patient data come from SIGIR/TREC)
  - PubMed eUtils: Not reported
  - Other: SIGIR 2016 patient-trial matching cohort (58 patients, 3,621 trials); TREC 2021 Clinical Trials (CT) track (75 patients, 26,149 trials); TREC 2022 CT track (50 patients, 26,581 trials) — 183 synthetic/semi-synthetic patients total, >75,000 trial annotations

## Research Category

Core Clinical Trial Intelligence; Clinical Trial Matching (patient-to-trial)

## Research Problem

Patient recruitment for clinical trials is challenging: matching patients to suitable trials requires analyzing patient medical history, understanding heterogeneous eligibility criteria, and finding a match — a process that is manual, labor-intensive, time-consuming, and error-prone.

## Motivation

Two directions exist: "trial-to-patient" (one trial to many candidate patients) and "patient-to-trial" (one patient to many candidate trials). Prior AI approaches encoded patient records and trial criteria as dense embeddings for similarity search, but this requires large paired annotated datasets (rarely available) and produces non-explainable matches, causing skepticism among medical experts. LLMs offer a way to do this with less labeled data and with natural-language explanations.

## Objective

Build an end-to-end, zero-shot, explainable framework for patient-to-trial matching using LLMs, covering retrieval of candidate trials, criterion-level eligibility prediction, and trial-level ranking/exclusion.

## Proposed Method

TrialGPT has three modules, all backed by GPT-4 (default) or GPT-3.5 (Azure OpenAI API, temperature 0):

1. **TrialGPT-Retrieval**: Given a free-text patient note, the LLM generates up to 32 ranked keywords. Each keyword is sent to both a lexical retriever (BM25) and a dense semantic retriever (MedCPT). Per-keyword rankings are combined via reciprocal rank fusion (constant C=20) with a decaying weight (1/i) across keywords and retrievers, producing a single relevance score per trial. Top-ranked trials become candidates.
2. **TrialGPT-Matching**: For each candidate trial, one LLM call handles all inclusion criteria and another handles all exclusion criteria. Using chain-of-thought style prompting, the model outputs, per criterion: (a) a free-text relevance explanation, (b) relevant sentence IDs in the patient note, and (c) an eligibility label — {included, not included, not enough information, not applicable} for inclusion criteria, {excluded, not excluded, not enough information, not applicable} for exclusion criteria. Outputs are generated in JSON for easy parsing.
3. **TrialGPT-Ranking**: Aggregates criterion-level predictions into trial-level scores via (a) linear aggregation — percentages of met/unmet/unknown inclusion and exclusion criteria, and (b) LLM aggregation — an LLM-generated "relevance" score (0–100) and "eligibility" score (−100 to 100, sign-constrained by relevance). A feature-combination score merges both aggregation types for final ranking/exclusion.

## Datasets Used

- **SIGIR 2016**: 58 patient case narratives (from TREC Clinical Decision Support tracks), 3,621 candidate trials, labels {irrelevant, potential, eligible}.
- **TREC 2021 CT**: 75 synthetic patient notes, 26,149 candidate trials, labels {irrelevant, excluded/ineligible, eligible}.
- **TREC 2022 CT**: 50 synthetic patient notes, 26,581 candidate trials, same label scheme as 2021.
- Candidate trial pools were built from the pooled judgments used by each original track (not a full external ClinicalTrials.gov crawl).
- 1,015 patient-criterion pairs (105 patient-trial pairs, 53 patients) were manually annotated by three physicians for detailed evaluation of TrialGPT-Matching.

## Models / Technologies

- GPT-4 (version 0613) and GPT-3.5 (version 0613) via Microsoft Azure OpenAI
- BM25 (lexical retriever)
- MedCPT (dense/semantic biomedical retriever)
- Reciprocal rank fusion
- Chain-of-thought prompting
- Baselines: BioBERT, PubMedBERT, SapBERT (dual-encoder), BioLinkBERT (cross-encoder, trained on MedNLI), SciFive (encoder-decoder, trained on MedNLI)

## Experimental Setup

- Inference temperature fixed at 0 for determinism.
- Retrieval evaluated via Recall@k at multiple depths k.
- Matching evaluated via manual review by 3 physicians on 1,015 patient-criterion pairs (explanation correctness, sentence-location precision/recall/F1, eligibility-label accuracy vs. consensus ground truth).
- Ranking/exclusion evaluated via NDCG@10, P@10 (ranking) and AUROC (excluding ineligible trials), computed on the top-500 trials returned by TrialGPT-Retrieval per patient across all three cohorts.
- Pilot user study: 2 MD annotators screened 6 oncology trials × 6 patient vignettes (3 short, 3 long), half with TrialGPT assistance and half without, with screening time and accuracy recorded.

## Results

- Retrieval: recalls >90% of relevant trials using <6% of the initial trial collection on average (GPT-4-based keywords need only 5.5% of the collection for 90% recall).
- Matching: 87.8% of relevance explanations judged "correct"; sentence-location F1 = 88.6% (close to human range 86.9–91.5%); overall eligibility-label accuracy = 0.873 (close to expert range 0.876–0.900).
- Ranking: GPT-4-based TrialGPT-Ranking feature combination reaches NDCG@10 = 0.7275, P@10 = 0.6688, AUROC (excluding) = 0.7979; overall average score 0.7314 vs. best baseline (BioLinkBERT/MedNLI) 0.5085 — a 43.8% relative improvement.
- User study: average screening time reduced by 42.6% with TrialGPT assistance; accuracy with TrialGPT 97.2% vs. 91.7% without (not statistically significant given sample size).

## Strengths

- High-recall first-stage retrieval that scales to tens of thousands of trials.
- Criterion-level, explainable predictions (explanation + evidence sentence + label), close to human-expert accuracy.
- Strong, validated improvement over embedding-based ranking/exclusion baselines.
- Demonstrated real-world time savings in a pilot clinician user study.
- LLM-agnostic design (works with GPT-4 or GPT-3.5).

## Limitations

- Relies on closed-source GPT-4/GPT-3.5, accessible only via commercial APIs.
- Evaluated only on free-text patient summary paragraphs, not longitudinal EHR data, lab values, or imaging.
- Does not address trial geolocation or recruitment status — must be combined with structured filters for real deployment.
- Pilot user study has a small sample size (6 trials × 6 vignettes, 2 annotators).

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: The patient-matching / eligibility-assessment module is the direct analog — this paper is essentially a blueprint for that component.
- **What to implement**: (1) LLM-based keyword generation feeding a hybrid BM25 + dense retriever with reciprocal rank fusion for first-stage candidate trial retrieval; (2) criterion-by-criterion eligibility prediction with explicit reasoning, evidence sentence IDs, and a small controlled label set (avoid ambiguous NLI labels — use eligibility-oriented labels as done here); (3) both linear and LLM-based aggregation of criterion-level predictions into trial-level relevance/eligibility scores for ranking and exclusion.
- **What should NOT be copied**: Exclusive dependence on closed-source GPT-4/GPT-3.5 as the only viable backbone; the assumption that only free-text patient notes are available (MOSAIC's PubMed/ClinicalTrials.gov integration could extend to structured data).
- **Possible improvements**: Swap in MedCPT-style retrievers already integrated with ClinicalTrials.gov data; extend matching to incorporate structured EHR fields; add geolocation/recruitment-status filtering as a preprocessing step before LLM-based matching.



