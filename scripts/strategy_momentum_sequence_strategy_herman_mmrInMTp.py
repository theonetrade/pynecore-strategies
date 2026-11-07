"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barstate, close, color, currency, high, input, location, low, na, open,
    plot, plotshape, position, script, shape, size, strategy, string, table
)
from pynecore.types import Color, Persistent, Table

G_SEQUENCE: str = "Sequence Settings"
G_TRADE: str = "Trade Settings"
G_VISUALS: str = "Visuals"
G_TABLE: str = "Statistics Table"


@script.strategy("Momentum Sequence Strategy [Herman]", overlay=True, pyramiding=0, initial_capital=50000, currency=currency.USD, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=2.5, slippage=1, margin_long=5, margin_short=5)
def main(
    followingCandles=input.int(5, title="Following Candles", options=(2, 3, 4, 5), group=G_SEQUENCE, tooltip="Number of consecutive candles required after the main candle."),
    takeProfitR=input.string("1.5R", title="Take Profit", options=("0.5R", "1R", "1.5R", "2R"), group=G_TRADE),
    enableLongTrades=input.bool(True, title="Long Trades", group=G_TRADE, tooltip="Enable or disable Long trades."),
    enableShortTrades=input.bool(False, title="Short Trades", group=G_TRADE, tooltip="Enable or disable Short trades."),
    showSignal=input.bool(True, title="Show Entry Signal", group=G_VISUALS),
    showSLTP=input.bool(True, title="Show Stop Loss / Take Profit", group=G_VISUALS),
    showTable=input.bool(True, "Show Table", group=G_TABLE),
    tableTheme=input.string("Light", "Theme", options=("Dark", "Light"), group=G_TABLE),
    tableSize=input.string("small", "Size", options=("tiny", "small", "normal", "large"), group=G_TABLE),
    tablePos=input.string(position.top_right, "Position", options=(position.top_right, position.bottom_right, position.top_left, position.bottom_left), group=G_TABLE)
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

    stopLossPriceDisplay: Persistent[float] = na(float)
    takeProfitPriceDisplay: Persistent[float] = na(float)

    mainBearish = close[followingCandles] < open[followingCandles]

    mainBullish = close[followingCandles] > open[followingCandles]

    validBullishSequence: bool = True

    for i in pine_range(0, followingCandles - 1):
        if close[i] <= open[i]:
            validBullishSequence = False

        if low[i] <= low[followingCandles]:
            validBullishSequence = False

        if i < followingCandles - 1:
            if close[i] <= close[i + 1]:
                validBullishSequence = False

    validBearishSequence: bool = True

    for i in pine_range(0, followingCandles - 1):
        if close[i] >= open[i]:
            validBearishSequence = False

        if high[i] >= high[followingCandles]:
            validBearishSequence = False

        if i < followingCandles - 1:
            if close[i] >= close[i + 1]:
                validBearishSequence = False

    longSetup = mainBearish and validBullishSequence

    shortSetup = mainBullish and validBearishSequence

    if enableLongTrades and longSetup and (strategy.position_size == 0):
        stopLossPrice = low[followingCandles]

        longRisk = close - stopLossPrice

        takeProfitPrice = close + longRisk * rrMultiple

        strategy.entry('Long', strategy.long)

    if enableShortTrades and shortSetup and (strategy.position_size == 0):
        stopLossPrice = high[followingCandles]

        shortRisk = stopLossPrice - close

        takeProfitPrice = close - shortRisk * rrMultiple

        strategy.entry('Short', strategy.short)

    if not na(stopLossPrice) and strategy.position_size > 0:
        strategy.exit('Long Take Profit / Stop Loss', from_entry='Long', stop=stopLossPrice, limit=takeProfitPrice)

    if not na(stopLossPrice) and strategy.position_size < 0:
        strategy.exit('Short Take Profit / Stop Loss', from_entry='Short', stop=stopLossPrice, limit=takeProfitPrice)

    if strategy.position_size == 0:
        stopLossPriceDisplay = na
        takeProfitPriceDisplay = na
    else:
        stopLossPriceDisplay = stopLossPrice
        takeProfitPriceDisplay = takeProfitPrice

    c_green: Persistent[Color] = na(Color)
    c_red: Persistent[Color] = na(Color)
    c_nbg: Persistent[Color] = na(Color)
    c_ntxt: Persistent[Color] = na(Color)
    c_hdr: Persistent[Color] = na(Color)
    c_sep: Persistent[Color] = na(Color)

    if tableTheme == 'Dark':
        c_green = color.new('#29A071')
        c_red = color.new('#E54B4B')

        c_nbg = color.new('#2A2E39')
        c_ntxt = color.new('#E0E0E0')

        c_hdr = color.new('#3C415E')
        c_sep = color.new('#454955')
    else:
        c_green = color.new('#29A071')
        c_red = color.new('#E54B4B')

        c_nbg = color.new('#F7F7F7')
        c_ntxt = color.new('#1E2025')

        c_hdr = color.new('#E5EEF7')
        c_sep = color.new('#E1E4E6')

    c_dhdr: Color = color.new('#F0F3F6')

    nbg2: Color = color.new(c_nbg, 50)

    def font_sz(sz):
        __block_result_1__ = na
        __switch__ = sz
        if __switch__ == "tiny":
            __block_result_1__ = size.tiny
        elif __switch__ == "small":
            __block_result_1__ = size.small
        elif __switch__ == "normal":
            __block_result_1__ = size.normal
        elif __switch__ == "large":
            __block_result_1__ = size.large
        else:
            __block_result_1__ = size.small
        return __block_result_1__

    tbl: Persistent[Table] = table.new(tablePos, 2, 6)

    if barstate.islast:
        table.clear(tbl, 0, 0, 1, 5)

        if showTable:
            r: int = 0

            fsz = font_sz(tableSize)

            table.cell(tbl, 0, r, 'Momentum Sequence Strategy [Herman]', text_color=c_ntxt, bgcolor=c_hdr, text_size=fsz)

            table.cell(tbl, 1, r, '', text_color=c_ntxt, bgcolor=c_hdr)

            r += 1

            table.cell(tbl, 0, r, 'Current Settings', text_color=c_ntxt, bgcolor=c_dhdr, text_size=fsz)

            table.cell(tbl, 1, r, '', bgcolor=c_dhdr)

            r += 1

            table.cell(tbl, 0, r, 'Take Profit', bgcolor=nbg2, text_color=c_ntxt, text_size=fsz)

            table.cell(tbl, 1, r, takeProfitR, bgcolor=nbg2, text_color=c_ntxt, text_size=fsz)

            r += 1

            table.cell(tbl, 0, r, 'Consecutive Candles', bgcolor=c_nbg, text_color=c_ntxt, text_size=fsz)

            table.cell(tbl, 1, r, string.tostring(followingCandles), bgcolor=c_nbg, text_color=c_ntxt, text_size=fsz)

            r += 1

            table.cell(tbl, 0, r, 'Long Trades', bgcolor=nbg2, text_color=c_ntxt, text_size=fsz)

            table.cell(tbl, 1, r, 'ON' if enableLongTrades else 'OFF', bgcolor=nbg2, text_color=c_green if enableLongTrades else c_red, text_size=fsz)

            r += 1

            table.cell(tbl, 0, r, 'Short Trades', bgcolor=c_nbg, text_color=c_ntxt, text_size=fsz)

            table.cell(tbl, 1, r, 'ON' if enableShortTrades else 'OFF', bgcolor=c_nbg, text_color=c_green if enableShortTrades else c_red, text_size=fsz)

    plotshape(showSignal and enableLongTrades and longSetup and (strategy.position_size == 0), title='Long Setup', location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)

    plotshape(showSignal and enableShortTrades and shortSetup and (strategy.position_size == 0), title='Short Setup', location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)

    plot(stopLossPriceDisplay if showSLTP else na, color=color.red, title='Stop Loss', linewidth=2, style=plot.style_linebr)

    plot(takeProfitPriceDisplay if showSLTP else na, color=color.green, title='Take Profit', linewidth=2, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
