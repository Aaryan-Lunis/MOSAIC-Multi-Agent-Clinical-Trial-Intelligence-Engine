# MetaGPT

## Basic Information

- **Title:** MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework
- **Authors:** Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, Jürgen Schmidhuber
- **Year:** 2024 (arXiv preprint originally posted 2023; ICLR 2024 camera-ready cited "1 Nov 2024" arXiv version)
- **Venue:** ICLR 2024 (International Conference on Learning Representations), published as a conference paper
- **DOI:** Not reported in the provided document
- **Official DOI Link:** Not reported
- **Official Publisher Link:** Not reported (arXiv version: arXiv:2308.00352v7 [cs.AI])
- **GitHub Repository:** https://github.com/geekan/MetaGPT
- **Dataset(s) Used:**
  - ClinicalTrials.gov: No
  - AACT: No
  - PubMed: No
  - PubMed eUtils: No
  - Other: HumanEval (164 handwritten Python programming tasks), MBPP (427 Python tasks), SoftwareDev (self-generated benchmark of 70 representative software development tasks)

## Research Category

- Multi-Agent Architecture
- Core Clinical Trial Intelligence: Not applicable (this is a general-purpose software engineering multi-agent framework, not medical/clinical)

## Research Problem

Existing LLM-based multi-agent systems can handle simple dialogue tasks but struggle with complex, real-world problem solving because naively chaining LLMs together causes logic inconsistencies from cascading hallucinations. Multi-agent systems built on unconstrained natural-language dialogue between agents ("chit-chat") lose information across turns (analogous to the "telephone game"), and prior frameworks lack standardized, verifiable intermediate outputs, leading to inefficient collaboration and unreliable results, particularly in software engineering tasks.

## Motivation

Human teams rely on Standardized Operating Procedures (SOPs) to decompose complex work, assign role-specific responsibilities, and define quality standards for intermediate outputs (e.g., a Product Manager in a software company producing a Product Requirement Document that guides an Architect and Engineers). Existing LLM multi-agent frameworks (e.g., CAMEL, ChatDev) had not fully exploited such structured, human-inspired workflows, instead relying on free-form dialogue, which increases ambiguity, redundant "chit-chat," and hallucination risk. There was a gap in frameworks that combine role specialization with structured, document-based communication.

## Objective

To design a meta-programming framework, MetaGPT, that encodes SOPs into prompt sequences for LLM-based agents, enabling agents with human-like domain expertise (Product Manager, Architect, Project Manager, Engineer, QA Engineer) to collaboratively and reliably transform a one-line natural language requirement into complete, executable software, while reducing hallucination and improving software development benchmark performance (HumanEval, MBPP, SoftwareDev).

## Proposed Method

**Architecture / Roles:** MetaGPT simulates a software company with five specialized agent roles: Product Manager, Architect, Project Manager, Engineer, and QA Engineer. Each agent has a defined profile (name, goal, constraints) and tool access (e.g., Product Manager can use web search tools; Engineer can execute code).

**Workflow (SOP-based pipeline):**
1. Product Manager analyzes the user's one-line requirement and produces a Product Requirement Document (PRD) containing Product Goals, User Stories, Competitive Analysis (with a competitive quadrant chart), Requirement Analysis, and Requirement Pool.
2. Architect translates the PRD into a System Design: implementation approach, Python package name, file list, data structures/interface definitions (class diagrams), and a program call flow / sequence diagram.
3. Project Manager breaks the system design into a task list, analyzes required third-party packages, and produces a Logic Analysis assigning tasks to files.
4. Engineer(s) write code for each file/task based on the design and task list.
5. QA Engineer writes unit tests and performs code review to catch bugs.

**Communication Protocol:**
- *Structured Communication Interfaces:* Agents communicate via structured documents and diagrams rather than unconstrained natural-language dialogue (unlike ChatDev), reducing information loss analogous to the "telephone game."
- *Publish-Subscribe Mechanism:* A shared global message pool lets all agents publish and access structured messages; a subscription mechanism lets each agent retrieve only role-relevant information based on its profile, mitigating information overload.

**Iterative Programming with Executable Feedback:** After initial code generation, the Engineer agent executes the code and associated unit tests; if errors occur, the agent references PRD, system design, and code history in memory to debug and iterate, up to a maximum of 3 retries. This self-correction step is shown to materially improve code executability and reduce human revision cost.

**Models/Inference:** MetaGPT is LLM-agnostic in principle but primary experiments use GPT-4 (also tested with GPT-3.5 and DeepSeek Coder 33B as backends). No model training/fine-tuning is performed; the framework operates entirely via prompting, structured output formats, and executable feedback (inference-time only).

## Datasets Used

- **HumanEval:** 164 handwritten Python programming tasks with function specifications, descriptions, reference code, and tests. Used to evaluate Pass@1 code generation accuracy. Source: Chen et al., 2021a.
- **MBPP:** 427 Python tasks covering core programming concepts and standard library features, each with descriptions, reference code, and automated tests. Source: Austin et al., 2021.
- **SoftwareDev:** A self-generated benchmark of 70 representative software development tasks (e.g., mini-games, data visualization, image processing) with diverse scopes; 7 tasks used in main comparative experiments. Created by the authors specifically to test authentic, engineering-focused development tasks (not just isolated function generation). No external preprocessing described beyond task curation by the authors.

## Models / Technologies

- GPT-4 (primary backend LLM)
- GPT-3.5 (backend comparison)
- DeepSeek Coder 33B (open-source backend comparison)
- ReAct-style agent behavior (Yao et al., 2022) underlying agent action loops
- Structured communication interfaces (custom, not RAG/vector-DB based)
- Shared message pool with publish-subscribe mechanism (custom messaging architecture)
- Executable feedback / self-correction loop (code execution + unit testing)
- No BioBERT, no Knowledge Graph, no FAISS/vector database, no PubMed/ClinicalTrials.gov integration (not used in this paper)

## Experimental Setup

- **Training:** None — the framework is purely prompt-engineered and inference-time; no model fine-tuning.
- **Evaluation:** Pass@k metric (unbiased estimator per Chen et al., 2021a) on HumanEval and MBPP. For SoftwareDev, evaluation used a mix of human ratings (Executability score 1–4) and statistical analysis of Cost (running time, token usage, expense), Code Statistics (files, lines/file, total lines), Productivity (tokens per line of code), and Human Revision Cost (number of manual corrections, typically ≤3 lines per correction).
- **Baselines compared:** AlphaCode, Incoder, CodeGeeX, CodeGen, Codex, CodeT, PaLM Coder, GPT-4 (for HumanEval/MBPP); AutoGPT, LangChain (with Python REPL), AgentVerse, ChatDev (for SoftwareDev).
- **Hardware:** Not reported.

## Results

- HumanEval Pass@1: MetaGPT achieved 85.9% (new SOTA), vs. GPT-4 alone at 67.0%.
- MBPP Pass@1: MetaGPT achieved 87.7% (new SOTA).
- Executable feedback mechanism contributed a 4.2% (HumanEval) and 5.4% (MBPP) absolute Pass@1 improvement over MetaGPT without feedback.
- SoftwareDev benchmark: MetaGPT scored Executability 3.75 (near-flawless, scale 1–4) vs. ChatDev's 2.25; MetaGPT ran in 503–541s vs. ChatDev's 762s; MetaGPT achieved lower Productivity ratio (124.3–126.5 tokens/line vs. ChatDev's 248.9, lower is better); Human Revision Cost dropped to 0.83 vs. ChatDev's 2.5.
- MetaGPT achieved a 100% task completion rate in evaluations, and generated more code files/lines than comparable frameworks (avg. 5.1 files, 251.4 lines per task with feedback).
- Ablation on roles: adding Product Manager, Architect, and Project Manager roles beyond a lone Engineer improved executability from 1.0 to 4.0 and reduced human revisions from 10 to 2.5 (Table 3).
- Using GPT-4 as backend outperformed GPT-3.5 and DeepSeek Coder 33B in executability and revision cost (Table 5).

## Strengths

- Demonstrates state-of-the-art Pass@1 performance on two standard code-generation benchmarks using a training-free, prompting-based multi-agent framework.
- Structured, document-based inter-agent communication (PRD, system design, task lists) is directly analogous to structured artifacts (e.g., eligibility criteria documents, trial protocols) that could be reused for other structured-output multi-agent pipelines.
- Executable feedback / self-correction loop is a generalizable pattern for improving reliability of LLM-generated structured outputs beyond code (e.g., validating extracted eligibility criteria against source text).
- Explicit ablation studies isolate the contribution of each role and of the feedback mechanism, providing clear evidence for which design choices matter.
- Open-source GitHub repository available for direct architectural reference.

## Limitations

- Domain is software engineering, not biomedical/clinical — no direct handling of medical NLP, ClinicalTrials.gov, or PubMed data; nothing to adapt for retrieval directly.
- No fine-tuning or domain adaptation; heavily reliant on GPT-4's general capability, so performance may not transfer to specialized/technical domains like clinical trial matching without significant prompt/role redesign.
- Cannot fully address UI/frontend or multimodal scenarios per the authors' own stated limitations.
- Users cannot easily interrupt/checkpoint individual agents mid-run (human-in-the-loop control limitation).
- Self-improvement (learning across projects) is only an early/limited exploration (Appendix A.1), not a core validated contribution.
- No formal statistical significance testing reported for main benchmark comparisons (point estimates only in main tables, though some ablations report variability from repeated runs).

## How MOSAIC Can Reuse This Paper

**Which MOSAIC module benefits:** The Multi-Agent Architecture module of MOSAIC (the core multi-agent orchestration layer coordinating retrieval, eligibility extraction, and trial-matching agents) is the primary beneficiary.

**Exactly what we should implement:**
1. **Role specialization pattern:** Define MOSAIC-specific agent roles analogous to MetaGPT's (e.g., "Query Analyst" playing the Product Manager role to parse a patient/researcher query into a structured requirement; "Retrieval Architect" playing the Architect role to design the retrieval/knowledge-graph query plan; "Eligibility Engineer" agents that extract and code eligibility criteria; "QA/Verification Agent" that checks retrieved trial matches against source criteria).
2. **Structured communication over free dialogue:** Adopt document-based handoffs (e.g., a structured "Eligibility Requirement Document" analogous to the PRD) instead of unconstrained agent chit-chat, to reduce hallucination when agents pass information about trial eligibility or extracted PubMed evidence between each other.
3. **Shared message pool + subscription mechanism:** Implement a central message/blackboard store where all MOSAIC agents publish outputs (e.g., retrieved trial records, extracted criteria, retrieved literature snippets) and subscribe only to relevant upstream outputs, to prevent information overload as the number of retrieval/reasoning agents grows.
4. **Executable feedback / self-correction loop:** Adapt this pattern for verification — e.g., after an agent drafts a structured eligibility summary, have a verification step that checks the extracted criteria against the original ClinicalTrials.gov "eligibility" free-text field (analogous to code execution + unit tests), iterating up to a bounded number of retries if mismatches are found.

**What should NOT be copied:**
- The specific software-engineering roles (Product Manager, Engineer, QA Engineer) themselves — these must be redesigned entirely for the clinical trial/biomedical domain.
- The code-execution-based feedback mechanism cannot be directly reused (there is no "compiler" for clinical text); MOSAIC would need an analogous but different verification mechanism (e.g., cross-referencing structured extraction back to source text, or a rules/ontology-based checker).
- The HumanEval/MBPP/SoftwareDev benchmarks are irrelevant to MOSAIC and should not be used for evaluation.

**Possible improvements:**
- Combine MetaGPT's SOP-based structured handoff pattern with RAG so that each MOSAIC agent's structured output is grounded in retrieved PubMed/ClinicalTrials.gov evidence, not just prior agent outputs.
- Extend the "executable feedback" idea into a "retrieval-grounded feedback" loop, where an agent's extracted claim is automatically checked for support in the retrieved source document, iterating if unsupported (reducing hallucination in eligibility extraction).
- Log and analyze the "Human Revision Cost" style metric adapted to MOSAIC (e.g., number of manual corrections needed to a generated eligibility summary) as an evaluation metric for the capstone.

## Personal Notes

