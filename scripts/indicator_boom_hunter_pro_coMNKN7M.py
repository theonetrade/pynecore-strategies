"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, fixnan, high, hl2, hlc3,
    hline, input, location, low, math, na, nz, ohlc4, open, plot, plotshape, script, shape, size,
    ta, volume
)
from pynecore.types import Persistent, Series

title: str = 'Boom Hunter Pro'
stitle: str = 'Boom Pro'
version: str = ' 1.022'


@script.indicator(title=title + version, shorttitle=stitle, overlay=False, timeframe='')
def main(
    showfib=input.bool(defval=False, title='Show Fibonacci Lines?', group='Main Settings', inline='main2'),
    showentry=input.bool(defval=True, title='Show Entry and Exit Points?', group='Main Settings'),
    square=input.bool(True, title='Square Line?', group='Main Settings'),
    showdboom=input.bool(True, title='Show Downward Boom Line?', group='Main Settings'),
    showlongs=input.bool(True, title='Show Long Entries?', group='Main Settings'),
    showshorts=input.bool(True, title='Show Short Entries?', group='Main Settings'),
    LPPeriod=input.int(6, title='Quotient | LPPeriod', inline='quotient', group='EOT 1 (Main Oscillator)'),
    K1=input.int(0, title='K1', inline='quotient', group='EOT 1 (Main Oscillator)'),
    trigno=input.int(2, 'Trigger Length', group='EOT 1 (Main Oscillator)', inline='quotient2'),
    osccol=input.color(color.blue, title='Oscillator Color:', group='EOT 1 (Main Oscillator)', inline='q2'),
    trigcol=input.color(color.white, title='Trigger Color:', group='EOT 1 (Main Oscillator)', inline='q2'),
    LPPeriod2=input.int(27, title='LPPeriod2', group='EOT 2 (Red Wave)', inline='q2'),
    K12=input.float(0.8, title='K1', group='EOT 2 (Red Wave)', inline='q2'),
    K22=input.float(0.3, title='K2', group='EOT 2 (Red Wave)', inline='q2'),
    osccol2=input.color(color.red, title='Line Color:', inline='quotient22', group='EOT 2 (Red Wave)'),
    osccol22=input.color(color.red, title='Fill Color:', inline='quotient22', group='EOT 2 (Red Wave)'),
    LPPeriod3=input.int(11, title='LPPeriod3', group='EOT 3 (Yellow Line)', inline='q2'),
    K13=input.float(0.99, title='K1', group='EOT 3 (Yellow Line)', inline='q2'),
    osccol3=input.color(color.yellow, title='Line Color:', group='EOT 3 (Yellow Line)', inline='quotient3'),
    n1=input.int(9, 'WT | master', inline='lsma', group='LSMA Wave Trend Settings'),
    n2=input.int(6, 'time 1', inline='lsma', group='LSMA Wave Trend Settings'),
    n3=input.int(3, '2', inline='lsma', group='LSMA Wave Trend Settings'),
    n4=input.int(21, 'LSMA | 1', inline='LSMA', group='LSMA Wave Trend Settings'),
    n5=input.int(0, '2', inline='LSMA', group='LSMA Wave Trend Settings'),
    lsmaline=input.int(200, title='LSMA Long', group='LSMA Wave Trend Settings', inline='LSMA'),
    toggleBreaks=input.bool(False, title='Show Break Lines?', group='Support and Resistance Breaks'),
    leftBars=input.int(1, title='Resistance | Left Bars ', group='Support and Resistance Breaks', inline='2'),
    rightBars=input.int(1, title='Right Bars', group='Support and Resistance Breaks', inline='2'),
    leftBars2=input.int(5, title='Support (Long) | Left Bars ', group='Support and Resistance Breaks', inline='3'),
    rightBars2=input.int(5, title='Right Bars', group='Support and Resistance Breaks', inline='3'),
    leftBars3=input.int(1, title='Support (Short) |Left Bars ', group='Support and Resistance Breaks', inline='4'),
    rightBars3=input.int(1, title='Right Bars', group='Support and Resistance Breaks', inline='4'),
    dragno=input(3),
    allbars=input(False, title='Show Bar Colors?'),
    barc=input(False, title='Show Pump Bar Colors?')
):
    theme: str = 'Dark'
    K2: float = 0.3
    esize: int = 60
    ey: int = 50
    esize3: int = 60
    ey3: int = 50
    K33 = K13 * -1
    esize2: int = 60
    ey2: int = 50
    smalen: int = 2
    if square:
        K13 = 0.9999
        K33 = -0.9999
    hline(84 if showfib else na, linestyle=hline.style_solid, color=color.new(color.blue, 50))
    hline(64 if showfib else na, linestyle=hline.style_solid, color=color.new(color.blue, 50))
    hline(50 if showfib else na, linestyle=hline.style_solid, color=color.new(color.blue, 50))
    hline(36 if showfib else na, linestyle=hline.style_solid, color=color.new(color.blue, 50))
    hline(18 if showfib else na, linestyle=hline.style_solid, color=color.new(color.blue, 50))
    alpha1: float = 0.0
    HP: Series[float] = 0.0
    a1: float = 0.0
    b1: float = 0.0
    c1: float = 0.0
    c2: float = 0.0
    c3: float = 0.0
    Filt: Series[float] = 0.0
    Peak: Series[float] = 0.0
    X: float = 0.0
    Quotient1: float = 0.0
    Quotient2: float = 0.0
    pi = 2 * math.asin(1)
    alpha1 = (math.cos(0.707 * 2 * pi / 100) + math.sin(0.707 * 2 * pi / 100) - 1) / math.cos(0.707 * 2 * pi / 100)
    HP = (1 - alpha1 / 2) * (1 - alpha1 / 2) * (close - 2 * nz(close[1]) + nz(close[2])) + 2 * (1 - alpha1) * nz(HP[1]) - (1 - alpha1) * (1 - alpha1) * nz(HP[2])
    a1 = math.exp(-1.414 * pi / LPPeriod)
    b1 = 2 * a1 * math.cos(1.414 * pi / LPPeriod)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    Filt = c1 * (HP + nz(HP[1])) / 2 + c2 * nz(Filt[1]) + c3 * nz(Filt[2])
    Peak = 0.991 * nz(Peak[1])
    if math.abs(Filt) > Peak:
        Peak = math.abs(Filt)
    if Peak != 0:
        X = Filt / Peak
    Quotient1 = (X + K1) / (K1 * X + 1)
    Quotient2 = (X + K2) / (K2 * X + 1)
    alpha1222: float = 0.0
    HP2: Series[float] = 0.0
    a12: float = 0.0
    b12: float = 0.0
    c12: float = 0.0
    c22: float = 0.0
    c32: float = 0.0
    Filt2: Series[float] = 0.0
    Peak2: Series[float] = 0.0
    X2: float = 0.0
    Quotient3: float = 0.0
    Quotient4: float = 0.0
    alpha1222 = (math.cos(0.707 * 2 * pi / 100) + math.sin(0.707 * 2 * pi / 100) - 1) / math.cos(0.707 * 2 * pi / 100)
    HP2 = (1 - alpha1222 / 2) * (1 - alpha1222 / 2) * (close - 2 * nz(close[1]) + nz(close[2])) + 2 * (1 - alpha1222) * nz(HP2[1]) - (1 - alpha1222) * (1 - alpha1222) * nz(HP2[2])
    a12 = math.exp(-1.414 * pi / LPPeriod2)
    b12 = 2 * a12 * math.cos(1.414 * pi / LPPeriod2)
    c22 = b12
    c32 = -a12 * a12
    c12 = 1 - c22 - c32
    Filt2 = c12 * (HP2 + nz(HP2[1])) / 2 + c22 * nz(Filt2[1]) + c32 * nz(Filt2[2])
    Peak2 = 0.991 * nz(Peak2[1])
    if math.abs(Filt2) > Peak2:
        Peak2 = math.abs(Filt2)
    if Peak2 != 0:
        X2 = Filt2 / Peak2
    Quotient3 = (X2 + K12) / (K12 * X2 + 1)
    Quotient4 = (X2 + K22) / (K22 * X2 + 1)
    alpha1333: float = 0.12
    HP3: Series[float] = 0.0
    a13: float = 0.0
    b13: float = 0.0
    c13: float = 0.0
    c33: float = 0.0
    c333: float = 0.0
    Filt3: Series[float] = 0.0
    Peak3: Series[float] = 0.0
    X3: float = 0.0
    Quotient5: float = 0.0
    Quotient6: float = 0.0
    alpha1333 = (math.cos(0.707 * 2 * pi / 100) + math.sin(0.707 * 2 * pi / 100) - 1) / math.cos(0.707 * 2 * pi / 100)
    HP3 = (1 - alpha1333 / 3) * (1 - alpha1333 / 2) * (close - 2 * nz(close[1]) + nz(close[2])) + 2 * (1 - alpha1333) * nz(HP3[1]) - (1 - alpha1333) * (1 - alpha1333) * nz(HP3[2])
    a13 = math.exp(-1.414 * pi / LPPeriod3)
    b13 = 2 * a13 * math.cos(1.414 * pi / LPPeriod3)
    c33 = b13
    c333 = -a13 * a13
    c13 = 1 - c33 - c333
    Filt3 = c13 * (HP3 + nz(HP3[1])) / 2 + c33 * nz(Filt3[1]) + c333 * nz(Filt3[2])
    Peak3 = 0.991 * nz(Peak3[1])
    if math.abs(Filt3) > Peak3:
        Peak3 = math.abs(Filt3)
    if Peak3 != 0:
        X3 = Filt3 / Peak3
    Quotient5 = (X3 + K13) / (K13 * X3 + 1)
    Quotient6 = (X3 + K33) / (K33 * X3 + 1)
    line1 = -0.9
    src0 = open
    src1 = high
    src2 = low
    src3 = close
    src4 = hl2
    src5 = hlc3
    src6 = ohlc4
    src7 = ta.tr
    vol = volume
    def tci(src):
        return ta.ema((src - ta.ema(src, n1)) / (0.025 * ta.ema(math.abs(src - ta.ema(src, n1)), n1)), n2) + 50

    def mf(src):
        return 100.0 - 100.0 / (1.0 + math.sum(volume * (0 if ta.change(src) <= 0 else src), n3) / math.sum(volume * (0 if ta.change(src) >= 0 else src), n3))

    def willy(src):
        return 60 * (src - ta.highest(src, n2)) / (ta.highest(src, n2) - ta.lowest(src, n2)) + 80

    def csi(src):
        return math.avg(ta.rsi(src, n3), ta.tsi(src0, n1, n2) * 50 + 50)

    def phoenix(src):
        return math.avg(tci(src), csi(src), mf(src), willy(src))

    def tradition(src):
        return math.avg(tci(src), mf(src), ta.rsi(src, n3))

    wt1 = tradition(src5)
    wt2 = ta.sma(wt1, 6)
    wt3 = ta.linreg(wt1, n4, n5)
    wt4 = ta.ema((wt1 - wt2) * 2 + 50, n3)
    trig = ta.sma(wt3, smalen)
    q3 = Quotient3 * esize + ey
    q4 = Quotient4 * esize + ey
    Plot33 = plot(q3, color=color.new(color.red, 50), linewidth=1, title='Quotient 1')
    Plot44 = plot(q4, color=color.new(color.red, 50), linewidth=1, title='Quotient 2')
    fill(Plot33, Plot44, color=color.new(color.red, 90))
    q1 = Quotient1 * esize + ey
    q2 = Quotient2 * esize + ey
    trigger = ta.sma(q1, trigno)
    ext1 = trigger + 9 if wt2 < 20 else trigger - 9 if wt2 > 80 else na
    lsma = ta.linreg(wt3, lsmaline, 0)
    q5 = Quotient5 * esize2 + ey2
    q6 = Quotient6 * esize2 + ey2
    Plot54 = plot(q6 if showdboom else na, color=color.new(color.blue, 0), linewidth=1, title='Quotient 1')
    Plot55 = plot(q5, color=color.new(color.orange, 0) if theme == 'Light' else color.new(color.yellow, 0), linewidth=1, title='Quotient 1')
    sma200 = ta.sma(close, 200)
    entry = ta.crossunder(Quotient2, line1)
    color2 = Quotient1 <= -1 and Quotient2 <= -1
    exit = ta.cross(Quotient1, Quotient2) and close > sma200 and (Quotient1 > 0.5)
    over = ta.cross(Quotient5, Quotient6) and Quotient5 > 0.5
    over2 = ta.crossover(Quotient5, Quotient6) and Quotient5 > 0.5
    over3 = ta.cross(Quotient3, Quotient4) and Quotient3 > 0
    enter = ta.crossover(q1, trigger) and q1 < lsma
    plotshape(over if showentry else False, title='Exit Warning', location=location.bottom, style=shape.circle, size=size.tiny, color=color.new(color.orange, 0))
    plotshape(over3 if showentry else False, title='Exit Warning', location=location.bottom, style=shape.circle, size=size.tiny, color=color.new(color.red, 0), text='Overbought')
    highUsePivot = fixnan(inline_series(ta.pivothigh(q1, leftBars, rightBars), 1))
    lowUsePivot = fixnan(inline_series(ta.pivotlow(q1, leftBars2, rightBars2), 1))
    lowUsePivot2 = fixnan(inline_series(ta.pivotlow(q1, leftBars3, rightBars3), 1))
    highUsePivot2 = fixnan(inline_series(ta.pivothigh(q1, leftBars3, rightBars3), 1))
    r1 = plot(highUsePivot if toggleBreaks else na, color=na if cast_bool(ta.change(highUsePivot)) else color.red, linewidth=1, offset=-(rightBars + 1), title='Resistance')
    s2 = plot(lowUsePivot2 if toggleBreaks else na, color=na if cast_bool(ta.change(lowUsePivot2)) else color.silver, linewidth=1, offset=-(rightBars3 + 1), title='Support')
    s1 = plot(lowUsePivot if toggleBreaks else na, color=na if cast_bool(ta.change(lowUsePivot)) else color.blue, linewidth=1, offset=-(rightBars2 + 1), title='Support')
    crossover = ta.crossover(q1, trigger)
    crossunder = ta.crossunder(q1, trigger)
    ubreak: Persistent[int] = 0
    ubreak2: Persistent[int] = 0
    dbreak: Persistent[int] = 0
    cont: Persistent[int] = 0
    cont2: Persistent[int] = 0
    pull: Persistent[int] = 0
    dbreak2: Persistent[int] = 0
    cross: Persistent[int] = 0
    if crossunder:
        cross = 0
    if crossover:
        cross = 1
    if ta.crossunder(q1, lowUsePivot):
        dbreak = dbreak + 1
    if entry:
        dbreak = 0
        dbreak2 = 0
        ubreak = 0
        ubreak2 = 0
        cont = 0
        cont2 = 0
    volcond = ta.linreg(volume, 20, 0)
    drag: Persistent[int] = 0
    if Quotient1 <= -1:
        drag = drag + 1
    if ta.crossover(Quotient1, -0.9):
        drag = 0
    if ta.crossover(q1, highUsePivot) and dbreak >= 1:
        ubreak = ubreak + 1
    if ta.crossover(q1, highUsePivot) and dbreak >= 1 and (ubreak <= 1):
        cont = 1
    if ta.crossover(q1, highUsePivot) and dbreak >= 2 and (ubreak >= 2) and (cont <= 2):
        cont2 = 1
    if ta.crossunder(q1, lowUsePivot2):
        dbreak2 = dbreak2 + 1
    if ta.crossunder(q1, highUsePivot2):
        ubreak2 = ubreak2 + 1
    if ta.crossunder(q1, lowUsePivot2) and dbreak2 == 1:
        ubreak2 = 0
    Plot = plot(q1, color=color.new('#00FFAA') if cross == 1 else color.purple if drag >= dragno else color.yellow if Quotient1 <= -0.8 else color.white if Quotient3 <= -0.9 else color.red if cross == 0 else color.gray, linewidth=2, title='Quotient 2', trackprice=True)
    Plot4 = plot(q1, color=osccol, linewidth=2, title='Quotient 2')
    Plot3 = plot(trigger, color=trigcol, linewidth=2, title='Quotient 1')
    plot(ext1, 'Pressure', color=color.new('#00FFAA') if wt2 < 20 else color.red if wt2 > 80 else na, style=plot.style_circles, linewidth=2)
    warn = ta.crossover(Quotient3, -0.9)
    warn2 = ta.crossover(Quotient1, -0.9)
    warn3 = ta.crossunder(Quotient1, 0.9)
    crossover_1 = ta.crossover(q1, trigger)
    barssince_1 = ta.barssince(warn)
    enter2 = Quotient1 <= -0.9 and crossover_1 and (barssince_1 <= 7)
    crossover_2 = ta.crossover(q1, trigger)
    barssince_2 = ta.barssince(warn2)
    crossover_3 = ta.crossover(q1, 20)
    barssince_3 = ta.barssince(crossover_3)
    enter3 = Quotient3 <= -0.9 and crossover_2 and (barssince_2 <= 7) and (q1 <= 20) and (barssince_3 <= 21)
    entercond = ta.crossover(q1, trigger) and q1 < 10
    barssince_4 = ta.barssince(entercond)
    crossover_4 = ta.crossover(q1, trigger)
    enter4 = q1 <= 20 and barssince_4 <= 5 and crossover_4
    crossunder_1 = ta.crossunder(q1, trigger)
    crossover_5 = ta.crossover(q1, trigger)
    enter5 = ta.barssince(q1 <= 0 and crossunder_1) <= 5 and crossover_5
    crossunder_2 = ta.crossunder(q1, trigger)
    crossover_6 = ta.crossover(q1, trigger)
    enter6 = ta.barssince(q1 <= 20 and crossunder_2) <= 11 and crossover_6
    crossover_7 = ta.crossover(q1, trigger)
    enter7 = Quotient3 <= -0.9 and crossover_7
    crossunder_3 = ta.crossunder(q1, trigger)
    barssince_5 = ta.barssince(warn3)
    crossover_8 = ta.crossover(q1, 80)
    barssince_6 = ta.barssince(crossover_8)
    senter3 = Quotient3 >= -0.9 and crossunder_3 and (barssince_5 <= 7) and (q1 >= 99) and (barssince_6 <= 21)
    plotshape(showlongs and enter6 and (q1 <= 60), title='Long gray', text='Long', style=shape.labeldown, location=location.top, color=color.new(color.silver, 20), textcolor=color.new(color.white, 20), size=size.tiny)
    plotshape(showlongs and enter7, title='Long yellow', text='Long', style=shape.labeldown, location=location.top, color=color.new(color.yellow, 20), textcolor=color.new(color.white, 20), size=size.tiny)
    plotshape(showlongs and enter5, title='Long blue', text='Long', style=shape.labeldown, location=location.top, color=color.new(color.blue, 20), textcolor=color.new(color.white, 20), size=size.tiny)
    plotshape(showlongs and enter3, title='Long Lime', text='Long', style=shape.labeldown, location=location.top, color=color.new(color.lime, 20), textcolor=color.new(color.white, 20), size=size.tiny)
    plotshape(senter3 if showshorts else False, title='Break', text='Short', style=shape.labeldown, location=location.top, color=color.new(color.red, 20), textcolor=color.new(color.white, 20), size=size.tiny)
    plotshape(ta.crossover(q1, highUsePivot) and dbreak >= 1 and (ubreak <= 1), title='Break', style=shape.triangleup, location=location.bottom, color=color.new(color.new('#00FFAA'), 0), size=size.tiny, text='Continuation')
    barcolor(color.purple if allbars and drag >= dragno else color.white if allbars and Quotient3 <= -0.9 else color.yellow if allbars and Quotient1 <= -0.9 else na)
    barcolor(color.new('#00FFAA') if allbars and barc and (q1 > trigger) else color.red if allbars and barc and (q1 < trigger) else color.gray if allbars and barc else na)
    crossunder_4 = ta.crossunder(wt2, 80)
    plotshape(wt2 + 9 if ta.barssince(ta.crossover(wt2, 80)) <= 1 and crossunder_4 else na, location=location.absolute, style=shape.triangledown, color=color.yellow, size=size.tiny)
    crossover_9 = ta.crossover(wt2, 20)
    plotshape(wt2 - 9 if ta.barssince(ta.crossunder(wt2, 20)) <= 1 and crossover_9 else na, location=location.absolute, style=shape.triangleup, color=color.yellow, size=size.tiny)
    alertcondition(crossover, title='Crossover')
    alertcondition(crossunder, title='Crossunder')
    alertcondition(enter6 or enter7 or enter5 or enter3, title='Long')
    alertcondition(ta.crossunder(Quotient5, -0.9), title='Entry Zone')
    alertcondition(ta.crossover(q1, highUsePivot), title='Break Resistance')
    alertcondition(ta.crossunder(q1, lowUsePivot), title='Break Support')
    alertcondition(Quotient1 <= -0.9 and crossover, title='Crossover - Market Low')
    alertcondition(Quotient1 >= 0.9 and crossunder, title='Crossunder - Market High')
    alertcondition(wt2 <= 20 and crossover, title='Crossover With Pressure')
    alertcondition(wt2 >= 80 and crossunder, title='Crossunder With Pressure')
    alertcondition(ta.crossover(q1, highUsePivot) and dbreak >= 1 and (ubreak <= 1), title='Continuation')
    alertcondition(over, title='Orange - Overbought')
    alertcondition(over3, title='Red - Overbought')
    crossunder_5 = ta.crossunder(wt2, 80)
    alertcondition(ta.barssince(ta.crossover(wt2, 80)) <= 1 and crossunder_5, title='Bounce down')
    crossover_10 = ta.crossover(wt2, 20)
    alertcondition(ta.barssince(ta.crossunder(wt2, 20)) <= 1 and crossover_10, title='Bounce up')
    alertcondition(senter3, title='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
