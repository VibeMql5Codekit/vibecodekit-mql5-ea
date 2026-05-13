#!/usr/bin/env python3
"""mt5-bridge tools — READ-ONLY market data and account info."""
from __future__ import annotations

TOOLS: list[dict] = [
    {"name": "market_info", "description": "Get symbol market info (bid, ask, spread, digits)",
     "inputSchema": {"type": "object",
                     "properties": {"symbol": {"type": "string"}},
                     "required": ["symbol"]}},
    {"name": "account_info", "description": "Get account info (balance, equity, margin)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "positions", "description": "List open positions (READ-ONLY)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "history", "description": "Get trade history for date range",
     "inputSchema": {"type": "object",
                     "properties": {"from_date": {"type": "string"},
                                    "to_date": {"type": "string"}}}},
]


def handle_market_info(params: dict) -> dict:
    """Get market info for a symbol via MetaTrader 5 Python package."""
    symbol = params.get("symbol", "EURUSD")
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        info = mt5.symbol_info(symbol)
        if info is None:
            return {"status": "error", "reason": f"Symbol {symbol} not found"}
        return {"status": "ok", "symbol": symbol, "bid": info.bid,
                "ask": info.ask, "spread": info.spread,
                "digits": info.digits, "point": info.point}
    except ImportError:
        return {"status": "unavailable",
                "reason": "MetaTrader5 package not installed"}


def handle_account_info(params: dict) -> dict:
    """Get account information."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        info = mt5.account_info()
        if info is None:
            return {"status": "error", "reason": "No account connected"}
        return {"status": "ok", "balance": info.balance,
                "equity": info.equity, "margin": info.margin,
                "free_margin": info.margin_free,
                "leverage": info.leverage, "currency": info.currency}
    except ImportError:
        return {"status": "unavailable",
                "reason": "MetaTrader5 package not installed"}


def handle_positions(params: dict) -> dict:
    """List open positions (read-only)."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        positions = mt5.positions_get()
        if positions is None:
            return {"status": "ok", "positions": [], "count": 0}
        pos_list = [{"ticket": p.ticket, "symbol": p.symbol,
                     "type": "BUY" if p.type == 0 else "SELL",
                     "volume": p.volume, "price_open": p.price_open,
                     "sl": p.sl, "tp": p.tp, "profit": p.profit}
                    for p in positions]
        return {"status": "ok", "positions": pos_list,
                "count": len(pos_list)}
    except ImportError:
        return {"status": "unavailable",
                "reason": "MetaTrader5 package not installed"}


def handle_history(params: dict) -> dict:
    """Get trade history (read-only)."""
    try:
        import MetaTrader5 as mt5
        from datetime import datetime
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        from_date = datetime.fromisoformat(
            params.get("from_date", "2024-01-01"))
        to_date = datetime.fromisoformat(
            params.get("to_date", datetime.now().isoformat()[:10]))
        deals = mt5.history_deals_get(from_date, to_date)
        if deals is None:
            return {"status": "ok", "deals": [], "count": 0}
        deal_list = [{"ticket": d.ticket, "symbol": d.symbol,
                      "type": d.type, "volume": d.volume,
                      "price": d.price, "profit": d.profit}
                     for d in deals[:100]]
        return {"status": "ok", "deals": deal_list,
                "count": len(deal_list)}
    except ImportError:
        return {"status": "unavailable",
                "reason": "MetaTrader5 package not installed"}


HANDLERS = {"market_info": handle_market_info,
            "account_info": handle_account_info,
            "positions": handle_positions,
            "history": handle_history}
