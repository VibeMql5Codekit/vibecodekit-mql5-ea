#!/usr/bin/env python3
"""8-step workflow state machine for MQL5 EA development."""
from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class StepState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class Step(NamedTuple):
    id: int
    name: str
    command: str
    state: StepState = StepState.PENDING


WORKFLOW_STEPS = [
    Step(1, "Scan", "/mql5-scan"),
    Step(2, "RRI", "/mql5-rri"),
    Step(3, "Vision", "/mql5-vision"),
    Step(4, "Blueprint", "/mql5-blueprint"),
    Step(5, "Build", "/mql5-build"),
    Step(6, "Lint + Compile", "/mql5-lint && /mql5-compile"),
    Step(7, "Backtest + Validate", "/mql5-backtest && /mql5-walkforward"),
    Step(8, "Ship", "/mql5-ship"),
]


class WorkflowEngine:
    """Simple state machine for 8-step EA workflow."""

    def __init__(self, mode: str = "TEAM"):
        self.mode = mode
        self.steps = {s.id: s._replace(state=StepState.PENDING) for s in WORKFLOW_STEPS}
        self.current_step = 1

    def can_advance(self) -> bool:
        step = self.steps.get(self.current_step)
        return step is not None and step.state == StepState.DONE

    def advance(self) -> int | None:
        if self.can_advance():
            self.current_step += 1
            return self.current_step if self.current_step <= 8 else None
        return None

    def complete_step(self, step_id: int):
        if step_id in self.steps:
            self.steps[step_id] = self.steps[step_id]._replace(state=StepState.DONE)

    def skip_step(self, step_id: int):
        if step_id in self.steps:
            self.steps[step_id] = self.steps[step_id]._replace(state=StepState.SKIPPED)

    def status(self) -> dict:
        return {
            "mode": self.mode,
            "current": self.current_step,
            "steps": {s.id: {"name": s.name, "state": s.state.value}
                      for s in self.steps.values()},
        }
