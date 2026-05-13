#!/usr/bin/env python3
"""LLM context bridge — 3 variants for EA signal analysis.

Variants:
  cloud-api        — OpenAI/Claude/Gemini HTTP API
  embedded-onnx    — On-device ONNX text model
  self-hosted      — Ollama local HTTP server

Usage:
    mql5-llm-context --variant cloud-api --prompt "Analyze EURUSD H1"
    mql5-llm-context --variant embedded-onnx --model model.onnx
    mql5-llm-context --variant self-hosted --host localhost:11434
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path


def cloud_api(prompt: str, api_key: str = "",
              model: str = "gpt-4o-mini") -> dict:
    """Call cloud LLM API (OpenAI-compatible)."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {api_key}"}
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": "You are an MQL5 trading analyst."},
        {"role": "user", "content": prompt}],
        "max_tokens": 500}).encode()

    if not api_key:
        return {"variant": "cloud-api", "status": "no-api-key",
                "response": "Set OPENAI_API_KEY or pass --api-key"}
    try:
        req = urllib.request.Request(url, body, headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return {"variant": "cloud-api", "status": "ok",
                "response": data["choices"][0]["message"]["content"]}
    except urllib.error.URLError as exc:
        return {"variant": "cloud-api", "status": "error",
                "response": str(exc)}


def embedded_onnx(prompt: str, model_path: str = "") -> dict:
    """Run prompt through local ONNX text model."""
    if not model_path or not Path(model_path).exists():
        return {"variant": "embedded-onnx", "status": "no-model",
                "response": f"Model not found: {model_path}"}
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name
        tokens = [ord(c) for c in prompt[:512]]
        import numpy as np
        inp = np.array([tokens], dtype=np.int64)
        result = session.run(None, {input_name: inp})
        return {"variant": "embedded-onnx", "status": "ok",
                "response": str(result[0][:100])}
    except ImportError:
        return {"variant": "embedded-onnx", "status": "no-onnxruntime",
                "response": "pip install onnxruntime"}
    except Exception as exc:
        return {"variant": "embedded-onnx", "status": "error",
                "response": str(exc)}


def self_hosted(prompt: str, host: str = "localhost:11434",
                model: str = "llama3") -> dict:
    """Call self-hosted Ollama server."""
    url = f"http://{host}/api/generate"
    body = json.dumps({"model": model, "prompt": prompt,
                       "stream": False}).encode()
    try:
        req = urllib.request.Request(url, body,
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return {"variant": "self-hosted", "status": "ok",
                "response": data.get("response", "")}
    except urllib.error.URLError as exc:
        return {"variant": "self-hosted", "status": "error",
                "response": f"Ollama at {host}: {exc}"}


VARIANTS = {"cloud-api": cloud_api, "embedded-onnx": embedded_onnx,
            "self-hosted": self_hosted}


def main() -> int:
    ap = argparse.ArgumentParser(description="LLM context bridge")
    ap.add_argument("--variant", choices=VARIANTS, default="cloud-api")
    ap.add_argument("--prompt", default="Analyze current market conditions")
    ap.add_argument("--api-key", default="")
    ap.add_argument("--model", default="")
    ap.add_argument("--host", default="localhost:11434")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kwargs: dict = {"prompt": args.prompt}
    if args.variant == "cloud-api":
        kwargs["api_key"] = args.api_key
    elif args.variant == "embedded-onnx":
        kwargs["model_path"] = args.model
    elif args.variant == "self-hosted":
        kwargs["host"] = args.host

    result = VARIANTS[args.variant](**kwargs)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[{result['variant']}] {result['status']}")
        print(result["response"])
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
