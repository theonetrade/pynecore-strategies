"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.lib import (
    array, bar_index, barcolor, close, color, display, fill, hline, input,
    line, linefill, math, matrix, na, nz, plot, script, ta
)
from pynecore.types import Color, Line, Matrix, NA, Persistent, PersistentSeries, Series

settings: str = 'Settings'
style: str = 'Style'


@script.indicator('Momentum Ghost Machine [ChartPrime]', overlay=False, explicit_plot_zorder=True)
def main(
    source: Series[float] = input.source(close, 'Source', group=settings),
    momentum_length=input.int(50, 'Momentum Length', minval=1, group=settings),
    momentum_smoothing=input.float(50, 'Momentum Smoothing', tooltip='Adjust the level of smoothing for the momentum length. The longer the momentum length the more you can smooth it.', minval=1, group=settings),
    post_smoothing=input.int(4, 'Post Smoothing', minval=1, tooltip='Adjust the level of smoothing for the indicator.', group=settings),
    post_smoothing_style=input.string('WMA', 'Post Smoothing Style', options=('EMA', 'DEMA', 'TEMA', 'WMA', 'SMA'), group=settings),
    ma_length=input.int(24, 'MA Length', minval=2, group=settings),
    ma_style=input.string('EMA', 'MA Style', options=('EMA', 'DEMA', 'TEMA', 'WMA', 'SMA'), group=settings),
    enable_projection=input.bool(True, 'Ghost Mode', group=style),
    cd_alpha=input.int(25, 'MA Difference Alpha', minval=0, maxval=100, group=style),
    candle_color_style=input.string('Both', 'Candle Color Style', options=('MA', 'Direct', 'Both', 'None'), tooltip='MA: Use the moving average convergance divergance to color the candles.' + '\n\n' + 'Direct: Use the momentum as a source of color. When the momentum is positive it will be the bullish color and when its negative it will be the bearish color.' + '\n\n' + 'Both: Color the candles bassed on the ma and the polarity of the momentum. The bullish color will be darker if the momentum is negative and the bearish color will be lighter if the momentum is positive.' + '\n\n' + 'None: Dont color the candles.', group=style),
    momentum_color=input.color(color.new('#FFFFFF'), 'Momentum Color', group=style),
    ma_color=input.color(color.new('#F7A000'), 'MA Color', group=style),
    cd_up_over=input.color(color.new('#2AC075'), 'Bullish Up', group=style),
    cd_up_under=input.color(color.new('#D5FCE9'), 'Bullish Down', group=style),
    cd_down_under=input.color(color.new('#F82934'), 'Bearish Down', group=style),
    cd_down_over=input.color(color.new('#FFC8CB'), 'Bearish Up', group=style),
    glow=input.bool(True, 'Glow', group=style)
):
    @method
    def is_even(n: int):
        return n % 2 == 0

    def sinc(x: float):
        return 1 if x == 0 else math.sin(math.pi * x) / (math.pi * x)

    def blackman(n: float, length: int):
        return 0.42 - 0.5 * math.cos(2 * math.pi * n / (length - 1)) + 0.08 * math.cos(4 * math.pi * n / (length - 1))

    def mid_point(x: int):
        return (x - 1) / 2

    def offset(length: int):
        return (length - 1) / 2

    def get_data(source: float, length: int):
        data: Persistent[list[float]] = array.new_float()
        __block_result__ = na
        if array.size(data) < length:
            array.unshift(data, source)
            __block_result__ = data
        else:
            array.unshift(data, source)
            array.pop(data)
            __block_result__ = data
        return __block_result__

    def sinc_coefficients(length: int, fc: float):
        coefficients: list[float] = array.new_float()
        mid: int = mid_point(length)
        cutoff: float = 1 / fc
        for i in pine_range(0, length - 1, 1):
            n: int = i - mid
            k: int = i
            M: int = length
            if is_even(length):
                coefficient: float = sinc(2 * cutoff * n) * blackman(k + 0.5, M)
                array.push(coefficients, coefficient)
            else:
                coefficient: float = sinc(2 * cutoff * n) * blackman(k, M)
                array.push(coefficients, coefficient)
        return coefficients

    def toeplitz_matrix_valid(coefficients: list[float], M: int):
        N: int = array.size(coefficients)
        rows: int = M - N + 1
        toeplitz: Matrix[float] = matrix.new(rows, M, 0.0)
        for r in pine_range(0, rows - 1, 1):
            for c in pine_range(0, N - 1, 1):
                if c + r < M:
                    matrix.set(toeplitz, r, c + r, array.get(coefficients, c))
                else:
                    break
        return toeplitz

    def convolution(data: list[float], coefficients: list[float]):
        normalize: Persistent[float] = array.sum(coefficients)
        toeplitz_matrix: Persistent[Matrix[float]] = toeplitz_matrix_valid(coefficients, array.size(data))
        convolved: float = method_call('first', matrix.mult(toeplitz_matrix, data))
        return convolved / normalize

    def lti_sinc(source: Series[float], length: int, fc: float = 100):
        data: list[float] = get_data(source, length)
        coefficients: Persistent[list[float]] = sinc_coefficients(length, fc)
        __block_result_1__ = na
        if bar_index > length:
            convolved = convolution(data, coefficients)
            __block_result_1__ = convolved
        else:
            __block_result_1__ = NA(float)
        return __block_result_1__

    def ema(source: Series[float], length: float):
        alpha: float = 2.0 / (length + 1)
        smoothed: PersistentSeries[float] = na(float)
        smoothed = alpha * source + (1.0 - alpha) * nz(smoothed[1], source)
        return smoothed

    def dema(source: Series[float], length: float):
        ema1: float = ema(source, length)
        ema2: float = ema(ema1, length)
        return 2.0 * ema1 - ema2

    def tema(source: Series[float], length: float):
        ema1: float = ema(source, length)
        ema2: float = ema(ema1, length)
        ema3: float = ema(ema2, length)
        return (ema1 - ema2) * 3.0 + ema3

    def wma(source: Series[float], length: int):
        weight_sum: Persistent[float] = length * 0.5 * (length + 1)
        sum: float = 0.0
        for i in pine_range(0, length - 1, 1):
            sum = sum + source[i] * (length - i)
        return sum / weight_sum

    def sma(source: Series[float], length: int):
        sum: Series[float] = ta.cum(source)
        __block_result_2__ = na
        if bar_index < length - 1:
            __block_result_2__ = sum / (bar_index + 1)
        else:
            __block_result_2__ = (sum - sum[length]) / length
        return __block_result_2__

    def filter(source: Series[float], length: int, style: str):
        __block_result_3__ = na
        if length > 1:
            __block_result_4__ = na
            __switch_1__ = style
            if __switch_1__ == 'EMA':
                __block_result_4__ = ema(source, length)
            elif __switch_1__ == 'DEMA':
                __block_result_4__ = dema(source, length)
            elif __switch_1__ == 'TEMA':
                __block_result_4__ = tema(source, length)
            elif __switch_1__ == 'WMA':
                __block_result_4__ = wma(source, length)
            else:
                __block_result_4__ = sma(source, length)
            __block_result_3__ = __block_result_4__
        else:
            __block_result_3__ = source
        return __block_result_3__

    def color_changer(source: Color, direction: bool):
        r: float = color.r(source)
        g: float = color.g(source)
        b: float = color.b(source)
        __block_result_5__ = na
        if direction:
            __block_result_5__ = color.rgb((255 - r) / 3 + r, (255 - g) / 3 + g, (255 - b) / 3 + b)
        else:
            __block_result_5__ = color.rgb(r / 1.5, g / 1.5, b / 1.5)
        return __block_result_5__

    length_correction: int = momentum_length * 2
    sinc__global__: float = lti_sinc(source, length_correction, momentum_smoothing)
    offset__global__: int = offset(length_correction)
    delta: Series[float] = filter((source - sinc__global__) / offset__global__, post_smoothing, post_smoothing_style)
    projection: float = math.avg(delta - delta[1], (delta - delta[2]) / 2)
    ma: Series[float] = filter(filter(delta, 2, ma_style), ma_length, ma_style)
    ma_project: float = math.avg(ma - ma[1], (ma - ma[2]) / 2)
    momo: Series[float] = delta - ma
    momo_color: Persistent[Color] = na(Color)
    if momo > 0:
        if momo > momo[1]:
            momo_color = cd_up_over
        else:
            momo_color = cd_up_under
    else:
        if momo < momo[1]:
            momo_color = cd_down_under
        else:
            momo_color = cd_down_over
    direct_color: Persistent[Color] = na(Color)
    if candle_color_style == 'Both':
        if delta > 0:
            if momo < 0:
                direct_color = color_changer(momo_color, True)
            else:
                direct_color = momo_color
        else:
            if momo > 0:
                direct_color = color_changer(momo_color, False)
            else:
                direct_color = momo_color
    else:
        if delta > 0:
            if delta > delta[1]:
                direct_color = cd_up_over
            else:
                direct_color = cd_up_under
        else:
            if delta < delta[1]:
                direct_color = cd_down_under
            else:
                direct_color = cd_down_over
    hline(0)
    plot(momo, 'Convergance Divergence', color.new(momo_color, cd_alpha), 5, plot.style_histogram if glow else plot.style_columns)
    plot(momo if glow else na, 'Convergance Divergence Glow', color.new(momo_color, cd_alpha + (100 - cd_alpha) / 2), 1, plot.style_columns, display=display.pane)
    plot(ma, 'MA', ma_color)
    a = plot(ma if glow else na, 'MA Glow', color.new(ma_color, 80), 4, display=display.pane)
    plot(delta, 'Momentum', momentum_color)
    b = plot(delta if glow else na, 'Momentum Glow', color.new(momentum_color, 80), 4, display=display.pane)
    fill(a, b, color.new(momentum_color if delta > ma else ma_color, 90), 'Momentum Fill', editable=True)
    p_ma1: Persistent[float] = na(float)
    p_ma2: Persistent[float] = na(float)
    p_m1: Persistent[float] = na(float)
    p_m2: Persistent[float] = na(float)
    if enable_projection:
        p_ma1 = ma + ma_project
        p_m1 = delta + projection
        p_ma2 = ma + ma_project * 2
        p_m2 = delta + projection * 2
        project_delta: Persistent[Line] = line.new(na, na, na, na, color=momentum_color, style=line.style_dotted)
        project_ma: Persistent[Line] = line.new(na, na, na, na, color=ma_color, style=line.style_dotted)
        line.set_xy1(project_ma, bar_index, ma)
        line.set_xy2(project_ma, bar_index + 2, p_ma2)
        line.set_xy1(project_delta, bar_index, delta)
        line.set_xy2(project_delta, bar_index + 2, p_m2)
        linefill.new(project_delta, project_ma, color.new(ma_color if p_ma2 > p_m2 else momentum_color, 90))
    d1: float = p_m1 - p_ma1
    d2: float = p_m2 - p_ma2
    dc1: Color = na(Color)
    dc2: Color = na(Color)
    if d1 > 0:
        if d1 > momo:
            dc1 = cd_up_over
        else:
            dc1 = cd_up_under
    else:
        if d1 < momo:
            dc1 = cd_down_under
        else:
            dc1 = cd_down_over
    if d2 > 0:
        if d2 > d1:
            dc2 = cd_up_over
        else:
            dc2 = cd_up_under
    else:
        if d2 < d1:
            dc2 = cd_down_under
        else:
            dc2 = cd_down_over
    plot(d1, 'Projected Delta', color.new(dc1, 60), 1, plot.style_columns, offset=1, show_last=1)
    plot(d2, 'Projected Delta', color.new(dc2, 60), 1, plot.style_columns, offset=2, show_last=1)
    __block_result_6__ = na
    __switch__ = candle_color_style
    if __switch__ == 'MA':
        __block_result_6__ = momo_color
    elif __switch__ == 'Both':
        __block_result_6__ = direct_color
    elif __switch__ == 'Direct':
        __block_result_6__ = direct_color
    elif __switch__ == 'None':
        __block_result_6__ = na
    bar_color = __block_result_6__
    barcolor(bar_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
