# 04 - Subject Audit and Visual Hierarchy

## Purpose

Translate a visual subject into an ordered engineering checklist so shader instructions and pass budgets go to the cues viewers notice first. Build the silhouette before micro-detail.

## When to load

Load for `architecture` and `review` tasks whenever visual credibility, material fidelity, or feature-cut order matters.

## Inputs

- Subject description or reference capture
- Camera framing (close-up, medium shot, wide environment, orthographic UI)
- Project class and available GPU fragment/vertex budget

## Rules

### 1. Decompose the subject into five observable layers

Audit the target subject across five concrete layers before writing shader math:

1. **Primary silhouette & proportions** (macro bounding volumes, aspect ratios, horizon or contour read)
2. **Secondary structure** (major anatomical planes, architectural joints, terrain ridge hierarchy, widget bounds)
3. **Material response** (roughness contrast, Fresnel rim, subsurface scatter approximation, anisotropic glint)
4. **Lighting & depth separation** (key-to-fill ratio, contact shadows, sky/ground hemisphere split, atmospheric fog)
5. **Motion & temporal stability** (sub-pixel antialiasing, specular aliasing suppression, camera easing)

### 2. Rank every visual feature as P0, P1, or P2

Assign each feature a strict priority tier with an estimated GPU cost:

- **P0 - Identity-defining (must ship on all tiers)**
  - If missing, the subject fails to read at target framing.
  - Examples: cranial/jaw proportions and eye socket depth on a portrait bust; primary ridge/valley elevation and horizon fog on terrain; crisp glyph SDF edge and contrast in UI.
- **P1 - Material and depth reinforcement (enabled on `mid` and `high` tiers)**
  - Adds physical believability once P0 proportions hold.
  - Examples: multi-tap ambient occlusion, soft shadow penumbra, dual-lobe specular, detail normal maps.
- **P2 - Luxury polish (enabled only on `high` tier with verified frame-time headroom)**
  - High fragment cost per visible gain.
  - Examples: skin pore micro-displacement, volumetric god-rays, chromatic dispersion, full-res screen-space reflections.

### 3. Enforce the budget-pressure cut order

Cut luxury polish first. When frame time exceeds `gpuBudgetMs`, shed load in this exact sequence:

1. Disable P2 micro-detail passes and extra raymarch/filter taps.
2. Drop auxiliary passes (AO, bloom, volumetric fog) to `0.5x` resolution per axis (`0.25x` pixel count).
3. Clamp `targetDPR` toward `1.25-1.5` on high-DPI mobile screens.
4. Simplify P1 shadow/AO sample counts (for example `16 -> 6` taps).
5. Never distort P0 silhouette proportions or primary lighting read to save ALU cycles.

### 4. Define an explicit visual definition of done

Every subject audit must output 4-8 verifiable checks:

- **Portrait / organic SDF**: cranial-to-jaw ratio holds from 3 camera angles; eyelids wrap the corneal bulge; nose bridge and alar crease separate cleanly; roughness varies between forehead, nose tip, and cheeks.
- **Terrain / environment**: macro ridge silhouette reads without textures; slope/altitude material transitions avoid hard UV tiling seams; aerial perspective separates foreground, mid-ground, and distant peaks.
- **Data-vis / UI**: glyph edges stay anti-aliased across DPR `1.0-2.0`; hover/selection states read within 1 frame; zero z-fighting on overlapping layers.

## Failure modes

- Spending 40 fragment ALU ops on procedural pore noise while the skull or jaw silhouette is deformed
- Keeping P2 full-resolution postprocessing active while mobile FPS drops below 30
- Using vague words ("photorealistic", "cinematic") instead of naming the P0/P1 cues and pass costs

## Output contribution

Populate `deliverables` (P0/P1/P2 feature table and cut order), `decisions`, and visual-credibility `risks`.
