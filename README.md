# Abhyas — student-facing maths practice

A calm, self-paced practice front-end for the **abhyas** curriculum-content engine, styled as a fork of [naklios.dev](https://naklios.dev). Class 1–5 (K5) Mathematics.

- **Browse** by strand → concept, respecting grade banding (Class 1–5).
- **Practice drills** — endless procedural stream per concept, exact machine-checkable answers, instant feedback.
- **Take a quiz** — multiple-choice sets; every wrong answer surfaces the *named misconception* (the diagnostic value from abhyas), not just right/wrong.
- **Progress** — per-concept mastery, stored only in the viewer's browser. No account, no server, no telemetry.

## How it's built

- **Single-file app.** Everything is in [`index.html`](index.html) — zero build step, deployable as static.
- **Data snapshot.** [`data/maths-k5.js`](data/maths-k5.js) is a read-only snapshot of abhyas `content/maths/k5` (102 concepts, 510 MCQs, 11,008 drills), assigned to `window.ABHYAS_DATA` so the app works both when served and when opened directly from `file://`.
- **Sovereign.** Progress lives in `localStorage` (`abhyas.progress.v1`). Nothing leaves the device.

## Run it

Open `index.html` directly, or serve the folder:

```bash
python3 -m http.server 4178 --directory .
```

Then visit `http://127.0.0.1:4178`.

## Regenerating the data snapshot

The snapshot is generated from the abhyas repo (do **not** edit abhyas from here):

```bash
python3 tools/build-data.py
```

## Status

First working loop shipped: **browse → practice a drill → answer an MCQ**, with per-concept progress. Next layers: mock tests (blueprint over strand/grade/difficulty) and a mastery dashboard.

Content © the abhyas engine · app styled for the naklios.dev house shell.
