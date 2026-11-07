"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, fill, input, math, na, nz, open, plot, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Color, Series


@script.strategy(title='Open Close Cross Strategy NoRepaint Version by JustUncleL', shorttitle='OCC Strategy NRP', overlay=True, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=10, calc_on_every_tick=False, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    useRes=input(defval=True, title='Use Alternate Resolution?'),
    intRs_=input(defval=6, title='Multiplier for Alernate Resolution'),
    basisType=input.string(defval='ZEMA', title='MA Type: ', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HullMA', 'ZEMA', 'SSMA', 'TMA')),
    basisLen=input.int(defval=8, title='MA Period', minval=1),
    scolor=input(False, title='Show coloured Bars to indicate Trend?'),
    tradeType=input.string('BOTH', title='What trades should be taken : ', options=('LONG', 'SHORT', 'BOTH', 'NONE')),
    slPoints=input.int(defval=0, title='Initial Stop Loss Points (zero to disable)', minval=0),
    tpPoints=input.int(defval=0, title='Initial Target Profit Points (zero for disable)', minval=0),
    testStartYear=input.int(2018, 'Backtest Start Year', minval=1980),
    testStartMonth=input.int(1, 'Backtest Start Month', minval=1, maxval=12),
    testStartDay=input.int(1, 'Backtest Start Day', minval=1, maxval=31),
    testStopYear=input.int(9999, 'Backtest Stop Year', minval=1980),
    testStopMonth=input.int(12, 'Backtest Stop Month', minval=1, maxval=12),
    testStopDay=input.int(31, 'Backtest Stop Day', minval=1, maxval=31)
):
    intRes = intRs_ if useRes else 1
    green100: Color = color.new('#008000')
    lime100: Color = color.new('#00FF00')
    red100: Color = color.new('#FF0000')
    blue100: Color = color.new('#0000FF')
    aqua100: Color = color.new('#00FFFF')
    darkred100: Color = color.new('#8B0000')
    gray100: Color = color.new('#808080')
    def variant_supersmoother(src: Series, len):
        a1 = math.exp(-1.414 * 3.14159 / len)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / len)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        v9: Series[float] = 0.0
        v9 = c1 * (src + nz(src[1])) / 2 + c2 * nz(v9[1]) + c3 * nz(v9[2])
        return v9

    def variant_smoothed(src, len):
        v5: Series[float] = 0.0
        sma_1 = ta.sma(src, len)
        v5 = sma_1 if na(v5[1]) else (v5[1] * (len - 1) + src) / len
        return v5

    def variant_zerolagema(src: Series, len):
        lag = (len - 1) / 2
        emaSrc = src + src - src[lag]
        v10 = ta.ema(emaSrc, len)
        return v10

    def variant_doubleema(src, len):
        v2 = ta.ema(src, len)
        v6 = 2 * v2 - ta.ema(v2, len)
        return v6

    def variant_tripleema(src, len):
        v2 = ta.ema(src, len)
        v7 = 3 * (v2 - ta.ema(v2, len)) + ta.ema(ta.ema(v2, len), len)
        return v7

    def variant_lag(p, g):
        L0: Series[float] = 0.0
        L1: Series[float] = 0.0
        L2: Series[float] = 0.0
        L3: Series[float] = 0.0
        L0 = (1 - g) * p + g * nz(L0[1])
        L1 = -g * L0 + nz(L0[1]) + g * nz(L1[1])
        L2 = -g * L1 + nz(L1[1]) + g * nz(L2[1])
        L3 = -g * L2 + nz(L2[1]) + g * nz(L3[1])
        f = (L0 + 2 * L1 + 2 * L2 + L3) / 6
        return f

    def variant(type, src, len):
        ema_1 = ta.ema(src, len)
        wma_1 = ta.wma(src, len)
        vwma_1 = ta.vwma(src, len)
        variant_smoothed__1 = variant_smoothed(src, len)
        variant_doubleema__1 = variant_doubleema(src, len)
        variant_tripleema__1 = variant_tripleema(src, len)
        wma_2 = ta.wma(src, len / 2)
        wma_3 = ta.wma(src, len)
        wma_4 = ta.wma(2 * wma_2 - wma_3, math.round(math.sqrt(len)))
        variant_supersmoother__1 = variant_supersmoother(src, len)
        variant_zerolagema__1 = variant_zerolagema(src, len)
        sma_1 = ta.sma(src, len)
        sma_2 = ta.sma(sma_1, len)
        sma_3 = ta.sma(src, len)
        return ema_1 if type == 'EMA' else wma_1 if type == 'WMA' else vwma_1 if type == 'VWMA' else variant_smoothed__1 if type == 'SMMA' else variant_doubleema__1 if type == 'DEMA' else variant_tripleema__1 if type == 'TEMA' else wma_4 if type == 'HullMA' else variant_supersmoother__1 if type == 'SSMA' else variant_zerolagema__1 if type == 'ZEMA' else sma_2 if type == 'TMA' else sma_3

    closeSeries = variant(basisType, close, basisLen)
    openSeries = variant(basisType, open, basisLen)
    closeSeriesAlt = variant(basisType, close, basisLen * intRes)
    openSeriesAlt = variant(basisType, open, basisLen * intRes)
    trendColour = color.green if closeSeriesAlt > openSeriesAlt else color.red
    bcolour = lime100 if closeSeries > openSeriesAlt else red100
    barcolor(bcolour if scolor else na, title='Bar Colours')
    closeP = plot(closeSeriesAlt, title='Close Series', color=trendColour, linewidth=2, style=plot.style_line)
    openP = plot(openSeriesAlt, title='Open Series', color=trendColour, linewidth=2, style=plot.style_line)
    fill(closeP, openP, color=color.new(trendColour, 80))
    xlong = ta.crossover(closeSeriesAlt, openSeriesAlt)
    xshort = ta.crossunder(closeSeriesAlt, openSeriesAlt)
    longCond = xlong
    shortCond = xshort
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    TP = tpPoints if tpPoints > 0 else na
    SL = slPoints if slPoints > 0 else na
    if testPeriod() and tradeType != 'NONE':
        if longCond == True and tradeType != 'SHORT':
            strategy.entry('long', strategy.long)
        if shortCond == True and tradeType != 'LONG':
            strategy.entry('short', strategy.short)
        if shortCond == True and tradeType == 'LONG':
            strategy.close('long')
        if longCond == True and tradeType == 'SHORT':
            strategy.close('short')
        strategy.exit('XL', from_entry='long', profit=TP, loss=SL)
        strategy.exit('XS', from_entry='short', profit=TP, loss=SL)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
