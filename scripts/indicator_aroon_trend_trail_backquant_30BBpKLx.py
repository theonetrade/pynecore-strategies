"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, close, color, display, fill, high, hl2, input, low, math,
    na, open, plot, plotcandle, script, ta
)
from pynecore.types import Color, PersistentSeries

calc: str = "Aroon Calculation"
rail: str = "Trend Rail Settings"
ui: str = "Plotting and Coloring"
GREEN: Color = color.new('#00FF00')
RED: Color = color.new('#FF0000')


@script.indicator("Aroon Trend Trail [BackQuant]", shorttitle="Aroon Trail [BackQuant]", overlay=True)
def main(
    aroonLen=input.int(25, "Aroon Length", minval=2, group=calc),
    flipThreshold=input.float(0.15, "Bias Threshold", minval=0.0, maxval=1.0, step=0.01, group=calc, tooltip="Minimum Aroon bias required to establish the opposite trend."),
    atrLen=input.int(14, "ATR Length", minval=1, group=rail, inline="ATR"),
    atrFactor=input.float(1.8, "Base Width", minval=0.1, step=0.05, group=rail, inline="ATR"),
    strongWidth=input.float(0.65, "Strong Trend Width", minval=0.1, maxval=3.0, step=0.05, group=rail, inline="WIDTH"),
    weakWidth=input.float(1.25, "Weak Trend Width", minval=0.1, maxval=3.0, step=0.05, group=rail, inline="WIDTH"),
    breakOnFlip=input.bool(True, "Break Rail On Flips", group=rail),
    longCol=input.color(GREEN, "Bullish", group=ui, inline="COL"),
    shortCol=input.color(RED, "Bearish", group=ui, inline="COL"),
    lineW=input.int(3, "Line Width", minval=1, maxval=6, group=ui),
    showFill=input.bool(True, "Gradient Fill", group=ui),
    showGlow=input.bool(True, "Rail Glow", group=ui),
    showAroon=input.bool(False, "Show Aroon Values", group=ui),
    paintCandles=input.bool(True, "Color Candles", group=ui)
):
    sinceHigh: int = math.abs(ta.highestbars(high, aroonLen))
    sinceLow: int = math.abs(ta.lowestbars(low, aroonLen))

    aroonUp: float = 100.0 * (aroonLen - sinceHigh) / aroonLen
    aroonDown: float = 100.0 * (aroonLen - sinceLow) / aroonLen

    aroonBias: float = (aroonUp - aroonDown) / 100.0
    aroonStrength: float = math.min(math.abs(aroonBias), 1.0)

    trend: PersistentSeries[int] = 0

    if trend == 0:
        trend = 1 if aroonBias >= 0.0 else -1
    elif trend != 1 and aroonBias > flipThreshold:
        trend = 1
    elif trend != -1 and aroonBias < -flipThreshold:
        trend = -1

    bullFlip: bool = trend == 1 and trend[1] == -1
    bearFlip: bool = trend == -1 and trend[1] == 1
    trendFlip: bool = bullFlip or bearFlip

    trendCol: Color = longCol if trend == 1 else shortCol

    atr: float = ta.atr(atrLen)
    widthScale: float = weakWidth + (strongWidth - weakWidth) * aroonStrength
    railWidth: float = atr * atrFactor * widthScale

    rawLower: float = hl2 - railWidth
    rawUpper: float = hl2 + railWidth

    lowerRail: PersistentSeries[float] = na(float)
    upperRail: PersistentSeries[float] = na(float)

    if na(lowerRail):
        lowerRail = rawLower
        upperRail = rawUpper
    else:
        if trend == 1:
            lowerRail = rawLower if bullFlip else math.max(lowerRail[1], rawLower)
        else:
            lowerRail = rawLower

        if trend == -1:
            upperRail = rawUpper if bearFlip else math.min(upperRail[1], rawUpper)
        else:
            upperRail = rawUpper

    activeRail: float = lowerRail if trend == 1 else upperRail
    plottedRail: float = na if breakOnFlip and trendFlip else activeRail

    railDistance: float = math.abs(close - activeRail)
    distanceStrength: float = math.min(railDistance / railWidth, 1.0) if railWidth > 0.0 else 0.0
    trendStrength: float = math.min(aroonStrength * 0.75 + distanceStrength * 0.25, 1.0)

    strengthBoost: int = cast_int(math.round(trendStrength * 14.0))

    fillReady: bool = showFill and (not na(plottedRail))
    priceAbove: bool = close >= activeRail

    grad1: float = activeRail + (close - activeRail) * 0.15
    grad2: float = activeRail + (close - activeRail) * 0.35
    grad3: float = activeRail + (close - activeRail) * 0.6
    grad4: float = activeRail + (close - activeRail) * 0.82

    pRail = plot(plottedRail, 'Aroon Trend Rail', trendCol, lineW, plot.style_linebr)
    pPrice = plot(close if fillReady else na, 'Price Ref', display=display.none, editable=False)
    pGrad1 = plot(grad1 if fillReady else na, 'Gradient Ref 1', display=display.none, editable=False)
    pGrad2 = plot(grad2 if fillReady else na, 'Gradient Ref 2', display=display.none, editable=False)
    pGrad3 = plot(grad3 if fillReady else na, 'Gradient Ref 3', display=display.none, editable=False)
    pGrad4 = plot(grad4 if fillReady else na, 'Gradient Ref 4', display=display.none, editable=False)

    fill(pRail, pGrad1, grad1 if priceAbove else activeRail, activeRail if priceAbove else grad1, color.new(trendCol, 82) if fillReady else na, color.new(trendCol, math.max(28, 55 - strengthBoost)) if fillReady else na, title='Gradient Layer 1')
    fill(pGrad1, pGrad2, grad2 if priceAbove else grad1, grad1 if priceAbove else grad2, color.new(trendCol, 90) if fillReady else na, color.new(trendCol, 68) if fillReady else na, title='Gradient Layer 2')
    fill(pGrad2, pGrad3, grad3 if priceAbove else grad2, grad2 if priceAbove else grad3, color.new(trendCol, 94) if fillReady else na, color.new(trendCol, 79) if fillReady else na, title='Gradient Layer 3')
    fill(pGrad3, pGrad4, grad4 if priceAbove else grad3, grad3 if priceAbove else grad4, color.new(trendCol, 97) if fillReady else na, color.new(trendCol, 88) if fillReady else na, title='Gradient Layer 4')
    fill(pGrad4, pPrice, close if priceAbove else grad4, grad4 if priceAbove else close, color.new(trendCol, 99) if fillReady else na, color.new(trendCol, 95) if fillReady else na, title='Gradient Layer 5')

    glow: float = atr * (0.045 + trendStrength * 0.025)
    outerGlow: float = glow * 2.3

    pGlowOuterLower = plot(activeRail - outerGlow if showGlow else na, 'Outer Glow Lower', display=display.none, editable=False)
    pGlowOuterUpper = plot(activeRail + outerGlow if showGlow else na, 'Outer Glow Upper', display=display.none, editable=False)
    pGlowLower = plot(activeRail - glow if showGlow else na, 'Glow Lower', display=display.none, editable=False)
    pGlowUpper = plot(activeRail + glow if showGlow else na, 'Glow Upper', display=display.none, editable=False)

    fill(pGlowOuterLower, pGlowOuterUpper, color.new(trendCol, 95) if showGlow else na, title='Outer Rail Glow')
    fill(pGlowLower, pGlowUpper, color.new(trendCol, math.max(60, 84 - strengthBoost)) if showGlow else na, title='Inner Rail Glow')

    plotcandle(open, high, low, close, 'Trend Candles', trendCol, trendCol, True, bordercolor=trendCol, display=display.all if paintCandles else display.none)

    plot(aroonUp, 'Aroon Up', display=display.data_window)
    plot(aroonDown, 'Aroon Down', display=display.data_window)
    plot(aroonBias, 'Aroon Bias', display=display.data_window)
    plot(aroonStrength * 100.0, 'Aroon Strength', display=display.data_window)
    plot(railWidth, 'Active Rail Width', display=display.data_window)

    plot(aroonUp if showAroon else na, 'Aroon Up Diagnostic', display=display.data_window)
    plot(aroonDown if showAroon else na, 'Aroon Down Diagnostic', display=display.data_window)

    alertcondition(bullFlip, 'Aroon Rail Bullish', 'Aroon Trend Rail turned bullish on {{ticker}}')
    alertcondition(bearFlip, 'Aroon Rail Bearish', 'Aroon Trend Rail turned bearish on {{ticker}}')
    alertcondition(trendFlip, 'Aroon Rail Flip', 'Aroon Trend Rail changed direction on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)