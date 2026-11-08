"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    barstate, chart, close, color, format, high, input, location, low, na,
    plotcandle, plotshape, position, script, shape, size, string, ta, table
)
from pynecore.types import Persistent, Series


@script.indicator("Triangular Hull Moving Average + Volatility [BigBeluga]", "THMA + Volatility [BigBeluga]", overlay=True)
def main(
    len_=input.int(40, "Length"),
    source: Series[float] = input.source(close, "Source"),
    volat=input.bool(True, "Volatility", inline="vola"),
    len_vol=input.int(15, "", inline="vola"),
    color_u=input.color(color.new('#16E5A0'), "", inline="colors"),
    color_d=input.color(color.new('#741DDD'), "", inline="colors")
):
    volatility: float = ta.hma(high - low, len_vol)
    trend: Persistent[str] = ""

    vv = ta.percentile_nearest_rank(volatility, 1000, 100)
    vol = volatility / vv

    def thma(_src, _length):
        return ta.wma(ta.wma(_src, _length / 3) * 3 - ta.wma(_src, _length / 2) - ta.wma(_src, _length), _length)

    thma__global__: Series[float] = thma(source, len_)
    thma1: float = thma__global__[2]

    signal_up: bool = ta.crossover(thma__global__, thma1)
    signal_dn: bool = ta.crossunder(thma__global__, thma1)

    if signal_up:
        trend = "🢁"
    elif signal_dn:
        trend = "🢃"

    color__ren__ = color_u if thma__global__ > thma1 else color_d
    color1 = color__ren__

    atr = ta.atr(200)

    plotcandle(thma__global__, thma__global__ + volatility, thma1 - volatility, thma1, '', color.new(color1, 40 if volat else 0), color.new(color1, 40 if volat else 100), bordercolor=color.new(color1, 0))

    plotshape(thma1 - atr if signal_up else na, 'Up', shape.triangleup, location.absolute, color=color.new(color__ren__, 60), size=size.small, force_overlay=True)
    plotshape(thma1 - atr if signal_up else na, 'Up', shape.triangleup, location.absolute, color=color.new(color__ren__, 0), size=size.tiny, force_overlay=True)

    plotshape(thma1 + atr if signal_dn else na, 'Dn', shape.triangledown, location.absolute, color=color.new(color__ren__, 60), size=size.small, force_overlay=True)
    plotshape(thma1 + atr if signal_dn else na, 'Dn', shape.triangledown, location.absolute, color=color.new(color__ren__, 0), size=size.tiny, force_overlay=True)

    if barstate.islast:
        dash = table.new(position.bottom_right, 10, 10, bgcolor=color.new(chart.fg_color, 90), border_color=chart.bg_color, border_width=5)
        method_call('cell', dash, 0, 0, 'Trend: ' + trend, text_color=color_d if trend == '🢃' else color_u)
        method_call('cell', dash, 0, 1, 'Volatility: ' + string.tostring(vol * 100, format.percent), text_color=chart.fg_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
