"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, chart, close, color, display, extend, fill,
    high, input, line, location, low, math, na, open, plot, plotcandle, plotchar, script, size, ta,
    xloc
)
from pynecore.types import Color, Line, Persistent, Series

group_regression: str = "Regression"
group_oscillator: str = "Oscillator"
group_volatility: str = "Volatility"
group_levels: str = "Liquidity Levels"
group_appearance: str = "Appearance"


@script.indicator("Nadaraya-Watson Regression Liquidity Sweeps [AlgoAlpha]", "AlgoAlpha - Nadaraya-Watson Regression Liquidity", overlay=False, max_lines_count=500)
def main(
    norm_len=input.int(100, "Normalization Length", minval=1, group=group_oscillator, tooltip="Controls the standard deviation window used to normalize the Nadaraya-Watson slope. Increasing it makes oscillator scaling more stable and slower to adapt; decreasing it makes scaling adapt faster but can make the oscillator more reactive and noisy."),
    nw_bandwidth=input.int(30, "Nadaraya-Watson Bandwidth", minval=1, group=group_regression, tooltip="Controls the width of the Nadaraya-Watson kernel. Increasing it makes the regression smoother and slower to turn; decreasing it makes the regression track price more closely but can add noise."),
    nw_lookback=input.int(140, "Nadaraya-Watson Lookback", minval=1, group=group_regression, tooltip="Controls how many historical bars are included in the Nadaraya-Watson estimate. Increasing it uses more history for a more stable curve; decreasing it focuses more on recent price action and reacts faster."),
    osc_smooth_len=input.int(21, "Oscillator Smoothing Length", minval=1, group=group_oscillator, tooltip="Controls the WMA smoothing applied to the normalized slope oscillator. Increasing it makes the oscillator smoother with fewer sharp turns; decreasing it makes the oscillator more responsive but choppier."),
    signal_len=input.int(14, "Signal Length", minval=1, group=group_oscillator, tooltip="Controls the EMA length of the oscillator signal line. Increasing it makes signal crosses slower and less frequent; decreasing it makes crosses happen earlier and more often."),
    atr_len=input.int(14, "ATR Length", minval=1, group=group_volatility, tooltip="Controls the ATR window used for the price overlay volatility offset. Increasing it makes volatility measurement smoother; decreasing it makes the overlay react faster to recent range expansion or contraction."),
    vol_smooth_len=input.int(21, "Volatility Smoothing Length", minval=1, group=group_volatility, tooltip="Controls the smoothing applied to ATR before it is used in the overlay. Increasing it creates a steadier volatility offset; decreasing it makes the offset expand and contract more quickly."),
    use_tip=input.bool(True, "Use Swing Points", group=group_levels, tooltip="When enabled, liquidity levels are anchored to the highest high or lowest low reached during the active oscillator phase. When disabled, new levels are anchored to the current bar high or low when the signal event occurs."),
    show_nw_band_candles=input.bool(True, "Show Nadaraya-Watson Band Candles", group=group_appearance, tooltip="When enabled, plots the Nadaraya-Watson volatility band as overlay candles. Disabling it hides the band candles without changing calculations, levels, signals, or alerts."),
    show_bar_color_candles=input.bool(True, "Show Bar Colour Candles", group=group_appearance, tooltip="When enabled, redraws price candles with oscillator-based bullish or bearish colours using plotcandle. Disabling it leaves the chart's normal candles visually unchanged."),
    show_signal_line=input.bool(True, "Show Oscillator Signal Line", group=group_appearance, tooltip="When enabled, displays the EMA signal line of the oscillator. Disabling it hides the signal line but keeps signal-cross logic active."),
    show_momentum_signals=input.bool(True, "Show Momentum Weakening Signals", group=group_appearance, tooltip="When enabled, displays the small momentum weakening dots on the chart. Disabling it hides those visual markers without affecting alert conditions."),
    show_rebound_signals=input.bool(True, "Show Rebound Signals", group=group_appearance, tooltip="When enabled, displays bullish and bearish rebound markers around the Nadaraya-Watson value. Disabling it hides those visual markers without affecting calculations."),
    green=input.color(color.new('#00FFBB'), "Bullish Colour", group=group_appearance, tooltip="Sets the bullish color used for positive oscillator fills, bullish price overlay coloring, lower liquidity levels, and bullish momentum events."),
    red=input.color(color.new('#FF1100'), "Bearish Colour", group=group_appearance, tooltip="Sets the bearish color used for negative oscillator fills, bearish price overlay coloring, upper liquidity levels, and bearish momentum events.")
):
    def nw(src: Series[float], bandwidth: int, lookback: int):
        num: float = 0.0
        den: float = 0.0
        h2: float = 2.0 * math.pow(bandwidth, 2)
        for i in pine_range(0, lookback - 1):
            w: float = math.exp(-math.pow(i, 2) / h2)
            num += src[i] * w
            den += w
        return num / den

    def pseudo_transp(c: Color, transp: int):
        return color.from_gradient(transp, 0, 100, c, chart.bg_color)

    nw_val: Series = nw(close, nw_bandwidth, nw_lookback)
    nw_slope = nw_val - nw_val[1]

    slope_std = ta.stdev(nw_slope, norm_len)
    osc_ = nw_slope / slope_std
    osc = ta.wma(osc_, osc_smooth_len)
    signal = ta.ema(osc, signal_len)

    volatility = ta.sma(ta.atr(atr_len), vol_smooth_len)

    overflow = math.max(math.abs(osc) - 2, 0)

    con1 = ta.crossunder(osc, signal)
    con2 = ta.crossover(osc, signal)

    above_signal: Series = osc > signal
    below_signal: Series = osc < signal

    above_tip_price: Persistent[float] = na(float)
    above_tip_bar: Persistent[int] = na(int)

    below_tip_price: Persistent[float] = na(float)
    below_tip_bar: Persistent[int] = na(int)

    if above_signal:
        if not above_signal[1]:
            above_tip_price = high
            above_tip_bar = bar_index
        elif na(above_tip_price) or high > above_tip_price:
            above_tip_price = high
            above_tip_bar = bar_index

    if below_signal:
        if not below_signal[1]:
            below_tip_price = low
            below_tip_bar = bar_index
        elif na(below_tip_price) or low < below_tip_price:
            below_tip_price = low
            below_tip_bar = bar_index

    draw_upper_line = osc > 0 and con1
    draw_lower_line = osc < 0 and con2
    draw_new_line = draw_upper_line or draw_lower_line

    active_line: Persistent[Line] = na(Line)
    active_line_price: Persistent[float] = na(float)
    active_line_type: Persistent[int] = 0

    upper_level_swept = not na(active_line) and active_line_type == 1 and (close > active_line_price)
    lower_level_swept = not na(active_line) and active_line_type == -1 and (close < active_line_price)

    if not na(active_line) and active_line_type != 0:
        line.set_x2(active_line, bar_index)

        line_crossed = close > active_line_price if active_line_type == 1 else close < active_line_price

        if line_crossed or draw_new_line:
            active_line_type = 0

    if draw_upper_line:
        level_price: float = above_tip_price if use_tip and (not na(above_tip_price)) else high
        level_bar: int = above_tip_bar if use_tip and (not na(above_tip_bar)) else bar_index

        active_line = line.new(x1=level_bar, y1=level_price, x2=bar_index, y2=level_price, xloc=xloc.bar_index, extend=extend.none, color=red, style=line.style_solid, width=2, force_overlay=True)

        active_line_price = level_price
        active_line_type = 1

    if draw_lower_line:
        level_price: float = below_tip_price if use_tip and (not na(below_tip_price)) else low
        level_bar: int = below_tip_bar if use_tip and (not na(below_tip_bar)) else bar_index

        active_line = line.new(x1=level_bar, y1=level_price, x2=bar_index, y2=level_price, xloc=xloc.bar_index, extend=extend.none, color=green, style=line.style_solid, width=2, force_overlay=True)

        active_line_price = level_price
        active_line_type = -1

    weakening_bullish_momentum = osc > 0 and con1
    weakening_bearish_momentum = osc < 0 and con2
    bullish_zero_cross = ta.crossover(osc, 0)
    bearish_zero_cross = ta.crossunder(osc, 0)
    bullish_signal_cross = con2
    bearish_signal_cross = con1
    bullish_rebound = osc > 0 and close[1] < nw_val and (close > nw_val)
    bearish_rebound = osc < 0 and close[1] > nw_val and (close < nw_val)

    main = plot(osc, 'Oscillator', color.blue, 2, plot.style_line, display=display.none)
    plot(signal, 'Signal Line', color.new(chart.fg_color, 50) if show_signal_line else na)

    ovf = plot(overflow if osc > 2 else -overflow if osc < -2 else 0, 'Overflow', display=display.none)

    zero = plot(0, 'Zero Line', chart.fg_color)

    col_ = color.from_gradient(osc, 0, 3, pseudo_transp(green, 80), pseudo_transp(green, 30)) if osc > 0 else color.from_gradient(osc, -3, 0, pseudo_transp(red, 30), pseudo_transp(red, 80))

    fill(main, ovf, col_, 'Oscillator Fill')
    fill(zero, ovf, green if osc > 0 else red, 'Oscillator Fill')

    plotcandle(open=nw_val + (-volatility if osc > 0 else volatility) if show_nw_band_candles else na, high=(high if osc < 0 else nw_val) if show_nw_band_candles else na, low=(low if osc > 0 else nw_val) if show_nw_band_candles else na, close=nw_val if show_nw_band_candles else na, title='Nadaraya-Watson Band', bordercolor=na, force_overlay=True, color=col_, wickcolor=color.new(col_, 70))

    plotcandle(open=open if show_bar_color_candles else na, high=high if show_bar_color_candles else na, low=low if show_bar_color_candles else na, close=close if show_bar_color_candles else na, title='Price', color=col_, wickcolor=col_, bordercolor=col_, force_overlay=True)

    plotchar(show_momentum_signals and weakening_bullish_momentum, 'Weakening Bullish Momentum', '●', location.abovebar, green, size=size.tiny, force_overlay=True)
    plotchar(show_momentum_signals and weakening_bearish_momentum, 'Weakening Bearish Momentum', '●', location.belowbar, red, size=size.tiny, force_overlay=True)

    plotchar(nw_val - volatility * 1.5 if show_rebound_signals and bullish_rebound else na, 'Bullish Rebound', '▲', location.absolute, green, size=size.tiny, force_overlay=True)
    plotchar(nw_val + volatility * 1.5 if show_rebound_signals and bearish_rebound else na, 'Bearish Rebound', '▼', location.absolute, red, size=size.tiny, force_overlay=True)

    alertcondition(weakening_bullish_momentum, title='Weakening Bullish Momentum')
    alertcondition(weakening_bearish_momentum, title='Weakening Bearish Momentum')
    alertcondition(bullish_signal_cross, title='Bullish Signal Cross')
    alertcondition(bearish_signal_cross, title='Bearish Signal Cross')
    alertcondition(bullish_zero_cross, title='Bullish Zero Cross')
    alertcondition(bearish_zero_cross, title='Bearish Zero Cross')
    alertcondition(draw_upper_line, title='New Upper Liquidity Sweep Level')
    alertcondition(draw_lower_line, title='New Lower Liquidity Sweep Level')
    alertcondition(upper_level_swept, title='Upper Liquidity Sweep Level Swept')
    alertcondition(lower_level_swept, title='Lower Liquidity Sweep Level Swept')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
