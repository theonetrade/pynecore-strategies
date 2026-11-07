"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, hl2, input, location, low, math, na, nz,
    plot, plotarrow, plotshape, request, script, shape, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('FRAMA strategy', overlay=True, precision=6, initial_capital=1000, calc_on_every_tick=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=10000, currency=currency.EUR, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    ma_src: Series[float] = input(title='MA FRAMA Source', defval=close),
    ma_frama_len=input(title='MA FRAMA Length', defval=12),
    res=input.timeframe(title='Resolution', defval='1W'),
    frama_FC=input.int(defval=1, minval=1, title='* Fractal Adjusted (FRAMA) Only - FC'),
    frama_SC=input.int(defval=200, minval=1, title='* Fractal Adjusted (FRAMA) Only - SC'),
    enterRule=input(False, title='Use supertrend for enter'),
    exitRule=input(False, title='Use supertrend for exit'),
    Factor=input.int(3, minval=1, maxval=100),
    Pd=input.int(7, minval=1, maxval=100),
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
    High = request.security(syminfo.tickerid, res, high)
    Low = request.security(syminfo.tickerid, res, low)
    source = request.security(syminfo.tickerid, res, ma_src)
    def ma(src, len):
        result: float = 0
        len1: int = len / 2
        e: float = 2.718281828459045
        w = math.log(2 / (frama_SC + 1)) / math.log(e)
        H1 = ta.highest(High, len1)
        L1 = ta.lowest(Low, len1)
        N1 = (H1 - L1) / len1
        H2_: Series = ta.highest(High, len1)
        H2 = H2_[len1]
        L2_: Series = ta.lowest(Low, len1)
        L2 = L2_[len1]
        N2 = (H2 - L2) / len1
        H3 = ta.highest(High, len)
        L3 = ta.lowest(Low, len)
        N3 = (H3 - L3) / len
        dimen1: Series = (math.log(N1 + N2) - math.log(N3)) / math.log(2)
        dimen = dimen1 if N1 > 0 and N2 > 0 and (N3 > 0) else nz(dimen1[1])
        alpha1 = math.exp(w * (dimen - 1))
        oldalpha = 1 if alpha1 > 1 else 0.01 if alpha1 < 0.01 else alpha1
        oldN = (2 - oldalpha) / oldalpha
        N = (frama_SC - frama_FC) * (oldN - 1) / (frama_SC - 1) + frama_FC
        alpha_ = 2 / (N + 1)
        alpha = 2 / (frama_SC + 1) if alpha_ < 2 / (frama_SC + 1) else 1 if alpha_ > 1 else alpha_
        frama: Series[float] = 0.0
        frama = (1 - alpha) * nz(frama[1]) + alpha * src
        result = frama
        return result

    frama = ma(ta.sma(source, 1), ma_frama_len)
    signal = ma(frama, ma_frama_len)
    plot(frama, color=color.new(color.red, 0))
    plot(signal, color=color.new(color.green, 0))
    longCondition = ta.crossover(frama, signal)
    shortCondition = ta.crossunder(frama, signal)
    Up = hl2 - Factor * ta.atr(Pd)
    Dn = hl2 + Factor * ta.atr(Pd)
    TrendUp: Series[float] = 0.0
    TrendDown: Series[float] = 0.0
    Trend: Series[float] = 0.0
    Tsl: float = 0.0
    TrendUp = math.max(Up, TrendUp[1]) if close[1] > TrendUp[1] else Up
    TrendDown = math.min(Dn, TrendDown[1]) if close[1] < TrendDown[1] else Dn
    Trend = 1 if close > TrendDown[1] else -1 if close < TrendUp[1] else nz(Trend[1], 1)
    Tsl = TrendUp if Trend == 1 else TrendDown
    linecolor = color.green if Trend == 1 else color.red
    plotshape(ta.cross(close, Tsl) and close > Tsl, 'Up Arrow', shape.triangleup, location.belowbar, color.new(color.green, 0), 0)
    plotshape(ta.cross(Tsl, close) and close < Tsl, 'Down Arrow', shape.triangledown, location.abovebar, color.new(color.red, 0), 0)
    plotarrow(Trend if Trend == 1 and Trend[1] == -1 else na, title='Up Entry Arrow', colorup=color.new(color.lime, 0), maxheight=60, minheight=50)
    plotarrow(Trend if Trend == -1 and Trend[1] == 1 else na, title='Down Entry Arrow', colordown=color.new(color.red, 0), maxheight=60, minheight=50)
    useTakeProfit = inpTakeProfit if inpTakeProfit >= 1 else na
    useStopLoss = inpStopLoss if inpStopLoss >= 1 else na
    useTrailStop = inpTrailStop if inpTrailStop >= 1 else na
    useTrailOffset = inpTrailOffset if inpTrailOffset >= 1 else na
    def enterLong():
        return longCondition and Trend == 1 if enterRule else longCondition

    def exitLong():
        return exitRule and Trend == -1

    if enterLong():
        strategy.entry(id='Buy', direction=strategy.long)
    if exitLong():
        strategy.close(id='Buy')
    def enterShort():
        return shortCondition and Trend == -1 if enterRule else shortCondition

    def exitShort():
        return exitRule and Trend == 1

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
