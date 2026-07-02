#!/usr/bin/env python3
"""
allxall_mapper_phenx.py
========================
Inject inBundleExact / inBundleClose OWL restrictions into an existing
annotated CDE ontology by matching it against the bundle_phenx ChromaDB
collection via curategpt all-by-all.

Thresholds
----------
  inBundleExact : similarity >= 0.99
  inBundleClose : similarity >= 0.95 and < 0.99

Architecture
------------
  INPUT : annotated OWL file (cdes_values_ontology_annotated.owl)
          phenx_bundle_schema.yaml
          ChromaDB at --chroma
  PROCESS:
    1. Scan OWL → build label_snake -> local_id map (crosswalk)
    2. Run curategpt all-by-all -c bundle_phenx -X <source> -t csv
    3. Filter to SlotDefinition rows
    4. right_name (cde_phenx slot key) -> crosswalk -> OWL local_id
    5. left_name  (bundle_phenx slot key) -> phenx_bundle_schema.yaml -> protocol_id
    6. Inject owl:equivalentClass restriction into existing OWL class block
    7. Append PhenX hierarchy + object properties (once, skipped on re-runs)
  OUTPUT: same OWL with restrictions injected

Usage
-----
  # First source
  python cde2onto/allxall_mapper_phenx.py \\
      --owl    cde2onto/cdes_values_ontology_annotated.owl \\
      --phenx  linkml/phenx_bundle_schema.yaml \\
      --chroma db \\
      --source cde_phenx \\
      --out    cde2onto/cdes_values_ontology_annotated_phenx.owl

  # Incremental: chain sources
  python cde2onto/allxall_mapper_phenx.py \\
      --owl    cde2onto/cdes_values_ontology_annotated_phenx.owl \\
      --phenx  linkml/phenx_bundle_schema.yaml \\
      --chroma db \\
      --source cde_nih \\
      --out    cde2onto/cdes_values_ontology_annotated_phenx2.owl
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


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

EXACT_THRESHOLD = 0.98 #0.99
CLOSE_THRESHOLD = 0.90 #0.95


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--owl",    required=True, help="Input annotated OWL file")
    p.add_argument("--phenx",  required=True, help="phenx_bundle_schema.yaml")
    p.add_argument("--chroma", required=True, help="ChromaDB directory (e.g. db)")
    p.add_argument("--source", required=True,
                   help="Source collection to match (e.g. cde_phenx, cde_nih)")
    p.add_argument("--out",    required=True, help="Output OWL file")
    p.add_argument("--phenx-collection", default="bundle_phenx",
                   dest="phenx_collection")
    p.add_argument("--limit", type=int, default=50,
                   help="all-by-all -l flag: candidates per left item (default 50)")
    p.add_argument("--ns-prefix", default="ex", dest="ns_prefix")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def safe_id(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s/,]+", "_", text.strip())
    return text or "Unknown"

def snake(text: str) -> str:
    """Convert OWL rdfs:label to the slot-key format used in ChromaDB.
    PX121802_Anxiety_Disorders -> px121802_anxiety_disorders"""
    text = re.sub(r"[\s\-\.]+", "_", str(text).strip())
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower()

def xe(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

def _s(v) -> str:
    return "" if (v is None or (isinstance(v, float) and v != v)) \
           else str(v).strip()

def fresh_node() -> str:
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
# Step 1 — scan OWL → {snake(label): local_id}  crosswalk
# ─────────────────────────────────────────────────────────────────────────────

def scan_owl(owl_content: str) -> Tuple[str, str, Dict[str, str]]:
    """
    Returns (namespace, var_prefix, label_to_local_id).
    label_to_local_id: { snake(rdfs:label): local_id }
    Used to map all-by-all right_name -> OWL local_id.
    """
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
            key = snake(labels[0].strip())
            label_to_lid[key] = local_id

    return ns, var_prefix, label_to_lid


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — run curategpt all-by-all
# ─────────────────────────────────────────────────────────────────────────────

def run_all_by_all(chroma: str, left: str, right: str,
                   limit: int) -> List[Dict[str, str]]:
    """Run at the close threshold (0.95) — we split exact/close ourselves."""
    cmd = [
        "curategpt", "all-by-all",
        "-p", chroma,
        "-c", left,
        "-X", right,
        "-D", "chromadb",
        "--threshold", str(CLOSE_THRESHOLD),
        "-l", str(limit),
        "-t", "csv",
    ]
    print(f"    $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [ERROR] all-by-all failed:\n{result.stderr[-2000:]}")
        return []
    rows = list(csv.DictReader(io.StringIO(result.stdout)))
    slot_rows = [r for r in rows if r.get("left_@type") == "SlotDefinition"]
    print(f"    {len(slot_rows):,} SlotDefinition rows "
          f"(of {len(rows):,} total, {len(rows)-len(slot_rows):,} noise filtered)")
    return slot_rows


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — load PhenX schema → slot_to_proto + hierarchy
# ─────────────────────────────────────────────────────────────────────────────

def load_and_parse_phenx(yaml_path: str):
    import yaml
    with open(yaml_path, encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    collections:   Dict[str, dict] = {}
    subcols:       Dict[str, dict] = {}
    domains:       Dict[str, dict] = {}
    proto_info:    Dict[str, dict] = {}
    slot_to_proto: Dict[str, str]  = {}

    for slot_key, slot in schema.get("slots", {}).items():
        ann    = slot.get("annotations", {})
        pid    = _s(ann.get("protocol_id",         ""))
        pname  = _s(ann.get("protocol_name",       ""))
        purl   = _s(ann.get("protocol_url",        ""))
        did    = _s(ann.get("domain_id",           ""))
        dname  = _s(ann.get("domain_name",         ""))
        sub_id = _s(ann.get("sub_collection_id",   ""))
        sub_nm = _s(ann.get("sub_collection_name", ""))
        col_id = _s(ann.get("collection_id",       ""))
        col_nm = _s(ann.get("collection_name",     ""))

        if not pid:
            continue

        if col_id and col_id not in collections:
            collections[col_id] = {"name": col_nm}
        if sub_id and sub_id not in subcols:
            subcols[sub_id] = {"name": sub_nm, "col_id": col_id}
        if did and did not in domains:
            domains[did] = {"name": dname, "col_id": col_id, "sub_id": sub_id}
        if pid not in proto_info:
            proto_info[pid] = {"name": pname, "url": purl,
                               "domain_id": did, "sub_id": sub_id, "col_id": col_id}
        slot_to_proto[slot_key] = pid

    print(f"    {len(collections)} collections  {len(subcols)} sub-collections  "
          f"{len(domains)} domains  {len(proto_info)} protocols  "
          f"{len(slot_to_proto):,} slot->protocol mappings")
    return collections, subcols, domains, proto_info, slot_to_proto


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — build match_results
# { owl_local_id: { 'exact': [proto_id,...], 'close': [proto_id,...] } }
# ─────────────────────────────────────────────────────────────────────────────

def build_match_results(
        rows: List[Dict[str, str]],
        label_to_lid: Dict[str, str],
        slot_to_proto: Dict[str, str],
        proto_info: Dict,
) -> Dict[str, dict]:
    results: Dict[str, dict] = {}
    no_crosswalk = 0
    no_proto     = 0

    for row in rows:
        left_name  = _s(row.get("left_name",  ""))
        right_name = _s(row.get("right_name", ""))
        try:
            score = float(row.get("similarity", 0))
        except (TypeError, ValueError):
            continue

        # Crosswalk: right_name (ChromaDB slot key) -> OWL local_id
        local_id = label_to_lid.get(right_name)
        if not local_id:
            no_crosswalk += 1
            continue

        # left_name (bundle_phenx slot key) -> protocol_id
        pid = slot_to_proto.get(left_name)
        if not pid or pid not in proto_info:
            no_proto += 1
            continue

        if local_id not in results:
            results[local_id] = {"exact": [], "close": []}

        if score >= EXACT_THRESHOLD:
            if pid not in results[local_id]["exact"]:
                results[local_id]["exact"].append(pid)
        else:  # already filtered to >= CLOSE_THRESHOLD
            if pid not in results[local_id]["close"]:
                results[local_id]["close"].append(pid)

    n_exact = sum(1 for v in results.values() if v["exact"])
    n_close = sum(1 for v in results.values() if v["close"])
    print(f"    Matched {len(results):,} OWL classes "
          f"({n_exact:,} inBundleExact, {n_close:,} inBundleClose)")
    if no_crosswalk:
        print(f"    [INFO] {no_crosswalk:,} rows had no OWL crosswalk "
              f"(source slot key not found via snake(label))")
    if no_proto:
        print(f"    [INFO] {no_proto:,} rows had no protocol mapping in schema")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — inject owl:equivalentClass restrictions into existing OWL classes
# ─────────────────────────────────────────────────────────────────────────────

def build_rdf_list(uris: List[str]) -> Tuple[str, str]:
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


def build_restriction(prop_uri: str, target_uris: List[str]) -> Tuple[str, str]:
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


def proto_uri(pid: str, proto_info: Dict, ns: str) -> str:
    name = safe_id(proto_info[pid]["name"]) if pid in proto_info else safe_id(pid)
    return f"{ns}PhenXProtocol_{pid}_{name}"


def inject_restrictions(
        owl_content: str,
        match_results: Dict[str, dict],
        proto_info: Dict,
        var_prefix: str,
        ns: str,
) -> Tuple[str, str]:
    """
    Inject owl:equivalentClass restrictions into existing OWL class blocks.
    Returns (modified_owl, blank_node_xml).
    """
    blank_nodes: List[str] = []

    def make_equiv(prop_local: str, pids: List[str]) -> str:
        prop_uri_  = f"{ns}{prop_local}"
        uris       = [proto_uri(p, proto_info, ns) for p in pids]
        xml, rid   = build_restriction(prop_uri_, uris)
        blank_nodes.append(xml)
        return f'    <owl:equivalentClass rdf:nodeID="{rid}"/>\n'

    pat = re.compile(
        r'(<rdf:Description rdf:about="' + re.escape(ns)
        + re.escape(var_prefix) + r'[^"]+">)(.*?)(</rdf:Description>)',
        re.DOTALL)

    def replacer(m: re.Match) -> str:
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        lid_m = re.search(r'rdf:about="' + re.escape(ns) + r'([^"]+)"', open_tag)
        if not lid_m:
            return m.group(0)
        mr = match_results.get(lid_m.group(1))
        if not mr:
            return m.group(0)
        injected = ""
        if mr.get("exact"):
            injected += make_equiv("inBundleExact", mr["exact"])
        if mr.get("close"):
            injected += make_equiv("inBundleClose", mr["close"])
        return open_tag + body + injected + close_tag

    modified = pat.sub(replacer, owl_content)
    return modified, "".join(blank_nodes)


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — append PhenX hierarchy + object properties (once)
# ─────────────────────────────────────────────────────────────────────────────

def build_property_owl(ns: str) -> str:
    props = [
        ("inBundleExact",
         f"Links a CDE variable to PhenX Protocol(s) with cosine similarity "
         f">= {EXACT_THRESHOLD}."),
        ("inBundleClose",
         f"Links a CDE variable to PhenX Protocol(s) with cosine similarity "
         f">= {CLOSE_THRESHOLD} and < {EXACT_THRESHOLD}."),
    ]
    parts = ['\n  <!-- PhenX Bundle Object Properties -->\n\n']
    for local, comment in props:
        parts.append(
            f'  <rdf:Description rdf:about="{ns}{local}">\n'
            f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#ObjectProperty"/>\n'
            f'    <rdfs:label>{xe(local)}</rdfs:label>\n'
            f'    <rdfs:comment>{xe(comment)}</rdfs:comment>\n'
            f'  </rdf:Description>\n\n'
        )
    return "".join(parts)


def build_hierarchy_owl(collections, subcols, domains, proto_info, ns) -> str:
    dom_pfx = "PhenXDomain_"
    parts   = ['\n  <!-- PhenX Bundle Hierarchy -->\n\n']

    parts.append(
        f'  <rdf:Description rdf:about="{ns}Bundles">\n'
        f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
        f'    <rdfs:label>Bundles</rdfs:label>\n'
        f'    <rdfs:comment>Top-level class for all bundle types.</rdfs:comment>\n'
        f'  </rdf:Description>\n\n'
        f'  <rdf:Description rdf:about="{ns}bundle_phenx">\n'
        f'    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/>\n'
        f'    <rdfs:label>bundle_phenx</rdfs:label>\n'
        f'    <rdfs:comment>PhenX Toolkit bundle.</rdfs:comment>\n'
        f'    <rdfs:subClassOf rdf:resource="{ns}Bundles"/>\n'
        f'  </rdf:Description>\n\n'
    )

    for col_id, col in sorted(collections.items(), key=lambda x: x[1]["name"]):
        local = f"PhenXCollection_{safe_id(col['name'])}"
        parts.append(owl_class(f"{ns}{local}", col["name"],
                               f"PhenX Collection (ID {col_id}).",
                               f"{ns}bundle_phenx"))

    for sub_id, sub in sorted(subcols.items(), key=lambda x: x[1]["name"]):
        col    = collections.get(sub.get("col_id", ""), {})
        parent = (f"PhenXCollection_{safe_id(col['name'])}"
                  if col else "bundle_phenx")
        parts.append(owl_class(f"{ns}PhenXSubCollection_{safe_id(sub['name'])}",
                               sub["name"],
                               f"PhenX Sub-collection (ID {sub_id}).",
                               f"{ns}{parent}"))

    for dom_id, dom in sorted(domains.items(), key=lambda x: x[1]["name"]):
        sub    = subcols.get(dom.get("sub_id", ""), {})
        parent = (f"PhenXSubCollection_{safe_id(sub['name'])}"
                  if sub else "bundle_phenx")
        parts.append(owl_class(f"{ns}{dom_pfx}{safe_id(dom['name'])}",
                               dom["name"],
                               f"PhenX Domain (ID {dom_id}).",
                               f"{ns}{parent}"))

    for pid, proto in sorted(proto_info.items(), key=lambda x: x[1]["name"]):
        dom    = domains.get(proto.get("domain_id", ""), {})
        sub    = subcols.get(proto.get("sub_id", ""), {})
        parent = (f"{dom_pfx}{safe_id(dom['name'])}" if dom else
                  f"PhenXSubCollection_{safe_id(sub['name'])}" if sub else
                  "bundle_phenx")
        parts.append(owl_class(
            proto_uri(pid, proto_info, ns),
            proto["name"],
            f"PhenX Protocol {pid}. URL: {proto['url']}",
            f"{ns}{parent}",
        ))

    return "".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # 1. Load OWL + build crosswalk
    print("[1] Loading OWL …")
    owl_content = Path(args.owl).read_text(encoding="utf-8")
    ns, var_prefix, label_to_lid = scan_owl(owl_content)
    print(f"    Namespace  : {ns}")
    print(f"    Var prefix : {var_prefix}")
    print(f"    Crosswalk  : {len(label_to_lid):,} OWL classes indexed "
          f"by snake(label)")

    # 2. Run all-by-all
    print(f"\n[2] Running all-by-all: "
          f"'{args.phenx_collection}' vs '{args.source}' …")
    rows = run_all_by_all(
        args.chroma, args.phenx_collection, args.source, args.limit)

    # 3. Load PhenX schema
    print(f"\n[3] Loading {args.phenx} …")
    collections, subcols, domains, proto_info, slot_to_proto = \
        load_and_parse_phenx(args.phenx)

    # 4. Build match_results
    print(f"\n[4] Building match_results …")
    print(f"    inBundleExact : similarity >= {EXACT_THRESHOLD}")
    print(f"    inBundleClose : similarity >= {CLOSE_THRESHOLD} "
          f"and < {EXACT_THRESHOLD}")
    match_results = build_match_results(
        rows, label_to_lid, slot_to_proto, proto_info)

    # 5. Inject restrictions into existing OWL classes
    print(f"\n[5] Injecting owl:equivalentClass restrictions …")
    out, blank_nodes = inject_restrictions(
        owl_content, match_results, proto_info, var_prefix, ns)

    # 6. Append hierarchy + properties (skip if already present)
    already_props = f"{ns}inBundleExact" in owl_content
    already_hier  = f"{ns}bundle_phenx"  in owl_content
    if already_props:
        print(f"    [SKIP] Properties already present (incremental run)")
    if already_hier:
        print(f"    [SKIP] PhenX hierarchy already present (incremental run)")

    prop_owl = "" if already_props else build_property_owl(ns)
    hier_owl = "" if already_hier  else build_hierarchy_owl(
        collections, subcols, domains, proto_info, ns)

    if f'xmlns:{args.ns_prefix}=' not in out:
        out = out.replace('<rdf:RDF',
                          f'<rdf:RDF\n   xmlns:{args.ns_prefix}="{ns}"', 1)

    out = out.replace(
        "</rdf:RDF>",
        blank_nodes + prop_owl + hier_owl + "\n</rdf:RDF>",
    )

    # 7. Write
    print(f"\n[6] Writing → {args.out}")
    Path(args.out).write_text(out, encoding="utf-8")
    size_mb = Path(args.out).stat().st_size / 1024 / 1024

    n_exact = sum(len(v["exact"]) for v in match_results.values())
    n_close = sum(len(v["close"]) for v in match_results.values())
    print(f"""
── Summary ──────────────────────────────────────────────────────────────
  Input OWL      : {args.owl}
  PhenX schema   : {args.phenx}
  ChromaDB       : {args.chroma}
  Reference      : {args.phenx_collection}
  Source         : {args.source}
  OWL crosswalk  : {len(label_to_lid):,} classes
  Matched classes: {len(match_results):,}
  inBundleExact  : {n_exact:,} protocol links  (>= {EXACT_THRESHOLD})
  inBundleClose  : {n_close:,} protocol links  (>= {CLOSE_THRESHOLD}, < {EXACT_THRESHOLD})
  Output         : {args.out}  ({size_mb:.1f} MB)
─────────────────────────────────────────────────────────────────────────""")


if __name__ == "__main__":
    main()