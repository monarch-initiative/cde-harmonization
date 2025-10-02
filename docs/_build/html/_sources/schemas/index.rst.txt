Schema Documentation
====================

This section describes the LinkML schemas used in the CDE Harmonization project.

Overview
--------

The project converts CDEs from various repositories into LinkML schemas, creating what we call "Condor microschemas". These schemas provide:

- Structured representation of CDEs
- Type definitions and constraints
- Ontology bindings and mappings
- Permissible values (enumerations)

Available Schemas
-----------------

.. toctree::
   :maxdepth: 2

   nih-nlm
   phenx
   radx-up

Schema Components
-----------------

Each CDE schema typically includes:

**Classes**
   Represent data collection forms or surveys

**Slots**
   Individual data elements (questions, measurements)

**Enumerations**
   Permissible values for categorical fields

**Types**
   Data types with constraints

**Prefixes**
   Ontology and vocabulary namespaces

Working with Schemas
--------------------

Schemas are stored in the ``linkml/`` directory as YAML files:

- ``nih_nlm_schema.yaml`` - NIH NLM CDEs
- ``phenx_schema.yaml`` - PhenX CDEs  
- ``radx_up_schema.yaml`` - RADx-UP CDEs

See the :doc:`../howtos/index` section for guides on using these schemas.
