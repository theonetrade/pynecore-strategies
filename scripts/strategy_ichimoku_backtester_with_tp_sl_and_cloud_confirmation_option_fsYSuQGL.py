"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, currency, fill, input, math, na, plot, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Ichimoku Backtester with Optional RSI, TP, and SL', overlay=True, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=95, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    ts_bars=input.int(9, minval=1, title='Tenkan-Sen Bars', group='Ichimoku Cloud'),
    ks_bars=input.int(26, minval=1, title='Kijun-Sen Bars', group='Ichimoku Cloud'),
    ssb_bars=input.int(52, minval=1, title='Senkou-Span B Bars', group='Ichimoku Cloud'),
    cs_offset=input.int(26, minval=1, title='Chikou-Span Offset', group='Ichimoku Cloud'),
    ss_offset=input.int(26, minval=1, title='Senkou-Span Offset', group='Ichimoku Cloud'),
    trade_long=input.bool(True, title='Long Entry', group='Ichimoku Cloud'),
    trade_short=input.bool(True, title='Short Entry', group='Ichimoku Cloud'),
    use_short_stop_loss=input.bool(False, title='Short Stop Loss', group='Stop Loss and Take Profit', inline='Short_SL'),
    __input_8__=input.float(title='(%)', minval=0.0, step=0.1, defval=5, group='Stop Loss and Take Profit', inline='Short_SL'),
    use_long_stop_loss=input.bool(False, title='Long Stop Loss', group='Stop Loss and Take Profit', inline='Long_SL'),
    __input_10__=input.float(title='(%)', minval=0.0, step=0.1, defval=5, group='Stop Loss and Take Profit', inline='Long_SL'),
    use_short_take_profit=input.bool(False, title='Short Take Profit', group='Stop Loss and Take Profit', inline='Short_TP'),
    __input_12__=input.float(title='(%)', minval=0.0, step=0.1, defval=20, group='Stop Loss and Take Profit', inline='Short_TP'),
    use_long_take_profit=input.bool(False, title='Long Take Profit', group='Stop Loss and Take Profit', inline='Long_TP'),
    __input_14__=input.float(title='(%)', minval=0.0, step=0.1, defval=20, group='Stop Loss and Take Profit', inline='Long_TP'),
    use_rsi_entry=input.bool(False, title='Use for Entry', group='RSI'),
    use_rsi_tp=input.bool(False, title='Use for Take Profit', group='RSI'),
    rsi_period=input.int(defval=7, title='RSI Period', group='RSI'),
    overbought_rsi=input.float(defval=80, title='Overbought Level', group='RSI'),
    oversold_rsi=input.float(defval=20, title='Oversold Level', group='RSI'),
    showDate=input.bool(defval=False, title='Show Date Range', group='Date Range'),
    start=input.time(defval=timestamp('01 Jan 2019 00:00 +0000'), title='Start', group='Date Range', inline='Start Date'),
    finish=input.time(defval=timestamp('31 Dec 2021 23:59 +0000'), title='End', group='Date Range', inline='End Date')
):
    short_stop_loss = __input_8__ * 0.01
    long_stop_loss = __input_10__ * 0.01
    short_take_profit = __input_12__ * 0.01
    long_take_profit = __input_14__ * 0.01
    seq_rsi: int = 1
    toggle_stoch_rsi: bool = False
    def window():
        return True if time >= start and time <= finish else False

    def middle(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    tenkan = middle(ts_bars)
    kijun = middle(ks_bars)
    senkouA: Series = math.avg(tenkan, kijun)
    senkouB: Series = middle(ssb_bars)
    chikou = close[cs_offset]
    window_1 = window()
    bgcolor(color=color.gray if showDate and window_1 else na)
    plot(tenkan, color=color.new(color.new('#0496FF'), 0), title='Tenkan-Sen')
    plot(kijun, color=color.new(color.new('#991515'), 0), title='Kijun-Sen')
    plot(chikou, color=color.new(color.new('#CAEB36'), 0), title='Chikou-Span')
    sa = plot(senkouA, offset=ss_offset, color=color.new(color.green, 0), title='Senkou-Span A')
    sb = plot(senkouB, offset=ss_offset, color=color.new(color.red, 0), title='Senkou-Span B')
    fill(sa, sb, color=color.green if senkouA > senkouB else color.red, title='Cloud color')
    ss_high = math.max(senkouA[ss_offset], senkouB[ss_offset])
    ss_low = math.min(senkouA[ss_offset], senkouB[ss_offset])
    tk_cross_bull = ta.crossover(tenkan, kijun)
    tk_cross_bear = ta.crossunder(tenkan, kijun)
    cs_cross_bull = ta.mom(close, cs_offset) > 0
    cs_cross_bear = ta.mom(close, cs_offset) < 0
    price_above_kumo = close > ss_high
    price_below_kumo = close < ss_low
    senkou_green = True if senkouA > senkouB else False
    rsi1 = ta.rsi(close, rsi_period)
    rsi_value = ta.stoch(rsi1, rsi1, rsi1, rsi_period) if toggle_stoch_rsi else rsi1
    in_long: Series[bool] = False
    in_long = in_long[1]
    in_short: Series[bool] = False
    in_short = in_short[1]
    long_entry = tk_cross_bull and cs_cross_bull and price_above_kumo and senkou_green and (not in_long)
    short_entry = tk_cross_bear and cs_cross_bear and price_below_kumo and (not senkou_green) and (not in_short)
    long_exit = short_entry and in_long
    short_exit = long_entry and in_short
    overbought = ta.crossover(rsi_value, overbought_rsi)
    oversold = ta.crossunder(rsi_value, oversold_rsi)
    underbought = rsi_value < overbought_rsi
    undersold = rsi_value > oversold_rsi
    if use_rsi_entry:
        long_entry = long_entry and underbought
        short_entry = short_entry and undersold
    if use_rsi_tp:
        long_exit = overbought and in_long
        short_exit = oversold and in_short
    if long_entry:
        in_long = True
        in_short = False
    if long_exit:
        in_long = False
    if short_entry:
        in_short = True
        in_long = False
    if short_exit:
        in_short = False
    longStopPrice = strategy.position_avg_price * (1 - long_stop_loss)
    shortStopPrice = strategy.position_avg_price * (1 + short_stop_loss)
    longLimitPrice = strategy.position_avg_price * (1 + long_take_profit)
    shortLimitPrice = strategy.position_avg_price * (1 - short_take_profit)
    window_2 = window()
    if long_entry and trade_long and (window_2 if showDate else True):
        strategy.entry('Long', strategy.long)
    window_3 = window()
    if short_entry and trade_short and (window_3 if showDate else True):
        strategy.entry('Short', strategy.short)
    if strategy.position_size > 0.0:
        if use_long_stop_loss and (not use_long_take_profit):
            strategy.exit('Long', stop=longStopPrice)
        if use_long_take_profit and (not use_long_stop_loss):
            strategy.exit('Long', limit=longLimitPrice)
        if use_long_take_profit and use_long_stop_loss:
            strategy.exit('Long', stop=longStopPrice, limit=longLimitPrice)
    if strategy.position_size < 0.0:
        if use_short_stop_loss and (not use_short_take_profit):
            strategy.exit('Short', stop=shortStopPrice)
        if use_short_take_profit and (not use_short_stop_loss):
            strategy.exit('Short', limit=shortLimitPrice)
        if use_short_take_profit and use_short_stop_loss:
            strategy.exit('Short', stop=shortStopPrice, limit=shortLimitPrice)
    window_4 = window()
    if long_exit and (window_4 if showDate else True):
        strategy.close('Long')
    window_5 = window()
    if short_exit and (window_5 if showDate else True):
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
