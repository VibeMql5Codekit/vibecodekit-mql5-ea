"""Phase D acceptance tests — tech 2024-2025 gate."""
import json
import sys
import tempfile
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_connxloader_exists():
    assert (REPO_ROOT / "Include" / "COnnxLoader.mqh").exists()


def test_connxloader_has_predict_and_shape():
    content = (REPO_ROOT / "Include" / "COnnxLoader.mqh").read_text()
    assert "SetInputShape" in content
    assert "SetOutputShape" in content
    assert "OnnxRun" in content
    assert "PredictClass" in content


def test_casynctrademanager_exists():
    assert (REPO_ROOT / "Include" / "CAsyncTradeManager.mqh").exists()


def test_casynctrademanager_has_sell_and_cleanup():
    content = (REPO_ROOT / "Include" / "CAsyncTradeManager.mqh").read_text()
    assert "SellAsync" in content
    assert "CleanupCompleted" in content
    assert "ASYNC_PENDING" in content
    assert "ASYNC_FILLED" in content


def test_13_strategy_scaffolds():
    scaffolds_dir = REPO_ROOT / "scaffolds"
    expected = ["hft-async", "trend", "mean-reversion", "breakout",
                "hedging-multi", "news-trading", "arbitrage-stat",
                "scalping", "library", "indicator-only", "grid", "dca"]
    for name in expected:
        assert (scaffolds_dir / name).exists(), f"Scaffold {name} missing"


def test_llm_bridge_3_variants():
    from vibecodekit_mql5.llm_context import VARIANTS
    assert set(VARIANTS.keys()) == {"cloud-api", "embedded-onnx", "self-hosted"}


def test_llm_bridge_cloud_api_no_key():
    from vibecodekit_mql5.llm_context import cloud_api
    result = cloud_api("test prompt")
    assert result["variant"] == "cloud-api"
    assert result["status"] == "no-api-key"


def test_llm_bridge_embedded_no_model():
    from vibecodekit_mql5.llm_context import embedded_onnx
    result = embedded_onnx("test", model_path="/nonexistent.onnx")
    assert result["variant"] == "embedded-onnx"
    assert result["status"] == "no-model"


def test_llm_bridge_self_hosted_no_server():
    from vibecodekit_mql5.llm_context import self_hosted
    result = self_hosted("test", host="localhost:19999")
    assert result["variant"] == "self-hosted"
    assert result["status"] == "error"


def test_forge_init_creates_workspace():
    from vibecodekit_mql5.forge_init import create_workspace
    ea = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td) / "test-forge"
        result = create_workspace(ea, ws)
        assert ws.exists()
        assert (ws / "forge-config.json").exists()
        assert (ws / "results").is_dir()
        config = json.loads((ws / "forge-config.json").read_text())
        assert "fitness" in config
        assert config["fitness"]["primary"] == "profit_factor"


def test_forge_pr_evaluate_fitness():
    from vibecodekit_mql5.forge_pr import evaluate_fitness
    fitness_cfg = {"primary": "profit_factor", "secondary": "sharpe_ratio",
                   "constraints": {"max_drawdown_pct": 30, "min_trades": 100}}
    metrics = {"profit_factor": 2.5, "sharpe_ratio": 1.8,
               "max_drawdown_pct": 15, "total_trades": 200}
    score = evaluate_fitness(metrics, fitness_cfg)
    assert score > 0
    assert score == round(0.6 * 2.5 + 0.4 * 1.8, 4)


def test_forge_pr_constraint_violation():
    from vibecodekit_mql5.forge_pr import evaluate_fitness
    cfg = {"constraints": {"max_drawdown_pct": 10}}
    metrics = {"max_drawdown_pct": 50, "total_trades": 200}
    assert evaluate_fitness(metrics, cfg) == -1.0


def test_3_llm_scaffold_dirs():
    llm_dir = REPO_ROOT / "scaffolds" / "service-llm-bridge"
    for variant in ["cloud-api", "embedded-onnx-llm", "self-hosted-ollama"]:
        assert (llm_dir / variant).exists(), f"LLM scaffold {variant} missing"


def test_onnx_export_detect_framework():
    from vibecodekit_mql5.onnx_export import detect_framework
    assert detect_framework(Path("model.pt")) == "pytorch"
    assert detect_framework(Path("model.h5")) == "tensorflow"
    assert detect_framework(Path("model.pkl")) == "sklearn"
    assert detect_framework(Path("model.xyz")) == "unknown"


def test_onnx_export_validate_opset():
    from vibecodekit_mql5.onnx_export import validate_opset
    ok, _ = validate_opset(17)
    assert ok
    fail, msg = validate_opset(5)
    assert not fail
    assert "too low" in msg


def test_onnx_embed_generates_loader():
    from vibecodekit_mql5.onnx_embed import generate_embed
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        f.write(b"fake-onnx-data")
        f.flush()
        result = generate_embed(Path(f.name))
    assert result["success"]
    assert "COnnxLoader" in result["loader_code"]
    assert "ExtModel" in result["resource_directive"]


def test_async_build_creates_scaffold():
    from vibecodekit_mql5.async_build import build_hft_scaffold
    with tempfile.TemporaryDirectory() as td:
        result = build_hft_scaffold("TestHFT", Path(td), "netting")
        assert result["success"]
        assert (Path(td) / "TestHFT" / "TestHFT.mq5").exists()
        content = (Path(td) / "TestHFT" / "TestHFT.mq5").read_text()
        assert "CAsyncTradeManager" in content
        assert "OnTradeTransaction" in content


def test_cloud_optimize_cost_gate():
    from vibecodekit_mql5.cloud_optimize import check_cost_gate
    result = check_cost_gate("PERSONAL", 10)
    assert not result["allowed"]
    result = check_cost_gate("TEAM", 30)
    assert result["allowed"]
    result = check_cost_gate("TEAM", 100)
    assert not result["allowed"]
    result = check_cost_gate("ENTERPRISE", 200)
    assert result["allowed"]


def test_method_hiding_check_detects():
    from vibecodekit_mql5.method_hiding_check import extract_classes, check_hiding
    code = """
class CBase { public: int Calculate(int x) { return x; } };
class CDerived : public CBase { public: int Calculate(int x) { return x*2; } };
"""
    classes = extract_classes(code)
    assert len(classes) == 2
    issues = check_hiding(classes)
    assert len(issues) >= 1


def test_ml_onnx_python_dir_exists():
    py_dir = REPO_ROOT / "scaffolds" / "ml-onnx" / "python-bridge" / "python"
    assert py_dir.exists()
    assert (py_dir / "train.py").exists()
    assert (py_dir / "export_onnx.py").exists()
    assert (py_dir / "requirements.txt").exists()


def test_onnx_export_not_stub():
    path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "onnx_export.py"
    content = path.read_text()
    assert len(content.splitlines()) > 50
    assert "detect_framework" in content


def test_cloud_optimize_generates_ini():
    from vibecodekit_mql5.cloud_optimize import generate_cloud_config
    result = generate_cloud_config(Path("test.mq5"), "ENTERPRISE", 100, "XAUUSD", "M5")
    assert result["success"]
    assert "XAUUSD" in result["config_ini"]
    assert "CloudMaxAgents" in result["config_ini"]


def test_method_hiding_no_false_positive():
    from vibecodekit_mql5.method_hiding_check import extract_classes, check_hiding
    code = "class CSimple { public: void OnTick() {} };"
    classes = extract_classes(code)
    issues = check_hiding(classes)
    assert len(issues) == 0
