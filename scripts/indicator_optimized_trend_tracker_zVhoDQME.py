"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, input, location, math, na,
    nz, ohlc4, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('Optimized Trend Tracker', 'OTT', overlay=True, na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    length=input.int(2, 'OTT Period', minval=1),
    percent=input.float(1.4, 'OTT Percent', step=0.1, minval=0),
    showsupport=input(title='Show Support Line?', defval=True),
    showsignalsk=input(title='Show Support Line Crossing Signals?', defval=True),
    showsignalsc=input(title='Show Price/OTT Crossing Signals?', defval=False),
    highlight=input(title='Show OTT Color Changes?', defval=False),
    showsignalsr=input(title='Show OTT Color Change Signals?', defval=False),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
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
    OTT: Series = MT * (200 + percent) / 200 if MAvg > MT else MT * (200 - percent) / 200
    plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Support Line')
    OTTC = (color.green if OTT[2] > OTT[3] else color.red) if highlight else color.new('#B800D9')
    pALL = plot(nz(OTT[2]), color=OTTC, linewidth=2, title='OTT')
    alertcondition(ta.cross(OTT[2], OTT[3]), title='Color ALARM', message='OTT Has Changed Color!')
    alertcondition(ta.crossover(OTT[2], OTT[3]), title='GREEN ALERT', message='OTT GREEN BUY SIGNAL!')
    alertcondition(ta.crossunder(OTT[2], OTT[3]), title='RED ALERT', message='OTT RED SELL SIGNAL!')
    alertcondition(ta.cross(MAvg, OTT[2]), title='Cross Alert', message='OTT - Support Line Crossing!')
    alertcondition(ta.crossover(MAvg, OTT[2]), title='Crossover Alarm', message='Support Line BUY SIGNAL!')
    alertcondition(ta.crossunder(MAvg, OTT[2]), title='Crossunder Alarm', message='Support Line SELL SIGNAL!')
    alertcondition(ta.cross(src, OTT[2]), title='Price Cross Alert', message='OTT - Price Crossing!')
    alertcondition(ta.crossover(src, OTT[2]), title='Price Crossover Alarm', message='PRICE OVER OTT - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, OTT[2]), title='Price Crossunder Alarm', message='PRICE UNDER OTT - SELL SIGNAL!')
    buySignalk = ta.crossover(MAvg, OTT[2])
    plotshape(OTT * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, OTT[2])
    plotshape(OTT * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    buySignalc = ta.crossover(src, OTT[2])
    plotshape(OTT * 0.995 if buySignalc and showsignalsc else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossunder(src, OTT[2])
    plotshape(OTT * 1.005 if sellSignallc and showsignalsc else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > OTT else na) if highlighting else na
    shortFillColor = (color.red if MAvg < OTT else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)
    buySignalr = ta.crossover(OTT[2], OTT[3])
    plotshape(OTT * 0.995 if buySignalr and showsignalsr else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallr = ta.crossunder(OTT[2], OTT[3])
    plotshape(OTT * 1.005 if sellSignallr and showsignalsr else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)