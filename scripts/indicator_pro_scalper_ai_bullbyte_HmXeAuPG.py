"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, barstate, close, color, fill, high, input, location, low, math,
    na, nz, open, plot, plotshape, position, request, script, shape, size, string, syminfo, ta,
    table, volume
)
from pynecore.types import Persistent, PersistentSeries, Series, Table


@script.indicator(" Pro Scalper AI [BullByte]", overlay=False, dynamic_requests=True, max_labels_count=500, max_lines_count=500)
def main(
    useHTF=input.bool(False, "Use Higher Timeframe Trend Filter?", inline="HTF"),
    htf_tf=input.timeframe("15", "HTF", inline="HTF"),
    useMACDFilter=input.bool(False, "Use MACD Filter?"),
    usePinbarFilter=input.bool(False, "Use Pinbar Filter?"),
    adxLen=input.int(14, "ADX Length"),
    diLen=input.int(14, "DI Length"),
    atrLen=input.int(14, "ATR Length"),
    hmaLen=input.int(21, "HMA Length"),
    momChoice=input.string("Stochastic RSI", "Momentum Mode", options=("Stochastic RSI", "Fisher RSI", "Williams %R")),
    stochRsiLen=input.int(12, "Stoch RSI Length", group="Stoch RSI"),
    stochKLen=input.int(3, "Stoch RSI %K Smoothing", group="Stoch RSI"),
    stochDLen=input.int(3, "Stoch RSI %D Smoothing", group="Stoch RSI"),
    fisherRsiLen=input.int(14, "Fisher RSI Length", group="Fisher RSI"),
    wprLen=input.int(14, "Williams %R Length", group="Williams %R"),
    tdiRsiLen=input.int(13, "TDI RSI Length"),
    tdiSignalLen=input.int(7, "TDI Signal Length"),
    wTrend=input.float(0.3, "Trend Weight", step=0.1),
    wMomentum=input.float(0.3, "Momentum Weight", step=0.1),
    wVolatility=input.float(0.2, "Volatility Weight", step=0.1),
    wVolume=input.float(0.2, "Volume Weight", step=0.1),
    baseUpper=input.float(25.0, "Base Upper Threshold", step=0.1),
    baseLower=input.float(-25.0, "Base Lower Threshold", step=0.1),
    dynMultiplier=input.float(0.5, "Dynamic Threshold Multiplier", step=0.1),
    oscLookback=input.int(50, "Oscillator Std Dev Lookback"),
    useHysteresis=input.bool(True, "Use Adaptive Hysteresis?"),
    baseHystGap=input.float(1.0, "Base Hysteresis Gap", step=0.1),
    hystMultiplier=input.float(1.0, "Hysteresis Volatility Multiplier", step=0.1),
    useDynamicW=input.bool(True, "Use Dynamic Weighting?"),
    maxVolFactor=input.float(2.0, "Max Volatility Factor", step=0.1),
    maxTrendFactor=input.float(1.5, "Max Trend Factor", step=0.1),
    volLookback=input.int(50, "Volume Lookback"),
    useAI=input.bool(False, "Use AI Forecast?"),
    ai_length=input.int(20, "AI Length", minval=1),
    ai_future=input.int(2, "AI Forecast Bars Ahead", minval=1),
    aiAdjustment=input.float(1.5, "AI Threshold Shift", step=0.1),
    aiSmoothing=input.bool(True, "Smooth AI Forecast?"),
    useLatching=input.bool(True, "Enable Latching?"),
    dashboardSizeOption=input.string(title="Dashboard Text Size", defval="Normal", options=("Tiny", "Small", "Normal", "Large"))
):
    def f_nr(src: Series):
        return src if barstate.isconfirmed else nz(src[1])

    cOpen = f_nr(open)
    cHigh = f_nr(high)
    cLow = f_nr(low)
    cClose: Series = f_nr(close)
    cVolume = f_nr(volume)
    textSizeEnum = size.tiny if dashboardSizeOption == 'Tiny' else size.small if dashboardSizeOption == 'Small' else size.normal if dashboardSizeOption == 'Normal' else size.large

    def f_tr(_high, _low, _close: Series):
        return math.max(_high - _low, math.abs(_high - nz(_close[1])), math.abs(_low - nz(_close[1])))

    def dirmov(_len):
        up = ta.change(cHigh)
        down = -ta.change(cLow)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        tr = f_tr(cHigh, cLow, cClose)
        truerange = ta.rma(tr, _len)
        plusVal = nz(100 * ta.rma(plusDM, _len) / truerange)
        minusVal = nz(100 * ta.rma(minusDM, _len) / truerange)
        return (plusVal, minusVal)

    diplus, diminus = dirmov(diLen)
    adxVal = 100 * ta.rma(math.abs(diplus - diminus) / (1 if diplus + diminus == 0 else diplus + diminus), adxLen)
    trendDir = 1.0 if diplus > diminus else -1.0 if diminus > diplus else 0.0
    normTrend = trendDir * math.min(math.max((adxVal - 20) / 20, 0.0), 1.0)
    confirmedADX: Series = f_nr(adxVal)
    confirmedNormTrend = f_nr(normTrend)

    atrVal = ta.rma(f_tr(cHigh, cLow, cClose), atrLen)
    normATR = atrVal / cClose
    normVolatilityRaw = normATR * 2 - 1
    confirmedNormVolatility = f_nr(normVolatilityRaw)

    def f_tanh(_x):
        e2x = math.exp(2.0 * _x)
        return (e2x - 1.0) / (e2x + 1.0)

    def f_stochRsi(_len, _k, _d):
        _rsi = ta.rsi(cClose, _len)
        lowestVal = ta.lowest(_rsi, _len)
        highestVal = ta.highest(_rsi, _len)
        stochVal = (_rsi - lowestVal) / math.max(highestVal - lowestVal, 0.0001)
        K = ta.sma(stochVal, _k)
        return (K - 0.5) * 2

    def f_fisherRsi(_len):
        _rsi = ta.rsi(cClose, _len)
        normRsi = _rsi / 100.0 * 2 - 1
        clipped = math.max(math.min(normRsi, 0.999), -0.999)
        fish = 0.5 * math.log((1 + clipped) / (1 - clipped))
        return f_tanh(fish)

    def f_wpr(_len):
        highestHigh = ta.highest(cHigh, _len)
        lowestLow = ta.lowest(cLow, _len)
        wprVal = (highestHigh - cClose) / math.max(highestHigh - lowestLow, 0.0001) * -100
        return (wprVal + 50) / 50 - 1

    momentumVal: float = 0.0
    if momChoice == 'Mode 1':
        momentumVal = f_stochRsi(stochRsiLen, stochKLen, stochDLen)
    elif momChoice == 'Mode 2':
        momentumVal = f_fisherRsi(fisherRsiLen)
    elif momChoice == 'Mode 3':
        momentumVal = f_wpr(wprLen)
    confirmedMomentum = f_nr(momentumVal)

    tdiRsi = ta.rsi(cClose, tdiRsiLen)
    tdiSignal = ta.ema(tdiRsi, tdiSignalLen)
    confirmedTdiRsi = f_nr(tdiRsi)
    confirmedTdiSignal = f_nr(tdiSignal)

    def f_calcOBV():
        __hist_cClose__: Series = cClose[0]
        obv: PersistentSeries[float] = 0.0
        obv = nz(obv[1]) + (cVolume if cClose > __hist_cClose__[1] else -cVolume if cClose < __hist_cClose__[1] else 0)
        return obv

    obvVal = f_calcOBV()
    obvMin = ta.lowest(obvVal, volLookback)
    obvMax = ta.highest(obvVal, volLookback)
    normVolumeRaw = (obvVal - obvMin) / math.max(obvMax - obvMin, 0.0001) * 2 - 1
    confirmedVolumeNorm: Series = f_nr(normVolumeRaw)

    volFactor: float = 1.0
    trendFactor: float = 1.0
    if useDynamicW:
        baseVol: float = 0.005
        ratioVol = normATR / baseVol
        volFactor = math.min(ratioVol, maxVolFactor)
        baseAdx: float = 25.0
        ratioAdx = adxVal / baseAdx
        trendFactor = math.min(ratioAdx, maxTrendFactor)
    effWTrend = wTrend * trendFactor
    effWVolatility = wVolatility * volFactor
    effWMomentum = wMomentum
    effWVolume = wVolume
    totalWeight = effWTrend + effWMomentum + effWVolatility + effWVolume

    oscillatorRaw = (effWTrend * confirmedNormTrend + effWMomentum * confirmedMomentum + effWVolatility * confirmedNormVolatility + effWVolume * confirmedVolumeNorm) / totalWeight
    oscillator = oscillatorRaw * 100
    confirmedOscillator = f_nr(oscillator)
    oscStd = ta.stdev(confirmedOscillator, oscLookback)
    upperThreshold = baseUpper + oscStd * dynMultiplier
    lowerThreshold = baseLower - oscStd * dynMultiplier
    confirmedUpperThreshold = f_nr(upperThreshold)
    confirmedLowerThreshold = f_nr(lowerThreshold)

    aiOsc_current: float = na(float)
    aiOsc: float = na(float)
    ai_bias: float = 0.0
    if useAI:
        ai_value = ta.linreg(cClose, ai_length, 0)
        ai_slope = ai_value - ta.linreg(cClose, ai_length, 1)
        ai_pred = ai_value + ai_slope * ai_future
        ai_pred_smooth = ta.sma(ai_pred, 2) if aiSmoothing else ai_pred
        osc_lb = ta.lowest(confirmedOscillator, ai_length)
        osc_hb = ta.highest(confirmedOscillator, ai_length)
        ai_lb = ta.lowest(ai_pred_smooth, ai_length)
        ai_hb = ta.highest(ai_pred_smooth, ai_length)
        osc_range = math.max(osc_hb - osc_lb, 0.001)
        ai_range = math.max(ai_hb - ai_lb, 0.001)
        aiOsc = (ai_pred_smooth - ai_lb) / ai_range * osc_range + osc_lb
        ai_value_lb = ta.lowest(ai_value, ai_length)
        ai_value_hb = ta.highest(ai_value, ai_length)
        ai_value_range = math.max(ai_value_hb - ai_value_lb, 0.001)
        aiOsc_current = (ai_value - ai_value_lb) / ai_value_range * osc_range + osc_lb
        osc_mid = (baseUpper + baseLower) / 2
        ai_bias = aiOsc - osc_mid
    confirmedAiBias = f_nr(ai_bias)
    adjustedUpperThreshold = confirmedUpperThreshold + (aiAdjustment if confirmedAiBias > 0 else 0) if useAI else confirmedUpperThreshold
    adjustedLowerThreshold = confirmedLowerThreshold + (-aiAdjustment if confirmedAiBias < 0 else 0) if useAI else confirmedLowerThreshold
    confirmedAdjustedUpperThreshold = f_nr(adjustedUpperThreshold)
    confirmedAdjustedLowerThreshold = f_nr(adjustedLowerThreshold)

    def hma(src, length):
        wma1 = ta.wma(src, length)
        wma2 = ta.wma(src, math.round(length / 2))
        diff = 2 * wma2 - wma1
        return ta.wma(diff, math.round(math.sqrt(length)))

    localHMA = hma(cClose, hmaLen)
    trendHMA = 1.0 if cClose > localHMA else -1.0 if cClose < localHMA else 0.0
    confirmedTrendHMA = f_nr(trendHMA)

    htfTrend: float = 0.0
    if useHTF:
        htfHMA = request.security(syminfo.tickerid, htf_tf, hma(cClose, hmaLen), lookahead=barmerge.lookahead_off)
        htfTrend = 0.0 if na(htfHMA) else 1.0 if cClose > htfHMA else -1.0 if cClose < htfHMA else 0.0
    confirmedHTFTrend = f_nr(htfTrend)

    condStrongBuy = confirmedOscillator > confirmedAdjustedUpperThreshold and confirmedTrendHMA > 0 and (not useHTF or confirmedHTFTrend > 0) and (confirmedADX > 20)
    condStrongSell = confirmedOscillator < confirmedAdjustedLowerThreshold and confirmedTrendHMA < 0 and (not useHTF or confirmedHTFTrend < 0) and (confirmedADX > 20)
    condEarlyBuy = confirmedOscillator > baseUpper and confirmedOscillator < confirmedAdjustedUpperThreshold
    condEarlySell = confirmedOscillator < baseLower and confirmedOscillator > confirmedAdjustedLowerThreshold

    immediateSignal: str = "No Signal"
    if condStrongBuy:
        immediateSignal = "Strong Buy"
    elif condStrongSell:
        immediateSignal = "Strong Sell"
    elif condEarlyBuy:
        immediateSignal = "Early Buy"
    elif condEarlySell:
        immediateSignal = "Early Sell"

    storedState: Persistent[str] = "Neutral"
    if useLatching and barstate.isconfirmed:
        if storedState == 'Neutral':
            if condEarlyBuy:
                storedState = "EarlyBuy"
            elif condEarlySell:
                storedState = "EarlySell"
            elif condStrongBuy:
                storedState = "Long"
            elif condStrongSell:
                storedState = "Short"
        elif storedState == 'EarlyBuy':
            if condStrongBuy:
                storedState = "Long"
            elif not condEarlyBuy:
                storedState = "Neutral"
        elif storedState == 'Long':
            if condStrongSell:
                storedState = "Short"
            elif condEarlySell:
                storedState = "EarlySell"
        elif storedState == 'EarlySell':
            if condStrongSell:
                storedState = "Short"
            elif not condEarlySell:
                storedState = "Neutral"
        elif storedState == 'Short':
            if condStrongBuy:
                storedState = "Long"
            elif condEarlyBuy:
                storedState = "EarlyBuy"

    storedSignal = 'Strong Buy' if storedState == 'Long' else 'Strong Sell' if storedState == 'Short' else 'Early Buy' if storedState == 'EarlyBuy' else 'Early Sell' if storedState == 'EarlySell' else 'No Signal'

    plotOsc = plot(confirmedOscillator, color=color.green if confirmedOscillator >= 0 else color.red, linewidth=2, title='Composite Oscillator')
    plotZero = plot(0, color=color.gray, title='Zero Line')
    plotUpper = plot(confirmedUpperThreshold, color=color.purple, linewidth=1, title='Dynamic Upper Threshold')
    plotLower = plot(confirmedLowerThreshold, color=color.purple, linewidth=1, title='Dynamic Lower Threshold')

    activeSignal = storedSignal if useLatching else immediateSignal
    fillColor = color.new(color.green, 80) if activeSignal == 'Strong Buy' else color.new(color.red, 80) if activeSignal == 'Strong Sell' else color.new(color.lime, 80) if activeSignal == 'Early Buy' else color.new(color.maroon, 80) if activeSignal == 'Early Sell' else color.new(color.blue, 90)

    fill(plotUpper, plotLower, color=fillColor, title='Band Background')

    immediateStrongBuy = not useLatching and immediateSignal == 'Strong Buy'
    immediateStrongSell = not useLatching and immediateSignal == 'Strong Sell'
    immediateEarlyBuy = not useLatching and immediateSignal == 'Early Buy'
    immediateEarlySell = not useLatching and immediateSignal == 'Early Sell'

    plotshape(immediateStrongBuy, style=shape.circle, color=color.green, title='Immediate Strong Buy', location=location.bottom, size=size.tiny)
    plotshape(immediateStrongSell, style=shape.circle, color=color.red, title='Immediate Strong Sell', location=location.top, size=size.tiny)
    plotshape(immediateEarlyBuy, style=shape.cross, color=color.lime, title='Immediate Early Buy', location=location.bottom, size=size.tiny)
    plotshape(immediateEarlySell, style=shape.cross, color=color.maroon, title='Immediate Early Sell', location=location.top, size=size.tiny)

    latchedStrongBuy = useLatching and storedState == 'Long'
    latchedStrongSell = useLatching and storedState == 'Short'
    latchedEarlyBuy = useLatching and storedState == 'EarlyBuy'
    latchedEarlySell = useLatching and storedState == 'EarlySell'

    plotshape(latchedStrongBuy, style=shape.triangleup, color=color.green, title='Latched Strong Buy', location=location.bottom, size=size.tiny)
    plotshape(latchedStrongSell, style=shape.triangledown, color=color.red, title='Latched Strong Sell', location=location.top, size=size.tiny)
    plotshape(latchedEarlyBuy, style=shape.diamond, color=color.lime, title='Latched Early Buy', location=location.bottom, size=size.tiny)
    plotshape(latchedEarlySell, style=shape.diamond, color=color.maroon, title='Latched Early Sell', location=location.top, size=size.tiny)

    plot(confirmedAiBias if useAI else na, color=color.blue, title='AI Bias')

    adxDiff = 0 if na(confirmedADX[1]) else confirmedADX - confirmedADX[1]

    adxArrow = '⬆️' if adxDiff > 0 else '⬇️' if adxDiff < 0 else ''

    volDiff = 0 if na(confirmedVolumeNorm[1]) else confirmedVolumeNorm - confirmedVolumeNorm[1]

    volArrow = '⬆️' if volDiff > 0 else '⬇️' if volDiff < 0 else ''

    dash: Persistent[Table] = table.new(position.top_right, 3, 9, border_width=1)
    def f_getCellColor(value):
        return color.new(color.green, 70) if value > 0 else color.new(color.red, 70) if value < 0 else color.new(color.gray, 80)

    if barstate.isconfirmed:
        table.cell(dash, 0, 0, 'ADX', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 0, string.tostring(confirmedADX, '#.##') + ' ' + adxArrow, text_color=color.white, bgcolor=color.new(color.green, 70) if confirmedADX > 25 else color.new(color.red, 70), text_size=textSizeEnum)
        table.cell(dash, 0, 1, 'Osc', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 1, string.tostring(confirmedOscillator, '#.##'), text_color=color.white, bgcolor=f_getCellColor(confirmedOscillator), text_size=textSizeEnum)

        table.cell(dash, 0, 2, 'Mom Mode', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 2, '1' if momChoice == 'Mode 1' else '2' if momChoice == 'Mode 2' else '3', text_color=color.white, bgcolor=color.new(color.gray, 80), text_size=textSizeEnum)

        table.cell(dash, 0, 3, 'TrendHMA', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 3, 'Bullish' if confirmedTrendHMA > 0 else 'Bearish' if confirmedTrendHMA < 0 else 'Flat', text_color=color.white, bgcolor=color.new(color.green, 70) if confirmedTrendHMA > 0 else color.new(color.red, 70) if confirmedTrendHMA < 0 else color.new(color.gray, 80), text_size=textSizeEnum)

        table.cell(dash, 0, 4, 'HTF Trend', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        htfText = ('Bullish' if confirmedHTFTrend > 0 else 'Bearish' if confirmedHTFTrend < 0 else 'Flat') if useHTF else 'Off'
        table.cell(dash, 1, 4, htfText, text_color=color.white, bgcolor=color.new(color.green, 70) if confirmedHTFTrend > 0 else color.new(color.red, 70) if confirmedHTFTrend < 0 else color.new(color.gray, 80), text_size=textSizeEnum)

        table.cell(dash, 0, 5, 'VolFactor', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 5, string.tostring(volFactor, '#.##'), text_color=color.white, bgcolor=color.new(color.green, 70) if volFactor > 1 else color.new(color.gray, 80), text_size=textSizeEnum)

        table.cell(dash, 0, 6, 'Signal', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        activeSig = storedSignal if useLatching else immediateSignal
        table.cell(dash, 1, 6, activeSig, text_color=color.white, bgcolor=color.new(color.green, 70) if activeSig == 'Strong Buy' else color.new(color.red, 70) if activeSig == 'Strong Sell' else color.new(color.gray, 80), text_size=textSizeEnum)

        table.cell(dash, 0, 7, 'AI Bias', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        aiText = string.tostring(confirmedAiBias, '#.##') if useAI else 'Disabled'
        table.cell(dash, 1, 7, aiText, text_color=color.white, bgcolor=f_getCellColor(confirmedAiBias), text_size=textSizeEnum)

        table.cell(dash, 0, 8, 'Volume', text_color=color.white, bgcolor=color.black, text_size=textSizeEnum)
        table.cell(dash, 1, 8, string.tostring(confirmedVolumeNorm, '#.##') + ' ' + volArrow, text_color=color.white, bgcolor=f_getCellColor(confirmedVolumeNorm), text_size=textSizeEnum)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
