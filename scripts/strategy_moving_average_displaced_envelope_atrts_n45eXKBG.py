"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barcolor, close, color, input, math, nz, plot, script, strategy, ta
from pynecore.types import PersistentSeries, Series


@script.strategy(title='Moving Average Displaced Envelope & ATRTS', shorttitle='MADE+ATR', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    tradeDirection=input.string('Both', title='Trade Direction', options=('Both', 'Long', 'Short')),
    Price: Series[float] = input(title='Source', defval=close),
    Period=input.int(defval=9, minval=1),
    perAb=input.float(title='Percent above', defval=0.5, minval=0.01, step=0.1),
    perBl=input.float(title='Percent below', defval=0.5, minval=0.01, step=0.1),
    disp=input.int(title='Displacement', defval=13, minval=1),
    nATRPeriod=input(15),
    nATRMultip=input(2),
    useATR=input(False, title='ATR Filter'),
    reverse=input(False, title='Trade reverse')
):
    longAllowed = tradeDirection == 'Long' or tradeDirection == 'Both'
    shortAllowed = tradeDirection == 'Short' or tradeDirection == 'Both'
    pos: Series[int] = 0
    sEMA: Series = ta.ema(Price, Period)
    top = sEMA[disp] * ((100 + perAb) / 100)
    bott = sEMA[disp] * ((100 - perBl) / 100)
    xATR = ta.atr(nATRPeriod)
    xHHs = ta.sma(ta.highest(nATRPeriod), nATRPeriod)
    xLLs = ta.sma(ta.lowest(nATRPeriod), nATRPeriod)
    nSpread = (xHHs - xLLs) / 2
    nLoss = nATRMultip * xATR
    xATRTrailingStop: PersistentSeries[float] = 0.0
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), close - nLoss) if close > nz(xATRTrailingStop[1], 0) and close[1] > nz(xATRTrailingStop[1], 0) else math.min(nz(xATRTrailingStop[1]), close + nLoss) if close < nz(xATRTrailingStop[1], 0) and close[1] < nz(xATRTrailingStop[1], 0) else close - nLoss if close > nz(xATRTrailingStop[1], 0) else close + nLoss
    ATRLong = True if close > xATRTrailingStop else False
    ATRShort = True if close < xATRTrailingStop else False
    iff_1 = 1 if close > top else pos[1]
    pos = -1 if close < bott else iff_1
    iff_2 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_2
    clr = strategy.position_size
    if possig == 1:
        if longAllowed and ATRLong:
            strategy.entry('Long', strategy.long)
        else:
            if ATRLong or strategy.position_size > 0:
                strategy.close_all()
    if possig == -1:
        if shortAllowed and ATRShort:
            strategy.entry('Short', strategy.short)
        else:
            if ATRShort or strategy.position_size < 0:
                strategy.close_all()
    if possig == 0:
        strategy.close_all()
    plot(xATRTrailingStop[1], color=color.blue, title='ATR Trailing Stop')
    barcolor(color.new('#B50404') if clr < 0 else color.new('#079605') if clr > 0 else color.new('#0536B3'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)