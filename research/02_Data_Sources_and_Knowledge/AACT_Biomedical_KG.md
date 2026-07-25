# AACT Biomedical KG

## Basic Information

- **Title**: Generating Biomedical Knowledge Graphs from Knowledge Bases, Registries, and Multiomic Data
- **Authors**: Guangrong Qin, Kamileh Narsinh, Qi Wei, Jared C. Roach, Arpita Joshi, Skye L. Goetz, Sierra T. Moxon, Matthew H. Brush, Colleen Xu, Yao Yao, Amy K. Glen, Evan D. Morris, Alexandra Ralevski, Ryan Roper, Basazin Belhu, Yue Zhang, Ilya Shmulevich, Jennifer Hadlock, Gwênlyn Glusman
- **Year**: 2024
- **Venue**: bioRxiv (preprint)
- **DOI**: 10.1101/2024.11.14.623648
- **Official DOI Link**: https://doi.org/10.1101/2024.11.14.623648
- **Official Publisher Link**: https://doi.org/10.1101/2024.11.14.623648 (bioRxiv)
- **GitHub Repository(s)**:
  - Clinical Connections KG: https://github.com/Hadlock-Lab/clinical_risk_kp
  - BigGIM-Drug Response KG: https://github.com/multiomicsKP/drug_response_kp
  - Clinical Trials KG: https://github.com/multiomicsKP/clinical_trials_kp
  - Drug Approvals KG: https://github.com/multiomicsKP/drug_approvals_kp
  - Wellness Multiomics KG: https://github.com/Hadlock-Lab/multiomics_wellness_kp
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Yes — via AACT (Aggregate Analysis of ClinicalTrials.gov), 514,498 trials extracted (as of Nov 3, 2024), 115,086 modeled
  - AACT: Yes — primary source for the Clinical Trials KG
  - PubMed: Indirectly — used as a knowledge source for drug-target interactions (text mining) in BigGIM-DrugResponse KG
  - PubMed eUtils: Not reported
  - Other: DailyMed (152,812 product labels), FDA FAERS (20.4M+ adverse event reports), TCGA, GDSC, GTEx, BioGRID, HuRI, CellMarker 2.0, ISB Wellness cohort (4,879 individuals), Providence Health & Services EHRs (33.8M patients)

## Research Category

Core Biomedical Knowledge Graph Construction; Multi-source Data-to-Knowledge Transformation

## Research Problem

Large clinical and multiomics datasets and knowledge resources accumulate faster than they can be transformed into computable, actionable information for automated reasoning. Barriers include diversity of content, scale, and privacy (e.g., HIPAA-protected EHR data), and the lack of harmonized standards across data sources.

## Motivation

Systems like the Biomedical Data Translator rely on standardized knowledge graphs (KGs) to support automated reasoning across disparate biomedical data types. Without a general, reproducible pipeline for converting multiomics data and knowledge resources into KGs, each data source risks becoming a silo that automated reasoners cannot jointly leverage.

## Objective

Present a general, reproducible pipeline — used within the Translator ecosystem — for transforming multiomics data, clinical trial registries, drug approval records, and EHR data into five standardized, Biolink-compliant knowledge graphs, and demonstrate their combined use for biomedical hypothesis generation.

## Proposed Method

A five-stage workflow applied across all five KGs:

1. **Collection of data resources**: public multiomics datasets, public knowledge resources, in-house multiomics/EHR datasets, and clinical trials data.
2. **Data pre-processing**: cleaning, cohort selection, concept mapping to standard ontologies (NCBI Gene/HGNC, UniProt, PubChem, ChEBI, HMDB, CAS, KEGG, MONDO, LOINC, HPO, etc.) using Babel (Translator's Name Resolver/Node Normalizer).
3. **Statistical modeling**: correlation analysis (Spearman), logistic regression (for EHR-derived Clinical Connections KG), differential expression/T-tests with FDR correction, and drug-response threshold-based classification (BigGIM-DrugResponse).
4. **KG standardization (Biolink Model)**: mapping nodes/edges to Biolink classes (Disease, Gene, Protein, ChemicalEntity, SmallMolecule, PhenotypicFeature, ClinicalFinding, etc.) and predicates (correlated_with, treats, applied_to_treat, in_clinical_trials_for, associated_with_increased/decreased_likelihood_of, etc.), exported as KGX TSV node/edge files.
5. **API/deployment**: BioThings APIs, SmartAPI registration, and TRAPI endpoints (via BioThings Explorer, Plover, Plater) for querying by Translator's automated reasoning agents (ARAs).

Four-layer QC process: (1) domain-agnostic internal-consistency checks (BDQC-style), (2) expert manual review of ~40–100 sampled edges per KG, (3) internal FastAPI-based query testing, (4) external querying/testing via the Translator ecosystem with GitHub-based feedback.

## Datasets Used

- **BigGIM-DrugResponse KG**: TCGA, GDSC, GTEx (v8), BioGRID, HuRI/HI-union, CellMarker 2.0, DrugCentral, Therapeutic Target Database — gene-gene, protein-protein, gene-drug response, drug-target, and cell-gene relationships.
- **Clinical Trials KG**: AACT database, 514,498 trials, 115,086 modeled, 22,337 mapped biomedical concepts, 176,656 "in_clinical_trials_for" edges, 13,450 "treats" edges (Phase 4).
- **Drug Approvals KG**: DailyMed (152,812 product labels) cross-referenced with FAERS (20.4M+ adverse event reports, 35,571,841 non-redundant assertions), yielding 4,117 "treats" edges and 92,056 "applied_to_treat" edges.
- **Clinical Connections KG**: Providence Health & Services EHRs (51 hospitals, 1,085 clinics, 7 US states), 148 logistic regression models on data from 2008–2024, 39,553+ edges.
- **Wellness Multiomics KG**: ISB Wellness cohort, 4,879 individuals, 679,420 statistically significant correlations across 101 clinical labs, 264 proteins, 830 metabolites, under 27 stratification modes.

## Models / Technologies

- Biolink Model (semantic standardization)
- Babel (Translator's Name Resolver/Node Normalizer) for CURIE-based entity unification
- Spearman correlation (Wellness Multiomics KG)
- Logistic regression (Clinical Connections KG), AUROC/log-odds-ratio-based edge annotation
- T-test with Benjamini-Hochberg FDR correction (BigGIM-DrugResponse)
- KGX (Knowledge Graph Exchange) TSV format
- BioThings Studio/APIs, SmartAPI, TRAPI (BioThings Explorer, Plover, Plater)
- LOINC2HPO (lab-to-phenotype mapping)
- OMOP CDM, SNOMED CT, RxNorm (Clinical Connections KG concept mapping)

## Experimental Setup

- No single held-out benchmark; validation instead performed per-KG via a four-layer QC pipeline (internal consistency checks, expert edge sampling/review, internal query testing, external Translator-ecosystem testing).
- BigGIM-DrugResponse cross-validated using known drug-target interactions as gold-standard checks.
- Wellness Multiomics KG stratified by demographic/lifestyle variables (age, sex, race/ethnicity, alcohol/tobacco/marijuana use, family structure), with Bonferroni correction across 1,189,745 total tests.
- Use-case demonstration: a type 1 diabetes (T1D) subgraph combining edges from all five KGs plus other Translator KGs to reproduce the known finding that teplizumab treats/prevents T1D progression.

## Results

- Five KGs deployed and accessible via Translator/SmartAPI: BigGIM-DrugResponse, Clinical Trials, Drug Approvals, Clinical Connections, Wellness Multiomics.
- Clinical Trials KG: 176,656 "in_clinical_trials_for" edges + 13,450 Phase-4 "treats" edges across ~22,337 mapped concepts.
- Drug Approvals KG: 4,117 approved-treatment edges and 92,056 off-label "applied_to_treat" edges.
- Clinical Connections KG: over 39,553 edges representing predictive factors of disease from EHR-derived logistic regression models.
- Wellness Multiomics KG: 679,420 significant correlations (e.g., CRP–IL6 correlation varies from 0.53–0.60 by alcohol use and 0.57–0.70 by ancestry group), illustrating environment- and genetics-dependent immune relationships.
- Demonstrated multi-KG reasoning subgraph reproducing the known teplizumab–T1D treatment relationship and generating hypotheses about other candidate autoimmune-disease treatments (e.g., tocilizumab for early-stage T1D).

## Strengths

- Reusable, general five-stage pipeline applicable across very different data modalities (multiomics, clinical trials, drug labels, EHRs, wellness cohorts).
- Full Biolink Model standardization enables federated cross-KG reasoning within Translator.
- Explicit four-layer QC/validation process combining automated and expert review.
- Demonstrates privacy-preserving conversion of HIPAA-protected EHR data into shareable, de-identified knowledge.
- Rich edge-level provenance/attributes (p-values, effect sizes, confidence intervals, trial phase, sample sizes).

## Limitations

- KGs vary greatly in "knowledge level" — some (Drug Approvals, Clinical Trials) largely encode simple boolean/registry facts rather than newly inferred knowledge.
- Difficult to represent conditional/multi-step biological logic (e.g., metabolic cycles) in a KG structure.
- Large numbers of low-confidence/noisy edges can distract downstream reasoning; path-scoring/quality-filtering is left as future work.
- LLM-based knowledge extraction was not used in this iteration (noted as a likely direction for future KGs).
- Clinical Connections KG required costly infrastructure/domain expertise and only covers a curated subset (148 conditions) rather than the full space of clinical concepts.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: Any module needing to convert clinical-trials or EHR-adjacent data into a queryable, standardized knowledge graph — directly relevant to a trial-knowledge or evidence-graph component.
- **What to implement**: (1) The five-stage ETL → statistical modeling → Biolink standardization → KG generation → API deployment pipeline as a template for building a MOSAIC-specific Clinical Trials KG from AACT; (2) Babel-style CURIE normalization to unify entity identifiers across data sources; (3) the four-layer QC process (internal consistency, expert sampling, internal query testing, external validation) as a KG quality-assurance checklist.
- **What should NOT be copied**: The EHR-specific Clinical Connections pipeline (requires a secure data enclave and hospital-system access MOSAIC likely lacks); reliance on manually curated concept subsets (148 conditions) which limits generalizability.
- **Possible improvements**: Incorporate LLM-based entity/relation extraction (explicitly flagged by the authors as a future direction) to enrich edges beyond simple statistical correlations; add path-quality scoring to reduce noisy-edge distraction during multi-hop reasoning, which the authors identify as an open problem.
