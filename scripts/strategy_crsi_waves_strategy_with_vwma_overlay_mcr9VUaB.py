"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, close, color, fill, fixnan, high, hline, input, location,
    low, math, na, nz, open, plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Series

overlay: bool = True


@script.strategy('cRSI + Waves Strategy with VWMA overlay', overlay=overlay, max_bars_back=300, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    useVolume=input(title='Use Volume for VWMA (uncheck if equity does not have volume)', defval=True),
    vwmaLen=input.int(defval=21, title='VWMA Length', minval=1, maxval=200),
    smaLen1=input.int(defval=50, title='SMA #1 Length', minval=1, maxval=200),
    smaLen2=input.int(defval=100, title='SMA #2 Length', minval=1, maxval=200),
    domcycle=input.int(10, minval=5, title='cRSI Dominant Cycle Length (persist after high/low)'),
    crsiMaLen=input.int(title='cRSI Moving Average Length', defval=50, minval=0, step=5),
    topBottomLookback=input.int(title='cRSI Top/Bottom Detector Lookback (3 is more robust but misses smaller)', defval=2, minval=2, maxval=3, step=1),
    __input_7__=input(title='Plot Strong Impulse Waves (above upper band)', defval=True),
    __input_8__=input(title='Plot Weak Impulse Waves (below upper band)', defval=True),
    __input_9__=input(title='Plot Corrective Waves (ABC,ABCDE)', defval=True),
    __input_10__=input(title='Plot Bullish (cRSI Higher-Low : Price Lower-Low)', defval=True),
    __input_11__=input(title='Plot Hidden Bullish (cRSI Lower-Low : Price Higher-Low)', defval=True),
    __input_12__=input(title='Plot Bearish (cRSI Lower-High : Price Higher-High', defval=True),
    __input_13__=input(title='Plot Hidden Bearish (cRSI Higher-High : Price Lower-High)', defval=True)
):
    DEBUG: bool = False
    def b2i(bval):
        ival = 1 if bval else 0
        return ival

    def recentAbove(in_1: Series, thresh, lookback):
        found: bool = False
        for i in pine_range(0, lookback, 1):
            if in_1[i] >= thresh:
                found = True
                break
        __block_result__ = na
        if found:
            res: bool = True
            __block_result__ = res
        else:
            res: bool = False
            __block_result__ = res
        return __block_result__

    def isRisingFalling(in_2: Series, lookback):
        cntThresh = math.round(lookback * 0.6)
        cntUp: int = 0
        cntDown: int = 0
        rising: Series[bool] = False
        falling: Series[bool] = False
        for i in pine_range(1, lookback, 1):
            if in_2 > in_2[i]:
                cntUp = cntUp + 1
            elif in_2 < in_2[i]:
                cntDown = cntDown + 1
        if cntUp > cntThresh:
            rising = True
        else:
            rising = False
        if cntDown > cntThresh:
            falling = True
        else:
            falling = False
        flat = not rising and (not falling)
        if flat:
            rising = rising[1]
            falling = falling[1]
        return (rising, falling, flat)

    def isTop(price: Series, lookback):
        __block_result_1__ = na
        if lookback == 3:
            __block_result_2__ = na
            if price[2] > price[3] and price[1] > price[2] and (price < price[1]):
                top: bool = True
                __block_result_2__ = top
            else:
                top: bool = False
                __block_result_2__ = top
            __block_result_1__ = __block_result_2__
        else:
            __block_result_3__ = na
            if price[1] > price[2] and price < price[1]:
                top: bool = True
                __block_result_3__ = top
            else:
                top: bool = False
                __block_result_3__ = top
            __block_result_1__ = __block_result_3__
        return __block_result_1__

    def isBottom(price: Series, lookback):
        __block_result_4__ = na
        if lookback == 3:
            __block_result_5__ = na
            if price[2] < price[3] and price[1] < price[2] and (price > price[1]):
                bottom: bool = True
                __block_result_5__ = bottom
            else:
                bottom: bool = False
                __block_result_5__ = bottom
            __block_result_4__ = __block_result_5__
        else:
            __block_result_6__ = na
            if price[1] < price[2] and price > price[1]:
                bottom: bool = True
                __block_result_6__ = bottom
            else:
                bottom: bool = False
                __block_result_6__ = bottom
            __block_result_4__ = __block_result_6__
        return __block_result_4__

    def filterSignal(signalFlag, lookback):
        signalFlagFilt: Series = signalFlag
        __block_result_7__ = na
        for i in pine_range(1, lookback, 1):
            signalFlagFilt = False if signalFlagFilt == True and signalFlagFilt[i] == True else signalFlagFilt
            __block_result_7__ = signalFlagFilt
        return __block_result_7__

    priceRising = close >= close[1] and close[1] >= close[2]
    priceFalling = close <= close[1] and close[1] <= close[2]
    plotVWMA = overlay and (not DEBUG)
    vwma = ta.vwma(close, vwmaLen)
    vwma_high = ta.vwma(high, vwmaLen)
    vwma_low = ta.vwma(low, vwmaLen)
    if not useVolume:
        vwma = ta.wma(close, vwmaLen)
        vwma_high = ta.wma(high, vwmaLen)
        vwma_low = ta.wma(low, vwmaLen)
    def vwmaSignal(priceOpen, priceClose, vwmaHigh, vwmaLow):
        sig: int = 0
        color__ren__ = color.gray
        if priceClose > vwmaHigh:
            sig = 1
            color__ren__ = color.green
        elif priceClose < vwmaLow:
            sig = -1
            color__ren__ = color.red
        else:
            sig = 0
            color__ren__ = color.gray
        return (sig, color__ren__)

    vwma_sig, vwma_color = vwmaSignal(open, close, vwma_high, vwma_low)
    priceAboveVWMA = True if vwma_sig == 1 else False
    priceBelowVWMA = True if vwma_sig == -1 else False
    bandTrans: int = 70
    fillTrans: int = 70
    highband = plot(fixnan(vwma_high) if plotVWMA else na, title='VWMA High band', color=vwma_color, linewidth=1)
    lowband = plot(fixnan(vwma_low) if plotVWMA else na, title='VWMA Low band', color=vwma_color, linewidth=1)
    fill(lowband, highband, title='VWMA Band fill', color=color.new(vwma_color, fillTrans))
    plot(vwma if plotVWMA else na, title='VWMA', color=vwma_color, linewidth=3)
    smaLineWidth: int = 8
    plot(ta.sma(close, smaLen1), title='SMA', color=color.new(color.blue, 0), linewidth=math.max(1, smaLineWidth))
    plot(ta.sma(close, smaLen2), title='SMA', color=color.new(color.black, 0), linewidth=math.max(1, smaLineWidth))
    histLine: Series
    macdLine, signalLine, histLine = ta.macd(close, 12, 26, 9)
    histLineRising = histLine >= histLine[1] and histLine[1] >= histLine[2]
    histLineFalling = histLine <= histLine[1] and histLine[1] <= histLine[2]
    histLineCrossNeg2Pos = histLine >= 0.0 and histLine[1] < 0.0
    histLineCrossPos2Neg = histLine <= 0.0 and histLine[1] > 0.0
    plotCRSI = not overlay and (not DEBUG)
    src = close
    crsi: Series[float] = 0.0
    cyclelen = domcycle / 2
    vibration: int = 10
    leveling: float = 10.0
    cyclicmemory = domcycle * 2
    torque = 2.0 / (vibration + 1)
    phasingLag = (vibration - 1) / 2.0
    up = ta.rma(math.max(ta.change(src), 0), cyclelen)
    down = ta.rma(-math.min(ta.change(src), 0), cyclelen)
    rsi: Series = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    crsi = torque * (2 * rsi - rsi[phasingLag]) + (1 - torque) * nz(crsi[1])
    lmax: float = 0.0
    lmin: float = 0.0
    for i in pine_range(0, cyclicmemory - 1, 1):
        if nz(crsi[i], -999999.0) > lmax:
            lmax = nz(crsi[i])
        else:
            if nz(crsi[i], 999999.0) < lmin:
                lmin = nz(crsi[i])
    mstep = (lmax - lmin) / 100
    aperc = leveling / 100
    crsiLowband: float = 0.0
    for steps in pine_range(0, 100, 1):
        testvalue = lmin + mstep * steps
        above: int = 0
        below: int = 0
        for m in pine_range(0, cyclicmemory - 1, 1):
            below = below + (1 if crsi[m] < testvalue else 0)
        ratio = below / cyclicmemory
        if ratio >= aperc:
            crsiLowband = testvalue
            break
        else:
            continue
    crsiHighband: float = 0.0
    for steps in pine_range(0, 100, 1):
        testvalue = lmax - mstep * steps
        above: int = 0
        for m in pine_range(0, cyclicmemory - 1, 1):
            above = above + (1 if crsi[m] >= testvalue else 0)
        ratio = above / cyclicmemory
        if ratio >= aperc:
            crsiHighband = testvalue
            break
        else:
            continue
    crsiWMA = ta.wma(crsi, crsiMaLen)
    crsiAboveHighband: Series = crsi >= crsiHighband
    crsiBelowHighband: Series = not crsiAboveHighband
    crsiCrossAboveHighband = True if crsiAboveHighband and crsiBelowHighband[1] else False
    crsiCrossBelowHighband = True if crsiBelowHighband and crsiAboveHighband[1] else False
    crsiAboveLowband: Series = crsi >= crsiLowband
    crsiBelowLowband: Series = not crsiAboveLowband
    crsiCrossAboveLowband = True if crsiAboveLowband and crsiBelowLowband[1] else False
    crsiCrossBelowLowband = True if crsiBelowLowband and crsiAboveLowband[1] else False
    crsiAboveWMA: Series = crsi >= crsiWMA
    crsiBelowWMA: Series = not crsiAboveWMA
    crsiCrossAboveWMA = True if crsiAboveWMA and crsiBelowWMA[1] else False
    crsiCrossBelowWMA = True if crsiBelowWMA and crsiAboveWMA[1] else False
    crsiAbove50: Series = crsi >= 50
    crsiBelow50: Series = not crsiAbove50
    crsiCrossAbove50 = True if crsiAbove50 and crsiBelow50[1] else False
    crsiCrossBelow50 = True if crsiBelow50 and crsiAbove50[1] else False
    crsiRising = crsi >= crsi[1]
    crsiFalling = crsi < crsi[1]
    bull: Series = crsiAboveWMA
    bear: Series = not bull
    bullBearColor = color.green if bull else color.red
    bullStart = True if bull and bear[1] else False
    bearStart = True if bear and bull[1] else False
    alertcondition(bullStart, title='Bull - cRSI above WMA', message='Bull - cRSI above WMA')
    alertcondition(bearStart, title='Bear - cRSI below WMA', message='Bear - cRSI below WMA')
    hline(50 if plotCRSI else na, title='Middle Line', linestyle=hline.style_dashed, linewidth=2)
    h2 = hline(70 if plotCRSI else na, title='Overbought', linestyle=hline.style_dashed, linewidth=2)
    h1 = hline(30 if plotCRSI else na, title='Oversold', linestyle=hline.style_dashed, linewidth=2)
    fill(h1, h2, color=color.new(color.silver, 80))
    crsiLB2 = plot(crsiLowband if plotCRSI else na, 'cRSI LowBand', bullBearColor)
    crsiHB2 = plot(crsiHighband if plotCRSI else na, 'cRSI HighBand', bullBearColor)
    fill(crsiLB2, crsiHB2, color.new(bullBearColor, 75))
    plot(crsiWMA if plotCRSI else na, 'CRSI WMA', color.new(color.fuchsia, 0), linewidth=2)
    plot(crsi if plotCRSI else na, 'CRSI', color.new(color.black, 0), linewidth=4)
    motiveWave = bull
    correctiveWave = bear
    crsiTop = isTop(crsi, topBottomLookback)
    crsiBottom = isBottom(crsi, topBottomLookback)
    crsiTopAboveHighband = crsiTop and crsiAboveHighband[1]
    waveStrongImpulse = crsiTopAboveHighband
    crsiTopBelowHighband = crsiTop and crsiBelowHighband[1] and (crsi > crsiWMA)
    waveWeakImpulse = crsiTopBelowHighband
    possibleWaveA = crsiBottom and crsiBelowLowband[1]
    possibleWaveB = crsiTop and crsiBelowWMA[1] or (crsiTop and crsiBelow50[1])
    possibleWaveC = possibleWaveA or (crsiBottom and crsiBelowWMA[1])
    def findWaveAB(possibleWaveA: Series, possibleWaveB, correctiveWave: Series):
        isWaveAB: bool = False
        foundMatch: bool = False
        __block_result_8__ = na
        if possibleWaveB:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if possibleWaveA[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_9__ = na
            if foundMatch:
                isWaveAB = True
                __block_result_9__ = isWaveAB
            else:
                isWaveAB = False
                __block_result_9__ = isWaveAB
            __block_result_8__ = __block_result_9__
        else:
            isWaveAB = False
            __block_result_8__ = isWaveAB
        return __block_result_8__

    waveAB = findWaveAB(possibleWaveA, possibleWaveB, correctiveWave)
    def findWaveABC(possibleWaveC, waveAB: Series, correctiveWave: Series):
        isWaveABC: bool = False
        foundMatch: bool = False
        __block_result_10__ = na
        if possibleWaveC:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if waveAB[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_11__ = na
            if foundMatch:
                isWaveABC = True
                __block_result_11__ = isWaveABC
            else:
                isWaveABC = False
                __block_result_11__ = isWaveABC
            __block_result_10__ = __block_result_11__
        else:
            isWaveABC = False
            __block_result_10__ = isWaveABC
        return __block_result_10__

    waveABC = findWaveABC(possibleWaveC, waveAB, correctiveWave)
    def findWaveABCD(possibleWaveB, waveABC: Series, correctiveWave: Series):
        isWaveABCD: bool = False
        foundMatch: bool = False
        __block_result_12__ = na
        if possibleWaveB:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if waveABC[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_13__ = na
            if foundMatch:
                isWaveABCD = True
                __block_result_13__ = isWaveABCD
            else:
                isWaveABCD = False
                __block_result_13__ = isWaveABCD
            __block_result_12__ = __block_result_13__
        else:
            isWaveABCD = False
            __block_result_12__ = isWaveABCD
        return __block_result_12__

    waveABCD = findWaveABCD(possibleWaveB, waveABC, correctiveWave)
    def findWaveABCDE(possibleWaveC, waveABCD: Series, correctiveWave: Series):
        isWaveABCDE: bool = False
        foundMatch: bool = False
        __block_result_14__ = na
        if possibleWaveC:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if waveABCD[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_15__ = na
            if foundMatch:
                isWaveABCDE = True
                __block_result_15__ = isWaveABCDE
            else:
                isWaveABCDE = False
                __block_result_15__ = isWaveABCDE
            __block_result_14__ = __block_result_15__
        else:
            isWaveABCDE = False
            __block_result_14__ = isWaveABCDE
        return __block_result_14__

    waveABCDE = findWaveABCDE(possibleWaveC, waveABCD, correctiveWave)
    def findWaveABCDEF(possibleWaveB, waveABCDE: Series, correctiveWave: Series):
        isWaveABCDEF: bool = False
        foundMatch: bool = False
        __block_result_16__ = na
        if possibleWaveB:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if waveABCDE[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_17__ = na
            if foundMatch:
                isWaveABCDEF = True
                __block_result_17__ = isWaveABCDEF
            else:
                isWaveABCDEF = False
                __block_result_17__ = isWaveABCDEF
            __block_result_16__ = __block_result_17__
        else:
            isWaveABCDEF = False
            __block_result_16__ = isWaveABCDEF
        return __block_result_16__

    waveABCDEF = findWaveABCDEF(possibleWaveB, waveABCDE, correctiveWave)
    def findWaveABCDEFG(possibleWaveC, waveABCDEF: Series, correctiveWave: Series):
        isWaveABCDEFG: bool = False
        foundMatch: bool = False
        __block_result_18__ = na
        if possibleWaveC:
            for i in pine_range(1, 50, 1):
                if correctiveWave[i]:
                    if waveABCDEF[i]:
                        foundMatch = True
                        break
                else:
                    foundMatch = False
                    break
            __block_result_19__ = na
            if foundMatch:
                isWaveABCDEFG = True
                __block_result_19__ = isWaveABCDEFG
            else:
                isWaveABCDEFG = False
                __block_result_19__ = isWaveABCDEFG
            __block_result_18__ = __block_result_19__
        else:
            isWaveABCDEFG = False
            __block_result_18__ = isWaveABCDEFG
        return __block_result_18__

    waveABCDEFG = findWaveABCDEFG(possibleWaveC, waveABCDEF, correctiveWave)
    waveA = possibleWaveA and (not waveABC) and (not waveABCDE)
    waveB = waveAB and (not waveABCD)
    waveC = waveABC
    waveD = waveABCD
    waveE = waveABCDE
    waveF = waveABCDEF
    waveG = waveABCDEFG
    plotStrong = __input_7__ and plotCRSI
    plotWeak = __input_8__ and plotCRSI
    impWaveSz = size.tiny
    plotshape(crsi[1] if plotStrong and waveStrongImpulse else na, text='s', title='Strong Impulse', style=shape.labeldown, location=location.absolute, color=color.new(color.navy, 0), offset=-1, textcolor=color.new(color.white, 0), size=impWaveSz)
    plotshape(crsi[1] if plotWeak and waveWeakImpulse else na, text='w', title='Weak Impulse', style=shape.labeldown, location=location.absolute, color=color.new(color.purple, 0), offset=-1, textcolor=color.new(color.white, 0), size=impWaveSz)
    plotWaves = __input_9__ and plotCRSI
    corWaveSz = size.small
    plotshape(crsi[1] if plotWaves and waveA else na, text='A', title='Wave A', style=shape.labelup, location=location.absolute, color=color.new(color.blue, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveB else na, text='B', title='Wave B', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveC else na, text='C', title='Wave C', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveD else na, text='D', title='Wave D', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveE else na, text='E', title='Wave E', style=shape.labelup, location=location.absolute, color=color.new(color.lime, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveF else na, text='F', title='Wave F', style=shape.labeldown, location=location.absolute, color=color.new(color.fuchsia, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] if plotWaves and waveG else na, text='G', title='Wave G', style=shape.labelup, location=location.absolute, color=color.new(color.aqua, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotBull = __input_10__ and plotCRSI
    plotHiddenBull = __input_11__ and plotCRSI
    plotBear = __input_12__ and plotCRSI
    plotHiddenBear = __input_13__ and plotCRSI
    crsiHighs = waveStrongImpulse or waveWeakImpulse
    crsiLows = possibleWaveA or possibleWaveC
    def bullish(crsiLows: Series, crsi: Series, price: Series):
        foundLow: bool = False
        crsiHigherLow: bool = False
        priceHigher: bool = False
        regularBullish: bool = False
        hiddenBullish: bool = False
        if crsiLows == True:
            for i in pine_range(1, 50, 1):
                if crsiLows[i] == True:
                    foundLow = True
                    if crsi > crsi[i]:
                        crsiHigherLow = True
                    else:
                        crsiHigherLow = False
                    if price > price[i]:
                        priceHigher = True
                    else:
                        priceHigher = False
                    break
                else:
                    continue
            if foundLow:
                if crsiHigherLow == True and priceHigher == False:
                    regularBullish = True
                    hiddenBullish = False
                elif crsiHigherLow == False and priceHigher == True:
                    regularBullish = False
                    hiddenBullish = True
                else:
                    regularBullish = False
                    hiddenBullish = False
            else:
                regularBullish = False
                hiddenBullish = False
        else:
            regularBullish = False
            hiddenBullish = False
        return (regularBullish, hiddenBullish)

    regularBullish, hiddenBullish = bullish(crsiLows, crsi, close)
    plotshape(crsi[1] - 12 if plotBull and regularBullish else na, text='Bull', title='Bull', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] - 12 if plotHiddenBull and hiddenBullish else na, text='H Bull', title='Hidden Bull', style=shape.labelup, location=location.absolute, color=color.new(color.green, 20), offset=-1, textcolor=color.new(color.white, 20), size=corWaveSz)
    def bearish(crsiHighs: Series, crsi: Series, price: Series):
        foundHigh: bool = False
        crsiHigherHigh: bool = False
        priceHigher: bool = False
        regularBearish: bool = False
        hiddenBearish: bool = False
        if crsiHighs == True:
            for i in pine_range(1, 50, 1):
                if crsiHighs[i] == True:
                    foundHigh = True
                    if crsi > crsi[i]:
                        crsiHigherHigh = True
                    else:
                        crsiHigherHigh = False
                    if price > price[i]:
                        priceHigher = True
                    else:
                        priceHigher = False
                    break
                else:
                    continue
            if foundHigh:
                if crsiHigherHigh == False and priceHigher == True:
                    regularBearish = True
                    hiddenBearish = False
                elif crsiHigherHigh == True and priceHigher == False:
                    regularBearish = False
                    hiddenBearish = True
                else:
                    regularBearish = False
                    hiddenBearish = False
            else:
                regularBearish = False
                hiddenBearish = False
        else:
            regularBearish = False
            hiddenBearish = False
        return (regularBearish, hiddenBearish)

    regularBearish, hiddenBearish = bearish(crsiHighs, crsi, close)
    plotshape(crsi[1] + 10 if plotBear and regularBearish else na, text='Bear', title='Bear', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), offset=-1, textcolor=color.new(color.white, 0), size=corWaveSz)
    plotshape(crsi[1] + 10 if plotHiddenBear and hiddenBearish else na, text='H Bear', title='Hidden Bear', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 20), offset=-1, textcolor=color.new(color.white, 20), size=corWaveSz)
    filterLookback: int = 5
    def normalize(val, valMin, valMax):
        valNorm = val
        valNorm = valMin if valNorm < valMin else valNorm
        valNorm = valMax if valNorm > valMax else valNorm
        valNorm = (valNorm - valMin) / (valMax - valMin)
        return valNorm

    def recentWave(wave: Series, lookback):
        ret: bool = False
        found: bool = False
        for i in pine_range(0, lookback, 1):
            if wave[i] == True:
                found = True
                break
        __block_result_20__ = na
        if found:
            ret = True
            __block_result_20__ = ret
        else:
            ret = False
            __block_result_20__ = ret
        return __block_result_20__

    crsiHighband_extremeHighLevel: int = 90
    crsiHighband_highLevel: int = 70
    crsiHighband_highWeight = normalize(crsiHighband, crsiHighband_highLevel, crsiHighband_extremeHighLevel)
    crsiHighband_extremeLowLevel: int = 45
    crsiHighband_lowLevel: int = 55
    crsiHighband_lowWeight = 1.0 - normalize(crsiHighband, crsiHighband_extremeLowLevel, crsiHighband_lowLevel)
    crsiLowband_extremeHighLevel: int = 80
    crsiLowband_highLevel: int = 60
    crsiLowband_higheight = normalize(crsiLowband, crsiLowband_highLevel, crsiLowband_extremeHighLevel)
    crsiLowband_extremeLowLevel: int = 20
    crsiLowband_lowLevel: int = 45
    crsiLowband_lowWeight = 1.0 - normalize(crsiLowband, crsiLowband_extremeLowLevel, crsiLowband_lowLevel)
    maxSellOrderSize: int = 10
    crsiHighband_above_crsiHighband_highLevel = True if crsiHighband > crsiHighband_highLevel else False
    Sell1 = waveStrongImpulse
    Sell2 = True if crsiAboveHighband and crsiFalling else False
    Sell3 = True if crsiAboveHighband[1] and crsiFalling else False
    Sell4 = True if crsiAboveHighband[2] and crsiFalling else False
    Sell = (Sell1 or Sell2 or Sell3 or Sell4) and crsiHighband_above_crsiHighband_highLevel
    Sell = filterSignal(Sell, filterLookback)
    sellSize = crsiHighband_highWeight * maxSellOrderSize
    sellSize = 1.5 * maxSellOrderSize if crsi > crsiHighband_extremeHighLevel else sellSize
    sellSize = 0 if sellSize < cast_int(maxSellOrderSize / 3) else sellSize
    sellSize = math.round(sellSize)
    if Sell:
        strategy.order('Sell', strategy.short, sellSize)
    maxBuyOrderSize: int = 10
    Buy1 = bullStart
    Buy2 = waveA and regularBullish
    Buy3 = waveC and regularBullish
    Buy4 = waveE and topBottomLookback == 3
    Buy5 = waveG and topBottomLookback == 2
    Buy = Buy1 or Buy2 or Buy3 or Buy4 or Buy5
    Buy = filterSignal(Buy, filterLookback)
    buySize = crsiLowband_lowWeight * maxBuyOrderSize
    recentWaveC = recentWave(waveC, 10)
    recentWaveE = recentWave(waveE, 10)
    recentWaveG = recentWave(waveG, 10)
    buySize = maxBuyOrderSize if recentWaveE else buySize
    buySize = maxBuyOrderSize if recentWaveG else buySize
    buySize = 0 if buySize < cast_int(maxSellOrderSize / 3) else buySize
    buySize = math.round(buySize)
    if Buy:
        strategy.order('Buy', strategy.long, buySize)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
