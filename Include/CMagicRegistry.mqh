//+------------------------------------------------------------------+
//| CMagicRegistry.mqh — File-backed magic number reservation        |
//| vibecodekit-mql5-ea v5 · Phase A                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.1.0"
#property strict

class CMagicRegistry
{
private:
    string m_filename;
    int    m_magic;

public:
    CMagicRegistry() : m_magic(0) {}

    bool Reserve(const string ea_name, const string symbol, int desired_magic)
    {
        m_filename = ea_name + "_" + symbol + "_magic.dat";
        string full_path = TerminalInfoString(TERMINAL_DATA_PATH)
                           + "\\MQL5\\Files\\" + m_filename;

        int handle = FileOpen(m_filename, FILE_READ | FILE_TXT);
        if(handle != INVALID_HANDLE)
        {
            string stored = FileReadString(handle);
            FileClose(handle);
            int existing = (int)StringToInteger(stored);
            if(existing > 0 && existing != desired_magic)
            {
                PrintFormat("[MagicRegistry] Collision: %s/%s already uses magic %d",
                            ea_name, symbol, existing);
                return false;
            }
            if(existing == desired_magic)
            {
                m_magic = desired_magic;
                return true;
            }
        }

        handle = FileOpen(m_filename, FILE_WRITE | FILE_TXT);
        if(handle == INVALID_HANDLE) return false;
        FileWriteString(handle, IntegerToString(desired_magic));
        FileClose(handle);
        m_magic = desired_magic;
        return true;
    }

    bool Check(int magic_to_check)
    {
        if(magic_to_check == m_magic && m_magic > 0) return true;
        string search_pattern = "*_magic.dat";
        long   handle_find = FileFindFirst(search_pattern, m_filename, FILE_COMMON);
        if(handle_find == INVALID_HANDLE) return false;
        bool found = false;
        do
        {
            int fh = FileOpen(m_filename, FILE_READ | FILE_TXT);
            if(fh != INVALID_HANDLE)
            {
                string stored = FileReadString(fh);
                FileClose(fh);
                if((int)StringToInteger(stored) == magic_to_check)
                { found = true; break; }
            }
        }
        while(FileFindNext(handle_find, m_filename));
        FileFindClose(handle_find);
        return found;
    }

    string List()
    {
        string result = "";
        string fname;
        long handle_find = FileFindFirst("*_magic.dat", fname, FILE_COMMON);
        if(handle_find == INVALID_HANDLE) return result;
        do
        {
            int fh = FileOpen(fname, FILE_READ | FILE_TXT);
            if(fh != INVALID_HANDLE)
            {
                string stored = FileReadString(fh);
                FileClose(fh);
                if(result != "") result += ";";
                result += fname + "=" + stored;
            }
        }
        while(FileFindNext(handle_find, fname));
        FileFindClose(handle_find);
        return result;
    }

    void Release()
    {
        if(m_filename != "")
            FileDelete(m_filename);
        m_magic = 0;
    }

    int Magic() const { return m_magic; }
};
//+------------------------------------------------------------------+
