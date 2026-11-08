"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    alertcondition, array, close, color, display, fill, high, input, low,
    math, na, nz, open, plot, plotcandle, script, syminfo, ta
)
from pynecore.types import Color, PersistentSeries, Series
import lib.TradingView.ta.v12 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

g1: str = "Regression Settings"
g2: str = "Variance Weighting"
g3: str = "Channel Settings"
g4: str = "Trend Settings"
g5: str = "UI Settings"
GREEN: Color = color.new('#00FF00')
RED: Color = color.new('#FF0000')


@script.indicator("Variance-Weighted Regression Trend [BackQuant]", overlay=True)
def main(
    src: Series[float] = input.source(close, "Source", group=g1),
    regLen=input.int(60, "Regression Length", minval=10, maxval=300, group=g1, inline="1"),
    projectionBars=input.int(5, "Projection Bars", minval=1, maxval=50, group=g1, inline="1"),
    varianceLen=input.int(20, "Variance Length", minval=2, maxval=100, group=g2, inline="2"),
    varianceMode=input.string("EMA", "Variance Model", options=("EMA", "RMA", "Rolling Mean"), group=g2, inline="2"),
    weightPower=input.float(1.0, "Weight Power", minval=0.0, maxval=3.0, step=0.05, group=g2, tooltip="Controls inverse-variance weighting. 0 = equal weights, 1 = inverse variance, values above 1 suppress high-variance observations more aggressively."),
    varianceReg=input.float(0.05, "Variance Regularization", minval=0.0, maxval=1.0, step=0.01, group=g2, tooltip="Adds a fraction of mean residual variance to each local variance estimate to prevent unstable extreme weights."),
    minWeight=input.float(0.1, "Minimum Relative Weight", minval=0.01, maxval=1.0, step=0.05, group=g2, inline="3"),
    maxWeight=input.float(10.0, "Maximum Relative Weight", minval=1.0, maxval=100.0, step=0.5, group=g2, inline="3"),
    channelMode=input.string("Weighted Residual RMS", "Channel Width", options=("Weighted Residual RMS", "Regression Standard Error"), group=g3),
    channelMult=input.float(2.0, "Channel Multiplier", minval=0.1, maxval=10.0, step=0.05, group=g3),
    expandPoorFit=input.bool(False, "Expand During Poor Fit", group=g3),
    poorFitExpansion=input.float(0.5, "Poor Fit Expansion", minval=0.0, maxval=3.0, step=0.05, group=g3),
    qualityConfirm=input.bool(False, "Quality Confirmation", group=g4, tooltip="Requires minimum fit quality before allowing the trend state to flip."),
    minR2=input.float(0.15, "Minimum Weighted R²", minval=0.0, maxval=1.0, step=0.05, group=g4, inline="4"),
    minSlopeScore=input.float(0.5, "Minimum Slope / SE", minval=0.0, maxval=10.0, step=0.1, group=g4, inline="4"),
    showRegression=input.bool(True, "Show Weighted Regression", group=g5),
    showOLS=input.bool(False, "Show OLS Comparison", group=g5),
    showChannel=input.bool(True, "Show Regression Channel", group=g5),
    showFill=input.bool(True, "Gradient Fill", group=g5),
    showGlow=input.bool(True, "Regression Glow", group=g5),
    showProjection=input.bool(True, "Show Projection", group=g5),
    paintBars=input.bool(True, "Color Candles", group=g5),
    lineW=input.int(3, "Line Width", minval=1, maxval=6, group=g5),
    longCol=input.color(GREEN, "Bullish", inline="c", group=g5),
    shortCol=input.color(RED, "Bearish", inline="c", group=g5),
    olsCol=input.color(color.new('#FFFFFF'), "OLS", inline="c", group=g5)
):
    def hwRegression(source: Series[float], length: int, varLen: int, varMode: str, power: float, reg: float, minW: float, maxW: float, projection: int):
        sx: float = 0.0
        sy: float = 0.0
        sxx: float = 0.0
        sxy: float = 0.0
        n: int = 0

        for i in pine_range(0, length - 1):
            if not na(source[i]):
                x: float = length - 1 - i
                y: float = source[i]
                sx += x
                sy += y
                sxx += x * x
                sxy += x * y
                n += 1

        olsDen: float = n * sxx - sx * sx
        olsSlope: float = (n * sxy - sx * sy) / olsDen if n == length and olsDen != 0.0 else na
        olsIntercept: float = (sy - olsSlope * sx) / n if n == length and (not na(olsSlope)) else na
        olsCurrent: float = olsIntercept + olsSlope * (length - 1) if not na(olsIntercept) else na

        residual2: list[float] = array.new_float(length, na)
        residualSum: float = 0.0

        if n == length and (not na(olsIntercept)):
            for i in pine_range(0, length - 1):
                x: float = length - 1 - i
                fitted: float = olsIntercept + olsSlope * x
                resid: float = source[i] - fitted
                r2: float = resid * resid
                array.set(residual2, i, r2)
                residualSum += r2

        meanResidual2: float = residualSum / length if n == length else na
        varianceFloor: float = math.max(meanResidual2 * reg, syminfo.mintick * syminfo.mintick) if not na(meanResidual2) else na

        variances: list[float] = array.new_float(length, na)
        varianceState: float = na(float)
        rollingSum: float = 0.0

        if n == length:
            for j in pine_range(0, length - 1):
                i: int = length - 1 - j
                r2: float = array.get(residual2, i)

                if varMode == 'EMA':
                    alpha: float = 2.0 / (varLen + 1.0)
                    varianceState = r2 if na(varianceState) else alpha * r2 + (1.0 - alpha) * varianceState
                elif varMode == 'RMA':
                    alpha: float = 1.0 / varLen
                    varianceState = r2 if na(varianceState) else alpha * r2 + (1.0 - alpha) * varianceState
                else:
                    rollingSum += r2
                    if j >= varLen:
                        oldIndex: int = length - 1 - (j - varLen)
                        rollingSum -= array.get(residual2, oldIndex)
                    varianceState = rollingSum / math.min(j + 1, varLen)

                array.set(variances, i, varianceState + varianceFloor)

        rawWeightSum: float = 0.0

        if n == length:
            for i in pine_range(0, length - 1):
                variance: float = array.get(variances, i)
                rawWeight: float = 1.0 if power == 0.0 else 1.0 / math.pow(math.max(variance, 1e-12), power)
                rawWeightSum += rawWeight

        avgRawWeight: float = rawWeightSum / length if n == length else na

        sw: float = 0.0
        sw2: float = 0.0
        swx: float = 0.0
        swy: float = 0.0
        swxx: float = 0.0
        swxy: float = 0.0

        if n == length and (not na(avgRawWeight)):
            for i in pine_range(0, length - 1):
                x: float = length - 1 - i
                y: float = source[i]
                variance: float = array.get(variances, i)
                rawWeight: float = 1.0 if power == 0.0 else 1.0 / math.pow(math.max(variance, 1e-12), power)
                relativeWeight: float = rawWeight / avgRawWeight
                w: float = math.max(minW, math.min(maxW, relativeWeight))

                sw += w
                sw2 += w * w
                swx += w * x
                swy += w * y
                swxx += w * x * x
                swxy += w * x * y

        weightedDen: float = sw * swxx - swx * swx
        slope: float = (sw * swxy - swx * swy) / weightedDen if weightedDen != 0.0 else na
        intercept: float = (swy - slope * swx) / sw if sw > 0.0 and (not na(slope)) else na
        regression: float = intercept + slope * (length - 1) if not na(intercept) else na
        projected: float = intercept + slope * (length - 1 + projection) if not na(intercept) else na
        weightedMean: float = swy / sw if sw > 0.0 else na

        sse: float = 0.0
        sst: float = 0.0

        if n == length and (not na(intercept)):
            for i in pine_range(0, length - 1):
                x: float = length - 1 - i
                y: float = source[i]
                variance: float = array.get(variances, i)
                rawWeight: float = 1.0 if power == 0.0 else 1.0 / math.pow(math.max(variance, 1e-12), power)
                relativeWeight: float = rawWeight / avgRawWeight
                w: float = math.max(minW, math.min(maxW, relativeWeight))
                fitted: float = intercept + slope * x

                sse += w * math.pow(y - fitted, 2)
                sst += w * math.pow(y - weightedMean, 2)

        residualRms: float = math.sqrt(sse / sw) if sw > 0.0 else na
        weightedR2: float = math.max(0.0, math.min(1.0, 1.0 - sse / sst)) if sst > 0.0 else 0.0
        residualVariance: float = sse / (n - 2) if n > 2 else na

        xMean: float = swx / sw if sw > 0.0 else na
        centeredSxx: float = swxx - swx * swx / sw if sw > 0.0 else na
        slopeVariance: float = residualVariance / centeredSxx if not na(residualVariance) and centeredSxx > 0.0 else na
        slopeSE: float = math.sqrt(slopeVariance) if not na(slopeVariance) and slopeVariance > 0.0 else na
        slopeScore: float = math.abs(slope) / slopeSE if not na(slopeSE) and slopeSE > 0.0 else 0.0

        currentX: float = length - 1
        fitVariance: float = residualVariance * (1.0 / sw + math.pow(currentX - xMean, 2) / centeredSxx) if not na(residualVariance) and centeredSxx > 0.0 else na
        regressionSE: float = math.sqrt(fitVariance) if not na(fitVariance) and fitVariance > 0.0 else na

        effectiveN: float = sw * sw / sw2 if sw2 > 0.0 else na

        currentVariance: float = array.get(variances, 0)
        currentRawWeight: float = 1.0 if power == 0.0 else 1.0 / math.pow(math.max(currentVariance, 1e-12), power)
        currentWeight: float = math.max(minW, math.min(maxW, currentRawWeight / avgRawWeight)) if not na(avgRawWeight) and avgRawWeight > 0.0 else na

        return (regression, projected, slope, residualRms, regressionSE, weightedR2, slopeScore, currentWeight, effectiveN, olsCurrent)

    regression, projected, slope, residualRms, regressionSE, weightedR2, slopeScore, currentWeight, effectiveN, ols = hwRegression(src, regLen, varianceLen, varianceMode, weightPower, varianceReg, minWeight, maxWeight, projectionBars)

    qualityPass: bool = not qualityConfirm or (weightedR2 >= minR2 and slopeScore >= minSlopeScore)

    trend: PersistentSeries[int] = 0

    if trend == 0 and (not na(slope)):
        trend = 1 if slope >= 0.0 else -1
    elif slope > 0.0 and trend != 1 and qualityPass:
        trend = 1
    elif slope < 0.0 and trend != -1 and qualityPass:
        trend = -1

    bullFlip: bool = trend == 1 and trend[1] == -1
    bearFlip: bool = trend == -1 and trend[1] == 1
    trendFlip: bool = bullFlip or bearFlip

    trendCol: Color = longCol if trend == 1 else shortCol if trend == -1 else color.gray

    channelBase: float = residualRms if channelMode == 'Weighted Residual RMS' else regressionSE
    fitExpansion: float = 1.0 + (1.0 - weightedR2) * poorFitExpansion if expandPoorFit else 1.0
    channelWidth: float = channelBase * channelMult * fitExpansion

    upperChannel: float = regression + channelWidth
    lowerChannel: float = regression - channelWidth

    fitStrength: float = math.max(0.0, math.min(weightedR2, 1.0))
    slopeStrength: float = math.max(0.0, math.min(slopeScore / 3.0, 1.0))
    trendStrength: float = math.min(fitStrength * 0.6 + slopeStrength * 0.4, 1.0)

    barsSinceFlip: int = nz(ta__ren__.barssince(trendFlip), 100000)
    bloomStrength: float = 1.0 if barsSinceFlip == 1 else 0.55 if barsSinceFlip == 2 else 0.25 if barsSinceFlip == 3 else 0.0

    pReg = plot(regression if showRegression else na, 'Variance-Weighted Regression', color=trendCol, linewidth=lineW)
    plot(ols if showOLS else na, 'OLS Comparison', color=color.new(olsCol, 50), linewidth=1)

    pUpper = plot(upperChannel if showChannel else na, 'Upper Regression Channel', color=color.new(trendCol, 80), linewidth=1)
    pLower = plot(lowerChannel if showChannel else na, 'Lower Regression Channel', color=color.new(trendCol, 80), linewidth=1)

    fill(pReg, pUpper, upperChannel, regression, color.new(trendCol, 92) if showChannel and showFill else na, color.new(trendCol, 28) if showChannel and showFill else na, title='Upper Channel Gradient')

    fill(pReg, pLower, regression, lowerChannel, color.new(trendCol, 28) if showChannel and showFill else na, color.new(trendCol, 92) if showChannel and showFill else na, title='Lower Channel Gradient')

    plot(projected if showProjection else na, 'Regression Projection', color=color.new(trendCol, 30), linewidth=2, offset=projectionBars)

    atr: float = ta__ren__.atr(14)
    glow: float = atr * (0.035 + trendStrength * 0.03)
    outerGlow: float = glow * 2.4

    pGlowLower = plot(regression - glow if showGlow else na, 'Glow Lower', display=display.none, editable=False)
    pGlowUpper = plot(regression + glow if showGlow else na, 'Glow Upper', display=display.none, editable=False)
    pOuterGlowLower = plot(regression - outerGlow if showGlow else na, 'Outer Glow Lower', display=display.none, editable=False)
    pOuterGlowUpper = plot(regression + outerGlow if showGlow else na, 'Outer Glow Upper', display=display.none, editable=False)

    fill(pOuterGlowLower, pOuterGlowUpper, color.new(trendCol, 95 - cast_int(math.round(trendStrength * 8.0))) if showGlow else na, title='Outer Regression Glow')
    fill(pGlowLower, pGlowUpper, color.new(trendCol, 86 - cast_int(math.round(trendStrength * 22.0))) if showGlow else na, title='Inner Regression Glow')

    bloomWidth: float = atr * (0.1 + bloomStrength * 0.1)
    bloomReady: bool = showGlow and bloomStrength > 0.0 and (not na(regression))

    pBloomLower = plot(regression - bloomWidth if bloomReady else na, 'Bloom Lower', display=display.none, editable=False)
    pBloomUpper = plot(regression + bloomWidth if bloomReady else na, 'Bloom Upper', display=display.none, editable=False)

    fill(pBloomLower, pBloomUpper, color.new(trendCol, 90 - cast_int(math.round(bloomStrength * 18.0))) if bloomReady else na, title='Flip Bloom')

    plotcandle(open, high, low, close, 'Trend Candles', trendCol, trendCol, True, bordercolor=trendCol, display=display.all if paintBars else display.none)

    plot(slope, 'Weighted Slope', display=display.data_window, editable=False)
    plot(weightedR2 * 100.0, 'Weighted R²', display=display.data_window, editable=False)
    plot(slopeScore, 'Slope / Standard Error', display=display.data_window, editable=False)
    plot(residualRms, 'Weighted Residual RMS', display=display.data_window, editable=False)
    plot(regressionSE, 'Regression Standard Error', display=display.data_window, editable=False)
    plot(currentWeight, 'Current Relative Weight', display=display.data_window, editable=False)
    plot(effectiveN, 'Effective Sample Size', display=display.data_window, editable=False)
    plot(trendStrength * 100.0, 'Trend Strength', display=display.data_window, editable=False)

    alertcondition(bullFlip, 'Variance-Weighted Regression Bullish', 'Variance-Weighted Regression Trend turned bullish on {{ticker}}')
    alertcondition(bearFlip, 'Variance-Weighted Regression Bearish', 'Variance-Weighted Regression Trend turned bearish on {{ticker}}')
    alertcondition(bullFlip or bearFlip, 'Variance-Weighted Regression Flip', 'Variance-Weighted Regression Trend changed direction on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
