"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, bar_index, barmerge, barstate, close, color,
    display, format, high, hline, input, label, last_bar_index, line, linefill, location, low,
    math, na, open, plot, plotcandle, plotshape, position, request, script, shape, size, string,
    syminfo, ta, table, text, timeframe, volume
)
from pynecore.types import Color, Label, Line, LineFill, Persistent, PersistentSeries, Series, Table

GRP_CORE: str = "⚙️ Core Settings"
GRP_FILT: str = "🕯️ Filters"
GRP_TRADE: str = "📐 Trade Tools"
GRP_VIS: str = "🎨 Visuals"
GRP_DASH: str = "📊 Dashboard"
GRP_WH: str = "🔔 Alerts"
GRP_COL: str = "🌈 Colors"


@script.indicator(title="Coppock Curve Multi-Filter [MarkitTick]", overlay=False)
def main(
    i_src: Series[float] = input.source(close, "Source", group=GRP_CORE),
    i_rocLong=input.int(14, "Long ROC Length", group=GRP_CORE, minval=1),
    i_rocShort=input.int(11, "Short ROC Length", group=GRP_CORE, minval=1),
    i_wmaLen=input.int(10, "WMA Smoothing Length", group=GRP_CORE, minval=1),
    i_useAdxFilter=input.bool(False, "📈 Use ADX Filter", group=GRP_FILT),
    i_adxThresh=input.float(20.0, "ADX Threshold", group=GRP_FILT, minval=0, step=0.5),
    i_adxLen=input.int(14, "ADX Length", group=GRP_FILT, minval=1),
    i_adaptFilterType=input.string("None", "🧠 Adaptive Filter", options=("None", "SMA", "EMA", "RMA", "Double WMA", "Triple VWMA", "HMA", "LLAMA", "Kalman Filter"), group=GRP_FILT),
    i_adaptFilterLen=input.int(20, "Adaptive Filter Length", group=GRP_FILT, minval=1),
    i_useDivFilter=input.bool(False, "🔀 Use Divergence Filter", group=GRP_FILT, tooltip="Suppress cross signals that oppose a detected price/Coppock divergence"),
    i_divLookback=input.int(5, "Divergence Pivot Lookback", group=GRP_FILT, minval=2),
    i_useAccelFilter=input.bool(False, "⚡ Use Slope Acceleration Filter", group=GRP_FILT, tooltip="Require the slope itself to be increasing, not just positive"),
    i_useVolFilter=input.bool(False, "🔊 Use Volume Confirmation Filter", group=GRP_FILT, tooltip="Require volume above its average for a signal to fire"),
    i_volLen=input.int(20, "Volume MA Length", group=GRP_FILT, minval=1),
    i_useMtfFilter=input.bool(False, "⏱️ Use HTF Alignment Filter", group=GRP_FILT, tooltip="Require a higher timeframe Coppock to agree with the signal direction"),
    i_mtfTimeframe=input.timeframe("240", "HTF Alignment Timeframe", group=GRP_FILT),
    i_useVolatZeroFilter=input.bool(False, "🌊 Use Volatility-Adjusted Zero Line", group=GRP_FILT, tooltip="Require zero-line crosses to exceed the indicator's own noise band"),
    i_volatZeroMult=input.float(0.5, "Volatility Zero Band Multiple", group=GRP_FILT, minval=0.1, step=0.1),
    i_volatZeroLen=input.int(20, "Volatility Zero Band Length", group=GRP_FILT, minval=1),
    i_usePersistFilter=input.bool(False, "⏳ Use Signal Persistence Filter", group=GRP_FILT, tooltip="Require direction to hold for N consecutive bars before signaling"),
    i_persistBars=input.int(2, "Persistence Bars", group=GRP_FILT, minval=1),
    i_lockSignal=input.bool(False, "🔒 Lock Signal", group=GRP_TRADE, tooltip="Freeze current signal · block new ones"),
    i_atrMult=input.float(1.5, "SL ATR Multiple", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp1R=input.float(1.0, "TP1 R-Multiple", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp2R=input.float(2.0, "TP2 R-Multiple", group=GRP_TRADE, minval=0.1, step=0.1),
    i_tp3R=input.float(3.0, "TP3 R-Multiple", group=GRP_TRADE, minval=0.1, step=0.1),
    i_atrLen=input.int(14, "ATR Length", group=GRP_TRADE, minval=1),
    i_showLevels=input.bool(True, "Show Trade Levels", group=GRP_TRADE),
    i_showCandles=input.bool(True, "Use Candle Coloring", group=GRP_VIS),
    i_showHist=input.bool(True, "Show Histogram", group=GRP_VIS),
    i_showZeroX=input.bool(True, "Show Zero-Cross Markers", group=GRP_VIS),
    i_showDash=input.bool(True, "Show Dashboard", group=GRP_DASH),
    i_dashPos=input.string(position.top_right, "Position", group=GRP_DASH, options=(position.top_right, position.top_left, position.bottom_right, position.bottom_left, position.middle_right, position.middle_left)),
    i_actionBull=input.string("bull", "↑ Bull Cross Action", group=GRP_WH),
    i_actionBear=input.string("bear", "↓ Bear Cross Action", group=GRP_WH),
    i_actionZeroUp=input.string("zeroup", "⤴ Zero Cross Up Action", group=GRP_WH),
    i_actionZeroDown=input.string("zerodown", "⤵ Zero Cross Down Action", group=GRP_WH),
    i_actionCloseLong=input.string("closelong", "✕ Close Long Action", group=GRP_WH),
    i_actionCloseShort=input.string("closeshort", "✕ Close Short Action", group=GRP_WH),
    i_actionTp1=input.string("tp1hit", "◆ TP1 Hit Action", group=GRP_WH),
    i_actionTp2=input.string("tp2hit", "◆ TP2 Hit Action", group=GRP_WH),
    i_actionTp3=input.string("tp3hit", "◆ TP3 Hit Action", group=GRP_WH),
    i_actionSlHit=input.string("slhit", "✕ SL Hit Action", group=GRP_WH),
    c_bull=input.color(color.new('#26A69A'), "Bull Color", group=GRP_COL),
    c_bear=input.color(color.new('#EF5350'), "Bear Color", group=GRP_COL),
    c_neutral=input.color(color.new('#787B86'), "Neutral Color", group=GRP_COL),
    c_zeroLine=input.color(color.new('#787B86'), "Zero Line Color", group=GRP_COL),
    c_histBullStrong=input.color(color.new('#26A69A'), "Histogram Bull Strong", group=GRP_COL),
    c_histBullWeak=input.color(color.new('#B2DFDB'), "Histogram Bull Weak", group=GRP_COL),
    c_histBearWeak=input.color(color.new('#FFCDD2'), "Histogram Bear Weak", group=GRP_COL),
    c_histBearStrong=input.color(color.new('#FF5252'), "Histogram Bear Strong", group=GRP_COL),
    C_DASH_HDR=input.color(color.new(color.new('#3A2A6D'), 55), "Dashboard Header", group=GRP_COL),
    C_DASH_BG=input.color(color.new(color.new('#0A0F1A'), 10), "Dashboard Background", group=GRP_COL),
    C_DASH_TXT=input.color(color.new('#FFFFFF'), "Dashboard Text", group=GRP_COL),
    C_SUP=input.color(color.new('#26A69A'), "Bullish Value Color", group=GRP_COL),
    C_RES=input.color(color.new('#EF5350'), "Bearish Value Color", group=GRP_COL),
    c_sl=input.color(color.new('#EF5350'), "SL Line Color", group=GRP_COL),
    c_entry=input.color(color.new('#2196F3'), "Entry Line Color", group=GRP_COL),
    c_tp1=input.color(color.new(color.new('#26A69A'), 40), "TP1 Line Color", group=GRP_COL),
    c_tp2=input.color(color.new(color.new('#26A69A'), 20), "TP2 Line Color", group=GRP_COL),
    c_tp3=input.color(color.new(color.new('#26A69A'), 0), "TP3 Line Color", group=GRP_COL),
    c_riskFill=input.color(color.new(color.new('#EF5350'), 80), "Risk Zone Fill", group=GRP_COL),
    c_rewardFill=input.color(color.new(color.new('#26A69A'), 85), "Reward Zone Fill", group=GRP_COL)
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

    _adaptedSrc: float = f_sma(i_src, i_adaptFilterLen) if i_adaptFilterType == 'SMA' else f_ema(i_src, i_adaptFilterLen) if i_adaptFilterType == 'EMA' else f_rma(i_src, i_adaptFilterLen) if i_adaptFilterType == 'RMA' else f_doubleWma(i_src, i_adaptFilterLen) if i_adaptFilterType == 'Double WMA' else f_tripleVwma(i_src, i_adaptFilterLen) if i_adaptFilterType == 'Triple VWMA' else f_hma(i_src, i_adaptFilterLen) if i_adaptFilterType == 'HMA' else f_llama(i_src, i_adaptFilterLen) if i_adaptFilterType == 'LLAMA' else f_kalman(i_src, i_adaptFilterLen) if i_adaptFilterType == 'Kalman Filter' else i_src

    _rocLongVal: float = ta.roc(_adaptedSrc, i_rocLong)
    _rocShortVal: float = ta.roc(_adaptedSrc, i_rocShort)
    coppock: Series[float] = ta.wma(_rocLongVal + _rocShortVal, i_wmaLen)

    def f_pivotHigh(src: Series[float], len: int):
        candidate: float = src[len]
        isValid: bool = True
        for i in pine_range(0, len * 2):
            if i != len and src[i] >= candidate:
                isValid = False
        return candidate if isValid else na

    def f_pivotLow(src: Series[float], len: int):
        candidate: float = src[len]
        isValid: bool = True
        for i in pine_range(0, len * 2):
            if i != len and src[i] <= candidate:
                isValid = False
        return candidate if isValid else na

    _diPlus, _diMinus, _adxVal = ta.dmi(i_adxLen, i_adxLen)
    _adxPass: bool = not i_useAdxFilter or _adxVal >= i_adxThresh

    _pivLowPrice: Persistent[float] = na(float)
    _pivLowCop: Persistent[float] = na(float)
    _lastPivLowPrice: Persistent[float] = na(float)
    _lastPivLowCop: Persistent[float] = na(float)
    _bullDiv: Persistent[bool] = False
    _pivHighPrice: Persistent[float] = na(float)
    _pivHighCop: Persistent[float] = na(float)
    _lastPivHighPrice: Persistent[float] = na(float)
    _lastPivHighCop: Persistent[float] = na(float)
    _bearDiv: Persistent[bool] = False
    _candPivLow: float = f_pivotLow(low, i_divLookback)
    _candPivHigh: float = f_pivotHigh(high, i_divLookback)
    if not na(_candPivLow):
        _lastPivLowPrice = _pivLowPrice
        _lastPivLowCop = _pivLowCop
        _pivLowPrice = _candPivLow
        _pivLowCop = coppock[i_divLookback]
        _bullDiv = not na(_lastPivLowPrice) and _pivLowPrice < _lastPivLowPrice and (_pivLowCop > _lastPivLowCop)
    if not na(_candPivHigh):
        _lastPivHighPrice = _pivHighPrice
        _lastPivHighCop = _pivHighCop
        _pivHighPrice = _candPivHigh
        _pivHighCop = coppock[i_divLookback]
        _bearDiv = not na(_lastPivHighPrice) and _pivHighPrice > _lastPivHighPrice and (_pivHighCop < _lastPivHighCop)
    _divPassLong: bool = not i_useDivFilter or not _bearDiv
    _divPassShort: bool = not i_useDivFilter or not _bullDiv

    _slope0: float = coppock - coppock[1]
    _slope1: float = coppock[1] - coppock[2]
    _accelPassLong: bool = not i_useAccelFilter or _slope0 > _slope1
    _accelPassShort: bool = not i_useAccelFilter or _slope0 < _slope1

    _volMa: float = ta.sma(volume, i_volLen)
    _volPass: bool = not i_useVolFilter or volume > _volMa

    _htfCoppock, _htfCoppockPrev = request.security(syminfo.tickerid, i_mtfTimeframe, (coppock[1], coppock[2]), lookahead=barmerge.lookahead_on)
    _htfBullish: bool = _htfCoppock > _htfCoppockPrev
    _mtfPassLong: bool = not i_useMtfFilter or _htfBullish
    _mtfPassShort: bool = not i_useMtfFilter or not _htfBullish

    _copStdev: float = ta.stdev(coppock, i_volatZeroLen)
    _noiseBand: float = _copStdev * i_volatZeroMult
    _volatZeroPass: bool = not i_useVolatZeroFilter or math.abs(coppock) > _noiseBand

    _riseStreak: PersistentSeries[int] = 0
    _fallStreak: PersistentSeries[int] = 0
    _risingRaw: bool = coppock > coppock[1]
    _fallingRaw: bool = coppock < coppock[1]
    if _risingRaw:
        _riseStreak += 1
        _fallStreak = 0
    elif _fallingRaw:
        _fallStreak += 1
        _riseStreak = 0
    else:
        _riseStreak = 0
        _fallStreak = 0
    _persistPassLong: bool = not i_usePersistFilter or _fallStreak[1] >= i_persistBars
    _persistPassShort: bool = not i_usePersistFilter or _riseStreak[1] >= i_persistBars

    coppockRising: bool = _risingRaw and _adxPass
    coppockFalling: bool = _fallingRaw and _adxPass

    bullCross: bool = ta.crossover(coppock, coppock[1]) and _adxPass and _divPassLong and _accelPassLong and _volPass and _mtfPassLong and _persistPassLong
    bearCross: bool = ta.crossunder(coppock, coppock[1]) and _adxPass and _divPassShort and _accelPassShort and _volPass and _mtfPassShort and _persistPassShort
    zeroCrossUp: bool = ta.crossover(coppock, 0) and _adxPass and _volatZeroPass
    zeroCrossDown: bool = ta.crossunder(coppock, 0) and _adxPass and _volatZeroPass

    coppockColor: Color = c_bull if coppockRising else c_bear if coppockFalling else c_neutral
    hColor: Color = (c_histBullStrong if _risingRaw else c_histBullWeak) if coppock >= 0 else c_histBearWeak if _risingRaw else c_histBearStrong
    bodyColor: Color = hColor
    borderColor: Color = bodyColor

    _atrVal: float = ta.atr(i_atrLen)
    _locked: bool = i_lockSignal and barstate.islast
    newLongSignal: bool = bullCross and (not _locked) and barstate.isconfirmed
    newShortSignal: bool = bearCross and (not _locked) and barstate.isconfirmed
    newSignal: bool = newLongSignal or newShortSignal

    _activeDir: Persistent[str] = na(str)
    entryPrice: Persistent[float] = na(float)
    slPrice: Persistent[float] = na(float)
    tp1Price: Persistent[float] = na(float)
    tp2Price: Persistent[float] = na(float)
    tp3Price: Persistent[float] = na(float)
    _sigBar: Persistent[int] = na(int)
    _tradeOpen: Persistent[bool] = False
    _slDone: Persistent[bool] = False
    _tp1Done: Persistent[bool] = False
    _tp2Done: Persistent[bool] = False
    _tp3Done: Persistent[bool] = False

    if newLongSignal:
        _activeDir = "long"
        _sigBar = bar_index
        _tradeOpen = True
        _slDone = False
        _tp1Done = False
        _tp2Done = False
        _tp3Done = False
        entryPrice = close
        slPrice = entryPrice - _atrVal * i_atrMult
        _riskLong: float = entryPrice - slPrice
        tp1Price = entryPrice + _riskLong * i_tp1R
        tp2Price = entryPrice + _riskLong * i_tp2R
        tp3Price = entryPrice + _riskLong * i_tp3R
    if newShortSignal:
        _activeDir = "short"
        _sigBar = bar_index
        _tradeOpen = True
        _slDone = False
        _tp1Done = False
        _tp2Done = False
        _tp3Done = False
        entryPrice = close
        slPrice = entryPrice + _atrVal * i_atrMult
        _riskShort: float = slPrice - entryPrice
        tp1Price = entryPrice - _riskShort * i_tp1R
        tp2Price = entryPrice - _riskShort * i_tp2R
        tp3Price = entryPrice - _riskShort * i_tp3R

    _levelsLive: bool = _tradeOpen and (not na(_sigBar)) and (bar_index > _sigBar)

    _slHit: bool = _levelsLive and (not _slDone) and (_activeDir == 'long' and (not na(slPrice)) and (low <= slPrice) or (_activeDir == 'short' and (not na(slPrice)) and (high >= slPrice)))
    tp1Hit: bool = _levelsLive and (not _slDone) and (not _slHit) and (not _tp1Done) and (_activeDir == 'long' and (not na(tp1Price)) and (high >= tp1Price) or (_activeDir == 'short' and (not na(tp1Price)) and (low <= tp1Price)))
    tp2Hit: bool = _levelsLive and (not _slDone) and (not _slHit) and (not _tp2Done) and (_activeDir == 'long' and (not na(tp2Price)) and (high >= tp2Price) or (_activeDir == 'short' and (not na(tp2Price)) and (low <= tp2Price)))
    tp3Hit: bool = _levelsLive and (not _slDone) and (not _slHit) and (not _tp3Done) and (_activeDir == 'long' and (not na(tp3Price)) and (high >= tp3Price) or (_activeDir == 'short' and (not na(tp3Price)) and (low <= tp3Price)))

    if _slHit:
        _slDone = True
        _tradeOpen = False
    if tp1Hit:
        _tp1Done = True
    if tp2Hit:
        _tp2Done = True
    if tp3Hit:
        _tp3Done = True

    def f_pct(_from: float, _to: float, _isLong: bool):
        return (_to - _from) / _from * 100 if _isLong else (_from - _to) / _from * 100

    slPct: float = f_pct(entryPrice, slPrice, _activeDir == 'long') if not na(entryPrice) and (not na(slPrice)) else na
    tp1Pct: float = f_pct(entryPrice, tp1Price, _activeDir == 'long') if not na(entryPrice) and (not na(tp1Price)) else na
    tp2Pct: float = f_pct(entryPrice, tp2Price, _activeDir == 'long') if not na(entryPrice) and (not na(tp2Price)) else na
    tp3Pct: float = f_pct(entryPrice, tp3Price, _activeDir == 'long') if not na(entryPrice) and (not na(tp3Price)) else na

    if newLongSignal and barstate.isconfirmed:
        _bullInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","value":"{3}","direction":"long","entry":"{4}","sl":"{5}","tp1":"{6}","tp2":"{7}","tp3":"{8}"', i_actionBull, syminfo.tickerid, timeframe.period, string.tostring(coppock, '#.####'), string.tostring(entryPrice, format.mintick), string.tostring(slPrice, format.mintick), string.tostring(tp1Price, format.mintick), string.tostring(tp2Price, format.mintick), string.tostring(tp3Price, format.mintick))
        alert('{' + _bullInner + '}', alert.freq_once_per_bar_close)
    if newShortSignal and barstate.isconfirmed:
        _bearInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","value":"{3}","direction":"short","entry":"{4}","sl":"{5}","tp1":"{6}","tp2":"{7}","tp3":"{8}"', i_actionBear, syminfo.tickerid, timeframe.period, string.tostring(coppock, '#.####'), string.tostring(entryPrice, format.mintick), string.tostring(slPrice, format.mintick), string.tostring(tp1Price, format.mintick), string.tostring(tp2Price, format.mintick), string.tostring(tp3Price, format.mintick))
        alert('{' + _bearInner + '}', alert.freq_once_per_bar_close)
    if newShortSignal and barstate.isconfirmed:
        _closeLongInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"long"', i_actionCloseLong, syminfo.tickerid, timeframe.period)
        alert('{' + _closeLongInner + '}', alert.freq_once_per_bar_close)
    if newLongSignal and barstate.isconfirmed:
        _closeShortInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"short"', i_actionCloseShort, syminfo.tickerid, timeframe.period)
        alert('{' + _closeShortInner + '}', alert.freq_once_per_bar_close)
    if zeroCrossUp and barstate.isconfirmed:
        _zeroUpInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","value":"{3}"', i_actionZeroUp, syminfo.tickerid, timeframe.period, string.tostring(coppock, '#.####'))
        alert('{' + _zeroUpInner + '}', alert.freq_once_per_bar_close)
    if zeroCrossDown and barstate.isconfirmed:
        _zeroDownInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","value":"{3}"', i_actionZeroDown, syminfo.tickerid, timeframe.period, string.tostring(coppock, '#.####'))
        alert('{' + _zeroDownInner + '}', alert.freq_once_per_bar_close)
    if tp1Hit:
        _tp1Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","level":"tp1","price":"{3}","pct":"{4}"', i_actionTp1, syminfo.tickerid, timeframe.period, string.tostring(tp1Price, format.mintick), string.tostring(tp1Pct, '#.##'))
        alert('{' + _tp1Inner + '}', alert.freq_once_per_bar)
    if tp2Hit:
        _tp2Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","level":"tp2","price":"{3}","pct":"{4}"', i_actionTp2, syminfo.tickerid, timeframe.period, string.tostring(tp2Price, format.mintick), string.tostring(tp2Pct, '#.##'))
        alert('{' + _tp2Inner + '}', alert.freq_once_per_bar)
    if tp3Hit:
        _tp3Inner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","level":"tp3","price":"{3}","pct":"{4}"', i_actionTp3, syminfo.tickerid, timeframe.period, string.tostring(tp3Price, format.mintick), string.tostring(tp3Pct, '#.##'))
        alert('{' + _tp3Inner + '}', alert.freq_once_per_bar)
    if _slHit:
        _slHitInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","price":"{3}","pct":"{4}"', i_actionSlHit, syminfo.tickerid, timeframe.period, string.tostring(slPrice, format.mintick), string.tostring(slPct, '#.##'))
        alert('{' + _slHitInner + '}', alert.freq_once_per_bar)

    alertcondition(newLongSignal and barstate.isconfirmed, 'Bull Cross', 'MarkitTick — Coppock Bull Cross')
    alertcondition(newShortSignal and barstate.isconfirmed, 'Bear Cross', 'MarkitTick — Coppock Bear Cross')
    alertcondition(newShortSignal and barstate.isconfirmed, 'Close Long Signal', 'MarkitTick — Close Long')
    alertcondition(newLongSignal and barstate.isconfirmed, 'Close Short Signal', 'MarkitTick — Close Short')
    alertcondition(zeroCrossUp and barstate.isconfirmed, 'Zero Cross Up', 'MarkitTick — Coppock Zero Cross Up')
    alertcondition(zeroCrossDown and barstate.isconfirmed, 'Zero Cross Down', 'MarkitTick — Coppock Zero Cross Down')
    alertcondition(tp1Hit, 'TP1 Hit', 'MarkitTick — TP1 Hit')
    alertcondition(tp2Hit, 'TP2 Hit', 'MarkitTick — TP2 Hit')
    alertcondition(tp3Hit, 'TP3 Hit', 'MarkitTick — TP3 Hit')
    alertcondition(_slHit, 'SL Hit', 'MarkitTick — SL Hit')

    plot(coppock, 'Coppock', color=coppockColor, linewidth=2, display=display.all - display.pane)
    plot(coppock if i_showHist else na, 'Histogram', color=hColor, style=plot.style_columns, histbase=0)
    hline(0, 'Zero Line', color=c_zeroLine, linestyle=hline.style_dashed)
    plotshape(coppock if i_showZeroX and zeroCrossUp else na, 'Zero Up', style=shape.triangleup, location=location.absolute, color=c_bull, size=size.tiny)
    plotshape(coppock if i_showZeroX and zeroCrossDown else na, 'Zero Down', style=shape.triangledown, location=location.absolute, color=c_bear, size=size.tiny)
    plotcandle(open, high, low, close, title='Heatmap Candles', color=bodyColor if i_showCandles else na, wickcolor=borderColor if i_showCandles else na, bordercolor=borderColor if i_showCandles else na, display=display.all if i_showCandles else display.none, force_overlay=True)

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

    if newSignal and (not _locked) and i_showLevels:
        f_deleteLevels()
        _x1: int = bar_index - 1
        _x2: int = bar_index + 10
        slLine = line.new(_x1, slPrice, _x2, slPrice, color=c_sl, style=line.style_solid, width=2, force_overlay=True)
        entryLine = line.new(_x1, entryPrice, _x2, entryPrice, color=c_entry, style=line.style_dashed, width=1, force_overlay=True)
        tp1Line = line.new(_x1, tp1Price, _x2, tp1Price, color=c_tp1, style=line.style_dashed, width=1, force_overlay=True)
        tp2Line = line.new(_x1, tp2Price, _x2, tp2Price, color=c_tp2, style=line.style_dashed, width=1, force_overlay=True)
        tp3Line = line.new(_x1, tp3Price, _x2, tp3Price, color=c_tp3, style=line.style_dashed, width=1, force_overlay=True)
        slLbl = label.new(_x2, slPrice, '✕ SL ' + string.tostring(slPrice, format.mintick), style=label.style_label_left, color=c_sl, textcolor=color.new('#FFFFFF'), size=size.small, force_overlay=True)
        entryLbl = label.new(_x2, entryPrice, '▶ Entry ' + string.tostring(entryPrice, format.mintick), style=label.style_label_left, color=c_entry, textcolor=color.new('#FFFFFF'), size=size.small, force_overlay=True)
        tp1Lbl = label.new(_x2, tp1Price, '◆ TP1 ' + string.tostring(tp1Price, format.mintick), style=label.style_label_left, color=c_tp1, textcolor=color.new('#FFFFFF'), size=size.small, force_overlay=True)
        tp2Lbl = label.new(_x2, tp2Price, '✦ TP2 ' + string.tostring(tp2Price, format.mintick), style=label.style_label_left, color=c_tp2, textcolor=color.new('#FFFFFF'), size=size.small, force_overlay=True)
        tp3Lbl = label.new(_x2, tp3Price, '◆ TP3 ' + string.tostring(tp3Price, format.mintick), style=label.style_label_left, color=c_tp3, textcolor=color.new('#FFFFFF'), size=size.small, force_overlay=True)
        riskFill = linefill.new(slLine, entryLine, c_riskFill)
        rewardFill = linefill.new(entryLine, tp3Line, c_rewardFill)

    if not na(slLine) and barstate.islast:
        _extX: int = bar_index + 10 if i_lockSignal else last_bar_index + 10
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

    if not na(slLbl):
        if tp1Hit:
            label.set_text(tp1Lbl, '◆ TP1 ✓ HIT ' + ('+' if tp1Pct >= 0 else '') + string.tostring(tp1Pct, '#.##') + '%')
        if tp2Hit:
            label.set_text(tp2Lbl, '✦ TP2 ✓ HIT ' + ('+' if tp2Pct >= 0 else '') + string.tostring(tp2Pct, '#.##') + '%')
        if tp3Hit:
            label.set_text(tp3Lbl, '◆ TP3 ✓ HIT ' + ('+' if tp3Pct >= 0 else '') + string.tostring(tp3Pct, '#.##') + '%')
        if _slHit:
            label.set_text(slLbl, '✕ SL ✓ HIT ' + string.tostring(slPct, '#.##') + '%')

    dash: Persistent[Table] = table.new(i_dashPos, 2, 14, border_width=1, border_color=color.new(color.new('#2A3040'), 40), frame_width=1, frame_color=color.new(color.new('#3A2A6D'), 40), force_overlay=True)

    if i_showDash and barstate.islast:
        row_a: Color = C_DASH_BG
        row_b: Color = color.new(C_DASH_BG, 40)
        lbl_col: Color = color.new(C_DASH_TXT, 25)
        valColor: Color = C_SUP if coppockRising else C_RES if coppockFalling else C_DASH_TXT
        biasTxt: str = 'BULLISH' if coppockRising else 'BEARISH' if coppockFalling else 'NEUTRAL'

        table.cell(dash, 0, 0, 'Coppock Curve', text_color=C_DASH_TXT, text_size=size.small, bgcolor=C_DASH_HDR, text_halign=text.align_left)
        table.cell(dash, 1, 0, syminfo.ticker + '  ·  ' + timeframe.period, text_color=C_DASH_TXT, text_size=size.small, bgcolor=C_DASH_HDR, text_halign=text.align_right)

        table.cell(dash, 0, 1, '  Lock', text_color=lbl_col, text_size=size.small, bgcolor=row_a, text_halign=text.align_left)
        table.cell(dash, 1, 1, ('ACTIVE' if i_lockSignal else 'OFF') + '  ', text_color=C_RES if i_lockSignal else C_DASH_TXT, text_size=size.small, bgcolor=row_a, text_halign=text.align_right)

        table.cell(dash, 0, 2, '  Value', text_color=lbl_col, text_size=size.small, bgcolor=row_b, text_halign=text.align_left)
        table.cell(dash, 1, 2, string.tostring(coppock, '#.####') + '  ', text_color=valColor, text_size=size.small, bgcolor=row_b, text_halign=text.align_right)

        table.cell(dash, 0, 3, '  Bias', text_color=lbl_col, text_size=size.small, bgcolor=row_a, text_halign=text.align_left)
        table.cell(dash, 1, 3, biasTxt + '  ', text_color=valColor, text_size=size.small, bgcolor=row_a, text_halign=text.align_right)

        table.cell(dash, 0, 4, '  Long ROC', text_color=lbl_col, text_size=size.small, bgcolor=row_b, text_halign=text.align_left)
        table.cell(dash, 1, 4, string.tostring(_rocLongVal, '#.##') + '  ', text_color=C_DASH_TXT, text_size=size.small, bgcolor=row_b, text_halign=text.align_right)

        table.cell(dash, 0, 5, '  Short ROC', text_color=lbl_col, text_size=size.small, bgcolor=row_a, text_halign=text.align_left)
        table.cell(dash, 1, 5, string.tostring(_rocShortVal, '#.##') + '  ', text_color=C_DASH_TXT, text_size=size.small, bgcolor=row_a, text_halign=text.align_right)

        table.cell(dash, 0, 6, '  Zero Cross', text_color=lbl_col, text_size=size.small, bgcolor=row_b, text_halign=text.align_left)
        table.cell(dash, 1, 6, ('ABOVE' if coppock >= 0 else 'BELOW') + '  ', text_color=C_SUP if coppock >= 0 else C_RES, text_size=size.small, bgcolor=row_b, text_halign=text.align_right)

        _row: int = 7
        if i_showLevels:
            table.cell(dash, 0, _row, '  Entry', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, (string.tostring(entryPrice, format.mintick) if not na(entryPrice) else '—') + '  ', text_color=C_DASH_TXT, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1
            table.cell(dash, 0, _row, '  SL', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, (string.tostring(slPrice, format.mintick) if not na(slPrice) else '—') + '  ', text_color=C_RES, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1
            table.cell(dash, 0, _row, '  TP1', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, (string.tostring(tp1Price, format.mintick) if not na(tp1Price) else '—') + '  ', text_color=C_SUP, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1
            table.cell(dash, 0, _row, '  TP2', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, (string.tostring(tp2Price, format.mintick) if not na(tp2Price) else '—') + '  ', text_color=C_SUP, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1
            table.cell(dash, 0, _row, '  TP3', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, (string.tostring(tp3Price, format.mintick) if not na(tp3Price) else '—') + '  ', text_color=C_SUP, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1

        if i_useAdxFilter:
            table.cell(dash, 0, _row, '  ADX', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, string.tostring(_adxVal, '#.##') + '  ', text_color=C_SUP if _adxPass else C_RES, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)
            _row += 1

        if i_adaptFilterType != 'None':
            table.cell(dash, 0, _row, '  Adapt Filter', text_color=lbl_col, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_left)
            table.cell(dash, 1, _row, i_adaptFilterType + '  ', text_color=C_DASH_TXT, text_size=size.small, bgcolor=row_a if _row % 2 == 1 else row_b, text_halign=text.align_right)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
