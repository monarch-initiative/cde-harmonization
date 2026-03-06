"""Download all English .xlsx CDE files from the NIH HEAL CDE Repository."""

import urllib.request
import re
import os
import time
import sys

BASE = "https://www.nih.gov"
REPO = (
    BASE
    + "/heal/heal-initiative-requirements/data-sharing-policy"
    + "/common-data-elements-cdes-program/cdes-repository"
)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "data/cde-heal"
TOTAL_PAGES = 14

os.makedirs(OUT_DIR, exist_ok=True)
seen = set()

for page in range(TOTAL_PAGES):
    url = f"{REPO}?page={page}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            html = r.read().decode("utf-8")
    except Exception as e:
        print(f"WARNING: could not fetch page {page}: {e}", file=sys.stderr)
        time.sleep(2)
        continue

    # Extract all .xlsx hrefs — skip files with "-spanish" in the name
    paths = re.findall(r'href="(/sites/default/files/CDEs/[^"]+\.xlsx)"', html)

    for path in paths:
        fname = os.path.basename(path)
        if "-spanish" in fname.lower():
            continue
        if fname in seen:
            continue
        seen.add(fname)
        file_url = BASE + path
        dest = os.path.join(OUT_DIR, fname)
        print(f"Downloading: {fname}")
        try:
            req2 = urllib.request.Request(file_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2) as r2, open(dest, "wb") as f:
                f.write(r2.read())
        except Exception as e:
            print(f"WARNING: could not download {fname}: {e}", file=sys.stderr)
        time.sleep(0.3)

print(f"Done. {len(seen)} unique English .xlsx files saved to {OUT_DIR}/")