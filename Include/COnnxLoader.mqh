//+------------------------------------------------------------------+
//| COnnxLoader.mqh — ONNX model loader for MQL5 inference           |
//| vibecodekit-mql5-ea v5 · Phase D                                  |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea contributors"
#property version   "0.5.0"
#property strict

class COnnxLoader
{
private:
    long   m_model;
    bool   m_loaded;
    string m_model_path;

public:
    COnnxLoader() : m_model(INVALID_HANDLE), m_loaded(false) {}

    bool Load(const string model_path)
    {
        m_model_path = model_path;
        m_model = OnnxCreate(model_path, 0);
        m_loaded = (m_model != INVALID_HANDLE);
        return m_loaded;
    }

    bool Predict(const double &input[], double &output[])
    {
        if(!m_loaded) return false;
        // Stub: actual ONNX inference via OnnxRun
        return true;
    }

    void Unload()
    {
        if(m_model != INVALID_HANDLE)
            OnnxRelease(m_model);
        m_model = INVALID_HANDLE;
        m_loaded = false;
    }

    bool IsLoaded() const { return m_loaded; }
};
//+------------------------------------------------------------------+
