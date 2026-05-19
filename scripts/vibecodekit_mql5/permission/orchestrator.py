#!/usr/bin/env python3
"""7-layer permission orchestrator — mode-dependent layer execution."""
from __future__ import annotations

from vibecodekit_mql5.permission import (
    layer1_source_lint, layer2_compile, layer3_ap_lint,
    layer4_checklist, layer5_methodology, layer6_quality_matrix,
    layer7_broker_safety,
)

MODE_LAYERS = {
    "PERSONAL": [1, 2, 3, 4, 7],
    "TEAM": [1, 2, 3, 4, 5, 7],
    "ENTERPRISE": [1, 2, 3, 4, 5, 6, 7],
}

LAYER_MAP = {
    1: layer1_source_lint,
    2: layer2_compile,
    3: layer3_ap_lint,
    4: layer4_checklist,
    5: layer5_methodology,
    6: layer6_quality_matrix,
    7: layer7_broker_safety,
}


def run_permission_pipeline(ea_path: str, mode: str = "TEAM") -> dict:
    """Run mode-dependent permission layers sequentially."""
    if mode not in MODE_LAYERS:
        return {"mode": mode, "layers_run": 0, "all_pass": False,
                "error": f"Invalid mode '{mode}'. Valid: {list(MODE_LAYERS.keys())}",
                "results": {}}
    layers = MODE_LAYERS[mode]
    results = {}
    all_pass = True

    for layer_id in layers:
        module = LAYER_MAP[layer_id]
        result = module.check(ea_path)
        results[f"L{layer_id}"] = result
        if not result.get("pass", False):
            all_pass = False
            break  # Fail-fast

    return {"mode": mode, "layers_run": len(results),
            "all_pass": all_pass, "results": results}


def main() -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="7-layer permission pipeline")
    parser.add_argument("--ea", required=True, help=".mq5 file to check")
    parser.add_argument("--mode", default="TEAM", choices=list(MODE_LAYERS.keys()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_permission_pipeline(args.ea, args.mode)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["all_pass"] else "FAIL"
        print(f"Permission [{args.mode}]: {status} ({result['layers_run']} layers)")
        for k, v in result["results"].items():
            icon = "+" if v.get("pass") else "X"
            print(f"  [{icon}] {k}: {v.get('details', '')[:60]}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
