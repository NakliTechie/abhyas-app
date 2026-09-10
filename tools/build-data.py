#!/usr/bin/env python3
"""Build the multi-subject Abhyas data bundle from the abhyas content engine (read-only).

Emits:
  data/catalog.js         -> window.ABHYAS_CATALOG   (small: one summary row per graph)
  data/graph-<id>.js      -> window.ABHYAS_GRAPHS['<id>'] = {meta, concepts, mcqs, drills}

Each graph is a separate file so the app lazy-loads only the subject the student opens
(time-to-first-value stays fast; the catalog alone is a few KB). Concept id is the join key.

Run from the abhyas-app repo root:  python3 tools/build-data.py
Source root override:  ABHYAS_SRC=/path/to/abhyas/content
"""
import json, os, sys

SRC = os.environ.get("ABHYAS_SRC", os.path.expanduser("~/Code/abhyas/content"))
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "data")

SUBJECT_SHORT = {"Mathematics": "Maths", "Environmental Studies": "EVS"}
# band dir -> (order, label)
BANDS = {"k5": (0, "Class 1–5"), "6-10": (1, "Class 6–10"), "11-testprep": (2, "Class 11–12 · JEE/NEET")}
SUBJECT_ORDER = ["maths", "physics", "chemistry", "biology", "evs",
                 "english", "history", "geography", "civics", "economics"]


def band_key(band):
    return BANDS.get(band, (9, band))[0]


def discover():
    graphs = []
    for subject in sorted(os.listdir(SRC)):
        sdir = os.path.join(SRC, subject)
        if not os.path.isdir(sdir):
            continue
        for band in sorted(os.listdir(sdir)):
            bdir = os.path.join(sdir, band)
            cj = os.path.join(bdir, "concepts.json")
            ds = os.path.join(bdir, "dataset.json")
            if os.path.exists(cj) and os.path.exists(ds):
                graphs.append((subject, band, cj, ds))
    # order: subject (by SUBJECT_ORDER), then band
    def okey(g):
        subj, band = g[0], g[1]
        si = SUBJECT_ORDER.index(subj) if subj in SUBJECT_ORDER else 99
        return (band_key(band), si, subj)
    return sorted(graphs, key=okey)


def main():
    if not os.path.isdir(SRC):
        sys.exit(f"abhyas content not found under {SRC} (set ABHYAS_SRC)")
    os.makedirs(os.path.abspath(OUTDIR), exist_ok=True)

    found = discover()
    if not found:
        sys.exit(f"no <subject>/<band>/(concepts.json+dataset.json) pairs under {SRC}")

    catalog = []
    total_mcq = total_drill = total_concept = 0
    for subject, band, cj_path, ds_path in found:
        with open(cj_path) as f:
            cj = json.load(f)
        with open(ds_path) as f:
            ds = json.load(f)
        gid = f"{subject}-{band}"
        concepts = cj["concepts"]
        mcqs = ds.get("mcqs", [])
        drills = ds.get("drills", [])
        meta = dict(ds.get("meta", {}))
        subj_name = meta.get("subject") or subject.title()
        short = SUBJECT_SHORT.get(subj_name, subj_name)
        grades = meta.get("grades") or sorted({c.get("grade") for c in concepts if c.get("grade") is not None})

        # strand summary (ordered as concepts appear)
        strand_order, strand_n = [], {}
        for c in concepts:
            s = c.get("strand") or "—"
            if s not in strand_n:
                strand_n[s] = 0
                strand_order.append(s)
            strand_n[s] += 1

        # per-concept drill counts (so the UI can show/enable drills without loading them)
        drill_counts = {}
        for d in drills:
            cid = d.get("concept_id")
            if cid:
                drill_counts[cid] = drill_counts.get(cid, 0) + 1

        # main file: concepts + mcqs (+ drill counts) — powers browse/quiz/mock/dashboard
        graph = {"id": gid, "meta": meta, "concepts": concepts, "mcqs": mcqs, "drillCounts": drill_counts}
        out = os.path.abspath(os.path.join(OUTDIR, f"graph-{gid}.js"))
        with open(out, "w") as f:
            f.write(f"/* Snapshot of abhyas {subject}/{band} — concepts + MCQs (read-only source). Generated — do not hand-edit. */\n")
            f.write("(window.ABHYAS_GRAPHS=window.ABHYAS_GRAPHS||{})[" + json.dumps(gid) + "]=")
            json.dump(graph, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")
        sz = os.path.getsize(out) / 1e6

        # drills file: emitted only when the graph has drills — lazy-loaded on first drill
        dsz = 0.0
        if drills:
            dout = os.path.abspath(os.path.join(OUTDIR, f"graph-{gid}-drills.js"))
            with open(dout, "w") as f:
                f.write(f"/* Snapshot of abhyas {subject}/{band} — drills (read-only source). Generated — do not hand-edit. */\n")
                f.write("(window.ABHYAS_DRILLS=window.ABHYAS_DRILLS||{})[" + json.dumps(gid) + "]=")
                json.dump({"id": gid, "drills": drills}, f, ensure_ascii=False, separators=(",", ":"))
                f.write(";\n")
            dsz = os.path.getsize(dout) / 1e6

        catalog.append({
            "id": gid, "subject": subj_name, "subjectShort": short,
            "band": band, "bandLabel": BANDS.get(band, (9, band))[1],
            "grades": grades,
            "conceptCount": len(concepts), "mcqCount": len(mcqs), "drillCount": len(drills),
            "strands": [{"name": s, "n": strand_n[s]} for s in strand_order],
            "file": f"data/graph-{gid}.js",
            "drillsFile": (f"data/graph-{gid}-drills.js" if drills else None),
        })
        total_mcq += len(mcqs); total_drill += len(drills); total_concept += len(concepts)
        print(f"  {gid:24} {len(concepts):4} concepts · {len(mcqs):5} mcqs · {len(drills):6} drills · main {sz:.2f} MB{f' + drills {dsz:.2f} MB' if drills else ''}")

    cat = {"version": 1, "graphs": catalog,
           "totals": {"graphs": len(catalog), "concepts": total_concept, "mcqs": total_mcq, "drills": total_drill}}
    cout = os.path.abspath(os.path.join(OUTDIR, "catalog.js"))
    with open(cout, "w") as f:
        f.write("/* Abhyas catalog — one summary row per graph. Generated — do not hand-edit. */\n")
        f.write("window.ABHYAS_CATALOG = ")
        json.dump(cat, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"\ncatalog.js: {len(catalog)} graphs · {total_concept} concepts · {total_mcq} mcqs · {total_drill} drills ({os.path.getsize(cout)/1e3:.1f} KB)")


if __name__ == "__main__":
    main()
