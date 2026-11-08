"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, high, input, line,
    location, low, na, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Line, Persistent, Series

grp_ema: str = "EMA 200 Settings"
grp_filtros: str = "Visual Filters"


@script.indicator("Leviathan Protocol [Ultimate Sniper]", overlay=True, max_lines_count=100)
def main(
    length=input.int(29, "Liquidity Period (Swing)", minval=3),
    rsiLen=input.int(14, "RSI Period"),
    emaLen=input.int(200, "Main EMA Period", group=grp_ema),
    futuro=input.int(30, "EMA Future Projection (Candles)", group=grp_ema),
    suavizacao=input.int(5, "Inertia Smoothing", group=grp_ema),
    ignorarGaps=input.bool(True, "Ignore GAP Signals (Stocks/Forex)", group=grp_filtros),
    mostrarSimples=input.bool(False, "Show Simple Sweeps (No Divergence)", group=grp_filtros)
):
    ema200: Series = ta.ema(close, emaLen)
    plot(ema200, color=color.yellow, linewidth=2, title='Real EMA 200')

    velocidade = (ema200 - ema200[suavizacao]) / suavizacao
    linhaProjecao: Persistent[Line] = na(Line)

    if barstate.islast:
        line.delete(linhaProjecao)
        y_futuro = ema200 + velocidade * futuro
        linhaProjecao = line.new(x1=bar_index, y1=ema200, x2=bar_index + futuro, y2=y_futuro, color=color.new(color.yellow, 40), width=2, style=line.style_dashed)

    rsi: Series = ta.rsi(close, rsiLen)

    ph = ta.pivothigh(high, length, length)
    pl = ta.pivotlow(low, length, length)

    topLiquidity: Persistent[float] = na(float)
    bottomLiquidity: Persistent[float] = na(float)
    topRsi: Persistent[float] = na(float)
    botRsi: Persistent[float] = na(float)

    brokenSupport: Persistent[float] = na(float)
    brokenResistance: Persistent[float] = na(float)

    if not na(ph):
        topLiquidity = high[length]
        topRsi = rsi[length]
    if not na(pl):
        bottomLiquidity = low[length]
        botRsi = rsi[length]

    plot(topLiquidity, title='Top Liquidity', color=color.new(color.red, 30), linewidth=2, style=plot.style_circles, offset=-length)
    plot(bottomLiquidity, title='Bottom Liquidity', color=color.new(color.green, 30), linewidth=2, style=plot.style_circles, offset=-length)

    if close < bottomLiquidity and close[1] >= bottomLiquidity:
        brokenSupport = bottomLiquidity

    if close > topLiquidity and close[1] <= topLiquidity:
        brokenResistance = topLiquidity

    plot(brokenSupport, title='Retest Target (Short)', color=color.new(color.orange, 50), style=plot.style_cross, linewidth=1)
    plot(brokenResistance, title='Retest Target (Long)', color=color.new(color.aqua, 50), style=plot.style_cross, linewidth=1)

    isGap = low > high[1] or high < low[1]

    sweepUp: Series = high > topLiquidity and close < topLiquidity and (not isGap or not ignorarGaps)
    sweepDown: Series = low < bottomLiquidity and close > bottomLiquidity and (not isGap or not ignorarGaps)

    bearDiv: Series = sweepUp and rsi < topRsi
    bullDiv: Series = sweepDown and rsi > botRsi

    retesteBaixa: Series = high >= brokenSupport and close < brokenSupport and (open < brokenSupport)
    retesteAlta: Series = low <= brokenResistance and close > brokenResistance and (open > brokenResistance)

    plotshape(mostrarSimples and sweepUp and (not bearDiv) and (not sweepUp[1]), title='Simple Top Sweep', location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)
    plotshape(mostrarSimples and sweepDown and (not bullDiv) and (not sweepDown[1]), title='Simple Bottom Sweep', location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)

    plotshape(bearDiv and (not bearDiv[1]), title='BEAR DIV', location=location.abovebar, color=color.purple, style=shape.labeldown, text='BEAR\nDIV', textcolor=color.white, size=size.small)
    plotshape(bullDiv and (not bullDiv[1]), title='BULL DIV', location=location.belowbar, color=color.teal, style=shape.labelup, text='BULL\nDIV', textcolor=color.white, size=size.small)

    plotshape(retesteBaixa and (not retesteBaixa[1]), title='SHORT RETEST', location=location.abovebar, color=color.orange, style=shape.xcross, text='RETEST\nSHORT', textcolor=color.orange, size=size.small)
    plotshape(retesteAlta and (not retesteAlta[1]), title='LONG RETEST', location=location.belowbar, color=color.aqua, style=shape.xcross, text='RETEST\nLONG', textcolor=color.aqua, size=size.small)

    alertcondition(bearDiv and (not bearDiv[1]), title='🔴 SELL (Top)', message='Short Opportunity (Divergence & Sweep)')
    alertcondition(bullDiv and (not bullDiv[1]), title='🟢 BUY (Bottom)', message='Long Opportunity (Divergence & Sweep)')
    alertcondition(retesteBaixa and (not retesteBaixa[1]), title='⚠️ SNIPER ALERT: Short Retest', message='Price retesting broken support. Short Opportunity!')
    alertcondition(retesteAlta and (not retesteAlta[1]), title='⚠️ SNIPER ALERT: Long Retest', message='Price retesting broken resistance. Long Opportunity!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
