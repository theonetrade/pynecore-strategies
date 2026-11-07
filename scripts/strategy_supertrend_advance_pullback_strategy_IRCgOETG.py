"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, display, fill, high, hlc3, input, low, math, na, nz, open,
    plot, script, strategy, ta, time, timestamp
)
from pynecore.types import NA, Persistent, Series

group_text0: str = 'Supertrend Settings'
group_text0000: str = 'Ema Settings'
group_text00: str = 'Rsi Settings'
group_text1: str = 'Backtest Period'
group_text2: str = 'Trade Direction'
group_text3: str = 'Quantity Settings'
group_text5: str = 'Enable/Disable Condition Filter'
group_macd: str = 'Macd Set'
group_cci: str = 'Cci Set'
group_text6: str = 'Choose Sl/Tp'
group_text7: str = 'Percentage Sl/Tp'
group_text9: str = 'Atr SL/Tp'
group_text8: str = 'Swing Hl & Supertrend Sl/Tp'


@script.strategy('Supertrend advance', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=1, process_orders_on_close=False, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True, na_bool=True)
def main(
    on_ma=input.bool(True, 'Ema Condition On/Off', group=group_text5, inline='CL'),
    en_rsi=input.bool(True, 'Rsi Condition On/Off', group=group_text5, inline='CL'),
    en_macd=input.bool(True, title='Enable Macd Condition', group=group_text5, inline='CS'),
    en_cci=input.bool(True, title='Enable/Disable CCi Filter', group=group_text5, inline='CS'),
    option_ch=input.string('Pullback', title='Type Of Stratgey', options=('Pullback', 'Simple'), group='Choose Strategy Type'),
    option_ts=input.string('Percentage', 'Chosse Type Of Sl/tp', options=('Percentage', 'Supertrend', 'Swinghl', 'Atr'), group=group_text6),
    atrPeriod=input(10, 'ATR Length', group=group_text0),
    factor=input.float(3.0, 'Factor', step=0.01, group=group_text0),
    ma_len=input.int(200, minval=1, title='Ema Length', group=group_text0000),
    ma_src: Series[float] = input.source(close, title='Ema Source', group=group_text0000),
    rsiSource: Series[float] = input(title='RSI Source', defval=close, group=group_text00),
    rsiLength=input(title='RSI Length', defval=14, group=group_text00),
    rsiOverbought=input(title='RSI BUY Level', defval=50, group=group_text00),
    rsiOversold=input(title='RSI SELL Level', defval=50, group=group_text00),
    fast_length=input(title='Fast Length', defval=12, group=group_macd),
    slow_length=input(title='Slow Length', defval=26, group=group_macd),
    macd_src: Series[float] = input(title='Source', defval=close, group=group_macd),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group=group_macd),
    length_cci=input.int(20, minval=1, group=group_cci),
    src_cci: Series[float] = input(hlc3, title='Source', group=group_cci),
    cci_gr=input.int(200, title='CCi > Input', group=group_cci, tooltip='CCi iS Greater thn 100 buy'),
    cci_ls=input.int(-200, title='CCi < -Input', group=group_cci, tooltip='CCi iS Less thn -100 Sell'),
    start=input.time(timestamp('2005-01-01'), title='Start calculations from', group=group_text1),
    end=input.time(timestamp('2045-03-01'), title='End calculations', group=group_text1),
    tradeDirection=input.string(title='Trade Direction', options=('Long', 'Short', 'Both'), defval='Both', group=group_text2),
    qty_new=input.float(1.0, step=0.1, title='Quantity', group=group_text3),
    tpnewf=input.float(title='take profit swinghl||supertrend ', step=0.1, defval=1.5, group=group_text8),
    hiLen=input.int(title='Highest High Lookback', defval=6, minval=2, group=group_text8),
    loLen=input.int(title='Lowest Low Lookback', defval=6, minval=2, group=group_text8),
    enable_trail=input.bool(False, 'Enable Trail', group=group_text7),
    __input_30__=input.float(1.0, step=0.1, title='Stop Loss %', group=group_text7),
    __input_31__=input.float(2.0, step=0.1, title='Take Profit %', group=group_text7),
    __input_32__=input.float(title='Trailing Stop (%)', minval=0.0, step=0.1, defval=1, group=group_text7),
    enable_atrtrail=input.bool(False, 'Enable Atr Trail', group=group_text9),
    atrLength=input(title='ATR Length', defval=14, group=group_text9),
    slATRMult=input.float(title='Stop loss ATR multiplier', step=0.1, defval=2.0, group=group_text9),
    tpATRMult=input.float(title='Take profit multiplier', step=0.1, defval=1.5, group=group_text9),
    lookback=input.int(title='How Far To Look Back For High/Lows', defval=7, minval=1, group=group_text9)
):
    group_text000: Persistent[str] = 'Choose Strategy'
    group_text4: Persistent[str] = 'Sl/Tp Settings'
    supertrend, direction = ta.supertrend(factor, atrPeriod)
    bodyMiddle = plot((open + close) / 2, display=display.none)
    upTrend = plot(supertrend if direction < 0 else na, 'Up Trend', color=color.green, style=plot.style_linebr)
    downTrend = plot(na if direction < 0 else supertrend, 'Down Trend', color=color.red, style=plot.style_linebr)
    fill(bodyMiddle, upTrend, color.new(color.green, 90), fillgaps=False)
    fill(bodyMiddle, downTrend, color.new(color.red, 90), fillgaps=False)
    long = supertrend if direction < 0 else na
    short = na if direction < 0 else supertrend
    longpos: Series[bool] = False
    shortpos: Series[bool] = False
    longpos = True if cast_bool(long) else False if cast_bool(short) else longpos[1]
    shortpos = True if cast_bool(short) else False if cast_bool(long) else shortpos[1]
    fin_pullbuy = ta.crossunder(low[1], long) and cast_bool(long) and (high > high[1])
    fin_pullsell = ta.crossover(high[1], short) and cast_bool(short) and (low < low[1])
    ma_out = ta.ema(ma_src, ma_len)
    ma_buy = (True if close > ma_out else False) if on_ma else True
    ma_sell = (True if close < ma_out else False) if on_ma else True
    rsiValue = ta.rsi(rsiSource, rsiLength)
    rsi_buy = (True if rsiValue >= rsiOverbought else False) if en_rsi else True
    rsi_sell = (True if rsiValue <= rsiOversold else False) if en_rsi else True
    macdLine, signalLine, histLine = ta.macd(macd_src, fast_length, slow_length, signal_length)
    buy_macd = (True if macdLine > 0 else False) if en_macd else True
    sell_macd = (True if macdLine < 0 else False) if en_macd else True
    ma = ta.sma(src_cci, length_cci)
    cci = (src_cci - ma) / (0.015 * ta.dev(src_cci, length_cci))
    buy_cci = (True if cci > cci_gr else False) if en_cci else True
    sell_cci = (True if cci < cci_ls else False) if en_cci else True
    buy_cond = cast_bool(long) and (not longpos[1]) and rsi_buy and ma_buy and buy_macd and buy_cci if option_ch == 'Simple' else fin_pullbuy and rsi_buy and ma_buy and buy_macd and buy_cci if option_ch == 'Pullback' else False
    sell_cond = cast_bool(short) and (not shortpos[1]) and rsi_sell and ma_sell and sell_macd and sell_cci if option_ch == 'Simple' else fin_pullsell and rsi_sell and ma_sell and sell_macd and sell_cci if option_ch == 'Pullback' else False
    time_cond = time >= start and time <= end
    longOK = tradeDirection == 'Long' or tradeDirection == 'Both'
    shortOK = tradeDirection == 'Short' or tradeDirection == 'Both'
    globl = nz(ta.lowest(low, loLen), low[1]) if option_ts == 'Swinghl' else nz(supertrend, low[1]) if option_ts == 'Supertrend' else na
    globl2 = nz(ta.highest(high, hiLen), high[1]) if option_ts == 'Swinghl' else nz(supertrend, high[1]) if option_ts == 'Supertrend' else na
    store: Persistent = NA(float)
    store2: Persistent = NA(float)
    if buy_cond and longOK and time_cond and (strategy.position_size == 0):
        strategy.entry('enter long', direction=strategy.long, qty=qty_new)
        store = globl
    if sell_cond and shortOK and time_cond and (strategy.position_size == 0):
        strategy.entry('enter short', direction=strategy.short, qty=qty_new)
        store2 = globl2
    stopPer = __input_30__ * 0.01
    takePer = __input_31__ * 0.01
    trailStop = __input_32__ * 0.01
    longStopPrice: Series[float] = 0.0
    shortStopPrice: Series[float] = 0.0
    __block_result__ = na
    if strategy.position_size > 0:
        stopValue = close * (1 - trailStop)
        __block_result__ = math.max(stopValue, longStopPrice[1])
    else:
        __block_result__ = 0
    longStopPrice = __block_result__
    __block_result_1__ = na
    if strategy.position_size < 0:
        stopValue = close * (1 + trailStop)
        __block_result_1__ = math.min(stopValue, shortStopPrice[1])
    else:
        __block_result_1__ = 999999
    shortStopPrice = __block_result_1__
    longStop: float = 0.0
    shortStop: float = 0.0
    shortTake: float = 0.0
    longTake: float = 0.0
    if option_ts == 'Percentage':
        longStop = strategy.position_avg_price * (1 - stopPer)
        shortStop = strategy.position_avg_price * (1 + stopPer)
        shortTake = strategy.position_avg_price * (1 - takePer)
        longTake = strategy.position_avg_price * (1 + takePer)
    if enable_trail and option_ts == 'Percentage':
        longStop = longStopPrice
        shortStop = shortStopPrice
    if strategy.position_size > 0 and option_ts == 'Percentage':
        strategy.exit(id='Close Long', from_entry='enter long', stop=longStop, limit=longTake)
    if strategy.position_size < 0 and option_ts == 'Percentage':
        strategy.exit(id='Close Short', from_entry='enter short', stop=shortStop, limit=shortTake)
    plot(longStop if strategy.position_size > 0 and option_ts == 'Percentage' else na, style=plot.style_linebr, color=na if enable_trail else color.new(color.new('#C0FF52'), 0), linewidth=1, title='Long Fixed SL')
    plot(shortStop if strategy.position_size < 0 and option_ts == 'Percentage' else na, style=plot.style_linebr, color=na if enable_trail else color.new(color.new('#5269FF'), 0), linewidth=1, title='Short Fixed SL')
    plot(longTake if strategy.position_size > 0 and option_ts == 'Percentage' else na, style=plot.style_linebr, color=color.new(color.new('#5E6192'), 0), linewidth=1, title='Long Take Profit')
    plot(shortTake if strategy.position_size < 0 and option_ts == 'Percentage' else na, style=plot.style_linebr, color=color.new(color.new('#DCB53D'), 0), linewidth=1, title='Short Take Profit')
    plot(series=longStopPrice if strategy.position_size > 0 and option_ts == 'Percentage' and enable_trail else na, color=color.new(color.red, 0), style=plot.style_linebr, linewidth=1, title='Long Trail Stop', offset=1)
    plot(series=shortStopPrice if strategy.position_size < 0 and option_ts == 'Percentage' and enable_trail else na, color=color.new(color.red, 0), style=plot.style_linebr, linewidth=1, title='Short Trail Stop', offset=1)
    takeProfit_buy = strategy.position_avg_price - (store - strategy.position_avg_price) * tpnewf
    takeProfit_sell = strategy.position_avg_price - (store2 - strategy.position_avg_price) * tpnewf
    if strategy.position_size >= 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend'):
        strategy.exit(id='XL HH', from_entry='enter long', stop=store, limit=takeProfit_buy, comment='Long Exit')
    if strategy.position_size <= 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend'):
        strategy.exit(id='XS LL', from_entry='enter short', stop=store2, limit=takeProfit_sell, comment='Short Exit')
    plot(series=takeProfit_sell if strategy.position_size < 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend') else na, style=plot.style_circles, color=color.orange, linewidth=1, title='take profit sell')
    plot(series=takeProfit_buy if strategy.position_size > 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend') else na, style=plot.style_circles, color=color.blue, linewidth=1, title='take profit buy')
    plot(series=store if strategy.position_size > 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend') else na, style=plot.style_circles, color=color.new(color.green, 0), linewidth=1, title='Lowest Low Stop')
    plot(series=store2 if strategy.position_size < 0 and (option_ts == 'Swinghl' or option_ts == 'Supertrend') else na, style=plot.style_circles, color=color.new(color.red, 0), linewidth=1, title='Highest High Stop')
    atr: Series = ta.atr(atrLength)
    lowestLow = ta.lowest(low, lookback)
    highestHigh = ta.highest(high, lookback)
    longStopa = (lowestLow if enable_atrtrail else close) - atr * slATRMult
    shortStopa = (highestHigh if enable_atrtrail else close) + atr * slATRMult
    atr_l: float = 0.0
    atr_s: float = 0.0
    atr_l = nz(strategy.position_avg_price - atr[1] * slATRMult, strategy.position_avg_price - 1 * slATRMult)
    atr_s = nz(strategy.position_avg_price + atr[1] * slATRMult, strategy.position_avg_price - 1 * slATRMult)
    stoploss_l = ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0, atr_l, 0)
    stoploss_s = ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0, atr_s, 0)
    takeprofit_l = strategy.position_avg_price - (stoploss_l - strategy.position_avg_price) * tpATRMult
    takeprofit_s = strategy.position_avg_price - (stoploss_s - strategy.position_avg_price) * tpATRMult
    if strategy.position_size > 0 and option_ts == 'Atr':
        strategy.exit(id='Xl', stop=longStopa if enable_atrtrail else stoploss_l, limit=takeprofit_l, comment='Long Exit')
    if strategy.position_size < 0 and option_ts == 'Atr':
        strategy.exit(id='XH', stop=shortStopa if enable_atrtrail else stoploss_s, limit=takeprofit_s, comment='Short Exit')
    plot(series=takeprofit_l if strategy.position_size > 0 and option_ts == 'Atr' else na, style=plot.style_circles, color=color.orange, linewidth=1, title='take profit sell')
    plot(series=takeprofit_s if strategy.position_size < 0 and option_ts == 'Atr' else na, style=plot.style_circles, color=color.blue, linewidth=1, title='take profit buy')
    plot(series=stoploss_l if strategy.position_size > 0 and option_ts == 'Atr' and (not enable_atrtrail) else na, style=plot.style_circles, color=color.new(color.green, 0), linewidth=1, title='Lowest Low Stop')
    plot(series=stoploss_s if strategy.position_size < 0 and option_ts == 'Atr' and (not enable_atrtrail) else na, style=plot.style_circles, color=color.new(color.red, 0), linewidth=1, title='Highest High Stop')
    plot(series=longStopa if strategy.position_size > 0 and option_ts == 'Atr' and enable_atrtrail else na, color=color.new(color.green, 0), style=plot.style_linebr, linewidth=1, title='Long Trail Stop', offset=1)
    plot(series=shortStopa if strategy.position_size < 0 and option_ts == 'Atr' and enable_atrtrail else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='short Trail Stop', offset=1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)