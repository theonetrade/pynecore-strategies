"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, close, color, extend, fill, high, input,
    label, line, location, low, math, na, open, plot, plotchar, plotshape, script, shape, size,
    string, ta, text, time, time_close, xloc, yloc
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Order Block Finder', overlay=True, na_bool=True)
def main(
    colors=input.string(title='Color Scheme', defval='DARK', options=('DARK', 'BRIGHT')),
    periods=input(5, 'Relevant Periods to identify OB'),
    threshold=input.float(0.0, 'Min. Percent move to identify OB', step=0.1),
    usewicks=input(False, 'Use whole range [High/Low] for OB marking?'),
    showbull=input(True, 'Show latest Bullish Channel?'),
    showbear=input(True, 'Show latest Bearish Channel?'),
    showdocu=input(False, 'Show Label for documentation tooltip?'),
    info_pan=input(False, 'Show Latest OB Panel?')
):
    ob_period = periods + 1
    absmove = math.abs(close[ob_period] - close[1]) / close[ob_period] * 100
    relmove = absmove >= threshold
    bullcolor = color.white if colors == 'DARK' else color.green
    bearcolor = color.blue if colors == 'DARK' else color.red
    bullishOB = close[ob_period] < open[ob_period]
    upcandles: int = 0
    for i in pine_range(1, periods, 1):
        upcandles = upcandles + (1 if close[i] > open[i] else 0)
    OB_bull = bullishOB and upcandles == periods and relmove
    OB_bull_high = (high[ob_period] if usewicks else open[ob_period]) if OB_bull else na
    OB_bull_low = low[ob_period] if OB_bull else na
    OB_bull_avg = (OB_bull_high + OB_bull_low) / 2
    bearishOB = close[ob_period] > open[ob_period]
    downcandles: int = 0
    for i in pine_range(1, periods, 1):
        downcandles = downcandles + (1 if close[i] < open[i] else 0)
    OB_bear = bearishOB and downcandles == periods and relmove
    OB_bear_high = high[ob_period] if OB_bear else na
    OB_bear_low = (low[ob_period] if usewicks else open[ob_period]) if OB_bear else na
    OB_bear_avg = (OB_bear_low + OB_bear_high) / 2
    plotshape(OB_bull, title='Bullish OB', style=shape.triangleup, color=bullcolor, textcolor=bullcolor, size=size.tiny, location=location.belowbar, offset=-ob_period, text='Bullish OB')
    bull1 = plot(OB_bull_high, title='Bullish OB High', style=plot.style_linebr, color=bullcolor, offset=-ob_period, linewidth=3)
    bull2 = plot(OB_bull_low, title='Bullish OB Low', style=plot.style_linebr, color=bullcolor, offset=-ob_period, linewidth=3)
    fill(bull1, bull2, color=color.new(bullcolor, 0), title='Bullish OB fill')
    plotshape(OB_bull_avg, title='Bullish OB Average', style=shape.cross, color=bullcolor, size=size.normal, location=location.absolute, offset=-ob_period)
    plotshape(OB_bear, title='Bearish OB', style=shape.triangledown, color=bearcolor, textcolor=bearcolor, size=size.tiny, location=location.abovebar, offset=-ob_period, text='Bearish OB')
    bear1 = plot(OB_bear_low, title='Bearish OB Low', style=plot.style_linebr, color=bearcolor, offset=-ob_period, linewidth=3)
    bear2 = plot(OB_bear_high, title='Bearish OB High', style=plot.style_linebr, color=bearcolor, offset=-ob_period, linewidth=3)
    fill(bear1, bear2, color=color.new(bearcolor, 0), title='Bearish OB fill')
    plotshape(OB_bear_avg, title='Bearish OB Average', style=shape.cross, color=bearcolor, size=size.normal, location=location.absolute, offset=-ob_period)
    linebull1: Persistent[Line] = na(Line)
    linebull2: Persistent[Line] = na(Line)
    linebull3: Persistent[Line] = na(Line)
    linebear1: Persistent[Line] = na(Line)
    linebear2: Persistent[Line] = na(Line)
    linebear3: Persistent[Line] = na(Line)
    if OB_bull and showbull:
        line.delete(linebull1)
        linebull1 = line.new(x1=bar_index, y1=OB_bull_avg, x2=bar_index - 1, y2=OB_bull_avg, extend=extend.left, color=bullcolor, style=line.style_solid, width=1)
        line.delete(linebull2)
        linebull2 = line.new(x1=bar_index, y1=OB_bull_high, x2=bar_index - 1, y2=OB_bull_high, extend=extend.left, color=bullcolor, style=line.style_dashed, width=1)
        line.delete(linebull3)
        linebull3 = line.new(x1=bar_index, y1=OB_bull_low, x2=bar_index - 1, y2=OB_bull_low, extend=extend.left, color=bullcolor, style=line.style_dashed, width=1)
    if OB_bear and showbear:
        line.delete(linebear1)
        linebear1 = line.new(x1=bar_index, y1=OB_bear_avg, x2=bar_index - 1, y2=OB_bear_avg, extend=extend.left, color=bearcolor, style=line.style_solid, width=1)
        line.delete(linebear2)
        linebear2 = line.new(x1=bar_index, y1=OB_bear_high, x2=bar_index - 1, y2=OB_bear_high, extend=extend.left, color=bearcolor, style=line.style_dashed, width=1)
        line.delete(linebear3)
        linebear3 = line.new(x1=bar_index, y1=OB_bear_low, x2=bar_index - 1, y2=OB_bear_low, extend=extend.left, color=bearcolor, style=line.style_dashed, width=1)
    alertcondition(OB_bull, title='New Bullish OB detected', message='New Bullish OB detected - This is NOT a BUY signal!')
    alertcondition(OB_bear, title='New Bearish OB detected', message='New Bearish OB detected - This is NOT a SELL signal!')
    latest_bull_high: Persistent[float] = 0.0
    latest_bull_avg: Persistent[float] = 0.0
    latest_bull_low: Persistent[float] = 0.0
    latest_bear_high: Persistent[float] = 0.0
    latest_bear_avg: Persistent[float] = 0.0
    latest_bear_low: Persistent[float] = 0.0
    if OB_bull_high > 0:
        latest_bull_high = OB_bull_high
    if OB_bull_avg > 0:
        latest_bull_avg = OB_bull_avg
    if OB_bull_low > 0:
        latest_bull_low = OB_bull_low
    if OB_bear_high > 0:
        latest_bear_high = OB_bear_high
    if OB_bear_avg > 0:
        latest_bear_avg = OB_bear_avg
    if OB_bear_low > 0:
        latest_bear_low = OB_bear_low
    plotchar(latest_bull_high, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bull High')
    plotchar(latest_bull_avg, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bull Avg')
    plotchar(latest_bull_low, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bull Low')
    plotchar(latest_bear_high, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bear High')
    plotchar(latest_bear_avg, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bear Avg')
    plotchar(latest_bear_low, char=' ', location=location.abovebar, color=color.new(color.new('#777777'), 100), size=size.tiny, title='Latest Bear Low')
    def draw_InfoPanel(_text, _x, _y, font_size):
        la_panel: Persistent[Label] = na(Label)
        label.delete(la_panel)
        la_panel = label.new(x=_x, y=_y, text=_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.new(color.new('#383838'), 5), style=label.style_label_left, textcolor=color.white, size=font_size)
        return la_panel

    info_panel_x = time_close + math.round(ta.change(time) * 100)
    info_panel_y = close
    title: str = 'LATEST ORDER BLOCKS'
    row0: str = '-----------------------------------------------------'
    row1 = ' Bullish - High: ' + string.tostring(latest_bull_high, '#.##')
    row2 = ' Bullish - Avg: ' + string.tostring(latest_bull_avg, '#.##')
    row3 = ' Bullish - Low: ' + string.tostring(latest_bull_low, '#.##')
    row4: str = '-----------------------------------------------------'
    row5 = ' Bearish - High: ' + string.tostring(latest_bear_high, '#.##')
    row6 = ' Bearish - Avg: ' + string.tostring(latest_bear_avg, '#.##')
    row7 = ' Bearish - Low: ' + string.tostring(latest_bear_low, '#.##')
    panel_text = '\n' + title + '\n' + row0 + '\n' + row1 + '\n' + row2 + '\n' + row3 + '\n' + row4 + '\n\n' + row5 + '\n' + row6 + '\n' + row7 + '\n'
    if info_pan:
        draw_InfoPanel(panel_text, info_panel_x, info_panel_y, size.normal)
    chper: Series = time - time[1]
    chper = chper[1] if ta.change(chper) > 0 else chper
    vartooltip: Persistent[str] = 'Indicator to help identifying instituational Order Blocks. Often these blocks signal the beginning of a strong move, but there is a high probability, that these prices will be revisited at a later point in time again and therefore are interesting levels to place limit orders. \nBullish Order block is the last down candle before a sequence of up candles. \nBearish Order Block is the last up candle before a sequence of down candles. \nIn the settings the number of required sequential candles can be adjusted. \nFurthermore a %-threshold can be entered which the sequential move needs to achieve in order to validate a relevant Order Block. \nChannels for the last Bullish/Bearish Block can be shown/hidden.'
    l_docu: Persistent[Label] = na(Label)
    label.delete(l_docu)
    if showdocu:
        l_docu = label.new(x=time + chper * 35, y=close, text='DOCU OB', color=color.gray, textcolor=color.white, style=label.style_label_center, xloc=xloc.bar_time, yloc=yloc.price, size=size.tiny, textalign=text.align_left, tooltip=vartooltip)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
