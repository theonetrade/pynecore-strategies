"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, close,
    color, display, fill, fixnan, high, hl2, hlc3, hlcc4, input, location, low, math, matrix, na,
    nz, ohlc4, open, plot, plotshape, position, request, script, shape, size, strategy, string,
    syminfo, ta, table, ticker, time, timeframe, timestamp, volume
)
from pynecore.types import Color, IBPersistent, Matrix, NA, Persistent, Series, Table
import lib.loxx.loxxexpandedsourcetypes.v4 as loxxexpandedsourcetypes


@script.strategy('Strategy Myth-Busting #12 - OSGFC+SuperTrend - [MYN]', max_bars_back=5000, overlay=True, pyramiding=0, initial_capital=1000, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=10.0, commission_value=0.075, use_bar_magnifier=False, margin_long=0, margin_short=0, close_by_id=True)
def main(
    smthtype=input.string('Kaufman', 'Heiken-Ashi Better Smoothing', options=('AMA', 'T3', 'Kaufman'), group='One-Sided Gaussian Filter w/ Channels'),
    srcoption=input.string('Close', 'Source', group='One-Sided Gaussian Filter w/ Channels', options=('Close', 'Open', 'High', 'Low', 'Median', 'Typical', 'Weighted', 'Average', 'Average Median Body', 'Trend Biased', 'Trend Biased (Extreme)', 'HA Close', 'HA Open', 'HA High', 'HA Low', 'HA Median', 'HA Typical', 'HA Weighted', 'HA Average', 'HA Average Median Body', 'HA Trend Biased', 'HA Trend Biased (Extreme)', 'HAB Close', 'HAB Open', 'HAB High', 'HAB Low', 'HAB Median', 'HAB Typical', 'HAB Weighted', 'HAB Average', 'HAB Average Median Body', 'HAB Trend Biased', 'HAB Trend Biased (Extreme)')),
    smthper=input.int(10, 'Guassian Levels Depth', maxval=100, group='Basic Settings'),
    extrasmthper=input.int(10, 'Extra Smoothing (2-Pole Ehlers Super Smoother) Period', group='Basic Settings'),
    atrper=input.int(21, 'ATR Period', group='Basic Settings'),
    mult=input.float(0.628, 'ATR Multiplier', group='Basic Settings'),
    colorbars=input.bool(True, 'Color bars?', group='UI Options'),
    showsignals=input.bool(True, 'Show signals?', group='UI Options'),
    kfl=input.float(0.666, title='* Kaufman\'s Adaptive MA (KAMA) Only - Fast End', group='Moving Average Inputs'),
    ksl=input.float(0.0645, title='* Kaufman\'s Adaptive MA (KAMA) Only - Slow End', group='Moving Average Inputs'),
    amafl=input.int(2, title='* Adaptive Moving Average (AMA) Only - Fast', group='Moving Average Inputs'),
    amasl=input.int(30, title='* Adaptive Moving Average (AMA) Only - Slow', group='Moving Average Inputs'),
    i_numLookbackBarsOSGFC=input(0, title='Number of bars to look back to validate Trend'),
    atrPeriod1=input(10, 'ATR Length', group='SuperTrend'),
    factor=input.float(3.0, 'Factor', step=0.01),
    i_numLookbackBarsST=input(0, title='Number of bars to look back to validate Trend'),
    adxEnabled=input.bool(defval=False, title='Average Directional Index (ADX)', tooltip='', group='ADX'),
    adxlen=input(14, title='ADX Smoothing', group='ADX'),
    adxdilen=input(14, title='DI Length', group='ADX'),
    adxabove=input(25, title='ADX Threshold', group='ADX'),
    useStartPeriodTime=input.bool(True, 'Start', group='Date Range', inline='Start Period'),
    startPeriodTime=input.time(timestamp('1 Jan 2019'), '', group='Date Range', inline='Start Period'),
    useEndPeriodTime=input.bool(True, 'End', group='Date Range', inline='End Period'),
    endPeriodTime=input.time(timestamp('31 Dec 2030'), '', group='Date Range', inline='End Period'),
    tradeDirection=input.string('Long and Short', title='Trade Direction', options=('Long and Short', 'Long Only', 'Short Only'), group='Trade Direction'),
    tp1=input.float(title='Take Profit 1 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 1'),
    q1=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 1'),
    tp2=input.float(title='Take Profit 2 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 2'),
    q2=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 2'),
    tp3=input.float(title='Take Profit 3 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 3'),
    q3=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 3'),
    tp4=input.float(title='Take Profit 4 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit'),
    __input_32__=input.float(title='Stop Loss (%)', defval=999, minval=0.01, group='Stop Loss'),
    leverage=input.float(1, 'Leverage', step=0.5, group='Leverage'),
    alertSyntaxPrefix=input.string(defval='CRYPTANEX_99FTX_Strategy-Name-Here', title='Alert Syntax Prefix', group='ProfitView Alert Syntax'),
    showDashboard=input.bool(group='Dashboard', title='Show Dashboard', defval=True)
):
    greencolor: Color = color.new('#2DD204')
    redcolor: Color = color.new('#D2042D')
    def _twopoless(src: float, len: int):
        a1: float = 0.0
        b1: float = 0.0
        coef1: float = 0.0
        coef2: float = 0.0
        coef3: float = 0.0
        filt: Series[float] = 0.0
        trig: float = 0.0
        a1 = math.exp(-1.414 * math.pi / len)
        b1 = 2 * a1 * math.cos(1.414 * math.pi / len)
        coef2 = b1
        coef3 = -a1 * a1
        coef1 = 1 - coef2 - coef3
        filt = coef1 * src + coef2 * nz(filt[1]) + coef3 * nz(filt[2])
        filt = src if bar_index < 3 else filt
        return filt

    def _gaussian(size__ren__, x):
        out = math.exp(-x * x * 9 / ((size__ren__ + 1) * (size__ren__ + 1)))
        return out

    def _fiblevels(len):
        arr_levels: list[float] = array.new_float(len, 0.0)
        t1: int = 0
        t2: int = 1
        nxt = t1 + t2
        for i in pine_range(0, len - 1, 1):
            array.set(arr_levels, i, nxt)
            t1 = t2
            t2 = nxt
            nxt = t1 + t2
        return arr_levels

    def _gaussout(levels):
        perin = array.size(levels)
        arr_gauss: Matrix[float] = matrix.new(perin, perin, 0.0)
        for k in pine_range(0, array.size(levels) - 1, 1):
            sum: float = 0.0
            for i in pine_range(0, perin - 1, 1):
                if i >= array.get(levels, k):
                    break
                matrix.set(arr_gauss, i, k, _gaussian(array.get(levels, k), i))
                sum = sum + matrix.get(arr_gauss, i, k)
            for i in pine_range(0, perin - 1, 1):
                if i >= array.get(levels, k):
                    break
                temp = matrix.get(arr_gauss, i, k) / sum
                matrix.set(arr_gauss, i, k, temp)
        return arr_gauss

    def _smthMA(level, src: Series, per__00000027__):
        sum: float = 0.0
        lvltemp = _fiblevels(per__00000027__)
        gtemp = _gaussout(lvltemp)
        for i in pine_range(0, matrix.rows(gtemp) - 1, 1):
            sum = sum + matrix.get(gtemp, i, level) * nz(src[i])
        return sum

    haclose = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
    haopen = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open)
    hahigh = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high)
    halow = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low)
    hamedian = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hl2)
    hatypical = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hlc3)
    haweighted = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hlcc4)
    haaverage = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, ohlc4)
    __block_result__ = na
    __switch__ = srcoption
    if __switch__ == 'Close':
        __block_result__ = loxxexpandedsourcetypes.rclose()
    elif __switch__ == 'Open':
        __block_result__ = loxxexpandedsourcetypes.ropen()
    elif __switch__ == 'High':
        __block_result__ = loxxexpandedsourcetypes.rhigh()
    elif __switch__ == 'Low':
        __block_result__ = loxxexpandedsourcetypes.rlow()
    elif __switch__ == 'Median':
        __block_result__ = loxxexpandedsourcetypes.rmedian()
    elif __switch__ == 'Typical':
        __block_result__ = loxxexpandedsourcetypes.rtypical()
    elif __switch__ == 'Weighted':
        __block_result__ = loxxexpandedsourcetypes.rweighted()
    elif __switch__ == 'Average':
        __block_result__ = loxxexpandedsourcetypes.raverage()
    elif __switch__ == 'Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.ravemedbody()
    elif __switch__ == 'Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.rtrendb()
    elif __switch__ == 'Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.rtrendbext()
    elif __switch__ == 'HA Close':
        __block_result__ = loxxexpandedsourcetypes.haclose(haclose)
    elif __switch__ == 'HA Open':
        __block_result__ = loxxexpandedsourcetypes.haopen(haopen)
    elif __switch__ == 'HA High':
        __block_result__ = loxxexpandedsourcetypes.hahigh(hahigh)
    elif __switch__ == 'HA Low':
        __block_result__ = loxxexpandedsourcetypes.halow(halow)
    elif __switch__ == 'HA Median':
        __block_result__ = loxxexpandedsourcetypes.hamedian(hamedian)
    elif __switch__ == 'HA Typical':
        __block_result__ = loxxexpandedsourcetypes.hatypical(hatypical)
    elif __switch__ == 'HA Weighted':
        __block_result__ = loxxexpandedsourcetypes.haweighted(haweighted)
    elif __switch__ == 'HA Average':
        __block_result__ = loxxexpandedsourcetypes.haaverage(haaverage)
    elif __switch__ == 'HA Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.haavemedbody(haclose, haopen)
    elif __switch__ == 'HA Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.hatrendb(haclose, haopen, hahigh, halow)
    elif __switch__ == 'HA Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.hatrendbext(haclose, haopen, hahigh, halow)
    elif __switch__ == 'HAB Close':
        __block_result__ = loxxexpandedsourcetypes.habclose(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Open':
        __block_result__ = loxxexpandedsourcetypes.habopen(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB High':
        __block_result__ = loxxexpandedsourcetypes.habhigh(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Low':
        __block_result__ = loxxexpandedsourcetypes.hablow(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Median':
        __block_result__ = loxxexpandedsourcetypes.habmedian(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Typical':
        __block_result__ = loxxexpandedsourcetypes.habtypical(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Weighted':
        __block_result__ = loxxexpandedsourcetypes.habweighted(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Average':
        __block_result__ = loxxexpandedsourcetypes.habaverage(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.habavemedbody(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.habtrendb(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.habtrendbext(smthtype, amafl, amasl, kfl, ksl)
    else:
        __block_result__ = haclose
    src: float = __block_result__
    lmax = smthper + 1
    out1 = _smthMA(smthper, src, lmax)
    out: Series = _twopoless(out1, extrasmthper)
    sig = out[1]
    colorout = greencolor if out > sig else redcolor
    atr = ta.atr(atrper)
    smax = out + atr * mult
    smin = out - atr * mult
    plot(smax, color=color.silver if bar_index % 2 else na, linewidth=1)
    plot(smin, color=color.silver if bar_index % 2 else na, linewidth=1)
    plot(out, 'GMA', color=colorout, linewidth=4)
    barcolor(colorout if colorbars else na)
    goLong = ta.crossover(out, sig)
    goShort = ta.crossunder(out, sig)
    plotshape(goLong and showsignals, title='Long', color=color.yellow, textcolor=color.yellow, text='L', style=shape.triangleup, location=location.belowbar, size=size.tiny)
    plotshape(goShort and showsignals, title='Short', color=color.fuchsia, textcolor=color.fuchsia, text='S', style=shape.triangledown, location=location.abovebar, size=size.tiny)
    alertcondition(goLong, title='Long', message='One-Sided Gaussian Filter w/ Channels [Loxx]: Long\nSymbol: {{ticker}}\nPrice: {{close}}')
    alertcondition(goShort, title='Short', message='One-Sided Gaussian Filter w/ Channels [Loxx]: Short\nSymbol: {{ticker}}\nPrice: {{close}}')
    OSGFCLongEntry = goLong
    OSGFCShortgEntry = goShort
    barssince_1 = ta.barssince(OSGFCShortgEntry)
    OSGFCLongEntryFinal = goLong and barssince_1 > i_numLookbackBarsOSGFC
    barssince_2 = ta.barssince(OSGFCLongEntry)
    OSGFCShortgEntryFinal = goShort and barssince_2 > i_numLookbackBarsOSGFC
    OSGFCLongClose = OSGFCShortgEntry
    OSGFCShortClose = OSGFCLongEntry
    supertrend1, direction1 = ta.supertrend(factor, atrPeriod1)
    bodyMiddle = plot((open + close) / 2, display=display.none)
    upTrend = plot(supertrend1 if direction1 < 0 else na, 'Up Trend', color=color.green, style=plot.style_linebr)
    downTrend = plot(na if direction1 < 0 else supertrend1, 'Down Trend', color=color.red, style=plot.style_linebr)
    fill(bodyMiddle, upTrend, color.new(color.green, 90), fillgaps=False)
    fill(bodyMiddle, downTrend, color.new(color.red, 90), fillgaps=False)
    superTrendLongEntry = direction1 < 0
    superTrendShortEntry = direction1 > 0
    barssince_3 = ta.barssince(superTrendShortEntry)
    superTrendLongEntryFinal = superTrendLongEntry and barssince_3 > i_numLookbackBarsST
    barssince_4 = ta.barssince(superTrendLongEntry)
    superTrendShortEntryFinal = superTrendShortEntry and barssince_4 > i_numLookbackBarsST
    longCondition = OSGFCLongEntryFinal and superTrendLongEntryFinal
    shortCondition = OSGFCShortgEntryFinal and superTrendShortEntryFinal
    closeLongCondition = OSGFCLongClose
    closeShortCondition = OSGFCShortClose
    def adxdirmov(len):
        adxup = ta.change(high)
        adxdown = -ta.change(low)
        adxplusDM = na if na(adxup) else adxup if adxup > adxdown and adxup > 0 else 0
        adxminusDM = na if na(adxdown) else adxdown if adxdown > adxup and adxdown > 0 else 0
        adxtruerange = ta.rma(ta.tr, len)
        adxplus = fixnan(100 * ta.rma(adxplusDM, len) / adxtruerange)
        adxminus = fixnan(100 * ta.rma(adxminusDM, len) / adxtruerange)
        return (adxplus, adxminus)

    def adx(adxdilen, adxlen):
        adxplus, adxminus = adxdirmov(adxdilen)
        adxsum = adxplus + adxminus
        adx__000000b6__ = 100 * ta.rma(math.abs(adxplus - adxminus) / (1 if adxsum == 0 else adxsum), adxlen)
        return adx__000000b6__

    adxsig = adx(adxdilen, adxlen) if adxEnabled else na
    isADXEnabledAndAboveThreshold = adxsig > adxabove if adxEnabled else True
    start = startPeriodTime >= time if useStartPeriodTime else False
    end = endPeriodTime <= time if useEndPeriodTime else False
    calcPeriod = not start and (not end)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    stoplossPercent = __input_32__ * 0.01
    slLongClose = close < strategy.position_avg_price * (1 - stoplossPercent)
    slShortClose = close > strategy.position_avg_price * (1 + stoplossPercent)
    contracts = math.min(math.max(1e-06, strategy.equity / close * leverage), 1000000000)
    isInLongPosition = strategy.position_size > 0
    isInShortPosition = strategy.position_size < 0
    alertSyntaxBase = alertSyntaxPrefix + '\n#' + string.tostring(open) + ',' + string.tostring(high) + ',' + string.tostring(low) + ',' + string.tostring(close) + ',' + string.tostring(volume) + ','
    longConditionCalc = longCondition and isADXEnabledAndAboveThreshold
    shortConditionCalc = shortCondition and isADXEnabledAndAboveThreshold
    if calcPeriod:
        if longConditionCalc and tradeDirection != 'Short Only' and (isInLongPosition == False):
            strategy.entry('Long', strategy.long, qty=contracts)
            alert(message=alertSyntaxBase + 'side:long', freq=alert.freq_once_per_bar_close)
        if shortConditionCalc and tradeDirection != 'Long Only' and (isInShortPosition == False):
            strategy.entry('Short', strategy.short, qty=contracts)
            alert(message=alertSyntaxBase + 'side:short', freq=alert.freq_once_per_bar_close)
        strategy.exit('TP1', qty_percent=q1, profit=per(tp1))
        strategy.exit('TP2', qty_percent=q2, profit=per(tp2))
        strategy.exit('TP3', qty_percent=q3, profit=per(tp3))
        strategy.exit('TP4', profit=per(tp4))
        if slLongClose:
            strategy.close('Long', qty_percent=100, comment='SL Long')
        if slShortClose:
            strategy.close('Short', qty_percent=100, comment='SL Short')
        if closeLongCondition or closeShortCondition:
            strategy.close_all(comment='Close Postion')
    def f_fillCell(_table, _column, _row, _title, _value, _bgcolor, _txtcolor):
        _cellText = _title + '\n' + _value
        return table.cell(_table, _column, _row, _cellText, bgcolor=_bgcolor, text_color=_txtcolor, text_size=size.auto)

    if showDashboard:
        bgcolor__ren__: Persistent = color.new(color.black, 0)
        newWin = strategy.wintrades > strategy.wintrades[1] and strategy.losstrades == strategy.losstrades[1] and (strategy.eventrades == strategy.eventrades[1])
        newLoss = strategy.wintrades == strategy.wintrades[1] and strategy.losstrades > strategy.losstrades[1] and (strategy.eventrades == strategy.eventrades[1])
        winRow: IBPersistent[int] = 0
        lossRow: IBPersistent[int] = 0
        maxWinRow: IBPersistent[int] = 0
        maxLossRow: IBPersistent[int] = 0
        if newWin:
            lossRow = 0
            winRow = winRow + 1
        if winRow > maxWinRow:
            maxWinRow = winRow
        if newLoss:
            winRow = 0
            lossRow = lossRow + 1
        if lossRow > maxLossRow:
            maxLossRow = lossRow
        dashTable: Persistent[Table] = table.new(position.bottom_right, 1, 15, border_width=1)
        if barstate.islastconfirmedhistory:
            dollarReturn = strategy.netprofit
            f_fillCell(dashTable, 0, 0, 'Start:', string.format('{0,date,long}', strategy.closedtrades.entry_time(0)), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 1, 'End:', string.format('{0,date,long}', strategy.opentrades.entry_time(0)), bgcolor__ren__, color.white)
            _profit = strategy.netprofit / strategy.initial_capital * 100
            f_fillCell(dashTable, 0, 2, 'Net Profit:', string.tostring(_profit, '##.##') + '%', color.green if _profit > 0 else color.red, color.white)
            _numOfDaysInStrategy = (strategy.opentrades.entry_time(0) - strategy.closedtrades.entry_time(0)) / (1000 * 3600 * 24)
            f_fillCell(dashTable, 0, 3, 'Percent Per Day', string.tostring(_profit / _numOfDaysInStrategy, '#########################.#####') + '%', color.green if _profit > 0 else color.red, color.white)
            _winRate = strategy.wintrades / strategy.closedtrades * 100
            f_fillCell(dashTable, 0, 4, 'Percent Profitable:', string.tostring(_winRate, '##.##') + '%', color.red if _winRate < 50 else color.new('#999900') if _winRate < 75 else color.green, color.white)
            f_fillCell(dashTable, 0, 5, 'Profit Factor:', string.tostring(strategy.grossprofit / strategy.grossloss, '##.###'), color.green if strategy.grossprofit > strategy.grossloss else color.red, color.white)
            f_fillCell(dashTable, 0, 6, 'Total Trades:', string.tostring(strategy.closedtrades), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 8, 'Max Wins In A Row:', string.tostring(maxWinRow, '######'), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 9, 'Max Losses In A Row:', string.tostring(maxLossRow, '######'), bgcolor__ren__, color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
