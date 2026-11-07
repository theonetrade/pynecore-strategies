"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta, time, timestamp


@script.strategy('MA 10/20 Crossover', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    testStartYear=input(2016, 'Backtest Start Year'),
    testStartMonth=input(4, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(2018, 'BackTest Stop Year'),
    testStopMonth=input(10, 'Backtest Stop Month'),
    testStopDay=input(15, 'Backtest Stop Day')
):
    ma10 = ta.sma(close, 10)
    ma20 = ta.sma(close, 20)
    long = ta.cross(ma10, ma20) and ma10 > ma20
    short = ta.cross(ma10, ma20) and ma10 < ma20
    plot(ma10, title='10', color=color.new(color.yellow, 0), linewidth=2)
    plot(ma20, title='20', color=color.new(color.red, 0), linewidth=2)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    if time >= testPeriodStart:
        if time <= testPeriodStop:
            if long:
                strategy.entry('Long', strategy.long, 1.0)
            if short:
                strategy.entry('Short', strategy.short, 1.0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
