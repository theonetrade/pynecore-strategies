"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, currency, high, input, location, low, math, na, nz, plot,
    plotshape, script, shape, strategy, ta, volume
)
from pynecore.types import Series


@script.strategy(title='[STRATEGY][UL]Price Divergence Strategy v1.1', pyramiding=0, overlay=True, initial_capital=10000, calc_on_every_tick=False, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    method__ren__=input.int(title='Method (0=rsi, 1=macd, 2=stoch, 3=volume, 4=acc/dist, 5=fisher, 6=cci):', defval=1, minval=0, maxval=6),
    SHOW_LABEL=input(title='Show Labels', defval=True),
    SHOW_CHANNEL=input(title='Show Channel', defval=False),
    uHid=input(True, title='Use Hidden Divergence in Strategy'),
    uReg=input(True, title='Use Regular Divergence in Strategy'),
    rsi_smooth=input(title='RSI/STOCH/Volume/ACC-DIST/Fisher/cci Smooth:', defval=5),
    macd_src: Series[float] = input(title='MACD Source:', defval=close),
    macd_fast=input(title='MACD Fast:', defval=12),
    macd_slow=input(title='MACD Slow:', defval=26),
    macd_smooth=input(title='MACD Smooth Signal:', defval=9),
    length=input.int(100, minval=10, title='MMLO Look back Length'),
    quad=input.int(2, minval=1, maxval=4, step=1, title='Mininum Quadrant for MMLO Support'),
    inpTakeProfit=input.int(defval=0, title='Take Profit Points', minval=0),
    inpStopLoss=input.int(defval=0, title='Stop Loss Points', minval=0),
    inpTrailStop=input.int(defval=100, title='Trailing Stop Loss Points', minval=0),
    inpTrailOffset=input.int(defval=0, title='Trailing Stop Loss Offset Points', minval=0)
):
    def f_top_fractal(_src: Series):
        return _src[4] < _src[2] and _src[3] < _src[2] and (_src[2] > _src[1]) and (_src[2] > _src)

    def f_bot_fractal(_src: Series):
        return _src[4] > _src[2] and _src[3] > _src[2] and (_src[2] < _src[1]) and (_src[2] < _src)

    def f_fractalize(_src):
        f_bot_fractal__1 = f_bot_fractal(_src)
        return 1 if f_top_fractal(_src) else -1 if f_bot_fractal__1 else 0

    def f_macd(_src, _fast, _slow, _smooth):
        _fast_ma = ta.sma(_src, _fast)
        _slow_ma = ta.sma(_src, _slow)
        _macd = _fast_ma - _slow_ma
        _signal = ta.ema(_macd, _smooth)
        _hist = _macd - _signal
        return _hist

    def f_accdist(_smooth):
        _return = ta.sma(ta.cum(0 if close == high and close == low or high == low else (2 * close - low - high) / (high - low) * volume), _smooth)
        return _return

    def f_fisher(_src, _window):
        _h = ta.highest(_src, _window)
        _l = ta.lowest(_src, _window)
        _value0: Series[float] = 0.0
        _fisher: Series[float] = 0.0
        _value0 = 0.66 * ((_src - _l) / math.max(_h - _l, 0.001) - 0.5) + 0.67 * nz(_value0[1])
        _value1 = 0.999 if _value0 > 0.99 else -0.999 if _value0 < -0.99 else _value0
        _fisher = 0.5 * math.log((1 + _value1) / math.max(1 - _value1, 0.001)) + 0.5 * nz(_fisher[1])
        return _fisher

    rsi_1 = ta.rsi(high, rsi_smooth)
    f_macd__1 = f_macd(macd_src, macd_fast, macd_slow, macd_smooth)
    stoch_1 = ta.stoch(close, high, low, rsi_smooth)
    sma_1 = ta.sma(volume, rsi_smooth)
    f_accdist__1 = f_accdist(rsi_smooth)
    f_fisher__1 = f_fisher(high, rsi_smooth)
    cci_1 = ta.cci(high, rsi_smooth)
    method_high: Series = rsi_1 if method__ren__ == 0 else f_macd__1 if method__ren__ == 1 else stoch_1 if method__ren__ == 2 else sma_1 if method__ren__ == 3 else f_accdist__1 if method__ren__ == 4 else f_fisher__1 if method__ren__ == 5 else cci_1 if method__ren__ == 6 else na
    rsi_2 = ta.rsi(low, rsi_smooth)
    f_macd__2 = f_macd(macd_src, macd_fast, macd_slow, macd_smooth)
    stoch_2 = ta.stoch(close, high, low, rsi_smooth)
    sma_2 = ta.sma(volume, rsi_smooth)
    f_accdist__2 = f_accdist(rsi_smooth)
    f_fisher__2 = f_fisher(low, rsi_smooth)
    cci_2 = ta.cci(low, rsi_smooth)
    method_low: Series = rsi_2 if method__ren__ == 0 else f_macd__2 if method__ren__ == 1 else stoch_2 if method__ren__ == 2 else sma_2 if method__ren__ == 3 else f_accdist__2 if method__ren__ == 4 else f_fisher__2 if method__ren__ == 5 else cci_2 if method__ren__ == 6 else na
    fractal_top = method_high[2] if f_fractalize(method_high) > 0 else na
    fractal_bot = method_low[2] if f_fractalize(method_low) < 0 else na
    high_prev = ta.valuewhen(cast_bool(fractal_top), method_high[2], 1)
    high_price = ta.valuewhen(cast_bool(fractal_top), high[2], 1)
    low_prev = ta.valuewhen(cast_bool(fractal_bot), method_low[2], 1)
    low_price = ta.valuewhen(cast_bool(fractal_bot), low[2], 1)
    regular_bearish_div = fractal_top and high[2] > high_price and (method_high[2] < high_prev)
    hidden_bearish_div = fractal_top and high[2] < high_price and (method_high[2] > high_prev)
    regular_bullish_div = fractal_bot and low[2] < low_price and (method_low[2] > low_prev)
    hidden_bullish_div = fractal_bot and low[2] > low_price and (method_low[2] < low_prev)
    plot(title='H F', series=high[2] if fractal_top else na, color=color.maroon if regular_bearish_div or hidden_bearish_div else na if not SHOW_CHANNEL else color.silver, offset=-2)
    plot(title='L F', series=low[2] if fractal_bot else na, color=color.green if regular_bullish_div or hidden_bullish_div else na if not SHOW_CHANNEL else color.silver, offset=-2)
    plot(title='H D', series=high[2] if fractal_top else na, style=plot.style_circles, color=color.maroon if regular_bearish_div or hidden_bearish_div else na if not SHOW_CHANNEL else color.silver, linewidth=3, offset=-2)
    plot(title='L D', series=low[2] if fractal_bot else na, style=plot.style_circles, color=color.green if regular_bullish_div or hidden_bullish_div else na if not SHOW_CHANNEL else color.silver, linewidth=3, offset=-2)
    plotshape(title='+RBD', series=na if not SHOW_LABEL else high[2] if regular_bearish_div else na, text='R', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='+HBD', series=na if not SHOW_LABEL else high[2] if hidden_bearish_div else na, text='H', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-RBD', series=na if not SHOW_LABEL else low[2] if regular_bullish_div else na, text='R', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-HBD', series=na if not SHOW_LABEL else low[2] if hidden_bullish_div else na, text='H', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    mult: float = 0.125
    hi = ta.highest(high, length)
    lo = ta.lowest(low, length)
    range_1 = hi - lo
    multiplier = range_1 * mult
    midline = lo + multiplier * 4
    oscillator = (close - midline) / (range_1 / 2)
    a: Series = oscillator > 0
    b: Series = oscillator > 0 and oscillator > mult * 2
    c: Series = oscillator > 0 and oscillator > mult * 4
    d: Series = oscillator > 0 and oscillator > mult * 6
    z: Series = oscillator < 0
    y: Series = oscillator < 0 and oscillator < -mult * 2
    x: Series = oscillator < 0 and oscillator < -mult * 4
    w: Series = oscillator < 0 and oscillator < -mult * 6
    useTakeProfit = inpTakeProfit if inpTakeProfit >= 1 else na
    useStopLoss = inpStopLoss if inpStopLoss >= 1 else na
    useTrailStop = inpTrailStop if inpTrailStop >= 1 else na
    useTrailOffset = inpTrailOffset if inpTrailOffset >= 1 else na
    def enterLong():
        __hist_d__: Series = d[0]
        __hist_c__: Series = c[0]
        __hist_b__: Series = b[0]
        __hist_a__: Series = a[0]
        return (uReg and regular_bullish_div or (uHid and hidden_bullish_div)) and (__hist_a__[1] if quad == 1 else __hist_b__[1] if quad == 2 else __hist_c__[1] if quad == 3 else __hist_d__[1] if quad == 4 else False)

    def exitLong():
        return oscillator <= 0

    if enterLong():
        strategy.entry(id='Buy', direction=strategy.long)
    if exitLong():
        strategy.close(id='Buy')
    def enterShort():
        __hist_w__: Series = w[0]
        __hist_x__: Series = x[0]
        __hist_y__: Series = y[0]
        __hist_z__: Series = z[0]
        return (uReg and regular_bearish_div or (uHid and hidden_bearish_div)) and (__hist_z__[1] if quad == 1 else __hist_y__[1] if quad == 2 else __hist_x__[1] if quad == 3 else __hist_w__[1] if quad == 4 else False)

    def exitShort():
        return oscillator >= 0

    if enterShort():
        strategy.entry(id='Sell', direction=strategy.short)
    if exitShort():
        strategy.close(id='Sell')
    strategy.exit('Exit Buy', from_entry='Buy', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)
    strategy.exit('Exit Sell', from_entry='Sell', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
