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

| Make Target           | Description                                       |
|----------------------|-------------------------------------------------|
| `make embed-nih-cde`    | Embed NIH/NLM CDE schema from `linkml/nih_nlm_schema.yaml`      |
| `make embed-phenx-cde`  | Embed PhenX CDE schema from `linkml/phenx_schema.yaml`          |
| `make embed-radx-up-cde`| Embed RADx-UP CDE schema from `linkml/radx_up_schema.yaml`      |

### 🔹 Embed Ontologies

| Make Target              | Description                  |
|-------------------------|------------------------------|
| `make embed-hp-ontology`    | Embed HPO (Human Phenotype Ontology)    |
| `make embed-mondo-ontology` | Embed MONDO Disease Ontology             |
| `make embed-cl-ontology`    | Embed CL (Cell Ontology)                  |

---

# Vector Store Location

Embeddings for the following CDE Schemas and Ontologies will be generated and stored in the `db` folder , which is the **ChromaDB vector database**.

## 📂 View Indexed Collections

To list all collections currently embedded in your database, run:

```bash
curategpt collections list -p db
```
---

# 🔍 Search Embedded CDEs and Ontologies

Once embeddings are generated and stored in the vector DB (`db/`), you can use CurateGPT to run semantic search queries across any indexed collection.

## Basic Search Command

```bash
curategpt search \
  -p db \
  -c <collection_name> \
  "<your search query>"
```
- `-p db`: path to your ChromaDB folder  
- `-c <collection_name>`: name of the collection to search (e.g., `ont_hp`, `cde_phenx`)  
- `"..."`: your natural language or keyword-based query  

## 🔎 Examples

### 🔹 Search the Human Phenotype Ontology (`ont_hp`)

```bash
curategpt search -p db -c ont_hp "symptom involving hearing loss"
```
### 🔹 Search the RADx-UP CDE Schema (`cde_radx_up`)

```bash
curategpt search -p db -c cde_radx_up "participant's COVID-19 test history"
```
---

