"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, barmerge, close, color, extend, fill, high, input,
    line, location, low, math, na, open, plot, plotshape, request, script, shape, size, syminfo,
    time_close, xloc
)
from pynecore.types import Line, Persistent, Series

tip1: str = 'Indicator to help identify instituational Order Blocks (OB). OBs often signal the beginning of a strong move. There is a high probability that OB price levels will be revisited in the future and are interesting levels to place limit orders. Bullish Order block is the last down candle before a sequence of up candles. Bearish Order Block is the last up candle before a sequence of down candles.'
tip3: str = 'Required number of subsequent candles in the same direction to identify Order Block'
tip4: str = 'Measured from from potential OB close to close of first candle in sequence'


@script.indicator('Order Block Finder', overlay=True, na_bool=True)
def main(
    dummy=input.bool(True, 'Hover over ( ! ) for documentation', tooltip=tip1),
    colors=input.string('LIGHT', 'Color Scheme', options=('DARK', 'LIGHT')),
    periods=input.int(7, 'Relevant Periods to identify OB', tooltip=tip3),
    threshold=input.float(0.0, 'Min. Percent move for valid OB', step=0.1, tooltip=tip4),
    bull_channels=input(2, 'Number of Bullish Channels to show'),
    bear_channels=input(2, 'Number of Bearish Channels to show')
):
    tip2: str = '!Experimental!\nFind Order Blocks from different timeframes. Channels prices are accurate, but arrow position is not. Most useful when selecting a timeframe higher than the chart.'
    res: str = ''
    copen: Series
    chigh: Series
    clow: Series
    cclose: Series
    copen, chigh, clow, cclose = request.security(syminfo.tickerid, res, (open, high, low, close), barmerge.gaps_on, barmerge.lookahead_off)
    ob_period = periods + 1
    absmove = math.abs(cclose[ob_period] - cclose[1]) / cclose[ob_period] * 100
    relmove = absmove >= threshold
    bullcolor = color.white if colors == 'DARK' else color.green
    bearcolor = color.blue if colors == 'DARK' else color.red
    bullishOB = cclose[ob_period] < copen[ob_period]
    upcandles: int = 0
    for i in pine_range(1, periods, 1):
        upcandles = upcandles + (1 if cclose[i] > copen[i] else 0)
    OB_bull = bullishOB and upcandles == periods and relmove
    OB_bull_chigh = chigh[ob_period] if OB_bull else na
    OB_bull_clow = clow[ob_period] if OB_bull else na
    OB_bull_avg = (OB_bull_chigh + OB_bull_clow) / 2
    bearishOB = cclose[ob_period] > copen[ob_period]
    downcandles: int = 0
    for i in pine_range(1, periods, 1):
        downcandles = downcandles + (1 if cclose[i] < copen[i] else 0)
    OB_bear = bearishOB and downcandles == periods and relmove
    OB_bear_chigh = chigh[ob_period] if OB_bear else na
    OB_bear_clow = clow[ob_period] if OB_bear else na
    OB_bear_avg = (OB_bear_clow + OB_bear_chigh) / 2
    plotshape(OB_bull, title='Bullish OB', style=shape.triangleup, color=bullcolor, textcolor=bullcolor, size=size.tiny, location=location.belowbar, offset=-ob_period, text='Bull')
    bull1 = plot(OB_bull_chigh, title='Bullish OB High', style=plot.style_linebr, color=bullcolor, offset=-ob_period, linewidth=2)
    bull2 = plot(OB_bull_clow, title='Bullish OB Low', style=plot.style_linebr, color=bullcolor, offset=-ob_period, linewidth=2)
    fill(bull1, bull2, color=color.new(bullcolor, 50), title='Bullish OB fill')
    plotshape(OB_bull_avg, title='Bullish OB Average', style=shape.cross, color=bullcolor, size=size.small, location=location.absolute, offset=-ob_period)
    plotshape(OB_bear, title='Bearish OB', style=shape.triangledown, color=bearcolor, textcolor=bearcolor, size=size.tiny, location=location.abovebar, offset=-ob_period, text='Bear')
    bear1 = plot(OB_bear_clow, title='Bearish OB Low', style=plot.style_linebr, color=bearcolor, offset=-ob_period, linewidth=2)
    bear2 = plot(OB_bear_chigh, title='Bearish OB High', style=plot.style_linebr, color=bearcolor, offset=-ob_period, linewidth=2)
    fill(bear1, bear2, color=color.new(bearcolor, 50), title='Bearish OB fill')
    plotshape(OB_bear_avg, title='Bearish OB Average', style=shape.cross, color=bearcolor, size=size.small, location=location.absolute, offset=-ob_period)
    LineBullAvg: Persistent[list[Line]] = array.new_line()
    LineBullHigh: Persistent[list[Line]] = array.new_line()
    LineBullLow: Persistent[list[Line]] = array.new_line()
    LineBearAvg: Persistent[list[Line]] = array.new_line()
    LineBearHigh: Persistent[list[Line]] = array.new_line()
    LineBearLow: Persistent[list[Line]] = array.new_line()
    sync: Series = time_close(res)
    if OB_bull and bull_channels > 0:
        if array.size(LineBullAvg) == bull_channels:
            line.delete(array.get(LineBullAvg, 0))
            array.remove(LineBullAvg, 0)
            line.delete(array.get(LineBullHigh, 0))
            array.remove(LineBullHigh, 0)
            line.delete(array.get(LineBullLow, 0))
            array.remove(LineBullLow, 0)
        array.push(LineBullAvg, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bull_avg, x2=sync[1], y2=OB_bull_avg, extend=extend.left, color=bullcolor, style=line.style_solid, width=1))
        array.push(LineBullHigh, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bull_chigh, x2=sync[1], y2=OB_bull_chigh, extend=extend.left, color=bullcolor, style=line.style_dashed, width=1))
        array.push(LineBullLow, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bull_clow, x2=sync[1], y2=OB_bull_clow, extend=extend.left, color=bullcolor, style=line.style_dashed, width=1))
    if OB_bear and bear_channels > 0:
        if array.size(LineBearAvg) == bear_channels:
            line.delete(array.get(LineBearAvg, 0))
            array.remove(LineBearAvg, 0)
            line.delete(array.get(LineBearHigh, 0))
            array.remove(LineBearHigh, 0)
            line.delete(array.get(LineBearLow, 0))
            array.remove(LineBearLow, 0)
        array.push(LineBearAvg, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bear_avg, x2=sync[1], y2=OB_bear_avg, extend=extend.left, color=bearcolor, style=line.style_solid, width=1))
        array.push(LineBearHigh, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bear_chigh, x2=sync[1], y2=OB_bear_chigh, extend=extend.left, color=bearcolor, style=line.style_dashed, width=1))
        array.push(LineBearLow, line.new(x1=sync, xloc=xloc.bar_time, y1=OB_bear_clow, x2=sync[1], y2=OB_bear_clow, extend=extend.left, color=bearcolor, style=line.style_dashed, width=1))
    alertcondition(OB_bull, title='New Bullish OB detected', message='New Bullish OB detected - This is NOT a BUY signal!')
    alertcondition(OB_bear, title='New Bearish OB detected', message='New Bearish OB detected - This is NOT a SELL signal!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
