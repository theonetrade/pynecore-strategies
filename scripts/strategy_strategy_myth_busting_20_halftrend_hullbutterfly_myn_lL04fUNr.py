"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, close, color, fill,
    high, input, location, low, math, na, nz, open, plot, plotshape, position, script, shape, size,
    strategy, string, syminfo, ta, table, time, timeframe, timestamp, volume
)
from pynecore.types import Color, IBPersistent, NA, Persistent, PersistentSeries, Series, Table


@script.strategy('Strategy Myth-Busting #20 - HalfTrend+HullButterfly - [MYN]', max_bars_back=5000, overlay=True, pyramiding=0, initial_capital=10000, currency='NONE', default_qty_type=strategy.percent_of_equity, default_qty_value=1.0, commission_value=0.075, use_bar_magnifier=False, margin_long=0, margin_short=0, close_by_id=True)
def main(
    length=input(11, group='Hull Butterfly Oscillator'),
    mult=input(2.0, 'Levels Multiplier'),
    src: Series[float] = input(close),
    bull_css_0=input.color(color.new(color.new('#0CB51A'), 50), 'Bullish Gradient', inline='inline0', group='Style'),
    bull_css_1=input.color(color.new('#0CB51A'), '', inline='inline0', group='Style'),
    bear_css_0=input.color(color.new(color.new('#FF1100'), 50), 'Bearish Gradient', inline='inline1', group='Style'),
    bear_css_1=input.color(color.new('#FF1100'), '', inline='inline1', group='Style'),
    amplitude=input(title='Amplitude', defval=2, group='HalfTrend'),
    channelDeviation=input(title='Channel Deviation', defval=2),
    showArrows=input(title='Show Arrows', defval=True),
    showChannels=input(title='Show Channels', defval=False),
    i_numLookbackBarsHull=input(3, title='Max Number Of Bars Between Hull and HalfTrend Trigger', group='Global'),
    i_emaFilterEnabled=input.bool(defval=False, title='Enable EMA Filter', tooltip='Enable if you would like to conditionally have entries incorporate EMA as a filter where source is above/below the EMA line', group='EMA Filter'),
    i_emaLength=input.int(200, title='EMA Length', minval=1, group='EMA Filter'),
    i_emaSource: Series[float] = input.source(close, 'EMA Source', group='EMA Filter'),
    i_adxFilterEnabled=input.bool(defval=False, title='Enable ADX Filter', tooltip='Enable if you would like to conditionally have entries incorporate ADX as a filter', group='ADX Filter'),
    i_adxVariant=input.string('ORIGINAL', title='ADX Variant', options=('ORIGINAL', 'MASANAKAMURA'), group='ADX Filter'),
    i_adxSmoothing=input.int(14, title='ADX Smoothing', group='ADX Filter'),
    i_adxDILength=input.int(14, title='DI Length', group='ADX Filter'),
    i_adxLowerThreshold=input.float(25, title='ADX Threshold', step=0.5, group='ADX Filter'),
    i_startPeriodEnabled=input.bool(True, 'Start', group='Date Range', inline='Start Period'),
    i_startPeriodTime=input.time(timestamp('1 Jan 2019'), '', group='Date Range', inline='Start Period'),
    i_endPeriodEnabled=input.bool(True, 'End', group='Date Range', inline='End Period'),
    i_endPeriodTime=input.time(timestamp('31 Dec 2030'), '', group='Date Range', inline='End Period'),
    i_timeFilterEnabled=input.bool(defval=False, title='Enable Time-Of-Day Window', tooltip='Limit the time of day for trade execution', group='Time Window'),
    i_timeZone=input.string(title='Select Local Time Zone', defval='GMT-5', options=('GMT-8', 'GMT-7', 'GMT-6', 'GMT-5', 'GMT-4', 'GMT-3', 'GMT-2', 'GMT-1', 'GMT', 'GMT+1', 'GMT+2', 'GMT+3', 'GMT+4', 'GMT+5', 'GMT+6', 'GMT+7', 'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12', 'GMT+13'), group='Time Window'),
    i_betweenTime=input.session('0700-0900', title='Time Filter', group='Time Window'),
    i_tradeDirection=input.string('Long and Short', title='Trade Direction', options=('Long and Short', 'Long Only', 'Short Only'), group='Trade Direction'),
    i_takeProfitTargetPercent1=input.float(title='Take Profit 1 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 1'),
    i_takeProfitQuantityPercent1=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 1'),
    i_takeProfitTargetPercent2=input.float(title='Take Profit 2 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 2'),
    i_takeProfitQuantityPercent2=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 2'),
    i_takeProfitTargetPercent3=input.float(title='Take Profit 3 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 3'),
    i_takeProfitQuantityPercent3=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 3'),
    i_takeProfitTargetPercent4=input.float(title='Take Profit 4 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit'),
    __input_35__=input.float(title='Stop Loss (%)', defval=999, minval=0.01, step=0.5, group='Stop Loss'),
    i_leverage=input.float(1, 'Leverage', step=0.5, group='Leverage'),
    i_alertSyntaxPrefix=input.string(defval='CRYPTANEX_99FTX_Strategy-Name-Here', title='Alert Syntax Prefix', group='ProfitView Alert Syntax'),
    showDashboard=input.bool(group='Dashboard', title='Show Dashboard', defval=True)
):
    short_len: Persistent = cast_int(length / 2)
    hull_len: Persistent = cast_int(math.sqrt(length))
    den1: Persistent = short_len * (short_len + 1) / 2
    den2: Persistent = length * (length + 1) / 2
    den3: Persistent = hull_len * (hull_len + 1) / 2
    lcwa_coeffs: Persistent[list[float]] = array.new_float(hull_len, 0)
    hull_coeffs: Persistent[list[float]] = array.new_float(0)
    if barstate.isfirst:
        for i in pine_range(0, length - 1, 1):
            sum1 = math.max(short_len - i, 0)
            sum2 = length - i
            array.unshift(lcwa_coeffs, 2 * (sum1 / den1) - sum2 / den2)
        for i in pine_range(0, hull_len - 2, 1):
            array.unshift(lcwa_coeffs, 0)
        for i in pine_range(hull_len, array.size(lcwa_coeffs) - 1, 1):
            sum3: float = 0.0
            for j in pine_range(i - hull_len, i - 1, 1):
                sum3 = sum3 + array.get(lcwa_coeffs, j) * (i - j)
            array.unshift(hull_coeffs, sum3 / den3)
    os: PersistentSeries[int] = 0
    len: Persistent = array.size(hull_coeffs) - 1
    hma: float = 0.0
    inv_hma: float = 0.0
    for i in pine_range(0, len, 1):
        hma = hma + src[i] * array.get(hull_coeffs, i)
        inv_hma = inv_hma + src[len - i] * array.get(hull_coeffs, i)
    hso: Series = hma - inv_hma
    cmean = ta.cum(math.abs(hso)) / bar_index * mult
    cross_1 = ta.cross(hso, -cmean)
    os = 0 if ta.cross(hso, cmean) or cross_1 else -1 if hso < hso[1] and hso > cmean else 1 if hso > hso[1] and hso < -cmean else os
    css0 = color.from_gradient(hso, 0, cmean, bull_css_0, bull_css_1)
    css1 = color.from_gradient(hso, -cmean, 0, bear_css_1, bear_css_0)
    css = css0 if hso > 0 else css1
    plotshape(os > os[1] and os == 1, title='Arrow Up', style=shape.circle, location=location.belowbar, size=size.tiny, color=color.new(color.green, 0))
    plotshape(os < os[1] and os == -1, title='Arrow Down', style=shape.circle, location=location.abovebar, size=size.tiny, color=color.new(color.red, 0))
    hullLongEntry = os > os[1] and os == 1
    hullShortEntry = os < os[1] and os == -1
    trend: PersistentSeries[int] = 0
    nextTrend: Persistent[int] = 0
    maxLowPrice: Persistent[float] = nz(low[1], low)
    minHighPrice: Persistent[float] = nz(high[1], high)
    up: PersistentSeries[float] = 0.0
    down: PersistentSeries[float] = 0.0
    atrHigh: float = 0.0
    atrLow: float = 0.0
    arrowUp: float = na(float)
    arrowDown: float = na(float)
    atr2 = ta.atr(100) / 2
    dev = channelDeviation * atr2
    highPrice = high[math.abs(ta.highestbars(amplitude))]
    lowPrice = low[math.abs(ta.lowestbars(amplitude))]
    highma = ta.sma(high, amplitude)
    lowma = ta.sma(low, amplitude)
    if nextTrend == 1:
        maxLowPrice = math.max(lowPrice, maxLowPrice)
        if highma < maxLowPrice and close < nz(low[1], low):
            trend = 1
            nextTrend = 0
            minHighPrice = highPrice
    else:
        minHighPrice = math.min(highPrice, minHighPrice)
        if lowma > minHighPrice and close > nz(high[1], high):
            trend = 0
            nextTrend = 1
            maxLowPrice = lowPrice
    if trend == 0:
        if not na(trend[1]) and trend[1] != 0:
            up = down if na(down[1]) else down[1]
            arrowUp = up - atr2
        else:
            up = maxLowPrice if na(up[1]) else math.max(maxLowPrice, up[1])
        atrHigh = up + dev
        atrLow = up - dev
    else:
        if not na(trend[1]) and trend[1] != 1:
            down = up if na(up[1]) else up[1]
            arrowDown = down + atr2
        else:
            down = minHighPrice if na(down[1]) else math.min(minHighPrice, down[1])
        atrHigh = down + dev
        atrLow = down - dev
    ht = up if trend == 0 else down
    buyColor: Persistent[Color] = color.blue
    sellColor: Persistent[Color] = color.red
    htColor = buyColor if trend == 0 else sellColor
    htPlot = plot(ht, title='HalfTrend', linewidth=2, color=htColor)
    atrHighPlot = plot(atrHigh if showChannels else na, title='ATR High', style=plot.style_circles, color=color.new(sellColor, 0))
    atrLowPlot = plot(atrLow if showChannels else na, title='ATR Low', style=plot.style_circles, color=color.new(buyColor, 0))
    fill(htPlot, atrHighPlot, title='ATR High Ribbon', color=color.new(sellColor, 90))
    fill(htPlot, atrLowPlot, title='ATR Low Ribbon', color=color.new(buyColor, 90))
    buySignal = not na(arrowUp) and trend == 0 and (trend[1] == 1)
    sellSignal = not na(arrowDown) and trend == 1 and (trend[1] == 0)
    plotshape(atrLow if showArrows and buySignal else na, title='Arrow Up', style=shape.triangleup, location=location.absolute, size=size.tiny, color=color.new(buyColor, 0))
    plotshape(atrHigh if showArrows and sellSignal else na, title='Arrow Down', style=shape.triangledown, location=location.absolute, size=size.tiny, color=color.new(sellColor, 0))
    alertcondition(buySignal, title='Alert: HalfTrend Buy', message='HalfTrend Buy')
    alertcondition(sellSignal, title='Alert: HalfTrend Sell', message='HalfTrend Sell')
    halfTrendLongEntry = buySignal
    halfTrendShortEntry = sellSignal
    barssince_1 = ta.barssince(hullLongEntry)
    longCondition = halfTrendLongEntry and barssince_1 <= i_numLookbackBarsHull
    barssince_2 = ta.barssince(hullShortEntry)
    shortCondition = halfTrendShortEntry and barssince_2 <= i_numLookbackBarsHull
    closeLongCondition: int = 0
    closeShortCondition: int = 0
    emaValue = ta.ema(i_emaSource, i_emaLength) if i_emaFilterEnabled else na
    isEMAFilterEnabledAndCloseAboveMA: bool = i_emaSource > emaValue if i_emaFilterEnabled else True
    isEMAFilterEnabledAndCloseBelowMA: bool = i_emaSource < emaValue if i_emaFilterEnabled else True
    def calcADX_Masanakamura(_len: int):
        _smoothedTrueRange: Series[float] = 0.0
        _smoothedDirectionalMovementPlus: Series[float] = 0.0
        _smoothed_directionalMovementMinus: Series[float] = 0.0
        _trueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
        _directionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
        _directionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
        _smoothedTrueRange = nz(_smoothedTrueRange[1]) - nz(_smoothedTrueRange[1]) / _len + _trueRange
        _smoothedDirectionalMovementPlus = nz(_smoothedDirectionalMovementPlus[1]) - nz(_smoothedDirectionalMovementPlus[1]) / _len + _directionalMovementPlus
        _smoothed_directionalMovementMinus = nz(_smoothed_directionalMovementMinus[1]) - nz(_smoothed_directionalMovementMinus[1]) / _len + _directionalMovementMinus
        DIP = _smoothedDirectionalMovementPlus / _smoothedTrueRange * 100
        DIM = _smoothed_directionalMovementMinus / _smoothedTrueRange * 100
        _DX = math.abs(DIP - DIM) / (DIP + DIM) * 100
        adx = ta.sma(_DX, _len)
        return (DIP, DIM, adx)

    DIPlusO, DIMinusO, ADXO = ta.dmi(i_adxDILength, i_adxSmoothing)
    DIPlusM, DIMinusM, ADXM = calcADX_Masanakamura(i_adxDILength)
    adx = ADXO if i_adxFilterEnabled and i_adxVariant == 'ORIGINAL' else ADXM
    isADXFilterEnabledAndAboveThreshold: bool = adx > i_adxLowerThreshold if i_adxFilterEnabled else True
    isStartPeriodEnabledAndInRange = i_startPeriodTime <= time if i_startPeriodEnabled else True
    isEndPeriodEnabledAndInRange = i_endPeriodTime >= time if i_endPeriodEnabled else True
    def isWithinWindowOfTime(_position):
        currentTimeIsWithinWindowOfTime = not na(time(timeframe.period, _position + ':1234567', i_timeZone))
        return currentTimeIsWithinWindowOfTime

    isTimeFilterEnabledAndInRange: bool = isWithinWindowOfTime(i_betweenTime) if i_timeFilterEnabled else True
    isStartEndPeriodsAndTimeInRange = isStartPeriodEnabledAndInRange and isEndPeriodEnabledAndInRange and isTimeFilterEnabledAndInRange
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    i_stopLossPercent = __input_35__ * 0.01
    slLongClose = close < strategy.position_avg_price * (1 - i_stopLossPercent)
    slShortClose = close > strategy.position_avg_price * (1 + i_stopLossPercent)
    contracts = math.min(math.max(1e-06, strategy.equity / close * i_leverage), 1000000000)
    isInLongPosition = strategy.position_size > 0
    isInShortPosition = strategy.position_size < 0
    alertSyntaxBase = i_alertSyntaxPrefix + '\n#' + string.tostring(open) + ',' + string.tostring(high) + ',' + string.tostring(low) + ',' + string.tostring(close) + ',' + string.tostring(volume) + ','
    longConditionCalc = longCondition and isADXFilterEnabledAndAboveThreshold and isEMAFilterEnabledAndCloseAboveMA
    shortConditionCalc = shortCondition and isADXFilterEnabledAndAboveThreshold and isEMAFilterEnabledAndCloseBelowMA
    if isStartEndPeriodsAndTimeInRange:
        if longConditionCalc and i_tradeDirection != 'Short Only' and (isInLongPosition == False):
            strategy.entry('Long', strategy.long, qty=contracts)
            alert(message=alertSyntaxBase + 'side:long', freq=alert.freq_once_per_bar_close)
        if shortConditionCalc and i_tradeDirection != 'Long Only' and (isInShortPosition == False):
            strategy.entry('Short', strategy.short, qty=contracts)
            alert(message=alertSyntaxBase + 'side:short', freq=alert.freq_once_per_bar_close)
        strategy.exit('TP1', qty_percent=i_takeProfitQuantityPercent1, profit=per(i_takeProfitTargetPercent1))
        strategy.exit('TP2', qty_percent=i_takeProfitQuantityPercent2, profit=per(i_takeProfitTargetPercent2))
        strategy.exit('TP3', qty_percent=i_takeProfitQuantityPercent3, profit=per(i_takeProfitTargetPercent3))
        strategy.exit('i_takeProfitTargetPercent4', profit=per(i_takeProfitTargetPercent4))
        if slLongClose:
            strategy.close('Long', qty_percent=100, comment='SL Long')
        if slShortClose:
            strategy.close('Short', qty_percent=100, comment='SL Short')
        if cast_bool(closeLongCondition):
            strategy.close('Long', qty_percent=100, comment='Close Long')
        if cast_bool(closeShortCondition):
            strategy.close('Short', qty_percent=100, comment='Close Short')
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
