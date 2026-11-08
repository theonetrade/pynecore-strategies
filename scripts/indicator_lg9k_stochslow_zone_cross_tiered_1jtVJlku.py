"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, bgcolor, close, color, fill,
    high, hline, input, label, location, low, math, na, plot, plotshape, script, shape, size,
    string, ta, time, timeframe
)
from pynecore.types import Label, Persistent

grpS: str = "Stochastic (ToS StochasticSlow)"
grpE: str = "EXTREME tier"
grpG: str = "Gates"
grpL: str = "Mancini levels"


@script.indicator("LG9k StochSlow Zone-Cross (tiered)", overlay=False, precision=2, max_labels_count=500)
def main(
    kPeriod=input.int(10, "K period", group=grpS, minval=1),
    dPeriod=input.int(3, "D period", group=grpS, minval=1),
    slowing=input.int(3, "Slowing (smooth)", group=grpS, minval=1),
    obLevel=input.float(80, "Overbought 1", group=grpS, inline="ob1"),
    osLevel=input.float(20, "Oversold 1", group=grpS, inline="os1"),
    zoneBars=input.int(5, "Cross counts if K was in the zone within N bars", group=grpS, minval=1),
    useExtreme=input.bool(True, "Enable EXTREME tier", group=grpE),
    extremeOb=input.float(95, "Overbought 2 (EXTREME)", group=grpE, inline="ob2"),
    extremeOs=input.float(5, "Oversold 2 (EXTREME)", group=grpE, inline="os2"),
    extremeTrend=input.bool(False, "EXTREME must also pass the trend gate", group=grpE, tooltip="Off by default: the trend gate passed 0 of 16 signals on the 2026-09-17 overnight window and 2 of 28 across all 3m history, because a zone cross sits on the wrong side of the 8 EMA by construction. Turning this on will silence EXTREME almost entirely."),
    extremeLevel=input.bool(False, "EXTREME must also be near a major", group=grpE),
    useExcursion=input.bool(True, "Excursion gate (one signal per zone visit)", group=grpG),
    useTrend=input.bool(False, "Trend gate (8 EMA + PSAR) for tiers A/B", group=grpG),
    useLevel=input.bool(True, "Level gate (near a Mancini major) for tier A", group=grpG),
    emaLen=input.int(8, "EMA length", group=grpG, minval=1),
    showCounter=input.bool(True, "Show tier counter", group=grpG),
    showC=input.bool(True, "Draw tier C (the lowest-ranked crosses)", group=grpG),
    majorsCsv=input.string("7469,7526,7584,7604,7622,7663,7687,7695,7714,7728,7759,7782", "MAJORS (comma separated)", group=grpL),
    proxRth=input.float(8.0, "Proximity, RTH (points)", group=grpL, step=0.25),
    proxGlobex=input.float(5.0, "Proximity, Globex (points)", group=grpL, step=0.25)
):
    hh = ta.highest(high, kPeriod)
    ll = ta.lowest(low, kPeriod)
    rng = hh - ll
    rawK = 50.0 if rng == 0 else 100.0 * (close - ll) / rng
    fullK = ta.sma(rawK, slowing)
    fullD = ta.sma(fullK, dPeriod)


    ema8 = ta.ema(close, emaLen)
    psar = ta.sar(0.02, 0.02, 0.2)
    trendLong = close > ema8 and psar < close
    trendShort = close < ema8 and psar > close

    majors: Persistent[list[float]] = array.new_float(0)
    if barstate.isfirst:
        parts = string.split(string.replace_all(majorsCsv, ' ', ''), ',')
        for i in pine_range(0, array.size(parts) - 1):
            v = string.tonumber(array.get(parts, i))
            if not na(v):
                array.push(majors, v)

    def nearestMajor(px: float):
        best: float = na(float)
        if array.size(majors) > 0:
            for i in pine_range(0, array.size(majors) - 1):
                d = math.abs(px - array.get(majors, i))
                best = d if na(best) or d < best else best
        return best

    inRth = not na(time(timeframe.period, '0930-1600:23456', 'America/New_York'))
    prox = proxRth if inRth else proxGlobex
    dist = nearestMajor(close)
    nearLevel = not na(dist) and dist <= prox

    bullCross = ta.crossover(fullK, fullD)
    bearCross = ta.crossunder(fullK, fullD)
    kLo = ta.lowest(fullK, zoneBars)
    kHi = ta.highest(fullK, zoneBars)

    bullRaw = bullCross and kLo <= osLevel
    bearRaw = bearCross and kHi >= obLevel

    bullDeep = bullCross and kLo <= extremeOs and (fullK <= osLevel)
    bearDeep = bearCross and kHi >= extremeOb and (fullK >= obLevel)

    bullArmed: Persistent[bool] = True
    bearArmed: Persistent[bool] = True
    bullSig = bullRaw and (not useExcursion or bullArmed)
    bearSig = bearRaw and (not useExcursion or bearArmed)
    if bullSig:
        bullArmed = False
    elif fullK > osLevel:
        bullArmed = True
    if bearSig:
        bearArmed = False
    elif fullK < obLevel:
        bearArmed = True

    trendOkL = not useTrend or trendLong
    trendOkS = not useTrend or trendShort
    levelOk = not useLevel or nearLevel

    xLong = useExtreme and bullSig and bullDeep and (not extremeTrend or trendLong) and (not extremeLevel or nearLevel)
    xShort = useExtreme and bearSig and bearDeep and (not extremeTrend or trendShort) and (not extremeLevel or nearLevel)

    aLong = bullSig and (not xLong) and trendOkL and levelOk
    aShort = bearSig and (not xShort) and trendOkS and levelOk
    bLong = bullSig and (not xLong) and trendOkL and (not aLong)
    bShort = bearSig and (not xShort) and trendOkS and (not aShort)
    cLong = bullSig and (not xLong) and (not trendOkL)
    cShort = bearSig and (not xShort) and (not trendOkS)

    plot(fullK, 'SlowK', color=color.new('#26C6DA'), linewidth=2)
    plot(fullD, 'SlowD', color=color.new('#EF5350'), linewidth=2)
    hline(obLevel, 'Over Bought 1', color=color.new(color.gray, 50), linestyle=hline.style_dashed)
    hline(osLevel, 'Over Sold 1', color=color.new(color.gray, 50), linestyle=hline.style_dashed)
    xo = hline(extremeOb, 'Over Bought 2', color=color.new(color.new('#FF1744'), 40), linestyle=hline.style_dotted)
    xs = hline(extremeOs, 'Over Sold 2', color=color.new(color.new('#00E676'), 40), linestyle=hline.style_dotted)
    fill(hline(100), xo, color=color.new(color.new('#FF1744'), 88))
    fill(xs, hline(0), color=color.new(color.new('#00E676'), 88))

    plotshape(fullK if xLong else na, 'EXTREME LONG', shape.labelup, location.absolute, color.new('#00E676'), text='X', textcolor=color.black, size=size.normal)
    plotshape(fullK if xShort else na, 'EXTREME SHORT', shape.labeldown, location.absolute, color.new('#FF1744'), text='X', textcolor=color.white, size=size.normal)
    plotshape(fullK if aLong else na, 'A LONG', shape.triangleup, location.absolute, color.new('#00E676'), size=size.normal)
    plotshape(fullK if aShort else na, 'A SHORT', shape.triangledown, location.absolute, color.new('#FF1744'), size=size.normal)
    plotshape(fullK if bLong else na, 'B LONG', shape.triangleup, location.absolute, color.new('#00B85C'), size=size.small)
    plotshape(fullK if bShort else na, 'B SHORT', shape.triangledown, location.absolute, color.new('#C4142F'), size=size.small)
    plotshape(fullK if showC and cLong else na, 'C LONG', shape.xcross, location.absolute, color.new('#B0BEC5'), size=size.tiny)
    plotshape(fullK if showC and cShort else na, 'C SHORT', shape.xcross, location.absolute, color.new('#B0BEC5'), size=size.tiny)
    bgcolor(color.new(color.new('#00E676'), 88) if xLong else color.new(color.new('#FF1744'), 88) if xShort else na, title='EXTREME flash')

    alertcondition(xLong, '🔥 EXTREME LONG  (K<=5)', 'EXTREME LONG {{ticker}} {{close}} — StochSlow crossed up out of <=5. Deep oversold reversal.')
    alertcondition(xShort, '🔥 EXTREME SHORT (K>=95)', 'EXTREME SHORT {{ticker}} {{close}} — StochSlow crossed down out of >=95. Deep overbought reversal.')
    alertcondition(xLong or xShort, '🔥 EXTREME either way', 'EXTREME {{ticker}} {{close}} — StochSlow reversed out of a deep zone.')
    alertcondition(aLong, 'A LONG  — cross AT a level', 'A LONG {{ticker}} {{close}} — stoch zone cross AT a Mancini major')
    alertcondition(aShort, 'A SHORT — cross AT a level', 'A SHORT {{ticker}} {{close}} — stoch zone cross AT a Mancini major')
    alertcondition(bLong, 'B LONG  — cross, no level', 'B LONG {{ticker}} {{close}} — stoch zone cross, no level nearby')
    alertcondition(bShort, 'B SHORT — cross, no level', 'B SHORT {{ticker}} {{close}} — stoch zone cross, no level nearby')

    nX: Persistent[int] = 0
    nA: Persistent[int] = 0
    nB: Persistent[int] = 0
    nC: Persistent[int] = 0
    if xLong or xShort:
        nX += 1
    if aLong or aShort:
        nA += 1
    if bLong or bShort:
        nB += 1
    if cLong or cShort:
        nC += 1
    if showCounter and barstate.islast:
        lab: Persistent[Label] = na(Label)
        label.delete(lab)
        lab = label.new(bar_index, 100, string.format('EXTREME {0} · A {1} · B {2} · C {3}', nX, nA, nB, nC), style=label.style_label_left, color=color.new(color.black, 20), textcolor=color.white, size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)