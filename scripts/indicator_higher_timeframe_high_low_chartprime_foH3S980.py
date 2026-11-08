"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barcolor, barstate, bgcolor, chart, close, color, fill, high,
    input, label, line, location, low, math, na, plot, plotchar, request, script, size, syminfo,
    ta
)
from pynecore.types import Color, Persistent, PersistentSeries


@script.indicator(title='Higher Timeframe High & Low [ChartPrime]', shorttitle='H/L HTF [ChartPrime]', overlay=True, max_lines_count=2, max_labels_count=10, na_bool=True)
def main(
    extension=input.int(50, 'Extension to the right of High and Low', group='Settings'),
    timeframe__ren__=input.timeframe('D', 'timeframe', tooltip='Use Higher Timeframe then Current', group='Settings'),
    separator=input.bool(False, 'Period Separator'),
    show_trend=input.bool(False, 'Show Trend?'),
    show_break=input.bool(False, 'Show Breakout Labels?')
):
    color__ren__: Persistent[Color] = na(Color)
    color1: Color = na(Color)
    check: PersistentSeries[bool] = na(bool)
    colorDn: Color = color.new('#D41919')
    colorUp: Color = color.new('#13B818')
    indexHighTF = 1 if barstate.isrealtime else 0
    indexCurrTF = 0 if barstate.isrealtime else 1
    pricehigh = inline_series(request.security(syminfo.tickerid, timeframe__ren__, high[indexHighTF]), indexCurrTF)
    pricelow = inline_series(request.security(syminfo.tickerid, timeframe__ren__, low[indexHighTF]), indexCurrTF)
    price_avg = math.avg(pricelow, pricehigh)
    high_break = ta.crossover(close, pricehigh)
    low_break = ta.crossunder(close, pricelow)
    if high_break:
        check = True
        color1 = colorUp
        color__ren__ = colorUp
    elif low_break:
        check = False
        color1 = colorDn
        color__ren__ = colorDn
    if high_break and check[1] == False and show_break:
        label.new(x=bar_index, y=low * 0.99, text=timeframe__ren__ + '\nHigh Break', style=label.style_label_up, textcolor=chart.fg_color, color=color.new('#0E4E11'), size=size.small)
    if low_break and check[1] == True and show_break:
        label.new(x=bar_index, y=high * 1.01, text=timeframe__ren__ + '\nLow Break', style=label.style_label_down, textcolor=chart.fg_color, color=color.new('#6E1414'), size=size.small)
    change_1 = ta.change(pricelow)
    change_hl = not ta.change(pricehigh) or not change_1
    ph = plot(series=pricehigh if change_hl and (not show_trend) else pricehigh if show_trend else na, title='High', style=plot.style_linebr, linewidth=2, color=colorDn if not show_trend else color.new(colorDn, 80))
    pm = plot(series=price_avg if change_hl and (not show_trend) else price_avg if show_trend else na, title='L & H Avg', style=plot.style_stepline_diamond if show_trend else plot.style_circles, linewidth=1, color=color.new(chart.fg_color, 90) if show_trend else color.new(chart.fg_color, 50))
    pl = plot(series=pricelow if change_hl and (not show_trend) else pricelow if show_trend else na, title='Low', style=plot.style_linebr, linewidth=2, color=colorUp if not show_trend else color.new(colorUp, 80))
    plotchar(series=ta.crossunder(high, pricehigh), title='Resistance', char='◆', location=location.abovebar, offset=-1, color=colorDn, size=size.tiny)
    plotchar(series=ta.crossover(low, pricelow), title='Support', char='◆', location=location.belowbar, offset=-1, color=colorUp, size=size.tiny)
    if barstate.islast:
        label.new(point=chart.point.from_index(bar_index + extension, pricehigh), text='⮪ ' + timeframe__ren__ + ' High', style=label.style_label_left, textcolor=chart.fg_color, color=colorDn, size=size.normal)
        label.new(point=chart.point.from_index(bar_index + extension, pricelow), text='⮨ ' + timeframe__ren__ + ' Low', style=label.style_label_left, textcolor=chart.fg_color, color=color.new('#158D19'), size=size.normal)
    if change_hl and barstate.islast:
        h_Left = chart.point.from_index(bar_index, pricehigh)
        h_Right = chart.point.from_index(bar_index + extension, pricehigh)
        line.new(h_Left, h_Right, color=colorDn, style=line.style_solid, width=2)
        l_Left = chart.point.from_index(bar_index, pricelow)
        l_Right = chart.point.from_index(bar_index + extension, pricelow)
        line.new(l_Left, l_Right, color=colorUp, width=2)
        m_Left = chart.point.from_index(bar_index, math.avg(pricelow, pricehigh))
        m_Right = chart.point.from_index(bar_index + extension, math.avg(pricelow, pricehigh))
        line.new(m_Left, m_Right, color=chart.fg_color, width=1 if show_trend else 2, style=line.style_solid if show_trend else line.style_dotted)
    barcolor(color__ren__ if show_trend else color1)
    bgcolor((color.new(chart.fg_color, 90) if not change_hl else na) if separator else na)
    fill(plot1=ph, plot2=pl, top_value=pricehigh, bottom_value=pricelow, top_color=color.new(colorDn, 80 if chart.bg_color == color.white else 92) if not show_trend else na, bottom_color=color.new(colorUp, 80 if chart.bg_color == color.white else 92) if not show_trend else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
