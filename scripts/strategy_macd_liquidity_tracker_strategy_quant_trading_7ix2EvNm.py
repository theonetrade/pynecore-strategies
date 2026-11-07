"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, hline, input, location, low, na, nz,
    open, plot, plotcandle, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.strategy(title='MACD Liquidity Tracker Strategy [Quant Trading]', overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, slippage=3, initial_capital=1000, margin_long=0, margin_short=0)
def main(
    startDate=input.time(timestamp('01 Jan 2018 00:00 +0000'), "Start Date", group="Date Range"),
    endDate=input.time(timestamp('31 Dec 2069 23:59 +0000'), "End Date", group="Date Range"),
    allowShortTrades=input.bool(False, "Allow Short Trades?", group="Short Trades"),
    fastMA=input.int(title='Fast MA', defval=25, minval=1, step=1, group="MACD Settings", tooltip="Fast EMA period for MACD calculation"),
    slowMA=input.int(title='Slow MA', defval=60, minval=1, step=1, group="MACD Settings", tooltip="Slow EMA period for MACD calculation"),
    signalMA=input.int(title='Signal MA', defval=220, minval=1, step=1, group="MACD Settings", tooltip="Signal line EMA period - now actually used!"),
    systemChoice=input.string(title="System Type", defval="Normal", options=("Fast", "Normal", "Safe", "Crossover"), group="System Logic"),
    ma_type=input.string(title="MA Type", defval="EMA", options=("SMA", "EMA", "WMA", "HMA", "RMA", "LSMA", "DEMA", "TEMA", "VIDYA"), group="Trend MA Settings"),
    ma_length=input.int(title="MA Length", defval=50, minval=1, step=1, group="Trend MA Settings"),
    vidya_volatility_length=input.int(title="VIDYA Volatility Length", defval=9, minval=1, group="Trend MA Settings"),
    useStopLoss=input.bool(title="Enable Stop Loss", defval=False, group="Risk Management"),
    stopLossPercent=input.float(title="Stop Loss %", defval=3.0, minval=0.1, step=0.1, group="Risk Management"),
    useTakeProfit=input.bool(title="Enable Take Profit", defval=False, group="Risk Management"),
    takeProfitPercent=input.float(title="Take Profit %", defval=6.0, minval=0.1, step=0.1, group="Risk Management"),
    signalDisplay=input.string(title="Show Signals", defval="Both", options=("Both", "Long Only", "Short Only", "None"), group="Signal Display"),
    showText=input.bool(title="Show Signal Text", defval=True, group="Signal Display")
):
    inDateRange = time >= startDate and time <= endDate

    smoothedMA: Persistent[float] = 0.0
    if ma_type == 'SMA':
        smoothedMA = ta.sma(close, ma_length)
    elif ma_type == 'EMA':
        smoothedMA = ta.ema(close, ma_length)
    elif ma_type == 'WMA':
        smoothedMA = ta.wma(close, ma_length)
    elif ma_type == 'HMA':
        smoothedMA = ta.hma(close, ma_length)
    elif ma_type == 'RMA':
        smoothedMA = ta.rma(close, ma_length)
    elif ma_type == 'LSMA':
        smoothedMA = ta.linreg(close, ma_length, 0)
    elif ma_type == 'DEMA':
        ema1: float = ta.ema(close, ma_length)
        ema2: float = ta.ema(ema1, ma_length)
        smoothedMA = 2 * ema1 - ema2
    elif ma_type == 'TEMA':
        ema1: float = ta.ema(close, ma_length)
        ema2: float = ta.ema(ema1, ma_length)
        ema3: float = ta.ema(ema2, ma_length)
        smoothedMA = 3 * ema1 - 3 * ema2 + ema3
    elif ma_type == 'VIDYA':
        volatility: float = ta.stdev(close, vidya_volatility_length)
        effectiveVolatility: float = 0.01 if volatility == 0 else volatility
        alpha: float = 2.0 / (ma_length + 1)
        k: float = ta.stdev(close, vidya_volatility_length) / ta.stdev(ta.stdev(close, vidya_volatility_length), vidya_volatility_length)
        k = 1.0 if k > 1.0 else 0.0 if k < 0.0 else k
        vidyaValue: Series[float] = 0.0
        vidyaValue = alpha * k * close + (1 - alpha * k) * nz(vidyaValue[1], close)
        smoothedMA = vidyaValue

    currentMacd, currentSignal, currentHistogram = ta.macd(close, fastMA, slowMA, signalMA)
    previousMacd, previousSignal, previousHistogram = ta.macd(close[1], fastMA, slowMA, signalMA)

    colorBrightBlue = color.rgb(0, 169, 230)
    colorDarkBlueTransp = color.rgb(2, 25, 225, 31)
    colorBrightMagenta = color.rgb(255, 0, 238)
    colorDarkMagentaTransp = color.rgb(178, 0, 169, 17)

    __block_result__ = na
    if currentMacd > 0:
        __block_result_1__ = na
        if currentMacd > previousMacd:
            __block_result_1__ = colorBrightBlue
        else:
            __block_result_1__ = colorDarkBlueTransp
        __block_result__ = __block_result_1__
    elif currentMacd <= 0:
        __block_result_2__ = na
        if currentMacd < previousMacd:
            __block_result_2__ = colorBrightMagenta
        else:
            __block_result_2__ = colorDarkMagentaTransp
        __block_result__ = __block_result_2__
    plotColor = __block_result__

    isBrightBlue = plotColor == colorBrightBlue
    isDarkBlueTransp = plotColor == colorDarkBlueTransp
    isBrightMagenta = plotColor == colorBrightMagenta
    isDarkMagentaTransp = plotColor == colorDarkMagentaTransp

    macdCrossoverLong: Persistent[bool] = currentMacd > currentSignal and previousMacd <= previousSignal and (not na(currentSignal)) and (not na(previousSignal))
    macdCrossoverShort: Persistent[bool] = currentMacd < currentSignal and previousMacd >= previousSignal and (not na(currentSignal)) and (not na(previousSignal))

    longSignal: PersistentSeries[bool] = False
    shortSignal: PersistentSeries[bool] = False

    if systemChoice == 'Fast':
        longSignal = isBrightBlue or isDarkMagentaTransp
        shortSignal = isDarkBlueTransp or isBrightMagenta
    elif systemChoice == 'Normal':
        longSignal = currentMacd > currentSignal and (not na(currentSignal))
        shortSignal = currentMacd < currentSignal and (not na(currentSignal))
    elif systemChoice == 'Safe':
        longSignal = isBrightBlue
        shortSignal = isDarkBlueTransp or isBrightMagenta or isDarkMagentaTransp
    elif systemChoice == 'Crossover':
        longSignal = macdCrossoverLong
        shortSignal = macdCrossoverShort

    __block_result_3__ = na
    if longSignal:
        __block_result_3__ = colorBrightBlue
    elif shortSignal:
        __block_result_3__ = colorBrightMagenta
    else:
        __block_result_3__ = na
    candleColor = __block_result_3__

    isAboveMA = close > smoothedMA
    isBelowMA = close < smoothedMA

    longEntryCondition = longSignal and (not longSignal[1]) and inDateRange
    shortEntryCondition = shortSignal and (not shortSignal[1]) and inDateRange

    longEntry = longEntryCondition
    shortEntry = shortEntryCondition and allowShortTrades

    longExit = shortSignal and (not shortSignal[1]) and inDateRange
    shortExit = longSignal and (not longSignal[1]) and inDateRange

    if longEntry:
        strategy.entry('Long', strategy.long)

    if shortEntry:
        strategy.entry('Short', strategy.short)

    if longExit:
        strategy.close('Long')

    if shortExit:
        strategy.close('Short')

    if useStopLoss and useTakeProfit:
        strategy.exit('Long SL/TP', from_entry='Long', stop=close * (1 - stopLossPercent / 100), limit=close * (1 + takeProfitPercent / 100))
        strategy.exit('Short SL/TP', from_entry='Short', stop=close * (1 + stopLossPercent / 100), limit=close * (1 - takeProfitPercent / 100))
    elif useStopLoss:
        strategy.exit('Long SL', from_entry='Long', stop=close * (1 - stopLossPercent / 100))
        strategy.exit('Short SL', from_entry='Short', stop=close * (1 + stopLossPercent / 100))
    elif useTakeProfit:
        strategy.exit('Long TP', from_entry='Long', limit=close * (1 + takeProfitPercent / 100))
        strategy.exit('Short TP', from_entry='Short', limit=close * (1 - takeProfitPercent / 100))

    plot(smoothedMA, title='Trend MA', color=color.gray, linewidth=1, force_overlay=True)

    showLongSignal = signalDisplay == 'Both' or signalDisplay == 'Long Only'
    showShortSignal = signalDisplay == 'Both' or signalDisplay == 'Short Only'

    plotshape(showText and showLongSignal and longEntryCondition, title='Long Entry Signal with Text', location=location.belowbar, color=candleColor, style=shape.triangleup, size=size.small, text='Long', textcolor=candleColor, force_overlay=True)
    plotshape(showText and showShortSignal and shortEntryCondition, title='Short Entry Signal with Text', location=location.abovebar, color=candleColor, style=shape.triangledown, size=size.small, text='Short', textcolor=candleColor, force_overlay=True)

    plotshape(not showText and showLongSignal and longEntryCondition, title='Long Entry Signal without Text', location=location.belowbar, color=candleColor, style=shape.triangleup, size=size.small, force_overlay=True)
    plotshape(not showText and showShortSignal and shortEntryCondition, title='Short Entry Signal without Text', location=location.abovebar, color=candleColor, style=shape.triangledown, size=size.small, force_overlay=True)

    plotcandle(open, high, low, close, title='Colored Candles', color=candleColor, wickcolor=candleColor, bordercolor=candleColor, force_overlay=True)

    macdPlot = plot(currentMacd, title='MACD Line', style=plot.style_line, color=color.blue, linewidth=2)
    signalPlot = plot(currentSignal, title='Signal Line', style=plot.style_line, color=color.red, linewidth=1)
    histogramPlot = plot(currentHistogram, title='MACD Histogram', style=plot.style_histogram, color=plotColor, linewidth=3)
    hline(0, title='Zero line', color=color.gray, linestyle=hline.style_dashed)

    alertcondition(longEntryCondition, title='Long Entry Signal Trigger', message='Long entry signal (triangle) detected.')
    alertcondition(shortEntryCondition, title='Short Entry Signal Trigger', message='Short entry signal (triangle) detected.')
    alertcondition(longExit, title='Long Exit Signal', message='Long exit signal detected.')
    alertcondition(shortExit, title='Short Exit Signal', message='Short exit signal detected.')

    isNeutralSell_Orig = isDarkMagentaTransp
    isNeutralBuy_Orig = isDarkBlueTransp
    isNoLeverage_Orig = isNeutralSell_Orig or isNeutralBuy_Orig or isBrightMagenta
    isLeverage_Orig = isBrightBlue

    alertcondition(isNeutralBuy_Orig, title='Color: Dark Blue Transp', message='Dark Blue Transp color detected.')
    alertcondition(isNeutralSell_Orig, title='Color: Dark Magenta Transp', message='Dark Magenta Transp color detected.')
    alertcondition(isNoLeverage_Orig, title='Color: No Leverage Colors', message='Indicator shows Dark Blue T, Dark Magenta T, or Bright Magenta.')
    alertcondition(isLeverage_Orig, title='Color: Bright Blue', message='Bright Blue (Leverage) color detected.')

    alertcondition(isAboveMA, title='Price Above MA', message='Price is above the selected MA.')
    alertcondition(isBelowMA, title='Price Below MA', message='Price is below the selected MA.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
