"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, close, color, display, format, high, input, label,
    line, low, math, na, nz, plot, script, strategy, string, ta, time, xloc, yloc
)
from pynecore.types import Label, Line, NA, Persistent
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa
import lib.HeWhoMustNotBeNamed.eHarmonicpatternsExtended.v6 as hp
import lib.HeWhoMustNotBeNamed.ta.v1 as eta


@udt
class Pivot:
    price: float = na(float)
    bar: int = na(int)
    bartime: int = na(int)
    direction: int = na(int)
    percentB: float = na(float)
    ratio: float = 0


@udt
class Drawing:
    zigzagLine: Line = na(Line)
    zigzagLabel: Label = na(Label)


tradeSettingsTooltip: str = 'Pullback - On first pullback after trend confirmation\nBreakout - On first breakout of trendPullback-Breakout - On first pullback and breakout of trend\nAny - As soon as trend change'


@script.strategy('Band-Zigzag - TrendFollower Strategy [Trendoscope]', 'BZSTF[Trendoscope]', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.05, close_entries_rule='ANY', margin_long=100, margin_short=100, max_lines_count=500, max_labels_count=500, max_boxes_count=500, use_bar_magnifier=False, close_by_id=True)
def main(
    tradeDirection=input.string(strategy.direction.all, 'Trade Direction', options=(strategy.direction.long, strategy.direction.short, strategy.direction.all), group='Trade Settings', tooltip='Use this to filter only long or short trades'),
    tradeType=input.string('Any', 'Trade Type', options=('Pullback', 'Breakout', 'Pullback-Breakout', 'Any'), group='Trade Settings', tooltip=tradeSettingsTooltip),
    useStopLoss=input.bool(False, 'Use Stop Loss', group='Trade Settings', tooltip='If set, initial stoploss is used for every trade. Otherwise, trade can only be closed by change of trend. Not required if using Recent Pivot Override'),
    bandType=input.string('Bollinger Bands', '', options=('Bollinger Bands', 'Keltner Channel', 'Donchian Channel'), group='Bands', inline='b1'),
    maType=input.string('sma', '', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'highlow', 'linreg', 'median'), inline='b1', group='Bands'),
    maLength=input.int(20, '', minval=5, step=5, inline='b1', group='Bands'),
    multiplier=input.float(2.0, '', step=0.5, minval=0.5, group='Bands', inline='b1', tooltip='Band parameters let you select type of band/channel, moving average base, length and multiplier'),
    useTrueRange=input.bool(True, 'Use True Range (For KC only)', group='Bands', tooltip='Used only for keltener channel calculation'),
    sticky=input.bool(True, 'Sticky', group='Bands', tooltip='Sticky bands avoids changing the band unless there is breach. Meaning, band positions only change when price is outside the band.'),
    useAdaptive=input.bool(True, 'Adaptive', group='Bands', tooltip='When selected, lower band will not decrease when pivot high is in motion and upper band will not increase when pivot low in motion'),
    showBands=input.bool(True, 'Display Bands', group='Bands', tooltip='If selected, displays bands on chart'),
    useLatestPivot=input.bool(True, 'Use Recent Pivot Override', group='Trend', inline='t'),
    currentTrendInvalidationMultiplier=input.float(1.618, '', minval=0, maxval=100, step=1, group='Trend', inline='t', tooltip='Trend calculation is done on last confirmed pivot. This option provides opportunity to also consider current unconfirmed pivot for defining trend on extreme moves. This will help in avoiding steep drawbacks')
):
    tradeOnBreakout = tradeType == 'Breakout'
    tradeOnPullback = tradeType == 'Pullback'
    tradeOnRetest = tradeType == 'Pullback-Breakout'
    tradeOnAny = tradeType == 'Any'
    strategy.risk.allow_entry_in(tradeDirection)
    upper: float = 0.0
    lower: float = 0.0
    middle: float = 0.0
    @overload
    def unshift(zigzag: list[Pivot], p: Pivot):
        if array.size(zigzag) > 1:
            lastPivot = array.get(zigzag, 0)
            llastPivot = array.get(zigzag, 1)
            p.direction = p.direction * 2 if p.price * p.direction > llastPivot.price * p.direction else p.direction
            p.ratio = math.abs(p.price - lastPivot.price) / math.abs(llastPivot.price - lastPivot.price)
        array.unshift(zigzag, p)
        __block_result__ = na
        if array.size(zigzag) > 15:
            __block_result__ = array.pop(zigzag)
        return __block_result__

    def shift(drawings: list[Drawing]):
        del__ren__ = array.shift(drawings)
        line.delete(del__ren__.zigzagLine)
        return label.delete(del__ren__.zigzagLabel)

    @overload
    def unshift(drawings: list[Drawing], drawing: Drawing, maxItems: int):
        array.unshift(drawings, drawing)
        __block_result_1__ = na
        if array.size(drawings) > maxItems:
            del__ren__ = array.pop(drawings)
            line.delete(del__ren__.zigzagLine)
            __block_result_1__ = label.delete(del__ren__.zigzagLabel)
        return __block_result_1__

    if bandType == 'Bollinger Bands':
        bmiddle, bupper, blower = eta.bb(close, maType, maLength, multiplier, sticky)
        upper = bupper
        lower = blower
        middle = bmiddle
    if bandType == 'Keltner Channel':
        kmiddle, kupper, klower = eta.kc(close, maType, maLength, multiplier, useTrueRange, sticky)
        upper = kupper
        lower = klower
        middle = kmiddle
    if bandType == 'Donchian Channel':
        dmiddle, dupper, dlower = eta.dc(maLength, False, close, sticky)
        upper = dupper
        lower = dlower
        middle = dmiddle
    zigzag: Persistent[list[Pivot]] = array.new(0, NA(Pivot))
    trend: Persistent[int] = 0
    currentTrend: Persistent[int] = 0
    currentDir: Persistent[int] = 0
    currentTrendForce: Persistent[int] = 0
    currentTrendExtreme: Persistent[int] = 0
    if array.size(zigzag) > 1:
        recentPivot = array.get(zigzag, 0)
        lastPivot = array.get(zigzag, 1)
        currentDir = recentPivot.direction
        currentTrend = cast_int(math.sign(recentPivot.direction)) if recentPivot.ratio > recentPivot.percentB else -cast_int(math.sign(recentPivot.direction))
        trend = cast_int(math.sign(lastPivot.direction)) if lastPivot.ratio > lastPivot.percentB else -cast_int(math.sign(lastPivot.direction))
        currentTrendForce = cast_int(math.sign(recentPivot.direction)) if recentPivot.ratio > recentPivot.percentB and recentPivot.ratio > currentTrendInvalidationMultiplier else -cast_int(math.sign(recentPivot.direction))
    uupper: Persistent = nz(upper)
    llower: Persistent = nz(lower)
    uupper = upper if currentDir >= 0 or not useAdaptive else math.min(upper, uupper)
    llower = lower if currentDir <= 0 or not useAdaptive else math.max(lower, llower)
    percentBHigh = (high - llower) / (uupper - llower)
    percentBLow = (uupper - low) / (uupper - llower)
    def addPivot(zigzag, direction__00000049__):
        lastRemoved: bool = False
        price = high if direction__00000049__ > 0 else low
        percentB = percentBHigh if direction__00000049__ > 0 else percentBLow
        p: Pivot = Pivot(price, bar_index, time, cast_int(direction__00000049__), percentB)
        if array.size(zigzag) == 0:
            unshift(zigzag, p)
        else:
            lastPivot = array.get(zigzag, 0)
            lastPivotDirection = math.sign(lastPivot.direction)
            if lastPivotDirection != p.direction:
                unshift(zigzag, p)
            if lastPivotDirection == p.direction and lastPivot.price * direction__00000049__ < p.price * direction__00000049__:
                array.remove(zigzag, 0)
                unshift(zigzag, p)
                lastRemoved = True
        return lastRemoved

    def add_pivots(zigzag, pHigh, pLow):
        count: int = 0
        removeLast: bool = False
        if array.size(zigzag) == 0:
            if pHigh:
                addPivot(zigzag, 1)
                count = count + 1
            if pLow:
                addPivot(zigzag, -1)
                count = count + 1
        else:
            lastPivot = array.get(zigzag, 0)
            lastDir = math.sign(lastPivot.direction)
            if pHigh and lastDir == 1 or (pLow and lastDir == -1):
                removeLast = addPivot(zigzag, lastDir)
                count = count + 1 if removeLast else count
            if pHigh and lastDir == -1 or (pLow and lastDir == 1):
                addPivot(zigzag, -lastDir)
                count = count + 1
        return (count, removeLast)

    def draw_zigzag(zigzag, count, removeLast):
        zigzagDrawings: Persistent[list[Drawing]] = array.new(0, NA(Drawing))
        if removeLast and array.size(zigzagDrawings) > 0:
            shift(zigzagDrawings)
        if array.size(zigzag) > count and count >= 1:
            for i in pine_range(count, 1, 1):
                startPivot = array.get(zigzag, count)
                endPivot = array.get(zigzag, count - 1)
                startDirection = startPivot.direction
                endDirection = endPivot.direction
                lineColor = color.green if endDirection == 2 else color.red if endDirection == -2 else color.silver
                txt = string.tostring(endPivot.ratio * 100, format.percent) + '/' + string.tostring(endPivot.percentB * 100, format.percent)
                ln = line.new(startPivot.bartime, startPivot.price, endPivot.bartime, endPivot.price, xloc.bar_time, color=lineColor, width=2)
                lbl = label.new(endPivot.bartime, endPivot.price, txt, xloc.bar_time, yloc.price, lineColor, label.style_label_down if endPivot.direction > 0 else label.style_label_up, textcolor=color.black)
                dr: Drawing = Drawing(ln, lbl)
                unshift(zigzagDrawings, dr, 500)
        return zigzagDrawings

    pHigh = high >= uupper
    pLow = low <= llower
    count, removeLast = add_pivots(zigzag, pHigh, pLow)
    draw_zigzag(zigzag, count, removeLast)
    plot(uupper if showBands else na, 'Upper', color.green, math.max(1, 0), plot.style_linebr)
    plot(llower if showBands else na, 'Lower', color.red, math.max(1, 0), plot.style_linebr)
    combinedTrend: Persistent[int] = 0
    combinedTrend = 1 if trend > 0 or (useLatestPivot and currentTrendForce > 0) else -1 if trend < 0 or (useLatestPivot and currentTrendForce < 0) else combinedTrend
    candleColor = color.green if combinedTrend > 0 else color.red if combinedTrend < 0 else color.silver
    plot(trend, 'Last Pivot Trend', color.green if trend > 0 else color.red if trend < 0 else color.silver, display=display.data_window)
    plot(currentTrend, 'Current Pivot Trend', color.green if currentTrend > 0 else color.red if currentTrend < 0 else color.silver, display=display.data_window)
    plot(currentTrendForce, 'Force Trend', color.green if currentTrendForce > 0 else color.red if currentTrendForce < 0 else color.silver, display=display.data_window)
    plot(combinedTrend, 'Combined Trend', candleColor, display=display.data_window)
    plot(currentDir, 'Current Direction', color=color.green if currentDir > 0 else color.red if currentDir < 0 else color.silver, display=display.data_window)
    allowEntry: Persistent[bool] = False
    crossunder_1 = ta.crossunder(combinedTrend, 0)
    allowEntry = True if ta.crossover(combinedTrend, 0) or crossunder_1 else allowEntry
    if combinedTrend > 0:
        strategy.close('Short')
        if (tradeOnBreakout and currentDir > 0 or (tradeOnPullback and currentDir < 0) or tradeOnAny or (currentTrend > 0 and trend > 0 and (currentDir > 0) and tradeOnRetest)) and allowEntry:
            allowEntry = False
            strategy.entry('Long', strategy.long)
            if useStopLoss:
                strategy.exit('ExitLong', 'Long', stop=low - (uupper - llower))
    if combinedTrend < 0:
        strategy.close('Long')
        if (tradeOnBreakout and currentDir < 0 or (tradeOnPullback and currentDir > 0) or tradeOnAny or (currentTrend < 0 and trend < 0 and (currentDir < 0) and tradeOnRetest)) and allowEntry:
            allowEntry = False
            strategy.entry('Short', strategy.short)
            if useStopLoss:
                strategy.exit('ExitShort', 'Short', stop=high + uupper - llower)
    if combinedTrend == 0:
        strategy.close_all()
    plot(1 if allowEntry else 0, 'Allow Entry', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
