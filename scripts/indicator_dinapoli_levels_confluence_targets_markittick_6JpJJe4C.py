"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, close,
    color, font, format, high, input, label, last_bar_index, line, low, math, na, plot, position,
    request, script, size, string, syminfo, ta, table, text, timeframe, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series, Table

GRP_CORE: str = "⚙️ Core"
GRP_FILT: str = "🕯️ Filters"
GRP_TRADE: str = "📐 Trade Tools"
GRP_VIS: str = "🎨 Visuals"
GRP_DASH: str = "📊 Dashboard"
GRP_WH: str = "🔔 Alerts"
GRP_COL: str = "🌈 Colors"


@script.indicator(title="DiNapoli Levels Confluence Targets [MarkitTick]", overlay=True, max_bars_back=300, max_lines_count=20, max_labels_count=500)
def main(
    i_pvtLeft=input.int(5, "Pivot Left", minval=1, maxval=50, group=GRP_CORE),
    i_pvtRight=input.int(5, "Pivot Right", minval=1, maxval=50, group=GRP_CORE),
    i_minSwing=input.float(1.0, "Min Swing × ATR", minval=0.0, step=0.1, group=GRP_CORE),
    i_maxRetr=input.float(0.9, "Max Retrace", minval=0.4, maxval=1.0, step=0.01, group=GRP_CORE),
    i_atrLen=input.int(14, "ATR Len", minval=1, group=GRP_CORE),
    i_useDma=input.bool(True, "DMA Filter", group=GRP_FILT),
    i_dmaLen=input.int(3, "DMA Len", minval=1, maxval=50, group=GRP_FILT),
    i_dmaDisp=input.int(3, "DMA Displace", minval=0, maxval=50, group=GRP_FILT),
    i_useConf=input.bool(False, "Confluence Required", group=GRP_FILT),
    i_confTol=input.float(0.25, "Confluence Tol × ATR", minval=0.01, step=0.05, group=GRP_FILT),
    i_useSmooth=input.bool(False, "Adaptive Smoothing", group=GRP_FILT),
    i_smoothMethod=input.string("EMA", "Smoothing Method", options=("SMA", "EMA", "RMA", "WMA", "VWMA"), group=GRP_FILT),
    i_smoothLen=input.int(3, "Smoothing Len", minval=1, maxval=100, group=GRP_FILT),
    i_useAdx=input.bool(False, "ADX Filter", group=GRP_FILT),
    i_adxLen=input.int(14, "ADX DI Len", minval=1, maxval=100, group=GRP_FILT),
    i_adxSmth=input.int(14, "ADX Smoothing", minval=1, maxval=100, group=GRP_FILT),
    i_adxMin=input.float(20.0, "ADX Min", minval=0.0, maxval=100.0, step=1.0, group=GRP_FILT),
    i_useHtf=input.bool(False, "HTF Confirmation", group=GRP_FILT),
    i_htfTf=input.timeframe("240", "HTF Timeframe", group=GRP_FILT),
    i_lockSignal=input.bool(False, "🔒 Lock Signal", tooltip="Freeze current signal · block new ones", group=GRP_TRADE),
    i_slAtr=input.float(0.5, "Stop Buffer × ATR", minval=0.0, step=0.1, group=GRP_TRADE),
    i_showNodes=input.bool(True, "Fibnodes", group=GRP_VIS),
    i_showConf=input.bool(True, "Confluence Line", group=GRP_VIS),
    i_showMarkers=input.bool(True, "Signal Markers", group=GRP_VIS),
    i_showDma=input.bool(True, "DMA Line", group=GRP_VIS),
    i_showDash=input.bool(True, "Show Dashboard", group=GRP_DASH),
    i_dashPos=input.string("Top Right", "Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=GRP_DASH),
    i_actionLong=input.string("long", "↑ Long Action", group=GRP_WH),
    i_actionShort=input.string("short", "↓ Short Action", group=GRP_WH),
    i_actionCloseLong=input.string("closelong", "✕ Close Long Action", group=GRP_WH),
    i_actionCloseShort=input.string("closeshort", "✕ Close Short Action", group=GRP_WH),
    i_actionCop=input.string("tp1", "◆ COP Action", group=GRP_WH),
    i_actionOp=input.string("tp2", "✦ OP Action", group=GRP_WH),
    i_actionXop=input.string("tp3", "◆ XOP Action", group=GRP_WH),
    i_actionStop=input.string("stop", "✕ Stop Action", group=GRP_WH),
    C_SUP=input.color(color.new('#26A69A'), "Bull", group=GRP_COL),
    C_RES=input.color(color.new('#EF5350'), "Bear", group=GRP_COL),
    C_SL=input.color(color.new('#EF5350'), "SL", group=GRP_COL),
    C_ENTRY=input.color(color.new('#2196F3'), "Entry", group=GRP_COL),
    C_TP1=input.color(color.new(color.new('#26A69A'), 40), "COP", group=GRP_COL),
    C_TP2=input.color(color.new(color.new('#26A69A'), 20), "OP", group=GRP_COL),
    C_TP3=input.color(color.new(color.new('#26A69A'), 0), "XOP", group=GRP_COL),
    C_N382=input.color(color.new('#F9A825'), "Node 38.2", group=GRP_COL),
    C_N618=input.color(color.new('#FB8C00'), "Node 61.8", group=GRP_COL),
    C_CONF=input.color(color.new('#AB47BC'), "Confluence", group=GRP_COL),
    C_DMA=input.color(color.new('#7E57C2'), "DMA", group=GRP_COL),
    C_LBLTXT=input.color(color.new('#FFFFFF'), "Label Text", group=GRP_COL),
    C_BAR_HI=input.color(color.new('#26A69A'), "Bar High", group=GRP_COL),
    C_BAR_MID=input.color(color.new('#F9A825'), "Bar Mid", group=GRP_COL),
    C_BAR_LO=input.color(color.new('#EF5350'), "Bar Low", group=GRP_COL),
    C_DASH_HDR=input.color(color.new(color.new('#3A2A6D'), 55), "Dash Header", group=GRP_COL),
    C_DASH_BG=input.color(color.new(color.new('#0A0F1A'), 10), "Dash BG", group=GRP_COL),
    C_DASH_TXT=input.color(color.new('#FFFFFF'), "Dash Text", group=GRP_COL)
):
    def f_pivotHigh(lb: int, rb: int):
        _res: float = NA(float)
        if bar_index >= lb + rb:
            _p: float = high[rb]
            _ok: bool = True
            for i in pine_range(1, lb):
                if high[rb + i] >= _p:
                    _ok = False
                    break
            if _ok:
                for i in pine_range(1, rb):
                    if high[rb - i] > _p:
                        _ok = False
                        break
            if _ok:
                _res = _p
        return _res

    def f_pivotLow(lb: int, rb: int):
        _res: float = NA(float)
        if bar_index >= lb + rb:
            _p: float = low[rb]
            _ok: bool = True
            for i in pine_range(1, lb):
                if low[rb + i] <= _p:
                    _ok = False
                    break
            if _ok:
                for i in pine_range(1, rb):
                    if low[rb - i] < _p:
                        _ok = False
                        break
            if _ok:
                _res = _p
        return _res

    def f_pctTxt(lvl: float, ent: float, dirLong: bool):
        _p: float = (lvl - ent if dirLong else ent - lvl) / ent * 100
        return ('+' if _p >= 0 else '') + string.tostring(_p, '#.00') + '%'

    def f_smooth(method__ren__: str, src: float, len: int):
        _sma: float = ta.sma(src, len)
        _ema: float = ta.ema(src, len)
        _rma: float = ta.rma(src, len)
        _wma: float = ta.wma(src, len)
        _vwma: float = ta.vwma(src, len)
        __block_result__ = na
        __switch__ = method__ren__
        if __switch__ == "SMA":
            __block_result__ = _sma
        elif __switch__ == "EMA":
            __block_result__ = _ema
        elif __switch__ == "RMA":
            __block_result__ = _rma
        elif __switch__ == "WMA":
            __block_result__ = _wma
        elif __switch__ == "VWMA":
            __block_result__ = _vwma
        else:
            __block_result__ = _ema
        _res: float = __block_result__
        return _res

    _atr: float = ta.atr(i_atrLen)
    _dma: Series[float] = ta.sma(close, i_dmaLen)
    _dmaRef: float = _dma[i_dmaDisp]
    _smoothed: float = f_smooth(i_smoothMethod, close, i_smoothLen)

    _diPlus, _diMinus, _adx = ta.dmi(i_adxLen, i_adxSmth)

    _adxOk: bool = not i_useAdx or _adx >= i_adxMin

    _htfClose: float = request.security(syminfo.tickerid, i_htfTf, close[1], lookahead=barmerge.lookahead_on)

    _pvPrice: Persistent[list[float]] = array.new_float(0)
    _pvBar: Persistent[list[int]] = array.new_int(0)
    _pvHigh: Persistent[list[bool]] = array.new_bool(0)

    _ph: float = f_pivotHigh(i_pvtLeft, i_pvtRight)
    _pl: float = f_pivotLow(i_pvtLeft, i_pvtRight)

    if not na(_ph):
        _sameSide: bool = False
        if array.size(_pvHigh) > 0:
            _sameSide = array.get(_pvHigh, 0)
        if _sameSide:
            if _ph > array.get(_pvPrice, 0):
                array.set(_pvPrice, 0, _ph)
                array.set(_pvBar, 0, bar_index - i_pvtRight)
        else:
            array.unshift(_pvPrice, _ph)
            array.unshift(_pvBar, bar_index - i_pvtRight)
            array.unshift(_pvHigh, True)

    if not na(_pl):
        _sameSideLow: bool = False
        if array.size(_pvHigh) > 0:
            _sameSideLow = not array.get(_pvHigh, 0)
        if _sameSideLow:
            if _pl < array.get(_pvPrice, 0):
                array.set(_pvPrice, 0, _pl)
                array.set(_pvBar, 0, bar_index - i_pvtRight)
        else:
            array.unshift(_pvPrice, _pl)
            array.unshift(_pvBar, bar_index - i_pvtRight)
            array.unshift(_pvHigh, False)

    if array.size(_pvPrice) > 8:
        array.pop(_pvPrice)
        array.pop(_pvBar)
        array.pop(_pvHigh)

    _pvN: int = array.size(_pvPrice)
    _pxC: float = NA(float)
    _pxB: float = NA(float)
    _pxA: float = NA(float)
    _pxA2: float = NA(float)
    _barC: int = NA(int)
    _hiC: bool = False
    _hiB: bool = False
    _hiA: bool = False

    if _pvN >= 3:
        _pxC = array.get(_pvPrice, 0)
        _pxB = array.get(_pvPrice, 1)
        _pxA = array.get(_pvPrice, 2)
        _barC = array.get(_pvBar, 0)
        _hiC = array.get(_pvHigh, 0)
        _hiB = array.get(_pvHigh, 1)
        _hiA = array.get(_pvHigh, 2)

    if _pvN >= 5:
        _pxA2 = array.get(_pvPrice, 4)

    _isBull: bool = not na(_pxC) and (not _hiC) and _hiB and (not _hiA)
    _isBear: bool = not na(_pxC) and _hiC and (not _hiB) and _hiA
    _swing: float = _pxB - _pxA
    _retr: float = NA(float)

    if (_isBull or _isBear) and _swing != 0:
        _retr = (_pxB - _pxC) / _swing

    _n382: float = _pxB - 0.382 * _swing
    _n618: float = _pxB - 0.618 * _swing
    _entry: float = NA(float)

    if not na(_retr):
        _entry = _n618 if _retr >= 0.618 else _n382

    _stop: float = _pxC - _atr * i_slAtr if _isBull else _pxC + _atr * i_slAtr
    _cop: float = _pxC + 0.618 * _swing
    _op: float = _pxC + _swing
    _xop: float = _pxC + 1.618 * _swing

    _swing2: float = _pxB - _pxA2
    _m382: float = _pxB - 0.382 * _swing2
    _m618: float = _pxB - 0.618 * _swing2
    _confPx: float = NA(float)
    _confIs618: bool = False

    if not na(_pxA2) and (not na(_n382)) and (not na(_atr)) and (_swing2 > 0 if _isBull else _swing2 < 0):
        _d1: float = math.abs(_n382 - _m382)
        _d2: float = math.abs(_n382 - _m618)
        _d3: float = math.abs(_n618 - _m382)
        _d4: float = math.abs(_n618 - _m618)
        _best: float = math.min(_d1, _d2, _d3, _d4)
        if _best <= _atr * i_confTol:
            if _best == _d1:
                _confPx = (_n382 + _m382) / 2
            elif _best == _d2:
                _confPx = (_n382 + _m618) / 2
            elif _best == _d3:
                _confPx = (_n618 + _m382) / 2
                _confIs618 = True
            else:
                _confPx = (_n618 + _m618) / 2
                _confIs618 = True

    _smoothOk: bool = not i_useSmooth or (close > _smoothed if _isBull else close < _smoothed)
    _htfOk: bool = not i_useHtf or na(_htfClose) or (close > _htfClose if _isBull else close < _htfClose)
    _trendOk: bool = (not i_useDma or (close > _dmaRef if _isBull else close < _dmaRef)) and _smoothOk and _adxOk and _htfOk
    _setupValid: bool = (_isBull or _isBear) and (not na(_retr)) and (not na(_barC)) and (_retr >= 0.382) and (_retr <= i_maxRetr) and (math.abs(_swing) >= _atr * i_minSwing) and (_swing > 0 if _isBull else _swing < 0) and _trendOk and (not i_useConf or not na(_confPx))

    slLine: Persistent[Line] = na(Line)
    entryLine: Persistent[Line] = na(Line)
    tp1Line: Persistent[Line] = na(Line)
    tp2Line: Persistent[Line] = na(Line)
    tp3Line: Persistent[Line] = na(Line)
    n382Line: Persistent[Line] = na(Line)
    n618Line: Persistent[Line] = na(Line)
    confLine: Persistent[Line] = na(Line)
    slLbl: Persistent[Label] = na(Label)
    entryLbl: Persistent[Label] = na(Label)
    tp1Lbl: Persistent[Label] = na(Label)
    tp2Lbl: Persistent[Label] = na(Label)
    tp3Lbl: Persistent[Label] = na(Label)
    n382Lbl: Persistent[Label] = na(Label)
    n618Lbl: Persistent[Label] = na(Label)
    confLbl: Persistent[Label] = na(Label)

    isLong: Persistent[bool] = False
    entryPrice: Persistent[float] = NA(float)
    slPrice: Persistent[float] = NA(float)
    tp1Price: Persistent[float] = NA(float)
    tp2Price: Persistent[float] = NA(float)
    tp3Price: Persistent[float] = NA(float)
    node382: Persistent[float] = NA(float)
    node618: Persistent[float] = NA(float)
    confPrice: Persistent[float] = NA(float)
    confIs618: Persistent[bool] = False
    swingSize: Persistent[float] = NA(float)
    nodeRetr: Persistent[float] = NA(float)
    nodeIs618: Persistent[bool] = False
    signalBar: Persistent[int] = NA(int)
    tp1Hit: Persistent[bool] = False
    tp2Hit: Persistent[bool] = False
    tp3Hit: Persistent[bool] = False
    slHit: Persistent[bool] = False
    _closeBar: Persistent[int] = NA(int)
    _lastSetupBar: Persistent[int] = NA(int)
    lvPx: Persistent[list[float]] = array.new_float(7, na)
    lvName: Persistent[list[str]] = array.new_string(7, '')
    lvHit: Persistent[list[str]] = array.new_string(7, '')
    lvHost: Persistent[list[int]] = array.new_int(7, -1)

    def f_hostOf(_i: int):
        _h: int = _i
        if _i > 0:
            for j in pine_range(0, _i - 1):
                if array.get(lvHost, j) == j and array.get(lvPx, j) == array.get(lvPx, _i):
                    _h = j
                    break
        return _h

    def f_lvText(_host: int):
        _hPx: float = array.get(lvPx, _host)
        _last: int = -1
        for i in pine_range(0, 6):
            if array.get(lvHost, i) == _host and array.get(lvHit, i) == '' and (array.get(lvPx, i) == _hPx):
                _last = i
        _out: str = ""
        for i in pine_range(0, 6):
            if array.get(lvHost, i) == _host:
                _px: float = array.get(lvPx, i)
                _hit: str = array.get(lvHit, i)
                _atHst: bool = _px == _hPx
                _piece: str = _hit if _hit != '' else array.get(lvName, i) + ' ' + string.tostring(_px, format.mintick) if not _atHst else array.get(lvName, i) + ' ' + string.tostring(_hPx, format.mintick) if i == _last else array.get(lvName, i)
                _out = _piece if _out == '' else _out + ' · ' + _piece
        return _out

    _tp1Cross: bool = high >= tp1Price if isLong else low <= tp1Price
    _tp2Cross: bool = high >= tp2Price if isLong else low <= tp2Price
    _tp3Cross: bool = high >= tp3Price if isLong else low <= tp3Price
    _slCross: bool = low <= slPrice if isLong else high >= slPrice
    _slFire: bool = _slCross and (not slHit) and (not tp3Hit)
    _tp1Fire: bool = _tp1Cross and (not tp1Hit) and (not slHit) and (not _slFire)
    _tp2Fire: bool = _tp2Cross and (not tp2Hit) and (not slHit) and (not _slFire)
    _tp3Fire: bool = _tp3Cross and (not tp3Hit) and (not slHit) and (not _slFire)

    if not na(slLbl) and (not slHit) and (not tp3Hit) and _slCross:
        slHit = True
        array.set(lvHit, 0, 'SL ✓ HIT ' + f_pctTxt(slPrice, entryPrice, isLong))
        label.set_text(slLbl, f_lvText(array.get(lvHost, 0)))
        label.set_color(slLbl, color.new(C_SL, 0))

    if not na(tp1Lbl) and (not tp1Hit) and (not slHit) and _tp1Cross:
        tp1Hit = True
        array.set(lvHit, 2, 'COP ✓ HIT ' + f_pctTxt(tp1Price, entryPrice, isLong))
        label.set_text(tp1Lbl, f_lvText(array.get(lvHost, 2)))
        if array.get(lvHost, 2) == 2:
            label.set_color(tp1Lbl, color.new(C_TP1, 0))

    if not na(tp2Lbl) and (not tp2Hit) and (not slHit) and _tp2Cross:
        tp2Hit = True
        array.set(lvHit, 3, 'OP ✓ HIT ' + f_pctTxt(tp2Price, entryPrice, isLong))
        label.set_text(tp2Lbl, f_lvText(array.get(lvHost, 3)))
        if array.get(lvHost, 3) == 3:
            label.set_color(tp2Lbl, color.new(C_TP2, 0))

    if not na(tp3Lbl) and (not tp3Hit) and (not slHit) and _tp3Cross:
        tp3Hit = True
        array.set(lvHit, 4, 'XOP ✓ HIT ' + f_pctTxt(tp3Price, entryPrice, isLong))
        label.set_text(tp3Lbl, f_lvText(array.get(lvHost, 4)))
        if array.get(lvHost, 4) == 4:
            label.set_color(tp3Lbl, color.new(C_TP3, 0))

    _tradeClosed: bool = slHit or tp3Hit

    if not na(slLine) and _tradeClosed and na(_closeBar):
        _closeBar = bar_index

    _preOpen: bool = not na(slLine) and (not _tradeClosed)
    _preLong: bool = isLong
    _preSl: float = slPrice
    _preTp1: float = tp1Price
    _preTp2: float = tp2Price
    _preTp3: float = tp3Price

    _locked: bool = i_lockSignal and barstate.islast
    _newSignal: bool = _setupValid and barstate.isconfirmed and (na(_lastSetupBar) or _barC != _lastSetupBar)
    _fire: bool = _newSignal and (not _locked)

    if _fire:
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        slHit = False
        _closeBar = NA(int)
        isLong = _isBull
        entryPrice = _entry
        slPrice = _stop
        tp1Price = _cop
        tp2Price = _op
        tp3Price = _xop
        node382 = _n382
        node618 = _n618
        confPrice = _confPx
        confIs618 = _confIs618
        swingSize = _swing
        nodeRetr = _retr
        nodeIs618 = _retr >= 0.618
        signalBar = bar_index
        _lastSetupBar = _barC

    longSignal: bool = _fire and _isBull
    shortSignal: bool = _fire and _isBear

    if longSignal and barstate.isconfirmed:
        _nodeTxt: str = '61.8' if nodeIs618 else '38.2'
        _confTxt: str = 'no' if na(confPrice) else 'yes'
        _retrTxt: str = string.tostring(nodeRetr * 100, '#.0')
        _tp3Txt: str = string.tostring(tp3Price, format.mintick)
        _longInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"long","entry":"{3}","sl":"{4}","tp":"{5}","cop":"{6}","op":"{7}","xop":"{8}","node":"{9}","retrace":"{10}","confluence":"{11}"', i_actionLong, syminfo.tickerid, timeframe.period, string.tostring(entryPrice, format.mintick), string.tostring(slPrice, format.mintick), _tp3Txt, string.tostring(tp1Price, format.mintick), string.tostring(tp2Price, format.mintick), _tp3Txt, _nodeTxt, _retrTxt, _confTxt)
        longPayload: str = '{' + _longInner + '}'
        alert(longPayload, alert.freq_once_per_bar_close)
        if _preOpen and (not _preLong):
            _closeShortInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"short"', i_actionCloseShort, syminfo.tickerid, timeframe.period)
            closeShortPayload: str = '{' + _closeShortInner + '}'
            alert(closeShortPayload, alert.freq_once_per_bar_close)

    if shortSignal and barstate.isconfirmed:
        _nodeTxt: str = '61.8' if nodeIs618 else '38.2'
        _confTxt: str = 'no' if na(confPrice) else 'yes'
        _retrTxt: str = string.tostring(nodeRetr * 100, '#.0')
        _tp3Txt: str = string.tostring(tp3Price, format.mintick)
        _shortInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"short","entry":"{3}","sl":"{4}","tp":"{5}","cop":"{6}","op":"{7}","xop":"{8}","node":"{9}","retrace":"{10}","confluence":"{11}"', i_actionShort, syminfo.tickerid, timeframe.period, string.tostring(entryPrice, format.mintick), string.tostring(slPrice, format.mintick), _tp3Txt, string.tostring(tp1Price, format.mintick), string.tostring(tp2Price, format.mintick), _tp3Txt, _nodeTxt, _retrTxt, _confTxt)
        shortPayload: str = '{' + _shortInner + '}'
        alert(shortPayload, alert.freq_once_per_bar_close)
        if _preOpen and _preLong:
            _closeLongInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"long"', i_actionCloseLong, syminfo.tickerid, timeframe.period)
            closeLongPayload: str = '{' + _closeLongInner + '}'
            alert(closeLongPayload, alert.freq_once_per_bar_close)

    if _tp1Fire:
        _copInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","level":"COP","price":"{4}"', i_actionCop, syminfo.tickerid, timeframe.period, 'long' if _preLong else 'short', string.tostring(_preTp1, format.mintick))
        copPayload: str = '{' + _copInner + '}'
        alert(copPayload, alert.freq_once_per_bar)

    if _tp2Fire:
        _opInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","level":"OP","price":"{4}"', i_actionOp, syminfo.tickerid, timeframe.period, 'long' if _preLong else 'short', string.tostring(_preTp2, format.mintick))
        opPayload: str = '{' + _opInner + '}'
        alert(opPayload, alert.freq_once_per_bar)

    if _tp3Fire:
        _xopInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","level":"XOP","price":"{4}"', i_actionXop, syminfo.tickerid, timeframe.period, 'long' if _preLong else 'short', string.tostring(_preTp3, format.mintick))
        xopPayload: str = '{' + _xopInner + '}'
        alert(xopPayload, alert.freq_once_per_bar)

    if _slFire:
        _stopInner: str = string.format('"action":"{0}","ticker":"{1}","tf":"{2}","direction":"{3}","level":"SL","price":"{4}"', i_actionStop, syminfo.tickerid, timeframe.period, 'long' if _preLong else 'short', string.tostring(_preSl, format.mintick))
        stopPayload: str = '{' + _stopInner + '}'
        alert(stopPayload, alert.freq_once_per_bar)

    alertcondition(longSignal and barstate.isconfirmed, 'BUY Signal', 'MarkitTick — DiNapoli BUY Signal Fired')
    alertcondition(shortSignal and barstate.isconfirmed, 'SELL Signal', 'MarkitTick — DiNapoli SELL Signal Fired')
    alertcondition(shortSignal and barstate.isconfirmed and _preOpen and _preLong, 'Close Long Signal', 'MarkitTick — Close Long')
    alertcondition(longSignal and barstate.isconfirmed and _preOpen and (not _preLong), 'Close Short Signal', 'MarkitTick — Close Short')
    alertcondition(_tp1Fire, 'COP Reached', 'MarkitTick — COP Objective Reached')
    alertcondition(_tp2Fire, 'OP Reached', 'MarkitTick — OP Objective Reached')
    alertcondition(_tp3Fire, 'XOP Reached', 'MarkitTick — XOP Objective Reached')
    alertcondition(_slFire, 'Stop Hit', 'MarkitTick — Stop Hit')

    def f_deleteLevels():
        line.delete(slLine)
        line.delete(entryLine)
        line.delete(tp1Line)
        line.delete(tp2Line)
        line.delete(tp3Line)
        line.delete(n382Line)
        line.delete(n618Line)
        line.delete(confLine)
        label.delete(slLbl)
        label.delete(entryLbl)
        label.delete(tp1Lbl)
        label.delete(tp2Lbl)
        label.delete(tp3Lbl)
        label.delete(n382Lbl)
        label.delete(n618Lbl)
        return label.delete(confLbl)

    if _fire:
        f_deleteLevels()
        n382Line = na
        n618Line = na
        confLine = na
        n382Lbl = na
        n618Lbl = na
        confLbl = na
        _x1: int = bar_index
        _x2: int = bar_index + 10
        slLine = line.new(_x1, slPrice, _x2, slPrice, color=C_SL, style=line.style_solid, width=2)
        entryLine = line.new(_x1, entryPrice, _x2, entryPrice, color=C_ENTRY, style=line.style_dashed, width=1)
        tp1Line = line.new(_x1, tp1Price, _x2, tp1Price, color=C_TP1, style=line.style_dashed, width=1)
        tp2Line = line.new(_x1, tp2Price, _x2, tp2Price, color=C_TP2, style=line.style_dashed, width=1)
        tp3Line = line.new(_x1, tp3Price, _x2, tp3Price, color=C_TP3, style=line.style_dashed, width=1)
        if i_showNodes:
            if nodeIs618:
                n382Line = line.new(_x1, node382, _x2, node382, color=C_N382, style=line.style_dotted, width=1)
            else:
                n618Line = line.new(_x1, node618, _x2, node618, color=C_N618, style=line.style_dotted, width=1)
        if i_showConf and (not na(confPrice)):
            confLine = line.new(_x1, confPrice, _x2, confPrice, color=C_CONF, style=line.style_dashed, width=2)
        array.fill(lvHost, -1)
        array.fill(lvHit, '')
        array.set(lvPx, 0, slPrice)
        array.set(lvPx, 1, entryPrice)
        array.set(lvPx, 2, tp1Price)
        array.set(lvPx, 3, tp2Price)
        array.set(lvPx, 4, tp3Price)
        array.set(lvPx, 5, (node382 if nodeIs618 else node618) if i_showNodes else NA(float))
        array.set(lvPx, 6, confPrice if i_showConf else NA(float))
        array.set(lvName, 0, '✕ SL')
        array.set(lvName, 1, '▶ Entry ' + ('F 61.8' if nodeIs618 else 'F 38.2'))
        array.set(lvName, 2, '◆ COP')
        array.set(lvName, 3, '✦ OP')
        array.set(lvName, 4, '◆ XOP')
        array.set(lvName, 5, 'F 38.2' if nodeIs618 else 'F 61.8')
        array.set(lvName, 6, '◈ Conf')
        for i in pine_range(0, 5):
            if not na(array.get(lvPx, i)):
                array.set(lvHost, i, f_hostOf(i))
        if not na(array.get(lvPx, 6)):
            _src: int = 1 if confIs618 == nodeIs618 else 5
            array.set(lvHost, 6, array.get(lvHost, _src) if not na(array.get(lvPx, _src)) else f_hostOf(6))
        _lvCol: list[Color] = array.from_items(C_SL, C_ENTRY, C_TP1, C_TP2, C_TP3, C_N382 if nodeIs618 else C_N618, C_CONF)
        _lvLbl: list[Label] = array.new_label(7, na)
        for i in pine_range(0, 6):
            if array.get(lvHost, i) == i:
                array.set(_lvLbl, i, label.new(_x2, array.get(lvPx, i), f_lvText(i), style=label.style_label_left, color=array.get(_lvCol, i), textcolor=C_LBLTXT, size=size.small))
        for i in pine_range(0, 6):
            _h: int = array.get(lvHost, i)
            if _h >= 0 and _h != i:
                array.set(_lvLbl, i, array.get(_lvLbl, _h))
        slLbl = array.get(_lvLbl, 0)
        entryLbl = array.get(_lvLbl, 1)
        tp1Lbl = array.get(_lvLbl, 2)
        tp2Lbl = array.get(_lvLbl, 3)
        tp3Lbl = array.get(_lvLbl, 4)
        if nodeIs618:
            n382Lbl = array.get(_lvLbl, 5)
        else:
            n618Lbl = array.get(_lvLbl, 5)
        confLbl = array.get(_lvLbl, 6)
        if i_showMarkers:
            label.new(bar_index, low if isLong else high, 'BULL' if isLong else 'BEAR', yloc=yloc.belowbar if isLong else yloc.abovebar, style=label.style_label_up if isLong else label.style_label_down, color=C_SUP if isLong else C_RES, textcolor=C_LBLTXT, size=size.small)

    _extUpdate: bool = not na(_closeBar) and _closeBar == bar_index if _tradeClosed else barstate.islast

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
        if not na(n382Line):
            line.set_x2(n382Line, _extX)
            label.set_x(n382Lbl, _extX)
        if not na(n618Line):
            line.set_x2(n618Line, _extX)
            label.set_x(n618Lbl, _extX)
        if not na(confLine):
            line.set_x2(confLine, _extX)
            label.set_x(confLbl, _extX)

    plot(_dma, 'DMA', color=C_DMA if i_showDma else na, offset=i_dmaDisp)

    def f_tf():
        _r: str = timeframe.period
        if timeframe.isseconds:
            _r = string.tostring(timeframe.multiplier) + 's'
        elif timeframe.isminutes:
            _r = string.tostring(math.round(timeframe.multiplier / 60)) + 'H' if timeframe.multiplier % 60 == 0 else string.tostring(timeframe.multiplier) + 'm'
        elif timeframe.isdaily:
            _r = string.tostring(timeframe.multiplier) + 'D'
        elif timeframe.isweekly:
            _r = string.tostring(timeframe.multiplier) + 'W'
        elif timeframe.ismonthly:
            _r = string.tostring(timeframe.multiplier) + 'M'
        elif timeframe.isticks:
            _r = string.tostring(timeframe.multiplier) + 'T'
        return _r

    def f_num(v: float):
        _a: float = math.abs(v)
        _s: str = string.tostring(v, '#')
        if _a >= 1000000000:
            _s = string.tostring(v / 1000000000, '#.#') + 'B'
        elif _a >= 1000000:
            _s = string.tostring(v / 1000000, '#.#') + 'M'
        elif _a >= 1000:
            _s = string.tostring(v / 1000, '#.#') + 'K'
        return _s

    def f_barColor(pct: float):
        return color.new(C_BAR_HI, 0) if pct >= 0.66 else color.new(C_BAR_MID, 0) if pct >= 0.33 else color.new(C_BAR_LO, 0)

    def f_bar(val: float, maxVal: float):
        _ratio: float = val / maxVal
        filled: int = math.round(math.min(_ratio, 1.0) * 10)
        bar: str = ""
        for i in pine_range(1, 10):
            bar += '█' if i <= filled else '░'
        return bar + '  ' + string.tostring(math.round(_ratio * 100)) + '%'

    def f_px(v: float):
        return '—' if na(v) else string.tostring(v, format.mintick)

    _dash: Persistent[Table] = table.new(position.top_left if i_dashPos == 'Top Left' else position.bottom_right if i_dashPos == 'Bottom Right' else position.bottom_left if i_dashPos == 'Bottom Left' else position.top_right, 2, 20, border_width=1, border_color=color.new(color.new('#2A3040'), 40), frame_width=1, frame_color=color.new(color.new('#3A2A6D'), 40))
    _rowA: Color = C_DASH_BG
    _rowB: Persistent[Color] = color.new(C_DASH_BG, 40)
    _lblCol: Persistent[Color] = color.new(C_DASH_TXT, 25)

    def f_row(r: int, lbl: str, val: str, vcol: Color):
        _bg: Color = _rowA if r % 2 == 1 else _rowB
        table.cell(_dash, 0, r, '  ' + lbl, text_halign=text.align_left, text_color=_lblCol, text_size=size.small, bgcolor=_bg, text_font_family=font.family_monospace)
        return table.cell(_dash, 1, r, val + '  ', text_halign=text.align_right, text_color=vcol, text_size=size.small, bgcolor=_bg, text_font_family=font.family_monospace)

    if barstate.islast and i_showDash:
        _hasSet: bool = not na(entryPrice)
        _biasTxt: str = ('BULL' if isLong else 'BEAR') if _hasSet else '—'
        _biasCol: Color = (C_SUP if isLong else C_RES) if _hasSet else C_DASH_TXT
        _status: str = '—' if na(slLine) else 'SL HIT' if slHit else 'XOP HIT' if tp3Hit else 'OP HIT' if tp2Hit else 'COP HIT' if tp1Hit else 'OPEN'
        _risk: float = math.abs(entryPrice - slPrice)
        _rr: float = math.abs(tp2Price - entryPrice) / _risk if _risk > 0 else 0.0
        _rrPct: float = math.min(_rr / 5.0, 1.0)
        _prog: float = 0.0
        if _hasSet and tp2Price != entryPrice:
            _prog = math.min(math.max((close - entryPrice) / (tp2Price - entryPrice), 0.0), 1.0)
        table.cell(_dash, 0, 0, 'DiNapoli Levels', text_halign=text.align_left, text_color=C_DASH_TXT, text_size=size.small, bgcolor=C_DASH_HDR, text_font_family=font.family_monospace)
        table.cell(_dash, 1, 0, syminfo.prefix + ':' + syminfo.ticker + '  ·  ' + f_tf(), text_halign=text.align_right, text_color=C_DASH_TXT, text_size=size.small, bgcolor=C_DASH_HDR, text_font_family=font.family_monospace)
        f_row(1, 'Lock', 'ACTIVE' if i_lockSignal else 'OFF', C_RES if i_lockSignal else C_DASH_TXT)
        f_row(2, 'Bias', _biasTxt, _biasCol)
        f_row(3, 'Node', ('F 61.8' if nodeIs618 else 'F 38.2') if _hasSet else '—', C_DASH_TXT)
        f_row(4, 'Retrace', '—' if na(nodeRetr) else f_bar(nodeRetr, 1.0), C_DASH_TXT if na(nodeRetr) else f_barColor(nodeRetr))
        f_row(5, 'Confluence', 'NO' if na(confPrice) else 'YES', C_DASH_TXT if na(confPrice) else C_SUP)
        f_row(6, 'Entry', f_px(entryPrice), C_ENTRY)
        f_row(7, 'Stop', f_px(slPrice), C_RES)
        f_row(8, 'COP', f_px(tp1Price), C_SUP)
        f_row(9, 'OP', f_px(tp2Price), C_SUP)
        f_row(10, 'XOP', f_px(tp3Price), C_SUP)
        f_row(11, 'R:R', f_bar(_rr, 5.0) if _risk > 0 else '—', f_barColor(_rrPct) if _risk > 0 else C_DASH_TXT)
        f_row(12, 'To OP', f_bar(_prog, 1.0) if _hasSet else '—', f_barColor(_prog) if _hasSet else C_DASH_TXT)
        f_row(13, 'Status', _status, C_RES if slHit else C_SUP if tp1Hit else C_DASH_TXT)
        f_row(14, 'Swing', f_px(math.abs(swingSize)), C_DASH_TXT)
        f_row(15, 'ATR', f_px(_atr), C_DASH_TXT)
        f_row(16, 'Bars Since', '—' if na(signalBar) else f_num(bar_index - signalBar), C_DASH_TXT)
        f_row(17, 'ADX', f_bar(math.min(_adx, 100.0), 100.0) if i_useAdx else 'OFF', f_barColor(math.min(_adx, 100.0) / 100.0) if i_useAdx else C_DASH_TXT)
        f_row(18, 'HTF Bias', 'OFF' if not i_useHtf else '—' if na(_htfClose) else 'BULL' if close > _htfClose else 'BEAR', C_DASH_TXT if not i_useHtf or na(_htfClose) else C_SUP if close > _htfClose else C_RES)
        f_row(19, 'Smoothing', i_smoothMethod if i_useSmooth else 'OFF', C_DASH_TXT)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)