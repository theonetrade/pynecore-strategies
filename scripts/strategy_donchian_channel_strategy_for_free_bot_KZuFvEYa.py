"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, input, plot, script, strategy, ta, time, timestamp


@script.strategy('Donchian Channel Strategy [for free bot]', overlay=True, default_qty_type=strategy.percent_of_equity, initial_capital=1000, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.036, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    buyPeriodEnter=input(10, 'Channel Period for Long enter position'),
    buyPeriodExit=input(10, 'Channel Period for Long exit position'),
    isMiddleBuy=input(True, 'Is exit on Base Line? If \'no\' - exit on bottom line'),
    takeProfitBuy=input(2.5, 'Take Profit (%) for Long position'),
    isBuy=input(True, 'Allow Long?'),
    sellPeriodEnter=input(20, 'Channel Period for Short enter position'),
    sellPeriodExit=input(20, 'Channel Period for Short exit position'),
    isMiddleSell=input(True, 'Is exit on Base Line? If \'no\' - exit on upper line'),
    takeProfitSell=input(2.5, 'Take Profit (%) for Short position'),
    isSell=input(True, 'Allow Short?'),
    startYear=input(2005, 'Test Start Year'),
    startMonth=input(1, 'Test Start Month'),
    startDay=input(1, 'Test Start Day'),
    endYear=input(2050, 'Test End Year'),
    endMonth=input(12, 'Test End Month'),
    endDay=input(30, 'Test End Day')
):
    startTest = timestamp(startYear, startMonth, startDay, 0, 0)
    endTest = timestamp(endYear, endMonth, endDay, 23, 59)
    timeRange = True if time > startTest and time < endTest else False
    BuyEnter = ta.highest(buyPeriodEnter)
    BuyExit = (ta.highest(buyPeriodExit) + ta.lowest(buyPeriodExit)) / 2 if isMiddleBuy else ta.lowest(buyPeriodExit)
    SellEnter = ta.lowest(sellPeriodEnter)
    SellExit = (ta.highest(sellPeriodExit) + ta.lowest(sellPeriodExit)) / 2 if isMiddleSell else ta.highest(sellPeriodExit)
    plot(BuyEnter, style=plot.style_line, linewidth=2, color=color.new(color.blue, 0), title='Buy Enter')
    plot(BuyExit, style=plot.style_line, linewidth=1, color=color.new(color.blue, 50), title='Buy Exit')
    plot(SellEnter, style=plot.style_line, linewidth=2, color=color.new(color.red, 0), title='Sell Enter')
    plot(SellExit, style=plot.style_line, linewidth=1, color=color.new(color.red, 50), title='Sell Exit')
    TakeProfitBuy: float = 0.0
    TakeProfitSell: float = 0.0
    if strategy.position_size > 0:
        TakeProfitBuy = strategy.position_avg_price * (1 + takeProfitBuy / 100)
    if strategy.position_size < 0:
        TakeProfitSell = strategy.position_avg_price * (1 - takeProfitSell / 100)
    if isBuy and timeRange:
        if strategy.position_size == 0:
            strategy.entry('Long', strategy.long, stop=BuyEnter)
    if strategy.position_size > 0:
        strategy.exit('Long Exit', 'Long', stop=BuyExit, limit=TakeProfitBuy)
    if isSell and timeRange:
        if strategy.position_size == 0:
            strategy.entry('Short', strategy.short, stop=SellEnter)
    if strategy.position_size < 0:
        strategy.exit('Short Exit', 'Short', stop=SellExit, limit=TakeProfitSell)
    if time > endTest:
        strategy.close_all()
        strategy.cancel_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
