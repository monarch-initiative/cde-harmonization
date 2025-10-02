# Overview

## What is CDE Harmonization?

The CDE Harmonization project addresses a critical challenge in clinical research: the lack of interoperability among Common Data Elements (CDEs) used across different studies and repositories.

## The Problem

Clinical datasets hold enormous potential for advancing biomedical research, but their value is undermined by:

- **Semantic heterogeneity**: The same concept (e.g., "heart attack" vs. "myocardial infarction") is expressed differently across datasets
- **Structural variability**: Equivalent data elements appear in incompatible formats (free text, categorical, numeric)
- **CDE proliferation**: Multiple CDEs often exist for the same concept, each with different units, contexts, or measurement types
- **Non-CDE variables**: Countless datasets capture variables without using formal CDEs, creating additional harmonization challenges
- **Fragmented CDE repositories**: Over a dozen repositories (NIH CDE Repository, PhenX, caDSR, etc.) with overlapping but inconsistent CDEs
- **Lack of computability**: Most CDEs are free text without formal schemas, ontology bindings, or machine-readable mappings

Without systematic harmonization, researchers cannot reliably integrate data across studies or leverage datasets for AI/ML applications.

## Our Approach

We are developing a comprehensive framework to make CDEs and study variables interoperable:

### Integration and AI-Assisted Curation

- **Ingest CDEs** from major repositories (NIH CDE Repository, PhenX, caDSR, HEAL, RADx, etc.) and study-specific variables
- **Convert to LinkML schemas**: Transform heterogeneous CDEs into a unified, computable format called *Condor microschemas*
- **Build Common Value Sets**: Standardize permissible values (e.g., "Yes/No", Likert scales) across CDEs
- **AI-assisted mapping**: Use large language models and semantic embeddings to generate mappings between CDEs and to ontologies (LOINC, HPO, Mondo, etc.)
- **Human-in-the-loop curation**: Expert curators validate AI-generated mappings via GitHub-based workflows using SSSOM (Simple Standard for Sharing Ontological Mappings)

### Community Tools and Integration

- **Semantic clustering**: Use embeddings to group similar CDEs, enabling discovery and recommendation
- **API and widgets**: Provide tools for semantic search and CDE selection, integrated into REDCap, CEDAR, and CDE repositories
- **Prospective harmonization**: Generate data collection forms directly from schematized CDEs to ensure new data is "born interoperable"
- **Retrospective harmonization**: Enable alignment of existing heterogeneous datasets through crosswalk tables and schema mappings
- **Collaboration with repositories**: Work with governance committees to integrate our framework into standard CDE development workflows
- **FAIR data release**: Publish harmonized CDEs at stable URLs with versioned snapshots

## Repository Contents

- **Raw CDEs**: Collected from 10+ repositories, preserving native formats with full provenance
- **Condor microschemas**: LinkML representations of CDEs with ontology bindings and cross-CDE mappings
- **Common Value Sets**: Reusable library of standardized permissible values
- **Crosswalk tables**: Schema mappings for retrospective data harmonization
- **Curation workflows**: AI-assisted pipelines for generating and validating mappings

Large files are stored in the [Monarch Google Cloud bucket](https://console.cloud.google.com/storage/browser/cde-harmonization).

## Impact

This work will create a **virtuous cycle of CDE interoperability**, enabling:

- **Cross-study integration**: Harmonized datasets that can be jointly analyzed across initiatives
- **AI-readiness**: Semantically annotated, schema-validated data suitable for machine learning
- **Prospective standardization**: Tools that help researchers select and use harmonized CDEs from the start
- **Retrospective harmonization**: Methods to align existing heterogeneous datasets
- **Computational modeling**: Connections between clinical data and physiological simulation models

By making CDEs computable and FAIR (Findable, Accessible, Interoperable, Reusable), we will unlock the full value of clinical research data for discovery, validation, and translation.
