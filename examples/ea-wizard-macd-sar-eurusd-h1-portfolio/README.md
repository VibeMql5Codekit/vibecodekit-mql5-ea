# Worked Example: MACD+SAR EURUSD H1 Portfolio

Full 8-step walkthrough demonstrating the vibecodekit-mql5-ea methodology.

## Steps

1. `/mql5-build --preset wizard-composable --stack netting --name EAWizardMacdSar`
2. `/mql5-lint EAWizardMacdSar.mq5`
3. `/mql5-compile EAWizardMacdSar.mq5`
4. `/mql5-backtest report.xml`
5. `/mql5-walkforward is.xml oos.xml`
6. `/mql5-multibroker fxpro.xml exness.xml icm.xml`
7. `/mql5-trader-check --ea EAWizardMacdSar.mq5`
8. `/mql5-ship`

## Results

See `results/` directory for backtest XML, multibroker CSV, canary log.
