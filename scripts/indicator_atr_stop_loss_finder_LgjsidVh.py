"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, color, high, input, low, na, plot, position, script, string,
    ta, table
)
from pynecore.types import Persistent, Series, Table


@script.indicator(title='Average True Range Stop Loss Finder', shorttitle='ATR', overlay=True, na_bool=True)
def main(
    length=input.int(title='Length', defval=14, minval=1),
    smoothing=input.string(title='Smoothing', defval='RMA', options=('RMA', 'SMA', 'EMA', 'WMA')),
    m=input(1.5, 'Multiplier'),
    src1: Series[float] = input(high),
    src2: Series[float] = input(low),
    pline=input(True, 'Show Price Lines'),
    col1=input(color.blue, 'ATR Text Color'),
    col2=input.color(color.teal, 'Low Text Color', inline='1'),
    col3=input.color(color.red, 'High Text Color', inline='2'),
    collong=input.color(color.teal, 'Low Line Color', inline='1'),
    colshort=input.color(color.red, 'High Line Color', inline='2')
):
    def ma_function(source, length):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, length)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, length)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, length)
                else:
                    __block_result_2__ = ta.wma(source, length)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    a = ma_function(ta.tr(True), length) * m
    x = ma_function(ta.tr(True), length) * m + src1
    x2 = src2 - ma_function(ta.tr(True), length) * m
    p1 = plot(x, title='ATR Short Stop Loss', color=colshort, trackprice=True if pline else False)
    p2 = plot(x2, title='ATR Long Stop Loss', color=collong, trackprice=True if pline else False)
    Table__ren__: Persistent[Table] = table.new(position.bottom_center, 3, 1, border_width=3)
    def f_fillCell(_table, _column, _row, _value, _timeframe):
        _cellText = _timeframe + string.tostring(_value, '#.#')
        table.cell(_table, _column, _row, _cellText, text_color=col1)
        table.cell_set_text_color(Table__ren__, 1, 0, color.new(col3, transp=0))
        return table.cell_set_text_color(Table__ren__, 2, 0, color.new(col2, transp=0))

    if barstate.islast:
        f_fillCell(Table__ren__, 0, 0, a, 'ATR: ')
        f_fillCell(Table__ren__, 1, 0, x, 'H: ')
        f_fillCell(Table__ren__, 2, 0, x2, 'L: ')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
