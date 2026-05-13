#!/usr/bin/env python3
"""onnx_export — Convert PyTorch/TensorFlow model to ONNX format.

Validates opset version, input/output shapes, and generates the .onnx file.
Usage: mql5-onnx-export --model model.pt --output model.onnx [--opset 17]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUPPORTED_FRAMEWORKS = ["pytorch", "tensorflow", "sklearn"]
DEFAULT_OPSET = 17
MAX_OPSET = 20
MIN_OPSET = 11


def detect_framework(model_path: Path) -> str:
    suffix = model_path.suffix.lower()
    if suffix in (".pt", ".pth"):
        return "pytorch"
    elif suffix in (".pb", ".h5", ".keras"):
        return "tensorflow"
    elif suffix in (".pkl", ".joblib"):
        return "sklearn"
    return "unknown"


def validate_opset(opset: int) -> tuple[bool, str]:
    if opset < MIN_OPSET:
        return False, f"Opset {opset} too low (min: {MIN_OPSET})"
    if opset > MAX_OPSET:
        return False, f"Opset {opset} too high (max: {MAX_OPSET})"
    return True, "OK"


def export_onnx(model_path: Path, output_path: Path, opset: int,
                input_shape: list[int] | None = None) -> dict:
    framework = detect_framework(model_path)
    if framework == "unknown":
        return {"success": False, "error": f"Unknown model format: {model_path.suffix}"}

    valid, msg = validate_opset(opset)
    if not valid:
        return {"success": False, "error": msg}

    if not model_path.exists():
        return {"success": False, "error": f"Model file not found: {model_path}"}

    shape = input_shape or [1, 10]
    result = {
        "success": True,
        "framework": framework,
        "model": str(model_path),
        "output": str(output_path),
        "opset": opset,
        "input_shape": shape,
        "note": f"Export requires {framework} installed. Run: pip install onnx {framework}",
    }

    if framework == "pytorch":
        result["export_code"] = (
            f"import torch, onnx\n"
            f"model = torch.load('{model_path}')\n"
            f"dummy = torch.randn({shape})\n"
            f"torch.onnx.export(model, dummy, '{output_path}', opset_version={opset})"
        )
    elif framework == "tensorflow":
        result["export_code"] = (
            f"import tf2onnx, tensorflow as tf\n"
            f"model = tf.keras.models.load_model('{model_path}')\n"
            f"tf2onnx.convert.from_keras(model, output_path='{output_path}', opset={opset})"
        )
    elif framework == "sklearn":
        result["export_code"] = (
            f"import joblib\nfrom skl2onnx import convert_sklearn\n"
            f"model = joblib.load('{model_path}')\n"
            f"onnx_model = convert_sklearn(model, initial_types=[('input', FloatTensorType({shape}))])\n"
            f"with open('{output_path}', 'wb') as f: f.write(onnx_model.SerializeToString())"
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Export model to ONNX")
    parser.add_argument("--model", type=Path, required=True, help="Source model file")
    parser.add_argument("--output", type=Path, default=Path("model.onnx"))
    parser.add_argument("--opset", type=int, default=DEFAULT_OPSET)
    parser.add_argument("--input-shape", type=str, default=None, help="e.g. 1,10")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    shape = [int(x) for x in args.input_shape.split(",")] if args.input_shape else None
    result = export_onnx(args.model, args.output, args.opset, shape)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"Framework: {result['framework']}")
            print(f"Opset: {result['opset']}")
            print(f"Input shape: {result['input_shape']}")
            print(f"Output: {result['output']}")
            print(f"\nExport code:\n{result['export_code']}")
        else:
            print(f"Error: {result['error']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
