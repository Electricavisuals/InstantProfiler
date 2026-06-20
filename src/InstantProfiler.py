"""
InstantProfiler — Houdini cook-time node colorizer

Paints SOP/OBJ/DOP/ROP nodes in the selected network with a color
gradient based on their cook time. Run again to restore original colors.

Usage:
    Select at least one node inside the target network, then run this script.

Author: Albert Callejo Amat(Electricavisuals)
https://github.com/Electricavisuals/InstantProfiler
"""

import hou
import time
import math


def cook_gradient(ratio):
    if ratio < 0.333:
        t = ratio / 0.333
        r, g, b = t * 0.75, 0.8, 0.0
    elif ratio < 0.666:
        t = (ratio - 0.333) / 0.333
        r, g, b = 0.75 + (t * 0.1), 0.8 - (t * 0.45), 0.0
    else:
        t = (ratio - 0.666) / 0.334
        r, g, b = 0.85, 0.35 - (t * 0.3), 0.0
    return hou.Color(r, g, b)


def normalize_log(times):
    # Logarithmic normalization - spreads the gradient across the full range
    # so differences between fast nodes are visible, not just the slowest one
    eps = 0.001
    log_times = {n: math.log(t + eps) for n, t in times.items()}
    min_l = min(log_times.values())
    max_l = max(log_times.values())
    span  = max_l - min_l if max_l != min_l else 1.0
    return {n: (l - min_l) / span for n, l in log_times.items()}


def save_state(nodes):
    hou.session.cook_profiler_originals = {
        n.path(): n.color().rgb() for n in nodes
    }
    flags = {}
    for n in nodes:
        node_flags = {}
        for flag_name, flag in (
            ("Highlight", hou.nodeFlag.Highlight),
            ("Template",  hou.nodeFlag.Template),
        ):
            try:
                node_flags[flag_name] = n.isGenericFlagSet(flag)
            except Exception:
                node_flags[flag_name] = False
        flags[n.path()] = node_flags
    hou.session.cook_profiler_flags = flags


def restore_colors():
    originals = getattr(hou.session, "cook_profiler_originals", {})
    flags     = getattr(hou.session, "cook_profiler_flags", {})

    if not originals:
        print("COOK PROFILER: nothing to restore.")
        return

    for path, color_tuple in originals.items():
        node = hou.node(path)
        if node is None:
            continue
        node.setColor(hou.Color(color_tuple))
        node_flags = flags.get(path, {})
        for flag_name, flag in (
            ("Highlight", hou.nodeFlag.Highlight),
            ("Template",  hou.nodeFlag.Template),
        ):
            try:
                node.setGenericFlag(flag, node_flags.get(flag_name, False))
            except Exception:
                pass

    hou.session.cook_profiler_originals = {}
    hou.session.cook_profiler_flags     = {}
    hou.clearAllSelected()
    print("COOK PROFILER: colors restored.")


def run_profile():
    selected = hou.selectedNodes()
    if not selected:
        print("COOK PROFILER: select at least one node in the target network.")
        return

    network      = selected[0].parent()
    network_path = network.path()
    all_nodes    = list(network.children())

    if not all_nodes:
        print("COOK PROFILER: no nodes found in network.")
        return

    save_state(all_nodes)

    cookable = [
        n for n in all_nodes
        if n.type().category() in (
            hou.sopNodeTypeCategory(),
            hou.objNodeTypeCategory(),
            hou.dopNodeTypeCategory(),
            hou.ropNodeTypeCategory(),
        )
        and "invoke" not in n.type().name().lower()
    ]

    if not cookable:
        print("COOK PROFILER: no cookable nodes found.")
        hou.session.cook_profiler_originals = {}
        hou.session.cook_profiler_flags     = {}
        return

    # Measure cook time with perf_counter - no perfMon, no glow
    times = {}
    with hou.InterruptableOperation("Cooking nodes...", open_interrupt_dialog=True) as op:
        for i, n in enumerate(cookable):
            try:
                op.updateLongProgress(i / len(cookable), "Cooking: {}".format(n.name()))
                start = time.perf_counter()
                n.cook(force=True)
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                times[n] = elapsed_ms
            except hou.OperationInterrupted:
                restore_colors()
                return
            except Exception:
                times[n] = 0.0

    max_t = max(times.values()) if times else 0.0
    if max_t == 0.0:
        hou.session.cook_profiler_originals = {}
        hou.session.cook_profiler_flags     = {}
        print("COOK PROFILER: all nodes 0.0ms - dirty the network and run again.")
        return

    # Apply logarithmic normalization before painting
    ratios = normalize_log(times)

    for n, ratio in ratios.items():
        n.setColor(cook_gradient(ratio))

    hou.clearAllSelected()

    # Print summary with real ms values sorted slowest to fastest
    print("\n=== COOK TIME PROFILER  {} ===".format(network_path))
    print("{:<35} {:>9}".format("NODE", "ms"))
    print("-" * 50)
    for n, t in sorted(times.items(), key=lambda x: x[1], reverse=True):
        ratio = ratios[n]
        bar = int(ratio * 25) * u"\u2588"
        print("{:<35} {:>9.3f} ms  {}".format(n.name(), t, bar))
    print("\n>>> Run this tool again to restore colors <<<\n")


# --- Main: toggle between paint and restore ---
if getattr(hou.session, "cook_profiler_originals", {}):
    restore_colors()
else:
    run_profile()
