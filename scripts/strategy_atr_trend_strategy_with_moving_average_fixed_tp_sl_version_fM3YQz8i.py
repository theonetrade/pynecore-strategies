"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    array, bar_index, box, close, color, currency, display, fill, high,
    input, label, low, math, na, plot, position, script, size, strategy, string, syminfo, ta,
    table
)
from pynecore.types import Box, Persistent, PersistentSeries, Series, Table
import lib.TradingView.ta.v12 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

MA: str = "Moving Average"
ATR: str = "ATR Signal"
Thresh: str = "Threshold (%)"
BarsConf: str = "Number Bars Confirmed"


@script.strategy(title="ATR Trend Strategy with Moving Average | Fixed TP/SL version", shorttitle="ATR MA Strategy | Fixed TP/SL", overlay=True, initial_capital=10000, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.04, slippage=2, pyramiding=0, calc_on_order_fills=False, calc_on_every_tick=False)
def main(
    MAtype=input.string(defval="EMA", title="MA Type", options=("EMA", "SMA", "WMA", "Hull MA", "VWMA", "RMA", "TEMA"), group=MA, display=display.none),
    MAlen=input.int(defval=100, title="MA Length", group=MA, display=display.none),
    MAsrc: Series[float] = input.source(defval=close, title="MA Source", group=MA, display=display.none),
    ATRtype=input.string(defval="RMA", title="ATR Type", group=ATR, options=("EMA", "SMA", "WMA", "RMA"), display=display.none),
    ATRmult=input.float(defval=3, title="ATR Multiplier", tooltip="Multiplier applied to ATR to define the distance of trend bands or signal thresholds. Higher values require stronger price movement to confirm trends, reducing noise but delaying signals.", minval=0.1, step=0.1, group=ATR, display=display.none),
    ATRlen=input.int(defval=7, title="ATR Length", tooltip="Number of bars used to calculate the Average True Range (ATR). Higher values produce smoother, more stable volatility estimates, while lower values make ATR more responsive to recent price changes.", group=ATR, display=display.none),
    useAtrFilter=input.bool(defval=False, title="Use ATR Filter", tooltip="Enable a volatility filter using ATR. Trades are only allowed when current ATR is above its moving average, helping avoid low-volatility conditions.", group=ATR, display=display.none),
    atrFilterLen=input.int(defval=14, title="ATR Filter Length", group=ATR, display=display.none),
    confirmBars=input.int(defval=2, title="Bars Confirmed", tooltip="Number of consecutive bars required outside the ATR band to confirm a trend. Higher values reduce noise but delay signals.", minval=1, step=1, group=BarsConf, display=display.none),
    confirmSrc=input.string(defval="Low/high", title="Source Confirmed", options=("Close", "Low/high"), group=BarsConf, display=display.none),
    entryMethod=input.string(defval="Breakout", title="Entry Method", options=("Breakout", "MA Cross"), tooltip="Select entry logic: Breakout enters on trend confirmation, MA Cross enters on pullbacks within the trend.", group=Thresh, display=display.none),
    useAutoTP_SL=input.bool(True, title="Use Auto TP/SL", group=Thresh, tooltip="Automatically sets TP/SL based on trend distribution (Position 70% of MFE, MAE). Disable to use a fixed manual TP/SL value."),
    TPinput=input.float(defval=5.0, title="TP (%)", minval=0.1, step=0.1, group=Thresh, display=display.none),
    SLinput=input.float(defval=2.0, title="SL (%)", minval=0.1, step=0.1, group=Thresh, display=display.none)
):
    def MAselect(_source, _lockback, _type):
        __block_result__ = na
        __switch__ = _type
        if __switch__ == "EMA":
            __block_result__ = ta__ren__.ema(_source, _lockback)
        elif __switch__ == "SMA":
            __block_result__ = ta__ren__.sma(_source, _lockback)
        elif __switch__ == "WMA":
            __block_result__ = ta__ren__.wma(_source, _lockback)
        elif __switch__ == "Hull MA":
            __block_result__ = ta__ren__.hma(_source, _lockback)
        elif __switch__ == "VWMA":
            __block_result__ = ta__ren__.vwma(_source, _lockback)
        elif __switch__ == "RMA":
            __block_result__ = ta__ren__.rma(_source, _lockback)
        elif __switch__ == "TEMA":
            __block_result__ = ta__ren__.tema(_source, _lockback)
        return __block_result__

    MAtmp: Series = MAselect(MAsrc, MAlen, MAtype)
    TR = ta__ren__.tr(True)
    ATRtmp: Series = MAselect(TR, ATRlen, ATRtype)
    ATRfilter = ta__ren__.sma(TR, atrFilterLen)
    MAval: float = MAtmp[1]
    ATRval: float = ATRtmp[1]
    ATRupper = MAval + ATRval * ATRmult
    ATRlower = MAval - ATRval * ATRmult
    plot(MAval, title='MA Line', color=color.blue, linewidth=1)
    plotATRupper = plot(ATRupper, title='ATR Upper', color=color.green, linewidth=1)
    plotATRlower = plot(ATRlower, title='ATR Lower', color=color.red, linewidth=1)

    trend: PersistentSeries[int] = 0
    breakPoint: int = 0
    uptrendPrice = close if confirmSrc == 'Close' else high
    downtrendPrice = close if confirmSrc == 'Close' else low
    isUptrendRaw = uptrendPrice > ATRupper
    isDowntrendRaw = downtrendPrice < ATRlower
    isUptrendConfirmed = ta__ren__.barssince(not isUptrendRaw) == confirmBars
    isDowntrendConfirmed = ta__ren__.barssince(not isDowntrendRaw) == confirmBars
    if isUptrendConfirmed and trend != 1:
        trend = 1
        breakPoint = 1
    if isDowntrendConfirmed and trend != -1:
        trend = -1
        breakPoint = -1
    uptrendBg = color.new(color.green, 80)
    downtrendBg = color.new(color.red, 80)
    NeutralBg = color.new(color.gray, 80)
    fill(plotATRupper, plotATRlower, color=uptrendBg if trend == 1 else downtrendBg if trend == -1 else NeutralBg)

    newUptrend = trend == 1 and trend[1] != 1
    newDowntrend = trend == -1 and trend[1] != -1
    endUptrend = trend[1] == 1 and trend != 1
    endDowntrend = trend[1] == -1 and trend != -1
    trendBars: Persistent[int] = 0
    startTrendPrice: Persistent[float] = na(float)
    highestTrendPrice: Persistent[float] = na(float)
    lowestTrendPrice: Persistent[float] = na(float)
    mfe: Persistent[float] = na(float)
    mae: Persistent[float] = na(float)
    totalTrend: Persistent[int] = 0
    validTrend: Persistent[int] = 0
    validMae: Persistent[int] = 0
    validTrendPct: Persistent[float] = na(float)
    totalMaePct: Persistent[float] = 0
    totalMfePct: Persistent[float] = 0
    avgMaePct: Persistent[float] = na(float)
    avgMfePct: Persistent[float] = na(float)
    totalEfficiency: Persistent[float] = 0
    avgEfficiency: Persistent[float] = na(float)
    totalVolatility: Persistent[float] = 0
    avgVolatility: Persistent[float] = na(float)
    mfeArr: Persistent[list[float]] = array.new_float()
    maeArr: Persistent[list[float]] = array.new_float()
    if endUptrend or endDowntrend:
        totalTrend += 1
        isValid = ATRval / startTrendPrice * ATRmult
        if mfe / startTrendPrice > 0:
            if mfe / startTrendPrice > isValid:
                validTrend += 1
            mfePct = mfe / startTrendPrice * 100
            totalMfePct += mfePct
            array.push(mfeArr, mfePct)
        if mae / startTrendPrice > 0:
            validMae += 1
            maePct = mae / startTrendPrice * 100
            totalMaePct += maePct
            array.push(maeArr, maePct)
        trendRange = highestTrendPrice - lowestTrendPrice
        efficiency = (mfe - mae) / trendRange if trendRange > 0 else 0
        totalEfficiency += efficiency
        volatility = trendRange / startTrendPrice * 100
        totalVolatility += volatility
    if newUptrend or newDowntrend:
        startTrendPrice = close
        highestTrendPrice = close
        lowestTrendPrice = close
        mfe = 0
        mae = 0
        trendBars = 0
    if trend == 1 or trend == -1:
        trendBars += 1
    else:
        trendBars = 0
    if trendBars > 1:
        highestTrendPrice = math.max(highestTrendPrice, high)
        lowestTrendPrice = math.min(lowestTrendPrice, low)
        if trend == 1:
            mfe = highestTrendPrice - startTrendPrice
            mae = startTrendPrice - lowestTrendPrice
        if trend == -1:
            mfe = startTrendPrice - lowestTrendPrice
            mae = highestTrendPrice - startTrendPrice
    maxSamples: int = 500
    if array.size(mfeArr) > maxSamples:
        array.shift(mfeArr)
    sortedMfe: list[float] = array.copy(mfeArr)
    array.sort(sortedMfe)
    if array.size(maeArr) > maxSamples:
        array.shift(maeArr)
    sortedMae: list[float] = array.copy(maeArr)
    array.sort(sortedMae)
    def f_percentile(arr, p):
        size__ren__ = array.size(arr)
        __block_result_1__ = na
        if size__ren__ == 0:
            __block_result_1__ = na
        else:
            idx = (size__ren__ - 1) * p
            lower = math.floor(idx)
            upper = math.ceil(idx)
            lowerVal = array.get(arr, lower)
            upperVal = array.get(arr, upper)
            __block_result_1__ = lowerVal + (upperVal - lowerVal) * (idx - lower)
        return __block_result_1__

    mfeP50 = f_percentile(sortedMfe, 0.5)
    mfeP70 = f_percentile(sortedMfe, 0.7)
    mfeP90 = f_percentile(sortedMfe, 0.9)
    maeP50 = f_percentile(sortedMae, 0.5)
    maeP70 = f_percentile(sortedMae, 0.7)
    maeP90 = f_percentile(sortedMae, 0.9)
    plot(avgMfePct, 'Avg MFE', display=display.data_window)
    plot(mfeP50, 'MFE Position 50%', display=display.data_window)
    plot(mfeP70, 'MFE Position 70%', display=display.data_window)
    plot(mfeP90, 'MFE Position 90%', display=display.data_window)
    plot(avgMaePct, 'Avg MAE', display=display.data_window)
    plot(maeP50, 'MAE Position 50%', display=display.data_window)
    plot(maeP70, 'MAE Position 70%', display=display.data_window)
    plot(maeP90, 'MAE Position 90%', display=display.data_window)
    plot(avgEfficiency, 'Efficiency', display=display.data_window)
    plot(avgVolatility, 'Volatility', display=display.data_window)
    validTrendPct = validTrend / totalTrend * 100
    avgMaePct = totalMaePct / validMae if validMae > 0 else na
    avgMfePct = totalMfePct / validTrend if validTrend > 0 else na
    avgEfficiency = totalEfficiency / totalTrend if totalTrend > 0 else na
    avgVolatility = totalVolatility / totalTrend if totalTrend > 0 else na
    trendTable: Persistent[Table] = table.new(position=position.bottom_right, columns=2, rows=4, bgcolor=color.rgb(0, 255, 255, 30), border_color=color.black, border_width=2)
    table.cell(trendTable, 0, 0, 'Total Trends')
    table.cell(trendTable, 1, 0, string.tostring(totalTrend))
    table.cell(trendTable, 0, 1, 'Valid Trends')
    table.cell(trendTable, 1, 1, string.tostring(validTrend) + '\n' + string.tostring(validTrendPct, '#.##') + '%')
    table.cell(trendTable, 0, 2, 'Auto TP')
    table.cell(trendTable, 1, 2, string.tostring(mfeP70, '#.##') + '%')
    table.cell(trendTable, 0, 3, 'Auto SL')
    table.cell(trendTable, 1, 3, string.tostring(maeP70, '#.##') + '%')

    offset = 100 * syminfo.mintick
    longSignal: bool = False
    shortSignal: bool = False
    crossUnder = ta__ren__.crossunder(low, MAval)
    crossOver = ta__ren__.crossover(high, MAval)
    crossUsed: Persistent[bool] = False
    positionClosed = strategy.position_size == 0 and strategy.position_size[1] != 0
    if positionClosed:
        crossUsed = False
    if entryMethod == 'Breakout':
        longSignal = breakPoint == 1
        shortSignal = breakPoint == -1
    if entryMethod == 'MA Cross' and (not crossUsed):
        longSignal = trend == 1 and crossUnder
        shortSignal = trend == -1 and crossOver
    atrfilterActive = ATRval > ATRfilter
    if strategy.position_size == 0:
        if atrfilterActive if longSignal and useAtrFilter else longSignal:
            strategy.entry('Long', strategy.long)
        if atrfilterActive if shortSignal and useAtrFilter else shortSignal:
            strategy.entry('Short', strategy.short)

    if ta__ren__.barssince(strategy.position_size <= 0) == 1:
        label.new(x=bar_index, y=low - offset, text='Long', color=color.green, style=label.style_label_up, size=size.normal)
    if ta__ren__.barssince(strategy.position_size >= 0) == 1:
        label.new(x=bar_index, y=high + offset, text='Short', color=color.red, size=size.normal)

    TPthresh = mfeP70 if useAutoTP_SL else TPinput
    SLthresh = maeP70 if useAutoTP_SL else SLinput
    longTP = strategy.position_avg_price * (1 + TPthresh / 100)
    longSL = strategy.position_avg_price * (1 - SLthresh / 100)
    shortTP = strategy.position_avg_price * (1 - TPthresh / 100)
    shortSL = strategy.position_avg_price * (1 + SLthresh / 100)
    strategy.exit('Long Exit', 'Long', limit=longTP, stop=longSL)
    strategy.exit('Short Exit', 'Short', limit=shortTP, stop=shortSL)
    longBox: Persistent[Box] = na(Box)
    if strategy.position_size > 0 and na(longBox):
        longBox = box.new(left=bar_index, right=bar_index, top=longTP, bottom=longSL, border_width=0, bgcolor=color.new(color.blue, 80))
    if not na(longBox):
        box.set_right(longBox, bar_index)
    shortBox: Persistent[Box] = na(Box)
    if strategy.position_size < 0 and na(shortBox):
        shortBox = box.new(left=bar_index, right=bar_index, top=shortSL, bottom=shortTP, border_width=0, bgcolor=color.new(color.blue, 80))
    if not na(shortBox):
        box.set_right(shortBox, bar_index)
    if strategy.position_size == 0:
        longBox = na
        shortBox = na

    statsTable: Persistent[Table] = table.new(position=position.top_right, columns=2, rows=7, bgcolor=color.rgb(0, 255, 255, 30), border_color=color.black, border_width=2)
    totalTrades = strategy.closedtrades
    wintrades = strategy.wintrades
    lossTrades = strategy.losstrades
    netProfit = strategy.netprofit_percent
    profitFactor = strategy.grossprofit / math.abs(strategy.grossloss)
    winRate = wintrades / totalTrades * 100 if totalTrades > 0 else na
    avgWin = strategy.grossprofit / wintrades if wintrades > 0 else na
    avgLoss = math.abs(strategy.grossloss) / lossTrades if lossTrades > 0 else na
    lossRate = 100 - winRate
    expectancy = winRate / 100 * avgWin - lossRate / 100 * avgLoss
    avgR = avgWin / avgLoss
    maxDDpct = strategy.max_drawdown_percent
    table.cell(statsTable, 0, 0, 'Total Trades')
    table.cell(statsTable, 1, 0, string.tostring(totalTrades))
    table.cell(statsTable, 0, 1, 'Win Rate')
    table.cell(statsTable, 1, 1, string.tostring(winRate, '#.##') + '%')
    table.cell(statsTable, 0, 2, 'Profit Factor')
    table.cell(statsTable, 1, 2, string.tostring(profitFactor, '#.##'))
    table.cell(statsTable, 0, 3, 'Net Profit')
    table.cell(statsTable, 1, 3, string.tostring(netProfit, '#.##') + '%')
    table.cell(statsTable, 0, 4, 'Expectancy')
    table.cell(statsTable, 1, 4, string.tostring(expectancy, '#.##'))
    table.cell(statsTable, 0, 5, 'Avg R')
    table.cell(statsTable, 1, 5, string.tostring(avgR, '#.##'))
    table.cell(statsTable, 0, 6, 'M.Drawdown')
    table.cell(statsTable, 1, 6, string.tostring(maxDDpct, '#.##') + '%')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
