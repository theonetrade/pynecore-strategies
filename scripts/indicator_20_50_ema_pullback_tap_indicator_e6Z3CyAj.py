"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barmerge, close, color, display, fill, high,
    input, location, low, na, plot, plotshape, request, script, shape, size, syminfo, ta,
    timeframe
)
from pynecore.types import Persistent

grpEMA: str = "EMA Settings"
grpSetup: str = "Setup Rules"
grpST: str = "Supertrend Filter"


@script.indicator("20/50 EMA Pullback + MTF Supertrend", overlay=True, max_labels_count=500)
def main(
    emaTimeframe=input.timeframe("", "EMA Timeframe", group=grpEMA, tooltip="Timeframe used to calculate the 20/50 EMAs. Leave blank to use the current chart timeframe."),
    fastLength=input.int(20, "Fast EMA", minval=1, group=grpEMA),
    slowLength=input.int(50, "Slow EMA", minval=1, group=grpEMA),
    setupExpiry=input.int(30, "Setup Expiry (Candles)", minval=1, group=grpSetup, tooltip="Number of chart candles allowed for price to touch the 20 EMA after the crossover."),
    showSetupLabels=input.bool(True, "Show Setup Labels", group=grpSetup),
    showExpiry=input.bool(True, "Show Expiry Labels", group=grpSetup),
    showEMAs=input.bool(True, "Show 20/50 EMAs", group=grpSetup),
    stTimeframe=input.timeframe("15", "Supertrend Timeframe", group=grpST, tooltip="Timeframe used to calculate the Supertrend. It is projected onto the current chart."),
    stFactor=input.float(3.0, "Supertrend Factor", minval=0.1, step=0.1, group=grpST),
    stATRPeriod=input.int(10, "Supertrend ATR Period", minval=1, group=grpST),
    showSupertrend=input.bool(True, "Show Supertrend", group=grpST),
    showSTShading=input.bool(True, "Show Supertrend Shading", group=grpST),
    stShadeTransparency=input.int(90, "Shading Transparency", minval=0, maxval=100, group=grpST)
):
    ema20 = request.security(syminfo.tickerid, timeframe.period if emaTimeframe == '' else emaTimeframe, ta.ema(close, fastLength), lookahead=barmerge.lookahead_off)

    ema50 = request.security(syminfo.tickerid, timeframe.period if emaTimeframe == '' else emaTimeframe, ta.ema(close, slowLength), lookahead=barmerge.lookahead_off)

    bullCross = ta.crossover(ema20, ema50)
    bearCross = ta.crossunder(ema20, ema50)

    supertrend, direction = request.security(syminfo.tickerid, stTimeframe, ta.supertrend(stFactor, stATRPeriod), lookahead=barmerge.lookahead_off)

    supertrendBullish = direction < 0
    supertrendBearish = direction > 0

    setupState: Persistent[int] = 0
    setupBar: Persistent[int] = na(int)

    priceEstablishedAbove: Persistent[bool] = False
    priceEstablishedBelow: Persistent[bool] = False

    if bullCross:
        setupState = 1
        setupBar = bar_index
        priceEstablishedAbove = False
        priceEstablishedBelow = False

    if bearCross:
        setupState = -1
        setupBar = bar_index
        priceEstablishedAbove = False
        priceEstablishedBelow = False

    if setupState == 1 and bar_index > setupBar and (close > ema20):
        priceEstablishedAbove = True

    if setupState == -1 and bar_index > setupBar and (close < ema20):
        priceEstablishedBelow = True

    setupAge = bar_index - setupBar if setupState != 0 and (not na(setupBar)) else na

    bullExpired = setupState == 1 and setupAge >= setupExpiry

    bearExpired = setupState == -1 and setupAge >= setupExpiry

    if bullExpired:
        setupState = 0
        setupBar = na
        priceEstablishedAbove = False

    if bearExpired:
        setupState = 0
        setupBar = na
        priceEstablishedBelow = False

    longTap = setupState == 1 and priceEstablishedAbove and (bar_index > setupBar) and (low <= ema20)

    shortTap = setupState == -1 and priceEstablishedBelow and (bar_index > setupBar) and (high >= ema20)

    longSignal = longTap and supertrendBullish

    shortSignal = shortTap and supertrendBearish

    if longSignal:
        setupState = 0
        setupBar = na
        priceEstablishedAbove = False

    if shortSignal:
        setupState = 0
        setupBar = na
        priceEstablishedBelow = False

    plot(ema20 if showEMAs else na, title='20 EMA', color=color.orange, linewidth=2)

    plot(ema50 if showEMAs else na, title='50 EMA', color=color.blue, linewidth=2)

    stBullPlot = supertrend if showSupertrend and supertrendBullish else na

    stBearPlot = supertrend if showSupertrend and supertrendBearish else na

    plot(stBullPlot, title='Bullish Supertrend', color=color.green, linewidth=2, style=plot.style_linebr)

    plot(stBearPlot, title='Bearish Supertrend', color=color.red, linewidth=2, style=plot.style_linebr)

    bullPriceLowPlot = plot(low if showSTShading and supertrendBullish else na, title='Bullish Candle Boundary', display=display.none)

    bullSTFillPlot = plot(supertrend if showSTShading and supertrendBullish else na, title='Bullish Supertrend Fill Boundary', display=display.none)

    fill(bullPriceLowPlot, bullSTFillPlot, color=color.new(color.green, stShadeTransparency), title='Bullish Supertrend Shading')

    bearPriceHighPlot = plot(high if showSTShading and supertrendBearish else na, title='Bearish Candle Boundary', display=display.none)

    bearSTFillPlot = plot(supertrend if showSTShading and supertrendBearish else na, title='Bearish Supertrend Fill Boundary', display=display.none)

    fill(bearPriceHighPlot, bearSTFillPlot, color=color.new(color.red, stShadeTransparency), title='Bearish Supertrend Shading')

    plotshape(showSetupLabels and bullCross, title='Bullish Cross', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, text='20/50\nARMED', size=size.small)

    plotshape(showSetupLabels and bearCross, title='Bearish Cross', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, text='20/50\nARMED', size=size.small)

    plotshape(longSignal, title='BUY', style=shape.labelup, location=location.belowbar, color=color.lime, textcolor=color.white, text='BUY', size=size.normal)

    plotshape(shortSignal, title='SELL', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, text='SELL', size=size.normal)

    plotshape(showExpiry and bullExpired, title='Bullish Setup Expired', style=shape.xcross, location=location.abovebar, color=color.gray, text='EXPIRED', size=size.tiny)

    plotshape(showExpiry and bearExpired, title='Bearish Setup Expired', style=shape.xcross, location=location.belowbar, color=color.gray, text='EXPIRED', size=size.tiny)

    alertcondition(bullCross, title='20/50 Bullish Cross', message='20 EMA crossed ABOVE 50 EMA — bullish setup armed. Waiting for 20 EMA pullback.')

    alertcondition(bearCross, title='20/50 Bearish Cross', message='20 EMA crossed BELOW 50 EMA — bearish setup armed. Waiting for 20 EMA pullback.')

    alertcondition(longSignal, title='20/50 BUY + MTF Supertrend Bullish', message='BUY — 20/50 EMA pullback confirmed with bullish Multi-Timeframe Supertrend.')

    alertcondition(shortSignal, title='20/50 SELL + MTF Supertrend Bearish', message='SELL — 20/50 EMA pullback confirmed with bearish Multi-Timeframe Supertrend.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)