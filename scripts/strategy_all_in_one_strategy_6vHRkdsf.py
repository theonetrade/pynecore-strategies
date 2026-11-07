"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barcolor, bgcolor, close, color, fill, high, hline, input, label, low,
    math, na, nz, ohlc4, open, plot, scale, script, size, strategy, string, ta, text, time,
    timestamp, xloc, yloc
)
from pynecore.types import Color, Label, NA, Persistent, Series


@script.strategy(shorttitle='Ain1v4', title='All in One Strategy', overlay=True, scale=scale.left, initial_capital=1000, process_orders_on_close=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.18, calc_on_every_tick=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    start=input.time(defval=timestamp('22 June 2021 00:00 -0500'), title='Start Time'),
    finish=input.time(defval=timestamp('31 December 2021 00:00 -0600'), title='End Time'),
    stratinfo=input(True, 'Long/Short for Mixed Market, Long for Bull, Short for Bear'),
    strat=input.string(title='Trade Types', defval='Long/Short', options=('Long Only', 'Long/Short', 'Short Only')),
    sl=input.float(10.0, 'Stop Loss %', minval=0, maxval=100, step=0.01),
    tp=input.float(20.0, 'Target Profit %', minval=0, maxval=100, step=0.01),
    ld=input.int(2, 'Stop Trading After This Many Losing Days', minval=0, maxval=100, step=1),
    ml=input.int(10, 'Maximum % of Equity Lost to Halt Trading', minval=1, maxval=100, step=1),
    useXRSI=input(False, 'Use RSI crossing back, select only one strategy'),
    useCRSI=input(False, 'Use Tweaked Connors RSI, select only one'),
    RSIInfo=input(True, 'These are the RSI Strategy Inputs, RSI Length applies to MACD, set OB and OS to 45 for using Stoch and EMA strategies.'),
    length=input.int(14, 'RSI Length', minval=1),
    overbought=input(62, 'Overbought'),
    oversold=input(35, 'Oversold'),
    cl1=input.int(3, 'Connor\'s MA Length 1', minval=1, step=1),
    cl2=input.int(20, 'Connor\'s MA Lenght 2', minval=1, step=1),
    cl3=input.int(50, 'Connor\'s MA Lenght 3', minval=1, step=1),
    useMACD=input(False, 'Use MACD Only, select only one strategy'),
    useEMA=input(False, 'Use EMA Only, select only one strategy (EMA uses Stochastic inputs too)'),
    MACDInfo=input(True, 'These are the MACD strategy variables'),
    fastLength=input.int(5, minval=1, title='EMA Fast Length'),
    slowLength=input.int(10, minval=1, title='EMA Slow Length'),
    ob_min=input.int(52, 'Overbought Lookback Minimum Value', minval=0, maxval=200),
    ob_lb=input.int(25, 'Overbought Lookback Bars', minval=0, maxval=100),
    os_min=input.int(50, 'Oversold Lookback Minimum Value', minval=0, maxval=200),
    os_lb=input.int(35, 'Oversold Lookback Bars', minval=0, maxval=100),
    source: Series[float] = input(title='Source', defval=close),
    PriceInfo=input(True, 'Price Change Percentage Cross Check Inputs for all Strategies, added logic to avoid early sell. This is different from setting of max loss in risk management.'),
    lkbk=input(5, 'Max Lookback Period'),
    useStoch=input(False, 'Use Stochastic Strategy, choose only one'),
    StochInfo=input(True, 'Stochastic Strategy Inputs'),
    smoothK=input.int(3, 'K', minval=1),
    periodK=input.int(14, 'K Period', minval=1),
    periodD=input.int(3, 'D Period', minval=1),
    k_mode=input.string('SMA', 'K Mode', options=('SMA', 'EMA', 'WMA')),
    high_source: Series[float] = input(high, 'High Source'),
    low_source: Series[float] = input(low, 'Low Source'),
    showZones=input(True, title='Show Bullish/Bearish Zones'),
    showStoch=input(True, title='Show Stochastic Overlays'),
    showRSIBS=input(True, title='Show RSI Buy Sell Zones'),
    showMACD=input(True, title='Show MACD'),
    color_bars=input(True, 'Color Bars')
):
    kcolor = color.new(color.new('#0094FF'), 60)
    dcolor = color.new(color.new('#FF6A00'), 60)
    def window():
        return True if time >= start and time <= finish else False

    strat_val = 1 if strat == 'Long Only' else 0 if strat == 'Long/Short' else -1
    stoploss = sl / 100
    TargetProfit = tp / 100
    strategy.risk.max_cons_loss_days(count=ld)
    strategy.risk.max_drawdown(value=ml, type=strategy.percent_of_equity)
    RSI = ta.rsi(source, length)
    def f_print(_text):
        _label: Persistent = NA(Label)
        label.delete(_label)
        _label = label.new(time + time - time[1], ohlc4, _text, xloc.bar_time, yloc.price, NA(Color), label.style_none, color.gray, size.large, text.align_left)
        return _label

    def AvgHigh(src: Series, cnt, val):
        total: float = 0.0
        count: int = 0
        for i in pine_range(0, cnt, 1):
            if src[i] > val:
                count = count + 1
                total = total + src[i]
        return math.round(total / count)

    RSI_high = AvgHigh(RSI, ob_lb, ob_min)
    def AvgLow(src: Series, cnt, val):
        total: float = 0.0
        count: int = 0
        for i in pine_range(5, cnt, 5):
            if src[i] < val:
                count = count + 1
                total = total + src[i]
        return math.round(total / count)

    RSI_low = AvgLow(RSI, os_lb, os_min)
    f_print('Recommended RSI Settings:' + '\nOverbought = ' + string.tostring(RSI_high) + '\nOversold = ' + string.tostring(RSI_low))
    over = hline(oversold, title='Oversold', color=color.green)
    under = hline(overbought, title='Overbought', color=color.red)
    fillcolor = color.new(color.new('#9915FF'), 90)
    fill(over, under, fillcolor, title='Band Background')
    rsi_ema = ta.ema(RSI, length)
    emaA = ta.ema(rsi_ema, fastLength)
    emaFast = 2 * emaA - ta.ema(emaA, fastLength)
    emaB = ta.ema(rsi_ema, slowLength)
    emaSlow = 2 * emaB - ta.ema(emaB, slowLength)
    out: Series = ta.ema(RSI, length)
    bullishRule = emaFast > emaSlow and out >= out[1]
    bearishRule = emaFast < emaSlow and out <= out[1]
    crossunder_1 = ta.crossunder(rsi_ema, emaSlow)
    window_1 = window()
    EMAShortSell = ta.crossunder(rsi_ema, emaFast) and crossunder_1 and bearishRule and window_1
    crossover_1 = ta.crossover(rsi_ema, emaSlow)
    window_2 = window()
    EMAShortBuy = ta.crossover(rsi_ema, emaFast) and crossover_1 and bullishRule and window_2
    crossover_2 = ta.crossover(rsi_ema, emaFast)
    window_3 = window()
    EMALongBuy = ta.crossover(rsi_ema, emaSlow) and crossover_2 and bullishRule and window_3
    window_4 = window()
    EMALongSell = ta.crossunder(emaFast, emaSlow) and bearishRule and window_4
    ruleState: Series[int] = 0
    ruleState = 1 if bullishRule else -1 if bearishRule else nz(ruleState[1])
    ruleColor = color.new(color.blue, 90) if ruleState == 1 else color.new(color.red, 90) if ruleState == -1 else color.new(color.gray, 90) if ruleState == 0 else na
    bgcolor(ruleColor if showZones else na, title='Bullish/Bearish Zones')
    def perc_change(lkbk):
        overall_change = (close - open[lkbk]) / open[lkbk] * 100
        highest_high: Series[float] = 0.0
        lowest_low: Series[float] = 0.0
        for i in pine_range(lkbk, 0, 1):
            highest_high = high if i == lkbk else high[i] if high[i] > high[i + 1] else highest_high[1]
            lowest_low = low if i == lkbk else low[i] if low[i] < low[i + 1] else lowest_low[1]
        start_to_high = (highest_high - open[lkbk]) / open[lkbk] * 100
        start_to_low = (lowest_low - open[lkbk]) / open[lkbk] * 100
        previous_to_high = (highest_high - open[1]) / open[1] * 100
        previous_to_low = (lowest_low - open[1]) / open[1] * 100
        previous_bar = (close[1] - open[1]) / open[1] * 100
        return (overall_change, start_to_high, start_to_low, previous_to_high, previous_to_low, previous_bar)

    overall, to_high, to_low, last_high, last_low, last_bar = perc_change(lkbk)
    true_dip = overall < 0 and to_high > 0 and (to_low < 0) and (last_high > 0) and (last_low < 0) and (last_bar < 0)
    true_peak = overall > 0 and to_high > 0 and (to_low > 0) and (last_high > 0) and (last_low < 0) and (last_bar > 0)
    h_high: Series = ta.highest(high_source, lkbk)
    l_low: Series = ta.lowest(low_source, lkbk)
    stoch = ta.stoch(close, high_source, low_source, periodK)
    k = ta.ema(stoch, smoothK) if k_mode == 'EMA' else ta.wma(stoch, smoothK) if k_mode == 'WMA' else ta.sma(stoch, smoothK)
    d = ta.sma(k, periodD)
    k_c = ta.change(k)
    d_c = ta.change(d)
    kd = k - d
    signalColor = kcolor if k > oversold and d < overbought and (k > d) and (k_c > 0) and (d_c > 0) else dcolor if k < overbought and d > oversold and (k < d) and (k_c < 0) and (d_c < 0) else na
    kp = plot(k if showStoch else na, 'K', color=kcolor)
    dp = plot(d if showStoch else na, 'D', color=dcolor)
    fill(kp, dp, color=signalColor, title='K-D')
    signalUp = not na(signalColor) and kd > 0 if showStoch else False
    signalDown = not na(signalColor) and kd < 0 if showStoch else False
    window_5 = window()
    StochBuy = ta.crossover(k, d) and k_c > 0 and (d_c > 0) and (k < RSI) and (d < RSI) and window_5
    window_6 = window()
    StochSell = ta.crossunder(k, d) and k_c < 0 and (d_c < 0) and (k < RSI) and (d < RSI) and window_6
    h1 = ta.vwma(high, length)
    l1 = ta.vwma(low, length)
    hp = h_high[1]
    lp = l_low[1]
    plot_color: Persistent[Color] = color.new('#353535')
    sig: Persistent[int] = 0
    if h1 > hp:
        sig = 1
        plot_color = color.lime
    elif l1 < lp:
        sig = -1
        plot_color = color.maroon
    connor_ob = overbought
    connor_os = oversold
    ma1 = ta.sma(close, cl1)
    ma2 = ta.sma(close, cl2)
    ma3 = ta.sma(close, cl3)
    window_7 = window()
    RSI_SELL = ma1 > ma2 and open > ma3 and (RSI >= connor_ob) and true_peak and window_7
    window_8 = window()
    RSI_BUY = ma2 < ma3 and ma3 > close and (RSI <= connor_os) and true_dip and window_8
    col = (color.lime if close > ma2 and close < ma3 and (RSI <= connor_os) else color.red if close < ma2 and close > ma3 and (RSI <= connor_ob) else color.yellow) if useCRSI else color.yellow
    plot(RSI, title='RSI', linewidth=3, color=col)
    macdLine, signalLine, _ = ta.macd(close, fastLength, slowLength, length)
    bartrendcolor = color.teal if macdLine > signalLine and k > 50 and (RSI > 50) else color.maroon if macdLine < signalLine and k < 50 and (RSI < 50) else color.yellow if macdLine < signalLine else color.gray
    barcolor(color=bartrendcolor if color_bars else na)
    window_9 = window()
    MACDBuy = macdLine > signalLine and RSI < RSI_low and (overall < 0) and window_9
    window_10 = window()
    MACDSell = macdLine < signalLine and RSI > RSI_high and (overall > 0) and window_10
    MACColor = color.new(color.teal, 50) if MACDBuy else color.new(color.maroon, 50) if MACDSell else na
    bgcolor(MACColor if showMACD else na, title='MACD Signals')
    window_11 = window()
    XRSI_OB = ta.crossunder(RSI, overbought) and overall < 0 and window_11
    window_12 = window()
    RSI_OB = RSI > overbought and true_peak and window_12
    window_13 = window()
    XRSI_OS = ta.crossover(RSI, oversold) and overall > 0 and window_13
    window_14 = window()
    RSI_OS = RSI < oversold and true_dip and window_14
    if strategy.opentrades == 0 and strat_val > -1:
        OtherLong = rsi_ema > RSI and k < d
        GoLong = StochBuy if useStoch else OtherLong and XRSI_OS if useXRSI else OtherLong and MACDBuy if useMACD else OtherLong and RSI_BUY if useCRSI else EMALongBuy if useEMA else RSI_OS
        if GoLong:
            strategy.entry('LONG', strategy.long)
    if strategy.opentrades == 0 and strat_val < 1:
        OtherShort = rsi_ema < RSI and d < k
        GoShort = StochSell if useStoch else OtherShort and XRSI_OB if useXRSI else OtherShort and MACDSell if useMACD else OtherShort and RSI_SELL if useCRSI else EMAShortSell if useEMA else OtherShort and RSI_OB
        if GoShort:
            strategy.entry('SHORT', strategy.short)
    longStopPrice = strategy.position_avg_price * (1 - stoploss)
    longTakePrice = strategy.position_avg_price * (1 + TargetProfit)
    shortStopPrice = strategy.position_avg_price * (1 + stoploss)
    shortTakePrice = strategy.position_avg_price * (1 - TargetProfit)
    if strategy.position_size > 0:
        strategy.exit(id='Exit Long', from_entry='LONG', stop=longStopPrice, limit=longTakePrice)
    if strategy.position_size < 0:
        strategy.exit(id='Exit Short', from_entry='SHORT', stop=shortStopPrice, limit=shortTakePrice)
    StochLong2 = strategy.position_size < 0 and strat_val > -1
    OtherLong2 = strategy.position_size < 0 and strat_val > -1 and (rsi_ema > RSI) and (k < d)
    CloseShort = StochLong2 and StochBuy if useStoch else OtherLong2 and XRSI_OS if useXRSI else OtherLong2 and MACDBuy if useMACD else OtherLong2 and RSI_BUY if useCRSI else EMAShortBuy if useEMA else RSI_OS
    StochShort2 = strategy.position_size > 0 and strat_val < 1
    OtherShort2 = strategy.position_size > 0 and strat_val < 1 and (rsi_ema < RSI) and (d < k)
    CloseLong = StochShort2 and StochSell if useStoch else OtherShort2 and XRSI_OB if useXRSI else OtherShort2 and MACDSell if useMACD else OtherShort2 and RSI_SELL if useCRSI else EMALongSell if useEMA else OtherShort2 and RSI_OB
    if CloseLong:
        strategy.close('LONG')
    if CloseShort:
        strategy.close('SHORT')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
