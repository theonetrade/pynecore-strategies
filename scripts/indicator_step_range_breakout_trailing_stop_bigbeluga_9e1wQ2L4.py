"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, fill, high, hl2,
    input, label, line, location, low, math, na, plot, plotshape, position, script, shape, size,
    string, syminfo, ta, table
)
from pynecore.types import Box, Label, Line, Persistent, Table


@script.indicator("Step Range Breakout & Trailing Stop [BigBeluga]", overlay=True, precision=2, max_lines_count=500, max_boxes_count=500)
def main(
    len=input.int(20, "Structure Length", minval=1, tooltip="Lookback period to calculate the highest high and lowest low for structural boundaries."),
    len1=input.int(5, "Consolidation Bars / Length", minval=1, tooltip="Number of consecutive bars the range average must remain unchanged to confirm a valid consolidation zone."),
    dspMd=input.string("Price", "Range Display Format", options=("Price", "Ticks", "Both"), group="Display Settings", tooltip="Choose whether to show the range value in Price, Ticks/Pips, or Both."),
    aLen=input.int(14, "Trailing Stop ATR Length", minval=1, tooltip="Average True Range (ATR) length used for calculating the trailing stop distance."),
    aMul=input.float(3.0, "Trailing Stop Multiplier", minval=0.1, step=0.1, tooltip="Multiplier applied to the ATR to set how far the trailing stop trails behind the price."),
    wLen=input.int(100, "Win Rate Lookback Trades", minval=1, tooltip="Number of recent closed trades to calculate the win rate percentage."),
    cBul=input.color(color.rgb(10, 167, 151), "Bullish Color", group="Color Settings", tooltip="Color used for bullish breakouts, fills, and trailing stops."),
    cBar=input.color(color.red, "Bearish Color", group="Color Settings", tooltip="Color used for bearish breakouts, fills, and trailing stops."),
    cMid=input.color(color.rgb(190, 193, 204), "Mid Line Color", group="Color Settings", tooltip="Color used for the center line of the range.")
):
    hi = ta.highest(high, len)
    lo = ta.lowest(low, len)
    rAvg = (hi + lo) / 2

    stbl = ta.change(rAvg, len1) == 0

    def f_txt(pUp: float, pLo: float):
        pDif: float = pUp - pLo
        tDif: float = pDif / syminfo.mintick
        txt: str = ""
        if dspMd == 'Price':
            txt = 'Range: ' + string.tostring(pDif, '#.##')
        elif dspMd == 'Ticks':
            txt = 'Range: ' + string.tostring(tDif, '#.##') + ' Ticks'
        else:
            txt = 'Range: ' + string.tostring(pDif, '#.##') + ' (' + string.tostring(tDif, '#.##') + ' Ticks)'
        return txt

    mLVal: Persistent[float] = na(float)
    uLVal: Persistent[float] = na(float)
    lLVal: Persistent[float] = na(float)
    tStop: Persistent[float] = na(float)
    stat: Persistent[str] = "SEARCHING"
    isBul: Persistent[bool] = True

    mLin: Persistent[Line] = na(Line)
    rLab: Persistent[Label] = na(Label)
    zBar: Persistent[int] = na(int)

    aBox: Persistent[list[Box]] = array.new_box(0)
    nSli: int = 16

    cAtr = ta.atr(aLen)
    jstTr: bool = False

    lDir: Persistent[str] = "None"
    lPrc: Persistent[float] = na(float)
    eCls: Persistent[float] = na(float)
    trRes: Persistent[list[int]] = array.new_int(0)

    if stat == 'SEARCHING':
        if stbl:
            mLVal = rAvg
            uLVal = hi
            lLVal = lo
            zBar = bar_index - len1

            mLin = line.new(zBar, mLVal, bar_index, mLVal, width=1, color=cMid)

            midBar: int = math.round(zBar + (bar_index - zBar) / 2.0)
            rLab = label.new(midBar, uLVal, text=f_txt(uLVal, lLVal), color=color.new(cMid, 100), textcolor=chart.fg_color, style=label.style_label_down, size=size.small)

            aBox = array.new_box(0)
            sSiz = (uLVal - lLVal) / nSli

            for i in pine_range(0, nSli - 1):
                bBot = lLVal + i * sSiz
                bTop = lLVal + (i + 1) * sSiz

                dCtr = math.abs(i - (nSli - 1) / 2.0)
                mDst = (nSli - 1) / 2.0
                trns = math.round(110 - (90 - 50) * (dCtr / mDst))

                b = box.new(zBar, bTop, bar_index, bBot, border_color=na, bgcolor=color.new(cMid, cast_int(trns)))
                array.push(aBox, b)

            stat = "ZONE_ACTIVE"
    elif stat == 'ZONE_ACTIVE':
        line.set_x2(mLin, bar_index)

        midBar: int = math.round(zBar + (bar_index - zBar) / 2.0)
        label.set_x(rLab, midBar)
        label.set_y(rLab, uLVal)
        label.set_text(rLab, f_txt(uLVal, lLVal))

        if array.size(aBox) > 0:
            for b in aBox:
                box.set_right(b, bar_index)

        if close > uLVal and barstate.isconfirmed:
            isBul = True
            tStop = low - cAtr * aMul

            lDir = "BULLISH"
            lPrc = close
            eCls = close

            label.set_x(rLab, math.round(zBar + (bar_index - zBar) / 2.0))
            label.set_y(rLab, lLVal)
            label.set_style(rLab, label.style_label_up)
            label.set_textcolor(rLab, chart.fg_color)

            if array.size(aBox) > 0:
                for i in pine_range(0, array.size(aBox) - 1):
                    b = array.get(aBox, i)
                    dCtr = math.abs(i - (nSli - 1) / 2.0)
                    mDst = (nSli - 1) / 2.0
                    trns = math.round(110 - (90 - 50) * (dCtr / mDst))
                    box.set_bgcolor(b, color.new(cBul, cast_int(trns)))

            stat = "TRAILING"
            jstTr = True
        elif close < lLVal and barstate.isconfirmed:
            isBul = False
            tStop = high + cAtr * aMul

            lDir = "BEARISH"
            lPrc = close
            eCls = close

            label.set_x(rLab, math.round(zBar + (bar_index - zBar) / 2.0))
            label.set_y(rLab, uLVal)
            label.set_style(rLab, label.style_label_down)
            label.set_textcolor(rLab, chart.fg_color)

            if array.size(aBox) > 0:
                for i in pine_range(0, array.size(aBox) - 1):
                    b = array.get(aBox, i)
                    dCtr = math.abs(i - (nSli - 1) / 2.0)
                    mDst = (nSli - 1) / 2.0
                    trns = math.round(110 - (90 - 50) * (dCtr / mDst))
                    box.set_bgcolor(b, color.new(cBar, cast_int(trns)))

            stat = "TRAILING"
            jstTr = True
    elif stat == 'TRAILING':
        if isBul:
            tStop = math.max(tStop, low - cAtr * aMul)
            if close < tStop and barstate.isconfirmed:
                isWin: bool = close > eCls if isBul else close < eCls
                array.push(trRes, 1 if isWin else 0)
                if array.size(trRes) > wLen:
                    array.shift(trRes)
                stat = "SEARCHING"
        else:
            tStop = math.min(tStop, high + cAtr * aMul)
            if close > tStop and barstate.isconfirmed:
                isWin: bool = close > eCls if isBul else close < eCls
                array.push(trRes, 1 if isWin else 0)
                if array.size(trRes) > wLen:
                    array.shift(trRes)
                stat = "SEARCHING"

    tSPlt = tStop if stat == 'TRAILING' else na
    hPlt = hl2 if stat == 'TRAILING' else na

    p1 = plot(tSPlt, title='Trailing Stop', color=cBul if isBul else cBar, linewidth=1, style=plot.style_linebr)
    p2 = plot(tSPlt + (cAtr if isBul else -cAtr), title='Trailing Stop Reference', color=color.new(color.white, 100), style=plot.style_linebr)
    fill(p1, p2, color=color.new(cBul if isBul else cBar, 90), title='Trailing Stop Fill')

    plotshape(tSPlt if jstTr else na, title='Trailing Start Circle', style=shape.circle, location=location.absolute, color=color.new(cBul if isBul else cBar, 50), size=size.small)
    plotshape(tSPlt if jstTr else na, title='Trailing Start Circle', style=shape.circle, location=location.absolute, color=color.new(cBul if isBul else cBar, 0), size=size.tiny)

    dash: Persistent[Table] = table.new(position=position.top_right, columns=2, rows=3, bgcolor=color.new(color.black, 50), border_color=chart.bg_color, border_width=2)
    if barstate.islast:
        tTrd: int = array.size(trRes)
        wins: int = array.sum(trRes) if tTrd > 0 else 0
        wRat: float = cast_float(wins) / cast_float(tTrd) * 100.0 if tTrd > 0 else 0.0

        table.cell(dash, 0, 0, 'Last Breakout', text_color=chart.fg_color, text_size=size.normal)
        table.cell(dash, 1, 0, lDir + '/' + string.tostring(lPrc, '#.##'), text_color=cBul if lDir == 'BULLISH' else cBar, text_size=size.normal)

        table.cell(dash, 0, 1, 'Closed Trades', text_color=chart.fg_color, text_size=size.normal)
        table.cell(dash, 1, 1, string.tostring(tTrd), text_color=chart.fg_color, text_size=size.normal)

        table.cell(dash, 0, 2, 'Win Rate', text_color=chart.fg_color, text_size=size.normal)
        table.cell(dash, 1, 2, string.tostring(wins) + '/' + string.tostring(tTrd) + ' (' + string.tostring(wRat, '#.##') + '%)', text_color=cBul if wRat >= 50 else cBar, text_size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)