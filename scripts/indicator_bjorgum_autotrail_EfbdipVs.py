"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, bar_index, barstate, close, color, high, input,
    location, low, math, na, open, plot, plotshape, runtime, script, shape, size, string, syminfo,
    ta, time, time_close
)
from pynecore.types import Color, Persistent, PersistentSeries

barTimeTip: str = 'Time to start trail. Time can be interactively selected with the cursor'
priceTip: str = 'Price to start trail. Price can be interactively selected with the cursor'
trailTypeTip: str = '4 different trail types can be used. Refer to release documentation for more info'
trailSourceTip: str = 'The price source for calculating trailing stop'
atrLengthTip: str = 'Length of the period for the ATR to average. Valid only if ATR type trail is envoked'
atrMultTip: str = 'Multiplier as a function of the ATR value projected from the calculated swing high/low. ex 1 = ATR distance. Valid only if ATR type trail is envoked'
percTip: str = 'Percent offset from closing price. Stop will set at the cursor selected price, and trail a change in price by a factor of percent if percent trail is selected.'
lookbackTip: str = 'Look back period to measure swing lows. A lower number brings a trail tighter to price action, where as a higher number will look back farther for significant swing points.'
startTip: str = 'PSAR Start'
incTip: str = 'Step Setting (Sensitivity) - A higher step moves SAR closer to the price action, which makes a reversal more likely'
maxTip: str = 'PSAR Max - While the Maximum Step can influence sensitivity, the Step carries more weight'
quantityTip: str = 'Will fill in quantity for an alert if used'
marketTip: str = 'Will fill in a market for an alert if used. Ex. Spot or futures acronyms'
brokerTip: str = 'Will fill in a broker for a fx based alert if used'


@script.indicator('Bjorgum AutoTrail', 'Bj AutoTrail', overlay=True, na_bool=True)
def main(
    barTime=input.time(0, 'Bar Time', group='Set Trade', tooltip=barTimeTip, inline='1', confirm=True),
    price=input.price(0, 'Price', group='Set Trade', tooltip=priceTip, inline='1', confirm=True),
    trailType=input.string('Price', 'Trail Type', group='Set Trade', tooltip=trailTypeTip, options=('ATR', 'Percent', 'Price', 'Sar')),
    trailSource=input.string('High/Low', 'Stop Source', group='Set Trade', tooltip=trailSourceTip, options=('High/Low', 'Close', 'Open')),
    atrLength=input.int(14, 'ATR Length', group='Trail Offset', tooltip=atrLengthTip),
    atrMult=input.float(1, 'ATR Multiplier', group='Trail Offset', tooltip=atrMultTip),
    perc=input.float(2.0, 'Percent Trail', group='Trail Offset', tooltip=percTip),
    lookback=input.int(5, 'Lookback', group='Trail Offset', tooltip=lookbackTip),
    start=input.float(0.043, 'Start', group='Psar Settings', tooltip=startTip),
    inc=input.float(0.043, 'inc', group='Psar Settings', tooltip=incTip),
    max=input.float(0.34, 'max', group='Psar Settings', tooltip=maxTip),
    longCol=input.color(color.new('#64B5F6'), '', group='Stop Color', inline='2'),
    ShortCol=input.color(color.new('#EF5350'), '', group='Stop Color', inline='2'),
    lineWidth=input.int(2, '', group='Stop Color', inline='2'),
    transp=input.int(0, '', group='Stop Color', inline='2'),
    quantity=input.float(0.001, 'Quantity', group='Live Trade Metrics', tooltip=quantityTip),
    market=input.string('usdm', 'Market', group='Live Trade Metrics', tooltip=marketTip),
    broker=input.string('Test', 'Broker', group='Live Trade Metrics', tooltip=brokerTip)
):
    lColor: Persistent[Color] = color.new(longCol, transp)
    sColor: Persistent[Color] = color.new(ShortCol, transp)
    trade: PersistentSeries[int] = 0
    trailPrice: Persistent[float] = 0.0
    initSrc: Persistent[float] = 0.0
    initHigh: Persistent[float] = 0.0
    initLow: Persistent[float] = 0.0
    long: Persistent[bool] = False
    short: Persistent[bool] = False
    oneTime: Persistent[bool] = True
    psar: Persistent[bool] = trailType == 'Sar'
    atrTrail: Persistent[bool] = trailType == 'ATR'
    percTrail: Persistent[bool] = trailType == 'Percent'
    tTrailPrice: float = 0.0
    sar: Persistent[float] = na(float)
    maxMin: Persistent[float] = na(float)
    accel: Persistent[float] = na(float)
    isBelow: PersistentSeries[bool] = na(bool)
    lsar: Persistent[float] = 0.0
    isFirstTrendBar: bool = False
    if bar_index == 1:
        if close > close[1]:
            isBelow = True
            maxMin = high
            sar = low[1]
        else:
            isBelow = False
            maxMin = low
            sar = high[1]
        isFirstTrendBar = True
        accel = start
    sar = sar + accel * (maxMin - sar)
    lsar = sar
    if isBelow:
        if sar > low:
            isFirstTrendBar = True
            isBelow = False
            sar = math.max(high, maxMin)
            maxMin = low
            accel = start
    else:
        if sar < high:
            isFirstTrendBar = True
            isBelow = True
            sar = math.min(low, maxMin)
            maxMin = high
            accel = start
    if not isFirstTrendBar:
        if isBelow:
            if high > maxMin:
                maxMin = high
                accel = math.min(accel + inc, max)
        else:
            if low < maxMin:
                maxMin = low
                accel = math.min(accel + inc, max)
    if isBelow:
        sar = math.min(sar, low[1])
        if bar_index > 1:
            sar = math.min(sar, low[2])
    else:
        sar = math.max(sar, high[1])
        if bar_index > 1:
            sar = math.max(sar, high[2])
    timeStart = time_close[1] <= barTime and time >= barTime
    if timeStart:
        long = price < close
        short = price > close
        initSrc = close if trailSource == 'Close' else open if trailSource == 'Open' else low if long else high
        initHigh = high
        initLow = low
        if long:
            trade = 1
        if short:
            trade = -1
    atr = ta.atr(atrLength)
    trailSrc = close[1] if trailSource == 'Close' else open[1] if trailSource == 'Open' else low if long else high
    diff = math.abs(initSrc - price)
    offset = close * (perc / 100) if percTrail else atr * atrMult if atrTrail else diff
    swingLow = ta.lowest(trailSrc, lookback) - offset
    swingHigh = ta.highest(trailSrc, lookback) + offset
    sarTrail = long and isBelow or (short and (not isBelow))
    levelCheck = long and price < swingLow or (short and price > swingHigh)
    tTrailPrice = sar if psar and sarTrail else price if timeStart and (not levelCheck) else swingLow if long else swingHigh if short else 0
    if time >= barTime and (psar or barstate.isconfirmed):
        if long and trade == 1:
            if tTrailPrice > trailPrice or trailPrice == 0.0:
                trailPrice = tTrailPrice
            if low <= trailPrice:
                trade = 0
            if isBelow[1] and psar and (not isBelow) and inline_series(trade != 0, 1):
                trade = 0
        if short and trade == -1:
            if tTrailPrice < trailPrice or trailPrice == 0.0:
                trailPrice = tTrailPrice
            if high >= trailPrice:
                trade = 0
            if isBelow and (not isBelow[1]) and psar and inline_series(trade != 0, 1):
                trade = 0
    longSig = inline_series(trade == 1, 1) and low <= trailPrice
    shortSig = inline_series(trade == -1, 1) and high >= trailPrice
    psarSig = psar and trade != trade[1] and inline_series(trade != 0, 1)
    plotPsar = lsar if psarSig else trailPrice if psar and trade != 0 else na
    plotTrail = na if psar else trailPrice if trailPrice != 0 else na
    longStop = psarSig if long and psar else longSig
    shortStop = psarSig if short and psar else shortSig
    plotColor = lColor if long else sColor
    plotshape(longStop, style=shape.xcross, size=size.tiny, text='Long Stop', color=lColor, textcolor=lColor, location=location.abovebar)
    plotshape(shortStop, style=shape.xcross, size=size.tiny, text='Short Stop', color=sColor, textcolor=sColor, location=location.belowbar)
    plot(na if psar else trailPrice if trailPrice != 0 else na, 'Trailing Stop', color=na if inline_series(trade == 0, 1) else plotColor, style=plot.style_linebr, linewidth=math.max(1, lineWidth))
    plot(plotPsar, 'SAR', plotColor, style=plot.style_circles, linewidth=math.max(1, lineWidth))
    if price <= initHigh and price >= initLow and (time_close >= barTime) and (time_close[1] <= barTime):
        runtime.error('Stop cannot be placed in candle range')
    action = 'sell' if long else 'buy' if short else na
    if (longStop or shortStop) and oneTime and (syminfo.type == 'crypto'):
        alert(action + ' ' + syminfo.basecurrency + syminfo.currency + ' ' + 'q=' + string.tostring(quantity) + ' ' + 'a=' + market)
        oneTime = False
    if (longStop or shortStop) and oneTime and (syminfo.type == 'forex'):
        alert('e=' + broker + ' s=' + syminfo.basecurrency + '/' + syminfo.currency + ' b=' + action + ' q=' + string.tostring(quantity))
        oneTime = False
    alertcondition(longStop, 'Long Trail', 'Long  Trail Trigger on {{interval}} chart. Price is {{close}}')
    alertcondition(shortStop, 'Short Trail', 'Short Trail Trigger on {{interval}} chart. Price is {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)