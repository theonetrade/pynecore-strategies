"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, chart, close, color, display, fill, high, hlc3,
    input, location, low, math, na, nz, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series

grp1: str = "Indicator Settings"
grp2: str = "Visual Options"


@script.indicator("Fibonacci Entry Bands [AlgoAlpha]", shorttitle="AlgoAlpha - Entry Bands", overlay=True, max_lines_count=500)
def main(
    tpAggressiveness=input.string("low", "TP Aggressiveness", options=("low", "medium", "high"), group=grp1, tooltip="Controls how aggressive the Take Profit (TP) trigger is. Low = slower exits, High = faster exits.", display=display.data_window),
    src: Series[float] = input.source(hlc3, "Source", group=grp1, tooltip="Price source used for band calculations", display=display.data_window),
    len=input.int(21, "Length", group=grp1, tooltip="Length for the basis calculation", display=display.data_window),
    atrLen=input.int(14, "ATR Length", group=grp1, tooltip="Length for ATR or Stdev volatility basis", display=display.data_window),
    useATR=input.bool(True, "Use ATR", group=grp1, tooltip="Toggle between ATR or standard deviation for band width", display=display.data_window),
    showRej=input.bool(True, "Show Take Profit Crosses", group=grp2, display=display.data_window),
    showBounce=input.bool(True, "Show Basis Bounce Arrows", group=grp2, display=display.data_window),
    colorbar=input.bool(True, "Custom Bar Color", group=grp2, display=display.data_window),
    green=input.color(color.new('#00FFBB'), "Bullish Color", group=grp2, display=display.data_window),
    red=input.color(color.new('#FF1100'), "Bearish Color", group=grp2, display=display.data_window),
    gray=input.color(color.gray, "Basis Color", group=grp2, display=display.data_window)
):
    basis: Series = ta.ema(ta.ema(src, len), len)
    vol = ta.atr(atrLen) if useATR else ta.stdev(src, len)

    mult1: float = 0.618
    mult2: float = 1.0
    mult3: float = 1.618
    mult4: float = 2.618

    trend: PersistentSeries[int] = 0
    trend = 1 if basis > basis[1] else -1 if basis < basis[1] else nz(trend[1])

    upper1 = basis + vol * mult1
    upper2 = basis + vol * mult2
    upper3 = basis + vol * mult3
    upper4 = basis + vol * mult4
    lower1 = basis - vol * mult1
    lower2 = basis - vol * mult2
    lower3 = basis - vol * mult3
    lower4 = basis - vol * mult4

    plot(basis, title='Basis', color=gray, linewidth=1)

    upper1_plot = plot(upper1 if trend == -1 else na, title='Upper 0.618', color=color.new(red, 60), style=plot.style_linebr)
    upper4_plot = plot(upper4 if trend == -1 else na, title='Upper 2.618', color=color.new(red, 30), style=plot.style_linebr)
    lower1_plot = plot(lower1 if trend == 1 else na, title='Lower 0.618', color=color.new(green, 60), style=plot.style_linebr)
    lower4_plot = plot(lower4 if trend == 1 else na, title='Lower 2.618', color=color.new(green, 30), style=plot.style_linebr)

    plot(upper2 if trend == -1 else na, title='Upper 1.0', color=color.new(red, 50), style=plot.style_linebr)
    plot(upper3 if trend == -1 else na, title='Upper 1.618', color=color.new(red, 40), style=plot.style_linebr)
    plot(lower2 if trend == 1 else na, title='Lower 1.0', color=color.new(green, 50), style=plot.style_linebr)
    plot(lower3 if trend == 1 else na, title='Lower 1.618', color=color.new(green, 40), style=plot.style_linebr)

    fill(upper1_plot, upper4_plot, upper1 if trend == -1 else na, upper4 if trend == -1 else na, color.new(chart.bg_color, 90), color.new(red, 70), title='Downtrend Band Fill')

    fill(lower1_plot, lower4_plot, lower1 if trend == 1 else na, lower4 if trend == 1 else na, color.new(chart.bg_color, 90), color.new(green, 70), title='Uptrend Band Fill')

    normDist = math.abs(close - basis) / (vol * mult4) if trend == -1 else math.abs(close - basis) / (vol * mult4) if trend == 1 else 0
    normDist = math.min(normDist, 1)

    alpha = math.min(math.round(normDist * 100), 70)

    avg_oc = math.avg(open, close)

    barCol = NA(Color)
    if trend == 1:
        barCol = gray if avg_oc < basis else color.new(green, alpha)
    elif trend == -1:
        barCol = gray if avg_oc > basis else color.new(red, alpha)
    else:
        barCol = na

    barcolor(barCol if colorbar else na)

    longSignal = ta.crossover(basis, basis[1])
    shortSignal = ta.crossunder(basis, basis[1])
    plotshape(lower4 if longSignal else na, title='Long Entry', location=location.absolute, style=shape.labelup, color=green, text='▲', textcolor=color.white)
    plotshape(upper4 if shortSignal else na, title='Short Entry', location=location.absolute, style=shape.labeldown, color=red, text='▼', textcolor=color.white)

    tpLongBand: Persistent[float] = na(float)
    tpShortBand: Persistent[float] = na(float)
    __switch__ = tpAggressiveness
    if __switch__ == "low":
        tpLongBand = lower4
        tpShortBand = upper4
    elif __switch__ == "medium":
        tpLongBand = lower2
        tpShortBand = upper2
    elif __switch__ == "high":
        tpLongBand = lower1
        tpShortBand = upper1

    con1 = ta.crossunder(close, tpLongBand)
    con2 = ta.crossover(close, tpShortBand)

    rejectionLong = showRej and con1 and (trend == -1)
    rejectionShort = showRej and con2 and (trend == 1)
    plotshape(rejectionLong, title='Rejection Long', location=location.belowbar, color=red, style=shape.xcross, size=size.tiny)
    plotshape(rejectionShort, title='Rejection Short', location=location.abovebar, color=green, style=shape.xcross, size=size.tiny)

    longBounce = showBounce and trend == 1 and (low < basis) and (close > basis) and (not longSignal)
    shortBounce = showBounce and trend == -1 and (high > basis) and (close < basis) and (not shortSignal)

    plotshape(longBounce, title='Long Bounce', location=location.belowbar, style=shape.triangleup, color=green, size=size.tiny)
    plotshape(shortBounce, title='Short Bounce', location=location.abovebar, style=shape.triangledown, color=red, size=size.tiny)

    alertcondition(longSignal, title='Long Entry')
    alertcondition(shortSignal, title='Short Entry')
    alertcondition(rejectionLong, title='Rejection Long (TP for Short)')
    alertcondition(rejectionShort, title='Rejection Short (TP for Long)')
    alertcondition(longBounce, title='Long Bounce')
    alertcondition(shortBounce, title='Short Bounce')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
