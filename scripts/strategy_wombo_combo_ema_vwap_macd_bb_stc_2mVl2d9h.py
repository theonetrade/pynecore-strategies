"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bgcolor, close, color, currency, fixnan, high, input, low, math, na, nz,
    open, plot, plotshape, script, shape, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('WOMBO COMBO: 100/200EMA & VWAP & MACD', shorttitle='WOMBO COMBO', default_qty_type=strategy.percent_of_equity, default_qty_value=5, initial_capital=20000, slippage=2, currency=currency.USD, overlay=True, pyramiding=2, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    price: Series[float] = input(title='Price Source', defval=close),
    RunTrend=input.string(title='Run Strategy Trending Up, Down, or Both', defval='Both', options=('Up', 'Down', 'Both')),
    EMAlength=input(title='EMA_Length', defval=200),
    ShowBB=input.string(title='Show BB', defval='Y', options=('Y', 'N')),
    cycleLength=input(title='Cycle Length', defval=40),
    upperSTC=input(title='Upper STC limit', defval=85),
    lowerSTC=input(title='Lower STC limit', defval=15),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromYear=input.int(defval=2020, title='From Year', minval=1970),
    thruMonth=input.int(defval=1, title='Thru Month', minval=1, maxval=12),
    thruDay=input.int(defval=1, title='Thru Day', minval=1, maxval=31),
    thruYear=input.int(defval=2112, title='Thru Year', minval=1970),
    showDate=input(defval=True, title='Show Date Range'),
    countback=input.int(minval=0, maxval=5, title='Price CountBack', defval=0),
    EMA_Y_N=input.string(defval='Y', title='Run EMA', options=('Y', 'N')),
    VWAP_Y_N=input.string(defval='Y', title='Run VWAP', options=('Y', 'N')),
    MACD_Y_N=input.string(defval='N', title='Run MACD', options=('Y', 'N')),
    BB_Y_N=input.string(defval='N', title='Run BB', options=('Y', 'N')),
    STC_Y_N=input.string(defval='Y', title='Run STC', options=('Y', 'N')),
    trailStop_YN=input.string(title='Run a Trailing Stop', defval='N', options=('Y', 'N')),
    __input_21__=input.float(title='Trail Loss %', minval=0, step=1, defval=6),
    __input_22__=input.float(15, title='Stop Loss %'),
    __input_23__=input.float(25, title='Take Profit %')
):
    EMA = ta.ema(price, EMAlength)
    ColorEMA = color.blue if EMAlength == 200 else color.aqua if EMAlength == 100 else color.orange if EMAlength == 50 else color.red
    plot(EMA, title='EMA', color=ColorEMA)
    ColorVWAP = color.lime if price > ta.vwap else color.maroon
    plot(ta.vwap, title='VWAP', color=ColorVWAP, linewidth=2)
    fast: int = 12
    slow: int = 26
    fastMA = ta.ema(price, fast)
    slowMA = ta.ema(price, slow)
    macd: Series = fastMA - slowMA
    signal: Series = ta.sma(macd, 9)
    lengthBB: int = 20
    multBB: int = 2
    basisBB = ta.sma(price, lengthBB)
    devBB = multBB * ta.stdev(price, lengthBB)
    upperBB = basisBB + devBB
    lowerBB = basisBB - devBB
    transP = 0 if ShowBB == 'Y' else 100
    plot(upperBB, title='BB Upper Band', color=color.aqua)
    plot(basisBB, title='BB Average', color=color.red)
    plot(lowerBB, title='BB Lower Band', color=color.aqua)
    fastLength: int = 23
    slowLength: int = 50
    d1Length: int = 3
    d2Length: int = 3
    srcSTC = close
    macdSTC = ta.ema(srcSTC, fastLength) - ta.ema(srcSTC, slowLength)
    k = nz(fixnan(ta.stoch(macdSTC, macdSTC, macdSTC, cycleLength)))
    d = ta.ema(k, d1Length)
    kd = nz(fixnan(ta.stoch(d, d, d, cycleLength)))
    stc = ta.ema(kd, d2Length)
    stc = 100 if stc > 100 else 0 if stc < 0 else stc
    ma1length: int = 35
    ma1 = ta.ema(close, ma1length)
    ma2 = ta.ema(close, EMAlength)
    STCbuy = ta.crossover(stc, lowerSTC)
    STCsell = ta.crossunder(stc, upperSTC)
    data2 = close[2] > open[2] and math.min(open[1], close[1]) > close[2] and (open < math.min(open[1], close[1])) and (close < open)
    data3 = close[2] < open[2] and math.max(open[1], close[1]) < close[2] and (open > math.max(open[1], close[1])) and (close > open)
    data4 = open[1] < close[1] and open > close[1] and (high - math.max(open, close) >= math.abs(open - close) * 3) and (math.min(close, open) - low <= math.abs(open - close))
    data5 = high - low > 3 * (open - close) and (close - low) / (0.001 + high - low) > 0.6 and ((open - low) / (0.001 + high - low) > 0.6)
    data5b = high - low > 3 * (open - close) and (high - close) / (0.001 + high - low) > 0.6 and ((high - open) / (0.001 + high - low) > 0.6)
    data6 = close[1] > open[1] and open > close and (open <= close[1]) and (open[1] <= close) and (open - close < close[1] - open[1])
    data7 = open[1] > close[1] and close > open and (close <= open[1]) and (close[1] <= open) and (close - open < open[1] - close[1])
    data8 = close[1] > open[1] and open > close and (open >= close[1]) and (open[1] >= close) and (open - close > close[1] - open[1])
    data9 = open[1] > close[1] and close > open and (close >= open[1]) and (close[1] >= open) and (close - open > open[1] - close[1])
    upper = inline_series(ta.highest(10), 1)
    data10 = close[1] < open[1] and open < low[1] and (close > close[1] + (open[1] - close[1]) / 2) and (close < open[1])
    lower = inline_series(ta.lowest(10), 1)
    data11 = low == open and open < lower and (open < close) and (close > (high[1] - low[1]) / 2 + low[1])
    data12 = open[1] > close[1] and open >= open[1] and (close > open)
    data13 = open[1] < close[1] and open <= open[1] and (close <= open)
    data14 = high - low > 4 * (open - close) and (close - low) / (0.001 + high - low) >= 0.75 and ((open - low) / (0.001 + high - low) >= 0.75) and (high[1] < open) and (high[2] < open)
    data15 = close[1] > open[1] and (close[1] + open[1]) / 2 > close and (open > close) and (open > close[1]) and (close > open[1]) and ((open - close) / (0.001 + high - low) > 0.6)
    start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finish = timestamp(thruYear, thruMonth, thruDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    window_1 = window()
    bgcolor(color=color.gray if showDate and window_1 else na)
    RunTrendUp: bool = False
    RunTrendUp = True if RunTrend == 'Up' or RunTrend == 'Both' else False
    RunTrendDWN: bool = False
    RunTrendDWN = True if RunTrend == 'Down' or RunTrend == 'Both' else False
    crossunder_1 = ta.crossunder(price[countback], lowerBB)
    crossunder_2 = ta.crossunder(signal[countback], macd[countback])
    dataHCLB = RunTrendUp and (STCbuy if STC_Y_N == 'Y' else True) and (price[countback] > EMA if EMA_Y_N == 'Y' else True) and (price[countback] > ta.vwap if VWAP_Y_N == 'Y' else True) and (crossunder_2 if MACD_Y_N == 'Y' else True) and (macd[countback] < 0 if MACD_Y_N == 'Y' else True) and (crossunder_1 if BB_Y_N == 'Y' else True)
    plotshape(dataHCLB, title='HC-LB', color=color.new(color.lime, 0), style=shape.circle, text='HC-LB')
    window_2 = window()
    if dataHCLB and window_2:
        strategy.entry('HC-Long', strategy.long, comment='HC-Long')
    crossover_1 = ta.crossover(price[countback], upperBB)
    crossunder_3 = ta.crossunder(macd[countback], signal[countback])
    dataHCSB = RunTrendDWN and (STCsell if STC_Y_N == 'Y' else True) and (price[countback] < EMA if EMA_Y_N == 'Y' else True) and (price[countback] < ta.vwap if VWAP_Y_N == 'Y' else True) and (crossunder_3 if MACD_Y_N == 'Y' else True) and (signal[countback] > 0 if MACD_Y_N == 'Y' else True) and (crossover_1 if BB_Y_N == 'Y' else True)
    plotshape(dataHCSB, title='HC-SB', color=color.new(color.fuchsia, 0), style=shape.circle, text='HC-SB')
    window_3 = window()
    if dataHCSB and window_3:
        strategy.entry('HC-Short', strategy.short, comment='HC-Short')
    TrailPerc = __input_21__ / 100
    stopPer = __input_22__ / 100
    takePer = __input_23__ / 100
    longStopPrice: Series[float] = 0.0
    __block_result__ = na
    if strategy.position_size > 0:
        stopValue = close * (1 - TrailPerc)
        __block_result__ = math.max(stopValue, longStopPrice[1])
    else:
        __block_result__ = 0
    longStopPrice = __block_result__
    shortStopPrice: Series[float] = 0.0
    __block_result_1__ = na
    if strategy.position_size < 0:
        shortStopValue = close * (1 + TrailPerc)
        __block_result_1__ = math.min(shortStopValue, shortStopPrice[1])
    else:
        __block_result_1__ = 999999
    shortStopPrice = __block_result_1__
    longStop = strategy.position_avg_price * (1 - stopPer)
    shortStop = strategy.position_avg_price * (1 + stopPer)
    shortTake = strategy.position_avg_price * (1 - takePer)
    longTake = strategy.position_avg_price * (1 + takePer)
    if strategy.position_size > 0:
        if window():
            strategy.exit(id='Close Long', stop=longStop, limit=longTake)
    if strategy.position_size < 0:
        if window():
            strategy.exit(id='Close Short', stop=shortStop, limit=shortTake)
    if strategy.position_size > 0:
        if trailStop_YN == 'Y':
            if window():
                strategy.exit(id='Close Long', stop=longStop, limit=longTake, qty_percent=50)
            if window():
                strategy.exit(id='Close Long Trailing Stop', stop=longStopPrice, qty_percent=100)
        if trailStop_YN == 'N':
            if window():
                strategy.exit(id='Close Long', stop=longStop, limit=longTake)
    if strategy.position_size < 0:
        if trailStop_YN == 'Y':
            if window():
                strategy.exit(id='Close Short', stop=shortStop, limit=shortTake, qty_percent=50)
            if window():
                strategy.exit(id='Close Short Trailing Stop', stop=shortStopPrice, qty_percent=100)
        if trailStop_YN == 'N':
            if window():
                strategy.exit(id='Close Short', stop=shortStop, limit=shortTake)
    plot(series=longStopPrice if strategy.position_size > 0 and trailStop_YN == 'Y' else na, color=color.new(color.fuchsia, 0), style=plot.style_cross, linewidth=2, title='Long Trail Stop')
    plot(series=shortStopPrice if strategy.position_size < 0 and trailStop_YN == 'Y' else na, color=color.new(color.fuchsia, 0), style=plot.style_cross, linewidth=2, title='Short Trail Stop')
    plot(series=longStop if strategy.position_size > 0 and trailStop_YN == 'N' else na, color=color.new(color.fuchsia, 0), style=plot.style_cross, linewidth=2, title='Long Trail Stop')
    plot(series=shortStop if strategy.position_size < 0 and trailStop_YN == 'N' else na, color=color.new(color.fuchsia, 0), style=plot.style_cross, linewidth=2, title='Short Trail Stop')
    plot(series=longTake if strategy.position_size > 0 else na, color=color.new(color.lime, 0), style=plot.style_cross, linewidth=2, title='Short Trail Stop')
    plot(series=shortTake if strategy.position_size < 0 else na, color=color.new(color.lime, 0), style=plot.style_cross, linewidth=2, title='Short Trail Stop')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
