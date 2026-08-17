# Playbook B: 2D_GenAI_Comfy_Pipelines

Definitive Manual for AI-Assisted 2D Game Asset Generation
As Lead Technical Artist, this manual defines the deterministic generation layer for our automated asset pipeline. This workflow moves AI from a "slot machine" of random results into a rigorous engineering discipline suitable for production-scale asset delivery
.
Phase 1: Foundational ComfyUI Architecture
Selection of the base model dictates the technical constraints of the entire pipeline. Consistency is achieved by locking these models early; changing models mid-project will break visual cohesion
.
Model Selection:
Flux.1-dev: The primary choice for assets requiring extreme prompt adherence and complex structural conditioning
.
SDXL (Dream Shaper XL v2.0): Preferred for assets requiring seamless tiling or lower VRAM overhead (8GB vs Flux's higher requirements)
.
Essential Node Stacks:
Loaders: Use IP-Adapter Unified Loader for identity and standard Checkpoint Loaders for style LoRAs
.
Conditioning: Implement Dual CLIP (t5xxl + clip_l) for Flux or standard CLIP for SDXL
.
Deterministic Anchoring: Lock random seeds for minor iterations, but rely on ControlNet and IP-Adapter for identity/pose
.
Phase 2: Character Identity & Style Consistency
Style consistency is maintained through a hybrid of deep training (LoRA) and zero-shot reference (IP-Adapter).
1. LoRA Training (Style & Major Characters)
For flagship characters appearing in 50+ panels, a custom LoRA is required
.
Tool: Kohya_ss
.
Dataset Curation: 15–30 high-quality images (1024x1024)
.
Training Parameters: 10 repeats per image, 10–15 epochs, learning rate 1e-4 for UNet
.
Tagging: Use WD14 captioning to establish a unique Trigger Word
.
2. IP-Adapter (Side Characters & Quick Iteration)
Use for zero-shot identity preservation without training time
.
Industry Standard: FaceID Plus v2 for SDXL
.
Node Setup: Set ip_adapter_scale to 0.65
. Scales above 0.7 often copy the reference pose too strictly, killing action freedom
.
Commercial Compliance: Stick to the CLIP-based path for commercial work to avoid non-commercial InsightFace dependencies
.
Phase 3: Structural Control & Sprite-Sheet Layout
To ensure every sprite in a set aligns perfectly, we use explicit geometric constraints rather than text-only prompts
.
ControlNet Stacking:
Slot 1 (Structure): Depth Anything or Canny at weight 0.7–0.75 for locking character grids/sheets
.
Slot 2 (Action): OpenPose for specific limb placement
.
Control Scheduling: Set start_percent 0 and end_percent 0.5 with strength 0.5
. This locks the silhouette early in the diffusion process while allowing the model to render natural textures in the final steps
.
Sprite Sheet Logic: Use the Aseprite Visual Novel Atlas node to define frames (Neutral, Happy, Angry) and layout direction (Horizontal/Grid)
.
Phase 4: Post-Processing & Finishing
Raw AI output requires a "deterministic polish" layer before engine ingestion.
1. Background Removal
Node: InSPyReNet or BiRefNet
.
Parameters: Use Color Decontamination (-dc) to remove colored halos (e.g., green rim from a grass background) around fine hair/edges
.
2. Super-Resolution & Detail
Upscalers: Real-ESRGAN for real-world textures; 4x-Fatal-Anime for stylized assets
.
Detailing: Use ADetailer (After Detailer) to automatically detect and redraw faces/hands with high definition
.
3. Pixel Art & Palette Enforcement
Technique: For pixel-perfect 32x32 assets, generate at 512x512 and downscale by a factor of 4 using k-centroid scaling
.
Nodes: Use the WAS Node Suite for palette enforcement and traditional pixelization
.
Phase 5: Atlas Packing & Engine Export
The final step automates the transition from image batches to game-ready textures.
Texture Atlas Packing: Use FastPack (Rust-based) or TexturePacker
.
Algorithm: MaxRects with "ShortSideFit" for optimal density
.
Optimization:
Alias Detection: Deduplicate pixel-identical sprites
.
Trimming: Remove transparent borders while storing offsets to reduce file size
.
Export Formats: Generate JSON Hash metadata for Phaser/Unity/Godot integration
.
How do I configure the Aseprite Visual Novel Atlas node?
Explain IP-Adapter's 'Plus Face' vs 'FaceID' presets.
Can I use ControlNet Tile for 2D texture upscaling?
