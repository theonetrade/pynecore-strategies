"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, math, na, open, plot, script, ta, volume
from pynecore.types import Series


@script.indicator('Volume-Supported Linear Regression Trend', 'VSLRT', overlay=False, na_bool=True)
def main(
    src: Series[float] = input(defval=close, title='Source'),
    len1=input.int(defval=20, title='Short Term Length', minval=5),
    len2=input.int(defval=50, title='Long Term Length', minval=5),
    ccol11=input.color(defval=color.new('#00FF00'), title='Column Colors', inline='gr1'),
    ccol12=input.color(defval=color.new('#00BC00'), title='', inline='gr1'),
    ccol13=input.color(defval=color.new('#00FF006F'), title='', inline='gr1'),
    ccol21=input.color(defval=color.new('#FF0000'), title='', inline='gr1'),
    ccol22=input.color(defval=color.new('#BF0000'), title='', inline='gr1'),
    ccol23=input.color(defval=color.new('#FF00006F'), title='', inline='gr1'),
    col11=input.color(defval=color.new('#008EFF'), title='Line Colors', inline='gr2'),
    col12=input.color(defval=color.new('#006EC5'), title='', inline='gr2'),
    col13=input.color(defval=color.new('#024478'), title='', inline='gr2'),
    col21=input.color(defval=color.new('#FD9701'), title='', inline='gr2'),
    col22=input.color(defval=color.new('#CE7A00'), title='', inline='gr2'),
    col23=input.color(defval=color.new('#663D00'), title='', inline='gr2')
):
    slope_price = ta.linreg(src, len1, 0) - ta.linreg(src, len1, 1)
    slope_price_lt = ta.linreg(src, len2, 0) - ta.linreg(src, len2, 1)
    tw = high - math.max(open, close)
    bw = math.min(open, close) - low
    body = math.abs(close - open)
    def _rate(cond):
        ret = 0.5 * (tw + bw + (2 * body if cond else 0)) / (tw + bw + body)
        ret = 0.5 if na(ret) else ret
        return ret

    def _get_trend(len):
        deltaup = volume * _rate(open <= close)
        deltadown = volume * _rate(open > close)
        slope_volume_up = ta.linreg(deltaup, len, 0) - ta.linreg(deltaup, len, 1)
        slope_volume_down = ta.linreg(deltadown, len, 0) - ta.linreg(deltadown, len, 1)
        return (slope_volume_up, slope_volume_down)

    slope_volume_up, slope_volume_down = _get_trend(len1)
    column_col = ((ccol11 if slope_volume_up > slope_volume_down else ccol12) if slope_volume_up > 0 else ccol13) if slope_price > 0 else ((ccol21 if slope_volume_up < slope_volume_down else ccol22) if slope_volume_down > 0 else ccol23) if slope_price < 0 else color.gray
    plot(slope_price * len1, color=column_col, style=plot.style_columns)
    slope_volume_up_lt, slope_volume_down_lt = _get_trend(len2)
    column_col = ((col11 if slope_volume_up_lt > slope_volume_down_lt else col12) if slope_volume_up_lt > 0 else col13) if slope_price_lt > 0 else ((col21 if slope_volume_up_lt < slope_volume_down_lt else col22) if slope_volume_down_lt > 0 else col23) if slope_price_lt < 0 else color.gray
    plot(slope_price_lt * len2, color=column_col, linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
