"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, format, high, hline, input, location,
    low, math, na, nz, plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Color, Series


@script.strategy(title='Stochastic Optimized Trend Tracker', shorttitle='SOTT', format=format.price, precision=2, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    periodK=input.int(250, title='%K Length', minval=1),
    smoothK=input.int(50, title='%K Smoothing', minval=1),
    src1: Series[float] = input(close, title='Source'),
    length=input.int(3, 'OTT Period', minval=1),
    percent=input.float(0.618, 'OTT Percent', step=0.1, minval=0),
    showsupport=input(title='Show Support Line?', defval=False),
    showsignalsc=input(title='Show Stochastic/OTT Crossing Signals?', defval=False),
    dummy0=input(True, title='=Backtest Inputs='),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromYear=input.int(defval=2005, title='From Year', minval=2005),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToYear=input.int(defval=9999, title='To Year', minval=2006)
):
    def Var_Func1(src1: Series, length):
        valpha1 = 2 / (length + 1)
        vud11 = src1 - src1[1] if src1 > src1[1] else 0
        vdd11 = src1[1] - src1 if src1 < src1[1] else 0
        vUD1 = math.sum(vud11, 9)
        vDD1 = math.sum(vdd11, 9)
        vCMO1 = nz((vUD1 - vDD1) / (vUD1 + vDD1))
        VAR1: Series[float] = 0.0
        VAR1 = nz(valpha1 * math.abs(vCMO1) * src1) + (1 - valpha1 * math.abs(vCMO1)) * nz(VAR1[1])
        return VAR1

    VAR1 = Var_Func1(src1, length)
    k = Var_Func1(ta.stoch(close, high, low, periodK), smoothK)
    src = k + 1000
    def Var_Func(src: Series, length):
        valpha = 2 / (length + 1)
        vud1 = src - src[1] if src > src[1] else 0
        vdd1 = src[1] - src if src < src[1] else 0
        vUD = math.sum(vud1, 9)
        vDD = math.sum(vdd1, 9)
        vCMO = nz((vUD - vDD) / (vUD + vDD))
        VAR: Series[float] = 0.0
        VAR = nz(valpha * math.abs(vCMO) * src) + (1 - valpha * math.abs(vCMO)) * nz(VAR[1])
        return VAR

    VAR = Var_Func(src, length)
    h0 = hline(1080, 'Upper Band', color=color.new('#606060'))
    h1 = hline(1020, 'Lower Band', color=color.new('#606060'))
    fill(h0, h1, color=color.new(color.new('#9915FF'), 80), title='Background')
    plot(k + 1000, title='%K', color=color.new(color.new('#0094FF'), 0))
    MAvg = Var_Func(src, length)
    fark = MAvg * percent * 0.01
    longStop: Series = MAvg - fark
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
    shortStop: Series = MAvg + fark
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if MAvg < shortStopPrev else shortStop
    dir: Series[int] = 1
    dir = nz(dir[1], dir)
    dir = 1 if dir == -1 and MAvg > shortStopPrev else -1 if dir == 1 and MAvg < longStopPrev else dir
    MT = longStop if dir == 1 else shortStop
    OTT: Series = MT * (200 + percent) / 200 if MAvg > MT else MT * (200 - percent) / 200
    plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Support Line')
    OTTC: Color = color.new('#B800D9')
    pALL = plot(nz(OTT[2]), color=color.new(OTTC, 0), linewidth=2, title='OTT')
    alertcondition(ta.cross(src, OTT[2]), title='Price Cross Alert', message='OTT - Price Crossing!')
    alertcondition(ta.crossover(src, OTT[2]), title='Price Crossover Alarm', message='PRICE OVER OTT - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, OTT[2]), title='Price Crossunder Alarm', message='PRICE UNDER OTT - SELL SIGNAL!')
    buySignalc = ta.crossover(src, OTT[2])
    plotshape(OTT * 0.995 if buySignalc and showsignalsc else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossunder(src, OTT[2])
    plotshape(OTT * 1.005 if sellSignallc and showsignalsc else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    Start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    Finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def Timerange():
        return True if time >= Start and time <= Finish else False

    if buySignalc:
        if Timerange():
            strategy.entry('Long', strategy.long)
    if sellSignallc:
        if Timerange():
            strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
