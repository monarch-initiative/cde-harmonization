#!/usr/bin/env python3
"""
allxall_mapper_omop.py
=======================
Inject inCDMExact / inCDMClose OWL restrictions into an existing
annotated CDE ontology by matching it against the cdm_omop ChromaDB
collection via curategpt all-by-all.

Thresholds
----------
  inCDMExact : similarity >= 0.99
  inCDMClose : similarity >= 0.95 and < 0.99

Architecture
------------
  INPUT : annotated OWL file (cdes_values_ontology_annotated.owl)
          omop_cdm_schema.yaml (or omop_5.4.xlsx)
          ChromaDB at --chroma
  PROCESS:
    1. Scan OWL -> build label_snake -> local_id map (crosswalk)
    2. Run curategpt all-by-all -c cdm_omop -X <source> -t csv
    3. Filter to SlotDefinition rows
    4. right_name (source slot key) -> crosswalk -> OWL local_id
    5. left_name  (cdm_omop slot key) -> omop_cdm_schema.yaml -> column_id/table
    6. Inject owl:equivalentClass restriction into existing OWL class block
    7. Append OMOP hierarchy + object properties (once, skipped on re-runs)
  OUTPUT: same OWL with restrictions injected

Usage
-----
  python cde2onto/allxall_mapper_omop.py \\
      --owl    cde2onto/cdes_values_ontology_annotated_phenx.owl \\
      --omop   linkml/omop_cdm_schema.yaml \\
      --chroma db \\
      --source cde_phenx \\
      --out    cde2onto/cdes_values_ontology_annotated_phenx_omop.owl
"""

import argparse
import csv
import io
import re
import subprocess
import unicodedata
import uuid
from pathlib import Path
from typing import Dict, List, Tuple


EXACT_THRESHOLD = 0.97 #0.99
CLOSE_THRESHOLD = 0.85 #0.95


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--owl",    required=True)
    p.add_argument("--omop",   required=True,
                   help="omop_cdm_schema.yaml or omop_5.4.xlsx")
    p.add_argument("--chroma", required=True)
    p.add_argument("--source", required=True,
                   help="Source collection to match (e.g. cde_phenx, cde_nih)")
    p.add_argument("--out",    required=True)
    p.add_argument("--omop-collection", default="cdm_omop", dest="omop_collection")
    p.add_argument("--limit",  type=int, default=50)
    p.add_argument("--ns-prefix", default="ex", dest="ns_prefix")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Utilities (shared with phenx mapper)
# ─────────────────────────────────────────────────────────────────────────────

def safe_id(text):
    text = unicodedata.normalize("NFKD", str(text))
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s/,]+", "_", text.strip())
    return text or "Unknown"

def snake(text):
    text = re.sub(r"[\s\-\.]+", "_", str(text).strip())
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower()

def xe(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

def _s(v):
    return "" if (v is None or (isinstance(v, float) and v != v)) \
           else str(v).strip()

def fresh_node():
    return "N" + uuid.uuid4().hex

def owl_class(uri, label, comment, parent_uri):
    return (
        f'  <rdf:Description rdf:about="{uri}">\n'
        f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
        f'    <rdfs:label>{xe(label)}</rdfs:label>\n'
        f'    <rdfs:comment>{xe(comment)}</rdfs:comment>\n'
        f'    <rdfs:subClassOf rdf:resource="{parent_uri}"/>\n'
        f'  </rdf:Description>\n'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — scan OWL (same as phenx mapper)
# ─────────────────────────────────────────────────────────────────────────────

def scan_owl(owl_content):
    ns_m = re.search(
        r'rdf:about="(https?://[^"]+#)(?:cde_|dd_|bdc_|REPO_)', owl_content)
    if not ns_m:
        raise ValueError("Cannot detect OWL namespace")
    ns = ns_m.group(1)

    var_prefix = "cde_"
    for pfx in ("cde_", "dd_", "bdc_"):
        if re.search(r'rdf:about="' + re.escape(ns) + re.escape(pfx) + r'\d',
                     owl_content):
            var_prefix = pfx
            break

    block_pat = re.compile(
        r'<rdf:Description rdf:about="' + re.escape(ns)
        + re.escape(var_prefix) + r'[^"]+">.*?</rdf:Description>',
        re.DOTALL)

    label_to_lid: Dict[str, str] = {}
    for m in block_pat.finditer(owl_content):
        block = m.group(0)
        lid_m = re.search(r'rdf:about="' + re.escape(ns) + r'([^"]+)"', block)
        if not lid_m:
            continue
        local_id = lid_m.group(1)
        labels = re.findall(r'<rdfs:label>(.*?)</rdfs:label>', block, re.DOTALL)
        if labels:
            label_to_lid[snake(labels[0].strip())] = local_id

    return ns, var_prefix, label_to_lid


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — run all-by-all (same as phenx mapper)
# ─────────────────────────────────────────────────────────────────────────────

def run_all_by_all(chroma, left, right, limit):
    cmd = [
        "curategpt", "all-by-all",
        "-p", chroma, "-c", left, "-X", right,
        "-D", "chromadb",
        "--threshold", str(CLOSE_THRESHOLD),
        "-l", str(limit), "-t", "csv",
    ]
    print(f"    $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [ERROR] all-by-all failed:\n{result.stderr[-2000:]}")
        return []
    rows = list(csv.DictReader(io.StringIO(result.stdout)))
    slot_rows = [r for r in rows if r.get("left_@type") == "SlotDefinition"]
    print(f"    {len(slot_rows):,} SlotDefinition rows "
          f"(of {len(rows):,} total)")
    return slot_rows


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — load OMOP schema
# ─────────────────────────────────────────────────────────────────────────────

def load_and_parse_omop(omop_path):
    path = Path(omop_path)
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml
        with open(path, encoding="utf-8") as f:
            schema = yaml.safe_load(f)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        schema = _xlsx_to_schema(str(path))
    else:
        raise ValueError(f"Unsupported --omop format: {path.suffix}")

    table_groups: Dict[str, dict] = {}
    tables:       Dict[str, dict] = {}
    columns:      Dict[str, dict] = {}
    slot_to_col:  Dict[str, str]  = {}

    for slot_key, slot in schema.get("slots", {}).items():
        ann     = slot.get("annotations", {})
        col_id  = _s(ann.get("source_variable_id", slot_key))
        tname   = _s(ann.get("table_name",  "")).upper()
        tgroup  = _s(ann.get("table_group", "Unknown_Tables"))
        tdesc   = _s(ann.get("table_description", ""))
        turl    = _s(ann.get("table_url",   ""))
        cdm_ver = _s(ann.get("cdm_version", ""))

        if not tname:
            continue

        if tgroup not in table_groups:
            table_groups[tgroup] = {"tables": []}
        if tname not in table_groups[tgroup]["tables"]:
            table_groups[tgroup]["tables"].append(tname)

        if tname not in tables:
            tables[tname] = {"group": tgroup, "description": tdesc,
                              "url": turl, "cdm_version": cdm_ver}

        if col_id and col_id not in columns:
            columns[col_id] = {
                "name":        _s(ann.get("column_name",   slot_key)),
                "description": _s(slot.get("description",  "")),
                "table_name":  tname,
                "datatype":    _s(ann.get("datatype",      "")),
                "is_required": _s(ann.get("is_required",   "")),
                "is_pk":       _s(ann.get("is_primary_key","")),
            }
            slot_to_col[slot_key] = col_id

    cdm_ver = (list(tables.values())[0].get("cdm_version", "") if tables else "")
    print(f"    CDM v{cdm_ver}  |  {len(table_groups)} groups  "
          f"{len(tables)} tables  {len(columns)} columns  "
          f"{len(slot_to_col):,} slot->column mappings")
    return table_groups, tables, columns, slot_to_col


def _xlsx_to_schema(xlsx_path):
    import pandas as pd
    df = pd.read_excel(xlsx_path, sheet_name="Columns (CDEs)", header=1)
    df.columns = df.columns.str.strip()

    COL_MAP = {
        "Column ID (CDE ID)": "source_variable_id",
        "CDM Version":        "cdm_version",
        "Column Name":        "column_name",
        "Datatype":           "datatype",
        "Is Required":        "is_required",
        "Is Primary Key":     "is_primary_key",
        "Table Name":         "table_name",
        "Table Description":  "table_description",
        "Table Group":        "table_group",
        "Table URL":          "table_url",
    }
    active = {c: k for c, k in COL_MAP.items() if c in df.columns}

    def _snk(t):
        t = re.sub(r'[\s\-\.]+', '_', str(t).strip())
        t = re.sub(r'[^a-zA-Z0-9_]', '', t)
        return re.sub(r'_+', '_', t).strip('_').lower()

    slots = {}
    for _, row in df.iterrows():
        col_name = _s(row.get("Column Name", ""))
        tname    = _s(row.get("Table Name",  "")).upper()
        desc     = _s(row.get("Column Description", col_name))
        if not col_name or not tname:
            continue
        key = f"{_snk(tname)}__{_snk(col_name)}"
        if not key or key in slots:
            continue
        ann = {"source": "OMOP_CDM"}
        for col, ak in active.items():
            v = _s(row.get(col, ""))
            if v:
                ann[ak] = v
        slots[key] = {"description": desc, "annotations": ann}

    return {"slots": slots}


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — build match_results
# ─────────────────────────────────────────────────────────────────────────────

def build_match_results(rows, label_to_lid, slot_to_col, columns):
    results: Dict[str, dict] = {}
    no_crosswalk = 0
    no_col       = 0

    for row in rows:
        left_name  = _s(row.get("left_name",  ""))
        right_name = _s(row.get("right_name", ""))
        try:
            score = float(row.get("similarity", 0))
        except (TypeError, ValueError):
            continue

        local_id = label_to_lid.get(right_name)
        if not local_id:
            no_crosswalk += 1
            continue

        col_id = slot_to_col.get(left_name)
        if not col_id or col_id not in columns:
            no_col += 1
            continue

        if local_id not in results:
            results[local_id] = {"exact": [], "close": []}

        bucket = "exact" if score >= EXACT_THRESHOLD else "close"
        if col_id not in results[local_id][bucket]:
            results[local_id][bucket].append(col_id)

    n_exact = sum(1 for v in results.values() if v["exact"])
    n_close = sum(1 for v in results.values() if v["close"])
    print(f"    Matched {len(results):,} OWL classes "
          f"({n_exact:,} inCDMExact, {n_close:,} inCDMClose)")
    if no_crosswalk:
        print(f"    [INFO] {no_crosswalk:,} rows had no OWL crosswalk")
    if no_col:
        print(f"    [INFO] {no_col:,} rows had no column mapping in schema")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — inject restrictions (same pattern as phenx mapper)
# ─────────────────────────────────────────────────────────────────────────────

def build_rdf_list(uris):
    nodes = [fresh_node() for _ in uris]
    blocks = []
    for i, (uri, nid) in enumerate(zip(uris, nodes)):
        rest = (
            'rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"'
            if i == len(uris) - 1 else f'rdf:nodeID="{nodes[i+1]}"'
        )
        blocks.append(
            f'  <rdf:Description rdf:nodeID="{nid}">\n'
            f'    <rdf:first rdf:resource="{uri}"/>\n'
            f'    <rdf:rest {rest}/>\n'
            f'  </rdf:Description>\n'
        )
    return "".join(blocks), nodes[0]


def build_restriction(prop_uri, target_uris):
    restr_id = fresh_node()
    if len(target_uris) == 1:
        blocks = (
            f'  <rdf:Description rdf:nodeID="{restr_id}">\n'
            f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Restriction"/>\n'
            f'    <owl:onProperty rdf:resource="{prop_uri}"/>\n'
            f'    <owl:someValuesFrom rdf:resource="{target_uris[0]}"/>\n'
            f'  </rdf:Description>\n'
        )
    else:
        list_xml, list_head = build_rdf_list(target_uris)
        union_id = fresh_node()
        blocks = (
            f'  <rdf:Description rdf:nodeID="{restr_id}">\n'
            f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Restriction"/>\n'
            f'    <owl:onProperty rdf:resource="{prop_uri}"/>\n'
            f'    <owl:someValuesFrom rdf:nodeID="{union_id}"/>\n'
            f'  </rdf:Description>\n'
            f'  <rdf:Description rdf:nodeID="{union_id}">\n'
            f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
            f'    <owl:unionOf rdf:nodeID="{list_head}"/>\n'
            f'  </rdf:Description>\n'
            + list_xml
        )
    return blocks, restr_id


def col_uri(col_id, ns):
    return f"{ns}{safe_id(col_id)}"


def inject_restrictions(owl_content, match_results, columns, var_prefix, ns):
    blank_nodes: List[str] = []

    def make_equiv(prop_local, ids, uri_fn):
        uris     = [uri_fn(i, ns) for i in ids]
        xml, rid = build_restriction(f"{ns}{prop_local}", uris)
        blank_nodes.append(xml)
        return f'    <owl:equivalentClass rdf:nodeID="{rid}"/>\n'

    pat = re.compile(
        r'(<rdf:Description rdf:about="' + re.escape(ns)
        + re.escape(var_prefix) + r'[^"]+">)(.*?)(</rdf:Description>)',
        re.DOTALL)

    def replacer(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        lid_m = re.search(r'rdf:about="' + re.escape(ns) + r'([^"]+)"', open_tag)
        if not lid_m:
            return m.group(0)
        mr = match_results.get(lid_m.group(1))
        if not mr:
            return m.group(0)
        injected = ""
        if mr.get("exact"):
            injected += make_equiv("inCDMExact", mr["exact"], col_uri)
        if mr.get("close"):
            injected += make_equiv("inCDMClose", mr["close"], col_uri)
        return open_tag + body + injected + close_tag

    return pat.sub(replacer, owl_content), "".join(blank_nodes)


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — append OMOP hierarchy + object properties (once)
# ─────────────────────────────────────────────────────────────────────────────

def build_property_owl(ns):
    props = [
        ("inCDMExact",
         f"Links a CDE variable to OMOP CDM Column(s) with cosine similarity "
         f">= {EXACT_THRESHOLD}."),
        ("inCDMClose",
         f"Links a CDE variable to OMOP CDM Column(s) with cosine similarity "
         f">= {CLOSE_THRESHOLD} and < {EXACT_THRESHOLD}."),
    ]
    parts = ['\n  <!-- OMOP CDM Object Properties -->\n\n']
    for local, comment in props:
        parts.append(
            f'  <rdf:Description rdf:about="{ns}{local}">\n'
            f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#ObjectProperty"/>\n'
            f'    <rdfs:label>{xe(local)}</rdfs:label>\n'
            f'    <rdfs:comment>{xe(comment)}</rdfs:comment>\n'
            f'  </rdf:Description>\n\n'
        )
    return "".join(parts)


def build_hierarchy_owl(table_groups, tables, columns, ns):
    parts = ['\n  <!-- OMOP CDM Hierarchy -->\n\n']

    parts.append(
        f'  <rdf:Description rdf:about="{ns}CDM_Bundles">\n'
        f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
        f'    <rdfs:label>CDM_Bundles</rdfs:label>\n'
        f'    <rdfs:comment>Top-level class for all CDM bundle types.</rdfs:comment>\n'
        f'  </rdf:Description>\n\n'
        f'  <rdf:Description rdf:about="{ns}cdm_omop">\n'
        f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
        f'    <rdfs:label>cdm_omop</rdfs:label>\n'
        f'    <rdfs:comment>OMOP Common Data Model. '
        f'{len(table_groups)} table groups, {len(tables)} tables, '
        f'{len(columns)} columns.</rdfs:comment>\n'
        f'    <rdfs:subClassOf rdf:resource="{ns}CDM_Bundles"/>\n'
        f'  </rdf:Description>\n\n'
    )

    for grp in sorted(table_groups):
        local = f"OMOPTableGroup_{safe_id(grp)}"
        parts.append(owl_class(
            f"{ns}{local}", grp.replace("_", " "),
            f"OMOP CDM table group: {grp}.", f"{ns}cdm_omop"))

    for tname, tinfo in sorted(tables.items()):
        grp_local = f"OMOPTableGroup_{safe_id(tinfo['group'])}"
        desc = tinfo["description"][:300] if tinfo["description"] else tname
        url  = f"  URL: {tinfo['url']}" if tinfo["url"] else ""
        parts.append(owl_class(
            f"{ns}OMOPTable_{safe_id(tname)}", tname,
            f"{desc}{url}", f"{ns}{grp_local}"))

    for col_id, col in sorted(columns.items(),
                               key=lambda x: (x[1]["table_name"], x[0])):
        meta = []
        if col["datatype"]:    meta.append(f"Datatype: {col['datatype']}.")
        if col["is_required"] == "Yes": meta.append("Required.")
        if col["is_pk"]       == "Yes": meta.append("Primary key.")
        desc    = col["description"][:400] if col["description"] else col["name"]
        comment = (desc + ("  " + "  ".join(meta) if meta else "")).strip()
        parts.append(owl_class(
            col_uri(col_id, ns),
            f"{col['table_name']}.{col['name']}",
            comment,
            f"{ns}OMOPTable_{safe_id(col['table_name'])}"))

    return "".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    print("[1] Loading OWL …")
    owl_content = Path(args.owl).read_text(encoding="utf-8")
    ns, var_prefix, label_to_lid = scan_owl(owl_content)
    print(f"    Namespace  : {ns}")
    print(f"    Var prefix : {var_prefix}")
    print(f"    Crosswalk  : {len(label_to_lid):,} OWL classes")

    print(f"\n[2] Running all-by-all: "
          f"'{args.omop_collection}' vs '{args.source}' …")
    rows = run_all_by_all(
        args.chroma, args.omop_collection, args.source, args.limit)

    print(f"\n[3] Loading {args.omop} …")
    table_groups, tables, columns, slot_to_col = load_and_parse_omop(args.omop)

    print(f"\n[4] Building match_results …")
    print(f"    inCDMExact : similarity >= {EXACT_THRESHOLD}")
    print(f"    inCDMClose : similarity >= {CLOSE_THRESHOLD} "
          f"and < {EXACT_THRESHOLD}")
    match_results = build_match_results(
        rows, label_to_lid, slot_to_col, columns)

    print(f"\n[5] Injecting owl:equivalentClass restrictions …")
    out, blank_nodes = inject_restrictions(
        owl_content, match_results, columns, var_prefix, ns)

    already_props = f"{ns}inCDMExact"  in owl_content
    already_hier  = f"{ns}cdm_omop"    in owl_content
    if already_props:
        print(f"    [SKIP] Properties already present (incremental run)")
    if already_hier:
        print(f"    [SKIP] OMOP hierarchy already present (incremental run)")

    prop_owl = "" if already_props else build_property_owl(ns)
    hier_owl = "" if already_hier  else build_hierarchy_owl(
        table_groups, tables, columns, ns)

    if f'xmlns:{args.ns_prefix}=' not in out:
        out = out.replace('<rdf:RDF',
                          f'<rdf:RDF\n   xmlns:{args.ns_prefix}="{ns}"', 1)

    out = out.replace(
        "</rdf:RDF>",
        blank_nodes + prop_owl + hier_owl + "\n</rdf:RDF>",
    )

    print(f"\n[6] Writing → {args.out}")
    Path(args.out).write_text(out, encoding="utf-8")
    size_mb = Path(args.out).stat().st_size / 1024 / 1024

    n_exact = sum(len(v["exact"]) for v in match_results.values())
    n_close = sum(len(v["close"]) for v in match_results.values())
    print(f"""
── Summary ──────────────────────────────────────────────────────────────
  Input OWL      : {args.owl}
  OMOP schema    : {args.omop}
  ChromaDB       : {args.chroma}
  Reference      : {args.omop_collection}
  Source         : {args.source}
  OWL crosswalk  : {len(label_to_lid):,} classes
  Matched classes: {len(match_results):,}
  inCDMExact     : {n_exact:,} column links  (>= {EXACT_THRESHOLD})
  inCDMClose     : {n_close:,} column links  (>= {CLOSE_THRESHOLD}, < {EXACT_THRESHOLD})
  Output         : {args.out}  ({size_mb:.1f} MB)
─────────────────────────────────────────────────────────────────────────""")


if __name__ == "__main__":
    main()