//+------------------------------------------------------------------+
//| CAsyncTradeManager.mqh — Async trade management with handler     |
//| vibecodekit-mql5-ea v5 · Phase D                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.5.0"
#property strict

#include <Trade\Trade.mqh>

enum ENUM_ASYNC_STATUS { ASYNC_PENDING, ASYNC_FILLED, ASYNC_REJECTED };

struct AsyncRequest
{
    ulong              request_id;
    ulong              order;
    ENUM_ASYNC_STATUS  status;
    uint               retcode;
    datetime           sent_time;
};

class CAsyncTradeManager
{
private:
    CTrade         m_trade;
    AsyncRequest   m_requests[];
    int            m_count;
    int            m_max_pending;

public:
    CAsyncTradeManager() : m_count(0), m_max_pending(50) {}

    bool Init(int magic, int deviation = 10, int max_pending = 50)
    {
        m_trade.SetExpertMagicNumber(magic);
        m_trade.SetDeviationInPoints(deviation);
        m_trade.SetAsyncMode(true);
        m_max_pending = max_pending;
        return true;
    }

    ulong BuyAsync(double lots, const string symbol, double price,
                   double sl, double tp, const string comment = "")
    {
        if(m_count >= m_max_pending) return 0;
        if(!m_trade.Buy(lots, symbol, price, sl, tp, comment))
            return 0;

        MqlTradeResult res;
        m_trade.Result(res);
        ulong req_id = res.request_id;
        AddRequest(req_id);
        return req_id;
    }

    ulong SellAsync(double lots, const string symbol, double price,
                    double sl, double tp, const string comment = "")
    {
        if(m_count >= m_max_pending) return 0;
        if(!m_trade.Sell(lots, symbol, price, sl, tp, comment))
            return 0;

        MqlTradeResult res;
        m_trade.Result(res);
        ulong req_id = res.request_id;
        AddRequest(req_id);
        return req_id;
    }

    void OnTradeTransactionHandler(const MqlTradeTransaction &trans,
                                    const MqlTradeRequest &request,
                                    const MqlTradeResult &result)
    {
        if(trans.type != TRADE_TRANSACTION_REQUEST) return;

        for(int i = 0; i < m_count; i++)
        {
            if(m_requests[i].request_id == result.request_id)
            {
                m_requests[i].order   = result.order;
                m_requests[i].retcode = result.retcode;
                if(result.retcode == TRADE_RETCODE_DONE)
                    m_requests[i].status = ASYNC_FILLED;
                else
                    m_requests[i].status = ASYNC_REJECTED;
                break;
            }
        }
    }

    void CleanupCompleted()
    {
        int write = 0;
        for(int i = 0; i < m_count; i++)
        {
            if(m_requests[i].status == ASYNC_PENDING)
            {
                if(write != i)
                    m_requests[write] = m_requests[i];
                write++;
            }
        }
        m_count = write;
        ArrayResize(m_requests, m_count);
    }

    int PendingCount() const
    {
        int cnt = 0;
        for(int i = 0; i < m_count; i++)
            if(m_requests[i].status == ASYNC_PENDING) cnt++;
        return cnt;
    }

    int TotalCount()   const { return m_count; }
    int MaxPending()   const { return m_max_pending; }

private:
    void AddRequest(ulong req_id)
    {
        ArrayResize(m_requests, m_count + 1);
        m_requests[m_count].request_id = req_id;
        m_requests[m_count].order      = 0;
        m_requests[m_count].status     = ASYNC_PENDING;
        m_requests[m_count].retcode    = 0;
        m_requests[m_count].sent_time  = TimeCurrent();
        m_count++;
    }
};
//+------------------------------------------------------------------+
