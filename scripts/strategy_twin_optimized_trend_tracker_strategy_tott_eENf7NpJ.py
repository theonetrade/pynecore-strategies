"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, display, fill, high, input, location, low, math, na, nz,
    ohlc4, plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Twin Optimized Trend Tracker', 'TOTT', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    length=input.int(40, 'OTT Period', minval=1),
    percent=input.float(1, 'Optimization Constant', step=0.1, minval=0),
    coeff=input.float(0.001, 'Twin OTT Coefficient', step=0.001, minval=0),
    showsupport=input(title='Show Support Line?', defval=True),
    showsignalsk=input(title='Show Signals?', defval=True),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    dummy0=input(True, title='=Backtest Inputs='),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromYear=input.int(defval=2005, title='From Year', minval=2005),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToYear=input.int(defval=9999, title='To Year', minval=2006)
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
    OTT = MT * (200 + percent) / 200 if MAvg > MT else MT * (200 - percent) / 200
    OTTup: Series = OTT * (1 + coeff)
    OTTdn: Series = OTT * (1 - coeff)
    PPLOT = plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Support Line')
    pALLup = plot(nz(OTTup[2]), color=color.new(color.green, 0), linewidth=2, title='OTTup')
    pALLdn = plot(nz(OTTdn[2]), color=color.new(color.red, 0), linewidth=2, title='OTTdown')
    buySignalk: Series = ta.crossover(MAvg, OTTup[2])
    sellSignalk: Series = ta.crossunder(MAvg, OTTdn[2])
    K1 = ta.barssince(buySignalk)
    K2 = ta.barssince(sellSignalk)
    O1 = ta.barssince(buySignalk[1])
    O2 = ta.barssince(sellSignalk[1])
    plotshape(math.min(low, OTTdn) if buySignalk and showsignalsk and (O1 > K2) else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(math.max(high, OTTup) if sellSignalk and showsignalsk and (O2 > K1) else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if O2 > K1 else na) if highlighting else na
    shortFillColor = (color.red if O1 > K2 else na) if highlighting else na
    fill(mPlot, PPLOT, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, PPLOT, title='DownTrend Highligter', color=shortFillColor)
    fill(pALLup, pALLdn, title='Flat Zone Highligter', color=color.new(color.blue, 90))
    Start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    Finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def Timerange():
        return True if time >= Start and time <= Finish else False

    if buySignalk:
        if Timerange():
            strategy.entry('Long', strategy.long)
    if sellSignalk:
        if Timerange():
            strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
