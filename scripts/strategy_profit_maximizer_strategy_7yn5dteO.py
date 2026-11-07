"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, display, fill, high, hl2, input,
    location, low, math, na, nz, ohlc4, plot, plotshape, script, shape, size, strategy, syminfo,
    ta
)
from pynecore.types import Persistent, Series


@script.strategy('Profit Maximizer Strategy', 'PMax strat', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(hl2, title='Source'),
    Periods=input(title='ATR Length', defval=10),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    length=input.int(12, 'Moving Average Length', minval=1),
    changeATR=input(title='Change ATR Calculation Method ?', defval=False),
    showsupport=input(title='Show Moving Average?', defval=True),
    showsignalsk=input(title='Show Crossing Signals?', defval=True),
    showsignalsc=input(title='Show Price/Pmax Crossing Signals?', defval=False),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    fast_length=input(title='Fast Length', defval=12),
    slow_length=input(title='Slow Length', defval=26),
    srcc: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input(title='Simple MA(Oscillator)', defval=True),
    sma_signal=input(title='Simple MA(Signal Line)', defval=False),
    start=input(0.02),
    increment=input(0.03),
    maximum=input(0.3),
    CCI=input(20),
    ATR=input(5),
    Multiplierc=input(1, title='ATR Multiplier'),
    original=input(True, title='original coloring'),
    srce: Series[float] = input(close, title='source'),
    sma1length=input(5),
    sma2length=input(35),
    UsePercent=input(title='Show Dif as percent of current Candle', defval=True),
    tp=input(0.35, title='tp'),
    sl=input(0.01, title='sl')
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
    plotshape(PMax * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, PMax)
    plotshape(PMax * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    buySignalc = ta.crossover(src, PMax)
    sellSignallc = ta.crossunder(src, PMax)
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)
    uptrend: Persistent[bool] = na(bool)
    EP: Persistent[float] = na(float)
    SAR: Persistent[float] = na(float)
    AF: Persistent[float] = start
    nextBarSAR: Persistent[float] = na(float)
    if bar_index > 0:
        firstTrendBar: bool = False
        SAR = nextBarSAR
        if bar_index == 1:
            prevSAR: float = na(float)
            prevEP: float = na(float)
            lowPrev = low[1]
            highPrev = high[1]
            closeCur = close
            closePrev = close[1]
            if closeCur > closePrev:
                uptrend = True
                EP = high
                prevSAR = lowPrev
                prevEP = high
            else:
                uptrend = False
                EP = low
                prevSAR = highPrev
                prevEP = low
            firstTrendBar = True
            SAR = prevSAR + start * (prevEP - prevSAR)
        if uptrend:
            if SAR > low:
                firstTrendBar = True
                uptrend = False
                SAR = math.max(EP, high)
                EP = low
                AF = start
        else:
            if SAR < high:
                firstTrendBar = True
                uptrend = True
                SAR = math.min(EP, low)
                EP = high
                AF = start
        if not firstTrendBar:
            if uptrend:
                if high > EP:
                    EP = high
                    AF = math.min(AF + increment, maximum)
            else:
                if low < EP:
                    EP = low
                    AF = math.min(AF + increment, maximum)
        if uptrend:
            SAR = math.min(SAR, low[1])
            if bar_index > 1:
                SAR = math.min(SAR, low[2])
        else:
            SAR = math.max(SAR, high[1])
            if bar_index > 1:
                SAR = math.max(SAR, high[2])
        nextBarSAR = SAR + AF * (EP - SAR)
    fast_ma = ta.sma(srcc, fast_length) if sma_source else ta.ema(srcc, fast_length)
    slow_ma = ta.sma(srcc, slow_length) if sma_source else ta.ema(srcc, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal else ta.ema(macd, signal_length)
    hist = macd - signal
    thisCCI: Series = ta.cci(close, CCI)
    lastCCI = nz(thisCCI[1])
    bufferDn: Series = high + Multiplierc * ta.sma(ta.tr, ATR)
    bufferUp: Series = low - Multiplierc * ta.sma(ta.tr, ATR)
    if thisCCI >= 0 and lastCCI < 0:
        bufferUp = bufferDn[1]
    if thisCCI <= 0 and lastCCI > 0:
        bufferDn = bufferUp[1]
    if thisCCI >= 0:
        if bufferUp < bufferUp[1]:
            bufferUp = bufferUp[1]
    else:
        if thisCCI <= 0:
            if bufferDn > bufferDn[1]:
                bufferDn = bufferDn[1]
    x: Series[float] = 0.0
    x = bufferUp if thisCCI >= 0 else bufferDn if thisCCI <= 0 else x[1]
    swap: Series[float] = 0.0
    swap = 1 if x > x[1] else -1 if x < x[1] else swap[1]
    swap2 = color.lime if swap == 1 else color.red
    swap3 = color.lime if thisCCI >= 0 else color.red
    swap4 = swap3 if original else swap2
    sma_1 = ta.sma(srce, sma1length)
    sma_2 = ta.sma(srce, sma2length)
    sma_3 = ta.sma(srce, sma1length)
    sma_4 = ta.sma(srce, sma2length)
    smadif = (sma_1 - sma_2) / srce * 100 if UsePercent else sma_3 - sma_4
    col = color.red if smadif <= 0 else color.green
    longC = hist > 0 and uptrend and (swap4 == color.lime) and buySignalk
    shortC = hist < 0 and (not uptrend) and (swap4 == color.red) and sellSignallk
    if longC:
        strategy.entry('long', strategy.long)
    if shortC:
        strategy.entry('short', strategy.short)
    strategy.exit('x_long', 'long', loss=close * sl / syminfo.mintick, profit=close * tp / syminfo.mintick, alert_message='closelong')
    strategy.exit('x_short', 'short', loss=close * sl / syminfo.mintick, profit=close * tp / syminfo.mintick, alert_message='closeshort')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)