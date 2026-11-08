"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barstate, close, color, fill, input, location, math, na,
    nz, plot, plotshape, position, request, script, shape, size, string, syminfo, ta, table,
    timeframe
)
from pynecore.types import Persistent, Series, Table


@script.indicator("MTF Trend Dashboard", shorttitle="MTF Trend", overlay=True)
def main(
    fastLen=input.int(20, "Fast EMA", minval=1, group="Trend"),
    slowLen=input.int(50, "Slow EMA", minval=1, group="Trend"),
    rsiLen=input.int(14, "RSI Length", minval=1, group="Trend"),
    showSignals=input.bool(True, "Show EMA cross signals", group="Trend"),
    tf1=input.timeframe("5", "Timeframe 1", group="Dashboard"),
    tf2=input.timeframe("15", "Timeframe 2", group="Dashboard"),
    tf3=input.timeframe("60", "Timeframe 3", group="Dashboard"),
    tf4=input.timeframe("240", "Timeframe 4", group="Dashboard"),
    tf5=input.timeframe("D", "Timeframe 5", group="Dashboard"),
    tablePos=input.string("Top Right", "Dashboard position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group="Dashboard"),
    tableSize=input.string("Small", "Text size", options=("Tiny", "Small", "Normal"), group="Dashboard")
):
    def trendState():
        f = ta.ema(close, fastLen)
        s = ta.ema(close, slowLen)
        r = ta.rsi(close, rsiLen)
        st: int = 0
        if close > f and f > s and (r > 50):
            st = 1
        elif close < f and f < s and (r < 50):
            st = -1
        return (st, r)

    s1, r1 = request.security(syminfo.tickerid, tf1, trendState())
    s2, r2 = request.security(syminfo.tickerid, tf2, trendState())
    s3, r3 = request.security(syminfo.tickerid, tf3, trendState())
    s4, r4 = request.security(syminfo.tickerid, tf4, trendState())
    s5, r5 = request.security(syminfo.tickerid, tf5, trendState())

    score = nz(s1) + nz(s2) + nz(s3) + nz(s4) + nz(s5)
    allBull: Series = score == 5
    allBear: Series = score == -5

    fastEma = ta.ema(close, fastLen)
    slowEma = ta.ema(close, slowLen)
    stNow, _ = trendState()

    trendCol = color.teal if stNow == 1 else color.red if stNow == -1 else color.gray
    p1 = plot(fastEma, 'Fast EMA', trendCol, 2)
    p2 = plot(slowEma, 'Slow EMA', color.new(trendCol, 40), 1)
    fill(p1, p2, color.new(trendCol, 85), title='EMA cloud')

    bullCross = ta.crossover(fastEma, slowEma)
    bearCross = ta.crossunder(fastEma, slowEma)
    plotshape(showSignals and bullCross, 'Bullish cross', shape.triangleup, location.belowbar, color.teal, size=size.small)
    plotshape(showSignals and bearCross, 'Bearish cross', shape.triangledown, location.abovebar, color.red, size=size.small)

    alertcondition(bullCross, 'Bullish EMA cross', '{{ticker}}: bullish EMA crossover on {{interval}}')
    alertcondition(bearCross, 'Bearish EMA cross', '{{ticker}}: bearish EMA crossover on {{interval}}')
    alertcondition(allBull and (not allBull[1]), 'All timeframes bullish', '{{ticker}}: all dashboard timeframes are bullish')
    alertcondition(allBear and (not allBear[1]), 'All timeframes bearish', '{{ticker}}: all dashboard timeframes are bearish')

    __block_result__ = na
    __switch__ = tablePos
    if __switch__ == "Top Left":
        __block_result__ = position.top_left
    elif __switch__ == "Bottom Right":
        __block_result__ = position.bottom_right
    elif __switch__ == "Bottom Left":
        __block_result__ = position.bottom_left
    else:
        __block_result__ = position.top_right
    tPos = __block_result__

    __block_result_1__ = na
    __switch__ = tableSize
    if __switch__ == "Tiny":
        __block_result_1__ = size.tiny
    elif __switch__ == "Normal":
        __block_result_1__ = size.normal
    else:
        __block_result_1__ = size.small
    tSize = __block_result_1__

    dash: Persistent[Table] = table.new(tPos, 3, 7, bgcolor=color.new(color.new('#0B1220'), 10), border_color=color.new(color.gray, 70), border_width=1)

    def tfName(tf: str):
        sec = timeframe.in_seconds(tf)
        return string.tostring(math.round(sec / 60)) + 'm' if sec < 3600 else string.tostring(math.round(sec / 3600)) + 'H' if sec < 86400 else tf

    def fillRow(row: int, tf: str, st: int, r: float):
        txt = '▲ Bull' if st == 1 else '▼ Bear' if st == -1 else '• Neutral'
        bg = color.new(color.teal, 30) if st == 1 else color.new(color.red, 30) if st == -1 else color.new(color.gray, 60)
        table.cell(dash, 0, row, tfName(tf), text_color=color.white, text_size=tSize)
        table.cell(dash, 1, row, txt, bgcolor=bg, text_color=color.white, text_size=tSize)
        return table.cell(dash, 2, row, '-' if na(r) else string.tostring(r, '#.0'), text_color=color.white, text_size=tSize)

    if barstate.islast:
        table.cell(dash, 0, 0, 'TF', text_color=color.silver, text_size=tSize)
        table.cell(dash, 1, 0, 'Trend', text_color=color.silver, text_size=tSize)
        table.cell(dash, 2, 0, 'RSI', text_color=color.silver, text_size=tSize)
        fillRow(1, tf1, s1, r1)
        fillRow(2, tf2, s2, r2)
        fillRow(3, tf3, s3, r3)
        fillRow(4, tf4, s4, r4)
        fillRow(5, tf5, s5, r5)
        bias = 'Bullish bias' if score >= 3 else 'Bearish bias' if score <= -3 else 'Mixed'
        biasBg = color.new(color.teal, 20) if score >= 3 else color.new(color.red, 20) if score <= -3 else color.new(color.gray, 50)
        table.cell(dash, 0, 6, 'Score ' + string.tostring(score) + '/5', text_color=color.white, text_size=tSize)
        table.cell(dash, 1, 6, bias, bgcolor=biasBg, text_color=color.white, text_size=tSize)
        table.merge_cells(dash, 1, 6, 2, 6)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)