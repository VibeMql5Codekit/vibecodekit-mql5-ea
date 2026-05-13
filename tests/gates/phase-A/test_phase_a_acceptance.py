"""Phase A acceptance tests — core foundation gate.

3 e2e + 25 unit tests covering:
- CPipNormalizer digit classes
- CRiskGuard / CMagicRegistry structure
- lint.py 8 critical AP detection
- build.py scaffold rendering
- pip_normalize.py refactoring
"""
from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from vibecodekit_mql5.lint import lint_file, lint_paths, Finding
from vibecodekit_mql5.build import list_presets, render_scaffold, SCAFFOLDS_DIR
from vibecodekit_mql5.pip_normalize import scan_file


# ─── CPipNormalizer structure tests ─────────────────────────────

class TestCPipNormalizer:
    MQH = REPO_ROOT / "Include" / "CPipNormalizer.mqh"

    def test_file_exists(self):
        assert self.MQH.exists()

    def test_loc_under_250(self):
        lines = [l for l in self.MQH.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("//")]
        assert len(lines) <= 250, f"CPipNormalizer.mqh has {len(lines)} LOC (max 250)"

    def test_has_init_method(self):
        content = self.MQH.read_text()
        assert "bool Init(" in content

    def test_has_pips_method(self):
        content = self.MQH.read_text()
        assert "double Pips(" in content

    def test_has_lot_for_risk(self):
        content = self.MQH.read_text()
        assert "double LotForRisk(" in content

    def test_truth_table_present(self):
        """pip = (digits ∈ {3,5}) ? 10*point : 1*point"""
        content = self.MQH.read_text()
        assert "m_digits == 3 || m_digits == 5" in content or \
               "m_digits==3||m_digits==5" in content or \
               "digits == 3" in content.replace(" ", "").lower()

    def test_price_to_pips(self):
        content = self.MQH.read_text()
        assert "PriceToPips" in content

    def test_is_valid_sl_distance(self):
        content = self.MQH.read_text()
        assert "IsValidSLDistance" in content

    def test_clamp_sl_pips(self):
        content = self.MQH.read_text()
        assert "ClampSLPips" in content

    def test_no_hardcoded_pip(self):
        content = self.MQH.read_text()
        assert "0.0001" not in content or "Truth table" in content


# ─── CRiskGuard structure tests ─────────────────────────────────

class TestCRiskGuard:
    MQH = REPO_ROOT / "Include" / "CRiskGuard.mqh"

    def test_file_exists(self):
        assert self.MQH.exists()

    def test_loc_under_150(self):
        lines = [l for l in self.MQH.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("//")]
        assert len(lines) <= 150

    def test_has_daily_loss_limit(self):
        content = self.MQH.read_text()
        assert "m_daily_loss_limit" in content

    def test_has_can_open_trade(self):
        content = self.MQH.read_text()
        assert "CanOpenTrade" in content

    def test_has_reset_daily(self):
        content = self.MQH.read_text()
        assert "ResetDaily" in content


# ─── CMagicRegistry structure tests ──────────────────────────────

class TestCMagicRegistry:
    MQH = REPO_ROOT / "Include" / "CMagicRegistry.mqh"

    def test_file_exists(self):
        assert self.MQH.exists()

    def test_loc_under_100(self):
        lines = [l for l in self.MQH.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("//")]
        assert len(lines) <= 100

    def test_has_reserve(self):
        content = self.MQH.read_text()
        assert "Reserve" in content

    def test_has_release(self):
        content = self.MQH.read_text()
        assert "Release" in content


# ─── lint.py tests ───────────────────────────────────────────────

class TestLint:
    FIXTURES = REPO_ROOT / "tests" / "fixtures"

    def test_ap01_no_sl_detected(self):
        findings = lint_file(self.FIXTURES / "ap_01_no_sl.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-01" in ap_ids, f"AP-01 not detected, got: {ap_ids}"

    def test_ap03_fixed_lot_detected(self):
        findings = lint_file(self.FIXTURES / "ap_03_lot_fixed.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-03" in ap_ids, f"AP-03 not detected, got: {ap_ids}"

    def test_ap05_overfitted_detected(self):
        findings = lint_file(self.FIXTURES / "ap_05_overfitted.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-05" in ap_ids, f"AP-05 not detected, got: {ap_ids}"

    def test_ap15_raw_ordersend_detected(self):
        findings = lint_file(self.FIXTURES / "ap_15_raw_ordersend.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-15" in ap_ids, f"AP-15 not detected, got: {ap_ids}"

    def test_ap17_webrequest_ontick_detected(self):
        findings = lint_file(self.FIXTURES / "ap_17_webrequest_ontick.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-17" in ap_ids, f"AP-17 not detected, got: {ap_ids}"

    def test_ap18_async_no_handler_detected(self):
        findings = lint_file(self.FIXTURES / "ap_18_async_no_handler.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-18" in ap_ids, f"AP-18 not detected, got: {ap_ids}"

    def test_ap20_hardcoded_pip_detected(self):
        findings = lint_file(self.FIXTURES / "ap_20_hardcoded_pip.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-20" in ap_ids, f"AP-20 not detected, got: {ap_ids}"

    def test_ap21_jpy_xau_broken_detected(self):
        findings = lint_file(self.FIXTURES / "ap_21_jpy_xau_broken.mq5")
        ap_ids = {f.ap_id for f in findings}
        assert "AP-21" in ap_ids, f"AP-21 not detected, got: {ap_ids}"

    def test_all_criticals_exit_1(self):
        findings = lint_paths([self.FIXTURES])
        criticals = [f for f in findings if f.severity == "CRITICAL"]
        assert len(criticals) >= 8, f"Expected ≥8 criticals, got {len(criticals)}"


# ─── build.py tests ──────────────────────────────────────────────

class TestBuild:
    def test_list_presets_returns_4(self):
        presets = list_presets()
        preset_names = {p["preset"] for p in presets}
        for expected in ["stdlib", "wizard-composable", "portfolio-basket", "ml-onnx"]:
            assert expected in preset_names

    def test_render_stdlib_netting(self, tmp_path):
        result = render_scaffold("stdlib", "netting", "TestEA", tmp_path)
        ea_file = result / "TestEA.mq5"
        assert ea_file.exists()
        content = ea_file.read_text()
        assert "TestEA" in content
        assert "EAName" not in content

    def test_render_replaces_ea_name(self, tmp_path):
        result = render_scaffold("stdlib", "netting", "MyCustomEA", tmp_path)
        content = (result / "MyCustomEA.mq5").read_text()
        assert "MyCustomEA" in content
        assert "CPipNormalizer" in content


# ─── pip_normalize.py tests ──────────────────────────────────────

class TestPipNormalize:
    def test_detects_hardcoded_pip(self, tmp_path):
        mq5 = tmp_path / "test.mq5"
        mq5.write_text("double sl = 50 * 0.0001;")
        results = scan_file(mq5)
        assert len(results) >= 1

    def test_suggests_pipnorm_call(self, tmp_path):
        mq5 = tmp_path / "test.mq5"
        mq5.write_text("double sl = 50 * 0.0001;")
        results = scan_file(mq5)
        assert any("pipNorm.Pips" in r[2] for r in results)


# ─── LOC ceiling tests ──────────────────────────────────────────

class TestLOCCeiling:
    SCRIPTS_DIR = REPO_ROOT / "scripts" / "vibecodekit_mql5"

    def test_lint_under_200_loc(self):
        self._check_loc(self.SCRIPTS_DIR / "lint.py", 200)

    def test_build_under_200_loc(self):
        self._check_loc(self.SCRIPTS_DIR / "build.py", 200)

    def test_compile_under_200_loc(self):
        self._check_loc(self.SCRIPTS_DIR / "compile.py", 200)

    def test_pip_normalize_under_200_loc(self):
        self._check_loc(self.SCRIPTS_DIR / "pip_normalize.py", 200)

    def _check_loc(self, path: Path, limit: int):
        assert path.exists(), f"{path} not found"
        lines = [l for l in path.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        assert len(lines) <= limit, f"{path.name} has {len(lines)} LOC (max {limit})"
