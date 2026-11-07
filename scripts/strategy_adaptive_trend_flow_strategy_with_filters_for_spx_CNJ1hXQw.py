"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, bar_index, chart, close, color, hlc3, input, label, na, plot,
    script, strategy, string, ta
)
from pynecore.types import Color, Persistent, Series


@script.strategy("Adaptive Trend Flow Strategy with Filters for SPX", overlay=True, max_labels_count=500, initial_capital=1000, commission_type=strategy.commission.cash_per_order, commission_value=0.01, slippage=2, margin_long=20, margin_short=20, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    atr=input.int(14, "Main Length", minval=2, group="Find more strategies like this on pineindicators.com"),
    length=input.int(2, "Main Length", minval=2),
    smooth_len=input.int(2, "Smoothing Length", minval=2),
    sensitivity=input.float(2.0, "Sensitivity", step=0.1),
    use_sma_filter=input.bool(True, "Enable SMA Filter?"),
    sma_length=input.int(4, "SMA Length", minval=1),
    use_macd_filter=input.bool(True, "Enable MACD Filter?"),
    macd_fast_length=input.int(2, "MACD Fast Length", minval=1),
    macd_slow_length=input.int(7, "MACD Slow Length", minval=1),
    macd_signal_length=input.int(2, "MACD Signal Length", minval=1),
    leverage_factor=input.float(4.5, "Leverage Factor", minval=1.0, step=0.1),
    id=input("besttrader123", title="Your TradingView username", group="Automate this strategy with plugpine.com"),
    key=input("nc739ja84gf", title="Unique identifier (UID)"),
    ticker__ren__=input("SPX", title="Ticker/symbol of your broker"),
    showbars=input.bool(True, "Color Bars?"),
    showbg=input.bool(True, "Background Color?"),
    showsignals=input.bool(True, "Show Signals?")
):
    bullcolor: Color = color.new('#0097A7')
    bearcolor: Color = color.new('#FF195F')

    def calculate_trend_levels():
        typical = hlc3
        fast_ema = ta.ema(typical, length)
        slow_ema = ta.ema(typical, length * 2)
        basis = (fast_ema + slow_ema) / 2
        vol = ta.stdev(typical, length)
        smooth_vol = ta.ema(vol, smooth_len)
        upper = basis + smooth_vol * sensitivity
        lower = basis - smooth_vol * sensitivity
        return (basis, upper, lower)

    def get_trend_state(upper, lower, basis):
        prev_level: Persistent[float] = na(float)
        trend: Persistent[int] = 0
        if na(prev_level):
            trend = 1 if close > basis else -1
            prev_level = lower if trend == 1 else upper
        if trend == 1:
            if close < lower:
                trend = -1
                prev_level = upper
            else:
                prev_level = lower
        else:
            if close > upper:
                trend = 1
                prev_level = lower
            else:
                prev_level = upper
        return (trend, prev_level)

    basis, upper, lower = calculate_trend_levels()
    trend: Series
    trend, level = get_trend_state(upper, lower, basis)

    sma_value = ta.sma(close, sma_length)
    sma_condition = close > sma_value if use_sma_filter else True

    macd_line, signal_line, _ = ta.macd(close, macd_fast_length, macd_slow_length, macd_signal_length)
    macd_condition = macd_line > signal_line if use_macd_filter else True

    long_signal = trend == 1 and trend[1] == -1 and sma_condition and macd_condition
    short_signal = trend == -1 and trend[1] == 1

    p2 = plot(basis, color=bullcolor if trend == 1 else bearcolor, linewidth=2)
    p1 = plot(level, color=bullcolor if close > level else bearcolor, linewidth=2, style=plot.style_linebr)
    if showsignals and ta.crossover(close, level):
        label.new(bar_index, level, '▲', color=bullcolor, textcolor=chart.bg_color, style=label.style_label_upper_right)
    if showsignals and ta.crossunder(close, level):
        label.new(bar_index, level, '▼', color=bearcolor, textcolor=chart.fg_color, style=label.style_label_lower_right)

    qty = strategy.equity / close * leverage_factor

    if long_signal:
        alert('{"AccountID": "' + id + '","Key": "' + key + '", "symbol": "' + ticker__ren__ + '", "action": "long", "volume": ' + string.tostring(qty) + '}', alert.freq_once_per_bar)
    if short_signal:
        alert('{"AccountID": "' + id + '","Key": "' + key + '", "symbol": "' + ticker__ren__ + '", "action": "closelong"}', alert.freq_once_per_bar)

    if long_signal:
        strategy.entry('Long', strategy.long, qty=qty)
    if short_signal:
        strategy.close('Long')

    plot(sma_value if use_sma_filter else na, color=color.new(color.blue, 80), title='SMA')
    plot(macd_line if use_macd_filter else na, color=color.new(color.orange, 80), title='MACD Line')
    plot(signal_line if use_macd_filter else na, color=color.new(color.red, 80), title='Signal Line')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
