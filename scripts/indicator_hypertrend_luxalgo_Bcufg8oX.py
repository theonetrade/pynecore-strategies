"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import chart, close, color, fill, input, math, na, nz, plot, script, ta
from pynecore.types import Color, Persistent, PersistentSeries


@script.indicator('HyperTrend [LuxAlgo]', 'LuxAlgo - HyperTrend', overlay=True)
def main(
    mult=input.float(5, 'Multiplicative Factor', minval=0),
    slope=input.float(14, 'Slope', minval=0),
    __input_2__=input.float(80, 'Width %', minval=0, maxval=100),
    bullCss=input.color(color.teal, 'Average Color', inline='avg', group='Style'),
    bearCss=input.color(color.red, '', inline='avg', group='Style'),
    area=input.string('Gradient', 'Area', options=('Gradient', 'Solid'), group='Style'),
    upperCss=input.color(color.new(color.red, 70), 'Upper Area', group='Style'),
    lowerCss=input.color(color.new(color.teal, 70), 'Lower Area', group='Style')
):
    width = __input_2__ / 100
    upper: Persistent[float] = na(float)
    lower: Persistent[float] = na(float)
    avg: PersistentSeries[float] = close
    hold: Persistent[float] = 0.0
    os: PersistentSeries[float] = 1.0
    atr = nz(ta.atr(200)) * mult
    avg = math.avg(close, avg) if math.abs(close - avg) > atr else avg + os * (hold / mult / slope)
    os = math.sign(avg - avg[1])
    hold = atr if os != os[1] else hold
    upper = avg + width * hold
    lower = avg - width * hold
    css = bullCss if os == 1 else bearCss
    plot_upper = plot(upper, 'Upper', na)
    plot_avg = plot(avg, 'Average', na if os != os[1] else css)
    plot_lower = plot(lower, 'Lower', na)
    upper_topcol: Persistent[Color] = na(Color)
    upper_btmcol: Persistent[Color] = na(Color)
    lower_topcol: Persistent[Color] = na(Color)
    lower_btmcol: Persistent[Color] = na(Color)
    if area == 'Gradient':
        upper_topcol = upperCss
        upper_btmcol = color.new(chart.bg_color, 100)
        lower_topcol = color.new(chart.bg_color, 100)
        lower_btmcol = lowerCss
    else:
        upper_topcol = upperCss
        upper_btmcol = upperCss
        lower_topcol = lowerCss
        lower_btmcol = lowerCss
    fill(plot_upper, plot_avg, top_color=na if os != os[1] else upper_topcol, bottom_color=na if os != os[1] else upper_btmcol, top_value=upper, bottom_value=avg)
    fill(plot_avg, plot_lower, top_color=na if os != os[1] else lower_topcol, bottom_color=na if os != os[1] else lower_btmcol, top_value=avg, bottom_value=lower)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
