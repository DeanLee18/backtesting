import backtrader as bt

def add_analyzer(cerebro):
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio', timeframe=bt.TimeFrame.Days, annualize=True, riskfreerate=0) # 计算夏普比率
    # cerebro.addanalyzer(bt.analyzers.GrossLeverage, _name='_GrossLeverage')
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
