"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alertcondition, close, color, hline, input, math, na, plot, script, ta
from pynecore.types import Series

group_primary: str = "Primary QQE Settings"
group_secondary: str = "Secondary QQE Settings"
group_bollinger: str = "Bollinger Bands Settings"


@script.indicator("QQE MOD", overlay=False, max_lines_count=1)
def main(
    rsiLengthPrimary=input.int(6, title="RSI Length", group=group_primary),
    rsiSmoothingPrimary=input.int(5, title="RSI Smoothing", group=group_primary),
    qqeFactorPrimary=input.float(3.0, title="QQE Factor", group=group_primary),
    thresholdPrimary=input.float(3.0, title="Threshold", group=group_primary),
    sourcePrimary: Series[float] = input.source(close, title="RSI Source", group=group_primary),
    rsiLengthSecondary=input.int(6, title="RSI Length", group=group_secondary),
    rsiSmoothingSecondary=input.int(5, title="RSI Smoothing", group=group_secondary),
    qqeFactorSecondary=input.float(1.61, title="QQE Factor", group=group_secondary),
    thresholdSecondary=input.float(3.0, title="Threshold", group=group_secondary),
    sourceSecondary: Series[float] = input.source(close, title="RSI Source", group=group_secondary),
    bollingerLength=input.int(50, minval=1, title="Length", group=group_bollinger, tooltip="The length of the Bollinger Bands calculation."),
    bollingerMultiplier=input.float(0.35, step=0.1, minval=0.001, maxval=5, title="Multiplier", group=group_bollinger, tooltip="The multiplier used to calculate Bollinger Band width.")
):
    def calculateQQE(rsiLength, smoothingFactor, qqeFactor, source):
        wildersLength = rsiLength * 2 - 1
        rsi = ta.rsi(source, rsiLength)
        smoothedRsi: Series = ta.ema(rsi, smoothingFactor)
        atrRsi = math.abs(smoothedRsi[1] - smoothedRsi)
        smoothedAtrRsi = ta.ema(atrRsi, wildersLength)
        dynamicAtrRsi = smoothedAtrRsi * qqeFactor

        longBand: Series[float] = 0.0
        shortBand: Series[float] = 0.0
        trendDirection: Series[int] = 0

        atrDelta = dynamicAtrRsi
        newShortBand = smoothedRsi + atrDelta
        newLongBand = smoothedRsi - atrDelta
        longBand = math.max(longBand[1], newLongBand) if smoothedRsi[1] > longBand[1] and smoothedRsi > longBand[1] else newLongBand
        shortBand = math.min(shortBand[1], newShortBand) if smoothedRsi[1] < shortBand[1] and smoothedRsi < shortBand[1] else newShortBand
        longBandCross = ta.cross(longBand[1], smoothedRsi)

        if ta.cross(smoothedRsi, shortBand[1]):
            trendDirection = 1
        elif longBandCross:
            trendDirection = -1
        else:
            trendDirection = trendDirection[1]

        qqeTrendLine = longBand if trendDirection == 1 else shortBand
        return (qqeTrendLine, smoothedRsi)

    primaryQQETrendLine, primaryRSI = calculateQQE(rsiLengthPrimary, rsiSmoothingPrimary, qqeFactorPrimary, sourcePrimary)

    secondaryQQETrendLine, secondaryRSI = calculateQQE(rsiLengthSecondary, rsiSmoothingSecondary, qqeFactorSecondary, sourceSecondary)

    bollingerBasis = ta.sma(primaryQQETrendLine - 50, bollingerLength)
    bollingerDeviation = bollingerMultiplier * ta.stdev(primaryQQETrendLine - 50, bollingerLength)
    bollingerUpper = bollingerBasis + bollingerDeviation
    bollingerLower = bollingerBasis - bollingerDeviation

    rsiColorPrimary = color.new(color.new('#00C3FF'), 0) if primaryRSI - 50 > bollingerUpper else color.new(color.new('#FF0062'), 0) if primaryRSI - 50 < bollingerLower else color.new(color.new('#707070'), 20)

    rsiColorSecondary = color.new(color.new('#707070'), 20) if secondaryRSI - 50 > thresholdSecondary else color.new(color.new('#707070'), 20) if secondaryRSI - 50 < -thresholdSecondary else na

    plot(secondaryQQETrendLine - 50, title='Secondary QQE Trend Line', color=color.white, linewidth=2)
    plot(secondaryRSI - 50, color=rsiColorSecondary, title='Secondary RSI Histogram', style=plot.style_columns)

    plot(secondaryRSI - 50 if secondaryRSI - 50 > thresholdSecondary and primaryRSI - 50 > bollingerUpper else na, title='QQE Up Signal', style=plot.style_columns, color=color.new('#00C3FF'))
    plot(secondaryRSI - 50 if secondaryRSI - 50 < -thresholdSecondary and primaryRSI - 50 < bollingerLower else na, title='QQE Down Signal', style=plot.style_columns, color=color.new('#FF0062'))

    hline(0, title='Zero Line', color=color.white, linestyle=hline.style_dotted)

    alertcondition(ta.crossover(primaryRSI, 50), title='Primary RSI Cross Above Zero', message='Primary RSI crossed above zero')
    alertcondition(ta.crossunder(primaryRSI, 50), title='Primary RSI Cross Below Zero', message='Primary RSI crossed below zero')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
