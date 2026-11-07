"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, barstate, close, color, format, high, input, location, low, na,
    open, plot, plotshape, position, request, script, shape, size, strategy, string, syminfo, ta,
    table, text, time, timeframe, volume
)
from pynecore.types import Persistent, Table


@script.strategy("Universal Breakout Strategy [KedArc Quant]", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_every_tick=True)
def main(
    len=input.int(20, "Lookback Period", minval=1),
    bbMult=input.float(2.0, "Bollinger Multiplier", minval=0.1, step=0.1),
    mode=input.string("Prev Day", title="Breakout Mode", options=("Prev Day", "Bollinger", "Volume", "ATR Stop", "Time Filter", "EMA Trend", "RSI Confirm", "Candle Confirm")),
    sess=input.session("0900-1500", "Session (exchange time)"),
    intrabar=input.bool(False, "Evaluate intrabar (simulate tick mode)"),
    showTable=input.bool(True, "Show Info Table"),
    showStats=input.bool(True, "Show P&L Stats"),
    tableCorner=input.string("Top Right", "Table Corner", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"))
):
    hhPrev = ta.highest(high[1], len)
    llPrev = ta.lowest(low[1], len)

    prevHigh = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_on)
    prevLow = request.security(syminfo.tickerid, 'D', low[1], lookahead=barmerge.lookahead_on)

    basis, bbUpper, bbLower = ta.bb(close, len, bbMult)

    volSma = ta.sma(volume, len)
    volConfirm = volume > volSma

    atr = ta.atr(len)

    inSession = not na(time(timeframe.period, sess))

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)
    trendUp = emaFast > emaSlow
    trendDown = emaFast < emaSlow

    rsiVal = ta.rsi(close, len)

    bullishCndl = close > open and close > close[1]
    bearishCndl = close < open and close < close[1]
    candleType = 'Bullish' if bullishCndl else 'Bearish' if bearishCndl else 'Neutral'

    longBase = high > hhPrev if intrabar else ta.crossover(close, hhPrev)
    shortBase = low < llPrev if intrabar else ta.crossunder(close, llPrev)

    longCond = ta.crossover(close, prevHigh) if mode == 'Prev Day' else ta.crossover(close, bbUpper) if mode == 'Bollinger' else longBase and volConfirm if mode == 'Volume' else longBase and high - close[1] > atr if mode == 'ATR Stop' else longBase and inSession if mode == 'Time Filter' else longBase and trendUp if mode == 'EMA Trend' else longBase and rsiVal > 55 if mode == 'RSI Confirm' else longBase and bullishCndl if mode == 'Candle Confirm' else False

    shortCond = ta.crossunder(close, prevLow) if mode == 'Prev Day' else ta.crossunder(close, bbLower) if mode == 'Bollinger' else shortBase and volConfirm if mode == 'Volume' else shortBase and close[1] - low > atr if mode == 'ATR Stop' else shortBase and inSession if mode == 'Time Filter' else shortBase and trendDown if mode == 'EMA Trend' else shortBase and rsiVal < 45 if mode == 'RSI Confirm' else shortBase and bearishCndl if mode == 'Candle Confirm' else False

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(prevHigh if mode == 'Prev Day' else na, 'Prev High', color=color.new(color.green, 0))
    plot(prevLow if mode == 'Prev Day' else na, 'Prev Low', color=color.new(color.red, 0))

    plot(hhPrev if mode != 'Bollinger' and mode != 'Prev Day' else na, 'HH prev (len)', color=color.new(color.teal, 0))
    plot(llPrev if mode != 'Bollinger' and mode != 'Prev Day' else na, 'LL prev (len)', color=color.new(color.orange, 0))

    plot(bbUpper if mode == 'Bollinger' else na, 'BB Upper', color=color.new(color.fuchsia, 0))
    plot(basis if mode == 'Bollinger' else na, 'BB Basis', color=color.new(color.gray, 60))
    plot(bbLower if mode == 'Bollinger' else na, 'BB Lower', color=color.new(color.aqua, 0))

    plotshape(longCond, title='Long', location=location.belowbar, color=color.green, style=shape.triangleup, size=size.tiny, text='↗︎')
    plotshape(shortCond, title='Short', location=location.abovebar, color=color.red, style=shape.triangledown, size=size.tiny, text='↘︎')

    infoTbl: Persistent[Table] = na(Table)
    if barstate.isfirst:
        if tableCorner == 'Top Right':
            infoTbl = table.new(position.top_right, columns=2, rows=9, border_width=1)
        elif tableCorner == 'Top Left':
            infoTbl = table.new(position.top_left, columns=2, rows=9, border_width=1)
        elif tableCorner == 'Bottom Right':
            infoTbl = table.new(position.bottom_right, columns=2, rows=9, border_width=1)
        else:
            infoTbl = table.new(position.bottom_left, columns=2, rows=9, border_width=1)

    def f_set(row, label__ren__, value, txtColor = color.white):
        table.cell(infoTbl, 0, row, label__ren__, text_color=color.white, text_halign=text.align_left, bgcolor=color.black)
        return table.cell(infoTbl, 1, row, value, text_color=txtColor, text_halign=text.align_right, bgcolor=color.black)

    def f_clear(row):
        table.cell(infoTbl, 0, row, '', bgcolor=color.black)
        return table.cell(infoTbl, 1, row, '', bgcolor=color.black)

    def fmtPrice(x):
        return string.tostring(x, format.mintick)

    def fmtVol(x):
        return string.tostring(x, format.volume)

    def fmt2(x):
        return string.tostring(x, '#.##')

    totalTrades = strategy.closedtrades
    winTrades = strategy.wintrades
    lossTrades = strategy.losstrades
    winRate = 100.0 * winTrades / totalTrades if totalTrades > 0 else na
    avgTrade = strategy.netprofit / totalTrades if totalTrades > 0 else na

    if barstate.islast and showTable:
        f_set(0, 'Universal Breakout', syminfo.ticker)
        f_set(1, 'Mode', mode)
        f_set(2, 'Current Price', fmtPrice(close))

        f_clear(3)
        f_clear(4)

        if mode == 'Prev Day':
            f_set(3, 'Prev High', fmtPrice(prevHigh))
            f_set(4, 'Prev Low', fmtPrice(prevLow))
        elif mode == 'Bollinger':
            f_set(3, 'Upper BB', fmtPrice(bbUpper))
            f_set(4, 'Lower BB', fmtPrice(bbLower))
        elif mode == 'Volume':
            f_set(3, 'Avg Volume', fmtVol(volSma))
            f_set(4, 'Volume', fmtVol(volume))
        elif mode == 'ATR Stop':
            f_set(3, 'ATR (' + string.tostring(len) + ')', fmt2(atr))
        elif mode == 'Time Filter':
            pass
        elif mode == 'EMA Trend':
            f_set(3, 'EMA Fast (9)', fmtPrice(emaFast))
            f_set(4, 'EMA Slow (21)', fmtPrice(emaSlow))
        elif mode == 'RSI Confirm':
            rsiColor = color.green if rsiVal > 55 else color.red if rsiVal < 45 else color.white
            f_set(3, 'RSI (' + string.tostring(len) + ')', fmt2(rsiVal), rsiColor)
        elif mode == 'Candle Confirm':
            cCol = color.green if candleType == 'Bullish' else color.red if candleType == 'Bearish' else color.white
            f_set(3, 'Candle', candleType, cCol)

        if showStats:
            netCol = color.green if strategy.netprofit >= 0 else color.red
            f_set(5, 'Net Profit', string.tostring(strategy.netprofit, '#.##'), netCol)
            f_set(6, 'Trades (W/L)', string.tostring(winTrades) + '/' + string.tostring(lossTrades))
            f_set(7, 'Win Rate %', '—' if na(winRate) else string.tostring(winRate, '#.##'))
            f_set(8, 'Avg Trade', '—' if na(avgTrade) else string.tostring(avgTrade, '#.##'))
        else:
            f_clear(5)
            f_clear(6)
            f_clear(7)
            f_clear(8)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
