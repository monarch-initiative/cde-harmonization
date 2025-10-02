# Project Roadmap

This document outlines the current status and planned development for the CDE Harmonization project.

## Current Status

### ✅ Completed

**CDE Collection**
- Ingested CDEs from multiple repositories:
  - NIH/NLM CDE Repository
  - PhenX Toolkit
  - caDSR (NCI Cancer Data Standards Registry)
  - RADx-UP
- Raw data stored with full provenance

**Beta LinkML Conversion**
- Prototype `cde2linkml` tool converts CDEs to LinkML schemas
- Captures identifiers, permissible values, datatypes, and metadata
- Generated schemas for NIH NLM, PhenX, and RADx-UP CDEs

**Data Infrastructure**
- Database views for querying CDE metadata
- CSV exports of flattened CDE data

## Planned Development

### 🔨 In Progress

**LinkML Schema Refinement**
- Improve LinkML schema quality and consistency
- Add more metadata and provenance tracking
- Standardize slot and class naming conventions

### 📋 Planned Features

**AI-Powered Mapping Generation**
- Use large language models (LLMs) to generate SSSOM mappings
- Map CDEs to standard ontologies (LOINC, HPO, Mondo, NCIT, OBA)
- Identify equivalent CDEs across repositories
- Generate confidence scores for AI suggestions

**Human-in-the-Loop Curation Workflow**
- GitHub-based review process for AI-generated mappings
- Expert validation of ontology bindings
- Transparent provenance tracking
- Collaborative curation with multiple reviewers

**Common Value Sets**
- Build library of standardized permissible values
- Map value sets to ontology terms
- Enable reuse across CDEs (e.g., Yes/No/Unknown, Likert scales)

**Retrospective Data Harmonization**
- Generate schema crosswalks for aligning datasets
- Transform data using validated mappings
- Assess harmonization quality

**Prospective CDE Tools**
- Semantic clustering to recommend CDEs
- API integration with CDE repositories
- REDCap integration for harmonized data collection

## Timeline

Detailed timeline to be determined based on funding and resources.

## Technology Stack

**Current:**
- LinkML for schema modeling
- Python for data processing
- SSSOM for mapping representation
- Git/GitHub for version control

**Planned:**
- CurateGPT or similar AI tools for mapping generation
- OAK (Ontology Access Kit) for ontology access
- Semantic embedding models for CDE similarity

## Get Involved

This project is under active development. Contributions and feedback are welcome:
- Report issues or suggest features on GitHub
- Contribute CDE mappings or value sets
- Help review and validate AI-generated mappings (once available)

## References

- [LinkML Framework](https://linkml.io)
- [SSSOM Mapping Standard](https://mapping-commons.github.io/sssom/)
- [CurateGPT](https://github.com/monarch-initiative/curate-gpt)
