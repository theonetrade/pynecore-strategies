"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, barmerge, color, input, location, math, na, nz, open, plot,
    plotshape, request, script, shape, size, strategy, syminfo, ta, ticker, timeframe
)
from pynecore.types import Series


@script.strategy(title='UT Bot v5', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    AllowBuy=input(defval=True, title='Allow Buy?'),
    AllowSell=input(defval=False, title='Allow Sell?'),
    h=input(False, title='Signals from Heikin Ashi Candles'),
    Price: Series[float] = input(defval=open, title='Price Source (recommended OPEN to avoid repainting)'),
    smoothing=input.string(title='Moving Average Type', defval='HMA', options=('SMA', 'EMA', 'WMA', 'HMA')),
    MA_Period=input(2, title='This changes the MAPeriod'),
    a=input.float(1, title='This changes the sensitivity', step=0.1),
    c=input(11, title='ATR Period'),
    TakeProfit=input.int(defval=50000, title='Take Profit ($)', minval=1),
    StopLoss=input.int(defval=50000, title='Stop Loss ($)', minval=1)
):
    xATR = ta.atr(c)
    nLoss = a * xATR
    src: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, Price, lookahead=barmerge.lookahead_off) if h else Price
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = src - nLoss if src > nz(xATRTrailingStop[1], 0) else src + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), src + nLoss) if src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), src - nLoss) if src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0) else iff_2
    pos: Series[int] = 0
    iff_3 = -1 if src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0) else iff_3
    xcolor = color.red if pos == -1 else color.green if pos == 1 else color.blue
    def ma_function(src, MA_Period):
        __block_result__ = na
        __switch__ = smoothing
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(src, MA_Period)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(src, MA_Period)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(src, MA_Period)
        else:
            __block_result__ = ta.hma(src, MA_Period)
        return __block_result__

    thema = ma_function(src, MA_Period)
    above = ta.crossover(thema, xATRTrailingStop)
    below = ta.crossover(xATRTrailingStop, thema)
    buy = src > xATRTrailingStop and above
    sell = src < xATRTrailingStop and below
    barbuy = src > xATRTrailingStop
    barsell = src < xATRTrailingStop
    plot(thema, title='The M.A.', color=color.green, linewidth=2)
    plot(xATRTrailingStop, title='The M.A.', color=color.red, linewidth=2)
    plotshape(buy, title='Buy', text='Buy', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, size=size.tiny)
    plotshape(sell, title='Sell', text='Sell', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, size=size.tiny)
    barcolor(color.green if barbuy else na)
    barcolor(color.red if barsell else na)
    if strategy.openprofit > TakeProfit:
        strategy.close_all(alert_message='Close- TakeProfit', comment='TP')
    if strategy.openprofit < StopLoss - StopLoss * 2:
        strategy.close_all(alert_message='Close- StopLoss', comment='SL')
    if sell and AllowSell == False:
        strategy.close('buy', comment='close buy')
    if buy and AllowBuy == False:
        strategy.close('sell', comment='close sell')
    if buy and AllowBuy:
        strategy.entry('buy', strategy.long)
    if sell and AllowSell:
        strategy.entry('sell', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
