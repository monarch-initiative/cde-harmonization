CDE Harmonization Documentation
=================================

Welcome to the CDE Harmonization project documentation. This project supports the harmonization of Common Data Elements (CDEs) to enable interoperability across clinical research studies.

Overview
--------

CDEs are standardized data fields and survey questions with defined permissible values that facilitate consistent data collection. Despite their widespread use, CDEs remain fragmented across multiple repositories, lack semantic bindings to ontologies, and are often incompatible with one another—limiting cross-study integration and AI-readiness.

Our goal is to transform CDEs and study-specific variables into computable, semantically rich, and interoperable data assets using the LinkML framework, AI-assisted curation, and ontology-based standardization.

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro/overview
   intro/installation
   schemas/index
   howtos/index
   roadmap

Key Technologies
----------------

- **LinkML**: Schema language for defining computable, semantically rich data models
- **SSSOM**: Standard for representing and sharing ontology and CDE mappings with provenance
- **Ontologies**: HPO (phenotypes), Mondo (diseases), LOINC (lab tests), OBA (biological attributes)
- **AI/LLM tools**: CurateGPT, AI4Curation, and semantic embeddings for automated mapping and curation

Project Links
-------------

- `GitHub Repository <https://github.com/monarch-initiative/cde-harmonization>`_
- `LinkML Framework <https://linkml.io>`_
- `SSSOM Mappings <https://github.com/mapping-commons/sssom>`_

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
