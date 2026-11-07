"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, hl2, input, na, open, plot, request, script, strategy,
    syminfo, ta, ticker, time, timeframe, timestamp
)
from pynecore.types import Series


@script.strategy('Bill Williams Alligator improved', shorttitle='Scalping alligator', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    useHA=input(True, 'Use heikin ashi candle?'),
    smoothinput=input.int(1, minval=1, maxval=5, title='Moving Average Calculation: (1=SMA), (2=EMA), (3=WMA), (4=Linear), (5=VWMA)'),
    jawLength=input.int(13, minval=1, title='Jaw Length'),
    teethLength=input.int(8, minval=1, title='Teeth Length'),
    lipsLength=input.int(5, minval=1, title='Lips Length'),
    jawOffset=input(8, title='Jaw Offset'),
    teethOffset=input(5, title='Teeth Offset'),
    lipsOffset=input(3, title='Lips Offset'),
    inpTakeProfit=input.int(defval=0, title='Take Profit Points', minval=0),
    inpStopLoss=input.int(defval=0, title='Stop Loss Points', minval=0),
    inpTrailStop=input.int(defval=0, title='Trailing Stop Loss Points', minval=0),
    inpTrailOffset=input.int(defval=0, title='Trailing Stop Loss Offset Points', minval=0),
    testPeriodSwitch=input(False, 'Custom Backtesting Dates'),
    testStartYear=input(2020, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStartHour=input(0, 'Backtest Start Hour'),
    testStopYear=input(2020, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day'),
    testStopHour=input(23, 'Backtest Stop Hour')
):
    def calc_ma(src, l):
        return ta.sma(src, l) if smoothinput == 1 else ta.ema(src, l) if smoothinput == 2 else ta.wma(src, l) if smoothinput == 3 else ta.linreg(src, l, 0) if smoothinput == 4 else ta.vwma(src, l) if smoothinput == 5 else na

    heikinashi_close: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
    heikinashi_open: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open)
    heikinashi_hl2 = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hl2)
    direzione = 1 if heikinashi_close > heikinashi_open and heikinashi_close[1] > heikinashi_open[1] else -1 if heikinashi_close < heikinashi_open and heikinashi_close[1] < heikinashi_open[1] else 0
    jaw = calc_ma(heikinashi_hl2, jawLength)
    teeth = calc_ma(heikinashi_hl2, teethLength)
    lips = calc_ma(heikinashi_hl2, lipsLength)
    plot(jaw, title='jaw', offset=jawOffset, color=color.new(color.new('#3BB3E4'), 0))
    plot(teeth, title='teeth', offset=teethOffset, color=color.new(color.new('#FF006E'), 0))
    plot(lips, title='lips', offset=lipsOffset, color=color.new(color.new('#36C711'), 0))
    longCondition = direzione == 1 and jaw < teeth and (jaw < lips) and (teeth < lips)
    shortCondition = direzione == -1 and jaw > teeth and (jaw > lips) and (teeth > lips)
    useTakeProfit = inpTakeProfit if inpTakeProfit >= 1 else na
    useStopLoss = inpStopLoss if inpStopLoss >= 1 else na
    useTrailStop = inpTrailStop if inpTrailStop >= 1 else na
    useTrailOffset = inpTrailOffset if inpTrailOffset >= 1 else na
    def enterLong():
        return direzione == 1 and jaw < teeth and (jaw < lips) and (teeth < lips)

    def exitLong():
        return jaw > teeth or jaw > lips or teeth > lips

    if enterLong():
        strategy.entry(id='Buy', direction=strategy.long)
    if exitLong():
        strategy.close(id='Buy')
    def enterShort():
        return direzione == -1 and jaw > teeth and (jaw > lips) and (teeth > lips)

    def exitShort():
        return jaw < teeth or jaw < lips or teeth < lips

    if enterShort():
        strategy.entry(id='Sell', direction=strategy.short)
    if exitShort():
        strategy.close(id='Sell')
    strategy.exit('Exit Buy', from_entry='Buy', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)
    strategy.exit('Exit Sell', from_entry='Sell', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, testStartHour, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, testStopHour, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    isPeriod = testPeriod() if testPeriodSwitch == True else True
    if not isPeriod:
        strategy.cancel_all()
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
