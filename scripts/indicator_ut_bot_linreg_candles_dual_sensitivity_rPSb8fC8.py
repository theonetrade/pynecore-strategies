"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, close,
    color, high, input, label, line, linefill, location, low, math, na, nz, open, plot, plotcandle,
    plotshape, position, request, script, shape, size, string, syminfo, ta, table, text, timeframe,
    volume
)
from pynecore.types import Label, Line, LineFill, NA, Persistent, PersistentSeries, Series, Table


@udt
class level:
    top: float = na(float)
    bot: float = na(float)
    start: int = na(int)


@udt
class drawing:
    top: Line = na(Line)
    bot: Line = na(Line)
    fill__ren__: LineFill = na(LineFill)
    lbl: Label = na(Label)


groupUT: str = "UT Bot"
groupZones: str = "Longevity Zones"
groupAdd: str = "Add-ons (Panel & S/R)"
groupOsc: str = "Oscillator Settings"


@script.indicator("UT Bot + LinReg Candles + Longevity Zones + S/R + Dashboard", overlay=True, max_labels_count=500, max_lines_count=500, max_bars_back=5000)
def main(
    a_buy=input.float(2, "Buy Sensitivity (Multiplier)", group=groupUT, minval=0),
    c_buy=input.int(1, "Buy ATR Period (0 = disable)", group=groupUT, minval=0),
    a_sell=input.float(2, "Sell Sensitivity (Multiplier)", group=groupUT, minval=0),
    c_sell=input.int(1, "Sell ATR Period (0 = disable)", group=groupUT, minval=0),
    showTrailBuy=input.bool(False, "Show Buy Trailing Line", group=groupUT),
    showTrailSell=input.bool(False, "Show Sell Trailing Line", group=groupUT),
    signal_length=input.int(7, "Signal Smoothing", minval=1, maxval=200, group="LinReg"),
    sma_signal=input.bool(True, "Simple MA (Signal Line)", group="LinReg"),
    lin_reg=input.bool(True, "Use LinReg", group="LinReg"),
    linreg_length=input.int(11, "Linear Regression Length", minval=1, maxval=200, group="LinReg"),
    showZones=input.bool(True, "Show Longevity Zones", group=groupZones),
    len_z=input.int(5, "Longevity Length", group=groupZones),
    col_upper=input.color(color.new(color.red, 75), "Upper Zone Color", group=groupZones),
    col_lower=input.color(color.new(color.green, 75), "Lower Zone Color", group=groupZones),
    lab_pos=input.string("LastBar", "Labels Position", options=("Root", "LastBar"), group=groupZones),
    labelOffsetBars=input.int(10, "Label Offset (bars)", group=groupZones, minval=10, maxval=500),
    srLines=input.bool(False, "Support & Resistance Lines", group=groupAdd),
    dashOn=input.bool(True, "Dashboard Panel", group=groupAdd),
    dashShiftBars=input.int(60, "Panel Right Shift (bars)", group=groupAdd, minval=40, maxval=200),
    dashColor=input.color(color.new(color.new('#8FD46D'), 80), "Panel Background", inline="dash", group=groupAdd),
    dashTextColor=input.color(color.white, "Text Color", inline="dash", group=groupAdd),
    volMaLen=input.int(20, "Volume MA Length", group=groupAdd, minval=1),
    panelAnchorBars=input.int(300, "Panel anchor bars (top-right)", group=groupAdd, minval=100, maxval=9000),
    panelPadPct=input.float(0.2, "Panel vertical padding", group=groupAdd, minval=0.0, maxval=0.4, step=0.005),
    panelPlacement=input.string("Top-Right", "Dashboard Placement", options=("Top-Right", "Top-Left", "Bottom-Right", "Bottom-Left", "Bottom-Center"), group=groupAdd),
    showSR=input.bool(True, "Show Support & Resistance Lines", group="Support & Resistance"),
    macdFastLen=input.int(12, "MACD Fast Length", group=groupOsc),
    macdSlowLen=input.int(26, "MACD Slow Length", group=groupOsc),
    macdSignalLen=input.int(9, "MACD Signal Length", group=groupOsc),
    stochLen=input.int(14, "Stochastic Length", group=groupOsc),
    stochK=input.int(3, "Stoch K Smoothing", group=groupOsc),
    stochD=input.int(3, "Stoch D Smoothing", group=groupOsc)
):
    labels_at_root = lab_pos == 'LastBar'

    buyEnabled = c_buy > 0 and a_buy > 0
    sellEnabled = c_sell > 0 and a_sell > 0

    src_buy: Series = close
    ema_buy = ta.ema(src_buy, 1)
    atr_buy = ta.atr(c_buy) if buyEnabled else na
    nLoss_buy = a_buy * atr_buy if buyEnabled else na
    trail_buy: PersistentSeries[float] = na(float)
    if buyEnabled:
        if na(trail_buy[1]):
            trail_buy = src_buy - nLoss_buy
        else:
            if src_buy > trail_buy[1] and src_buy[1] > trail_buy[1]:
                trail_buy = math.max(trail_buy[1], src_buy - nLoss_buy)
            elif src_buy < trail_buy[1] and src_buy[1] < trail_buy[1]:
                trail_buy = math.min(trail_buy[1], src_buy + nLoss_buy)
            else:
                trail_buy = src_buy - nLoss_buy if src_buy > trail_buy[1] else src_buy + nLoss_buy
    else:
        trail_buy = na

    src_sell: Series = close
    ema_sell = ta.ema(src_sell, 1)
    atr_sell = ta.atr(c_sell) if sellEnabled else na
    nLoss_sell = a_sell * atr_sell if sellEnabled else na
    trail_sell: PersistentSeries[float] = na(float)
    if sellEnabled:
        if na(trail_sell[1]):
            trail_sell = src_sell + nLoss_sell
        else:
            if src_sell > trail_sell[1] and src_sell[1] > trail_sell[1]:
                trail_sell = math.max(trail_sell[1], src_sell - nLoss_sell)
            elif src_sell < trail_sell[1] and src_sell[1] < trail_sell[1]:
                trail_sell = math.min(trail_sell[1], src_sell + nLoss_sell)
            else:
                trail_sell = src_sell - nLoss_sell if src_sell > trail_sell[1] else src_sell + nLoss_sell
    else:
        trail_sell = na

    above_buy_cross = ta.crossover(ema_buy, trail_buy)
    below_sell_cross = ta.crossover(trail_sell, ema_sell)

    above_buy = buyEnabled and above_buy_cross
    buy_signal_raw = buyEnabled and src_buy > trail_buy and above_buy
    buy_signal = buy_signal_raw and barstate.isconfirmed

    below_sell = sellEnabled and below_sell_cross
    sell_signal_raw = sellEnabled and src_sell < trail_sell and below_sell
    sell_signal = sell_signal_raw and barstate.isconfirmed

    posState: Persistent[int] = 0
    buy_signal_confirmed = buyEnabled and buy_signal and (posState <= 0)
    sell_signal_confirmed = sellEnabled and sell_signal and (posState >= 0)
    if buy_signal_confirmed:
        posState = 1
    elif sell_signal_confirmed:
        posState = -1

    buy_sig_vis = buyEnabled and buy_signal_raw
    sell_sig_vis = sellEnabled and sell_signal_raw

    plotshape(buy_sig_vis, title='UT Buy', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, size=size.tiny, text='Buy')
    plotshape(sell_sig_vis, title='UT Sell', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, size=size.tiny, text='Sell')

    utColor = color.new(color.green, 75) if buy_sig_vis else color.new(color.red, 75) if sell_sig_vis else na
    barcolor(utColor)

    plot(trail_buy if showTrailBuy and buyEnabled else na, title='UT Bot Buy Trail', color=color.new(color.green, 0), linewidth=1)
    plot(trail_sell if showTrailSell and sellEnabled else na, title='UT Bot Sell Trail', color=color.new(color.red, 0), linewidth=1)

    alertcondition(buy_signal_confirmed, title='UT Long', message='UT Long')
    alertcondition(sell_signal_confirmed, title='UT Short', message='UT Short')

    _bopen = ta.linreg(open, linreg_length, 0) if lin_reg else open
    _bhigh = ta.linreg(high, linreg_length, 0) if lin_reg else high
    _blow = ta.linreg(low, linreg_length, 0) if lin_reg else low
    _bclose = ta.linreg(close, linreg_length, 0) if lin_reg else close
    signal = ta.sma(_bclose, signal_length) if sma_signal else ta.ema(_bclose, signal_length)
    inLong = posState == 1
    inShort = posState == -1
    isFlat = posState == 0
    dirUp = _bclose >= _bopen
    plotcandle(open=_bopen if inLong else na, high=_bhigh if inLong else na, low=_blow if inLong else na, close=_bclose if inLong else na, title='LinReg Long (regime)', color=color.green, wickcolor=color.green, bordercolor=color.green)
    plotcandle(open=_bopen if inShort else na, high=_bhigh if inShort else na, low=_blow if inShort else na, close=_bclose if inShort else na, title='LinReg Short (regime)', color=color.red, wickcolor=color.red, bordercolor=color.red)
    plotcandle(open=_bopen if isFlat and dirUp else na, high=_bhigh if isFlat and dirUp else na, low=_blow if isFlat and dirUp else na, close=_bclose if isFlat and dirUp else na, title='LinReg Flat Green', color=color.green, wickcolor=color.green, bordercolor=color.green)
    plotcandle(open=_bopen if isFlat and (not dirUp) else na, high=_bhigh if isFlat and (not dirUp) else na, low=_blow if isFlat and (not dirUp) else na, close=_bclose if isFlat and (not dirUp) else na, title='LinReg Flat Red', color=color.red, wickcolor=color.red, bordercolor=color.red)
    plot(signal, color=color.blue, linewidth=2, title='LinReg Signal')

    upper: Persistent[list[level]] = array.new(0, NA(level))
    lower: Persistent[list[level]] = array.new(0, NA(level))
    upperDraw: Persistent[list[drawing]] = array.new(0, NA(drawing))
    lowerDraw: Persistent[list[drawing]] = array.new(0, NA(drawing))
    h: Series = ta.highest(len_z)
    l: Series = ta.lowest(len_z)
    high_pivot = high[1] == h[1] and high < h
    low_pivot = low[1] == l[1] and low > l
    halfATR = ta.atr(20) * 0.5
    if showZones:
        if high_pivot:
            array.push(upper, level(h, h - halfATR, bar_index - 1))
        if low_pivot:
            array.push(lower, level(l + halfATR, l, bar_index - 1))
        if array.size(upper) > 10:
            array.shift(upper)
        if array.size(lower) > 10:
            array.shift(lower)
        for i in pine_range(array.size(upper) - 1, 0):
            if array.size(upper) == 0:
                break
            zUp = array.get(upper, i)
            if high > zUp.top and bar_index > zUp.start:
                array.remove(upper, i)
        for i in pine_range(array.size(lower) - 1, 0):
            if array.size(lower) == 0:
                break
            zLo = array.get(lower, i)
            if low < zLo.bot and bar_index > zLo.start:
                array.remove(lower, i)

    upperFillColor = col_upper
    lowerFillColor = col_lower
    if barstate.islast and showZones:
        if array.size(upperDraw) > 0:
            for i in pine_range(0, array.size(upperDraw) - 1):
                d__00000095__ = array.get(upperDraw, i)
                line.delete(d__00000095__.top)
                line.delete(d__00000095__.bot)
                if not na(d__00000095__.fill__ren__):
                    linefill.delete(d__00000095__.fill__ren__)
                label.delete(d__00000095__.lbl)
            array.clear(upperDraw)
        if array.size(lowerDraw) > 0:
            for i in pine_range(0, array.size(lowerDraw) - 1):
                d__000000a1__ = array.get(lowerDraw, i)
                line.delete(d__000000a1__.top)
                line.delete(d__000000a1__.bot)
                if not na(d__000000a1__.fill__ren__):
                    linefill.delete(d__000000a1__.fill__ren__)
                label.delete(d__000000a1__.lbl)
            array.clear(lowerDraw)
        if array.size(upper) > 0:
            for i in pine_range(0, array.size(upper) - 1):
                z = array.get(upper, i)
                l1 = line.new(z.start, z.top, bar_index, z.top, color=col_upper, width=8)
                l2 = line.new(z.start, z.bot, bar_index, z.bot, color=col_upper, width=8)
                f = linefill.new(l1, l2, color=upperFillColor)
                dur = bar_index - z.start
                daysTot = cast_int(dur * (timeframe.in_seconds(timeframe.period) / 86400))
                txt = string.tostring(cast_int(daysTot / 365)) + ' Y (' + string.tostring(dur) + ' bars)' if daysTot >= 365 else string.tostring(cast_int(daysTot / 30)) + ' M (' + string.tostring(dur) + ' bars)' if daysTot >= 30 else string.tostring(daysTot) + ' D (' + string.tostring(dur) + ' bars)'
                lx = z.start if labels_at_root else bar_index + labelOffsetBars
                ly = (z.top + z.bot) / 2
                lbl = label.new(lx, ly, txt, style=label.style_label_center, textcolor=color.white, color=color.new(color.black, 0))
                array.push(upperDraw, drawing(l1, l2, f, lbl))
        if array.size(lower) > 0:
            for i in pine_range(0, array.size(lower) - 1):
                z = array.get(lower, i)
                l1 = line.new(z.start, z.top, bar_index, z.top, color=col_lower, width=8)
                l2 = line.new(z.start, z.bot, bar_index, z.bot, color=col_lower, width=8)
                f = linefill.new(l1, l2, color=lowerFillColor)
                dur = bar_index - z.start
                daysTot = cast_int(dur * (timeframe.in_seconds(timeframe.period) / 86400))
                txt = string.tostring(cast_int(daysTot / 365)) + ' Y (' + string.tostring(dur) + ' bars)' if daysTot >= 365 else string.tostring(cast_int(daysTot / 30)) + ' M (' + string.tostring(dur) + ' bars)' if daysTot >= 30 else string.tostring(daysTot) + ' D (' + string.tostring(dur) + ' bars)'
                lx = z.start if labels_at_root else bar_index + labelOffsetBars
                ly = (z.top + z.bot) / 2
                lbl = label.new(lx, ly, txt, style=label.style_label_center, textcolor=color.white, color=color.new(color.black, 0))
                array.push(lowerDraw, drawing(l1, l2, f, lbl))
    elif barstate.islast:
        if array.size(upperDraw) > 0:
            for i in pine_range(0, array.size(upperDraw) - 1):
                d__000000d4__ = array.get(upperDraw, i)
                line.delete(d__000000d4__.top)
                line.delete(d__000000d4__.bot)
                if not na(d__000000d4__.fill__ren__):
                    linefill.delete(d__000000d4__.fill__ren__)
                label.delete(d__000000d4__.lbl)
            array.clear(upperDraw)
        if array.size(lowerDraw) > 0:
            for i in pine_range(0, array.size(lowerDraw) - 1):
                d__000000e0__ = array.get(lowerDraw, i)
                line.delete(d__000000e0__.top)
                line.delete(d__000000e0__.bot)
                if not na(d__000000e0__.fill__ren__):
                    linefill.delete(d__000000e0__.fill__ren__)
                label.delete(d__000000e0__.lbl)
            array.clear(lowerDraw)
    h1000 = ta.highest(high, 1000)
    h750 = ta.highest(high, 750)
    h500 = ta.highest(high, 500)
    h250 = ta.highest(high, 250)
    h100 = ta.highest(high, 100)
    h50 = ta.highest(high, 50)
    h10 = ta.highest(high, 10)
    l1000 = ta.lowest(low, 1000)
    l750 = ta.lowest(low, 750)
    l500 = ta.lowest(low, 500)
    l250 = ta.lowest(low, 250)
    l100 = ta.lowest(low, 100)
    l50 = ta.lowest(low, 50)
    l10 = ta.lowest(low, 10)
    plot(h1000 if showSR else na, title='R1', color=color.green if close > h1000 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h750 if showSR else na, title='R2', color=color.green if close > h750 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h500 if showSR else na, title='R3', color=color.green if close > h500 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h250 if showSR else na, title='R4', color=color.green if close > h250 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h100 if showSR else na, title='R5', color=color.green if close > h100 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h50 if showSR else na, title='R6', color=color.green if close > h50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h10 if showSR else na, title='R7', color=color.green if close > h10 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l1000 if showSR else na, title='S1', color=color.green if close > l1000 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l750 if showSR else na, title='S2', color=color.green if close > l750 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l500 if showSR else na, title='S3', color=color.green if close > l500 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l250 if showSR else na, title='S4', color=color.green if close > l250 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l100 if showSR else na, title='S5', color=color.green if close > l100 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l50 if showSR else na, title='S6', color=color.green if close > l50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l10 if showSR else na, title='S7', color=color.green if close > l10 else color.red, linewidth=1, offset=-9999, trackprice=True)

    def emaTrend_tf(tf):
        emaFast = request.security(syminfo.tickerid, tf, ta.ema(close, 9), barmerge.gaps_off, barmerge.lookahead_off)
        emaSlow = request.security(syminfo.tickerid, tf, ta.ema(close, 21), barmerge.gaps_off, barmerge.lookahead_off)
        return '🟢 BULL' if emaFast > emaSlow else '🔴 BEAR' if emaFast < emaSlow else '— FLAT'

    def trendStrHTF(tf):
        return emaTrend_tf(tf)

    def calcVol():
        _atr = ta.atr(14)
        _std2 = 2.0 * ta.stdev(_atr, 20)
        _sma = ta.sma(_atr, 20)
        top = _sma + _std2
        bot = _sma - _std2
        return nz(30.0 + 40.0 * ((_atr - bot) / math.max(1e-10, top - bot)), 50)

    volNow = volume
    volMA = ta.sma(volume, volMaLen)
    volBias = '🟢 Above Avg' if volNow > volMA else '🔴 Below Avg' if volNow < volMA else '— Avg'
    vwapVal = ta.vwap(close)
    vwapPos = '🟢 Price Above' if close > vwapVal else '🔴 Price Below'
    macdLine, signalLine, histLine = ta.macd(close, macdFastLen, macdSlowLen, macdSignalLen)
    macdBias = '🟢 Bullish' if macdLine > signalLine else '🔴 Bearish'
    k = ta.sma(ta.stoch(close, high, low, stochLen), stochK)
    d = ta.sma(k, stochD)
    stochPos = '🟢 Up' if k > d else '🔴 Down'
    stochState = stochPos + ' but ' + ('Overbought' if k > 80 else 'Oversold' if k < 20 else 'Neutral')
    atrNow = ta.atr(14)
    atrSma20 = ta.sma(atrNow, 20)
    atrHiLo = '🟢 High' if atrNow > atrSma20 * 1.2 else '🔴 Low' if atrNow < atrSma20 * 0.8 else '— Mid'
    todayOpen = request.security(syminfo.tickerid, 'D', open)
    todayClose = request.security(syminfo.tickerid, 'D', close)
    todayHighD = request.security(syminfo.tickerid, 'D', high)
    todayLowD = request.security(syminfo.tickerid, 'D', low)
    todayDirection = '🟢↑' if todayClose > todayOpen else '🔴↓' if todayClose < todayOpen else '➖'
    todayRangePerc = (todayHighD - todayLowD) / math.max(todayLowD, syminfo.mintick) * 100
    prevHigh = request.security(syminfo.tickerid, 'D', high[1])
    prevLow = request.security(syminfo.tickerid, 'D', low[1])
    prevOpen = request.security(syminfo.tickerid, 'D', open[1])
    prevClose = request.security(syminfo.tickerid, 'D', close[1])
    prevRangePerc = (prevHigh - prevLow) / math.max(prevLow, syminfo.mintick) * 100
    prevDayDirection = '🟢↑' if prevClose > prevOpen else '🔴↓' if prevClose < prevOpen else '➖'
    atrTpStr = string.tostring(trail_buy, '#.#####') if posState == 1 and buyEnabled else string.tostring(trail_sell, '#.#####') if posState == -1 and sellEnabled else '—'
    atrTpSide = ' (BUY)' if posState == 1 else ' (SELL)' if posState == -1 else ''

    dashTable: Persistent[Table] = na(Table)
    prevPlace: Persistent[str] = ""

    if dashOn and (na(dashTable) or panelPlacement != prevPlace):
        if not na(dashTable):
            table.clear(dashTable, 0, 0, 0, 0)
        __block_result__ = na
        __switch_1__ = panelPlacement
        if __switch_1__ == "Top-Right":
            __block_result__ = table.new(position.top_right, 1, 1, border_width=1)
        elif __switch_1__ == "Top-Left":
            __block_result__ = table.new(position.top_left, 1, 1, border_width=1)
        elif __switch_1__ == "Bottom-Right":
            __block_result__ = table.new(position.bottom_right, 1, 1, border_width=1)
        elif __switch_1__ == "Bottom-Left":
            __block_result__ = table.new(position.bottom_left, 1, 1, border_width=1)
        elif __switch_1__ == "Bottom-Center":
            __block_result__ = table.new(position.bottom_center, 1, 1, border_width=1)
        else:
            __block_result__ = table.new(position.top_right, 1, 1, border_width=1)
        dashTable = __block_result__
        prevPlace = panelPlacement

    if dashOn and (not na(dashTable)):
        panelText = '📊 MARKET STATUS' + '\n━━━━━━━━━━━━━━━━━' + '\nVolatility       | ' + string.tostring(calcVol(), '##.##') + '%' + '\nVolume           | ' + string.tostring(volNow, '#.##') + ' (' + volBias + ')' + '\nVWAP vs Price    | ' + vwapPos + '\nMACD Bias        | ' + macdBias + '\nStoch Bias       | ' + stochState + '\nRSI              | ' + string.tostring(ta.rsi(close, 14), '##.##') + '\n' + '\n📈 TREND Overall timeframes' + '\n━━━━━━━━━━━━━━━━━' + '\n 1m  | ' + trendStrHTF('1') + '    2h | ' + trendStrHTF('120') + '\n 5m  | ' + trendStrHTF('5') + '    4h | ' + trendStrHTF('240') + '\n15m  | ' + trendStrHTF('15') + '    1D | ' + trendStrHTF('D') + '\n30m  | ' + trendStrHTF('30') + '    1W | ' + trendStrHTF('W') + '\n 1h  | ' + trendStrHTF('60') + '    1M | ' + trendStrHTF('M') + '\n' + '\n💰 PRICE POSITION' + '\n━━━━━━━━━━━━━━━━━' + '\nToday’s Range %       | ' + todayDirection + ' ' + string.tostring(todayRangePerc, '##.##') + '\nYesterday’s Range %   | ' + prevDayDirection + ' ' + string.tostring(prevRangePerc, '##.##') + '\nYesterday’s High      | ' + string.tostring(prevHigh, '#.#####') + '\nYesterday’s Low       | ' + string.tostring(prevLow, '#.#####') + '\n' + '\n━━━━━━━━━━━━━━━━━' + '\n📊 ACTUAL IN TRADE PROGRESSION' + '\n━━━━━━━━━━━━━━━━━' + '\nATR state            | ' + atrHiLo + ' (' + string.tostring(atrNow, '#.###') + ')' + '\nATR Trailing stop' + atrTpSide + ' | ' + atrTpStr
        table.cell(dashTable, 0, 0, panelText, text_color=dashTextColor, text_size=size.small, text_halign=text.align_left, text_valign=text.align_top, bgcolor=dashColor)
    elif not dashOn and (not na(dashTable)):
        table.clear(dashTable, 0, 0, 0, 0)
        dashTable = na
        prevPlace = ""


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
