"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    alert, barstate, close, color, fixnan, high, hl2, input, low, math, na,
    nz, open, plot, position, request, script, size, strategy, string, syminfo, ta, table, time,
    timeframe, timestamp, volume
)
from pynecore.types import Color, IBPersistent, NA, Persistent, Series, Table


@script.strategy('Strategy Myth-Busting #6 - PSAR+MA+SQZMOM+HVI - [MYN]', max_bars_back=5000, overlay=True, pyramiding=0, initial_capital=20000, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100.0, commission_value=0.075, use_bar_magnifier=False, margin_long=0, margin_short=0, close_by_id=True)
def main(
    overrideAdaptiveSar=input(False, title='Override Adaptive PSAR', group='Adaptive Parabolic Sar'),
    TrendCodeOverRide=input(5, title='Trend Code (If Overriding Adaptive PSAR)'),
    lengthBB=input(20, title='BB Length', group='Squeeze Momentum'),
    mult=input(2.0, title='BB MultFactor'),
    lengthKC=input(20, title='KC Length'),
    multKC=input(1.5, title='KC MultFactor'),
    useTrueRange=input(True, title='Use TrueRange (KC)'),
    plot_ma_1=input.bool(True, '', inline='MA 1', group='Multi Timeframe Moving Averages'),
    ma_1_type=input.string(defval='EMA', title='MA 1', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 1', group='Multi Timeframe Moving Averages'),
    ma_1_val=input.int(200, '', minval=1, inline='MA 1', group='Multi Timeframe Moving Averages'),
    ma1_tf=input.timeframe(title='', defval='', inline='MA 1', group='Multi Timeframe Moving Averages'),
    ma_1_colour=input.color(color.green, '', inline='MA 1', group='Multi Timeframe Moving Averages'),
    plot_ma_2=input.bool(True, '', inline='MA 2', group='Multi Timeframe Moving Averages'),
    ma_2_type=input.string(defval='SMA', title='MA 2 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 2', group='Multi Timeframe Moving Averages'),
    ma_2_val=input.int(50, '', minval=1, inline='MA 2', group='Multi Timeframe Moving Averages'),
    ma2_tf=input.timeframe(title='', defval='', inline='MA 2', group='Multi Timeframe Moving Averages'),
    ma_2_colour=input.color(color.yellow, '', inline='MA 2', group='Multi Timeframe Moving Averages'),
    plot_ma_3=input.bool(False, '', inline='MA 3', group='Multi Timeframe Moving Averages'),
    ma_3_type=input.string(defval='SMA', title='MA 3 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 3', group='Multi Timeframe Moving Averages'),
    ma_3_val=input.int(1, '', minval=1, inline='MA 3', group='Multi Timeframe Moving Averages'),
    ma3_tf=input.timeframe(title='', defval='', inline='MA 3', group='Multi Timeframe Moving Averages'),
    ma_3_colour=input.color(color.black, '', inline='MA 3', group='Multi Timeframe Moving Averages'),
    plot_ma_4=input.bool(False, '', inline='MA 4', group='Multi Timeframe Moving Averages'),
    ma_4_type=input.string(defval='SMA', title='MA 4 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 4', group='Multi Timeframe Moving Averages'),
    ma_4_val=input.int(1, '', minval=1, inline='MA 4', group='Multi Timeframe Moving Averages'),
    ma4_tf=input.timeframe(title='', defval='', inline='MA 4', group='Multi Timeframe Moving Averages'),
    ma_4_colour=input.color(color.black, '', inline='MA 4', group='Multi Timeframe Moving Averages'),
    plot_ma_5=input.bool(False, '', inline='MA 5', group='Multi Timeframe Moving Averages'),
    ma_5_type=input.string(defval='SMA', title='MA 5 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 5', group='Multi Timeframe Moving Averages'),
    ma_5_val=input.int(1, '', minval=1, inline='MA 5', group='Multi Timeframe Moving Averages'),
    ma5_tf=input.timeframe(title='', defval='', inline='MA 5', group='Multi Timeframe Moving Averages'),
    ma_5_colour=input.color(color.black, '', inline='MA 5', group='Multi Timeframe Moving Averages'),
    plot_ma_6=input.bool(False, '', inline='MA 6', group='Normal Moving Averages'),
    ma_6_type=input.string(defval='SMA', title='MA 6 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 6', group='Normal Moving Averages'),
    ma_6_val=input.int(1, '', minval=1, inline='MA 6', group='Normal Moving Averages'),
    ma_6_src: Series[float] = input.source(defval=close, title='', inline='MA 6', group='Normal Moving Averages'),
    ma_6_colour=input.color(color.black, '', inline='MA 6', group='Normal Moving Averages'),
    plot_ma_7=input.bool(False, '', inline='MA 7', group='Normal Moving Averages'),
    ma_7_type=input.string(defval='SMA', title='MA 7 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 7', group='Normal Moving Averages'),
    ma_7_val=input.int(1, '', minval=1, inline='MA 7', group='Normal Moving Averages'),
    ma_7_src: Series[float] = input.source(defval=close, title='', inline='MA 7', group='Normal Moving Averages'),
    ma_7_colour=input.color(color.black, '', inline='MA 7', group='Normal Moving Averages'),
    plot_ma_8=input.bool(False, '', inline='MA 8', group='Normal Moving Averages'),
    ma_8_type=input.string(defval='SMA', title='MA 8', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 8', group='Normal Moving Averages'),
    ma_8_val=input.int(1, '', minval=1, inline='MA 8', group='Normal Moving Averages'),
    ma_8_src: Series[float] = input.source(defval=close, title='', inline='MA 8', group='Normal Moving Averages'),
    ma_8_colour=input.color(color.black, '', inline='MA 8', group='Normal Moving Averages'),
    plot_ma_9=input.bool(False, '', inline='MA 9', group='Normal Moving Averages'),
    ma_9_type=input.string(defval='SMA', title='MA 9 ', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 9', group='Normal Moving Averages'),
    ma_9_val=input.int(1, '', minval=1, inline='MA 9', group='Normal Moving Averages'),
    ma_9_src: Series[float] = input.source(defval=close, title='', inline='MA 9', group='Normal Moving Averages'),
    ma_9_colour=input.color(color.black, '', inline='MA 9', group='Normal Moving Averages'),
    plot_ma_10=input.bool(False, '', inline='MA 10', group='Normal Moving Averages'),
    ma_10_type=input.string(defval='SMA', title='MA 10', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'VWMA'), inline='MA 10', group='Normal Moving Averages'),
    ma_10_val=input.int(1, '', minval=1, inline='MA 10', group='Normal Moving Averages'),
    ma_10_src: Series[float] = input.source(defval=close, title='', inline='MA 10', group='Normal Moving Averages'),
    ma_10_colour=input.color(color.black, '', inline='MA 10', group='Normal Moving Averages'),
    lengthhvi=input(200, group='HawkEye Volume Indicator'),
    divisor=input(1),
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
    __input_75__=input.float(title='Stop Loss (%)', defval=999, minval=0.01, group='Stop Loss'),
    leverage=input.float(1, 'Leverage', step=0.5, group='Leverage'),
    alertSyntaxPrefix=input.string(defval='CRYPTANEX_99FTX_Strategy-Name-Here', title='Alert Syntax Prefix', group='ProfitView Alert Syntax'),
    showDashboard=input.bool(group='Dashboard', title='Show Dashboard', defval=True)
):
    __block_result__ = na
    __switch__ = timeframe.multiplier
    if __switch__ == 1:
        __block_result__ = 1
    elif __switch__ == 3:
        __block_result__ = 1
    elif __switch__ == 5:
        __block_result__ = 1
    elif __switch__ == 10:
        __block_result__ = 2
    elif __switch__ == 15:
        __block_result__ = 3
    elif __switch__ == 30:
        __block_result__ = 5
    elif __switch__ == 45:
        __block_result__ = 5
    elif __switch__ == 60:
        __block_result__ = 7
    elif __switch__ == 120:
        __block_result__ = 9
    elif __switch__ == 180:
        __block_result__ = 9
    elif __switch__ == 240:
        __block_result__ = 13
    elif __switch__ == 300:
        __block_result__ = 14
    elif __switch__ == 360:
        __block_result__ = 15
    else:
        __block_result__ = cast_int(4)
    trendCodeAdaptive: int = __block_result__
    startPSAR: float = 0.02
    increment: float = 0.02
    maximum = TrendCodeOverRide * 0.005 if overrideAdaptiveSar else trendCodeAdaptive * 0.005
    psar = ta.sar(startPSAR, increment, maximum)
    dir: Series = 1 if psar < close else -1
    psarColor = color.new('#00C3FF') if dir == 1 else color.new('#FF0062')
    psarPlot = plot(psar, title='PSAR', style=plot.style_circles, linewidth=3, color=psarColor)
    longColor: Persistent[Color] = color.green
    shortColor: Persistent[Color] = color.red
    PSARLongEntry = dir == 1 and dir[1] == -1
    PSARShortEntry = dir == -1 and dir[1] == 1
    source = close
    basis = ta.sma(source, lengthBB)
    dev = multKC * ta.stdev(source, lengthBB)
    upperBB = basis + dev
    lowerBB = basis - dev
    ma = ta.sma(source, lengthKC)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.sma(range_1, lengthKC)
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC
    sqzOn = lowerBB > lowerKC and upperBB < upperKC
    sqzOff = lowerBB < lowerKC and upperBB > upperKC
    noSqz = sqzOn == False and sqzOff == False
    val: Series = ta.linreg(source - math.avg(math.avg(ta.highest(high, lengthKC), ta.lowest(low, lengthKC)), ta.sma(close, lengthKC)), lengthKC, 0)
    iff_1 = color.lime if val > nz(val[1]) else color.green
    iff_2 = color.red if val < nz(val[1]) else color.maroon
    bcolor = iff_1 if val > 0 else iff_2
    scolor = color.blue if noSqz else color.black if sqzOn else color.gray
    SQZMOMLongEntry = val > 0
    SQZMOMShortEntry = val < 0
    def ma_function(source, length, type):
        __block_result_1__ = na
        if type == 'RMA':
            __block_result_1__ = ta.rma(source, length)
        elif type == 'SMA':
            __block_result_1__ = ta.sma(source, length)
        elif type == 'EMA':
            __block_result_1__ = ta.ema(source, length)
        elif type == 'WMA':
            __block_result_1__ = ta.wma(source, length)
        elif type == 'HMA':
            __block_result_2__ = na
            if length < 2:
                __block_result_2__ = ta.hma(source, 2)
            else:
                __block_result_2__ = ta.hma(source, length)
            __block_result_1__ = __block_result_2__
        else:
            __block_result_1__ = ta.vwma(source, length)
        return __block_result_1__

    ma_1 = request.security(syminfo.tickerid, ma1_tf, ma_function(close, ma_1_val, ma_1_type)) if plot_ma_1 else 0
    ma_2 = request.security(syminfo.tickerid, ma2_tf, ma_function(close, ma_2_val, ma_2_type)) if plot_ma_2 else 0
    ma_3 = request.security(syminfo.tickerid, ma3_tf, ma_function(close, ma_3_val, ma_3_type)) if plot_ma_3 else 0
    ma_4 = request.security(syminfo.tickerid, ma4_tf, ma_function(close, ma_4_val, ma_4_type)) if plot_ma_4 else 0
    ma_5 = request.security(syminfo.tickerid, ma5_tf, ma_function(close, ma_5_val, ma_5_type)) if plot_ma_5 else 0
    ma_6 = ma_function(ma_6_src, ma_6_val, ma_6_type) if plot_ma_6 else 0
    ma_7 = ma_function(ma_7_src, ma_7_val, ma_7_type) if plot_ma_7 else 0
    ma_8 = ma_function(ma_8_src, ma_8_val, ma_8_type) if plot_ma_8 else 0
    ma_9 = ma_function(ma_9_src, ma_9_val, ma_9_type) if plot_ma_9 else 0
    ma_10 = ma_function(ma_10_src, ma_10_val, ma_10_type) if plot_ma_10 else 0
    plot(ma_1 if plot_ma_1 else na, 'MA 1', ma_1_colour)
    plot(ma_2 if plot_ma_2 else na, 'MA 2', ma_2_colour)
    plot(ma_3 if plot_ma_3 else na, 'MA 3', ma_3_colour)
    plot(ma_4 if plot_ma_4 else na, 'MA 4', ma_4_colour)
    plot(ma_5 if plot_ma_5 else na, 'MA 5', ma_5_colour)
    plot(ma_6 if plot_ma_6 else na, 'MA 6', ma_6_colour)
    plot(ma_7 if plot_ma_7 else na, 'MA 7', ma_7_colour)
    plot(ma_8 if plot_ma_8 else na, 'MA 8', ma_8_colour)
    plot(ma_9 if plot_ma_9 else na, 'MA 9', ma_9_colour)
    plot(ma_10 if plot_ma_10 else na, 'MA 10', ma_10_colour)
    MALongEntry = close > ma_1 and close > ma_2 and (ma_2 > ma_1)
    MAShortEntry = close < ma_1 and close < ma_2 and (ma_2 < ma_1)
    range_1HVI = high - low
    rangeAvg = ta.sma(range_1HVI, lengthhvi)
    volumeA = ta.sma(volume, lengthhvi)
    high1 = high[1]
    low1 = low[1]
    mid1 = hl2[1]
    u1 = mid1 + (high1 - low1) / divisor
    d1 = mid1 - (high1 - low1) / divisor
    r_enabled1 = range_1HVI > rangeAvg and close < d1 and (volume > volumeA)
    r_enabled2 = close < mid1
    r_enabled = r_enabled1 or r_enabled2
    g_enabled1 = close > mid1
    g_enabled2 = range_1HVI > rangeAvg and close > u1 and (volume > volumeA)
    g_enabled3 = high > high1 and range_1HVI < rangeAvg / 1.5 and (volume < volumeA)
    g_enabled4 = low < low1 and range_1HVI < rangeAvg / 1.5 and (volume > volumeA)
    g_enabled = g_enabled1 or g_enabled2 or g_enabled3 or g_enabled4
    gr_enabled1 = range_1HVI > rangeAvg and close > d1 and (close < u1) and (volume > volumeA) and (volume < volumeA * 1.5) and (volume > volume[1])
    gr_enabled2 = range_1HVI < rangeAvg / 1.5 and volume < volumeA / 1.5
    gr_enabled3 = close > d1 and close < u1
    gr_enabled = gr_enabled1 or gr_enabled2 or gr_enabled3
    v_color = color.gray if gr_enabled else color.green if g_enabled else color.red if r_enabled else color.blue
    HVILongEntry = g_enabled
    HVIShortEntry = r_enabled
    longCondition = PSARLongEntry and MALongEntry and HVILongEntry and SQZMOMLongEntry
    shortCondition = PSARShortEntry and MAShortEntry and HVIShortEntry and SQZMOMShortEntry
    closeLongCondition: int = 0
    closeShortCondition: int = 0
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
        adx__0000009d__ = 100 * ta.rma(math.abs(adxplus - adxminus) / (1 if adxsum == 0 else adxsum), adxlen)
        return adx__0000009d__

    adxsig = adx(adxdilen, adxlen) if adxEnabled else na
    isADXEnabledAndAboveThreshold = adxsig > adxabove if adxEnabled else True
    start = startPeriodTime >= time if useStartPeriodTime else False
    end = endPeriodTime <= time if useEndPeriodTime else False
    calcPeriod = not start and (not end)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    stoplossPercent = __input_75__ * 0.01
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
        if cast_bool(closeLongCondition) or cast_bool(closeShortCondition):
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
