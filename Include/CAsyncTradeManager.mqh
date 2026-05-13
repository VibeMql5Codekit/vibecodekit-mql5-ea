//+------------------------------------------------------------------+
//| CAsyncTradeManager.mqh — Async trade management with handler     |
//| vibecodekit-mql5-ea v5 · Phase D                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.5.0"
#property strict

#include <Trade\Trade.mqh>

class CAsyncTradeManager
{
private:
    CTrade m_trade;
    int    m_pending_count;
    ulong  m_pending_requests[];

public:
    CAsyncTradeManager() : m_pending_count(0) {}

    bool Init(int magic, int deviation = 10)
    {
        m_trade.SetExpertMagicNumber(magic);
        m_trade.SetDeviationInPoints(deviation);
        m_trade.SetAsyncMode(true);
        return true;
    }

    ulong BuyAsync(double lots, const string symbol, double price,
                   double sl, double tp, const string comment = "")
    {
        if(!m_trade.Buy(lots, symbol, price, sl, tp, comment))
            return 0;
        ulong req_id = m_trade.ResultOrder();
        ArrayResize(m_pending_requests, m_pending_count + 1);
        m_pending_requests[m_pending_count++] = req_id;
        return req_id;
    }

    void OnTradeTransactionHandler(const MqlTradeTransaction &trans,
                                    const MqlTradeRequest &request,
                                    const MqlTradeResult &result)
    {
        if(trans.type == TRADE_TRANSACTION_REQUEST)
        {
            for(int i = 0; i < m_pending_count; i++)
            {
                if(m_pending_requests[i] == result.order)
                {
                    // Remove from pending
                    for(int j = i; j < m_pending_count - 1; j++)
                        m_pending_requests[j] = m_pending_requests[j + 1];
                    m_pending_count--;
                    break;
                }
            }
        }
    }

    int PendingCount() const { return m_pending_count; }
};
//+------------------------------------------------------------------+
