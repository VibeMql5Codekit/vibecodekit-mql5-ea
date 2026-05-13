#!/usr/bin/env python3
"""Parse MT5 Strategy Tester XML reports and extract key metrics.

Usage:
    mql5-backtest report.xml
    mql5-backtest report.xml --json
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BacktestMetrics:
    symbol: str = ""
    period: str = ""
    total_trades: int = 0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    recovery_factor: float = 0.0
    win_rate: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0


def parse_report(path: Path) -> BacktestMetrics:
    """Parse a Strategy Tester XML report."""
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r'encoding="[^"]*"', 'encoding="utf-8"', text)
    root = ET.fromstring(text)
    m = BacktestMetrics()

    def _find_text(tag: str, default: str = "0") -> str:
        el = root.find(f".//{tag}")
        return el.text.strip() if el is not None and el.text else default

    m.symbol = _find_text("Symbol", "UNKNOWN")
    m.period = _find_text("Period", "H1")
    m.total_trades = int(float(_find_text("TotalTrades")))
    m.profit_factor = float(_find_text("ProfitFactor"))
    m.expected_payoff = float(_find_text("ExpectedPayoff"))
    m.max_drawdown_pct = float(_find_text("MaxDrawdownPercent", "0"))
    m.sharpe_ratio = float(_find_text("SharpeRatio"))
    m.recovery_factor = float(_find_text("RecoveryFactor"))
    m.gross_profit = float(_find_text("GrossProfit"))
    m.gross_loss = float(_find_text("GrossLoss"))
    m.net_profit = m.gross_profit + m.gross_loss
    if m.total_trades > 0:
        wins = int(float(_find_text("WinTrades", "0")))
        m.win_rate = (wins / m.total_trades) * 100.0

    return m


def main() -> int:
    parser = argparse.ArgumentParser(description="MT5 backtest report parser")
    parser.add_argument("report", type=Path, help="XML report file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.report.exists():
        print(f"Error: {args.report} not found", file=sys.stderr)
        return 1

    metrics = parse_report(args.report)

    if args.json:
        import json
        print(json.dumps(asdict(metrics), indent=2))
    else:
        print(f"Symbol: {metrics.symbol} ({metrics.period})")
        print(f"Trades: {metrics.total_trades}")
        print(f"PF: {metrics.profit_factor:.2f}")
        print(f"Sharpe: {metrics.sharpe_ratio:.2f}")
        print(f"Max DD: {metrics.max_drawdown_pct:.2f}%")
        print(f"Win rate: {metrics.win_rate:.1f}%")
        print(f"Net profit: {metrics.net_profit:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
