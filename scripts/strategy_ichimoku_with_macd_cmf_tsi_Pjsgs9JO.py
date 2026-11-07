"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, hl2, input, low, math, plot, script, strategy,
    ta, volume
)
from pynecore.types import Color, Series


@script.strategy('Ichimoku with MACD/ CMF/ TSI ', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    ts_bars=input.int(10, minval=1, title='Tenkan-Sen Bars'),
    ks_bars=input.int(30, minval=1, title='Kijun-Sen Bars'),
    ssb_bars=input.int(52, minval=1, title='Senkou-Span B Bars'),
    cs_offset=input.int(26, minval=1, title='Chikou-Span Offset'),
    ss_offset=input.int(26, minval=1, title='Senkou-Span Offset'),
    long_entry=input(True, title='Long Entry'),
    short_entry=input(True, title='Short Entry'),
    fast_length=input(title='Fast Length', defval=12),
    slow_length=input(title='Slow Length', defval=26),
    src: Series[float] = input(title='Source', defval=hl2),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input(title='Simple MA(Oscillator)', defval=True),
    sma_signal=input(title='Simple MA(Signal Line)', defval=False),
    lengthA=input.int(10, minval=1, title='CMF Length'),
    long=input(title='Long Length', defval=20),
    short=input(title='Short Length', defval=20)
):
    def middle(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    tenkan = middle(ts_bars)
    kijun = middle(ks_bars)
    senkouA: Series = math.avg(tenkan, kijun)
    senkouB: Series = middle(ssb_bars)
    plot(tenkan, color=color.new(color.new('#0496FF'), 0), title='Tenkan-Sen')
    plot(kijun, color=color.new(color.new('#991515'), 0), title='Kijun-Sen')
    plot(close, offset=-cs_offset + 1, color=color.new(color.new('#459915'), 0), title='Chikou-Span')
    sa = plot(senkouA, offset=ss_offset - 1, color=color.new(color.green, 0), title='Senkou-Span A')
    sb = plot(senkouB, offset=ss_offset - 1, color=color.new(color.red, 0), title='Senkou-Span B')
    fill(sa, sb, color=color.green if senkouA > senkouB else color.red, title='Cloud color')
    ss_high = math.max(senkouA[ss_offset - 1], senkouB[ss_offset - 1])
    ss_low = math.min(senkouA[ss_offset - 1], senkouB[ss_offset - 1])
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    fast_ma = ta.sma(src, fast_length) if sma_source else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal else ta.ema(macd, signal_length)
    hist = macd - signal
    tk_cross_bull = tenkan > kijun
    tk_cross_bear = tenkan < kijun
    cs_cross_bull = ta.mom(close, cs_offset - 1) > 0
    cs_cross_bear = ta.mom(close, cs_offset - 1) < 0
    price_above_kumo = close > ss_high
    price_below_kumo = close < ss_low
    ad = 0 if close == high and close == low or high == low else (2 * close - low - high) / (high - low) * volume
    mf = math.sum(ad, lengthA) / math.sum(volume, lengthA)
    price = close
    def double_smooth(src, long, short):
        fist_smooth = ta.ema(src, long)
        return ta.ema(fist_smooth, short)

    pc = ta.change(price)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(math.abs(pc), long, short)
    tsi_value = 100 * (double_smoothed_pc / double_smoothed_abs_pc)
    bullish = tk_cross_bull and cs_cross_bull and price_above_kumo and (hist > 0) and (mf > 0.1) and (tsi_value > 0)
    bearish = tk_cross_bear and cs_cross_bear and price_below_kumo and (hist < 0) and (mf < -0.1) and (tsi_value < 0)
    if bullish and long_entry:
        strategy.entry('Long', strategy.long)
    if bearish and short_entry:
        strategy.entry('Short', strategy.short)
    if bearish and (not short_entry):
        strategy.close('Long')
    if bullish and (not long_entry):
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
