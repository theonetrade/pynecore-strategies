"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, format, hl2, input,
    location, math, na, nz, ohlc4, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('Profit Maximizer', 'PMax', overlay=True, format=format.price, precision=2, timeframe='', na_bool=True)
def main(
    src: Series[float] = input(hl2, title='Source'),
    Periods=input(title='ATR Length', defval=10),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    mav=input.string(title='Moving Average Type', defval='EMA', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    length=input.int(10, 'Moving Average Length', minval=1),
    changeATR=input(title='Change ATR Calculation Method ?', defval=True),
    Normalize=input(title='Normalize ATR ?', defval=False),
    showsupport=input(title='Show Moving Average?', defval=True),
    showsignalsk=input(title='Show Crossing Signals?', defval=True),
    showsignalsc=input(title='Show Price/Pmax Crossing Signals?', defval=False),
    highlighting=input(title='Highlighter On/Off ?', defval=True)
):
    atr2 = ta.sma(ta.tr, Periods)
    atr = ta.atr(Periods) if changeATR else atr2
    valpha = 2 / (length + 1)
    vud1 = src - src[1] if src > src[1] else 0
    vdd1 = src[1] - src if src < src[1] else 0
    vUD = math.sum(vud1, 9)
    vDD = math.sum(vdd1, 9)
    vCMO = nz((vUD - vDD) / (vUD + vDD))
    VAR: Series[float] = 0.0
    VAR = nz(valpha * math.abs(vCMO) * src) + (1 - valpha * math.abs(vCMO)) * nz(VAR[1])
    wwalpha = 1 / length
    WWMA: Series[float] = 0.0
    WWMA = wwalpha * src + (1 - wwalpha) * nz(WWMA[1])
    zxLag = length / 2 if length / 2 == math.round(length / 2) else (length - 1) / 2
    zxEMAData = src + src - src[zxLag]
    ZLEMA = ta.ema(zxEMAData, length)
    lrc = ta.linreg(src, length, 0)
    lrc1 = ta.linreg(src, length, 1)
    lrs = lrc - lrc1
    TSF = ta.linreg(src, length, 0) + lrs
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
    longStop: Series = MAvg - Multiplier * atr / close if Normalize else MAvg - Multiplier * atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
    shortStop: Series = MAvg + Multiplier * atr / close if Normalize else MAvg + Multiplier * atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if MAvg < shortStopPrev else shortStop
    dir: Series[int] = 1
    dir = nz(dir[1], dir)
    dir = 1 if dir == -1 and MAvg > shortStopPrev else -1 if dir == 1 and MAvg < longStopPrev else dir
    PMax = longStop if dir == 1 else shortStop
    plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Moving Avg Line')
    pALL = plot(PMax, color=color.new(color.red, 0), linewidth=2, title='PMax')
    alertcondition(ta.cross(MAvg, PMax), title='Cross Alert', message='PMax - Moving Avg Crossing!')
    alertcondition(ta.crossover(MAvg, PMax), title='Crossover Alarm', message='Moving Avg BUY SIGNAL!')
    alertcondition(ta.crossunder(MAvg, PMax), title='Crossunder Alarm', message='Moving Avg SELL SIGNAL!')
    alertcondition(ta.cross(src, PMax), title='Price Cross Alert', message='PMax - Price Crossing!')
    alertcondition(ta.crossover(src, PMax), title='Price Crossover Alarm', message='PRICE OVER PMax - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, PMax), title='Price Crossunder Alarm', message='PRICE UNDER PMax - SELL SIGNAL!')
    buySignalk = ta.crossover(MAvg, PMax)
    plotshape(PMax * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, PMax)
    plotshape(PMax * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    buySignalc = ta.crossover(src, PMax)
    plotshape(PMax * 0.995 if buySignalc and showsignalsc else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossunder(src, PMax)
    plotshape(PMax * 1.005 if sellSignallc and showsignalsc else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
