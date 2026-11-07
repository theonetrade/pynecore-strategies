"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barcolor, barmerge, bgcolor, close, color, display, fill, high, input,
    location, low, math, na, nz, plot, plotshape, request, script, shape, size, strategy, syminfo,
    ta, ticker, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('UT Bot alerts strategy', overlay=True, process_orders_on_close=True, initial_capital=1000000, default_qty_type=strategy.cash, precision=2, calc_on_every_tick=True, commission_value=0.03, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    initial_actual_capital=input.float(defval=10000, title='Enter initial/current capital', group='============ Calculate amount position ============'),
    risk_c=input.float(2.5, '% account risk per trade', step=1, group='============ Calculate amount position ============', tooltip='Percentage of total account to risk per trade. The USD value that should be used to risk the inserted percentage of the account. Appears green in the upper left corner'),
    initial_date=input.time(title='Initial date', defval=timestamp('10 Feb 2014 13:30 +0000'), group='============ Time filter ============ ', tooltip='Enter the start date and time of the strategy'),
    final_date=input.time(title='Final date', defval=timestamp('01 Jan 2030 19:30 +0000'), group='============ Time filter ============ ', tooltip='Enter the end date and time of the strategy'),
    colorDate=input.bool(defval=False, title='Date background', tooltip='Add color to the period of time of the strategy tester'),
    timeSession=input.session(title='Time session', defval='0000-2400', group='============ Time filter ============ ', tooltip='Session time to operate. It may be different depending on your time zone, you have to find the correct hours manually.'),
    colorBG=input.bool(title='Session background', defval=False, tooltip='Add color to session time background'),
    ema=input.int(200, title='Ema length', minval=1, maxval=500, group='============ Trend ============'),
    show_ema=input.bool(defval=False, title='Show ema ?', group='============ Appearance ============'),
    a=input(3, title='Key Vaule', group='============ UT BOT ALERTS ============', tooltip='Higher amount, less trades. Changing this could be useful in some assets or time frames'),
    c=input(1, title='ATR Period', group='============ UT BOT ALERTS ============', tooltip='Higher amount, less trades. Changing this could be useful in some assets or time frames'),
    h=input(False, title='Signals from Heikin Ashi Candles', group='============ UT BOT ALERTS ============'),
    show_atr_ut=input.bool(defval=False, title='Show atr from ut bot alerts ?', group='============ Appearance ============'),
    show_ema_ut=input.bool(defval=False, title='Show ema from ut bot alerts ?', group='============ Appearance ============'),
    show_signals=input.bool(True, title='Show signals ?', group='============ Appearance ============'),
    paint_candles=input.bool(False, title='Paint candles ?', group='============ Appearance ============'),
    source_atr: Series[float] = input(close, title='Source', group='============ Atr stop loss ============', inline='A'),
    length_atr=input.int(14, minval=1, title='Period', group='============ Atr stop loss ============', inline='A'),
    multiplier: Series[float] = input.float(1.5, minval=0.1, step=0.1, title='Atr multiplier', group='============ Atr stop loss ============', inline='A', tooltip='Defines the stop loss distance based on the Atr stop loss indicator'),
    show_stoploss=input.bool(defval=True, title='Show stop loss ?', group='============ Appearance ============'),
    candle_of_stoploss=input.string(defval='Current candle', title='Stop loss source for atr stoploss', group='============ Risk management for trades ============', options=('Current candle', 'Past candle')),
    high_bars=input.int(defval=10, title='Highest price bars: ', group='============ Swing highs/lows stop losses ============'),
    low_bars=input.int(defval=10, title='Lowest price bars: ', group='============ Swing highs/lows stop losses ============'),
    stoploss_type=input.string(defval='Atr stop loss', title='General stop loss source', group='============ Risk management for trades ============', options=('Atr stop loss', 'Swing high/low')),
    risk=input.float(2.5, '% Account risk per trade for backtesting', step=1, group='============ Risk management for trades ============', tooltip='Percentage of total account to risk per trade'),
    leverage=input.bool(defval=True, title='Use leverage for backtesting ?', group='============ Risk management for trades ============', tooltip='If it is activated, there will be no monetary units or amount of assets limit for each operation (That is, each operation will not be affected by the initial / current capital since it would be using leverage). If it is deactivated, the monetary units or the amount of assets to use for each operation will be limited by the initial/current capital.'),
    risk_reward_breakeven_long=input.float(title='Risk/reward for breakeven long', defval=0.75, step=0.1, group='============ Risk management for trades ============'),
    risk_reward_take_profit_long=input.float(title='Risk/reward for take profit long', defval=3.0, step=0.1, group='============ Risk management for trades ============'),
    risk_reward_breakeven_short=input.float(title='Risk/reward for break even short', defval=0.75, step=0.1, group='============ Risk management for trades ============'),
    risk_reward_take_profit_short=input.float(title='Risk/reward for take profit short', defval=3.0, step=0.1, group='============ Risk management for trades ============'),
    tp_percent=input.float(title='% of trade for first take profit', defval=50, step=5, group='============ Risk management for trades ============', tooltip='Closing percentage of the current position when the first take profit is reached.'),
    long_positions=input.bool(defval=True, title='Long positions ?', group='============ Positions management ============'),
    short_positions=input.bool(defval=True, title='Short positions ?', group='============ Positions management ============'),
    use_takeprofit=input.bool(defval=True, title='Use take profit ?', group='============ Risk management for trades ============'),
    show_position_on_chart=input.bool(defval=True, title='Draw position on chart ?', group='============ Appearance ============', tooltip='Activate to graphically display profit, stop loss and break even'),
    show_break_even_on_chart=input.bool(defval=True, title='Draw first take profit/breakeven price on chart ?', group='============ Appearance ============', tooltip='Activate to display take profit and breakeven price. It appears as a green point in the chart'),
    leverage_for_calculator=input.bool(defval=True, title='Use leverage ?', group='============ Calculate amount position ============', tooltip='If it is activated, there will be no monetary units or amount of assets limit for each operation (That is, each operation will not be affected by the initial / current capital since it would be using leverage). If it is deactivated, the monetary units or the amount of assets to use for each operation will be limited by the initial/current capital.')
):
    def dateFilter(st: int, et: int):
        return time >= st and time <= et

    dateFilter_1 = dateFilter(initial_date, final_date)
    bgcolor(color.new(color.blue, transp=90) if colorDate and dateFilter_1 else na)
    def inSession(sess):
        return na(time(timeframe.period, sess + ':1234567')) == False

    bgcolor(color.rgb(0, 38, 255, 84) if inSession(timeSession) and colorBG else na)
    ema200 = ta.ema(close, ema)
    bullish = close > ema200
    bearish = close < ema200
    plot(ema200 if show_ema else na, title='Ema', color=color.white, linewidth=2, display=display.all - display.status_line - display.price_scale)
    xATR = ta.atr(c)
    nLoss = a * xATR
    src: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close, lookahead=barmerge.lookahead_off) if h else close
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = src - nLoss if src > nz(xATRTrailingStop[1], 0) else src + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), src + nLoss) if src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), src - nLoss) if src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0) else iff_2
    plot(xATRTrailingStop if show_atr_ut else na, color=color.orange, linewidth=2, display=display.all - display.price_scale - display.status_line)
    pos: Series[int] = 0
    iff_3 = -1 if src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0) else iff_3
    xcolor = color.red if pos == -1 else color.green if pos == 1 else color.blue
    ema_ut = ta.ema(src, 1)
    plot(ema_ut if show_ema_ut else na, color=color.white, linewidth=2, display=display.all - display.price_scale - display.status_line)
    above = ta.crossover(ema_ut, xATRTrailingStop)
    below = ta.crossover(xATRTrailingStop, ema_ut)
    buy = src > xATRTrailingStop and above
    sell = src < xATRTrailingStop and below
    close_buy = src < xATRTrailingStop and below
    close_sell = src > xATRTrailingStop and above
    barbuy = src > xATRTrailingStop
    barsell = src < xATRTrailingStop
    plotshape(buy if bullish and show_signals else False, title='Buy', text='Buy', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all - display.price_scale - display.status_line)
    plotshape(sell if bearish and show_signals else False, title='Sell', text='Sell', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all - display.price_scale - display.status_line)
    plotshape(close_buy if bullish and show_signals else False, title='Close Buy', text='Cl Buy', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 80), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all - display.price_scale - display.status_line)
    plotshape(close_sell if bearish and show_signals else False, title='Close Sell', text='Cl Sell', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 80), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all - display.price_scale - display.status_line)
    barcolor(color.green if barbuy and paint_candles else na)
    barcolor(color.red if barsell and paint_candles else na)
    long_condition_atr = src > xATRTrailingStop and above
    short_condition_atr = src < xATRTrailingStop and below
    shortStopLoss: Persistent[float] = na(float)
    longStopLoss: Persistent[float] = na(float)
    atr_past_candle_long: Persistent[float] = na(float)
    atr_past_candle_short: Persistent[float] = na(float)
    if candle_of_stoploss == 'Current candle':
        shortStopLoss = source_atr + ta.atr(length_atr) * multiplier
        longStopLoss = source_atr - ta.atr(length_atr) * multiplier
    if candle_of_stoploss == 'Past candle':
        shortStopLoss = close[1] + inline_series(ta.atr(length_atr), 1) * multiplier[1]
        longStopLoss = close[1] - inline_series(ta.atr(length_atr), 1) * multiplier[1]
    stop_high = ta.highest(high, high_bars)
    stop_low = ta.lowest(low, low_bars)
    if stoploss_type == 'Atr stop loss':
        shortStopLoss = source_atr + ta.atr(length_atr) * multiplier
        longStopLoss = source_atr - ta.atr(length_atr) * multiplier
    if candle_of_stoploss == 'Past candle' and stoploss_type == 'Atr stop loss':
        shortStopLoss = close[1] + inline_series(ta.atr(length_atr), 1) * multiplier[1]
        longStopLoss = close[1] - inline_series(ta.atr(length_atr), 1) * multiplier[1]
    if stoploss_type == 'Swing high/low':
        shortStopLoss = stop_high
        longStopLoss = stop_low
    plot(longStopLoss if show_stoploss and long_condition_atr and bullish else na, color=color.white, style=plot.style_circles, linewidth=2)
    plot(shortStopLoss if show_stoploss and short_condition_atr and bearish else na, color=color.white, style=plot.style_circles, linewidth=2)
    strategy_contracts = strategy.equity / close
    distance_sl_atr_long = -1 * (longStopLoss - close) / close
    distance_sl_atr_short = (shortStopLoss - close) / close
    long_amount = strategy_contracts * (risk / 100) / distance_sl_atr_long
    short_amount = strategy_contracts * (risk / 100) / distance_sl_atr_short
    if not leverage and long_amount > strategy_contracts:
        long_amount = strategy.equity / close
    if not leverage and short_amount > strategy_contracts:
        short_amount = strategy.equity / close
    bullish = close > ema200
    bearish = close < ema200
    bought = strategy.position_size > 0
    sold = strategy.position_size < 0
    buy = src > xATRTrailingStop and above
    sell = src < xATRTrailingStop and below
    sl_long: Persistent[float] = na(float)
    sl_short: Persistent[float] = na(float)
    be_long: Persistent[float] = na(float)
    be_short: Persistent[float] = na(float)
    tp_long: Persistent[float] = na(float)
    tp_short: Persistent[float] = na(float)
    if not bought:
        be_long = na
        sl_long = na
        tp_long = na
    if not sold:
        be_short = na
        sl_short = na
        tp_short = na
    dateFilter_2 = dateFilter(initial_date, final_date)
    inSession_1 = inSession(timeSession)
    if not bought and buy and dateFilter_2 and long_positions and bullish and inSession_1 and use_takeprofit:
        sl_long = longStopLoss
        long_stoploss_distance__0000008c__ = close - longStopLoss
        be_long = close + long_stoploss_distance__0000008c__ * risk_reward_breakeven_long
        tp_long = close + long_stoploss_distance__0000008c__ * risk_reward_take_profit_long
        strategy.entry('L', strategy.long, long_amount, alert_message='Long')
        strategy.exit('Tp', 'L', stop=sl_long, limit=tp_long, qty_percent=tp_percent)
        strategy.exit('Exit', 'L', stop=sl_long)
    if bought and high > be_long:
        sl_long = strategy.position_avg_price
        strategy.exit('Tp', 'L', stop=sl_long, limit=tp_long, qty_percent=tp_percent)
        strategy.exit('Exit', 'L', stop=sl_long)
    if bought and sell and (strategy.openprofit > 0):
        strategy.close('L', comment='CL')
    dateFilter_3 = dateFilter(initial_date, final_date)
    inSession_2 = inSession(timeSession)
    if not bought and buy and dateFilter_3 and long_positions and bullish and inSession_2:
        sl_long = longStopLoss
        long_stoploss_distance__00000097__ = close - longStopLoss
        be_long = close + long_stoploss_distance__00000097__ * risk_reward_breakeven_long
        strategy.entry('L', strategy.long, long_amount, alert_message='Long')
        strategy.exit('Tp', 'L', stop=sl_long, qty_percent=tp_percent)
        strategy.exit('Exit', 'L', stop=sl_long)
    if bought and high > be_long:
        sl_long = strategy.position_avg_price
        strategy.exit('Tp', 'L', stop=sl_long, qty_percent=tp_percent)
        strategy.exit('Exit', 'L', stop=sl_long)
    if bought and sell and (strategy.openprofit > 0):
        strategy.close('L', comment='CL')
    dateFilter_4 = dateFilter(initial_date, final_date)
    inSession_3 = inSession(timeSession)
    if not sold and sell and dateFilter_4 and short_positions and bearish and inSession_3 and use_takeprofit:
        sl_short = shortStopLoss
        short_stoploss_distance__000000a2__ = shortStopLoss - close
        be_short = (short_stoploss_distance__000000a2__ * risk_reward_breakeven_short - close) * -1
        tp_short = (short_stoploss_distance__000000a2__ * risk_reward_take_profit_short - close) * -1
        strategy.entry('S', strategy.short, short_amount, alert_message='Short')
        strategy.exit('Tp', 'S', stop=sl_short, limit=tp_short, qty_percent=tp_percent)
        strategy.exit('Exit', 'S', stop=sl_short)
    if sold and low < be_short:
        sl_short = strategy.position_avg_price
        strategy.exit('Tp', 'S', stop=sl_short, limit=tp_short, qty_percent=tp_percent)
        strategy.exit('Exit', 'S', stop=sl_short)
    if sold and buy and (strategy.openprofit > 0):
        strategy.close('S', comment='CS')
    dateFilter_5 = dateFilter(initial_date, final_date)
    inSession_4 = inSession(timeSession)
    if not sold and sell and dateFilter_5 and short_positions and bearish and inSession_4:
        sl_short = shortStopLoss
        short_stoploss_distance__000000ad__ = shortStopLoss - close
        be_short = (short_stoploss_distance__000000ad__ * risk_reward_breakeven_short - close) * -1
        strategy.entry('S', strategy.short, short_amount, alert_message='Short')
        strategy.exit('Tp', 'S', stop=sl_short, qty_percent=tp_percent)
        strategy.exit('Exit', 'S', stop=sl_short)
    if sold and low < be_short:
        sl_short = strategy.position_avg_price
        strategy.exit('Tp', 'S', stop=sl_short, qty_percent=tp_percent)
        strategy.exit('Exit', 'S', stop=sl_short)
    if sold and buy and (strategy.openprofit > 0):
        strategy.close('S', comment='CS')
    if high > tp_long:
        tp_long = na
    if low < tp_short:
        tp_short = na
    if high > be_long:
        be_long = na
    if low < be_short:
        be_short = na
    position_price = plot(strategy.position_avg_price if show_position_on_chart else na, style=plot.style_linebr, color=color.new(color.new('#FFFFFF'), 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    sl_long_price = plot(sl_long if show_position_on_chart and bought else na, style=plot.style_linebr, color=color.new(color.red, 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    sl_short_price = plot(sl_short if show_position_on_chart and sold else na, style=plot.style_linebr, color=color.new(color.red, 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    tp_long_price = plot(tp_long if strategy.position_size > 0 and show_position_on_chart and use_takeprofit else na, style=plot.style_linebr, color=color.new(color.new('#4CD350'), 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    tp_short_price = plot(tp_short if strategy.position_size < 0 and show_position_on_chart and use_takeprofit else na, style=plot.style_linebr, color=color.new(color.new('#4CD350'), 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    breakeven_long = plot(be_long if strategy.position_size > 0 and high < be_long and show_position_on_chart else na, style=plot.style_linebr, color=color.new(color.new('#1FC9FD'), 60), linewidth=1, display=display.all - display.status_line - display.price_scale)
    breakeven_short = plot(be_short if strategy.position_size < 0 and low > be_short and show_position_on_chart else na, style=plot.style_linebr, color=color.new(color.new('#1FC9FD'), 60), linewidth=1, display=display.all - display.status_line - display.price_scale)
    long_stoploss_distance = close - longStopLoss
    short_stoploss_distance = shortStopLoss - close
    be_long_plot = close + long_stoploss_distance * risk_reward_breakeven_long
    be_short_plot = (short_stoploss_distance * risk_reward_breakeven_short - close) * -1
    plot(be_long_plot if show_break_even_on_chart and buy and bullish else na, color=color.new(color.new('#1FC9FD'), 10), style=plot.style_circles, linewidth=2, display=display.all - display.price_scale)
    plot(be_short_plot if show_break_even_on_chart and sell and bearish else na, color=color.new(color.new('#1FC9FD'), 10), style=plot.style_circles, linewidth=2, display=display.all - display.price_scale)
    position_profit_long = plot(close if bought and show_position_on_chart and (strategy.openprofit > 0) else na, style=plot.style_linebr, color=color.new(color.new('#4CD350'), 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    position_profit_short = plot(close if sold and show_position_on_chart and (strategy.openprofit > 0) else na, style=plot.style_linebr, color=color.new(color.new('#4CD350'), 10), linewidth=1, display=display.all - display.status_line - display.price_scale)
    fill(plot1=position_price, plot2=position_profit_long, color=color.new(color.new('#4CD350'), 90))
    fill(plot1=position_price, plot2=position_profit_short, color=color.new(color.new('#4CD350'), 90))
    fill(plot1=position_price, plot2=sl_long_price, color=color.new(color.red, 90))
    fill(plot1=position_price, plot2=sl_short_price, color=color.new(color.red, 90))
    fill(plot1=position_price, plot2=tp_long_price, color=color.new(color.green, 90))
    fill(plot1=position_price, plot2=tp_short_price, color=color.new(color.green, 90))
    contracts_amount_c = initial_actual_capital / close
    distance_sl_long_c = -1 * (longStopLoss - close) / close
    distance_sl_short_c = (shortStopLoss - close) / close
    long_amount_c = close * (contracts_amount_c * (risk_c / 100) / distance_sl_long_c)
    short_amount_c = close * (contracts_amount_c * (risk_c / 100) / distance_sl_short_c)
    long_amount_lev = close * (contracts_amount_c * (risk_c / 100) / distance_sl_long_c)
    short_amount_lev = close * (contracts_amount_c * (risk_c / 100) / distance_sl_short_c)
    if not leverage_for_calculator and long_amount_lev > initial_actual_capital:
        long_amount_lev = initial_actual_capital
    if not leverage_for_calculator and short_amount_lev > initial_actual_capital:
        short_amount_lev = initial_actual_capital
    plot(long_amount_c if buy and leverage_for_calculator else na, color=color.rgb(136, 255, 0), display=display.all - display.pane - display.price_scale)
    plot(short_amount_c if sell and leverage_for_calculator else na, color=color.rgb(136, 255, 0), display=display.all - display.pane - display.price_scale)
    plot(long_amount_lev if buy and (not leverage_for_calculator) else na, color=color.rgb(136, 255, 0), display=display.all - display.pane - display.price_scale)
    plot(short_amount_lev if sell and (not leverage_for_calculator) else na, color=color.rgb(136, 255, 0), display=display.all - display.pane - display.price_scale)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)