"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, input, location, math, na, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('Optimized Trend Tracker Oscillator', 'OTTO', overlay=False)
def main(
    length=input.int(2, 'OTT Period', minval=1),
    percent=input.float(0.6, 'OTT Optimization Coeff', step=0.1, minval=0),
    flength=input.int(10, 'FAST VIDYA Length', minval=1),
    slength=input.int(25, 'SLOW VIDYA Length', minval=1),
    coco=input.int(100000, 'Correcting Constant', minval=1),
    src1: Series[float] = input(close, title='Source'),
    showsignalsc=input(title='OTTO Crossing Signals?', defval=True),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'DEMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF', 'HULL'))
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
    mov1 = Var_Func1(src1, slength / 2)
    mov2 = Var_Func1(src1, slength)
    mov3 = Var_Func1(src1, slength * flength)
    src = mov1 / (mov2 - mov3 + coco)
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
    DEMA = 2 * ta.ema(src, length) - ta.ema(ta.ema(src, length), length)
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
    HMA = ta.wma(2 * ta.wma(src, length / 2) - ta.wma(src, length), math.round(math.sqrt(length)))
    def Var_Funcl(srcl: Series, length):
        valphal = 2 / (length + 1)
        vud1l = srcl - srcl[1] if srcl > srcl[1] else 0
        vdd1l = srcl[1] - srcl if srcl < srcl[1] else 0
        vUDl = math.sum(vud1l, 9)
        vDDl = math.sum(vdd1l, 9)
        vCMOl = nz((vUDl - vDDl) / (vUDl + vDDl))
        VARl: Series[float] = 0.0
        VARl = nz(valphal * math.abs(vCMOl) * srcl) + (1 - valphal * math.abs(vCMOl)) * nz(VARl[1])
        return VARl

    def getMA(src, length):
        ma: float = 0.0
        if mav == 'SMA':
            ma = ta.sma(src, length)
        if mav == 'EMA':
            ma = ta.ema(src, length)
        if mav == 'WMA':
            ma = ta.wma(src, length)
        if mav == 'DEMA':
            ma = DEMA
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
        if mav == 'HULL':
            ma = HMA
        return ma

    MAvg = getMA(src, length)
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
    HOTT: Series = MT * (200 + percent) / 200 if MAvg > MT else MT * (200 - percent) / 200
    HOTTC = color.new(color.red, 0)
    LOTT = src
    LOTTC = color.new(color.blue, 0)
    HOTTLine = plot(nz(HOTT[2]), title='HOTT', color=HOTTC, linewidth=2, style=plot.style_line)
    LOTTLine = plot(nz(LOTT), title='LOTT', color=LOTTC, linewidth=2, style=plot.style_line)
    FillColor = color.new(color.red, 20) if highlighting and LOTT < HOTT[2] else color.new(color.green, 20)
    fill(HOTTLine, LOTTLine, title='Highligter', color=FillColor)
    alertcondition(ta.crossunder(HOTT[2], LOTT), title='Crossover Alarm', message='OTTO - BUY SIGNAL!')
    alertcondition(ta.crossover(HOTT[2], LOTT), title='Crossunder Alarm', message='OTTO - SELL SIGNAL!')
    buySignalc = ta.crossunder(HOTT[2], LOTT)
    plotshape(HOTT[2] * 0.9995 if buySignalc and showsignalsc else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossover(HOTT[2], LOTT)
    plotshape(LOTT * 1.0005 if sellSignallc and showsignalsc else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
