"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, high,
    input, label, line, location, low, math, na, nz, plot, plotshape, script, shape, size,
    strategy, ta
)
from pynecore.types import Color, Line, Persistent, Series


@script.strategy("Market Trend Levels Non-Repainting [BigBeluga X PineIndicators]", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, max_boxes_count=500, max_labels_count=500, max_lines_count=500, commission_value=0.05, process_orders_on_close=True, margin_long=20, margin_short=20)
def main(
    tradeDir=input.string("Long Only", "Trade Direction", options=("Long Only", "Short Only", "Long & Short"), group="Trade"),
    length1=input.int(12, "Fast", group="Trend"),
    length2=input.int(25, "Slow", group="Trend"),
    extend__ren__=input.bool(False, "Extend Lines", group="Levels"),
    qty=input.int(50, "Display Last", group="Levels"),
    col1=input.color(color.new('#26BA9F'), "", inline="col", group="Color"),
    col2=input.color(color.new('#6626BA'), "", inline="col", group="Color"),
    applyExitFilters=input.bool(False, "Apply Filters for Exit", group="Filters"),
    useRSI=input.bool(False, "RSI Filter", group="Filters"),
    rsiLength=input.int(14, "RSI Length", group="Filters"),
    rsiLongThreshold=input.float(50, "RSI Long Threshold", group="Filters"),
    rsiShortThreshold=input.float(50, "RSI Short Threshold", group="Filters"),
    useMACD=input.bool(False, "MACD Filter", group="Filters"),
    macdFast=input.int(12, "MACD Fast", group="Filters"),
    macdSlow=input.int(26, "MACD Slow", group="Filters"),
    macdSignal=input.int(9, "MACD Signal", group="Filters"),
    useStoch=input.bool(False, "Stochastic Filter", group="Filters"),
    stochKLength=input.int(14, "Stoch %K Length", group="Filters"),
    stochDLength=input.int(3, "Stoch %D Length", group="Filters"),
    stochSmooth=input.int(3, "Stoch Smooth", group="Filters"),
    stochLongThreshold=input.float(50, "Stoch Long Threshold", group="Filters"),
    stochShortThreshold=input.float(50, "Stoch Short Threshold", group="Filters"),
    useBB=input.bool(False, "Bollinger Bands Filter", group="Filters"),
    bbLength=input.int(20, "BB Length", group="Filters"),
    bbMult=input.float(2.0, "BB Multiplier", group="Filters"),
    useADX=input.bool(False, "ADX Filter", group="Filters"),
    adxLength=input.int(14, "ADX Length", group="Filters"),
    adxThreshold=input.float(25, "ADX Threshold", group="Filters"),
    useCCI=input.bool(False, "CCI Filter", group="Filters"),
    cciLength=input.int(20, "CCI Length", group="Filters"),
    useWilliams=input.bool(False, "Williams %R Filter", group="Filters"),
    williamsLength=input.int(14, "Williams %R Length", group="Filters"),
    williamsLongThreshold=input.float(-50, "Williams %R Long Threshold", group="Filters"),
    williamsShortThreshold=input.float(-50, "Williams %R Short Threshold", group="Filters")
):
    lines_up: Persistent[list[Line]] = array.new_line()
    lines_dn: Persistent[list[Line]] = array.new_line()

    ema1: Series[float] = ta.ema(close, length1)
    ema2: float = ta.ema(close, length2)
    diff: float = ema1 - ema2

    cross_up: bool = ta.crossover(ema1, ema2) and barstate.isconfirmed
    cross_dn: bool = ta.crossunder(ema1, ema2) and barstate.isconfirmed
    rsiValue: float = ta.rsi(close, rsiLength)
    macdLine, signalLine, histLine = ta.macd(close, macdFast, macdSlow, macdSignal)
    k: float = ta.sma(ta.stoch(close, high, low, stochKLength), stochSmooth)
    d: float = ta.sma(k, stochDLength)
    basis: float = ta.sma(close, bbLength)
    dev: float = bbMult * ta.stdev(close, bbLength)
    upper: float = basis + dev
    lower: float = basis - dev

    prevClose: float = nz(close[1], close)
    tr: float = math.max(high - low, math.max(math.abs(high - prevClose), math.abs(low - prevClose)))

    upMove: float = high - nz(high[1])
    downMove: float = nz(low[1]) - low
    plusDM: float = upMove if upMove > downMove and upMove > 0 else 0.0
    minusDM: float = downMove if downMove > upMove and downMove > 0 else 0.0

    atr: float = ta.rma(tr, adxLength)
    smPlusDM: float = ta.rma(plusDM, adxLength)
    smMinusDM: float = ta.rma(minusDM, adxLength)
    plusDI: float = 100 * (smPlusDM / atr) if atr != 0 else 0.0
    minusDI: float = 100 * (smMinusDM / atr) if atr != 0 else 0.0
    sumDI: float = plusDI + minusDI
    dx: float = 100 * math.abs(plusDI - minusDI) / sumDI if sumDI != 0 else 0.0
    adxValue: float = ta.rma(dx, adxLength)
    cciValue: float = ta.cci(close, cciLength)
    williamsValue: float = ta.wpr(williamsLength)

    filterLong: bool = True
    if useRSI:
        filterLong = filterLong and rsiValue > rsiLongThreshold
    if useMACD:
        filterLong = filterLong and histLine > 0
    if useStoch:
        filterLong = filterLong and k > stochLongThreshold
    if useBB:
        filterLong = filterLong and close > basis
    if useADX:
        filterLong = filterLong and adxValue > adxThreshold
    if useCCI:
        filterLong = filterLong and cciValue > 0
    if useWilliams:
        filterLong = filterLong and williamsValue > williamsLongThreshold

    filterShort: bool = True
    if useRSI:
        filterShort = filterShort and rsiValue < rsiShortThreshold
    if useMACD:
        filterShort = filterShort and histLine < 0
    if useStoch:
        filterShort = filterShort and k < stochShortThreshold
    if useBB:
        filterShort = filterShort and close < basis
    if useADX:
        filterShort = filterShort and adxValue > adxThreshold
    if useCCI:
        filterShort = filterShort and cciValue < 0
    if useWilliams:
        filterShort = filterShort and williamsValue < williamsShortThreshold

    if cross_up:
        longLine = line.new(bar_index, low, bar_index + 25, low, color=col1)
        array.push(lines_dn, longLine)
        label.new(bar_index, low, '●', color=col1, style=label.style_label_up, textcolor=color.white, size=size.tiny)
    if cross_dn:
        shortLine = line.new(bar_index, high, bar_index + 25, high, color=col2)
        array.push(lines_up, shortLine)
        label.new(bar_index, high, '●', color=col2, style=label.style_label_down, textcolor=color.white, size=size.tiny)

    if tradeDir == 'Long & Short':
        if cross_up and strategy.position_size <= 0 and filterLong:
            strategy.entry('Long', strategy.long)

        if cross_dn and strategy.position_size >= 0 and filterShort:
            strategy.entry('Short', strategy.short)

        if applyExitFilters:
            if strategy.position_size > 0 and (not filterLong):
                strategy.close('Long')
            if strategy.position_size < 0 and (not filterShort):
                strategy.close('Short')
    elif tradeDir == 'Long Only':
        if cross_up and strategy.position_size <= 0 and filterLong:
            strategy.entry('Long', strategy.long)
        if (cross_dn or (applyExitFilters and (not filterLong))) and strategy.position_size > 0:
            strategy.close('Long')
    elif tradeDir == 'Short Only':
        if cross_dn and strategy.position_size >= 0 and filterShort:
            strategy.entry('Short', strategy.short)
        if (cross_up or (applyExitFilters and (not filterShort))) and strategy.position_size < 0:
            strategy.close('Short')

    if extend__ren__:
        if array.size(lines_up) > 0:
            for i in pine_range(array.size(lines_up) - 1, 0):
                line_id = array.get(lines_up, i)
                line.set_x2(line_id, bar_index)
                if high > line.get_y2(line_id):
                    line.set_style(line_id, line.style_dotted)

        if array.size(lines_dn) > 0:
            for i in pine_range(array.size(lines_dn) - 1, 0):
                line_id = array.get(lines_dn, i)
                line.set_x2(line_id, bar_index)
                if low < line.get_y2(line_id):
                    line.set_style(line_id, line.style_dotted)

    p1 = plot(ema1, 'Fast EMA', display=display.none, color=col1)
    p2 = plot(ema2, 'Slow EMA', display=display.none, color=col2)
    color1: Color = color.from_gradient(diff, 0, ta.highest(diff, 100), color.new(col1, 70), col1)
    color2: Color = color.from_gradient(diff, ta.lowest(diff, 100), 0, col2, color.new(col2, 70))
    fill(p1, p2, color1 if ema1 > ema2 else color2)
    plotshape(ema1[1] if cross_up or cross_dn else na, 'Signal', shape.xcross, location=location.absolute, offset=-1, color=chart.fg_color)

    a_allLines: list[Line] = line.all
    if array.size(a_allLines) > qty:
        line.delete(array.shift(a_allLines))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
