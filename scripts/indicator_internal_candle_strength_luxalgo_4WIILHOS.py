"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, format, high, input, line,
    low, math, na, open, plotcandle, position, request, script, string, syminfo, ta, table
)
from pynecore.types import Color, Persistent, Table


@script.indicator('Internal Candle Strength [LuxAlgo]', 'LuxAlgo - Internal Candle Strength', overlay=True, max_lines_count=500, max_boxes_count=500)
def main(
    timeframeInput=input.timeframe('1', 'Timeframe'),
    sizeInput=input(20.0, 'Row Size', inline='size'),
    autoInput=input.bool(True, 'Auto', inline='size')
):
    t_able: Persistent[Table] = table.new(position.bottom_right, 2, 2, bgcolor=color.new('#1E222D'), border_color=color.new('#373A46'), border_width=1, frame_color=color.new('#373A46'), frame_width=1)

    def ohlc():
        return (open, high, low, close)

    volatility = math.round_to_mintick(0.1 * ta.atr(200))
    parsedSize = volatility if autoInput else sizeInput
    n = bar_index
    idx = math.max(math.round((high - low) / parsedSize), 1)
    o, h, l, c = request.security_lower_tf(syminfo.tickerid, timeframeInput, ohlc())

    min = low
    max = low
    avg: float = na(float)
    css: Color = na(Color)

    for i in pine_range(0, idx - 1):
        max += (high - low) / idx
        num: list[float] = array.new_float()
        den: list[float] = array.new_float()

        for index, value in enumerate(o):
            if array.get(h, index) > min and array.get(l, index) < max:
                diff = array.get(c, index) - array.get(o, index)

                array.push(num, diff)
                array.push(den, math.abs(diff))

        strength = 50 * (array.sum(num) / array.sum(den)) + 50
        css = color.from_gradient(strength, 0, 100, color.red, color.teal)

        box.new(n, max, n + 1, min, text=string.tostring(strength, format.percent), text_color=css, bgcolor=color.new(color.new('#5D606B'), 80), border_color=na)

        line.new(n, min, n + 1, min, color=css)

        min = max

    line.new(n, min, n + 1, min, color=css)

    plotcandle(open, math.max(close, open), math.min(close, open), open, bordercolor=color.new('#00000000'), color=color.new('#00000000'), wickcolor=color.teal if close > open else color.red)

    if barstate.islast:
        table.cell(t_able, 0, 0, 'Current Row Size', text_color=color.new(color.white, 50))
        table.cell(t_able, 0, 1, 'Optimal Row Size', text_color=color.new(color.white, 50))
        table.cell(t_able, 1, 0, string.tostring(parsedSize), text_color=color.new(color.white, 50))
        table.cell(t_able, 1, 1, string.tostring(volatility), text_color=color.new(color.white, 50))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
