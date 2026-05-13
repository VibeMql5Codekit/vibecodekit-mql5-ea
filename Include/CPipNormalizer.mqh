//+------------------------------------------------------------------+
//| CPipNormalizer.mqh — Cross-broker pip math (FLAGSHIP)            |
//| vibecodekit-mql5-ea v5 · Phase A                                  |
//|                                                                  |
//| Truth table:                                                     |
//|   pip = (digits ∈ {3,5}) ? 10 * point : 1 * point               |
//|                                                                  |
//| Supported digit classes:                                         |
//|   5d — EURUSD (1.12345)  → pip = 10 * 0.00001 = 0.0001         |
//|   4d — USDJPY-old (123.45) → pip = 1 * 0.01 = 0.01             |
//|   3d — XAUUSD-Exness (1850.123) → pip = 10 * 0.001 = 0.01      |
//|   2d — XAUUSD-ICM (1850.12) → pip = 1 * 0.01 = 0.01            |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.1.0"
#property strict

#include <Trade\SymbolInfo.mqh>

class CPipNormalizer
{
private:
    string m_symbol;
    int    m_digits;
    double m_point;
    double m_pip;
    double m_pip_in_points;
    double m_tick_size;
    double m_tick_value;
    double m_pip_value_per_lot;
    long   m_stops_level;
    long   m_freeze_level;
    bool   m_initialized;

public:
    CPipNormalizer() : m_initialized(false), m_digits(0), m_point(0),
                       m_pip(0), m_pip_in_points(0), m_tick_size(0),
                       m_tick_value(0), m_pip_value_per_lot(0),
                       m_stops_level(0), m_freeze_level(0) {}

    bool Init(const string symbol = NULL)
    {
        m_symbol = (symbol == NULL || symbol == "") ? _Symbol : symbol;
        if(!SymbolSelect(m_symbol, true))
            return false;

        m_digits      = (int)SymbolInfoInteger(m_symbol, SYMBOL_DIGITS);
        m_point       = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
        m_tick_size   = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_SIZE);
        m_tick_value  = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE);
        m_stops_level = SymbolInfoInteger(m_symbol, SYMBOL_TRADE_STOPS_LEVEL);
        m_freeze_level= SymbolInfoInteger(m_symbol, SYMBOL_TRADE_FREEZE_LEVEL);

        if(m_point <= 0 || m_tick_size <= 0)
            return false;

        m_pip_in_points = (m_digits == 3 || m_digits == 5) ? 10.0 : 1.0;
        m_pip           = m_pip_in_points * m_point;

        if(m_tick_size > 0)
            m_pip_value_per_lot = (m_pip / m_tick_size) * m_tick_value;
        else
            m_pip_value_per_lot = 0;

        m_initialized = true;
        return true;
    }

    double Pips(int pips) const
    {
        return m_pip * pips;
    }

    double PriceToPips(double dist) const
    {
        if(m_pip <= 0) return 0;
        return MathAbs(dist) / m_pip;
    }

    double PipValue(int pips, double lots) const
    {
        return m_pip_value_per_lot * pips * lots;
    }

    double LotForRisk(double risk_money, int sl_pips) const
    {
        if(sl_pips <= 0 || m_pip_value_per_lot <= 0) return 0;
        double lot_min  = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double lot_max  = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
        double lot_step = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        double raw = risk_money / (sl_pips * m_pip_value_per_lot);
        if(lot_step > 0)
            raw = MathFloor(raw / lot_step) * lot_step;
        return MathMax(lot_min, MathMin(lot_max, raw));
    }

    bool IsValidSLDistance(int sl_pips) const
    {
        long points_distance = (long)(sl_pips * m_pip_in_points);
        return points_distance >= m_stops_level;
    }

    int ClampSLPips(int desired) const
    {
        long min_points = MathMax(m_stops_level, m_freeze_level + 1);
        int  min_pips   = (int)MathCeil((double)min_points / m_pip_in_points);
        return MathMax(desired, min_pips);
    }

    // Getters
    string Symbol()          const { return m_symbol; }
    int    Digits()          const { return m_digits; }
    double Point()           const { return m_point; }
    double Pip()             const { return m_pip; }
    double PipInPoints()     const { return m_pip_in_points; }
    double TickSize()        const { return m_tick_size; }
    double TickValue()       const { return m_tick_value; }
    double PipValuePerLot()  const { return m_pip_value_per_lot; }
    long   StopsLevel()      const { return m_stops_level; }
    long   FreezeLevel()     const { return m_freeze_level; }
    bool   IsInitialized()   const { return m_initialized; }
};
//+------------------------------------------------------------------+
