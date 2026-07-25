# MDAgents

## Basic Information

- **Title:** MDAgents: An Adaptive Collaboration of LLMs for Medical Decision-Making
- **Authors:** Yubin Kim, Chanwoo Park, Hyewon Jeong, Yik Siu Chan, Xuhai Xu, Daniel McDuff, Hyeonhoon Lee, Marzyeh Ghassemi, Cynthia Breazeal, Hae Won Park
- **Year:** 2024
- **Venue:** 38th Conference on Neural Information Processing Systems (NeurIPS 2024)
- **DOI:** Not reported in the provided document
- **Official DOI Link:** Not reported
- **Official Publisher Link:** Not reported (arXiv version: arXiv:2404.15155v3 [cs.CL])
- **GitHub Repository:** https://github.com/mitmedialab/MDAgents
- **Dataset(s) Used:**
  - ClinicalTrials.gov: No
  - AACT: No
  - PubMed: Indirectly (PubMedQA uses PubMed abstracts) — see Datasets Used
  - PubMed eUtils: No
  - Other: MedQA, PubMedQA, DDXPlus, SymCat, JAMA (Clinical Challenge), MedBullets, Path-VQA, PMC-VQA, MedVidQA, MIMIC-CXR-VQA

## Research Category

- Multi-Agent Architecture
- Clinical NLP
- Evaluation
- Medical Retrieval (peripherally, via MedRAG ablation)

## Research Problem

Solitary LLMs, and even existing static multi-agent LLM frameworks (fixed number of agents, fixed interaction pattern — e.g., Voting, Debate, MedAgents, ReConcile), do not adapt their collaboration structure to the varying complexity of medical decision-making (MDM) tasks. Real-world clinical decision-making ranges from single-clinician management of simple cases to multidisciplinary team (MDT) discussion or sequential integrated care team (ICT) consultation for complex cases, but prior LLM multi-agent "generalist" designs apply the same fixed collaboration structure regardless of task complexity, which can be computationally inefficient (over-provisioned for easy cases) or insufficiently thorough (under-provisioned for hard cases).

## Motivation

Clinicians naturally scale their collaborative effort to case complexity (e.g., a PCP handles routine cases alone; complex multi-organ or trauma cases require MDT or ICT consultation). No prior LLM framework mirrors this adaptive, tiered structure — existing multi-agent methods (Voting, Debate, MedAgents, ReConcile, AutoGen, DyLAN) rely on a pre-determined, static number of agents and a fixed interaction pattern regardless of query difficulty, risking suboptimal configurations, wasted computation (excessive API calls for easy cases), or inadequate reasoning depth for hard cases.

## Objective

To introduce MDAgents, the first adaptive multi-agent LLM decision-making framework for medicine that dynamically assigns a solo, moderate (MDT), or high (ICT) collaboration structure based on automatically assessed query complexity, aiming to improve both accuracy and computational efficiency (fewer API calls) relative to static solo and group baselines across a broad suite of medical benchmarks.

## Proposed Method

**Four-stage pipeline (Algorithm 1):**
1. **Medical Complexity Check:** A Moderator LLM agent (acting as a generalist practitioner/GP) classifies each incoming medical query as *Low*, *Moderate*, or *High* complexity based on clinical decision-making constructs (acuity for low; comorbidity/case-management complexity for moderate; severity of illness for high).
2. **Expert Recruitment:** A Recruiter LLM agent assembles the response team based on the complexity level:
   - *Low* → a single Primary Care Clinician (PCC) agent.
   - *Moderate* → a Multidisciplinary Team (MDT) of several domain-specialist LLM agents.
   - *High* → an Integrated Care Team (ICT) composed of multiple sequential specialist sub-teams.
3. **Analysis and Synthesis:**
   - *Low:* the PCC agent answers directly via few-shot prompting (Chain-of-Thought / Self-Consistency).
   - *Moderate:* the MDT engages in iterative multi-turn, multi-round collaborative discussion (up to R rounds, T turns per round) to reach consensus; if no consensus, a Moderator reviews the discourse and provides feedback for another round.
   - *High:* the ICT proceeds through multiple teams (e.g., Initial Assessment Team → diagnostic teams → Final Review & Decision Team), each producing a structured report that synthesizes findings and passes to the next team.
4. **Decision-Making:** A final decision-maker agent synthesizes the low-complexity direct answer, the moderate-complexity interaction/conversation history, or the high-complexity accumulated reports into the final answer, using ensemble techniques (e.g., temperature ensembling) for robustness.

**Agent roles:** Moderator (GP who triages complexity and oversees process), Recruiter (assembles expert team), General Doctor/Specialist agents (domain-specific or general physicians who reason individually or in a team).

**Models/Inference:** Entirely inference-time / prompting-based — no fine-tuning. Backbone models: GPT-4(V) for text/text+image benchmarks, Gemini-Pro(Vision) for the video+text benchmark (MedVidQA), and additional experiments with GPT-3.5 and GPT-4o-mini. Ablations add MedRAG (Retrieval-Augmented Generation over biomedical/clinical/general-medicine corpora) and an added "Moderator's Review" step for further accuracy gains.

## Datasets Used

- **MedQA:** 1,273 USMLE-style multiple-choice questions (5 options), English test set; low complexity, text-only.
- **PubMedQA:** Yes/No/Maybe QA grounded in PubMed abstracts (context minus conclusion); 500 total, 50 used for testing; low complexity, text-only.
- **DDXPlus:** ~134K synthetic patient records (age, sex, evidences, pathology) for differential diagnosis; text-only, multiple choice.
- **SymCat:** ~369K synthetic disease–symptom records enhanced via the NLICE method; text-only, multiple choice.
- **JAMA (Clinical Challenge):** 1,524 real-world challenging clinical case questions from the JAMA Network; text-only.
- **MedBullets:** 308 USMLE Step 2/3-style questions sourced from public tweets since April 2022; text-only.
- **Path-VQA:** 3,391 (yes/no subset used) pathology-image visual question-answer pairs; image+text.
- **PMC-VQA:** ~50K VQA pairs derived from images/text in scientific publications; image+text, multiple choice.
- **MedVidQA:** 155 (subset; full dataset 3,010) health-related video question pairs, augmented with GPT-4-generated multiple-choice distractors; video+text.
- **MIMIC-CXR (VQA):** 1,531 chest radiograph VQA pairs from a large-scale de-identified chest X-ray dataset; image+text.
- Sampling: 50 samples per dataset used for main experiments (Table 2); an additional experiment used N=100 samples with GPT-4o-mini (Table 12) and the full MedQA 5-option set (Table 5, D.1).

## Models / Technologies

- GPT-4(V) (primary backbone for most benchmarks)
- Gemini-Pro(Vision) (backbone for MedVidQA and robustness comparisons)
- GPT-3.5, GPT-4o-mini (additional backbone comparisons)
- MedRAG (Retrieval-Augmented Generation toolkit over biomedical/clinical/general medicine corpora; Xiong et al., 2024)
- Chain-of-Thought (CoT) and Self-Consistency (CoT-SC) prompting
- Ensemble Refinement (ER), Medprompt (prompting strategies)
- No fine-tuning, no BioBERT/Knowledge Graph/FAISS/vector DB described directly in the core framework (MedRAG internally handles retrieval but details of its retriever are external to this paper)
- No direct ClinicalTrials.gov API or PubMed eUtils integration (PubMedQA dataset uses pre-extracted PubMed abstracts, not live eUtils queries)

## Experimental Setup

- **Training:** None; fully prompting/inference-based (zero-shot/few-shot/CoT variants).
- **Evaluation:** Classification accuracy (%) across ten benchmarks, compared across three settings: Solo (single agent), Group (static multi-agent methods: Voting, MedAgents, Reconcile, AutoGen, DyLAN, Meta-Prompting), and Adaptive (MDAgents). All experiments run with 3 random seeds; accuracy reported as mean ± standard deviation.
- **Inference time (average):** Low complexity ~14.7s, Moderate ~95.5s, High ~226s per query.
- **API-call efficiency analysis:** Number of agents (N) varied from 2–7 in Group setting; Adaptive method achieved peak accuracy (83.5%) at N=3 with 9.3 average API calls, vs. Group's 20.3 calls (N=5) and Solo's 6.0 calls.
- **Robustness testing:** Performance evaluated under low (T=0.3) and high (T=1.2) temperature settings.
- **Hardware:** Not reported.
- **Cost estimation:** Full test-set cost estimates in USD reported for GPT-4(V) across datasets and methods (Table 6), e.g., total cost for MDAgents ≈ $172,704.33 vs. CoT baseline ≈ $58,871.29 across all datasets combined.

## Results

- MDAgents outperformed both Solo and Group baselines (p < 0.05) on 7 of 10 medical benchmarks (Table 2).
- Notable gains: DDXPlus — MDAgents 77.9% vs. best single-agent 72.7% (+5.2%) and best multi-agent 68.4% (+9.5%).
- SymCat: MDAgents 93.1% (best across all methods).
- MedBullets: MDAgents 80.8% vs. best baseline (MedAgents group) 77.0%.
- PMC-VQA (image+text): MDAgents 56.4% (best).
- MIMIC-CXR: MDAgents 55.9% (competitive/best among multi-agent methods).
- On the full MedQA 5-option dataset (GPT-4o-mini), MDAgents achieved 83.6% vs. best baseline (Reconcile) 80.2% (Table 5).
- Complexity-classification analysis: the LLM-as-classifier selects the empirically optimal complexity level for a given problem with estimated probability ≥ 80% (a = 0.81 ± 0.29).
- Ablations: adding MedRAG alone improved average accuracy from 71.8% to 75.2% (+4.7%); adding Moderator's Review alone raised it to 77.6% (+8.1%); combining both achieved 80.3% (+11.8%) (Table 3).
- Optimal number of agents in Group setting was N=3 (peak accuracy 83.5%), not the maximum tested — more agents did not monotonically improve performance.
- MDAgents showed improved robustness to temperature changes (better performance at higher temperature, T=1.2) compared to Solo/Group settings.
- Entropy analysis (Figure 7) showed consensus (entropy decline) among collaborating agents over discussion rounds across all data modalities, with text+video showing the fastest convergence.

## Strengths

- First framework to adaptively select collaboration structure (solo/MDT/ICT) based on automatically assessed task complexity, rather than a fixed architecture.
- Evaluated across ten diverse benchmarks spanning text-only, image+text, and video+text medical QA, providing broad evidence of generalizability.
- Demonstrates a favorable accuracy/efficiency trade-off (fewer API calls at comparable or higher accuracy vs. static Group methods).
- Rich ablations isolating the contributions of complexity classification, RAG augmentation, and moderator review.
- Publicly available code (GitHub) and detailed prompt templates (Appendix C) for reproducibility.
- Explicit human-physician validation study comparing LLM vs. physician complexity judgments, revealing an important limitation (low correlation) which future work — including MOSAIC — can address.

## Limitations

- LLM-vs-physician complexity classification showed only weak/low correlation (Pearson r ranging from –0.090 to 0.110 across models; Table 13), casting some doubt on how well "complexity" is truly captured relative to expert judgment, even though the ablation on optimal complexity selection (Section "Why Do Adaptive Decision-making Framework Work Well?") suggests the LLM implicitly finds a locally optimal complexity level.
- Framework is confined to multiple-choice QA and does not model the interactive, patient-centered, multi-turn nature of real clinical diagnosis (explicitly noted by authors as a limitation).
- Risk of medical hallucination and inaccurate information remains unaddressed by a dedicated correction mechanism (self-correction/RLHF-style fixes are proposed only as future work).
- High computational/API cost for the ICT (high-complexity) pathway, and overall higher total cost than single-prompt CoT baselines (Table 6).
- Physician inter-rater reliability on complexity itself was only "moderate" (ICC2k = 0.269, ICC3k = 0.280), indicating inherent subjectivity in the ground-truth complexity labels used for validation.
- No dedicated retrieval or knowledge-graph module in the core framework (MedRAG is treated as an add-on ablation, not integrated by default).

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** Primarily the Multi-Agent Architecture module and, secondarily, the Clinical Trial Matching / Eligibility Extraction reasoning layer, since MOSAIC will need to route queries of varying complexity (e.g., a simple eligibility lookup vs. a complex multi-condition patient-to-trial matching task) to differently sized reasoning pipelines.

**Exactly what we should implement:**
1. **Complexity-triage stage:** Implement a "Moderator" agent analogous to MDAgents' GP-moderator that classifies an incoming MOSAIC query (e.g., "find trials for patient X") into Low/Moderate/High complexity based on factors such as number of eligibility criteria, ambiguity of the condition, or number of candidate trials retrieved — before deciding whether to use a single retrieval+reasoning agent or a multi-agent MDT-style discussion among specialized retrieval/eligibility agents.
2. **Adaptive recruitment:** Reuse the recruiter pattern to dynamically instantiate: a single "Trial Matching Agent" for simple queries; a small MDT of role-specific agents (e.g., "Eligibility Parser," "PubMed Evidence Retriever," "Trial Ranker") for moderate queries; and a sequential ICT-style pipeline of report-generating agent teams for high-complexity queries (e.g., rare disease, multi-condition eligibility).
3. **Consensus/discussion mechanism with bounded rounds:** For moderate-complexity trial-matching disagreements (e.g., conflicting relevance judgments between a keyword-based filter agent and an LLM-based semantic matcher), adopt the multi-turn, multi-round discussion-with-moderator-feedback pattern, capped at R rounds, to reach consensus efficiently.
4. **Efficiency-aware evaluation:** Track number of API/tool calls per query (as MDAgents does) as a MOSAIC evaluation metric, and use the "optimal-N-agents" finding (fewer agents can outperform more) to guide MOSAIC's agent-count tuning rather than assuming "more agents = better."
5. **RAG integration as an add-on:** Following the MedRAG ablation, integrate PubMed/ClinicalTrials.gov retrieval explicitly as an augmentation to whichever MOSAIC agent needs grounding (e.g., the Eligibility Extraction agent), and evaluate its marginal accuracy contribution the same way (baseline vs. +RAG vs. +Review vs. +RAG+Review).

**What should NOT be copied:**
- The specific medical-QA benchmarks (MedQA, DDXPlus, JAMA, etc.) are not directly relevant to MOSAIC's clinical-trial-matching task and should not be used for evaluation, though the evaluation methodology (accuracy with error bars over multiple seeds) can be reused.
- The complexity-classification categories (Low/Moderate/High mapped to PCC/MDT/ICT) are specific to diagnostic decision-making and should be redefined for trial-matching/eligibility-extraction complexity (e.g., based on number of eligibility criteria, ambiguity of condition terms, or amount of retrieved evidence) rather than copied verbatim.
- Do not assume the LLM-based complexity classifier is well-calibrated against human expert judgment without validation — MOSAIC should run its own validation study (as MDAgents did with physicians) rather than trusting the classifier out of the box, given the paper's own reported low correlation with physician judgments.

**Possible improvements:**
- Combine MDAgents' adaptive complexity-triage idea with MetaGPT's structured document handoffs (from the MetaGPT.md notes) so that MOSAIC's MDT/ICT-style agents exchange structured eligibility/evidence documents rather than free-form dialogue, potentially reducing hallucination further.
- Extend the entropy-based consensus-tracking method (Appendix B) as a real-time signal to decide when to terminate multi-agent discussion in MOSAIC's trial-matching MDT, rather than using a fixed round cap.
- Since MDAgents found human-LLM complexity agreement to be weak, MOSAIC could validate its complexity classifier against clinical-research-coordinator judgments specifically for trial eligibility complexity, and iterate on the classifier prompt accordingly.

## Personal Notes

