"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barstate, close, color, high, input,
    label, line, location, low, math, na, plot, plotchar, script, size, ta
)
from pynecore.types import Persistent


@script.indicator("Market Structure Confluence [AlgoAlpha]", shorttitle="AlgoAlpha - Market Structure", overlay=True, max_lines_count=500, max_labels_count=500, max_bars_back=5000)
def main(
    swingSize=input.int(10, "Time-Horizon", minval=2, tooltip="Look-back bars for pivot detection", group="Market Structure"),
    bosConfType=input.string("Candle Close", "BOS Confirmation", options=("Candle Close", "Wicks"), tooltip="Close vs. wick confirmation", group="Market Structure"),
    bosStyleIn=input.string("Solid", "BOS/CHoCH Line Style", options=("Solid", "Dashed", "Dotted"), group="Market Structure"),
    showCHoCH=input.bool(True, "Show CHoCH", group="Market Structure"),
    showSwing=input.bool(True, "Show Swing Labels", group="Market Structure"),
    basisLength=input.int(100, "Basis Length", minval=1, tooltip="Length for the basis calculation (WMA)", group="Band Settings"),
    atrLength=input.int(14, "ATR Length", minval=1, tooltip="Length for the volatility (ATR) calculation", group="Band Settings"),
    atrSmooth=input.int(21, "ATR Smoothing", minval=1, tooltip="Length for smoothing the volatility", group="Band Settings"),
    volMult=input.float(2.0, "Volatility Multiplier", minval=0.1, step=0.1, tooltip="Multiplier for the bands", group="Band Settings"),
    colBull=input.color(color.new('#00FFBB'), "Bull   Color", inline="msc", group="Appearance"),
    colBear=input.color(color.new('#FF1100'), "Bear   Color", inline="msc", group="Appearance"),
    waitClose=input.bool(True, "Wait for Bar Close (alerts)", group="⚠️ Alerts")
):
    bosWidth: int = 1
    colBull50 = color.new(colBull, 50)
    colBear50 = color.new(colBear, 50)
    colClear = color.rgb(0, 0, 0, 100)
    barConfirmed = not waitClose or barstate.isconfirmed

    def lineStyle(s: str):
        return line.style_solid if s == 'Solid' else line.style_dashed if s == 'Dashed' else line.style_dotted

    prevHigh: Persistent[float] = na(float)
    prevLow: Persistent[float] = na(float)
    prevHighIdx: Persistent[int] = na(int)
    prevLowIdx: Persistent[int] = na(int)
    highActive: Persistent[bool] = False
    lowActive: Persistent[bool] = False
    prevBreakDir: Persistent[int] = 0
    lastBreakDir: Persistent[int] = 0
    enMS: bool = True

    pivHi = ta.pivothigh(high, swingSize, swingSize)
    pivLo = ta.pivotlow(low, swingSize, swingSize)

    hh: bool = False
    lh: bool = False
    hl: bool = False
    ll: bool = False

    if enMS:
        if not na(pivHi):
            hh = na(prevHigh) or pivHi >= prevHigh
            lh = not hh
            prevHigh = pivHi
            prevHighIdx = bar_index - swingSize
            highActive = True
        if not na(pivLo):
            hl = na(prevLow) or pivLo >= prevLow
            ll = not hl
            prevLow = pivLo
            prevLowIdx = bar_index - swingSize
            lowActive = True

    highSrc = close if bosConfType == 'Candle Close' else high
    lowSrc = close if bosConfType == 'Candle Close' else low

    highBroken: bool = False
    lowBroken: bool = False
    if enMS:
        if highActive and (not na(prevHigh)) and (highSrc > prevHigh):
            highBroken = True
            highActive = False
        if lowActive and (not na(prevLow)) and (lowSrc < prevLow):
            lowBroken = True
            lowActive = False

    volatility = ta.atr(atrLength)
    svol = ta.sma(volatility, atrSmooth)

    basis = ta.wma(close, basisLength)
    upper = basis + volMult * svol
    lower = basis - volMult * svol

    plot(lower if prevBreakDir == 1 else na, color=colBull, title='Lower Band', style=plot.style_linebr, linewidth=3)
    plot(upper if prevBreakDir == -1 else na, color=colBear, title='Upper Band', style=plot.style_linebr, linewidth=3)

    bullishArrow = prevBreakDir == 1 and low < lower and (high > lower)
    bearishArrow = prevBreakDir == -1 and low < upper and (high > upper)

    arrowOffset = volatility * 1

    plotchar(lower - arrowOffset if bullishArrow else na, 'Bullish Signal', '▲', location.absolute, colBull, size=size.tiny)
    plotchar(upper + arrowOffset if bearishArrow else na, 'Bearish Signal', '▼', location.absolute, colBear, size=size.tiny)

    if enMS and showSwing:
        if hh:
            label.new(bar_index - swingSize, pivHi, 'HH', style=label.style_label_down, textcolor=colBull50, color=colClear)
        if lh:
            label.new(bar_index - swingSize, pivHi, 'LH', style=label.style_label_down, textcolor=colBear50, color=colClear)
        if hl:
            label.new(bar_index - swingSize, pivLo, 'HL', style=label.style_label_up, textcolor=colBull50, color=colClear)
        if ll:
            label.new(bar_index - swingSize, pivLo, 'LL', style=label.style_label_up, textcolor=colBear50, color=colClear)

    bullishChange: bool = False
    bearishChange: bool = False

    if enMS and highBroken:
        line.new(prevHighIdx, prevHigh, bar_index, prevHigh, color=colBull, style=lineStyle(bosStyleIn), width=bosWidth)
        mid = math.floor(bar_index - (bar_index - prevHighIdx) / 2)
        label.new(mid, prevHigh, 'CHoCH' if prevBreakDir == -1 and showCHoCH else 'BOS', color=colClear, textcolor=colBull, size=size.tiny)
        lastBreakDir = prevBreakDir
        prevBreakDir = 1
        bullishChange = lastBreakDir == -1 or lastBreakDir == 0

    if enMS and lowBroken:
        line.new(prevLowIdx, prevLow, bar_index, prevLow, color=colBear, style=lineStyle(bosStyleIn), width=bosWidth)
        mid = math.floor(bar_index - (bar_index - prevLowIdx) / 2)
        label.new(mid, prevLow, 'CHoCH' if prevBreakDir == 1 and showCHoCH else 'BOS', style=label.style_label_up, color=colClear, textcolor=colBear, size=size.tiny)
        lastBreakDir = prevBreakDir
        prevBreakDir = -1
        bearishChange = lastBreakDir == 1 or lastBreakDir == 0

    plotchar(lower if bullishChange else na, 'Trend Change Bullish', '◉', location.absolute, colBull, size=size.tiny)
    plotchar(upper if bearishChange else na, 'Trend Change Bearish', '◉', location.absolute, colBear, size=size.tiny)

    barcolor((color.new(colBear, 30) if prevBreakDir == -1 else color.new(colBull, 30)) if enMS else na)

    alertcondition(highBroken and prevBreakDir == -1 and barConfirmed, 'Bullish CHoCH')
    alertcondition(highBroken and prevBreakDir != -1 and barConfirmed, 'Bullish BOS')
    alertcondition(lowBroken and prevBreakDir == 1 and barConfirmed, 'Bearish CHoCH')
    alertcondition(lowBroken and prevBreakDir != 1 and barConfirmed, 'Bearish BOS')
    alertcondition(hh and barConfirmed, 'HH Detected')
    alertcondition(lh and barConfirmed, 'LH Detected')
    alertcondition(hl and barConfirmed, 'HL Detected')
    alertcondition(ll and barConfirmed, 'LL Detected')
    alertcondition(bullishArrow and barConfirmed, 'Bullish Arrow Signal', 'Bullish Rejection Signal')
    alertcondition(bearishArrow and barConfirmed, 'Bearish Arrow Signal', 'Bearish Rejection Signal')
    alertcondition(bullishChange and barConfirmed, 'Bullish Trend Change', 'Trend changed to bullish')
    alertcondition(bearishChange and barConfirmed, 'Bearish Trend Change', 'Trend changed to bearish')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
