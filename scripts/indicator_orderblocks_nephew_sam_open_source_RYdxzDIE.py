"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, barstate, close, color, high, input, line, location, low, na,
    open, plotshape, script, shape, size, string, table, time, timeframe, xloc
)
from pynecore.types import Label, Line, Persistent


@script.indicator('Orderblocks (Nephew_Sam_)', overlay=True, max_bars_back=500, max_labels_count=100, max_lines_count=100)
def main(
    temp0=input(title='••••••••••••••••••• Fractals ••••••••••••••••••••••', defval=False),
    showFractals=input(title='Show Fractal Points ?', defval=False),
    filterFractal=input.string(title='Filter 3/5 bar fractal', defval='3', options=('3', '5')),
    temp1=input(title='••••••••••••••••••• Orderblocks •••••••••••••••••••', defval=False),
    findObType=input.string(title='Find OB after fractal break of close/HL', defval='Close', options=('Close', 'HL')),
    filterFvgs=input(title='Filter only OB that follow with FVG ?', defval=True),
    fvgDistance=input.int(3, title='Max bars between the OB and FVG', minval=1, maxval=6),
    lineHeight=input.string(title='Line Height', defval='Body', options=('Body', 'Wick')),
    delLines=input(title='Delete lines after fill ?', defval=True),
    temp3=input(title='•••••••••••••••••••• Styles ••••••••••••••••••••••••', defval=False),
    lines_style=input.string(title='Lines style', defval='Solid', options=('Solid', 'Dashed', 'Dotted')),
    line_length=input.int(5, 'Length of lines', minval=1, maxval=100),
    linesWidth=input.int(2, 'Lines Width ?', minval=1, maxval=4),
    bear_line_color=input(color.red, 'Bear OB Line color'),
    bull_line_color=input(color.blue, 'Bull OB Line color')
):
    bars_back: int = 500

    lineStyle = line.style_solid if lines_style == 'Solid' else line.style_dashed if lines_style == 'Dashed' else line.style_dotted
    def bullishImb(i = 0):
        return close[i + 1] > high[i + 2] and low[i] > high[i + 2]

    def bearishImb(i = 0):
        return close[i + 1] < low[i + 2] and high[i] < low[i + 2]

    def isRegularFractal(mode):
        ret = high < high[1] and (high[2] < high[1] or (high[2] == high[1] and high[3] < high[2])) if mode == 'Buy' else low > low[1] and (low[2] > low[1] or (low[2] == low[1] and low[3] > low[2])) if mode == 'Sell' else False
        return ret

    def isBWFractal(mode):
        ret = high < high[2] and high[1] < high[2] and (high[3] < high[2]) and (high[4] < high[2]) if mode == 'Buy' else low > low[2] and low[1] > low[2] and (low[3] > low[2]) and (low[4] > low[2]) if mode == 'Sell' else False
        return ret

    def isFractalHigh():
        return isRegularFractal('Buy') if filterFractal == '3' else isBWFractal('Buy')

    def isFractalLow():
        return isRegularFractal('Sell') if filterFractal == '3' else isBWFractal('Sell')

    def resolutionInMinutes():
        resInMinutes = timeframe.multiplier * (1.0 / 60 if timeframe.isseconds else 1.0 if timeframe.isminutes else 60.0 * 24 if timeframe.isdaily else 60.0 * 24 * 7 if timeframe.isweekly else 60.0 * 24 * 30.4375 if timeframe.ismonthly else na)
        return resInMinutes

    def f_timeFrom(_from, length, _units, i):
        _timeFrom: int = na(int)
        _unit = string.replace_all(_units, 's', '')
        _timeFrom = cast_int(time[i] + resolutionInMinutes() * 60 * 1000 * length)
        return _timeFrom

    fractal_high_val: float = 0.0
    fractal_low_val: float = 0.0
    fractal_highs: Persistent[list[float]] = array.new_float(0)
    fractal_high_times: Persistent[list[int]] = array.new_int(0)
    fractal_lows: Persistent[list[float]] = array.new_float(0)
    fractal_low_times: Persistent[list[int]] = array.new_int(0)
    if isFractalHigh():
        if filterFractal == '3':
            array.push(fractal_highs, high[1])
            array.push(fractal_high_times, time[1])
            fractal_high_val = high[1]
        else:
            array.push(fractal_highs, high[2])
            array.push(fractal_high_times, time[2])
            fractal_high_val = high[2]
    if isFractalLow():
        if filterFractal == '3':
            array.push(fractal_lows, low[1])
            array.push(fractal_low_times, time[1])
            fractal_low_val = low[1]
        else:
            array.push(fractal_lows, low[2])
            array.push(fractal_low_times, time[2])
            fractal_low_val = low[2]
    line1: Persistent[list[Line]] = array.new_line()
    line2: Persistent[list[Line]] = array.new_line()
    line3: Persistent[list[Line]] = array.new_line()
    line4: Persistent[list[Line]] = array.new_line()
    label1: Persistent[list[Label]] = array.new_label()
    label2: Persistent[list[Label]] = array.new_label()
    if array.size(fractal_lows) > 0:
        for i in pine_range(array.size(fractal_lows) - 1, 0, 1):
            if (close if findObType == 'Close' else low) < array.get(fractal_lows, i):
                idx: int = 0
                max = low
                gapIndex: int = 0
                for k in pine_range(0, bars_back, 1):
                    bearishGap = close[k + 1] < low[k + 2] and high[k] < low[k + 2]
                    if time[k] < array.get(fractal_low_times, i):
                        break
                    if close[k] > open[k] and high[k] > max:
                        idx = k
                        max = high[k]
                    if bearishGap and high[k] > max:
                        gapIndex = k + 2
                _filterFvg = gapIndex > 0 and idx - gapIndex >= 0 and (idx - gapIndex <= fvgDistance) if filterFvgs else True
                if idx != 0 and _filterFvg:
                    TimeTo = f_timeFrom('bar', line_length, 'chart', idx)
                    loc = open[idx] if lineHeight == 'Body' else low[idx]
                    array.push(line1, line.new(x1=time[idx], y1=high[idx], x2=TimeTo, y2=high[idx], xloc=xloc.bar_time, style=lineStyle, color=bear_line_color, width=linesWidth))
                    array.push(line2, line.new(x1=time[idx], y1=loc, x2=TimeTo, y2=loc, xloc=xloc.bar_time, style=lineStyle, color=bear_line_color, width=linesWidth))
                array.remove(fractal_lows, i)
                array.remove(fractal_low_times, i)
    if array.size(fractal_highs) > 0:
        for i in pine_range(array.size(fractal_highs) - 1, 0, 1):
            if (close if findObType == 'Close' else high) > array.get(fractal_highs, i):
                idx: int = 0
                min = low
                gapIndex: int = 0
                for k in pine_range(0, bars_back, 1):
                    bullishGap = close[k + 1] > high[k + 2] and low[k] > high[k + 2]
                    if time[k] < array.get(fractal_high_times, i):
                        break
                    if close[k] < open[k] and low[k] < min:
                        idx = k
                        min = low[k]
                    if bullishGap:
                        gapIndex = k + 2
                _filterFvg = gapIndex > 0 and idx - gapIndex >= 0 and (idx - gapIndex <= fvgDistance) if filterFvgs else True
                if idx != 0 and _filterFvg:
                    TimeTo = f_timeFrom('bar', line_length, 'chart', idx)
                    loc = open[idx] if lineHeight == 'Body' else high[idx]
                    array.push(line3, line.new(x1=time[idx], y1=low[idx], x2=TimeTo, y2=low[idx], xloc=xloc.bar_time, style=lineStyle, color=bull_line_color, width=linesWidth))
                    array.push(line4, line.new(x1=time[idx], y1=loc, x2=TimeTo, y2=loc, xloc=xloc.bar_time, style=lineStyle, color=bull_line_color, width=linesWidth))
                array.remove(fractal_highs, i)
                array.remove(fractal_high_times, i)
    if array.size(line1) > 0:
        for i in pine_range(array.size(line1) - 1, 0, 1):
            if high >= line.get_y1(array.get(line1, i)) and high >= line.get_y1(array.get(line2, i)):
                if delLines:
                    line.delete(array.get(line1, i))
                    line.delete(array.get(line2, i))
                array.remove(line1, i)
                array.remove(line2, i)
    if array.size(line3) > 0:
        for i in pine_range(array.size(line3) - 1, 0, 1):
            if low <= line.get_y1(array.get(line3, i)) and low <= line.get_y1(array.get(line4, i)):
                if delLines:
                    line.delete(array.get(line3, i))
                    line.delete(array.get(line4, i))
                array.remove(line3, i)
                array.remove(line4, i)
    isFractalHigh_1 = isFractalHigh()
    plotshape(showFractals and isFractalHigh_1, title='Fractal High', style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), offset=-1 if filterFractal == '3' else -2, size=size.auto)
    isFractalLow_1 = isFractalLow()
    plotshape(showFractals and isFractalLow_1, title='Fractal Low', style=shape.triangleup, location=location.belowbar, color=color.new(color.blue, 0), offset=-1 if filterFractal == '3' else -2, size=size.auto)
    if barstate.islast:
        _table = table.new('bottom_left', 1, 2)
        table.cell(_table, 0, 0, text='@Nephew_Sam_', text_size=size.small, text_color=color.new(color.gray, 50))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
