"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, input, math, na, nz, script, strategy, ta, time,
    timestamp
)
from pynecore.types import Series


@script.strategy('MACD ReLoaded', 'MACDReSt', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    src: Series[float] = input(close, title='Source'),
    length=input.int(12, 'Short Moving Average Length', minval=1),
    length1=input.int(26, 'Long Moving Average Length', minval=1),
    length2=input.int(9, 'Trigger Length', minval=1),
    T3a1=input.float(0.7, 'TILLSON T3 Volume Factor', step=0.1),
    barcoloring=input(title='Bar Coloring On/Off ?', defval=True),
    mav=input.string(title='Moving Average Type', defval='VAR', options=('SMA', 'EMA', 'WMA', 'DEMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF', 'HULL', 'TILL')),
    FromMonth=input.int(defval=9, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2018, title='From Year', minval=999),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=999)
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
    T3e1 = ta.ema(src, length)
    T3e2 = ta.ema(T3e1, length)
    T3e3 = ta.ema(T3e2, length)
    T3e4 = ta.ema(T3e3, length)
    T3e5 = ta.ema(T3e4, length)
    T3e6 = ta.ema(T3e5, length)
    T3c1 = -T3a1 * T3a1 * T3a1
    T3c2 = 3 * T3a1 * T3a1 + 3 * T3a1 * T3a1 * T3a1
    T3c3 = -6 * T3a1 * T3a1 - 3 * T3a1 - 3 * T3a1 * T3a1 * T3a1
    T3c4 = 1 + 3 * T3a1 + T3a1 * T3a1 * T3a1 + 3 * T3a1 * T3a1
    T3 = T3c1 * T3e6 + T3c2 * T3e5 + T3c3 * T3e4 + T3c4 * T3e3
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
        if mav == 'TILL':
            ma = T3
        return ma

    MA12 = getMA(src, length)
    def Var_Func1(src: Series, length1):
        valpha1 = 2 / (length1 + 1)
        vud11 = src - src[1] if src > src[1] else 0
        vdd11 = src[1] - src if src < src[1] else 0
        vUD1 = math.sum(vud11, 9)
        vDD1 = math.sum(vdd11, 9)
        vCMO1 = nz((vUD1 - vDD1) / (vUD1 + vDD1))
        VAR1: Series[float] = 0.0
        VAR1 = nz(valpha1 * math.abs(vCMO1) * src) + (1 - valpha1 * math.abs(vCMO1)) * nz(VAR1[1])
        return VAR1

    VAR1 = Var_Func1(src, length1)
    DEMA1 = 2 * ta.ema(src, length1) - ta.ema(ta.ema(src, length1), length1)
    def Wwma_Func1(src, length1):
        wwalpha1 = 1 / length1
        WWMA1: Series[float] = 0.0
        WWMA1 = wwalpha1 * src + (1 - wwalpha1) * nz(WWMA1[1])
        return WWMA1

    WWMA1 = Wwma_Func1(src, length1)
    def Zlema_Func1(src: Series, length1):
        zxLag1 = length1 / 2 if length1 / 2 == math.round(length1 / 2) else (length1 - 1) / 2
        zxEMAData1 = src + src - src[zxLag1]
        ZLEMA1 = ta.ema(zxEMAData1, length1)
        return ZLEMA1

    ZLEMA1 = Zlema_Func1(src, length1)
    def Tsf_Func1(src, length1):
        lrc1 = ta.linreg(src, length1, 0)
        lrc11 = ta.linreg(src, length1, 1)
        lrs1 = lrc1 - lrc11
        TSF1 = ta.linreg(src, length1, 0) + lrs1
        return TSF1

    TSF1 = Tsf_Func1(src, length1)
    HMA1 = ta.wma(2 * ta.wma(src, length1 / 2) - ta.wma(src, length1), math.round(math.sqrt(length1)))
    T3e11 = ta.ema(src, length1)
    T3e21 = ta.ema(T3e11, length1)
    T3e31 = ta.ema(T3e21, length1)
    T3e41 = ta.ema(T3e31, length1)
    T3e51 = ta.ema(T3e41, length1)
    T3e61 = ta.ema(T3e51, length1)
    T3c11 = -T3a1 * T3a1 * T3a1
    T3c21 = 3 * T3a1 * T3a1 + 3 * T3a1 * T3a1 * T3a1
    T3c31 = -6 * T3a1 * T3a1 - 3 * T3a1 - 3 * T3a1 * T3a1 * T3a1
    T3c41 = 1 + 3 * T3a1 + T3a1 * T3a1 * T3a1 + 3 * T3a1 * T3a1
    T31 = T3c11 * T3e61 + T3c21 * T3e51 + T3c31 * T3e41 + T3c41 * T3e31
    def getMA1(src, length1):
        ma1: float = 0.0
        if mav == 'SMA':
            ma1 = ta.sma(src, length1)
        if mav == 'EMA':
            ma1 = ta.ema(src, length1)
        if mav == 'WMA':
            ma1 = ta.wma(src, length1)
        if mav == 'DEMA':
            ma1 = DEMA1
        if mav == 'TMA':
            ma1 = ta.sma(ta.sma(src, math.ceil(length1 / 2)), math.floor(length1 / 2) + 1)
        if mav == 'VAR':
            ma1 = VAR1
        if mav == 'WWMA':
            ma1 = WWMA1
        if mav == 'ZLEMA':
            ma1 = ZLEMA1
        if mav == 'TSF':
            ma1 = TSF1
        if mav == 'HULL':
            ma1 = HMA1
        if mav == 'TILL':
            ma1 = T31
        return ma1

    MA26 = getMA1(src, length1)
    src2 = MA12 - MA26
    def Var_Func2(src2: Series, length2):
        valpha2 = 2 / (length2 + 1)
        vud12 = src2 - src2[1] if src2 > src2[1] else 0
        vdd12 = src2[1] - src2 if src2 < src2[1] else 0
        vUD2 = math.sum(vud12, 9)
        vDD2 = math.sum(vdd12, 9)
        vCMO2 = nz((vUD2 - vDD2) / (vUD2 + vDD2))
        VAR2: Series[float] = 0.0
        VAR2 = nz(valpha2 * math.abs(vCMO2) * src2) + (1 - valpha2 * math.abs(vCMO2)) * nz(VAR2[1])
        return VAR2

    VAR2 = Var_Func2(src2, length2)
    DEMA2 = 2 * ta.ema(src2, length2) - ta.ema(ta.ema(src2, length2), length2)
    def Wwma_Func2(src2, length2):
        wwalpha2 = 1 / length2
        WWMA2: Series[float] = 0.0
        WWMA2 = wwalpha2 * src2 + (1 - wwalpha2) * nz(WWMA2[1])
        return WWMA2

    WWMA2 = Wwma_Func2(src2, length2)
    def Zlema_Func2(src2: Series, length2):
        zxLag2 = length2 / 2 if length2 / 2 == math.round(length2 / 2) else (length2 - 1) / 2
        zxEMAData2 = src2 + src2 - src2[zxLag2]
        ZLEMA2 = ta.ema(zxEMAData2, length2)
        return ZLEMA2

    ZLEMA2 = Zlema_Func2(src2, length2)
    def Tsf_Func2(src2, length2):
        lrc2 = ta.linreg(src2, length2, 0)
        lrc12 = ta.linreg(src2, length2, 1)
        lrs2 = lrc2 - lrc12
        TSF2 = ta.linreg(src2, length2, 0) + lrs2
        return TSF2

    TSF2 = Tsf_Func2(src2, length2)
    HMA2 = ta.wma(2 * ta.wma(src2, length2 / 2) - ta.wma(src2, length2), math.round(math.sqrt(length2)))
    T3e12 = ta.ema(src2, length2)
    T3e22 = ta.ema(T3e12, length2)
    T3e32 = ta.ema(T3e22, length2)
    T3e42 = ta.ema(T3e32, length2)
    T3e52 = ta.ema(T3e42, length2)
    T3e62 = ta.ema(T3e52, length2)
    T3c12 = -T3a1 * T3a1 * T3a1
    T3c22 = 3 * T3a1 * T3a1 + 3 * T3a1 * T3a1 * T3a1
    T3c32 = -6 * T3a1 * T3a1 - 3 * T3a1 - 3 * T3a1 * T3a1 * T3a1
    T3c42 = 1 + 3 * T3a1 + T3a1 * T3a1 * T3a1 + 3 * T3a1 * T3a1
    T32 = T3c12 * T3e62 + T3c22 * T3e52 + T3c32 * T3e42 + T3c42 * T3e32
    def getMA2(src2, length2):
        ma2: float = 0.0
        if mav == 'SMA':
            ma2 = ta.sma(src2, length2)
        if mav == 'EMA':
            ma2 = ta.ema(src2, length2)
        if mav == 'WMA':
            ma2 = ta.wma(src2, length2)
        if mav == 'DEMA':
            ma2 = DEMA2
        if mav == 'TMA':
            ma2 = ta.sma(ta.sma(src2, math.ceil(length2 / 2)), math.floor(length2 / 2) + 1)
        if mav == 'VAR':
            ma2 = VAR2
        if mav == 'WWMA':
            ma2 = WWMA2
        if mav == 'ZLEMA':
            ma2 = ZLEMA2
        if mav == 'TSF':
            ma2 = TSF2
        if mav == 'HULL':
            ma2 = HMA2
        if mav == 'TILL':
            ma2 = T32
        return ma2

    MATR = getMA2(MA12 - MA26, length2)
    hist = src2 - MATR
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    buySignal = ta.crossover(hist, 0)
    if ta.crossover(hist, 0):
        strategy.entry('MacdLong', strategy.long, comment='MacdLong')
    sellSignal = ta.crossunder(hist, 0)
    if ta.crossunder(hist, 0):
        strategy.entry('MacdShort', strategy.short, comment='MacdShort')
    buy1: Series = ta.barssince(buySignal)
    sell1: Series = ta.barssince(sellSignal)
    color1 = color.green if buy1[1] < sell1[1] else color.red if buy1[1] > sell1[1] else na
    barcolor(color1 if barcoloring else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
