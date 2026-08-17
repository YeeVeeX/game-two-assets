# Master 2D Agent Playbook (AWS-backed agentic pipeline)

This blueprint defines a production-grade, AWS-orchestrated pipeline for 2D asset generation, integrating traditional art fundamentals with agentic Generative AI workflows.
I. Input & Orchestration Layer: The Agentic Brain
The pipeline initiates via a chat interface or S3-based GDD upload, processed through a Multi-Agent System (MAS) following the UTPC (Understanding, Thinking, Planning, and Creation) framework
.
1. Interpreter Agent (Model: Claude 3.5 Sonnet via Bedrock)
Task: Parses natural language or GDDs into a structured JSON Demand Manifest
.
Data Flow: Extracts object types, materials, art style (e.g., "Hi-Bit" pixel art), and resolution requirements (e.g., 320x180 base)
.
Tool: MCP Resource Gateway to query existing asset metadata to prevent redundant generations
.
2. Planner Agent (Model: Claude 3.5 Sonnet via Bedrock)
Task: Semantic Enrichment. Expands brief notes into "Subject-Context-Style" prompts
.
Logic Enforcement: Applies Art Direction constraints from Playbook A, such as "wonkiness" rules for asymmetry and color scripting for narrative shifts
.
Output: A serialized JSON workflow dispatched to the Execution Layer
.
II. Generation Layer: SageMaker & ComfyUI Execution
The execution layer utilizes a node-based architecture hosted on AWS SageMaker Multi-Model Endpoints (MME) to maximize GPU utilization
.
Primary Engine: ComfyUI Control Plane
.
Base Models:
Flux.1-dev: For high prompt adherence and structural complexity
.
SDXL (Dream Shaper XL v2.0): For seamless tiling or lower VRAM overhead tasks
.
Identity & Style Anchoring:
LoRA (Flagship Assets): Trained via Kohya_ss; 15–30 images, learning rate 1e-4, 10–15 epochs
.
IP-Adapter (Side Assets): FaceID Plus v2 for SDXL. Set ip_adapter_scale to 0.65 to preserve action freedom
.
Structural Control (ControlNet Stacking):
Slot 1 (Structure): Depth Anything or Canny (Weight 0.7–0.75) to lock the character grid
.
Slot 2 (Action): OpenPose for precise limb placement
.
Schedule: Start 0%, End 50%, Strength 0.5 to allow for natural texture rendering in final diffusion steps
.
Sprite Sheet Logic:
Node: Aseprite Visual Novel Atlas to define Neutral, Happy, and Angry frames in a horizontal/grid layout
.
III. Post-Processing & Deterministic Polish
Raw outputs are passed through a deterministic engineering layer to ensure engine readiness.
Background Removal: InSPyReNet or BiRefNet using Color Decontamination (-dc) to eliminate rim halos
.
Detailing: ADetailer for automated face and hand redraws
.
Pixel Art Enforcement:
Technique: Generate at 512x512, then downscale by 4x using k-centroid scaling to achieve 32x32 purity
.
Tool: WAS Node Suite for palette enforcement (limited to 8-16 colors)
.
Atlas Packing: FastPack (Rust-based) or TexturePacker using the MaxRects algorithm with "ShortSideFit"
.
IV. Automated QA & Vision-Critique Loop
A Vision-Language Model (VLM) serves as a Critic-in-the-Loop (CITL) to reduce the failure rate of the pipeline
.
Critic Agent (Model: Claude 3.5 Sonnet or Nova Lite): Analyzes the asset against the original JSON Demand Manifest
.
QA Gates (Pass/Fail Criteria):
Identity: Does the character match the LoRA/IP-Adapter reference?
Purity: Is the pixel size consistent across the sheet? (No resizing within engine)
.
Readability: Does UI text meet the 28px/1080p legibility standard?
.
Failure Handling (Iterative Actions):
CONTINUE: Apply localized inpainting for minor errors
.
BACKTRACK: Revert to previous seed/prompt version
.
RESTART: Discard and regenerate if major alignment failures occur
.
V. Data Flow & Final Delivery
The final stage automates the transition from cloud generation to version-controlled game assets.
Naming Convention: category_role_variant_strip[framecount].png (e.g., char_hero_attack_strip12.png)
.
Metadata: Generate JSON Hash metadata for engine integration (Unity/Godot/Phaser)
.
Optimization: Alias Detection to deduplicate identical sprites and Trimming to remove transparent borders while storing offsets
.
Storage: Verified assets move to the "Production-Ready" S3 prefix, triggering a notification to the Lead Technical Artist
.
Cost Control: Use AWS Step Functions for batch inference (50% discount) and Warm Worker Pools to eliminate 60-120s cold start penalties
.
