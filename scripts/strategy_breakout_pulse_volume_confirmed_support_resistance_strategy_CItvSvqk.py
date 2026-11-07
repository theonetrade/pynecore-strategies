"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, display, fill, high, input, location, low, na, open,
    plot, plotcandle, plotshape, script, shape, size, strategy, syminfo, ta, time, timestamp,
    volume
)
from pynecore.types import Color, Persistent

g_sr: str = "✧ Support / Resistance ✧"
g_vol: str = "✧ Volume Confirmation ✧"
g_trend: str = "✧ Trend Filter ✧"
g_risk: str = "✧ Risk Management ✧"
g_date: str = "✧ Backtest Range ✧"
g_vis: str = "✧ Visuals ✧"


@script.strategy("Volume-Confirmed Support/Resistance Breakout Strategy", shorttitle="Vol S/R Breakout", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.01, slippage=2, pyramiding=0)
def main(
    pivotLeft=input.int(10, "Pivot Left Bars", minval=1, group=g_sr),
    pivotRight=input.int(10, "Pivot Right Bars", minval=1, group=g_sr, tooltip="Pivot confirms 'pivotRight' bars after it forms — inherent to swing-structure detection, not lookahead."),
    volLength=input.int(20, "Volume Average Length", minval=1, group=g_vol),
    volMultiplier=input.float(1.5, "Volume Surge Multiplier", minval=1.0, step=0.1, group=g_vol, tooltip="Needs real traded volume — works on stocks, futures, crypto, most index proxies. Spot FX volume is not meaningful."),
    useTrendFilter=input.bool(True, "Require EMA trend filter", group=g_trend),
    emaLength=input.int(200, "EMA Length", minval=1, group=g_trend),
    atrLength=input.int(14, "ATR Length", minval=1, group=g_risk),
    atrStopMult=input.float(1.5, "ATR Stop Multiplier", minval=0.1, step=0.1, group=g_risk),
    atrTargetMult=input.float(3.0, "ATR Target Multiplier", minval=0.1, step=0.1, group=g_risk),
    useStructStop=input.bool(True, "Use broken swing level as stop (else pure ATR)", group=g_risk),
    stopBufferAtr=input.float(0.25, "Structural Stop ATR Buffer", minval=0.0, step=0.05, group=g_risk),
    startDate=input.time(timestamp('01 Jan 2018 00:00 +0000'), "Start Date", group=g_date),
    endDate=input.time(timestamp('31 Dec 2025 00:00 +0000'), "End Date", group=g_date),
    colorCandles=input.bool(True, "Color candles by position", group=g_vis),
    enableGlow=input.bool(True, "Glow effect on S/R lines", group=g_vis),
    showChannelGradient=input.bool(True, "Gradient fill inside S/R channel", group=g_vis, tooltip="Fades from each line toward the channel midpoint, like a heat gradient rather than a flat fill."),
    bullColor=input.color(color.new('#0097A7'), "Bullish / Long Color", group=g_vis),
    bearColor=input.color(color.new('#FF195F'), "Bearish / Short Color", group=g_vis)
):
    ph: float = ta.pivothigh(high, pivotLeft, pivotRight)
    pl: float = ta.pivotlow(low, pivotLeft, pivotRight)

    resistance: Persistent[float] = na(float)
    support: Persistent[float] = na(float)

    if not na(ph):
        resistance = ph
    if not na(pl):
        support = pl

    avgVolume: float = ta.sma(volume, volLength)
    volumeSurge: bool = volume > avgVolume * volMultiplier

    emaVal: float = ta.ema(close, emaLength)
    trendUpOk: bool = not useTrendFilter or close > emaVal
    trendDownOk: bool = not useTrendFilter or close < emaVal

    atrVal: float = ta.atr(atrLength)

    inRange: bool = time >= startDate and time <= endDate

    longBreakout: bool = not na(resistance) and ta.crossover(close, resistance) and volumeSurge and trendUpOk and inRange
    shortBreakout: bool = not na(support) and ta.crossunder(close, support) and volumeSurge and trendDownOk and inRange

    longStopPrice: Persistent[float] = na(float)
    longTgtPrice: Persistent[float] = na(float)
    shortStopPrice: Persistent[float] = na(float)
    shortTgtPrice: Persistent[float] = na(float)

    if longBreakout:
        strategy.entry('Long', strategy.long)
        longStopPrice = support - atrVal * stopBufferAtr if useStructStop and (not na(support)) else close - atrVal * atrStopMult
        longTgtPrice = close + atrVal * atrTargetMult
        alert('Long breakout — ' + syminfo.ticker, alert.freq_once_per_bar_close)

    if shortBreakout:
        strategy.entry('Short', strategy.short)
        shortStopPrice = resistance + atrVal * stopBufferAtr if useStructStop and (not na(resistance)) else close + atrVal * atrStopMult
        shortTgtPrice = close - atrVal * atrTargetMult
        alert('Short breakout — ' + syminfo.ticker, alert.freq_once_per_bar_close)

    if strategy.position_size > 0:
        strategy.exit('Long Exit', 'Long', stop=longStopPrice, limit=longTgtPrice)

    if strategy.position_size < 0:
        strategy.exit('Short Exit', 'Short', stop=shortStopPrice, limit=shortTgtPrice)

    flatNow: bool = strategy.position_size == 0
    flatPrev: bool = strategy.position_size[1] != 0
    if flatNow and flatPrev:
        longStopPrice = na
        longTgtPrice = na
        shortStopPrice = na
        shortTgtPrice = na

    posColor: Color = bullColor if strategy.position_size > 0 else bearColor if strategy.position_size < 0 else na

    plotcandle(open, high, low, close, 'Position Coloring', posColor if colorCandles else na, posColor if colorCandles else na, bordercolor=posColor if colorCandles else na, display=display.all - display.status_line - display.price_scale)

    plot(resistance if enableGlow else na, 'Resistance Glow Outer', color=color.new(bearColor, 88), linewidth=7, style=plot.style_linebr)
    plot(resistance if enableGlow else na, 'Resistance Glow Inner', color=color.new(bearColor, 75), linewidth=4, style=plot.style_linebr)
    p_res = plot(resistance, 'Resistance', color=bearColor, style=plot.style_linebr, linewidth=1)

    plot(support if enableGlow else na, 'Support Glow Outer', color=color.new(bullColor, 88), linewidth=7, style=plot.style_linebr)
    plot(support if enableGlow else na, 'Support Glow Inner', color=color.new(bullColor, 75), linewidth=4, style=plot.style_linebr)
    p_sup = plot(support, 'Support', color=bullColor, style=plot.style_linebr, linewidth=1)

    midChannel: float = (resistance + support) / 2 if not na(resistance) and (not na(support)) else na
    p_mid = plot(midChannel if showChannelGradient else na, 'Channel Midline', display=display.none, editable=False)

    fill(p_res, p_mid, resistance, midChannel, color.new(bearColor, 65), color.new(bearColor, 100), title='Resistance Side Gradient')
    fill(p_mid, p_sup, midChannel, support, color.new(bullColor, 100), color.new(bullColor, 65), title='Support Side Gradient')

    plot(emaVal if useTrendFilter else na, 'EMA Trend', color=color.new(color.gray, 40))

    plotshape(longBreakout, title='Long Signal', location=location.belowbar, style=shape.triangleup, size=size.small, color=bullColor)
    plotshape(shortBreakout, title='Short Signal', location=location.abovebar, style=shape.triangledown, size=size.small, color=bearColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)