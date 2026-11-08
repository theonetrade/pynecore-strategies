"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, close, color, display, fill, high, hline, input, label,
    line, location, low, na, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import NA, Persistent, Series


@udt
class level:
    issupport: bool = na(bool)
    lvl: float = na(float)
    start: int = na(int)


@script.indicator(title="MACD Support and Resistance [ChartPrime]", shorttitle="MACD S/R [ChartPrime]")
def main(
    fast_length=input(title="Fast Length", defval=12),
    slow_length=input(title="Slow Length", defval=26),
    src: Series[float] = input(title="Source", defval=close),
    signal_length=input.int(title="Signal Smoothing", minval=1, maxval=50, defval=9, display=display.data_window),
    sma_source=input.string(title="Oscillator MA Type", defval="EMA", options=("SMA", "EMA"), display=display.data_window),
    sma_signal=input.string(title="Signal Line MA Type", defval="EMA", options=("SMA", "EMA"), display=display.data_window),
    col_up=input.color(color.new('#2962FF'), "", inline="color"),
    col_dn=input.color(color.new('#FF6D00'), "", inline="color")
):
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)

    macd_col = col_up if macd > signal else col_dn

    s_r_levels: Persistent[list[level]] = array.new(0, NA(level))

    if ta.crossunder(macd, signal):
        max: list[float] = array.new_float()

        for i in pine_range(0, 5):
            h = high[i]
            array.push(max, h)

        for i in pine_range(0, 5):
            h = high[i]
            if h == array.max(max):
                sr: level = level(False, array.max(max), bar_index - i)
                array.push(s_r_levels, sr)

    if ta.crossover(macd, signal):
        min: list[float] = array.new_float()

        for i in pine_range(0, 5):
            l = low[i]
            array.push(min, l)

        for i in pine_range(0, 5):
            l = low[i]
            if l == array.min(min):
                sr: level = level(True, array.min(min), bar_index - i)
                array.push(s_r_levels, sr)

    if array.size(s_r_levels) > 20:
        array.shift(s_r_levels)

    if array.size(s_r_levels) > 0:
        __loop_1__ = pine_loop(0)
        while __loop_1__.step(array.size(s_r_levels) - 1):
            i = __loop_1__.value
            sr = array.get(s_r_levels, i)
            start = sr.start
            is_sup = sr.issupport
            level_ = sr.lvl

            if bar_index > start and is_sup and (low < level_):
                array.remove(s_r_levels, array.indexof(s_r_levels, sr))

            if bar_index > start and (not is_sup) and (high > level_):
                array.remove(s_r_levels, array.indexof(s_r_levels, sr))

        for sr in s_r_levels:
            start: int = sr.start
            is_sup: bool = sr.issupport
            level_: float = sr.lvl

            col = col_up if is_sup else col_dn

            line.new(start, level_, bar_index, level_, color=col, force_overlay=True)

            label.new(start, level_, '', style=label.style_diamond, color=col, force_overlay=True, size=size.tiny)
            label.delete(inline_series(label.new(bar_index, level_, string.tostring(level_), style=label.style_label_left, color=col, force_overlay=True, size=size.small), 1))

    hline(0, 'Zero Line', color=color.new(color.new('#787B86'), 30))

    pm = plot(macd, title='MACD', color=macd_col, display=display.none)
    ps = plot(signal, title='Signal', color=macd_col, linewidth=2)

    fill(pm, ps, color.new(macd_col, 70))

    plotshape(signal if ta.crossover(macd, signal) else NA(float), 'Macd UP', style=shape.diamond, location=location.absolute, size=size.tiny, color=macd_col)
    plotshape(signal if ta.crossunder(macd, signal) else NA(float), 'Macd DN', style=shape.diamond, location=location.absolute, size=size.tiny, color=macd_col)

    plot(ta.highest(macd, 100), 'Local high', color=na if bar_index % 5 == 0 or bar_index % 4 == 0 or bar_index % 3 == 0 else color.new(color.new('#787B86'), 30))
    plot(ta.lowest(macd, 100), 'Local Low', color=na if bar_index % 5 == 0 or bar_index % 4 == 0 or bar_index % 3 == 0 else color.new(color.new('#787B86'), 30))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
