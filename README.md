# InstantProfiler — Houdini Cook-Time Profiler

A lightweight tool for Houdini that paints SOP/OBJ/DOP/ROP nodes with a color gradient based on their cook time, helping you quickly spot performance bottlenecks inside a network.

![Houdini](https://img.shields.io/badge/Houdini-21.0%2B-orange)
![Python](https://img.shields.io/badge/Python-3.11-blue)

Repo: [github.com/Electricavisuals/InstantProfiler](https://github.com/Electricavisuals/InstantProfiler)

🎥 [Watch the tutorial on YouTube](https://www.youtube.com/watch?v=e1Dvn-Shauk)

## What it does

- Selects a network, cooks every direct child node, and measures the time each one takes.
- Paints nodes on a **green → yellow → orange → red** gradient depending on relative cost.
- Uses **logarithmic normalization** so differences between fast nodes remain visible even when one node is much slower than the rest.
- Excludes `invoke` nodes from the ranking (they only measure call overhead, not real work).
- Run the tool a second time to **restore original node colors**.
- No glow/highlight artifacts — does not rely on Houdini's Performance Monitor, so it avoids the visual "halo" effect that lingers on nodes after profiling.

## Install

1. Copy `src/InstantProfiler.py` to your Houdini scripts folder:
   ```
   $HOUDINI_USER_PREF_DIR/scripts/
   ```
   (on Windows, typically `C:/Users/<you>/Documents/houdini21.0/scripts/`)

2. Copy the icon to:
   ```
   $HOUDINI_USER_PREF_DIR/config/Icons/
   ```
   (the icon should be named `MISC_instantprofiler.svg` or `.png`)

3. Create a new shelf tool in Houdini:
   - Right-click any shelf → **New Tool...**
   - Name: `InstantProfiler`
   - Icon: `MISC_instantprofiler`
   - In the **Script** tab, paste:
     ```python
     exec(open(hou.expandString("$HOUDINI_USER_PREF_DIR/scripts/InstantProfiler.py")).read())
     ```
   - Save

4. The **InstantProfiler** tool will appear in your shelf.

## Usage

1. Select one or more nodes inside the network you want to profile (the tool profiles all direct children of the selected node's parent network).
2. Click the shelf tool. It cooks every node, paints them by relative cost, and prints a ranked summary to the **Python Shell**:

```
=== COOK TIME PROFILER  /obj/ROCKWALLS_CREATION ===
NODE                                       ms
--------------------------------------------------
RocksWall1                           1649.802 ms  █████████████████████████
CURVE                                  61.606 ms  ████████████████
testgeometry_tommy1                    26.253 ms  ██████████████
boolean1                                1.702 ms  ████
edit1                                    0.195 ms  ██
...
```

3. Explore the network freely — nodes stay painted.
4. Click the tool **again** to restore original colors.

## Why not just use the Performance Monitor?

Houdini's built-in Performance Monitor (`Windows → Performance Monitor`) is more accurate since it captures real cook context with dependencies. However:

- It leaves a glow/highlight on nodes that can't easily be cleared via Python.
- It requires manually opening a pane, hitting Record/Stop, and reading a text list.
- This tool gives an instant visual read directly in the network editor, with no extra panes and no lingering visual artifacts.

For deep profiling with full dependency context, still use the Performance Monitor. For a quick "what's slow in this network" visual scan, use this tool.

## Requirements

- Houdini 19.5+ (uses `hou.nodeFlag`, `hou.InterruptableOperation`)
- Python 3 (Houdini 21.0.631 tested)

## License

MIT — use it, fork it, improve it.
