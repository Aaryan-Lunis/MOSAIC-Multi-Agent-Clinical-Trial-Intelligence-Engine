# MedRAG / MIRAGE

## Basic Information

**Title:** Benchmarking Retrieval-Augmented Generation for Medicine

**Authors:** Guangzhi Xiong, Qiao Jin, Zhiyong Lu, Aidong Zhang

**Year:** 2024

**Venue:** Findings of the Association for Computational Linguistics: ACL 2024 (pages 6233–6251), August 11–16, 2024

**DOI:** Not reported

**Official DOI Link:** Not reported

**Official Publisher Link:** Not reported (ACL Anthology; exact URL not present in the provided PDF)

**GitHub Repository (if available):**
- MIRAGE benchmark: https://github.com/Teddy-XiongGZ/MIRAGE
- MedRAG toolkit: https://github.com/Teddy-XiongGZ/MedRAG
- Project homepage: https://teddy-xionggz.github.io/benchmark-medical-rag/
- Leaderboard: https://teddy-xionggz.github.io/MIRAGE/

**Dataset(s) Used:**
- ClinicalTrials.gov: Not used
- AACT: Not used
- PubMed: Yes — used as one of the retrieval corpora (23.9M articles subset with valid titles/abstracts)
- PubMed eUtils: Not reported
- Other:
  - MIRAGE benchmark (5 QA datasets, 7,663 questions total): MMLU-Med (1,089 questions), MedQA-US (1,273 questions), MedMCQA (4,183 questions), PubMedQA* (500 questions), BioASQ-Y/N (618 questions)
  - Corpora for retrieval: PubMed (23.9M docs), StatPearls (9.3k docs), Textbooks (18 books), Wikipedia (6.5M docs), MedCorp (combination of all four, 30.4M docs)

---

## Research Category

- Core Clinical Trial Intelligence: Not applicable (this paper does not use clinical trial data)
- Data Sources & Knowledge: Yes (PubMed, StatPearls, Textbooks, Wikipedia corpora)
- Medical Retrieval: Yes (primary focus — retriever benchmarking)
- Multi-Agent Architecture: Not applicable
- Clinical NLP: Yes (medical question answering)
- Evaluation: Yes (primary focus — first systematic benchmark of medical RAG components)

---

## Research Problem

Large language models (LLMs) achieve strong performance on medical question-answering (QA) tasks but suffer from hallucinations and outdated knowledge. Retrieval-Augmented Generation (RAG) is a proposed remedy, but RAG systems are composed of multiple flexible components — document corpora, retrieval algorithms, and backbone LLMs — and there was no systematic understanding of which combinations of these components work best for medical QA. The paper addresses the lack of a standardized, comprehensive benchmark and toolkit for evaluating medical RAG configurations.

---

## Motivation

Prior medical RAG systems (e.g., Almanac, Clinfo.ai) were evaluated in isolated, non-comprehensive ways, and existing systematic evaluations of biomedical LLMs (e.g., Nori et al., Chen et al.) focused on vanilla LLMs without RAG. There was no first-of-its-kind benchmark that simultaneously combined zero-shot learning, multi-choice evaluation, RAG, and question-only retrieval settings to reflect realistic medical information-seeking scenarios. This gap motivated the creation of MIRAGE (benchmark) and MedRAG (toolkit).

---

## Objective

To systematically evaluate how different RAG components (corpora, retrievers, and backbone LLMs) affect performance on medical question answering, and to derive practical, evidence-based recommendations for building effective medical RAG systems.

---

## Proposed Method

**Architecture:** MedRAG toolkit — a modular RAG pipeline with three interchangeable components: (1) Corpora, (2) Retrievers, (3) LLMs.

**Pipeline:**
1. A medical question (without answer options, i.e., question-only retrieval) is passed to a retriever.
2. The retriever selects the top-*k* (default 32) snippets from a chosen corpus.
3. Retrieved snippets are concatenated and prepended to the LLM prompt.
4. Chain-of-Thought (CoT) prompting is used to have the LLM reason step-by-step and output a JSON-formatted answer with an explicit answer choice.
5. Temperature is set to 0 for deterministic outputs.

**Corpora (5):** PubMed (23.9M docs / 23.9M snippets), StatPearls (9.3k docs / 301.2k snippets), Textbooks (18 docs / 125.8k snippets), Wikipedia (6.5M docs / 29.9M snippets), MedCorp (combination of all four; 30.4M docs / 54.2M snippets).

**Retrievers (4) + fusion:** BM25 (lexical), Contriever (general-domain dense), SPECTER (scientific-domain dense), MedCPT (biomedical-domain dense, trained on PubMed user click logs). Reciprocal Rank Fusion (RRF) is used to combine retrievers: RRF-2 (BM25 + MedCPT) and RRF-4 (all four).

**LLMs (6):** GPT-4 (32k, 0613), GPT-3.5 (16k, 0613), Mixtral (8×7B), Llama-2 (70B), MEDITRON (70B, biomedical fine-tune of Llama-2), PMC-LLaMA (13B, fine-tuned on PMC papers).

**Algorithms:** No novel model training; the contribution is systematic benchmarking (41 combinations of corpora × retrievers × LLMs) plus the reusable MedRAG toolkit implementation. Retrieved snippets and answer prediction are formalized as:
Ã = RAG(Q; M, R, D) = argmax_A P_M(A | Q, inst., {d_i})
where {d_i} = R(Q; D).

**Inference:** Zero-shot, question-only retrieval (answer options withheld from the retriever, only given to the LLM for final prediction).

**Training:** No fine-tuning performed by the authors; all LLMs used off-the-shelf (closed-source via API, or open-source checkpoints).

---

## Datasets Used

**MIRAGE benchmark (evaluation set), 7,663 questions total across 5 datasets:**
- **MMLU-Med** — 1,089 questions (subset of 6 biomedical MMLU tasks: anatomy, clinical knowledge, professional medicine, human genetics, college medicine, college biology). Source: examination.
- **MedQA-US** — 1,273 four-option questions from USMLE. Source: examination. Average length 177 tokens.
- **MedMCQA** — 4,183 questions (dev set) from Indian medical entrance exams. Source: examination.
- **PubMedQA\*** — 500 questions; a modified version of PubMedQA with ground-truth supporting contexts removed to force retrieval. Source: literature (PubMed abstracts).
- **BioASQ-Y/N** — 618 Yes/No questions from BioASQ Task B (years 2019–2023), with ground-truth snippets removed. Source: literature (biomedical literature).

**Retrieval corpora:**
- **PubMed** — 23.9M documents/snippets, biomedical abstracts.
- **StatPearls** — 9,330 raw articles, 301.2k snippets; point-of-care clinical decision support content, chunked hierarchically by article structure.
- **Textbooks** — 18 widely used USMLE reference textbooks, 125.8k snippets, chunked to ≤1000 characters via LangChain's RecursiveCharacterTextSplitter.
- **Wikipedia** — 6.5M documents, 29.9M snippets, general-domain knowledge.
- **MedCorp** — union of the above four corpora (30.4M docs, 54.2M snippets), enabling cross-source retrieval.

**Preprocessing:** All corpora chunked into short snippets; snippet size varies by corpus average length (StatPearls 119, Textbooks 182, PubMed 296, Wikipedia 162 tokens average).

---

## Models / Technologies

- GPT-4 (32k context, 0613), GPT-3.5 (16k context, 0613) — via Microsoft Azure OpenAI Services
- Mixtral-8×7B (open-source mixture-of-experts)
- Llama-2-70B (open-source)
- MEDITRON-70B (biomedical fine-tune of Llama-2)
- PMC-LLaMA-13B (biomedical fine-tune of LLaMA)
- BM25 (lexical retriever, implemented via Pyserini)
- Contriever (dense retriever, pretrained on Wikipedia + CCNet)
- SPECTER (document-level scientific dense retriever, pretrained on Semantic Scholar)
- MedCPT (biomedical dense retriever, contrastively pretrained on 255M PubMed user click logs; Query Encoder + Article Encoder)
- Reciprocal Rank Fusion (RRF) for combining retrievers
- Chain-of-Thought (CoT) prompting
- Vector/embedding-based dense retrieval (no explicit vector DB named; embeddings computed via HuggingFace checkpoints)
- LangChain (RecursiveCharacterTextSplitter) for text chunking

Notably **no ClinicalTrials.gov or PubMed eUtils integration** in this paper — retrieval is from static offline corpora (PubMed abstract dump, StatPearls, textbooks, Wikipedia), not live API queries.

---

## Experimental Setup

**Training:** No model training/fine-tuning; all LLMs used as-is (zero-shot).

**Evaluation:** Accuracy of predicted multi-choice answers on each of the 5 MIRAGE datasets, plus a standard deviation reflecting the error bound; an average score across all five tasks used as the overall metric. 41 combinations of corpora, retrievers, and LLMs evaluated with over 1.8 trillion prompt tokens processed.

**Hardware:** Not reported (uses commercial APIs for GPT-4/GPT-3.5 and presumably GPU inference for open-source models; no specifics given).

**Default retrieval setting:** 32 snippets retrieved per query (default); scaling experiments test k ∈ {1, 2, 4, ..., 64}.

---

## Results

- MedRAG improves accuracy of six different LLMs by **1% to 18%** relative to Chain-of-Thought prompting alone.
- With MedRAG, **GPT-3.5 and Mixtral reach accuracy comparable to GPT-4 (CoT-only)** — around 70% average vs. GPT-4's 73.44% (CoT).
- GPT-4 (CoT) baseline average: 73.44%; GPT-4 (MedRAG): 79.97% average across 5 tasks.
- GPT-3.5 (CoT): 60.69% average; GPT-3.5 (MedRAG): 71.57% average (best average score, +17.9% relative gain — the largest improvement of all LLMs tested).
- Best individual corpus per task: Textbooks for MMLU-Med (76.68%); StatPearls for MedQA-US (67.48%); PubMed is the only single corpus that improves performance on **all** five tasks.
- MedCorp (combination of all corpora) with RRF-4 retriever achieved a state-of-the-art average of **71.57%** for GPT-3.5 on MIRAGE.
- MedCPT and BM25 were the strongest individual retrievers; RRF fusion (especially RRF-2 and RRF-4) generally improved results but not universally (e.g., RRF-2 outperformed RRF-4 on Wikipedia corpus because SPECTER performed poorly there).
- Log-linear scaling observed: accuracy improves roughly log-linearly with number of retrieved snippets k up to k≈32, then can degrade due to signal-to-noise dilution.
- "Lost-in-the-middle" effect confirmed: accuracy is lowest when the ground-truth snippet is placed in the middle of the retrieved context (U-shaped curve).
- Domain-specific LLMs (MEDITRON, PMC-LLaMA) substantially outperform general models on literature-based tasks (PubMedQA*, BioASQ-Y/N) in the CoT setting but do not always benefit as much from MedRAG.

---

## Strengths

- First systematic, large-scale benchmark (MIRAGE) combining zero-shot, multi-choice, RAG, and question-only retrieval settings for medical QA.
- Modular, open-source toolkit (MedRAG) enabling reproducible comparison of corpora, retrievers, and LLMs.
- Provides concrete, practical recommendations (e.g., MedCorp + RRF-4 as a robust default; MedCPT/BM25 as reliable retrievers).
- Reveals generalizable phenomena (log-linear scaling, lost-in-the-middle) relevant beyond medicine.
- Publicly available leaderboard and GitHub repositories support reuse.

---

## Limitations

- Only evaluates the "vanilla" single-round RAG architecture; does not test more advanced iterative/active retrieval methods (addressed later by i-MedRAG).
- Retrieval evaluation for ground-truth snippet position and "lost-in-the-middle" effects is limited to PubMedQA* and BioASQ-Y/N (the only datasets with ground-truth supporting snippets).
- Corpora restricted to PubMed abstracts, StatPearls, Textbooks, and Wikipedia; does not include full-text PMC articles or FAQs from trusted sources.
- No evaluation of the quality/faithfulness of generated rationales, only final answer accuracy.
- No integration with live clinical data sources such as ClinicalTrials.gov.

---

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** Medical Retrieval module and Evaluation module of MOSAIC; also informs the Knowledge Graph / Data Sources module design (corpus selection strategy) and any Clinical NLP QA component.

**Exactly what we should implement:**
- Adopt the **MedRAG-style modular RAG architecture** (interchangeable corpus / retriever / LLM components) as the backbone retrieval design pattern for MOSAIC's evidence-retrieval agent(s), even though MOSAIC's actual corpus will be ClinicalTrials.gov/PubMed rather than the static corpora used here.
- Reuse the **RRF (Reciprocal Rank Fusion)** strategy to combine a lexical retriever (BM25) with a domain-specific dense retriever (e.g., MedCPT) when querying PubMed/ClinicalTrials.gov-derived text, since RRF-2/RRF-4 was shown to be a robust default.
- Reuse the **evaluation methodology** (multi-choice or ground-truth-snippet based accuracy, log-linear scaling analysis of the number of retrieved snippets, "lost-in-the-middle" position analysis) as a template for MOSAIC's own retrieval-quality evaluation harness.
- Reuse **MedCPT** (query/article encoders trained on PubMed search logs) as a candidate embedding model for MOSAIC's PubMed-based retrieval component, since it consistently outperformed general-domain retrievers.
- Reuse the **prompt template design** (structured JSON output with "step_by_step_thinking" and "answer_choice" fields) as a pattern for structured LLM outputs in MOSAIC's eligibility-extraction or trial-matching agents.

**What should NOT be copied:**
- The specific benchmark datasets (MMLU-Med, MedQA-US, MedMCQA, PubMedQA*, BioASQ-Y/N) are QA-exam-style datasets, not clinical trial data — MOSAIC should not treat this as its evaluation dataset, only as an inspiration for methodology.
- The static, offline corpus snapshot approach (PubMed dump, Wikipedia dump) should not be copied wholesale; MOSAIC should favor live/periodically refreshed retrieval from PubMed eUtils and ClinicalTrials.gov to keep clinical trial data current.
- Domain-specific fine-tuned LLMs (MEDITRON, PMC-LLaMA) are heavyweight (70B/13B) and may not be practical for a capstone-scale deployment; lighter-weight open models or API-based LLMs should be substituted.

**Possible improvements:**
- Extend the MedRAG evaluation methodology to trial-eligibility matching questions instead of exam-style multi-choice QA.
- Combine MedRAG's retriever-fusion approach with i-MedRAG's iterative follow-up query mechanism (see i-MedRAG.md) for more complex, multi-hop trial-matching queries.
- Add ClinicalTrials.gov/AACT as an additional corpus type within the MedRAG-style modular architecture, benchmarking retrievers specifically on structured trial eligibility criteria text.

---

## Personal Notes

