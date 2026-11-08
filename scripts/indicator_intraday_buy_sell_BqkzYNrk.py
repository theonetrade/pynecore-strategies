"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, barcolor, barstate, close, color, high, input, location,
    low, na, open, plot, plotshape, script, shape, ta
)


@script.indicator(title='CRUDE OIL BUY/SELL', shorttitle='CRUDE Scalp |3 Min', precision=2, overlay=True)
def main(
    Rsi_value=input.int(14, title='RSI Length', step=1),
    hl=input.int(80, title='Higher Value of RSI', step=1),
    ll=input.int(20, title='Lower value of RSI', step=1),
    sma_value=input.int(70, title='SMA Length', step=1)
):
    rs = ta.rsi(close, Rsi_value)
    sma1 = ta.sma(close, sma_value)
    dist_SMA: int = 1
    candle_length: int = 1
    iff_1 = color.new(color.red, 30) if high < sma1 else color.new(color.yellow, 30)
    iff_2 = color.new(color.lime, 30) if low > sma1 else iff_1
    mycolor = color.new(color.yellow, 30) if rs >= hl or rs <= ll else iff_2
    gaps = sma1 + dist_SMA
    gapb = sma1 - dist_SMA
    chartgap = cast_bool(gaps) or cast_bool(gapb)
    gap1 = sma1 + 5
    gapvalue = open / 100 * candle_length
    gapp = high - low > gapvalue
    gapp2 = high - low > gapvalue
    bull = open < close and high - low > 2 * gapvalue and (close > (high + open) / 2)
    bear = open > close and high - low > 2 * gapvalue and (close < (low + open) / 2)
    rev1 = rs > 68 and open > close and (open > gaps) and (high - low > gapvalue + 0.5) and (low != close)
    rev1a = rs > 90 and open < close and (close > gaps) and (high != close) and (open != low)
    sellrev = rev1 or rev1a
    rev2 = rs < 50 and open < close and (open < gapb) and (open == low)
    rev3 = rs < 30 and open > close and (high > gapb) and (open != high) and (barstate.isconfirmed != bear)
    rev4 = rs < 85 and close == high and (high - low > gapvalue) and (open < close)
    hlrev_s = ta.crossunder(rs, hl)
    llrev_b = ta.crossover(rs, ll) and open < close
    cross_1 = ta.cross(close[1], sma1)
    buycall = open < close and open > sma1 and cross_1 and (close > sma1)
    sellcall = ta.cross(close, sma1) and open > close
    BUY = ta.crossover(close[1], sma1) and close[1] > open[1] and (high > high[1]) and (close > open)
    SELL = ta.crossunder(low[1], sma1) and close[1] < open[1] and (low < low[1]) and (close < open)
    plotshape(SELL, title='SELL', style=shape.labeldown, color=color.new(color.red, 30), text='S', textcolor=color.new(color.black, 30))
    plotshape(BUY, title='BUY', style=shape.labelup, color=color.new(color.aqua, 30), text='B', textcolor=color.new(color.black, 30), location=location.belowbar)
    plotshape(hlrev_s, title='Reversal1', style=shape.labeldown, color=color.new(color.yellow, 20), text='!', textcolor=color.new(color.black, 20))
    plotshape(llrev_b, title='Reversal2', style=shape.labelup, color=color.new(color.yellow, 20), text='!', textcolor=color.new(color.black, 20), location=location.belowbar)
    barcolor(color.new(color.green, 0) if BUY else color.new(color.maroon, 30) if SELL else color.new(color.yellow, 0) if hlrev_s or llrev_b else na)
    plot(sma1, title='SMA', color=mycolor, linewidth=1)
    alertcondition(hlrev_s or llrev_b, title='Both Reversal Signal', message='Reversal Alert')
    alertcondition(SELL or BUY, title='Buy & Sell Signal Both', message='Buy/Sell Alert')
    alertcondition(BUY, title='Only Buy Signal', message='Buy Alert')
    alertcondition(SELL, title='Only Sell Signal', message='Sell Alert')
    alertcondition(hlrev_s, title='Reversal from Top', message='Down Reversal Alert')
    alertcondition(llrev_b, title='Reversal from Down', message='Up Reversal Alert')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
