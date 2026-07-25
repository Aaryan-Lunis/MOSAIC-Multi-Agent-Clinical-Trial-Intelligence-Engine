# PubMed Knowledge Graph 2.0 (PKG 2.0)

## Basic Information

- **Title**: PubMed knowledge graph 2.0: Connecting papers, patents, and clinical trials in biomedical science
- **Authors**: Jian Xu, Chao Yu, Jiawei Xu, Vetle I. Torvik, Jaewoo Kang, Mujeen Sung, Min Song, Yi Bu, Ying Ding
- **Year**: 2025
- **Venue**: Scientific Data, 12:1018
- **DOI**: 10.1038/s41597-025-05343-8
- **Official DOI Link**: https://doi.org/10.1038/s41597-025-05343-8
- **Official Publisher Link**: https://doi.org/10.1038/s41597-025-05343-8 (Nature Scientific Data)
- **GitHub Repository**: https://pubmedkg.github.io (dataset); https://github.com/dmis-lab/BERN2 (NER/NEN tool)
- **Dataset Availability**: Figshare — https://doi.org/10.6084/m9.figshare.26893861
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Yes — 480,795 clinical trial studies, one of the three core literature types
  - AACT: Yes — used for paper-clinical trial citation linkage via the URM trial-registration-number requirement
  - PubMed: Yes — entirety of PubMed papers (36,551,113 articles), the core dataset
  - PubMed eUtils: Not explicitly reported (PubMed XML files used directly for trial-registration linkage)
  - Other: USPTO/PatentsView (1,344,469 patents), NIH Exporter (2,023,148 projects), iCite, SciMago, iBKH, LAGOS-AND, Author-ity, Semantic Scholar, PCS dataset (patent-to-paper citations), SciSciNet (validation)

## Research Category

Core Biomedical Knowledge Graph Construction; Bibliometric/Scientometric Knowledge Graph; Multi-type Literature Linkage (papers, patents, clinical trials)

## Research Problem

Papers, patents, and clinical trials are stored in disparate databases with different data formats and management standards, making it difficult to form systematic, fine-grained connections among them. Prior knowledge graphs are either fine-grained but single-type (e.g., only clinical trials or only patents) or multi-type but coarse-grained (e.g., SciSciNet, Dimensions), lacking fine-grained, multi-perspective linkage across all three literature types.

## Motivation

Each literature type captures a different facet of the research lifecycle: papers provide theoretical/scientific narrative, patents provide commercialization/IP detail, and clinical trials provide regulatory/procedural detail — but each lacks what the others provide. Integrating all three via fine-grained entity-, citation-, and project-level links would enable more holistic scientometric analysis and knowledge-flow tracing (e.g., tracing how a clinical trial finding propagates into a paper and then a patent).

## Objective

Build PKG 2.0, a large-scale, fine-grained knowledge graph integrating the entirety of PubMed, all ClinicalTrials.gov studies, and biomedical-related USPTO/PatentsView patents, connected via biomedical entities, citations, and NIH-funded projects, with supplementary author/institution disambiguation and journal metrics.

## Proposed Method

Four main linkage mechanisms, each with its own extraction pipeline:

1. **Fine-grained knowledge-entity linkage**: BERN2 (a multi-task NER + normalization tool) extracts nine entity categories (gene/protein, disease, drug/chemical, species, mutation, cell line, cell type, DNA, RNA) from titles/abstracts of papers, trials, and patents. tmVar 2.0 handles mutation-type NER; BioSyn provides neural entity normalization for entities not covered by rule-based methods. The iBKH dataset is then used to map six relationship types (disease-drug, disease-disease, disease-gene, drug-drug, drug-gene, gene-gene) between the extracted entities.
2. **Citation linkage**: Paper-paper citations integrated from PubMed-provided data and the NIH Open Citation Collection (NIH-OCC); paper-patent citations from the PCS dataset (DOI-to-PMID mapping); paper-clinical trial citations from AACT (trial registration numbers embedded in PubMed XML, per Uniform Requirements for Manuscripts); patent-clinical trial citations extracted via regex-style pattern matching on "CT########" / "patent########" strings in citation text.
3. **Project linkage**: NIH Exporter data linked to papers, patents, and clinical trials via project/application IDs, enabling funding-to-output tracing.
4. **Author name disambiguation (AND)**: Combines the Author-ity dataset (primary AND_ID source, pre-2018) with Semantic Scholar's AND results (post-2018), reconciled via a trained DNN model (using author names, institutions, emails, countries, OpenAlex name variants, and title/abstract embeddings) when the two sources disagree. The same disambiguation model is extended to patent inventors and clinical trial investigators.

Supplementary/extended works: institution name disambiguation (via MapAffil for affiliation parsing + OpenAlex's MAG/ROR-trained classification models), author scientific metrics (publication counts, h-index), and annual journal metadata enrichment via SCImago (SJR, impact factor, h-index) linked by ISSN and publication year.

## Datasets Used

- **Core corpus**: 36,551,113 PubMed articles, 1,344,469 USPTO patents, 480,795 ClinicalTrials.gov studies, 26,217,594 disambiguated authors, 69,457 disambiguated institutions, 357,686 BioEntities, 21,382 journals, 2,023,148 NIH projects.
- **Relation counts**: 160,848,959 paper-author links; 774,810,780 paper-paper citations; 464,643,559 BioEntity-paper links; 11,416,614 BioEntity-clinical trial links; 6,469,587 BioEntity-patent links; 18,192,186 paper-patent citations; 967,719 paper-clinical trial citations; 53,424,596 author-PI links.
- **Validation datasets**: LAGOS-AND (author disambiguation ground truth), Matt's PCS dataset (paper-patent citation validation, 183 patents / 4,223 known-good PubMed rows), SciSciNet (paper-clinical trial citation cross-validation).

## Models / Technologies

- BERN2 (biomedical NER + normalization; multi-task learning model + tmVar 2.0 for mutations)
- BioSyn (neural entity normalization via synonym marginalization)
- iBKH (integrative Biomedical Knowledge Hub) for entity relation mapping
- Author-ity dataset + Semantic Scholar Academic Graph (S2AG), reconciled via a custom DNN (trained on LAGOS-AND)
- MapAffil (affiliation string parsing) + OpenAlex institution-disambiguation classifiers (trained on MAG + ROR data)
- NIH Open Citation Collection (NIH-OCC), PCS dataset (patent-to-paper citations)
- SCImago (SJR, impact factor, h-index by publication year)
- OMOP CDM / SNOMED CT / RxNorm / LOINC (used contextually via AACT/clinical concept mapping)

## Experimental Setup

- Author disambiguation validated against LAGOS-AND 2.0 (built on OpenAlex April 2022 baseline), reporting precision/recall/F1 for Author-ity alone, Semantic Scholar alone, and PKG's integrated approach.
- Paper-patent citation validated against Matt's PCS dataset at multiple confidence-level thresholds (1–10), computing precision (via 100-sample manual annotation per level) and recall (against 4,223 known-good PubMed rows).
- Paper-clinical trial citation cross-validated against SciSciNet's nct_id-to-paper linkages.
- Holistic validation: manual verification of 100 randomly sampled linkages per type (e.g., patent-project links checked against USPTO's "GOVERNMENT INTEREST" section) across five linkage types.
- Ablation-style evaluation of author disambiguation improvements from adding patent-based and clinical-trial-based features (Base group vs. Patent-based group vs. Trial-based group vs. Comprehensive group), reporting Precision/Recall/F1/Macro-F1.
- Case study: knowledge-flow tracing across the earliest ten BioNTech COVID-19 clinical trials, linking each to its earliest associated papers and patents on a timeline.

## Results

- Author disambiguation: PKG's integrated approach reached 98.45% precision / 94.10% recall / 96.24% F1, versus Author-ity alone (98.58% / 67.79% / 80.33%) and Semantic Scholar alone (98.53% / 86.55% / 92.15%) — substantially improving recall while preserving precision.
- Adding patent/clinical-trial features to author disambiguation improved Macro-F1 from 88.9% (baseline features) to 93.7% (comprehensive feature set).
- Paper-patent citations: at confidence level ≥4, precision ≈99.1% (estimated cumulative) with 89.3% recall; confidence level 10 achieves 100% precision at 75.3% recall.
- Paper-clinical trial citations: 98.99% of SciSciNet's linkages were also found in PKG (428,627 of 432,... matched; 76,154 PKG-only linkages not in SciSciNet).
- Holistic validation accuracy by linkage type: Link_Papers_ClinicalTrials 100%, Link_Papers_Patents 97%, Link_Papers_Projects 99%, Link_ClinicalTrials_Projects 98%, Link_Patents_Projects 82% (lower because funding sources aren't always mentioned in patent text).
- Case study successfully traced a BioNTech COVID-19 vaccine's path from clinical trial (NCT04368728, started April 2020) → Nature paper (published Aug 2020) → patent ("Coronavirus vaccine," filed April 2021, granted Jan 2023), demonstrating cross-literature knowledge flow.

## Strengths

- Massive scale: over 36M papers, 1.3M patents, 480K clinical trials, and 482M+ entity linkages — the largest such integrated resource reported.
- Fine-grained, fully validated multi-perspective linkage (entities, citations, projects, authors) rather than coarse bibliometric-only linking.
- Rigorous, multi-pronged technical validation (external gold-standard datasets, manual sampling, cross-database consistency checks).
- Demonstrated concrete utility for both scientometric research (author disambiguation improvement) and knowledge-flow analysis (COVID-19 vaccine case study).
- Fully open dataset (Figshare) and open-source NER/NEN tooling (BERN2 on GitHub) with a public roadmap for annual updates.

## Limitations

- Currently distributed only as TSV/SQL files; no user interface yet for non-technical users to query the graph directly.
- Underlying entity extraction, author disambiguation, and institution disambiguation rely on probabilistic/statistical models — some inherent bias/error is unavoidable and disambiguation results are explicitly "not recommended for individual research" use.
- Patent-project linkage precision is comparatively low (82%) since NIH funding isn't always disclosed in patent text.
- Dataset and method entity extraction (via dictionary-based approach) is described as exploratory, with unresolved name-ambiguity issues.
- Citation linkage between patents and clinical trials is sparse and based on simple string-pattern matching, likely missing many true links.
- Updating the dataset is computationally expensive and currently planned only annually.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: Any module needing to connect clinical trial records to their supporting literature and downstream commercialization (patents) — directly useful for an evidence-provenance or knowledge-flow tracing component, and for author/institution-level trust or expertise scoring.
- **What to implement**: (1) The BERN2-based entity extraction + iBKH relation-mapping pipeline for tagging clinical-trial text with standardized biomedical entities; (2) the citation-integration approach (combining native PubMed citations with NIH-OCC and AACT trial-registration-number linkage) to connect trials to their result papers; (3) the author/institution disambiguation pipeline (Author-ity + Semantic Scholar + DNN reconciliation, MapAffil + OpenAlex institution classifiers) if MOSAIC needs to resolve investigator or sponsor identities across trials, papers, and patents.
- **What should NOT be copied**: Full-scale ingestion of all 36M PubMed papers/1.3M patents is likely unnecessary if MOSAIC's scope is narrower (e.g., trial-focused); the dictionary-based dataset/method entity extraction, which the authors themselves flag as exploratory and unresolved for name ambiguity.
- **Possible improvements**: Combine this paper's citation/project/author linkage backbone with TrialGPT- or AACT-KG-style eligibility/criteria-level modeling for a more complete trial-to-evidence-to-commercialization pipeline; consider replacing the confidence-threshold-based citation filtering (Table 26 in the source) with a learned relevance model to improve precision at low confidence levels.
