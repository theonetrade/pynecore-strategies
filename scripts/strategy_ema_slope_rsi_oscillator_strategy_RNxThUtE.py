"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.lib import (
    alert, array, bar_index, barstate, close, color, fill, high, hline,
    input, label, line, location, low, math, na, nz, open, plot, plotshape, position, script,
    shape, size, strategy, string, ta, table, time, xloc
)
from pynecore.types import Persistent, PersistentSeries, Series, Table

strategyGroup: str = 'Strategy Settings (Close Confirmed)'
pivotTT: str = 'Higher value = More sensitive (more signals, faster detection). Lower value = Less sensitive (fewer but stronger signals, more delay)'


@script.strategy('EMA Slope - RSI Oscilator Strategy', precision=5, overlay=False, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=90, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.04, calc_on_every_tick=False)
def main(
    shortMALength=input.int(20, 'Short MA Length', minval=1, tooltip='Period length for the short moving average used in the stretch filter. Compared with the long MA to detect overextended market conditions.'),
    shortMAType=input.string('EMA', 'Short MA Type', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMWMA', 'SWMA', 'HMA'), tooltip='Moving average type for the short MA. Should match or complement the long MA type for consistent calculations.'),
    longMALength=input.int(160, 'Long MA Length', minval=1, tooltip='Period length for the long moving average used for slope calculation and NTZ detection.'),
    longMAType=input.string('EMA', 'Long MA Type', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMWMA', 'SWMA', 'HMA'), tooltip='Moving average type for the long MA.'),
    smoothBars=input.int(3, 'Smooth Bars', minval=1),
    slopeStdevBars=input.int(140, 'Slope Arctan Scale (Bars)', minval=2, tooltip='Lookback for stdev used in arctan slope normalization. Higher = smoother scale, slope approaches ±50 more slowly. Lower = more responsive, steeper curve.'),
    noTZone=input(True, 'No Trade Zone Threshold'),
    maDL=input.int(10, 'NTZ Threshold', step=1, minval=1),
    accTh=input.int(20, 'Acceleration display greater than', step=1, minval=1),
    src: Series[float] = input(close, 'MA Source'),
    positionSizeType=input.string('Percent of Equity', 'Position Size Type', options=('Percent of Equity', 'Fixed Quantity', 'Percent of Cash'), group=strategyGroup, tooltip='How to calculate position size: Percent of Equity (uses % of total equity), Fixed Quantity (uses fixed number of contracts/units), Percent of Cash (uses % of available cash)'),
    positionSizeValue=input.float(90, 'Position Size Value', minval=0.01, step=0.1, group=strategyGroup, tooltip='Position size value: For Percent of Equity/Cash: enter percentage (e.g., 80 = 80%). For Fixed Quantity: enter number of contracts/units.'),
    maxStretchPercent=input.float(0.34, 'Max Stretch Threshold (%)', minval=0.0, step=0.01, group=strategyGroup, tooltip='Maximum percentage difference between long MA and short MA to allow trade entry. Enter as percentage points: 0.3 = 0.3%, 1.0 = 1.0%. Prevents entries when market is overextended: blocks longs when long MA > short MA by this amount, blocks shorts when long MA < short MA by this amount. Higher = more permissive. Set 0 to disable.'),
    minDelta=input.float(2.3, 'Minimum Delta Threshold', minval=0.0, step=0.1, group=strategyGroup, tooltip='Minimum required change in EMA slope (maDf) to enter a trade. Delta = slope difference between current and previous bar/timeframe. Higher values = stronger momentum required, filters weak signals. Set 0 to disable.'),
    useTimeframeDelta=input(True, 'Use Timeframe Delta', group=strategyGroup, tooltip='This script now evaluates on bar close only to avoid intrabar repaint. Enabled: compare slope delta versus the previous confirmed closed bar. Disabled: compare versus the previous bar value, still using close-confirmed calculations.'),
    enableAccelEntry=input.bool(True, 'Enable Acceleration Entry', group=strategyGroup, tooltip='Enable alternative entry condition when EMA slope shows sudden raise (acceleration) indicated by color dots. Signals are confirmed only after the bar closes to avoid intrabar repaint.'),
    minAccelForEntry=input.float(5, 'Min Acceleration for Entry', minval=0, step=1, group=strategyGroup, tooltip='Minimum acceleration value required for acceleration-based entries. Higher values = more selective, only strongest momentum moves. Default 50 matches typical acceleration display threshold.'),
    useTrendConfirmation=input.bool(True, 'Use MA Trend Confirmation', group=strategyGroup, tooltip='Enable trend confirmation filter based on MA relationship. When enabled: Longs only allowed when Short MA > Long MA (uptrend), Shorts only allowed when Short MA < Long MA (downtrend). Prevents counter-trend entries.'),
    useLastBarFilter=input.bool(True, 'Last Bar Filter', group=strategyGroup, tooltip='When enabled, long entries require both the current bar and the previous bar to be bullish (close above open). Short entries require both bars to be bearish (close below open). Applies to all entries, including reversals; disable to skip this confirmation.'),
    enableRSIDivergence=input.bool(False, 'Enable RSI Divergence Entries', group=strategyGroup, tooltip='Enable RSI divergence-based entry signals. Bullish divergence: price makes lower lows while RSI makes higher lows. Bearish divergence: price makes higher highs while RSI makes lower highs.'),
    showDivergence=input.bool(True, 'Show RSI Divergences', group=strategyGroup, tooltip='Show divergence lines and markers on the chart.'),
    rsiLength=input.int(12, 'RSI Length', minval=1, group=strategyGroup, tooltip='Period length for RSI calculation used in divergence detection.'),
    rsiSmooth=input.int(3, 'RSI Smoothing', minval=1, group=strategyGroup, tooltip='Number of bars to smooth the RSI calculation using SMA.'),
    rsiSource: Series[float] = input(close, 'RSI Source', group=strategyGroup, tooltip='Price source for RSI calculation.'),
    sensitivityInput=input.int(6, title='Divergence Sensitivity', minval=1, maxval=12, group=strategyGroup, tooltip=pivotTT),
    maxPivots=input.int(8, title='Max Peaks to Compare', minval=2, maxval=15, group=strategyGroup, tooltip='Number of previous peaks to check for divergences'),
    showSlopeRsiExhaustion=input.bool(True, 'Show Slope-RSI Exhaustion', group=strategyGroup, tooltip='Display Slope-RSI exhaustion markers when slope momentum and RSI momentum diverge. Orange/Yellow triangles indicate potential trend exhaustion.'),
    enableSlopeRsiEntries=input.bool(True, 'Enable Slope-RSI Divergence Entries', group=strategyGroup, tooltip='Enable direct entries on Slope-RSI divergences (counter-trend reversals). When enabled, enters trades when slope and RSI momentum diverge significantly, indicating trend exhaustion and potential reversal.'),
    useSlopeRsiConfirmation=input.bool(False, 'Require Slope-RSI Confirmation', group=strategyGroup, tooltip='When enabled, RSI divergence entries require Slope-RSI confirmation for higher quality signals. Filters divergence entries where slope and RSI momentum don\'t align.'),
    slopeRsiLookback=input.int(5, 'Slope-RSI Lookback Bars', minval=2, maxval=10, group=strategyGroup, tooltip='Number of bars to compare RSI direction against slope momentum. Higher = more conservative detection.'),
    minDivergenceGap=input.float(5.0, 'Min Slope-RSI Gap (pts)', minval=0, maxval=100, step=0.5, group=strategyGroup, tooltip='Minimum distance between EMA Slope (maDf) and Centered RSI (RSI-50) to trigger a Slope-RSI divergence. Higher = only strong divergences detected. Lower = more sensitive. Set 0 to disable gap threshold.'),
    enableNTZCross=input.bool(True, 'Enable NTZ Cross Entries', group=strategyGroup, tooltip='Enable entries when EMA slope crosses above/below No Trade Zone (NTZ) boundaries with sufficient delta. Crosses are confirmed on bar close to keep signals stable and non-intrabar-repainting.'),
    enableRSISlopeOscillator=input.bool(False, 'Enable RSI-Slope Oscillator Entries', group=strategyGroup, tooltip='Enable RSI-Slope Oscillator entry signals. Long: RSI crosses above EMA Slope outside the NTZ, then enters when both RSI and Slope are heading UP. Short: RSI crosses below EMA Slope outside the NTZ, then enters when both RSI and Slope are heading DOWN. All signals are bar-close confirmed.'),
    maxCrossingBackPeriod=input.int(3, 'RSI-Slope Oscillator Max Crossing Back Period', minval=1, maxval=50, group=strategyGroup, tooltip='Maximum number of bars after RSI-Slope cross to allow entry. If conditions are not met within this period, the entry signal expires. Prevents stale signals from triggering entries.'),
    filterOscCrossPastNTZ=input.bool(True, 'RSI-Slope Osc: Block Cross Past NTZ', group=strategyGroup, tooltip='When enabled, does not arm oscillator entries if RSI crosses above EMA slope while both are already above the NTZ (long), or crosses below while both are already below the NTZ (short). Reduces late chase entries near trend exhaustion. Disable to allow all armed crosses.'),
    exitConfirmBars=input.int(0, 'Exit Confirmation Bars', minval=0, maxval=10, group=strategyGroup, tooltip='Number of consecutive bars exit conditions must be met before closing position. 0 = immediate exit. 1-3 = filters false signals. Higher = more tolerant of pullbacks.'),
    enableNTZReentryExit=input.bool(True, 'Enable NTZ Re-entry Exit', group=strategyGroup, tooltip='When enabled, standard entries (NTZ Cross, Acceleration) can exit when slope re-enters the NTZ after being outside for longer than Exit Confirmation Bars. Disable to rely only on trailing stops and other exits.'),
    enableRSISlopeCrossExit=input.bool(True, 'Reverse/Close on RSI-Slope Cross (Same Direction)', group=strategyGroup, tooltip='When enabled, reverses or closes any position when RSI crosses EMA Slope with both lines moving in the same direction. Bearish: RSI crosses below Slope AND both heading DOWN. Bullish: RSI crosses above Slope AND both heading UP. Exits are confirmed on bar close.'),
    reverseOnRSISlopeCross=input.bool(False, 'Reverse Position (vs Close Only)', group=strategyGroup, tooltip='When enabled, reverses position on RSI-Slope cross. When disabled, only closes position without reversing.'),
    enableRSISlopeCrossEntry=input.bool(False, 'Enable RSI-Slope Cross Entries', group=strategyGroup, tooltip='When enabled, RSI-Slope cross can open the opposite position on exit (reversal). When disabled, RSI-Slope cross only closes the current position.'),
    enableRSIColoring=input.bool(True, 'Enable RSI Coloring', tooltip='Enable dynamic coloring for RSI line: Red when RSI is high/overbought (cRSI > 20), Green when RSI is low/oversold (cRSI < -20), Neutral when near center.'),
    rsiLineWidth=input.int(1, 'RSI Line Width', minval=1, maxval=5, tooltip='Line width for the RSI plot'),
    rsiColorHigh=input.color(color.new(color.red, 0), 'RSI High Color', tooltip='Color for RSI when overbought (cRSI > 20)'),
    rsiColorLow=input.color(color.new(color.green, 0), 'RSI Low Color', tooltip='Color for RSI when oversold (cRSI < -20)'),
    rsiColorNeutral=input.color(color.new(color.new('#87CEEB'), 0), 'RSI Neutral Color', tooltip='Color for RSI when near center (between -20 and 20)'),
    entryATRPeriod=input.int(10, 'Entry ATR Period', minval=1, group='Entry Stop Loss', tooltip='Period for ATR calculation used to determine initial stop loss price when entering a position.'),
    entryATRFactor=input.float(4.4, 'Entry ATR Factor', minval=0.1, step=0.1, group='Entry Stop Loss', tooltip='Multiplier for Entry ATR in initial stop loss calculation. Higher values = wider initial stop loss.'),
    useTrailingStop=input.bool(False, 'Use Trailing Stop', group='Trailing Stop', tooltip='Enable trailing stop based on Blackflag FTS Swingarm. Trailing exits are evaluated on bar close for stable, non-intrabar-repainting behavior.'),
    trailType=input.string('modified', 'Trail Type', options=('modified', 'unmodified'), group='Trailing Stop', tooltip='Modified: Uses enhanced true range calculation. Unmodified: Uses standard true range.'),
    ATRPeriod=input.int(12, 'Trailing Stop ATR Period', minval=1, group='Trailing Stop', tooltip='Period for ATR calculation used in trailing stop updates after entry. Typically wider than Entry ATR.'),
    ATRFactor=input.float(7, 'Trailing Stop ATR Factor', minval=0.1, step=0.1, group='Trailing Stop', tooltip='Multiplier for Trailing Stop ATR in trailing stop calculation. Higher values = wider trailing stop.'),
    divTrailingStopGrace=input.int(5, 'Divergence Entry Grace Bars', minval=0, maxval=10, group='Trailing Stop', tooltip='Number of bars to wait before activating trailing stop for divergence entries. Gives the position time to develop. 0 = immediate activation.'),
    divATRFactor=input.float(6, 'Divergence Entry ATR Factor', minval=0.1, step=0.1, group='Trailing Stop', tooltip='ATR multiplier for divergence entry trailing stops. Higher than standard to give reversal trades more room. Recommended: 5-8.'),
    oscTrailingStopGrace=input.int(3, 'RSI-Slope Oscillator Entry Grace Bars', minval=0, maxval=10, group='Trailing Stop', tooltip='Number of bars to wait before activating trailing stop for RSI-Slope Oscillator entries. Gives the position time to develop. 0 = immediate activation.'),
    oscATRFactor=input.float(6, 'RSI-Slope Oscillator Entry ATR Factor', minval=0.1, step=0.1, group='Trailing Stop', tooltip='ATR multiplier for RSI-Slope Oscillator entry trailing stops. Higher than standard to give reversal trades more room. Recommended: 5-8.'),
    standardTrailingStopGrace=input.int(3, 'Standard Entry Grace Bars', minval=0, maxval=10, group='Trailing Stop', tooltip='Number of bars to wait before activating trailing stop for standard entries (NTZ Cross, Acceleration). Prevents immediate exits after entry. 0 = immediate activation. Recommended: 2-5.'),
    ntzFillC=input.color(color.new(color.new('#777777'), 70), 'NTZ fill color')
):
    hLineHeight = maDL if noTZone else 0

    def fma(type, src, _len):
        result: float = 0
        if type == 'SMA':
            result = ta.sma(src, _len)
        if type == 'EMA':
            result = ta.ema(src, _len)
        if type == 'DEMA':
            e = ta.ema(src, _len)
            result = 2 * e - ta.ema(e, _len)
        if type == 'TEMA':
            e = ta.ema(src, _len)
            result = 3 * (e - ta.ema(e, _len)) + ta.ema(ta.ema(e, _len), _len)
        if type == 'WMA':
            result = ta.wma(src, _len)
        if type == 'VWMA':
            result = ta.vwma(src, _len)
        if type == 'SMWMA':
            w: Series = ta.wma(src, _len)
            wb = ta.sma(src, _len)
            result = wb if na(w[1]) else (w[1] * (_len - 1) + src) / _len
        if type == 'SWMA':
            result = ta.swma(src)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, _len / 2) - ta.wma(src, _len), math.round(math.sqrt(_len)))
        return result

    shortMA = fma(shortMAType, src, shortMALength)
    longMA: Series = fma(longMAType, src, longMALength)

    maPercentDiff = (longMA - shortMA) / shortMA * 100

    maDF = longMA - longMA[smoothBars]

    maDFScale = math.max(ta.stdev(maDF, slopeStdevBars), 1e-10)
    maDf: Series = 100 / math.pi * math.atan(maDF / maDFScale)

    prevConfirmedSlope: Persistent[float] = na(float)
    delta: float = na(float)

    if useTimeframeDelta:
        if barstate.isconfirmed:
            if not na(prevConfirmedSlope):
                delta = maDf - prevConfirmedSlope
            prevConfirmedSlope = maDf
    else:
        delta = maDf - maDf[1]

    maAcce = math.abs(maDf - maDf[1]) * smoothBars * 2
    maAccHt = ta.highest(maAcce, 200)
    maAcc = math.min(50 * maAcce / maAccHt, 50) if maAccHt > 0 else 0

    rsi = ta.sma(ta.rsi(rsiSource, rsiLength), rsiSmooth)

    cRsi: Series = rsi - 50

    waitingForLongConfirmation: Persistent[bool] = False
    waitingForShortConfirmation: Persistent[bool] = False
    crossBarLong: Persistent[int] = na(int)
    crossBarShort: Persistent[int] = na(int)

    rsiSlopeCrossUp = ta.crossover(cRsi, maDf)
    rsiSlopeCrossDown = ta.crossunder(cRsi, maDf)

    rsiHeadingUp = cRsi > cRsi[1]
    rsiHeadingDown = cRsi < cRsi[1]
    slopeHeadingUp = maDf > maDf[1]
    slopeHeadingDown = maDf < maDf[1]

    oscillatorCrossOutsideNTZ = not noTZone or math.abs(maDf) > hLineHeight

    oscArmLongBlockedPastNTZ = filterOscCrossPastNTZ and cRsi > hLineHeight and (maDf > hLineHeight)
    oscArmShortBlockedPastNTZ = filterOscCrossPastNTZ and cRsi < -hLineHeight and (maDf < -hLineHeight)
    if enableRSISlopeOscillator:
        if rsiSlopeCrossUp and oscillatorCrossOutsideNTZ:
            if not oscArmLongBlockedPastNTZ:
                waitingForLongConfirmation = True
                waitingForShortConfirmation = False
                crossBarLong = bar_index
                crossBarShort = na
            else:
                waitingForLongConfirmation = False
                crossBarLong = na

        if rsiSlopeCrossDown and oscillatorCrossOutsideNTZ:
            if not oscArmShortBlockedPastNTZ:
                waitingForShortConfirmation = True
                waitingForLongConfirmation = False
                crossBarShort = bar_index
                crossBarLong = na
            else:
                waitingForShortConfirmation = False
                crossBarShort = na
    else:
        waitingForLongConfirmation = False
        waitingForShortConfirmation = False
        crossBarLong = na
        crossBarShort = na

    barsSinceCrossLong = bar_index - crossBarLong if not na(crossBarLong) else 999999
    barsSinceCrossShort = bar_index - crossBarShort if not na(crossBarShort) else 999999

    if enableRSISlopeOscillator and waitingForLongConfirmation and (not na(crossBarLong)):
        if barsSinceCrossLong > maxCrossingBackPeriod:
            waitingForLongConfirmation = False
            crossBarLong = na

    if enableRSISlopeOscillator and waitingForShortConfirmation and (not na(crossBarShort)):
        if barsSinceCrossShort > maxCrossingBackPeriod:
            waitingForShortConfirmation = False
            crossBarShort = na

    barsSinceCrossLongValid = not na(crossBarLong) and barsSinceCrossLong <= maxCrossingBackPeriod

    rsiSlopeOscLong = waitingForLongConfirmation and barsSinceCrossLongValid and rsiHeadingUp and slopeHeadingUp and (not useTimeframeDelta or barstate.isconfirmed) if enableRSISlopeOscillator else False

    barsSinceCrossShortValid = not na(crossBarShort) and barsSinceCrossShort <= maxCrossingBackPeriod

    rsiSlopeOscShort = waitingForShortConfirmation and barsSinceCrossShortValid and rsiHeadingDown and slopeHeadingDown and (not useTimeframeDelta or barstate.isconfirmed) if enableRSISlopeOscillator else False

    waitingForBearishCrossConfirmation: Persistent[bool] = False
    waitingForBullishCrossConfirmation: Persistent[bool] = False
    crossBarBearish: Persistent[int] = na(int)
    crossBarBullish: Persistent[int] = na(int)

    if enableRSISlopeCrossExit:
        if rsiSlopeCrossDown:
            waitingForBearishCrossConfirmation = True
            waitingForBullishCrossConfirmation = False
            crossBarBearish = bar_index
            crossBarBullish = na

        if rsiSlopeCrossUp:
            waitingForBullishCrossConfirmation = True
            waitingForBearishCrossConfirmation = False
            crossBarBullish = bar_index
            crossBarBearish = na
    else:
        waitingForBearishCrossConfirmation = False
        waitingForBullishCrossConfirmation = False
        crossBarBearish = na
        crossBarBullish = na

    barsSinceCrossBearish = bar_index - crossBarBearish if not na(crossBarBearish) else 999999
    barsSinceCrossBullish = bar_index - crossBarBullish if not na(crossBarBullish) else 999999

    if enableRSISlopeCrossExit and waitingForBearishCrossConfirmation and (not na(crossBarBearish)):
        if barsSinceCrossBearish > maxCrossingBackPeriod:
            waitingForBearishCrossConfirmation = False
            crossBarBearish = na

    if enableRSISlopeCrossExit and waitingForBullishCrossConfirmation and (not na(crossBarBullish)):
        if barsSinceCrossBullish > maxCrossingBackPeriod:
            waitingForBullishCrossConfirmation = False
            crossBarBullish = na

    barsSinceCrossBearishValid = not na(crossBarBearish) and barsSinceCrossBearish <= maxCrossingBackPeriod

    rsiSlopeCrossBearish = enableRSISlopeCrossExit and (waitingForBearishCrossConfirmation and barsSinceCrossBearishValid or rsiSlopeCrossDown) and rsiHeadingDown and slopeHeadingDown and (close < open) and (not useTimeframeDelta or barstate.isconfirmed)

    barsSinceCrossBullishValid = not na(crossBarBullish) and barsSinceCrossBullish <= maxCrossingBackPeriod

    rsiSlopeCrossBullish = enableRSISlopeCrossExit and (waitingForBullishCrossConfirmation and barsSinceCrossBullishValid or rsiSlopeCrossUp) and rsiHeadingUp and slopeHeadingUp and (close > open) and (not useTimeframeDelta or barstate.isconfirmed)

    bullSlopeRsiBar: Persistent[int] = na(int)
    bearSlopeRsiBar: Persistent[int] = na(int)
    prevBullSlopeRsiTime: Persistent[int] = na(int)
    prevBearSlopeRsiTime: Persistent[int] = na(int)
    prevBullSlope: Persistent[float] = na(float)
    prevBearSlope: Persistent[float] = na(float)
    prevBullCRsi: Persistent[float] = na(float)
    prevBearCRsi: Persistent[float] = na(float)
    bullishSlopeRsiDiv: bool = False
    bearishSlopeRsiDiv: bool = False

    accelerationActive = maAcc >= minAccelForEntry

    divergenceGap = math.abs(maDf - cRsi)

    if accelerationActive and (not na(delta)) and (delta > 0) and (maDf > hLineHeight):
        if cRsi < cRsi[slopeRsiLookback] and cRsi < cRsi[slopeRsiLookback * 2]:
            if minDivergenceGap == 0 or divergenceGap >= minDivergenceGap:
                bearishSlopeRsiDiv = True
                bearSlopeRsiBar = bar_index

                if showSlopeRsiExhaustion and (not na(prevBearSlopeRsiTime)):
                    line.new(prevBearSlopeRsiTime, prevBearSlope, time, maDf, xloc=xloc.bar_time, color=color.new(color.green, 60), width=2, style=line.style_dashed)
                    line.new(prevBearSlopeRsiTime, prevBearCRsi, time, cRsi, xloc=xloc.bar_time, color=color.new(color.red, 60), width=2, style=line.style_dashed)

                    label.new(bar_index, 80, text='Gap: ' + string.tostring(divergenceGap, '#.#'), style=label.style_none, color=color.yellow, textcolor=color.yellow, size=size.tiny)

                prevBearSlopeRsiTime = time
                prevBearSlope = maDf
                prevBearCRsi = cRsi

    if accelerationActive and (not na(delta)) and (delta < 0) and (maDf < -hLineHeight):
        if cRsi > cRsi[slopeRsiLookback] and cRsi > cRsi[slopeRsiLookback * 2]:
            if minDivergenceGap == 0 or divergenceGap >= minDivergenceGap:
                bullishSlopeRsiDiv = True
                bullSlopeRsiBar = bar_index

                if showSlopeRsiExhaustion and (not na(prevBullSlopeRsiTime)):
                    line.new(prevBullSlopeRsiTime, prevBullSlope, time, maDf, xloc=xloc.bar_time, color=color.new(color.red, 60), width=2, style=line.style_dashed)
                    line.new(prevBullSlopeRsiTime, prevBullCRsi, time, cRsi, xloc=xloc.bar_time, color=color.new(color.green, 60), width=2, style=line.style_dashed)

                    label.new(bar_index, -80, text='Gap: ' + string.tostring(divergenceGap, '#.#'), style=label.style_none, color=color.orange, textcolor=color.orange, size=size.tiny)

                prevBullSlopeRsiTime = time
                prevBullSlope = maDf
                prevBullCRsi = cRsi

    pivotHighsRSI: Persistent[list[float]] = array.new_float(0)
    pivotHighsTime: Persistent[list[int]] = array.new_int(0)
    pivotHighsPrice: Persistent[list[float]] = array.new_float(0)

    pivotLowsRSI: Persistent[list[float]] = array.new_float(0)
    pivotLowsTime: Persistent[list[int]] = array.new_int(0)
    pivotLowsPrice: Persistent[list[float]] = array.new_float(0)

    bullishDivergence: bool = False
    bearishDivergence: bool = False
    bullDivBar: Persistent[int] = na(int)
    bearDivBar: Persistent[int] = na(int)

    if showDivergence or enableRSIDivergence:
        pivotLookback = 16 - sensitivityInput

        pivotHigh = ta.pivothigh(rsi, pivotLookback, pivotLookback)
        pivotLow = ta.pivotlow(rsi, pivotLookback, pivotLookback)
        priceHigh = ta.pivothigh(high, pivotLookback, pivotLookback)
        priceLow = ta.pivotlow(low, pivotLookback, pivotLookback)

        if not na(pivotHigh):
            if array.size(pivotHighsRSI) > 0:
                __loop_3__ = pine_loop(0, 1)
                while __loop_3__.step(math.min(array.size(pivotHighsRSI) - 1, maxPivots - 1)):
                    i = __loop_3__.value
                    prevRSI = array.get(pivotHighsRSI, i)
                    prevPivotTime = array.get(pivotHighsTime, i)
                    prevPrice = array.get(pivotHighsPrice, i)

                    if priceHigh > prevPrice and pivotHigh < prevRSI:
                        bearishDivergence = True
                        bearDivBar = bar_index

                        if showDivergence:
                            line.new(prevPivotTime, prevRSI - 50, time, pivotHigh - 50, xloc=xloc.bar_time, color=color.new(color.purple, 20), width=2, style=line.style_solid)
                        break

            array.unshift(pivotHighsRSI, pivotHigh)
            array.unshift(pivotHighsTime, time)
            array.unshift(pivotHighsPrice, priceHigh)

            if array.size(pivotHighsRSI) > maxPivots:
                array.pop(pivotHighsRSI)
                array.pop(pivotHighsTime)
                array.pop(pivotHighsPrice)

        if not na(pivotLow):
            if array.size(pivotLowsRSI) > 0:
                __loop_3__ = pine_loop(0, 1)
                while __loop_3__.step(math.min(array.size(pivotLowsRSI) - 1, maxPivots - 1)):
                    i = __loop_3__.value
                    prevRSI = array.get(pivotLowsRSI, i)
                    prevPivotTime = array.get(pivotLowsTime, i)
                    prevPrice = array.get(pivotLowsPrice, i)

                    if priceLow < prevPrice and pivotLow > prevRSI:
                        bullishDivergence = True
                        bullDivBar = bar_index

                        if showDivergence:
                            line.new(prevPivotTime, prevRSI - 50, time, pivotLow - 50, xloc=xloc.bar_time, color=color.new(color.lime, 20), width=2, style=line.style_solid)
                        break

            array.unshift(pivotLowsRSI, pivotLow)
            array.unshift(pivotLowsTime, time)
            array.unshift(pivotLowsPrice, priceLow)

            if array.size(pivotLowsRSI) > maxPivots:
                array.pop(pivotLowsRSI)
                array.pop(pivotLowsTime)
                array.pop(pivotLowsPrice)

    inChannel = maDf < hLineHeight and maDf > -hLineHeight and (maDf[1] >= hLineHeight or maDf[1] <= -hLineHeight)

    prevConfirmedSlopeForCross: Persistent[float] = na(float)
    crossAboveNTZ: bool = False
    crossBelowNTZ: bool = False

    if useTimeframeDelta:
        if barstate.isconfirmed:
            if not na(prevConfirmedSlopeForCross):
                crossAboveNTZ = maDf > hLineHeight and prevConfirmedSlopeForCross <= hLineHeight
                crossBelowNTZ = maDf < -hLineHeight and prevConfirmedSlopeForCross >= -hLineHeight
            prevConfirmedSlopeForCross = maDf
    else:
        crossAboveNTZ = maDf > hLineHeight and maDf[1] <= hLineHeight
        crossBelowNTZ = maDf < -hLineHeight and maDf[1] >= -hLineHeight

    deltaSufficient = not na(delta) and math.abs(delta) >= minDelta

    stretchFilterLong = maPercentDiff >= 0 or (maPercentDiff < 0 and maPercentDiff >= -maxStretchPercent)
    stretchFilterShort = maPercentDiff <= 0 or (maPercentDiff > 0 and maPercentDiff <= maxStretchPercent)
    entryOutsideNTZ = not noTZone or math.abs(maDf) > hLineHeight

    trendConfirmLong = not useTrendConfirmation or shortMA > longMA
    trendConfirmShort = not useTrendConfirmation or shortMA < longMA

    lastBarFilterLong = not useLastBarFilter or (close > open and close[1] > open[1])
    lastBarFilterShort = not useLastBarFilter or (close < open and close[1] < open[1])

    def getPositionSize():
        qty: float = 1.0
        if positionSizeType == 'Percent of Equity':
            qty = strategy.equity * positionSizeValue / 100.0 / close
        elif positionSizeType == 'Percent of Cash':
            qty = strategy.equity * positionSizeValue / 100.0 / close
        elif positionSizeType == 'Fixed Quantity':
            qty = positionSizeValue
        return qty

    def Wild_ma(_src, _malength):
        _wild: Series[float] = 0.0
        _wild = nz(_wild[1]) + (_src - nz(_wild[1])) / _malength
        return _wild

    suddenSlopeRaiseLong = enableAccelEntry and accelerationActive and deltaSufficient and (delta > 0) and (maDf > hLineHeight) and stretchFilterLong and trendConfirmLong and (not useTimeframeDelta or barstate.isconfirmed)
    suddenSlopeRaiseShort = enableAccelEntry and accelerationActive and deltaSufficient and (delta < 0) and (maDf < -hLineHeight) and stretchFilterShort and trendConfirmShort and (not useTimeframeDelta or barstate.isconfirmed)

    slopeRsiConfirmLong = not useSlopeRsiConfirmation or bullishSlopeRsiDiv
    slopeRsiConfirmShort = not useSlopeRsiConfirmation or bearishSlopeRsiDiv

    rsiDivergenceLong = enableRSIDivergence and bullishDivergence and slopeRsiConfirmLong and (not useTimeframeDelta or barstate.isconfirmed)

    rsiDivergenceShort = enableRSIDivergence and bearishDivergence and slopeRsiConfirmShort and (not useTimeframeDelta or barstate.isconfirmed)

    slopeRsiDivergenceLong = enableSlopeRsiEntries and bullishSlopeRsiDiv and (not useTimeframeDelta or barstate.isconfirmed)

    slopeRsiDivergenceShort = enableSlopeRsiEntries and bearishSlopeRsiDiv and (not useTimeframeDelta or barstate.isconfirmed)

    isRSIDivergenceLong: Persistent[bool] = False
    isRSIDivergenceShort: Persistent[bool] = False
    isRSISlopeOscLong: Persistent[bool] = False
    isRSISlopeOscShort: Persistent[bool] = False
    isAccelerationLong: Persistent[bool] = False
    isAccelerationShort: Persistent[bool] = False
    entryBarLong: Persistent[int] = 0
    entryBarShort: Persistent[int] = 0

    standardTrailLong: PersistentSeries[float] = na(float)
    standardTrailShort: PersistentSeries[float] = na(float)
    standardEntryPriceLong: Persistent[float] = na(float)
    standardEntryPriceShort: Persistent[float] = na(float)
    standardTrailInitBarLong: Persistent[int] = -1
    standardTrailInitBarShort: Persistent[int] = -1
    divTrailLong: PersistentSeries[float] = na(float)
    divTrailShort: PersistentSeries[float] = na(float)
    divEntryPrice: Persistent[float] = na(float)
    divTrailInitBarLong: Persistent[int] = -1
    divTrailInitBarShort: Persistent[int] = -1
    oscTrailLong: PersistentSeries[float] = na(float)
    oscTrailShort: PersistentSeries[float] = na(float)
    oscEntryPrice: Persistent[float] = na(float)
    oscTrailInitBarLong: Persistent[int] = -1
    oscTrailInitBarShort: Persistent[int] = -1

    canEnterLong = strategy.position_size <= 0
    canEnterShort = strategy.position_size >= 0

    suppressLongPositionLogic: bool = False
    suppressShortPositionLogic: bool = False

    ntzCrossLong = enableNTZCross and (not rsiSlopeCrossUp) and (not rsiSlopeCrossDown) and (crossAboveNTZ or (maDf > hLineHeight and deltaSufficient and (delta > 0))) and stretchFilterLong and trendConfirmLong and (not useTimeframeDelta or barstate.isconfirmed)

    rsiSlopeOscLongEntry = enableRSISlopeOscillator and rsiSlopeOscLong
    accelerationLongEntry = enableAccelEntry and suddenSlopeRaiseLong
    longCondition = canEnterLong and entryOutsideNTZ and lastBarFilterLong and (ntzCrossLong or accelerationLongEntry or rsiDivergenceLong or slopeRsiDivergenceLong or rsiSlopeOscLongEntry)

    ntzCrossShort = enableNTZCross and (not rsiSlopeCrossUp) and (not rsiSlopeCrossDown) and (crossBelowNTZ or (maDf < -hLineHeight and deltaSufficient and (delta < 0))) and stretchFilterShort and trendConfirmShort and (not useTimeframeDelta or barstate.isconfirmed)

    rsiSlopeOscShortEntry = enableRSISlopeOscillator and rsiSlopeOscShort
    accelerationShortEntry = enableAccelEntry and suddenSlopeRaiseShort
    shortCondition = canEnterShort and entryOutsideNTZ and lastBarFilterShort and (ntzCrossShort or accelerationShortEntry or rsiDivergenceShort or slopeRsiDivergenceShort or rsiSlopeOscShortEntry)

    normalReverseToLong = longCondition and strategy.position_size < 0
    normalReverseToShort = shortCondition and strategy.position_size > 0

    exitConfirmCountLong: Persistent[int] = 0
    exitConfirmCountShort: Persistent[int] = 0

    if longCondition:
        if normalReverseToLong:
            suppressShortPositionLogic = True
            standardTrailShort = na
            standardTrailInitBarShort = -1
            standardEntryPriceShort = na
            divTrailShort = na
            divTrailInitBarShort = -1
            divEntryPrice = na
            oscTrailShort = na
            oscTrailInitBarShort = -1
            oscEntryPrice = na

        isRSIDivergenceLong = rsiDivergenceLong or slopeRsiDivergenceLong
        isRSIDivergenceShort = False
        isRSISlopeOscLong = rsiSlopeOscLongEntry
        isRSISlopeOscShort = False
        isAccelerationLong = accelerationLongEntry
        isAccelerationShort = False
        entryBarLong = bar_index

        exitConfirmCountLong = 0
        exitConfirmCountShort = 0

    if shortCondition:
        if normalReverseToShort:
            suppressLongPositionLogic = True
            standardTrailLong = na
            standardTrailInitBarLong = -1
            standardEntryPriceLong = na
            divTrailLong = na
            divTrailInitBarLong = -1
            divEntryPrice = na
            oscTrailLong = na
            oscTrailInitBarLong = -1
            oscEntryPrice = na

        isRSIDivergenceLong = False
        isRSIDivergenceShort = rsiDivergenceShort or slopeRsiDivergenceShort
        isRSISlopeOscLong = False
        isRSISlopeOscShort = rsiSlopeOscShortEntry
        isAccelerationLong = False
        isAccelerationShort = accelerationShortEntry
        entryBarShort = bar_index

        exitConfirmCountLong = 0
        exitConfirmCountShort = 0

    if longCondition:
        qty = getPositionSize()
        strategy.entry('Long', strategy.long, qty=qty, comment='EMA Slope Long')

        entryPrice = close
        posSize = qty
        entryType = 'RSI-Slope Osc' if rsiSlopeOscLongEntry else 'Slope-RSI Div' if slopeRsiDivergenceLong else 'RSI Divergence' if rsiDivergenceLong else 'Acceleration' if suddenSlopeRaiseLong else 'NTZ Cross'
        trendStatus = ('Uptrend' if shortMA > longMA else 'No trend') if useTrendConfirmation else 'Disabled'
        slopeRsiStatus = ('Yes' if bullishSlopeRsiDiv else 'No') if useSlopeRsiConfirmation else 'Disabled'
        alertMsg = '🟢 LONG ENTRY (' + entryType + ')\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Delta: ' + string.tostring(delta, '#.##') + '\n' + 'Acceleration: ' + string.tostring(maAcc, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Trend Confirm: ' + trendStatus + '\n' + 'Slope-RSI Confirm: ' + slopeRsiStatus + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
        alert(alertMsg, alert.freq_once_per_bar_close)

        if rsiSlopeOscLongEntry:
            waitingForLongConfirmation = False
            waitingForShortConfirmation = False
            crossBarLong = na
            crossBarShort = na

    if shortCondition:
        qty = getPositionSize()
        strategy.entry('Short', strategy.short, qty=qty, comment='EMA Slope Short')

        entryPrice = close
        posSize = qty
        entryType = 'RSI-Slope Osc' if rsiSlopeOscShortEntry else 'Acceleration' if accelerationShortEntry else 'Slope-RSI Div' if slopeRsiDivergenceShort else 'RSI Divergence' if rsiDivergenceShort else 'NTZ Cross'
        trendStatus = ('Downtrend' if shortMA < longMA else 'No trend') if useTrendConfirmation else 'Disabled'
        slopeRsiStatus = ('Yes' if bearishSlopeRsiDiv else 'No') if useSlopeRsiConfirmation else 'Disabled'
        alertMsg = '🔴 SHORT ENTRY (' + entryType + ')\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Delta: ' + string.tostring(delta, '#.##') + '\n' + 'Acceleration: ' + string.tostring(maAcc, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Trend Confirm: ' + trendStatus + '\n' + 'Slope-RSI Confirm: ' + slopeRsiStatus + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
        alert(alertMsg, alert.freq_once_per_bar_close)

        if rsiSlopeOscShortEntry:
            waitingForLongConfirmation = False
            waitingForShortConfirmation = False
            crossBarLong = na
            crossBarShort = na

    if strategy.position_size > 0 and entryBarLong > 0 and (bar_index > entryBarLong):
        isRSIDivergenceLong = isRSIDivergenceLong
        isRSISlopeOscLong = isRSISlopeOscLong
        isAccelerationLong = isAccelerationLong

    if strategy.position_size < 0 and entryBarShort > 0 and (bar_index > entryBarShort):
        isRSIDivergenceShort = isRSIDivergenceShort
        isRSISlopeOscShort = isRSISlopeOscShort
        isAccelerationShort = isAccelerationShort

    barsSinceEntryLong = bar_index - entryBarLong if strategy.position_size > 0 else 0
    barsSinceEntryShort = bar_index - entryBarShort if strategy.position_size < 0 else 0

    entryATR = ta.atr(entryATRPeriod)
    trailATR = ta.atr(ATRPeriod)

    if useTrailingStop and strategy.position_size > 0 and (not suppressLongPositionLogic) and (not isRSIDivergenceLong or not enableRSIDivergence) and (not isRSISlopeOscLong or not enableRSISlopeOscillator):
        if standardTrailInitBarLong != entryBarLong:
            standardEntryPriceLong = close

            standardTrailLong = close - entryATRFactor * entryATR
            standardTrailInitBarLong = entryBarLong
        elif barsSinceEntryLong > standardTrailingStopGrace:
            newStop = high - ATRFactor * trailATR

            standardTrailLong = math.max(nz(standardTrailLong[1], newStop), newStop)
    elif strategy.position_size <= 0 or not useTrailingStop or suppressLongPositionLogic:
        standardTrailLong = na
        standardTrailInitBarLong = -1
        standardEntryPriceLong = na

    if useTrailingStop and strategy.position_size < 0 and (not suppressShortPositionLogic) and (not isRSIDivergenceShort or not enableRSIDivergence) and (not isRSISlopeOscShort or not enableRSISlopeOscillator):
        if standardTrailInitBarShort != entryBarShort:
            standardEntryPriceShort = close

            standardTrailShort = close + entryATRFactor * entryATR
            standardTrailInitBarShort = entryBarShort
        elif barsSinceEntryShort > standardTrailingStopGrace:
            newStop = low + ATRFactor * trailATR

            standardTrailShort = math.min(nz(standardTrailShort[1], newStop), newStop)
    elif strategy.position_size >= 0 or not useTrailingStop or suppressShortPositionLogic:
        standardTrailShort = na
        standardTrailInitBarShort = -1
        standardEntryPriceShort = na

    if enableRSIDivergence and strategy.position_size > 0 and (not suppressLongPositionLogic) and isRSIDivergenceLong:
        if divTrailInitBarLong != entryBarLong:
            divEntryPrice = close
            divTrailLong = close - entryATRFactor * entryATR
            divTrailInitBarLong = entryBarLong
        elif barsSinceEntryLong > divTrailingStopGrace:
            newStop = high - divATRFactor * trailATR
            divTrailLong = math.max(nz(divTrailLong[1], newStop), newStop)
    elif strategy.position_size <= 0 or not enableRSIDivergence or suppressLongPositionLogic:
        divTrailLong = na
        divTrailInitBarLong = -1

    if enableRSIDivergence and strategy.position_size < 0 and (not suppressShortPositionLogic) and isRSIDivergenceShort:
        if divTrailInitBarShort != entryBarShort:
            divEntryPrice = close
            divTrailShort = close + entryATRFactor * entryATR
            divTrailInitBarShort = entryBarShort
        elif barsSinceEntryShort > divTrailingStopGrace:
            newStop = low + divATRFactor * trailATR
            divTrailShort = math.min(nz(divTrailShort[1], newStop), newStop)
    elif strategy.position_size >= 0 or not enableRSIDivergence or suppressShortPositionLogic:
        divTrailShort = na
        divTrailInitBarShort = -1

    if enableRSISlopeOscillator and strategy.position_size > 0 and (not suppressLongPositionLogic) and isRSISlopeOscLong:
        if oscTrailInitBarLong != entryBarLong:
            oscEntryPrice = close
            oscTrailLong = close - entryATRFactor * entryATR
            oscTrailInitBarLong = entryBarLong
        elif barsSinceEntryLong > oscTrailingStopGrace:
            newStop = high - oscATRFactor * trailATR
            oscTrailLong = math.max(nz(oscTrailLong[1], newStop), newStop)
    elif strategy.position_size <= 0 or not enableRSISlopeOscillator or suppressLongPositionLogic:
        oscTrailLong = na
        oscTrailInitBarLong = -1

    if enableRSISlopeOscillator and strategy.position_size < 0 and (not suppressShortPositionLogic) and isRSISlopeOscShort:
        if oscTrailInitBarShort != entryBarShort:
            oscEntryPrice = close
            oscTrailShort = close + entryATRFactor * entryATR
            oscTrailInitBarShort = entryBarShort
        elif barsSinceEntryShort > oscTrailingStopGrace:
            newStop = low + oscATRFactor * trailATR
            oscTrailShort = math.min(nz(oscTrailShort[1], newStop), newStop)
    elif strategy.position_size >= 0 or not enableRSISlopeOscillator or suppressShortPositionLogic:
        oscTrailShort = na
        oscTrailInitBarShort = -1

    if strategy.position_size > 0 and (not suppressLongPositionLogic) and rsiSlopeCrossBearish:
        entryPrice = strategy.opentrades.entry_price(0)
        posSize = strategy.position_size
        currentPrice = close
        profit = strategy.opentrades.profit(0)
        profitPct = (currentPrice - entryPrice) / entryPrice * 100 if entryPrice > 0 else 0
        bearishCrossExitReason: str = ''
        bearishCrossDidAction: bool = False

        canReverseToShort = reverseOnRSISlopeCross and enableRSISlopeCrossEntry and entryOutsideNTZ and lastBarFilterShort
        if canReverseToShort:
            bearishCrossDidAction = True
            suppressLongPositionLogic = True
            standardTrailLong = na
            standardTrailInitBarLong = -1
            standardEntryPriceLong = na
            divTrailLong = na
            divTrailInitBarLong = -1
            divEntryPrice = na
            oscTrailLong = na
            oscTrailInitBarLong = -1
            oscEntryPrice = na
            qty = getPositionSize()
            strategy.close('Long', comment='Exit: RSI-Slope Cross (Reversal to Short)')
            strategy.entry('Short', strategy.short, qty=qty, comment='RSI-Slope Cross Short')
            bearishCrossExitReason = 'Reversed to Short (RSI-Slope Cross)'

            isRSIDivergenceLong = False
            isRSIDivergenceShort = False
            isRSISlopeOscLong = False
            isRSISlopeOscShort = False
            isAccelerationLong = False
            isAccelerationShort = False
            entryBarShort = bar_index
            entryBarLong = 0
            exitConfirmCountLong = 0
            exitConfirmCountShort = 0
        else:
            bearishCrossDidAction = True
            suppressLongPositionLogic = True
            standardTrailLong = na
            standardTrailInitBarLong = -1
            standardEntryPriceLong = na
            divTrailLong = na
            divTrailInitBarLong = -1
            divEntryPrice = na
            oscTrailLong = na
            oscTrailInitBarLong = -1
            oscEntryPrice = na
            strategy.close('Long', comment='Exit: RSI-Slope Cross (Close Only)')
            bearishCrossExitReason = 'RSI-Slope Cross (Close; short last-bar filter blocked reversal)' if reverseOnRSISlopeCross and enableRSISlopeCrossEntry and entryOutsideNTZ and (not lastBarFilterShort) else 'RSI-Slope Cross (Close)'

            isRSIDivergenceLong = False
            isRSISlopeOscLong = False
            isAccelerationLong = False
            entryBarLong = 0
            exitConfirmCountLong = 0

        if bearishCrossDidAction:
            waitingForBearishCrossConfirmation = False
            waitingForBullishCrossConfirmation = False

            alertMsg = '🟡 LONG EXIT (RSI-Slope Cross)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + bearishCrossExitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

    if strategy.position_size < 0 and (not suppressShortPositionLogic) and rsiSlopeCrossBullish:
        entryPrice = strategy.opentrades.entry_price(0)
        posSize = strategy.position_size
        currentPrice = close
        profit = strategy.opentrades.profit(0)
        profitPct = (entryPrice - currentPrice) / entryPrice * 100 if entryPrice > 0 else 0
        bullishCrossExitReason: str = ''
        bullishCrossDidAction: bool = False

        canReverseToLong = reverseOnRSISlopeCross and enableRSISlopeCrossEntry and entryOutsideNTZ and lastBarFilterLong
        if canReverseToLong:
            bullishCrossDidAction = True
            suppressShortPositionLogic = True
            standardTrailShort = na
            standardTrailInitBarShort = -1
            standardEntryPriceShort = na
            divTrailShort = na
            divTrailInitBarShort = -1
            divEntryPrice = na
            oscTrailShort = na
            oscTrailInitBarShort = -1
            oscEntryPrice = na
            qty = getPositionSize()
            strategy.close('Short', comment='Exit: RSI-Slope Cross (Reversal to Long)')
            strategy.entry('Long', strategy.long, qty=qty, comment='RSI-Slope Cross Long')
            bullishCrossExitReason = 'Reversed to Long (RSI-Slope Cross)'

            isRSIDivergenceLong = False
            isRSIDivergenceShort = False
            isRSISlopeOscLong = False
            isRSISlopeOscShort = False
            isAccelerationLong = False
            isAccelerationShort = False
            entryBarLong = bar_index
            entryBarShort = 0
            exitConfirmCountLong = 0
            exitConfirmCountShort = 0
        else:
            bullishCrossDidAction = True
            suppressShortPositionLogic = True
            standardTrailShort = na
            standardTrailInitBarShort = -1
            standardEntryPriceShort = na
            divTrailShort = na
            divTrailInitBarShort = -1
            divEntryPrice = na
            oscTrailShort = na
            oscTrailInitBarShort = -1
            oscEntryPrice = na
            strategy.close('Short', comment='Exit: RSI-Slope Cross (Close Only)')
            bullishCrossExitReason = 'RSI-Slope Cross (Close; long last-bar filter blocked reversal)' if reverseOnRSISlopeCross and enableRSISlopeCrossEntry and entryOutsideNTZ and (not lastBarFilterLong) else 'RSI-Slope Cross (Close)'

            isRSIDivergenceShort = False
            isRSISlopeOscShort = False
            isAccelerationShort = False
            entryBarShort = 0
            exitConfirmCountShort = 0

        if bullishCrossDidAction:
            waitingForBearishCrossConfirmation = False
            waitingForBullishCrossConfirmation = False

            alertMsg = '🟡 SHORT EXIT (RSI-Slope Cross)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + bullishCrossExitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

    if strategy.position_size > 0 and (not suppressLongPositionLogic) and enableRSISlopeOscillator and isRSISlopeOscLong and (barsSinceEntryLong > 0):
        oppositeSignalExit = rsiSlopeOscShort
        trailStopExit = barsSinceEntryLong > oscTrailingStopGrace and (not na(oscTrailLong)) and (close < oscTrailLong)
        shouldExit = oppositeSignalExit or trailStopExit

        if shouldExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (currentPrice - entryPrice) / entryPrice * 100 if entryPrice > 0 else 0
            exitReason = 'Trailing Stop (ATR)' if trailStopExit else 'Opposite Oscillator Short Signal'
            strategy.close('Long', comment='Exit: RSI-Slope Osc (Trailing Stop)' if trailStopExit else 'Exit: RSI-Slope Osc (Opposite Short Signal)')

            alertMsg = '🟡 LONG EXIT (RSI-Slope Oscillator)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + exitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

            if trailStopExit:
                isRSISlopeOscLong = False
                isAccelerationLong = False
                entryBarLong = 0

    if strategy.position_size < 0 and (not suppressShortPositionLogic) and enableRSISlopeOscillator and isRSISlopeOscShort and (barsSinceEntryShort > 0):
        oppositeSignalExit = rsiSlopeOscLong
        trailStopExit = barsSinceEntryShort > oscTrailingStopGrace and (not na(oscTrailShort)) and (close > oscTrailShort)
        shouldExit = oppositeSignalExit or trailStopExit

        if shouldExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (entryPrice - currentPrice) / entryPrice * 100 if entryPrice > 0 else 0
            exitReason = 'Trailing Stop (ATR)' if trailStopExit else 'Opposite Oscillator Long Signal'
            strategy.close('Short', comment='Exit: RSI-Slope Osc (Trailing Stop)' if trailStopExit else 'Exit: RSI-Slope Osc (Opposite Long Signal)')

            alertMsg = '🟡 SHORT EXIT (RSI-Slope Oscillator)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + exitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'RSI: ' + string.tostring(rsi, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

            if trailStopExit:
                isRSISlopeOscShort = False
                isAccelerationShort = False
                entryBarShort = 0

    if strategy.position_size > 0 and (not suppressLongPositionLogic) and enableRSIDivergence and isRSIDivergenceLong and (barsSinceEntryLong > 0):
        trailStopExit = barsSinceEntryLong > divTrailingStopGrace and (not na(divTrailLong)) and (close < divTrailLong)
        if trailStopExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (currentPrice - entryPrice) / entryPrice * 100 if entryPrice > 0 else 0
            strategy.close('Long', comment='Exit: RSI Divergence (Trailing Stop)')

            alertMsg = '🟡 LONG EXIT (RSI Divergence)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: Trailing Stop (RSI Div)\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

            isRSIDivergenceLong = False
            entryBarLong = 0

    if strategy.position_size > 0 and (not suppressLongPositionLogic) and (not isRSIDivergenceLong or not enableRSIDivergence) and (not isRSISlopeOscLong or not enableRSISlopeOscillator) and (barsSinceEntryLong > 0):
        ntzReentryCondition = enableNTZReentryExit and maDf <= hLineHeight and (maDf[1] > hLineHeight)

        trailStopExit = useTrailingStop and barsSinceEntryLong > standardTrailingStopGrace and (not na(standardTrailLong)) and (close < standardTrailLong)

        ntzReentryConfirmed: bool = False
        if enableNTZReentryExit:
            slopeInNTZ = maDf <= hLineHeight
            if ntzReentryCondition:
                exitConfirmCountLong = 1
            elif slopeInNTZ and exitConfirmCountLong > 0:
                exitConfirmCountLong = exitConfirmCountLong + 1
            else:
                exitConfirmCountLong = 0

            ntzReentryConfirmed = slopeInNTZ and exitConfirmCountLong > exitConfirmBars
        else:
            exitConfirmCountLong = 0
            ntzReentryConfirmed = False
        shouldExit = ntzReentryConfirmed or trailStopExit

        if shouldExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (currentPrice - entryPrice) / entryPrice * 100 if entryPrice > 0 else 0
            exitReason = 'Trailing Stop' if trailStopExit else 'NTZ Re-entry'
            strategy.close('Long', comment='Exit: Standard Long (Trailing Stop)' if trailStopExit else 'Exit: Standard Long (NTZ Re-entry)')

            alertMsg = '🟡 LONG EXIT\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + exitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Confirm Bars: ' + string.tostring(exitConfirmCountLong) + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

            isRSIDivergenceLong = False
            isRSISlopeOscLong = False
            entryBarLong = 0
            exitConfirmCountLong = 0

    if strategy.position_size < 0 and (not suppressShortPositionLogic) and enableRSIDivergence and isRSIDivergenceShort and (barsSinceEntryShort > 0):
        trailStopExit = barsSinceEntryShort > divTrailingStopGrace and (not na(divTrailShort)) and (close > divTrailShort)
        if trailStopExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (entryPrice - currentPrice) / entryPrice * 100 if entryPrice > 0 else 0
            strategy.close('Short', comment='Exit: RSI Divergence (Trailing Stop)')

            alertMsg = '🟡 SHORT EXIT (RSI Divergence)\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: Trailing Stop (RSI Div)\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar_close)

            isRSIDivergenceShort = False
            isAccelerationShort = False
            entryBarShort = 0

    if strategy.position_size < 0 and (not suppressShortPositionLogic) and (not isRSIDivergenceShort or not enableRSIDivergence) and (not isRSISlopeOscShort or not enableRSISlopeOscillator) and (barsSinceEntryShort > 0):
        ntzReentryCondition = enableNTZReentryExit and maDf >= -hLineHeight and (maDf[1] < -hLineHeight)

        trailStopExit = useTrailingStop and barsSinceEntryShort > standardTrailingStopGrace and (not na(standardTrailShort)) and (close > standardTrailShort)

        ntzReentryConfirmed: bool = False
        if enableNTZReentryExit:
            slopeInNTZ = maDf >= -hLineHeight
            if ntzReentryCondition:
                exitConfirmCountShort = 1
            elif slopeInNTZ and exitConfirmCountShort > 0:
                exitConfirmCountShort = exitConfirmCountShort + 1
            else:
                exitConfirmCountShort = 0

            ntzReentryConfirmed = slopeInNTZ and exitConfirmCountShort > exitConfirmBars
        else:
            exitConfirmCountShort = 0
            ntzReentryConfirmed = False
        shouldExit = ntzReentryConfirmed or trailStopExit

        if shouldExit:
            entryPrice = strategy.opentrades.entry_price(0)
            posSize = strategy.position_size
            currentPrice = close
            profit = strategy.opentrades.profit(0)
            profitPct = (entryPrice - currentPrice) / entryPrice * 100 if entryPrice > 0 else 0
            exitReason = 'Trailing Stop' if trailStopExit else 'NTZ Re-entry'
            strategy.close('Short', comment='Exit: Standard Short (Trailing Stop)' if trailStopExit else 'Exit: Standard Short (NTZ Re-entry)')

            alertMsg = '🟡 SHORT EXIT\n' + 'Exit Price: ' + string.tostring(currentPrice, '#.####') + '\n' + 'Entry Price: ' + string.tostring(entryPrice, '#.####') + '\n' + 'Position Size: ' + string.tostring(math.abs(posSize), '#.####') + '\n' + 'Profit: ' + string.tostring(profit, '#.##') + '\n' + 'Profit %: ' + string.tostring(profitPct, '#.##') + '%\n' + 'Exit Reason: ' + exitReason + '\n' + 'EMA Slope: ' + string.tostring(maDf, '#.##') + '\n' + 'Confirm Bars: ' + string.tostring(exitConfirmCountShort) + '\n' + 'Time: ' + string.tostring(time, 'yyyy-MM-dd HH:mm')
            alert(alertMsg, alert.freq_once_per_bar)

            isRSIDivergenceShort = False
            isRSISlopeOscShort = False
            isAccelerationShort = False
            entryBarShort = 0
            exitConfirmCountShort = 0

    cUP = color.rgb(38, 255, 72, 50)
    cUPb = color.rgb(38, 255, 52, 40)
    cLP = color.rgb(255, 20, 20, 40)
    cLPb = color.rgb(229, 18, 18, 40)
    cNTZ = color.rgb(186, 167, 167, 70)
    colorS = cUP if maDf > 0 else cLP if maDf < 0 else cNTZ

    def f_colorN(maDf: Series, maDL, cUP, cUPb, cLP, cLPb, cNTZ):
        colorN = color.rgb(38, 255, 72, 75)
        colorN = cUPb if maDf > 0 and maDf > maDL and (maDf > maDf[1]) else cUP if maDf > 0 and maDf > maDL and (maDf <= maDf[1]) else cNTZ if maDf > 0 and maDf <= maDL else cLPb if maDf <= 0 and maDf < -maDL and (maDf > maDf[1]) else cLP if maDf <= 0 and maDf < -maDL and (maDf <= maDf[1]) else cNTZ if maDf > -maDL else na
        return colorN

    c_ntz = f_colorN(maDf, maDL, cUP, cUPb, cLP, cLPb, cNTZ) if noTZone else colorS
    trspa = 92 if maAcc < accTh else 100 - maAcc * 1.5
    c_Acc = color.rgb(10, 246, 255, trspa) if maAcc > 0.3 * maAcc and close > open else color.rgb(239, 2, 77, trspa) if maAcc > 0.3 * maAcc and close < open else color.rgb(160, 160, 160, trspa)

    hUp = hline(hLineHeight, title='NTZ Top', color=color.rgb(75, 219, 94, 40), linewidth=1, linestyle=hline.style_dashed)
    hDn = hline(-hLineHeight, title='NTZ Bottom', color=color.rgb(244, 34, 34, 40), linewidth=1, linestyle=hline.style_dashed)
    fill(hUp, hDn, color=ntzFillC)
    hline(0, linestyle=hline.style_solid, color=color.rgb(255, 255, 255, 70))
    plot(maDf, 'Diff MA', c_ntz)
    plot(maDf, 'Diff MA fill', c_ntz, style=plot.style_area)
    plot(maAcc, 'MA Accel', color=c_Acc, style=plot.style_circles, linewidth=4)

    rsiPlotColor = (rsiColorHigh if cRsi > 20 else rsiColorLow if cRsi < -20 else rsiColorNeutral) if enableRSIColoring else rsiColorNeutral
    plot(cRsi, 'Centered RSI (RSI-50)', color=rsiPlotColor, linewidth=rsiLineWidth)

    plotshape(showDivergence and bullishDivergence and (bar_index == bullDivBar), 'Bull Div', style=shape.diamond, location=location.bottom, color=color.lime, size=size.tiny)
    plotshape(showDivergence and bearishDivergence and (bar_index == bearDivBar), 'Bear Div', style=shape.diamond, location=location.top, color=color.purple, size=size.tiny)

    plotshape(showSlopeRsiExhaustion and bullishSlopeRsiDiv and (bar_index == bullSlopeRsiBar), 'Bull Slope-RSI Exhaustion', style=shape.triangleup, location=location.bottom, color=color.orange, size=size.tiny)
    plotshape(showSlopeRsiExhaustion and bearishSlopeRsiDiv and (bar_index == bearSlopeRsiBar), 'Bear Slope-RSI Exhaustion', style=shape.triangledown, location=location.top, color=color.yellow, size=size.tiny)

    tableLeftMarginPct: int = 6
    slopeRsiTable: Persistent[Table] = table.new(position.bottom_left, 3, 5, bgcolor=color.rgb(30, 30, 30), border_width=1, border_color=color.rgb(80, 80, 80), frame_color=color.rgb(90, 90, 90), frame_width=1, force_overlay=False)

    if barstate.islast or barstate.islastconfirmedhistory:
        marginBg = color.new(color.black, 100)

        table.cell(slopeRsiTable, 0, 0, '', bgcolor=marginBg, width=tableLeftMarginPct, text_size=size.small)
        table.cell(slopeRsiTable, 0, 1, '', bgcolor=marginBg, width=tableLeftMarginPct, text_size=size.small)
        table.cell(slopeRsiTable, 0, 2, '', bgcolor=marginBg, width=tableLeftMarginPct, text_size=size.small)
        table.cell(slopeRsiTable, 0, 3, '', bgcolor=marginBg, width=tableLeftMarginPct, text_size=size.small)
        table.cell(slopeRsiTable, 0, 4, '', bgcolor=marginBg, width=tableLeftMarginPct, text_size=size.small)

        table.cell(slopeRsiTable, 1, 0, 'Metric', text_color=color.white, bgcolor=color.rgb(40, 40, 40), text_size=size.small)
        table.cell(slopeRsiTable, 2, 0, 'Value', text_color=color.white, bgcolor=color.rgb(40, 40, 40), text_size=size.small)

        slopeColor = color.green if maDf > hLineHeight else color.red if maDf < -hLineHeight else color.gray
        table.cell(slopeRsiTable, 1, 1, 'Slope', text_color=color.white, bgcolor=color.rgb(60, 60, 60), text_size=size.small)
        table.cell(slopeRsiTable, 2, 1, string.tostring(maDf, '#.##'), text_color=slopeColor, bgcolor=color.rgb(60, 60, 60), text_size=size.small)

        cRsiColor = color.red if cRsi > 20 else color.green if cRsi < -20 else color.white
        table.cell(slopeRsiTable, 1, 2, 'cRSI', text_color=color.white, bgcolor=color.rgb(60, 60, 60), text_size=size.small)
        table.cell(slopeRsiTable, 2, 2, string.tostring(cRsi, '#.##'), text_color=cRsiColor, bgcolor=color.rgb(60, 60, 60), text_size=size.small)

        gapOverThreshold = minDivergenceGap > 0 and divergenceGap >= minDivergenceGap
        gapTextColor = color.yellow if gapOverThreshold else color.white
        gapBgColor = color.rgb(80, 80, 0) if gapOverThreshold else color.rgb(60, 60, 60)
        table.cell(slopeRsiTable, 1, 3, 'Gap', text_color=color.white, bgcolor=gapBgColor, text_size=size.small)
        table.cell(slopeRsiTable, 2, 3, string.tostring(divergenceGap, '#.##'), text_color=gapTextColor, bgcolor=gapBgColor, text_size=size.small)

        tableProfitPct: float = na(float)
        if strategy.position_size != 0:
            entryPrice = strategy.opentrades.entry_price(0)
            if strategy.position_size > 0:
                tableProfitPct = (close - entryPrice) / entryPrice * 100
            else:
                tableProfitPct = (entryPrice - close) / entryPrice * 100

        profitPctColor = color.gray if na(tableProfitPct) else color.green if tableProfitPct >= 0 else color.red
        profitPctText = 'N/A' if na(tableProfitPct) else string.tostring(tableProfitPct, '#.##') + '%'
        table.cell(slopeRsiTable, 1, 4, 'P/L %', text_color=color.white, bgcolor=color.rgb(60, 60, 60), text_size=size.small)
        table.cell(slopeRsiTable, 2, 4, profitPctText, text_color=profitPctColor, bgcolor=color.rgb(60, 60, 60), text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
