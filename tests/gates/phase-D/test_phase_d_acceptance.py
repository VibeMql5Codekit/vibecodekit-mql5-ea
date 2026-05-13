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
