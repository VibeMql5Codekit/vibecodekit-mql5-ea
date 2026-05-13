//+------------------------------------------------------------------+
//| CMfeMaeLogger.mqh — Per-trade MFE/MAE CSV logger                 |
//| vibecodekit-mql5-ea v5 · Phase B                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.2.0"
#property strict

class CMfeMaeLogger
{
private:
    string m_filename;
    int    m_handle;
    bool   m_active;

public:
    CMfeMaeLogger() : m_handle(INVALID_HANDLE), m_active(false) {}

    bool Init(const string ea_name, const string symbol)
    {
        m_filename = ea_name + "_" + symbol + "_mfe_mae.csv";
        m_handle = FileOpen(m_filename, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
        if(m_handle == INVALID_HANDLE) return false;

        FileWriteString(m_handle, "Ticket,Symbol,Type,OpenPrice,ClosePrice,"
                                  "SL,TP,MFE,MAE,Profit,Duration\r\n");
        m_active = true;
        return true;
    }

    void LogTrade(ulong ticket, const string symbol, int type,
                  double open_price, double close_price,
                  double sl, double tp,
                  double mfe, double mae, double profit, int duration_sec)
    {
        if(!m_active || m_handle == INVALID_HANDLE) return;

        string line = StringFormat("%I64u,%s,%d,%.5f,%.5f,%.5f,%.5f,%.2f,%.2f,%.2f,%d\r\n",
                                   ticket, symbol, type, open_price, close_price,
                                   sl, tp, mfe, mae, profit, duration_sec);
        FileWriteString(m_handle, line);
        FileFlush(m_handle);
    }

    void Deinit()
    {
        if(m_handle != INVALID_HANDLE)
        {
            FileClose(m_handle);
            m_handle = INVALID_HANDLE;
        }
        m_active = false;
    }

    bool IsActive() const { return m_active; }
};
//+------------------------------------------------------------------+
