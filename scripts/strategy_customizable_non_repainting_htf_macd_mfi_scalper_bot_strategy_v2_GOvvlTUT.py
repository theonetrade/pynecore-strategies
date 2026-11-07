"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barmerge, barstate, bgcolor, close, color, currency, fill,
    format, high, hlc3, hline, input, label, low, math, na, nz, plot, request, script, size,
    strategy, string, syminfo, ta, time, timestamp, volume, yloc
)
from pynecore.types import Color, Persistent, Series


@script.strategy('Customizable HTF MACD Strategy v2.0', overlay=False, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.08, default_qty_type=strategy.percent_of_equity, default_qty_value=100, currency=currency.USD, calc_on_every_tick=True, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    res=input.timeframe(title='Resolution', defval='5', group='Strategy', inline='1'),
    ribbon_period=input.int(19, 'Period', step=1, group='Strategy', inline='1'),
    olc=input.string(title='Open Long Comment', defval='', group='Strategy', inline='2'),
    clc=input.string(title='Close Long Comment', defval='', group='Strategy', inline='2'),
    fast_length=input.int(title='Fast Length', defval=7, group='MACD', inline='1'),
    slow_length=input.int(title='Slow Length', defval=23, group='MACD', inline='1'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=10, group='MACD', inline='2'),
    src: Series[float] = input.source(title='Source', defval=close, group='MACD', inline='2'),
    sma_source=input.bool(title='Simple MA(Oscillator)', defval=False, group='MACD', inline='3'),
    sma_signal=input.bool(title='Simple MA(Signal Line)', defval=False, group='MACD', inline='3'),
    length=input.int(15, minval=1, group='MFI', inline='1'),
    lower=input.int(12, minval=0, maxval=50, group='MFI', inline='1'),
    upper=input.int(80, minval=50, maxval=100, group='MFI', inline='1'),
    HighlightBreaches=input(True, title='Highlight Oversold/Overbought?'),
    enableTrailing=input.bool(defval=True, title='Enable Trailing', tooltip='Enable or disable the trailing for take profit.', group='Trailing Profit', inline='1'),
    __input_15__=input.float(title='Long TP (%)', minval=0.0, step=0.1, defval=4, group='Trailing Profit', inline='1'),
    __input_16__=input.float(defval=0.5, title='TTP Dev %%', minval=0.01, maxval=100, step=0.1, tooltip='The step to follow the price when the take profit limit is reached.', group='Trailing Profit', inline='1'),
    __input_17__=input.float(8, title='Fixed SL (%)', minval=0.0, step=0.1, tooltip='Use 100 to turn off - Stop loss % even if ATR did not catch it'),
    showData=input.bool(False, title='Show Data', group='Filters', inline='3', tooltip='Use this to help see numbers and help set filters'),
    useVariantFilter=input.bool(False, title='Use MA', group='Filters', inline='1'),
    VariantFilterType=input.string(defval='LSMA', title='Type: ', group='Filters', inline='1', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HullMA', 'LSMA', 'ALMA', 'SSMA', 'TMA')),
    VariantTimeFrame=input.timeframe(defval='3', title='TF: ', group='Filters', inline='1'),
    VariantFilterLength=input.int(20, minval=1, title='Len', group='Filters', inline='1'),
    useRSI=input.bool(False, title='Use RSI', group='RSI Filter', inline='2'),
    rsiTimeFrame=input.timeframe(defval='5', title='TF: ', group='RSI Filter', inline='2'),
    RSILength=input.int(13, minval=1, title='RSI Length', group='RSI Filter', inline='2'),
    aboveRSIFilter=input.int(45, minval=1, title='Buy Above  RSI', group='RSI Filter', inline='2'),
    belowRSIFilter=input.int(80, minval=1, title='Buy Below RSI', group='RSI Filter', inline='2'),
    minATR=input.float(0, title='Min ATR', minval=0.0, step=0.001, tooltip='Use 0 to turn off - can remove periods of low volatility where less likely profitable'),
    testStartYear=input.int(2018, 'Fr Year', group='Backtest', inline='1'),
    testStartMonth=input.int(1, 'Fr Month', group='Backtest', inline='1'),
    testStartDay=input.int(1, 'Fr Day', group='Backtest', inline='1'),
    testStopYear=input.int(9999, 'To Year', group='Backtest', inline='2'),
    testStopMonth=input.int(12, 'To Month', group='Backtest', inline='2'),
    testStopDay=input.int(31, 'To Day', group='Backtest', inline='2')
):
    openlongcomment: str = 'Long In Here'
    closelongcomment: str = 'Close'
    openshortcomment: str = ''
    closeshortcommment: str = ''
    if not olc == '':
        openlongcomment = olc
    if not clc == '':
        closelongcomment = clc
    def Ema(src, p):
        ema: Series[float] = 0.0
        sf = 2 / (p + 1)
        ema = nz(ema[1] + sf * (src - ema[1]), src)
        return ema

    def Sma(src, p):
        a: Series = ta.cum(src)
        return (a - a[math.max(p, 0)]) / math.max(p, 0)

    def Atr(p, res):
        atr: Series[float] = 0.0
        highHTF = request.security(syminfo.tickerid, res, high[1 if barstate.isrealtime else 0])
        lowHTF = request.security(syminfo.tickerid, res, low[1 if barstate.isrealtime else 0])
        closeHTF: Series = request.security(syminfo.tickerid, res, close[1 if barstate.isrealtime else 0])
        Tr = math.max(highHTF - lowHTF, math.max(math.abs(highHTF - closeHTF[1]), math.abs(lowHTF - closeHTF[1])))
        atr = nz(atr[1] + (Tr - atr[1]) / p, Tr)
        return atr

    def reso(exp: Series, use, res):
        security_1 = request.security(syminfo.tickerid, res, exp[1 if barstate.isrealtime else 0], gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
        return security_1 if use else exp[1 if barstate.isrealtime else 0]

    def rp_security(_symbol, _res, _src: Series):
        return inline_series(request.security(_symbol, _res, _src[1 if barstate.isrealtime else 0]), 1 if barstate.isrealtime else 0)

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

    htfClose = request.security(syminfo.tickerid, res, close[1 if barstate.isrealtime else 0])
    leadLine1 = ta.ema(htfClose, ribbon_period)
    leadLine2 = ta.sma(htfClose, ribbon_period)
    UT = leadLine2 < leadLine1
    DT = leadLine2 > leadLine1
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    srcHTF = request.security(syminfo.tickerid, res, src[1 if barstate.isrealtime else 0])
    fast_ma = Sma(srcHTF, fast_length) if sma_source else Ema(srcHTF, fast_length)
    slow_ma = Sma(srcHTF, slow_length) if sma_source else Ema(srcHTF, slow_length)
    macd = fast_ma - slow_ma
    signal = Sma(macd, signal_length) if sma_signal else Ema(macd, signal_length)
    hist = macd - signal
    MFIsource: Series = hlc3
    MFTsourceHTF = request.security(syminfo.tickerid, res, MFIsource[1 if barstate.isrealtime else 0])
    volumeHTF = request.security(syminfo.tickerid, res, volume[1 if barstate.isrealtime else 0])
    upper_s = math.sum(volumeHTF * (0 if ta.change(MFTsourceHTF) <= 0 else MFTsourceHTF), length)
    lower_s = math.sum(volumeHTF * (0 if ta.change(MFTsourceHTF) >= 0 else MFTsourceHTF), length)
    mf = 100.0 - 100.0 / (1.0 + upper_s / lower_s)
    top = hline(upper, color=color.new(color.gray, 100), linewidth=1, editable=False)
    bottom = hline(lower, color=color.new(color.gray, 100), linewidth=1, editable=False)
    hline(0, color=color.new(color.black, 100), editable=False)
    hline(100, color=color.new(color.black, 100), editable=False)
    b_color = color.new(color.red, 70) if mf > upper else color.new(color.green, 60) if mf < lower else na
    bgcolor(b_color if HighlightBreaches else na)
    fill(top, bottom, color=color.new(color.gray, 75))
    useTP1: bool = False
    long_tp1_inp: int = 6
    long_tp1_qty: int = 100
    longTakeProfitPerc = __input_15__ * 0.01
    trailingTakeProfitDeviationPerc = __input_16__ / 100
    long_trailing: float = 1.3
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    longTPPrice = strategy.position_avg_price * (1 + longTakeProfitPerc)
    longLossPerc = __input_17__ * 0.01
    longStopPrice = strategy.position_avg_price * (1 - longLossPerc)
    multiplier: int = 2
    ATR_period: int = 40
    offsetSigma: int = 1
    offsetALMA: float = 0.085
    variantFilter = reso(variant(VariantFilterType, close[1 if barstate.isrealtime else 0], VariantFilterLength, offsetSigma, offsetALMA), True, VariantTimeFrame)
    isAboveVariantFilter = close[1 if barstate.isrealtime else 0] >= variantFilter or not useVariantFilter
    variantFilterP = plot(variantFilter, title='VariantFilter', color=color.blue, linewidth=4, style=plot.style_line)
    rsiTmp = ta.rsi(close[0 if barstate.isconfirmed else 1], RSILength)
    rsi = rp_security(syminfo.tickerid, rsiTimeFrame, rsiTmp)
    rising_1 = ta.rising(rsi, 1)
    RSIFilter = rsi <= belowRSIFilter and rsi >= aboveRSIFilter and rising_1 or not useRSI
    atr = Atr(ATR_period, res)
    crossover_1 = ta.crossover(mf, lower)
    entry_long = (ta.crossover(macd, signal) or (crossover_1 and leadLine2 < leadLine1)) and RSIFilter and isAboveVariantFilter and (atr > minATR)
    entry_price_long = ta.valuewhen(entry_long, high, 0)
    SL_floating_long = entry_price_long - multiplier * atr
    exit_long = close < SL_floating_long or close < longStopPrice
    longIsActive: bool = entry_long or strategy.position_size > 0
    longTakeProfitPrice: Series[float] = na(float)
    __block_result__ = na
    if longIsActive:
        __block_result_1__ = na
        if entry_long and (not strategy.position_size > 0):
            __block_result_1__ = close * (1 + longTakeProfitPerc)
        else:
            __block_result_1__ = nz(longTakeProfitPrice[1], close * (1 + longTakeProfitPerc))
        __block_result__ = __block_result_1__
    else:
        __block_result__ = na
    longTakeProfitPrice = __block_result__
    longTrailingTakeProfitStepTicks = longTakeProfitPrice * trailingTakeProfitDeviationPerc / syminfo.mintick
    takeProfitColor: Persistent = color.new(color.new('#419388'), 0)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    if testPeriod():
        if UT:
            if entry_long == True:
                strategy.entry('long', strategy.long, comment=openlongcomment)
        if useTP1:
            strategy.exit('TP1', 'long', qty_percent=long_tp1_qty, limit=long_take_level_1)
        if strategy.position_size > 0 and close > longTPPrice:
            if longIsActive:
                strategy.exit(id='Long Trailing Profit', from_entry='long', comment=closelongcomment, limit=na if enableTrailing else longTakeProfitPrice, trail_price=longTakeProfitPrice if enableTrailing else na, trail_offset=longTrailingTakeProfitStepTicks if enableTrailing else na, alert_message='Long(' + syminfo.ticker + '): Take Profit activated')
            strategy.exit('ATR Trail stop', 'long', comment=closelongcomment, trail_points=entry_price_long * long_trailing / syminfo.mintick, trail_offset=entry_price_long * long_trailing / syminfo.mintick)
        if exit_long == True:
            strategy.close('long', comment=closelongcomment)
    plot(macd, title='MACD', color=color.new(col_macd, 0))
    plot(signal, title='Signal', color=color.new(col_signal, 0))
    mfp = plot(mf, color=color.new(color.gray, 0), linewidth=1)
    plot(series=longTakeProfitPrice, title='Long Take Profit', color=takeProfitColor, linewidth=1, style=plot.style_linebr, offset=1)
    if UT and entry_long and (strategy.position_size == 0) and showData:
        label.new(bar_index, na, 'RSI = ' + string.tostring(rsi, format.mintick) + '\nATR = ' + string.tostring(atr, format.mintick), yloc=yloc.abovebar, style=label.style_none, textcolor=color.white, size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
