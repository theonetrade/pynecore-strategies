"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, currency, display, fill, high, hl2, input, location, low,
    math, na, nz, ohlc4, plot, plotchar, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Series


@script.strategy('Y-Profit Maximizer Strategy with Exit Points', shorttitle='Y-PMax Strategy with Exit Points', overlay=True, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, currency=currency.USD, commission_value=0.1, commission_type=strategy.commission.percent, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    baslik1=input(title='-------------------- PMax Setttings -------------------', defval=False),
    src: Series[float] = input(hl2, title='Source'),
    Periods=input(title='ATR Length', defval=10),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    mav=input.string(title='Moving Average Type', defval='ZLEMA', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    length=input.int(13, 'Moving Average Length', minval=1),
    changeATR=input(title='Change ATR calculation Method?', defval=True),
    showsupport=input(title='Show Moving Average?', defval=False),
    showsignalsk=input(title='Show Buy sell signals?', defval=True),
    showsignalsc=input(title='Show Price/Pmax cross signals?', defval=False),
    highlighting=input(title='Cloud On/Off?', defval=False),
    baslik4=input(title='-------------------- T3 Setttings --------------------', defval=False),
    length1=input(89, 'T3 Length'),
    length2=input(5, 'T3 Filter Length'),
    a1=input(0.84, 'T3 Volume Factor'),
    length12=input(5, 'Fibo T3 Length'),
    a12=input(0.618, 'T3 Fibo Volume Factor'),
    T31Show=input(title='Show T3?', defval=False),
    T32Show=input(title='T3 Filter On/Off?', defval=False),
    T3FiboLine=input(False, title='T3 Fibonacci Lines?'),
    baslik7=input(title='---------------- Take Profit Setttings --------------', defval=False),
    len=input(25, 'Snake Length'),
    domcycle=input.int(20, minval=10, title='Dominant Cycle Length'),
    rapida=input(8, 'Fast Avg'),
    lenta=input(26, 'Slow Avg'),
    stdv=input(0.8, 'Length'),
    tpfiltre=input(False, title='TP Filter avg2/avg4?'),
    tplevelshow=input(False, title='TP Level and Exit Level Count On/Off?'),
    tp1show=input(False, title='Early TP Signals On/Off ?'),
    baslik8=input(title='------------------- MOST Setttings ------------------', defval=False),
    src_most: Series[float] = input(close, 'Source'),
    AP2=input.int(defval=8, title='Length', minval=1),
    __input_32__=input.float(defval=2, title='Percent', minval=0.1),
    mav1=input.string(title='Moving Average Type', defval='ZLEMA', options=('VAR', 'ZLEMA')),
    plotbuysell=input(True, 'Buy/Sell Shapes On/Off ?')
):
    a13: float = 0.84
    shownum: bool = True
    AF2 = __input_32__ / 100
    e1 = ta.ema((high + low + 2 * close) / 4, length1)
    e2 = ta.ema(e1, length1)
    e3 = ta.ema(e2, length1)
    e4 = ta.ema(e3, length1)
    e5 = ta.ema(e4, length1)
    e6 = ta.ema(e5, length1)
    c1 = -a1 * a1 * a1
    c2 = 3 * a1 * a1 + 3 * a1 * a1 * a1
    c3 = -6 * a1 * a1 - 3 * a1 - 3 * a1 * a1 * a1
    c4 = 1 + 3 * a1 + a1 * a1 * a1 + 3 * a1 * a1
    T3: Series = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    e13 = ta.ema((high + low + 2 * close) / 4, length2)
    e23 = ta.ema(e13, length2)
    e33 = ta.ema(e23, length2)
    e43 = ta.ema(e33, length2)
    e53 = ta.ema(e43, length2)
    e63 = ta.ema(e53, length2)
    c13 = -a13 * a13 * a13
    c23 = 3 * a13 * a13 + 3 * a13 * a13 * a13
    c33 = -6 * a13 * a13 - 3 * a13 - 3 * a13 * a13 * a13
    c43 = 1 + 3 * a13 + a13 * a13 * a13 + 3 * a13 * a13
    T33: Series = c13 * e63 + c23 * e53 + c33 * e43 + c43 * e33
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
        if mav == 'T3':
            ma = T3
        return ma

    MAvg: Series = getMA(src, length)
    longStop: Series = MAvg - Multiplier * atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
    shortStop: Series = MAvg + Multiplier * atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if MAvg < shortStopPrev else shortStop
    dir: Series[int] = 1
    dir = nz(dir[1], dir)
    dir = 1 if dir == -1 and MAvg > shortStopPrev else -1 if dir == 1 and MAvg < longStopPrev else dir
    PMax: Series = longStop if dir == 1 else shortStop
    zxLag1 = AP2 / 2 if AP2 / 2 == math.round(AP2 / 2) else (AP2 - 1) / 2
    zxEMAData1 = src_most + src_most - src_most[zxLag1]
    ZLEMA1 = ta.ema(zxEMAData1, AP2)
    valpha1 = 2 / (AP2 + 1)
    vud2 = src_most - src_most[1] if src_most > src_most[1] else 0
    vdd2 = src_most[1] - src_most if src_most < src_most[1] else 0
    vUD1 = math.sum(vud2, 9)
    vDD1 = math.sum(vdd2, 9)
    vCMO1 = nz((vUD1 - vDD1) / (vUD1 + vDD1))
    VAR1: Series[float] = 0.0
    VAR1 = nz(valpha1 * math.abs(vCMO1) * src_most) + (1 - valpha1 * math.abs(vCMO1)) * nz(VAR1[1])
    def getMA1(src, length):
        ma1: float = 0.0
        if mav1 == 'VAR':
            ma1 = VAR1
        __block_result__ = na
        if mav1 == 'ZLEMA':
            ma1 = ZLEMA1
            __block_result__ = ma1
        return __block_result__

    Trail1: Series = getMA1(src, length)
    SL2 = Trail1 * AF2
    Trail2: Series[float] = 0.0
    iff_1 = Trail1 - SL2 if Trail1 > nz(Trail2[1], 0) else Trail1 + SL2
    iff_2 = math.min(nz(Trail2[1], 0), Trail1 + SL2) if Trail1 < nz(Trail2[1], 0) and Trail1[1] < nz(Trail2[1], 0) else iff_1
    Trail2 = math.max(nz(Trail2[1], 0), Trail1 - SL2) if Trail1 > nz(Trail2[1], 0) and Trail1[1] > nz(Trail2[1], 0) else iff_2
    Buy = ta.crossover(Trail1, Trail2)
    Sell = ta.crossunder(Trail1, Trail2)
    iff_3 = -1 if Trail2 > Trail1 else 0
    SR = 1 if Trail1 > Trail2 else iff_3
    col1 = T3 > T3[1]
    col3 = T3 < T3[1]
    col4 = T33 > T33[1]
    col5 = T33 < T33[1]
    color_1 = color.green if col1 else color.red if col3 else color.yellow
    color_4 = color.green if col4 else color.red if col5 else color.yellow
    e12 = ta.ema((high + low + 2 * close) / 4, length12)
    e22 = ta.ema(e12, length12)
    e32 = ta.ema(e22, length12)
    e42 = ta.ema(e32, length12)
    e52 = ta.ema(e42, length12)
    e62 = ta.ema(e52, length12)
    c12 = -a12 * a12 * a12
    c22 = 3 * a12 * a12 + 3 * a12 * a12 * a12
    c32 = -6 * a12 * a12 - 3 * a12 - 3 * a12 * a12 * a12
    c42 = 1 + 3 * a12 + a12 * a12 * a12 + 3 * a12 * a12
    T32: Series = c12 * e62 + c22 * e52 + c32 * e42 + c42 * e32
    col12 = T32 > T32[1]
    col32 = T32 < T32[1]
    h: Series = ta.ema(high, len)
    l: Series = ta.ema(low, len)
    hp = h / h[len]
    lp = l / l[len]
    avg = math.avg(hp, lp)
    havg = ta.ema(ta.highest(avg, len), len)
    lavg = ta.ema(ta.lowest(avg, len), len)
    avg2 = math.avg(havg, lavg)
    avg3 = math.avg(havg, avg2)
    avg4 = math.avg(havg, avg3)
    dif = havg - avg2
    ust = havg + dif
    alt = lavg - dif
    SDev: float = 0.0
    banda_supe: float = 0.0
    banda_inf: float = 0.0
    m_rapida = ta.ema(close, rapida)
    m_lenta = ta.ema(close, lenta)
    BBMacd = m_rapida - m_lenta
    Avg = ta.ema(BBMacd, 9)
    SDev = ta.stdev(BBMacd, 9)
    banda_supe = Avg + stdv * SDev
    banda_inf = Avg - stdv * SDev
    color2 = color.blue if col12 else color.purple if col32 else color.yellow
    TS1 = plot(Trail1, 'ExMov', style=plot.style_line, color=color.blue if Trail1 > Trail2 else color.yellow, linewidth=2)
    TS2 = plot(Trail2, 'Most', style=plot.style_line, color=color.green if Trail1 > Trail2 else color.red, linewidth=2)
    tp1 = ta.crossunder(BBMacd, banda_supe) and avg > avg2 and (MAvg > PMax) and (nz(MAvg[10]) > nz(PMax[10])) if tpfiltre else ta.crossunder(BBMacd, banda_supe) and avg > avg4 and (MAvg > PMax) and (nz(MAvg[15]) > nz(PMax[15]))
    plotshape(tp1 and tp1show, title='TP1', text='TP1', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.aqua, 0), textcolor=color.new(color.white, 0))
    plot(T3 if T31Show else na, color=color_1, linewidth=3, title='T3')
    plot(T33 if T32Show else na, color=color_4, linewidth=3, title='T3 Filter')
    plot(T32 if T3FiboLine and cast_bool(T32) else na, color=color2, linewidth=2, title='T3fibo')
    plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Moving Avg Line')
    pALL = plot(PMax, color=color.new(color.red, 100), linewidth=2, title='PMax')
    buySignalk = ta.crossover(MAvg, PMax)
    plotshape(PMax * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='BUY', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, PMax)
    plotshape(PMax * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='SELL', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    buySignalc = ta.crossover(src, PMax)
    plotshape(PMax * 0.995 if buySignalc and showsignalsc else na, title='Buy-Price', text='BUY', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossunder(src, PMax)
    plotshape(PMax * 1.005 if sellSignallc and showsignalsc else na, title='Sell-Price', text='SELL', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='Up Trend Cloud', color=longFillColor)
    fill(mPlot, pALL, title='Down Trend Cloud', color=shortFillColor)
    tplevel: Series[int] = 0
    tplevel = 0 if sellSignallk or MAvg < PMax else 0 if Trail1 < Trail2 else 2 if tp1 and nz(tplevel[1]) == 1 else 1 if nz(tplevel[1]) == 1 else 2 if nz(tplevel[1]) == 2 else 1
    exitlevel: Series[int] = 0
    exitlevel = 0 if sellSignallk or MAvg < PMax else 2 if Sell and nz(tplevel[1]) == 2 and (nz(exitlevel[1]) == 1) else 3 if Sell and nz(tplevel[1]) == 2 and (nz(exitlevel[1]) == 2) else 4 if Sell and nz(tplevel[1]) == 2 and (nz(exitlevel[1]) == 3) else 5 if Sell and nz(tplevel[1]) == 2 and (nz(exitlevel[1]) == 4) else 1 if nz(exitlevel[1]) == 1 else 2 if nz(exitlevel[1]) == 2 else 3 if nz(exitlevel[1]) == 3 else 4 if nz(exitlevel[1]) == 4 else 5 if nz(exitlevel[1]) == 5 else 1
    plotchar(tplevel == 0 and tplevelshow, char='0', color=color.new(color.green, 0))
    plotchar(tplevel == 1 and tplevelshow, char='1', color=color.new(color.green, 0))
    plotchar(tplevel == 2 and tplevelshow, char='2', color=color.new(color.green, 0))
    plotshape(exitlevel == 0 and tplevelshow, text='0', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(exitlevel == 1 and tplevelshow, text='1', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(exitlevel == 2 and tplevelshow, text='2', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(exitlevel == 3 and tplevelshow, text='3', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(exitlevel == 4 and tplevelshow, text='4', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(exitlevel == 5 and tplevelshow, text='5', location=location.belowbar, style=shape.triangledown, color=color.new(color.red, 0))
    plotshape(nz(tplevel[1]) == 2 and Sell and (exitlevel >= 2), title='TP', text='TP', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.lime, 0), textcolor=color.new(color.white, 0))
    if buySignalk:
        strategy.entry('Buy', strategy.long)
    if nz(tplevel[1]) == 2 and Sell and (exitlevel == 2):
        strategy.exit('Exit1', from_entry='Buy', limit=close, qty_percent=25)
    if nz(tplevel[1]) == 3 and Sell and (exitlevel == 3):
        strategy.exit('Exit2', from_entry='Buy', limit=close, qty_percent=33.3)
    if nz(tplevel[1]) == 4 and Sell and (exitlevel == 3):
        strategy.exit('Exit3', from_entry='Buy', limit=close, qty_percent=50)
    if nz(tplevel[1]) == 5 and Sell and (exitlevel == 3):
        strategy.exit('Exit4', from_entry='Buy', limit=close)
    if sellSignallk:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
