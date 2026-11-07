"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, barstate, bgcolor, close, color, currency, display, high, input,
    location, low, math, na, plot, plotcandle, plotshape, script, shape, size, strategy, string,
    syminfo, ta
)
from pynecore.types import Persistent, PersistentSeries, Series

headlineTMO: str = 'TMO Settings'
headlineAMA: str = 'AMA Settings'
headlineSL: str = 'Stop Loss Settings'


@script.strategy('TradeIQ - Crazy Scalping Trading Strategy [Kaspricci]', overlay=True, initial_capital=1000, currency=currency.USD, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    tmoLength=input.int(7, 'TMO Length', minval=1, group=headlineTMO),
    tmoSource: Series[float] = input.source(close, 'TMO Source', group=headlineTMO),
    amaSource: Series[float] = input.source(defval=close, title='AMA Source', group=headlineAMA),
    amaLength=input.int(defval=50, title='AMA Length', minval=2, group=headlineAMA),
    amaMulti=input.float(defval=2.0, title='Factor', minval=1),
    amaShowCd=input(defval=True, title='As Smoothed Candles'),
    amaShowEx=input(defval=True, title='Show Alternating Extremities'),
    amaAlpha=input.float(1.0, 'Lag', minval=0, step=0.1, tooltip='Control the lag of the moving average (higher = more lag)', group='AMA Kernel Parameters'),
    amaBeta=input.float(0.5, 'Overshoot', minval=0, step=0.1, tooltip='Control the overshoot amplitude of the moving average (higher = overshoots with an higher amplitude)', group='AMA Kernel Parameters'),
    slLength=input.int(defval=10, title='SL Period', minval=1, group=headlineSL, tooltip='Number of bars for swing high / low')
):
    osc: Series = ta.mom(ta.sma(ta.sma(tmoSource, tmoLength), tmoLength), tmoLength)
    oscColor = color.new('#00C42B') if osc > osc[1] and osc > 0 else color.new('#4EE567') if osc < osc[1] and osc > 0 else color.new('#FF441F') if osc < osc[1] and osc < 0 else color.new('#C03920') if osc > osc[1] and osc < 0 else na
    up = ta.highest(tmoSource, tmoLength)
    dn = ta.lowest(tmoSource, tmoLength)
    phosc = ta.crossunder(ta.change(osc), 0)
    plosc = ta.crossover(ta.change(osc), 0)
    valuewhen_1 = ta.valuewhen(phosc, osc, 0)
    valuewhen_2 = ta.valuewhen(phosc, osc, 1)
    valuewhen_3 = ta.valuewhen(phosc, up, 0)
    valuewhen_4 = ta.valuewhen(phosc, up, 1)
    bear = 1 if osc > 0 and phosc and (valuewhen_1 < valuewhen_2) and (valuewhen_3 > valuewhen_4) else 0
    valuewhen_5 = ta.valuewhen(plosc, osc, 0)
    valuewhen_6 = ta.valuewhen(plosc, osc, 1)
    valuewhen_7 = ta.valuewhen(plosc, dn, 0)
    valuewhen_8 = ta.valuewhen(plosc, dn, 1)
    bull = 1 if osc < 0 and plosc and (valuewhen_5 > valuewhen_6) and (valuewhen_7 < valuewhen_8) else 0
    b: Persistent[list[float]] = array.new_float(0)
    x: Persistent[float] = na(float)
    if barstate.isfirst:
        for i in pine_range(0, amaLength - 1, 1):
            x = i / (amaLength - 1)
            w = math.sin(2 * 3.14159 * math.pow(x, amaAlpha)) * (1 - math.pow(x, amaBeta))
            array.push(b, w)
    def filter(x: Series[float]):
        sum: float = 0.0
        for i in pine_range(0, amaLength - 1, 1):
            sum = sum + x[i] * array.get(b, i)
        return sum / array.sum(b)

    srcFiltered = filter(amaSource)
    deviation = ta.sma(math.abs(amaSource - srcFiltered), amaLength) * amaMulti
    upper = srcFiltered + deviation
    lower = srcFiltered - deviation
    crossHigh = ta.cross(high, upper)
    crossLow = ta.cross(low, lower)
    os: PersistentSeries[int] = 0
    os = 1 if crossHigh else 0 if crossLow else os[1]
    ext = os * upper + (1 - os) * lower
    os_css = ta.rsi(srcFiltered, amaLength) / 100
    extColor = color.new('#30FF85') if os == 1 else color.new('#FF1100')
    plot(srcFiltered, 'MA', na if amaShowCd else color.black, 2, editable=False)
    plot(ext if amaShowEx else na, 'Extremities', na if cast_bool(ta.change(os)) else extColor, 2, editable=False)
    h: Persistent[float] = na(float)
    l: Persistent[float] = na(float)
    c: PersistentSeries[float] = na(float)
    body: PersistentSeries[float] = na(float)
    if amaShowCd:
        h = filter(high)
        l = filter(low)
        c = filter(amaSource)
        body = math.abs(math.avg(c[1], c[2]) - c)
    ohlc_os = ta.rsi(c, amaLength) / 100
    plotcandle(math.avg(c[1], c[2]), h, l, c, 'Smooth Candles', color.new('#434651'), bordercolor=na, editable=False, display=display.all if amaShowCd else display.none)
    plotshape(ext if cast_bool(bull) else na, 'Bullish Circle', shape.circle, location.absolute, color=color.new('#00C42B'), size=size.tiny)
    plotshape(ext if cast_bool(bear) else na, 'Bearish Circle', shape.circle, location.absolute, color=color.new('#FF441F'), size=size.tiny)
    plotshape(ext if cast_bool(bull) else na, 'Bullish Label', shape.labeldown, location.absolute, color=color.new('#00C42B'), text='Buy', textcolor=color.white, size=size.tiny)
    plotshape(ext if cast_bool(bear) else na, 'Bearish Label', shape.labelup, location.absolute, color=color.new('#FF441F'), text='Sell', textcolor=color.white, size=size.tiny)
    candleSizeIncreasing: Series = body[2] < body[1] and body[1] < body
    longEntryCond = os == 1 and cast_bool(bull)
    shortEntryCond = os == 0 and cast_bool(bear)
    barssince_1 = ta.barssince(longEntryCond)
    barssince_2 = ta.barssince(os == 0)
    barssince_3 = ta.barssince(longEntryCond)
    barssince_4 = ta.barssince(cast_bool(bear))
    longEntry = strategy.opentrades == 0 and candleSizeIncreasing and (not candleSizeIncreasing[1]) and (barssince_1 < barssince_2) and (barssince_3 < barssince_4)
    barssince_5 = ta.barssince(shortEntryCond)
    barssince_6 = ta.barssince(os == 1)
    barssince_7 = ta.barssince(shortEntryCond)
    barssince_8 = ta.barssince(cast_bool(bull))
    shortEntry = strategy.opentrades == 0 and candleSizeIncreasing and (not candleSizeIncreasing[1]) and (barssince_5 < barssince_6) and (barssince_7 < barssince_8)
    longExit = strategy.opentrades > 0 and strategy.position_size > 0 and (cast_bool(bear) or os == 0)
    shortExit = strategy.opentrades > 0 and strategy.position_size < 0 and (cast_bool(bull) or os == 1)
    recentSwingHigh = ta.highest(high, slLength)
    recentSwingLow = ta.lowest(low, slLength)
    bgcolor(color.rgb(76, 175, 79, 90) if longEntry else na)
    bgcolor(color.rgb(255, 82, 82, 90) if shortEntry else na)
    slLong = (close - recentSwingLow) / syminfo.mintick
    slShort = (recentSwingHigh - close) / syminfo.mintick
    newOrderID = string.tostring(strategy.closedtrades + strategy.opentrades + 1)
    curOrderID = string.tostring(strategy.closedtrades + strategy.opentrades)
    alertMessageForEntry: str = 'Trade {0} - New {1} Entry at price: {2} with stop loss at: {3}'
    if longEntry:
        alertMessage = string.format(alertMessageForEntry, newOrderID, 'Long', close, recentSwingLow)
        strategy.entry(newOrderID, strategy.long, alert_message=alertMessage)
        strategy.exit('Stop Loss Long', newOrderID, loss=slLong, alert_message='Stop Loss for Trade ' + newOrderID)
    if longExit:
        strategy.close(curOrderID, alert_message='Close Trade ' + curOrderID)
    if shortEntry:
        alertMessage = string.format(alertMessageForEntry, newOrderID, 'Short', close, recentSwingLow)
        strategy.entry(newOrderID, strategy.short, alert_message=alertMessage)
        strategy.exit('Stop Loss Short', newOrderID, loss=slShort, alert_message='Stop Loss for Trade ' + newOrderID)
    if shortExit:
        strategy.close(curOrderID, alert_message='Close Trade ' + curOrderID)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
