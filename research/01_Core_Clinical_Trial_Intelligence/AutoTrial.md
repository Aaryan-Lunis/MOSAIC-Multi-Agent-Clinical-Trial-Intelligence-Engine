# AutoTrial

## Basic Information

- **Title**: AutoTrial: Prompting Language Models for Clinical Trial Design
- **Authors**: Zifeng Wang, Cao Xiao, Jimeng Sun
- **Year**: 2023
- **Venue**: Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023), pages 12461–12472
- **DOI**: Not reported
- **Official DOI Link**: Not reported
- **Official Publisher Link**: Not reported
- **GitHub Repository**: Not reported
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Yes — 75,977 clinical trials extracted and filtered (valid interventions, diseases, titles, non-void eligibility criteria)
  - AACT: Not reported
  - PubMed: Not reported
  - PubMed eUtils: Not reported
  - Other: Clinical Trial Parser (FAIR, 2022) used to extract 751,258 medical relations from eligibility criteria

## Research Category

Clinical NLP; Core Clinical Trial Intelligence (trial design / eligibility criteria generation)

## Research Problem

Constructing appropriate eligibility criteria for clinical trials is essential to trial success but difficult even for experienced professionals — around 57% of trial protocols require at least one substantial amendment to eligibility criteria, causing large financial losses and delays. The paper addresses how to automatically generate high-quality, controllable eligibility criteria text.

## Motivation

Prior work in clinical trial design NLP focused on trial feature embedding or trial design evaluation, not on generation/automation. LLMs have shown they can act as implicit knowledge bases, but generating clinical trial criteria requires: (1) comprehending trial-specific instructions, (2) referencing prior/precedent trials for context, and (3) producing rationales so clinical experts can understand and trust the output. No existing work addressed clinical trial design automation directly.

## Objective

Develop a language-model-based method (AutoTrial) that generates eligibility criteria under controllable instructions, incorporates knowledge from precedent trials scalably, and produces explicit reasoning chains for its outputs.

## Proposed Method

AutoTrial uses a decoder-based causal language model (GPT-2 backbone) trained in two stages:

- **Pretraining**: On a large unlabeled corpus of trial documents, the model learns to reason through multiple steps and mimic retrieved in-context criteria exemplars, using special tokens (`<inc>`, `<exc>`) to mark step-by-step reasoning toward a target criterion.
- **Finetuning**: The model is trained to generate a target criterion given trial setup + instruction (e.g., `<age>`, `<bmi>`, `<nyha>`) using a combination of MLE loss and a token-level contrastive loss.

**Hybrid prompting**:
- *Discrete prompt*: Trial Setup (title/disease/treatment wrapped in special tokens) + In-context Exemplar (retrieved reasoning chain of prior criteria, targeting instruction, and target criterion, stored in an external knowledge store keyed by Trial2Vec embeddings of trial setups) + Textual Instruction (the specific criterion type requested).
- *Neural prompt*: A trainable embedding matrix maps each instruction type to a continuous prompt vector (via MLP), prepended to the input; new instructions can be added by extending this embedding matrix without retraining the rest of the model (mitigating catastrophic forgetting).

**Generation**: Top-k sampling produces diverse candidate criteria; candidates are encoded via Trial2Vec, clustered with k-means, and the lowest-perplexity candidate per cluster is retained as the final output set.

## Datasets Used

- 75,977 clinical trials from ClinicalTrials.gov with valid interventions/diseases/titles and non-empty eligibility criteria.
- Clinical Trial Parser (FAIR, 2022) extracted 751,258 medical relations from eligibility criteria for training/evaluation.
- Train/valid/test split: 54,703 / 6,079 / 15,195 trials (153,169/17,145/42,269 inclusion criteria; 128,310/14,581/35,247 exclusion criteria).
- Pretraining set: 2,528,231 unique instruction-criterion training samples drawn from ~400K trials (validation/test trials excluded from pretraining).

## Models / Technologies

- GPT-2 (primary backbone) and T5 (compared backbone)
- Trial2Vec (external encoder for trial-setup embeddings and knowledge-store retrieval, and for clustering generated candidates)
- Prefix-tuning (PT), Retrieval-Augmented Generation (RAG), SimCTG (contrastive search) as comparison methods
- GPT-3.5 (as a general-LLM comparison baseline via human evaluation)
- Clinical Trial Parser (FAIR) for clinical relation extraction and accuracy scoring

## Experimental Setup

- Pretraining: batch size 64, learning rate 5e-5, weight decay 1e-4, 5 epochs.
- Finetuning: batch size 16, learning rate 5e-5, weight decay 1e-5, 10 epochs.
- Evaluated at both criteria-level (single criterion generation) and trial-level (all criteria at once).
- Automatic NLG metrics: BLEU-1, METEOR, ROUGE-L, CIDEr.
- Clinical accuracy: precision, recall, F1, Jaccard similarity of extracted medical relations vs. ground truth (via Clinical Trial Parser).
- Human evaluation: domain experts compared AutoTrial vs. GPT-3.5 (zero-shot, 1-shot, 5-shot) outputs, computing winning rate.
- Ablation studies on multi-step reasoning supervision (MSR), RAG, and neural prompting; incremental-learning experiments (Re-train vs. Incremental variants across 4 sequential data subsets).
- Hardware: not reported.

## Results

- Trial-level automatic metrics: AutoTrial achieves BLEU-1 58.7 / METEOR 40.8 / ROUGE-L 40.6 / CIDEr 0.24 for inclusion criteria and BLEU-1 54.4 / METEOR 36.3 / ROUGE-L 35.3 / CIDEr 0.33 for exclusion criteria, outperforming all GPT-2/T5-based baselines (FT, RAG, PT, SimCTG).
- Clinical accuracy: AutoTrial is the only method with recall >0.5, F1 >0.6, and Jaccard >0.4 for inclusion criteria (P=0.91, R=0.92, F1=0.91, Jaccard=0.84); similarly strong margin for exclusion criteria (P=0.85, R=0.89, F1=0.87, Jaccard=0.76).
- Human evaluation: AutoTrial wins over GPT-3.5 in over 60% of cases across zero-shot, 1-shot, and 5-shot GPT-3.5 settings; notably, 5-shot GPT-3.5 performed worse than zero-shot/1-shot GPT-3.5.
- Incremental learning: the Incremental variant approaches the performance of full Re-training until new instructions reach roughly 3x the volume of the last full retrain, after which a full retrain is recommended.
- Ablation: removing RAG or neural prompting significantly hurts performance; removing multi-step reasoning supervision (MSR) has mixed effects but is retained for interpretability and balance across inclusion/exclusion criteria.

## Strengths

- Achieves clinical accuracy far above baselines with a much smaller model than GPT-3.5.
- Controllable, instruction-driven generation across many criterion types.
- Supports incremental updates to new instructions/trials without full retraining.
- Provides explicit reasoning chains, aiding interpretability and clinician trust.

## Limitations

- Performance depends on the quality of training data; biases/inaccuracies in the clinical trial database propagate to generated criteria.
- Does not account for unexpected or rare side effects/issues that may emerge during a trial.
- Should be used only as a supportive design aid — final decisions must remain with human clinicians.
- Exclusion-criteria generation is somewhat weaker than inclusion-criteria generation, attributed to ordering/truncation effects in training data and autoregressive error accumulation.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: The eligibility-criteria generation / trial-design-assistance module.
- **What to implement**: Hybrid discrete + neural prompting for controllable, instruction-specific criterion generation; an external knowledge store of exemplar criteria retrieved via trial-embedding similarity (reusing a Trial2Vec-style encoder); multi-step "reasoning-then-answer" pretraining objective; incremental-learning strategy (freeze base model, only update new instruction embeddings) for adding new criterion types over time without full retraining.
- **What should NOT be copied**: The GPT-2-scale backbone (a modern instruction-tuned LLM would likely perform better); the specific reliance on the FAIR Clinical Trial Parser for scoring, unless that exact tool is replicated in MOSAIC's pipeline.
- **Possible improvements**: Replace the GPT-2 backbone with a modern LLM while keeping the hybrid prompting scheme; connect the knowledge-store retrieval directly to MOSAIC's own clinical trial vector database (e.g., built via Trial2Vec) rather than a separate store; extend incremental-learning approach to support continuous updates as new ClinicalTrials.gov data arrives.



