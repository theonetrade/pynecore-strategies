"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, extend, fill,
    input, label, line, location, math, na, open, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.indicator('EMA 9/21 with Target Price [SS]', overlay=True, na_bool=True)
def main(
    arraylookback=input.float(500, 'ATR Lookback Length'),
    showlbls=input.bool(True, 'Show Target Price Labels')
):
    ema9 = ta.ema(close, 9)
    ema21 = ta.ema(close, 21)
    ema9_cross_ema21 = ta.crossover(ema9, ema21)
    ema21_cross_ema9 = ta.crossover(ema21, ema9)
    plotshape(close if ema9_cross_ema21 else na, title='Up Arrow', location=location.belowbar, style=shape.triangleup, size=size.small, color=color.green)
    plotshape(close if ema21_cross_ema9 else na, title='Down Arrow', location=location.abovebar, style=shape.triangledown, size=size.small, color=color.red)
    bullish: bool = close >= ema9 and close >= ema21
    bearish: bool = close <= ema9 and close <= ema21
    neutral: bool = close < ema9 and close > ema21
    bull = color.new(color.lime, 50)
    bear = color.new(color.red, 50)
    white = color.white
    neutralcolor = color.new(color.gray, 50)
    crossovercolor = color.new(color.purple, 75)
    crossundercolor = color.new(color.orange, 75)
    pallette: Color = bull if bullish else bear if bearish else neutralcolor
    emacolor: Color = crossovercolor if ema9_cross_ema21 else crossundercolor if ema21_cross_ema9 else pallette
    filla = plot(ema9, color=emacolor, linewidth=1)
    fillb = plot(ema21, color=emacolor, linewidth=1)
    fill(filla, fillb, color=pallette)
    above_ema: Series[bool] = close >= ema9 and close >= ema21
    below_ema: Series[bool] = close < ema9 and close <= ema21
    crossover: Series[bool] = ema9_cross_ema21
    crossunder: Series[bool] = ema21_cross_ema9
    bull_a: list[float] = array.new_float()
    open_a: list[float] = array.new_float()
    crossover_a: list[float] = array.new_float()
    crossunder_a: list[float] = array.new_float()
    bear_a: list[float] = array.new_float()
    for i in pine_range(0, arraylookback, 1):
        if above_ema[i]:
            array.push(bull_a, close[i])
        if crossover[i]:
            array.push(crossover_a, close[i])
            array.push(open_a, open[i])
        if below_ema[i]:
            array.push(bear_a, close[i])
        if crossunder[i]:
            array.push(crossunder_a, close[i])
    max_above = array.max(bull_a)
    crossover_avg = array.avg(crossover_a)
    max_below = array.min(bear_a)
    crossunder_avg = array.avg(crossunder_a)
    bull_dif1 = (max_above - crossover_avg) / 2
    bull_dif2 = max_above - crossover_avg
    bear_dif1 = (crossunder_avg - max_below) / 2
    bear_dif2 = crossunder_avg - max_below
    op: float = 0.0
    bull_tgt: float = 0.0
    bull_tgt_2: float = 0.0
    bear_tgt: float = 0.0
    bear_tgt_2: float = 0.0
    bull_tgt_1_lbl: Persistent[Label] = na(Label)
    bull_tgt_2_lbl: Persistent[Label] = na(Label)
    bear_tgt_1_lbl: Persistent[Label] = na(Label)
    bear_tgt_2_lbl: Persistent[Label] = na(Label)
    bull_tgt_lin: Persistent[Line] = na(Line)
    bull_tgt_lin_2: Persistent[Line] = na(Line)
    bear_tgt_lin: Persistent[Line] = na(Line)
    bear_tgt_lin_2: Persistent[Line] = na(Line)
    if crossover:
        if array.size(open_a) > 0:
            op = array.get(open_a, 0)
        bull_tgt = op + bull_dif1
        bull_tgt_2 = op + bull_dif2
    if crossunder:
        if array.size(open_a) > 0:
            op = array.get(open_a, 0)
        bear_tgt = op - bear_dif1
        bear_tgt_2 = op - bear_dif2
    if crossover and barstate.isconfirmed:
        line.delete(bull_tgt_lin)
        line.delete(bull_tgt_lin_2)
        label.delete(bull_tgt_1_lbl)
        label.delete(bull_tgt_2_lbl)
        bull_tgt_lin = line.new(bar_index[1], y1=bull_tgt, x2=bar_index, y2=bull_tgt, extend=extend.right, color=bull, width=3)
        bull_tgt_lin_2 = line.new(bar_index[1], y1=bull_tgt_2, x2=bar_index, y2=bull_tgt_2, extend=extend.right, color=bull, width=3)
        if showlbls:
            bull_tgt_1_lbl = label.new(bar_index[1], y=bull_tgt, text='Bull Target 1 \n' + string.tostring(math.round(bull_tgt, 2)), color=bull, textcolor=white)
            bull_tgt_2_lbl = label.new(bar_index[1], y=bull_tgt_2, text='Bull Target 2 \n' + string.tostring(math.round(bull_tgt_2, 2)), color=bull, textcolor=white)
    if crossunder and barstate.isconfirmed:
        line.delete(bear_tgt_lin)
        line.delete(bear_tgt_lin_2)
        label.delete(bear_tgt_1_lbl)
        label.delete(bear_tgt_2_lbl)
        bear_tgt_lin = line.new(bar_index[1], y1=bear_tgt, x2=bar_index, y2=bear_tgt, extend=extend.right, color=bear, width=3)
        bear_tgt_lin_2 = line.new(bar_index[1], y1=bear_tgt_2, x2=bar_index, y2=bear_tgt_2, extend=extend.right, color=bear, width=3)
        if showlbls:
            bear_tgt_1_lbl = label.new(bar_index[1], y=bear_tgt, text='Bear Target 1 \n' + string.tostring(math.round(bear_tgt, 2)), color=bear, style=label.style_label_up, textcolor=white)
            bear_tgt_2_lbl = label.new(bar_index[1], y=bear_tgt_2, text='Bear Target 2 \n' + string.tostring(math.round(bear_tgt_2, 2)), color=bear, style=label.style_label_up, textcolor=white)
    alertcondition(crossover, 'EMA 9/21 Crossover', 'Bullish Cross')
    alertcondition(crossunder, 'EMA 9/21 Crossunder', 'Bearish Cross')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
