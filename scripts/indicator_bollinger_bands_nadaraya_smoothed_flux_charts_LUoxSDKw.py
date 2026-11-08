"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, close, color, display, fill, high,
    input, line, location, low, math, matrix, na, plot, plotshape, script, shape, size, syminfo,
    ta
)
from pynecore.types import Color, Matrix, NA, Persistent, Series


@udt
class pallete:
    bear: Color = na(Color)
    bull: Color = na(Color)
    shade1_bear: Color = na(Color)
    shade1_bull: Color = na(Color)
    shade2_bear: Color = na(Color)
    shade2_bull: Color = na(Color)


group_smoothing: str = 'smoothing'
group_boll: str = 'Bollinger Bands Settings (Short, Medium, Long)'
group_graphics: str = 'Plots and Labels'
grp: str = 'Color Theme'
grp_n: str = 'Notifications'
bollinger_bands_lvl1: bool = True
bollinger_bands_lvl2: bool = True


@script.indicator('Bollinger Bands (Nadaraya Smoothed) | Flux Charts', overlay=True, max_lines_count=500, max_bars_back=500)
def main(
    h=input.float(6, 'Smoothing Factor', step=0.5, tooltip='The bandwith(h) used in the kernel of the Nadaraya-Watson estimator function.', group=group_smoothing),
    repaint=input.bool(False, 'Repaint Smoothing', tooltip='This setting allows for repainting of the estimation', group=group_smoothing),
    short_period=input.int(20, 'Period', inline='short', group=group_boll),
    short_stdev=input.float(3, 'Deviation', inline='short', group=group_boll),
    med_period=input.int(75, 'Period', inline='med', group=group_boll),
    med_stdev=input.float(4, 'Deviation', inline='med', group=group_boll),
    long_period=input.int(100, ' Period', inline='long', group=group_boll),
    long_stdev=input.float(4.25, 'Deviation', inline='long', group=group_boll),
    label_src=input.string('Close', 'Label Source', options=('Pivots', 'Close', 'High/Low'), group=group_graphics, tooltip='The source used to determine if price is outside of the Bollinger Bands. The Pivots setting has a four bar delay.'),
    labels=input.bool(True, 'Labels', inline='label', group=group_graphics, display=display.none),
    plots=input.bool(True, 'Plot Lines', group=group_graphics, display=display.none),
    plot_thickness=input.int(2, 'Line Width', group=group_graphics, display=display.none),
    bands_lvl1=input.bool(True, 'Level 1 Bands', inline='bands', group=group_graphics),
    bands_lvl2=input.bool(True, 'Level 2 Bands', inline='bands', group=group_graphics),
    pallete_bear=input.color(color.red, 'Bearish', inline='theme', group=grp, display=display.none),
    pallete_bull=input.color(color.green, 'Bullish', inline='theme', group=grp, display=display.none),
    alpha1=input.float(0.9, 'Transparency: Level 1 ', minval=0.1, maxval=1, inline='alpha', step=0.1, display=display.none),
    alpha2=input.float(0.85, 'Level 2', minval=0.1, maxval=1, inline='alpha', step=0.1, display=display.none),
    notifs=input.bool(False, 'Band Breaks', group=grp_n, tooltip='Recieve notifications when price goes above or below the first level.', display=display.none)
):
    sens: int = 4
    def create_pallete(bear: Color, bull: Color, alpha1: float = 1, alpha2: float = 2):
        shade1: float = 100 * alpha1
        shade2: float = 100 * alpha2
        shade1_bear: Color = color.new(bear, shade1)
        shade1_bull: Color = color.new(bull, shade1)
        shade2_bear: Color = color.new(bear, shade2)
        shade2_bull: Color = color.new(bull, shade2)
        return pallete(bear, bull, shade1_bear, shade1_bull, shade2_bear, shade2_bull)

    theme = create_pallete(pallete_bear, pallete_bull, alpha1, alpha2)
    tp: float = (high + low + close) / 3
    n_first: int = 20
    n_second: int = 75
    n_third: int = 100
    def guass_w(x, h):
        return math.exp(-1 * (x * x / (2 * h * h)))

    def bollingers(n, factor = 3):
        bolu = ta.sma(tp, n) + factor * ta.stdev(tp, n)
        bold = ta.sma(tp, n) - factor * ta.stdev(tp, n)
        return (bolu, bold)

    BOLU_FIRST, BOLD_FIRST = bollingers(n_first, short_stdev)
    BOL_FIRST_GAP: float = BOLU_FIRST - BOLD_FIRST
    BOLU_SECOND, BOLD_SECOND = bollingers(n_second, short_stdev)
    BOL_SECOND_GAP: float = BOLU_SECOND - BOLD_SECOND
    BOLU_THIRD, BOLD_THIRD = bollingers(n_third, med_stdev)
    BOL_THIRD_GAP: float = BOLU_THIRD - BOLD_THIRD
    BOLU_FOURTH, BOLD_FOURTH = bollingers(n_third, long_stdev)
    pivots: Persistent[list[float]] = array.new_float()
    pivots2: Persistent[list[float]] = array.new_float()
    pivot_rad = sens
    pivot_high: float = ta.pivothigh(high, pivot_rad, pivot_rad)
    pivot_low: float = ta.pivotlow(low, pivot_rad, pivot_rad)
    def add_cols(mat, h_n = 1):
        sum_array: list[float] = array.new_float()
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(matrix.rows(mat) - 1):
            i = __loop_0__.value
            array.push(sum_array, array.sum(matrix.row(mat, i)) / h_n)
        return sum_array

    def nadaraya(src: Series, color__ren__):
        smoothed: list[float] = array.new_float()
        if barstate.islast and repaint:
            for i in pine_range(0, 499, 1):
                sum: float = 0.0
                gk: list[float] = array.new_float()
                for y in pine_range(0, 499, 1):
                    array.push(gk, guass_w(y - i, h))
                gk_sum = array.sum(gk)
                for y in pine_range(0, 499, 1):
                    sum = sum + src[y] * (array.get(gk, y) / gk_sum)
                array.push(smoothed, sum)
                if i % 2 == 0 and i != 0:
                    line.new(bar_index[i - 1], array.get(smoothed, i - 1), bar_index[i], array.get(smoothed, i), color=color__ren__, width=2)
        return smoothed

    def running_nadaraya(src: Series, n):
        gk: Persistent[list[float]] = array.new_float(0)
        gk_sum: Persistent[float] = 0.0
        src_matrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
        smoothed: float = 0.0
        if barstate.isfirst and (not repaint):
            for i in pine_range(0, n, 1):
                array.push(gk, guass_w(i, h))
            gk_sum = array.sum(gk)
        if not repaint:
            for i in pine_range(n, 0, 1):
                smoothed = smoothed + src[i] * (array.get(gk, i) / gk_sum)
        return smoothed

    n: int = 499
    smoothed_bolu_1: Series = running_nadaraya(BOLU_FIRST, n)
    smoothed_bold_1: Series = running_nadaraya(BOLD_FIRST, n)
    smoothed_bolu_2 = running_nadaraya(BOLU_SECOND, n)
    smoothed_bold_2 = running_nadaraya(BOLD_SECOND, n)
    smoothed_bolu_3 = running_nadaraya(BOLU_THIRD, n)
    smoothed_bold_3 = running_nadaraya(BOLD_THIRD, n)
    smoothed_bolu_4 = running_nadaraya(BOLU_FOURTH, n)
    smoothed_bold_4 = running_nadaraya(BOLD_FOURTH, n)
    BOLU_FIRST_PLOT = plot(smoothed_bolu_1, display=display.none)
    BOLD_FIRST_PLOT = plot(smoothed_bold_1, display=display.none)
    BOLU_SECOND_PLOT = plot(smoothed_bolu_2, display=display.none)
    BOLD_SECOND_PLOT = plot(smoothed_bold_2, display=display.none)
    BOLU_THIRD_PLOT = plot(smoothed_bolu_3, display=display.none)
    BOLD_THIRD_PLOT = plot(smoothed_bold_3, display=display.none)
    BOLU_FOURTH_PLOT = plot(smoothed_bolu_4, display=display.none)
    BOLD_FOURTH_PLOT = plot(smoothed_bold_4, display=display.none)
    if repaint:
        nadaraya(BOLU_FIRST, theme.bear)
        nadaraya(BOLD_FIRST, theme.bull)
    spacing = ta.atr(300)
    band_test_upper_source: Series = pivot_high if label_src == 'Pivots' else close if label_src == 'Close' else high
    band_test_lower_source: Series = pivot_low if label_src == 'Pivots' else close if label_src == 'Close' else low
    offset = sens if label_src == 'Pivots' else 0
    upper_band_test = band_test_upper_source + spacing * 1.01 if band_test_upper_source >= smoothed_bolu_1[offset] and (band_test_upper_source[1] <= smoothed_bolu_1[offset] or na(band_test_upper_source[1])) and (not repaint) else na
    lower_band_test = band_test_lower_source - spacing * 1.01 if band_test_lower_source <= smoothed_bold_1[offset] and (band_test_lower_source[1] >= smoothed_bold_1[offset] or na(band_test_upper_source[1])) and (not repaint) else na
    if notifs and close > smoothed_bolu_1:
        alert('Upper Band Crossed on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    elif notifs and close < smoothed_bold_1:
        alert('Lower Band Crossed on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    plotshape(upper_band_test if labels else na, style=shape.triangledown, location=location.absolute, color=theme.bear, offset=-1 * offset, size=size.tiny)
    plotshape(lower_band_test if labels else na, style=shape.triangleup, location=location.absolute, color=theme.bull, offset=-1 * offset, size=size.tiny)
    plot(smoothed_bolu_1 if not repaint and plots else na, linewidth=math.max(1, plot_thickness), color=theme.bear)
    plot(smoothed_bold_1 if not repaint and plots else na, linewidth=math.max(1, plot_thickness), color=theme.bull)
    fill(BOLU_FIRST_PLOT, BOLU_SECOND_PLOT, theme.shade1_bear, display=display.all if bands_lvl1 else display.none)
    fill(BOLD_FIRST_PLOT, BOLD_SECOND_PLOT, theme.shade1_bull, display=display.all if bands_lvl1 else display.none)
    fill(BOLU_SECOND_PLOT, BOLU_THIRD_PLOT, theme.shade2_bear, display=display.all if bands_lvl2 else display.none)
    fill(BOLD_SECOND_PLOT, BOLD_THIRD_PLOT, theme.shade2_bull, display=display.all if bands_lvl2 else display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
