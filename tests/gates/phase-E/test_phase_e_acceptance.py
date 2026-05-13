"""Phase E acceptance tests — polish & ship gate (stub)."""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

def test_3_mcp_servers_exist():
    for name in ["metaeditor-bridge", "mt5-bridge", "algo-forge-bridge"]:
        assert (REPO_ROOT / "mcp" / name / "server.py").exists()

def test_26_reference_docs():
    refs_dir = REPO_ROOT / "docs" / "references"
    md_files = list(refs_dir.glob("*.md"))
    assert len(md_files) >= 26, f"Only {len(md_files)} reference docs (need 26)"

def test_worked_example_exists():
    example_dir = REPO_ROOT / "examples" / "ea-wizard-macd-sar-eurusd-h1-portfolio"
    assert (example_dir / "EAName.mq5").exists()
    assert (example_dir / "README.md").exists()

def test_mt5_bridge_readonly():
    server = (REPO_ROOT / "mcp" / "mt5-bridge" / "server.py").read_text()
    tools = (REPO_ROOT / "mcp" / "mt5-bridge" / "tools.py").read_text()
    combined = server + tools
    for forbidden in ["order_send", "order_close", "position_modify", "position_close"]:
        assert forbidden not in combined, f"mt5-bridge contains forbidden: {forbidden}"
