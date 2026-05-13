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


def handle_symbols_list(params: dict) -> dict:
    """List available symbols."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        group = params.get("group", "")
        symbols = mt5.symbols_get(group=group) if group else mt5.symbols_get()
        if symbols is None:
            return {"status": "ok", "symbols": [], "count": 0}
        sym_list = [{"name": s.name, "digits": s.digits, "trade_mode": s.trade_mode}
                    for s in symbols[:200]]
        return {"status": "ok", "symbols": sym_list, "count": len(sym_list)}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


def handle_rates_copy(params: dict) -> dict:
    """Copy OHLCV rates for a symbol (READ-ONLY)."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        symbol = params.get("symbol", "EURUSD")
        timeframe = getattr(mt5, f"TIMEFRAME_{params.get('timeframe', 'H1')}", mt5.TIMEFRAME_H1)
        count = min(params.get("count", 100), 1000)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            return {"status": "error", "reason": "No rates available"}
        rate_list = [{"time": int(r[0]), "open": r[1], "high": r[2],
                      "low": r[3], "close": r[4], "volume": int(r[5])}
                     for r in rates[-50:]]
        return {"status": "ok", "symbol": symbol, "count": len(rates), "rates": rate_list}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


def handle_tick_last(params: dict) -> dict:
    """Get last tick for a symbol (READ-ONLY)."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        symbol = params.get("symbol", "EURUSD")
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return {"status": "error", "reason": f"No tick for {symbol}"}
        return {"status": "ok", "symbol": symbol, "bid": tick.bid,
                "ask": tick.ask, "last": tick.last, "volume": tick.volume,
                "time": tick.time}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


def handle_terminal_info(params: dict) -> dict:
    """Get terminal info (READ-ONLY)."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        info = mt5.terminal_info()
        if info is None:
            return {"status": "error", "reason": "Terminal info unavailable"}
        return {"status": "ok", "build": info.build, "connected": info.connected,
                "trade_allowed": info.trade_allowed, "path": info.path}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


def handle_positions_history(params: dict) -> dict:
    """Get closed positions history (READ-ONLY)."""
    try:
        import MetaTrader5 as mt5
        from datetime import datetime
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        from_date = datetime.fromisoformat(params.get("from_date", "2024-01-01"))
        to_date = datetime.fromisoformat(params.get("to_date", datetime.now().isoformat()[:10]))
        orders = mt5.history_orders_get(from_date, to_date)
        if orders is None:
            return {"status": "ok", "orders": [], "count": 0}
        order_list = [{"ticket": o.ticket, "symbol": o.symbol,
                       "type": o.type, "volume_initial": o.volume_initial,
                       "price_open": o.price_open, "state": o.state}
                      for o in orders[:100]]
        return {"status": "ok", "orders": order_list, "count": len(order_list)}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


def handle_market_book(params: dict) -> dict:
    """Get market depth / book (READ-ONLY)."""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return {"status": "error", "reason": "MT5 not initialized"}
        symbol = params.get("symbol", "EURUSD")
        if not mt5.market_book_add(symbol):
            return {"status": "error", "reason": f"Cannot subscribe to {symbol} book"}
        book = mt5.market_book_get(symbol)
        mt5.market_book_release(symbol)
        if book is None:
            return {"status": "ok", "symbol": symbol, "book": []}
        entries = [{"type": "BUY" if b.type == 1 else "SELL",
                    "price": b.price, "volume": b.volume}
                   for b in book[:20]]
        return {"status": "ok", "symbol": symbol, "book": entries}
    except ImportError:
        return {"status": "unavailable", "reason": "MetaTrader5 package not installed"}


# Register new tools in TOOLS list
TOOLS.extend([
    {"name": "symbols_list", "description": "List available trading symbols (READ-ONLY)",
     "inputSchema": {"type": "object", "properties": {"group": {"type": "string"}}}},
    {"name": "rates_copy", "description": "Copy OHLCV rates for a symbol (READ-ONLY)",
     "inputSchema": {"type": "object",
                     "properties": {"symbol": {"type": "string"}, "timeframe": {"type": "string"},
                                    "count": {"type": "integer"}},
                     "required": ["symbol"]}},
    {"name": "tick_last", "description": "Get last tick for a symbol (READ-ONLY)",
     "inputSchema": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}},
    {"name": "terminal_info", "description": "Get terminal info (build, connected, path) (READ-ONLY)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "positions_history", "description": "Get closed positions/orders history (READ-ONLY)",
     "inputSchema": {"type": "object",
                     "properties": {"from_date": {"type": "string"}, "to_date": {"type": "string"}}}},
    {"name": "market_book", "description": "Get market depth / order book (READ-ONLY)",
     "inputSchema": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}},
])

HANDLERS = {"market_info": handle_market_info,
            "account_info": handle_account_info,
            "positions": handle_positions,
            "history": handle_history,
            "symbols_list": handle_symbols_list,
            "rates_copy": handle_rates_copy,
            "tick_last": handle_tick_last,
            "terminal_info": handle_terminal_info,
            "positions_history": handle_positions_history,
            "market_book": handle_market_book}
