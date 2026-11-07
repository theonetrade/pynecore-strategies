"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, input, location, math, na, plot, plotshape, script,
    shape, size, strategy, ta, time, timestamp
)


@script.strategy('Backtest single EMA cross', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    qty=input(100000, 'Buy quantity'),
    testStartYear=input(2019, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStartHour=input(0, 'Backtest Start Hour'),
    testStartMin=input(0, 'Backtest Start Minute'),
    testStopYear=input(2099, 'Backtest Stop Year'),
    testStopMonth=input(1, 'Backtest Stop Month'),
    testStopDay=input(30, 'Backtest Stop Day'),
    testPeriodBackground=input(title='Color Background?', defval=True),
    ema1=input(10, title='Select EMA 1'),
    ema2=input(20, title='Select EMA 2')
):
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, testStartHour, testStartMin)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    testPeriodBackgroundColor = color.new('#00FF00') if testPeriodBackground and time >= testPeriodStart and (time <= testPeriodStop) else na
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    expo = ta.ema(close, ema1)
    ma = ta.ema(close, ema2)
    avg_1 = math.avg(expo, ma)
    s2 = avg_1 if ta.cross(expo, ma) else na
    p1 = plot(expo, color=color.new(color.new('#00FFFF'), 0), linewidth=2)
    p2 = plot(ma, color=color.new(color.orange, 0), linewidth=2)
    fill(p1, p2, color=color.new(color.white, 80))
    longCondition = ta.crossover(expo, ma)
    shortCondition = ta.crossunder(expo, ma)
    if testPeriod():
        if longCondition:
            strategy.entry('Long', strategy.long)
        if shortCondition:
            strategy.entry('Short', strategy.short)
    plotshape(longCondition, title='Buy Signal', text='BUY', textcolor=color.new(color.new('#FFFFFF'), 0), style=shape.labelup, size=size.normal, location=location.belowbar, color=color.new(color.new('#1B8112'), 0))
    plotshape(shortCondition, title='Sell Signal', text='SELL', textcolor=color.new(color.new('#FFFFFF'), 0), style=shape.labeldown, size=size.normal, location=location.abovebar, color=color.new(color.new('#FF5733'), 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
