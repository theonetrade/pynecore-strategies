"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    barstate, close, color, dayofmonth, format, high, hline, input, low,
    month, na, nz, plot, plotcandle, runtime, script, string, ta, time, timeframe, timestamp,
    volume, year
)
from pynecore.types import Persistent
import lib.TradingView.ta.v12 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

dataAggregationTooltip: str = "Defines how lower timeframe data is aggregated for the delta calculation. \"1 tick\" computes the delta on tick data and is available only on expert plans."
lowerTimeframeTooltip = 'The indicator scans lower timeframe data to approximate up and down volume used in the delta calculation. By default, the timeframe is chosen automatically. These inputs override this with a custom timeframe.' + ' \n\nHigher timeframes provide more historical data, but the data will be less precise.'


@script.indicator("Cumulative Volume Delta + VWAP + EMA & Volume OWI By ADK", "ADK CVD", format=format.volume)
def main(
    anchorInput=input.timeframe("1D", "Anchor Period", group="CVD Settings"),
    dataAggregationInput=input.string("Time", "Data Aggregation", options=("Time", "1 tick"), tooltip=dataAggregationTooltip, group="CVD Settings"),
    useCustomTimeframeInput=input.bool(True, "Custom timeframe", tooltip=lowerTimeframeTooltip, group="CVD Settings"),
    lowerTimeframeInput=input.timeframe("", "Timeframe", group="CVD Settings"),
    showCvdVwapInput=input.bool(False, "Show CVD VWAP", group="CVD VWAP"),
    showMaInput=input.bool(False, "Show CVD EMA", group="CVD EMA"),
    maLengthInput=input.int(20, "EMA Length", minval=1, group="CVD EMA"),
    showVOWI=input.bool(False, "Show Vol-OWI", group="VOWI Settings"),
    smaLength=input.int(20, "SMA Length", group="VOWI Settings"),
    useTimeFilter=input.bool(True, "Enable Time Filter", group="VOWI Settings"),
    startHour=input.int(9, "Start Hour (ET)", group="VOWI Settings"),
    startMinute=input.int(45, "Start Minute (ET)", group="VOWI Settings"),
    endHour=input.int(16, "End Hour (ET)", group="VOWI Settings"),
    endMinute=input.int(15, "End Minute (ET)", group="VOWI Settings")
):
    useTicks = dataAggregationInput == '1 tick'

    __block_result__ = na
    if useTicks:
        __block_result__ = "1T"
    elif useCustomTimeframeInput:
        __block_result__ = lowerTimeframeInput
    elif timeframe.isseconds:
        __block_result__ = "1S"
    elif timeframe.isintraday:
        __block_result__ = "1"
    elif timeframe.isdaily:
        __block_result__ = "5"
    else:
        __block_result__ = "60"
    lowerTimeframe: Persistent = __block_result__

    openVolume, maxVolume, minVolume, lastVolume = ta__ren__.requestVolumeDelta(lowerTimeframe, anchorInput)

    col = color.blue if lastVolume >= openVolume else color.red
    hline(0)
    plotcandle(openVolume, maxVolume, minVolume, lastVolume, 'CVD', color=col, bordercolor=col, wickcolor=col)

    newSession = timeframe.change('1D')

    vwapNumSession: Persistent[float] = 0.0
    vwapDenSession: Persistent[float] = 0.0
    if newSession:
        vwapNumSession = 0.0
        vwapDenSession = 0.0
    if not na(lastVolume) and (not na(volume)):
        vwapNumSession += lastVolume * volume
        vwapDenSession += volume
    cvdVwap = vwapNumSession / vwapDenSession if vwapDenSession > 0 else na

    plot(cvdVwap if showCvdVwapInput else na, 'CVD VWAP', color=color.new(color.black, 0), linewidth=2)

    cvdEma = ta__ren__.ema(lastVolume, maLengthInput)

    plot(cvdEma if showMaInput else na, 'CVD EMA', color=color.new(color.fuchsia, 0), linewidth=1)

    cumVol: Persistent[float] = 0.0
    cumVol += nz(volume)
    deltaIsNa = na(openVolume) and na(maxVolume) and na(minVolume) and na(lastVolume)
    if barstate.islast:
        if cumVol == 0:
            runtime.error("The data vendor doesn't provide volume data for this symbol.")
        if string.endswith(lowerTimeframe, 'T') and deltaIsNa:
            runtime.error('Not enough tick depth for the current anchor period. The available tick depth ends before reaching the start of the anchor period (' + anchorInput + "). Please shorten the 'Anchor period' input or switch the calculation base from '1 Tick' to 'Time' or higher custom timeframe.")

    buyVolume = 0.0 if high == low else volume * (close - low) / (high - low)
    sellVolume = 0.0 if high == low else volume * (high - close) / (high - low)

    startTime = timestamp('America/New_York', year, month, dayofmonth, startHour, startMinute)
    endTime = timestamp('America/New_York', year, month, dayofmonth, endHour, endMinute)
    isUSMarketTime = time >= startTime and time <= endTime

    plot(volume if showVOWI else na, 'SELL V', color=color.red, style=plot.style_columns)
    plot(buyVolume if showVOWI else na, 'BUY V', color=color.green, style=plot.style_columns)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
