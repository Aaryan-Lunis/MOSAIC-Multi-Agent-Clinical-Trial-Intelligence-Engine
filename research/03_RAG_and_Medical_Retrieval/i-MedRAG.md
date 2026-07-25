# i-MedRAG

## Basic Information

**Title:** Improving Retrieval-Augmented Generation in Medicine with Iterative Follow-up Questions

**Authors:** Guangzhi Xiong, Qiao Jin, Xiao Wang, Minjia Zhang, Zhiyong Lu, Aidong Zhang

**Year:** 2024 (copyright notice) / presented at Pacific Symposium on Biocomputing 2025

**Venue:** Pacific Symposium on Biocomputing (PSB) 2025, pages 199–214

**DOI:** Not reported

**Official DOI Link:** Not reported

**Official Publisher Link:** Not reported (published via World Scientific Publishing Company under CC BY-NC 4.0; specific URL not present in the provided PDF)

**GitHub Repository (if available):** Not reported

**Dataset(s) Used:**
- ClinicalTrials.gov: Not used
- AACT: Not used
- PubMed: Indirectly — via the Textbooks and StatPearls corpora used for the underlying RAG retrieval (as introduced in the MedRAG paper); MedCPT retriever (trained on PubMed search logs) is used
- PubMed eUtils: Not reported
- Other: MedQA (USMLE subset), MMLU-Med (6 biomedical MMLU tasks), Textbooks corpus, StatPearls corpus (both corpora reused from MedRAG/MIRAGE)

---

## Research Category

- Core Clinical Trial Intelligence: Not applicable (paper addresses medical exam QA, not clinical trials directly)
- Data Sources & Knowledge: Yes (reuses Textbooks and StatPearls corpora)
- Medical Retrieval: Yes (primary focus — iterative retrieval)
- Multi-Agent Architecture: Partially — iterative self-querying LLM loop (single LLM acting iteratively, not a multi-agent system per se, but conceptually related to agentic reasoning loops)
- Clinical NLP: Yes (medical question answering / multi-step clinical reasoning)
- Evaluation: Yes (benchmarked on MedQA-USMLE and MMLU-Med)

---

## Research Problem

Standard (vanilla) RAG systems in medicine perform only a **single round of retrieval** based on the original question. This is insufficient for complex clinical questions (e.g., USMLE-style vignettes) that require multi-step reasoning — such as first inferring a diagnosis from symptoms, then retrieving information about treatment for that diagnosis. Text retrievers based on lexical/semantic similarity to the original question cannot decompose such multi-hop questions, so vanilla RAG often fails to retrieve the specific information needed partway through the reasoning chain.

---

## Motivation

While RAG has been shown to help on single-hop biomedical QA tasks (e.g., PubMedQA, BioASQ) with direct answers in one document, prior medical RAG systems (Almanac, Clinfo.ai, MedRAG) all use a single round of retrieval and show only marginal gains on complex multi-hop questions like MedQA. Iterative retrieval-generation approaches had been explored in the general NLP domain (e.g., interleaving retrieval with chain-of-thought), but not yet applied to medicine. This gap motivated i-MedRAG.

---

## Objective

To design and evaluate a RAG framework that allows LLMs to iteratively generate and answer follow-up queries — building an information-seeking history — in order to improve performance on complex, multi-step medical reasoning questions, without requiring any training examples (zero-shot).

---

## Proposed Method

**Architecture:** i-MedRAG replaces the single information-retrieval step of vanilla RAG with an iterative "reason-then-query" loop.

**Pipeline (Algorithm 1):**
1. Initialize an empty information-seeking history H.
2. For each iteration i = 1 to m:
   - If i = 1: the LLM generates n follow-up queries given only the original question Q.
   - If i > 1: the LLM generates n new follow-up queries given Q and the accumulated history H.
   - For each of the n queries: retrieve N relevant documents using retriever R and corpus D; the LLM generates an answer to that specific query using the retrieved documents; the (query, answer) pair is appended to H.
3. After m iterations, the LLM generates the final predicted answer Ã using the original question Q and the full history H.

**Formalization:**
Ã = i-MedRAG(Q; M, R, D) = argmax_A P_M(A | Q, inst., {(q_i, a_i)}_{i=1}^{N})
Query generation at iteration i:
- i=1: q_i1,...,q_in = argmax P_M(q_i1,...,q_in | Q, inst.′)
- i>1: q_i1,...,q_in = argmax P_M(q_i1,...,q_in | Q, inst.′, history of prior (query, answer) pairs)

**Key hyperparameters:** m (number of iterations) and n (number of queries generated per iteration).

**LLMs used:** GPT-3.5 (closed-source) and Llama-3.1-8B (open-source, 128k context).

**Retrieval component reused from MedRAG:** Textbooks and StatPearls corpora, MedCPT retriever.

**Training:** None — fully zero-shot; hyperparameters (m, n) tuned on a 100-sample validation set, then evaluated on the test set.

**Inference:** Zero-shot; no few-shot demonstrations used (explicitly chosen to reflect realistic clinical scenarios).

---

## Datasets Used

- **MedQA (USMLE subset)** — patient-vignette-style multi-choice medical questions from the United States Medical Licensing Examination; used as primary testbed for complex multi-hop clinical reasoning. Source: examination questions (citation 26 in the paper).
- **MMLU-Med** — six medical tasks from Massive Multitask Language Understanding (anatomy, clinical knowledge, professional medicine, human genetics, college medicine, college biology), following prior work; used as a secondary, generally "less complex" QA testbed.
- **Retrieval corpora (reused from MedRAG/MIRAGE):** Textbooks and StatPearls, both shown effective on medical examination questions in the earlier MedRAG study.
- **Preprocessing:** Hyperparameters tuned on a validation set of 100 samples; results reported on the held-out test set. No new corpus preprocessing introduced; corpora reused as-is from MedRAG.

---

## Models / Technologies

- GPT-3.5-Turbo (closed-source LLM backbone)
- Llama-3.1-8B (open-source LLM backbone, 128k context window)
- MedCPT (biomedical dense retriever, reused from MedRAG)
- Textbooks and StatPearls corpora (reused from MedRAG)
- Chain-of-Thought (CoT) prompting (baseline comparison)
- Self-Consistency (SC) prompting (baseline comparison)
- MedAgents (multi-agent communication baseline comparison)
- Knowledge Solver (KSL), LLM-AMT (LLMs Augmented with Medical Textbooks), MedAdapter (baseline comparisons)
- Iterative "reason-then-query" prompting framework (the paper's core contribution — a prompting technique, not a new model)

---

## Experimental Setup

**Training:** None (zero-shot; no fine-tuning or parameter updates). Hyperparameters (m: iterations, n: queries per iteration) tuned via grid search over a 100-sample validation set per LLM/dataset pair.

**Evaluation:** Accuracy of predicted multi-choice answers on MedQA-USMLE and MMLU-Med test sets, compared against official reported scores for baseline methods (CoT, SC, KSL, MedAgents, LLM-AMT, MedRAG, MedAdapter) and against the authors' own re-implementations of CoT and MedRAG for the Llama-3.1-8B/MMLU-Med generalization experiments.

**Hardware:** Not reported.

**Hyperparameter scaling experiments:** Tested m (iterations) from 1–6 and n (queries per iteration) ∈ {1, 2, 3} across both GPT-3.5 and Llama-3.1-8B on both MedQA and MMLU-Med.

---

## Results

- **i-MedRAG (zero-shot) achieves 69.68% accuracy on MedQA with GPT-3.5**, setting a new state-of-the-art among GPT-3.5-based methods — surpassing all previously reported prompt-engineering and even fine-tuned methods (CoT 50.82%, KSL 58.40%, CoT+SC 61.30%, MedAgents 64.10%, LLM-AMT 65.00% zero-shot / 67.90% fine-tuned, MedRAG 66.61%, MedAdapter 68.66% fine-tuned).
- This is a statistically significant improvement (p < 0.05) over the previous best zero-shot record (MedRAG, 66.61%).
- On Llama-3.1-8B: i-MedRAG achieves **73.61% on MedQA-USMLE** (vs. CoT 64.73%, MedRAG 66.54%) — a +13.72% relative improvement over CoT, and 78.42% on MMLU-Med (vs. CoT 77.23%, MedRAG 78.05%) — a smaller +1.54% relative improvement.
- Averaged across MedQA-USMLE and MMLU-Med: GPT-3.5 i-MedRAG reaches 72.77% average (+5.49% relative vs. CoT); Llama-3.1-8B i-MedRAG reaches 76.02% average (+7.10% relative vs. CoT).
- Improvement from i-MedRAG is **much larger on MedQA (complex, multi-hop USMLE vignettes) than on MMLU-Med (simpler, more direct questions)**, confirming the hypothesis that iterative retrieval specifically helps multi-step reasoning.
- Scaling analysis: accuracy on MedQA generally improves with more iterations (up to 5–6); accuracy on MMLU-Med converges or drops after just 1–2 iterations. More queries per iteration (n) yields faster but earlier-converging improvement.
- Case studies (Tables 3 and 4) qualitatively show i-MedRAG successfully identifying an unstated drug (cisplatin) causing ototoxicity, and correctly diagnosing diverticulitis, in scenarios where CoT and vanilla MedRAG both failed or hallucinated.

---

## Strengths

- First-of-its-kind study introducing follow-up-query iteration specifically for medical RAG.
- Achieves new zero-shot state-of-the-art on MedQA-USMLE with GPT-3.5, without any fine-tuning or few-shot examples.
- Demonstrated generalizability across both a closed-source (GPT-3.5) and an open-source (Llama-3.1-8B) LLM, and across two different datasets (MedQA, MMLU-Med).
- Detailed hyperparameter scaling analysis (iterations × queries per iteration) provides practical tuning guidance.
- Qualitative case studies clearly illustrate the mechanism by which iterative queries resolve information gaps that single-round retrieval misses.

---

## Limitations

- **High cost:** cost grows linearly with the number of follow-up queries generated (and with number of documents retrieved per query); much more expensive than baseline CoT prompting.
- **Hyperparameter sensitivity:** optimal (m, n) settings vary by LLM and by task/dataset, making it non-trivial to select good hyperparameters for a new medical task without a validation set — potentially inefficient for real-world deployment.
- No few-shot demonstration strategy has been integrated (left as future work), unlike few-shot CoT which is known to outperform zero-shot CoT.
- Only tested on multi-choice QA benchmarks (MedQA, MMLU-Med); not tested on open-ended or trial-matching-style tasks.
- No automation of hyperparameter selection — an LLM agent to dynamically decide number of follow-up queries is proposed as future work but not implemented.

---

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** Multi-Agent Architecture module and Medical/Clinical Trial Retrieval module — specifically any component that must resolve **multi-hop clinical trial eligibility questions** (e.g., "does this patient with condition X and lab value Y qualify for trial Z, which requires prior treatment W") where a single retrieval pass over ClinicalTrials.gov/PubMed text is unlikely to surface all needed facts.

**Exactly what we should implement:**
- Implement the **iterative "reason-then-query" loop (Algorithm 1)** as a core reasoning strategy for MOSAIC's trial-eligibility-matching agent: given a candidate patient profile and a trial's eligibility criteria, allow the LLM to generate follow-up queries (e.g., about drug mechanisms, lab value thresholds, prior-treatment history definitions) and answer them against PubMed/trial-corpus retrieval before final matching.
- Reuse the **information-seeking history representation** — storing (query, answer) pairs rather than raw retrieved documents — to keep LLM context length manageable while preserving grounding, directly applicable to MOSAIC's multi-agent orchestration where an "eligibility agent" needs a compact evidence trail.
- Reuse the **hyperparameter tuning protocol** (small validation set to tune m and n) as a lightweight calibration step before deploying MOSAIC's iterative retrieval agent on a new trial domain.

**What should NOT be copied:**
- The specific evaluation datasets (MedQA, MMLU-Med) are exam-style QA, not clinical trial matching, so they should not be adopted as MOSAIC's own benchmark — only the iterative retrieval *mechanism* should be reused.
- The paper's retrieval corpora (Textbooks, StatPearls) are static, exam-oriented references; MOSAIC's retrieval backend should instead target live ClinicalTrials.gov / PubMed data.
- Do not blindly copy the high iteration counts (up to 6) without cost-awareness — the paper itself flags the linear cost growth as a limitation, so MOSAIC should implement an early-stopping or confidence-based termination criterion rather than a fixed m.

**Possible improvements:**
- Combine i-MedRAG's iterative query framework with MedRAG's retriever-fusion (RRF) approach for stronger per-iteration retrieval quality (see MedRAG.md).
- Automate the choice of m and n per query using an LLM-based controller (as suggested by the authors' own "future work" section) rather than a fixed hyperparameter grid — potentially implemented as a dedicated "orchestrator agent" within MOSAIC's multi-agent design.
- Extend the query-answer history mechanism into a lightweight knowledge graph of accumulated facts per patient-trial pair, enabling reuse of previously retrieved information across multiple trial evaluations for the same patient.

---

## Personal Notes

