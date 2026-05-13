"""Phase C acceptance tests — methodology gate."""
import sys
import pytest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_6_persona_yamls_exist():
    personas_dir = REPO_ROOT / "docs" / "rri-personas"
    for name in ["trader", "risk-auditor", "broker-engineer",
                 "strategy-architect", "devops", "perf-analyst"]:
        assert (personas_dir / f"{name}.yaml").exists()


def test_persona_yamls_have_real_questions():
    personas_dir = REPO_ROOT / "docs" / "rri-personas"
    for name in ["trader", "risk-auditor", "broker-engineer",
                 "strategy-architect", "devops", "perf-analyst"]:
        data = yaml.safe_load((personas_dir / f"{name}.yaml").read_text())
        assert data["name"] == name, f"{name}: wrong name field"
        assert len(data["questions"]) == 12, f"{name}: expected 12 questions"
        for q in data["questions"]:
            assert "Placeholder" not in q["text"], f"{name} Q{q['id']}: still placeholder"


def test_7_permission_layers_exist():
    perm_dir = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "permission"
    for i in range(1, 8):
        files = list(perm_dir.glob(f"layer{i}_*.py"))
        assert len(files) >= 1, f"Layer {i} missing"


def test_orchestrator_exists():
    path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "permission" / "orchestrator.py"
    assert path.exists()


def test_permission_layers_not_stub():
    """Each layer check() must return real logic, not just stub."""
    from vibecodekit_mql5.permission import (
        layer1_source_lint, layer3_ap_lint, layer5_methodology,
        layer6_quality_matrix, layer7_broker_safety,
    )
    fixture = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    for mod in [layer1_source_lint, layer3_ap_lint, layer5_methodology,
                layer6_quality_matrix, layer7_broker_safety]:
        result = mod.check(str(fixture))
        assert "stub" not in result.get("details", ""), \
            f"{mod.__name__} still returns stub"


def test_orchestrator_runs_pipeline():
    from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
    fixture = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    result = run_permission_pipeline(str(fixture), mode="PERSONAL")
    assert "all_pass" in result
    assert "results" in result
    assert result["layers_run"] >= 1


def test_quality_matrix_returns_scores():
    from vibecodekit_mql5.permission.layer6_quality_matrix import check
    fixture = REPO_ROOT / "scaffolds" / "stdlib" / "netting" / "EAName.mq5"
    result = check(str(fixture))
    assert "scores" in result
    assert "average" in result
    assert isinstance(result["scores"], dict)
    assert len(result["scores"]) == 8


def test_lint_detects_13_ap_ids():
    """Lint must detect 13 AP IDs (8 critical + 5 warning)."""
    from vibecodekit_mql5.lint import CRITICAL_DETECTORS, WARNING_DETECTORS
    assert len(CRITICAL_DETECTORS) == 8, "Expected 8 critical AP detectors"
    assert len(WARNING_DETECTORS) == 5, "Expected 5 warning AP detectors"
    all_ids = {d[0] for d in CRITICAL_DETECTORS} | {d[0] for d in WARNING_DETECTORS}
    assert len(all_ids) == 13


def test_lint_warning_detectors():
    """Warning detectors should fire on appropriate code."""
    from vibecodekit_mql5.lint import lint_file
    import tempfile
    code = """
#property strict
#property copyright "test"
void OnTick() {
    trade.Buy(0.1, Symbol(), 0.0, 0.0);
    Print("Price is " + DoubleToString(Ask));
}
"""
    with tempfile.NamedTemporaryFile(suffix=".mq5", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        findings = lint_file(Path(f.name))
    warnings = [f for f in findings if f.severity == "WARNING"]
    warning_ids = {f.ap_id for f in warnings}
    assert "AP-04" in warning_ids or "AP-06" in warning_ids or "AP-07" in warning_ids, \
        f"Expected at least one warning AP, got: {warning_ids}"
