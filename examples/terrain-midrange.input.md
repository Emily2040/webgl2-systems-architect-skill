# Example Input - Terrain Midrange Optimization

My terrain scene runs in WebGL 2.0 on mid-range Android but drops frames when the camera flies low.
It uses a mesh terrain, water, atmospheric fog, and three fullscreen postprocess passes.
I have code already, but no GPU capture.
I need a practical optimization review: what to cut first, what to measure, and what should stay async.
