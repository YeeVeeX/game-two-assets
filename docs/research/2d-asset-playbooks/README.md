# 2D asset playbooks (external research corpus)

Distilled from a 138-source Gemini Notebook research operation (2026-08-17).
Raw provenance and method: `knowledge/sources/gemini-2d-asset-research-2026-08-17/PROVENANCE.md`.

## Precedence

These documents are **reference research, subordinate to `docs/asset-contract.md`
and `AGENTS.md`**. Where they conflict with the contract, the contract wins.
In particular: the playbooks describe pipelines that emit AI rasters as final
assets; in this repository a general-model raster is only ever a *concept*
(`ai_reconstruction` origin requires native re-authoring at 32x32).

## Contents

| File | Domain | Backing notebook (source-grounded chat) |
|---|---|---|
| `playbook-a-traditional-foundations.md` | Pixel-art fundamentals, art direction, animation, tilesets, UI, open-source tooling | [2D_Foundations_Traditional](https://notebook.google.com/notebook/6de7134e-c63a-410d-9b78-0f70fc60c3a2) (45 sources) |
| `playbook-b-genai-comfy-pipelines.md` | ComfyUI/SDXL/Flux, LoRA style consistency, ControlNet/IP-Adapter, post-processing | [2D_GenAI_Comfy_Pipelines](https://notebook.google.com/notebook/2a18eeb6-74b5-4c9a-afa9-896efe23f431) (26 sources) |
| `playbook-c-agentic-aws-orchestration.md` | Agent architectures, spec-to-asset, vision critique loops, Bedrock/SageMaker | [Agentic_AWS_Orchestration](https://notebook.google.com/notebook/9a78314f-35de-4ed8-81dc-d01639dfc007) (67 sources) |
| `master-agentic-pipeline-blueprint.md` | End-to-end AWS agentic pipeline blueprint | [Master_2D_Agent_Playbook](https://notebook.google.com/notebook/3d9c005f-06fa-4707-a096-2070a3b5ddc7) |

## Trust level

- Master blueprint: 21/22 distinctive claims trace verbatim to playbooks A-C.
- Playbooks: NotebookLM-grounded summaries; the tool has previously dressed
  model priors as quotes. **Verify any load-bearing claim** (parameter values,
  model names, costs) in the backing notebook's cited source before building
  on it. Deeper questions: ask the backing notebook's chat, then re-verify.
