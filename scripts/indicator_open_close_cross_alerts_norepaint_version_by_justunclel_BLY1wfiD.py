"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, high, hline, input, location, low, math,
    na, nz, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Series


@script.indicator(title='Open Close Cross Alerts NoRepaint Version by JustUncleL', shorttitle='OCC Alerts NRP', overlay=False, na_bool=True)
def main(
    useRes=input(defval=True, title='Use Alternate Resolution?'),
    intRs_=input.int(defval=6, title='Multiplier for Alernate Resolution', minval=1),
    basisType=input.string(defval='ZEMA', title='MA Type: ', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HullMA', 'ZEMA', 'SSMA', 'TMA')),
    basisLen=input.int(defval=8, title='MA Period', minval=1),
    uDiv=input(False, 'Show Divergence Channel'),
    multi=input.float(0.5, minval=0.0, maxval=3.0, title='Divergence Channel Width Factor (Stddev)'),
    uHid=input(False, title='Show Hidden Divergence'),
    uReg=input(False, title='Show Regular Divergence')
):
    intRes = intRs_ if useRes else 1
    uDiv = uDiv if uReg or uHid else False
    green100: Color = color.new('#008000')
    lime100: Color = color.new('#00FF00')
    red100: Color = color.new('#FF0000')
    blue100: Color = color.new('#0000FF')
    aqua100: Color = color.new('#00FFFF')
    darkred100: Color = color.new('#8B0000')
    gray100: Color = color.new('#808080')
    def variant_supersmoother(src: Series, len):
        a1 = math.exp(-1.414 * 3.14159 / len)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / len)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        v9: Series[float] = 0.0
        v9 = c1 * (src + nz(src[1])) / 2 + c2 * nz(v9[1]) + c3 * nz(v9[2])
        return v9

    def variant_smoothed(src, len):
        v5: Series[float] = 0.0
        sma_1 = ta.sma(src, len)
        v5 = sma_1 if na(v5[1]) else (v5[1] * (len - 1) + src) / len
        return v5

    def variant_zerolagema(src: Series, len):
        lag = (len - 1) / 2
        emaSrc = src + src - src[lag]
        v10 = ta.ema(emaSrc, len)
        return v10

    def variant_doubleema(src, len):
        v2 = ta.ema(src, len)
        v6 = 2 * v2 - ta.ema(v2, len)
        return v6

    def variant_tripleema(src, len):
        v2 = ta.ema(src, len)
        v7 = 3 * (v2 - ta.ema(v2, len)) + ta.ema(ta.ema(v2, len), len)
        return v7

    def variant_lag(p, g):
        L0: Series[float] = 0.0
        L1: Series[float] = 0.0
        L2: Series[float] = 0.0
        L3: Series[float] = 0.0
        L0 = (1 - g) * p + g * nz(L0[1])
        L1 = -g * L0 + nz(L0[1]) + g * nz(L1[1])
        L2 = -g * L1 + nz(L1[1]) + g * nz(L2[1])
        L3 = -g * L2 + nz(L2[1]) + g * nz(L3[1])
        f = (L0 + 2 * L1 + 2 * L2 + L3) / 6
        return f

    def variant(type, src, len):
        ema_1 = ta.ema(src, len)
        wma_1 = ta.wma(src, len)
        vwma_1 = ta.vwma(src, len)
        variant_smoothed__1 = variant_smoothed(src, len)
        variant_doubleema__1 = variant_doubleema(src, len)
        variant_tripleema__1 = variant_tripleema(src, len)
        wma_2 = ta.wma(src, len / 2)
        wma_3 = ta.wma(src, len)
        wma_4 = ta.wma(2 * wma_2 - wma_3, math.round(math.sqrt(len)))
        variant_supersmoother__1 = variant_supersmoother(src, len)
        variant_zerolagema__1 = variant_zerolagema(src, len)
        sma_1 = ta.sma(src, len)
        sma_2 = ta.sma(sma_1, len)
        sma_3 = ta.sma(src, len)
        return ema_1 if type == 'EMA' else wma_1 if type == 'WMA' else vwma_1 if type == 'VWMA' else variant_smoothed__1 if type == 'SMMA' else variant_doubleema__1 if type == 'DEMA' else variant_tripleema__1 if type == 'TEMA' else wma_4 if type == 'HullMA' else variant_supersmoother__1 if type == 'SSMA' else variant_zerolagema__1 if type == 'ZEMA' else sma_2 if type == 'TMA' else sma_3

    closeSeries = variant(basisType, close, basisLen)
    openSeries = variant(basisType, open, basisLen)
    closeOpenAvg = (closeSeries + openSeries) / 2
    closeSeriesAlt = variant(basisType, close, basisLen * intRes)
    openSeriesAlt = variant(basisType, open, basisLen * intRes)
    xlong = ta.crossover(closeSeriesAlt, openSeriesAlt)
    xshort = ta.crossunder(closeSeriesAlt, openSeriesAlt)
    longCond = xlong
    shortCond = xshort
    diff = closeSeriesAlt - openSeriesAlt
    pcd = 50000.0 * diff / closeOpenAvg
    alert__ren__ = longCond or shortCond
    trendColour = color.green if closeSeriesAlt > openSeriesAlt else color.red
    hline(0, color=color.gray, linestyle=hline.style_dashed)
    plot(pcd, title='OCC Difference Factor', color=trendColour, linewidth=1, style=plot.style_area)
    plot(pcd, title='OCC Difference Factor', color=trendColour, linewidth=2, style=plot.style_line)
    plotshape(alert__ren__, title='OCC Alert Plot', color=trendColour, style=shape.circle, location=location.bottom, size=size.auto)
    def f_top_fractal(_src: Series):
        return _src[4] < _src[2] and _src[3] < _src[2] and (_src[2] > _src[1]) and (_src[2] > _src)

    def f_bot_fractal(_src: Series):
        return _src[4] > _src[2] and _src[3] > _src[2] and (_src[2] < _src[1]) and (_src[2] < _src)

    def f_fractalize(_src):
        f_bot_fractal__1 = f_bot_fractal(_src)
        return 1 if f_top_fractal(_src) else -1 if f_bot_fractal__1 else 0

    rsi_high: Series = pcd
    rsi_low: Series = pcd
    offset_ = multi * ta.stdev(pcd, 20)
    fractal_top_rsi = rsi_high[2] if f_fractalize(rsi_high) > 0 else na
    fractal_bot_rsi = rsi_low[2] if f_fractalize(rsi_low) < 0 else na
    rsi_high_prev = ta.valuewhen(cast_bool(fractal_top_rsi), rsi_high[2], 1)
    rsi_high_price = ta.valuewhen(cast_bool(fractal_top_rsi), high[2], 1)
    rsi_low_prev = ta.valuewhen(cast_bool(fractal_bot_rsi), rsi_low[2], 1)
    rsi_low_price = ta.valuewhen(cast_bool(fractal_bot_rsi), low[2], 1)
    regular_bearish_div = fractal_top_rsi and high[2] > rsi_high_price and (rsi_high[2] < rsi_high_prev) and (rsi_high > 0)
    hidden_bearish_div = fractal_top_rsi and high[2] < rsi_high_price and (rsi_high[2] > rsi_high_prev) and (rsi_high > 0)
    regular_bullish_div = fractal_bot_rsi and low[2] < rsi_low_price and (rsi_low[2] > rsi_low_prev) and (rsi_low < 0)
    hidden_bullish_div = fractal_bot_rsi and low[2] > rsi_low_price and (rsi_low[2] < rsi_low_prev) and (rsi_low < 0)
    plot(title='RSI High', series=rsi_high if uDiv else na, color=color.new(color.gray, 0))
    plot(title='RSI Low', series=rsi_low if uDiv else na, color=color.new(color.gray, 0))
    plot(title='RSI H F', series=fractal_top_rsi + offset_ if uDiv else na, color=color.new(color.red, 0), offset=-2)
    plot(title='RSI L F', series=fractal_bot_rsi - offset_ if uDiv else na, color=color.new(color.green, 0), offset=-2)
    plot(title='RSI H D', series=fractal_top_rsi + offset_ if uDiv else na, style=plot.style_circles, color=color.maroon if regular_bearish_div and uReg or (hidden_bearish_div and uHid) else color.gray, linewidth=3, offset=-2)
    plot(title='RSI L D', series=fractal_bot_rsi - offset_ if uDiv else na, style=plot.style_circles, color=color.green if regular_bullish_div and uReg or (hidden_bullish_div and uHid) else color.gray, linewidth=3, offset=-2)
    plotshape(title='+RBD', series=rsi_high[2] + offset_ if regular_bearish_div and uReg else na, text='Regular', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='+HBD', series=rsi_high[2] + offset_ if hidden_bearish_div and uHid else na, text='hidden', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-RBD', series=rsi_low[2] - offset_ if regular_bullish_div and uReg else na, text='Regular', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-HBD', series=rsi_low[2] - offset_ if hidden_bullish_div and uHid else na, text='hidden', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    alertcondition(alert__ren__, message='OCC BothCond', title='OCC BothCond')
    alertcondition(longCond, message='OCC LongCond', title='OCC LongCond')
    alertcondition(shortCond, message='OCC ShortCond', title='OCC ShortCond')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
