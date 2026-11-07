"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, location, na, plot, plotshape, script, shape, size,
    strategy, ta, time, timenow
)
from pynecore.types import Persistent, Series


@script.strategy(title='Super Guppy Strategy', shorttitle='Super Guppy Strat', overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type='percent', commission_value=0.0, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    useShorts=input(True, 'Test w/Shorts?'),
    useEarlySignals=input(True, 'Use Early Signals?'),
    show200Ema=input(False, 'Show 200 EMA?'),
    daysBackMax=input.int(defval=100000, title='Max Days Back to Test', minval=0),
    daysBackMin=input.int(defval=0, title='Min Days Back to Test', minval=0),
    len1=input.int(3, minval=1, title='Fast EMA 1'),
    len2=input.int(6, minval=1, title='Fast EMA 2'),
    len3=input.int(9, minval=1, title='Fast EMA 3'),
    len4=input.int(12, minval=1, title='Fast EMA 4'),
    len5=input.int(15, minval=1, title='Fast EMA 5'),
    len6=input.int(18, minval=1, title='Fast EMA 6'),
    len7=input.int(21, minval=1, title='Fast EMA 7'),
    len8=input.int(24, minval=1, title='Slow EMA 8'),
    len9=input.int(27, minval=1, title='Slow EMA 9'),
    len10=input.int(30, minval=1, title='Slow EMA 10'),
    len11=input.int(33, minval=1, title='Slow EMA 11'),
    len12=input.int(36, minval=1, title='Slow EMA 12'),
    len13=input.int(39, minval=1, title='Slow EMA 13'),
    len14=input.int(42, minval=1, title='Slow EMA 14'),
    len15=input.int(45, minval=1, title='Slow EMA 15'),
    len16=input.int(48, minval=1, title='Slow EMA 16'),
    len17=input.int(51, minval=1, title='Slow EMA 17'),
    len18=input.int(54, minval=1, title='Slow EMA 18'),
    len19=input.int(57, minval=1, title='Slow EMA 19'),
    len20=input.int(60, minval=1, title='Slow EMA 20'),
    len21=input.int(63, minval=1, title='Slow EMA 21'),
    len22=input.int(66, minval=1, title='Slow EMA 22'),
    len23=input.int(200, minval=1, title='EMA 200')
):
    msBackMax = 1000 * 60 * 60 * 24 * daysBackMax
    msBackMin = 1000 * 60 * 60 * 24 * daysBackMin
    src = close
    ema1 = ta.ema(src, len1)
    ema2 = ta.ema(src, len2)
    ema3 = ta.ema(src, len3)
    ema4 = ta.ema(src, len4)
    ema5 = ta.ema(src, len5)
    ema6 = ta.ema(src, len6)
    ema7 = ta.ema(src, len7)
    ema8 = ta.ema(src, len8)
    ema9 = ta.ema(src, len9)
    ema10 = ta.ema(src, len10)
    ema11 = ta.ema(src, len11)
    ema12 = ta.ema(src, len12)
    ema13 = ta.ema(src, len13)
    ema14 = ta.ema(src, len14)
    ema15 = ta.ema(src, len15)
    ema16 = ta.ema(src, len16)
    ema17 = ta.ema(src, len17)
    ema18 = ta.ema(src, len18)
    ema19 = ta.ema(src, len19)
    ema20 = ta.ema(src, len20)
    ema21 = ta.ema(src, len21)
    ema22 = ta.ema(src, len22)
    ema23 = ta.ema(src, len23)
    colfastL = ema1 > ema2 and ema2 > ema3 and (ema3 > ema4) and (ema4 > ema5) and (ema5 > ema6) and (ema6 > ema7)
    colfastS = ema1 < ema2 and ema2 < ema3 and (ema3 < ema4) and (ema4 < ema5) and (ema5 < ema6) and (ema6 < ema7)
    colslowL = ema8 > ema9 and ema9 > ema10 and (ema10 > ema11) and (ema11 > ema12) and (ema12 > ema13) and (ema13 > ema14) and (ema14 > ema15) and (ema15 > ema16) and (ema16 > ema17) and (ema17 > ema18) and (ema18 > ema19) and (ema19 > ema20) and (ema20 > ema21) and (ema21 > ema22)
    colslowS = ema8 < ema9 and ema9 < ema10 and (ema10 < ema11) and (ema11 < ema12) and (ema12 < ema13) and (ema13 < ema14) and (ema14 < ema15) and (ema15 < ema16) and (ema16 < ema17) and (ema17 < ema18) and (ema18 < ema19) and (ema19 < ema20) and (ema20 < ema21) and (ema21 < ema22)
    colFinal = color.aqua if colfastL and colslowL else color.orange if colfastS and colslowS else color.gray
    colFinal2: Series = color.lime if colslowL else color.red if colslowS else color.gray
    p1 = plot(ema1, linewidth=2, color=colFinal)
    plot(ema2, linewidth=1, color=colFinal)
    plot(ema3, linewidth=1, color=colFinal)
    plot(ema4, linewidth=1, color=colFinal)
    plot(ema5, linewidth=1, color=colFinal)
    plot(ema6, linewidth=1, color=colFinal)
    p2 = plot(ema7, linewidth=2, color=colFinal)
    p3 = plot(ema8, linewidth=1, color=colFinal2)
    plot(ema9, linewidth=1, color=colFinal2)
    plot(ema10, linewidth=1, color=colFinal2)
    plot(ema11, linewidth=1, color=colFinal2)
    plot(ema12, linewidth=1, color=colFinal2)
    plot(ema13, linewidth=1, color=colFinal2)
    plot(ema14, linewidth=1, color=colFinal2)
    plot(ema15, linewidth=1, color=colFinal2)
    plot(ema16, linewidth=1, color=colFinal2)
    plot(ema17, linewidth=1, color=colFinal2)
    plot(ema18, linewidth=1, color=colFinal2)
    plot(ema19, linewidth=1, color=colFinal2)
    plot(ema20, linewidth=1, color=colFinal2)
    plot(ema21, linewidth=1, color=colFinal2)
    plot(ema22, linewidth=2, color=colFinal2)
    p4 = plot(ema23 if show200Ema == True else na, linewidth=2)
    isLong: Persistent[bool] = False
    isShort: Persistent[bool] = False
    long = not isLong and (colFinal2 == color.lime and colFinal2[1] == color.gray or (colFinal2 == color.gray and colFinal2[1] == color.red))
    short = not isShort and (colFinal2 == color.gray and colFinal2[1] == color.lime or (colFinal2 == color.red and colFinal2[1] == color.gray))
    if long:
        isLong = True
        isShort = False
    if short:
        isLong = False
        isShort = True
    openLong = colFinal2 == color.lime and colFinal2[1] == color.gray
    closeLong = colFinal2 == color.gray and colFinal2[1] == color.lime
    openShort = colFinal2 == color.red and colFinal2[1] == color.gray
    closeShort = colFinal2 == color.gray and colFinal2[1] == color.red
    plotshape(openLong and (not useEarlySignals), title='open long', text='open long', style=shape.labelup, location=location.belowbar, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(closeLong and (not useEarlySignals), title='close long', text='close long', style=shape.labeldown, location=location.abovebar, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0))
    plotshape(openShort and useShorts and (not useEarlySignals), title='open short', text='open short', style=shape.labelup, location=location.abovebar, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(closeShort and useShorts and (not useEarlySignals), title='close short', text='close short', style=shape.labeldown, location=location.belowbar, size=size.tiny, color=color.new(color.black, 0), textcolor=color.new(color.white, 0))
    plotshape(long and useEarlySignals, title='long', text='long', style=shape.labelup, location=location.belowbar, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(short and useEarlySignals and useShorts, title='short', text='short', style=shape.labeldown, location=location.abovebar, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(short and useEarlySignals and (not useShorts), title='close long', text='close long', style=shape.labeldown, location=location.abovebar, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    isWithinTimeBounds = (msBackMax == 0 or time > timenow - msBackMax) and (msBackMin == 0 or time < timenow - msBackMin)
    if openLong and isWithinTimeBounds and (not useEarlySignals):
        strategy.entry('LONG', direction=strategy.long)
    if closeLong and isWithinTimeBounds and (not useEarlySignals):
        strategy.close('LONG')
    if openShort and useShorts and isWithinTimeBounds and (not useEarlySignals):
        strategy.entry('short', direction=strategy.short)
    if closeShort and useShorts and isWithinTimeBounds and (not useEarlySignals):
        strategy.close('short')
    if long and isWithinTimeBounds and useEarlySignals:
        strategy.entry('LONG', direction=strategy.long)
    if short and isWithinTimeBounds and useEarlySignals:
        strategy.close('LONG')
    if short and useShorts and isWithinTimeBounds and useEarlySignals:
        strategy.entry('short', direction=strategy.short)
    if long and useShorts and isWithinTimeBounds and (not useEarlySignals):
        strategy.close('short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)