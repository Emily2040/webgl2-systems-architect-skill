# Example Input - Terrain Midrange Optimization

My terrain scene runs in WebGL 2.0 on mid-range Android devices, but frame time spikes well above 16.67 ms whenever the camera flies low over the water and terrain horizon with three fullscreen postprocess passes active.
It uses a mesh terrain, water, and atmospheric fog.
I have code already, but no GPU capture.
I need a practical optimization review: what to cut first, what to measure, and what should stay async. Keep the silhouette intact.
