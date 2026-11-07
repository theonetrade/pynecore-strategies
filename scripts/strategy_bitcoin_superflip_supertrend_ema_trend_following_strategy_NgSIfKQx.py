"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, display, fill, input, location, na,
    plot, plotshape, script, shape, size, strategy, ta
)

g_strategy: str = '════════ Strategy Settings ════════'
g_adx: str = '════════ ADX Filter ════════'
g_visual: str = '════════ Visual Settings ════════'


@script.strategy("BTCUSD Supertrend + EMA Trend Filter (1H)", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=25, commission_type=strategy.commission.percent, commission_value=0.075, slippage=1)
def main(
    atrPeriod=input.int(10, title="Supertrend ATR Length", group=g_strategy),
    factor=input.float(1.8, title="Supertrend Factor", step=0.1, group=g_strategy),
    emaLen=input.int(200, title="EMA Trend Filter Length", group=g_strategy),
    enableSL=input.bool(False, title="Enable Stop Loss", group=g_strategy),
    enableTP=input.bool(False, title="Enable Take Profit", group=g_strategy),
    __input_5__=input.float(4.0, title="Stop Loss %", step=0.1, group=g_strategy),
    __input_6__=input.float(8.0, title="Take Profit %", step=0.1, group=g_strategy),
    enableADX=input.bool(False, title="Enable ADX Filter", group=g_adx, tooltip="Only take signals when ADX is above the threshold, filtering out low-conviction/choppy conditions."),
    adxLen=input.int(14, title="ADX Length", minval=1, group=g_adx),
    adxSmooth=input.int(14, title="ADX Smoothing", minval=1, group=g_adx),
    adxThresh=input.float(20.0, title="ADX Threshold", step=1.0, group=g_adx),
    show_fill=input.bool(True, 'Show Gradient Fill', group=g_visual),
    show_markers=input.bool(True, 'Show Flip Markers', group=g_visual),
    color_preset=input.string('Custom', 'Color Preset', options=('Classic', 'Aqua', 'Cosmic', 'Cyber', 'Neon', 'Custom'), group=g_visual),
    bullish_input=input.color(color.new('#00FFAA'), 'Bullish Color', group=g_visual),
    bearish_input=input.color(color.new('#FF0000'), 'Bearish Color', group=g_visual),
    show_candles=input.bool(False, 'Enable Bar Coloring', group=g_visual),
    bar_trans=input.int(0, 'Bar Color Transparency', minval=0, maxval=100, group=g_visual),
    show_bgcolor=input.bool(False, 'Enable Background Coloring', group=g_visual),
    bg_trans=input.int(90, 'Background Color Transparency', minval=0, maxval=100, group=g_visual)
):
    slPct = __input_5__ / 100
    tpPct = __input_6__ / 100

    __block_result__ = (na, na)
    __switch__ = color_preset
    if __switch__ == 'Classic':
        __block_result__ = (color.new('#00FF00'), color.new('#FF0000'))
    elif __switch__ == 'Aqua':
        __block_result__ = (color.new('#00D4FF'), color.new('#FF8C00'))
    elif __switch__ == 'Cosmic':
        __block_result__ = (color.new('#49FFCE'), color.new('#9932CC'))
    elif __switch__ == 'Cyber':
        __block_result__ = (color.new('#00CCCC'), color.new('#FF6600'))
    elif __switch__ == 'Neon':
        __block_result__ = (color.new('#FFFF00'), color.new('#FF00FF'))
    elif __switch__ == 'Custom':
        __block_result__ = (bullish_input, bearish_input)
    bullish_color, bearish_color = __block_result__

    supertrend, direction = ta.supertrend(factor, atrPeriod)
    trendEMA = ta.ema(close, emaLen)

    bullFlip = ta.change(direction) < 0
    bearFlip = ta.change(direction) > 0

    diplus, diminus, adx = ta.dmi(adxLen, adxSmooth)
    adxOK = not enableADX or adx > adxThresh

    longCondition = bullFlip and close > trendEMA and adxOK
    shortCondition = bearFlip and close < trendEMA and adxOK

    trend_color = bullish_color if direction < 0 else bearish_color

    if longCondition:
        strategy.entry('Long', strategy.long)

    if shortCondition:
        strategy.entry('Short', strategy.short)

    if bearFlip:
        strategy.close('Long')
    if bullFlip:
        strategy.close('Short')

    if strategy.position_size > 0:
        entryPrice = strategy.position_avg_price
        if enableSL:
            strategy.exit('Long SL/TP', 'Long', stop=entryPrice * (1 - slPct), limit=entryPrice * (1 + tpPct) if enableTP else na)

    if strategy.position_size < 0:
        entryPrice = strategy.position_avg_price
        if enableSL:
            strategy.exit('Short SL/TP', 'Short', stop=entryPrice * (1 + slPct), limit=entryPrice * (1 - tpPct) if enableTP else na)

    st_up = supertrend if direction < 0 else na
    st_dn = supertrend if direction > 0 else na

    plot(st_up, 'Glow Up', color=color.new(bullish_color, 70), linewidth=6, style=plot.style_linebr)
    plot(st_dn, 'Glow Down', color=color.new(bearish_color, 70), linewidth=6, style=plot.style_linebr)
    p_st_up = plot(st_up, 'Bullish Supertrend', color=bullish_color, linewidth=2, style=plot.style_linebr)
    p_st_dn = plot(st_dn, 'Bearish Supertrend', color=bearish_color, linewidth=2, style=plot.style_linebr)

    plot(trendEMA, title='EMA Trend Filter', color=color.new(color.orange, 20), linewidth=1)

    p_price = plot(close, 'Price Anchor', color=na, display=display.none, editable=False)

    step_up = (close - st_up) / 4.0 if not na(st_up) else na
    grad1_up = st_up + step_up * 1.0 if not na(step_up) else na
    grad2_up = st_up + step_up * 2.0 if not na(step_up) else na
    grad3_up = st_up + step_up * 3.0 if not na(step_up) else na

    step_dn = (close - st_dn) / 4.0 if not na(st_dn) else na
    grad1_dn = st_dn + step_dn * 1.0 if not na(step_dn) else na
    grad2_dn = st_dn + step_dn * 2.0 if not na(step_dn) else na
    grad3_dn = st_dn + step_dn * 3.0 if not na(step_dn) else na

    p_g1u = plot(grad1_up if show_fill else na, display=display.none, editable=False)
    p_g2u = plot(grad2_up if show_fill else na, display=display.none, editable=False)
    p_g3u = plot(grad3_up if show_fill else na, display=display.none, editable=False)
    p_g1d = plot(grad1_dn if show_fill else na, display=display.none, editable=False)
    p_g2d = plot(grad2_dn if show_fill else na, display=display.none, editable=False)
    p_g3d = plot(grad3_dn if show_fill else na, display=display.none, editable=False)

    fill(p_st_up, p_g1u, color=color.new(bullish_color, 65) if show_fill else na, title='Up Gradient 1')
    fill(p_g1u, p_g2u, color=color.new(bullish_color, 78) if show_fill else na, title='Up Gradient 2')
    fill(p_g2u, p_g3u, color=color.new(bullish_color, 88) if show_fill else na, title='Up Gradient 3')
    fill(p_g3u, p_price, color=color.new(bullish_color, 95) if show_fill else na, title='Up Gradient 4')

    fill(p_st_dn, p_g1d, color=color.new(bearish_color, 65) if show_fill else na, title='Down Gradient 1')
    fill(p_g1d, p_g2d, color=color.new(bearish_color, 78) if show_fill else na, title='Down Gradient 2')
    fill(p_g2d, p_g3d, color=color.new(bearish_color, 88) if show_fill else na, title='Down Gradient 3')
    fill(p_g3d, p_price, color=color.new(bearish_color, 95) if show_fill else na, title='Down Gradient 4')

    plotshape(supertrend if show_markers and bullFlip else na, title='Bullish Flip', style=shape.triangleup, location=location.belowbar, color=bullish_color, size=size.small)
    plotshape(supertrend if show_markers and bearFlip else na, title='Bearish Flip', style=shape.triangledown, location=location.abovebar, color=bearish_color, size=size.small)

    plotshape(longCondition, title='Long Entry', style=shape.circle, location=location.belowbar, color=color.new(bullish_color, 0), size=size.tiny)
    plotshape(shortCondition, title='Short Entry', style=shape.circle, location=location.abovebar, color=color.new(bearish_color, 0), size=size.tiny)

    barcolor(color.new(trend_color, bar_trans) if show_candles else na, title='Trend Bar Color')
    bgcolor(color.new(trend_color, bg_trans) if show_bgcolor else na, title='Trend Background Color')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
