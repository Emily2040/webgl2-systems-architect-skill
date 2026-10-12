# Input Brief: Instanced Mesh VAO + std140 UBO Implementation

Implement a self-contained WebGL 2.0 instanced mesh pass for 4,096 CAD mechanical pins (`raster-mesh`) that eliminates per-draw `gl.uniformMatrix4fv` overhead by binding a dedicated VAO, a 16-byte-aligned `std140` `FrameBlock` UBO, per-instance transform columns using `gl.vertexAttribDivisor`, and `gl.drawElementsInstanced`. Return a `runtime-compact` plan.
