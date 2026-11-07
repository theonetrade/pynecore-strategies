"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bgcolor, close, color, display, fill, high, hline, input, low, math, na,
    nz, open, plot, plotshape, script, shape, size, strategy, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Investments/swing trading strategy for different assets', overlay=True, process_orders_on_close=True, initial_capital=100000, default_qty_type=strategy.cash, pyramiding=1, precision=2, calc_on_every_tick=True, commission_value=0.05, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    how_to_use=input.bool(defval=True, title='How to use the strategy ----->', group='Information', tooltip='When there is a buy signal at the end of the candle, buy. To close, you must wait for the candle to close, exit in breakeven or, failing that, exit through stop loss. Use the amounts and stop loss based on the values ​​provided in the upper left corner by the indicator (choose the candlestick where the signal was produced to obtain the position information). Do not modify the parameters of the indicators as it is the most optimal setting for different assets from different markets. Use the info boxes to see more information about using the strategy'),
    initial_actual_capital_c=input.float(defval=1000000.0, title='Initial/Actual Capital', group='Position amount calculator', tooltip='Enter the current amount of your capital. This amount will be used to calculate the size of your position that will be reflected in the upper left corner of the indicator. Remember that to change the amount in the back test you must go to properties. >>The amount in currency units is the green value<<'),
    risk_c=input.float(defval=2.5, title='% account risk per trade', step=1, group='Position amount calculator'),
    initial_date=input.time(title='Initial date', defval=timestamp('01 Jan 1800 13:30 +0000'), group='Time filter', tooltip='Enter the start date and time of the strategy'),
    final_date=input.time(title='Final date', defval=timestamp('1 Jan 2030 19:30 +0000'), group='Time filter', tooltip='Enter the end date and time of the strategy'),
    colorDate=input.bool(defval=False, title='Date background', tooltip='Add color to the period of time of the strategy tester'),
    timeSession=input.session(title='Time session', defval='0000-2400', group='Time filter', tooltip='Session time to operate. It may be different depending on your time zone, you have to find the correct hours manually.'),
    colorBG=input.bool(title='Session background', defval=False, tooltip='Add color to session time background'),
    length=input(20, title='BB Length', group='Squeeze Momentum', inline='c'),
    mult=input(2.0, title='BB MultFactor', group='Squeeze Momentum', inline='c'),
    lengthKC=input(20, title='KC Length', group='Squeeze Momentum', inline='c'),
    multKC=input(1.5, title='KC MultFactor', group='Squeeze Momentum', inline='c'),
    useTrueRange=input(True, title='Use TrueRange (KC)', group='Squeeze Momentum', inline='c'),
    show_sqz=input.bool(defval=False, title='Show squeeze momentum ?', group='Appearance'),
    ema=input.int(200, title='Ema length', minval=1, maxval=500, group='Trend'),
    show_ema=input.bool(defval=True, title='Show Ema ?', group='Appearance'),
    overbought=input.int(70, title='Over bought line rsi', minval=50, maxval=100, group='Rsi', inline='b'),
    oversold=input.int(30, title='Over sold line rsi', minval=0, maxval=50, group='Rsi', inline='b'),
    periods=input.int(5, title='Rsi Length', minval=1, maxval=200, group='Rsi', inline='b'),
    show_rsi=input.bool(defval=False, title='Show Rsi ?', group='Appearance'),
    fast_length=input(title='Fast Length', defval=16, group='Macd'),
    slow_length=input(title='Slow Length', defval=26, group='Macd'),
    src: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=8, group='Macd'),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA'), group='Macd'),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA'), group='Macd'),
    col_macd=input(color.new('#2962FF'), 'MACD Line  ', group='Color Settings', inline='MACD'),
    col_signal=input(color.new('#FF6D00'), 'Signal Line  ', group='Color Settings', inline='Signal'),
    col_grow_above=input(color.new('#26A69A'), 'Above   Grow', group='Histogram', inline='Above'),
    col_fall_above=input(color.new('#B2DFDB'), 'Fall', group='Histogram', inline='Above'),
    col_grow_below=input(color.new('#FFCDD2'), 'Below Grow', group='Histogram', inline='Below'),
    col_fall_below=input(color.new('#FF5252'), 'Fall', group='Histogram', inline='Below'),
    show_macd=input.bool(defval=False, title='Show Macd ?', group='Appearance'),
    source_atr: Series[float] = input(close, title='Source', group='Atr stop loss', inline='A'),
    length_atr=input.int(14, minval=1, title='Period', group='Atr stop loss', inline='A'),
    multiplier: Series[float] = input.float(1.6, minval=0.1, step=0.1, title='Atr multiplier', group='Atr stop loss', inline='A', tooltip='Defines the stop loss distance based in the Atr stop loss indicator'),
    risk=input.float(2.5, '% Account risk per trade for backtesting', step=1, group='Risk management', tooltip='Percentage of total account to risk per trade. >>The price of the stop loss is the red value<<. >>The distance of the stop loss is the orange value<<. It is recommended not to use more than 5%'),
    risk_reward_breakeven=input.float(title='Risk reward for break even', defval=1.0, step=0.1, group='Risk management', tooltip='Risk/reward level to determine the target price to move the stop loss to the buy price (neither win nor lose). >>It is the light blue value<<'),
    leverage=input.bool(defval=False, title='Use leverage ?', group='Risk management', tooltip='If it is activated, there will be no monetary units or amount of assets limit for each operation (That is, each operation will not be affected by the initial / current capital since it would be using leverage). If it is deactivated, the monetary units or the amount of assets to use for each operation will be limited by the initial/current capital.'),
    draw_sl_be=input.bool(defval=True, title='Show stop loss and break even ?', group='Appearance'),
    information=input.bool(defval=True, title='Read ------>', group='Final information', tooltip='Thank you for using this model, I hope it can be very useful for you when making decisions in the short/medium and long term. Remember that it is not a crystal ball and it is not the Holy Grail of investments, it is just a model that seeks to adapt to different market situations to position yourself in favor of having the chances in your favor and making management much easier. Any questions you have about the model, feel free to ask :). Don\'t forget to leave your boost!'),
    againts_trend=input.bool(defval=False, title='Againts trend ?', group='Risk management', tooltip='Activate to trade when the price is below the EMA of 200 periods. It can be useful in certain assets or timeframes like weelky and risky in others'),
    break_even_with_rsi=input.bool(defval=False, title='Break even using rsi ?', group='Risk management', tooltip='Activate to apply break even when rsi crosses under overbought line. It appears as a blue arrow'),
    show_position_on_chart=input.bool(defval=True, title='Draw position on chart ?', group='Appearance', tooltip='Activate to graphically display profit, stop loss and break even'),
    show_signals=input.bool(defval=True, title='Draw signals on chart ?', group='Appearance')
):
    def dateFilter(st: int, et: int):
        return time >= st and time <= et

    dateFilter_1 = dateFilter(initial_date, final_date)
    bgcolor(color.new(color.blue, transp=90) if colorDate and dateFilter_1 else na)
    def inSession(sess):
        return na(time(timeframe.period, sess + ':1234567')) == False

    bgcolor(color.rgb(0, 38, 255, 84) if inSession(timeSession) and colorBG else na)
    source = close
    ma = ta.sma(source, length)
    basis = ma
    dev = mult * ta.stdev(source, length)
    upperBB = basis + dev
    lowerBB = basis - dev
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.sma(range_1, lengthKC)
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC
    sqzOn = lowerBB > lowerKC and upperBB < upperKC
    sqzOff = lowerBB < lowerKC and upperBB > upperKC
    noSqz = sqzOn == False and sqzOff == False
    val: Series = ta.linreg(source - math.avg(math.avg(ta.highest(high, lengthKC), ta.lowest(low, lengthKC)), ta.sma(close, lengthKC)), lengthKC, 0)
    iff_1 = color.new('#00FF00') if val > nz(val[1]) else color.new('#008000')
    iff_2 = color.new('#FF0000') if val < nz(val[1]) else color.new('#800000')
    bcolor = iff_1 if val > 0 else iff_2
    green_sqz = val > 0
    red_sqz = val < 0
    plot(val if show_sqz else na, color=bcolor, style=plot.style_columns, linewidth=4, display=display.all - display.price_scale - display.status_line)
    ema200 = ta.ema(close, ema)
    bullish = close > ema200
    bearish = close < ema200
    plot(ema200 if show_ema else na, color=color.white, linewidth=2, display=display.all - display.status_line)
    rsi_filter = ta.rsi(close, periods)
    plot(rsi_filter if show_rsi else na, color=color.white, linewidth=2, display=display.all - display.price_scale - display.status_line - display.data_window)
    hline(overbought if show_rsi else na, color=color.green, linewidth=1, display=display.all)
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    hist: Series = macd - signal
    plot(hist if show_macd else na, title='Histogram', style=plot.style_columns, color=(col_grow_above if hist[1] < hist else col_fall_above) if hist >= 0 else col_grow_below if hist[1] < hist else col_fall_below, display=display.all - display.price_scale - display.status_line - display.data_window)
    shortStopLoss = source_atr + ta.atr(length_atr) * multiplier
    longStopLoss = source_atr - ta.atr(length_atr) * multiplier
    atr_past_candle_buy = close[1] - inline_series(ta.atr(length_atr), 1) * multiplier[1]
    strategy_contracts = strategy.equity / close
    distance_sl_buy = -1 * (longStopLoss - close) / close
    distance_sl_buy_past_candle = -1 * (atr_past_candle_buy - close) / close
    amount_1 = strategy_contracts * (risk / 100) / distance_sl_buy
    amount_2 = strategy_contracts * (risk / 100) / distance_sl_buy_past_candle
    sl: Persistent[float] = na(float)
    be_buy: Persistent[float] = na(float)
    tp_buy: Persistent[float] = na(float)
    stop_loss_distance: Persistent[float] = na(float)
    buy_amount: Persistent[float] = na(float)
    asset_amount: Persistent[float] = na(float)
    be_buy_calculator: Persistent[float] = na(float)
    stoploss_distance: Persistent[float] = na(float)
    if not leverage and amount_1 > strategy_contracts:
        amount_1 = strategy.equity / close
    if not leverage and amount_2 > strategy_contracts:
        amount_2 = strategy.equity / close
    number_of_contracts = initial_actual_capital_c / close
    buy_amount_atr_actual_candle = close * (number_of_contracts * (risk_c / 100) / distance_sl_buy)
    buy_amount_atr_past_candle = close * (number_of_contracts * (risk_c / 100) / distance_sl_buy_past_candle)
    if close > ema200:
        buy_amount = close * (number_of_contracts * (risk / 100) / distance_sl_buy)
    if close > ema200 and hist > hist[1] and (close > close[1]) and (hist < 0) and red_sqz and (open[1] > ema200):
        buy_amount = close * (number_of_contracts * (risk / 100) / distance_sl_buy_past_candle)
    if close < ema200:
        buy_amount = close * (number_of_contracts * (risk / 100) / distance_sl_buy)
    if not leverage and buy_amount > initial_actual_capital_c:
        buy_amount = initial_actual_capital_c
    plot(buy_amount, display=display.all - display.pane, color=color.rgb(0, 255, 55), title='Amount purchase currency units')
    if close > ema200:
        sl = longStopLoss
    if close > ema200 and hist > hist[1] and (close > close[1]) and (hist < 0) and red_sqz and (open[1] > ema200):
        sl = atr_past_candle_buy
    if close < ema200:
        sl = longStopLoss
    if close > ema200:
        stop_loss_distance = -1 * (longStopLoss - close) / close * 100
    if close > ema200 and hist > hist[1] and (close > close[1]) and (hist < 0) and red_sqz and (open[1] > ema200):
        stop_loss_distance = -1 * (atr_past_candle_buy - close) / close * 100
    if close < ema200:
        stop_loss_distance = -1 * (longStopLoss - close) / close * 100
    plot(stop_loss_distance, title='Stop loss % distance', color=color.rgb(255, 136, 0), display=display.all - display.pane)
    distance_stop_buy_break_even = close - longStopLoss
    distance_stop_buy_break_even_past_candle = close - atr_past_candle_buy
    be_buy_calculator = close + distance_stop_buy_break_even * risk_reward_breakeven
    if close > ema200:
        be_buy_calculator = close + distance_stop_buy_break_even * risk_reward_breakeven
    if close > ema200 and hist > hist[1] and (close > close[1]) and (hist < 0) and red_sqz and (open[1] > ema200):
        be_buy_calculator = close + distance_stop_buy_break_even_past_candle * risk_reward_breakeven
    if close < ema200:
        be_buy_calculator = close + distance_stop_buy_break_even * risk_reward_breakeven
    bought = strategy.position_size > 0
    sold = strategy.position_size < 0
    buy_rsi_signal = ta.crossover(rsi_filter, oversold) and red_sqz and bearish
    buy_macd_signal = hist > hist[1] and close > close[1] and (hist < 0) and red_sqz and (open[1] > ema200)
    sell_rsi_signal = ta.crossunder(rsi_filter, overbought) and green_sqz and bought
    trend_sell_signal_sqz = ta.crossunder(val, 0)
    trend_buy_signal_sqz = ta.crossover(val, 0) or (val > 0 and val > val[1] and (val[1] < val[2]))
    positive_close = strategy.openprofit > 0
    sl_1: Persistent[float] = na(float)
    sl_2: Persistent[float] = na(float)
    sl_3: Persistent[float] = na(float)
    if not bought:
        sl_1 = na
        sl_2 = na
        sl_3 = na
    dateFilter_2 = dateFilter(initial_date, final_date)
    inSession_1 = inSession(timeSession)
    if trend_buy_signal_sqz and dateFilter_2 and inSession_1 and (strategy.opentrades < 1) and againts_trend:
        sl_1 = longStopLoss
        stoploss_distance = close - longStopLoss
        be_buy = close + stoploss_distance * risk_reward_breakeven
        strategy.entry('Buy', strategy.long, qty=amount_1)
        strategy.exit('Cl Buy', 'Buy', stop=sl_1)
    if high > be_buy or (sell_rsi_signal and positive_close and break_even_with_rsi):
        sl_1 = strategy.position_avg_price
        strategy.exit('Cl Buy', 'Buy', stop=sl_1)
    if bought and trend_sell_signal_sqz:
        strategy.close('Buy', comment='Cl Buy')
    dateFilter_3 = dateFilter(initial_date, final_date)
    inSession_2 = inSession(timeSession)
    if trend_buy_signal_sqz and dateFilter_3 and inSession_2 and (strategy.opentrades < 1) and bullish and (not againts_trend):
        sl_2 = longStopLoss
        stoploss_distance = close - longStopLoss
        be_buy = close + stoploss_distance * risk_reward_breakeven
        strategy.entry('Buy', strategy.long, qty=amount_1)
        strategy.exit('Cl Buy', 'Buy', stop=sl_2)
    if high > be_buy or (sell_rsi_signal and positive_close and break_even_with_rsi):
        sl_2 = strategy.position_avg_price
        strategy.exit('Cl Buy', 'Buy', stop=sl_2)
    if trend_sell_signal_sqz:
        strategy.close('Buy', comment='Cl Buy')
    dateFilter_4 = dateFilter(initial_date, final_date)
    inSession_3 = inSession(timeSession)
    if buy_macd_signal and dateFilter_4 and inSession_3 and bullish and (strategy.opentrades < 1):
        sl_3 = atr_past_candle_buy
        stoploss_distance = close - atr_past_candle_buy
        be_buy = close + stoploss_distance * risk_reward_breakeven
        strategy.entry('Buy.', strategy.long, qty=amount_2)
        strategy.exit('Cl Buy.', 'Buy.', stop=sl_3)
    if high > be_buy or (sell_rsi_signal and positive_close and break_even_with_rsi):
        sl_3 = strategy.position_avg_price
        strategy.exit('Cl Buy.', 'Buy.', stop=sl_3)
    if trend_sell_signal_sqz:
        strategy.close('Buy.', comment='Cl Buy.')
    if high > be_buy:
        be_buy = na
    position_price = plot(strategy.position_avg_price if show_position_on_chart else na, style=plot.style_linebr, color=color.new(color.new('#FFFFFF'), 20), linewidth=1, display=display.all - display.status_line)
    break_even_price = plot(be_buy if strategy.position_size > 0 and high < be_buy and show_position_on_chart else na, style=plot.style_linebr, color=color.new(color.new('#41A3FF'), 20), linewidth=1, display=display.all - display.status_line)
    sl1_price = plot(sl_1 if show_position_on_chart and bought and againts_trend else na, style=plot.style_linebr, color=color.new(color.red, 20), linewidth=1, display=display.all - display.status_line)
    sl2_price = plot(sl_2 if show_position_on_chart and bought else na, style=plot.style_linebr, color=color.new(color.red, 20), linewidth=1, display=display.all - display.status_line)
    sl3_price = plot(sl_3 if show_position_on_chart and bought else na, style=plot.style_linebr, color=color.new(color.red, 20), linewidth=1, display=display.all - display.status_line)
    position_profit_price = plot(close if strategy.position_size > 0 and show_position_on_chart and positive_close else na, style=plot.style_linebr, color=color.new(color.green, 20), linewidth=1, display=display.all - display.status_line)
    fill(plot1=position_price, plot2=position_profit_price, color=color.new(color.green, 90))
    fill(plot1=position_price, plot2=sl1_price, color=color.new(color.red, 90))
    fill(plot1=position_price, plot2=sl2_price, color=color.new(color.red, 90))
    fill(plot1=position_price, plot2=sl3_price, color=color.new(color.red, 90))
    plot(sl if draw_sl_be and trend_buy_signal_sqz and (not bought) or (draw_sl_be and buy_macd_signal and (not bought)) else na, title='Stop loss price', color=color.rgb(255, 255, 255), linewidth=1, style=plot.style_circles, display=display.all - display.price_scale)
    plot(be_buy_calculator if draw_sl_be and trend_buy_signal_sqz and (not bought) or (draw_sl_be and buy_macd_signal and (not bought)) else na, title='Target price for break event', color=color.rgb(72, 210, 245), linewidth=1, style=plot.style_circles, display=display.all - display.price_scale)
    plotshape(sell_rsi_signal if show_signals and break_even_with_rsi and bought else False, style=shape.triangledown, color=color.blue, size=size.tiny, display=display.all - display.price_scale - display.status_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
