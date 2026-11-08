"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barstate, chart, close, color, fill, input, location,
    math, na, open, plot, plotchar, plotshape, position, request, script, shape, size, syminfo, ta,
    table, text
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Zero Lag Trend Signals (MTF) [AlgoAlpha]', shorttitle='AlgoAlpha - 0️⃣Zero Lag Signals', overlay=True)
def main(
    length=input.int(70, 'Length', tooltip='The Look-Back window for the Zero-Lag EMA calculations', group='Main Calculations'),
    mult=input.float(1.2, 'Band Multiplier', tooltip='This value controls the thickness of the bands, a larger value makes the indicato less noisy', group='Main Calculations'),
    t1=input.timeframe('5', 'Time frame 1', group='Extra Timeframes'),
    t2=input.timeframe('15', 'Time frame 2', group='Extra Timeframes'),
    t3=input.timeframe('60', 'Time frame 3', group='Extra Timeframes'),
    t4=input.timeframe('240', 'Time frame 4', group='Extra Timeframes'),
    t5=input.timeframe('1D', 'Time frame 5', group='Extra Timeframes'),
    green=input.color(color.new('#00FFBB'), 'Bullish Color', group='Appearance'),
    red=input.color(color.new('#FF1100'), 'Bearish Color', group='Appearance')
):
    src: Series = close
    lag = math.floor((length - 1) / 2)
    zlema = ta.ema(src + src - src[lag], length)
    volatility = ta.highest(ta.atr(length), length * 3) * mult
    trend: PersistentSeries[int] = 0
    if ta.crossover(close, zlema + volatility):
        trend = 1
    if ta.crossunder(close, zlema - volatility):
        trend = -1
    zlemaColor = color.new(green, 70) if trend == 1 else color.new(red, 70)
    m = plot(zlema, title='Zero Lag Basis', linewidth=2, color=zlemaColor)
    upper = plot(zlema + volatility if trend == -1 else na, style=plot.style_linebr, color=color.new(red, 90), title='Upper Deviation Band')
    lower = plot(zlema - volatility if trend == 1 else na, style=plot.style_linebr, color=color.new(green, 90), title='Lower Deviation Band')
    fill(m, upper, (open + close) / 2, zlema + volatility, color.new(red, 90), color.new(red, 70))
    fill(m, lower, (open + close) / 2, zlema - volatility, color.new(green, 90), color.new(green, 70))
    plotshape(zlema + volatility if ta.crossunder(trend, 0) else na, 'Bearish Trend', shape.labeldown, location.absolute, red, text='▼', textcolor=chart.fg_color, size=size.small)
    plotshape(zlema - volatility if ta.crossover(trend, 0) else na, 'Bullish Trend', shape.labelup, location.absolute, green, text='▲', textcolor=chart.fg_color, size=size.small)
    plotchar(zlema - volatility * 1.5 if ta.crossover(close, zlema) and trend == 1 and (trend[1] == 1) else na, 'Bullish Entry', '▲', location.absolute, green, size=size.tiny)
    plotchar(zlema + volatility * 1.5 if ta.crossunder(close, zlema) and trend == -1 and (trend[1] == -1) else na, 'Bearish Entry', '▼', location.absolute, red, size=size.tiny)
    s1 = request.security(syminfo.tickerid, t1, trend)
    s2 = request.security(syminfo.tickerid, t2, trend)
    s3 = request.security(syminfo.tickerid, t3, trend)
    s4 = request.security(syminfo.tickerid, t4, trend)
    s5 = request.security(syminfo.tickerid, t5, trend)
    s1a = 'Bullish' if s1 == 1 else 'Bearish'
    s2a = 'Bullish' if s2 == 1 else 'Bearish'
    s3a = 'Bullish' if s3 == 1 else 'Bearish'
    s4a = 'Bullish' if s4 == 1 else 'Bearish'
    s5a = 'Bullish' if s5 == 1 else 'Bearish'
    if barstate.islast:
        data_table: Persistent = table.new(position=position.top_right, columns=2, rows=6, bgcolor=chart.bg_color, border_width=1, border_color=chart.fg_color, frame_color=chart.fg_color, frame_width=1)
        table.cell(data_table, text_halign=text.align_center, column=0, row=0, text='Time Frame', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=0, text='Signal', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=0, row=1, text=t1, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=1, text=s1a, text_color=chart.fg_color, bgcolor=color.new(green, 70) if s1a == 'Bullish' else color.new(red, 70))
        table.cell(data_table, text_halign=text.align_center, column=0, row=2, text=t2, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=2, text=s2a, text_color=chart.fg_color, bgcolor=color.new(green, 70) if s2a == 'Bullish' else color.new(red, 70))
        table.cell(data_table, text_halign=text.align_center, column=0, row=3, text=t3, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=3, text=s3a, text_color=chart.fg_color, bgcolor=color.new(green, 70) if s3a == 'Bullish' else color.new(red, 70))
        table.cell(data_table, text_halign=text.align_center, column=0, row=4, text=t4, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=4, text=s4a, text_color=chart.fg_color, bgcolor=color.new(green, 70) if s4a == 'Bullish' else color.new(red, 70))
        table.cell(data_table, text_halign=text.align_center, column=0, row=5, text=t5, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=5, text=s5a, text_color=chart.fg_color, bgcolor=color.new(green, 70) if s5a == 'Bullish' else color.new(red, 70))
    alertcondition(ta.crossover(close, zlema) and trend == 1 and (trend[1] == 1), 'Bullish Entry Signal', message='Bullish Entry Signal detected. Consider entering a long position.')
    alertcondition(ta.crossunder(close, zlema) and trend == -1 and (trend[1] == -1), 'Bearish Entry Signal', message='Bearish Entry Signal detected. Consider entering a short position.')
    alertcondition(ta.crossover(trend, 0), 'Bullish Trend')
    alertcondition(ta.crossunder(trend, 0), 'Bearish Trend')
    alertcondition(ta.cross(trend, 0), '(Bullish or Bearish) Trend')
    alertcondition(ta.crossover(s1, 0), 'Bullish Trend Time Frame 1')
    alertcondition(ta.crossunder(s1, 0), 'Bearish Trend Time Frame 1')
    alertcondition(ta.cross(s1, 0), '(Bullish or Bearish) Trend Time Frame 1')
    alertcondition(ta.crossover(s2, 0), 'Bullish Trend Time Frame 2')
    alertcondition(ta.crossunder(s2, 0), 'Bearish Trend Time Frame 2')
    alertcondition(ta.cross(s2, 0), '(Bullish or Bearish) Trend Time Frame 2')
    alertcondition(ta.crossover(s3, 0), 'Bullish Trend Time Frame 3')
    alertcondition(ta.crossunder(s3, 0), 'Bearish Trend Time Frame 3')
    alertcondition(ta.cross(s3, 0), '(Bullish or Bearish) Trend Time Frame 3')
    alertcondition(ta.crossover(s4, 0), 'Bullish Trend Time Frame 4')
    alertcondition(ta.crossunder(s4, 0), 'Bearish Trend Time Frame 4')
    alertcondition(ta.cross(s4, 0), '(Bullish or Bearish) Trend Time Frame 4')
    alertcondition(ta.crossover(s5, 0), 'Bullish Trend Time Frame 5')
    alertcondition(ta.crossunder(s5, 0), 'Bearish Trend Time Frame 5')
    alertcondition(ta.cross(s5, 0), '(Bullish or Bearish) Trend Time Frame 5')
    alertcondition(ta.crossover(close, zlema) and trend == 1 and (trend[1] == 1), 'Bullish Entry')
    alertcondition(ta.crossunder(close, zlema) and trend == -1 and (trend[1] == -1), 'Bearish Entry')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
