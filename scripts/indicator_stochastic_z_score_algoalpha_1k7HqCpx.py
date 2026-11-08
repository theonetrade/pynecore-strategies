"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, chart, color, display, fill, hlc3, input, location, math,
    na, plot, plotchar, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator("Stochastic Z-Score [AlgoAlpha]", "AlgoAlpha - Stoch Z-Score")
def main(
    src: Series[float] = input.source(hlc3, title="Source", group="Calculation", tooltip="Price series used for all calculations. Changing it alters the base values from which the Z-score and momentum are derived."),
    len=input.int(21, title="Length", group="Calculation", tooltip="Look-back period for moving averages and deviations. Higher values give smoother, slower signals; lower values make the oscillator faster and more sensitive."),
    hist=input.bool(False, title="Show Histogram", group="Appearance", tooltip="Toggle display of the raw, unsmoothed Z-score as columns. Useful for visualising noise layer beneath the smoothed oscillator."),
    green=input.color(color.new('#00FFBB'), title="Bullish Colour", group="Appearance", tooltip="Primary colour for bullish visual elements. Adjust for preferred palette – affects bars, fills, and labels when momentum is positive."),
    red=input.color(color.new('#FF1100'), title="Bearish Colour", group="Appearance", tooltip="Primary colour for bearish visual elements. Adjust for preferred palette – affects bars, fills, and labels when momentum is negative.")
):
    basis = ta.sma(src, len)
    zscore = (src - basis) / ta.stdev(src, len)
    stochZ = ta.stoch(zscore, zscore, zscore, len)
    scaledSZ = stochZ / 25 - 2
    smoothed_scaled: Series = ta.hma(scaledSZ, len)
    ltm = ta.alma(zscore, len, 0, 0.1)

    zscore_color = color.new(color.from_gradient(zscore, -2, 2, red, green), math.max(math.min(cast_int((1 - math.abs(zscore) / 4) * 100), 70), 70))
    plot(zscore, color=zscore_color, linewidth=2, display=display.all if hist else display.none, style=plot.style_columns, title='Z-Score')

    smoothed_scaled_prev = smoothed_scaled[1]
    smoothed_scaled_color = color.new(color.gray, 0 if smoothed_scaled > smoothed_scaled_prev else 50)
    main = plot(smoothed_scaled, title='Smoothed Oscillator', color=smoothed_scaled_color, linewidth=3)
    main1 = plot(smoothed_scaled_prev, title='Oscillator (Lag 1)', color=color.new(color.gray, 20 if smoothed_scaled > smoothed_scaled_prev else 70), display=display.none)

    ltm_color = color.new(green if ltm > 0 else red, 70)
    longtm = plot(ltm, title='Long-Term Momentum (ALMA)', color=ltm_color, display=display.none)

    mid = plot(0, title='Zero Line', display=display.none)
    upper_color = color.new(color.from_gradient(math.max(0, smoothed_scaled), 0, 2, color.gray, red), 70)
    lower_color = color.new(color.from_gradient(math.min(0, smoothed_scaled), -2, 0, green, color.gray), 70)
    u = plot(2, 'Upper', upper_color, linewidth=3)
    d = plot(-2, 'Down', lower_color, linewidth=3)
    u1 = plot(2.5, 'Upper Outer', color.from_gradient(math.max(0, smoothed_scaled), 0, 2.5, color.gray, red), linewidth=3)
    d1 = plot(-2.5, 'Down Outer', color.from_gradient(math.min(0, smoothed_scaled), -2.5, 0, green, color.gray), linewidth=3)

    plotchar(smoothed_scaled_prev if ta.cross(smoothed_scaled, smoothed_scaled_prev) else na, 'Momentum Shift', '●', location.absolute, chart.fg_color, size=size.tiny)
    plotchar(-3 if ta.crossover(smoothed_scaled, smoothed_scaled_prev) and ltm > 0 and (smoothed_scaled_prev < -2) else na, 'Bullish Reversal', '▲', location.absolute, green, size=size.tiny)
    plotchar(3 if ta.crossunder(smoothed_scaled, smoothed_scaled_prev) and ltm < 0 and (smoothed_scaled_prev > 2) else na, 'Bearish Reversal', '▼', location.absolute, red, size=size.tiny)

    plotshape(ta.crossover(smoothed_scaled, smoothed_scaled_prev) and ltm > 0 and (smoothed_scaled_prev < -2), 'Bullish Trend', shape.labelup, location.belowbar, color.new(green, 50), text='▲', textcolor=chart.fg_color, size=size.small, force_overlay=True)
    plotshape(ta.crossunder(smoothed_scaled, smoothed_scaled_prev) and ltm < 0 and (smoothed_scaled_prev > 2), 'Bearish Trend', shape.labeldown, location.abovebar, color.new(red, 50), text='▼', textcolor=chart.fg_color, size=size.small, force_overlay=True)

    upper_fill_color = color.new(color.from_gradient(math.max(0, smoothed_scaled), 0, 2, chart.bg_color, red), 50)
    upper_fill_color_100 = color.new(color.from_gradient(math.max(0, smoothed_scaled), 0, 2, chart.bg_color, red), 100)
    lower_fill_color = color.new(color.from_gradient(math.min(0, smoothed_scaled), -2, 0, green, chart.bg_color), 100)
    lower_fill_color_50 = color.new(color.from_gradient(math.min(0, smoothed_scaled), -2, 0, green, chart.bg_color), 50)
    fill(u1, u, 2.5, 2, upper_fill_color, upper_fill_color_100, 'Upper Fill')
    fill(d, d1, -2, -2.5, lower_fill_color, lower_fill_color_50, 'Lower Fill')
    fill(main, main1, color.new(color.gray, 20 if smoothed_scaled > smoothed_scaled_prev else 70), 'Oscillator Fill')
    fill(longtm, mid, ltm, 0, ltm_color, color.new(green if ltm > 0 else red, 90))

    alertcondition(ta.cross(smoothed_scaled, smoothed_scaled_prev), title='Momentum Shift', message='Stochastic Z-Score momentum direction changed.')
    alertcondition(ta.crossover(smoothed_scaled, smoothed_scaled_prev) and ltm > 0 and (smoothed_scaled_prev < -2), title='Bullish Reversal', message='Bullish reversal detected (oscillator crosses up while long-term momentum is positive).')
    alertcondition(ta.crossunder(smoothed_scaled, smoothed_scaled_prev) and ltm < 0 and (smoothed_scaled_prev > 2), title='Bearish Reversal', message='Bearish reversal detected (oscillator crosses down while long-term momentum is negative).')
    alertcondition(ta.crossover(smoothed_scaled, 0), title='Oscillator Crosses Above Zero', message='Oscillator crossed above the zero line (bullish momentum).')
    alertcondition(ta.crossunder(smoothed_scaled, 0), title='Oscillator Crosses Below Zero', message='Oscillator crossed below the zero line (bearish momentum).')
    alertcondition(ta.crossover(ltm, 0), title='Long-Term Momentum Bullish', message='Long-term momentum (ALMA) crossed above zero.')
    alertcondition(ta.crossunder(ltm, 0), title='Long-Term Momentum Bearish', message='Long-term momentum (ALMA) crossed below zero.')
    alertcondition(smoothed_scaled > 2.5, title='Overbought', message='Oscillator entered overbought zone (> 2.5).')
    alertcondition(smoothed_scaled < -2.5, title='Oversold', message='Oscillator entered oversold zone (< -2.5).')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
