"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barcolor, close, color, display, fill, high, input,
    low, math, na, nz, open, order, plot, plotcandle, script, syminfo, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

G: str = "SPMA Settings"
G2: str = "Volatility"
G3: str = "Slope Gate"


@script.indicator("SPMA Trend | NAL", "SPMA Trend", overlay=True)
def main(
    col_mode=input.string("Standard", title="Color Mode", group="Visuals", options=("Standard", "Nordic", "Simple")),
    Length=input.int(30, "Baseline Length", group=G),
    Lookback=input.int(30, "Percentrank Lookback", minval=2, tooltip="Number of historical bars used to rank the current returns. Lower values react faster but produce a less stable rank. Higher values compare the current shock against a broader historical sample.", group=G),
    GateInp=input.int(50, "% Gate", minval=0, maxval=99, tooltip="Minimum percentile rank required for the SPMA to update. A value of 50 updates on above-median positive price shocks, while higher values restrict updates to increasingly unusual shocks. When the gate is not met, the SPMA holds its previous value.", group=G),
    useAsymBands=input.bool(False, "Use Asymmetric Bands?", group=G2, tooltip="Applies separate bullish and bearish shock multipliers to SD, ATR, MeanAD and MedianAD volatility. Quantile volatility is already asymmetric and therefore does not use this setting."),
    VolFeed=input.string("MeanAD", "Volatility Method", options=("SD", "ATR", "MeanAD", "MedianAD", "Quantile"), group=G2),
    VolLen=input.int(14, "Volatility Length", minval=2, group=G2),
    VolMul=input.float(0.75, "Volatility Multiple", minval=0.0, step=0.1, group=G2),
    QuantilePct=input.float(90.0, "Quantile Percentile", minval=50.0, maxval=99.0, step=1.0, tooltip="Percentile of positive and negative SPMA residual magnitudes used to construct Quantile bands. Higher values produce wider bands based on increasingly extreme historical deviations from the SPMA.", group=G2),
    UseSlope=input.bool(True, "Use Slope Gate?", tooltip="Requires the SPMA percentage slope to exceed the Slope Gate before a bullish state can activate. When disabled, any upward SPMA movement can produce a bullish state. The bearish condition is not affected by this setting.", group=G3),
    SlopeLen=input.int(10, "Slope Lookback (bars)", group=G3),
    SlopeGateL=input.float(0.5, "% Slope Gate", step=0.1, group=G3)
):
    __block_result__ = (na, na, na)
    __switch__ = col_mode
    if __switch__ == "Standard":
        __block_result__ = (color.rgb(0, 255, 200), color.rgb(32, 94, 144), color.gray)
    elif __switch__ == "Nordic":
        __block_result__ = (color.rgb(0, 96, 175), color.rgb(150, 154, 169), color.gray)
    elif __switch__ == "Simple":
        __block_result__ = (color.lime, color.red, color.gray)
    col_up, col_dn, col_nu = __block_result__

    def f_array_median(values: list[float]):
        array.sort(values, order.ascending)
        size__ren__: int = array.size(values)
        mid: int = cast_int(math.floor(size__ren__ / 2))
        return na if size__ren__ == 0 else array.get(values, mid) if size__ren__ % 2 == 1 else math.avg(array.get(values, mid - 1), array.get(values, mid))

    def f_median_ad(source: Series[float], length: int):
        values: list[float] = array.new_float(0)
        for i in pine_range(0, length - 1):
            if not na(source[i]):
                array.push(values, source[i])

        medianValue: float = f_array_median(values)

        deviations: list[float] = array.new_float(0)
        for i in pine_range(0, length - 1):
            if not na(source[i]) and (not na(medianValue)):
                array.push(deviations, math.abs(source[i] - medianValue))

        return f_array_median(deviations)

    def f_array_quantile(values: list[float], percentile: float):
        array.sort(values, order.ascending)
        size__ren__: int = array.size(values)

        __block_result_1__ = na
        if size__ren__ == 0:
            __block_result_1__ = na
        else:
            rank: float = percentile / 100.0 * (size__ren__ - 1)
            lowerIndex: int = cast_int(math.floor(rank))
            upperIndex: int = cast_int(math.ceil(rank))
            weight: float = rank - lowerIndex
            lowerValue: float = array.get(values, lowerIndex)
            upperValue: float = array.get(values, upperIndex)
            __block_result_1__ = lowerValue + (upperValue - lowerValue) * weight
        return __block_result_1__

    def f_quantile_volatility(residual: Series[float], length: int, percentile: float):
        upperValues: list[float] = array.new_float(0)
        lowerValues: list[float] = array.new_float(0)
        allValues: list[float] = array.new_float(0)

        for i in pine_range(0, length - 1):
            if not na(residual[i]):
                absResidual: float = math.abs(residual[i])
                array.push(allValues, absResidual)

                if residual[i] > 0.0:
                    array.push(upperValues, residual[i])
                elif residual[i] < 0.0:
                    array.push(lowerValues, -residual[i])

        fallback: float = f_array_quantile(allValues, percentile)
        upperQuantile: float = nz(f_array_quantile(upperValues, percentile), fallback)
        lowerQuantile: float = nz(f_array_quantile(lowerValues, percentile), fallback)

        return (math.max(nz(upperQuantile, syminfo.mintick), syminfo.mintick), math.max(nz(lowerQuantile, syminfo.mintick), syminfo.mintick))

    def f_clamp(value: float, minValue: float, maxValue: float):
        return math.max(minValue, math.min(value, maxValue))


    def f_SPMA(percentrank_lookback: int, ma_length: int, percentile_gate: int):
        Ret: float = close - close[1]
        Per: float = ta.percentrank(Ret, percentrank_lookback)
        Gate: bool = Per > percentile_gate
        emaValue: float = ta.ema(close, ma_length)

        MA: PersistentSeries[float] = na(float)
        MA = emaValue if na(MA[1]) else emaValue if Gate else MA[1]
        return MA

    SPMA: Series[float] = f_SPMA(Lookback, Length, GateInp)

    __block_result_2__ = na
    __switch__ = VolFeed
    if __switch__ == "SD":
        __block_result_2__ = ta.stdev(close, VolLen)
    elif __switch__ == "ATR":
        __block_result_2__ = ta.atr(VolLen)
    elif __switch__ == "MeanAD":
        __block_result_2__ = ta.dev(close, VolLen)
    elif __switch__ == "MedianAD":
        __block_result_2__ = f_median_ad(close, VolLen)
    elif __switch__ == "Quantile":
        __block_result_2__ = na
    VolatilityRaw: float = __block_result_2__

    Volatility: float = ta.ema(VolatilityRaw, VolLen)

    residual: float = close - SPMA
    quantileUpper, quantileLower = f_quantile_volatility(residual, VolLen, QuantilePct)

    def f_asymmetric_volatility(source: Series[float], symmetricVol: Series[float], smoothLen: int):
        ret: float = math.log(source / source[1]) if source > 0.0 and source[1] > 0.0 else 0.0
        spread: float = 1.0

        bullShock: float = math.pow(math.max(ret, 0.0), 2.0)
        bearShock: float = math.pow(math.max(-ret, 0.0), 2.0)
        totalShock: float = bullShock + bearShock

        bullVar: float = ta.ema(bullShock, smoothLen)
        bearVar: float = ta.ema(bearShock, smoothLen)
        totalVar: float = ta.ema(totalShock, smoothLen)

        bullRatio: float = math.sqrt(math.max(2.0 * bullVar / totalVar, 0.0)) if totalVar > 0.0 else 1.0
        bearRatio: float = math.sqrt(math.max(2.0 * bearVar / totalVar, 0.0)) if totalVar > 0.0 else 1.0

        upperMult: float = 1.0 + 3.0 * (bullRatio - 1.0)
        lowerMult: float = 1.0 + 3.0 * (bearRatio - 1.0)

        avgMult: float = nz(ta.sma(math.avg(upperMult, lowerMult), 180), ta.sma(math.avg(upperMult, lowerMult), math.min(math.max(bar_index, 1), 180)))

        upperMultAdj: float = f_clamp(upperMult, avgMult - spread, avgMult + spread)
        lowerMultAdj: float = f_clamp(lowerMult, avgMult - spread, avgMult + spread)

        upperVol: float = math.max(nz(symmetricVol, syminfo.mintick) * upperMultAdj, syminfo.mintick)
        lowerVol: float = math.max(nz(symmetricVol, syminfo.mintick) * lowerMultAdj, syminfo.mintick)

        return (upperVol, lowerVol)

    asymUpper, asymLower = f_asymmetric_volatility(close, Volatility, VolLen)

    useQuantile: bool = VolFeed == 'Quantile'

    finalUpper: float = quantileUpper if useQuantile else asymUpper if useAsymBands else Volatility
    finalLower: float = quantileLower if useQuantile else asymLower if useAsymBands else Volatility

    upperBand: float = SPMA + finalUpper * VolMul
    lowerBand: float = SPMA - finalLower * VolMul

    SlopePer: float = (SPMA - SPMA[SlopeLen]) / SPMA[SlopeLen] * 100.0 if not na(SPMA[SlopeLen]) and SPMA[SlopeLen] != 0.0 else 0.0
    SlopeGate: bool = SlopePer > SlopeGateL

    NAL: Persistent[int] = 0

    if SPMA > SPMA[1] and close > upperBand and (SlopeGate if UseSlope else True):
        NAL = 1

    if close < lowerBand:
        NAL = -1

    col: Color = col_up if NAL == 1 else col_dn if NAL == -1 else col_nu

    m = plot(SPMA, 'Shock Percentile Moving Average', color=color.new(color.white, 50), linewidth=2)
    u = plot(upperBand, 'Upper Band', color=col, linewidth=2)
    l = plot(lowerBand, 'Lower Band', color=col, linewidth=2)

    plot(upperBand, 'Upper Glow', color=color.new(col, 70), linewidth=7, display=display.pane)
    plot(lowerBand, 'Lower Glow', color=color.new(col, 70), linewidth=7, display=display.pane)

    fill(u, m, color.new(col, 90), title='Upper Core')
    fill(m, l, color.new(col, 90), title='Lower Core')

    plotcandle(open, high, low, close, 'Candles', color=col, wickcolor=col, bordercolor=col, display=display.pane, force_overlay=True)
    barcolor(col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
