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


def test_mt5_bridge_has_10_tools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mt5_tools2", REPO_ROOT / "mcp" / "mt5-bridge" / "tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert len(mod.TOOLS) >= 10, f"Expected >=10 tools, got {len(mod.TOOLS)}"
    assert len(mod.HANDLERS) >= 10


def test_mt5_bridge_new_tools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mt5_tools3", REPO_ROOT / "mcp" / "mt5-bridge" / "tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool_names = {t["name"] for t in mod.TOOLS}
    for name in ["symbols_list", "rates_copy", "tick_last",
                 "terminal_info", "positions_history", "market_book"]:
        assert name in tool_names, f"Missing tool: {name}"


def test_algo_forge_has_6_tools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "forge_tools2", REPO_ROOT / "mcp" / "algo-forge-bridge" / "tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert len(mod.TOOLS) >= 6, f"Expected >=6 tools, got {len(mod.TOOLS)}"
    tool_names = {t["name"] for t in mod.TOOLS}
    for name in ["clone", "commit", "repo_list"]:
        assert name in tool_names, f"Missing tool: {name}"


def test_phase_e_scripts_exist():
    scripts = ["scan", "vision", "blueprint", "tip", "survey", "doctor",
               "audit", "canary", "ship", "refine", "install", "second_opinion"]
    for name in scripts:
        path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / f"{name}.py"
        assert path.exists(), f"{name}.py missing"
        content = path.read_text()
        assert len(content.splitlines()) > 30, f"{name}.py too short"


def test_phase_e_scripts_not_stubs():
    for name in ["canary", "doctor", "ship", "refine", "audit", "scan"]:
        path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / f"{name}.py"
        content = path.read_text()
        assert "def main" in content, f"{name}.py missing main()"
        assert "argparse" in content, f"{name}.py missing argparse"


def test_scan_project():
    from vibecodekit_mql5.scan import scan_project
    result = scan_project(REPO_ROOT)
    assert result["mq5_count"] > 0
    assert result["has_pyproject"]
    assert len(result["scaffolds"]) > 0


def test_survey_presets():
    from vibecodekit_mql5.survey import survey_presets
    result = survey_presets(REPO_ROOT)
    assert result["success"]
    assert result["total"] >= 17


def test_audit_conformance():
    from vibecodekit_mql5.audit import run_audit
    result = run_audit(REPO_ROOT)
    assert result["total"] >= 40
    assert result["passed"] > 30


def test_doctor_health():
    from vibecodekit_mql5.doctor import check_health
    result = check_health()
    assert result["total"] > 0
    assert result["passed"] > 0


def test_refine_classify():
    from vibecodekit_mql5.refine import classify_diff
    diff = "+fix: corrected bug in calculation\n-old broken line\n+new fixed line"
    result = classify_diff(diff)
    assert result["primary_category"] in ["BUG_FIX", "PERF", "UX", "DOCS", "SCOPE_CREEP"]
    assert result["total_changed_lines"] > 0


def test_vision_generate():
    from vibecodekit_mql5.vision import generate_vision
    result = generate_vision("Test EA", "Trade gold")
    assert "content" in result
    assert "Test EA" in result["content"]


def test_tip_generate():
    from vibecodekit_mql5.tip import generate_tips
    tips = generate_tips()
    assert len(tips) == 10
    assert tips[0]["id"] == "TIP-001"


def test_canary_healthy_log():
    import tempfile
    from vibecodekit_mql5.canary import analyze_log
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("2024-01-01 Connected to server\nOrder executed successfully\n")
        f.flush()
        result = analyze_log(Path(f.name), "TestEA", 30)
    assert result["success"]
    assert result["status"] in ["HEALTHY", "DEGRADED"]


def test_canary_critical_log():
    import tempfile
    from vibecodekit_mql5.canary import analyze_log
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("error trade failed\nerror order rejected\nout of memory\n")
        f.flush()
        result = analyze_log(Path(f.name), "TestEA", 30)
    assert result["success"]
    assert result["status"] == "CRITICAL"


def test_pyproject_cli_entry_points():
    import tomllib
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    scripts = config.get("project", {}).get("scripts", {})
    assert len(scripts) >= 40, f"Only {len(scripts)} CLI entry points registered"
    assert "mql5-build" in scripts
    assert "mql5-canary" in scripts
    assert "mql5-audit" in scripts
    assert "mql5-cso" in scripts


def test_second_opinion_prompt():
    from vibecodekit_mql5.second_opinion import FOCUS_PROMPTS
    assert len(FOCUS_PROMPTS) >= 5
    assert "risk" in FOCUS_PROMPTS
    assert "security" in FOCUS_PROMPTS


def test_ship_dry_run():
    from vibecodekit_mql5.ship import ship_release
    result = ship_release("99.99.99", dry_run=True)
    assert result["success"]
    assert result["dry_run"]
    assert result["tag"] == "v99.99.99"


def test_all_scripts_under_200_loc():
    scripts_dir = REPO_ROOT / "scripts" / "vibecodekit_mql5"
    for py_file in scripts_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        lines = py_file.read_text().splitlines()
        assert len(lines) <= 200, f"{py_file.name} has {len(lines)} LOC (max 200)"


def test_no_forbidden_files():
    for forbidden in ["query_loop.py", "tool_executor.py", "intent_router.py"]:
        path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / forbidden
        assert not path.exists(), f"Forbidden file exists: {forbidden}"
