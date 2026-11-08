"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, chart, close, color, extend, format,
    high, hl2, input, label, line, linefill, location, low, math, na, open, plotcandle, plotchar,
    plotshape, request, script, shape, size, string, syminfo, ta, volume, xloc, yloc
)
from pynecore.types import Label, Line, LineFill, Persistent


@script.indicator("Zero Lag Liquidity [AlgoAlpha]", "AlgoAlpha – Zero Lag Liq", overlay=True, max_lines_count=500, max_labels_count=500, behind_chart=False)
def main(
    ltf=input.timeframe("3", title="Lower Timeframe", tooltip="The lower timeframe used to build the wick profile. This determines the resolution of the volume and price data used for liquidity calculations.", group="Wick Profile"),
    binCount=input.int(7, title="Profile Bin Count", minval=1, tooltip="Number of bins to divide the price range into for the wick profile. Higher values provide more granularity.", group="Wick Profile"),
    wickMult=input.float(2.0, title="Wick Multiplier", minval=0.1, step=0.1, tooltip="Multiplier for the average wick size to determine significant wick events. Higher values require larger wicks to trigger highlights.", group="Wick Profile"),
    trnd=input.bool(True, title="Show Liquidity Trend", tooltip="Enable to display the trend based on whether liquidity levels are being broken.", group="Appearance"),
    brk=input.bool(True, title="Show Liquidity Breaks", tooltip="Enable to highlight when the price breaks through a liquidity level.", group="Appearance"),
    rej=input.bool(True, title="Show Liquidity Rejections", tooltip="Enable to highlight when the price rejects off a liquidity level.", group="Appearance"),
    lblPercent=input.bool(True, title="Labels Show % Strength", tooltip="If true, labels display the level's volume as a percentage of the cumulative volume of all active levels. If false, labels display the absolute volume recorded at creation.", group="Appearance"),
    lblSizeOpt=input.string("Small", title="Label Text Size", options=("Tiny", "Small", "Medium", "Large"), group="Appearance"),
    bullCol=input.color(color.new('#00FFBB'), title="Bullish Colour", tooltip="Color used for bullish (buy-side) liquidity levels.", group="Appearance"),
    bearCol=input.color(color.new('#FF1100'), title="Bearish Colour", tooltip="Color used for bearish (sell-side) liquidity levels.", group="Appearance")
):
    lblSizeConst = size.tiny if lblSizeOpt == 'Tiny' else size.small if lblSizeOpt == 'Small' else size.normal if lblSizeOpt == 'Medium' else size.large

    filter = ta.ema(ta.hma(close, 7), 21)
    vol = ta.rsi(volume, 14)
    lower_wick = math.min(close, open) - low
    upper_wick = high - math.max(close, open)
    avg_wick = (lower_wick + upper_wick) / 2
    a_w = ta.sma(avg_wick, 21)
    highlightRaw = vol > 60 and avg_wick > a_w * wickMult
    highlight = highlightRaw and upper_wick != lower_wick

    ltVolsSeries = request.security_lower_tf(syminfo.tickerid, ltf, volume)
    ltPricesSeries = request.security_lower_tf(syminfo.tickerid, ltf, close)

    def f_wick_poc(top: float, bot: float, pricesArr: list[float], volsArr: list[float], bins: int):
        __block_result__ = na
        if array.size(pricesArr) == 0 or array.size(volsArr) == 0 or top == bot:
            __block_result__ = na
        else:
            range_ = top - bot
            seg = range_ / bins
            bounds: list[float] = array.new_float()
            volsBin: list[float] = array.new_float()
            for i in pine_range(0, bins):
                array.push(bounds, bot + i * seg)
            sizeP = array.size(pricesArr)
            for i in pine_range(0, bins - 1):
                totalVol: float = 0.0
                for j in pine_range(0, sizeP - 1):
                    pr = array.get(pricesArr, j)
                    if pr >= array.get(bounds, i) and pr <= array.get(bounds, i + 1):
                        totalVol += array.get(volsArr, j)
                array.push(volsBin, totalVol)
            maxVol = array.max(volsBin)
            pocIdx = array.indexof(volsBin, maxVol)
            __block_result__ = (array.get(bounds, pocIdx) + array.get(bounds, pocIdx + 1)) / 2
        return __block_result__

    pocLines: Persistent[list[Line]] = array.new_line()
    pocPrices: Persistent[list[float]] = array.new_float()
    pocTypes: Persistent[list[int]] = array.new_int()
    pocLabels: Persistent[list[Label]] = array.new_label()
    pocVols: Persistent[list[float]] = array.new_float()
    pocBodyLines: Persistent[list[Line]] = array.new_line()
    pocFills: Persistent[list[LineFill]] = array.new_linefill()

    isRedBar = highlight and lower_wick > upper_wick
    isGreenBar = highlight and upper_wick > lower_wick
    wickTop: float = na(float)
    wickBot: float = na(float)
    if isRedBar:
        wickTop = math.min(close, open)
        wickBot = low
    elif isGreenBar:
        wickTop = high
        wickBot = math.max(close, open)

    if highlight and (not na(ltPricesSeries)) and (not na(ltVolsSeries)):
        poc = f_wick_poc(wickTop, wickBot, ltPricesSeries, ltVolsSeries, binCount)
        if not na(poc):
            newLine = line.new(bar_index, poc, bar_index, poc, xloc.bar_index, extend.none, color=bullCol if isGreenBar else bearCol, width=1)
            array.unshift(pocLines, newLine)
            array.unshift(pocPrices, poc)
            array.unshift(pocTypes, 1 if isGreenBar else -1)
            array.unshift(pocVols, volume)
            newLabel = label.new(bar_index, poc, text='', xloc=xloc.bar_index, yloc=yloc.price, color=chart.fg_color, textcolor=chart.fg_color, style=label.style_none, size=lblSizeConst)
            array.unshift(pocLabels, newLabel)
            bodyPrice: float = wickBot if isGreenBar else wickTop
            bodyLine = line.new(bar_index, bodyPrice, bar_index, bodyPrice, xloc.bar_index, extend.none, color=color.new(bullCol if isGreenBar else bearCol, 80), width=1)
            array.unshift(pocBodyLines, bodyLine)
            fillColor = color.new(bullCol if isGreenBar else bearCol, 80)
            fillObj = linefill.new(newLine, bodyLine, fillColor)
            array.unshift(pocFills, fillObj)

    maxStored: int = 500
    if array.size(pocLines) > maxStored:
        array.pop(pocLines)
        array.pop(pocPrices)
        array.pop(pocTypes)
        array.pop(pocLabels)
        array.pop(pocVols)
        array.pop(pocBodyLines)
        array.pop(pocFills)

    bullrej: bool = False
    bearrej: bool = False
    trend: Persistent[int] = 0
    brkk: int = 0

    sumVols: float = 0.0
    if array.size(pocVols) > 0:
        for sv in pine_range(0, array.size(pocVols) - 1):
            sumVols += array.get(pocVols, sv)
    if array.size(pocLines) > 0:
        for i in pine_range(array.size(pocLines) - 1, 0):
            if i < array.size(pocLines):
                l = array.get(pocLines, i)
                lvlPrice = array.get(pocPrices, i)
                typ = array.get(pocTypes, i)
                lab = array.get(pocLabels, i)
                if not na(lab):
                    method_call('set_xy', lab, bar_index, lvlPrice)
                    vol_i = array.get(pocVols, i)
                    txt = string.tostring(vol_i / sumVols * 100, format.percent) if lblPercent else string.tostring(vol_i, format.volume)
                    method_call('set_text', lab, txt)
                    if sumVols > 0:
                        dominance = vol_i / sumVols
                        maxTrans: int = 60
                        trans: int = math.round((1 - dominance) * maxTrans)
                        trans = 0 if trans < 0 else maxTrans if trans > maxTrans else trans
                        method_call('set_color', l, color.new(bullCol, trans) if typ == 1 else color.new(bearCol, trans))
                done: bool = close > lvlPrice and close[1] > lvlPrice if typ == 1 else close < lvlPrice and close[1] < lvlPrice

                if done:
                    brkk = typ
                    trend = typ
                    array.remove(pocLines, i)
                    array.remove(pocPrices, i)
                    array.remove(pocTypes, i)
                    array.remove(pocLabels, i)
                    array.remove(pocVols, i)
                    array.remove(pocBodyLines, i)
                    array.remove(pocFills, i)
                else:
                    if high[1] > method_call('get_y1', l) and low[1] < method_call('get_y1', l) and (method_call('get_x2', l) - method_call('get_x1', l) > 0):
                        if hl2 > method_call('get_y2', l) and typ == -1:
                            bullrej = True
                        elif hl2 < method_call('get_y2', l) and typ == 1:
                            bearrej = True
                    method_call('set_x2', l, bar_index)
                    bodyL = array.get(pocBodyLines, i)
                    method_call('set_x2', bodyL, bar_index)

    plotchar(bullrej and rej, 'Bullish Rejection', '▲', location.belowbar, color.new(bullCol, 50), size=size.tiny)
    plotchar(bearrej and rej, 'Bearish Rejection', '▼', location.abovebar, color.new(bearCol, 50), size=size.tiny)

    x: int = 7
    lw = ta.lowest(x)
    hg = ta.highest(x)

    plotshape(lw if brkk > 0 and brk else na, 'Bullish Break', shape.labelup, location.absolute, color.new(bullCol, 30), text='▲', textcolor=chart.fg_color, size=size.tiny)
    plotshape(hg if brkk < 0 and brk else na, 'Bearish Break', shape.labeldown, location.absolute, color.new(bearCol, 30), text='▼', textcolor=chart.fg_color, size=size.tiny)

    candlecol = (bearCol if isRedBar else bullCol) if highlight else (color.from_gradient(0.65, 0, 1, bullCol, chart.bg_color) if trend > 0 else color.from_gradient(0.65, 0, 1, bearCol, chart.bg_color) if trend < 0 else na) if trnd else na
    plotcandle(open, high, low, close, 'Custom Candle', candlecol, candlecol, bordercolor=candlecol)

    alertcondition(bullrej and rej, title='Bullish Rejection')
    alertcondition(bearrej and rej, title='Bearish Rejection')
    alertcondition(brkk > 0 and brk, title='Bullish Break')
    alertcondition(brkk < 0 and brk, title='Bearish Break')
    alertcondition(trend > 0 and trnd, title='Bullish Trend')
    alertcondition(trend < 0 and trnd, title='Bearish Trend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
