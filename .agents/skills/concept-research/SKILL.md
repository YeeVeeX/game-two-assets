---
name: concept-research
description: Concept-stage art generation and 2D asset research for game-two-assets. Use when exploring art direction, generating AI concept references (Bedrock), building visual-critique rubrics, designing sprite/tileset/animation approaches, or deciding generation-vs-reconstruction workflow. Routes to the curated playbook corpus and its four backing NotebookLM notebooks. NOT for export/release mechanics (tools/ + docs/asset-contract.md govern those) and never produces production sprites directly.
---

# Concept research (game-two-assets)

Everything here is subordinate to `docs/asset-contract.md` and `AGENTS.md`
(repo root). Non-negotiables inherited from them:

- A general-model raster is a **concept**, never a production sprite. The only
  path to runtime is native re-authoring (`ai_reconstruction`) at 32x32,
  through `tools/` and the release gate.
- No lore: generic snake_case IDs only (`player_1_lane_a`, `zone_1_floor_01`).
- No named-living-artist imitation; no storing references whose license
  forbids it.
- Do not touch `../game-two` while v17 is open.

## Knowledge routing (in order)

1. `docs/research/2d-asset-playbooks/` — distilled playbooks (A: traditional
   foundations, B: ComfyUI/GenAI, C: agentic AWS, master blueprint). Read the
   README there for trust level and precedence.
2. Backing NotebookLM notebooks (URLs in that README) — ask their chat for
   deeper, citation-backed answers; re-verify quotes against the cited source
   before relying on them (known fabrication history).
3. `hub kb query --domain uiux-design` — visual-critique rubric inputs
   (global vision-check doctrine).

## Concept generation (AWS Bedrock, already owned)

Use the global `bedrock-image` CLI (see the global `bedrock-image-gen` skill
for flags; highest quality = Stable Image Ultra then 4x upscale).

1. Generate into `concepts/` (Git LFS; exploratory only).
2. Capture provenance **at generation time** — the contract requires it for
   any later `ai_reconstruction`. Sidecar `<name>.provenance.json` next to the
   image:

```json
{
  "provider": "AWS Bedrock",
  "model": "<exact model id from bedrock-image output>",
  "generation_date": "YYYY-MM-DD",
  "prompt": "<full prompt text>",
  "seed": "<seed or 'unavailable'>",
  "terms_url": "<provider terms URL>",
  "terms_retrieved": "YYYY-MM-DD",
  "concept_path": "concepts/<file>.png",
  "material_edits": []
}
```

3. Prompting for usable concepts (playbook A/B distillate): state projection
   (top-down, no overhang), silhouette-first readability, restricted palette
   intent (sprint-0 exports allow max 8 opaque colors), and the role's
   baseline color from `manifests/runtime-baseline.json` as dominant. Generate
   large (1MP); the concept informs pixel placement, it is never downscaled
   into an export.

## Critique loop (before any reconstruction effort)

Deterministic verification doctrine (Rule 2): scripted input + captured
artifact + critique, accuracy and presentation scored separately.

- Contact sheet over real game palettes: `tools/make_contact_sheet.py`;
  motion: `tools/make_motion_sheet.py` + `tools/motion_metrics.py`.
- Rubric gates distilled from the playbooks, applied on top of the contract's
  visual gate:
  - **Identity**: silhouette reads at native 1x; facing/attack/hurt tells
    survive; role color dominant, white possession ring stays readable.
  - **Purity**: consistent pixel size, hard alpha, no antialiasing, bounds
    inside `[2,2,29,29]`, anchor `[16,30]`.
  - **Readability**: legible over actual dark floors and light walls at 1x;
    magnified views are for diagnosis only, the native view decides.
- Verdicts land in `reviews/<lane>/rationale.md` (accuracy vs presentation,
  winner/reject, unresolved risks) per existing convention.

## When the task is actually export/release

Stop — that is `tools/` + `docs/asset-contract.md` territory (spec →
`build_sources.py` → Aseprite export → `asset_gate.py` → release manifest).
This skill only covers what happens before native pixels exist.
