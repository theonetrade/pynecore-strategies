"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, format, input, math, na, nz, plot,
    script, ta
)
from pynecore.types import Series


@script.indicator('Optimized Trend Tracker Bands', 'OTT Bands', overlay=True, format=format.price, precision=2, timeframe='', na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    length=input.int(2, 'OTT Moving Average Length', minval=1),
    percent=input.float(15, 'OTT Optimization Coeff', step=0.1, minval=0),
    X3=input.float(0.1, 'OTT UPPER BAND Optimization Coeff', step=0.001, minval=0),
    X5=input.float(0.077, 'OTT LOWER BAND Optimization Coeff', step=0.001, minval=0),
    showfibolines=input(title='Show OTT Bands Fibonacci Levels?', defval=False),
    showsupport=input(title='Show Support Line?', defval=False),
    highlight=input(title='Show OTT Support Line Color Changes?', defval=False),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF'))
):
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
    def Wwma_Func(src, length):
        wwalpha = 1 / length
        WWMA: Series[float] = 0.0
        WWMA = wwalpha * src + (1 - wwalpha) * nz(WWMA[1])
        return WWMA

    WWMA = Wwma_Func(src, length)
    def Zlema_Func(src: Series, length):
        zxLag = length / 2 if length / 2 == math.round(length / 2) else (length - 1) / 2
        zxEMAData = src + src - src[zxLag]
        ZLEMA = ta.ema(zxEMAData, length)
        return ZLEMA

    ZLEMA = Zlema_Func(src, length)
    def Tsf_Func(src, length):
        lrc = ta.linreg(src, length, 0)
        lrc1 = ta.linreg(src, length, 1)
        lrs = lrc - lrc1
        TSF = ta.linreg(src, length, 0) + lrs
        return TSF

    TSF = Tsf_Func(src, length)
    def getMA(src, length):
        ma: float = 0.0
        if mav == 'SMA':
            ma = ta.sma(src, length)
        if mav == 'EMA':
            ma = ta.ema(src, length)
        if mav == 'WMA':
            ma = ta.wma(src, length)
        if mav == 'TMA':
            ma = ta.sma(ta.sma(src, math.ceil(length / 2)), math.floor(length / 2) + 1)
        if mav == 'VAR':
            ma = VAR
        if mav == 'WWMA':
            ma = WWMA
        if mav == 'ZLEMA':
            ma = ZLEMA
        if mav == 'TSF':
            ma = TSF
        return ma

    MAvg: Series = getMA(src, length)
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
    OTTC = (color.green if MAvg > MAvg[1] else color.red) if highlight else color.new('#0585E1')
    OTTMAIN = plot(nz(OTT[2]), color=color.new(color.new('#B800D9'), 0), linewidth=2, title='OTT')
    plot(MAvg if showsupport else na, color=OTTC, linewidth=2, title='Support Line')
    OTTUST = plot(nz(OTT[2]) * (1 + X3), color=color.new(color.new('#4500C4'), 0), linewidth=2, title='OTT UPPER')
    OTTUSTYARI = plot(nz(OTT[2]) * (1 + X3 * 0.618) if showfibolines else nz(OTT[2]) * (1 + X3 / 2), color=color.new(color.new('#8400FF'), 0), linewidth=1, title='OTT UPPER HALF ')
    OTTFIBOUST2 = plot(nz(OTT[2]) * (1 + X3 * 0.382) if showfibolines else na, color=color.new(color.new('#C830FF'), 0), linewidth=1, title='OTT UPPER HALF ')
    OTTALT = plot(nz(OTT[2]) * (1 - X5), color=color.new(color.new('#00A6FF'), 0), linewidth=2, title='OTT LOWER')
    OTTALTYARI = plot(nz(OTT[2]) * (1 - X5 * 0.618) if showfibolines else nz(OTT[2]) * (1 - X5 / 2), color=color.new(color.new('#007BBD'), 0), linewidth=1, title='OTT LOWER HALF')
    OTTALTFIBO2 = plot(nz(OTT[2]) * (1 - X5 * 0.382) if showfibolines else na, color=color.new(color.new('#024DE3'), 0), linewidth=1, title='OTT LOWER HALF')
    fill(OTTUST, OTTUSTYARI, color=color.new(color.new('#4500C4'), 88))
    fill(OTTFIBOUST2, OTTUSTYARI, color=color.new(color.new('#8400FF'), 88))
    fill(OTTUSTYARI, OTTMAIN, color=color.new(color.new('#C810FF'), 88))
    fill(OTTFIBOUST2, OTTMAIN, color=color.new(color.new('#C810FF'), 88))
    fill(OTTALT, OTTALTYARI, color=color.new(color.new('#00A6FF'), 88))
    fill(OTTALTFIBO2, OTTALTYARI, color=color.new(color.new('#007BBD'), 88))
    fill(OTTALTYARI, OTTMAIN, color=color.new(color.new('#024DE3'), 88))
    fill(OTTALTFIBO2, OTTMAIN, color=color.new(color.new('#024DE3'), 88))
    alertcondition(ta.cross(MAvg, OTT[2]), title='Cross Alert', message='OTT - Support Line Crossing!')
    alertcondition(ta.crossover(MAvg, OTT[2]), title='Crossover Alarm', message='Support Line BUY SIGNAL!')
    alertcondition(ta.crossunder(MAvg, OTT[2]), title='Crossunder Alarm', message='Support Line SELL SIGNAL!')
    alertcondition(ta.cross(src, OTT[2]), title='Price Cross Alert', message='OTT - Price Crossing!')
    alertcondition(ta.crossover(src, OTT[2]), title='Price Crossover Alarm', message='PRICE OVER OTT - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, OTT[2]), title='Price Crossunder Alarm', message='PRICE UNDER OTT - SELL SIGNAL!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
