"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barmerge, barstate, close, color, extend, fill, format,
    high, input, label, line, linefill, low, math, na, plot, position, request, script, size,
    string, syminfo, ta, table, xloc
)
from pynecore.types import Color, Label, Line, LineFill, NA, Persistent, Series, Table

grp_calc: str = "Calculation Settings"
grp_proj: str = "Projection Settings"
grp_color: str = "Color & Visual Settings"
grp_dash: str = "Dashboard Settings"


@script.indicator('ATR Fibonacci Trend Envelopes [BigBeluga]', overlay=True, max_labels_count=500, max_lines_count=500)
def main(
    maType=input.string("RMA", "MA Type", options=("SMA", "EMA", "WMA", "HMA", "RMA"), group=grp_calc, tooltip="Select the Moving Average type used to calculate the baseline (Basis)."),
    maLength=input.int(100, 'MA Length', group=grp_calc, tooltip="The number of bars used to calculate the trend baseline."),
    atrLength=input.int(100, 'ATR Length', group=grp_calc, tooltip="The lookback period for Average True Range, used to determine envelope width."),
    atrMult=input.float(3.0, 'ATR Multiplier', group=grp_calc, tooltip="Multiplies the ATR to expand or contract the Trend Envelopes."),
    showProj=input.bool(True, "Show Projections", group=grp_proj, tooltip="Toggle the visibility of dotted line projections for the trend and Fibonacci levels."),
    projLen=input.int(50, "Projection Length (Bars)", minval=1, group=grp_proj, tooltip="Determines how many bars into the future the levels are projected."),
    colorUp=input.color(color.rgb(36, 192, 212), "Uptrend Color", group=grp_color, tooltip="Color used for the baseline and labels during a bullish trend."),
    colorDown=input.color(color.rgb(235, 51, 51), "Downtrend Color", group=grp_color, tooltip="Color used for the baseline and labels during a bearish trend."),
    colorMid=input.color(color.gray, "0.5 Fib Color", group=grp_color, tooltip="Color for the 50% Fibonacci retracement level."),
    baseFill=input.color(color.rgb(255, 123, 0), "Pocket Base Color", group=grp_color, tooltip="Base color for the Dynamic Golden Pocket (0.618 - 0.786)."),
    showDash=input.bool(True, "Show MTF Dashboard", group=grp_dash, tooltip="Toggle the visibility of the Multi-Timeframe status table."),
    dashLoc=input.string(position.bottom_right, "Location", options=(position.top_right, position.bottom_right, position.top_left, position.bottom_left, position.middle_right), group=grp_dash, tooltip="The corner of the chart where the dashboard is displayed."),
    dashSize=input.string(size.small, "Size", options=(size.tiny, size.small, size.normal, size.large), group=grp_dash, tooltip="The scaling size of the dashboard table and its text."),
    tf1=input.timeframe("5", "Timeframe 1", group=grp_dash, tooltip="The first timeframe to track in the dashboard."),
    tf2=input.timeframe("15", "Timeframe 2", group=grp_dash, tooltip="The second timeframe to track in the dashboard."),
    tf3=input.timeframe("60", "Timeframe 3", group=grp_dash, tooltip="The third timeframe to track in the dashboard."),
    tf4=input.timeframe("240", "Timeframe 4", group=grp_dash, tooltip="The fourth timeframe to track in the dashboard.")
):
    sens: float = 0.6

    fibMid: float = 0.5
    fibGold1: float = 0.618
    fibGold2: float = 0.786

    def get_ma(source, length, type):
        __block_result__ = na
        __switch__ = type
        if __switch__ == "SMA":
            __block_result__ = ta.sma(source, length)
        elif __switch__ == "EMA":
            __block_result__ = ta.ema(source, length)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(source, length)
        elif __switch__ == "HMA":
            __block_result__ = ta.hma(source, length)
        elif __switch__ == "RMA":
            __block_result__ = ta.rma(source, length)
        else:
            __block_result__ = ta.sma(source, length)
        return __block_result__

    def get_status(tf):
        return request.security(syminfo.tickerid, tf, (close, high, low), lookahead=barmerge.lookahead_off)

    def calc_trend_and_pocket():
        b = get_ma(close, maLength, maType)
        a = ta.atr(atrLength)
        u = b + a * atrMult
        l = b - a * atrMult
        t: Persistent[int] = 0
        if ta.crossover(close, u):
            t = 1
        elif ta.crossunder(close, l):
            t = -1

        f618 = l + (u - l) * (1 - fibGold1) if t == 1 else u - (u - l) * (1 - fibGold1)
        f786 = l + (u - l) * (1 - fibGold2) if t == 1 else u - (u - l) * (1 - fibGold2)

        inPocket = close <= math.max(f618, f786) and close >= math.min(f618, f786)
        return (t, inPocket)

    trend: Series
    trend, inPocket = calc_trend_and_pocket()

    basis = get_ma(close, maLength, maType)
    atrValue = ta.atr(atrLength)
    upperBand = basis + atrValue * atrMult
    lowerBand = basis - atrValue * atrMult

    fib50: Series = lowerBand + (upperBand - lowerBand) * (1 - fibMid) if trend == 1 else upperBand - (upperBand - lowerBand) * (1 - fibMid)
    fib618: Series = lowerBand + (upperBand - lowerBand) * (1 - fibGold1) if trend == 1 else upperBand - (upperBand - lowerBand) * (1 - fibGold1)
    fib786: Series = lowerBand + (upperBand - lowerBand) * (1 - fibGold2) if trend == 1 else upperBand - (upperBand - lowerBand) * (1 - fibGold2)

    pocketMid = (fib618 + fib786) / 2
    dist = math.abs(close - pocketMid)
    maxDist = (upperBand - lowerBand) * 0.5
    rawTransp = 65 + dist / maxDist * 30 * sens
    dynamicTransp = math.max(0, math.min(90, rawTransp))
    dynamicColor = color.new(baseFill, dynamicTransp)

    def create_proj(lvl, slope, col, txt, baseline = False):
        endVal = lvl + slope * projLen
        ln = line.new(bar_index, lvl, bar_index + projLen, endVal, xloc.bar_index, extend.none, col, line.style_solid if baseline else line.style_dotted, 3 if baseline else 1)
        lb = label.new(bar_index + projLen, endVal, txt, xloc.bar_index, style=label.style_label_left, color=color.new(color.black, 100), textcolor=col, size=dashSize)
        return (ln, lb)

    def format_tf(tf):
        m: float = string.tonumber(tf)
        __block_result_1__ = na
        if not na(m):
            __block_result_1__ = string.tostring(math.round(m / 1440)) + 'D' if m >= 1440 else string.tostring(math.round(m / 60)) + 'H' if m >= 60 else tf + 'm'
        else:
            __block_result_1__ = tf
        return __block_result_1__

    trendChange = trend != trend[1]
    level100: Series[float] = lowerBand if trend == 1 else upperBand
    trendCol = colorUp if trend == 1 else colorDown

    plot(level100 if not trendChange else na, 'Trend MA', color=trendCol, linewidth=3, style=plot.style_linebr)
    p1 = plot(fib618 if trend != 0 and (not trendChange) else na, 'Fib 0.618', color=dynamicColor, style=plot.style_linebr)
    p2 = plot(fib786 if trend != 0 and (not trendChange) else na, 'Fib 0.786', color=dynamicColor, style=plot.style_linebr)
    plot(fib50 if trend != 0 else na, 'Fib 0.5', color=colorMid, style=plot.style_linebr)
    fill(p1, p2, color=dynamicColor, title='Dynamic Golden Pocket')

    if trendChange:
        level = lowerBand if trend == 1 else upperBand
        style = label.style_label_up if trend == 1 else label.style_label_down
        label.new(bar_index, level, text='⦿', color=NA(Color), textcolor=colorUp if trend == 1 else colorDown, style=label.style_label_center, size=dashSize)
        label.new(bar_index, level, text=string.tostring(close, format.mintick), color=NA(Color), textcolor=colorUp if trend == 1 else colorDown, style=style, size=dashSize)

    if showDash and barstate.islast:
        dash: Persistent[Table] = table.new(dashLoc, 3, 5, bgcolor=color.new(color.black, 40), border_width=1, border_color=color.new(color.gray, 70))

        table.cell(dash, 0, 0, 'TF', text_color=color.white, text_size=dashSize)
        table.cell(dash, 1, 0, 'Trend', text_color=color.white, text_size=dashSize)
        table.cell(dash, 2, 0, 'Pocket', text_color=color.white, text_size=dashSize)

        tfs: list[str] = array.from_items(tf1, tf2, tf3, tf4)
        for i in pine_range(0, 3):
            curr_tf: str = array.get(tfs, i)
            t, p = request.security(syminfo.tickerid, curr_tf, (trend, inPocket))

            row = i + 1
            table.cell(dash, 0, row, format_tf(curr_tf), text_color=color.white, text_size=dashSize)
            table.cell(dash, 1, row, 'BULL' if t == 1 else 'BEAR', bgcolor=color.new(colorUp, 30) if t == 1 else color.new(colorDown, 30), text_color=color.white, text_size=dashSize)
            table.cell(dash, 2, row, 'INSIDE' if p else 'OUT', bgcolor=color.new(baseFill, 30) if p else color.new(color.gray, 80), text_color=color.white, text_size=dashSize)

    l100: Persistent[Line] = na(Line)
    l50: Persistent[Line] = na(Line)
    l618: Persistent[Line] = na(Line)
    l786: Persistent[Line] = na(Line)
    lb100: Persistent[Label] = na(Label)
    lb50: Persistent[Label] = na(Label)
    lb618: Persistent[Label] = na(Label)
    lb786: Persistent[Label] = na(Label)
    fGold: Persistent[LineFill] = na(LineFill)

    if barstate.islast and trend != 0:
        line.delete(l100)
        line.delete(l50)
        line.delete(l618)
        line.delete(l786)
        label.delete(lb100)
        label.delete(lb50)
        label.delete(lb618)
        label.delete(lb786)
        linefill.delete(fGold)

        s100 = (level100 - level100[4]) / 4
        s50 = (fib50 - fib50[4]) / 4
        s618 = (fib618 - fib618[4]) / 4
        s786 = (fib786 - fib786[4]) / 4

        if showProj:
            ln100, lab100 = create_proj(level100, s100, trendCol, '1.0', True)
            ln50, lab50 = create_proj(fib50, s50, colorMid, '0.5')
            ln618, lab618 = create_proj(fib618, s618, baseFill, '0.618')
            ln786, lab786 = create_proj(fib786, s786, baseFill, '0.786')
            fGold = linefill.new(ln618, ln786, dynamicColor)
            l100 = ln100
            l50 = ln50
            l618 = ln618
            l786 = ln786
            lb100 = lab100
            lb50 = lab50
            lb618 = lab618
            lb786 = lab786


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
