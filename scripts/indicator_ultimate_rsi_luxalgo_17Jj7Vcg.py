"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import chart, close, color, fill, hline, input, math, na, plot, script, ta
from pynecore.types import Series


@script.indicator('Ultimate RSI [LuxAlgo]', 'LuxAlgo - Ultimate RSI')
def main(
    length=input.int(14, minval=2),
    smoType1=input.string('RMA', 'Method', options=('EMA', 'SMA', 'RMA', 'TMA')),
    src: Series[float] = input(close, 'Source'),
    arsiCss=input(color.silver, 'Color', inline='rsicss'),
    autoCss=input(True, 'Auto', inline='rsicss'),
    smooth=input.int(14, minval=1, group='Signal Line'),
    smoType2=input.string('EMA', 'Method', options=('EMA', 'SMA', 'RMA', 'TMA'), group='Signal Line'),
    signalCss=input(color.new('#FF5D00'), 'Color', group='Signal Line'),
    obValue=input.float(80, 'Overbought', inline='ob', group='OB/OS Style'),
    obCss=input(color.new('#089981'), '', inline='ob', group='OB/OS Style'),
    obAreaCss=input(color.new(color.new('#089981'), 80), '', inline='ob', group='OB/OS Style'),
    osValue=input.float(20, 'Oversold    ', inline='os', group='OB/OS Style'),
    osCss=input(color.new('#F23645'), '', inline='os', group='OB/OS Style'),
    osAreaCss=input(color.new(color.new('#F23645'), 80), '', inline='os', group='OB/OS Style')
):
    def ma(x, len, maType):
        __block_result__ = na
        __switch__ = maType
        if __switch__ == 'EMA':
            __block_result__ = ta.ema(x, len)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(x, len)
        elif __switch__ == 'RMA':
            __block_result__ = ta.rma(x, len)
        elif __switch__ == 'TMA':
            __block_result__ = ta.sma(ta.sma(x, len), len)
        return __block_result__

    upper: Series = ta.highest(src, length)
    lower: Series = ta.lowest(src, length)
    r = upper - lower
    d = src - src[1]
    diff = r if upper > upper[1] else -r if lower < lower[1] else d
    num = ma(diff, length, smoType1)
    den = ma(math.abs(diff), length, smoType1)
    arsi = num / den * 50 + 50
    signal = ma(arsi, smooth, smoType2)
    plot_rsi = plot(arsi, 'Ultimate RSI', obCss if arsi > obValue else osCss if arsi < osValue else chart.fg_color if autoCss else arsiCss)
    plot(signal, 'Signal Line', signalCss)
    plot_up = plot(obValue, color=na, editable=False)
    plot_avg = plot(50, color=na, editable=False)
    plot_dn = plot(osValue, color=na, editable=False)
    fill(plot_rsi, plot_up, obAreaCss if arsi > obValue else na)
    fill(plot_dn, plot_rsi, osAreaCss if arsi < osValue else na)
    fill(plot_rsi, plot_avg, obValue, 50, obAreaCss, color.new(chart.bg_color, 100))
    fill(plot_avg, plot_rsi, 50, osValue, color.new(chart.bg_color, 100), osAreaCss)
    hline(obValue, 'Overbought')
    hline(50, 'Midline')
    hline(osValue, 'Oversold')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
