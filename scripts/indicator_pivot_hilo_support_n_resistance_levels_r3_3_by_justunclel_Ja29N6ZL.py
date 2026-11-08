"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, barcolor, close, color, extend, high, input,
    line, location, low, math, na, nz, open, plot, plotarrow, plotshape, script, shape, ta
)
from pynecore.types import Color, Line, Persistent, Series


@script.indicator(title='Pivot Hilo Support n Resistance Levels R5.4', shorttitle='PVTLVLS R5.4', overlay=True, max_bars_back=50, na_bool=True)
def main(
    ShowPivots=input(True, title='Show Pivot Points'),
    uAuto=input(False, title='Use Auto Strength Pivots Points'),
    left=input.int(5, minval=1, title='Pivot Length Left Hand Side'),
    right=input.int(5, minval=1, title='Pivot Length Right Hand Side'),
    ShowSRLevels=input(True, title='Show S/R Level Extensions'),
    ShowChannel=input(False, title='Show Levels as a Fractal Chaos Channel'),
    Shunt=input.int(1, minval=0, maxval=1, title='When to start Printing Pivot (0 = no wait, 1 = wait for candle close)'),
    maxLvlLen=input.int(0, minval=0, title='Maximum S/R Level Extension Length'),
    uRenko=input(False, title='Use Renko Style Pivots (open/close for high/low)'),
    sIdeal=input(False, title='Show Only Ideal Pivots (handy for Renko and HA)'),
    ShowHHLL=input(False, title='Show HH,LL,LH,HL markers on Pivots Points'),
    swing3Levels=input(False, title='Filter HH,LL,LH,HL to Third Level Swings'),
    clrPivot=input(False, title='Highlight Pivot with Coloured Bar'),
    ShowFB=input(False, title='Show Fractal Break Alert Arrows'),
    filterFB=input(False, title='Apply MA Filter to Fractal Break Alerts'),
    uMAf=input(False, title='Use MA Filter on Pivots'),
    fast_ma_type=input.string(defval='EMA', title='Fast MA Type ', options=('SMA', 'EMA', 'WMA', 'VWMA', 'Smooth SMA', 'DEMA', 'TEMA', 'Hull MA', 'ZeroLag EMA', 'Triangular MA', 'SuperSmooth MA')),
    fast_ma_len=input.int(defval=21, title='Fast MA - Length', minval=1),
    fast_ma_src: Series[float] = input(close, title='Fast MA - Source'),
    slow_ma_type=input.string(defval='EMA', title='Slow MA Type ', options=('SMA', 'EMA', 'WMA', 'VWMA', 'Smooth SMA', 'DEMA', 'TEMA', 'Hull MA', 'ZeroLag EMA', 'Triangular MA', 'SuperSmooth MA')),
    slow_ma_len=input.int(defval=55, title='Slow MA - Length', minval=1),
    slow_ma_src: Series[float] = input(close, title='Slow MA - Source'),
    sMAs=input(False, title='Show MA Lines')
):
    high_: Series = math.max(close, open) if uRenko else high
    low_: Series = math.min(close, open) if uRenko else low
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
        xLag = (len - 1) / 2
        xEMA = src + src - src[xLag]
        v10 = ta.ema(xEMA, len)
        return v10

    def variant_doubleema(src, len):
        v2 = ta.ema(src, len)
        v6 = 2 * v2 - ta.ema(v2, len)
        return v6

    def variant_tripleema(src, len):
        v2 = ta.ema(src, len)
        v7 = 3 * (v2 - ta.ema(v2, len)) + ta.ema(ta.ema(v2, len), len)
        return v7

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
        return ema_1 if type == 'EMA' else wma_1 if type == 'WMA' else vwma_1 if type == 'VWMA' else variant_smoothed__1 if type == 'Smooth SMA' else variant_doubleema__1 if type == 'DEMA' else variant_tripleema__1 if type == 'TEMA' else wma_4 if type == 'Hull MA' else variant_supersmoother__1 if type == 'SuperSmooth MA' else variant_zerolagema__1 if type == 'ZeroLag EMA' else sma_2 if type == 'Triangular MA' else sma_1

    def ipivothigh(src: Series, L, R):
        t: bool = True
        for i in pine_range(R, L + R - 1, 1):
            t = t and src[i] > src[i + 1]
        for i in pine_range(0, R - 1, 1):
            t = t and src[i] < src[i + 1]
        return src[R] if t else na

    def ipivotlow(src: Series, L, R):
        t: bool = True
        for i in pine_range(R, L + R - 1, 1):
            t = t and src[i] < src[i + 1]
        for i in pine_range(0, R - 1, 1):
            t = t and src[i] > src[i + 1]
        return src[R] if t else na

    fast_ma_series = variant(fast_ma_type, fast_ma_src, fast_ma_len)
    slow_ma_series = variant(slow_ma_type, slow_ma_src, slow_ma_len)
    plot(fast_ma_series if sMAs else na, color=color.new(color.lime, 15), title='Fast MA', join=True, style=plot.style_circles, linewidth=2)
    plot(slow_ma_series if sMAs and fast_ma_len <= slow_ma_len else na, color=color.new(color.gray, 15), title='Slow MA', join=True, style=plot.style_circles, linewidth=2)
    ema_1 = ta.ema(close, 21)
    pvtLenL = (left if close > ema_1 else left + 1) if uAuto else left
    pvtLenR = (right if close < ema_1 else right + 1) if uAuto else right
    pvthi_: Series = na if uMAf and (fast_ma_len > slow_ma_len or fast_ma_series < slow_ma_series) else ipivothigh(high_, pvtLenL, pvtLenR) if sIdeal else ta.pivothigh(high_, pvtLenL, pvtLenR)
    pvtlo_: Series = na if uMAf and (fast_ma_len > slow_ma_len or fast_ma_series > slow_ma_series) else ipivotlow(low_, pvtLenL, pvtLenR) if sIdeal else ta.pivotlow(low_, pvtLenL, pvtLenR)
    pvthi = pvthi_[Shunt]
    pvtlo = pvtlo_[Shunt]
    valuewhen_H0 = ta.valuewhen(pvthi, high_[pvtLenR + Shunt], 0)
    valuewhen_H1 = ta.valuewhen(pvthi, high_[pvtLenR + Shunt], 1)
    valuewhen_H2 = ta.valuewhen(pvthi, high_[pvtLenR + Shunt], 2)
    valuewhen_H3 = ta.valuewhen(pvthi, high_[pvtLenR + Shunt], 3)
    higherhigh = (na if na(pvthi) else pvthi if valuewhen_H1 < valuewhen_H0 and valuewhen_H2 < valuewhen_H0 and (valuewhen_H3 < valuewhen_H0) else na) if swing3Levels else na if na(pvthi) else pvthi if valuewhen_H1 < valuewhen_H0 else na
    lowerhigh = (na if na(pvthi) else pvthi if valuewhen_H1 > valuewhen_H0 and valuewhen_H2 > valuewhen_H0 and (valuewhen_H3 > valuewhen_H0) else na) if swing3Levels else na if na(pvthi) else pvthi if valuewhen_H1 > valuewhen_H0 else na
    valuewhen_L0 = ta.valuewhen(pvtlo, low_[pvtLenR + Shunt], 0)
    valuewhen_L1 = ta.valuewhen(pvtlo, low_[pvtLenR + Shunt], 1)
    valuewhen_L2 = ta.valuewhen(pvtlo, low_[pvtLenR + Shunt], 2)
    valuewhen_L3 = ta.valuewhen(pvtlo, low_[pvtLenR + Shunt], 3)
    higherlow = (na if na(pvtlo) else pvtlo if valuewhen_L1 < valuewhen_L0 and valuewhen_L2 < valuewhen_L0 and (valuewhen_L3 < valuewhen_L0) else na) if swing3Levels else na if na(pvtlo) else pvtlo if valuewhen_L1 < valuewhen_L0 else na
    lowerlow = (na if na(pvtlo) else pvtlo if valuewhen_L1 > valuewhen_L0 and valuewhen_L2 > valuewhen_L0 and (valuewhen_L3 > valuewhen_L0) else na) if swing3Levels else na if na(pvtlo) else pvtlo if valuewhen_L1 > valuewhen_L0 else na
    anySwing = not (na(higherhigh) and na(lowerhigh) and na(higherlow) and na(lowerlow))
    plotshape(higherhigh if ShowHHLL else na, title='HH', style=shape.triangleup, location=location.abovebar, color=color.new(color.green, 0), text='HH', offset=-pvtLenR - Shunt)
    plotshape(higherlow if ShowHHLL else na, title='HL', style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), text='HL', offset=-pvtLenR - Shunt)
    plotshape(lowerhigh if ShowHHLL else na, title='LH', style=shape.triangledown, location=location.abovebar, color=color.new(color.maroon, 0), text='LH', offset=-pvtLenR - Shunt)
    plotshape(lowerlow if ShowHHLL else na, title='LL', style=shape.triangledown, location=location.belowbar, color=color.new(color.maroon, 0), text='LL', offset=-pvtLenR - Shunt)
    plot(pvthi if ShowPivots and (not ShowHHLL) else na, title='High Pivot *', style=plot.style_circles, join=False, color=color.new(color.white, 50), offset=-pvtLenR - Shunt, linewidth=3)
    plot(pvtlo if ShowPivots and (not ShowHHLL) else na, title='Low Pivot *', style=plot.style_circles, join=False, color=color.new(color.white, 50), offset=-pvtLenR - Shunt, linewidth=3)
    plot(pvthi if ShowPivots and (not ShowHHLL) else na, title='High Pivot *', style=plot.style_circles, join=False, color=color.new(color.green, 0), offset=-pvtLenR - Shunt, linewidth=2)
    plot(pvtlo if ShowPivots and (not ShowHHLL) else na, title='Low Pivot *', style=plot.style_circles, join=False, color=color.new(color.maroon, 0), offset=-pvtLenR - Shunt, linewidth=2)
    ORANGE: Color = color.new('#FFA500')
    barcolor(ORANGE if clrPivot and (pvthi or pvtlo) else na, title='Colour Pivot Bar', offset=-pvtLenR - Shunt)
    counthi: Series[int] = 0
    countlo: Series[int] = 0
    counthi = nz(counthi[1]) + 1 if na(pvthi) else 0
    countlo = nz(countlo[1]) + 1 if na(pvtlo) else 0
    pvthis: Series[float] = 0.0
    pvtlos: Series[float] = 0.0
    pvthis = pvthis[1] if na(pvthi) else high[pvtLenR + Shunt]
    pvtlos = pvtlos[1] if na(pvtlo) else low[pvtLenR + Shunt]
    hipc = na if pvthis != pvthis[1] else color.maroon
    lopc = na if pvtlos != pvtlos[1] else color.green
    pvthiLine: Persistent[Line] = na(Line)
    pvtloLine: Persistent[Line] = na(Line)
    if not ShowChannel and ShowSRLevels:
        if not na(pvthis) and nz(pvthis[1]) != pvthis:
            pvthiLine = line.new(bar_index - (pvtLenR + Shunt), pvthis, bar_index, pvthis, extend=extend.none, width=1, color=color.maroon, style=line.style_solid)
        if not na(pvthiLine) and (not na(pvthis)) and (line.get_x2(pvthiLine) != bar_index):
            line.set_x2(pvthiLine, bar_index)
        if not na(pvtlos) and nz(pvtlos[1]) != pvtlos:
            pvtloLine = line.new(bar_index - (pvtLenR + Shunt), pvtlos, bar_index, pvtlos, extend=extend.none, width=1, color=color.green, style=line.style_solid)
        if not na(pvtloLine) and (not na(pvtlos)) and (line.get_x2(pvtloLine) != bar_index):
            line.set_x2(pvtloLine, bar_index)
    plot(pvthis if ShowSRLevels and (not ShowChannel) and (maxLvlLen == 0 or counthi < maxLvlLen) else na, color=hipc, linewidth=1, offset=-pvtLenR - Shunt, title='Top Levels')
    plot(pvtlos if ShowSRLevels and (not ShowChannel) and (maxLvlLen == 0 or countlo < maxLvlLen) else na, color=lopc, linewidth=1, offset=-pvtLenR - Shunt, title='Bottom Levels')
    plot(pvthis if ShowSRLevels and ShowChannel else na, color=color.new(color.green, 0), linewidth=1, style=plot.style_stepline, offset=0, title='Top Chaos Channel', trackprice=False)
    plot(pvtlos if ShowSRLevels and ShowChannel else na, color=color.new(color.maroon, 0), linewidth=1, style=plot.style_stepline, offset=0, title='Bottom Chaos Channel', trackprice=False)
    buy: bool = False
    sell: bool = False
    buy = close > pvthis and open <= pvthis and (not filterFB or ((fast_ma_len > slow_ma_len or fast_ma_series > slow_ma_series) and close > fast_ma_series))
    sell = close < pvtlos and open >= pvtlos and (not filterFB or ((fast_ma_len > slow_ma_len or fast_ma_series < slow_ma_series) and close < fast_ma_series))
    plotarrow(1 if ShowFB and buy else na, title='BUY Arrow', colorup=color.new(color.lime, 20), maxheight=60, minheight=50)
    plotarrow(-1 if ShowFB and sell else na, title='SELL Arrow', colordown=color.new(color.red, 20), maxheight=60, minheight=50)
    alertcondition(buy or sell, title='Fractal Break Arrow', message='Alert')
    alertcondition(buy, title='Fractal Break Long', message='Long')
    alertcondition(sell, title='Fractal Break Short', message='Short')
    alertcondition(anySwing, title='Any Swing', message='AnySwing')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
