"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, bgcolor,
    box, chart, close, color, dayofmonth, display, extend, fill, format, high, hl2, hlc3, input,
    label, line, location, low, math, na, open, plot, plotcandle, plotshape, polyline, position,
    request, script, shape, size, string, syminfo, ta, table, text, time, timeframe, volume, xloc
)
from pynecore.types import (
    Box, Color, Line, NA, Persistent, PersistentSeries, Polyline, Series,
    Table
)


@udt
class LiqVol:
    buyV: float = na(float)
    sellV: float = na(float)


@udt
class LiqVBox:
    upper: Box = na(Box)
    lower: Box = na(Box)
    end: Box = na(Box)


@udt
class OB:
    bx: Box = na(Box)
    b1: Box = na(Box)
    b2: Box = na(Box)
    b3: Box = na(Box)
    b4: Box = na(Box)
    left: int = na(int)
    top: float = na(float)
    bot: float = na(float)
    dir: int = na(int)
    vol: float = na(float)
    rate: str = na(str)
    broken: bool = na(bool)


@script.indicator("Sattam | Volume Edge", "Sattam | Volume Edge", overlay=True, max_polylines_count=55, max_boxes_count=100)
def main(
    showTS=input.bool(True, "Trend Signals", inline="1", group="Modules"),
    showLIQ=input.bool(True, "Liquidity", inline="M1", group="Modules"),
    showORB=input.bool(True, "ORB", inline="M1", group="Modules"),
    showTL=input.bool(True, "TrendLines", inline="M1", group="Modules"),
    showCAP=input.bool(True, "Capital Risk", inline="M2", group="Modules"),
    showEDGE=input.bool(True, "EDGE Volume", inline="M2", group="Modules"),
    showRMI=input.bool(True, "RMI Trend", inline="M2", group="Modules"),
    showOB=input.bool(True, "Order Blocks", inline="M2", group="Modules"),
    sens=input.float(1.7, "Sensitivity ", minval=0.5, maxval=5, inline="2", group="Trend Signal Settings"),
    showTP=input.bool(True, "TP", inline="2", group="Trend Signal Settings"),
    tsCandle=input.bool(True, "Trend Candles", inline="2", group="Trend Signal Settings"),
    tsTrail=input.bool(True, "Trailing TP", inline="3", group="Trend Signal Settings", tooltip="After a Buy signal, a trailing take-profit line (SuperTrend of ATR(10) x factor) follows the move until price closes below it"),
    tsTrailK=input.float(2.1, "", minval=0.5, step=0.1, inline="3", group="Trend Signal Settings"),
    liqLen=input.int(10, "", minval=3, inline="LIQ1", group="Liquidity Settings"),
    liqMax=input.int(5, "Max", inline="LIQ1", group="Liquidity Settings"),
    liqRight=input.int(5, "", inline="LIQ1", group="Liquidity Settings"),
    orbUTC=input.string("+3", "UTC +/-", inline="Sess", group="ORB Settings"),
    orbSess=input.session("0945-1015", "", inline="Sess", group="ORB Settings"),
    orbCol=input.color(color.new(color.new('#41E677'), 83), "", inline="Sess", group="ORB Settings"),
    orbSig=input.bool(True, "Signals", inline="Signals", group="ORB Settings"),
    tlPreset=input.string("Small", "", options=("Small", "Medium", "Big", "Macro"), inline="000", group="TrendLines Settings"),
    tlCol=input.color(color.new(color.new('#B2B5BE'), 50), "", inline="000", group="TrendLines Settings"),
    tlLast=input.int(2, "Last", options=(1, 2), inline="000", group="TrendLines Settings", tooltip="Show the Last # of Trendlines"),
    tlHist=input.bool(True, "History", inline="000", group="TrendLines Settings"),
    obPreset=input.string("Macro", "Preset", options=("Macro", "Big", "Medium", "Small"), inline="!!!", group="OrderBlock Settings"),
    obBrk=input.bool(True, "Breaker Block", inline="!!!", group="OrderBlock Settings"),
    rmiLen=input.int(14, "RMI Length ", inline="RMI", group="RMI Settings"),
    rmiPos=input.int(66, " Positive above", inline="rsi1", group="RMI Settings"),
    rmiNeg=input.int(30, "Negative below", inline="rsi1", group="RMI Settings"),
    rmiShow=input.bool(True, "Show MA ", inline="002", group="RMI Settings"),
    rmiBull=input.color(color.new('#00BCD4'), "", inline="002", group="RMI Settings"),
    rmiBear=input.color(color.new('#FF5252'), "", inline="002", group="RMI Settings"),
    capital=input.float(100000, "Capital", group="Capital Risk Settings"),
    riskPct=input.float(2, "Account Risk %", maxval=5, group="Capital Risk Settings"),
    slPct=input.float(3, "Stop Loss %", group="Capital Risk Settings"),
    rrRatio=input.float(2, "RR Ratio", group="Capital Risk Settings"),
    edgeCap=input.int(14, "Trading Capital", group="EDGE Volume Screener"),
    edgePos=input.string("Top Right", "Position", options=("Top Left", "Top Center", "Top Right", "Middle Left", "Middle Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"), inline="002", group="EDGE Volume Screener"),
    edgeSize=input.string("Small", "Size", options=("Tiny", "Small", "Normal", "Auto"), inline="002", group="EDGE Volume Screener"),
    e01=input.bool(True, "", inline="s01", group="Symbols"),
    e02=input.bool(True, "", inline="s02", group="Symbols"),
    e03=input.bool(True, "", inline="s03", group="Symbols"),
    e04=input.bool(True, "", inline="s04", group="Symbols"),
    e05=input.bool(True, "", inline="s05", group="Symbols"),
    e06=input.bool(True, "", inline="s06", group="Symbols"),
    e07=input.bool(True, "", inline="s07", group="Symbols"),
    e08=input.bool(True, "", inline="s08", group="Symbols"),
    e09=input.bool(True, "", inline="s09", group="Symbols"),
    e10=input.bool(True, "", inline="s10", group="Symbols"),
    e11=input.bool(False, "", inline="s11", group="Symbols"),
    e12=input.bool(False, "", inline="s12", group="Symbols"),
    e13=input.bool(False, "", inline="s13", group="Symbols"),
    e14=input.bool(False, "", inline="s14", group="Symbols"),
    e15=input.bool(False, "", inline="s15", group="Symbols"),
    e16=input.bool(False, "", inline="s16", group="Symbols"),
    e17=input.bool(False, "", inline="s17", group="Symbols"),
    e18=input.bool(False, "", inline="s18", group="Symbols"),
    e19=input.bool(False, "", inline="s19", group="Symbols"),
    e20=input.bool(False, "", inline="s20", group="Symbols"),
    e21=input.bool(False, "", inline="s21", group="Symbols"),
    e22=input.bool(False, "", inline="s22", group="Symbols"),
    e23=input.bool(False, "", inline="s23", group="Symbols"),
    e24=input.bool(False, "", inline="s24", group="Symbols"),
    e25=input.bool(False, "", inline="s25", group="Symbols"),
    e26=input.bool(False, "", inline="s26", group="Symbols"),
    e27=input.bool(False, "", inline="s27", group="Symbols"),
    e28=input.bool(False, "", inline="s28", group="Symbols"),
    e29=input.bool(False, "", inline="s29", group="Symbols"),
    e30=input.bool(False, "", inline="s30", group="Symbols"),
    e31=input.bool(False, "", inline="s31", group="Symbols"),
    e32=input.bool(False, "", inline="s32", group="Symbols"),
    e33=input.bool(False, "", inline="s33", group="Symbols"),
    e34=input.bool(False, "", inline="s34", group="Symbols"),
    e35=input.bool(False, "", inline="s35", group="Symbols"),
    e36=input.bool(False, "", inline="s36", group="Symbols"),
    e37=input.bool(False, "", inline="s37", group="Symbols"),
    e38=input.bool(False, "", inline="s38", group="Symbols"),
    e39=input.bool(False, "", inline="s39", group="Symbols"),
    e40=input.bool(False, "", inline="s40", group="Symbols"),
    s01=input.symbol("NASDAQ:NVDA", "Symbol 1", inline="s01", group="Symbols"),
    s02=input.symbol("NASDAQ:TSLA", "Symbol 2", inline="s02", group="Symbols"),
    s03=input.symbol("NASDAQ:AAPL", "Symbol 3", inline="s03", group="Symbols"),
    s04=input.symbol("NASDAQ:META", "Symbol 4", inline="s04", group="Symbols"),
    s05=input.symbol("NASDAQ:MSFT", "Symbol 5", inline="s05", group="Symbols"),
    s06=input.symbol("NASDAQ:AMD", "Symbol 6", inline="s06", group="Symbols"),
    s07=input.symbol("NASDAQ:AMZN", "Symbol 7", inline="s07", group="Symbols"),
    s08=input.symbol("NASDAQ:GOOGL", "Symbol 8", inline="s08", group="Symbols"),
    s09=input.symbol("NASDAQ:AVGO", "Symbol 9", inline="s09", group="Symbols"),
    s10=input.symbol("NYSE:ORCL", "Symbol 10", inline="s10", group="Symbols"),
    s11=input.symbol("NASDAQ:NFLX", "Symbol 11", inline="s11", group="Symbols"),
    s12=input.symbol("NASDAQ:INTC", "Symbol 12", inline="s12", group="Symbols"),
    s13=input.symbol("NASDAQ:QCOM", "Symbol 13", inline="s13", group="Symbols"),
    s14=input.symbol("NASDAQ:ADBE", "Symbol 14", inline="s14", group="Symbols"),
    s15=input.symbol("NASDAQ:CSCO", "Symbol 15", inline="s15", group="Symbols"),
    s16=input.symbol("NASDAQ:PEP", "Symbol 16", inline="s16", group="Symbols"),
    s17=input.symbol("NASDAQ:COST", "Symbol 17", inline="s17", group="Symbols"),
    s18=input.symbol("NASDAQ:TXN", "Symbol 18", inline="s18", group="Symbols"),
    s19=input.symbol("NASDAQ:AMGN", "Symbol 19", inline="s19", group="Symbols"),
    s20=input.symbol("NASDAQ:PLTR", "Symbol 20", inline="s20", group="Symbols"),
    s21=input.symbol("NASDAQ:MU", "Symbol 21", inline="s21", group="Symbols"),
    s22=input.symbol("NASDAQ:ARM", "Symbol 22", inline="s22", group="Symbols"),
    s23=input.symbol("NASDAQ:SMCI", "Symbol 23", inline="s23", group="Symbols"),
    s24=input.symbol("NASDAQ:COIN", "Symbol 24", inline="s24", group="Symbols"),
    s25=input.symbol("NASDAQ:MRVL", "Symbol 25", inline="s25", group="Symbols"),
    s26=input.symbol("NASDAQ:PYPL", "Symbol 26", inline="s26", group="Symbols"),
    s27=input.symbol("NASDAQ:SBUX", "Symbol 27", inline="s27", group="Symbols"),
    s28=input.symbol("NASDAQ:BKNG", "Symbol 28", inline="s28", group="Symbols"),
    s29=input.symbol("NASDAQ:ISRG", "Symbol 29", inline="s29", group="Symbols"),
    s30=input.symbol("NASDAQ:LRCX", "Symbol 30", inline="s30", group="Symbols"),
    s31=input.symbol("NYSE:KO", "Symbol 31", inline="s31", group="Symbols"),
    s32=input.symbol("NYSE:JPM", "Symbol 32", inline="s32", group="Symbols"),
    s33=input.symbol("NYSE:V", "Symbol 33", inline="s33", group="Symbols"),
    s34=input.symbol("NYSE:UNH", "Symbol 34", inline="s34", group="Symbols"),
    s35=input.symbol("NYSE:XOM", "Symbol 35", inline="s35", group="Symbols"),
    s36=input.symbol("NASDAQ:WMT", "Symbol 36", inline="s36", group="Symbols"),
    s37=input.symbol("NYSE:LLY", "Symbol 37", inline="s37", group="Symbols"),
    s38=input.symbol("NYSE:BAC", "Symbol 38", inline="s38", group="Symbols"),
    s39=input.symbol("NYSE:CRM", "Symbol 39", inline="s39", group="Symbols"),
    s40=input.symbol("NYSE:BA", "Symbol 40", inline="s40", group="Symbols"),
    showTables=input.bool(True, "Trading Capital & Volume Screener", group="Modules", tooltip="One switch for both tables (Capital Risk and Volume Screener)"),
    capPos=input.string("Middle Right", "Position", options=("Top Left", "Top Center", "Top Right", "Middle Left", "Middle Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"), group="Capital Risk Settings")
):
    orbTz = 'UTC' + orbUTC
    inSess: Series = not na(time(timeframe.period, orbSess, orbTz))
    sessOpen = inSess and (not inSess[1])
    orbHi: PersistentSeries[float] = na(float)
    orbLo: PersistentSeries[float] = na(float)
    orbBought: Persistent[bool] = False
    orbSold: Persistent[bool] = False
    if sessOpen:
        orbHi = high
        orbLo = low
        orbBought = False
        orbSold = False
    elif inSess:
        orbHi = math.max(orbHi, high)
        orbLo = math.min(orbLo, low)
    orbMid: Series = (orbHi + orbLo) / 2
    orbOn = showORB and (not na(orbHi))

    confirmed = barstate.isconfirmed
    orbBuy = confirmed and orbOn and orbSig and (not inSess) and (not orbBought) and (close > orbHi) and (close[1] <= orbHi[1])
    orbSell = confirmed and orbOn and orbSig and (not inSess) and (not orbSold) and (close < orbLo) and (close[1] >= orbLo[1])
    if orbBuy:
        orbBought = True
    if orbSell:
        orbSold = True
    bgcolor(color.new(color.new('#00BCD4'), 90) if showORB and inSess else na, title='Active session highlight')
    alertcondition(orbBuy, 'Buy Signal', 'Breakout (Buy)')
    alertcondition(orbSell, 'Sell Signal', 'BreakDown (Sell)')
    plotshape(orbBuy, 'Shapes', shape.labelup, location.belowbar, color.new('#57B4BA'), size=size.tiny, editable=False)
    plotshape(orbSell, 'Shapes', shape.labeldown, location.abovebar, color.new('#FE4F2D'), size=size.tiny, editable=False)

    orbHiCol = na if orbHi != orbHi[1] else color.new(color.new('#707070'), 0)
    orbLoCol = na if orbLo != orbLo[1] else color.new(color.new('#707070'), 0)
    orbMidCol = na if orbMid != orbMid[1] else color.new(color.new('#898989'), 0)
    pHi = plot(orbHi if orbOn else na, 'ORB High', orbHiCol, 1)
    pLo = plot(orbLo if orbOn else na, 'ORB Low', orbLoCol, 1)
    pMid = plot(orbMid if orbOn else na, 'ORB Mid', orbMidCol, 1)
    fill(pHi, pLo, orbHi, orbMid, na if orbHi != orbHi[1] else color.new(color.new('#57B4BA'), 85), color.new(color.blue, 100))
    fill(pMid, pLo, orbLo, orbMid, na if orbLo != orbLo[1] else color.new(color.new('#FE4F2D'), 85), color.new(color.yellow, 100))

    liqHiBox: Persistent[list[Box]] = array.new_box()
    liqLoBox: Persistent[list[Box]] = array.new_box()
    liqHiLn: Persistent[list[Line]] = array.new_line()
    liqLoLn: Persistent[list[Line]] = array.new_line()
    liqHiVB: Persistent[list[LiqVBox]] = array.new(0, NA(LiqVBox))
    liqLoVB: Persistent[list[LiqVBox]] = array.new(0, NA(LiqVBox))
    liqHiVol: Persistent[list[LiqVol]] = array.new(0, NA(LiqVol))
    liqLoVol: Persistent[list[LiqVol]] = array.new(0, NA(LiqVol))
    liqHiMid: Persistent[list[Line]] = array.new_line()
    liqLoMid: Persistent[list[Line]] = array.new_line()

    def liqRemoveOld(bxs: list[Box], lns: list[Line], vbs: list[LiqVBox], vols: list[LiqVol], mx: int, mids: list[Line]):
        if array.size(bxs) > mx:
            box.delete(array.shift(bxs))
        if array.size(vbs) > mx:
            c_ = array.shift(vbs)
            box.delete(c_.upper)
            box.delete(c_.lower)
            box.delete(c_.end)
        if array.size(vols) > mx:
            array.shift(vols)
        if array.size(lns) > mx:
            line.delete(array.shift(lns))
        __block_result__ = na
        if array.size(mids) > mx:
            __block_result__ = line.delete(array.shift(mids))
        return __block_result__

    def liqRemoveAt(bxs: list[Box], lns: list[Line], vbs: list[LiqVBox], vols: list[LiqVol], mids: list[Line], i: int):
        box.delete(array.remove(bxs, i))
        line.delete(array.remove(lns, i))
        aa = array.remove(vbs, i)
        box.delete(aa.upper)
        box.delete(aa.lower)
        box.delete(aa.end)
        array.remove(vols, i)
        return line.delete(array.remove(mids, i))

    def liqOverlap(tops: list[Box]):
        delIdx: int = 0
        deleted: bool = False
        if array.size(tops) > 0:
            for i in pine_range(0, array.size(tops) - 1):
                if i > 0:
                    bx__000000e2__ = array.get(tops, i)
                    for x in pine_range(i - 1, 0):
                        bx2 = array.get(tops, x)
                        if method_call('get_top', bx__000000e2__) < method_call('get_bottom', bx2) and method_call('get_bottom', bx__000000e2__) > method_call('get_top', bx2) or (method_call('get_bottom', bx__000000e2__) < method_call('get_top', bx2) and method_call('get_top', bx__000000e2__) > method_call('get_bottom', bx2)) or (method_call('get_top', bx__000000e2__) == method_call('get_top', bx2) and method_call('get_bottom', bx__000000e2__) == method_call('get_bottom', bx2)):
                            deleted = True
                            delIdx = i
        return (deleted, delIdx)

    def liqExtend(bxs: list[Box], lns: list[Line], vols: list[LiqVol], vbs: list[LiqVBox], mids: list[Line]):
        barT = time - time[1]
        __block_result_1__ = na
        if array.size(bxs) > 0:
            __block_result_2__ = na
            for i in pine_range(array.size(bxs) - 1, 0):
                bx__0000010a__ = array.get(bxs, i)
                vol = array.get(vols, i)
                buyV = vol.buyV
                sellV = vol.sellV
                delta = buyV + sellV
                buyM = buyV / delta * 100
                exT = time + barT * 20
                exT2 = time + barT * 2
                method_call('set_right', bx__0000010a__, exT)
                vb = array.get(vbs, i)
                dd = buyV - sellV
                method_call('set_text_color', bx__0000010a__, color.lime if dd > 0 else color.new('#FF0000'))
                bxR = method_call('get_right', bx__0000010a__)
                bxL = method_call('get_left', bx__0000010a__)
                lineT = (bxR + bxL) / 2
                volCol = color.lime if buyM > 50 else color.new('#FF0000')
                ln = array.get(lns, i)
                method_call('set_x2', ln, exT2)
                md = array.get(mids, i)
                method_call('set_x1', md, exT2)
                method_call('set_x2', md, exT2)
                method_call('set_color', md, volCol)
                method_call('set_color', ln, volCol)
                dist = math.abs(bxL - lineT)
                volT = cast_int(bxL + dist * buyM / 100)
                volT2 = cast_int(bxL + dist * (100 - buyM) / 100)
                method_call('set_right', vb.upper, volT)
                method_call('set_text', vb.upper, 'Bull % : ' + string.tostring(buyM, '#.##'))
                method_call('set_text', vb.lower, 'Bear % : ' + string.tostring(100 - buyM, '#.##'))
                method_call('set_right', vb.lower, volT2)
                method_call('set_bgcolor', vb.upper, color.rgb(45, 205, 42, 60))
                method_call('set_bgcolor', vb.lower, color.rgb(190, 18, 21, 60))
                method_call('set_left', vb.end, exT2)
                method_call('set_right', vb.end, exT)
                method_call('set_text', vb.end, 'Delta: ' + string.tostring(dd))
                method_call('set_bgcolor', vb.end, color.new(color.lime, 75) if dd > 0 else color.rgb(253, 5, 5, 75))
                __block_result_2__ = method_call('set_text_halign', vb.end, text.align_center)
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def liqVerify(bxs: list[Box], isHigh: bool, lns: list[Line], vbs: list[LiqVBox], vols: list[LiqVol], mx: int, mids: list[Line]):
        brk: bool = False
        if array.size(bxs) > 0:
            for i in pine_range(array.size(bxs) - 1, 0):
                bx__00000121__ = array.get(bxs, i)
                xl = array.get(lns, i)
                vb = array.get(vbs, i)
                md = array.get(mids, i)
                if isHigh and high > method_call('get_top', bx__00000121__) or (not isHigh and low < method_call('get_top', bx__00000121__)):
                    array.remove(bxs, i)
                    array.remove(lns, i)
                    array.remove(mids, i)
                    array.remove(vbs, i)
                    array.remove(vols, i)
                    method_call('delete', bx__00000121__)
                    method_call('delete', vb.upper)
                    method_call('delete', vb.lower)
                    method_call('delete', vb.end)
                    method_call('delete', xl)
                    method_call('delete', md)
                    brk = True
        liqRemoveOld(bxs, lns, vbs, vols, mx, mids)
        return brk

    def liqNewVBox(t0: int, top: float, t1: int, mid: float, bot: float, exT2: Series[int]):
        return LiqVBox(box.new(t0, top, t1, mid, bgcolor=color.new(color.red, 70), border_color=color.new(color.white, 100), xloc=xloc.bar_time, border_width=1, text='', text_halign=text.align_right, text_color=chart.fg_color, text_size=size.small), box.new(t0, mid, t0 + 1, bot, bgcolor=color.new(color.green, 70), border_color=color.new(color.white, 100), xloc=xloc.bar_time, border_width=1, text='', text_halign=text.align_right, text_color=chart.fg_color, text_size=size.small), box.new(exT2, top, exT2[1], bot, bgcolor=color.new(color.red, 70), border_color=color.new(color.white, 100), xloc=xloc.bar_time, border_width=1, text='', text_halign=text.align_right, text_color=chart.fg_color, text_size=size.small))

    liqAtr300 = ta.atr(300)
    liqPivHi = ta.pivothigh(high, liqLen, liqRight)
    liqPivLo = ta.pivotlow(low, liqLen, liqRight)
    def liqDraw():
        barT = time - time[1]
        thold = liqAtr300 * (2.5 / 3)
        exT2 = time + barT * 2
        si = liqRight
        liqLine = color.rgb(209, 203, 203, 45)
        if not na(liqPivHi):
            buyV = math.round(volume[si] * (close[si] - low[si]) / (high[si] - low[si]))
            sellV = math.round(volume[si] * (high[si] - close[si]) / (high[si] - low[si]))
            y1 = high[si] - thold
            array.push(liqHiBox, box.new(time[si], high[si], time[1], y1, bgcolor=color.new(color.new('#5D606B'), 70), border_color=color.new(color.white, 100), xloc=xloc.bar_time, border_width=2, text='', text_halign=text.align_right, text_color=chart.fg_color, text_size=size.small))
            array.push(liqHiMid, line.new(exT2, high[si], exT2, y1, xloc=xloc.bar_time, color=liqLine, style=line.style_dashed))
            mid = (high[si] + y1) / 2
            array.push(liqHiLn, line.new(time[si], mid, time[1], mid, xloc=xloc.bar_time, color=liqLine, style=line.style_dashed))
            array.push(liqHiVol, LiqVol(buyV, sellV))
            array.push(liqHiVB, liqNewVBox(time[si], high[si], time[1], mid, y1, exT2))
        __block_result_3__ = na
        if not na(liqPivLo):
            buyV = math.round(volume[si] * (close[si] - low[si]) / (high[si] - low[si]))
            sellV = math.round(volume[si] * (high[si] - close[si]) / (high[si] - low[si]))
            y1 = low[si] + thold
            array.push(liqLoVol, LiqVol(buyV, sellV))
            array.push(liqLoBox, box.new(time[si], low[si], time[1], y1, bgcolor=color.new(color.new('#5D606B'), 70), border_color=color.new(color.white, 100), xloc=xloc.bar_time, border_width=2, text='', text_halign=text.align_right, text_color=chart.fg_color, text_size=size.small))
            mid = (low[si] + y1) / 2
            array.push(liqLoLn, line.new(time[si], mid, time[1], mid, xloc=xloc.bar_time, color=liqLine, style=line.style_dashed))
            array.push(liqLoMid, line.new(exT2, low[si], exT2, y1, xloc=xloc.bar_time, color=liqLine, style=line.style_dashed))
            __block_result_3__ = array.push(liqLoVB, liqNewVBox(time[si], low[si], time[1], mid, y1, exT2))
        return __block_result_3__

    if showLIQ and confirmed:
        liqVerify(liqHiBox, True, liqHiLn, liqHiVB, liqHiVol, liqMax, liqHiMid)
        liqVerify(liqLoBox, False, liqLoLn, liqLoVB, liqLoVol, liqMax, liqLoMid)
        liqExtend(liqHiBox, liqHiLn, liqHiVol, liqHiVB, liqHiMid)
        liqExtend(liqLoBox, liqLoLn, liqLoVol, liqLoVB, liqLoMid)
        liqDraw()
        d1, i1 = liqOverlap(liqHiBox)
        if d1:
            liqRemoveAt(liqHiBox, liqHiLn, liqHiVB, liqHiVol, liqHiMid, i1)
        d2, i2 = liqOverlap(liqLoBox)
        if d2:
            liqRemoveAt(liqLoBox, liqLoLn, liqLoVB, liqLoVol, liqLoMid, i2)

        if array.size(liqHiBox) > 0:
            for b in liqHiBox:
                box.set_bgcolor(b, color.new(color.new('#F33838'), 80))
        if array.size(liqLoBox) > 0:
            for b in liqLoBox:
                box.set_bgcolor(b, color.new(color.new('#2FF56A'), 80))

    rmiP: PersistentSeries[bool] = False
    rmiN: PersistentSeries[bool] = False
    rUp = ta.rma(math.max(ta.change(close), 0), rmiLen)
    rDn = ta.rma(-math.min(ta.change(close), 0), rmiLen)
    rRsi = 100 if rDn == 0 else 0 if rUp == 0 else 100 - 100 / (1 + rUp / rDn)
    rMfi = ta.mfi(hlc3, rmiLen)
    rmi: Series = math.avg(rRsi, rMfi)
    ema5c = ta.change(ta.ema(close, 5))
    pMom = rmi[1] < rmiPos and rmi > rmiPos and (rmi > rmiNeg) and (ema5c > 0)
    nMom = rmi < rmiNeg and ema5c < 0
    if pMom and confirmed:
        rmiP = True
        rmiN = False
    if nMom and confirmed:
        rmiP = False
        rmiN = True
    rBand = inline_series(math.min(ta.atr(30) * 0.3, close * (0.3 / 100)), 20) / 2 * 8
    rRange = high - low
    rW = rRange / math.sum(rRange, 20)
    rwma = math.sum(close * rW, 20) / math.sum(rW, 20)
    rCol = rmiBull if rmiP else rmiBear
    RWMA = rwma - rBand if rmiP else rwma + rBand if rmiN else na
    rAlpha = color.new(color.black, 100)
    rOn = showRMI and rmiShow
    rCenter = plot(RWMA if rOn else na, 'RRTH', rCol)
    plot(RWMA if rOn else na, 'RRTH', color.new(rCol, 70), 2)
    plot(RWMA if rOn else na, 'RRTH', color.new(rCol, 80), 3)
    plot(RWMA if rOn else na, 'RRTH', color.new(rCol, 90), 4)
    rMax = RWMA + rBand
    rMin = RWMA - rBand
    rTop = plot(rMax if rOn else na, 'RRTH', rAlpha)
    rBot = plot(rMin if rOn else na, 'RRTH', rAlpha)
    fill(rTop, rCenter, rMax, RWMA, rAlpha, color.new(rCol, 75))
    fill(rCenter, rBot, RWMA, rMin, color.new(rCol, 75), rAlpha)
    rBarCol = color.green if rmiP else color.red
    if showRMI and rmiN and (not rmiN[1]):
        label.new(bar_index, rMax + rBand / 2, '', color=color.red, size=size.small)
    if showRMI and rmiP and (not rmiP[1]):
        label.new(bar_index, rMin - rBand / 2, '', color=color.green, size=size.small, style=label.style_label_up)
    plotcandle(open if showRMI else na, high, low, close, color=rBarCol, wickcolor=rBarCol, bordercolor=rBarCol)
    barcolor(rBarCol if showRMI else na)
    alertcondition(rmiP and (not rmiP[1]), 'BUY')
    alertcondition(rmiN and (not rmiN[1]), 'SELL')

    tsBull: Color = color.new('#33CFBB')
    tsBear: Color = color.new('#DD3024')
    tsMult = (15 * sens + 4) / 11
    tsAtr = ta.atr(25)
    tsBand = 1.1 * (sens + 2) * tsAtr
    tsTrend: PersistentSeries[int] = 0
    tsStop: Persistent[float] = na(float)
    tsUp = hl2 - tsBand
    tsDn = hl2 + tsBand
    tsUp = math.max(tsUp, tsStop) if tsTrend == 1 and (not na(tsStop)) else tsUp
    tsDn = math.min(tsDn, tsStop) if tsTrend == -1 and (not na(tsStop)) else tsDn
    if confirmed:
        if tsTrend == 0:
            tsTrend = 1 if close > hl2 else -1
            tsStop = tsUp if tsTrend == 1 else tsDn
        elif tsTrend == 1:
            if close < tsUp:
                tsTrend = -1
                tsStop = hl2 + tsBand
            else:
                tsStop = tsUp
        else:
            if close > tsDn:
                tsTrend = 1
                tsStop = hl2 - tsBand
            else:
                tsStop = tsDn
    tsFlipUp = tsTrend == 1 and tsTrend[1] == -1
    tsFlipDn = tsTrend == -1 and tsTrend[1] == 1
    tsRange = ta.highest(high, 300) - ta.lowest(low, 300)
    tsAtr14 = ta.atr(14)
    tsStrong = close > ta.wma(close, 186)
    tsCol = tsBull if tsTrend[1] == 1 else tsBear
    plotcandle(open if showTS and tsCandle else na, high, low, close, color=tsCol, wickcolor=tsCol, bordercolor=tsCol)
    barcolor(tsCol if showTS and tsCandle else na)
    plot(tsMult, '!@', display=display.data_window)
    plotshape(low - 0.18 * tsRange if showTS and tsFlipUp and (not tsStrong) else na, 'Buy Label', shape.labelup, location.absolute, tsBull, text='▲', textcolor=color.new('#FFFFFF'), size=size.tiny)
    plotshape(low - 0.18 * tsRange if showTS and tsFlipUp and tsStrong else na, 'Buy Label', shape.labelup, location.absolute, tsBull, text='▲+', textcolor=color.new('#FFFFFF'), size=size.tiny)
    plotshape(high + 0.18 * tsRange if showTS and tsFlipDn and tsStrong else na, 'Sell Label', shape.labeldown, location.absolute, tsBear, text='▼', textcolor=color.new('#FFFFFF'), size=size.tiny)
    plotshape(high + 0.18 * tsRange if showTS and tsFlipDn and (not tsStrong) else na, 'Sell Label', shape.labeldown, location.absolute, tsBear, text='▼+', textcolor=color.new('#FFFFFF'), size=size.tiny)

    alertcondition(tsFlipUp, 'Buy Signal (Trend)', 'Volume Edge: BUY on {{ticker}} {{interval}} @ {{close}}')
    alertcondition(tsFlipDn, 'Sell Signal (Trend)', 'Volume Edge: SELL on {{ticker}} {{interval}} @ {{close}}')
    alertcondition(tsFlipUp or tsFlipDn, 'Buy or Sell Signal (Trend)', 'Volume Edge: signal on {{ticker}} {{interval}} @ {{close}}')
    if showTS and tsFlipUp:
        alert('Volume Edge: BUY on ' + syminfo.ticker + ' ' + timeframe.period + ' @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if showTS and tsFlipDn:
        alert('Volume Edge: SELL on ' + syminfo.ticker + ' ' + timeframe.period + ' @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)

    tsTrailSt, tsTrailDir = ta.supertrend(tsTrailK, 10)
    tsTrailOn: Persistent[bool] = False
    tsTrailDnOn: Persistent[bool] = False
    if tsFlipUp:
        tsTrailOn = True
        tsTrailDnOn = False
    if tsFlipDn:
        tsTrailDnOn = True
        tsTrailOn = False
    if tsTrailDir == 1 and confirmed:
        tsTrailOn = False
    if tsTrailDir == -1 and confirmed:
        tsTrailDnOn = False
    plot(tsTrailSt if showTS and tsTrail and tsTrailOn and (tsTrailDir < 0) else na, 'Up Trend', color.new('#4CAF50'), 2, plot.style_linebr)
    plot(tsTrailSt if showTS and tsTrail and tsTrailDnOn and (tsTrailDir > 0) else na, 'Down Trend', color.new('#F23645'), 2, plot.style_linebr)

    tsEntry: Persistent[float] = na(float)
    tsTp1: Persistent[float] = na(float)
    tsTp2: Persistent[float] = na(float)
    tsHit1: Persistent[bool] = False
    tsHit2: Persistent[bool] = False
    if tsFlipUp or tsFlipDn:
        tsEntry = close
        tsTp1 = close + tsBand if tsFlipUp else close - tsBand
        tsTp2 = close + 2.5 * tsBand if tsFlipUp else close - 2.5 * tsBand
        tsHit1 = False
        tsHit2 = False
    tsTpCol = color.new(color.black, 100)
    if showTS and showTP and confirmed and (not na(tsTp1)) and (not (tsFlipUp or tsFlipDn)):
        if tsTrend == 1:
            if not tsHit1 and high >= tsTp1:
                tsHit1 = True
                label.new(bar_index, high + 0.27 * tsAtr14, '✓', style=label.style_label_center, color=tsTpCol, textcolor=color.new('#60E264'), size=size.normal, tooltip='LONG TP1 Reached')
                alert('Volume Edge: LONG TP1 reached on ' + syminfo.ticker + ' ' + timeframe.period, alert.freq_once_per_bar_close)
            if not tsHit2 and high >= tsTp2:
                tsHit2 = True
                label.new(bar_index, high + 0.27 * tsAtr14, '✓', style=label.style_label_center, color=tsTpCol, textcolor=color.new('#60E264'), size=size.normal, tooltip='LONG TP2 Reached')
                alert('Volume Edge: LONG TP2 reached on ' + syminfo.ticker + ' ' + timeframe.period, alert.freq_once_per_bar_close)
        else:
            if not tsHit1 and low <= tsTp1:
                tsHit1 = True
                label.new(bar_index, low - 0.07 * tsRange, '✓', style=label.style_label_center, color=tsTpCol, textcolor=color.new('#60E264'), size=size.normal, tooltip='SHORT TP1 Reached')
                alert('Volume Edge: SHORT TP1 reached on ' + syminfo.ticker + ' ' + timeframe.period, alert.freq_once_per_bar_close)
            if not tsHit2 and low <= tsTp2:
                tsHit2 = True
                label.new(bar_index, low - 0.07 * tsRange, '✓', style=label.style_label_center, color=tsTpCol, textcolor=color.new('#60E264'), size=size.normal, tooltip='SHORT TP2 Reached')
                alert('Volume Edge: SHORT TP2 reached on ' + syminfo.ticker + ' ' + timeframe.period, alert.freq_once_per_bar_close)

    __block_result_4__ = na
    __switch__ = obPreset
    if __switch__ == "Macro":
        __block_result_4__ = 50
    elif __switch__ == "Big":
        __block_result_4__ = 30
    elif __switch__ == "Medium":
        __block_result_4__ = 20
    else:
        __block_result_4__ = 10
    obLeft = __block_result_4__
    __block_result_5__ = na
    __switch__ = obPreset
    if __switch__ == "Macro":
        __block_result_5__ = 0.8
    elif __switch__ == "Big":
        __block_result_5__ = 0.55
    else:
        __block_result_5__ = 0.54
    obK = __block_result_5__
    obs: Persistent[list[OB]] = array.new(0, NA(OB))
    obAtr = ta.atr(300)

    obDayVol: Persistent[list[float]] = array.new_float()
    obCurDay: Persistent[float] = 0.0
    if ta.change(dayofmonth) != 0 or barstate.isfirst:
        if not barstate.isfirst:
            array.push(obDayVol, obCurDay)
            if array.size(obDayVol) > 19:
                array.shift(obDayVol)
        obCurDay = 0.0
    obCurDay += volume
    obRef = (array.sum(obDayVol) + obCurDay) / (array.size(obDayVol) + 1)
    obPH = ta.pivothigh(high, obLeft, 5)
    obPL = ta.pivotlow(low, obLeft, 5)

    def obRate(v: float, ref: float):
        return 'High' if v >= 0.09 * ref else 'Medium' if v >= 0.03 * ref else 'Low' if v >= 0.02 * ref else 'Very Low'

    obBullCols: list[Color] = array.from_items(color.new('#0980FF'), color.new('#00C3E5'), color.new('#00EAA4'), color.new('#05FF3F'))
    obBearCols: list[Color] = array.from_items(color.new('#8215FF'), color.new('#CD31F3'), color.new('#FF19BA'), color.new('#FF1515'))
    def obNew(idx: int, dir: int):
        th = obK * obAtr
        top: float = na(float)
        bot: float = na(float)
        if dir == 1:
            bot = low[idx]
            top = bot + math.max(math.min(math.min(open[idx], close[idx]) - bot, th), th * 0.5)
        else:
            top = high[idx]
            bot = top - math.max(math.min(top - math.max(open[idx], close[idx]), th), th * 0.5)
        return OB(box.new(bar_index - idx, top, bar_index, bot, xloc=xloc.bar_index, extend=extend.right, bgcolor=color.new(color.new('#5A5D77'), 80), border_color=color.new(color.new('#5A5D77'), 80), text_size=size.auto, text_halign=text.align_right, text_color=color.gray), box.new(na, na, na, na), box.new(na, na, na, na), box.new(na, na, na, na), box.new(na, na, na, na), bar_index - idx, top, bot, dir, volume[idx], obRate(volume[idx], obRef), False)

    def obOverlap(o: OB):
        hi_ = math.min(high, o.top)
        lo_ = math.max(low, o.bot)
        return (hi_ - lo_) / (high - low) if hi_ > lo_ and high > low else 0.0

    def obOverlapPrev(o: OB):
        hi_ = math.min(high[1], o.top)
        lo_ = math.max(low[1], o.bot)
        return (hi_ - lo_) / (high[1] - low[1]) if hi_ > lo_ and high[1] > low[1] else 0.0

    if showOB and confirmed:
        if array.size(obs) > 0:
            for i in pine_range(array.size(obs) - 1, 0):
                o = array.get(obs, i)
                if not o.broken:
                    o.vol -= obOverlap(o) * volume

                    if o.vol <= 0:
                        if obBrk:
                            o.broken = True
                            method_call('set_bgcolor', o.bx, color.new(color.new('#787B86'), 60))
                            method_call('set_border_color', o.bx, color.new(color.new('#787B86'), 60))
                            method_call('set_text', o.bx, 'Breaker Block')
                        else:
                            box.delete(o.bx)
                            box.delete(o.b1)
                            box.delete(o.b2)
                            box.delete(o.b3)
                            box.delete(o.b4)
                            array.remove(obs, i)
                            continue
                    else:
                        o.rate = obRate(math.max(o.vol, 0), obRef)
                        method_call('set_text', o.bx, o.rate + ': ' + string.tostring(math.max(o.vol, 0), format.volume))
                method_call('set_right', o.bx, bar_index)
                span = bar_index - o.left
                q = span / 4
                cols = obBullCols if o.dir == 1 else obBearCols
                bxs = array.from_items(o.b1, o.b2, o.b3, o.b4)
                for k in pine_range(0, 3):
                    b = method_call('get', bxs, k)
                    method_call('set_lefttop', b, o.left + math.round(q * k), o.top)
                    method_call('set_rightbottom', b, bar_index if k == 3 else o.left + math.round(q * (k + 1)), o.bot)
                    c_ = color.new('#363A45') if o.broken else method_call('get', cols, k)
                    method_call('set_bgcolor', b, color.new(c_, 100 if o.broken else 68))
                    method_call('set_border_color', b, color.new(c_, 100))
        if not na(obPL):
            o = obNew(5, 1)
            o.vol -= obOverlap(o) * volume + obOverlapPrev(o) * volume[1]
            method_call('set_text', o.bx, obRate(math.max(o.vol, 0), obRef) + ': ' + string.tostring(math.max(o.vol, 0), format.volume))
            array.push(obs, o)
        if not na(obPH):
            o = obNew(5, -1)
            o.vol -= obOverlap(o) * volume + obOverlapPrev(o) * volume[1]
            method_call('set_text', o.bx, obRate(math.max(o.vol, 0), obRef) + ': ' + string.tostring(math.max(o.vol, 0), format.volume))
            array.push(obs, o)
        while array.size(obs) > 5:
            o = array.shift(obs)
            box.delete(o.bx)
            box.delete(o.b1)
            box.delete(o.b2)
            box.delete(o.b3)
            box.delete(o.b4)

    __block_result_6__ = na
    __switch__ = tlPreset
    if __switch__ == "Small":
        __block_result_6__ = 10
    elif __switch__ == "Medium":
        __block_result_6__ = 15
    elif __switch__ == "Big":
        __block_result_6__ = 20
    else:
        __block_result_6__ = 30
    tlL = __block_result_6__
    __block_result_7__ = na
    __switch__ = tlPreset
    if __switch__ == "Small":
        __block_result_7__ = 5
    elif __switch__ == "Medium":
        __block_result_7__ = 7
    elif __switch__ == "Big":
        __block_result_7__ = 10
    else:
        __block_result_7__ = 15
    tlR = __block_result_7__
    tls: Persistent[list[Polyline]] = array.new(0, NA(Polyline))
    tlPrevLo: Persistent[float] = na(float)
    tlPrevLoT: Persistent[int] = na(int)
    tlPrevHi: Persistent[float] = na(float)
    tlPrevHiT: Persistent[int] = na(int)
    tlPL = ta.pivotlow(low, tlL, tlR)
    tlPH = ta.pivothigh(high, tlL, tlR)
    tlDelta = time - time[1]
    def tlMake(sup: bool, t0: int, y0: float, t2: int, y2: float):
        tEnd = t2 + 75 * tlDelta
        ye = y0 + (y2 - y0) * (tEnd - t0) / (t2 - t0)
        pts = array.from_items(chart.point.from_time(t0, y0), chart.point.from_time(t0 + 2 * tlDelta, y0), chart.point.from_time(tEnd, ye))
        return polyline.new(pts, False, False, xloc.bar_time, color.new(color.new('#484749'), 80), color.new(color.new('#F53ACC'), 50) if sup else tlCol, line.style_solid, 1)

    if showTL and confirmed:
        if not na(tlPL):
            if not na(tlPrevLo) and tlPrevLo < tlPL:
                array.push(tls, tlMake(True, tlPrevLoT, tlPrevLo, time[tlR], tlPL))
            tlPrevLo = tlPL
            tlPrevLoT = time[tlR]
        if not na(tlPH):
            if not na(tlPrevHi) and tlPrevHi > tlPH:
                array.push(tls, tlMake(False, tlPrevHiT, tlPrevHi, time[tlR], tlPH))
            tlPrevHi = tlPH
            tlPrevHiT = time[tlR]
        if not tlHist or barstate.isrealtime:
            while array.size(tls) > tlLast:
                polyline.delete(array.shift(tls))
        while array.size(tls) > 55:
            polyline.delete(array.shift(tls))

    def edgeTablePos(p):
        __block_result_8__ = na
        __switch__ = p
        if __switch__ == "Top Left":
            __block_result_8__ = position.top_left
        elif __switch__ == "Middle Right":
            __block_result_8__ = position.middle_right
        elif __switch__ == "Top Center":
            __block_result_8__ = position.top_center
        elif __switch__ == "Top Right":
            __block_result_8__ = position.top_right
        elif __switch__ == "Middle Left":
            __block_result_8__ = position.middle_left
        elif __switch__ == "Middle Center":
            __block_result_8__ = position.middle_center
        elif __switch__ == "Bottom Left":
            __block_result_8__ = position.bottom_left
        elif __switch__ == "Bottom Center":
            __block_result_8__ = position.bottom_center
        else:
            __block_result_8__ = position.bottom_right
        return __block_result_8__

    capT: Persistent[Table] = na(Table)
    if not (showCAP and showTables) and (not na(capT)):
        table.delete(capT)
        capT = na
    if showCAP and showTables and barstate.islast:
        if na(capT):
            capT = table.new(edgeTablePos(capPos), 3, 50, bgcolor=color.new('#B2B5BE'), frame_color=color.new('#464646'), frame_width=2, border_width=2)
        hdrBg = color.new(color.gray, 38)
        table.cell(capT, 0, 1, 'Total Capital', text_color=color.new('#000000'), bgcolor=hdrBg, text_size=size.normal)
        table.cell(capT, 1, 1, string.tostring(capital, '#') + ' $', text_color=color.new('#363A45'), bgcolor=color.new('#DBDBDB'), text_size=size.normal)
        table.cell(capT, 0, 2, 'Risk Per Trade', text_color=color.new('#000000'), bgcolor=hdrBg, text_size=size.normal)
        table.cell(capT, 1, 2, string.tostring(capital * riskPct / 100, '#') + ' $', text_color=color.new('#363A45'), bgcolor=color.new('#DBDBDB'), text_size=size.normal)
        table.cell(capT, 0, 3, 'Profit Per Trade', text_color=color.new('#000000'), bgcolor=hdrBg, text_size=size.normal)
        table.cell(capT, 1, 3, string.tostring(capital * riskPct / 100 * rrRatio, '#') + ' $', text_color=color.new('#363A45'), bgcolor=color.new('#DBDBDB'), text_size=size.normal)
        table.cell(capT, 0, 4, 'Trade Capital', text_color=color.new('#000000'), bgcolor=hdrBg, text_size=size.normal)
        table.cell(capT, 1, 4, string.tostring(capital * riskPct / slPct, '#') + ' $', text_color=color.new('#363A45'), bgcolor=color.new('#DBDBDB'), text_size=size.normal)

    def edgeTxtSize(s):
        __block_result_9__ = na
        __switch__ = s
        if __switch__ == "Tiny":
            __block_result_9__ = size.tiny
        elif __switch__ == "Small":
            __block_result_9__ = size.small
        elif __switch__ == "Normal":
            __block_result_9__ = size.normal
        else:
            __block_result_9__ = size.auto
        return __block_result_9__

    def edgeVal(sym):
        v1, dsc, tk = request.security(sym, 'D', (close * volume, syminfo.description, syminfo.ticker), ignore_invalid_symbol=True)
        return (v1, dsc, tk)

    v01, d01, t01 = edgeVal(s01)
    v02, d02, t02 = edgeVal(s02)
    v03, d03, t03 = edgeVal(s03)
    v04, d04, t04 = edgeVal(s04)
    v05, d05, t05 = edgeVal(s05)
    v06, d06, t06 = edgeVal(s06)
    v07, d07, t07 = edgeVal(s07)
    v08, d08, t08 = edgeVal(s08)
    v09, d09, t09 = edgeVal(s09)
    v10, d10, t10 = edgeVal(s10)
    v11, d11, t11 = edgeVal(s11)
    v12, d12, t12 = edgeVal(s12)
    v13, d13, t13 = edgeVal(s13)
    v14, d14, t14 = edgeVal(s14)
    v15, d15, t15 = edgeVal(s15)
    v16, d16, t16 = edgeVal(s16)
    v17, d17, t17 = edgeVal(s17)
    v18, d18, t18 = edgeVal(s18)
    v19, d19, t19 = edgeVal(s19)
    v20, d20, t20 = edgeVal(s20)
    v21, d21, t21 = edgeVal(s21)
    v22, d22, t22 = edgeVal(s22)
    v23, d23, t23 = edgeVal(s23)
    v24, d24, t24 = edgeVal(s24)
    v25, d25, t25 = edgeVal(s25)
    v26, d26, t26 = edgeVal(s26)
    v27, d27, t27 = edgeVal(s27)
    v28, d28, t28 = edgeVal(s28)
    v29, d29, t29 = edgeVal(s29)
    v30, d30, t30 = edgeVal(s30)
    v31, d31, t31 = edgeVal(s31)
    v32, d32, t32 = edgeVal(s32)
    v33, d33, t33 = edgeVal(s33)
    v34, d34, t34 = edgeVal(s34)
    v35, d35, t35 = edgeVal(s35)
    v36, d36, t36 = edgeVal(s36)
    v37, d37, t37 = edgeVal(s37)
    v38, d38, t38 = edgeVal(s38)
    v39, d39, t39 = edgeVal(s39)
    v40, d40, t40 = edgeVal(s40)

    edgeT32: Persistent[list[float]] = array.from_items(0.0, 0.05000000074505806, 0.10000000149011612, 0.15000000596046448, 0.20000000298023224, 0.25, 0.30000001192092896, 0.3499999940395355, 0.4000000059604645, 0.44999998807907104, 0.5, 0.550000011920929, 0.6000000238418579, 0.6499999761581421, 0.699999988079071, 0.75, 0.800000011920929, 0.8500000238418579, 0.8999999761581421, 0.949999988079071, 1.0)
    def edgeGrad(v: int, a: Color, b: Color):
        t = array.get(edgeT32, math.max(0, math.min(20, v)))
        return color.rgb(math.floor(color.r(a) + (color.r(b) - color.r(a)) * t), math.floor(color.g(a) + (color.g(b) - color.g(a)) * t), math.floor(color.b(a) + (color.b(b) - color.b(a)) * t))

    def edgeAdd(en: bool, tk: str, dsc: str, va: float, tks: list[str], dscs: list[str], vas: list[float]):
        __block_result_10__ = na
        if en and (not na(va)):
            array.push(tks, tk)
            array.push(dscs, dsc)
            __block_result_10__ = array.push(vas, va)
        return __block_result_10__

    edgeT: Persistent[Table] = na(Table)
    if not (showEDGE and showTables) and (not na(edgeT)):
        table.delete(edgeT)
        edgeT = na
    if showEDGE and showTables and barstate.islast:
        tks: list[str] = array.new_string()
        dscs: list[str] = array.new_string()
        vas: list[float] = array.new_float()
        edgeAdd(e01, t01, d01, v01, tks, dscs, vas)
        edgeAdd(e02, t02, d02, v02, tks, dscs, vas)
        edgeAdd(e03, t03, d03, v03, tks, dscs, vas)
        edgeAdd(e04, t04, d04, v04, tks, dscs, vas)
        edgeAdd(e05, t05, d05, v05, tks, dscs, vas)
        edgeAdd(e06, t06, d06, v06, tks, dscs, vas)
        edgeAdd(e07, t07, d07, v07, tks, dscs, vas)
        edgeAdd(e08, t08, d08, v08, tks, dscs, vas)
        edgeAdd(e09, t09, d09, v09, tks, dscs, vas)
        edgeAdd(e10, t10, d10, v10, tks, dscs, vas)
        edgeAdd(e11, t11, d11, v11, tks, dscs, vas)
        edgeAdd(e12, t12, d12, v12, tks, dscs, vas)
        edgeAdd(e13, t13, d13, v13, tks, dscs, vas)
        edgeAdd(e14, t14, d14, v14, tks, dscs, vas)
        edgeAdd(e15, t15, d15, v15, tks, dscs, vas)
        edgeAdd(e16, t16, d16, v16, tks, dscs, vas)
        edgeAdd(e17, t17, d17, v17, tks, dscs, vas)
        edgeAdd(e18, t18, d18, v18, tks, dscs, vas)
        edgeAdd(e19, t19, d19, v19, tks, dscs, vas)
        edgeAdd(e20, t20, d20, v20, tks, dscs, vas)
        edgeAdd(e21, t21, d21, v21, tks, dscs, vas)
        edgeAdd(e22, t22, d22, v22, tks, dscs, vas)
        edgeAdd(e23, t23, d23, v23, tks, dscs, vas)
        edgeAdd(e24, t24, d24, v24, tks, dscs, vas)
        edgeAdd(e25, t25, d25, v25, tks, dscs, vas)
        edgeAdd(e26, t26, d26, v26, tks, dscs, vas)
        edgeAdd(e27, t27, d27, v27, tks, dscs, vas)
        edgeAdd(e28, t28, d28, v28, tks, dscs, vas)
        edgeAdd(e29, t29, d29, v29, tks, dscs, vas)
        edgeAdd(e30, t30, d30, v30, tks, dscs, vas)
        edgeAdd(e31, t31, d31, v31, tks, dscs, vas)
        edgeAdd(e32, t32, d32, v32, tks, dscs, vas)
        edgeAdd(e33, t33, d33, v33, tks, dscs, vas)
        edgeAdd(e34, t34, d34, v34, tks, dscs, vas)
        edgeAdd(e35, t35, d35, v35, tks, dscs, vas)
        edgeAdd(e36, t36, d36, v36, tks, dscs, vas)
        edgeAdd(e37, t37, d37, v37, tks, dscs, vas)
        edgeAdd(e38, t38, d38, v38, tks, dscs, vas)
        edgeAdd(e39, t39, d39, v39, tks, dscs, vas)
        edgeAdd(e40, t40, d40, v40, tks, dscs, vas)
        n = array.size(tks)
        groups = 2 if n > 20 else 1
        perCol = math.ceil(n / 2.0) if groups == 2 else n
        cols = groups * 2
        edgeT = table.new(edgeTablePos(edgePos), cols, perCol + 2, frame_color=color.new(color.new('#23DEE1'), 60), frame_width=2, border_width=2)
        ts_ = edgeTxtSize(edgeSize)
        hdr = color.new(color.new('#2F319B'), 60)
        for c_ in pine_range(0, cols - 1):
            table.cell(edgeT, c_, 0, '(EDGE) Volume Screener' if c_ == 0 else '', text_color=color.new('#D2D2D2'), bgcolor=hdr, text_size=ts_)
        if cols > 1:
            table.merge_cells(edgeT, 0, 0, cols - 1, 0)
        for c_ in pine_range(0, cols - 1):
            table.cell(edgeT, c_, 1, 'Symbol' if c_ % 2 == 0 else 'Total Trading Volume', text_color=color.new('#000000'), bgcolor=color.new(color.gray, 38), text_size=ts_)
        if n > 0:
            for k in pine_range(0, n - 1):
                grp = 1 if k >= perCol else 0
                row = 2 + k - grp * perCol
                va = array.get(vas, k)
                symC = edgeGrad(row, color.new('#23DEE1'), color.new('#311B92')) if grp == 0 else edgeGrad(row, color.new('#311B92'), color.new('#23DEE1'))
                volC = edgeGrad(k, color.red, color.new('#D60404')) if va < edgeCap * 1000000 else edgeGrad(k, color.new('#00E676'), color.green)
                table.cell(edgeT, grp * 2, row, array.get(tks, k), text_color=color.new('#D2D2D2'), bgcolor=color.new(symC, 60), text_size=ts_, tooltip=array.get(dscs, k))
                table.cell(edgeT, grp * 2 + 1, row, '$' + string.tostring(va, '#,###.00'), text_color=color.new('#D2D2D2'), bgcolor=color.new(volC, 60), text_size=ts_)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)