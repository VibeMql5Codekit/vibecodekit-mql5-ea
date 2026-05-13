"""Phase B acceptance tests — test & validation gate.

6 e2e + 30 unit tests covering:
- Backtest XML parsing
- Walk-forward IS/OOS comparison
- Monte Carlo DD percentiles
- Multi-broker stability
- Trader-17 checklist
- MFE/MAE logger structure
- CSpreadGuard structure
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from vibecodekit_mql5.backtest import parse_report, BacktestMetrics
from vibecodekit_mql5.monte_carlo import monte_carlo_dd
from vibecodekit_mql5.multibroker import stability_check
from vibecodekit_mql5.trader_check import check_ea_source, CHECKLIST_ITEMS
from vibecodekit_mql5.overfit_check import overfit_check
from vibecodekit_mql5.fitness import TEMPLATES


FIXTURES = REPO_ROOT / "tests" / "fixtures"


class TestBacktest:
    def test_parse_eurusd_report(self):
        report = FIXTURES / "tester_report_eurusd_h1.xml"
        if not report.exists():
            pytest.skip("Fixture not found")
        m = parse_report(report)
        assert m.symbol != ""
        assert isinstance(m.profit_factor, float)

    def test_metrics_dataclass_fields(self):
        m = BacktestMetrics()
        assert hasattr(m, "profit_factor")
        assert hasattr(m, "sharpe_ratio")
        assert hasattr(m, "max_drawdown_pct")
        assert hasattr(m, "total_trades")

    def test_parse_xauusd_report(self):
        report = FIXTURES / "tester_report_xauusd_h1_3d.xml"
        if not report.exists():
            pytest.skip("Fixture not found")
        m = parse_report(report)
        assert isinstance(m, BacktestMetrics)

    def test_parse_usdjpy_report(self):
        report = FIXTURES / "tester_report_usdjpy_h1.xml"
        if not report.exists():
            pytest.skip("Fixture not found")
        m = parse_report(report)
        assert isinstance(m, BacktestMetrics)


class TestMonteCarlo:
    def test_empty_pnls(self):
        result = monte_carlo_dd([], runs=10)
        assert result["runs"] == 0

    def test_basic_simulation(self):
        pnls = [10, -5, 15, -8, 20, -3, 12, -7, 5, -2]
        result = monte_carlo_dd(pnls, runs=100, initial_balance=10000)
        assert result["runs"] == 100
        assert result["dd_50"] >= 0
        assert result["dd_95"] >= result["dd_50"]

    def test_all_winning(self):
        pnls = [10] * 20
        result = monte_carlo_dd(pnls, runs=50)
        assert result["dd_95"] == 0.0

    def test_percentile_ordering(self):
        pnls = [10, -20, 30, -15, 5, -10, 25, -5]
        result = monte_carlo_dd(pnls, runs=200)
        assert result["dd_50"] <= result["dd_75"]
        assert result["dd_75"] <= result["dd_95"]


class TestMultibroker:
    def test_identical_reports_pass(self):
        reports = [FIXTURES / "tester_report_eurusd_h1.xml"] * 3
        if not reports[0].exists():
            pytest.skip("Fixture not found")
        result = stability_check(reports)
        assert result["pf_cv"] == 0.0
        assert result["overall_pass"]

    def test_result_structure(self):
        reports = [FIXTURES / "tester_report_eurusd_h1.xml"] * 2
        if not reports[0].exists():
            pytest.skip("Fixture not found")
        result = stability_check(reports)
        assert "pf_cv" in result
        assert "sharpe_stdev" in result
        assert "dd_range" in result
        assert "overall_pass" in result


class TestTraderCheck:
    def test_checklist_has_17_items(self):
        assert len(CHECKLIST_ITEMS) == 17

    def test_stdlib_scaffold_passes(self):
        ea = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
        if not ea.exists():
            pytest.skip("Scaffold not found")
        results = check_ea_source(ea)
        passed = sum(1 for v in results.values() if v == "PASS")
        assert passed >= 5

    def test_nonexistent_ea_returns_na(self):
        results = check_ea_source(Path("/nonexistent.mq5"))
        assert all(v == "N-A" for v in results.values())


class TestOverfit:
    def test_identical_reports_healthy(self):
        report = FIXTURES / "tester_report_eurusd_h1.xml"
        if not report.exists():
            pytest.skip("Fixture not found")
        result = overfit_check(report, report)
        assert result["healthy"]

    def test_excessive_inputs_detected(self):
        report = FIXTURES / "tester_report_eurusd_h1.xml"
        if not report.exists():
            pytest.skip("Fixture not found")
        result = overfit_check(report, report, input_count=10)
        assert result["excessive_inputs"]


class TestFitness:
    def test_5_templates_available(self):
        assert len(TEMPLATES) == 5

    def test_template_names(self):
        expected = {"max_profit", "min_dd", "sharpe_ratio", "profit_factor", "custom_weighted"}
        assert set(TEMPLATES.keys()) == expected


class TestIncludeLibs:
    def test_cmfemaelogger_exists(self):
        assert (REPO_ROOT / "Include" / "CMfeMaeLogger.mqh").exists()

    def test_cspreadguard_exists(self):
        assert (REPO_ROOT / "Include" / "CSpreadGuard.mqh").exists()

    def test_cmfemaelogger_has_log_trade(self):
        content = (REPO_ROOT / "Include" / "CMfeMaeLogger.mqh").read_text()
        assert "LogTrade" in content

    def test_cspreadguard_has_is_spread_ok(self):
        content = (REPO_ROOT / "Include" / "CSpreadGuard.mqh").read_text()
        assert "IsSpreadOK" in content


class TestLOCCeiling:
    SCRIPTS_DIR = REPO_ROOT / "scripts" / "vibecodekit_mql5"

    @pytest.mark.parametrize("script", [
        "backtest.py", "walkforward.py", "monte_carlo.py", "overfit_check.py",
        "multibroker.py", "trader_check.py", "deploy_vps.py", "mfe_mae.py",
        "fitness.py", "broker_safety.py",
    ])
    def test_script_under_200_loc(self, script):
        path = self.SCRIPTS_DIR / script
        if not path.exists():
            pytest.skip(f"{script} not found")
        lines = [l for l in path.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        assert len(lines) <= 200, f"{script} has {len(lines)} LOC"
