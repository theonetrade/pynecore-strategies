"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, barmerge, close, color, input, location, math, na, nz,
    plotshape, request, script, shape, size, strategy, syminfo, ta, ticker, time, timeframe,
    timestamp
)
from pynecore.types import Series


@script.strategy(title='UT Bot Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    a=input(1, title='Key Vaule. \'This changes the sensitivity\''),
    c=input(10, title='ATR Period'),
    h=input(False, title='Signals from Heikin Ashi Candles'),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2019, title='From Year', minval=1970),
    toDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2100, title='To Year', minval=1970)
):
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate
    xATR = ta.atr(c)
    nLoss = a * xATR
    src: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close, lookahead=barmerge.lookahead_off) if h else close
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = src - nLoss if src > nz(xATRTrailingStop[1], 0) else src + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), src + nLoss) if src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), src - nLoss) if src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0) else iff_2
    pos: Series[int] = 0
    iff_3 = -1 if src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0) else iff_3
    xcolor = color.red if pos == -1 else color.green if pos == 1 else color.blue
    ema = ta.ema(src, 1)
    above = ta.crossover(ema, xATRTrailingStop)
    below = ta.crossover(xATRTrailingStop, ema)
    buy = src > xATRTrailingStop and above
    sell = src < xATRTrailingStop and below
    barbuy = src > xATRTrailingStop
    barsell = src < xATRTrailingStop
    plotshape(buy, title='Buy', text='Buy', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    plotshape(sell, title='Sell', text='Sell', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    barcolor(color.green if barbuy else na)
    barcolor(color.red if barsell else na)
    if buy and time_cond:
        strategy.entry('long', strategy.long)
    if sell and time_cond:
        strategy.entry('short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
