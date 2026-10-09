# Input Brief: Postprocess Bloom Black Screen & Mobile Context Loss

Our WebGL 2.0 HDR bloom postprocess chain renders a solid black screen on several mid-range mobile devices and also turns black permanently after switching browser tabs on mobile Safari and Android Chrome.

Please debug the root causes across FBO attachment formats, bright-pass shader NaN propagation, VAO state, and `webglcontextlost` / `webglcontextrestored` recovery. Return a `runtime-compact` plan.
