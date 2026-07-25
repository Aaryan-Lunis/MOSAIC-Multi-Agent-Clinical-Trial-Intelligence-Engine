# Trial2Vec

## Basic Information

- **Title**: Trial2Vec: Zero-Shot Clinical Trial Document Similarity Search using Self-Supervision
- **Authors**: Zifeng Wang, Jimeng Sun
- **Year**: 2022
- **Venue**: Findings of EMNLP 2022 (arXiv:2206.14719v2 [cs.CL])
- **DOI**: Not reported
- **Official DOI Link**: Not reported
- **Official Publisher Link**: Not reported (arXiv preprint: https://arxiv.org/abs/2206.14719)
- **GitHub Repository**: https://github.com/RyanWangZf/Trial2Vec
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Yes — ~400k trials total; 311,485 interventional trials kept for retrieval evaluation; 240k trials for outcome prediction
  - AACT: Not reported
  - PubMed: Not reported
  - PubMed eUtils: Not reported
  - Other: Medical Encyclopedia (MedlinePlus, ~4K articles), Wikipedia articles (for ~4k terminologies), UMLS knowledge base (for medical entity linking/negative sampling)

## Research Category

Medical Retrieval; Core Clinical Trial Intelligence (trial similarity search)

## Research Problem

Studying similar historical trials is valuable when designing a new clinical trial, but accurate similarity search over lengthy trial documents (avg. 622.4 words/trial) is difficult, and there is a lack of labeled data for training supervised retrieval models.

## Motivation

Existing zero-shot BERT-based retrieval methods (e.g., SimCSE-style contrastive learning) are designed for short sentences (usually <10 words) and degrade badly on long documents when embeddings are produced via naive truncation/averaging. Simple instance-discriminative contrastive learning also requires large batch sizes and long training — infeasible for long clinical trial documents. No prior work addressed trial-to-trial retrieval directly with a label-free approach.

## Objective

Develop a zero-shot, self-supervised method that produces compact, medically meaningful embeddings of whole clinical trial documents by exploiting the documents' meta-structure (title, disease, intervention, outcome, context) and external medical knowledge (UMLS), enabling trial-to-trial and query-to-trial similarity search without labeled data.

## Proposed Method

- **Backbone encoder (TrialBERT)**: BioBERT weights, continued pretraining with Masked Language Modeling (MLM) on three corpora: ClinicalTrials.gov (240M words), Medical Encyclopedia (3M words), Wikipedia articles (11M words).
- **Hierarchical embeddings**: Trial attributes are split into "key attributes" (title, intervention, condition, main outcome measure) and "context" (descriptions, eligibility criteria, references, etc.). Local attribute embeddings are produced per key attribute via TrialBERT; a context embedding is produced from the context text. Local embeddings are refined and aggregated into a single global trial embedding via multi-head attention conditioned on the context embedding.
- **Hierarchical contrastive learning**:
  - *Global contrastive loss*: Meta-structure-guided negative sampling — e.g., swap a trial's title with another trial's title that shares the same target disease, forcing the model to discriminate subtle attribute differences; positive samples are built via random attribute dropout. Optimized with InfoNCE loss.
  - *Local contrastive loss*: Medical entities are extracted from each attribute text (via SciSpacy) and linked to UMLS; positives replace an entity with its canonical name or a semantically similar parent-concept entity, negatives use deletion/replacement with dissimilar entities. Optimized with InfoNCE loss.
  - Final loss = global loss + local loss.
- **Applications**: complete trial-trial similarity search, partial/query-based trial search (using only title, keywords, intervention, or disease as query), trial topic visualization (t-SNE), and downstream trial outcome/termination prediction (fine-tuned classifier head on global embeddings).

## Datasets Used

- ClinicalTrials.gov: ~400k trials total; 311,485 interventional trials retained for the retrieval experiments.
- Labeled trial similarity dataset: 160 uniformly sampled query trials, each paired with TF-IDF top-10 candidate trials, labeled relevant/not-relevant by domain experts (clinical informatics researchers) — 1,600 labeled trial pairs total, using the guideline: relevant if (1) same disease, or (2) same intervention and similar diseases.
- Trial outcome (termination) prediction dataset: 240k trials, with 210,411 completion-labeled and 34,305 termination-labeled trials (Approved/Completed = completion; Suspended/Terminated/Withdrawn = termination); 70/20/10 train/test/validation split.
- Table 6 pretraining corpus stats: ClinicalTrials.gov 240M words, Medical Encyclopedia 3M words, Wikipedia Articles 11M words.

## Models / Technologies

- BERT / BioBERT (backbone), TrialBERT (continued MLM pretraining)
- UMLS knowledge base, SciSpacy (entity extraction and linking)
- Multi-head attention (for local-to-global embedding aggregation)
- InfoNCE contrastive loss
- t-SNE (embedding visualization)
- Baselines: TF-IDF, BM25, Word2Vec, BERT, BERT-Whitening, BERT-SimCSE, MonoT5-Med

## Experimental Setup

- Hardware: 6 × RTX 2080 Ti GPUs.
- TrialBERT continued pretraining: 5 epochs, batch size 100, learning rate 5e-5.
- Second-stage SSL training: AdamW optimizer, learning rate 2e-5, batch size 50, weight decay 1e-4.
- Embedding dimension kept at 768 for all compared methods (with an ablation across 128/256/512/768).
- Retrieval evaluation metrics: Precision@k, Recall@k (k=1,2,5), nDCG@5.
- Outcome prediction evaluation metrics: Accuracy (ACC), ROC-AUC, PR-AUC.
- Ablation studies isolate contribution of attribute-matching contrastive loss (att mc), context-matching contrastive loss (ctx mc), and local/semantic-matching contrastive loss (semantic mc).

## Results

- Complete trial similarity search: Trial2Vec achieves Prec@1 0.881, Prec@5 0.506, Rec@5 0.647, nDCG@5 0.883 — approximately 15% average improvement over the best baselines (which cluster closely together, e.g., BERT-Whitening nDCG@5 0.813).
- Partial/query retrieval: using only the title is already comparable to the best full-document baseline; combining title + disease performs similarly to using all attributes; adding keywords or intervention to the title actually reduces performance.
- Ablation: removing the context-matching contrastive task (ctx mc) causes the largest performance drop; all three tasks (att mc, ctx mc, semantic mc) contribute positively.
- Embedding dimension: performance is largely stable from 768 down to 128, allowing substantial storage/compute savings.
- Trial outcome (termination) prediction after fine-tuning: Trial2Vec achieves ACC 0.862, ROC-AUC 0.733, PR-AUC 0.314, outperforming TF-IDF, Word2Vec, and plain TrialBERT.
- Embedding visualization (t-SNE): trials cluster into medically coherent disease groups (e.g., cancers of different organs cluster together; brain-related diseases cluster together).
- Case studies: Trial2Vec retrieves top-1 trials with matching drug/intervention and clinical purpose, where TF-IDF and TrialBERT baselines retrieve topically similar but clinically irrelevant trials (attention biased toward frequent surface words).

## Strengths

- Fully zero-shot / self-supervised — no labeled trial-pair data needed for training.
- Explicitly designed to handle long documents via hierarchical meta-structure encoding, avoiding the semantic-vanishing problem of naive average pooling.
- Produces medically interpretable embeddings (validated via visualization and case studies).
- Supports partial-attribute (query) search in addition to full-document search.
- Embeddings transfer well to a downstream predictive task (trial termination) after fine-tuning.

## Limitations

- Evaluated only on English-language ClinicalTrials.gov documents; applicability to other languages not established.
- The labeled relevance dataset (1,600 pairs) may not cover all cases, despite careful construction.
- Can still retrieve incorrect/irrelevant trials in failure cases; the paper explicitly recommends use under supervision of professional clinicians rather than as a sole decision tool.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: The trial embedding / vector database and trial-similarity-search module — this is a core building block for RAG over ClinicalTrials.gov data, and is also directly referenced/reused by AutoTrial as its exemplar-retrieval encoder.
- **What to implement**: The TrialBERT continued-pretraining recipe (BioBERT + MLM on ClinicalTrials.gov/medical corpora); the hierarchical local-attribute + global-context embedding architecture; the two-part contrastive learning scheme (meta-structure-based global loss + UMLS-guided local/entity loss) to produce a reusable trial embedding for a FAISS/vector-DB-backed retrieval component; support for partial-attribute ("query-trial") search.
- **What should NOT be copied**: The specific 1,600-pair relevance-labeled evaluation set (small, dataset-specific, not something to depend on for production evaluation); the fixed 768-dim embedding assumption without re-validating on MOSAIC's own corpus.
- **Possible improvements**: Swap BioBERT/TrialBERT for a more modern biomedical encoder; extend the knowledge base beyond UMLS (e.g., integrate a broader knowledge graph); combine with PubMed-derived literature embeddings to unify trial and publication retrieval in one MOSAIC vector space.



