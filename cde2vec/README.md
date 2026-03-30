## `cde2vec`: Embedding CDE Schemas & Ontologies

The `cde2vec` component leverages [`CurateGPT`](https://github.com/monarch-initiative/curategpt) to generate semantic vector embeddings from:

- **CDE schemas** in [LinkML](https://linkml.io/) format
- **OBO ontologies** (e.g., HPO, MONDO, CL)

These embeddings are stored in a local vector database for downstream tasks like semantic similarity, search, and clustering.

### Prerequisites

Ensure **CurateGPT** is installed. It is automatically installed via `setup.py`, but for reference, you can install it manually using:

```bash
pip install curategpt
```
Additionally, make sure you have your **OpenAI API key** set in your environment:

```bash
export OPENAI_API_KEY="your-api-key-here"
```
---

# Usage

Use the Makefile to index any supported ontology or schema:

### 🔹 Embed CDE Schemas

| Make Target              | Description                                                      |
|--------------------------|------------------------------------------------------------------|
| `make embed-nih-cde`     | Embed NIH/NLM CDE schema from `linkml/nih_nlm_schema.yaml`      |
| `make embed-phenx-cde`   | Embed PhenX CDE schema from `linkml/phenx_schema.yaml`          |
| `make embed-radx-up-cde` | Embed RADx-UP CDE schema from `linkml/radx_up_schema.yaml`      |
| `make embed-heal-cde`    | Embed HEAL CDE schema from `linkml/heal_schema.yaml`            |
| `make embed-connects-cde`| Embed CONNECTS CDE schema from `linkml/connects_schema.yaml`    |

### 🔹 Search Examples

#### Search the HEAL CDE Schema (`cde_heal`)
```bash
curategpt search -p db -c cde_heal "pain intensity numeric rating"
```

#### Search the CONNECTS CDE Schema (`cde_connects`)
```bash
curategpt search -p db -c cde_connects "COVID-19 symptom severity"
```

---

# Vector Store Location

Embeddings for the following CDE Schemas and Ontologies will be generated and stored at location `TBD`  , which is the **ChromaDB vector database**.

---

