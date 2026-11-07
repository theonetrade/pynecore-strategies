"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barmerge, bgcolor, close, color, fill, high, hlc3, hline,
    input, location, low, math, na, nz, open, plot, plotchar, request, script, size, strategy,
    syminfo, ta, ticker, timeframe, volume
)
from pynecore.types import Color, Series


@script.strategy(title='VMC', shorttitle='VMC', overlay=True, precision=3, commission_value=0.025, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    wtShow=input(True, title='Show WaveTrend'),
    wtBuyShow=input(True, title='Show Buy dots'),
    wtGoldShow=input(True, title='Show Gold dots'),
    wtSellShow=input(True, title='Show Sell dots'),
    wtDivShow=input(True, title='Show Div. dots'),
    vwapShow=input(True, title='Show Fast WT'),
    wtChannelLen=input(9, title='WT Channel Length'),
    wtAverageLen=input(12, title='WT Average Length'),
    wtMASource: Series[float] = input(hlc3, title='WT MA Source'),
    wtMALen=input(3, title='WT MA Length'),
    obLevel=input(53, title='WT Overbought Level 1'),
    obLevel2=input(60, title='WT Overbought Level 2'),
    obLevel3=input(100, title='WT Overbought Level 3'),
    osLevel=input(-53, title='WT Oversold Level 1'),
    osLevel2=input(-60, title='WT Oversold Level 2'),
    osLevel3=input(-75, title='WT Oversold Level 3'),
    wtShowDiv=input(True, title='Show WT Regular Divergences'),
    wtShowHiddenDiv=input(False, title='Show WT Hidden Divergences'),
    showHiddenDiv_nl=input(True, title='Not apply OB/OS Limits on Hidden Divergences'),
    wtDivOBLevel=input(45, title='WT Bearish Divergence min'),
    wtDivOSLevel=input(-65, title='WT Bullish Divergence min'),
    wtDivOBLevel_addshow=input(True, title='Show 2nd WT Regular Divergences'),
    wtDivOBLevel_add=input(15, title='WT 2nd Bearish Divergence'),
    wtDivOSLevel_add=input(-40, title='WT 2nd Bullish Divergence 15 min'),
    rsiMFIShow=input(True, title='Show MFI'),
    rsiMFIperiod=input(60, title='MFI Period'),
    rsiMFIMultiplier=input.float(150, title='MFI Area multiplier'),
    rsiMFIPosY=input(2.5, title='MFI Area Y Pos'),
    rsiShow=input(False, title='Show RSI'),
    rsiSRC: Series[float] = input(close, title='RSI Source'),
    rsiLen=input(14, title='RSI Length'),
    rsiOversold=input.int(30, title='RSI Oversold', minval=50, maxval=100),
    rsiOverbought=input.int(60, title='RSI Overbought', minval=0, maxval=50),
    rsiShowDiv=input(False, title='Show RSI Regular Divergences'),
    rsiShowHiddenDiv=input(False, title='Show RSI Hidden Divergences'),
    rsiDivOBLevel=input(60, title='RSI Bearish Divergence min'),
    rsiDivOSLevel=input(30, title='RSI Bullish Divergence min'),
    stochShow=input(True, title='Show Stochastic RSI'),
    stochUseLog=input(True, title=' Use Log?'),
    stochAvg=input(False, title='Use Average of both K & D'),
    stochSRC: Series[float] = input(close, title='Stochastic RSI Source'),
    stochLen=input(14, title='Stochastic RSI Length'),
    stochRsiLen=input(14, title='RSI Length '),
    stochKSmooth=input(3, title='Stochastic RSI K Smooth'),
    stochDSmooth=input(3, title='Stochastic RSI D Smooth'),
    stochShowDiv=input(False, title='Show Stoch Regular Divergences'),
    stochShowHiddenDiv=input(False, title='Show Stoch Hidden Divergences'),
    tcLine=input(False, title='Show Schaff TC line'),
    tcSRC: Series[float] = input(close, title='Schaff TC Source'),
    tclength=input(10, title='Schaff TC'),
    tcfastLength=input(23, title='Schaff TC Fast Lenght'),
    tcslowLength=input(50, title='Schaff TC Slow Length'),
    tcfactor=input(0.5, title='Schaff TC Factor'),
    sommiFlagShow=input(False, title='Show Sommi flag'),
    sommiShowVwap=input(False, title='Show Sommi F. Wave'),
    sommiVwapTF=input('720', title='Sommi F. Wave timeframe'),
    sommiVwapBearLevel=input(0, title='F. Wave Bear Level (less than)'),
    sommiVwapBullLevel=input(0, title='F. Wave Bull Level (more than)'),
    soomiFlagWTBearLevel=input(0, title='WT Bear Level (more than)'),
    soomiFlagWTBullLevel=input(0, title='WT Bull Level (less than)'),
    soomiRSIMFIBearLevel=input(0, title='Money flow Bear Level (less than)'),
    soomiRSIMFIBullLevel=input(0, title='Money flow Bull Level (more than)'),
    sommiDiamondShow=input(False, title='Show Sommi diamond'),
    sommiHTCRes=input('60', title='HTF Candle Res. 1'),
    sommiHTCRes2=input('240', title='HTF Candle Res. 2'),
    soomiDiamondWTBearLevel=input(0, title='WT Bear Level (More than)'),
    soomiDiamondWTBullLevel=input(0, title='WT Bull Level (Less than)'),
    macdWTColorsShow=input(False, title='Show MACD Colors'),
    macdWTColorsTF=input('240', title='MACD Colors MACD TF'),
    darkMode=input(False, title='Dark mode'),
    len=input(14),
    th=input(20),
    rsi1LengthInput=input.int(100, minval=1, title='RSI Length', group='RSI Settings'),
    rsi1SourceInput: Series[float] = input.source(close, 'Source', group='RSI Settings'),
    rsi2LengthInput=input.int(25, minval=1, title='RSI Length', group='RSI Settings'),
    rsi2SourceInput: Series[float] = input.source(close, 'Source', group='RSI Settings'),
    length=input.int(10, minval=1),
    DER_avg=input.int(5, 'Average', minval=1, inline='DER', group='Directional Energy Ratio'),
    smooth=input.int(3, 'Smoothing', minval=1, inline='DER', group='Directional Energy Ratio'),
    v_calc=input.string('Relative', 'Calculation', options=('Relative', 'Full', 'None'), group='Volume Parameters'),
    vlookbk=input.int(20, 'Lookback (for Relative)', minval=1, group='Volume Parameters')
):
    colorRed: Color = color.new('#FF0000')
    colorPurple: Color = color.new('#E600E6')
    colorGreen: Color = color.new('#3FFF00')
    colorOrange: Color = color.new('#E2A400')
    colorYellow: Color = color.new('#FFE500')
    colorWhite: Color = color.new('#FFFFFF')
    colorPink: Color = color.new('#FF00F0')
    colorBluelight: Color = color.new('#31C0FF')
    colorWT1: Color = color.new('#90CAF9')
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
    rsiColor = colorGreen if rsi <= rsiOversold else colorRed if rsi >= rsiOverbought else colorPurple
    rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    rsiMFIColor = color.new('#3EE145') if rsiMFI > 0 else color.new('#FF3D2E')
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
    wtBearDivColor = colorRed if wtShowDiv and wtBearDiv or (wtShowHiddenDiv and wtBearDivHidden_) else na
    wtBullDivColor = colorGreen if wtShowDiv and wtBullDiv or (wtShowHiddenDiv and wtBullDivHidden_) else na
    wtBearDivColor_add = color.new('#9A0202') if wtShowDiv and wtDivOBLevel_addshow and wtBearDiv_add or (wtShowHiddenDiv and wtDivOBLevel_addshow and wtBearDivHidden_add) else na
    wtBullDivColor_add = color.new('#1B5E20') if wtShowDiv and wtDivOBLevel_addshow and wtBullDiv_add or (wtShowHiddenDiv and wtDivOBLevel_addshow and wtBullDivHidden_add) else na
    rsiFractalTop, rsiFractalBot, rsiLow_prev, rsiBearDiv, rsiBullDiv, rsiBearDivHidden, rsiBullDivHidden = f_findDivs(rsi, rsiDivOBLevel, rsiDivOSLevel, True)
    rsiFractalTop_nl, rsiFractalBot_nl, rsiLow_prev_nl, rsiBearDiv_nl, rsiBullDiv_nl, rsiBearDivHidden_nl, rsiBullDivHidden_nl = f_findDivs(rsi, 0, 0, False)
    rsiBearDivHidden_ = rsiBearDivHidden_nl if showHiddenDiv_nl else rsiBearDivHidden
    rsiBullDivHidden_ = rsiBullDivHidden_nl if showHiddenDiv_nl else rsiBullDivHidden
    rsiBearDivColor = colorRed if rsiShowDiv and rsiBearDiv or (rsiShowHiddenDiv and rsiBearDivHidden_) else na
    rsiBullDivColor = colorGreen if rsiShowDiv and rsiBullDiv or (rsiShowHiddenDiv and rsiBullDivHidden_) else na
    stochFractalTop, stochFractalBot, stochLow_prev, stochBearDiv, stochBullDiv, stochBearDivHidden, stochBullDivHidden = f_findDivs(stochK, 0, 0, False)
    stochBearDivColor = colorRed if stochShowDiv and stochBearDiv or (stochShowHiddenDiv and stochBearDivHidden) else na
    stochBullDivColor = colorGreen if stochShowDiv and stochBullDiv or (stochShowHiddenDiv and stochBullDivHidden) else na
    signalColor = color.red if wt2 - wt1 > 0 else color.lime
    buySignal = wtCross and wtCrossUp and wtOversold
    buySignalDiv = wtShowDiv and wtBullDiv or (wtShowDiv and wtBullDiv_add) or (stochShowDiv and stochBullDiv) or (rsiShowDiv and rsiBullDiv)
    buySignalDiv_color = colorGreen if wtBullDiv else color.new(colorGreen, 60) if wtBullDiv_add else colorGreen if rsiShowDiv else na
    sellSignal = wtCross and wtCrossDown and wtOverbought
    sellSignalDiv = wtShowDiv and wtBearDiv or (wtShowDiv and wtBearDiv_add) or (stochShowDiv and stochBearDiv) or (rsiShowDiv and rsiBearDiv)
    sellSignalDiv_color = colorRed if wtBearDiv else color.new(colorRed, 60) if wtBearDiv_add else colorRed if rsiBearDiv else na
    lastRsi = inline_series(ta.valuewhen(wtFractalBot, rsi[2], 0), 2)
    wtGoldBuy = (wtShowDiv and wtBullDiv or (rsiShowDiv and rsiBullDiv)) and wtLow_prev <= osLevel3 and (wt2 > osLevel3) and (wtLow_prev - wt2 <= -5) and (lastRsi < 30)
    bgcolor(color.new(color.new('#000000'), 80) if darkMode else na)
    zLine = plot(0, color=color.new(colorWhite, 50))
    rsiMfiBarTopLine = plot(-95 if rsiMFIShow else na, title='MFI Bar TOP Line')
    rsiMfiBarBottomLine = plot(-99 if rsiMFIShow else na, title='MFI Bar BOTTOM Line')
    fill(rsiMfiBarTopLine, rsiMfiBarBottomLine, title='MFI Bar Colors', color=color.new(rsiMFIColor, 75))
    plot(wt1 if wtShow else na, style=plot.style_area, title='WT Wave 1', color=macdWT1Color if macdWTColorsShow else colorWT1)
    plot(wt2 if wtShow else na, style=plot.style_area, title='WT Wave 2', color=macdWT2Color if macdWTColorsShow else colorWT2_ if darkMode else colorWT2)
    plot(wtVwap if vwapShow else na, title='VWAP', color=color.new(colorYellow, 45), style=plot.style_area, linewidth=2)
    rsiMFIplot = plot(rsiMFI if rsiMFIShow else na, title='RSI+MFI Area', color=rsiMFIColor)
    fill(rsiMFIplot, zLine, color.new(rsiMFIColor, 40))
    plot(series=wt2[2] if wtFractalTop else na, title='WT Bearish Divergence', color=wtBearDivColor, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalBot else na, title='WT Bullish Divergence', color=wtBullDivColor, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalTop_add else na, title='WT 2nd Bearish Divergence', color=wtBearDivColor_add, linewidth=2, offset=-2)
    plot(series=wt2[2] if wtFractalBot_add else na, title='WT 2nd Bullish Divergence', color=wtBullDivColor_add, linewidth=2, offset=-2)
    plot(rsi if rsiShow else na, title='RSI', color=rsiColor, linewidth=2)
    plot(series=rsi[2] if rsiFractalTop else na, title='RSI Bearish Divergence', color=rsiBearDivColor, linewidth=1, offset=-2)
    plot(series=rsi[2] if rsiFractalBot else na, title='RSI Bullish Divergence', color=rsiBullDivColor, linewidth=1, offset=-2)
    stochKplot = plot(stochK if stochShow else na, title='Stoch K', color=color.new(color.new('#21BAF3'), 0), linewidth=2)
    stochDplot = plot(stochD if stochShow else na, title='Stoch D', color=color.new(color.new('#673AB7'), 60), linewidth=1)
    stochFillColor = color.new(color.new('#21BAF3'), 75) if stochK >= stochD else color.new(color.new('#673AB7'), 60)
    fill(stochKplot, stochDplot, title='KD Fill', color=stochFillColor)
    plot(series=stochK[2] if stochFractalTop else na, title='Stoch Bearish Divergence', color=stochBearDivColor, linewidth=1, offset=-2)
    plot(series=stochK[2] if stochFractalBot else na, title='Stoch Bullish Divergence', color=stochBullDivColor, linewidth=1, offset=-2)
    plot(tcVal if tcLine else na, color=color.new(color.new('#673AB7'), 25), linewidth=2, title='Schaff Trend Cycle 1')
    plot(tcVal if tcLine else na, color=color.new(colorWhite, 50), linewidth=1, title='Schaff Trend Cycle 2')
    plot(obLevel2, title='Over Bought Level 2', color=color.new(colorWhite, 85), linewidth=1, style=plot.style_stepline)
    plot(obLevel3, title='Over Bought Level 3', color=color.new(colorWhite, 95), linewidth=1, style=plot.style_circles)
    plot(osLevel2, title='Over Sold Level 2', color=color.new(colorWhite, 85), linewidth=1, style=plot.style_stepline)
    plotchar(108 if sommiFlagShow and sommiBearish else na, title='Sommi bearish flag', char='⚑', color=color.new(colorPink, 0), location=location.absolute, size=size.tiny)
    plotchar(-108 if sommiFlagShow and sommiBullish else na, title='Sommi bullish flag', char='⚑', color=color.new(colorBluelight, 0), location=location.absolute, size=size.tiny)
    plot(ta.ema(hvwap, 3) if sommiShowVwap else na, title='Sommi higher VWAP', color=color.new(colorYellow, 15), linewidth=2, style=plot.style_line)
    plotchar(108 if sommiDiamondShow and sommiBearishDiamond else na, title='Sommi bearish diamond', char='◆', color=color.new(colorPink, 0), location=location.absolute, size=size.tiny)
    plotchar(-108 if sommiDiamondShow and sommiBullishDiamond else na, title='Sommi bullish diamond', char='◆', color=color.new(colorBluelight, 0), location=location.absolute, size=size.tiny)
    plot(wt2 if wtCross else na, title='Buy and sell circle', color=signalColor, style=plot.style_circles, linewidth=3)
    plotchar(-107 if wtBuyShow and buySignal else na, title='Buy circle', char='·', color=color.new(colorGreen, 50), location=location.absolute, size=size.small)
    plotchar(105 if wtSellShow and sellSignal else na, title='Sell circle', char='·', color=color.new(colorRed, 50), location=location.absolute, size=size.small)
    plotchar(-106 if wtDivShow and buySignalDiv else na, title='Divergence buy circle', char='•', color=buySignalDiv_color, location=location.absolute, size=size.small, offset=-2)
    plotchar(106 if wtDivShow and sellSignalDiv else na, title='Divergence sell circle', char='•', color=sellSignalDiv_color, location=location.absolute, size=size.small, offset=-2)
    plotchar(-106 if wtGoldBuy and wtGoldShow else na, title='Gold  buy gold circle', char='•', color=color.new(colorOrange, 15), location=location.absolute, size=size.small, offset=-2)
    TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
    DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
    DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
    SmoothedTrueRange: Series[float] = 0.0
    SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / len + TrueRange
    SmoothedDirectionalMovementPlus: Series[float] = 0.0
    SmoothedDirectionalMovementPlus = nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / len + DirectionalMovementPlus
    SmoothedDirectionalMovementMinus: Series[float] = 0.0
    SmoothedDirectionalMovementMinus = nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / len + DirectionalMovementMinus
    DIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100
    DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
    DX = math.abs(DIPlus - DIMinus) / (DIPlus + DIMinus) * 100
    ADX = ta.sma(DX, len)
    plot(ADX, color=color.new(color.white, 0), title='ADX')
    def f_RelVol(_value, _length):
        min_value = ta.lowest(_value, _length)
        max_value = ta.highest(_value, _length)
        return ta.stoch(_value, max_value, min_value, _length) / 100

    price = close
    uprsi1 = ta.rma(math.max(ta.change(rsi1SourceInput), 0), rsi1LengthInput)
    uprsi2 = ta.rma(math.max(ta.change(rsi2SourceInput), 0), rsi2LengthInput)
    downrsi1 = ta.rma(-math.min(ta.change(rsi1SourceInput), 0), rsi1LengthInput)
    downrsi2 = ta.rma(-math.min(ta.change(rsi2SourceInput), 0), rsi2LengthInput)
    rsi1 = 100 if downrsi1 == 0 else 0 if uprsi1 == 0 else 100 - 100 / (1 + uprsi1 / downrsi1)
    rsi2 = 100 if downrsi2 == 0 else 0 if uprsi2 == 0 else 100 - 100 / (1 + uprsi2 / downrsi2)
    vola = 1 if v_calc == 'None' or na(volume) else f_RelVol(volume, vlookbk) if v_calc == 'Relative' else volume
    R = (ta.highest(1) - ta.lowest(1)) / 2
    sr = ta.change(price) / R
    rsr = math.max(math.min(sr, 1), -1)
    c = rsr * vola
    c_plus = math.max(c, 0)
    c_minus = -math.min(c, 0)
    dem = ta.wma(c_plus, length) / ta.wma(vola, length)
    sup = ta.wma(c_minus, length) / ta.wma(vola, length)
    adp = 1 * ta.wma(dem, DER_avg)
    asp = 1 * ta.wma(sup, DER_avg)
    anp = adp - asp
    anp_s = ta.wma(anp, smooth)
    rsi1UpperBand = hline(70, 'RSI Upper Band', color=color.new('#787B86'))
    rsi1LowerBand = hline(30, 'RSI Lower Band', color=color.new('#787B86'))
    rsi2UpperBand = hline(70, 'RSI Upper Band', color=color.new('#787B86'))
    rsi2LowerBand = hline(30, 'RSI Lower Band', color=color.new('#787B86'))
    c_adp = color.new(color.aqua, 50)
    c_asp = color.new(color.orange, 50)
    c_zero = color.new(color.yellow, 70)
    c_fd = color.new(color.green, 80)
    c_fs = color.new(color.red, 80)
    c_up = color.new(color.new('#33FF00'), 0)
    c_dn = color.new(color.new('#FF1111'), 0)
    up = anp_s >= 0
    closeStatus = 'win' if strategy.openprofit > 0 else 'lose'
    long_entry = wt2 < wt1
    long_exit_entry = signalColor == color.red or sellSignal or sellSignalDiv
    short_entry = wt2 > wt1
    short_exit_entry = signalColor == color.lime or buySignal or buySignalDiv
    alertcondition(long_entry, 'Buy', 'Long entry')
    alertcondition(long_exit_entry, 'Buy', 'Long exit')
    alertcondition(short_entry, 'Sell', 'Short entry')
    alertcondition(short_exit_entry, 'Sell', 'Short exit')
    if long_entry:
        strategy.entry('long', strategy.long)
    if long_exit_entry:
        strategy.close('long', comment=closeStatus)
    if short_entry:
        strategy.entry('short', strategy.short)
    if short_exit_entry:
        strategy.close('short', comment=closeStatus)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
