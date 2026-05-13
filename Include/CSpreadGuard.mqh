//+------------------------------------------------------------------+
//| CSpreadGuard.mqh — Spread anomaly protection before trade entry  |
//| vibecodekit-mql5-ea v5 · Phase B                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.2.0"
#property strict

class CSpreadGuard
{
private:
    string m_symbol;
    int    m_avg_bars;
    double m_multiplier;
    double m_max_spread_pts;
    bool   m_initialized;

public:
    CSpreadGuard() : m_avg_bars(20), m_multiplier(2.0),
                     m_max_spread_pts(0), m_initialized(false) {}

    bool Init(const string symbol, int avg_bars = 20,
              double multiplier = 2.0, double max_spread_pts = 0)
    {
        m_symbol         = (symbol == "" || symbol == NULL) ? _Symbol : symbol;
        m_avg_bars       = avg_bars;
        m_multiplier     = multiplier;
        m_max_spread_pts = max_spread_pts;
        m_initialized    = true;
        return true;
    }

    bool IsSpreadOK()
    {
        if(!m_initialized) return false;

        double current = (double)SymbolInfoInteger(m_symbol, SYMBOL_SPREAD);

        if(m_max_spread_pts > 0 && current > m_max_spread_pts)
            return false;

        double spread_arr[];
        ArraySetAsSeries(spread_arr, true);
        if(CopySpread(m_symbol, PERIOD_CURRENT, 0, m_avg_bars, spread_arr) < m_avg_bars)
            return true;  // Not enough data — allow trade

        double sum = 0;
        for(int i = 0; i < m_avg_bars; i++)
            sum += spread_arr[i];
        double avg = sum / m_avg_bars;

        return current <= avg * m_multiplier;
    }

    double CurrentSpread() const
    {
        return (double)SymbolInfoInteger(m_symbol, SYMBOL_SPREAD);
    }
};
//+------------------------------------------------------------------+
