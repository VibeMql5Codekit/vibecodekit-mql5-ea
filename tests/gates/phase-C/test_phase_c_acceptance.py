"""Phase C acceptance tests — methodology gate (stub)."""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

def test_6_persona_yamls_exist():
    personas_dir = REPO_ROOT / "docs" / "rri-personas"
    for name in ["trader", "risk-auditor", "broker-engineer",
                 "strategy-architect", "devops", "perf-analyst"]:
        assert (personas_dir / f"{name}.yaml").exists()

def test_7_permission_layers_exist():
    perm_dir = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "permission"
    for i in range(1, 8):
        files = list(perm_dir.glob(f"layer{i}_*.py"))
        assert len(files) >= 1, f"Layer {i} missing"

def test_orchestrator_exists():
    path = REPO_ROOT / "scripts" / "vibecodekit_mql5" / "permission" / "orchestrator.py"
    assert path.exists()
