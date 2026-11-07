"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, plot, script, strategy,
    syminfo, ta
)
from pynecore.types import Series


@script.strategy(title='NoNonsense Forex', overlay=True, default_qty_value=100000, initial_capital=100, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    ma_slow_type=input.string(title='Baseline Type', defval='Kijun', options=('ALMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMA', 'SMMA', 'HMA', 'LSMA', 'Kijun', 'McGinley')),
    ma_slow_len=input(title='Baseline Length', defval=20),
    ma_slow_len_fast=input(title='Baseline Length Fast', defval=12),
    lsma_offset=input.int(defval=0, title='* Least Squares (LSMA) Only - Offset Value', minval=0),
    alma_offset=input.float(defval=0.85, title='* Arnaud Legoux (ALMA) Only - Offset Value', minval=0, step=0.01),
    alma_sigma=input.int(defval=6, title='* Arnaud Legoux (ALMA) Only - Sigma Value', minval=0),
    atrlength=input(14, title='ATR Length'),
    donttradeoutside_atrcave=input(True),
    lenaroon=input.int(8, minval=1, title='Length Aroon'),
    dont_use_macd=input(False),
    macd_fast_length=input(title='Fast Length', defval=13),
    macd_slow_length=input(title='Slow Length', defval=26),
    macd_signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    dont_use_rsi=input(False),
    lenrsi=input.int(14, minval=1, title='RSI Length'),
    dont_use_psar=input(False),
    psar_start=input.float(0.03, step=0.01),
    psar_increment=input.float(0.018, step=0.001),
    psar_maximum=input.float(0.11, step=0.01),
    use_exit=input(False),
    __input_20__=input.float(0.5, step=0.1),
    __input_21__=input.float(0.005, step=0.001)
):
    ma_slow_src = close
    def ma(type, src, len):
        result: float = 0
        if type == 'SMA':
            result = ta.sma(src, len)
        if type == 'EMA':
            result = ta.ema(src, len)
        if type == 'DEMA':
            e = ta.ema(src, len)
            result = 2 * e - ta.ema(e, len)
        if type == 'TEMA':
            e = ta.ema(src, len)
            result = 3 * (e - ta.ema(e, len)) + ta.ema(ta.ema(e, len), len)
        if type == 'WMA':
            result = ta.wma(src, len)
        if type == 'VWMA':
            result = ta.vwma(src, len)
        if type == 'SMMA':
            w: Series = ta.wma(src, len)
            result = ta.sma(src, len) if na(w[1]) else (w[1] * (len - 1) + src) / len
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'LSMA':
            result = ta.linreg(src, len, lsma_offset)
        if type == 'ALMA':
            result = ta.alma(src, len, alma_offset, alma_sigma)
        if type == 'Kijun':
            kijun = math.avg(ta.lowest(len), ta.highest(len))
            result = kijun
        if type == 'McGinley':
            mg: Series[float] = 0.0
            mg = ta.ema(src, len) if na(mg[1]) else mg[1] + (src - mg[1]) / (len * math.pow(src / mg[1], 4))
            result = mg
        return result

    baseline = ma(ma_slow_type, ma_slow_src, ma_slow_len)
    plot(baseline, title='Baseline', color=color.green if ta.rising(baseline, 1) else color.maroon if ta.falling(baseline, 1) else na, linewidth=3)
    one_atr = ta.rma(ta.tr(True), atrlength)
    upper_atr_band = baseline + one_atr
    lower_atr_band = baseline - one_atr
    plot(upper_atr_band, color=color.new(color.gray, 95), style=plot.style_areabr, histbase=50000, title='ATR Cave')
    plot(lower_atr_band, color=color.new(color.gray, 95), style=plot.style_areabr, histbase=0, title='ATR Cave')
    plot(upper_atr_band, color=color.fuchsia if close > upper_atr_band else na, style=plot.style_line, linewidth=5, title='Close above ATR cave')
    plot(lower_atr_band, color=color.fuchsia if close < lower_atr_band else na, style=plot.style_line, linewidth=5, title='Close below ATR cave')
    too_high = close > upper_atr_band and donttradeoutside_atrcave
    too_low = close < lower_atr_band and donttradeoutside_atrcave
    c1upper = 100 * (ta.highestbars(high, lenaroon + 1) + lenaroon) / lenaroon
    c1lower = 100 * (ta.lowestbars(low, lenaroon + 1) + lenaroon) / lenaroon
    c1CrossUp = ta.crossover(c1upper, c1lower)
    c1CrossDown = ta.crossunder(c1upper, c1lower)
    macd_fast_ma = ta.ema(close, macd_fast_length)
    macd_slow_ma = ta.ema(close, macd_slow_length)
    macd = macd_fast_ma - macd_slow_ma
    macd_signal = ta.ema(macd, macd_signal_length)
    macd_hist = macd - macd_signal
    macdLong = macd_hist > 0 or dont_use_macd
    macdShort = macd_hist < 0 or dont_use_macd
    up = ta.rma(math.max(ta.change(close), 0), lenrsi)
    down = ta.rma(-math.min(ta.change(close), 0), lenrsi)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    rsiLong = rsi > 50 or dont_use_rsi
    rsiShort = rsi < 50 or dont_use_rsi
    psar = ta.sar(psar_start, psar_increment, psar_maximum)
    plot(psar, style=plot.style_cross, color=color.new(color.blue, 0), title='PSAR')
    psarLong = close > psar or dont_use_psar
    psarShort = close < psar or dont_use_psar
    Long_Confirmations = psarLong and rsiLong and macdLong
    Short_Confirmations = psarShort and rsiShort and macdShort
    GoLong = c1CrossUp and Long_Confirmations and (not too_high)
    GoShort = c1CrossDown and Short_Confirmations and (not too_low)
    KillLong = c1CrossDown and use_exit
    KillShort = c1CrossUp and use_exit
    SL = __input_20__ / syminfo.mintick
    TP = __input_21__ / syminfo.mintick
    if GoLong:
        strategy.entry('nnL', strategy.long)
    if GoShort:
        strategy.entry('nnS', strategy.short)
    strategy.exit('XL-nn', from_entry='nnL', loss=SL, profit=TP)
    strategy.exit('XS-nn', from_entry='nnS', loss=SL, profit=TP)
    if KillLong:
        strategy.close('nnL')
    if KillShort:
        strategy.close('nnS')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
