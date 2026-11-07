"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barstate, bgcolor, close, color, currency, high, input, location, low,
    na, open, plot, plotshape, position, script, shape, size, strategy, string, syminfo, ta, table,
    text
)
from pynecore.types import Persistent, Series, Table

grpSeq: str = "Pattern Shape"
grpRsi: str = "Momentum Check"
grpTrade: str = "Trade Management"
grpVis: str = "Visuals"


@script.strategy("Sequence Snap | RSI-Confirmed Reversal Scalper", overlay=True, pyramiding=0, initial_capital=50000, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=5, margin_short=5)
def main(
    runLength=input.int(5, "Candles In The Run", options=(2, 3, 4, 5), group=grpSeq, tooltip="How many candles in a row must push the same direction after the reversal candle."),
    tolerancePct=input.float(0.05, "Wobble Allowance (%)", step=0.01, group=grpSeq, tooltip="Lets one candle in the run close slightly against the trend and still count. Set to 0 to require a perfectly clean run."),
    useRsiFilter=input.bool(True, "Require RSI Agreement", group=grpRsi, tooltip="The candle pattern alone is just shape — this makes sure real momentum backs it up."),
    rsiLen=input.int(14, "RSI Length", group=grpRsi),
    rsiMinLong=input.int(40, "RSI Floor For Longs", group=grpRsi),
    rsiMaxShort=input.int(60, "RSI Ceiling For Shorts", group=grpRsi),
    takeProfitR=input.string("1.5R", "Reward Target", options=("0.5R", "1R", "1.5R", "2R"), group=grpTrade),
    enableLongTrades=input.bool(True, "Allow Longs", group=grpTrade),
    enableShortTrades=input.bool(False, "Allow Shorts", group=grpTrade),
    showSignal=input.bool(True, "Show Entry Arrows", group=grpVis),
    showSLTP=input.bool(True, "Show Stop / Target Lines", group=grpVis),
    showFlash=input.bool(True, "Flash Background On Entry", group=grpVis),
    showDash=input.bool(True, "Show Dashboard", group=grpVis),
    dashPos=input.string("Top Right", "Dashboard Position", options=("Top Right", "Bottom Right", "Top Left", "Bottom Left"), group=grpVis),
    dashSize=input.string("Small", "Dashboard Text Size", options=("Tiny", "Small", "Normal"), group=grpVis),
    colBull=input.color(color.new('#00C176'), "Bull Color", group=grpVis),
    colBear=input.color(color.new('#FF3B30'), "Bear Color", group=grpVis),
    colDashBg=input.color(color.new('#161B22'), "Panel Background", group=grpVis),
    colDashHead=input.color(color.new('#0D1117'), "Header Background", group=grpVis)
):
    __block_result__ = na
    __switch__ = takeProfitR
    if __switch__ == "0.5R":
        __block_result__ = 0.5
    elif __switch__ == "1R":
        __block_result__ = 1.0
    elif __switch__ == "1.5R":
        __block_result__ = 1.5
    elif __switch__ == "2R":
        __block_result__ = 2.0
    else:
        __block_result__ = 1.5
    rrMultiple = __block_result__

    stopLossPrice: Persistent[float] = na(float)
    takeProfitPrice: Persistent[float] = na(float)
    stopDisplay: Persistent[float] = na(float)
    tpDisplay: Persistent[float] = na(float)

    rsiVal: Series = ta.rsi(close, rsiLen)
    rsiRising = rsiVal > rsiVal[1]
    rsiFalling = rsiVal < rsiVal[1]

    rsiOkLong = not useRsiFilter or (rsiVal > rsiMinLong and rsiRising)
    rsiOkShort = not useRsiFilter or (rsiVal < rsiMaxShort and rsiFalling)

    reversalWasDown = close[runLength] < open[runLength]
    reversalWasUp = close[runLength] > open[runLength]

    runIsBullish: bool = True

    for i in pine_range(0, runLength - 1):
        if close[i] <= open[i]:
            runIsBullish = False
        if low[i] <= low[runLength]:
            runIsBullish = False
        if i < runLength - 1:
            floorClose = close[i + 1] * (1 - tolerancePct / 100)
            if close[i] <= floorClose:
                runIsBullish = False

    runIsBearish: bool = True

    for i in pine_range(0, runLength - 1):
        if close[i] >= open[i]:
            runIsBearish = False
        if high[i] >= high[runLength]:
            runIsBearish = False
        if i < runLength - 1:
            ceilClose = close[i + 1] * (1 + tolerancePct / 100)
            if close[i] >= ceilClose:
                runIsBearish = False

    longSetup = reversalWasDown and runIsBullish and rsiOkLong
    shortSetup = reversalWasUp and runIsBearish and rsiOkShort

    if enableLongTrades and longSetup and (strategy.position_size == 0):
        stopLossPrice = low[runLength]
        riskPts = close - stopLossPrice
        takeProfitPrice = close + riskPts * rrMultiple
        strategy.entry('Long', strategy.long)

    if enableShortTrades and shortSetup and (strategy.position_size == 0):
        stopLossPrice = high[runLength]
        riskPts = stopLossPrice - close
        takeProfitPrice = close - riskPts * rrMultiple
        strategy.entry('Short', strategy.short)

    if not na(stopLossPrice) and strategy.position_size > 0:
        strategy.exit('Long Exit', from_entry='Long', stop=stopLossPrice, limit=takeProfitPrice)

    if not na(stopLossPrice) and strategy.position_size < 0:
        strategy.exit('Short Exit', from_entry='Short', stop=stopLossPrice, limit=takeProfitPrice)

    if strategy.position_size == 0:
        stopDisplay = na
        tpDisplay = na
    else:
        stopDisplay = stopLossPrice
        tpDisplay = takeProfitPrice

    bgcolor(color.new(colBull, 85) if showFlash and longSetup and enableLongTrades else na, title='Long Entry Flash')
    bgcolor(color.new(colBear, 85) if showFlash and shortSetup and enableShortTrades else na, title='Short Entry Flash')

    plotshape(showSignal and enableLongTrades and longSetup and (strategy.position_size == 0), title='Long Signal', location=location.belowbar, color=colBull, style=shape.triangleup, size=size.small)

    plotshape(showSignal and enableShortTrades and shortSetup and (strategy.position_size == 0), title='Short Signal', location=location.abovebar, color=colBear, style=shape.triangledown, size=size.small)

    plot(stopDisplay if showSLTP else na, 'Stop Loss', color=colBear, linewidth=2, style=plot.style_linebr)
    plot(tpDisplay if showSLTP else na, 'Take Profit', color=colBull, linewidth=2, style=plot.style_linebr)

    def f_dashPos(p):
        __block_result_1__ = na
        __switch__ = p
        if __switch__ == "Top Right":
            __block_result_1__ = position.top_right
        elif __switch__ == "Bottom Right":
            __block_result_1__ = position.bottom_right
        elif __switch__ == "Top Left":
            __block_result_1__ = position.top_left
        else:
            __block_result_1__ = position.bottom_left
        return __block_result_1__

    def f_dashSize(sz):
        __block_result_2__ = na
        __switch__ = sz
        if __switch__ == "Tiny":
            __block_result_2__ = size.tiny
        elif __switch__ == "Small":
            __block_result_2__ = size.small
        else:
            __block_result_2__ = size.normal
        return __block_result_2__

    dash: Persistent[Table] = table.new(f_dashPos(dashPos), 2, 8, border_width=1, border_color=color.new(colBull, 60))

    if showDash and barstate.islast:
        dSize = f_dashSize(dashSize)
        dbg = color.new(colDashBg, 0)
        hdr = color.new(colDashHead, 0)
        muted = color.new(color.new('#8B949E'), 0)

        posText = 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT'
        posColor = colBull if strategy.position_size > 0 else colBear if strategy.position_size < 0 else muted

        rsiColor = colBull if rsiVal > rsiMinLong else colBear if rsiVal < rsiMaxShort else muted

        table.cell(dash, 0, 0, 'Sequence Snap', text_color=color.white, text_size=dSize, bgcolor=hdr, text_halign=text.align_left)
        table.cell(dash, 1, 0, syminfo.ticker, text_color=muted, text_size=dSize, bgcolor=hdr, text_halign=text.align_right)

        table.cell(dash, 0, 1, 'Position', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 1, posText, text_color=posColor, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 2, 'RSI', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 2, string.tostring(rsiVal, '#.#'), text_color=rsiColor, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 3, 'Run Length', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 3, string.tostring(runLength) + ' candles', text_color=color.white, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 4, 'Wobble Allowance', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 4, string.tostring(tolerancePct, '#.##') + '%', text_color=color.white, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 5, 'RSI Filter', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 5, 'ON' if useRsiFilter else 'OFF', text_color=colBull if useRsiFilter else muted, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 6, 'Longs / Shorts', text_color=muted, text_size=dSize, bgcolor=dbg)
        sideText = ('ON' if enableLongTrades else 'OFF') + ' / ' + ('ON' if enableShortTrades else 'OFF')
        table.cell(dash, 1, 6, sideText, text_color=color.white, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)

        table.cell(dash, 0, 7, 'Target', text_color=muted, text_size=dSize, bgcolor=dbg)
        table.cell(dash, 1, 7, takeProfitR, text_color=color.white, text_size=dSize, bgcolor=dbg, text_halign=text.align_right)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
