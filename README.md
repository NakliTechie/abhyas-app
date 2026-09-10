# Abhyas — student-facing maths practice

A calm, self-paced practice app for the **abhyas** curriculum-content engine, built for the [naklios.dev](https://naklios.dev) family. Class 1–5 (K5) Mathematics. Runs standalone in any browser, or as a hosted app inside a naklios desktop (e.g. the [naklios-kids](../naklios-kids) desktop).

- **Browse** by strand → concept, respecting grade banding (Class 1–5).
- **Practice drills** — endless procedural stream per concept, exact machine-checkable answers, instant feedback across all 9 answer types.
- **Take a quiz** — multiple-choice sets; every wrong answer surfaces the *named misconception* (the diagnostic value from abhyas), not just right/wrong.
- **Mock test** — build a blueprint over classes / topics / difficulty / length, answer test-style, then get a scored report: per-topic breakdown + which misconceptions were hit.
- **Progress** — per-concept mastery dashboard (per-topic bars, keep-practising list, common misconceptions), stored only on the viewer's device. No account, no server, no telemetry.

## Runs under naklios

The app vendors the naklios cooperative SDK ([`sdk/naklios.js`](sdk/naklios.js)) and is a well-behaved guest:

- **Theme** — maps the host's theme tokens onto its own CSS variables (`naklios.theme.onChange`).
- **Storage adapter** — writes progress to `naklios.fs` (`progress.json`) when the host offers storage; falls back to `localStorage` standalone. Detect → attempt → fall back, always safe.
- **Lifecycle** — `ready()`, dynamic `title()`, host-aware "Options" (Close app), capability-aware storage copy.

The SDK is a no-op standalone, so the same file works in a plain tab and inside a naklios window. Refresh the vendored copy from `NakliTechie/nakliOS → sdk/naklios.js`.

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

Shipped: **browse → drill → quiz → mock test → progress dashboard**, per-concept mastery, and naklios host integration (theme, storage adapter, lifecycle). Next layers: chapter reading + video, AI Q&A (host `naklios.ai`), more bands/subjects as abhyas emits them.

Content © the abhyas engine · app for the naklios.dev family.
