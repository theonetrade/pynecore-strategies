"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, barmerge, barstate, close, color, dividends, earnings, fill,
    hl2, hlc3, input, na, plot, request, runtime, script, splits, strategy, syminfo, ta, timeframe,
    volume, year
)
from pynecore.types import Persistent, Series
import lib.wbburgin.wbburgin_utils.v2 as utils


@script.strategy(title='VWAP Trendfollow Strategy [wbburgin]', shorttitle='VWAP Trendfollow [wbburgin]', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=3, initial_capital=1000, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0.025, margin_long=0, margin_short=0, close_by_id=True)
def main(
    hideonDWM=input(False, title='Hide VWAP on 1D or Above', group='VWAP Settings'),
    anchor__input=input.string(defval='Session', title='Anchor Period', options=('Session', 'Week', 'Month', 'Quarter', 'Year', 'Decade', 'Century', 'Earnings', 'Dividends', 'Splits'), group='VWAP Settings'),
    src: Series[float] = input(title='Source', defval=hlc3, group='VWAP Settings'),
    offset=input(0, title='Offset', group='VWAP Settings'),
    showBand_1=input(True, title='', group='Standard Deviation Bands Settings', inline='band_1'),
    stdevMult_1=input(0.88, title='Standard Deviation Multiplier', group='Standard Deviation Bands Settings', inline='band_1'),
    matchedTrends=input.bool(True, 'Only Enter on Matched Trends', tooltip='This setting will only enter a long trade' + ' when the VWAP is trending up and will only enter a short trade when the VWAP is trending down.', group='Strategy'),
    displaybars=input.bool(True, 'Barcolors', group='Display')
):
    anchor: Persistent = anchor__input
    cum_1 = ta.cum(volume)
    if barstate.islast and cum_1 == 0:
        runtime.error('No volume is provided by the data vendor.')
    new_earnings = request.earnings(syminfo.tickerid, earnings.actual, barmerge.gaps_on, barmerge.lookahead_on, ignore_invalid_symbol=True)
    new_dividends = request.dividends(syminfo.tickerid, dividends.gross, barmerge.gaps_on, barmerge.lookahead_on, ignore_invalid_symbol=True)
    new_split = request.splits(syminfo.tickerid, splits.denominator, barmerge.gaps_on, barmerge.lookahead_on, ignore_invalid_symbol=True)
    __block_result__ = na
    __switch__ = anchor
    if __switch__ == 'Earnings':
        __block_result__ = not na(new_earnings)
    elif __switch__ == 'Dividends':
        __block_result__ = not na(new_dividends)
    elif __switch__ == 'Splits':
        __block_result__ = not na(new_split)
    elif __switch__ == 'Session':
        __block_result__ = timeframe.change('D')
    elif __switch__ == 'Week':
        __block_result__ = timeframe.change('W')
    elif __switch__ == 'Month':
        __block_result__ = timeframe.change('M')
    elif __switch__ == 'Quarter':
        __block_result__ = timeframe.change('3M')
    elif __switch__ == 'Year':
        __block_result__ = timeframe.change('12M')
    elif __switch__ == 'Decade':
        __block_result__ = timeframe.change('12M') and year % 10 == 0
    elif __switch__ == 'Century':
        __block_result__ = timeframe.change('12M') and year % 100 == 0
    else:
        __block_result__ = False
    isNewPeriod = __block_result__
    isEsdAnchor = anchor == 'Earnings' or anchor == 'Dividends' or anchor == 'Splits'
    if na(src[1]) and (not isEsdAnchor):
        isNewPeriod = True
    vwapValue: float = na(float)
    upperBandValue1: float = na(float)
    lowerBandValue1: float = na(float)
    upperBandValue2: float = na(float)
    lowerBandValue2: float = na(float)
    if not (hideonDWM and timeframe.isdwm):
        _vwap, _stdevUpper, _ = ta.vwap(src, isNewPeriod, 1)
        vwapValue = _vwap
        stdevAbs = _stdevUpper - _vwap
        upperBandValue1 = _vwap + stdevAbs * stdevMult_1
        lowerBandValue1 = _vwap - stdevAbs * stdevMult_1
        upperBandValue2 = _vwap + 2 * stdevAbs * stdevMult_1
        lowerBandValue2 = _vwap - 2 * stdevAbs * stdevMult_1
    vTopBreak = ta.crossover(close, upperBandValue1)
    vBottomBreak = ta.crossunder(close, lowerBandValue1)
    inLongTrade = ta.barssince(vTopBreak) < ta.barssince(vBottomBreak)
    upV = utils.trendUp(vwapValue)
    matchedTrendsFilter_long = True if not matchedTrends else cast_bool(upV)
    matchedTrendsFilter_short = True if not matchedTrends else not upV
    b_vwap = vTopBreak and matchedTrendsFilter_long
    s_vwap = vBottomBreak and matchedTrendsFilter_short
    takeprofit_long = ta.crossunder(close, upperBandValue2)
    takeprofit_short = ta.crossover(close, lowerBandValue2)
    if b_vwap:
        strategy.entry('Long', strategy.long)
    if s_vwap:
        strategy.entry('Short', strategy.short)
    if takeprofit_long:
        strategy.close('Long')
    if takeprofit_short:
        strategy.close('Short')
    plot(vwapValue, title='VWAP', color=color.white, offset=offset)
    upperBand_1 = plot(upperBandValue1, title='Upper Band #1', color=na, offset=offset)
    lowerBand_1 = plot(lowerBandValue1, title='Lower Band #1', color=na, offset=offset)
    plot(upperBandValue2, color=color.lime)
    plot(lowerBandValue2, color=color.red)
    hl2_plot = plot(hl2, color=na, title='HL2')
    fill(hl2_plot, upperBand_1, color=color.new(color.green, 50) if hl2 > upperBandValue1 else na)
    fill(hl2_plot, lowerBand_1, color=color.new(color.red, 50) if hl2 < lowerBandValue1 else na)
    fill(upperBand_1, lowerBand_1, title='Bands Fill', color=color.new(color.lime, 88) if cast_bool(upV) else color.new(color.red, 88))
    barcolor((color.lime if inLongTrade else color.red) if displaybars == True else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
