"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, bgcolor, close, color, currency, fill, high, hlc3, hline,
    input, low, math, na, nz, plot, request, script, strategy, syminfo, ta, time, timestamp,
    volume
)
from pynecore.types import Color, Series


@script.strategy('Customizable HTF MACD Strategy v1.2', overlay=False, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.07, default_qty_type=strategy.percent_of_equity, default_qty_value=100, currency=currency.USD, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
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
    useTP1=input.bool(False, title='Use TPI', group='TP/SL', inline='1'),
    __input_15__=input.float(1, title='Long TP 1 %', step=0.1, group='TP/SL', inline='1'),
    long_tp1_qty=input.int(20, title='Long TP 1 Qty', step=1, group='TP/SL', inline='1'),
    __input_17__=input.float(1.3, title='Trailing Stop', step=0.1, group='TP/SL', inline='1', tooltip=''),
    multiplier=input.float(2, 'SL Mult', minval=1, step=0.1, group='TP/SL', inline='2'),
    ATR_period=input.int(40, 'ATR Pd', minval=1, step=1, group='TP/SL', inline='2'),
    aboveTrend=input.bool(False, title='Use Trend', group='Filters', inline='1'),
    TrendLength=input.int(3, minval=1, title='Trend MA', group='Filters', inline='1'),
    useRSI=input.bool(False, title='Use RSI', group='Filters', inline='2'),
    RSILength=input.int(34, minval=1, title='RSI Length', group='Filters', inline='2'),
    belowRSIFilter=input.int(50, minval=1, title='Buy Below RSI Filter', group='Filters', inline='2'),
    testStartYear=input(2018, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(9999, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day')
):
    openlongcomment: str = 'Comment In Here'
    closelongcomment: str = ''
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
    plot(macd, title='MACD', color=color.new(col_macd, 0))
    plot(signal, title='Signal', color=color.new(col_signal, 0))
    MFIsource: Series = hlc3
    sourceHTF = request.security(syminfo.tickerid, res, MFIsource[1 if barstate.isrealtime else 0])
    volumeHTF = request.security(syminfo.tickerid, res, volume[1 if barstate.isrealtime else 0])
    upper_s = math.sum(volumeHTF * (0 if ta.change(sourceHTF) <= 0 else sourceHTF), length)
    lower_s = math.sum(volumeHTF * (0 if ta.change(sourceHTF) >= 0 else sourceHTF), length)
    mf = 100.0 - 100.0 / (1.0 + upper_s / lower_s)
    mfp = plot(mf, color=color.new(color.gray, 0), linewidth=1)
    top = hline(upper, color=color.new(color.gray, 100), linewidth=1, editable=False)
    bottom = hline(lower, color=color.new(color.gray, 100), linewidth=1, editable=False)
    hline(0, color=color.new(color.black, 100), editable=False)
    hline(100, color=color.new(color.black, 100), editable=False)
    b_color = color.new(color.red, 70) if mf > upper else color.new(color.green, 60) if mf < lower else na
    bgcolor(b_color if HighlightBreaches else na)
    fill(top, bottom, color=color.new(color.gray, 75))
    long_tp1_inp = __input_15__ / 100
    long_trailing = __input_17__ / 100
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    aboveTrendFilter = ta.sma(htfClose, TrendLength)
    rsi = ta.rsi(htfClose, RSILength)
    if not useRSI:
        belowRSIFilter = 100
    if not aboveTrend:
        aboveTrendFilter = 0
    crossover_1 = ta.crossover(mf, lower)
    entry_long = (ta.crossover(macd, signal) or (crossover_1 and leadLine2 < leadLine1)) and rsi < belowRSIFilter and (close > aboveTrendFilter)
    entry_price_long = ta.valuewhen(entry_long, close, 0)
    SL_floating_long = entry_price_long - multiplier * Atr(ATR_period, res)
    exit_long = close < SL_floating_long
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
        strategy.exit('Trail stop', 'long', comment=closelongcomment, trail_points=entry_price_long * long_trailing / syminfo.mintick, trail_offset=entry_price_long * long_trailing / syminfo.mintick)
        if exit_long == True:
            strategy.close('long', comment=closelongcomment)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
