# GeneGPT

## Basic Information

- **Title**: GeneGPT: augmenting large language models with domain tools for improved access to biomedical information
- **Authors**: Qiao Jin, Yifan Yang, Qingyu Chen, Zhiyong Lu
- **Year**: 2024
- **Venue**: Bioinformatics, 40(2), btae075 (Oxford University Press)
- **DOI**: 10.1093/bioinformatics/btae075
- **Official DOI Link**: https://doi.org/10.1093/bioinformatics/btae075
- **Official Publisher Link**: https://academic.oup.com/bioinformatics/article/40/2/btae075/7606338
- **GitHub Repository**: https://github.com/ncbi/GeneGPT
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Not reported
  - AACT: Not reported
  - PubMed: Not directly (NCBI databases used are gene, snp, omim, nt — not PubMed literature itself)
  - PubMed eUtils: Yes — E-utils (Entrez Programming Utilities) is a core tool used, providing access to 38 NCBI databases (esearch, efetch, esummary functions)
  - Other: GeneTuring benchmark (Hou and Ji 2023) — 12 genomics QA tasks, 9 used in this paper; GeneHop — a novel multi-hop QA dataset introduced by this paper (3 tasks, 50 questions each); NCBI BLAST URL API (nt database)

## Research Category

Medical Retrieval; Clinical NLP (biomedical/genomics question answering via tool augmentation)

## Research Problem

Large language models (LLMs) are prone to hallucination because auto-regressive generation has no intrinsic mechanism to "consult" a source of truth, which is especially problematic for data-intensive genomics questions requiring precise retrieval/recitation of database entries (e.g., gene locations, SNP associations) — tasks where even LLMs augmented with generic retrieval (e.g., search engines) fail, since specialized biomedical databases are not indexed by commercial search engines.

## Motivation

LLMs achieve strong general-domain and some domain-specific performance (e.g., clinical trial matching, biomedical QA) but cannot reliably access authoritative structured biomedical data through pretraining alone. Prior work explored augmenting LLMs via retrieval-augmented generation (conditioning on retrieved text) or tool augmentation (calling external program APIs), but no prior study had taught an LLM to directly use NCBI's Web APIs (which provide programmatic access to NCBI's full suite of biomedical databases and the BLAST alignment tool) via in-context learning.

## Objective

Teach an LLM (via in-context learning, no fine-tuning) to directly generate and execute NCBI Web API request URLs (E-utils and BLAST) to answer genomics questions accurately, and evaluate this approach (GeneGPT) on the GeneTuring benchmark plus a newly introduced multi-hop QA dataset (GeneHop).

## Proposed Method

GeneGPT has two main components:

1. **Prompt design for in-context learning**: A single fixed prompt (prepended to every task-specific test question) consisting of: (i) an instruction describing the overall task ("use NCBI APIs to answer genomic questions"); (ii) API **documentations** — natural-language descriptions of E-utils (Dc.1: gene/snp/omim databases, esearch/efetch/esummary functions) and BLAST (Dc.2: nt database, blastn function); (iii) API **demonstrations** — four manually written worked examples (Dm.1 Alias: gene esearch→efetch; Dm.2 Gene SNP: snp esummary; Dm.3 Gene disease: omim esearch→esummary; Dm.4 Alignment: nt blastn), with API URLs and results marked by "[...]" and a "->" symbol indicating an API call; (iv) the task-specific test question appended at the end.
2. **Inference algorithm**: The concatenated prompt+question is fed to Codex (`code-davinci-002`) at temperature 0. Generation is interrupted whenever the "->" token is produced; the last generated URL is extracted, the corresponding NCBI Web API (E-utils or BLAST) is called via Python's `urllib`, and the raw result is appended back into the generation context before continuing. Generation stops when the answer-indicator token "\n\n" appears, and the text after "Answer:" is extracted as the final answer.

Two prompt variants are compared: **GeneGPT-full** (all documentation + all 4 demonstrations) and **GeneGPT-slim** (only Dm.1 and Dm.4, found via ablation to be sufficient and to generalize better). Two additional implementation variants: **GeneGPT-turbo** (Codex replaced by `gpt-3.5-turbo-16k-0301`) and **GeneGPT-lang** (same NCBI tool set wrapped in LangChain's ReAct agent framework instead of the custom inference algorithm).

## Datasets Used

- **GeneTuring** (Hou and Ji 2023): 12 genomics QA tasks × 50 question-answer pairs each; this paper uses 9 NCBI-resource-related tasks grouped into four modules: Nomenclature (gene alias, gene name conversion), Genomic location (gene SNP association, gene location, SNP location), Functional analysis (gene disease association, protein-coding genes), Sequence alignment (DNA to human genome, DNA to multiple species).
- **GeneHop** (novel dataset introduced in this paper): 3 multi-hop QA tasks × 50 questions each — (i) SNP gene function (function of the gene associated with a given SNP), (ii) Disease gene location (chromosome locations of genes associated with a given disease), (iii) Sequence gene alias (aliases of the gene containing a specific DNA sequence). Built from the GeneTuring benchmark; collection pipeline detailed in the paper's Supplementary Appendix C.

## Models / Technologies

- Codex (`code-davinci-002`) — primary backbone LLM, chosen for strong code understanding and an 8K-token context window
- `gpt-3.5-turbo-16k-0301` — alternative backbone (GeneGPT-turbo)
- LangChain ReAct agent framework (GeneGPT-lang)
- NCBI E-utils (Entrez Programming Utilities) — esearch, efetch, esummary functions over gene, snp, omim, nt databases
- NCBI BLAST URL API — blastn function over the nt database
- Baselines: GPT-2, BioGPT, BioMedLM (PubMedGPT), GPT-3 (`text-davinci-003`), ChatGPT, New Bing (retrieval-augmented)

## Experimental Setup

- Evaluation performed with automatic exact-match scoring (stricter than the original GeneTuring paper's manual evaluation), with minor allowances: vocabulary mapping for yes/no→TRUE/NA and Latin↔informal species names; partial credit (0.5) for correct chromosome but incorrect position in the DNA-to-human-genome task (since no reference genome was specified); recall-based scoring (exact gene matches) for the gene disease association task.
- Four GeneGPT settings compared: -full, -slim, -turbo (Codex→gpt-3.5-turbo-16k), -lang (LangChain ReAct implementation).
- Ablation study: each prompt component (Dc.1, Dc.2, Dm.1–4) removed individually from GeneGPT-full to measure its contribution.
- Probing study: GeneGPT evaluated using only one prompt component at a time, to assess individual component sufficiency.
- Multi-hop evaluation on GeneHop compared GeneGPT against New Bing only (the only baseline capable of answering single-hop GeneTuring questions reasonably well), using manual evaluation criteria detailed in Supplementary Appendix D.
- Manual error analysis classified all GeneGPT mistakes into five types: E1 (wrong/no API used), E2 (right API, wrong arguments), E3 (right API/result but failed to extract the answer), E4 (right API call but answer not present in results — task genuinely unanswerable via NCBI databases), and O (other/unclassified).

## Results

- GeneGPT achieves an overall average score of 0.83 (GeneGPT-slim) / 0.80 (GeneGPT-full) across the 9 GeneTuring tasks — a large margin over the previous SOTA, New Bing (0.44), and far surpassing GPT-3 (0.16), ChatGPT (0.12), BioMedLM (0.08), and BioGPT (0.04).
- Task-module breakdown (GeneGPT-slim vs. New Bing): Nomenclature 0.92 vs. 0.76; Genomic location 0.88 vs. 0.21; Functional analysis 0.84 vs. 0.91 (New Bing wins here, likely due to Bing indexing many gene-function web pages); Sequence alignment 0.66 vs. 0.00 (New Bing essentially fails, since raw DNA sequences are not indexed by search engines but are trivial for the BLAST tool).
- GeneGPT-turbo (gpt-3.5-turbo-16k backbone) achieves comparable overall performance (0.78 vs. 0.83), showing the approach transfers across backbones. GeneGPT-lang (LangChain ReAct) scores lower (0.54) mainly due to E1 errors on gene name conversion, but still outperforms New Bing by 22%.
- Ablation: removing the BLAST demonstration (Dm.4) significantly hurts only the two alignment tasks; most other component removals affect only one relevant task, indicating redundancy among prompt components.
- Probing: using only Dm.1 (Alias demonstration) alone performs comparably to GeneGPT-full on all tasks except alignment; using only Dm.4 (Alignment demonstration) alone handles the two alignment tasks well — together these two demonstrations (GeneGPT-slim) are sufficient for near-full performance, indicating strong cross-task generalizability of API demonstrations (more so than documentations, which fail alone).
- GeneHop (multi-hop): GeneGPT achieves an average score of 0.50 vs. 0.24 for New Bing; GeneGPT successfully decomposes multi-hop questions into API-call chains (up to 3 sub-questions / 4 API calls, longer than any single in-context demonstration), sometimes discovering shortcuts (e.g., reusing an ID from a prior API result to skip a redundant esearch call) not explicitly shown in the prompt.
- Error analysis: different tasks show enriched error types — simple tasks (alias, location) fail mostly via E4 (unanswerable via NCBI databases); E1 (wrong API) occurs almost only in disease-related tasks; alignment tasks show more "other" (O) errors tied to BLAST interface/reference-genome issues; multi-hop GeneHop tasks show more E2/E3 (argument and comprehension) errors in the reasoning chain.

## Strengths

- Achieves large, consistent SOTA improvements over both general-purpose LLMs and retrieval-augmented baselines (New Bing) across nearly all evaluated tasks, using in-context learning only (no fine-tuning).
- Requires no task-specific training — a model-agnostic augmentation strategy that generalizes across backbone LLMs (Codex, GPT-3.5-turbo) and orchestration frameworks (custom algorithm, LangChain ReAct).
- Demonstrates genuine multi-hop chain-of-thought tool use, generalizing to longer API-call chains than shown in any in-context demonstration, including a self-discovered "shortcut" reasoning pattern.
- Clear, reproducible open-source release (code and data publicly available).
- Systematic ablation/probing/error analysis provides actionable insight into which prompt components matter and why (demonstrations > documentations).

## Limitations

- Scope is bounded by what NCBI Web APIs can directly answer or what can be decomposed into single-hop sub-questions answerable by those APIs — genuinely NCBI-unanswerable questions (E4 errors) cannot be fixed by better prompting.
- Relies on Codex (`code-davinci-002`), a deprecated/retired OpenAI model at the time of publication review, raising reproducibility concerns for future replication with the exact backbone.
- Evaluation, while more rigorous (automatic, strict exact-match) than the original GeneTuring paper, may undercount answers that are correct but phrased differently (e.g., position-mapping partial credit was a necessary workaround due to unspecified reference genomes).
- GeneHop, while useful, is a relatively small, newly introduced benchmark (150 questions total) that would benefit from further diversification and larger-scale validation.
- LangChain ReAct implementation (GeneGPT-lang) underperforms the custom inference algorithm, suggesting off-the-shelf agent frameworks may need task-specific tuning to match a purpose-built approach.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: Any module that needs to query structured NCBI/genomics resources programmatically as part of a broader clinical trial or biomedical knowledge pipeline — e.g., an eligibility-criteria enrichment agent that needs gene/SNP/disease facts, or a PubMed-eUtils-based retrieval agent (this paper is essentially the reference architecture for teaching an LLM to call E-utils and related APIs directly).
- **What to implement**: The prompt-design pattern of instruction + API documentation + few concrete worked demonstrations (with explicit "->" markers separating a generated API call from its injected result) as a lightweight, fine-tuning-free way to teach any MOSAIC agent to call PubMed eUtils / ClinicalTrials.gov APIs; the "decode-until-API-marker, execute, inject result, continue" inference loop as a general pattern for tool-augmented agents; the demonstrated multi-hop chain-of-thought decomposition capability, which suggests MOSAIC agents could similarly decompose complex trial-matching or eligibility questions into sequential API calls without needing to hard-code every possible chain.
- **What should NOT be copied**: Direct dependence on the deprecated Codex model — MOSAIC should use a current-generation LLM with equivalent or better code/API-call generation ability; the GeneTuring/GeneHop task scope itself (gene/SNP/disease-focused) is not directly MOSAIC's domain (clinical trial matching/eligibility), though the tool-augmentation technique transfers.
- **Possible improvements**: Extend the same in-context "documentation + demonstration" prompting pattern from NCBI E-utils to PubMed eUtils and the ClinicalTrials.gov API specifically for MOSAIC's retrieval agent; incorporate the paper's ablation finding (demonstrations matter more than documentation) when designing MOSAIC's own tool-use prompts, favoring a small number of well-chosen worked examples over verbose API documentation.

## Personal Notes

