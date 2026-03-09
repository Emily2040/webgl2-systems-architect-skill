# Module 04 - Subject Audit

## Purpose

Before geometry, shading, or optimization, define what the scene must visibly contain. This prevents the coder's ancient curse: polishing the wrong thing while the obvious missing feature sits in the middle of the frame wearing a fake mustache.

## Audit output

Build a checklist grouped into:

- `geometry`
- `materials`
- `lighting`
- `animation`
- `interaction` when relevant
- `presentation` for UI or data visualization
- `polish`
- `out-of-scope`

Each item gets:
- `priority`: `P0 | P1 | P2`
- `feature`
- `why_it_matters`
- `how_it_will_be_represented`
- `failure_if_missing`

## Evidence discipline

Only include details that are:
- explicitly requested by the user
- implied by the subject's anatomy, physics, or semantics
- supported by provided references or code

Do not fabricate decorative details just to make the answer sound rich.

## Subject templates

### Anatomical subjects

For faces, hands, bodies, creatures, and character busts, audit:
- landmark forms
- asymmetry
- soft-tissue transitions
- cavity lighting
- material zoning
- wet vs dry specular behavior
- motion cues such as blink, lip tension, or jaw motion

Avoid generic phrases like "realistic skin." Replace them with concrete requirements such as:
- per-zone albedo drift
- roughness variation
- pore or wrinkle scale
- subsurface thickness hints
- eyelid-corneal overlap
- nostril or ear cavity occlusion

### Environments and terrain

Audit:
- macro silhouette
- meso-scale erosion or structural breakup
- micro-detail
- slope-dependent materials
- atmosphere, haze, or fog
- water or reflective surfaces
- shadow storytelling
- horizon treatment

### Vehicles, props, hard-surface scenes

Audit:
- major silhouette breaks
- panel seams
- wear patterns
- material contrast between painted, raw, rubber, glass, or emissive parts
- motion-critical pieces such as wheels, suspension, or instrument states

### UI and data visualization

Audit:
- information hierarchy
- legibility at target scale
- state changes
- latency sensitivity
- color semantics
- interaction affordances
- accessibility or color-blind safety when relevant

## Definition of done

Translate the audit into a visible acceptance test:

- what must be readable at thumbnail scale
- what must hold up at close inspection
- which details can fall away on low tier hardware
- which omissions will make viewers immediately distrust the result

## Performance link

The audit must also feed performance priorities:

- P0 features survive on low tier paths
- P1 features may be reduced or approximated
- P2 features are quality toggles or high-tier only

This is how the visual spec talks to the hardware budget instead of living on a separate planet.

## Output fields

Return:

- `subject_checklist`
- `definition_of_done`
- `tiered_feature_gates`
- `missing_obvious_features`
- `reference_dependencies`

## Common failure modes

- confusing detail density with subject fidelity
- optimizing micro-detail before the silhouette reads correctly
- adding expensive polish to features the viewer will never notice
- forgetting medium-distance cues that sell the subject before close-up detail does
