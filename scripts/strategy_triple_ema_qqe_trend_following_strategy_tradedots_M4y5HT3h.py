"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, close, color, currency, dayofweek, fill, high,
    input, label, low, math, na, nz, plot, script, strategy, syminfo, ta
)
from pynecore.types import Persistent, Series


@script.strategy('Triple EMA + QQE Trend Following Strategy [TradeDots]', overlay=True, max_lines_count=500, max_boxes_count=100, initial_capital=10000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.01, default_qty_type=strategy.percent_of_equity, default_qty_value=80, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    rsi_period=input(14, title='RSI Length', group='QQE'),
    rsi_smoothing_period=input(5, title='RSI Smoothing Period', group='QQE'),
    factor=input(4.238, title='QQE Factor', group='QQE'),
    ma_source: Series[float] = input(close, 'TEMA Source', inline='MA1', group='TEMA'),
    tema1_length=input.int(20, 'TEMA #1 Length', minval=1, group='TEMA'),
    tema2_length=input.int(40, 'TEMA #2 Length', minval=1, group='TEMA'),
    input_stop_loss=input.int(120, 'Stop Loss (pip)', group='Strategy')
):
    def GetPipSize():
        return syminfo.mintick * (10 if syminfo.type == 'forex' else 1)

    pipSize = GetPipSize()
    ts: Persistent[float] = 0.0
    stopLoss: Persistent[float] = na(float)
    def tema(src, length):
        ema1 = ta.ema(src, length)
        ema2 = ta.ema(ema1, length)
        ema3 = ta.ema(ema2, length)
        tema__0000000e__ = 3 * ema1 - 3 * ema2 + ema3
        return tema__0000000e__

    tema1 = tema(ma_source, tema1_length)
    tema2: Series = tema(ma_source, tema2_length)
    tema1Plot = plot(tema1, title=' TEMA #1', color=color.new('#C7F9CC'), linewidth=2)
    tema2Plot = plot(tema2, title=' TEMA #2', color=color.new('#57CC99'), linewidth=2)
    rsi = ta.rsi(close, rsi_period)
    rsiMa: Series = ta.ema(rsi, rsi_smoothing_period)
    atrRsi = math.abs(rsiMa[1] - rsiMa)
    final_smooth = rsi_period * 2 - 1
    MaAtrRsi = ta.ema(atrRsi, final_smooth)
    dar = ta.ema(MaAtrRsi, final_smooth) * factor
    crossover = ta.crossover(rsiMa, ts)
    crossunder = ta.crossunder(rsiMa, ts)
    ts = nz(rsiMa - MaAtrRsi * factor if crossover else rsiMa + MaAtrRsi * factor if crossunder else math.max(rsiMa - MaAtrRsi * factor, ts) if rsiMa > ts else math.min(rsiMa + MaAtrRsi * factor, ts), rsiMa)
    crossover_1 = ta.crossover(rsiMa, ts)
    long_condition = close > tema1 and tema1 > tema2 and (tema2 > tema2[1]) and crossover_1 and (dayofweek != dayofweek.monday)
    crossunder_1 = ta.crossunder(rsiMa, ts)
    short_condition = close < tema1 and tema1 < tema2 and (tema2 < tema2[1]) and crossunder_1 and (dayofweek != dayofweek.monday)
    if long_condition and strategy.opentrades == 0:
        strategy.entry('Long', strategy.long)
        label.new(bar_index, low, '🟢 Long', color=color.new('#9CFF87'), style=label.style_label_up)
        stopLoss = close - input_stop_loss * pipSize
    elif short_condition and strategy.opentrades == 0:
        strategy.entry('Short', strategy.short)
        label.new(bar_index, high, '🔴 Short', color=color.new('#F9396A'), style=label.style_label_down, textcolor=color.white)
        stopLoss = close + input_stop_loss * pipSize
    elif strategy.opentrades == 0:
        stopLoss = na
    if barstate.isconfirmed and strategy.opentrades > 0:
        if strategy.opentrades.size(strategy.opentrades - 1) > 0:
            if close < stopLoss:
                strategy.close('Long')
            stopLoss = close - input_stop_loss * pipSize if close - input_stop_loss * pipSize > stopLoss else stopLoss
        elif strategy.opentrades.size(strategy.opentrades - 1) < 0:
            if close > stopLoss:
                strategy.close('Short')
            stopLoss = close + input_stop_loss * pipSize if close + input_stop_loss * pipSize < stopLoss else stopLoss
    is_pos_closed = strategy.position_size[1] != 0 and strategy.position_size == 0
    is_short: Series = strategy.position_size < 0
    is_long: Series = strategy.position_size > 0
    if is_pos_closed and is_short[1]:
        label.new(bar_index, low, '🟢 Close Short', color=color.new('#9CFF87'), style=label.style_label_up)
    elif is_pos_closed and is_long[1]:
        label.new(bar_index, high, '🔴 Close Long', color=color.new('#F9396A'), style=label.style_label_down, textcolor=color.white)
    fill(tema2Plot, tema1Plot, math.max(tema2, tema1), tema2, color.new(color.new('#9CFF87'), 85), color.new(color.new('#9CFF87'), 70))
    fill(tema2Plot, tema1Plot, tema2, math.min(tema2, tema1), color.new(color.new('#F9396A'), 70), color.new(color.new('#F9396A'), 85))
    plot(stopLoss, color=color.new('#F9396A'), style=plot.style_cross, linewidth=2, title='Trail Stop')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
