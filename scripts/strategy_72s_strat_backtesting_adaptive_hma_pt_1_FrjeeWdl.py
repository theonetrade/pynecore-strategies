"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, bgcolor, close, color, fill, high, hl2, input, label, location,
    low, math, na, nz, open, plot, plotchar, plotshape, script, shape, size, strategy, string,
    syminfo, ta, text, time, xloc
)
from pynecore.types import Label, Persistent, Series


@script.strategy('72s Strategy: Adaptive Hull Moving Average+ pt.1', shorttitle='72s Strat: Adaptive HMA+ pt.1', overlay=True, pyramiding=1, initial_capital=1000, commission_type=strategy.commission.cash_per_order, commission_value=0.5, slippage=3, max_bars_back=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    orderSize=input.float(0.1, title='Order Size (in Lot)', step=0.1, group='ORDERS'),
    __input_1__=input.float(1, step=0.1, title='Base Minimum Profit before exit (ATR)', group='ORDERS'),
    __input_2__=input.float(3, step=0.1, title='Default Target Profit (ATR)', group='ORDERS'),
    useSL=input.bool(True, title='Use StopLoss', group='ORDERS'),
    SLInput=input.string('Half Distance Zone', title='Base StopLoss Point', options=('One Distance Zone', 'Half Distance Zone', 'Last High/Low', 'ATR Only'), group='ORDERS'),
    __input_5__=input.float(4.5, step=0.1, title='Maximum StopLoss (ATR)', group='ORDERS'),
    doubleUp=input.bool(False, 'Activate 2nd order with xHMA+ exits', group='ORDERS'),
    minLength=input.int(172, title='Minimum:', group='Adaptive HMA+ Period', inline='HMA+'),
    maxLength=input.int(233, title='Maximum:', group='Adaptive HMA+ Period', inline='HMA+'),
    flat=input.int(17, title='Flat Market when xHMA\'s slope below', group='Market Movement'),
    atrFast=input.int(14, 'Charged if ATR', group='Market Movement', inline='volality', minval=2, maxval=34),
    atrSlow=input.int(46, '>= ATR', group='Market Movement', inline='volality', minval=21, maxval=120),
    showZone=input.bool(False, title='Show Adaptive HMA+ Distance Zone', group='DISTANCE ZONE'),
    mult=input.float(2.7, title='Distance (Envelope) Multiplier', step=0.1, group='DISTANCE ZONE'),
    minorMin=input.int(89, title='Minimum:', group='Minor Adaptive HMA+ Period', inline='mHMA+'),
    minorMax=input.int(121, title='Maximum:', group='Minor Adaptive HMA+ Period', inline='mHMA+'),
    showMA=input.bool(True, title='Show MA?', group='OTHER'),
    useBg=input.bool(True, title='Background color to differentiate movement', group='OTHER'),
    __input_18__: Series[float] = input.source(close, 'RSI Source', inline='RSI', group='OTHER'),
    __input_19__=input.int(14, 'RSI Length', inline='RSI', group='OTHER')
):
    atrBase = ta.atr(21)
    src = close
    adaptPct: float = 0.03141
    minProfit = __input_1__ * atrBase
    takeProfit = __input_2__ * atrBase
    maxSL = __input_5__ * atrBase
    rsi: Series = ta.rsi(__input_18__, __input_19__)
    charged = ta.atr(atrFast) > ta.atr(atrSlow)
    dynamicLength: Persistent[float] = math.avg(minLength, maxLength)
    minorLength: Persistent[float] = math.avg(minorMin, minorMax)
    dynamicLength = math.max(minLength, dynamicLength * (1 - adaptPct)) if charged else math.min(maxLength, dynamicLength * (1 + adaptPct))
    minorLength = math.max(minorMin, minorLength * (1 - adaptPct)) if charged else math.min(minorMax, minorLength * (1 + adaptPct))
    pi = math.atan(1) * 4
    highestHigh = ta.highest(34)
    lowestLow = ta.lowest(34)
    slope_range = 25 / (highestHigh - lowestLow) * lowestLow
    def calcslope(_ma: Series):
        dt = (_ma[2] - _ma) / src * slope_range
        c = math.sqrt(1 + dt * dt)
        xAngle = math.round(180 * math.acos(1 / c) / pi)
        maAngle = -xAngle if dt > 0 else xAngle
        return maAngle

    def dynColor(_ma, _col1a, _col1b, _col2a, _col2b, _col0):
        slope = calcslope(_ma)
        return (_col1a if charged else _col1b) if slope >= flat else _col0 if slope < flat and slope > -flat else (_col2a if charged else _col2b) if slope <= -flat else _col0

    def xhma(_src, _length):
        _return = ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.floor(math.sqrt(_length)))
        return _return

    dynamicHMA = xhma(src, cast_int(dynamicLength))
    minorHMA = xhma(src, cast_int(minorLength))
    _slope = calcslope(dynamicHMA)
    plotchar(_slope, 'slope is:', '', location.top)
    upperTL = dynamicHMA + mult * ta.atr(40)
    lowerTL = dynamicHMA - mult * ta.atr(40)
    topTL = dynamicHMA + mult * 2 * ta.atr(40)
    botTL = dynamicHMA - mult * 2 * ta.atr(40)
    stopupperTL = dynamicHMA + mult / 2 * ta.atr(40)
    stoplowerTL = dynamicHMA - mult / 2 * ta.atr(40)
    plot(upperTL if showZone else na, color=color.new(color.green, 72))
    plot(lowerTL if showZone else na, color=color.new(color.red, 72))
    plot(topTL if showZone else na, color=color.new(color.gray, 72))
    plot(botTL if showZone else na, color=color.new(color.gray, 72))
    sutl = plot(stopupperTL if showZone else na, color=color.new(color.white, 100))
    sltl = plot(stoplowerTL if showZone else na, color=color.new(color.white, 100))
    colZone = color.purple if showZone else color.new(color.white, 100)
    fill(sutl, sltl, color=color.new(colZone, 90))
    plot(dynamicHMA if showMA else na, 'Adaptive HMA+', dynColor(dynamicHMA, color.new('#6FBF73'), color.new('#C0F5AE'), color.new('#EB4D5C'), color.new('#F2B1D4'), color.yellow), 3)
    plot(minorHMA if showMA else na, 'minor HMA+', dynColor(minorHMA, color.new('#6FBF73'), color.new('#C0F5AE'), color.new('#EB4D5C'), color.new('#F2B1D4'), color.yellow), 1)
    notgreat = _slope < flat and _slope > -flat
    bgcolor((na if charged else color.new('#AFB4B9')) if useBg else na)
    emma200 = ta.ema(close, 200)
    upSig: Series = _slope >= flat and charged
    dnSig: Series = _slope <= -flat and charged
    buy = upSig and (not upSig[1]) and (close > dynamicHMA) and (low <= upperTL) and (rsi > 51) and (rsi <= 70)
    sell = dnSig and (not dnSig[1]) and (close < dynamicHMA) and (high >= lowerTL) and (rsi < 49) and (rsi >= 30)
    overBuy = upSig and (not upSig[1]) and (rsi > 70) and (close > dynamicHMA) and (hl2 > upperTL) and (minorHMA > dynamicHMA)
    overSell = dnSig and (not dnSig[1]) and (rsi < 30) and (close < dynamicHMA) and (hl2 < lowerTL) and (minorHMA < dynamicHMA)
    secondBuy = (buy or overBuy) and rsi[1] < rsi
    secondSell = (sell or overSell) and rsi[1] > rsi
    atrPos = 0.2 * ta.atr(5)
    plotshape(dynamicHMA - atrPos if buy else na, color=color.new(color.green, 0), location=location.absolute, style=shape.labelup, text='buy', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(dynamicHMA + atrPos if sell else na, color=color.new(color.red, 0), location=location.absolute, style=shape.labeldown, text='sell', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(dynamicHMA - atrPos if overBuy else na, color=color.new(color.green, 0), location=location.absolute, style=shape.labelup, text='overBuy', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(dynamicHMA + atrPos if overSell else na, color=color.new(color.red, 0), location=location.absolute, style=shape.labeldown, text='overSell', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(dynamicHMA - atrPos * 8 if doubleUp and secondBuy else na, color=color.new(color.green, 0), location=location.absolute, style=shape.labelup, text='+buy', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(dynamicHMA + atrPos * 8 if doubleUp and secondSell else na, color=color.new(color.red, 0), location=location.absolute, style=shape.labeldown, text='+sell', textcolor=color.new(color.white, 0), size=size.small)
    if buy:
        alert('Buy signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if sell:
        alert('Sell signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if overBuy:
        alert('OverBuy signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if overSell:
        alert('OverSell signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if doubleUp and secondBuy:
        alert('2nd Buy signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if doubleUp and secondSell:
        alert('2nd Sell signal at ' + string.tostring(close), alert.freq_once_per_bar_close)
    standard1LotUnits = 100000 if syminfo.type == 'forex' else 100 if syminfo.ticker == 'XAUUSD' else 5000 if syminfo.ticker == 'XAGUSD' else 1 if syminfo.type == 'crypto' else 1000
    lotSize = standard1LotUnits * orderSize
    def pip():
        return syminfo.mintick * (10 if syminfo.type == 'forex' else 1)

    SLHighMax = high + maxSL
    SLLowMax = low - maxSL
    lastHigh = ta.highest(high, 48) + 5 * pip()
    lastLow = ta.lowest(low, 48) - 5 * pip()
    SLBuy = botTL if SLInput == 'One Distance Zone' else lowerTL if SLInput == 'Half Distance Zone' else lastLow if SLInput == 'Last High/Low' else SLLowMax if SLInput == 'ATR Only' else SLLowMax
    SLSell = topTL if SLInput == 'One Distance Zone' else upperTL if SLInput == 'Half Distance Zone' else lastHigh if SLInput == 'Last High/Low' else SLHighMax if SLInput == 'ATR Only' else SLHighMax
    entryPrice: Series[float] = na(float)
    normOrder: Series[float] = 0
    riskOrder: Series[float] = 0
    buyTP: Series[float] = na(float)
    sellTP: Series[float] = na(float)
    buySL: Series[float] = na(float)
    sellSL: Series[float] = na(float)
    entryPrice = nz(entryPrice[1])
    normOrder = nz(normOrder[1])
    riskOrder = nz(riskOrder[1])
    buyTP = nz(buyTP[1])
    sellTP = nz(sellTP[1])
    buySL = nz(buySL[1])
    sellSL = nz(sellSL[1])
    if buy or sell or overBuy or overSell:
        entryPrice = close
        if buy or (sell and strategy.position_size == 0):
            normOrder = 1
        if overBuy or (overSell and strategy.position_size == 0):
            riskOrder = 1
        buyTP = high + takeProfit
        sellTP = low - takeProfit
        if buy or overBuy:
            buySL = SLBuy if SLLowMax < SLBuy else SLLowMax
        if sell or overSell:
            sellSL = SLSell if SLHighMax > SLSell else SLHighMax
    minBuyProfit = strategy.position_avg_price + minProfit
    minSellProfit = strategy.position_avg_price - minProfit
    stopLossBuy = low <= buySL if useSL else False
    stopLossSell = high >= sellSL if useSL else False
    takeProfitBuy = high >= buyTP
    takeProfitSell = low <= sellTP
    RSIexitBuy = ta.crossunder(rsi, 70) or rsi < 50
    RSIexitSell = ta.crossover(rsi, 30) or rsi > 50
    crossunder_1 = ta.crossunder(close, dynamicHMA)
    exitBuy = close >= minBuyProfit and (RSIexitBuy or crossunder_1) or stopLossBuy or takeProfitBuy
    crossover_1 = ta.crossover(close, dynamicHMA)
    exitSell = close <= minSellProfit and (RSIexitSell or crossover_1) or stopLossSell or takeProfitSell
    crossunder_2 = ta.crossunder(rsi, 45)
    exitoverBuy = close >= minBuyProfit and (crossunder_2 or (open < stopupperTL and hl2 < stopupperTL)) or (open < dynamicHMA and rsi < 60) or stopLossBuy or takeProfitBuy
    crossover_2 = ta.crossover(rsi, 55)
    exitoverSell = close <= minSellProfit and (crossover_2 or (open > stoplowerTL and hl2 > stoplowerTL)) or (open > dynamicHMA and rsi > 40) or stopLossSell or takeProfitSell
    crossunder_3 = ta.crossunder(close, minorHMA)
    exitSecondBuy = close >= minBuyProfit and crossunder_3 or stopLossBuy
    crossover_3 = ta.crossover(close, minorHMA)
    exitSecondSell = close <= minSellProfit and crossover_3 or stopLossSell
    inBuyExit = strategy.position_size > 0 and (normOrder == 1 and exitBuy or (riskOrder == 1 and exitoverBuy))
    inSellExit = strategy.position_size < 0 and (normOrder == 1 and exitSell or (riskOrder == 1 and exitoverSell))
    in2ndBuyExit = strategy.position_size > 0 and doubleUp and exitSecondBuy
    in2ndSellExit = strategy.position_size < 0 and doubleUp and exitSecondSell
    if inBuyExit or inSellExit:
        if normOrder == 1 and exitBuy:
            normOrder = 0
            alert('Close Buy Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
        if normOrder == 1 and exitSell:
            normOrder = 0
            alert('Close Sell Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
        if riskOrder == 1 and exitoverBuy:
            riskOrder = 0
            alert('Close overBuy Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
        if riskOrder == 1 and exitoverSell:
            riskOrder = 0
            alert('Close overSell Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if in2ndBuyExit:
        alert('Close 2nd Buy Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
    if in2ndSellExit:
        alert('Close 2nd Sell Position/s at ' + string.tostring(close), alert.freq_once_per_bar_close)
    plotchar(inBuyExit, color=color.new(color.green, 0), location=location.abovebar, char='ⓧ', size=size.tiny)
    plotchar(inSellExit, color=color.new(color.red, 0), location=location.belowbar, char='ⓧ', size=size.tiny)
    plotchar(in2ndBuyExit, color=color.new(color.teal, 0), location=location.abovebar, char='ⓧ', size=size.tiny)
    plotchar(in2ndSellExit, color=color.new(color.maroon, 0), location=location.belowbar, char='ⓧ', size=size.tiny)
    if buy:
        strategy.entry('buy', strategy.long, qty=lotSize)
    if sell:
        strategy.entry('sell', strategy.short, qty=lotSize)
    if overBuy:
        strategy.entry('overBuy', strategy.long, qty=lotSize)
    if overSell:
        strategy.entry('overSell', strategy.short, qty=lotSize)
    if doubleUp:
        if secondBuy:
            strategy.entry('2ndBuy', strategy.long, qty=lotSize)
        if secondSell:
            strategy.entry('2ndSell', strategy.short, qty=lotSize)
    if exitBuy:
        strategy.close('buy', comment='close buy')
    if exitSell:
        strategy.close('sell', comment='close sell')
    if exitoverBuy:
        strategy.close('overBuy', comment='close overBuy')
    if exitoverSell:
        strategy.close('overSell', comment='close overSell')
    if doubleUp:
        if exitSecondBuy:
            strategy.close('2ndBuy', comment='close 2nd Buy')
        if exitSecondSell:
            strategy.close('2ndSell', comment='close 2nd Sell')
    orderCol = color.green if strategy.position_size > 0 else color.red if strategy.position_size < 0 else na
    plot(entryPrice if strategy.position_size != 0 else na, style=plot.style_cross)
    plot(buySL if useSL and strategy.position_size > 0 else sellSL if useSL and strategy.position_size < 0 else na, color=color.new(color.red, 50), style=plot.style_cross, linewidth=1, title='Stop Loss')
    plot(buyTP if strategy.position_size > 0 else sellTP if strategy.position_size < 0 else na, color=color.new(color.green, 50), style=plot.style_cross, linewidth=1, title='Take Profit')
    mUnit = lotSize * pip()
    ppip = math.round((strategy.grossprofit - strategy.grossprofit[1]) / syminfo.pointvalue / mUnit, 1)
    lpip = math.round((strategy.grossloss - strategy.grossloss[1]) / syminfo.pointvalue / mUnit, 1)
    pipGain = math.round(strategy.grossprofit / syminfo.pointvalue / mUnit)
    pipLoss = math.round(strategy.grossloss / syminfo.pointvalue / mUnit)
    avg_ppip = math.round(pipGain / strategy.wintrades, 1)
    pctProfit = math.round(strategy.wintrades / strategy.closedtrades * 100, 2)
    maxDD = math.ceil(strategy.max_drawdown / syminfo.pointvalue / mUnit)
    txt2: Persistent[str] = ''
    txt = 'Total trades: ' + string.tostring(strategy.closedtrades) + '\n(' + string.tostring(pctProfit) + '%) Win: ' + string.tostring(strategy.wintrades) + ' / Loss: ' + string.tostring(strategy.losstrades) + '\nAverage win pips per trade: ' + string.tostring(avg_ppip) + ' pips\n\nApproximate (*give n take)\nTotal Pip Gain: ' + string.tostring(pipGain) + ' pips' + '\nTotal Pip Loss: ' + string.tostring(pipLoss) + ' pips' + '\n\nMax Drawdown so far: ' + string.tostring(maxDD) + ' pips'
    if strategy.wintrades > strategy.wintrades[1]:
        txt2 = '\n\nLast closed trade: Bagged ' + string.tostring(ppip) + ' pips 👻'
    if strategy.losstrades > strategy.losstrades[1]:
        txt2 = '\n\nLast closed trade: Blew ' + string.tostring(lpip) + ' pips 😪'
    txt = txt + txt2
    pvtLabel: Series[Label] = label.new(time, lowestLow, text=txt, color=color.new(color.white, 100), xloc=xloc.bar_time, style=label.style_label_left, textcolor=color.gray, textalign=text.align_left)
    label.set_x(pvtLabel, label.get_x(pvtLabel) + (time - time[1]) * 21)
    label.delete(pvtLabel[1])


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
