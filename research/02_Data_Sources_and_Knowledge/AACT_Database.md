# AACT Database

## Basic Information

- **Title**: The Database for Aggregate Analysis of ClinicalTrials.gov (AACT) and Subsequent Regrouping by Clinical Specialty
- **Authors**: Asba Tasneem, Laura Aberle, Hari Ananth, Swati Chakraborty, Karen Chiswell, Brian J. McCourt, Ricardo Pietrobon
- **Year**: 2012
- **Venue**: PLoS ONE, 7(3): e33677
- **DOI**: 10.1371/journal.pone.0033677
- **Official DOI Link**: https://doi.org/10.1371/journal.pone.0033677
- **Official Publisher Link**: https://doi.org/10.1371/journal.pone.0033677 (PLoS ONE, open access)
- **GitHub Repository**: Not reported (database, not a code repository)
- **Dataset(s) Used**:
  - ClinicalTrials.gov: Yes — 96,346 clinical trials downloaded in XML format as of September 27, 2010
  - AACT: This paper is the origin/definition of the AACT database itself
  - PubMed: Not reported
  - PubMed eUtils: Not reported
  - Other: 2010 MeSH Thesaurus (merged into AACT as a lookup table); Department of Health and Human Services clinical specialty designations (used as basis for the specialty taxonomy)

## Research Category

Data Sources & Knowledge (clinical trial registry database and taxonomy)

## Research Problem

ClinicalTrials.gov provides valuable registry data for individual studies and bulk download, but its data structure, nomenclature inconsistencies, and changes in data collection practices over time make aggregate analysis of the data — and analysis by clinical specialty in particular — difficult.

## Motivation

As ClinicalTrials.gov data accumulated, users increasingly wanted aggregated, descriptive characterization of the national clinical research portfolio, but data-format and usability issues blocked this. The FDA–Duke University Clinical Trials Transformation Initiative (CTTI) recognized ClinicalTrials.gov as a promising resource for benchmarking the clinical trials enterprise but noted no systematic aggregate-analysis database existed. Related initiatives (OCRe, HSDB, CDISC Protocol Representation Model, LinkedCT) address complementary but different aspects (ontological annotation, data mining, representation format, external linkage) — none directly solved the aggregate-analysis/usability problem this paper targets.

## Objective

Two goals: (1) build and validate a relational database (AACT) that restructures ClinicalTrials.gov content into discrete, analyzable fields with integrated metadata and an integrated MeSH thesaurus; (2) develop and validate a methodology to regroup/annotate studies by clinical specialty using both MeSH and non-MeSH (free-text) disease condition terms.

## Proposed Method

- **AACT database construction**: Downloaded 96,346 ClinicalTrials.gov XML studies (Sept 27, 2010). Designed a normalized (2NF) relational schema (via Enterprise Architect) covering entities such as CLINICAL_STUDY, SPONSORS, AUTHORITIES, REFERENCES, ARM_GROUPS, INTERVENTIONS, CONDITIONS, LOCATIONS, PERSONS, DESIGNS, OUTCOMES, KEYWORDS, LINKS, SECONDARY_IDS, plus metadata tables (CURRENT_VARIABLES, ENUMERATIONS, VARIABLE_HISTORY_DATES). The single concatenated `Study Design` XML field was parsed into a separate DESIGNS table with discrete Design Name/Design Value pairs (including masking/blinding components and masking subjects: Participant, Investigator, Outcome Assessor, Caregiver). The 2010 MeSH thesaurus was merged in as a lookup table for MeSH IDs (tree numbers). Data were loaded into Oracle RDBMS (v11.1g) via custom PL/SQL packages, with escape-character handling, error-log tables, and manual user-acceptance testing (5 studies per data element, 109 elements total).
- **Clinical specialty regrouping methodology**:
  1. Selected four high-level MeSH nodes (Diseases; Analytical/Diagnostic/Therapeutic Techniques and Equipment; Psychiatry and Psychology; Phenomena and Processes) as the basis for specialty classification.
  2. Clinical specialists (13 specialties + 5 sub-specialties) annotated 18,491 MeSH IDs (9,031 MeSH terms) as relevant (Y/yes), not relevant (N/no), or ambiguous (A) to each specialty, checking for hierarchical (parent-child) consistency.
  3. Non-MeSH (free-text) condition terms appearing in ≥5 interventional studies registered after Sept 27, 2007 (n=40,970 studies) were independently reviewed/annotated by two clinicians per specialty, with a third clinician adjudicating disagreements.
  4. An algorithm classified each study into one of 5 groups per specialty based on combinations of MeSH/condition-term Y/N/A tags (Group 1: any term tagged Y; Group 2: not in Group 1, any term tagged A; Group 3: not in 1/2, all terms tagged N; Group 4: not in 1/2/3, any term tagged N; Group 5: none of the above/unclassified).
  5. Separate keyword-search-based methods (not validated) were used for genomics (search "gene," "genomic," "DNA" in multiple fields, including observational studies) and pediatrics (enrollment restricted to age ≤18) datasets.

## Datasets Used

- 96,346 clinical trials downloaded from ClinicalTrials.gov in XML format (Sept 27, 2010); of these, 79,413 (82.4%) interventional, 16,506 (17.1%) observational, 107 (0.1%) expanded-access, 320 unclassified.
- 2010 MeSH Thesaurus (merged as lookup table for MeSH IDs/tree numbers).
- Validation subset: a random sample of 1,000 interventional studies (from 40,970 registered Sept 27, 2007 – Sept 27, 2010) manually classified by 7 clinical specialists (2 reviewers per 200-study batch, adjudicated by an 8th reviewer) for cardiology, oncology, and mental health.

## Models / Technologies

- Oracle RDBMS 11.1g (database housing)
- Enterprise Architect 7.1 (data modeling/design tool)
- PL/SQL with Oracle's DBMS_LOB package (XML parsing/loading)
- Toad for Data Analysts, Cognos ReportNet (quality control/reporting)
- MeSH Thesaurus (2010) and NLM's MeSH-annotation algorithm (for condition_browse / intervention_browse fields)
- Rule-based classification algorithm (Groups 1–5) combining MeSH and free-text annotations
- No AI/ML models used — this is a data-engineering and manual-annotation methodology paper, not an LLM-based paper

## Experimental Setup

- Database built once from the Sept 2010 ClinicalTrials.gov snapshot; validated via manual user-acceptance testing (5 studies × 109 data elements).
- Data-completeness trends analyzed over time (1999–2010) for selected data elements, correlated with two regulatory milestones: the 2005 ICMJE trial-registration policy and the 2007 FDAAA mandatory-registration requirement.
- Specialty-classification validation: random sample of 1,000 interventional studies (2007–2010) manually classified by clinical specialists (7 reviewers, 200-study batches, 2 reviewers/batch + adjudicator) for cardiology, oncology, and mental health; compared against algorithmic classification via contingency tables (false positive/negative rates computed two ways).
- A secondary comparison assessed reliability of using only NLM-generated MeSH terms (`condition_browse`) vs. only submitter-provided free-text conditions (`condition`) for the same three specialties.

## Results

- AACT was successfully built as a normalized (2NF) relational database with parsed study-design fields, integrated MeSH thesaurus, and metadata tables; made publicly downloadable as Oracle extracts (.dmp and text format).
- Data completeness for several data elements (e.g., masking, allocation, intervention model, enrollment, gender, lead sponsor) rose sharply around 2005 (ICMJE policy) and again around 2007 (FDAAA), approaching ~90–100% completeness for mandated fields by 2008–2010.
- Specialty classification vs. manual review: overall incorrectly classified studies were 4.2% (cardiology), 1.2% (oncology), and 3.3% (mental health); ~5.1% of studies were unclassified in each specialty (Table 7).
- False positive rates (among algorithm-Y studies) were notably higher than false negative rates in cardiology (20.0% FP among algorithm-Y vs. 22.1% FN among manual-Y) and mental health (22.6% FP vs. 12.2% FN), while oncology had low error rates in both directions (1.7% FP, 2.8% FN).
- Comparing MeSH-only (`condition_browse`) vs. free-text-only (`condition`) classification: results differed by ≤4.9% across the three specialties (cardiology within 1.1%, oncology within 2.5%, mental health 4.9%), suggesting reasonable — but not perfect — agreement between the two term sources.
- Inter-reviewer disagreement among clinical specialists ranged from 3.5% (oncology) to 6.8% (cardiology) overall.
- ~5.4% of interventional trials from the study period were classified as oncology by manual review; ~9.5% cardiology; ~8.2% mental health.

## Strengths

- First systematic effort to create and publicly maintain an aggregate-analysis-ready version of ClinicalTrials.gov data.
- Normalized schema (2NF) with parsed Study Design fields enables analyses not feasible on the raw concatenated XML.
- Rigorous, quantitatively validated methodology for clinical-specialty classification, combining MeSH hierarchy and submitter free-text terms with expert clinician annotation.
- Publicly downloadable resource with comprehensive data dictionary (variables, enumerations, constraints, record counts, schema, change history).
- Demonstrates and quantifies how registry policy changes (ICMJE, FDAAA) affected data completeness over time — useful context for anyone querying historical trial data.

## Limitations

- ClinicalTrials.gov itself was designed as a public repository, not for aggregate research analysis — the underlying data quality/structure issues are only partially mitigated by AACT.
- MeSH's hierarchical structure was not designed to align with clinical-specialty groupings, and a single MeSH term can appear in multiple trees with conflicting specialty tags (e.g., "Acromegaly" spans Musculoskeletal, Nervous System, and Endocrine System disease trees), causing potential false positives.
- Specialty annotation relied exclusively on Duke University clinical experts; broader external validation was noted as desirable.
- Curation/taxonomy development was time- and resource-intensive; not easily scalable without a distributed/open curation model.
- Genomics and pediatrics specialty datasets were built with a different (keyword-search) method and were not validated by the same rigorous process as cardiology/oncology/mental health.

## How MOSAIC Can Reuse This Paper

- **Which MOSAIC module benefits**: The Data Sources & Knowledge layer — specifically, any component that ingests, normalizes, or queries ClinicalTrials.gov data (e.g., for trial retrieval, eligibility extraction, or knowledge-graph construction).
- **What to implement**: The normalized relational schema design pattern (parsing the concatenated `Study Design` field into discrete Design Name/Value pairs; separating masking/blinding into structured subject-level fields) as a template for MOSAIC's own trial data model; the MeSH-ID lookup and hierarchical-consistency-checking approach for building a clinical-specialty or condition-based taxonomy over trial data; the Group 1–5 rule-based classification pattern for tagging trials by category (which could be adapted for tagging trials by module-relevant categories in MOSAIC, e.g., therapeutic area, phase, or study type) with quantified false-positive/negative validation methodology.
- **What should NOT be copied**: The 2010-era MeSH-hierarchy-only classification approach, which is known to produce false positives due to multi-tree ambiguity — a modern MOSAIC system could use LLM-based classification (as in later papers, e.g., TrialMind's eligibility-criteria approach) as either an alternative or complement, rather than relying purely on static MeSH-tree lookups; the Oracle-specific ETL implementation details (a modern MOSAIC pipeline would likely use a different DB stack, e.g., Postgres or a vector DB, alongside AACT/ClinicalTrials.gov ingestion).
- **Possible improvements**: Combine MOSAIC's own LLM-based trial classification/tagging (as in TrialMind or ClinicalAgent-style agents) with AACT's structured schema as ground truth/validation data; use the actual modern AACT database (maintained by CTTI, updated far beyond this 2012 paper's 2010 snapshot) as a live, queryable structured data source alongside PubMed/ClinicalTrials.gov API access in MOSAIC's data layer, rather than re-deriving the schema from scratch.

## Personal Notes

