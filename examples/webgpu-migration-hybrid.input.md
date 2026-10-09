# Input Brief: WebGL 2.0 to WebGPU Migration for Hybrid Mesh + Volumetric Renderer

We have an existing WebGL 2.0 hybrid renderer (forward mesh pass + fullscreen volumetric raymarch pass) that currently uses scattered `gl.uniform*` calls, mutable FBO state, and GLSL ES 3.00 clip-space conventions.

Please design a dual-backend migration plan to WebGPU + WGSL that preserves our WebGL 2.0 backend as a fallback, shares CPU-side uniform buffer layouts without repacking, and prevents derivative or clip-space depth bugs. Return an `authoring-base` plan.
