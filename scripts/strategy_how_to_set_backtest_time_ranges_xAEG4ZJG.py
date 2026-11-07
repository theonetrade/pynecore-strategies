"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, currency, input, plot, script, strategy, ta, time,
    timeframe, timestamp
)
from pynecore.types import Color, NA


@script.strategy(title='How To Set Time Ranges', shorttitle='Timed', overlay=True, precision=8, max_bars_back=200, pyramiding=0, initial_capital=100000, currency=currency.NONE, default_qty_type=strategy.cash, default_qty_value=100000, commission_type='percent', commission_value=0.27, margin_long=0, margin_short=0, close_by_id=True)
def main(
    fastMA=input.int(defval=14, title='FastMA Length', minval=1, step=1),
    slowMA=input.int(defval=28, title='SlowMA Length', minval=1, step=1),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromYear=input.int(defval=2021, title='From Year', minval=1970),
    thruMonth=input.int(defval=1, title='Thru Month', minval=1, maxval=12),
    thruDay=input.int(defval=1, title='Thru Day', minval=1, maxval=31),
    thruYear=input.int(defval=2112, title='Thru Year', minval=1970),
    entryTime=input.session('0000-0000', title='Entry Time'),
    exitTime=input.session('0000-0000', title='Exit Time'),
    showDate=input(True, title='Show Date Range'),
    showTimeE=input(True, title='Show Time Entry'),
    showTimeX=input(True, title='Show Time Exit')
):
    def isDate():
        start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
        finish = timestamp(thruYear, thruMonth, thruDay, 23, 59)
        isDate__00000011__ = time >= start and time <= finish
        return isDate__00000011__

    def isTime(_position):
        isTime__00000013__ = time(timeframe.period, _position + ':1234567')
        return isTime__00000013__

    enterLong = ta.crossover(ta.sma(close, fastMA), ta.sma(close, slowMA))
    exitLong = ta.crossunder(ta.sma(close, fastMA), ta.sma(close, slowMA))
    isTime_1 = isTime(entryTime)
    if isDate() and isTime_1 and enterLong:
        strategy.entry('L', strategy.long)
    isTime_2 = isTime(exitTime)
    if isDate() and isTime_2 and exitLong:
        strategy.close('L')
    isDate_1 = isDate()
    bgcolor(color=color.new(color.gray, 90) if showDate and isDate_1 else NA(Color))
    isDate_2 = isDate()
    isTime_3 = isTime(entryTime)
    bgcolor(color=color.new(color.lime, 90) if showTimeE and isDate_2 and isTime_3 else NA(Color))
    isDate_3 = isDate()
    isTime_4 = isTime(exitTime)
    bgcolor(color=color.new(color.purple, 90) if showTimeX and isDate_3 and isTime_4 else NA(Color))
    plot(ta.sma(close, fastMA), title='FastMA', color=color.new(color.yellow, 0), linewidth=2, style=plot.style_line)
    plot(ta.sma(close, slowMA), title='SlowMA', color=color.new(color.aqua, 0), linewidth=2, style=plot.style_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
