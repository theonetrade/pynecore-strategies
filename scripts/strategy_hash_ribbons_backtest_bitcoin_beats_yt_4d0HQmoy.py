"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, barmerge, barstate, bgcolor, close, color, fill, input,
    location, math, na, plot, plotshape, request, script, shape, size, strategy, syminfo, ta, time,
    timestamp
)
from pynecore.types import NA, Series


@script.strategy('hash ribbons backtest', precision=8, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    type=input.string('Ribbons', options=('Ribbons', 'Oscillator'), title='Plot Type'),
    len_s=input(30, 'Hash Rate Short SMA (days).'),
    len_l=input(60, 'Hash Rate Long SMA (days).'),
    signals=input(True, 'Plot Signals'),
    plot_halvings=input(True, 'Plot Halvings'),
    raw=input(False, 'Plot Raw Hash Rate'),
    trade_leverage=input.float(1, title='Trade - Leverage', step=0.25),
    trade_stop=input.float(20, title='Trade - Stop Loss Percent', step=0.1, minval=0.1),
    trade_risk=input.float(100, title='Trade - Risk Percent', step=0.1, minval=0.1, maxval=100),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2015, title='From Year', minval=2012),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=2017)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    def get_round(value, precision):
        return math.round(value * math.pow(10, precision)) / math.pow(10, precision)

    live_HR_raw = request.security('BTC_HASHRATE', 'D', close, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    live_HR_short = request.security('BTC_HASHRATE', 'D', ta.sma(close, len_s), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    live_HR_long = request.security('BTC_HASHRATE', 'D', ta.sma(close, len_l), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    hist_HR_raw = request.security('BTC_HASHRATE', 'D', close, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    hist_HR_short = request.security('BTC_HASHRATE', 'D', ta.sma(close, len_s), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    hist_HR_long = request.security('BTC_HASHRATE', 'D', ta.sma(close, len_l), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    daily_s10 = request.security(syminfo.tickerid, 'D', ta.sma(close, 10), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    daily_s20 = request.security(syminfo.tickerid, 'D', ta.sma(close, 20), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    def is_newbar(res):
        t = time(res)
        return True if ta.change(t) != 0 else False

    since_new_bar: Series = ta.barssince(is_newbar('D'))
    D_total_bars: Series = NA(int)
    D_total_bars = since_new_bar[1] if since_new_bar == 0 else D_total_bars[1]
    HR_short: Series = NA(float)
    HR_long = NA(float)
    HR_raw = NA(float)
    s10: Series = NA(float)
    s20: Series = NA(float)
    HR_short = live_HR_short if barstate.isrealtime else hist_HR_short
    HR_long = live_HR_long if barstate.isrealtime else hist_HR_long
    HR_raw = live_HR_raw if barstate.isrealtime else hist_HR_raw
    s10 = (daily_s10 if since_new_bar == D_total_bars else s10[1]) if barstate.isrealtime else daily_s10
    s20 = (daily_s20 if since_new_bar == D_total_bars else s20[1]) if barstate.isrealtime else daily_s20
    capitulation = ta.crossunder(HR_short, HR_long)
    miner_capitulation = HR_short < HR_long
    recovering = HR_short > HR_short[1] and HR_short > HR_short[2] and (HR_short > HR_short[3]) and miner_capitulation
    recovered = ta.crossover(HR_short, HR_long)
    buy: Series[bool] = False
    barssince_1 = ta.barssince(recovered)
    crossunder_1 = ta.crossunder(s10, s20)
    barssince_2 = ta.barssince(crossunder_1)
    barssince_3 = ta.barssince(recovered)
    barssince_4 = ta.barssince(capitulation)
    crossover_1 = ta.crossover(HR_short, HR_long)
    buy = ta.crossover(s10, s20) and barssince_1 < barssince_2 and (barssince_3 < barssince_4) or (s10 > s20 and crossover_1)
    buy_plot = buy
    delta = HR_short - HR_long
    diff = delta / HR_short * 100
    plot(HR_raw if raw else na, color=color.new(color.green, 0), linewidth=1, style=plot.style_line, title='HR Raw')
    p1 = plot(HR_long if type == 'Ribbons' else na, color=color.new(color.gray, 0), linewidth=2, style=plot.style_line, title='HR SMA Long')
    p2 = plot(HR_short if type == 'Ribbons' else na, color=color.red if HR_short < HR_long else color.lime, linewidth=2, style=plot.style_line, title='HR SMA Short')
    fill(p1, p2, color=color.new(color.red if HR_short < HR_long else na, 30))
    plot(diff if type == 'Oscillator' else na, style=plot.style_columns, color=color.red if diff < 0 else color.blue, title='Oscillator')
    plotshape((na if na(capitulation) else 1 if capitulation else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.gray, 50), size=size.normal, text='Capitulation', textcolor=color.new(color.black, 50), title='Capitulation')
    plotshape((na if na(miner_capitulation) else 1 if miner_capitulation else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.green, 90), size=size.normal, title='Miner Capitulation')
    plotshape((na if na(recovering) else 1 if recovering else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.green, 50), size=size.normal, title='Recovering')
    plotshape((na if na(recovered) else 1 if recovered else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.lime, 0), size=size.normal, textcolor=color.new(color.white, 0), title='Recovered')
    plotshape(buy_plot if signals else na, style=shape.circle, location=location.top, color=color.new(color.blue, 0), size=size.normal, text='Buy', textcolor=color.new(color.blue, 0), title='Buy')
    halving_1 = timestamp(2012, 11, 28, 0, 0)
    halving_2 = timestamp(2016, 7, 9, 0, 0)
    halving_3 = timestamp(2020, 4, 30, 0, 0)
    h1_range = time >= halving_1 - 3 * 24 * 60 * 60 * 1000 and time <= halving_1 + 3 * 24 * 60 * 60 * 1000
    h2_range = time >= halving_2 - 3 * 24 * 60 * 60 * 1000 and time <= halving_2 + 3 * 24 * 60 * 60 * 1000
    h3_range = time >= halving_3 - 3 * 24 * 60 * 60 * 1000 and time <= halving_3 + 3 * 24 * 60 * 60 * 1000
    bgcolor(color.red if h1_range and plot_halvings else na)
    bgcolor(color.red if h2_range and plot_halvings else na)
    bgcolor(color.red if h3_range and plot_halvings else na)
    alertcondition(capitulation, title='Alert - Capitulation')
    alertcondition(recovered, title='Alert - Recovered')
    alertcondition(buy and (not buy[1]), title='Alert - Buy')
    barssince_5 = ta.barssince(recovered)
    crossunder_2 = ta.crossunder(s10, s20)
    barssince_6 = ta.barssince(crossunder_2)
    barssince_7 = ta.barssince(recovered)
    barssince_8 = ta.barssince(capitulation)
    crossover_2 = ta.crossover(HR_short, HR_long)
    enter_long_condition = ta.crossover(s10, s20) and barssince_5 < barssince_6 and (barssince_7 < barssince_8) or (s10 > s20 and crossover_2)
    enter_short_condition = capitulation
    exit_condition = capitulation
    position_signal: Series[int] = 0
    position_signal = 1 if enter_long_condition else -1 if enter_short_condition else 0 if exit_condition else position_signal[1]
    if strategy.opentrades == 0:
        contracts = get_round(strategy.equity * trade_leverage / close * (trade_risk / 100), 4)
        if window() and enter_long_condition:
            strategy.entry('LONG', strategy.long, qty=contracts)
    stop_difference = strategy.position_avg_price / trade_leverage * (trade_stop / 100)
    in_long = strategy.position_size > 0
    long_stop = strategy.position_avg_price - stop_difference if in_long else na
    strategy.exit('S/L', 'LONG', stop=long_stop, qty=math.abs(get_round(strategy.position_size, 4)))
    change_1 = ta.change(position_signal)
    if exit_condition or math.abs(cast_bool(change_1)) > 0:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
