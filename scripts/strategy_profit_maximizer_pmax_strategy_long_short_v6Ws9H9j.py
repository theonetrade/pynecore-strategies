"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, color, currency, display, fill, hl2, input, math, na, nz,
    ohlc4, plot, script, strategy, ta
)
from pynecore.types import Series


@script.strategy('Profit Maximizer Strategy Long-Short', shorttitle='PMax-Strategy', overlay=True, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, currency=currency.USD, commission_value=0, commission_type=strategy.commission.percent, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(hl2, title='Source'),
    Periods=input(title='ATR Length', defval=10),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    mav=input.string(title='Moving Average Type', defval='EMA', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    length=input.int(10, 'Moving Average Length', minval=1),
    condition=input.string(title='Signal Type', defval='Only Crossing Signals', options=('Only Crossing Signals', 'Only Price/Pmax Crossing Signals')),
    changeATR=input(title='Change ATR Calculation Method ?', defval=True),
    showsupport=input(title='Show Moving Average?', defval=True),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    long_short=input(defval=False, title='Long-Short')
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
    longStop: Series = MAvg - Multiplier * atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
    shortStop: Series = MAvg + Multiplier * atr
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
    sellSignallk = ta.crossunder(MAvg, PMax)
    buySignalc = ta.crossover(src, PMax)
    sellSignallc = ta.crossunder(src, PMax)
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)
    if condition == 'Only Crossing Signals':
        if buySignalk:
            strategy.entry('BUY', strategy.long)
    else:
        if buySignalc:
            strategy.entry('BUY', strategy.long)
    if long_short:
        if condition == 'Only Crossing Signals':
            if sellSignallk:
                strategy.entry('SELL', strategy.short)
        else:
            if sellSignallc:
                strategy.entry('SELL', strategy.short)
    else:
        if condition == 'Only Crossing Signals':
            if sellSignallk:
                strategy.close('BUY')
        else:
            if sellSignallc:
                strategy.close('BUY')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
