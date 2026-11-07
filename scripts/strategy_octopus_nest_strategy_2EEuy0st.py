"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barcolor, barmerge, close, color, high, input, location, low,
    math, na, nz, plot, plotshape, request, script, shape, size, strategy, syminfo, ta
)
from pynecore.types import Color, Persistent, Series


@script.strategy('Octopus Nest Strategy', shorttitle='Octo', overlay=True, initial_capital=1000, default_qty_value=25, default_qty_type=strategy.percent_of_equity, calc_on_every_tick=False, process_orders_on_close=True, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    resolution=input.timeframe(defval='', title='Choose Timeframe', group='General', inline='1'),
    src: Series[float] = input.source(close, 'Choose Source', group='General', inline='1'),
    isSignalLabelEnabled=input.bool(title='Show Signal Labels?', defval=True, group='General', inline='2'),
    isPsarAdaptive=input.bool(title='Is PSAR Adaptive?', defval=False, group='General', inline='2'),
    isRepaintingEnabled=input.bool(title='Is Repainting Enabled?', defval=False, group='General', inline='3', tooltip='If repainting is enabled, the strategy uses the current bar to determine the signal. Otherwise, it uses the previous bar.'),
    highLowStopLossMultiplier=input.float(defval=0.98, step=0.01, minval=0, maxval=1, title='Multiplier', group='High Low Stop Loss', inline='1'),
    highLowStopLossBackupMultiplier=input.float(defval=0.98, step=0.01, minval=0, maxval=1, title='Backup Multiplier', group='High Low Stop Loss', inline='1'),
    highLowStopLossLookback=input.int(defval=20, step=5, minval=1, title='Lookback', group='High Low Stop Loss', inline='2'),
    automaticHighLowTakeProfitRatio=input.float(defval=1.125, step=0.1, minval=0, title='Risk Reward Ratio', group='Automatic High Low Take Profit', inline='2'),
    emaLength=input.int(100, minval=2, title='Length', group='EMA', inline='1'),
    bbLength=input(20, title='BB Length', group='TTM Squeeze/Squeeze Momentum', inline='3'),
    multBB=input(2.0, title='BB MultFactor', group='TTM Squeeze/Squeeze Momentum', inline='3'),
    lengthKC=input(20, title='KC Length', group='TTM Squeeze/Squeeze Momentum', inline='4'),
    multKC=input(1.5, title='KC MultFactor', group='TTM Squeeze/Squeeze Momentum', inline='4'),
    isTrueRangeEnabled=input.bool(title='Use True Range?', defval=True, group='TTM Squeeze/Squeeze Momentum', inline='5'),
    psarStart=input.float(0.02, 'Start', step=0.01, minval=0.0, group='PSAR', inline='1'),
    psarInc=input.float(0.02, 'Increment', step=0.01, minval=0.01, group='PSAR', inline='1'),
    psarMax=input.float(0.2, 'Max', step=0.05, minval=0.0, group='PSAR', inline='2'),
    startAFactor=input.float(0.02, 'Starting Acceleration Factor', step=0.001, group='Adaptive PSAR', inline='1'),
    minStep=input.float(0.0, 'Min Step', step=0.001, group='Adaptive PSAR', inline='1'),
    maxStep=input.float(0.02, 'Max Step', step=0.001, group='Adaptive PSAR', inline='2'),
    maxAFactor=input.float(0.2, 'Max Acceleration Factor', step=0.001, group='Adaptive PSAR', inline='2'),
    hiloMode=input.string('On', 'HiLo Mode', options=('Off', 'On'), group='Adaptive PSAR'),
    adaptMode=input.string('Kaufman', 'Adaptive Mode', options=('Kaufman', 'Ehlers'), group='Adaptive PSAR'),
    adaptSmth=input.int(5, 'Adaptive Smoothing Period', minval=1, group='Adaptive PSAR'),
    filt=input.float(0.0, 'Filter in Pips', group='Adaptive PSAR', minval=0),
    minChng=input.float(0.0, 'Min Change in Pips', group='Adaptive PSAR', minval=0),
    SignalMode=input.string('Only Stops', 'Signal Mode', options=('Only Stops', 'Signals & Stops'), group='Adaptive PSAR')
):
    rajah: Color = color.rgb(242, 166, 84)
    magicMint: Color = color.rgb(171, 237, 198)
    mediumAquamarine: Color = color.rgb(104, 223, 153)
    carrotOrange: Color = color.rgb(239, 146, 46)
    def tr(_high, _low, _close: Series):
        return math.max(_high - _low, math.abs(_high - _close[1]), math.abs(_low - _close[1]))

    lastTrade: Persistent[str] = 'initial'
    repaint: int = 0 if isRepaintingEnabled else 1
    _low: Series
    _high: Series
    _src, _low, _high, _close = request.security(syminfo.tickerid, resolution, (src[repaint], low[repaint], high[repaint], close[repaint]), barmerge.gaps_off, barmerge.lookahead_off if isRepaintingEnabled else barmerge.lookahead_on)
    osc: Series[float] = ta.linreg(_src - math.avg(math.avg(ta.highest(_high, lengthKC), ta.lowest(_low, lengthKC)), ta.sma(_close, lengthKC)), lengthKC, 0)
    _upperBB: Series
    _lowerBB: Series
    _, _upperBB, _lowerBB = ta.bb(_src, bbLength, multBB)
    _upperKC: Series
    _lowerKC: Series
    _, _upperKC, _lowerKC = ta.kc(_src, lengthKC, multKC, isTrueRangeEnabled)
    upperBB: float = _upperBB[repaint]
    lowerBB: float = _lowerBB[repaint]
    upperKC: float = _upperKC[repaint]
    lowerKC: float = _lowerKC[repaint]
    osc_color = (color.new('#00FFFF') if osc >= 0 else color.new('#CC00CC')) if osc[1] < osc else color.new('#009B9B') if osc >= 0 else color.new('#FF9BFF')
    def calcBaseUnit():
        isForexSymbol: bool = syminfo.type == 'forex'
        isYenPair: bool = syminfo.currency == 'JPY'
        result: float = (0.01 if isYenPair else 0.0001) if isForexSymbol else syminfo.mintick
        return result

    def _afact(mode, input__ren__: Series, per, smooth):
        eff: float = 0.0
        seff: float = 0.0
        len: int = 0
        sum: float = 0.0
        max: float = 0.0
        min: float = 1000000000.0
        len = math.ceil(per) if mode == 'Kaufman' else math.ceil(math.max(20, 5 * per))
        for i in pine_range(0, len, 1):
            if mode == 'Kaufman':
                sum = sum + math.abs(input__ren__[i] - input__ren__[i + 1])
            else:
                max = input__ren__[i] if input__ren__[i] > max else max
                min = input__ren__[i] if input__ren__[i] < min else min
        if mode == 'Kaufman' and sum != 0:
            eff = math.abs(input__ren__ - input__ren__[len]) / sum
        else:
            if mode == 'Ehlers' and max - min > 0:
                eff = (input__ren__ - min) / (max - min)
        seff = ta.ema(eff, smooth)
        return seff

    baseUnit = calcBaseUnit()
    hVal2 = nz(_high[2])
    hVal1 = nz(_high[1])
    hVal0 = _high
    lowVal2 = nz(_low[2])
    lowVal1 = nz(_low[1])
    lowVal0 = _low
    hiprice2 = nz(_high[2])
    hiprice1 = nz(_high[1])
    hiprice0 = _high
    loprice2 = nz(_low[2])
    loprice1 = nz(_low[1])
    loprice0 = _low
    upSig: float = 0.0
    dnSig: float = 0.0
    aFactor: Series[float] = 0.0
    step: float = 0.0
    trend: Series[float] = 0.0
    upTrndSAR: Series[float] = 0.0
    dnTrndSAR: Series[float] = 0.0
    length = 2 / maxAFactor - 1
    if hiloMode == 'On':
        hiprice0 = _high
        loprice0 = _low
    else:
        hiprice0 = _src
        loprice0 = hiprice0
    if isPsarAdaptive:
        if bar_index == 1:
            trend = 1
            hVal1 = hiprice1
            hVal0 = math.max(hiprice0, hVal1)
            lowVal1 = loprice1
            lowVal0 = math.min(loprice0, lowVal1)
            aFactor = startAFactor
            upTrndSAR = lowVal0
            dnTrndSAR = 0.0
        else:
            hVal0 = hVal1
            lowVal0 = lowVal1
            trend = nz(trend[1])
            aFactor = nz(aFactor[1])
            inputs: float = 0.0
            inprice = _src
            if hiloMode == 'On':
                inprice = _src
            else:
                inprice = hiprice0
            if adaptMode == 'Kaufman':
                inputs = inprice
            else:
                if adaptMode == 'Ehlers':
                    if nz(upTrndSAR[1]) != 0.0:
                        inputs = math.abs(inprice - nz(upTrndSAR[1]))
                    else:
                        if nz(dnTrndSAR[1]) != 0.0:
                            inputs = math.abs(inprice - nz(dnTrndSAR[1]))
            step = minStep + _afact(adaptMode, inputs, length, adaptSmth) * (maxStep - minStep)
            upTrndSAR = 0.0
            dnTrndSAR = 0.0
            upSig = 0.0
            dnSig = 0.0
            if nz(trend[1]) > 0:
                if nz(trend[1]) == nz(trend[2]):
                    aFactor = nz(aFactor[1]) + step if hVal1 > hVal2 else aFactor
                    aFactor = maxAFactor if aFactor > maxAFactor else aFactor
                    aFactor = startAFactor if hVal1 < hVal2 else aFactor
                else:
                    aFactor = nz(aFactor[1])
                upTrndSAR = nz(upTrndSAR[1]) + aFactor * (hVal1 - nz(upTrndSAR[1]))
                upTrndSAR = loprice1 if upTrndSAR > loprice1 else upTrndSAR
                upTrndSAR = loprice2 if upTrndSAR > loprice2 else upTrndSAR
            else:
                if nz(trend[1]) == nz(trend[2]):
                    aFactor = nz(aFactor[1]) + step if lowVal1 < lowVal2 else aFactor
                    aFactor = maxAFactor if aFactor > maxAFactor else aFactor
                    aFactor = startAFactor if lowVal1 > lowVal2 else aFactor
                else:
                    aFactor = nz(aFactor[1])
                dnTrndSAR = nz(dnTrndSAR[1]) + aFactor * (lowVal1 - nz(dnTrndSAR[1]))
                dnTrndSAR = hiprice1 if dnTrndSAR < hiprice1 else dnTrndSAR
                dnTrndSAR = hiprice2 if dnTrndSAR < hiprice2 else dnTrndSAR
            hVal0 = hiprice0 if hiprice0 > hVal0 else hVal0
            lowVal0 = loprice0 if loprice0 < lowVal0 else lowVal0
            if minChng > 0:
                if upTrndSAR - nz(upTrndSAR[1]) < minChng * baseUnit and upTrndSAR != 0.0 and (nz(upTrndSAR[1]) != 0.0):
                    upTrndSAR = nz(upTrndSAR[1])
                if nz(dnTrndSAR[1]) - dnTrndSAR < minChng * baseUnit and dnTrndSAR != 0.0 and (nz(dnTrndSAR[1]) != 0.0):
                    dnTrndSAR = nz(dnTrndSAR[1])
            dnTrndSAR = nz(dnTrndSAR[1]) if trend < 0 and dnTrndSAR > nz(dnTrndSAR[1]) else dnTrndSAR
            upTrndSAR = nz(upTrndSAR[1]) if trend > 0 and upTrndSAR < nz(upTrndSAR[1]) else upTrndSAR
            if trend < 0 and hiprice0 >= dnTrndSAR + filt * baseUnit:
                trend = 1
                upTrndSAR = lowVal0
                upSig = lowVal0 if SignalMode == 'Signals & Stops' else upSig
                dnTrndSAR = 0.0
                aFactor = startAFactor
                lowVal0 = loprice0
                hVal0 = hiprice0
            elif trend > 0 and loprice0 <= upTrndSAR - filt * baseUnit:
                trend = -1
                dnTrndSAR = hVal0
                dnSig = hVal0 if SignalMode == 'Signals & Stops' else dnSig
                upTrndSAR = 0.0
                aFactor = startAFactor
                lowVal0 = loprice0
                hVal0 = hiprice0
    psar = upTrndSAR if upTrndSAR > 0 else dnTrndSAR
    psar = psar if isPsarAdaptive else inline_series(ta.sar(psarStart, psarInc, psarMax), repaint)
    plot(psar, title='PSAR', color=rajah if _src < psar else magicMint, style=plot.style_circles)
    aHtf: str = '5' if resolution == '1' else '15' if resolution == '3' else '15' if resolution == '5' else '60' if resolution == '15' else '60' if resolution == '30' else '60' if resolution == '45' else '240' if resolution == '60' else '240' if resolution == '120' else '240' if resolution == '180' else 'D' if resolution == '240' else 'W' if resolution == 'D' else ''
    emaSrc: float = request.security(syminfo.tickerid, aHtf, _src, barmerge.gaps_off, barmerge.lookahead_on)
    ema: float = ta.ema(emaSrc, emaLength)
    plot(ema, title='EMA', color=osc_color)
    isTradeOpen: Persistent[str] = ''
    crossover_1 = ta.crossover(_src, psar)
    crossover_2 = ta.crossover(osc, 0)
    enterLong: bool = _src > ema and crossover_1 and crossover_2 and (isTradeOpen == '')
    crossunder_1 = ta.crossunder(_src, psar)
    crossunder_2 = ta.crossunder(osc, 0)
    enterShort: bool = _src < ema and crossunder_1 and crossunder_2 and (isTradeOpen == '')
    if isTradeOpen == '':
        if enterLong:
            isTradeOpen = 'long'
        elif enterShort:
            isTradeOpen = 'short'
    elif isTradeOpen == 'long':
        if enterLong:
            enterLong = False
    elif isTradeOpen == 'short':
        if enterShort:
            enterShort = False
    plotshape(ema if isSignalLabelEnabled and enterLong and (isTradeOpen == 'long') else na, title='LONG', text='L', style=shape.labelup, color=mediumAquamarine, textcolor=color.white, size=size.tiny, location=location.absolute)
    plotshape(ema if isSignalLabelEnabled and enterShort and (isTradeOpen == 'short') else na, title='SHORT', text='S', style=shape.labeldown, color=carrotOrange, textcolor=color.white, size=size.tiny, location=location.absolute)
    isHighLowStopLossEnabled: bool = True
    isAutomaticHighLowTakeProfitEnabled: bool = True
    recalculateStopLossTakeProfit: bool = False
    isStrategyEntryEnabled: bool = False
    isLongEnabled: bool = True
    isShortEnabled: bool = True
    isStopLossTakeProfitRecalculationEnabled: bool = True
    longStopLossTakeProfitRecalculation: bool = True if isStopLossTakeProfitRecalculationEnabled else lastTrade == 'short' or lastTrade == 'initial'
    shortStopLossTakeProfitRecalculation: bool = True if isStopLossTakeProfitRecalculationEnabled else lastTrade == 'long' or lastTrade == 'initial'
    longHighLowStopLoss: Persistent[float] = 0
    shortHighLowStopLoss: Persistent[float] = 0
    highLowStopLossLowest: float = ta.lowest(_low, highLowStopLossLookback)
    highLowStopLossHighest: float = ta.highest(_high, highLowStopLossLookback)
    if isHighLowStopLossEnabled:
        if (enterLong and longStopLossTakeProfitRecalculation or recalculateStopLossTakeProfit) and (isTradeOpen != 'long' if isStrategyEntryEnabled else True):
            if highLowStopLossLowest == _low:
                longHighLowStopLoss = _low * highLowStopLossBackupMultiplier
            elif highLowStopLossLowest > 0:
                longHighLowStopLoss = highLowStopLossLowest * highLowStopLossMultiplier
        if (enterShort and shortStopLossTakeProfitRecalculation or recalculateStopLossTakeProfit) and (isTradeOpen != 'short' if isStrategyEntryEnabled else True):
            if highLowStopLossHighest == _high:
                shortHighLowStopLoss = _high * (1 + 1 - highLowStopLossBackupMultiplier)
            elif highLowStopLossHighest > 0:
                shortHighLowStopLoss = highLowStopLossHighest * (1 + 1 - highLowStopLossMultiplier)
    plot(longHighLowStopLoss if isLongEnabled and isHighLowStopLossEnabled and (isTradeOpen == 'long') else na, 'Long High Low Stop Loss', color=magicMint, style=plot.style_circles, trackprice=False)
    plot(shortHighLowStopLoss if isShortEnabled and isHighLowStopLossEnabled and (isTradeOpen == 'short') else na, 'Short High Low Stop Loss ', color=rajah, style=plot.style_circles, trackprice=False)
    longAutomaticHighLowTakeProfit: Persistent[float] = na(float)
    shortAutomaticHighLowTakeProfit: Persistent[float] = na(float)
    if isAutomaticHighLowTakeProfitEnabled:
        if (enterLong and longStopLossTakeProfitRecalculation or recalculateStopLossTakeProfit) and (isTradeOpen != 'long' if isStrategyEntryEnabled else True):
            longHighLowStopLossPercentage = 1 - longHighLowStopLoss / _close
            longAutomaticHighLowTakeProfit = _close * (1 + longHighLowStopLossPercentage * automaticHighLowTakeProfitRatio)
        if (enterShort and shortStopLossTakeProfitRecalculation or recalculateStopLossTakeProfit) and (isTradeOpen != 'short' if isStrategyEntryEnabled else True):
            shortHighLowStopLossPercentage = 1 - _close / shortHighLowStopLoss
            shortAutomaticHighLowTakeProfit = _close * (1 - shortHighLowStopLossPercentage * automaticHighLowTakeProfitRatio)
    plot(longAutomaticHighLowTakeProfit if isAutomaticHighLowTakeProfitEnabled and isHighLowStopLossEnabled and (isTradeOpen == 'long') else na, 'Long Automatic High Low Take Profit', color=magicMint, style=plot.style_circles, trackprice=False)
    plot(shortAutomaticHighLowTakeProfit if isAutomaticHighLowTakeProfitEnabled and isHighLowStopLossEnabled and (isTradeOpen == 'short') else na, 'Short Automatic High Low Take Profit', color=rajah, style=plot.style_circles, trackprice=False)
    longHighLowStopLossCondition: bool = ta.crossunder(_close, longHighLowStopLoss)
    shortHighLowStopLossCondition: bool = ta.crossover(_close, shortHighLowStopLoss)
    longAutomaticHighLowTakeProfitCondition: bool = ta.crossover(_close, longAutomaticHighLowTakeProfit)
    shortAutomaticHighLowTakeProfitCondition: bool = ta.crossunder(_close, shortAutomaticHighLowTakeProfit)
    exitLong: bool = (longHighLowStopLossCondition or longAutomaticHighLowTakeProfitCondition) and isTradeOpen == 'long'
    exitShort: bool = (shortHighLowStopLossCondition or shortAutomaticHighLowTakeProfitCondition) and isTradeOpen == 'short'
    plotshape(ema if isSignalLabelEnabled and exitLong and (isTradeOpen == 'long') else na, title='LONG EXIT', style=shape.circle, color=magicMint, size=size.tiny, location=location.absolute)
    plotshape(ema if isSignalLabelEnabled and exitShort and (isTradeOpen == 'short') else na, title='SHORT EXIT', style=shape.circle, color=rajah, size=size.tiny, location=location.absolute)
    if exitLong:
        strategy.close('long', comment='EXIT_LONG_TP' if longAutomaticHighLowTakeProfitCondition else 'EXIT_LONG_SL')
        isTradeOpen = ''
    if exitShort:
        strategy.close('short', comment='EXIT_SHORT_TP' if shortAutomaticHighLowTakeProfitCondition else 'EXIT_SHORT_SL')
        isTradeOpen = ''
    if enterLong:
        strategy.order('long', strategy.long, comment='ENTER_LONG')
        isTradeOpen = 'long'
    if enterShort:
        strategy.order('short', strategy.short, comment='ENTER_SHORT')
        isTradeOpen = 'short'
    if enterLong or exitLong:
        lastTrade = 'long'
    if enterShort or exitShort:
        lastTrade = 'short'
    barcolor(color=mediumAquamarine if isTradeOpen == 'long' else carrotOrange if isTradeOpen == 'short' else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
