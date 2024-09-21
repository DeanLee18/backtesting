def set_broker(cerebro, cash=50000, slip_perc=0.0001, commission=0.002):
    cerebro.broker.setcash(cash)
    cerebro.broker.set_slippage_perc(perc=slip_perc)
    cerebro.broker.setcommission(commission=commission)
