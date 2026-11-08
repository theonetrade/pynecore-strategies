"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.lib import (
    array, bar_index, chart, close, color, high, input, location, low, na,
    plot, plotshape, polyline, script, shape, size, ta
)
from pynecore.types import NA, Series
from pynecore.types.chart import ChartPoint


@script.indicator('MA Sabres [LuxAlgo]', shorttitle='LuxAlgo - MA Sabres', max_polylines_count=100, overlay=True, na_bool=True)
def main(
    type=input.string('TEMA', 'MA Type', group='MA', options=('SMA', 'EMA', 'SMMA (RMA)', 'HullMA', 'WMA', 'VWMA', 'DEMA', 'TEMA', 'NONE')),
    len=input.int(50, 'Length', group='MA'),
    count=input.int(20, 'Previous Trend Duration', group='MA', tooltip='Reversal after x bars in the same direction'),
    colUp=input.color(color.new('#2962FF'), 'Bullish', group='Colours'),
    colDn=input.color(color.new('#F23645'), 'Bearish', group='Colours'),
    colMa=input.color(color.new('#787B86'), 'MA', group='Colours')
):
    @method
    def ma(type: str, length: int):
        ema1 = ta.ema(close, length)
        ema2 = ta.ema(ema1, length)
        ema3 = ta.ema(ema2, length)
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(close, length)
        elif __switch__ == 'EMA':
            __block_result__ = ema1
        elif __switch__ == 'SMMA (RMA)':
            __block_result__ = ta.rma(close, length)
        elif __switch__ == 'HullMA':
            __block_result__ = ta.hma(close, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(close, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(close, length)
        elif __switch__ == 'DEMA':
            __block_result__ = 2 * ema1 - ema2
        elif __switch__ == 'TEMA':
            __block_result__ = 3 * ema1 - 3 * ema2 + ema3
        else:
            __block_result__ = na
        return __block_result__

    ma__global__: Series = ma(type, len)
    fl: Series = ta.falling(ma__global__, count)
    rs: Series = ta.rising(ma__global__, count)
    up = fl[1] and ma__global__ > ma__global__[1]
    dn = rs[1] and ma__global__ < ma__global__[1]
    atr = ta.atr(14)
    n = bar_index
    if up:
        p: list[ChartPoint] = array.new(0, NA(ChartPoint))
        array.push(p, chart.point.from_index(n - 1, low[1] - atr / 15))
        array.push(p, chart.point.from_index(n + len / 2 - 1, low[1] + atr / 2.5))
        array.push(p, chart.point.from_index(n + len, low[1] + atr * 2))
        array.push(p, chart.point.from_index(n + len / 2 - 1, low[1] + atr / 2.5))
        array.push(p, chart.point.from_index(n - 1, low[1] + atr / 15))
        polyline.new(p, curved=True, closed=False, line_color=colUp, fill_color=color.new(colUp, 50))
    if dn:
        p: list[ChartPoint] = array.new(0, NA(ChartPoint))
        array.push(p, chart.point.from_index(n - 1, high[1] + atr / 15))
        array.push(p, chart.point.from_index(n + len / 2 - 1, high[1] - atr / 2.5))
        array.push(p, chart.point.from_index(n + len, high[1] - atr * 2))
        array.push(p, chart.point.from_index(n + len / 2 - 1, high[1] - atr / 2.5))
        array.push(p, chart.point.from_index(n - 1, high[1] - atr / 15))
        polyline.new(p, curved=True, closed=False, line_color=colDn, fill_color=color.new(colDn, 50))
    plot(ma__global__, 'MA', color=colMa)
    plotshape(low[1] if up else na, '', color=colUp, location=location.absolute, style=shape.circle, size=size.tiny, offset=-1)
    plotshape(low[1] if up else na, '', color=color.new(colUp, 50), location=location.absolute, style=shape.circle, size=size.small, offset=-1)
    plotshape(low[1] if up else na, '', color=color.new(colUp, 65), location=location.absolute, style=shape.circle, size=size.normal, offset=-1)
    plotshape(high[1] if dn else na, '', color=colDn, location=location.absolute, style=shape.circle, size=size.tiny, offset=-1)
    plotshape(high[1] if dn else na, '', color=color.new(colDn, 50), location=location.absolute, style=shape.circle, size=size.small, offset=-1)
    plotshape(high[1] if dn else na, '', color=color.new(colDn, 65), location=location.absolute, style=shape.circle, size=size.normal, offset=-1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)