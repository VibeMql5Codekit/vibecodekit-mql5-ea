//+------------------------------------------------------------------+
//| EAName.mq5 — Worked example: MACD+SAR EURUSD H1 portfolio       |
//| Full 8-step walkthrough from scaffold to ship                     |
//+------------------------------------------------------------------+
#property copyright "vibecodekit-mql5-ea worked example"
#property version   "1.00"
#property strict

#include <Expert\Expert.mqh>
#include <Expert\Signal\SignalMACD.mqh>
#include <Expert\Signal\SignalSAR.mqh>
#include <Expert\Trailing\TrailingParabolicSAR.mqh>
#include <Expert\Money\MoneyFixedRisk.mqh>

input int    InpMagic = 20240101;
input double InpRisk  = 1.0;

CExpert expert;

int OnInit()
{
    if(!expert.Init(_Symbol, _Period, true, InpMagic)) return INIT_FAILED;
    CExpertSignal *sig = new CExpertSignal();
    if(!expert.InitSignal(sig)) return INIT_FAILED;
    sig.AddFilter(new CSignalMACD());
    sig.AddFilter(new CSignalSAR());
    CTrailingPSAR *trail = new CTrailingPSAR();
    if(!expert.InitTrailing(trail)) return INIT_FAILED;
    CMoneyFixedRisk *money = new CMoneyFixedRisk();
    money.Percent(InpRisk);
    if(!expert.InitMoney(money)) return INIT_FAILED;
    if(!expert.InitTrade(InpMagic)) return INIT_FAILED;
    expert.OnInit();
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { expert.OnDeinit(); }
void OnTick()                   { expert.OnTick(); }
void OnTrade()                  { expert.OnTrade(); }
