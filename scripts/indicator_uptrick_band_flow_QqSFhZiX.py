"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, display, fill, format,
    high, input, label, location, low, math, na, open, plot, plotcandle, plotshape, position,
    script, shape, size, string, syminfo, ta, table
)
from pynecore.types import Color, Persistent, Series, Table

gTrend: str = "01. Trend Engine"
gOverlay: str = "02. Overlay"
gSignals: str = "03. Signal Anchor"
gTP: str = "04. ATR Take Profits"
gDisplay: str = "05. Display"


@script.indicator("Uptrick: Band Flow", shorttitle="Band Flow", overlay=True, max_labels_count=500)
def main(
    length=input.int(30, "Trend Length", minval=2, group=gTrend),
    smooth=input.int(4, "Trend Smoothing", minval=1, group=gTrend),
    atrLength=input.int(14, "Band ATR Length", minval=1, group=gTrend),
    upperMult=input.float(1.5, "Upper Band Multiplier", minval=0.1, step=0.05, group=gTrend),
    lowerMult=input.float(1.5, "Lower Band Multiplier", minval=0.1, step=0.05, group=gTrend),
    overlayMode=input.string("Bands", "Overlay Mode", options=("Center", "Trail", "Bands"), group=gOverlay),
    trailOuterATR=input.float(0.85, "Trail Outer Expansion", minval=0.1, step=0.05, group=gOverlay),
    trailSmooth=input.int(5, "Trail Smoothing", minval=1, group=gOverlay),
    signalAnchorMode=input.string("Bands", "Signal Anchor", options=("Bands", "ATR"), group=gSignals, tooltip="Bands anchors signals to the outer trend band. ATR anchors them beyond the candle high/low."),
    signalATRLength=input.int(14, "Signal ATR Length", minval=1, group=gSignals),
    signalATRMult=input.float(0.8, "Signal ATR Distance", minval=0.05, step=0.05, group=gSignals),
    showATRTP=input.bool(True, "Show ATR Take Profits", group=gTP),
    tp1Mult=input.float(1.0, "TP1 ATR", minval=0.1, step=0.25, group=gTP),
    tp2Mult=input.float(2.0, "TP2 ATR", minval=0.1, step=0.25, group=gTP),
    tp3Mult=input.float(3.0, "TP3 ATR", minval=0.1, step=0.25, group=gTP),
    tp4Mult=input.float(4.0, "TP4 ATR", minval=0.1, step=0.25, group=gTP),
    tp5Mult=input.float(5.0, "TP5 ATR", minval=0.1, step=0.25, group=gTP),
    showSignals=input.bool(True, "Show Signals", group=gDisplay),
    showCandles=input.bool(True, "Trend Candles", group=gDisplay),
    showTable=input.bool(True, "Dashboard", group=gDisplay)
):
    bullColor: Color = color.new('#00FFE5')
    bearColor: Color = color.new('#FF00B5')

    black: Color = color.new('#000000')
    white: Color = color.new('#FFFFFF')

    dimWhite = color.new(white, 45)

    baseWMA = ta.wma(close, length)

    basis = ta.ema(baseWMA, smooth) if smooth > 1 else baseWMA

    bandATR = ta.atr(atrLength)

    safeATR = math.max(bandATR, syminfo.mintick)

    upperBand: Series = basis + safeATR * upperMult

    lowerBand: Series = basis - safeATR * lowerMult

    trend: Persistent[int] = 0

    bullBreak = barstate.isconfirmed and close > upperBand and (close[1] <= upperBand[1])

    bearBreak = barstate.isconfirmed and close < lowerBand and (close[1] >= lowerBand[1])

    if bullBreak:
        trend = 1
    elif bearBreak:
        trend = -1

    if trend == 0:
        trend = 1 if close >= basis else -1

    bullish = trend == 1

    bearish = trend == -1

    trendColor = bullColor if bullish else bearColor

    smoothTrailBasis = ta.ema(basis, trailSmooth) if trailSmooth > 1 else basis

    smoothTrailATR = ta.ema(safeATR, trailSmooth) if trailSmooth > 1 else safeATR

    trailInner = basis - safeATR * lowerMult if bullish else basis + safeATR * upperMult

    trailOuter = smoothTrailBasis - smoothTrailATR * (lowerMult + trailOuterATR) if bullish else smoothTrailBasis + smoothTrailATR * (upperMult + trailOuterATR)

    signalATR = ta.atr(signalATRLength)

    safeSignalATR = math.max(signalATR, syminfo.mintick)

    bullBandAnchor = smoothTrailBasis - smoothTrailATR * (lowerMult + trailOuterATR)

    bearBandAnchor = smoothTrailBasis + smoothTrailATR * (upperMult + trailOuterATR)

    bullATRAnchor = low - safeSignalATR * signalATRMult

    bearATRAnchor = high + safeSignalATR * signalATRMult

    bullSignalAnchor = bullBandAnchor if signalAnchorMode == 'Bands' else bullATRAnchor

    bearSignalAnchor = bearBandAnchor if signalAnchorMode == 'Bands' else bearATRAnchor

    tradeSide: Persistent[int] = 0

    entryPrice: Persistent[float] = na(float)
    entryATR: Persistent[float] = na(float)

    newLong = bullBreak and tradeSide != 1

    newShort = bearBreak and tradeSide != -1

    if newLong:
        tradeSide = 1
        entryPrice = close
        entryATR = safeATR

    if newShort:
        tradeSide = -1
        entryPrice = close
        entryATR = safeATR

    direction = 1.0 if tradeSide == 1 else -1.0

    tp1 = entryPrice + entryATR * tp1Mult * direction if not na(entryPrice) else na

    tp2 = entryPrice + entryATR * tp2Mult * direction if not na(entryPrice) else na

    tp3 = entryPrice + entryATR * tp3Mult * direction if not na(entryPrice) else na

    tp4 = entryPrice + entryATR * tp4Mult * direction if not na(entryPrice) else na

    tp5 = entryPrice + entryATR * tp5Mult * direction if not na(entryPrice) else na

    tp1Hit: Persistent[bool] = False
    tp2Hit: Persistent[bool] = False
    tp3Hit: Persistent[bool] = False
    tp4Hit: Persistent[bool] = False
    tp5Hit: Persistent[bool] = False

    if newLong or newShort:
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        tp4Hit = False
        tp5Hit = False

    def f_targetHit(_level):
        return high >= _level if tradeSide == 1 else low <= _level

    newTP1 = showATRTP and (not tp1Hit) and (not na(tp1)) and f_targetHit(tp1)

    newTP2 = showATRTP and (not tp2Hit) and (not na(tp2)) and f_targetHit(tp2)

    newTP3 = showATRTP and (not tp3Hit) and (not na(tp3)) and f_targetHit(tp3)

    newTP4 = showATRTP and (not tp4Hit) and (not na(tp4)) and f_targetHit(tp4)

    newTP5 = showATRTP and (not tp5Hit) and (not na(tp5)) and f_targetHit(tp5)

    if newTP1:
        tp1Hit = True

    if newTP2:
        tp2Hit = True

    if newTP3:
        tp3Hit = True

    if newTP4:
        tp4Hit = True

    if newTP5:
        tp5Hit = True

    showCenter = overlayMode == 'Center'

    pCenter = plot(basis if showCenter else na, 'Center Line', color=trendColor, linewidth=3)

    pCenterPrice = plot(close if showCenter else na, 'Center Price', color=color.new(trendColor, 100), display=display.none)

    fill(pCenter, pCenterPrice, basis, close, color.new(trendColor, 58), color.new(trendColor, 95), title='Center Gradient')

    showTrail = overlayMode == 'Trail'

    pTrailInner = plot(trailInner if showTrail else na, 'Trail Inner', color=color.new(trendColor, 100), linewidth=1)

    pTrailOuter = plot(trailOuter if showTrail else na, 'Trail Outer', color=color.new(trendColor, 28), linewidth=2)

    trailTop = trailInner if bullish else trailOuter

    trailBottom = trailOuter if bullish else trailInner

    trailTopColor = color.new(trendColor, 100) if bullish else color.new(trendColor, 80)

    trailBottomColor = color.new(trendColor, 80) if bullish else color.new(trendColor, 100)

    fill(pTrailInner, pTrailOuter, trailTop, trailBottom, trailTopColor, trailBottomColor, title='Trail Gradient')

    showBands = overlayMode == 'Bands'

    pBandBasis = plot(basis if showBands else na, 'Band Center', color=trendColor, linewidth=3)

    pUpper = plot(upperBand if showBands else na, 'Upper Band', color=color.new(trendColor, 40), linewidth=1)

    pLower = plot(lowerBand if showBands else na, 'Lower Band', color=color.new(trendColor, 40), linewidth=1)

    fill(pUpper, pBandBasis, upperBand, basis, color.new(trendColor, 94), color.new(trendColor, 62), title='Upper Band Gradient')

    fill(pBandBasis, pLower, basis, lowerBand, color.new(trendColor, 62), color.new(trendColor, 94), title='Lower Band Gradient')

    plotcandle(open if showCandles else na, high if showCandles else na, low if showCandles else na, close if showCandles else na, 'Trend Candles', color=trendColor, wickcolor=trendColor, bordercolor=trendColor)

    if showSignals and newLong:
        label.new(bar_index, bullSignalAnchor, '𝓤𝓹', style=label.style_label_up, color=bullColor, textcolor=black, size=size.normal)

    if showSignals and newShort:
        label.new(bar_index, bearSignalAnchor, '𝓓𝓸𝔀𝓷', style=label.style_label_down, color=bearColor, textcolor=white, size=size.normal)

    plotshape(tp1 if newTP1 else na, title='TP1', style=shape.xcross, location=location.absolute, color=white, size=size.tiny)

    plotshape(tp2 if newTP2 else na, title='TP2', style=shape.xcross, location=location.absolute, color=white, size=size.tiny)

    plotshape(tp3 if newTP3 else na, title='TP3', style=shape.xcross, location=location.absolute, color=white, size=size.tiny)

    plotshape(tp4 if newTP4 else na, title='TP4', style=shape.xcross, location=location.absolute, color=white, size=size.tiny)

    plotshape(tp5 if newTP5 else na, title='TP5', style=shape.xcross, location=location.absolute, color=white, size=size.tiny)

    tpCount: int = (1 if tp1Hit else 0) + (1 if tp2Hit else 0) + (1 if tp3Hit else 0) + (1 if tp4Hit else 0) + (1 if tp5Hit else 0)

    progress = '○ ○ ○ ○ ○' if tpCount == 0 else '● ○ ○ ○ ○' if tpCount == 1 else '● ● ○ ○ ○' if tpCount == 2 else '● ● ● ○ ○' if tpCount == 3 else '● ● ● ● ○' if tpCount == 4 else '● ● ● ● ●'

    dashboard: Persistent[Table] = table.new(position.top_right, 2, 6, bgcolor=black, frame_color=color.new(white, 75), frame_width=1, border_width=0)

    if barstate.islast:
        table.clear(dashboard, 0, 0, 1, 5)

        if showTable:
            table.cell(dashboard, 0, 0, '𝓑𝓪𝓷𝓭 𝓕𝓵𝓸𝔀', text_color=white, bgcolor=black)

            table.cell(dashboard, 1, 0, '𝓑𝓾𝓵𝓵' if bullish else '𝓑𝓮𝓪𝓻', text_color=trendColor, bgcolor=black)

            table.cell(dashboard, 0, 1, 'Trend', text_color=dimWhite, bgcolor=black)

            table.cell(dashboard, 1, 1, 'UP' if bullish else 'DOWN', text_color=trendColor, bgcolor=black)

            table.cell(dashboard, 0, 2, 'Overlay', text_color=dimWhite, bgcolor=black)

            table.cell(dashboard, 1, 2, overlayMode, text_color=white, bgcolor=black)

            table.cell(dashboard, 0, 3, 'Signal Anchor', text_color=dimWhite, bgcolor=black)

            table.cell(dashboard, 1, 3, signalAnchorMode, text_color=white, bgcolor=black)

            table.cell(dashboard, 0, 4, 'Entry', text_color=dimWhite, bgcolor=black)

            table.cell(dashboard, 1, 4, '—' if na(entryPrice) else string.tostring(entryPrice, format.mintick), text_color=white, bgcolor=black)

            table.cell(dashboard, 0, 5, 'ATR Targets', text_color=dimWhite, bgcolor=black)

            table.cell(dashboard, 1, 5, progress, text_color=trendColor, bgcolor=black)

    alertcondition(newLong, 'Band Flow Up', 'Uptrick Band Flow turned bullish on {{ticker}}')

    alertcondition(newShort, 'Band Flow Down', 'Uptrick Band Flow turned bearish on {{ticker}}')

    alertcondition(newTP1, 'TP1', 'Band Flow TP1 hit on {{ticker}}')

    alertcondition(newTP2, 'TP2', 'Band Flow TP2 hit on {{ticker}}')

    alertcondition(newTP3, 'TP3', 'Band Flow TP3 hit on {{ticker}}')

    alertcondition(newTP4, 'TP4', 'Band Flow TP4 hit on {{ticker}}')

    alertcondition(newTP5, 'TP5', 'Band Flow TP5 hit on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)