"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barmerge, bgcolor, close, color, fill, high, hlc3, input,
    location, low, math, na, nz, open, plot, plotchar, request, script, size, syminfo, ta, ticker,
    timeframe
)
from pynecore.types import Color, Series


@script.indicator(title='VuManChu B Divergences', shorttitle='VMC Cipher_B_Divergences', na_bool=True)
def main(
    wtShow=input.bool(True, title='Show WaveTrend', group='WaveTrend Settings'),
    wtBuyShow=input.bool(True, title='Show Buy dots', group='WaveTrend Settings'),
    wtGoldShow=input.bool(True, title='Show Gold dots', group='WaveTrend Settings'),
    wtSellShow=input.bool(True, title='Show Sell dots', group='WaveTrend Settings'),
    wtDivShow=input.bool(True, title='Show Div. dots', group='WaveTrend Settings'),
    vwapShow=input.bool(True, title='Show Fast WT', group='WaveTrend Settings'),
    wtChannelLen=input.int(9, title='WT Channel Length', group='WaveTrend Settings'),
    wtAverageLen=input.int(12, title='WT Average Length', group='WaveTrend Settings'),
    wtMASource: Series[float] = input.source(hlc3, title='WT MA Source', group='WaveTrend Settings'),
    wtMALen=input.int(3, title='WT MA Length', group='WaveTrend Settings'),
    obLevel=input.int(53, title='WT Overbought Level 1', group='WaveTrend Settings'),
    obLevel2=input.int(60, title='WT Overbought Level 2', group='WaveTrend Settings'),
    obLevel3=input.int(100, title='WT Overbought Level 3', group='WaveTrend Settings'),
    osLevel=input.int(-53, title='WT Oversold Level 1', group='WaveTrend Settings'),
    osLevel2=input.int(-60, title='WT Oversold Level 2', group='WaveTrend Settings'),
    osLevel3=input.int(-75, title='WT Oversold Level 3', group='WaveTrend Settings'),
    wtShowDiv=input.bool(True, title='Show WT Regular Divergences', group='WaveTrend Settings'),
    wtShowHiddenDiv=input.bool(False, title='Show WT Hidden Divergences', group='WaveTrend Settings'),
    showHiddenDiv_nl=input.bool(True, title='Not apply OB/OS Limits on Hidden Divergences', group='WaveTrend Settings'),
    wtDivOBLevel=input.int(45, title='WT Bearish Divergence min', group='WaveTrend Settings'),
    wtDivOSLevel=input.int(-65, title='WT Bullish Divergence min', group='WaveTrend Settings'),
    wtDivOBLevel_addshow=input.bool(True, title='Show 2nd WT Regular Divergences', group='WaveTrend Settings'),
    wtDivOBLevel_add=input.int(15, title='WT 2nd Bearish Divergence', group='WaveTrend Settings'),
    wtDivOSLevel_add=input.int(-40, title='WT 2nd Bullish Divergence 15 min', group='WaveTrend Settings'),
    rsiMFIShow=input.bool(True, title='Show MFI', group='MFI Settings'),
    rsiMFIperiod=input.int(60, title='MFI Period', group='MFI Settings'),
    rsiMFIMultiplier=input.float(150, title='MFI Area multiplier', group='MFI Settings'),
    rsiMFIPosY=input.float(2.5, title='MFI Area Y Pos', group='MFI Settings'),
    rsiShow=input.bool(True, title='Show RSI', group='RSI Settings'),
    rsiSRC: Series[float] = input.source(close, title='RSI Source', group='RSI Settings'),
    rsiLen=input.int(14, title='RSI Length', group='RSI Settings'),
    rsiOversold=input.int(30, title='RSI Oversold', minval=50, maxval=100, group='RSI Settings'),
    rsiOverbought=input.int(60, title='RSI Overbought', minval=0, maxval=50, group='RSI Settings'),
    rsiShowDiv=input.bool(False, title='Show RSI Regular Divergences', group='RSI Settings'),
    rsiShowHiddenDiv=input.bool(False, title='Show RSI Hidden Divergences', group='RSI Settings'),
    rsiDivOBLevel=input.int(60, title='RSI Bearish Divergence min', group='RSI Settings'),
    rsiDivOSLevel=input.int(30, title='RSI Bullish Divergence min', group='RSI Settings'),
    stochShow=input.bool(True, title='Show Stochastic RSI', group='Stoch Settings'),
    stochUseLog=input.bool(True, title=' Use Log?', group='Stoch Settings'),
    stochAvg=input.bool(False, title='Use Average of both K & D', group='Stoch Settings'),
    stochSRC: Series[float] = input.source(close, title='Stochastic RSI Source', group='Stoch Settings'),
    stochLen=input.int(14, title='Stochastic RSI Length', group='Stoch Settings'),
    stochRsiLen=input.int(14, title='RSI Length ', group='Stoch Settings'),
    stochKSmooth=input.int(3, title='Stochastic RSI K Smooth', group='Stoch Settings'),
    stochDSmooth=input.int(3, title='Stochastic RSI D Smooth', group='Stoch Settings'),
    stochShowDiv=input.bool(False, title='Show Stoch Regular Divergences', group='Stoch Settings'),
    stochShowHiddenDiv=input.bool(False, title='Show Stoch Hidden Divergences', group='Stoch Settings'),
    tcLine=input.bool(False, title='Show Schaff TC line', group='Schaff Settings'),
    tcSRC: Series[float] = input.source(close, title='Schaff TC Source', group='Schaff Settings'),
    tclength=input.int(10, title='Schaff TC', group='Schaff Settings'),
    tcfastLength=input.int(23, title='Schaff TC Fast Lenght', group='Schaff Settings'),
    tcslowLength=input.int(50, title='Schaff TC Slow Length', group='Schaff Settings'),
    tcfactor=input.float(0.5, title='Schaff TC Factor', group='Schaff Settings'),
    sommiFlagShow=input.bool(False, title='Show Sommi flag', group='Sommi Settings'),
    sommiShowVwap=input.bool(False, title='Show Sommi F. Wave', group='Sommi Settings'),
    sommiVwapTF=input.string('720', title='Sommi F. Wave timeframe', group='Sommi Settings'),
    sommiVwapBearLevel=input.int(0, title='F. Wave Bear Level (less than)', group='Sommi Settings'),
    sommiVwapBullLevel=input.int(0, title='F. Wave Bull Level (more than)', group='Sommi Settings'),
    soomiFlagWTBearLevel=input.int(0, title='WT Bear Level (more than)', group='Sommi Settings'),
    soomiFlagWTBullLevel=input.int(0, title='WT Bull Level (less than)', group='Sommi Settings'),
    soomiRSIMFIBearLevel=input.int(0, title='Money flow Bear Level (less than)', group='Sommi Settings'),
    soomiRSIMFIBullLevel=input.int(0, title='Money flow Bull Level (more than)', group='Sommi Settings'),
    sommiDiamondShow=input.bool(False, title='Show Sommi diamond', group='Sommi Settings'),
    sommiHTCRes=input.string('60', title='HTF Candle Res. 1', group='Sommi Settings'),
    sommiHTCRes2=input.string('240', title='HTF Candle Res. 2', group='Sommi Settings'),
    soomiDiamondWTBearLevel=input.int(0, title='WT Bear Level (More than)', group='Sommi Settings'),
    soomiDiamondWTBullLevel=input.int(0, title='WT Bull Level (Less than)', group='Sommi Settings'),
    macdWTColorsShow=input.bool(False, title='Show MACD Colors', group='MACD Settings'),
    macdWTColorsTF=input.string('240', title='MACD Colors MACD TF', group='MACD Settings'),
    darkMode=input.bool(False, title='Dark mode', group='Mode Settings'),
    rsiobcolor=input.color(color.new(color.new('#E13E3E'), 0), 'RSI OverBought', group='Color Settings'),
    rsioscolor=input.color(color.new(color.new('#3EE145'), 0), 'RSI OverSold', group='Color Settings'),
    rsinacolor=input.color(color.new(color.new('#C33EE1'), 0), 'RSI InBetween', group='Color Settings'),
    rsiMFIColorAbove=input.color(color.new(color.new('#3EE145'), 0), 'MFI Color > 0', group='Color Settings'),
    rsiMFIColorBelow=input.color(color.new(color.new('#FF3D2E'), 0), 'MFI Color < 0', group='Color Settings'),
    WTBearDivColorDown=input.color(color.new(color.new('#E60000'), 0), 'WT Bear Div', group='Color Settings'),
    wtBullDivColorUp=input.color(color.new(color.new('#00E676'), 0), 'WT Bull Div', group='Color Settings'),
    signalcolorup=input.color(color.new(color.new('#00E676'), 0), 'WT Buy Dot', group='Color Settings'),
    signalcolordown=input.color(color.new(color.new('#FF5252'), 0), 'WT Sell Dot', group='Color Settings'),
    colorWT1blue=input.color(color.new(color.new('#4994EC'), 0), 'WT1 Fill', group='Color Settings'),
    colorWT2purple=input.color(color.new(color.new('#1F1559'), 0), 'WT2 Fill', group='Color Settings'),
    VWAPColor=input.color(color.new(color.new('#FFFFFF'), 50), 'VWAP', group='Color Settings'),
    stochkcolor=input.color(color.new(color.new('#21BAF3'), 70), 'Stoch K', group='Color Settings'),
    stochdcolor=input.color(color.new(color.new('#673AB7'), 90), 'Stoch D', group='Color Settings')
):
    colorRed: Color = color.new('#FF0000')
    colorPurple: Color = color.new('#E600E6')
    colorGreen: Color = color.new('#3FFF00')
    colorOrange: Color = color.new('#E2A400')
    colorYellow: Color = color.new('#FFE500')
    colorWhite: Color = color.new('#FFFFFF')
    colorPink: Color = color.new('#FF00F0')
    colorBluelight: Color = color.new('#31C0FF')
    colorWT2: Color = color.new('#0D47A1')
    colorWT2_: Color = color.new('#131722')
    colormacdWT1a: Color = color.new('#4CAF58')
    colormacdWT1b: Color = color.new('#AF4C4C')
    colormacdWT1c: Color = color.new('#7EE57E')
    colormacdWT1d: Color = color.new('#FF3535')
    colormacdWT2a: Color = color.new('#305630')
    colormacdWT2b: Color = color.new('#310101')
    colormacdWT2c: Color = color.new('#132213')
    colormacdWT2d: Color = color.new('#770000')
    def f_top_fractal(src: Series):
        return src[4] < src[2] and src[3] < src[2] and (src[2] > src[1]) and (src[2] > src)

    def f_bot_fractal(src: Series):
        return src[4] > src[2] and src[3] > src[2] and (src[2] < src[1]) and (src[2] < src)

    def f_fractalize(src):
        return 1 if f_top_fractal(src) else -1 if f_bot_fractal(src) else 0

    def f_findDivs(src: Series, topLimit, botLimit, useLimits):
        fractalTop = src[2] if f_fractalize(src) > 0 and (src[2] >= topLimit if useLimits else True) else na
        fractalBot = src[2] if f_fractalize(src) < 0 and (src[2] <= botLimit if useLimits else True) else na
        highPrev = inline_series(ta.valuewhen(fractalTop, src[2], 0), 2)
        highPrice = inline_series(ta.valuewhen(fractalTop, high[2], 0), 2)
        lowPrev = inline_series(ta.valuewhen(fractalBot, src[2], 0), 2)
        lowPrice = inline_series(ta.valuewhen(fractalBot, low[2], 0), 2)
        bearSignal = fractalTop and high[2] > highPrice and (src[2] < highPrev)
        bullSignal = fractalBot and low[2] < lowPrice and (src[2] > lowPrev)
        bearDivHidden = fractalTop and high[2] < highPrice and (src[2] > highPrev)
        bullDivHidden = fractalBot and low[2] > lowPrice and (src[2] < lowPrev)
        return (fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden)

    def f_rsimfi(_period, _multiplier, _tf):
        return request.security(syminfo.tickerid, _tf, ta.sma((close - open) / (high - low) * _multiplier, _period) - rsiMFIPosY)

    def f_wavetrend(src, chlen, avg, malen, tf):
        tfsrc = request.security(syminfo.tickerid, tf, src)
        esa = ta.ema(tfsrc, chlen)
        de = ta.ema(math.abs(tfsrc - esa), chlen)
        ci = (tfsrc - esa) / (0.015 * de)
        wt1: Series = request.security(syminfo.tickerid, tf, ta.ema(ci, avg))
        wt2: Series = request.security(syminfo.tickerid, tf, ta.sma(wt1, malen))
        wtVwap = wt1 - wt2
        wtOversold = wt2 <= osLevel
        wtOverbought = wt2 >= obLevel
        wtCross = ta.cross(wt1, wt2)
        wtCrossUp = wt2 - wt1 <= 0
        wtCrossDown = wt2 - wt1 >= 0
        wtCrosslast = ta.cross(wt1[2], wt2[2])
        wtCrossUplast = wt2[2] - wt1[2] <= 0
        wtCrossDownlast = wt2[2] - wt1[2] >= 0
        return (wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCrosslast, wtCrossUplast, wtCrossDownlast, wtVwap)

    def f_tc(src, length, fastLength, slowLength):
        ema1 = ta.ema(src, fastLength)
        ema2 = ta.ema(src, slowLength)
        macdVal = ema1 - ema2
        alpha = ta.lowest(macdVal, length)
        beta = ta.highest(macdVal, length) - alpha
        gamma: Series = (macdVal - alpha) / beta * 100
        gamma = gamma if beta > 0 else nz(gamma[1])
        delta: Series = gamma
        delta = delta if na(delta[1]) else delta[1] + tcfactor * (gamma - delta[1])
        epsilon = ta.lowest(delta, length)
        zeta = ta.highest(delta, length) - epsilon
        eta: Series = (delta - epsilon) / zeta * 100
        eta = eta if zeta > 0 else nz(eta[1])
        stcReturn: Series = eta
        stcReturn = stcReturn if na(stcReturn[1]) else stcReturn[1] + tcfactor * (eta - stcReturn[1])
        return stcReturn

    def f_stochrsi(_src, _stochlen, _rsilen, _smoothk, _smoothd, _log, _avg):
        src = math.log(_src) if _log else _src
        rsi = ta.rsi(src, _rsilen)
        kk = ta.sma(ta.stoch(rsi, rsi, rsi, _stochlen), _smoothk)
        d1 = ta.sma(kk, _smoothd)
        avg_1 = math.avg(kk, d1)
        k = avg_1 if _avg else kk
        return (k, d1)

    def f_macd(src, fastlen, slowlen, sigsmooth, tf):
        fast_ma = request.security(syminfo.tickerid, tf, ta.ema(src, fastlen))
        slow_ma = request.security(syminfo.tickerid, tf, ta.ema(src, slowlen))
        macd = fast_ma - slow_ma
        signal = request.security(syminfo.tickerid, tf, ta.sma(macd, sigsmooth))
        hist = macd - signal
        return (macd, signal, hist)

    def f_macdWTColors(tf):
        hrsimfi = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, tf)
        macd, signal, hist = f_macd(close, 28, 42, 9, macdWTColorsTF)
        macdup = macd >= signal
        macddown = macd <= signal
        macdWT1Color = (colormacdWT1c if hrsimfi > 0 else colormacdWT1a) if macdup else (colormacdWT1d if hrsimfi < 0 else colormacdWT1b) if macddown else na
        macdWT2Color = (colormacdWT2c if hrsimfi < 0 else colormacdWT2a) if macdup else (colormacdWT2d if hrsimfi < 0 else colormacdWT2b) if macddown else na
        return (macdWT1Color, macdWT2Color)

    def f_getTFCandle(_tf):
        _open = request.security(ticker.heikinashi(syminfo.tickerid), _tf, open, barmerge.gaps_off, barmerge.lookahead_on)
        _close = request.security(ticker.heikinashi(syminfo.tickerid), _tf, close, barmerge.gaps_off, barmerge.lookahead_on)
        _high = request.security(ticker.heikinashi(syminfo.tickerid), _tf, high, barmerge.gaps_off, barmerge.lookahead_on)
        _low = request.security(ticker.heikinashi(syminfo.tickerid), _tf, low, barmerge.gaps_off, barmerge.lookahead_on)
        hl2 = (_high + _low) / 2.0
        newBar = ta.change(_open)
        candleBodyDir = _close > _open
        return (candleBodyDir, newBar)

    def f_findSommiFlag(tf, wt1, wt2, rsimfi, wtCross, wtCrossUp, wtCrossDown):
        hwt1, hwt2, hwtOversold, hwtOverbought, hwtCross, hwtCrossUp, hwtCrossDown, hwtCrosslast, hwtCrossUplast, hwtCrossDownlast, hwtVwap = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen, tf)
        bearPattern = rsimfi < soomiRSIMFIBearLevel and wt2 > soomiFlagWTBearLevel and wtCross and wtCrossDown and (hwtVwap < sommiVwapBearLevel)
        bullPattern = rsimfi > soomiRSIMFIBullLevel and wt2 < soomiFlagWTBullLevel and wtCross and wtCrossUp and (hwtVwap > sommiVwapBullLevel)
        return (bearPattern, bullPattern, hwtVwap)

    def f_findSommiDiamond(tf, tf2, wt1, wt2, wtCross, wtCrossUp, wtCrossDown):
        candleBodyDir, newBar = f_getTFCandle(tf)
        candleBodyDir2, newBar2 = f_getTFCandle(tf2)
        bearPattern = wt2 >= soomiDiamondWTBearLevel and wtCross and wtCrossDown and (not candleBodyDir) and (not candleBodyDir2)
        bullPattern = wt2 <= soomiDiamondWTBullLevel and wtCross and wtCrossUp and candleBodyDir and candleBodyDir2
        return (bearPattern, bullPattern)

    rsi: Series = ta.rsi(rsiSRC, rsiLen)
    rsiColor = rsioscolor if rsi <= rsiOversold else rsiobcolor if rsi >= rsiOverbought else rsinacolor
    rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    rsiMFIColor = rsiMFIColorAbove if rsiMFI > 0 else rsiMFIColorBelow
    wt2: Series
    wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCross_last, wtCrossUp_last, wtCrossDown_last, wtVwap = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen, timeframe.period)
    stochK: Series
    stochK, stochD = f_stochrsi(stochSRC, stochLen, stochRsiLen, stochKSmooth, stochDSmooth, stochUseLog, stochAvg)
    tcVal = f_tc(tcSRC, tclength, tcfastLength, tcslowLength)
    sommiBearish, sommiBullish, hvwap = f_findSommiFlag(sommiVwapTF, wt1, wt2, rsiMFI, wtCross, wtCrossUp, wtCrossDown)
    sommiBearishDiamond, sommiBullishDiamond = f_findSommiDiamond(sommiHTCRes, sommiHTCRes2, wt1, wt2, wtCross, wtCrossUp, wtCrossDown)
    macdWT1Color, macdWT2Color = f_macdWTColors(macdWTColorsTF)
    wtFractalTop, wtFractalBot, wtLow_prev, wtBearDiv, wtBullDiv, wtBearDivHidden, wtBullDivHidden = f_findDivs(wt2, wtDivOBLevel, wtDivOSLevel, True)
    wtFractalTop_add, wtFractalBot_add, wtLow_prev_add, wtBearDiv_add, wtBullDiv_add, wtBearDivHidden_add, wtBullDivHidden_add = f_findDivs(wt2, wtDivOBLevel_add, wtDivOSLevel_add, True)
    wtFractalTop_nl, wtFractalBot_nl, wtLow_prev_nl, wtBearDiv_nl, wtBullDiv_nl, wtBearDivHidden_nl, wtBullDivHidden_nl = f_findDivs(wt2, 0, 0, False)
    wtBearDivHidden_ = wtBearDivHidden_nl if showHiddenDiv_nl else wtBearDivHidden
    wtBullDivHidden_ = wtBullDivHidden_nl if showHiddenDiv_nl else wtBullDivHidden
    wtBearDivColor = WTBearDivColorDown if wtShowDiv and wtBearDiv or (wtShowHiddenDiv and wtBearDivHidden_) else na
    wtBullDivColor = wtBullDivColorUp if wtShowDiv and wtBullDiv or (wtShowHiddenDiv and wtBullDivHidden_) else na
    wtBearDivColor_add = WTBearDivColorDown if wtShowDiv and wtDivOBLevel_addshow and wtBearDiv_add or (wtShowHiddenDiv and wtDivOBLevel_addshow and wtBearDivHidden_add) else na
    wtBullDivColor_add = wtBullDivColorUp if wtShowDiv and wtDivOBLevel_addshow and wtBullDiv_add or (wtShowHiddenDiv and wtDivOBLevel_addshow and wtBullDivHidden_add) else na
    rsiFractalTop, rsiFractalBot, rsiLow_prev, rsiBearDiv, rsiBullDiv, rsiBearDivHidden, rsiBullDivHidden = f_findDivs(rsi, rsiDivOBLevel, rsiDivOSLevel, True)
    rsiFractalTop_nl, rsiFractalBot_nl, rsiLow_prev_nl, rsiBearDiv_nl, rsiBullDiv_nl, rsiBearDivHidden_nl, rsiBullDivHidden_nl = f_findDivs(rsi, 0, 0, False)
    rsiBearDivHidden_ = rsiBearDivHidden_nl if showHiddenDiv_nl else rsiBearDivHidden
    rsiBullDivHidden_ = rsiBullDivHidden_nl if showHiddenDiv_nl else rsiBullDivHidden
    rsiBearColor = color.new(color.new('#E60000'), 0)
    rsiBullColor = color.new(color.new('#38FF42'), 0)
    rsiBearDivColor = rsiBearColor if rsiShowDiv and rsiBearDiv or (rsiShowHiddenDiv and rsiBearDivHidden_) else na
    rsiBullDivColor = rsiBullColor if rsiShowDiv and rsiBullDiv or (rsiShowHiddenDiv and rsiBullDivHidden_) else na
    stochFractalTop, stochFractalBot, stochLow_prev, stochBearDiv, stochBullDiv, stochBearDivHidden, stochBullDivHidden = f_findDivs(stochK, 0, 0, False)
    stochbearcolor = color.new(color.new('#E60000'), 0)
    stochbullcolor = color.new(color.new('#38FF42'), 0)
    stochBearDivColor = stochbearcolor if stochShowDiv and stochBearDiv or (stochShowHiddenDiv and stochBearDivHidden) else na
    stochBullDivColor = stochbullcolor if stochShowDiv and stochBullDiv or (stochShowHiddenDiv and stochBullDivHidden) else na
    signalColor = signalcolordown if wt2 - wt1 > 0 else signalcolorup
    buySignal = wtCross and wtCrossUp and wtOversold
    buySignalDiv = wtShowDiv and wtBullDiv or (wtShowDiv and wtBullDiv_add) or (stochShowDiv and stochBullDiv) or (rsiShowDiv and rsiBullDiv)
    buySignalDiv_color = colorGreen if wtBullDiv else color.new(colorGreen, 60) if wtBullDiv_add else colorGreen if rsiShowDiv else na
    sellSignal = wtCross and wtCrossDown and wtOverbought
    sellSignalDiv = wtShowDiv and wtBearDiv or (wtShowDiv and wtBearDiv_add) or (stochShowDiv and stochBearDiv) or (rsiShowDiv and rsiBearDiv)
    sellSignalDiv_color = colorRed if wtBearDiv else color.new(colorRed, 60) if wtBearDiv_add else colorRed if rsiBearDiv else na
    lastRsi = inline_series(ta.valuewhen(wtFractalBot, rsi[2], 0), 2)
    wtGoldBuy = (wtShowDiv and wtBullDiv or (rsiShowDiv and rsiBullDiv)) and wtLow_prev <= osLevel3 and (wt2 > osLevel3) and (wtLow_prev - wt2 <= -5) and (lastRsi < 30)
    bgcolor(color.new(color.new('#000000'), 0) if darkMode else na)
    zLine = plot(0, color=color.new(colorWhite, 50))
    rsiMfiBarTopLine = plot(-95 if rsiMFIShow else na, title='MFI Bar TOP Line')
    rsiMfiBarBottomLine = plot(-99 if rsiMFIShow else na, title='MFI Bar BOTTOM Line')
    fill(rsiMfiBarTopLine, rsiMfiBarBottomLine, title='MFI Bar Colors', color=color.new(rsiMFIColor, 75))
    plot(wt1 if wtShow else na, style=plot.style_area, title='WT Wave 1', color=color.new(colorWT1blue, 30))
    plot(wt2 if wtShow else na, style=plot.style_area, title='WT Wave 2', color=color.new(colorWT2purple, 25))
    plot(wtVwap if vwapShow else na, title='VWAP', color=VWAPColor, style=plot.style_area, linewidth=2)
    plot(rsiMFI if rsiMFIShow else na, style=plot.style_area, title='rsiMFI', color=color.new(rsiMFIColor, 50))
    plot(series=wt2[2] if wtFractalTop else na, title='WT Bearish Divergence', color=wtBearDivColor, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalBot else na, title='WT Bullish Divergence', color=wtBullDivColor, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalTop_add else na, title='WT 2nd Bearish Divergence', color=wtBearDivColor_add, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalBot_add else na, title='WT 2nd Bullish Divergence', color=wtBullDivColor_add, linewidth=2, offset=-2)
    plot(rsi if rsiShow else na, title='RSI', color=rsiColor, linewidth=2)
    plot(series=rsi[2] if rsiFractalTop else na, title='RSI Bearish Divergence', color=rsiBearDivColor, linewidth=1, offset=-2)
    plot(series=rsi[2] if rsiFractalBot else na, title='RSI Bullish Divergence', color=rsiBullDivColor, linewidth=1, offset=-2)
    stochKplot = plot(stochK if stochShow else na, title='Stoch K', color=stochkcolor, linewidth=2)
    stochDplot = plot(stochD if stochShow else na, title='Stoch D', color=stochdcolor, linewidth=1)
    stochFillColor = color.new(color.new('#21BAF3'), 95) if stochK >= stochD else color.new(color.new('#673AB7'), 90)
    fill(stochKplot, stochDplot, title='KD Fill', color=stochFillColor)
    plot(series=stochK[2] if stochFractalTop else na, title='Stoch Bearish Divergence', color=stochBearDivColor, linewidth=1, offset=-2)
    plot(series=stochK[2] if stochFractalBot else na, title='Stoch Bullish Divergence', color=stochBullDivColor, linewidth=1, offset=-2)
    plot(tcVal if tcLine else na, color=color.new(color.new('#673AB7'), 25), linewidth=2, title='Schaff Trend Cycle 1')
    plot(tcVal if tcLine else na, color=color.new(colorWhite, 50), linewidth=1, title='Schaff Trend Cycle 2')
    oblvl2color = color.new(color.new('#FFFFFF'), 0)
    oblvl3color = color.new(color.new('#FFFFFF'), 0)
    oslvl2color = color.new(color.new('#FFFFFF'), 0)
    plot(obLevel2, title='Over Bought Level 2', color=oblvl2color, linewidth=1, style=plot.style_stepline)
    plot(obLevel3, title='Over Bought Level 3', color=oblvl3color, linewidth=1, style=plot.style_circles)
    plot(osLevel2, title='Over Sold Level 2', color=oslvl2color, linewidth=1, style=plot.style_stepline)
    plotchar(108 if sommiFlagShow and sommiBearish else na, title='Sommi bearish flag', char='⚑', color=color.new(colorPink, 0), location=location.absolute, size=size.tiny)
    plotchar(-108 if sommiFlagShow and sommiBullish else na, title='Sommi bullish flag', char='⚑', color=color.new(colorBluelight, 0), location=location.absolute, size=size.tiny)
    plot(ta.ema(hvwap, 3) if sommiShowVwap else na, title='Sommi higher VWAP', color=color.new(colorYellow, 55), linewidth=2, style=plot.style_line)
    plotchar(108 if sommiDiamondShow and sommiBearishDiamond else na, title='Sommi bearish diamond', char='◆', color=color.new(colorPink, 0), location=location.absolute, size=size.tiny)
    plotchar(-108 if sommiDiamondShow and sommiBullishDiamond else na, title='Sommi bullish diamond', char='◆', color=color.new(colorBluelight, 0), location=location.absolute, size=size.tiny)
    plot(wt2 if wtCross else na, title='Buy and sell circle', color=signalColor, style=plot.style_circles, linewidth=3)
    plotchar(-107 if wtBuyShow and buySignal else na, title='Buy circle', char='·', color=color.new(colorGreen, 50), location=location.absolute, size=size.small)
    plotchar(105 if wtSellShow and sellSignal else na, title='Sell circle', char='·', color=color.new(colorRed, 50), location=location.absolute, size=size.small)
    plotchar(-106 if wtDivShow and buySignalDiv else na, title='Divergence buy circle', char='•', color=buySignalDiv_color, location=location.absolute, size=size.small, offset=-2)
    plotchar(106 if wtDivShow and sellSignalDiv else na, title='Divergence sell circle', char='•', color=sellSignalDiv_color, location=location.absolute, size=size.small, offset=-2)
    plotchar(-106 if wtGoldBuy and wtGoldShow else na, title='Gold  buy gold circle', char='•', color=color.new(colorOrange, 15), location=location.absolute, size=size.normal, offset=-2)
    alertcondition(buySignal, 'Buy (Big green circle)', 'Green circle WaveTrend Oversold')
    alertcondition(buySignalDiv, 'Buy (Big green circle + Div)', 'Buy & WT Bullish Divergence & WT Overbought')
    alertcondition(wtGoldBuy, 'GOLD Buy (Big GOLDEN circle)', 'Green & GOLD circle WaveTrend Overbought')
    alertcondition(sommiBullish or sommiBullishDiamond, 'Sommi bullish flag/diamond', 'Blue flag/diamond')
    alertcondition(wtCross and wtCrossUp, 'Buy (Small green dot)', 'Buy small circle')
    alertcondition(sommiBearish or sommiBearishDiamond, 'Sommi bearish flag/diamond', 'Purple flag/diamond')
    alertcondition(sellSignal, 'Sell (Big red circle)', 'Red Circle WaveTrend Overbought')
    alertcondition(sellSignalDiv, 'Sell (Big red circle + Div)', 'Buy & WT Bearish Divergence & WT Overbought')
    alertcondition(wtCross and wtCrossDown, 'Sell (Small red dot)', 'Sell small circle')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
