# Playbook C: Agentic_AWS_Orchestration

This manual outlines the architectural standards and operational workflows for a production-grade 2D asset pipeline using agentic LLMs orchestrated on AWS. As Lead Technical Artist, the focus is on moving from "one-off" generations to a hardened, scalable system that translates Game Design Documents (GDDs) into engine-ready assets with automated quality gates
.
I. Agentic Orchestration Architecture
The pipeline utilizes a Multi-Agent System (MAS) where specialized LLM agents handle distinct phases of the creative process, following the UTPC (Understanding, Thinking, Planning, and Creation) framework
.
Orchestration Pattern: Use a Hierarchical Orchestrator to decompose complex GDD intents into sub-tasks for worker agents
.
Specialized Agent Roles:
Interpreter/GDD Parser: Extracts structured JSON specifications from natural language design documents, identifying object types, materials, and art styles
.
Planner/Scene Agent: Determines spatial layouts and object-relation-object triples (e.g., "Sword on Table") to ensure compositional logic
.
Executor/Painter Agent: Interacts with image APIs (Bedrock) or node-based engines (ComfyUI) to synthesize the visual content
.
Critic/QA Agent: A Vision-Language Model (VLM) that evaluates generated outputs against the original spec and issues iterative correction commands
.
II. Spec-to-Asset Workflow: From GDD to Implementation
The transition from design intent to visual realization follows a structured five-step pipeline
.
GDD Decomposition: The Interpreter Agent parses the GDD into a "Demand Manifest," identifying required scripts, assets, and dependencies
.
Semantic Enrichment: The agent expands brief GDD notes into detailed Subject-Context-Style prompts, specifying lighting, camera angles, and color palettes
.
Layout Planning: Instead of one-shot generation, the Planner adopts a divide-and-conquer strategy, reasoning about object groups by priority (e.g., background first, then hero assets)
.
Retrieval-Augmented Generation (RAG): To prevent "tool-use hallucinations," the agents query a vector database of existing 3D/2D model metadata or ComfyUI node documentation to select valid assets and configurations
.
Procedural Execution: The final plan is serialized into a JSON workflow or API call dispatched to the execution layer
.
III. Vision-Model Critique and QA Loops
A production gate requires multi-dimensional evaluation to reduce the 5–15% "bad output" rate typical of unmanaged pipelines
.
Critic-in-the-Loop (CITL): Use a VLM (e.g., Claude 3.5 Sonnet or Nova Lite) as an automated quality inspector
.
Acceptance Criteria: Configure criteria in plain text (e.g., "The armor must have gold filigree on a black base") rather than numerical thresholds
.
The Iterative Refinement Loop: The Critic issues one of four actions based on the VLM's analysis
:
STOP: Acceptance of the asset
.
CONTINUE: Apply localized edits to the current result (inpainting)
.
BACKTRACK: Revert to the previous version and try a new prompt variation
.
RESTART/FRESH START: Discard the current attempt due to major alignment failures
.
IV. MCP and Tool-Use Patterns
The Model Context Protocol (MCP) standardizes the interface between the agentic "brain" and the engine "tools"
.
Tool Orchestrator Pattern: Wrap complex workflows (e.g., character consistency with LoRAs) into single callable tools for the agent to reduce context bloat
.
Resource Gateway Pattern: Expose image asset libraries or model repositories as URI-addressed Resources for the agent to "read" before generating
.
ComfyUI Control Plane: Use an MCP server to allow the agent to author, repair, and execute node graphs directly in natural language
.
Async Patterns: For long-running generations (e.g., upscaling), tools should return a Job ID and a poll_job(id) tool to prevent model timeouts
.
V. AWS Deployment and Cost Controls
Asset production is optimized using Amazon Bedrock for speed and Amazon SageMaker for custom workflow hosting
.
AWS Bedrock Patterns (Nova & Stable Image)
Nova Canvas: Ideal for assets requiring heavy iteration via built-in inpainting, outpainting, and background removal
. Supports color palette control for brand compliance
.
Stable Image Ultra: Best for high-fidelity hero assets and standalone reference images
.
Batch Inference: For non-time-sensitive bulk production, use Bedrock Batch Jobs for a 50% cost discount
. Orchestrate these using AWS Step Functions to manage preprocessing and quotas
.
SageMaker Deployment (ComfyUI & Custom Models)
Multi-Model Endpoints (MME): Host multiple Stable Diffusion or Flux variants on a single GPU instance to maximize utilization and reduce costs
.
Asynchronous Inference: Use for large-scale generation jobs with automatic scaling that can scale to zero during idle periods
.
Managed Spot Training: Save up to 90% on training costs for custom LoRAs or model fine-tuning by using interruptible instances with automatic checkpointing to S3
.
Operational Cost Control
Warm Worker Pools: Maintain N warm containers to avoid the 60-120 second cold start penalty typical of serverless GPU architectures
.
Runtime Fingerprinting: Tag workers with a hash of their environment (ComfyUI version, model, nodes) to route jobs to the correct "hot" instance
.
Observability: Tag every job with its Workflow ID and Version to itemize GPU spend by asset type or team
. Use CloudWatch metrics like GPUUtilization to identify over-provisioned instances
.
VI. Summary Orchestration Flow
GDD Input: Designer uploads a document to an S3 bucket.
Analysis: Lambda triggers an Interpreter Agent on Bedrock (Claude) to generate a structured JSON spec
.
Planning: A Planner Agent designs the layout, retrieving existing assets via MCP Resource Gateway
.
Generation: The Executor Agent dispatches the plan to a SageMaker Endpoint hosting ComfyUI or a Bedrock API
.
QA: The Critic Agent (VLM) analyzes the result in S3; if it fails, it initiates the Refinement Loop
.
Delivery: Once verified, the asset is tagged with metadata and moved to the "Production-Ready" S3 prefix
.
Tell me more about Option A
Option B sounds good!
How do I implement the ComfyUI control plane?
