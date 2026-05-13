#!/usr/bin/env python3
"""export_onnx.py — Export trained PyTorch model to ONNX format.

Usage: python export_onnx.py --model model.pt --output model.onnx --features 10
"""
import argparse
import sys
from pathlib import Path


def export(model_path: Path, output_path: Path, n_features: int, opset: int = 17):
    """Export PyTorch model to ONNX."""
    import torch

    model = torch.load(model_path, weights_only=False)
    model.eval()

    dummy_input = torch.randn(1, n_features)
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        opset_version=opset,
        input_names=["features"],
        output_names=["signal"],
        dynamic_axes={"features": {0: "batch"}, "signal": {0: "batch"}},
    )
    print(f"Exported: {output_path} (opset={opset}, features={n_features})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export to ONNX")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("model.onnx"))
    parser.add_argument("--features", type=int, required=True, help="Number of input features")
    parser.add_argument("--opset", type=int, default=17)
    args = parser.parse_args()

    if not args.model.exists():
        print(f"Error: {args.model} not found")
        return 1

    export(args.model, args.output, args.features, args.opset)
    return 0


if __name__ == "__main__":
    sys.exit(main())
