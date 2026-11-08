"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, display, fill, input, na, open, plot, request, script,
    syminfo, ta
)
from pynecore.types import Color, Persistent, Series
from typing import Protocol, Any
import lib.jason5480.series_collection.v4 as col
import lib.jason5480.tts_convention.v7 as conv


__all__ = ['TwoMaDrawings', 'getDealConditions']


@udt
class TwoMaDrawings:
    fastMA: float = na(float)
    slowMA: float = na(float)
    emaLine: float = na(float)
    emaUpperBand: float = na(float)
    emaLowerBand: float = na(float)


class _ProtocolGetdealconditions(Protocol):
    def __call__(self, drawings: TwoMaDrawings, longDealsEnabled: bool, shortDealsEnabled: bool, endDealsEnabled: bool, cnlStartDealsEnabled: bool, cnlEndDealsEnabled: bool, emaFilterEnabled: bool, emaAtrBandEnabled: bool, adxFilterEnabled: bool, adxSmoothing: int, diLength: int, adxThreshold: float) -> Any: ...


getDealConditions: _ProtocolGetdealconditions = Exported()


MA_GROUP_NAME: str = 'Moving Averages'
DEALS_GROUP_NAME: str = 'Deal Conditions'
FILTERS_GROUP_NAME: str = 'Filters'


@script.library(title='two_ma_logic')
def main(
    fastMaType=input.enum(defval=col.SeriesType.sma, title='Fast MA Type/Len       ', options=(col.SeriesType.alma, col.SeriesType.dema, col.SeriesType.ema, col.SeriesType.hma, col.SeriesType.rma, col.SeriesType.sma, col.SeriesType.swma, col.SeriesType.vwma, col.SeriesType.wma, col.SeriesType.linreg, col.SeriesType.median), inline='Fast MA', group=MA_GROUP_NAME, display=display.data_window),
    fastMaLength=input.int(defval=21, title='', minval=1, tooltip='The type and the length of the fast MA.', inline='Fast MA', group=MA_GROUP_NAME, display=display.data_window),
    slowMaType=input.enum(defval=col.SeriesType.sma, title='Slow MA Type/Len       ', options=(col.SeriesType.alma, col.SeriesType.dema, col.SeriesType.ema, col.SeriesType.hma, col.SeriesType.rma, col.SeriesType.sma, col.SeriesType.swma, col.SeriesType.vwma, col.SeriesType.wma, col.SeriesType.linreg, col.SeriesType.median), inline='Slow MA', group=MA_GROUP_NAME, display=display.data_window),
    slowMaLength=input.int(defval=49, title='', minval=1, tooltip='The type and the length of the slow MA.', inline='Slow MA', group=MA_GROUP_NAME, display=display.data_window),
    longDealsEnabled=input.bool(defval=True, title='Long Deals', inline='Long/Short Deals', group=DEALS_GROUP_NAME, display=display.data_window),
    shortDealsEnabled=input.bool(defval=True, title='Short Deals', tooltip='Enable long/short start/end/cancel deals. An open signal will be emitted when the long/short start deal conditions are met. If this option is unchecked you will not enter into long/short positions.', inline='Long/Short Deals', group=DEALS_GROUP_NAME, display=display.data_window),
    endDealsEnabled=input.bool(defval=False, title='End Deals', tooltip='Enable end deals. A close signal will be emitted when the end deal conditions are met. If this option is unchecked you will not exit your existing position based on the strategy logic. You will exit only when the stop loss or the take profit targets are reached.', group=DEALS_GROUP_NAME, display=display.data_window),
    cnlStartDealsEnabled=input.bool(defval=True, title='Cancel Start Deals', inline='Start/End Deals', group=DEALS_GROUP_NAME, display=display.data_window),
    cnlEndDealsEnabled=input.bool(defval=True, title='Cancel End Deals', tooltip='Enable cancel start/end deals. A cancel start/close signal will be emitted when the cancel start/end deal conditions are met. If this option is unchecked you will not cancel your entry/exit order based on the strategy logic when use limit, stop or stop-limit orders.', inline='Start/End Deals', group=DEALS_GROUP_NAME, display=display.data_window),
    emaFilterEnabled=input.bool(defval=True, title='EMA Filter', tooltip='Enable long/short trades based on EMA.', group=FILTERS_GROUP_NAME, display=display.data_window),
    emaTimeframe=input.timeframe(defval='', title='  EMA Res/Len/Src', inline='EMA Filter', group=FILTERS_GROUP_NAME, display=display.data_window),
    emaLength=input.int(defval=200, title='', minval=1, inline='EMA Filter', group=FILTERS_GROUP_NAME, display=display.data_window),
    emaSrc: Series[float] = input.source(defval=close, title='', tooltip='The timeframe, period and source for the EMA calculation.', inline='EMA Filter', group=FILTERS_GROUP_NAME, display=display.data_window),
    emaAtrBandEnabled=input.bool(defval=True, title='EMA ATR Band', tooltip='Enable ATR band for EMA filter.', group=FILTERS_GROUP_NAME, display=display.data_window),
    filterAtrMul=input.float(defval=1.0, title='  EMA ATR Mul/Len', minval=0.1, step=0.1, inline='EMA ATR', group=FILTERS_GROUP_NAME, display=display.data_window),
    filterAtrLength=input.int(defval=5, title='', minval=1, tooltip='ATR multiplier and length to be used for the ATR calculation that will be added on top of the EMA filter.', inline='EMA ATR', group=FILTERS_GROUP_NAME, display=display.data_window),
    adxFilterEnabled=input.bool(defval=False, title='ADX Filter', tooltip='Enable long/short trades based on ADX.', group=FILTERS_GROUP_NAME, display=display.data_window),
    adxSmoothing=input.int(defval=14, title='  Smooth/DI Len', minval=1, inline='ADX Filter', group=FILTERS_GROUP_NAME, display=display.data_window),
    diLength=input.int(defval=14, title='', minval=1, tooltip='ADX Smoothing length and Direction Length.', inline='ADX Filter', group=FILTERS_GROUP_NAME, display=display.data_window),
    adxThreshold=input.float(defval=20.0, title='  Threshold', minval=0.1, maxval=100.0, step=5.0, tooltip='ADX lower threshold.', group=FILTERS_GROUP_NAME, display=display.data_window)
):
    @export
    def getDealConditions(drawings: TwoMaDrawings, longDealsEnabled: bool, shortDealsEnabled: bool, endDealsEnabled: bool, cnlStartDealsEnabled: bool, cnlEndDealsEnabled: bool, emaFilterEnabled: bool, emaAtrBandEnabled: bool, adxFilterEnabled: bool, adxSmoothing: int, diLength: int, adxThreshold: float):
        emaLongApproval: Persistent[bool] = True
        emaShortApproval: Persistent[bool] = True
        if emaFilterEnabled:
            emaLongLine: float = drawings.emaUpperBand if emaAtrBandEnabled else drawings.emaLine
            emaShortLine: float = drawings.emaLowerBand if emaAtrBandEnabled else drawings.emaLine
            emaLongApproval = close > emaLongLine and open > emaLongLine
            emaShortApproval = close < emaShortLine and open < emaShortLine

        _, _, adx = ta.dmi(diLength, adxSmoothing)
        adxApproval: bool = adx > adxThreshold if adxFilterEnabled else True

        longFiltersApproval: Series[bool] = emaLongApproval and adxApproval
        shortFiltersApproval: Series[bool] = emaShortApproval and adxApproval

        crossover: bool = ta.crossover(drawings.fastMA, drawings.slowMA)
        crossunder: bool = ta.crossunder(drawings.fastMA, drawings.slowMA)

        return conv.DealConditions.new(startLongDeal=crossover and longFiltersApproval if longDealsEnabled else False, startShortDeal=crossunder and shortFiltersApproval if shortDealsEnabled else False, endLongDeal=crossunder if endDealsEnabled and longDealsEnabled else False, endShortDeal=crossover if endDealsEnabled and shortDealsEnabled else False, cnlStartLongDeal=not longFiltersApproval and longFiltersApproval[1] if cnlStartDealsEnabled and longDealsEnabled else False, cnlStartShortDeal=not shortFiltersApproval and shortFiltersApproval[1] if cnlStartDealsEnabled and shortDealsEnabled else False, cnlEndLongDeal=longFiltersApproval and (not longFiltersApproval[1]) if cnlEndDealsEnabled and endDealsEnabled and longDealsEnabled else False, cnlEndShortDeal=shortFiltersApproval and (not shortFiltersApproval[1]) if cnlEndDealsEnabled and endDealsEnabled and shortDealsEnabled else False)



    emaLine: float = request.security(symbol=syminfo.tickerid, timeframe=emaTimeframe, expression=inline_series(ta.ema(emaSrc, emaLength), 1)) if emaFilterEnabled else na
    emaAtr: float = filterAtrMul * ta.atr(filterAtrLength)
    twoMaDrawings: TwoMaDrawings = TwoMaDrawings(fastMA=col.cust_series(fastMaLength, fastMaType), slowMA=col.cust_series(slowMaLength, slowMaType), emaLine=emaLine, emaUpperBand=emaLine + emaAtr, emaLowerBand=emaLine - emaAtr)
    dealConditions = getDealConditions(twoMaDrawings, longDealsEnabled, shortDealsEnabled, endDealsEnabled, cnlStartDealsEnabled, cnlEndDealsEnabled, emaFilterEnabled, emaAtrBandEnabled, adxFilterEnabled, adxSmoothing, diLength, adxThreshold)

    plot(series=twoMaDrawings.emaLine, color=color.silver, style=plot.style_linebr, linewidth=2, title='EMA Line', display=display.all - display.status_line if emaFilterEnabled else display.none, force_overlay=True)
    EMA_BAND_FILL_COLOR: Color = color.new(color.silver, 90) if emaFilterEnabled and emaAtrBandEnabled else na
    emaUpperBandPlot = plot(series=twoMaDrawings.emaUpperBand, color=EMA_BAND_FILL_COLOR, style=plot.style_linebr, title='EMA Upper Band', display=display.data_window, force_overlay=True)
    emaLowerBandPlot = plot(series=twoMaDrawings.emaLowerBand, color=EMA_BAND_FILL_COLOR, style=plot.style_linebr, title='EMA Lower Band', display=display.data_window, force_overlay=True)
    fill(plot1=emaUpperBandPlot, plot2=emaLowerBandPlot, color=EMA_BAND_FILL_COLOR, title='EMA Band')

    plot(series=twoMaDrawings.fastMA, title='Fast MA', color=color.yellow, linewidth=1, style=plot.style_line, display=display.all - display.status_line, force_overlay=True)
    plot(series=twoMaDrawings.slowMA, title='Slow MA', color=color.orange, linewidth=1, style=plot.style_line, display=display.all - display.status_line, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
