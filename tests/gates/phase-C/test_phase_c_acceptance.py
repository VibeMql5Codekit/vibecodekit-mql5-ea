"""Phase C acceptance tests — methodology gate."""
import sys
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
        assert len(data["questions"]) == 25, f"{name}: expected 25 questions"
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


def test_8_rri_templates_exist():
    tmpl_dir = REPO_ROOT / "docs" / "rri-templates"
    assert tmpl_dir.exists(), "docs/rri-templates/ missing"
    for i in range(1, 9):
        files = list(tmpl_dir.glob(f"step-{i}-*.tmpl"))
        assert len(files) >= 1, f"step-{i} template missing"


def test_matrix_has_8x8_dimensions():
    from vibecodekit_mql5.rri.matrix import DIMENSIONS, AXES
    assert len(DIMENSIONS) == 8, f"Expected 8 dimensions, got {len(DIMENSIONS)}"
    assert len(AXES) == 8, f"Expected 8 axes, got {len(AXES)}"


def test_matrix_html_output():
    from vibecodekit_mql5.rri.matrix import evaluate_matrix, render_html
    result = evaluate_matrix(mode="TEAM")
    html = render_html(result)
    assert "<table" in html
    assert "</table>" in html
    assert result["total_cells"] == 64
    assert result["gate_pass"] is True


def test_rri_cli_session_returns_questions():
    from vibecodekit_mql5.rri.cli import build_rri_session
    result = build_rri_session(mode="PERSONAL", persona="trader")
    assert result["mode"] == "PERSONAL"
    assert result["total_questions"] > 0
    assert result["interviews"][0]["persona"] == "trader"


def test_rri_specialized_reviews_return_questions():
    from vibecodekit_mql5.rri.rri_bt import build_backtest_review
    from vibecodekit_mql5.rri.rri_chart import build_chart_review
    from vibecodekit_mql5.rri.rri_rr import build_risk_reward_review

    bt = build_backtest_review(mode="TEAM", personas="trader")
    rr = build_risk_reward_review(mode="TEAM", persona="trader")
    chart = build_chart_review(mode="TEAM", persona="trader")

    assert bt["reviews"][0]["questions"]
    assert bt["matrix"]["gate_pass"] is True
    assert rr["total_questions"] > 0
    assert chart["total_questions"] > 0


def test_persona_enterprise_has_25_questions():
    personas_dir = REPO_ROOT / "docs" / "rri-personas"
    for name in ["trader", "risk-auditor", "broker-engineer",
                 "strategy-architect", "devops", "perf-analyst"]:
        data = yaml.safe_load((personas_dir / f"{name}.yaml").read_text())
        enterprise_qs = [q for q in data["questions"] if "ENTERPRISE" in q.get("mode", [])]
        assert len(enterprise_qs) == 25, f"{name}: expected 25 ENTERPRISE, got {len(enterprise_qs)}"


def test_review_scripts_not_stubs():
    for mod_name in ["review", "eng_review", "ceo_review", "cso", "investigate"]:
        mod_path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "review" / f"{mod_name}.py"
        assert mod_path.exists(), f"{mod_name}.py missing"
        content = mod_path.read_text()
        assert "stub" not in content.lower(), f"{mod_name} still a stub"
        assert len(content.splitlines()) > 20, f"{mod_name} too short"


def test_review_7_perspectives():
    from vibecodekit_mql5.review.review import PERSPECTIVES
    assert len(PERSPECTIVES) == 7, f"Expected 7 perspectives, got {len(PERSPECTIVES)}"


def test_cso_10_security_checks():
    from vibecodekit_mql5.review.cso import SECURITY_CHECKS
    assert len(SECURITY_CHECKS) == 10, f"Expected 10 checks, got {len(SECURITY_CHECKS)}"


def test_eng_review_8_invariants():
    from vibecodekit_mql5.review.eng_review import INVARIANTS
    assert len(INVARIANTS) == 8, f"Expected 8 invariants, got {len(INVARIANTS)}"


def test_ceo_review_4_modes():
    from vibecodekit_mql5.review.ceo_review import CEO_MODES
    assert len(CEO_MODES) == 4
    assert "SCOPE_EXPANSION" in CEO_MODES
    assert "REDUCTION" in CEO_MODES


def test_permission_orchestrator_has_main():
    from vibecodekit_mql5.permission.orchestrator import main
    assert callable(main)


def test_step_workflow_8_steps():
    from vibecodekit_mql5.rri.step_workflow import WORKFLOW_STEPS
    assert len(WORKFLOW_STEPS) == 8, f"Expected 8 workflow steps, got {len(WORKFLOW_STEPS)}"


def test_orchestrator_enterprise_runs_all_7_layers():
    from vibecodekit_mql5.permission.orchestrator import MODE_LAYERS
    assert len(MODE_LAYERS["ENTERPRISE"]) == 7
