"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, close, color, input, na, plot, script, strategy,
    string, ta
)
from pynecore.types import Persistent


@script.strategy('(IK) Grid Script', overlay=True, pyramiding=14, close_entries_rule='ANY', default_qty_type=strategy.cash, initial_capital=100.0, currency='USD', commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    i_autoBounds=input.bool(group='Grid Bounds', title='Use Auto Bounds?', defval=False),
    i_boundSrc=input.string(group='Grid Bounds', title='(Auto) Bound Source', defval='Hi & Low', options=('Hi & Low', 'Average')),
    i_boundLookback=input.int(group='Grid Bounds', title='(Auto) Bound Lookback', defval=250, maxval=500, minval=0),
    i_boundDev=input.float(group='Grid Bounds', title='(Auto) Bound Deviation', defval=0.1, maxval=1, minval=-1),
    i_upperBound=input.float(group='Grid Bounds', title='(Manual) Upper Boundry', defval=0.285),
    i_lowerBound=input.float(group='Grid Bounds', title='(Manual) Lower Boundry', defval=0.225),
    i_gridQty=input.int(group='Grid Lines', title='Grid Line Quantity', defval=8, maxval=15, minval=3)
):
    def f_getGridBounds(_bs, _bl, _bd, _up):
        __block_result__ = na
        if _bs == 'Hi & Low':
            __block_result__ = ta.highest(close, _bl) * (1 + _bd) if _up else ta.lowest(close, _bl) * (1 - _bd)
        else:
            avg = ta.sma(close, _bl)
            __block_result__ = avg * (1 + _bd) if _up else avg * (1 - _bd)
        return __block_result__

    def f_buildGrid(_lb, _gw, _gq):
        gridArr: list[float] = array.new_float(0)
        for i in pine_range(0, _gq - 1, 1):
            array.push(gridArr, _lb + _gw * i)
        return gridArr

    def f_getNearGridLines(_gridArr, _price):
        arr: list[int] = array.new_int(3)
        for i in pine_range(0, array.size(_gridArr) - 1, 1):
            if array.get(_gridArr, i) > _price:
                array.set(arr, 0, i if i == array.size(_gridArr) - 1 else i + 1)
                array.set(arr, 1, i if i == 0 else i - 1)
                break
        return arr

    upperBound: Persistent = f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, True) if i_autoBounds else i_upperBound
    lowerBound: Persistent = f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, False) if i_autoBounds else i_lowerBound
    gridWidth: Persistent = (upperBound - lowerBound) / (i_gridQty - 1)
    gridLineArr: Persistent = f_buildGrid(lowerBound, gridWidth, i_gridQty)
    orderArr: Persistent[list[bool]] = array.new_bool(i_gridQty, False)
    closeLineArr: Persistent = f_getNearGridLines(gridLineArr, close)
    nearTopGridLine: Persistent = array.get(closeLineArr, 0)
    nearBotGridLine: Persistent = array.get(closeLineArr, 1)
    for i in pine_range(0, array.size(gridLineArr) - 1, 1):
        if close < array.get(gridLineArr, i) and (not array.get(orderArr, i)) and (i < array.size(gridLineArr) - 1):
            buyId = i
            array.set(orderArr, buyId, True)
            strategy.entry(id=string.tostring(buyId), direction=strategy.long, qty=strategy.initial_capital / (i_gridQty - 1) / close, comment='#' + string.tostring(buyId))
        if close > array.get(gridLineArr, i) and i != 0:
            if array.get(orderArr, i - 1):
                sellId = i - 1
                array.set(orderArr, sellId, False)
                strategy.close(id=string.tostring(sellId), comment='#' + string.tostring(sellId))
    if i_autoBounds:
        upperBound = f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, True)
        lowerBound = f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, False)
        gridWidth = (upperBound - lowerBound) / (i_gridQty - 1)
        gridLineArr = f_buildGrid(lowerBound, gridWidth, i_gridQty)
    closeLineArr = f_getNearGridLines(gridLineArr, close)
    nearTopGridLine = array.get(closeLineArr, 0)
    nearBotGridLine = array.get(closeLineArr, 1)
    plot(array.get(gridLineArr, 0) if array.size(gridLineArr) > 0 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 1) if array.size(gridLineArr) > 1 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 2) if array.size(gridLineArr) > 2 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 3) if array.size(gridLineArr) > 3 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 4) if array.size(gridLineArr) > 4 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 5) if array.size(gridLineArr) > 5 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 6) if array.size(gridLineArr) > 6 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 7) if array.size(gridLineArr) > 7 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 8) if array.size(gridLineArr) > 8 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 9) if array.size(gridLineArr) > 9 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 10) if array.size(gridLineArr) > 10 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 11) if array.size(gridLineArr) > 11 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 12) if array.size(gridLineArr) > 12 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 13) if array.size(gridLineArr) > 13 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, 14) if array.size(gridLineArr) > 14 else na, color=color.rgb(255, 255, 0, 50) if bar_index % 2 == 1 else color.new('#00000000'))
    plot(array.get(gridLineArr, nearTopGridLine), color=color.rgb(255, 0, 255, 20), style=plot.style_stepline, linewidth=2)
    plot(array.get(gridLineArr, nearBotGridLine), color=color.rgb(0, 0, 255, 20), style=plot.style_stepline, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
