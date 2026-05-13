"""Phase E acceptance tests — polish & ship gate."""
import json
import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_3_mcp_servers_exist():
    for name in ["metaeditor-bridge", "mt5-bridge", "algo-forge-bridge"]:
        assert (REPO_ROOT / "mcp" / name / "server.py").exists()
        assert (REPO_ROOT / "mcp" / name / "tools.py").exists()


def test_mcp_servers_have_tools():
    """Each MCP server must define actual tools, not empty list."""
    for name in ["metaeditor-bridge", "mt5-bridge", "algo-forge-bridge"]:
        tools_code = (REPO_ROOT / "mcp" / name / "tools.py").read_text()
        assert "TOOLS: list[dict] = []" not in tools_code, \
            f"{name} tools.py still has empty TOOLS list"
        assert "HANDLERS" in tools_code, \
            f"{name} tools.py missing HANDLERS dict"


def test_metaeditor_bridge_tools():
    """metaeditor-bridge should have compile, syntax_check, list_includes."""
    sys.path.insert(0, str(REPO_ROOT / "mcp" / "metaeditor-bridge"))
    from tools import TOOLS, HANDLERS
    tool_names = {t["name"] for t in TOOLS}
    assert "compile" in tool_names
    assert "syntax_check" in tool_names
    assert "list_includes" in tool_names
    assert len(HANDLERS) >= 3


def test_metaeditor_syntax_check_works():
    sys.path.insert(0, str(REPO_ROOT / "mcp" / "metaeditor-bridge"))
    from tools import handle_syntax_check
    fixture = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    result = handle_syntax_check({"file": str(fixture)})
    assert result["status"] in ("ok", "warning")
    assert "lines" in result


def test_metaeditor_list_includes_works():
    sys.path.insert(0, str(REPO_ROOT / "mcp" / "metaeditor-bridge"))
    from tools import handle_list_includes
    fixture = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    result = handle_list_includes({"file": str(fixture)})
    assert "includes" in result
    assert result["count"] >= 0


def test_mt5_bridge_readonly():
    server = (REPO_ROOT / "mcp" / "mt5-bridge" / "server.py").read_text()
    tools = (REPO_ROOT / "mcp" / "mt5-bridge" / "tools.py").read_text()
    combined = server + tools
    for forbidden in ["order_send", "order_close",
                      "position_modify", "position_close"]:
        assert forbidden not in combined, \
            f"mt5-bridge contains forbidden: {forbidden}"


def test_mt5_bridge_tools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mt5_tools", REPO_ROOT / "mcp" / "mt5-bridge" / "tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool_names = {t["name"] for t in mod.TOOLS}
    assert "market_info" in tool_names
    assert "account_info" in tool_names
    assert "positions" in tool_names
    assert "history" in tool_names


def test_algo_forge_bridge_tools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "forge_tools", REPO_ROOT / "mcp" / "algo-forge-bridge" / "tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool_names = {t["name"] for t in mod.TOOLS}
    assert "init_workspace" in tool_names
    assert "evaluate" in tool_names
    assert "suggest_params" in tool_names


def test_26_reference_docs():
    refs_dir = REPO_ROOT / "docs" / "references"
    md_files = list(refs_dir.glob("*.md"))
    assert len(md_files) >= 26, f"Only {len(md_files)} reference docs (need 26)"


def test_worked_example_exists():
    example_dir = REPO_ROOT / "examples" / "ea-wizard-macd-sar-eurusd-h1-portfolio"
    assert (example_dir / "EAName.mq5").exists()
    assert (example_dir / "README.md").exists()


def test_worked_example_has_results():
    results_dir = (REPO_ROOT / "examples" /
                   "ea-wizard-macd-sar-eurusd-h1-portfolio" / "results")
    assert results_dir.is_dir()
    for name in ["backtest-summary.json", "walkforward.json",
                 "monte-carlo.json", "multibroker.json"]:
        f = results_dir / name
        assert f.exists(), f"Missing result: {name}"
        data = json.loads(f.read_text())
        assert isinstance(data, dict)


def test_worked_example_backtest_metrics():
    bt = json.loads((REPO_ROOT / "examples" /
                     "ea-wizard-macd-sar-eurusd-h1-portfolio" /
                     "results" / "backtest-summary.json").read_text())
    assert bt["profit_factor"] > 1.0
    assert bt["total_trades"] > 100
    assert bt["maximal_drawdown_pct"] < 30


def test_worked_example_multibroker_pass():
    mb = json.loads((REPO_ROOT / "examples" /
                     "ea-wizard-macd-sar-eurusd-h1-portfolio" /
                     "results" / "multibroker.json").read_text())
    assert mb["pf_cv"] <= 0.30
    assert len(mb["brokers"]) >= 3


def test_mcp_server_jsonrpc():
    """Each MCP server.py should implement JSON-RPC 2.0 protocol."""
    for name in ["metaeditor-bridge", "mt5-bridge", "algo-forge-bridge"]:
        code = (REPO_ROOT / "mcp" / name / "server.py").read_text()
        assert "jsonrpc" in code
        assert "handle_request" in code
        assert "tools/list" in code
        assert "tools/call" in code
