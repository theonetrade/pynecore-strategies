"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barmerge, close, color, fill, input,
    label, location, na, plot, plotshape, request, script, shape, string, syminfo, ta, yloc
)
from pynecore.types import Series


@script.indicator('CDC ActionZone V3 2020', overlay=True, precision=6, na_bool=True)
def main(
    xsrc: Series[float] = input.source(title='Source Data', defval=close),
    xprd1=input.int(title='Fast EMA period', defval=12),
    xprd2=input.int(title='Slow EMA period', defval=26),
    xsmooth=input.int(title='Smoothing period (1 = no smoothing)', defval=1),
    fillSW=input.bool(title='Paint Bar Colors', defval=True),
    fastSW=input.bool(title='Show fast moving average line', defval=True),
    slowSW=input.bool(title='Show slow moving average line', defval=True),
    labelSwitch=input.bool(title='Turn on assistive text', defval=True),
    plotSigsw=input.bool(title='Plot Buy/Sell Signals? ', defval=True),
    plotRibsw=input.bool(title='Plot Buy/Sell Ribbon', defval=False),
    plotRibbonPos=input.string(title='Ribbon Position', options=('Top', 'Bottom'), defval='Top'),
    xfixtf=input.bool(title='** Use Fixed time frame Mode (advanced) **', defval=False),
    xtf=input.timeframe(title='** Fix chart to which time frame ? **)', defval='D'),
    plotSig2sw=input.bool(title='Plot momentum based Buy/Sell Signals? ', defval=False),
    plotSig2lv=input.int(title='Set signal threshold (higher = stricter)', defval=1, minval=0, maxval=1)
):
    def f_secureSecurity(_symbol, _res, _src: Series):
        return request.security(_symbol, _res, _src[1], lookahead=barmerge.lookahead_on)

    xPrice = ta.ema(xsrc, xsmooth)
    FastMA = ta.ema(f_secureSecurity(syminfo.tickerid, xtf, ta.ema(xsrc, xprd1)), xsmooth) if xfixtf else ta.ema(xPrice, xprd1)
    SlowMA = ta.ema(f_secureSecurity(syminfo.tickerid, xtf, ta.ema(xsrc, xprd2)), xsmooth) if xfixtf else ta.ema(xPrice, xprd2)
    Bull = FastMA > SlowMA
    Bear = FastMA < SlowMA
    Green: Series = Bull and xPrice > FastMA
    Blue = Bear and xPrice > FastMA and (xPrice > SlowMA)
    LBlue = Bear and xPrice > FastMA and (xPrice < SlowMA)
    Red: Series = Bear and xPrice < FastMA
    Orange = Bull and xPrice < FastMA and (xPrice < SlowMA)
    Yellow = Bull and xPrice < FastMA and (xPrice > SlowMA)
    bColor = color.green if Green else color.blue if Blue else color.aqua if LBlue else color.red if Red else color.orange if Orange else color.yellow if Yellow else color.black
    barcolor(color=bColor if fillSW else na)
    FastL = plot(FastMA if fastSW else na, 'Fast EMA', color=color.new(color.red, 0), style=plot.style_stepline if xfixtf else plot.style_line)
    SlowL = plot(SlowMA if slowSW else na, 'Slow EMA', color=color.new(color.blue, 0), style=plot.style_stepline if xfixtf else plot.style_line)
    fillcolor = color.new(color.green, 90) if Bull else color.new(color.red, 90) if Bear else color.new(color.black, 90)
    fill(FastL, SlowL, fillcolor)
    buycond = Green and Green[1] == 0
    sellcond = Red and Red[1] == 0
    bullish: Series = ta.barssince(buycond) < ta.barssince(sellcond)
    bearish: Series = ta.barssince(sellcond) < ta.barssince(buycond)
    buy = bearish[1] and buycond
    sell = bullish[1] and sellcond
    bColor_BullBear = color.green if bullish else color.red if bearish else color.black
    plotshape(buy if plotSigsw else na, style=shape.circle, title='Buy Signal', location=location.belowbar, color=color.new(color.green, 0))
    plotshape(sell if plotSigsw else na, style=shape.circle, title='Sell Signal', location=location.abovebar, color=color.new(color.red, 0))
    plotshape((close if plotRibbonPos == 'Top' else na) if plotRibsw else na, style=shape.square, title='Buy/Sell Ribbon', location=location.top, color=bColor_BullBear)
    plotshape((close if plotRibbonPos == 'Bottom' else na) if plotRibsw else na, style=shape.square, title='Buy/Sell Ribbon', location=location.bottom, color=bColor_BullBear)
    labelstyle = label.style_label_down if close > SlowMA else label.style_label_up
    labelyloc = yloc.abovebar if close > SlowMA else yloc.belowbar
    labeltcolor = color.black if buy else color.white if sell else color.green if close > close[1] else color.red
    labelbgcolor = color.green if buy else color.red if sell else color.silver
    labeltext = 'BUY next bar\n' if buy else 'SELL next bar\n' if sell else ' '
    trendText = 'bullish' if bullish else 'bearish' if bearish else 'sideways'
    l1: Series = label.new(bar_index, na, text=labeltext + syminfo.ticker + ' ' + string.tostring(close) + ' ' + syminfo.currency + '\n currently in a ' + trendText + ' trend \n', color=labelbgcolor, textcolor=labeltcolor, yloc=labelyloc, style=labelstyle)
    label.delete(l1[1] if labelSwitch else l1)
    smoothK: int = 3
    smoothD: int = 3
    RSIlen: int = 14
    STOlen: int = 14
    SRsrc = close
    OSlevel: int = 30
    OBlevel: int = 70
    rsi1 = ta.rsi(SRsrc, RSIlen)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, STOlen), smoothK)
    d = ta.sma(k, smoothD)
    crossover_1 = ta.crossover(k, d)
    crossover_2 = ta.crossover(k, d)
    iff_1 = 1 if d > OSlevel and crossover_2 else 0
    iff_2 = 2 if d < OSlevel and crossover_1 else iff_1
    storsiBuySig = iff_2 if bullish else 0
    crossunder_1 = ta.crossunder(k, d)
    crossunder_2 = ta.crossunder(k, d)
    iff_3 = 1 if d < OBlevel and crossunder_2 else 0
    iff_4 = 2 if d > OBlevel and crossunder_1 else iff_3
    storsiSellSig = iff_4 if bearish else 0
    plotshape((storsiBuySig if storsiBuySig > plotSig2lv else na) if plotSig2sw else na, 'Buy more signals', style=shape.triangleup, location=location.belowbar, color=color.new(color.teal, 0))
    plotshape((storsiSellSig if storsiSellSig > plotSig2lv else na) if plotSig2sw else na, 'Sell more signals', style=shape.triangledown, location=location.abovebar, color=color.new(color.orange, 0))
    alertcondition(buy, title='*Buy Alert', message='Buy {{exchange}}:{{ticker}}')
    alertcondition(sell, title='*Sell Alert', message='Sell {{exchange}}:{{ticker}}')
    alertcondition(bullish, title='is Bullish')
    alertcondition(bearish, title='is Bearish')
    alertcondition(Green, title='is Green')
    alertcondition(Blue, title='is Blue (Strong Rally)')
    alertcondition(LBlue, title='is Light Blue (Rally)')
    alertcondition(Red, title='is Red')
    alertcondition(Orange, title='is Orange (Strong Dip)')
    alertcondition(Yellow, title='is Yellow (Dip)')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
