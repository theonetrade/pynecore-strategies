"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, box, close, color, high, input, label, line, low, math, na,
    plot, script, size, strategy, ta
)
from pynecore.types import Box, Persistent


@script.strategy("VWAP Breakout Strategy + EMAs + Clean Cycle/TP/SL Plots", overlay=True, max_lines_count=100, max_labels_count=100)
def main(
    atr_length=input.int(14, "ATR Length"),
    atr_multiplier=input.float(1.5, "ATR Multiplier for Stop"),
    tp1_atr_mult=input.float(1.0, "TP1 Multiplier (ATR)"),
    tp2_atr_mult=input.float(2.0, "TP2 Multiplier (ATR)"),
    show_vwap=input(True, "Show VWAP"),
    show_emas=input(True, "Show EMAs (100,34,5)"),
    show_cycle_zone=input(True, "Show Full Cycle Range Zone"),
    cycle_points=input.int(200, "Full Cycle Range Points (see table for timeframe)"),
    round_step=input.int(500, "Round Number Level Step (e.g., 500/1000)"),
    show_round_lvls=input(True, "Show Round Number Levels"),
    show_tp_sl_labels=input(True, "Show TP/SL Labels"),
    pivot_len=input.int(5, "Pivot Lookback for Cycle Zone")
):
    vwap = ta.vwap
    atr_val = ta.atr(atr_length)
    ema100 = ta.ema(close, 100)
    ema34 = ta.ema(close, 34)
    ema5 = ta.ema(close, 5)

    plot(vwap if show_vwap else na, title='VWAP', color=color.blue, linewidth=2)
    plot(ema100 if show_emas else na, color=color.blue, title='EMA 100')
    plot(ema34 if show_emas else na, color=color.orange, title='EMA 34')
    plot(ema5 if show_emas else na, color=color.green, title='EMA 5')

    breakout_long = ta.crossover(close, vwap)
    breakout_short = ta.crossunder(close, vwap)

    stop_loss_long = close - atr_val * atr_multiplier if breakout_long else na
    stop_loss_short = close + atr_val * atr_multiplier if breakout_short else na
    tp1_long = close + atr_val * tp1_atr_mult if breakout_long else na
    tp2_long = close + atr_val * tp2_atr_mult if breakout_long else na
    tp1_short = close - atr_val * tp1_atr_mult if breakout_short else na
    tp2_short = close - atr_val * tp2_atr_mult if breakout_short else na

    if breakout_long:
        strategy.entry('Breakout Long', strategy.long)
        strategy.exit('Exit Long', from_entry='Breakout Long', stop=stop_loss_long, limit=tp2_long)
    if breakout_short:
        strategy.entry('Breakout Short', strategy.short)
        strategy.exit('Exit Short', from_entry='Breakout Short', stop=stop_loss_short, limit=tp2_short)

    if show_tp_sl_labels:
        if breakout_long:
            label.new(bar_index, low, 'Buy', color=color.new(color.green, 0), textcolor=color.white, style=label.style_label_up, size=size.normal)
            label.new(bar_index, close, 'ENTRY (Long)', color=color.green, style=label.style_label_up, textcolor=color.white, size=size.tiny)
            label.new(bar_index, tp1_long, 'TP1', color=color.teal, style=label.style_label_down, textcolor=color.white, size=size.tiny)
            label.new(bar_index, tp2_long, 'TP2', color=color.purple, style=label.style_label_down, textcolor=color.white, size=size.tiny)
            label.new(bar_index, stop_loss_long, 'STOP', color=color.red, style=label.style_label_down, textcolor=color.white, size=size.tiny)

            line.new(bar_index, tp1_long, bar_index + 10, tp1_long, color=color.teal, width=1, style=line.style_dashed)
            line.new(bar_index, tp2_long, bar_index + 10, tp2_long, color=color.purple, width=1, style=line.style_dotted)
            line.new(bar_index, stop_loss_long, bar_index + 10, stop_loss_long, color=color.red, width=1, style=line.style_dotted)
        if breakout_short:
            label.new(bar_index, high, 'Sell', color=color.new(color.red, 0), textcolor=color.white, style=label.style_label_down, size=size.normal)
            label.new(bar_index, close, 'ENTRY (Short)', color=color.red, style=label.style_label_down, textcolor=color.white, size=size.tiny)
            label.new(bar_index, tp1_short, 'TP1', color=color.teal, style=label.style_label_up, textcolor=color.white, size=size.tiny)
            label.new(bar_index, tp2_short, 'TP2', color=color.purple, style=label.style_label_up, textcolor=color.white, size=size.tiny)
            label.new(bar_index, stop_loss_short, 'STOP', color=color.green, style=label.style_label_up, textcolor=color.white, size=size.tiny)
            line.new(bar_index, tp1_short, bar_index + 10, tp1_short, color=color.teal, width=1, style=line.style_dashed)
            line.new(bar_index, tp2_short, bar_index + 10, tp2_short, color=color.purple, width=1, style=line.style_dotted)
            line.new(bar_index, stop_loss_short, bar_index + 10, stop_loss_short, color=color.green, width=1, style=line.style_dotted)

    if show_round_lvls:
        round = math.round(close / round_step) * round_step
        for offset in pine_range(-2, 2):
            level = round + offset * round_step
            line.new(bar_index - 50, level, bar_index + 1, level, color=color.gray, style=line.style_dotted, width=1)

    cycle_box: Persistent[Box] = na(Box)
    last_pivot_bar: Persistent[int] = na(int)
    last_pivot_price: Persistent[float] = na(float)

    pl = ta.pivotlow(low, pivot_len, pivot_len)
    if show_cycle_zone and (not na(pl)):
        last_pivot_bar = bar_index - pivot_len
        last_pivot_price = low[pivot_len]
        if not na(cycle_box):
            box.delete(cycle_box)

        cycle_box = box.new(last_pivot_bar, last_pivot_price + cycle_points, bar_index, last_pivot_price, border_color=color.yellow, bgcolor=color.new(color.yellow, 85))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
