"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, plot, script, strategy, ta


@script.strategy(title='STB - Gianno Nano Strategy', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    short_yes=input.bool(True, 'Active Short', group='Engine Strategy'),
    ema_fast=input.int(10, 'Fast Average Period', group='Engine Strategy'),
    ema_slow=input.int(60, 'Slow Average Period', group='Engine Strategy'),
    __input_3__=input.float(3, 'SL Long Percent', step=0.01, group='Take Profit and Stop Loss %'),
    __input_4__=input.float(5, 'SL Short Percent', step=0.01, group='Take Profit and Stop Loss %'),
    ema_stop_input=input.int(112, 'Stop Average Period', group='Stop Loss Cross'),
    ema_stop_sl_input=input.bool(False, 'Stop if Close crosses Stop Average', tooltip='If you choose this option, Percent Stop Loss will be disabled', group='Stop Loss Cross'),
    __input_7__=input.float(36, 'TP Long Percent', step=0.01, group='Take Profit and Stop Loss %'),
    __input_8__=input.float(24, 'TP Short Percent', step=0.01, group='Take Profit and Stop Loss %')
):
    SL_Long_input = __input_3__ / 100
    SL_Short_input = __input_4__ / 100
    TP_Long_input = __input_7__ / 100
    TP_Short_input = __input_8__ / 100
    ema10 = ta.ema(close, ema_fast)
    ema60 = ta.ema(close, ema_slow)
    ema_stop = ta.ema(close, ema_stop_input)
    plot(ema10, 'EMA 10', color.yellow, 2)
    plot(ema60, 'EMA 60', color.aqua, 2)
    plot(ema_stop if ema_stop_sl_input else na, 'EMA Stop', color.red, 2)
    long_cond = ta.crossover(ema10, ema60)
    short_cond = ta.crossunder(ema10, ema60) and short_yes
    close_cond = ta.crossunder(ema10, ema60) and (not short_yes)
    cond_stop_long = ta.crossunder(close, ema_stop)
    cond_stop_short = ta.crossover(close, ema_stop)
    if long_cond:
        strategy.entry('EL', strategy.long)
    if short_cond:
        strategy.entry('ES', strategy.short)
    if close_cond:
        strategy.close('EL')
    entry_price_long = ta.valuewhen(long_cond, close, 0)
    entry_price_short = ta.valuewhen(short_cond, close, 0)
    SL_long = entry_price_long * (1 - SL_Long_input) if SL_Long_input > 0 else 0
    SL_short = entry_price_short * (1 + SL_Short_input) if SL_Short_input > 0 else 999999
    TP_long = entry_price_long * (1 + TP_Long_input) if TP_Long_input > 0 else 999999
    TP_short = entry_price_short * (1 - TP_Short_input) if TP_Short_input > 0 else 0
    if strategy.position_size > 0 and (not ema_stop_sl_input):
        strategy.exit(id='XL STP', stop=SL_long, limit=TP_long)
    if strategy.position_size < 0 and (not ema_stop_sl_input):
        strategy.exit(id='XS STP', stop=SL_short, limit=TP_short)
    if strategy.position_size > 0 and ema_stop_sl_input:
        strategy.exit(id='XL2 STP', limit=TP_long)
    if strategy.position_size < 0 and ema_stop_sl_input:
        strategy.exit(id='XS2 STP', limit=TP_short)
    if cond_stop_long and ema_stop_sl_input:
        strategy.close('EL')
    if cond_stop_short and ema_stop_sl_input:
        strategy.close('ES')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
