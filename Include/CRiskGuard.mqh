//+------------------------------------------------------------------+
//| CRiskGuard.mqh — Daily-loss limit + max-positions enforcement    |
//| vibecodekit-mql5-ea v5 · Phase A                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.1.0"
#property strict

#include <Trade\AccountInfo.mqh>
#include <Trade\PositionInfo.mqh>

class CRiskGuard
{
private:
    double m_daily_loss_limit;
    int    m_max_positions;
    double m_start_balance;
    bool   m_disabled;
    string m_ea_comment;
    int    m_magic;

public:
    CRiskGuard() : m_daily_loss_limit(0), m_max_positions(0),
                   m_start_balance(0), m_disabled(false), m_magic(0) {}

    bool Init(double daily_loss_pct, int max_positions, int magic,
              const string comment = "")
    {
        if(daily_loss_pct <= 0 || daily_loss_pct > 100) return false;
        if(max_positions <= 0) return false;

        m_daily_loss_limit = daily_loss_pct;
        m_max_positions    = max_positions;
        m_magic            = magic;
        m_ea_comment       = comment;

        CAccountInfo acc;
        m_start_balance = acc.Balance();
        m_disabled      = false;
        return true;
    }

    bool CanOpenTrade()
    {
        if(m_disabled) return false;

        CAccountInfo acc;
        double current = acc.Balance();
        double loss_pct = 0;
        if(m_start_balance > 0)
            loss_pct = ((m_start_balance - current) / m_start_balance) * 100.0;

        if(loss_pct >= m_daily_loss_limit)
        {
            m_disabled = true;
            PrintFormat("[RiskGuard] Daily loss %.2f%% >= limit %.2f%%. EA disabled.",
                        loss_pct, m_daily_loss_limit);
            return false;
        }

        int count = CountOpenPositions();
        if(count >= m_max_positions)
        {
            PrintFormat("[RiskGuard] Open positions %d >= max %d. Blocked.",
                        count, m_max_positions);
            return false;
        }
        return true;
    }

    int CountOpenPositions()
    {
        int count = 0;
        for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
            if(PositionSelectByTicket(PositionGetTicket(i)))
            {
                if(m_magic == 0 || PositionGetInteger(POSITION_MAGIC) == m_magic)
                    count++;
            }
        }
        return count;
    }

    void ResetDaily()
    {
        CAccountInfo acc;
        m_start_balance = acc.Balance();
        m_disabled      = false;
    }

    bool   IsDisabled()       const { return m_disabled; }
    double DailyLossLimit()   const { return m_daily_loss_limit; }
    int    MaxPositions()     const { return m_max_positions; }
    double StartBalance()     const { return m_start_balance; }
};
//+------------------------------------------------------------------+
