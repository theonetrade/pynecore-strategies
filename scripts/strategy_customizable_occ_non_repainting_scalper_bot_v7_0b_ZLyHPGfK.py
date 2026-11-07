"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barcolor, barmerge, barstate, close, color, fill, format,
    input, label, math, na, nz, open, plot, request, script, size, strategy, string, syminfo, ta,
    time, timeframe, timenow, yloc
)
from pynecore.types import Color, Series


@script.strategy(title='Open Open Cross Strategy R7.1b revised by MZ', shorttitle='OCC Strategy R7.1', overlay=True, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_every_tick=True, process_orders_on_close=True, commission_value=0.08, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    useRes=input(defval=True, title='Use Alt Res?', group='Strategy', inline='1', tooltip='This Strategy modified to use LONG only'),
    intRes=input(defval=3, title='Mult Res', group='Strategy', inline='1'),
    calcOffset=input(defval=0, title='Interval Offset', group='Strategy', inline='1'),
    offset=input(defval=0, title='Cross Offset', group='Strategy', inline='1'),
    basisType=input.string(defval='TEMA', title='MA Type: ', group='Basis', inline='1', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HullMA', 'LSMA', 'ALMA', 'SSMA', 'TMA')),
    basisLen=input.int(defval=8, title='MA Period', minval=1, group='Basis', inline='1'),
    offsetSigma=input.int(defval=6, title='Offset LSMA/Sigma ALMA', minval=0, group='Basis', inline='2'),
    offsetALMA=input.float(defval=0.85, title='Offset ALMA', minval=0, step=0.01, group='Basis', inline='2'),
    scolor=input(True, title='Show Trend?', group='Basis', inline='3'),
    enableTrailing=input.bool(defval=True, title='Trailing', tooltip='Enable or disable the trailing for take profit.', group='Trailing Profit', inline='1'),
    __input_10__=input.float(title='Long TP (%)', minval=0.0, step=0.1, defval=4, group='Trailing Profit', inline='1'),
    __input_11__=input.float(defval=0.5, title='TTP Dev %%', minval=0.01, maxval=100, step=0.1, tooltip='The step to follow the price when the take profit limit is reached.', group='Trailing Profit', inline='1'),
    __input_12__=input.float(6, title='Fixed SL (%)', minval=0.0, step=0.1, tooltip='Use 100 to turn off - Stop loss % even if ATR did not catch it'),
    useVariantFilter=input.bool(False, title='Use MA', group='Filters', inline='1'),
    VariantFilterType=input.string(defval='LSMA', title='Type: ', group='Filters', inline='1', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HullMA', 'LSMA', 'ALMA', 'SSMA', 'TMA')),
    VariantTimeFrame=input.timeframe(defval='3', title='TF: ', group='Filters', inline='1'),
    VariantFilterLength=input.int(20, minval=1, title='Len', group='Filters', inline='1'),
    useRSI=input.bool(False, title='Use RSI', group='Filters', inline='2'),
    rsiTimeFrame=input.timeframe(defval='30', title='TF: ', group='Filters', inline='2'),
    RSILength=input.int(20, minval=1, title='RSI Length', group='Filters', inline='2'),
    aboveRSIFilter=input.int(40, minval=1, title='Buy Above RSI', group='Filters', inline='2'),
    belowRSIFilter=input.int(75, minval=1, title='Buy Below RSI', group='Filters', inline='2'),
    useATR=input.bool(False, title='Use ATR', group='Filters', inline='3'),
    ATRLength=input.int(34, minval=1, title='ATR Length', group='Filters', inline='3'),
    minATR=input.float(0, title='Min ATR', minval=0.0, step=0.001, group='Filters', inline='3', tooltip='Use 0 to turn off - can remove periods of low volatility where less likely profitable'),
    useADX=input.bool(True, title='Use ADX', group='Filters', inline='adx1'),
    useDiplus=input.bool(False, title='Uptrend Only', group='Filters', inline='adx1'),
    adxTF=input.timeframe('5', title='ADX TF', group='Filters', inline='adx1_2'),
    length=input(14, title='Length', group='Filters', inline='adx1_2'),
    smoothing=input(40, title='Smooth', group='Filters', inline='adx1_2'),
    adxMin=input(20, title='Min', group='Filters', inline='adx1_2'),
    adxMax=input(100, title='Max', group='Filters', inline='adx1_2'),
    useADX2=input.bool(False, title='Use ADX2', group='Filters', inline='Adx2'),
    useDiplus2=input.bool(False, title='Uptrend Only', group='Filters', inline='Adx2', tooltip='If you want to use a second ADX filter for a higher time frame, etc'),
    adxTF2=input.timeframe('5', title='ADX TF', group='Filters', inline='Adx23'),
    length2=input(14, title='Length', group='Filters', inline='Adx23'),
    smoothing2=input(40, title='Smooth', group='Filters', inline='Adx23'),
    adxMin2=input(20, title='Min', group='Filters', inline='Adx23'),
    adxMax2=input(100, title='Max', group='Filters', inline='Adx23'),
    ebar=input.int(defval=10000, title='Number of Bars for Back Testing', minval=0),
    dummy=input(False, title='- SET to ZERO for Daily or Longer Timeframes'),
    olc=input.string(title='Open Long Comment', defval='', group='Strategy', inline='2'),
    clc=input.string(title='Close Long Comment', defval='', group='Strategy', inline='2')
):
    def reso(exp: Series, use, res):
        security_1 = inline_series(request.security(syminfo.tickerid, res, exp[0 if barstate.isconfirmed else 1], gaps=barmerge.gaps_off), 0 if barstate.isconfirmed else 1)
        return security_1 if use else exp[0 if barstate.isconfirmed else 1]

    def rp_security(_symbol, _res, _src: Series):
        return inline_series(request.security(_symbol, _res, _src[0 if barstate.isconfirmed else 1]), 0 if barstate.isconfirmed else 1)

    def rp_security_merged(_symbol, _res, _src: Series):
        return inline_series(request.security(_symbol, _res, _src[0 if barstate.isconfirmed else 1], gaps=barmerge.gaps_on), 0 if barstate.isconfirmed else 1)

    def variant(type, src: Series, len, offSig, offALMA):
        v1 = ta.sma(src, len)
        v2 = ta.ema(src, len)
        v3 = 2 * v2 - ta.ema(v2, len)
        v4 = 3 * (v2 - ta.ema(v2, len)) + ta.ema(ta.ema(v2, len), len)
        v5 = ta.wma(src, len)
        v6 = ta.vwma(src, len)
        v7: Series[float] = 0.0
        sma_1 = ta.sma(src, len)
        v7 = sma_1 if na(v7[1]) else (v7[1] * (len - 1) + src) / len
        v8 = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        v9 = ta.linreg(src, len, offSig)
        v10 = ta.alma(src, len, offALMA, offSig)
        v11 = ta.sma(v1, len)
        a1 = math.exp(-1.414 * 3.14159 / len)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / len)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        v12: Series[float] = 0.0
        v12 = c1 * (src + nz(src[1])) / 2 + c2 * nz(v12[1]) + c3 * nz(v12[2])
        return v2 if type == 'EMA' else v3 if type == 'DEMA' else v4 if type == 'TEMA' else v5 if type == 'WMA' else v6 if type == 'VWMA' else v7 if type == 'SMMA' else v8 if type == 'HullMA' else v9 if type == 'LSMA' else v10 if type == 'ALMA' else v11 if type == 'TMA' else v12 if type == 'SSMA' else v1

    stratRes = string.tostring(timeframe.multiplier * intRes, '###M') if timeframe.ismonthly else string.tostring(timeframe.multiplier * intRes, '###W') if timeframe.isweekly else string.tostring(timeframe.multiplier * intRes, '###D') if timeframe.isdaily else string.tostring(timeframe.multiplier * intRes, '####') if timeframe.isintraday else '60'
    delayOffset: int = 0
    tradeType: str = 'LONG'
    longTakeProfitPerc = __input_10__ * 0.01
    trailingTakeProfitDeviationPerc = __input_11__ / 100
    longLossPerc = __input_12__ * 0.01
    longStopPrice = strategy.position_avg_price * (1 - longLossPerc)
    belowStopLoss = strategy.position_avg_price <= longStopPrice
    longTPPrice = strategy.position_avg_price * (1 + longTakeProfitPerc)
    aboveTakeProfit = strategy.position_avg_price >= longTPPrice
    variantFilter = reso(variant(VariantFilterType, close[1 if barstate.isrealtime else 0], VariantFilterLength, offsetSigma, offsetALMA), True, VariantTimeFrame)
    passesVariantFilter = close[1 if barstate.isrealtime else 0] >= variantFilter or not useVariantFilter
    variantFilterP = plot(variantFilter, title='VariantFilter', color=color.blue, linewidth=4, style=plot.style_line)
    rsiTmp = ta.rsi(close[0 if barstate.isconfirmed else 1], RSILength)
    rsi = rp_security(syminfo.tickerid, rsiTimeFrame, rsiTmp)
    passesRSIfilter = rsi <= belowRSIFilter and rsi >= aboveRSIFilter or not useRSI
    atr = ta.atr(ATRLength)
    isAboveATR = atr >= minATR or not useATR
    diplus, diminus, adx = ta.dmi(length, smoothing)
    adxHTF = rp_security(syminfo.tickerid, adxTF, adx)
    diplusHTF = rp_security(syminfo.tickerid, adxTF, diplus)
    diminusHTF = rp_security(syminfo.tickerid, adxTF, diminus)
    diCalc = diplusHTF - diminusHTF
    diEMA = ta.ema(diCalc, 2)
    upTrendTrue = diEMA > 0
    adxMsg = '\ndiplus : ' + string.tostring(diplusHTF) + '\ndiminus : ' + string.tostring(diminusHTF) + '\nadx : ' + string.tostring(adxHTF) + '\ndiEMA: ' + string.tostring(diEMA) + '\ndiUptrend : ' + string.tostring(upTrendTrue)
    passesADXFilters = adxHTF >= adxMin and adxHTF <= adxMax or not useADX
    passUptrendOnlyFilter = upTrendTrue or not useDiplus
    diplus2, diminus2, adx2 = ta.dmi(length2, smoothing2)
    adxHTF2 = rp_security(syminfo.tickerid, adxTF2, adx2)
    diplusHTF2 = rp_security(syminfo.tickerid, adxTF2, diplus2)
    diminusHTF2 = rp_security(syminfo.tickerid, adxTF2, diminus2)
    diCalc2 = diplusHTF2 - diminusHTF2
    diEMA2 = ta.ema(diCalc2, 2)
    upTrendTrue2 = diEMA2 > 0
    adxMsg2 = '\ndiplus2 : ' + string.tostring(diplusHTF2) + '\ndiminus2 : ' + string.tostring(diminusHTF2) + '\nadx2 : ' + string.tostring(adxHTF2) + '\ndiEMA2: ' + string.tostring(diEMA2) + '\ndiUptrend2 : ' + string.tostring(upTrendTrue2)
    passesADXFilters2 = adxHTF2 >= adxMin2 and adxHTF2 <= adxMax2 or not useADX2
    passUptrendOnlyFilter2 = upTrendTrue2 or not useDiplus2
    adxMsg = adxMsg + adxMsg2
    passesFilters = isAboveATR and passesRSIfilter and passesVariantFilter and passesADXFilters and passUptrendOnlyFilter and passesADXFilters2 and passUptrendOnlyFilter2
    green100: Color = color.new('#008000')
    lime100: Color = color.new('#00FF00')
    red100: Color = color.new('#FF0000')
    blue100: Color = color.new('#0000FF')
    aqua100: Color = color.new('#00FFFF')
    darkred100: Color = color.new('#8B0000')
    gray100: Color = color.new('#808080')
    closeSeries = variant(basisType, open, basisLen, offsetSigma, offsetALMA)
    openSeries = variant(basisType, open[1], basisLen, offsetSigma, offsetALMA)
    closeSeriesAlt: Series[float] = 0.0
    openSeriesAlt: Series[float] = 0.0
    closeTrade: bool = False
    xlong: bool = False
    xshort: bool = False
    modulus = intRes
    if (bar_index + calcOffset) % modulus == 0 and barstate.isconfirmed or (bar_index + calcOffset + 1) % intRes == 0:
        closeSeriesAlt = reso(closeSeries, useRes, stratRes)
        openSeriesAlt = reso(openSeries, useRes, stratRes)
    else:
        closeSeriesAlt = closeSeriesAlt[1]
        openSeriesAlt = openSeriesAlt[1]
    xlong = inline_series(ta.crossover(closeSeriesAlt, openSeriesAlt), offset) and passesFilters
    xshort = closeSeries < longStopPrice
    trendColour = color.green if closeSeriesAlt > openSeriesAlt else color.red
    bcolour = color.green if closeSeriesAlt > openSeriesAlt else color.red
    barcolor(bcolour if scolor else na, title='Bar Colours')
    closeP = plot(closeSeriesAlt, title='Close Series', color=trendColour, linewidth=2, style=plot.style_line)
    openP = plot(openSeriesAlt, title='Open Series', color=trendColour, linewidth=2, style=plot.style_line)
    fill(closeP, openP, color=trendColour)
    longCond = xlong
    shortCond = xshort
    showData: bool = True
    if longCond and strategy.position_size == 0 and showData:
        label.new(bar_index, na, 'RSI = ' + string.tostring(rsi, format.mintick) + '\nATR = ' + string.tostring(atr, format.mintick) + adxMsg, yloc=yloc.abovebar, style=label.style_none, textcolor=color.white, size=size.normal)
    slPercentage: int = 0
    tpPercentage: int = 0
    tdays = (timenow - time) / 60000.0
    tdays = tdays / 1440.0 / 5.0 / 4.3 / timeframe.multiplier if timeframe.ismonthly else tdays / 1440.0 / 5.0 / timeframe.multiplier if timeframe.isweekly else tdays / 1440.0 / timeframe.multiplier if timeframe.isdaily else tdays / timeframe.multiplier
    TP = tpPercentage if tpPercentage > 0 else na
    SL = slPercentage if slPercentage > 0 else na
    exitLong = belowStopLoss or shortCond == True or aboveTakeProfit
    openlongcomment: str = ''
    closelongcomment: str = ''
    if not olc == '':
        openlongcomment = olc
    if not clc == '':
        closelongcomment = clc
    longIsActive: bool = longCond or strategy.position_size > 0
    longTakeProfitPrice: Series[float] = na(float)
    __block_result__ = na
    if longIsActive:
        __block_result_1__ = na
        if longCond and (not strategy.position_size > 0):
            __block_result_1__ = close * (1 + longTakeProfitPerc)
        else:
            __block_result_1__ = nz(longTakeProfitPrice[1], close * (1 + longTakeProfitPerc))
        __block_result__ = __block_result_1__
    else:
        __block_result__ = na
    longTakeProfitPrice = __block_result__
    longTrailingTakeProfitStepTicks = longTakeProfitPrice * trailingTakeProfitDeviationPerc / syminfo.mintick
    if (ebar == 0 or tdays <= ebar) and tradeType != 'NONE':
        if longCond == True and tradeType != 'SHORT':
            strategy.entry('long', strategy.long, comment=openlongcomment)
        if exitLong and tradeType == 'LONG':
            strategy.close('long', comment=closelongcomment)
        if strategy.position_size > 0 and close > longTPPrice or exitLong or closeTrade:
            if longIsActive:
                strategy.exit(id='Long Trailing Profit', from_entry='long', comment=closelongcomment, limit=na if enableTrailing else longTakeProfitPrice, trail_price=longTakeProfitPrice if enableTrailing else na, trail_offset=longTrailingTakeProfitStepTicks if enableTrailing else na, alert_message='Long(' + syminfo.ticker + '): Take Profit activated')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
