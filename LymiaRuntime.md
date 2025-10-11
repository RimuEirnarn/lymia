# Lymia Runtime Explanatory

Lymia runtime runs with both FPS (frame/second)-based sync runtime which requires you to set `getch` as non-blocking (returns `-1` immediately) or with classic blocking `getch`. The runner takes `Root` scene and `Env` (Theme) configuration. The runtime uses Stack-based for Scenes which newly created Scenes is pushed into the stack and popped during unmount (i.e Back to previous Scene or Return to main Scene). Below, its runtime procedure is as described:

1. Set `start` with `perf_counter()`
2. Fetch current Scene
3. If it should clear?
	1. Calls `render.erase`
4. Check window changes
5. Calls `Scene.draw` (if FPS-based, wait for some time)
6. If `draw` returns `BACK`, pop current Scene from `stack` and repeat to Step 1
7. Otherwise, calls `getch`
8. Pass `render.getch()` result to `Scene.handle_key`
9. Do UI updates
10. Sets `end`, `delta`, and calculate `frame_count`
11. Result returned by `Scene.handle_key` is passed to processor,
	1. If returns `False`, the program quits (this imply `Scene.handle_key` returns `EXIT`)
	2. If returns `None`, the program continues forward (nothing happened)
	3. Otherwise, if returns `Window`, sets renderer with the returned value.

The processor from Step 11 automatically pushes new scene to Scene stack when `Scene.handle_key` returns `SceneResult` than `ReturnType` Enum.
