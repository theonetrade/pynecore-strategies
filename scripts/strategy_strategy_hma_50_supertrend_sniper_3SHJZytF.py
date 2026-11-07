"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, input, location, plot, plotshape, script, shape,
    size, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Strategy: HMA 50 + Supertrend Sniper', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True)
def main(
    hmaLength=input.int(50, title='HMA Length (Trend)', minval=1),
    atrPeriod=input.int(10, title='ATR Period'),
    factor=input.float(3.0, title='ATR Multiplier (ความกว้างของจุดคัท)', step=0.1),
    exitOnChoppy=input.bool(True, title='Exit when Choppy? (ปิดออเดอร์เมื่อเข้าโซนสีเทา)'),
    useDateFilter=input.bool(False, title='Use Date Filter'),
    startDate=input.time(timestamp('1 Jan 2024 00:00'), title='Start Date'),
    endDate=input.time(timestamp('1 Jan 2030 00:00'), title='End Date')
):
    hmaValue: Series = ta.hma(close, hmaLength)
    hmaRising = hmaValue > hmaValue[1]
    hmaFalling = hmaValue < hmaValue[1]
    supertrend, direction = ta.supertrend(factor, atrPeriod)
    isBullish = hmaRising and direction == -1
    isBearish = hmaFalling and direction == 1
    isChoppy = hmaRising and direction == 1 or (hmaFalling and direction == -1)
    inDateRange = time >= startDate and time <= endDate if useDateFilter else True
    if inDateRange:
        if isBullish:
            strategy.entry('Long', strategy.long, comment='LONG')
        if isBearish:
            strategy.entry('Short', strategy.short, comment='SHORT')
        if exitOnChoppy and isChoppy:
            strategy.close_all(comment='Close (Choppy)')
    hmaColor = color.gray if isChoppy else color.new('#00FF08') if isBullish else color.new('#FF0000')
    plot(hmaValue, title='HMA 50 Main', color=hmaColor, linewidth=3)
    plot(supertrend, title='Stop Loss Line', color=color.new(color.green, 50) if direction == -1 else color.new(color.red, 50), linewidth=1, style=plot.style_linebr)
    visualState: Persistent[int] = 0
    visualBuy = isBullish and visualState != 1
    visualSell = isBearish and visualState != -1
    if visualBuy:
        visualState = 1
    if visualSell:
        visualState = -1
    if isChoppy:
        visualState = 0
    plotshape(visualBuy, title='Long Visual', location=location.belowbar, color=color.new('#00FF08'), style=shape.cross, text='LONG', textcolor=color.white, size=size.small)
    plotshape(visualSell, title='Short Visual', location=location.abovebar, color=color.new('#FF0000'), style=shape.xcross, text='SHORT', textcolor=color.white, size=size.small)
    barcolor(color.new('#00FF08') if isBullish else color.new('#FF0000') if isBearish else color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
