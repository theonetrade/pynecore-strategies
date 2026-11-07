"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, close, color, display, high, input, low, math, na, nz, open, plot,
    script, strategy, ta
)
from pynecore.types import Persistent, PersistentSeries
import lib.HeWhoMustNotBeNamed.arrayutils.v22 as pa
import lib.HeWhoMustNotBeNamed.ta.v1 as eta


@script.strategy('Master Supertrend Strategy [Trendoscope]', 'MSTS [Trendoscope]', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.05, close_entries_rule='ANY', margin_long=100, margin_short=100, max_lines_count=500, max_labels_count=500, max_boxes_count=500, use_bar_magnifier=False, close_by_id=True)
def main(
    supertrendType=input.string('Plus/Minus Range', 'Range Type', options=('Plus/Minus Range', 'Ladder TR', 'True Range', 'Standard Deviation'), tooltip='Type of range used for supertrend calculation'),
    rangeType=input.string('high', 'Applied Calculation', options=('sma', 'ema', 'hma', 'rma', 'wma', 'high', 'median'), tooltip='Applied calculation method on the range before using them for calculation of supertrend stops'),
    length=input.int(60, 'Length', minval=10, maxval=1000, step=10, tooltip='Supertrend range calculation length'),
    multiplier=input.int(2, 'Multiplier', minval=2, maxval=100, step=1, tooltip='Supertrend range multiplier'),
    useClosePrices=input.bool(True, 'Use Close Price', tooltip='Use close price as reference instad of high/low for calculation of stop'),
    waitForClose=input.bool(True, 'Wait for Close', tooltip='Wait for close before changing the direction and change direction only if close price has breached the stop line'),
    useDiminishingRange=input.bool(True, 'Diminishing Stop Distance', tooltip='When selected stop distance from reference price can only decrease and not increase')
):
    ladderPositiveAtr: float = na(float)
    ladderNegativeAtr: float = na(float)
    if supertrendType == 'Ladder TR':
        plusLadderAtr: Persistent[list[float]] = array.new_float()
        minusLadderAtr: Persistent[list[float]] = array.new_float()
        if open < close:
            pa.push(plusLadderAtr, ta.tr, length)
        else:
            pa.push(minusLadderAtr, ta.tr, length)
        ladderPositiveAtr = pa.ma(plusLadderAtr, rangeType, length)
        ladderNegativeAtr = pa.ma(minusLadderAtr, rangeType, length)
    plusRange = math.max(high - open, high - close[1]) if supertrendType == 'Plus/Minus Range' else ladderPositiveAtr if supertrendType == 'Ladder TR' else ta.tr if supertrendType == 'True Range' else ta.stdev(close, length, True)
    minusRange = math.max(open - low, close[1] - low) if supertrendType == 'Plus/Minus Range' else ladderNegativeAtr if supertrendType == 'Ladder TR' else ta.tr if supertrendType == 'True Range' else ta.stdev(close, length, True)
    appliedPlusRange = plusRange if supertrendType == 'Ladder TR' else eta.ma(plusRange, rangeType, length)
    appliedMinusRange = minusRange if supertrendType == 'Ladder TR' else eta.ma(minusRange, rangeType, length)
    direction: PersistentSeries[int] = 1
    derivedPlusRange: Persistent = appliedPlusRange * multiplier
    derivedMinusRange: Persistent = appliedMinusRange * multiplier
    currentDerivedPlusRange = appliedPlusRange * multiplier
    derivedPlusRange = math.min(nz(derivedPlusRange, currentDerivedPlusRange), currentDerivedPlusRange) if direction < 0 and useDiminishingRange else currentDerivedPlusRange
    currentDerivedMinusRange = appliedMinusRange * multiplier
    derivedMinusRange = math.min(nz(derivedMinusRange, currentDerivedMinusRange), currentDerivedMinusRange) if direction > 0 and useDiminishingRange else currentDerivedMinusRange
    buyStopCurrent = (close if useClosePrices else low) - derivedMinusRange
    buyStop: Persistent = buyStopCurrent
    sellStopCurrent = (close if useClosePrices else high) + derivedPlusRange
    sellStop: Persistent = sellStopCurrent
    buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if direction > 0 else buyStopCurrent
    sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if direction < 0 else sellStopCurrent
    direction = -1 if direction > 0 and (close if waitForClose else low) < buyStop else 1 if direction < 0 and (close if waitForClose else high) > sellStop else direction
    supertrend = buyStop if direction[1] > 0 else sellStop
    plot(supertrend, 'Supertrend', color.red if direction[1] > 0 else color.green)
    plot(direction, 'direction', display=display.data_window)
    plot(strategy.equity, 'Equity', display=display.data_window)
    plot(strategy.openprofit, 'Open Profit', display=display.data_window)
    plot(strategy.opentrades, 'Open Trades', display=display.data_window)
    if direction > 0:
        strategy.entry('Long', strategy.long)
    if direction < 0:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
