"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, na, plot, script, strategy, ta
from pynecore.types import Color, Series


@script.strategy('MACD+RSI', initial_capital=100, overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type='percent', commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    fast_length=input.int(title='Fast Length', defval=12, group='MACD'),
    slow_length=input.int(title='Slow Length', defval=26, group='MACD'),
    src: Series[float] = input.source(title='Source', defval=close, group='MACD'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group='MACD'),
    sma_source1=input.string(title='Simple MA FAST (Oscillator)', defval='EMA', options=('HMA', 'DHMA', 'THMA', 'FHMA', 'WMA', 'DWMA', 'TWMA', 'FWMA', 'SMA', 'DSMA', 'TSMA', 'FSMA', 'EMA', 'DEMA', 'TEMA', 'FEMA', 'RMA', 'DRMA', 'TRMA', 'FRMA'), group='MACD'),
    sma_source2=input.string(title='Simple MA SLOW (Oscillator)', defval='EMA', options=('HMA', 'DHMA', 'THMA', 'FHMA', 'WMA', 'DWMA', 'TWMA', 'FWMA', 'SMA', 'DSMA', 'TSMA', 'FSMA', 'EMA', 'DEMA', 'TEMA', 'FEMA', 'RMA', 'DRMA', 'TRMA', 'FRMA'), group='MACD'),
    sma_signal=input.string(title='Simple MA(Signal Line)', defval='EMA', options=('HMA', 'DHMA', 'THMA', 'FHMA', 'WMA', 'DWMA', 'TWMA', 'FWMA', 'SMA', 'DSMA', 'TSMA', 'FSMA', 'EMA', 'DEMA', 'TEMA', 'FEMA', 'RMA', 'DRMA', 'TRMA', 'FRMA'), group='MACD'),
    use_stress=input.bool(False, title='Use stress on recent bars', group='Stress'),
    recent_stress=input.float(0.01, title='Stress on recent bars', group='Stress', step=0.01, minval=0.01, maxval=0.99),
    level=input.int(1, title='Level of stress', group='Stress'),
    use_ma=input.bool(True, title='Use moving average (MACD)?', group='Moving Average'),
    __input_11__=input.int(36, title='Length', group='Moving Average'),
    __input_12__=input.string(title='Type MA', defval='THMA', options=('HMA', 'DHMA', 'THMA', 'FHMA', 'WMA', 'DWMA', 'TWMA', 'FWMA', 'SMA', 'DSMA', 'TSMA', 'FSMA', 'EMA', 'DEMA', 'TEMA', 'FEMA', 'RMA', 'DRMA', 'TRMA', 'FRMA'), group='Moving Average'),
    use_linreg=input.bool(True, title='Use linear regression (MACD)?', group='Linear Regression'),
    __input_14__=input.int(10, title='Length', group='Linear Regression'),
    __input_15__=input.int(1, title='Offset', group='Linear Regression'),
    on_cross=input.bool(False, title='Use cross macd and signal', group='Condition entry/exit'),
    on_minmax=input.bool(True, title='Use min/max macd', group='Condition entry/exit'),
    rsiFilter=input.bool(False, title='Use RSI filter?', group='RSI'),
    rsiTP=input.bool(True, title='Use RSI Take Profit?', group='RSI'),
    len=input.int(14, title='RSI period', group='RSI'),
    srcr: Series[float] = input.source(close, title='RSI source', group='RSI'),
    ovb=input.int(90, title='Overbought height', group='RSI'),
    ovs=input.int(44, title='Oversold height', group='RSI'),
    usiLong=input(True, title='Use long?'),
    usiShort=input(True, title='Use short?')
):
    def ma(source, length, type):
        return 4 * ta.ema(source, length) - ta.ema(ta.ema(ta.ema(ta.ema(source, length), length), length), length) if type == 'FEMA' else 4 * ta.sma(source, length) - ta.sma(ta.sma(ta.sma(ta.sma(source, length), length), length), length) if type == 'FSMA' else 4 * ta.wma(source, length) - ta.wma(ta.wma(ta.wma(ta.wma(source, length), length), length), length) if type == 'FWMA' else 4 * ta.rma(source, length) - ta.rma(ta.rma(ta.rma(ta.rma(source, length), length), length), length) if type == 'FRMA' else 3 * ta.ema(source, length) - ta.ema(ta.ema(ta.ema(source, length), length), length) if type == 'TEMA' else 3 * ta.sma(source, length) - ta.sma(ta.sma(ta.sma(source, length), length), length) if type == 'TSMA' else 3 * ta.wma(source, length) - ta.wma(ta.wma(ta.wma(source, length), length), length) if type == 'TWMA' else 3 * ta.rma(source, length) - ta.rma(ta.rma(ta.rma(source, length), length), length) if type == 'TRMA' else ta.ema(source, length) if type == 'EMA' else ta.sma(source, length) if type == 'SMA' else ta.wma(source, length) if type == 'WMA' else ta.rma(source, length) if type == 'RMA' else 2 * ta.ema(source, length) - ta.ema(ta.ema(source, length), length) if type == 'DEMA' else 2 * ta.sma(source, length) - ta.sma(ta.sma(source, length), length) if type == 'DSMA' else 2 * ta.wma(source, length) - ta.wma(ta.wma(source, length), length) if type == 'DWMA' else 2 * ta.rma(source, length) - ta.rma(ta.rma(source, length), length) if type == 'DRMA' else ta.hma(source, length) if type == 'HMA' else 2 * ta.hma(source, length) - ta.hma(ta.hma(source, length), length) if type == 'DHMA' else 3 * ta.hma(source, length) - ta.hma(ta.hma(ta.hma(source, length), length), length) if type == 'THMA' else 4 * ta.hma(source, length) - ta.hma(ta.hma(ta.hma(ta.hma(source, length), length), length), length) if type == 'FHMA' else ta.ema(source, length)

    fast_ma = ma(src, fast_length, sma_source1)
    slow_ma = ma(src, slow_length, sma_source2)
    macd: Series = fast_ma - slow_ma
    signal = ma(macd, signal_length, sma_signal)
    hist = macd - signal
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    if use_stress:
        macd = macd * (1 / (1 - recent_stress))
        if not na(macd[1]):
            macd = math.pow(macd * recent_stress, level) + 1 - recent_stress * macd[1]
    if use_ma:
        macd = ma(macd, __input_11__, __input_12__)
    if use_linreg:
        macd = ta.linreg(macd, __input_14__, __input_15__)
    aperturaLong = ta.change(macd) > 0
    aperturashort = not ta.change(macd) > 0
    if on_cross:
        on_minmax = False
        aperturaLong = ta.crossover(macd, signal)
        aperturashort = ta.crossunder(macd, signal)
    if on_minmax:
        on_cross = False
        aperturaLong = ta.change(macd) > 0
        aperturashort = ta.change(macd) < 0
    plot(macd, title='MACD', color=color.white if ta.change(macd) > 0 and on_minmax else color.purple if ta.change(macd) < 0 and on_minmax else color.blue)
    plot(signal if on_cross else na, title='Signal', color=color.new(col_signal, 0))
    rsi = ta.rsi(srcr, len)
    change_1 = ta.change(macd)
    change_2: Series = ta.change(macd)
    okLong = rsi < ovb and change_1 > 0 and (change_2[1] <= 0)
    change_3 = ta.change(macd)
    change_4: Series = ta.change(macd)
    okShort = rsi > ovs and change_3 < 0 and (change_4[1] >= 0)
    if not rsiFilter:
        okLong = True
        okShort = True
    chiusuraShort = rsi < ovs or aperturaLong
    chiusuraLong = rsi > ovb or aperturashort
    if rsiTP:
        change_1__00000087__: Series = ta.change(macd)
        aperturaLong = ta.change(macd) > 0 and change_1__00000087__[1] <= 0 and (rsi < ovb)
        change_2__00000087__: Series = ta.change(macd)
        aperturashort = ta.change(macd) < 0 and change_2__00000087__[1] >= 0 and (rsi > ovs)
    if not rsiTP:
        chiusuraShort = okLong and aperturaLong
        chiusuraLong = okShort and aperturashort
    if chiusuraShort:
        strategy.close('SHORTISSIMO')
    if usiLong and strategy.position_size <= 0 and okLong and aperturaLong:
        strategy.entry('LONGHISSIMO', strategy.long)
    if chiusuraLong:
        strategy.close('LONGHISSIMO')
    if usiShort and strategy.position_size >= 0 and okShort and aperturashort:
        strategy.entry('SHORTISSIMO', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
