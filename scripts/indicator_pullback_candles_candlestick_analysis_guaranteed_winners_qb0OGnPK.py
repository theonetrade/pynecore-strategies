"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, close, color, high, input, location, low, na,
    plotshape, script, shape, size, ta
)

g_ema: str = 'EMA Filter'


@script.indicator('Pullback Candle  ', overlay=True)
def main(
    emaLength=input.int(title='EMA Length', defval=50, tooltip='Length of the EMA filter', group=g_ema),
    useEmaFilter=input.bool(title='Use EMA Filter?', defval=False, tooltip='Turns on/off the EMA filter', group=g_ema)
):
    highest_1 = ta.highest(high, 10)
    swingHigh = high == ta.highest(high, 10) or high[1] == highest_1
    lowest_1 = ta.lowest(low, 6)
    swingLow = low == ta.lowest(low, 6) or low[1] == lowest_1
    ema = ta.ema(close, emaLength)
    emaFilterLong = not useEmaFilter or close > ema
    emaFilterShort = not useEmaFilter or close < ema
    pullBack = close[2] < close[3] and close[2] < close[3] and (close[1] < close[2]) and (close > close[1]) and emaFilterLong and swingLow
    plotshape(pullBack, style=shape.xcross, size=size.tiny, color=color.green, text='PB', location=location.belowbar)
    alertcondition(pullBack, 'Pullback Candle ', 'Pullback Candle  detected for {{ticker}}')
    barcolor(color.green if pullBack else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
