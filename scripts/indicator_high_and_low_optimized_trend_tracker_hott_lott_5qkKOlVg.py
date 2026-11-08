"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, high, input, low, math, na,
    nz, plot, script, ta
)
from pynecore.types import Series


@script.indicator('HIGH AND LOW Optimized Trend Tracker', 'HL OTT', overlay=True)
def main(
    length=input.int(2, 'OTT Period', minval=1),
    percent=input.float(0.6, 'OTT Optimization Coeff', step=0.1, minval=0),
    hllength=input.int(10, 'Highest and Lowest Length', minval=1),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'DEMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF', 'HULL'))
):
    src = ta.highest(high, hllength)
    srcl = ta.lowest(low, hllength)
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

    VARl = Var_Funcl(srcl, length)
    DEMAl = 2 * ta.ema(srcl, length) - ta.ema(ta.ema(srcl, length), length)
    def Wwma_Funcl(srcl, length):
        wwalphal = 1 / length
        WWMAl: Series[float] = 0.0
        WWMAl = wwalphal * srcl + (1 - wwalphal) * nz(WWMAl[1])
        return WWMAl

    WWMAl = Wwma_Funcl(srcl, length)
    def Zlema_Funcl(srcl: Series, length):
        zxLagl = length / 2 if length / 2 == math.round(length / 2) else (length - 1) / 2
        zxEMADatal = srcl + srcl - srcl[zxLagl]
        ZLEMAl = ta.ema(zxEMADatal, length)
        return ZLEMAl

    ZLEMAl = Zlema_Funcl(srcl, length)
    def Tsf_Funcl(srcl, length):
        lrcl = ta.linreg(srcl, length, 0)
        lrc1l = ta.linreg(srcl, length, 1)
        lrsl = lrcl - lrc1l
        TSFl = ta.linreg(srcl, length, 0) + lrsl
        return TSFl

    TSFl = Tsf_Funcl(srcl, length)
    HMAl = ta.wma(2 * ta.wma(srcl, length / 2) - ta.wma(srcl, length), math.round(math.sqrt(length)))
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

    def getMAl(srcl, length):
        mal: float = 0.0
        if mav == 'SMA':
            mal = ta.sma(srcl, length)
        if mav == 'EMA':
            mal = ta.ema(srcl, length)
        if mav == 'WMA':
            mal = ta.wma(srcl, length)
        if mav == 'DEMA':
            mal = DEMAl
        if mav == 'TMA':
            mal = ta.sma(ta.sma(srcl, math.ceil(length / 2)), math.floor(length / 2) + 1)
        if mav == 'VAR':
            mal = VARl
        if mav == 'WWMA':
            mal = WWMAl
        if mav == 'ZLEMA':
            mal = ZLEMAl
        if mav == 'TSF':
            mal = TSFl
        if mav == 'HULL':
            mal = HMAl
        return mal

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
    HOTTC = color.blue
    MAvgl = getMAl(srcl, length)
    farkl = MAvgl * percent * 0.01
    longStopl: Series = MAvgl - farkl
    longStopPrevl = nz(longStopl[1], longStopl)
    longStopl = math.max(longStopl, longStopPrevl) if MAvgl > longStopPrevl else longStopl
    shortStopl: Series = MAvgl + farkl
    shortStopPrevl = nz(shortStopl[1], shortStopl)
    shortStopl = math.min(shortStopl, shortStopPrevl) if MAvgl < shortStopPrevl else shortStopl
    dirl: Series[int] = 1
    dirl = nz(dirl[1], dirl)
    dirl = 1 if dirl == -1 and MAvgl > shortStopPrevl else -1 if dirl == 1 and MAvgl < longStopPrevl else dirl
    MTl = longStopl if dirl == 1 else shortStopl
    LOTT: Series = MTl * (200 + percent) / 200 if MAvgl > MTl else MTl * (200 - percent) / 200
    LOTTC = color.red
    HOTTLine = plot(nz(HOTT[2]), title='HOTT', color=color.new(HOTTC, 0), linewidth=2, style=plot.style_line)
    LOTTLine = plot(nz(LOTT[2]), title='LOTT', color=color.new(LOTTC, 0), linewidth=2, style=plot.style_line)
    FillColor = color.new(color.new('#9915FF'), 80) if highlighting else na
    fill(HOTTLine, LOTTLine, title='Highligter', color=FillColor)
    color1 = color.new('#00FFFF') if close > HOTT[2] else color.new('#FF00FF') if close < LOTT[2] else na
    barcolor(color1)
    alertcondition(ta.crossover(close, HOTT[2]), title='Price Crossover Alarm', message='PRICE OVER HOTT - BUY SIGNAL!')
    alertcondition(ta.crossunder(close, LOTT[2]), title='Price Crossunder Alarm', message='PRICE UNDER LOTT - SELL SIGNAL!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
