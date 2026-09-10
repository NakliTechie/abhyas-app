#!/usr/bin/env python3
"""Build data/maths-k5.js from the abhyas content engine (read-only source).

Wraps the assembled dataset + the concept knowledge graph into a single
window global so the app works both served and from file://.
Run from the abhyas-app repo root:  python3 tools/build-data.py
"""
import json, os, sys

SRC = os.environ.get("ABHYAS_SRC", os.path.expanduser("~/Code/abhyas/content/maths/k5"))
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "maths-k5.js")


def main():
    ds_path = os.path.join(SRC, "dataset.json")
    cj_path = os.path.join(SRC, "concepts.json")
    if not (os.path.exists(ds_path) and os.path.exists(cj_path)):
        sys.exit(f"abhyas source not found under {SRC} (set ABHYAS_SRC)")

    with open(ds_path) as f:
        ds = json.load(f)
    with open(cj_path) as f:
        cj = json.load(f)

    bundle = {
        "meta": ds["meta"],
        "counts": ds["counts"],
        "concepts": cj["concepts"],
        "concepts_meta": cj["meta"],
        "mcqs": ds["mcqs"],
        "drills": ds["drills"],
        "snapshot_source": "NakliTechie/abhyas content/maths/k5 (read-only)",
    }

    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("/* Snapshot of abhyas K5 Mathematics content. Generated — do not hand-edit. */\n")
        f.write("window.ABHYAS_DATA = ")
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print(f"wrote {out} ({os.path.getsize(out)/1e6:.2f} MB)")
    print(f"concepts: {len(bundle['concepts'])}  mcqs: {len(bundle['mcqs'])}  drills: {len(bundle['drills'])}")


if __name__ == "__main__":
    main()
