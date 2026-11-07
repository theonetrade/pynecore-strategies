"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, box, chart, close, color, display, extend, high, input, label,
    line, low, math, na, plot, script, size, strategy, ta, xloc, yloc
)
from pynecore.types import Persistent, Series


@script.strategy("RCI Strategy [PineIndicators]", overlay=False, commission_value=0.01, default_qty_type=strategy.percent_of_equity, default_qty_value=100, slippage=2, max_labels_count=500, max_lines_count=500, max_boxes_count=500)
def main(
    src: Series[float] = input.source(close, "RCI Source"),
    rciLen=input.int(10, "RCI Length"),
    maType=input.string("SMA", "MA Type", options=("None", "SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA")),
    maLen=input.int(14, "MA Length"),
    dirOpt=input.string("Long & Short", "Trade Direction", options=("Long & Short", "Long Only", "Short Only"))
):
    rci = ta.rci(src, rciLen)

    def ma(series, l, t):
        __block_result__ = na
        __switch__ = t
        if __switch__ == "SMA":
            __block_result__ = ta.sma(series, l)
        elif __switch__ == "EMA":
            __block_result__ = ta.ema(series, l)
        elif __switch__ == "SMMA (RMA)":
            __block_result__ = ta.rma(series, l)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(series, l)
        elif __switch__ == "VWMA":
            __block_result__ = ta.vwma(series, l)
        return __block_result__

    rciMA = ma(rci, maLen, maType) if maType != 'None' else na

    plot(rci, 'RCI', color.blue, display=display.pane)
    plot(rciMA, 'RCI-MA', color.yellow, display=display.pane)
    plot(0, 'Zero', color.gray, display=display.pane)
    plot(80, '+80', color.green, display=display.pane)
    plot(-80, '-80', color.red, display=display.pane)

    longCond = ta.crossover(rci, rciMA)
    shortCond = ta.crossunder(rci, rciMA)
    canLong = dirOpt != 'Short Only'
    canShort = dirOpt != 'Long Only'

    if longCond:
        if canLong:
            strategy.entry('L', strategy.long)
        strategy.close('S')

    if shortCond:
        if canShort:
            strategy.entry('S', strategy.short)
        strategy.close('L')

    green = color.new(color.new('#0097A7'), 0)
    green90 = color.new(color.new('#0097A7'), 90)
    red = color.new(color.new('#FF195F'), 0)
    red90 = color.new(color.new('#FF195F'), 90)

    if strategy.position_size > strategy.position_size[1]:
        label.new(bar_index, low * 0.99, '▲', xloc=xloc.bar_index, yloc=yloc.price, textcolor=green, color=green90, style=label.style_text_outline, size=size.normal, force_overlay=True)
        label.new(bar_index, low * 0.99, 'Buy', xloc=xloc.bar_index, yloc=yloc.price, textcolor=green, color=green90, style=label.style_label_up, size=size.tiny, force_overlay=True)

    if strategy.position_size < strategy.position_size[1]:
        label.new(bar_index, high * 1.01, '▼', xloc=xloc.bar_index, yloc=yloc.price, textcolor=red, color=red90, style=label.style_text_outline, size=size.normal, force_overlay=True)
        label.new(bar_index, high * 1.01, 'Close', xloc=xloc.bar_index, yloc=yloc.price, textcolor=red, color=red90, style=label.style_label_down, size=size.tiny, force_overlay=True)

    entryPrice: Persistent[float] = na(float)
    entryBar: Persistent[int] = na(int)
    entryLong: Persistent[bool] = False

    if strategy.position_size != 0 and strategy.position_size[1] == 0:
        entryPrice = strategy.position_avg_price
        entryBar = bar_index
        entryLong = strategy.position_size > 0

    if strategy.position_size == 0 and strategy.position_size[1] != 0:
        exitBar = bar_index
        rightIdx = exitBar - 1
        exitClose = close[1]

        if rightIdx < entryBar:
            rightIdx = exitBar
            exitClose = close

        win: bool = exitClose > entryPrice if entryLong else exitClose < entryPrice
        col = green if win else red

        top = math.max(entryPrice, exitClose)
        bottom = math.min(entryPrice, exitClose)

        pTL = chart.point.from_index(entryBar, top)
        pBR = chart.point.from_index(rightIdx, bottom)

        box.new(pTL, pBR, border_color=color.new(color.black, 100), border_width=1, bgcolor=color.new(col, 80), force_overlay=True)

        line.new(entryBar, top, rightIdx, top, xloc=xloc.bar_index, color=col, width=1, extend=extend.none, force_overlay=True)
        line.new(entryBar, bottom, rightIdx, bottom, xloc=xloc.bar_index, color=col, width=1, extend=extend.none, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
