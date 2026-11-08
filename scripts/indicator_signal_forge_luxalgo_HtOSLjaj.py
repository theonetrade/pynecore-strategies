"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, high,
    hl2, input, label, line, location, low, math, na, plot, plotshape, position, script, shape,
    size, string, ta, table, text
)
from pynecore.types import Color, Persistent, Series, Table

TOP_RIGHT: str = 'Top Right'
BOTTOM_RIGHT: str = 'Bottom Right'
BOTTOM_LEFT: str = 'Bottom Left'
TINY: str = 'Tiny'
SMALL: str = 'Small'
NORMAL: str = 'Normal'
LARGE: str = 'Large'
HUGE: str = 'Huge'
DASHBOARD_GROUP: str = 'Dashboard'
dashboardTooltip: str = 'Enable or disable the dashboards.'
dashboardSizeTooltip: str = 'Select the dashboard size.'
grpLogic: str = 'Signal Logic'
grpRisk: str = 'Risk Management (ATR)'
grpVisuals: str = 'Visuals'
grpSma: str = 'SMA Crossover'
grpRsi: str = 'RSI Filter'
grpMacd: str = 'MACD Crossover'
grpSt: str = 'Supertrend'
grpStoch: str = 'Stochastic'
grpBb: str = 'Bollinger Bands'
grpEma: str = 'EMA Crossover'
grpAo: str = 'Awesome Oscillator'
grpSar: str = 'Parabolic SAR'
grpCci: str = 'CCI Filter'
grpAdx: str = 'ADX Filter'


@script.indicator("Signal Forge [LuxAlgo]", "LuxAlgo - Signal Forge", overlay=True, max_labels_count=500, max_lines_count=500)
def main(
    requireAllInput=input.bool(True, 'Require All Enabled Indicators to Align', group=grpLogic, tooltip='If enabled, ALL checked indicators must agree to generate a signal. If disabled, ANY checked indicator can generate a signal.'),
    atrLenInput=input.int(14, 'ATR Length', group=grpRisk),
    enableTpInput=input.bool(False, 'Take Profit', inline='tp', group=grpRisk),
    tpMultInput=input.float(2.0, 'Multiplier', inline='tp', step=0.1, group=grpRisk),
    enableSlInput=input.bool(False, 'Stop Loss', inline='sl', group=grpRisk),
    slMultInput=input.float(1.5, 'Multiplier', inline='sl', step=0.1, group=grpRisk),
    enableTsInput=input.bool(False, 'Trailing Stop', inline='ts', group=grpRisk),
    tsMultInput=input.float(1.0, 'Multiplier', inline='ts', step=0.1, group=grpRisk),
    orbDistInput=input.float(1.5, 'Orb Distance (ATR)', group=grpVisuals, step=0.1),
    orbSizeInput=input.int(10, 'Orb Base Size', group=grpVisuals, minval=3, maxval=20),
    enableSmaInput=input.bool(True, 'Enable SMA Crossover', group=grpSma),
    smaFastLenInput=input.int(10, 'Fast Length', minval=1, group=grpSma),
    smaSlowLenInput=input.int(20, 'Slow Length', minval=1, group=grpSma),
    enableRsiInput=input.bool(False, 'Enable RSI Filter', group=grpRsi),
    rsiLenInput=input.int(14, 'RSI Length', minval=1, group=grpRsi),
    rsiLongLevelInput=input.float(50, 'Long Above', group=grpRsi),
    rsiShortLevelInput=input.float(50, 'Short Below', group=grpRsi),
    enableMacdInput=input.bool(False, 'Enable MACD Crossover', group=grpMacd),
    macdFastLenInput=input.int(12, 'Fast Length', minval=1, group=grpMacd),
    macdSlowLenInput=input.int(26, 'Slow Length', minval=1, group=grpMacd),
    macdSignalLenInput=input.int(9, 'Signal Length', minval=1, group=grpMacd),
    enableStInput=input.bool(False, 'Enable Supertrend', group=grpSt),
    stFactorInput=input.float(3.0, 'Factor', minval=0.1, step=0.1, group=grpSt),
    stLenInput=input.int(10, 'Length', minval=1, group=grpSt),
    enableStochInput=input.bool(False, 'Enable Stochastic', group=grpStoch),
    stochKInput=input.int(14, 'K Length', minval=1, group=grpStoch),
    stochDInput=input.int(3, 'D Length', minval=1, group=grpStoch),
    stochSmoothInput=input.int(3, 'Smooth', minval=1, group=grpStoch),
    enableBbInput=input.bool(False, 'Enable BB Trend', group=grpBb, tooltip='Looks for price trading in the upper/lower half of the bands.'),
    bbLenInput=input.int(20, 'Length', minval=1, group=grpBb),
    bbMultInput=input.float(2.0, 'Multiplier', minval=0.1, step=0.1, group=grpBb),
    enableEmaInput=input.bool(False, 'Enable EMA Crossover', group=grpEma),
    emaFastLenInput=input.int(10, 'Fast Length', minval=1, group=grpEma),
    emaSlowLenInput=input.int(20, 'Slow Length', minval=1, group=grpEma),
    enableAoInput=input.bool(False, 'Enable AO', group=grpAo),
    enableSarInput=input.bool(False, 'Enable Parabolic SAR', group=grpSar),
    sarStartInput=input.float(0.02, 'Start', step=0.01, group=grpSar),
    sarIncInput=input.float(0.02, 'Increment', step=0.01, group=grpSar),
    sarMaxInput=input.float(0.2, 'Max Value', step=0.1, group=grpSar),
    enableCciInput=input.bool(False, 'Enable CCI Filter', group=grpCci),
    cciLenInput=input.int(20, 'Length', minval=1, group=grpCci),
    cciLongLevelInput=input.float(0, 'Long Above', group=grpCci),
    cciShortLevelInput=input.float(0, 'Short Below', group=grpCci),
    enableAdxInput=input.bool(False, 'Enable ADX Filter', group=grpAdx),
    adxLenInput=input.int(14, 'ADX Smoothing', minval=1, group=grpAdx),
    diLenInput=input.int(14, 'DI Length', minval=1, group=grpAdx),
    adxThresholdInput=input.float(20, 'ADX Threshold', group=grpAdx),
    dashboardInput=input.bool(True, 'Dashboards', group=DASHBOARD_GROUP, tooltip=dashboardTooltip),
    dashboardPositionInput=input.string(TOP_RIGHT, 'Indicator Dashboard Position', group=DASHBOARD_GROUP, options=(TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)),
    perfDashboardPositionIn=input.string(BOTTOM_RIGHT, 'Performance Dashboard Position', group=DASHBOARD_GROUP, options=(TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)),
    dashboardSizeInput=input.string(NORMAL, 'Size', group=DASHBOARD_GROUP, tooltip=dashboardSizeTooltip, options=(TINY, SMALL, NORMAL, LARGE, HUGE))
):
    DATA: Color = color.new('#DBDBDB')
    HEADERS: Color = color.new('#808080')
    BACKGROUND: Color = color.new('#161616')
    BORDERS: Color = color.new('#2E2E2E')













    smaFast = ta.sma(close, smaFastLenInput)
    smaSlow = ta.sma(close, smaSlowLenInput)
    smaBullish = smaFast > smaSlow
    smaBearish = smaFast < smaSlow

    rsi = ta.rsi(close, rsiLenInput)
    rsiBullish = rsi > rsiLongLevelInput
    rsiBearish = rsi < rsiShortLevelInput

    macdLine, signalLine, _ = ta.macd(close, macdFastLenInput, macdSlowLenInput, macdSignalLenInput)
    macdBullish = macdLine > signalLine
    macdBearish = macdLine < signalLine

    stLine, stDir = ta.supertrend(stFactorInput, stLenInput)
    stBullish = stDir == -1
    stBearish = stDir == 1

    k = ta.sma(ta.stoch(close, high, low, stochKInput), stochSmoothInput)
    d = ta.sma(k, stochDInput)
    stochBullish = k > 50
    stochBearish = k < 50

    bbMiddle, bbUpper, bbLower = ta.bb(close, bbLenInput, bbMultInput)
    bbBullish = close > bbMiddle
    bbBearish = close < bbMiddle

    emaFast = ta.ema(close, emaFastLenInput)
    emaSlow = ta.ema(close, emaSlowLenInput)
    emaBullish = emaFast > emaSlow
    emaBearish = emaFast < emaSlow

    ao = ta.sma(hl2, 5) - ta.sma(hl2, 34)
    aoBullish = ao > 0
    aoBearish = ao < 0

    sar = ta.sar(sarStartInput, sarIncInput, sarMaxInput)
    sarBullish = close > sar
    sarBearish = close < sar

    cci = ta.cci(close, cciLenInput)
    cciBullish = cci > cciLongLevelInput
    cciBearish = cci < cciShortLevelInput

    diPlus, diMinus, adx = ta.dmi(diLenInput, adxLenInput)
    adxBullish = adx > adxThresholdInput and diPlus > diMinus
    adxBearish = adx > adxThresholdInput and diMinus > diPlus

    atr = ta.atr(atrLenInput)

    bullArr: list[bool] = array.from_items(smaBullish, rsiBullish, macdBullish, stBullish, stochBullish, bbBullish, emaBullish, aoBullish, sarBullish, cciBullish, adxBullish)
    bearArr: list[bool] = array.from_items(smaBearish, rsiBearish, macdBearish, stBearish, stochBearish, bbBearish, emaBearish, aoBearish, sarBearish, cciBearish, adxBearish)

    indStates: Persistent[list[int]] = array.new_int(11, 0)
    indEntries: Persistent[list[float]] = array.new_float(11, na)
    indSlLevels: Persistent[list[float]] = array.new_float(11, na)
    indTpLevels: Persistent[list[float]] = array.new_float(11, na)
    indTsLevels: Persistent[list[float]] = array.new_float(11, na)
    indTotalTrades: Persistent[list[int]] = array.new_int(11, 0)
    indWinTrades: Persistent[list[int]] = array.new_int(11, 0)
    prevBullArr: Persistent[list[bool]] = array.new_bool(11, False)
    prevBearArr: Persistent[list[bool]] = array.new_bool(11, False)

    for i in pine_range(0, 10):
        bull = array.get(bullArr, i)
        bear = array.get(bearArr, i)
        state = array.get(indStates, i)
        entry = array.get(indEntries, i)
        sl = array.get(indSlLevels, i)
        tp = array.get(indTpLevels, i)
        ts = array.get(indTsLevels, i)

        prevBull = array.get(prevBullArr, i)
        prevBear = array.get(prevBearArr, i)

        indExitLong: bool = False
        indExitShort: bool = False
        indLongExitPrice: float = na(float)
        indShortExitPrice: float = na(float)

        if state == 1:
            if enableSlInput and low <= sl:
                indExitLong = True
                indLongExitPrice = sl
            elif enableTpInput and high >= tp:
                indExitLong = True
                indLongExitPrice = tp
            elif enableTsInput and low <= ts:
                indExitLong = True
                indLongExitPrice = ts
            elif bear:
                indExitLong = True
                indLongExitPrice = close

        if state == -1:
            if enableSlInput and high >= sl:
                indExitShort = True
                indShortExitPrice = sl
            elif enableTpInput and low <= tp:
                indExitShort = True
                indShortExitPrice = tp
            elif enableTsInput and high >= ts:
                indExitShort = True
                indShortExitPrice = ts
            elif bull:
                indExitShort = True
                indShortExitPrice = close

        if indExitLong:
            ret = (indLongExitPrice - entry) / entry * 100
            array.set(indTotalTrades, i, array.get(indTotalTrades, i) + 1)
            if ret > 0:
                array.set(indWinTrades, i, array.get(indWinTrades, i) + 1)
            array.set(indStates, i, 0)
            array.set(indSlLevels, i, na)
            array.set(indTpLevels, i, na)
            array.set(indTsLevels, i, na)
            state = 0

        if indExitShort:
            ret = (entry - indShortExitPrice) / entry * 100
            array.set(indTotalTrades, i, array.get(indTotalTrades, i) + 1)
            if ret > 0:
                array.set(indWinTrades, i, array.get(indWinTrades, i) + 1)
            array.set(indStates, i, 0)
            array.set(indSlLevels, i, na)
            array.set(indTpLevels, i, na)
            array.set(indTsLevels, i, na)
            state = 0

        enterLong__00000094__ = bull and (not prevBull) and (state != 1)
        enterShort__00000094__ = bear and (not prevBear) and (state != -1)

        if enterLong__00000094__:
            array.set(indStates, i, 1)
            array.set(indEntries, i, close)
            if enableSlInput:
                array.set(indSlLevels, i, close - atr * slMultInput)
            if enableTpInput:
                array.set(indTpLevels, i, close + atr * tpMultInput)
            if enableTsInput:
                array.set(indTsLevels, i, close - atr * tsMultInput)

        if enterShort__00000094__:
            array.set(indStates, i, -1)
            array.set(indEntries, i, close)
            if enableSlInput:
                array.set(indSlLevels, i, close + atr * slMultInput)
            if enableTpInput:
                array.set(indTpLevels, i, close - atr * tpMultInput)
            if enableTsInput:
                array.set(indTsLevels, i, close + atr * tsMultInput)

        if state == 1 and (not enterLong__00000094__) and enableTsInput:
            array.set(indTsLevels, i, math.max(array.get(indTsLevels, i), close - atr * tsMultInput))

        if state == -1 and (not enterShort__00000094__) and enableTsInput:
            array.set(indTsLevels, i, math.min(array.get(indTsLevels, i), close + atr * tsMultInput))

        array.set(prevBullArr, i, bull)
        array.set(prevBearArr, i, bear)

    longCond: Series[bool] = True if requireAllInput else False
    shortCond: Series[bool] = True if requireAllInput else False
    anyEnabled: bool = False

    if enableSmaInput:
        longCond = longCond and smaBullish if requireAllInput else longCond or smaBullish
        shortCond = shortCond and smaBearish if requireAllInput else shortCond or smaBearish
        anyEnabled = True

    if enableRsiInput:
        longCond = longCond and rsiBullish if requireAllInput else longCond or rsiBullish
        shortCond = shortCond and rsiBearish if requireAllInput else shortCond or rsiBearish
        anyEnabled = True

    if enableMacdInput:
        longCond = longCond and macdBullish if requireAllInput else longCond or macdBullish
        shortCond = shortCond and macdBearish if requireAllInput else shortCond or macdBearish
        anyEnabled = True

    if enableStInput:
        longCond = longCond and stBullish if requireAllInput else longCond or stBullish
        shortCond = shortCond and stBearish if requireAllInput else shortCond or stBearish
        anyEnabled = True

    if enableStochInput:
        longCond = longCond and stochBullish if requireAllInput else longCond or stochBullish
        shortCond = shortCond and stochBearish if requireAllInput else shortCond or stochBearish
        anyEnabled = True

    if enableBbInput:
        longCond = longCond and bbBullish if requireAllInput else longCond or bbBullish
        shortCond = shortCond and bbBearish if requireAllInput else shortCond or bbBearish
        anyEnabled = True

    if enableEmaInput:
        longCond = longCond and emaBullish if requireAllInput else longCond or emaBullish
        shortCond = shortCond and emaBearish if requireAllInput else shortCond or emaBearish
        anyEnabled = True

    if enableAoInput:
        longCond = longCond and aoBullish if requireAllInput else longCond or aoBullish
        shortCond = shortCond and aoBearish if requireAllInput else shortCond or aoBearish
        anyEnabled = True

    if enableSarInput:
        longCond = longCond and sarBullish if requireAllInput else longCond or sarBullish
        shortCond = shortCond and sarBearish if requireAllInput else shortCond or sarBearish
        anyEnabled = True

    if enableCciInput:
        longCond = longCond and cciBullish if requireAllInput else longCond or cciBullish
        shortCond = shortCond and cciBearish if requireAllInput else shortCond or cciBearish
        anyEnabled = True

    if enableAdxInput:
        longCond = longCond and adxBullish if requireAllInput else longCond or adxBullish
        shortCond = shortCond and adxBearish if requireAllInput else shortCond or adxBearish
        anyEnabled = True

    if not anyEnabled:
        longCond = False
        shortCond = False

    tradeState: Persistent[int] = 0
    entryPrice: Persistent[float] = na(float)
    slLevel: Persistent[float] = na(float)
    tpLevel: Persistent[float] = na(float)
    tsLevel: Persistent[float] = na(float)

    totalTrades: Persistent[int] = 0
    winTrades: Persistent[int] = 0
    netProfitPct: Persistent[float] = 0.0
    grossProfit: Persistent[float] = 0.0
    grossLoss: Persistent[float] = 0.0

    exitLong: bool = False
    exitShort: bool = False
    longExitPrice: float = na(float)
    shortExitPrice: float = na(float)

    if tradeState == 1:
        if enableSlInput and low <= slLevel:
            exitLong = True
            longExitPrice = slLevel
        elif enableTpInput and high >= tpLevel:
            exitLong = True
            longExitPrice = tpLevel
        elif enableTsInput and low <= tsLevel:
            exitLong = True
            longExitPrice = tsLevel
        elif shortCond:
            exitLong = True
            longExitPrice = close

    if tradeState == -1:
        if enableSlInput and high >= slLevel:
            exitShort = True
            shortExitPrice = slLevel
        elif enableTpInput and low <= tpLevel:
            exitShort = True
            shortExitPrice = tpLevel
        elif enableTsInput and high >= tsLevel:
            exitShort = True
            shortExitPrice = tsLevel
        elif longCond:
            exitShort = True
            shortExitPrice = close

    if exitLong:
        tradeRet: float = (longExitPrice - entryPrice) / entryPrice * 100
        netProfitPct += tradeRet
        totalTrades += 1
        if tradeRet > 0:
            winTrades += 1
            grossProfit += tradeRet
        else:
            grossLoss += math.abs(tradeRet)
        tradeState = 0
        slLevel = na
        tpLevel = na
        tsLevel = na

    if exitShort:
        tradeRet: float = (entryPrice - shortExitPrice) / entryPrice * 100
        netProfitPct += tradeRet
        totalTrades += 1
        if tradeRet > 0:
            winTrades += 1
            grossProfit += tradeRet
        else:
            grossLoss += math.abs(tradeRet)
        tradeState = 0
        slLevel = na
        tpLevel = na
        tsLevel = na

    enterLong: bool = longCond and (not longCond[1] == True) and (tradeState != 1)
    enterShort: bool = shortCond and (not shortCond[1] == True) and (tradeState != -1)

    if enterLong:
        tradeState = 1
        entryPrice = close
        if enableSlInput:
            slLevel = close - atr * slMultInput
        if enableTpInput:
            tpLevel = close + atr * tpMultInput
        if enableTsInput:
            tsLevel = close - atr * tsMultInput

    if enterShort:
        tradeState = -1
        entryPrice = close
        if enableSlInput:
            slLevel = close + atr * slMultInput
        if enableTpInput:
            tpLevel = close - atr * tpMultInput
        if enableTsInput:
            tsLevel = close + atr * tsMultInput

    if tradeState == 1 and (not enterLong) and enableTsInput:
        tsLevel = math.max(tsLevel, close - atr * tsMultInput)

    if tradeState == -1 and (not enterShort) and enableTsInput:
        tsLevel = math.min(tsLevel, close + atr * tsMultInput)

    longGlowY: float = low - atr * orbDistInput if enterLong else na
    shortGlowY: float = high + atr * orbDistInput if enterShort else na

    currentWR: float = winTrades / totalTrades * 100 if totalTrades > 0 else 0
    wrText: str = string.tostring(currentWR, '#.#') + '%'

    if enterLong:
        line.new(bar_index, low, bar_index, longGlowY, color=color.new(color.new('#089981'), 80), width=2)
        line.new(bar_index, low, bar_index, longGlowY, color=color.new(color.new('#089981'), 40), width=1)
        label.new(bar_index, longGlowY, text=wrText, color=color.new(color.new('#000000'), 100), textcolor=chart.fg_color, style=label.style_label_up, size=size.tiny)

    if enterShort:
        line.new(bar_index, high, bar_index, shortGlowY, color=color.new(color.new('#F23645'), 80), width=2)
        line.new(bar_index, high, bar_index, shortGlowY, color=color.new(color.new('#F23645'), 40), width=1)
        label.new(bar_index, shortGlowY, text=wrText, color=color.new(color.new('#000000'), 100), textcolor=chart.fg_color, style=label.style_label_down, size=size.tiny)

    plot(longGlowY, title='Long Glow 1', style=plot.style_circles, linewidth=orbSizeInput, color=color.new(color.new('#089981'), 80))
    plot(longGlowY, title='Long Glow 2', style=plot.style_circles, linewidth=math.max(1, orbSizeInput - 3), color=color.new(color.new('#089981'), 50))
    plot(longGlowY, title='Long Glow 3', style=plot.style_circles, linewidth=math.max(1, orbSizeInput - 6), color=color.new(color.new('#089981'), 0))

    plot(shortGlowY, title='Short Glow 1', style=plot.style_circles, linewidth=orbSizeInput, color=color.new(color.new('#F23645'), 80))
    plot(shortGlowY, title='Short Glow 2', style=plot.style_circles, linewidth=math.max(1, orbSizeInput - 3), color=color.new(color.new('#F23645'), 50))
    plot(shortGlowY, title='Short Glow 3', style=plot.style_circles, linewidth=math.max(1, orbSizeInput - 6), color=color.new(color.new('#F23645'), 0))

    plotshape(exitLong and (not enterShort), title='Exit Long', style=shape.xcross, location=location.abovebar, color=color.new('#F23645'), size=size.tiny)
    plotshape(exitShort and (not enterLong), title='Exit Short', style=shape.xcross, location=location.belowbar, color=color.new('#089981'), size=size.tiny)

    colorSl = (na if enterLong or enterShort else color.new(color.new('#F23645'), 0)) if tradeState != 0 and enableSlInput else na
    colorTp = (na if enterLong or enterShort else color.new(color.new('#089981'), 0)) if tradeState != 0 and enableTpInput else na

    plot(slLevel if tradeState != 0 and enableSlInput else na, title='Stop Loss', color=colorSl, style=plot.style_linebr, linewidth=1)
    plot(tpLevel if tradeState != 0 and enableTpInput else na, title='Take Profit', color=colorTp, style=plot.style_linebr, linewidth=1)

    tsPlotVal: float = tsLevel if tradeState != 0 and enableTsInput and (not (enterLong or enterShort)) else na
    p_ts = plot(tsPlotVal, title='Trailing Stop', color=color.new(color.new('#2962FF'), 0), style=plot.style_linebr, linewidth=2)

    tsTopVal: float = close if tradeState == 1 else tsLevel if tradeState == -1 else na
    tsBotVal: float = tsLevel if tradeState == 1 else close if tradeState == -1 else na
    tsTopCol: Color = color.new(color.new('#2962FF'), 70) if tradeState == 1 else color.new(color.new('#2962FF'), 100) if tradeState == -1 else na
    tsBotCol: Color = color.new(color.new('#2962FF'), 100) if tradeState == 1 else color.new(color.new('#2962FF'), 70) if tradeState == -1 else na

    p_price = plot(close if tradeState != 0 and enableTsInput and (not (enterLong or enterShort)) else na, title='Price for TS', display=display.none)
    fill(p_ts, p_price, tsTopVal, tsBotVal, tsTopCol, tsBotCol)

    __block_result__ = na
    __switch__ = dashboardPositionInput
    if __switch__ == TOP_RIGHT:
        __block_result__ = position.top_right
    elif __switch__ == BOTTOM_RIGHT:
        __block_result__ = position.bottom_right
    elif __switch__ == BOTTOM_LEFT:
        __block_result__ = position.bottom_left
    parsedDashboardPosition: Persistent = __block_result__

    __block_result_1__ = na
    __switch__ = perfDashboardPositionIn
    if __switch__ == TOP_RIGHT:
        __block_result_1__ = position.top_right
    elif __switch__ == BOTTOM_RIGHT:
        __block_result_1__ = position.bottom_right
    elif __switch__ == BOTTOM_LEFT:
        __block_result_1__ = position.bottom_left
    parsedPerfPosition: Persistent = __block_result_1__

    __block_result_2__ = na
    __switch__ = dashboardSizeInput
    if __switch__ == TINY:
        __block_result_2__ = size.tiny
    elif __switch__ == SMALL:
        __block_result_2__ = size.small
    elif __switch__ == NORMAL:
        __block_result_2__ = size.normal
    elif __switch__ == LARGE:
        __block_result_2__ = size.large
    elif __switch__ == HUGE:
        __block_result_2__ = size.huge
    parsedDashboardSize: Persistent = __block_result_2__

    def cell(t: Table, column: int, row: int, data: str, txt_color: Color = color.new('#FFFFFF'), align: str = text.align_right, bg_color: Color = na, height: float = 0):
        return table.cell(t, column, row, data, text_color=txt_color, text_size=parsedDashboardSize, text_halign=align, bgcolor=bg_color, height=height)

    def divider(t: Table, row: int, lastColumn: int):
        rowDivider: str = '━━━━━━━━━━━━━━'
        table.merge_cells(t, 0, row, lastColumn, row)
        return cell(t, 0, row, rowDivider, align=text.align_center, height=0.5, txt_color=BORDERS)

    t_able: Persistent[Table] = table.new(parsedDashboardPosition, 4, 30, bgcolor=BACKGROUND, border_width=0, frame_color=BORDERS, frame_width=1, force_overlay=True)

    t_perf: Persistent[Table] = table.new(parsedPerfPosition, 6, 10, bgcolor=BACKGROUND, border_width=0, frame_color=BORDERS, frame_width=1, force_overlay=True)

    c_gradStart = color.rgb(18, 20, 26)
    c_gradEnd = color.rgb(32, 36, 48)

    def f_perf_bg(c, maxC, isHeader):
        baseCol = color.from_gradient(c, 0, maxC, c_gradStart, c_gradEnd)
        return color.new(baseCol, 30) if isHeader else baseCol

    def f_status(bull, bear):
        statusStr = 'Bullish' if bull else 'Bearish' if bear else 'Neutral'
        statusColor = color.new('#089981') if bull else color.new('#F23645') if bear else HEADERS
        return (statusStr, statusColor)

    def f_hist(win, total):
        wr = win / total * 100 if total > 0 else 0
        blocks = math.max(0, math.min(10, cast_int(math.round(wr / 10))))
        histStr: str = ''
        for i in pine_range(1, 10):
            if i <= blocks:
                histStr += '█'
            else:
                histStr += '░'

        colorHist = color.new('#089981') if wr >= 50 else DATA if total == 0 else color.new('#F23645')
        return (histStr + '  ' + string.tostring(wr, '#.#') + '%', colorHist)

    def f_render_row(tbl, r, name, bullStr, bullCol, win, total, enabled):
        hist, histCol = f_hist(win, total)
        cell(tbl, 0, r, name, txt_color=DATA, align=text.align_left, bg_color=f_perf_bg(0, 3, False))
        cell(tbl, 1, r, bullStr, txt_color=bullCol, align=text.align_center, bg_color=f_perf_bg(1, 3, False))
        cell(tbl, 2, r, hist, txt_color=histCol, align=text.align_left, bg_color=f_perf_bg(2, 3, False))
        return cell(tbl, 3, r, '✓' if enabled else '✗', txt_color=color.new('#089981') if enabled else color.new('#F23645'), align=text.align_right, bg_color=f_perf_bg(3, 3, False))

    if dashboardInput and barstate.islast:
        winRate = winTrades / totalTrades * 100 if totalTrades > 0 else 0
        profitFactor = grossProfit / grossLoss if grossLoss > 0 else 999 if grossProfit > 0 else 0

        smaStr, smaCol = f_status(smaBullish, smaBearish)
        rsiStr, rsiCol = f_status(rsiBullish, rsiBearish)
        macdStr, macdCol = f_status(macdBullish, macdBearish)
        stStr, stCol = f_status(stBullish, stBearish)
        stochStr, stochCol = f_status(stochBullish, stochBearish)
        bbStr, bbCol = f_status(bbBullish, bbBearish)

        emaStr, emaCol = f_status(emaBullish, emaBearish)
        aoStr, aoCol = f_status(aoBullish, aoBearish)
        sarStr, sarCol = f_status(sarBullish, sarBearish)
        cciStr, cciCol = f_status(cciBullish, cciBearish)
        adxStr, adxCol = f_status(adxBullish, adxBearish)

        signalStatusStr = 'LONG' if longCond else 'SHORT' if shortCond else 'NEUTRAL'
        signalColor = color.new('#089981') if longCond else color.new('#F23645') if shortCond else HEADERS

        r: int = 0

        table.merge_cells(t_able, 0, r, 3, r)
        cell(t_able, 0, r, 'Indicator Dashboard', txt_color=DATA, align=text.align_center, bg_color=color.rgb(12, 14, 18))
        r += 1

        divider(t_able, r, 3)
        r += 1

        cell(t_able, 0, r, 'Indicator', txt_color=HEADERS, align=text.align_left, bg_color=f_perf_bg(0, 3, True))
        cell(t_able, 1, r, 'Status', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(1, 3, True))
        cell(t_able, 2, r, 'Standalone WR', txt_color=HEADERS, align=text.align_left, bg_color=f_perf_bg(2, 3, True))
        cell(t_able, 3, r, 'Enabled', txt_color=HEADERS, align=text.align_right, bg_color=f_perf_bg(3, 3, True))
        r += 1

        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'SMA Cross', smaStr, smaCol, array.get(indWinTrades, 0), array.get(indTotalTrades, 0), enableSmaInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'RSI', rsiStr, rsiCol, array.get(indWinTrades, 1), array.get(indTotalTrades, 1), enableRsiInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'MACD', macdStr, macdCol, array.get(indWinTrades, 2), array.get(indTotalTrades, 2), enableMacdInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'Supertrend', stStr, stCol, array.get(indWinTrades, 3), array.get(indTotalTrades, 3), enableStInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'Stochastic', stochStr, stochCol, array.get(indWinTrades, 4), array.get(indTotalTrades, 4), enableStochInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'Bollinger', bbStr, bbCol, array.get(indWinTrades, 5), array.get(indTotalTrades, 5), enableBbInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'EMA Cross', emaStr, emaCol, array.get(indWinTrades, 6), array.get(indTotalTrades, 6), enableEmaInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'AO', aoStr, aoCol, array.get(indWinTrades, 7), array.get(indTotalTrades, 7), enableAoInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'SAR', sarStr, sarCol, array.get(indWinTrades, 8), array.get(indTotalTrades, 8), enableSarInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'CCI', cciStr, cciCol, array.get(indWinTrades, 9), array.get(indTotalTrades, 9), enableCciInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        f_render_row(t_able, r, 'ADX Filter', adxStr, adxCol, array.get(indWinTrades, 10), array.get(indTotalTrades, 10), enableAdxInput)
        r += 1
        divider(t_able, r, 3)
        r += 1

        table.merge_cells(t_able, 0, r, 2, r)
        cell(t_able, 0, r, 'Current Signal', txt_color=HEADERS, align=text.align_left, bg_color=f_perf_bg(0, 3, False))
        cell(t_able, 3, r, signalStatusStr, txt_color=signalColor, align=text.align_right, bg_color=f_perf_bg(3, 3, False))

        pR: int = 0

        table.merge_cells(t_perf, 0, pR, 5, pR)
        cell(t_perf, 0, pR, 'Backtest Results [LuxAlgo]', txt_color=DATA, align=text.align_center, bg_color=color.rgb(12, 14, 18))
        pR += 1

        divider(t_perf, pR, 5)
        pR += 1

        cell(t_perf, 0, pR, 'Total Trades', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(0, 5, True))
        cell(t_perf, 1, pR, 'Wins', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(1, 5, True))
        cell(t_perf, 2, pR, 'Losses', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(2, 5, True))
        cell(t_perf, 3, pR, 'Winrate', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(3, 5, True))
        cell(t_perf, 4, pR, 'PF', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(4, 5, True))
        cell(t_perf, 5, pR, 'PNL %', txt_color=HEADERS, align=text.align_center, bg_color=f_perf_bg(5, 5, True))
        pR += 1

        divider(t_perf, pR, 5)
        pR += 1

        lossTrades: int = totalTrades - winTrades

        cell(t_perf, 0, pR, string.tostring(totalTrades), txt_color=DATA, align=text.align_center, bg_color=f_perf_bg(0, 5, False))
        cell(t_perf, 1, pR, string.tostring(winTrades), txt_color=DATA, align=text.align_center, bg_color=f_perf_bg(1, 5, False))
        cell(t_perf, 2, pR, string.tostring(lossTrades), txt_color=DATA, align=text.align_center, bg_color=f_perf_bg(2, 5, False))
        cell(t_perf, 3, pR, string.tostring(winRate, '#.##') + ' %', txt_color=color.new('#089981') if winRate >= 50 else DATA if totalTrades == 0 else color.new('#F23645'), align=text.align_center, bg_color=f_perf_bg(3, 5, False))
        cell(t_perf, 4, pR, 'MAX' if profitFactor == 999 else string.tostring(profitFactor, '#.##'), txt_color=color.new('#089981') if profitFactor > 1 else DATA if profitFactor == 0 else color.new('#F23645'), align=text.align_center, bg_color=f_perf_bg(4, 5, False))
        cell(t_perf, 5, pR, string.tostring(netProfitPct, '#.##') + ' %', txt_color=color.new('#089981') if netProfitPct > 0 else color.new('#F23645') if netProfitPct < 0 else DATA, align=text.align_center, bg_color=f_perf_bg(5, 5, False))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
