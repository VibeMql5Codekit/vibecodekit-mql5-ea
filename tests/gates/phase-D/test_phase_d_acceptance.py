"""Phase D acceptance tests — tech 2024-2025 gate (stub)."""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

def test_connxloader_exists():
    assert (REPO_ROOT / "Include" / "COnnxLoader.mqh").exists()

def test_casynctrademanager_exists():
    assert (REPO_ROOT / "Include" / "CAsyncTradeManager.mqh").exists()

def test_13_strategy_scaffolds():
    scaffolds_dir = REPO_ROOT / "scaffolds"
    expected = ["hft-async", "trend", "mean-reversion", "breakout",
                "hedging-multi", "news-trading", "arbitrage-stat",
                "scalping", "library", "indicator-only", "grid", "dca"]
    for name in expected:
        assert (scaffolds_dir / name).exists(), f"Scaffold {name} missing"
