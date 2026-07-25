# CliniDigest

## Basic Information

**Title:** CliniDigest: A Case Study in Large Language Model Based Large-Scale Summarization of Clinical Trial Descriptions

**Authors:** Renee D. White, Tristan Peng, Pann Sripitak, Alexander Rosenberg Johansen, Michael Snyder

**Year:** 2023

**Venue:** GoodIT '23 — ACM International Conference on Information Technology for Social Good, September 06–08, 2023, Lisbon, Portugal (pages 396–402)

**DOI:** https://doi.org/10.1145/3582515.3609559

**Official DOI Link:** https://doi.org/10.1145/3582515.3609559

**Official Publisher Link:** Not reported (ACM Digital Library; specific landing-page URL not present in the provided PDF beyond the DOI)

**GitHub Repository (if available):** Wearipedia data-extraction library — https://github.com/Stanford-Health/wearipedia (Note: this is the companion Wearipedia project's code repository, not necessarily a dedicated CliniDigest repository; no separate CliniDigest-specific repository URL is given in the paper.)

**Dataset(s) Used:**
- ClinicalTrials.gov: Yes — primary and only data source. 457 clinical trials related to Fitbit devices were scraped from ClinicalTrials.gov.
- AACT: Not reported
- PubMed: Not used
- PubMed eUtils: Not reported
- Other: Wearipedia (an open-source encyclopedic directory of biomedical wearable sensors, the platform into which CliniDigest is integrated)

---

## Research Category

- Core Clinical Trial Intelligence: Yes (summarizing clinical trial descriptions at scale)
- Data Sources & Knowledge: Yes (ClinicalTrials.gov as sole data source)
- Medical Retrieval: Not applicable (paper does not perform retrieval search; trials are pre-scraped and pre-annotated)
- Multi-Agent Architecture: Not applicable
- Clinical NLP: Yes (large-scale abstractive summarization)
- Evaluation: Yes (readability [SMOG] evaluation; planned ROUGE-L / user-study evaluation)

---

## Research Problem

Clinical trial descriptions on ClinicalTrials.gov are numerous (100+ new trials submitted per day in 2022) and lengthy (~1,500 words on average per trial), making it practically impossible for researchers, clinicians, and clinical research coordinators to keep up-to-date manually. The paper addresses the problem of condensing large numbers (dozens to ~85) of full-length clinical trial descriptions into a single short, accurate, and reference-backed summary — a scale of multi-document summarization not previously handled for clinical trial text by a truthful, real-time LLM tool.

---

## Motivation

- On average, clinical trials take 21 months from posting on MEDLINE/ClinicalTrials.gov to publication, and only ~46% of completed studies are ever published — meaning ClinicalTrials.gov (not published articles) is often the only up-to-date source of trial information.
- Manually crafting abstracts/summaries for each wearable device page on the Wearipedia platform did not scale with the enormity of trial data and the growing number of wearable devices.
- No prior tool provided real-time, truthful, and comprehensive summaries of clinical trials at this scale; existing text summarization/IR/LLM approaches individually were judged insufficient for this specific compression + faithfulness requirement.

---

## Objective

To design and evaluate a prompt-engineering-based method (CliniDigest) using GPT-3.5 that can condense up to 85 clinical trial descriptions (~10,500 words) into a single ~200-word, reference-backed, indicative-abstractive summary, integrated into the Wearipedia wearables platform, while minimizing hallucination.

---

## Proposed Method

**Architecture:** A cascading, multi-level batch summarization pipeline built entirely on prompt engineering over GPT-3.5 (GPT-3.5-Turbo), with no model fine-tuning.

**Pipeline (Figure 2 — Batch summarization method):**
1. Trials relevant to a given medical field (and wearable device) are split into batches of 15 clinical trials each (chosen because GPT-3.5-Turbo's 4,096-token limit is exceeded even by a single medical-field's trial set — e.g., 25 oncology trials ≈ 4,900 tokens as a compact list).
2. Each batch is summarized independently by GPT-3.5 using an "intermediate prompt" (Table 1) that asks for a ~200-word "thesis" with in-text bracketed references (e.g., "[1]") to specific trials, targeted at a clinical-research-coordinator reading level.
3. If a batch has fewer than 15 trials, the requested summary word count is scaled proportionally (13 words per trial).
4. The resulting batch-level summaries (each with its own references) are then recursively combined via a second "concatenated prompt" (Table 2) that produces a 150–250-word combined thesis, weighting each input paragraph by its word count (longer paragraphs weighted more).
5. This cascading/recursive combination continues until a single final ~200-word summary remains for the given wearable–medical-field combination.

**Key prompt-engineering choices:**
- Keywords "thesis" and "argument" (rather than "summary" or "essay") were empirically found to best induce **generalized, cross-trial synthesis** rather than trial-by-trial listing.
- Explicit reference format (e.g., "[1]") was required in the prompt to reduce hallucination, since forcing citation of specific input trials compels the model to ground statements in the provided text.
- Temperature was set to 0 (reducing creativity/hallucination).
- Summaries are explicitly requested as "indicative abstractive" (broad-concept paraphrase referencing sources), as opposed to "informative" (in-depth) or "extractive" summarization styles.

**LLM:** GPT-3.5(-Turbo), used purely via prompting — no fine-tuning, no embeddings/vector retrieval, no agent framework.

**Training / Inference:** No training performed; entirely inference-time prompt engineering. Zero additional model parameters introduced.

---

## Datasets Used

- **ClinicalTrials.gov Fitbit trial set:** 457 clinical trials related to Fitbit wearables, scraped from ClinicalTrials.gov.
- Trials were manually reviewed and annotated into **14 medical fields**: somnology, gynecology, obstetrics, cardiology, general physiology, endocrinology, bariatrics, psychiatry, oncology, gastroenterology, pulmonology, chronic pain/diseases, nephrology, and "other."
- Trials were further split into two subdomains: **completed** (within past 5 years) and **new** (within past 2 years), yielding **27 medical field/subdomain combinations** (nephrology had no completed-trial data, hence 27 not 28).
- Exclusion criteria: trials that were withdrawn, and trials with enrollment < 50 participants, were removed.
- Resulting per-combination trial counts ranged from **1 to 84 clinical studies**.
- **Preprocessing:** Each trial is represented by its ClinicalTrials.gov title and brief description text; no further NLP preprocessing (e.g., NER, structured field extraction) is described — the raw title+description text is fed directly into the GPT-3.5 prompt in batches of 15.

---

## Models / Technologies

- GPT-3.5 (GPT-3.5-Turbo) — sole model used, accessed via prompting (no fine-tuning)
- Prompt engineering (batch/cascading summarization prompts; explicit reference-citation prompting to reduce hallucination)
- ClinicalTrials.gov (as a data source, accessed via web scraping — "advanced text-search algorithm" mentioned but not detailed; no explicit mention of the ClinicalTrials.gov API or PubMed eUtils)
- Wearipedia platform / Python package (open-source wearable data extraction pipeline that CliniDigest is designed to integrate into) — https://github.com/Stanford-Health/wearipedia
- SMOG readability formula (evaluation metric)
- ROUGE-L F1 metric (planned/future evaluation metric, not yet executed in this paper)
- No knowledge graph, no vector database/FAISS, no BioBERT/transformer fine-tuning, no ClinicalTrials.gov or PubMed eUtils API integration described.

---

## Experimental Setup

**Training:** None — GPT-3.5 used purely via prompting; no parameter updates.

**Evaluation:**
- **Preliminary evaluation** (conducted): length and reference-density analysis of generated summaries across 14 medical fields; readability comparison via SMOG formula between raw ClinicalTrials.gov text and CliniDigest summaries (two-sample t-test of means).
- **Planned (not yet conducted) evaluation** (Section 4.2, "Systematic Evaluation Plan"): a controlled user study with clinical research coordinators comparing CliniDigest-generated summaries against Wearipedia's existing sidebar-links method, using participant-written summaries scored with ROUGE-L F1, plus a qualitative post-evaluation questionnaire.

**Hardware:** Not reported.

**Key quantitative evaluation results (preliminary):**
- Across all 14 fields, mean summary length μ = 153 words (σ = 69), utilizing μ = 54% (σ = 30%) of source trials referenced.
- For the 17 summaries requiring a second (cascading) combination step: final summaries μ = 192 words (σ = 27), with 100% falling within the requested 150–250-word range.
- Example single-batch result (general physiology, 39 completed trials): 201-word summary containing 11 references.
- Reference-count vs. input-trial scatter plot (Figure 3): linear trend up to ~50 input trials (slope m = 0.5140, r² = 0.7547); diminishing returns beyond 50 trials.

---

## Results

- CliniDigest successfully compresses up to 85 clinical trial descriptions (~10,500 words) into a ~200-word summary with in-text references, using multi-level cascading GPT-3.5 prompting.
- SMOG readability test: raw ClinicalTrials.gov text x̄₁ = 19.32 (s₁ = 1.220) vs. CliniDigest summaries x̄₂ = 18.49 (s₂ = 2.148); two-sample t-test p = 0.0929 — **not statistically significantly different in readability**, meaning CliniDigest's condensation did not oversaturate summaries with polysyllabic jargon relative to the source material.
- Authors note SMOG may be artificially inflated for CliniDigest's summaries due to (a) higher density of polysyllabic words per sentence from compression, and (b) the unavoidable presence of technical polysyllabic terms core to clinical trial content.
- The full systematic user-study evaluation (with real clinical research coordinators, ROUGE-L scoring against human-written reference summaries) was **planned but not completed** at the time of this publication — results reported are preliminary/descriptive only.

---

## Strengths

- Addresses a genuine, quantified real-world bottleneck (100+ trials/day, 1,500 words average, 21-month publication lag, only 46% of trials ever published).
- Simple, reproducible, fine-tuning-free method (pure prompt engineering) that can be adapted to any LLM with a context-window limitation.
- Explicit hallucination-mitigation strategy (forced in-text references + temperature=0) with an empirical (if preliminary) test of readability preservation.
- Designed for real integration into a live platform (Wearipedia), not just an academic proof-of-concept.
- Clear cascading/recursive design pattern for handling arbitrarily large document sets under a fixed LLM context window — broadly reusable beyond clinical trials.

---

## Limitations

- Evaluation is preliminary; the paper's own planned comprehensive evaluation (real clinical research coordinators, ROUGE-L against human summaries, breadth/depth comprehension testing) had **not yet been conducted** at publication time.
- No fact-checking or automated hallucination-detection mechanism beyond the informal expectation that reference-citation reduces (but does not eliminate) hallucination; hallucinations are explicitly acknowledged as still possible.
- Uses only GPT-3.5-Turbo (an older, weaker, and now largely superseded LLM); no comparison against more capable models (e.g., GPT-4) or open-source alternatives.
- Dataset limited to Fitbit-related trials on ClinicalTrials.gov (457 trials, 14 fields) — narrow scope compared to the full breadth of ClinicalTrials.gov content.
- No retrieval component: relies on a fixed, pre-scraped/pre-annotated batch of trials rather than a live query-driven retrieval pipeline.
- SMOG-based readability evaluation is explicitly called out by the authors as not fully authoritative and potentially artificially inflated by compression effects.

---

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** Core Clinical Trial Intelligence module (trial summarization sub-component); potentially feeds into a "Trial Digest / Overview Generation" feature that complements MOSAIC's eligibility-matching and retrieval modules by giving users/clinicians a compressed, human-readable overview of many related trials at once.

**Exactly what we should implement:**
- Reuse the **cascading/recursive batch-summarization pattern** (split into fixed-size batches → summarize each batch → recursively combine batch summaries weighted by length) as a general strategy for MOSAIC whenever the number of retrieved ClinicalTrials.gov/PubMed documents exceeds the LLM's context window.
- Reuse the **explicit in-text reference/citation prompting technique** ("write a thesis with references to trials in the format [1]") as a lightweight, low-cost hallucination-mitigation strategy for any MOSAIC module that summarizes multiple trial records or PubMed abstracts.
- Reuse the **prompt-keyword insight** (favor "thesis"/"argument" phrasing over "summary"/"essay" to induce cross-document synthesis rather than sequential listing) when designing MOSAIC's own summarization prompts.
- Reuse **temperature = 0** as a default setting for any MOSAIC LLM call intended to produce grounded, low-variance factual output (e.g., trial summaries, eligibility explanations).
- Consider adapting the **SMOG-based readability check** as a lightweight automated QA gate on any generated summary before it's shown to end users.

**What should NOT be copied:**
- Do not rely on GPT-3.5-Turbo as the production LLM; MOSAIC should use a more current, capable model (with a larger context window), which would reduce or eliminate the need for the batch-of-15 cascading workaround in many cases.
- Do not adopt the narrow, pre-scraped, single-device (Fitbit) dataset scope; MOSAIC's summarization module should operate over the full breadth of trials relevant to a given query, retrieved live rather than statically pre-annotated.
- Do not treat the preliminary SMOG readability result as a validated evaluation methodology — MOSAIC should implement (or adapt) the more rigorous, user-study-based evaluation plan that CliniDigest itself proposed but did not complete (ROUGE-L against human-written summaries, breadth/depth comprehension testing with real clinical stakeholders).
- Do not assume forced references alone are sufficient hallucination mitigation — MOSAIC should pair this technique with a more robust verification step (e.g., cross-checking generated claims against retrieved source spans, as explored in MedRAG/i-MedRAG-style grounded QA).

**Possible improvements:**
- Combine CliniDigest's cascading summarization technique with MedRAG's retriever-fusion approach (MedRAG.md) so that the "batches" fed into the cascade are themselves the output of a high-quality, ranked retrieval step over live ClinicalTrials.gov/PubMed data, rather than a fixed manually-curated trial set.
- Extend CliniDigest's reference-citation mechanism into a clickable/traceable citation system in MOSAIC's UI, linking each summary claim back to its specific source trial record (NCT ID) for auditability.
- Implement the user-study evaluation plan that CliniDigest proposed (Section 4.2) as MOSAIC's own formal evaluation protocol for any trial-summarization feature, since it was well-designed but left unexecuted in the original paper.

---

## Personal Notes

