"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, barstate, close, color, display, fill, high, input,
    label, line, linefill, low, math, na, open, plot, plotcandle, script, string, ta
)
from pynecore.types import Color, Label, Line, LineFill, Persistent, Series

GRP_GENERAL: str = "General Settings"
GRP_ST: str = "Supertrend Parameters"
GRP_BANDS: str = "Fibonacci Bands Parameters"
GRP_COLORS: str = "Main Styling & Colors"
GRP_LEVELS: str = "Fibonacci Level Settings"


@script.indicator("Supertrend + Fibonacci OTE Grid & Bands [BigBeluga]", overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    fibMode=input.string("OTE Grid", "Fibonacci Mode", options=("OTE Grid", "Fibonacci Bands"), group=GRP_GENERAL, tooltip="Select between drawing an anchored OTE Grid per trend or continuous Fibonacci Bands based on ATR."),
    showLabels=input.bool(True, "Show Fibonacci Labels", group=GRP_GENERAL, tooltip="Toggle right-edge text labels displaying ratio values and current price levels."),
    gridLineStyle=input.string("Dotted", "Grid Line Style", options=("Solid", "Dotted", "Dashed"), group=GRP_GENERAL, tooltip="Select the visual line style for drawing the OTE Grid levels."),
    proxThreshold=input.float(1.0, "Grid Highlight Distance (ATR Multiplier)", minval=0.01, step=0.05, group=GRP_GENERAL, tooltip="Sensitivity multiplier using ATR to highlight a grid level when price closes near it."),
    nonOteDim=input.bool(False, "Dim Non-OTE Levels when Far", group=GRP_GENERAL, tooltip="When enabled, non-OTE levels use a translucent version of their input color until price approaches."),
    stAtrPeriod=input.int(100, "Supertrend ATR Period", minval=1, group=GRP_ST, tooltip="Lookback period for Average True Range calculation driving the Supertrend stop line."),
    stFactor=input.float(4.5, "Supertrend Multiplier", minval=0.1, step=0.1, group=GRP_ST, tooltip="Multiplier applied to ATR to adjust distance of the Supertrend stop loss line."),
    atrLength=input.int(100, "Bands ATR Period", minval=1, group=GRP_BANDS, tooltip="ATR length used specifically to calculate dynamic channel width in Fibonacci Bands mode."),
    outerRatio=input.float(2.0, "Max Band ATR Multiplier", step=0.1, group=GRP_BANDS, tooltip="Multiplier controlling the max distance (1.000 ratio band) relative to ATR in Bands mode."),
    colUp=input.color(color.new('#26C477'), "Bullish Trend", group=GRP_COLORS, tooltip="Color used for bullish trend elements, lines, and text."),
    colDn=input.color(color.new('#2692C4'), "Bearish Trend", group=GRP_COLORS, tooltip="Color used for bearish trend elements, lines, and text."),
    colorCloseLVL=input.color(color.new('#FFD600'), "Active Fibonacci Level", group=GRP_COLORS, tooltip="Color highlight level when price is close to it"),
    useBarColor=input.bool(True, "Color Bars by Trend", group=GRP_COLORS, tooltip="Color the standard chart bars/candles according to the Supertrend direction."),
    usePlotCandle=input.bool(True, "Plot Trend Candles", group=GRP_COLORS, tooltip="Plot custom candles colored according to the Supertrend direction."),
    col0=input.color(color.new('#787B86'), "0.000 Level", group=GRP_LEVELS, inline="f0", tooltip="Toggle visibility and set color for 0.000 level."),
    show236=input.bool(True, "", group=GRP_LEVELS, inline="f0_2"),
    col236=input.color(color.new('#787B86'), "0.236 Level", group=GRP_LEVELS, inline="f0_2", tooltip="Toggle visibility and set color for 0.236 level."),
    show382=input.bool(True, "", group=GRP_LEVELS, inline="f1"),
    col382=input.color(color.new('#787B86'), "0.382 Level", group=GRP_LEVELS, inline="f1", tooltip="Toggle visibility and set color for 0.382 level."),
    show50=input.bool(True, "", group=GRP_LEVELS, inline="f1_2"),
    col50=input.color(color.new('#787B86'), "0.500 Level", group=GRP_LEVELS, inline="f1_2", tooltip="Toggle visibility and set color for 0.500 level."),
    show618=input.bool(True, "OTE 0.618", group=GRP_LEVELS, inline="f2"),
    show705=input.bool(True, "OTE 0.705", group=GRP_LEVELS, inline="f2_2"),
    show786=input.bool(True, "OTE 0.786", group=GRP_LEVELS, inline="f3"),
    col100=input.color(color.new('#787B86'), "1.000 Level", group=GRP_LEVELS, inline="f3_2", tooltip="Toggle visibility and set color for 1.000 level.")
):
    show0: bool = True

    show100: bool = True

    dir: Series
    supertrend, dir = ta.supertrend(stFactor, stAtrPeriod)

    trendHigh: Persistent[float] = high
    trendLow: Persistent[float] = low

    HH = ta.highest(5)
    LL = ta.lowest(5)

    if dir != dir[1]:
        trendHigh = high if dir < 0 else HH
        trendLow = LL if dir < 0 else low
    else:
        trendHigh = math.max(trendHigh, high)
        trendLow = math.min(trendLow, low)

    bandAtr: float = ta.atr(atrLength)
    isBands: bool = fibMode == 'Fibonacci Bands'

    bandMultiplier: float = 1.0 if dir < 0 else -1.0
    totalDist: float = bandMultiplier * bandAtr * outerRatio

    fibB100: float = supertrend if isBands and show100 else na
    fibB786: float = supertrend + totalDist * (1.0 - 0.786) if isBands and show786 else na
    fibB705: float = supertrend + totalDist * (1.0 - 0.705) if isBands and show705 else na
    fibB618: float = supertrend + totalDist * (1.0 - 0.618) if isBands and show618 else na
    fibB50: float = supertrend + totalDist * (1.0 - 0.5) if isBands and show50 else na
    fibB382: float = supertrend + totalDist * (1.0 - 0.382) if isBands and show382 else na
    fibB236: float = supertrend + totalDist * (1.0 - 0.236) if isBands and show236 else na
    fibB0: float = supertrend + totalDist if isBands and show0 else na

    trendBaseCol: Color = colUp if dir < 0 else colDn
    colOte: Color = color.new(trendBaseCol, 20)
    colOteFill: Color = color.new(trendBaseCol, 85)

    def getLineStyle(style):
        __block_result__ = na
        __switch__ = style
        if __switch__ == "Solid":
            __block_result__ = line.style_solid
        elif __switch__ == "Dotted":
            __block_result__ = line.style_dotted
        elif __switch__ == "Dashed":
            __block_result__ = line.style_dashed
        else:
            __block_result__ = line.style_dotted
        return __block_result__

    def getGridProperties(priceLevel: float, inputCol: Color, isOte: bool, threshold: float):
        isNear: bool = math.abs(close - priceLevel) <= threshold
        baseColor: Color = colOte if isOte else color.new(inputCol, 60) if nonOteDim else inputCol
        finalColor: Color = colorCloseLVL if isNear else baseColor
        finalWidth: int = 3 if isNear else 1
        return (finalColor, finalWidth)

    supTrendCol = colUp if dir < 0 else colDn

    trendBodyCol: Color = colUp if dir < 0 else colDn
    trendBorderCol: Color = colUp if dir < 0 else colDn
    trendWickCol: Color = colUp if dir < 0 else colDn

    barcolor(trendBodyCol if useBarColor else na, title='Trend Bar Color')

    plotcandle(open if usePlotCandle else na, high if usePlotCandle else na, low if usePlotCandle else na, close if usePlotCandle else na, title='Trend Candle Plot', color=trendBodyCol, wickcolor=trendWickCol, bordercolor=trendBorderCol)

    pSupertrend = plot(na if dir != dir[1] else supertrend, 'Supertrend Stop Loss', color=supTrendCol, linewidth=2, style=plot.style_linebr)
    pClose = plot(close, 'Close Price Stream', display=display.none)

    stFillCol: Color = color.new(colUp, 100 if isBands else 80) if dir < 0 else color.new(colDn, 100 if isBands else 80)
    closeFillCol: Color = color.new(colUp, 100) if dir < 0 else color.new(colDn, 100)

    fill(pSupertrend, pClose, supertrend, close, stFillCol, closeFillCol, title='Supertrend Gradient Fill')

    plotStl = plot.linestyle_dotted if gridLineStyle == 'Dotted' else plot.linestyle_dashed if gridLineStyle == 'Dashed' else plot.linestyle_solid

    p0 = plot(fibB0, 'Fib Band 0.000 (Outer)', color=col0, style=plot.style_linebr, linestyle=plotStl)
    p236 = plot(fibB236, 'Fib Band 0.236', color=col236, style=plot.style_linebr, linestyle=plotStl)
    p382 = plot(fibB382, 'Fib Band 0.382', color=col382, style=plot.style_linebr, linestyle=plotStl)
    p50 = plot(fibB50, 'Fib Band 0.500', color=col50, style=plot.style_linebr, linestyle=plotStl)
    p618 = plot(fibB618, 'Fib Band 0.618 (OTE)', color=colOte, style=plot.style_linebr, linestyle=plotStl)
    p705 = plot(fibB705, 'Fib Band 0.705 (OTE)', color=colOte, style=plot.style_linebr, linestyle=plotStl)
    p786 = plot(fibB786, 'Fib Band 0.786 (OTE)', color=colOte, style=plot.style_linebr, linestyle=plotStl)

    fill(p618, p786, color=colOteFill if isBands and show618 and show786 else na, title='Bands OTE Fill')

    lbB0: Persistent[Label] = na(Label)
    lbB236: Persistent[Label] = na(Label)
    lbB382: Persistent[Label] = na(Label)
    lbB50: Persistent[Label] = na(Label)
    lbB618: Persistent[Label] = na(Label)
    lbB705: Persistent[Label] = na(Label)
    lbB786: Persistent[Label] = na(Label)
    lbB100: Persistent[Label] = na(Label)

    if isBands and showLabels and barstate.islast:
        label.delete(lbB0)
        label.delete(lbB236)
        label.delete(lbB382)
        label.delete(lbB50)
        label.delete(lbB618)
        label.delete(lbB705)
        label.delete(lbB786)
        label.delete(lbB100)

        if show0:
            lbB0 = label.new(bar_index, fibB0, '0.000 (' + string.tostring(fibB0, '#.##') + ')', color=color.new(color.black, 100), textcolor=col0, style=label.style_label_left)
        if show236:
            lbB236 = label.new(bar_index, fibB236, '0.236 (' + string.tostring(fibB236, '#.##') + ')', color=color.new(color.black, 100), textcolor=col236, style=label.style_label_left)
        if show382:
            lbB382 = label.new(bar_index, fibB382, '0.382 (' + string.tostring(fibB382, '#.##') + ')', color=color.new(color.black, 100), textcolor=col382, style=label.style_label_left)
        if show50:
            lbB50 = label.new(bar_index, fibB50, '0.500 (' + string.tostring(fibB50, '#.##') + ')', color=color.new(color.black, 100), textcolor=col50, style=label.style_label_left)
        if show618:
            lbB618 = label.new(bar_index, fibB618, '0.618 OTE (' + string.tostring(fibB618, '#.##') + ')', color=color.new(color.black, 100), textcolor=colOte, style=label.style_label_left)
        if show705:
            lbB705 = label.new(bar_index, fibB705, '0.705 OTE (' + string.tostring(fibB705, '#.##') + ')', color=color.new(color.black, 100), textcolor=colOte, style=label.style_label_left)
        if show786:
            lbB786 = label.new(bar_index, fibB786, '0.786 OTE (' + string.tostring(fibB786, '#.##') + ')', color=color.new(color.black, 100), textcolor=colOte, style=label.style_label_left)
        if show100:
            lbB100 = label.new(bar_index, fibB100, '1.000 ST (' + string.tostring(fibB100, '#.##') + ')', color=color.new(color.black, 100), textcolor=col100, style=label.style_label_left)

    l0: Persistent[Line] = na(Line)
    l236: Persistent[Line] = na(Line)
    l382: Persistent[Line] = na(Line)
    l50: Persistent[Line] = na(Line)
    l618: Persistent[Line] = na(Line)
    l705: Persistent[Line] = na(Line)
    l786: Persistent[Line] = na(Line)
    l100: Persistent[Line] = na(Line)
    oteFill: Persistent[LineFill] = na(LineFill)

    lbl0: Persistent[Label] = na(Label)
    lbl236: Persistent[Label] = na(Label)
    lbl382: Persistent[Label] = na(Label)
    lbl50: Persistent[Label] = na(Label)
    lbl618: Persistent[Label] = na(Label)
    lbl705: Persistent[Label] = na(Label)
    lbl786: Persistent[Label] = na(Label)
    lbl100: Persistent[Label] = na(Label)

    if dir != dir[1] or fibMode != 'OTE Grid':
        line.delete(l0)
        line.delete(l236)
        line.delete(l382)
        line.delete(l50)
        line.delete(l618)
        line.delete(l705)
        line.delete(l786)
        line.delete(l100)
        label.delete(lbl0)
        label.delete(lbl236)
        label.delete(lbl382)
        label.delete(lbl50)
        label.delete(lbl618)
        label.delete(lbl705)
        label.delete(lbl786)
        label.delete(lbl100)

    if fibMode == 'OTE Grid':
        f0: float = na(float)
        f236: float = na(float)
        f382: float = na(float)
        f50: float = na(float)
        f618: float = na(float)
        f705: float = na(float)
        f786: float = na(float)
        f100: float = na(float)

        if dir < 0:
            f0 = trendHigh
            f100 = trendLow
            diff: float = f0 - f100
            f236 = f0 - diff * 0.236
            f382 = f0 - diff * 0.382
            f50 = f0 - diff * 0.5
            f618 = f0 - diff * 0.618
            f705 = f0 - diff * 0.705
            f786 = f0 - diff * 0.786
        else:
            f0 = trendLow
            f100 = trendHigh
            diff: float = f100 - f0
            f236 = f0 + diff * 0.236
            f382 = f0 + diff * 0.382
            f50 = f0 + diff * 0.5
            f618 = f0 + diff * 0.618
            f705 = f0 + diff * 0.705
            f786 = f0 + diff * 0.786

        styleEnum = getLineStyle(gridLineStyle)
        proximityRange: float = bandAtr * proxThreshold

        c0, w0 = getGridProperties(f0, col0, False, proximityRange)
        c236, w236 = getGridProperties(f236, col236, False, proximityRange)
        c382, w382 = getGridProperties(f382, col382, False, proximityRange)
        c50, w50 = getGridProperties(f50, col50, False, proximityRange)
        c618, w618 = getGridProperties(f618, colOte, True, proximityRange)
        c705, w705 = getGridProperties(f705, colOte, True, proximityRange)
        c786, w786 = getGridProperties(f786, colOte, True, proximityRange)
        c100, w100 = getGridProperties(f100, col100, False, proximityRange)

        if dir != dir[1] or na(l0):
            l0 = line.new(bar_index, f0, bar_index + 1, f0, color=c0, width=w0, style=styleEnum) if show0 else na
            l236 = line.new(bar_index, f236, bar_index + 1, f236, color=c236, width=w236, style=styleEnum) if show236 else na
            l382 = line.new(bar_index, f382, bar_index + 1, f382, color=c382, width=w382, style=styleEnum) if show382 else na
            l50 = line.new(bar_index, f50, bar_index + 1, f50, color=c50, width=w50, style=styleEnum) if show50 else na
            l618 = line.new(bar_index, f618, bar_index + 1, f618, color=c618, width=w618, style=styleEnum) if show618 else na
            l705 = line.new(bar_index, f705, bar_index + 1, f705, color=c705, width=w705, style=styleEnum) if show705 else na
            l786 = line.new(bar_index, f786, bar_index + 1, f786, color=c786, width=w786, style=styleEnum) if show786 else na
            l100 = line.new(bar_index, f100, bar_index + 1, f100, color=c100, width=w100, style=styleEnum) if show100 else na

            if show618 and show786:
                oteFill = linefill.new(l618, l786, colOteFill)

            if showLabels:
                lbl0 = label.new(bar_index + 1, f0, '0.000 (' + string.tostring(f0, '#.##') + ')', color=color.new(color.black, 100), textcolor=c0, style=label.style_label_left) if show0 else na
                lbl236 = label.new(bar_index + 1, f236, '0.236 (' + string.tostring(f236, '#.##') + ')', color=color.new(color.black, 100), textcolor=c236, style=label.style_label_left) if show236 else na
                lbl382 = label.new(bar_index + 1, f382, '0.382 (' + string.tostring(f382, '#.##') + ')', color=color.new(color.black, 100), textcolor=c382, style=label.style_label_left) if show382 else na
                lbl50 = label.new(bar_index + 1, f50, '0.500 (' + string.tostring(f50, '#.##') + ')', color=color.new(color.black, 100), textcolor=c50, style=label.style_label_left) if show50 else na
                lbl618 = label.new(bar_index + 1, f618, '0.618 OTE (' + string.tostring(f618, '#.##') + ')', color=color.new(color.black, 100), textcolor=c618, style=label.style_label_left) if show618 else na
                lbl705 = label.new(bar_index + 1, f705, '0.705 OTE (' + string.tostring(f705, '#.##') + ')', color=color.new(color.black, 100), textcolor=c705, style=label.style_label_left) if show705 else na
                lbl786 = label.new(bar_index + 1, f786, '0.786 OTE (' + string.tostring(f786, '#.##') + ')', color=color.new(color.black, 100), textcolor=c786, style=label.style_label_left) if show786 else na
                lbl100 = label.new(bar_index + 1, f100, '1.000 (' + string.tostring(f100, '#.##') + ')', color=color.new(color.black, 100), textcolor=c100, style=label.style_label_left) if show100 else na
        else:
            if show0:
                line.set_xy1(l0, line.get_x1(l0), f0)
                line.set_xy2(l0, bar_index + 1, f0)
                line.set_color(l0, c0)
                line.set_width(l0, w0)
            if show236:
                line.set_xy1(l236, line.get_x1(l236), f236)
                line.set_xy2(l236, bar_index + 1, f236)
                line.set_color(l236, c236)
                line.set_width(l236, w236)
            if show382:
                line.set_xy1(l382, line.get_x1(l382), f382)
                line.set_xy2(l382, bar_index + 1, f382)
                line.set_color(l382, c382)
                line.set_width(l382, w382)
            if show50:
                line.set_xy1(l50, line.get_x1(l50), f50)
                line.set_xy2(l50, bar_index + 1, f50)
                line.set_color(l50, c50)
                line.set_width(l50, w50)
            if show618:
                line.set_xy1(l618, line.get_x1(l618), f618)
                line.set_xy2(l618, bar_index + 1, f618)
                line.set_color(l618, c618)
                line.set_width(l618, w618)
            if show705:
                line.set_xy1(l705, line.get_x1(l705), f705)
                line.set_xy2(l705, bar_index + 1, f705)
                line.set_color(l705, c705)
                line.set_width(l705, w705)
            if show786:
                line.set_xy1(l786, line.get_x1(l786), f786)
                line.set_xy2(l786, bar_index + 1, f786)
                line.set_color(l786, c786)
                line.set_width(l786, w786)
            if show100:
                line.set_xy1(l100, line.get_x1(l100), f100)
                line.set_xy2(l100, bar_index + 1, f100)
                line.set_color(l100, c100)
                line.set_width(l100, w100)

            if show618 and show786 and (not na(oteFill)):
                linefill.set_color(oteFill, colOteFill)

            if showLabels:
                if show0:
                    label.set_xy(lbl0, bar_index + 1, f0)
                    label.set_text(lbl0, '0.000 (' + string.tostring(f0, '#.##') + ')')
                    label.set_textcolor(lbl0, c0)
                if show236:
                    label.set_xy(lbl236, bar_index + 1, f236)
                    label.set_text(lbl236, '0.236 (' + string.tostring(f236, '#.##') + ')')
                    label.set_textcolor(lbl236, c236)
                if show382:
                    label.set_xy(lbl382, bar_index + 1, f382)
                    label.set_text(lbl382, '0.382 (' + string.tostring(f382, '#.##') + ')')
                    label.set_textcolor(lbl382, c382)
                if show50:
                    label.set_xy(lbl50, bar_index + 1, f50)
                    label.set_text(lbl50, '0.500 (' + string.tostring(f50, '#.##') + ')')
                    label.set_textcolor(lbl50, c50)
                if show618:
                    label.set_xy(lbl618, bar_index + 1, f618)
                    label.set_text(lbl618, '0.618 OTE (' + string.tostring(f618, '#.##') + ')')
                    label.set_textcolor(lbl618, c618)
                if show705:
                    label.set_xy(lbl705, bar_index + 1, f705)
                    label.set_text(lbl705, '0.705 OTE (' + string.tostring(f705, '#.##') + ')')
                    label.set_textcolor(lbl705, c705)
                if show786:
                    label.set_xy(lbl786, bar_index + 1, f786)
                    label.set_text(lbl786, '0.786 OTE (' + string.tostring(f786, '#.##') + ')')
                    label.set_textcolor(lbl786, c786)
                if show100:
                    label.set_xy(lbl100, bar_index + 1, f100)
                    label.set_text(lbl100, '1.000 (' + string.tostring(f100, '#.##') + ')')
                    label.set_textcolor(lbl100, c100)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
