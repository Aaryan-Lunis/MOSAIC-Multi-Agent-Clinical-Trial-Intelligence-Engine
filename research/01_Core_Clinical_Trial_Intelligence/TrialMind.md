# TrialMind

## Basic Information

- **Title**: Accelerating clinical evidence synthesis with large language models
- **Authors**: Zifeng Wang, Lang Cao, Benjamin Danek, Qiao Jin, Zhiyong Lu, Jimeng Sun
- **Year**: 2025
- **Venue**: npj Digital Medicine, 8:509
- **DOI**: 10.1038/s41746-025-01840-7
- **Official DOI Link**: https://doi.org/10.1038/s41746-025-01840-7
- **Official Publisher Link**: https://doi.org/10.1038/s41746-025-01840-7 (npj Digital Medicine)
- **GitHub Repository**: https://github.com/RyanWangZf/TrialMind-SLR
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Not reported (this paper's evidence base is published literature/systematic reviews, not trial registry records)
  - AACT: Not reported
  - PubMed: Yes — used for literature search, and as the source of the systematic reviews and cited studies used to build TrialReviewBench
  - PubMed eUtils: Not explicitly named, but retrieval from PubMed is described as being done via APIs
  - Other: TrialReviewBench (custom benchmark built from 100 published systematic reviews, 2,220 associated clinical studies); dataset hosted at https://huggingface.co/datasets/zifeng-ai/TrialReviewBench

## Research Category

Medical Retrieval; Evaluation; Core Clinical Trial Intelligence (evidence synthesis)

## Research Problem

Clinical evidence synthesis relies on systematic reviews (SRs), which are expensive and slow to produce (avg. 5 experts and 67.3 weeks per review) and quickly become outdated given the rapid growth of the literature (PubMed indexes 35M+ citations, gaining 1M+ annually). The paper addresses how to accelerate study search, study screening, and data/result extraction — the core steps of SR construction — using generative AI while remaining PRISMA-compliant and trustworthy.

## Motivation

LLMs excel at instruction-following and have been applied piecemeal to SR sub-tasks (query generation, attribute extraction, citation screening, summarization), but few works evaluate LLMs across the full evidence-synthesis pipeline as defined by the PRISMA statement, and LLMs suffer from hallucination, weak numerical reasoning, generic outputs, and lack of transparency. A benchmark and an integrated, human-in-the-loop pipeline were both missing.

## Objective

Build TrialMind, a generative AI pipeline that streamlines study search, study screening, and data extraction within the PRISMA workflow, breaking the process into inspectable/editable subtasks so human experts can monitor, edit, and verify intermediate outputs, and evaluate it on a new benchmark (TrialReviewBench).

## Proposed Method

TrialMind follows the PRISMA stages (identification → screening → inclusion) via four pipeline steps:

1. **Literature search**: From PICO (Population, Intervention, Comparison, Outcome) elements, an LLM generates and augments treatment/condition search terms; users can check/edit/add terms; terms are combined into Boolean queries and used to retrieve studies from PubMed. Uses retrieval-augmented generation (abstracts of an initial retrieval round enrich the LLM context) and chain-of-thought (CoT) multi-step term generation → filtering → self-reflective augmentation.
2. **Literature screening**: The LLM generates a list of eligibility criteria from PICO; for each identified study it predicts criterion-level eligibility as {−1 = ineligible, 0 = unknown, 1 = eligible}; per-study, criterion-level predictions are summed into a study-level relevance score for ranking.
3. **Data extraction**: Given user-specified data fields (with natural-language descriptions), the LLM parses full study content (text, tables, figures) and extracts structured field values, each grounded with a source index/location for user verification.
4. **Evidence synthesis**: For target clinical endpoints, the LLM extracts raw result descriptions, then (via a separate step) writes and executes Python code to standardize the numeric values (e.g., event rates) into a common format; standardized results across studies are fed into R (`meta` package) to produce pooled statistics/forest plots, with human-in-the-loop qualitative synthesis.

Backbone LLMs: GPT-4 (gpt-4-0125-preview) and Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0 via AWS Bedrock). Techniques combined: in-context learning, retrieval-augmented generation, and chain-of-thought prompting, formalized as a general LLM-driven multi-step workflow where each subtask's output feeds the next.

## Datasets Used

- **TrialReviewBench**: Built from 100 published systematic reviews covering four cancer-therapy topics (Immunotherapy: 32 reviews/791 studies; Radiation/Chemotherapy: 24/635; Hormone Therapy: 22/521; Hyperthermia: 22/273), totaling 2,220 clinical studies.
- Manual annotations: 1,334 study-characteristic data points (696 study design, 353 population features, 285 results) and 1,049 study-result annotations (from forest-plot-reported outcomes).
- Built via PubMed search using cancer-treatment keywords from the National Cancer Institute's treatment list, MeSH-term filtering, and manual screening (46,192 → 2,691 → 1,967 → 352 → 100 reviews after successive filtering stages).
- Dataset publicly hosted on Hugging Face (zifeng-ai/TrialReviewBench).

## Models / Technologies

- GPT-4 (gpt-4-0125-preview) and Claude 3 Sonnet (Anthropic, via AWS Bedrock) as backbone LLMs
- MPNet and MedCPT (general-domain and medical-domain ranking baselines for screening)
- Random baseline (screening)
- OpenAI embeddings (for candidate-set relevance filtering in ranking experiments)
- Retrieval-Augmented Generation (RAG), Chain-of-Thought (CoT) prompting, in-context learning
- Python (for programmatic result standardization) and R `meta` package (for forest plots/pooled analysis)
- Software stack: pandas, numpy, scipy, scikit-learn, openai, langchain, boto3, pypdf, lxml, chromadb (Python 3.9)

## Experimental Setup

- **Study search**: Evaluated via Recall against GPT-4-prompted-query and Human (UMLS-expanded manual query) baselines, across the four therapy topics and 16 additional non-oncology therapeutic areas (in supplementary results).
- **Study screening**: Evaluated via Recall@20 and Recall@50 on a candidate set of 2,000 studies (mixing target studies with other retrieved studies) per review, compared to MPNet, MedCPT, and Random baselines; leave-one-out analysis (ΔRecall@200) assessed the contribution of individual eligibility criteria.
- **Data extraction**: Evaluated via Accuracy against manually digitized study-characteristic tables; a confusion-matrix analysis quantified hallucination (false positives) vs. missing information (false negatives) with precision/recall.
- **Result extraction**: Compared against GPT-4 and Claude 3 Sonnet baselines (minimal prompting + manual post-processing) via Accuracy, with error-type analysis (inaccurate, extraction failure, unavailable data, hallucination).
- **Human evaluation**: 8 annotators (5 medical doctors, 3 computer scientists) rated forest plots generated by TrialMind vs. a GPT-4+Human baseline across 5 systematic reviews, on a win/lose basis and a 1–5 rating scale, stratified by self-reported expertise level.
- **User study**: 2 participants compared Human-only vs. AI+Human (TrialMind-assisted) workflows for both study screening (4 reviews × 100 candidates each) and data extraction (10 studies each), measuring Recall/Accuracy and time cost.

## Results

- Study search: TrialMind achieves average Recall 0.782 overall (topic-wise: 0.797 Immunotherapy, 0.780 Radiation/Chemotherapy, 0.711 Hormone Therapy, 0.834 Hyperthermia) vs. GPT-4 baseline Recall ≈0.02–0.11 and Human baseline Recall ≈0.14–0.23.
- Study screening: TrialMind improves Recall@20/@50 by a fold-change of 1.3–2.6× over the best baseline across the four topics (e.g., Immunotherapy Recall@20 0.567 vs. best baseline 0.219).
- Data extraction: Accuracy of 0.72–0.83 across the four topics; outperforms GPT-4 by 16–32 percentage points on result extraction specifically (e.g., Immunotherapy ACC 0.70 vs. GPT-4 0.54).
- Precision/recall against hallucination and missing data: Precision 0.994 (study design) / 0.966 (population) / 0.862 (study results); Recall 0.946 / 0.889 / 0.930 respectively.
- Human evaluation: TrialMind's synthesized evidence was preferred over the GPT-4+Human baseline in 62.5–100% of cases across the 5 reviews studied.
- User study: AI+Human screening improved Recall by 71.4% and cut time by 44.2% vs. Human-only; AI+Human extraction improved Accuracy by 23.5% and cut time by 63.4% vs. Human-only.

## Strengths

- Modular, PRISMA-aligned pipeline enabling human-in-the-loop verification at every stage (search terms, eligibility criteria, extracted fields, standardized results).
- All extracted data are grounded with links back to source text, aiding trust and error correction.
- Large, purpose-built benchmark (TrialReviewBench) with substantial manual annotation for rigorous evaluation.
- Strong, consistent gains over both naive LLM prompting and prior document-ranking methods across search, screening, and extraction.
- Validated with a genuine human-AI collaboration user study showing both quality and time improvements.

## Limitations

- Even with multiple technique layers, LLMs can still make errors at any stage — human oversight remains necessary.
- The evaluation dataset, while large, is limited in size due to the cost of human labeling, and is focused on oncology treatments; generalizability to non-oncology domains, preventive interventions, or diagnostics remains to be established.
- Restricted to studies available on PubMed Central with structured PDFs/XMLs; many relevant studies are unavailable or require OCR, which is not yet incorporated.
- Not an end-to-end SR solution — steps like formal quality assessment and report drafting are not yet covered.
- LLM API costs and processing time may bottleneck practical use at scale.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: The PubMed/literature-retrieval and evidence-synthesis modules (complementary to a ClinicalTrials.gov-focused matching module like TrialGPT/AutoTrial).
- **What to implement**: The PICO-driven query generation + augmentation + CoT self-reflective refinement loop for PubMed search; the {−1, 0, 1} criterion-level eligibility screening scheme with per-study aggregation for ranking; the grounded/source-linked data-extraction pattern (extract value + index/location for traceability); and the two-step result-extraction approach (LLM extracts raw text → LLM/generated code numerically standardizes it) for building meta-analysis-ready outputs.
- **What should NOT be copied**: Exclusive dependence on GPT-4/Claude 3 Sonnet as the only backbones (cost/latency concerns for a capstone-scale system); the oncology-only scope of TrialReviewBench as a stand-in for general validation.
- **Possible improvements**: Extend the pipeline beyond oncology to match MOSAIC's broader scope; integrate ClinicalTrials.gov trial records alongside PubMed literature so screening/extraction can operate over both trial registries and publications in one workflow; consider open-source or smaller fine-tuned LLMs for lower-cost extraction steps.

## Personal Notes

