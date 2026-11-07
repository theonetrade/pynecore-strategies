"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, input, line, math, plot, script,
    strategy, ta
)
from pynecore.types import Series


@script.strategy('Turtle trading strategy (Donchian/ATR)', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    enter_period=input.int(20, minval=1, title='Enter Channel'),
    exit_period=input.int(10, minval=1, title='Exit Channel'),
    offset_bar=input.int(0, minval=0, title='Offset Bars'),
    direction=input.string('Long', options=('Long', 'Short'), title='Direction'),
    atrmult=input(2.0, title='ATR multiplier (Stop Loss)'),
    atrperiod=input(20, title='ATR Period')
):
    max_length = math.max(enter_period, exit_period)
    closed_pos: bool = False
    dir_long = True if direction == 'Long' else False
    atr = ta.ema(ta.tr(True), atrperiod)
    atrstop = atrmult * atr
    upper: Series = ta.highest(enter_period) if dir_long else ta.highest(exit_period)
    lower: Series = ta.lowest(exit_period) if dir_long else ta.lowest(enter_period)
    atrupper = ta.ema(close + atrstop, 3)
    atrlower = ta.ema(close - atrstop, 3)
    atrupper_incpos = close + atr
    atrlower_incpos = close - atr
    plotted_atr: Series = atrlower if dir_long else atrupper
    atr_incpos = atrupper_incpos if dir_long else atrlower_incpos
    l = plot(lower, style=plot.style_line, linewidth=3, color=color.new(color.lime, 0), offset=1)
    u = plot(upper, style=plot.style_line, linewidth=3, color=color.new(color.lime, 0), offset=1)
    a = plot(plotted_atr, style=plot.style_line, linewidth=2, color=color.new(color.red, 0), offset=1)
    lin: Series = line.new(x1=bar_index[5], x2=bar_index, y1=atr_incpos, y2=atr_incpos, color=color.lime, style=line.style_dashed)
    line.set_width(lin, 2)
    line.delete(lin[4])
    break_up = close >= upper[1]
    break_down = close <= lower[1]
    stop_loss = close <= plotted_atr[1] if dir_long else close >= plotted_atr[1]
    if break_up and dir_long:
        strategy.entry('buy', strategy.long, 1)
        closed_pos = False
    if (break_down or stop_loss) and dir_long:
        strategy.close('buy')
    if break_down and (not dir_long):
        strategy.entry('sell', strategy.short, 1)
        closed_pos = False
    if (break_up or stop_loss) and (not dir_long):
        strategy.close('sell')
        closed_pos = True
    alertcondition(True, 'TurtleTest', 'Teste Estratégia Turtle')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
