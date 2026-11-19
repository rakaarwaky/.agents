---
name: ascii-video
description: "ASCII video: convert video/audio to colored ASCII MP4/GIF."
when-to-use: "Use when the user wants ASCII video — video-to-ASCII conversion, audio-reactive music visualizers, generative ASCII animations, hybrid video+audio, text/lyrics overlays, or TTS narration videos (MP4, GIF, image sequence)."
argument-hint: "<video-to-ascii|audio-reactive|generative|hybrid|lyrics|tts> <input> [output.mp4]"
---

# ASCII Video Production Pipeline

Construct self-contained Python renderers using NumPy, Pillow, and ffmpeg to generate cinematic colored ASCII character videos across audio-reactive, generative, and hybrid input modes.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Define artistic concepts and visual styling explicitly before code generation to meet cinematic quality standards. | Verify aesthetic plan and scene transitions before executing renderer. |
| R2 | Apply adaptive `tonemap()` algorithms exclusively; never multiply dark canvas values by static scalar constants. | Inspect rendering code to ensure adaptive tonemapping is implemented. |
| R3 | Introduce per-section visual variations in background effects, character palettes, color schemes, and shader intensity. | Verify scene configuration varies across distinct timeline segments. |
| R4 | Incorporate at least one project-specific custom palette, procedural effect, or unique visual element per project. | Check codebase for customized visual effects or custom character maps. |
| R5 | Build single-file Python renderers with hardware profile detection using NumPy, Pillow, and ffmpeg pipelines. | Confirm renderer script is self-contained and manages process pipelines cleanly. |
| R6 | Verify test frames at key timestamps meet minimum brightness thresholds (`canvas.mean() > 8`) and match target formats. | Inspect sample rendered frames and test media container output. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Workflow | [`references/workflow.md`](references/workflow.md) | 4-step build sequence: creative vision, technical design, script component order, quality verification. |
| Creative standard | [`references/creative-standard.md`](references/creative-standard.md) | Creative rubric: first-render excellence, proactively creative, cohesive aesthetic, dense/layered, per-section variation, project-specific invention. |
| Pipeline architecture | [`references/architecture.md`](references/architecture.md) | 6-stage pipeline, grid system, resolution presets, font selection, character palettes, color system (HSV + OKLAB + discrete RGB + harmony), `_render_vf()`, GridLayer. |
| Composition | [`references/composition.md`](references/composition.md) | 20 pixel blend modes, `blend_canvas()`, multi-grid composition, adaptive `tonemap()`, `FeedbackBuffer`, `PixelBlendStack`, masking/stencil system. |
| Effects | [`references/effects.md`](references/effects.md) | Effect building blocks: value field generators, hue fields, noise/fBM/domain warp, voronoi, reaction-diffusion, cellular automata, SDFs, strange attractors, particle systems, coordinate transforms, temporal coherence. |
| Shaders | [`references/shaders.md`](references/shaders.md) | `ShaderChain`, `_apply_shader_step()` dispatch, 38-shader catalog, audio-reactive scaling, transitions, tint presets, output format encoding, terminal rendering. |
| Scenes | [`references/scenes.md`](references/scenes.md) | Scene protocol, `Renderer` class, `SCENES` table, `render_clip()`, beat-synced cutting, parallel rendering, scene design patterns, worked examples, design checklist. |
| Inputs (all 6 modes) | [`references/inputs.md`](references/inputs.md) | Mode table + audio analysis (FFT, bands, beats), video sampling, image conversion, text/lyrics, TTS integration (ElevenLabs, voice assignment, audio mixing). |
| Optimization | [`references/optimization.md`](references/optimization.md) | Hardware detection, quality profiles, vectorized patterns, parallel rendering, memory management, performance budgets. |
| Troubleshooting | [`references/troubleshooting.md`](references/troubleshooting.md) | NumPy broadcasting traps, blend mode pitfalls, multiprocessing/pickling, brightness diagnostics, ffmpeg issues, font problems, common mistakes. |
| Critical notes | [`references/implementation-notes.md`](references/implementation-notes.md) | `tonemap()` code, font cell height (macOS), ffmpeg pipe deadlock, font compatibility, per-clip architecture, performance budgets. |
| Creative divergence | [`references/creative-divergence.md`](references/creative-divergence.md) | Use only when the user requests experimental/creative/unique output: Forced Connections, Conceptual Blending, Oblique Strategies. |
