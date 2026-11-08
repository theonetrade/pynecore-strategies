"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, bar_index, barmerge, barstate, close, color,
    format, high, input, label, last_bar_index, line, linefill, low, math, max_bars_back, na, open,
    plot, plotcandle, position, request, script, size, string, syminfo, ta, table, text, timeframe,
    volume, yloc
)
from pynecore.types import Color, Label, Line, LineFill, Persistent, Series, Table

GRP_CORE: str = "⚙️ Core Settings"
GRP_FILT: str = "🕯️ Filters"
GRP_TRADE: str = "📐 Trade Tools"
GRP_VIS: str = "🎨 Visuals"
GRP_DASH: str = "📊 Dashboard"
GRP_WH: str = "🔔 Alerts"
GRP_COL: str = "🌈 Colors"


@script.indicator(title="Williams Variable A/D Pressure [MarkitTick]", overlay=False, precision=2, format=format.volume, max_labels_count=500)
def main(
    i_wvadLen=input.int(20, "WVAD Period", group=GRP_CORE, minval=1, tooltip="Summation length for Williams' Variable A/D"),
    i_sigLen=input.int(9, "Signal Length", group=GRP_CORE, minval=1),
    i_useHtf=input.bool(False, "🕐 Use HTF Confirmation", group=GRP_FILT),
    i_htfTf=input.timeframe("60", "HTF Timeframe", group=GRP_FILT),
    i_useAdxFilter=input.bool(False, "📈 Use ADX Filter", group=GRP_FILT),
    i_adxThresh=input.float(20.0, "ADX Threshold", group=GRP_FILT, minval=0, step=0.5),
    i_adxLen=input.int(14, "ADX Length", group=GRP_FILT, minval=1),
    i_adaptFilterType=input.string("SMA", "🧠 Adaptive Filter", options=("None", "SMA", "EMA", "RMA", "Double WMA", "Triple VWMA", "HMA", "LLAMA", "Kalman Filter"), group=GRP_FILT),
    i_adaptFilterLen=input.int(9, "Adaptive Filter Length", group=GRP_FILT, minval=1, maxval=500),
    i_lockSignal=input.bool(False, "🔒 Lock Signal", group=GRP_TRADE, tooltip="Freeze current signal · block new ones"),
    i_showLevels=input.bool(True, "Show Trade Levels", group=GRP_TRADE),
    i_slMult=input.float(1.5, "SL × ATR", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp1Mult=input.float(1.0, "TP1 × R", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp2Mult=input.float(2.0, "TP2 × R", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp3Mult=input.float(3.0, "TP3 × R", group=GRP_TRADE, minval=0.1, step=0.1),
    i_atrLen=input.int(14, "ATR Length", group=GRP_TRADE, minval=1),
    i_showHist=input.bool(True, "Show Histogram", group=GRP_VIS),
    i_showLines=input.bool(True, "Show WVAD/Signal Lines", group=GRP_VIS),
    i_showMarkers=input.bool(True, "Show Signal Markers", group=GRP_VIS),
    i_showZero=input.bool(True, "Show Zero Line", group=GRP_VIS),
    i_showCandles=input.bool(True, "Color Candles", group=GRP_VIS),
    i_showDash=input.bool(True, "Show Dashboard", group=GRP_DASH),
    i_dashPos=input.string("Top Right", "Position", group=GRP_DASH, options=("Top Right", "Top Left", "Bottom Right", "Bottom Left")),
    i_actionLong=input.string("long", "↑ Long Action", group=GRP_WH),
    i_actionShort=input.string("short", "↓ Short Action", group=GRP_WH),
    i_actionCloseLong=input.string("closelong", "✕ Close Long Action", group=GRP_WH),
    i_actionCloseShort=input.string("closeshort", "✕ Close Short Action", group=GRP_WH),
    i_actionTp1=input.string("tp1", "◆ TP1 Hit Action", group=GRP_WH),
    i_actionTp2=input.string("tp2", "✦ TP2 Hit Action", group=GRP_WH),
    i_actionTp3=input.string("tp3", "◆ TP3 Hit Action", group=GRP_WH),
    i_actionSl=input.string("sl", "✕ SL Hit Action", group=GRP_WH),
    c_wvadLine=input.color(color.new(color.new('#2196F3'), 0), "WVAD Line", group=GRP_COL),
    c_sigLine=input.color(color.new(color.new('#FF9800'), 0), "Signal Line", group=GRP_COL),
    c_histUp1=input.color(color.new(color.new('#26A69A'), 0), "Hist Rising +", group=GRP_COL),
    c_histUp2=input.color(color.new(color.new('#26A69A'), 60), "Hist Falling +", group=GRP_COL),
    c_histDn1=input.color(color.new(color.new('#EF5350'), 0), "Hist Falling -", group=GRP_COL),
    c_histDn2=input.color(color.new(color.new('#EF5350'), 60), "Hist Rising -", group=GRP_COL),
    c_zeroLine=input.color(color.new(color.new('#787B86'), 50), "Zero Line", group=GRP_COL),
    c_markerLong=input.color(color.new(color.new('#26A69A'), 0), "Long Marker", group=GRP_COL),
    c_markerShort=input.color(color.new(color.new('#EF5350'), 0), "Short Marker", group=GRP_COL),
    c_markerTxt=input.color(color.new(color.new('#FFFFFF'), 0), "Signal Marker Text", group=GRP_COL),
    c_candBullBody=input.color(color.new(color.new('#26A69A'), 0), "Candle Bull Body", group=GRP_COL),
    c_candBearBody=input.color(color.new(color.new('#EF5350'), 0), "Candle Bear Body", group=GRP_COL),
    c_candNeutBody=input.color(color.new(color.new('#787B86'), 0), "Candle Neutral Body", group=GRP_COL),
    c_candBullBrd=input.color(color.new(color.new('#26A69A'), 0), "Candle Bull Border", group=GRP_COL),
    c_candBearBrd=input.color(color.new(color.new('#EF5350'), 0), "Candle Bear Border", group=GRP_COL),
    c_candNeutBrd=input.color(color.new(color.new('#787B86'), 0), "Candle Neutral Border", group=GRP_COL),
    c_slLevel=input.color(color.new(color.new('#EF5350'), 0), "SL Level", group=GRP_COL),
    c_entryLevel=input.color(color.new(color.new('#2196F3'), 0), "Entry Level", group=GRP_COL),
    c_tp1Level=input.color(color.new(color.new('#26A69A'), 40), "TP1 Level", group=GRP_COL),
    c_tp2Level=input.color(color.new(color.new('#26A69A'), 20), "TP2 Level", group=GRP_COL),
    c_tp3Level=input.color(color.new(color.new('#26A69A'), 0), "TP3 Level", group=GRP_COL),
    c_riskFill=input.color(color.new(color.new('#EF5350'), 80), "Risk Fill", group=GRP_COL),
    c_rewardFill=input.color(color.new(color.new('#26A69A'), 85), "Reward Fill", group=GRP_COL),
    c_lvlTxt=input.color(color.new(color.new('#FFFFFF'), 0), "Level Label Text", group=GRP_COL),
    C_DASH_HDR=input.color(color.new(color.new('#3A2A6D'), 55), "Dash Header", group=GRP_COL),
    C_DASH_BG=input.color(color.new(color.new('#0A0F1A'), 10), "Dash Background", group=GRP_COL),
    C_DASH_TXT=input.color(color.new(color.new('#FFFFFF'), 0), "Dash Text", group=GRP_COL),
    C_SUP=input.color(color.new(color.new('#26A69A'), 0), "Bullish Value", group=GRP_COL),
    C_RES=input.color(color.new(color.new('#EF5350'), 0), "Bearish Value", group=GRP_COL)
):
    def f_sma(src: float, len: int):
        return ta.sma(src, len)

    def f_ema(src: float, len: int):
        return ta.ema(src, len)

    def f_rma(src: float, len: int):
        return ta.rma(src, len)

    def f_doubleWma(src: float, len: int):
        _wma1: float = ta.wma(src, len)
        _wma2: float = ta.wma(_wma1, len)
        return _wma2

    def f_tripleVwma(src: float, len: int):
        _vwma1: float = ta.vwma(src, len)
        _vwma2: float = ta.vwma(_vwma1, len)
        _vwma3: float = ta.vwma(_vwma2, len)
        return _vwma3

    def f_hma(src: float, len: int):
        return ta.hma(src, len)

    def f_kalman(src: float, len: int):
        _est: Persistent[float] = na(float)
        _err: Persistent[float] = 1.0
        _q: float = 1.0 / len
        _r: float = 1.0
        _est = src if na(_est) else _est
        _predErr: float = _err + _q
        _gain: float = _predErr / (_predErr + _r)
        _est = _est + _gain * (src - _est)
        _err = (1 - _gain) * _predErr
        return _est

    def f_llama(src: Series[float], len: int):
        _mean: float = ta.sma(src, len)
        _slope: float = (src - src[len]) / len
        return _mean + _slope * (len / 2)

    def f_bar(val: float, maxVal: float):
        filled: int = math.round(math.min(val / maxVal, 1.0) * 10)
        bar: str = ""
        for i in pine_range(1, 10):
            bar += '█' if i <= filled else '░'
        return bar + '  ' + string.tostring(math.round(math.min(val / maxVal, 1.0) * 100)) + '%'

    def f_barColor(pct: float):
        return color.new(color.new('#26A69A'), 0) if pct >= 0.66 else color.new(color.new('#F9A825'), 0) if pct >= 0.33 else color.new(color.new('#EF5350'), 0)

    def f_tf():
        _u: str = string.substring(timeframe.period, string.length(timeframe.period) - 1, string.length(timeframe.period))
        _tfNum: float = string.tonumber(timeframe.period)
        return timeframe.period if _u == 'S' else timeframe.period if _u == 'D' else timeframe.period if _u == 'W' else timeframe.period if _u == 'M' else timeframe.period if na(_tfNum) else string.tostring(_tfNum / 60) + 'H' if _tfNum % 60 == 0 else timeframe.period + 'm'

    def f_num(val: float):
        _a: float = math.abs(val)
        _s: str = '-' if val < 0 else ''
        return _s + string.tostring(_a / 1000000000, '#.#') + 'B' if _a >= 1000000000 else _s + string.tostring(_a / 1000000, '#.#') + 'M' if _a >= 1000000 else _s + string.tostring(_a / 1000, '#.#') + 'K' if _a >= 1000 else _s + string.tostring(_a, '#')

    rawWvad: float = (close - open) / (high - low) * volume if high != low else 0.0
    wvadSum: float = ta.sma(rawWvad, i_wvadLen) * i_wvadLen
    max_bars_back(wvadSum, 500)

    _adaptedSrc: float = f_sma(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'SMA' else f_ema(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'EMA' else f_rma(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'RMA' else f_doubleWma(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'Double WMA' else f_tripleVwma(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'Triple VWMA' else f_hma(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'HMA' else f_llama(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'LLAMA' else f_kalman(wvadSum, i_adaptFilterLen) if i_adaptFilterType == 'Kalman Filter' else wvadSum

    finalWvad: Series[float] = _adaptedSrc
    signalLine: Series[float] = ta.sma(finalWvad, i_sigLen)
    histWvad: Series[float] = finalWvad - signalLine

    _adxVal: Series
    _, __, _adxVal = ta.dmi(i_adxLen, i_adxLen)
    _adxPass: bool = not i_useAdxFilter or _adxVal[1] >= i_adxThresh

    htfClose, htfOpen = request.security(syminfo.tickerid, i_htfTf, (close[1], open[1]), lookahead=barmerge.lookahead_on)
    htfBullish: bool = htfClose > htfOpen
    htfBearish: bool = htfClose < htfOpen
    _htfPassLong: bool = not i_useHtf or htfBullish
    _htfPassShort: bool = not i_useHtf or htfBearish

    _rawLongSignal: bool = ta.crossover(finalWvad[1], signalLine[1])
    _rawShortSignal: bool = ta.crossunder(finalWvad[1], signalLine[1])

    longSignal: bool = _rawLongSignal and _adxPass and _htfPassLong
    shortSignal: bool = _rawShortSignal and _adxPass and _htfPassShort

    avgVol: float = ta.sma(volume, 20)
    volRatio: float = volume / avgVol if avgVol > 0 else 0.0
    volPct: float = math.min(volRatio / 2.0, 1.0) if avgVol > 0 else 0.0

    strengthMax: float = ta.highest(math.abs(finalWvad), 100)
    strengthRaw: float = math.abs(finalWvad) / strengthMax if strengthMax > 0 else 0.0

    _atr: Series[float] = ta.atr(i_atrLen)

    slLine: Persistent[Line] = na(Line)
    entryLine: Persistent[Line] = na(Line)
    tp1Line: Persistent[Line] = na(Line)
    tp2Line: Persistent[Line] = na(Line)
    tp3Line: Persistent[Line] = na(Line)
    slLbl: Persistent[Label] = na(Label)
    entryLbl: Persistent[Label] = na(Label)
    tp1Lbl: Persistent[Label] = na(Label)
    tp2Lbl: Persistent[Label] = na(Label)
    tp3Lbl: Persistent[Label] = na(Label)
    riskFill: Persistent[LineFill] = na(LineFill)
    rewardFill: Persistent[LineFill] = na(LineFill)

    entryPrice: Persistent[float] = na(float)
    slPrice: Persistent[float] = na(float)
    tp1Price: Persistent[float] = na(float)
    tp2Price: Persistent[float] = na(float)
    tp3Price: Persistent[float] = na(float)
    isLong: Persistent[bool] = False
    tp1Hit: Persistent[bool] = False
    tp2Hit: Persistent[bool] = False
    tp3Hit: Persistent[bool] = False
    slHit: Persistent[bool] = False

    _locked: bool = i_lockSignal and barstate.islast
    _calcLevels: bool = (longSignal or shortSignal) and (not _locked)
    _drawLevels: bool = i_showLevels and _calcLevels

    _closeBar: Persistent[int] = na(int)

    def f_pctTxt(lvl: float, entry: float, dir: bool):
        _p: float = (lvl - entry if dir else entry - lvl) / entry * 100
        return ('+' if _p >= 0 else '') + string.tostring(_p, '#.00') + '%'

    def f_deleteLevels():
        line.delete(slLine)
        line.delete(entryLine)
        line.delete(tp1Line)
        line.delete(tp2Line)
        line.delete(tp3Line)
        label.delete(slLbl)
        label.delete(entryLbl)
        label.delete(tp1Lbl)
        label.delete(tp2Lbl)
        label.delete(tp3Lbl)
        linefill.delete(riskFill)
        return linefill.delete(rewardFill)

    if _calcLevels:
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        slHit = False
        _closeBar = na
        isLong = longSignal
        entryPrice = close[1]
        _risk: float = _atr[1] * i_slMult
        slPrice = close[1] - _risk if longSignal else close[1] + _risk
        tp1Price = close[1] + _risk * i_tp1Mult if longSignal else close[1] - _risk * i_tp1Mult
        tp2Price = close[1] + _risk * i_tp2Mult if longSignal else close[1] - _risk * i_tp2Mult
        tp3Price = close[1] + _risk * i_tp3Mult if longSignal else close[1] - _risk * i_tp3Mult

    _tp1Cross: bool = not na(tp1Price) and (high >= tp1Price if isLong else low <= tp1Price)
    _tp2Cross: bool = not na(tp2Price) and (high >= tp2Price if isLong else low <= tp2Price)
    _tp3Cross: bool = not na(tp3Price) and (high >= tp3Price if isLong else low <= tp3Price)
    _slCross: bool = not na(slPrice) and (low <= slPrice if isLong else high >= slPrice)

    _tp1Fire: bool = not na(tp1Price) and (not tp1Hit) and (not slHit) and _tp1Cross
    _tp2Fire: bool = not na(tp2Price) and (not tp2Hit) and (not slHit) and _tp2Cross
    _tp3Fire: bool = not na(tp3Price) and (not tp3Hit) and (not slHit) and _tp3Cross
    _slFire: bool = not na(slPrice) and (not slHit) and _slCross

    _longInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"long","entry":"{3}","wvad":"{4}","signal":"{5}"', i_actionLong, syminfo.tickerid, timeframe.period, string.tostring(entryPrice, format.mintick), string.tostring(finalWvad, format.mintick), string.tostring(signalLine, format.mintick))
    longPayload: str = '{' + _longInner + '}'

    _shortInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"short","entry":"{3}","wvad":"{4}","signal":"{5}"', i_actionShort, syminfo.tickerid, timeframe.period, string.tostring(entryPrice, format.mintick), string.tostring(finalWvad, format.mintick), string.tostring(signalLine, format.mintick))
    shortPayload: str = '{' + _shortInner + '}'

    _closeLongInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"closelong"', i_actionCloseLong, syminfo.tickerid, timeframe.period)
    closeLongPayload: str = '{' + _closeLongInner + '}'

    _closeShortInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"closeshort"', i_actionCloseShort, syminfo.tickerid, timeframe.period)
    closeShortPayload: str = '{' + _closeShortInner + '}'

    if longSignal and barstate.isconfirmed:
        alert(closeShortPayload, alert.freq_once_per_bar_close)
    if longSignal and barstate.isconfirmed:
        alert(longPayload, alert.freq_once_per_bar_close)
    if shortSignal and barstate.isconfirmed:
        alert(closeLongPayload, alert.freq_once_per_bar_close)
    if shortSignal and barstate.isconfirmed:
        alert(shortPayload, alert.freq_once_per_bar_close)

    alertcondition(longSignal and barstate.isconfirmed, 'BUY Signal', 'MarkitTick — WVADP BUY Signal Fired')
    alertcondition(shortSignal and barstate.isconfirmed, 'SELL Signal', 'MarkitTick — WVADP SELL Signal Fired')
    alertcondition(shortSignal and barstate.isconfirmed, 'Close Long Signal', 'MarkitTick — Close Long')
    alertcondition(longSignal and barstate.isconfirmed, 'Close Short Signal', 'MarkitTick — Close Short')

    _tpDir: str = 'long' if isLong else 'short'
    _tp1Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","entry":"{4}","tp":"{5}"', i_actionTp1, syminfo.tickerid, timeframe.period, _tpDir, string.tostring(entryPrice, format.mintick), string.tostring(tp1Price, format.mintick))
    tp1Payload: str = '{' + _tp1Inner + '}'

    _tp2Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","entry":"{4}","tp":"{5}"', i_actionTp2, syminfo.tickerid, timeframe.period, _tpDir, string.tostring(entryPrice, format.mintick), string.tostring(tp2Price, format.mintick))
    tp2Payload: str = '{' + _tp2Inner + '}'

    _tp3Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","entry":"{4}","tp":"{5}"', i_actionTp3, syminfo.tickerid, timeframe.period, _tpDir, string.tostring(entryPrice, format.mintick), string.tostring(tp3Price, format.mintick))
    tp3Payload: str = '{' + _tp3Inner + '}'

    _slInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","entry":"{4}","sl":"{5}"', i_actionSl, syminfo.tickerid, timeframe.period, _tpDir, string.tostring(entryPrice, format.mintick), string.tostring(slPrice, format.mintick))
    slPayload: str = '{' + _slInner + '}'

    if _tp1Fire:
        alert(tp1Payload, alert.freq_once_per_bar)
    if _tp2Fire:
        alert(tp2Payload, alert.freq_once_per_bar)
    if _tp3Fire:
        alert(tp3Payload, alert.freq_once_per_bar)
    if _slFire:
        alert(slPayload, alert.freq_once_per_bar)

    alertcondition(_tp1Fire, 'TP1 Hit', 'MarkitTick — WVADP TP1 Hit')
    alertcondition(_tp2Fire, 'TP2 Hit', 'MarkitTick — WVADP TP2 Hit')
    alertcondition(_tp3Fire, 'TP3 Hit', 'MarkitTick — WVADP TP3 Hit')
    alertcondition(_slFire, 'SL Hit', 'MarkitTick — WVADP SL Hit')

    _histColor: Color = (c_histUp1 if histWvad >= histWvad[1] else c_histUp2) if histWvad >= 0 else c_histDn1 if histWvad <= histWvad[1] else c_histDn2
    plot(0.0 if i_showZero else na, 'Zero Line', color=c_zeroLine, style=plot.style_line, linewidth=1)
    plot(histWvad if i_showHist else na, 'Histogram', color=_histColor, style=plot.style_columns)
    plot(finalWvad if i_showLines else na, 'WVAD', color=c_wvadLine, linewidth=2)
    plot(signalLine if i_showLines else na, 'Signal', color=c_sigLine, linewidth=1)
    if i_showMarkers and longSignal:
        label.new(bar_index, finalWvad, 'BULL', style=label.style_label_up, color=c_markerLong, textcolor=c_markerTxt, size=size.small)
        label.new(bar_index, na, 'BULL', yloc=yloc.belowbar, style=label.style_label_up, color=c_markerLong, textcolor=c_markerTxt, size=size.small, force_overlay=True)
    if i_showMarkers and shortSignal:
        label.new(bar_index, finalWvad, 'BEAR', style=label.style_label_down, color=c_markerShort, textcolor=c_markerTxt, size=size.small)
        label.new(bar_index, na, 'BEAR', yloc=yloc.abovebar, style=label.style_label_down, color=c_markerShort, textcolor=c_markerTxt, size=size.small, force_overlay=True)
    _candleBody: Color = c_candBullBody if finalWvad > signalLine else c_candBearBody if finalWvad < signalLine else c_candNeutBody
    _candleBorder: Color = c_candBullBrd if finalWvad > signalLine else c_candBearBrd if finalWvad < signalLine else c_candNeutBrd
    plotcandle(open if i_showCandles else na, high if i_showCandles else na, low if i_showCandles else na, close if i_showCandles else na, title='Heatmap Candles', color=_candleBody, wickcolor=_candleBorder, bordercolor=_candleBorder, force_overlay=True)

    if _drawLevels:
        f_deleteLevels()
        _x2: int = bar_index + 10
        slLine = line.new(bar_index, slPrice, _x2, slPrice, color=c_slLevel, style=line.style_solid, width=2, force_overlay=True)
        entryLine = line.new(bar_index, entryPrice, _x2, entryPrice, color=c_entryLevel, style=line.style_dashed, width=1, force_overlay=True)
        tp1Line = line.new(bar_index, tp1Price, _x2, tp1Price, color=c_tp1Level, style=line.style_dashed, width=1, force_overlay=True)
        tp2Line = line.new(bar_index, tp2Price, _x2, tp2Price, color=c_tp2Level, style=line.style_dashed, width=1, force_overlay=True)
        tp3Line = line.new(bar_index, tp3Price, _x2, tp3Price, color=c_tp3Level, style=line.style_dashed, width=1, force_overlay=True)
        slLbl = label.new(_x2, slPrice, '✕ SL ' + string.tostring(slPrice, format.mintick), style=label.style_label_left, color=c_slLevel, textcolor=c_lvlTxt, size=size.small, force_overlay=True)
        entryLbl = label.new(_x2, entryPrice, '▶ Entry ' + string.tostring(entryPrice, format.mintick), style=label.style_label_left, color=c_entryLevel, textcolor=c_lvlTxt, size=size.small, force_overlay=True)
        tp1Lbl = label.new(_x2, tp1Price, '◆ TP1 ' + string.tostring(tp1Price, format.mintick), style=label.style_label_left, color=c_tp1Level, textcolor=c_lvlTxt, size=size.small, force_overlay=True)
        tp2Lbl = label.new(_x2, tp2Price, '✦ TP2 ' + string.tostring(tp2Price, format.mintick), style=label.style_label_left, color=c_tp2Level, textcolor=c_lvlTxt, size=size.small, force_overlay=True)
        tp3Lbl = label.new(_x2, tp3Price, '◆ TP3 ' + string.tostring(tp3Price, format.mintick), style=label.style_label_left, color=c_tp3Level, textcolor=c_lvlTxt, size=size.small, force_overlay=True)
        riskFill = linefill.new(slLine, entryLine, c_riskFill)
        rewardFill = linefill.new(entryLine, tp3Line, c_rewardFill)

    if _tp1Fire:
        tp1Hit = True
        label.set_text(tp1Lbl, 'TP1 ✓ HIT ' + f_pctTxt(tp1Price, entryPrice, isLong))
    if _tp2Fire:
        tp2Hit = True
        label.set_text(tp2Lbl, 'TP2 ✓ HIT ' + f_pctTxt(tp2Price, entryPrice, isLong))
    if _tp3Fire:
        tp3Hit = True
        label.set_text(tp3Lbl, 'TP3 ✓ HIT ' + f_pctTxt(tp3Price, entryPrice, isLong))
    if _slFire:
        slHit = True
        label.set_text(slLbl, 'SL ✓ HIT ' + f_pctTxt(slPrice, entryPrice, isLong))

    _tradeClosed: bool = slHit or tp3Hit
    if not na(slLine) and _tradeClosed and na(_closeBar):
        _closeBar = bar_index

    _extUpdate: bool = _closeBar == bar_index if _tradeClosed else barstate.islast
    if not na(slLine) and _extUpdate:
        _extX: int = _closeBar + 10 if _tradeClosed else last_bar_index + 10
        line.set_x2(slLine, _extX)
        line.set_x2(entryLine, _extX)
        line.set_x2(tp1Line, _extX)
        line.set_x2(tp2Line, _extX)
        line.set_x2(tp3Line, _extX)
        label.set_x(slLbl, _extX)
        label.set_x(entryLbl, _extX)
        label.set_x(tp1Lbl, _extX)
        label.set_x(tp2Lbl, _extX)
        label.set_x(tp3Lbl, _extX)

    tablePosition: Persistent[str] = position.top_right if i_dashPos == 'Top Right' else position.top_left if i_dashPos == 'Top Left' else position.bottom_right if i_dashPos == 'Bottom Right' else position.bottom_left
    dash: Persistent[Table] = table.new(tablePosition, 2, 18, bgcolor=na, border_width=1, border_color=color.new(color.new('#2A3040'), 40), frame_width=1, frame_color=color.new(color.new('#3A2A6D'), 40), force_overlay=True)

    row_a: Color = C_DASH_BG
    row_b: Color = color.new(C_DASH_BG, 40)
    lbl_col: Color = color.new(C_DASH_TXT, 25)

    biasStr: str = 'BULLISH  ' if finalWvad > signalLine else 'BEARISH  ' if finalWvad < signalLine else 'NEUTRAL  '
    biasColor: Color = C_SUP if finalWvad > signalLine else C_RES if finalWvad < signalLine else C_DASH_TXT
    wvadColor: Color = C_SUP if finalWvad >= 0 else C_RES
    histColorTxt: Color = C_SUP if histWvad >= 0 else C_RES
    htfBiasStr: str = 'OFF  ' if not i_useHtf else 'BULL  ' if htfBullish else 'BEAR  ' if htfBearish else 'FLAT  '
    htfColor: Color = C_DASH_TXT if not i_useHtf else C_SUP if htfBullish else C_RES if htfBearish else C_DASH_TXT
    adxColor: Color = C_SUP if _adxPass else C_RES
    lockStr: str = 'ACTIVE  ' if i_lockSignal else 'OFF  '
    lockCol: Color = C_RES if i_lockSignal else C_DASH_TXT
    tradeStr: str = '—  ' if na(entryPrice) else 'LONG  ' if isLong else 'SHORT  '
    tradeCol: Color = C_DASH_TXT if na(entryPrice) else C_SUP if isLong else C_RES
    entryStr: str = '—  ' if na(entryPrice) else string.tostring(entryPrice, format.mintick) + '  '
    slStr: str = '—  ' if na(slPrice) else string.tostring(slPrice, format.mintick) + '  '
    tp1Str: str = '—  ' if na(tp1Price) else string.tostring(tp1Price, format.mintick) + '  '
    tp2Str: str = '—  ' if na(tp2Price) else string.tostring(tp2Price, format.mintick) + '  '
    tp3Str: str = '—  ' if na(tp3Price) else string.tostring(tp3Price, format.mintick) + '  '
    slCol: Color = C_RES if slHit else C_DASH_TXT
    tp1Col: Color = C_SUP if tp1Hit else C_DASH_TXT
    tp2Col: Color = C_SUP if tp2Hit else C_DASH_TXT
    tp3Col: Color = C_SUP if tp3Hit else C_DASH_TXT

    if i_showDash:
        table.cell(dash, 0, 0, 'WVADP', text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_left, bgcolor=C_DASH_HDR)
        table.cell(dash, 1, 0, syminfo.ticker + '  ·  ' + f_tf(), text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_right, bgcolor=C_DASH_HDR)

        table.cell(dash, 0, 1, '  Lock', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_a)
        table.cell(dash, 1, 1, lockStr, text_color=lockCol, text_size=size.small, text_halign=text.align_right, bgcolor=row_a)

        table.cell(dash, 0, 2, '  Bias', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_b)
        table.cell(dash, 1, 2, biasStr, text_color=biasColor, text_size=size.small, text_halign=text.align_right, bgcolor=row_b)

        table.cell(dash, 0, 3, '  WVAD', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_a)
        table.cell(dash, 1, 3, string.tostring(finalWvad, '#.##') + '  ', text_color=wvadColor, text_size=size.small, text_halign=text.align_right, bgcolor=row_a)

        table.cell(dash, 0, 4, '  Signal', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_b)
        table.cell(dash, 1, 4, string.tostring(signalLine, '#.##') + '  ', text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_right, bgcolor=row_b)

        table.cell(dash, 0, 5, '  Histogram', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_a)
        table.cell(dash, 1, 5, string.tostring(histWvad, '#.##') + '  ', text_color=histColorTxt, text_size=size.small, text_halign=text.align_right, bgcolor=row_a)

        table.cell(dash, 0, 6, '  Strength', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_b)
        table.cell(dash, 1, 6, f_bar(strengthRaw, 1.0) + '  ', text_color=f_barColor(strengthRaw), text_size=size.small, text_halign=text.align_right, bgcolor=row_b)

        table.cell(dash, 0, 7, '  Volume', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_a)
        table.cell(dash, 1, 7, f_num(volume) + '  ', text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_right, bgcolor=row_a)

        table.cell(dash, 0, 8, '  Vol Ratio', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=row_b)
        table.cell(dash, 1, 8, f_bar(volRatio, 2.0) + '  ', text_color=f_barColor(volPct), text_size=size.small, text_halign=text.align_right, bgcolor=row_b)

        _row: int = 9

        if i_useHtf:
            _rowBg: Color = row_a if _row % 2 == 1 else row_b
            table.cell(dash, 0, _row, '  HTF Bias', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBg)
            table.cell(dash, 1, _row, htfBiasStr, text_color=htfColor, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBg)
            _row += 1

        if i_useAdxFilter:
            _rowBg: Color = row_a if _row % 2 == 1 else row_b
            table.cell(dash, 0, _row, '  ADX', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBg)
            table.cell(dash, 1, _row, string.tostring(_adxVal, '#.##') + '  ', text_color=adxColor, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBg)
            _row += 1

        if i_adaptFilterType != 'None':
            _rowBg: Color = row_a if _row % 2 == 1 else row_b
            table.cell(dash, 0, _row, '  Adapt Filter', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBg)
            table.cell(dash, 1, _row, i_adaptFilterType + '  ', text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBg)
            _row += 1

        _rowBgTrade: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  Trade', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgTrade)
        table.cell(dash, 1, _row, tradeStr, text_color=tradeCol, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgTrade)
        _row += 1

        _rowBgEntry: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  Entry', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgEntry)
        table.cell(dash, 1, _row, entryStr, text_color=C_DASH_TXT, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgEntry)
        _row += 1

        _rowBgSl: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  SL', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgSl)
        table.cell(dash, 1, _row, slStr, text_color=slCol, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgSl)
        _row += 1

        _rowBgTp1: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  TP1', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgTp1)
        table.cell(dash, 1, _row, tp1Str, text_color=tp1Col, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgTp1)
        _row += 1

        _rowBgTp2: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  TP2', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgTp2)
        table.cell(dash, 1, _row, tp2Str, text_color=tp2Col, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgTp2)
        _row += 1

        _rowBgTp3: Color = row_a if _row % 2 == 1 else row_b
        table.cell(dash, 0, _row, '  TP3', text_color=lbl_col, text_size=size.small, text_halign=text.align_left, bgcolor=_rowBgTp3)
        table.cell(dash, 1, _row, tp3Str, text_color=tp3Col, text_size=size.small, text_halign=text.align_right, bgcolor=_rowBgTp3)
        _row += 1


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
