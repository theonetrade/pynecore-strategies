"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bgcolor, close, color, display, fill, input, location,
    math, na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

GRP_RSI: str = '━━━  RSI  ━━━'
GRP_FISHER: str = '━━━  FISHER TRANSFORM  ━━━'
GRP_DISPLAY: str = '━━━  DISPLAY  ━━━'
GRP_THEME: str = '━━━  COLOR THEME  ━━━'


@script.indicator('FisherRSI', shorttitle='FRSI', overlay=False)
def main(
    rsi_source: Series[float] = input.source(close, 'RSI Source', group=GRP_RSI),
    rsi_length=input.int(14, 'RSI Length', minval=2, maxval=200, group=GRP_RSI, tooltip='Lookback for the RSI.'),
    rsi_smoothing=input.int(1, 'RSI Smoothing', minval=1, maxval=10, group=GRP_RSI, tooltip='SMA period applied to the RSI before the Fisher Transform. 1 = no smoothing.'),
    oversold_level=input.int(30, 'Oversold Level', minval=1, maxval=49, group=GRP_RSI, tooltip='Lower zone boundary. Bullish Fisher cross arrows fire when RSI or the Fisher line itself is at or below this level.'),
    overbought_level=input.int(70, 'Overbought Level', minval=51, maxval=99, group=GRP_RSI, tooltip='Upper zone boundary. Bearish Fisher cross arrows fire when RSI or the Fisher line itself is at or above this level.'),
    enable_fisher_transform=input.bool(True, 'Enable Fisher Transform Lines', group=GRP_FISHER, tooltip='Plots the Fisher Transform and signal lines derived from the RSI. Independent of Show RSI and Show Fisher Cross Arrows.'),
    fisher_length=input.int(10, 'Fisher Length', minval=2, maxval=100, group=GRP_FISHER, tooltip='Lookback for the min-max rescale used by the Fisher Transform.'),
    show_fisher_arrows=input.bool(True, 'Show Fisher Cross Arrows', group=GRP_FISHER, tooltip='Marks Fisher Transform crossovers with arrows on the Fisher line when RSI or the Fisher line is in an extreme zone. Works whether or not the Fisher lines are plotted.'),
    show_chart_highlight=input.bool(True, 'Show Price Chart Highlight', group=GRP_FISHER, tooltip='Highlights the price chart background on the same bars as the Fisher cross arrows. Not drawn in the indicator pane. Requires Show Fisher Cross Arrows to be on.'),
    chart_highlight_transparency=input.int(85, 'Chart Highlight Transparency', minval=0, maxval=100, group=GRP_FISHER, tooltip='Transparency of the zone-gated price chart highlight. Higher = more transparent. 0 = fully opaque, 100 = invisible.'),
    show_any_cross_highlight=input.bool(False, 'Show Highlight on Any Fisher Cross', group=GRP_FISHER, tooltip='Also highlights the price chart on every Fisher cross, including crosses outside the OB/OS zones that do not get an arrow. Drawn in the price chart only. Bars that already get the zone-gated highlight are not drawn twice.'),
    any_cross_highlight_transparency=input.int(93, 'Any-Cross Highlight Transparency', minval=0, maxval=100, group=GRP_FISHER, tooltip='Transparency of the any-cross highlight. The default is roughly half the opacity of the zone-gated highlight default.'),
    show_rsi=input.bool(False, 'Show RSI', group=GRP_DISPLAY, tooltip='Shows the RSI line and its glow. Off by default so only the Fisher Transform lines display. Independent of the Fisher Transform lines.'),
    show_regime_zones=input.bool(True, 'Show Regime Background', group=GRP_DISPLAY, tooltip='Colors the indicator pane background based on the current regime of the line selected in Regime Basis.'),
    regime_basis=input.string('Fisher Transform', 'Regime Basis', options=('Fisher Transform', 'RSI'), group=GRP_DISPLAY, tooltip='Which line drives the regime background color. The Fisher line and the RSI line are each colored from their own value.'),
    color_theme=input.string('Vaporwave', 'Color Theme', options=('Modern', 'Neon', 'Classic', 'Gold Standard', 'Ultraviolet', 'Infrared', 'Arctic', 'Vaporwave', 'Matrix', 'Terminal'), group=GRP_THEME, tooltip='Same theme set as the CCO and Stochastic / Fisher CVD indicators. Overridden entirely if Use Custom Colors below is on.'),
    use_custom_colors=input.bool(False, 'Use Custom Colors (Override Theme)', group=GRP_THEME, tooltip='Ignores the Color Theme above and uses the four colors below instead.'),
    custom_bearish_color=input.color(color.new('#00D4AA'), 'Custom Bearish/Oversold Color', group=GRP_THEME),
    custom_bullish_color=input.color(color.new('#FF073A'), 'Custom Bullish/Overbought Color', group=GRP_THEME),
    custom_neutral_color=input.color(color.new('#9D4EDD'), 'Custom Neutral/Mixed Color', group=GRP_THEME),
    custom_accent_color=input.color(color.new('#FFC107'), 'Custom Accent Color (Signal Line)', group=GRP_THEME),
    enable_visual_effects=input.bool(True, 'Enable Enhanced Visual Effects', group=GRP_THEME, tooltip='Master switch for the smooth color gradient on the lines, the shaded OB/OS band, and the overshoot fills when the Fisher line moves beyond a level. Line Glow is controlled separately below. Off = flat styling using the discrete regime colors.'),
    show_glow=input.bool(False, 'Show Line Glow', group=GRP_THEME, tooltip='Adds a soft halo around the Fisher line, and around the RSI line when it is shown. Independent of Enable Enhanced Visual Effects.'),
    gradient_lower_bound=input.float(25, 'Gradient Lower Bound', minval=0, maxval=49, step=1, group=GRP_THEME, tooltip='A line at or below this level shows the fully saturated bearish color. Applies to both the Fisher line (on its 50 +/- 10x scale) and the RSI line.'),
    gradient_upper_bound=input.float(75, 'Gradient Upper Bound', minval=51, maxval=100, step=1, group=GRP_THEME, tooltip='A line at or above this level shows the fully saturated bullish color. Applies to both the Fisher line and the RSI line.')
):
    rsi_score = ta.sma(ta.rsi(rsi_source, rsi_length), rsi_smoothing)
    score = rsi_score

    neutral_level: int = 50
    moderate_bearish_threshold = (oversold_level + neutral_level) / 2
    moderate_bullish_threshold = (overbought_level + neutral_level) / 2

    fisher_value1: PersistentSeries[float] = 0.0
    fisher_transform: PersistentSeries[float] = 0.0

    fisher_highest = ta.highest(rsi_score, fisher_length)
    fisher_lowest = ta.lowest(rsi_score, fisher_length)
    fisher_range = fisher_highest - fisher_lowest

    fisher_position = (rsi_score - fisher_lowest) / fisher_range - 0.5 if fisher_range != 0 else 0.0
    fisher_value1 = 0.33 * 2 * fisher_position + 0.67 * nz(fisher_value1[1])
    fisher_value1 = math.max(math.min(fisher_value1, 0.999), -0.999)
    fisher_transform = 0.5 * math.log((1 + fisher_value1) / (1 - fisher_value1)) + 0.5 * nz(fisher_transform[1])
    fisher_signal = fisher_transform[1]

    fisher_value_scaled = 50 + fisher_transform * 10

    fisher_bull_zone = score <= oversold_level or fisher_value_scaled <= oversold_level
    fisher_bear_zone = score >= overbought_level or fisher_value_scaled >= overbought_level

    fisher_cross_up = show_fisher_arrows and ta.crossover(fisher_transform, fisher_signal) and fisher_bull_zone
    fisher_cross_down = show_fisher_arrows and ta.crossunder(fisher_transform, fisher_signal) and fisher_bear_zone

    fisher_any_cross_up = ta.crossover(fisher_transform, fisher_signal)
    fisher_any_cross_down = ta.crossunder(fisher_transform, fisher_signal)

    fisher_scaled = fisher_value_scaled if enable_fisher_transform else na
    fisher_signal_scaled = 50 + fisher_signal * 10 if enable_fisher_transform else na

    def mix_color(color_a, color_b):
        return color.from_gradient(50, 0, 100, color_a, color_b)

    def f_theme_colors():
        bearish: Persistent[Color] = na(Color)
        bullish: Persistent[Color] = na(Color)
        neutral: Persistent[Color] = na(Color)
        accent: Persistent[Color] = na(Color)
        __switch__ = color_theme
        if __switch__ == 'Modern':
            bearish = color.new('#00D4AA')
            bullish = color.new('#FF073A')
            neutral = color.new('#9D4EDD')
            accent = color.new('#FFC107')
        elif __switch__ == 'Neon':
            bearish = color.new('#00FFFF')
            bullish = color.new('#FF00FF')
            neutral = color.new('#9932CC')
            accent = color.new('#FFFF00')
        elif __switch__ == 'Classic':
            bearish = color.rgb(0, 200, 83)
            bullish = color.rgb(255, 23, 68)
            neutral = color.rgb(136, 136, 136)
            accent = color.rgb(255, 179, 0)
        elif __switch__ == 'Gold Standard':
            bearish = color.new('#FFD700')
            bullish = color.new('#B0B0B0')
            neutral = color.new('#CD7F32')
            accent = color.new('#FFFFFF')
        elif __switch__ == 'Ultraviolet':
            bearish = color.new('#BF00FF')
            bullish = color.new('#6600AA')
            neutral = color.new('#5C0080')
            accent = color.new('#00FF00')
        elif __switch__ == 'Infrared':
            bearish = color.new('#FFFFFF')
            bullish = color.new('#CC0000')
            neutral = color.new('#882200')
            accent = color.new('#FF6600')
        elif __switch__ == 'Arctic':
            bearish = color.new('#A8D8FF')
            bullish = color.new('#4488CC')
            neutral = color.new('#3A5A8A')
            accent = color.new('#F0F8FF')
        elif __switch__ == 'Vaporwave':
            bearish = color.new('#FF6B9D')
            bullish = color.new('#9B30FF')
            neutral = color.new('#6622AA')
            accent = color.new('#00FFFF')
        elif __switch__ == 'Matrix':
            bearish = color.new('#00FF41')
            bullish = color.new('#007A1F')
            neutral = color.new('#003D0F')
            accent = color.new('#FFFFFF')
        elif __switch__ == 'Terminal':
            bearish = color.new('#00FF00')
            bullish = color.new('#FF6000')
            neutral = color.new('#707070')
            accent = color.new('#FFFFFF')
        return (bearish, bullish, neutral, accent)

    _theme_bearish, _theme_bullish, _theme_neutral, _theme_accent = f_theme_colors()

    theme_bearish = custom_bearish_color if use_custom_colors else _theme_bearish
    theme_bullish = custom_bullish_color if use_custom_colors else _theme_bullish
    theme_neutral = custom_neutral_color if use_custom_colors else _theme_neutral
    theme_accent = custom_accent_color if use_custom_colors else _theme_accent
    theme_moderate_bearish = mix_color(theme_bearish, theme_neutral)
    theme_moderate_bullish = mix_color(theme_neutral, theme_bullish)

    def f_line_color(val: float):
        clamped: float = math.max(math.min(val, gradient_upper_bound), gradient_lower_bound)
        gradient: Color = color.from_gradient(clamped, gradient_lower_bound, 50, theme_bearish, theme_neutral) if clamped <= 50 else color.from_gradient(clamped, 50, gradient_upper_bound, theme_neutral, theme_bullish)
        discrete: Color = theme_bearish if val <= oversold_level else theme_moderate_bearish if val <= moderate_bearish_threshold else theme_neutral if val < moderate_bullish_threshold else theme_moderate_bullish if val < overbought_level else theme_bullish
        return gradient if enable_visual_effects else discrete

    rsi_line_color = f_line_color(score)
    fisher_line_color = f_line_color(fisher_value_scaled)

    regime_color = color.new(rsi_line_color if regime_basis == 'RSI' else fisher_line_color, 90)

    p_zero_ref = plot(0, 'Zero Reference', display=display.none)
    p_hundred_ref = plot(100, 'Hundred Reference', display=display.none)
    p_oversold = plot(oversold_level, 'Oversold', color=color.new(theme_bearish, 40), style=plot.style_line, linewidth=1)
    plot(neutral_level, 'Neutral', color=color.new(theme_neutral, 50), style=plot.style_line, linewidth=1)
    p_overbought = plot(overbought_level, 'Overbought', color=color.new(theme_bullish, 40), style=plot.style_line, linewidth=1)

    fill(p_overbought, p_oversold, color=color.new(theme_neutral, 92) if enable_visual_effects else na, title='OB/OS Band Fill')

    glow_active = show_glow and show_rsi
    glow_value = score if glow_active else na
    plot(glow_value, 'RSI Glow Outer', color=color.new(rsi_line_color, 80), linewidth=8, display=display.all if glow_active else display.none)
    plot(glow_value, 'RSI Glow Inner', color=color.new(rsi_line_color, 60), linewidth=5, display=display.all if glow_active else display.none)

    plot(score, 'RSI', color=rsi_line_color, linewidth=3, display=display.all if show_rsi else display.none)

    fisher_glow_active = show_glow and enable_fisher_transform
    fisher_glow_value = fisher_value_scaled if fisher_glow_active else na
    plot(fisher_glow_value, 'Fisher Glow Outer', color=color.new(fisher_line_color, 80), linewidth=8, display=display.all if fisher_glow_active else display.none)
    plot(fisher_glow_value, 'Fisher Glow Inner', color=color.new(fisher_line_color, 60), linewidth=5, display=display.all if fisher_glow_active else display.none)

    plot(fisher_signal_scaled, 'Fisher Signal', color=theme_accent, linewidth=1, display=display.all if enable_fisher_transform else display.none)
    p_fisher = plot(fisher_scaled, 'Fisher Transform (RSI)', color=fisher_line_color, linewidth=2, display=display.all if enable_fisher_transform else display.none)

    fill(p_fisher, p_overbought, color=color.new(theme_bullish, 75) if enable_visual_effects and fisher_scaled > overbought_level else na, title='Overbought Overshoot Fill')
    fill(p_fisher, p_oversold, color=color.new(theme_bearish, 75) if enable_visual_effects and fisher_scaled < oversold_level else na, title='Oversold Overshoot Fill')

    plotshape(fisher_value_scaled if fisher_cross_up else na, style=shape.triangleup, location=location.absolute, color=theme_bearish, size=size.tiny, title='Fisher Cross Up', display=display.all if show_fisher_arrows else display.none)
    plotshape(fisher_value_scaled if fisher_cross_down else na, style=shape.triangledown, location=location.absolute, color=theme_bullish, size=size.tiny, title='Fisher Cross Down', display=display.all if show_fisher_arrows else display.none)

    bgcolor(regime_color if show_regime_zones else na, title='Regime')

    chart_highlight_color = na if not show_chart_highlight else color.new(theme_bearish, chart_highlight_transparency) if fisher_cross_up else color.new(theme_bullish, chart_highlight_transparency) if fisher_cross_down else na
    bgcolor(chart_highlight_color, title='Fisher Cross Highlight (Price Chart)', force_overlay=True)

    zone_highlight_drawn = show_chart_highlight and (fisher_cross_up or fisher_cross_down)
    any_cross_highlight_color = na if not show_any_cross_highlight or zone_highlight_drawn else color.new(theme_bearish, any_cross_highlight_transparency) if fisher_any_cross_up else color.new(theme_bullish, any_cross_highlight_transparency) if fisher_any_cross_down else na
    bgcolor(any_cross_highlight_color, title='Any Fisher Cross Highlight (Price Chart)', force_overlay=True)

    rsi_enter_overbought = ta.crossover(score, overbought_level)
    rsi_enter_oversold = ta.crossunder(score, oversold_level)

    alertcondition(fisher_cross_up, 'Fisher Arrow - Bullish', '{{ticker}} {{interval}}: Fisher Bullish Cross (arrow signal)')
    alertcondition(fisher_cross_down, 'Fisher Arrow - Bearish', '{{ticker}} {{interval}}: Fisher Bearish Cross (arrow signal)')

    alertcondition(fisher_any_cross_up, 'Fisher Turn - Any Bullish Cross', '{{ticker}} {{interval}}: Fisher crossed above its signal line')
    alertcondition(fisher_any_cross_down, 'Fisher Turn - Any Bearish Cross', '{{ticker}} {{interval}}: Fisher crossed below its signal line')

    alertcondition(rsi_enter_overbought, 'RSI Overbought', '{{ticker}} {{interval}}: RSI entered overbought')
    alertcondition(rsi_enter_oversold, 'RSI Oversold', '{{ticker}} {{interval}}: RSI entered oversold')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
