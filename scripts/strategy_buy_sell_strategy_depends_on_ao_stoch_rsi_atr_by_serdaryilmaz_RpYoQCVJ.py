"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, hl2, hline, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Buy&Sell Strategy depends on AO+Stoch+RSI+ATR by SerdarYILMAZ', shorttitle='Buy&Sell Strategy', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    fast=input(title='Fast Length', defval=5),
    slow=input(title='Slow length', defval=34),
    K=input(title='K', defval=14),
    D=input(title='D', defval=3),
    smooth=input(title='smooth', defval=3),
    rsisource: Series[float] = input(title='rsi source', defval=close),
    rsilength=input(title='rsi length', defval=10),
    atrlen=input(title='ATR Length', defval=14)
):
    awesome: Series = (ta.sma(hl2, fast) - ta.sma(hl2, slow)) * 1000
    plot(awesome, style=plot.style_histogram, color=color.green if awesome > awesome[1] else color.red)
    k = ta.sma(ta.stoch(close, high, low, K), D)
    d = ta.sma(k, smooth)
    hline(80)
    hline(20)
    plot(k, color=color.new(color.blue, 0))
    rsi = ta.rsi(rsisource, rsilength)
    hline(70, color=color.orange)
    hline(30, color=color.orange)
    plot(rsi, color=color.new(color.orange, 0))
    atrvalue = ta.rma(ta.tr, atrlen)
    plot(atrvalue * 1000, color=color.new(color.green, 0))
    LongCondition = k < 20 and rsi < 30 and (awesome > awesome[1])
    ShortCondition = k > 80 and rsi > 70 and (awesome < awesome[1])
    if LongCondition:
        stoploss = low - atrvalue
        takeprofit = close + atrvalue
        strategy.entry('Long Position', strategy.long)
        strategy.exit('TP/SL', stop=stoploss, limit=takeprofit)
    if ShortCondition:
        stoploss = high + atrvalue
        takeprofit = close - atrvalue
        strategy.entry('Short Position', strategy.short)
        strategy.exit('TP/SL', stop=stoploss, limit=takeprofit)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
