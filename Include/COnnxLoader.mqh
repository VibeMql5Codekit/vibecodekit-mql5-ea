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
    long   m_input_shape[];
    long   m_output_shape[];

public:
    COnnxLoader() : m_model(INVALID_HANDLE), m_loaded(false) {}

    bool Load(const string model_path)
    {
        m_model_path = model_path;
        m_model = OnnxCreate(model_path, 0);
        m_loaded = (m_model != INVALID_HANDLE);
        if(m_loaded)
            PrintFormat("COnnxLoader: loaded %s", model_path);
        else
            PrintFormat("COnnxLoader: FAILED to load %s", model_path);
        return m_loaded;
    }

    bool SetInputShape(const long &shape[])
    {
        if(!m_loaded) return false;
        ArrayResize(m_input_shape, ArraySize(shape));
        ArrayCopy(m_input_shape, shape);
        return OnnxSetInputShape(m_model, 0, m_input_shape);
    }

    bool SetOutputShape(const long &shape[])
    {
        if(!m_loaded) return false;
        ArrayResize(m_output_shape, ArraySize(shape));
        ArrayCopy(m_output_shape, shape);
        return OnnxSetOutputShape(m_model, 0, m_output_shape);
    }

    bool Predict(const double &input[], double &output[])
    {
        if(!m_loaded) return false;

        vectorf in_vec;
        in_vec.Resize(ArraySize(input));
        for(int i = 0; i < ArraySize(input); i++)
            in_vec[i] = (float)input[i];

        vectorf out_vec;
        if(!OnnxRun(m_model, ONNX_DEFAULT, in_vec, out_vec))
        {
            PrintFormat("COnnxLoader: OnnxRun failed, err=%d", GetLastError());
            return false;
        }

        ArrayResize(output, (int)out_vec.Size());
        for(int i = 0; i < (int)out_vec.Size(); i++)
            output[i] = (double)out_vec[i];
        return true;
    }

    bool PredictClass(const double &input[], int &predicted_class)
    {
        double output[];
        if(!Predict(input, output)) return false;

        predicted_class = 0;
        double max_val = output[0];
        for(int i = 1; i < ArraySize(output); i++)
        {
            if(output[i] > max_val)
            {
                max_val = output[i];
                predicted_class = i;
            }
        }
        return true;
    }

    void Unload()
    {
        if(m_model != INVALID_HANDLE)
            OnnxRelease(m_model);
        m_model = INVALID_HANDLE;
        m_loaded = false;
    }

    bool   IsLoaded()  const { return m_loaded; }
    string ModelPath() const { return m_model_path; }
};
//+------------------------------------------------------------------+
