"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barmerge, close, color, extend,
    fill, high, hlc3, input, label, line, location, low, math, na, nz, plot, plotshape, request,
    script, shape, size, string, syminfo, ta, text, time, volume, xloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, PersistentSeries, Series


@script.indicator('☁️ TV Community Algo ☁️', overlay=True, na_bool=True)
def main(
    voidLines=input(True, 'Void Lines On / Off'),
    dashOn=input(True, 'Dashboard On / Off'),
    colorBar=input(True, 'Signal Bars On / Off'),
    srLines=input(False, 'Support & Resistance Lines On / Off'),
    emaLines=input(False, 'EMA (8, 200) On / Off'),
    bsSignals=input(True, 'Buy & Sell Signals On / Off'),
    afibOn=input(False, 'Fibonacci Retracement On / Off'),
    dashDist=input(13, 'Dashboard Distance'),
    dashColor=input.color(color.new(color.new('#696969'), 80), 'Dashboard Color', inline='Dash Line'),
    dashTextColor=input.color(color.new(color.new('#FFFFFF'), 0), 'Text Color', inline='Dash Line'),
    threshold_multiplier=input(3, 'Fibonacci Deviation'),
    reverse=input(False, 'Reverse Fib?'),
    extendLeft__input=input.bool(False, 'Extend Left    |    Extend Right', inline='Extend Lines'),
    extendRight__input=input.bool(True, '', inline='Extend Lines'),
    prices=input(True, 'Show Prices?'),
    levels=input.bool(True, 'Show Levels?', inline='Levels'),
    levelsFormat=input.string('Percent', '', options=('Values', 'Percent'), inline='Levels'),
    labelsPosition=input.string('Right', 'Fib Label Position', options=('Left', 'Right'))
):
    atr = ta.atr(14)
    stdAtr = 2 * ta.stdev(atr, 20)
    smaAtr = ta.sma(atr, 20)
    topAtrDev = smaAtr + stdAtr
    bottomAtrDev = smaAtr - stdAtr
    calcDev = (atr - bottomAtrDev) / (topAtrDev - bottomAtrDev)
    percentVol = 40 * calcDev + 30
    volumeDash = volume
    rsiDash = ta.rsi(close, 14)
    ema9: Series = ta.ema(close, 9)
    totalSentTxt = 'Bullish' if ema9 > ema9[2] else 'Bearish' if ema9 < ema9[2] else 'Flat'
    sma = ta.sma(close, 50)
    oneM: Series = request.security(syminfo.tickerid, '1', sma, barmerge.gaps_off, barmerge.lookahead_off)
    fiveM: Series = request.security(syminfo.tickerid, '5', sma, barmerge.gaps_off, barmerge.lookahead_off)
    fifteenM: Series = request.security(syminfo.tickerid, '15', sma, barmerge.gaps_off, barmerge.lookahead_off)
    thirtyM: Series = request.security(syminfo.tickerid, '30', sma, barmerge.gaps_off, barmerge.lookahead_off)
    oneH: Series = request.security(syminfo.tickerid, '60', sma, barmerge.gaps_off, barmerge.lookahead_off)
    twoH: Series = request.security(syminfo.tickerid, '120', sma, barmerge.gaps_off, barmerge.lookahead_off)
    fourH: Series = request.security(syminfo.tickerid, '240', sma, barmerge.gaps_off, barmerge.lookahead_off)
    weekly: Series = request.security(syminfo.tickerid, 'W', sma, barmerge.gaps_off, barmerge.lookahead_off)
    monthly: Series = request.security(syminfo.tickerid, 'M', sma, barmerge.gaps_off, barmerge.lookahead_off)
    daily: Series = request.security(syminfo.tickerid, 'D', sma, barmerge.gaps_off, barmerge.lookahead_off)
    oneMUp = oneM > oneM[1]
    fiveMUp = fiveM > fiveM[1]
    fifteenMUp = fifteenM > fifteenM[1]
    thirtyMUp = thirtyM > thirtyM[1]
    oneHUp = oneH > oneH[1]
    twoHUp = twoH > twoH[1]
    fourHUp = fourH > fourH[1]
    weeklyUp = weekly > weekly[1]
    monthlyUp = monthly > monthly[1]
    dailyUp = daily > daily[1]
    up: str = '📈'
    down: str = '📉'
    oneMTrend = up if oneMUp else down
    fiveMTrend = up if fiveMUp else down
    fifteenMTrend = up if fifteenMUp else down
    thirtyMTrend = up if thirtyMUp else down
    oneHTrend = up if oneHUp else down
    twoHTrend = up if twoHUp else down
    fourHTrend = up if fourHUp else down
    weeklyTrend = up if weeklyUp else down
    monthlyTrend = up if monthlyUp else down
    dailyTrend = up if dailyUp else down
    if dashOn:
        lemonLabel: Series[Label] = label.new(time, close, text='☁️ TV Community Algo Dashboard ☁️' + '\n━━━━━━━━━━━━━━━━━' + '\n         \u200a\u200a🤹 Market Information 🤹' + '\n━━━━━━━━━━━━━━━━━' + '\n🎈\u200a\u200a\u200aVolatility              \u200a\u200a\u200a\u200a\u200a\u200a\u200a| ' + string.tostring(percentVol, '##.##') + '%' + '\n🎈 Volume               \u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a| ' + string.tostring(volumeDash, '##.##') + '\n🎈 RSI                   \u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a\u200a| ' + string.tostring(rsiDash, '##.##') + '\n🎈 Current Sentiment | ' + totalSentTxt + '\n━━━━━━━━━━━━━━━━━' + '\n               🎪 Trend Panel 🎪' + '\n━━━━━━━━━━━━━━━━━' + '\n     1 Minute | ' + oneMTrend + '         2 Hour | ' + twoHTrend + '\n     5 Minute | ' + fiveMTrend + '         4 Hour | ' + fourHTrend + '\n  \u200a\u200a\u200a\u200a\u200a\u200a15 Minute | ' + fifteenMTrend + '        \u200aWeekly | ' + weeklyTrend + '\n  \u200a\u200a\u200a\u200a\u200a\u200a30 Minute | ' + thirtyMTrend + '       Monthly |\u200a\u200a\u200a\u200a\u200a' + monthlyTrend + '\n        1 Hour | ' + oneHTrend + '         \u2009\u2009\u200a\u200a\u200a\u200a\u200aDaily | ' + dailyTrend + '\n━━━━━━━━━━━━━━━━━' + '\n                        with love, -Lemon 🍋', color=dashColor, xloc=xloc.bar_time, style=label.style_label_left, textcolor=dashTextColor, textalign=text.align_left)
        label.set_x(lemonLabel, label.get_x(lemonLabel) + math.round(ta.change(time) * dashDist))
        label.delete(lemonLabel[1])
    Red_1 = color.new(color.new('#FF0000'), 0)
    Orange_1 = color.new(color.new('#FF9800'), 0)
    Red_2 = color.new(color.new('#FF0000'), 30)
    Orange_2 = color.new(color.new('#FF9800'), 30)
    Red_3 = color.new(color.new('#FF0000'), 50)
    Orange_3 = color.new(color.new('#FF9800'), 50)
    Red_4 = color.new(color.new('#FF0000'), 60)
    Orange_4 = color.new(color.new('#FF9800'), 70)
    Red_5 = color.new(color.new('#FF0000'), 80)
    Orange_5 = color.new(color.new('#FF9800'), 80)
    Yellow_1 = color.new(color.new('#FFE500'), 0)
    Green_1 = color.new(color.new('#00FF00'), 0)
    Yellow_2 = color.new(color.new('#FFE500'), 30)
    Green_2 = color.new(color.new('#00FF00'), 30)
    Yellow_3 = color.new(color.new('#FFE500'), 50)
    Green_3 = color.new(color.new('#00FF00'), 50)
    Yellow_4 = color.new(color.new('#FFE500'), 60)
    Green_4 = color.new(color.new('#00FF00'), 70)
    Yellow_5 = color.new(color.new('#FFE500'), 80)
    Green_5 = color.new(color.new('#00FF00'), 80)
    Blue_1 = color.new(color.new('#4985E7'), 0)
    Indigo_1 = color.new(color.new('#7A2BCE'), 0)
    Blue_2 = color.new(color.new('#4985E7'), 30)
    Indigo_2 = color.new(color.new('#7A2BCE'), 30)
    Blue_3 = color.new(color.new('#4985E7'), 50)
    Indigo_3 = color.new(color.new('#7A2BCE'), 50)
    Blue_4 = color.new(color.new('#4985E7'), 60)
    Indigo_4 = color.new(color.new('#7A2BCE'), 60)
    Blue_5 = color.new(color.new('#4985E7'), 80)
    Indigo_5 = color.new(color.new('#7A2BCE'), 80)
    Purple_1 = color.new(color.new('#D12FAD'), 0)
    Purple_2 = color.new(color.new('#D12FAD'), 30)
    Purple_3 = color.new(color.new('#D12FAD'), 50)
    Purple_4 = color.new(color.new('#D12FAD'), 60)
    Purple_5 = color.new(color.new('#D12FAD'), 80)
    c: Persistent[Color] = na(Color)
    k: PersistentSeries[int] = na(int)
    k = nz(k[1], 1)
    if k == 1:
        c = Red_5
    if k == 2:
        c = Red_4
    if k == 3:
        c = Red_3
    if k == 4:
        c = Red_2
    if k == 5:
        c = Red_1
    if k == 6:
        c = Red_2
    if k == 7:
        c = Red_3
    if k == 8:
        c = Red_4
    if k == 9:
        c = Red_5
    if k == 10:
        c = Orange_5
    if k == 11:
        c = Orange_4
    if k == 12:
        c = Orange_3
    if k == 13:
        c = Orange_2
    if k == 14:
        c = Orange_1
    if k == 15:
        c = Orange_2
    if k == 16:
        c = Orange_3
    if k == 17:
        c = Orange_4
    if k == 18:
        c = Orange_5
    if k == 19:
        c = Yellow_5
    if k == 20:
        c = Yellow_4
    if k == 21:
        c = Yellow_3
    if k == 22:
        c = Yellow_2
    if k == 23:
        c = Yellow_1
    if k == 24:
        c = Yellow_2
    if k == 25:
        c = Yellow_3
    if k == 26:
        c = Yellow_4
    if k == 27:
        c = Yellow_5
    if k == 28:
        c = Green_5
    if k == 29:
        c = Green_4
    if k == 30:
        c = Green_3
    if k == 31:
        c = Green_2
    if k == 32:
        c = Green_1
    if k == 33:
        c = Green_2
    if k == 34:
        c = Green_3
    if k == 35:
        c = Green_4
    if k == 36:
        c = Green_5
    if k == 37:
        c = Blue_5
    if k == 38:
        c = Blue_4
    if k == 39:
        c = Blue_3
    if k == 40:
        c = Blue_2
    if k == 41:
        c = Blue_1
    if k == 42:
        c = Blue_2
    if k == 43:
        c = Blue_3
    if k == 44:
        c = Blue_4
    if k == 45:
        c = Blue_5
    if k == 46:
        c = Indigo_5
    if k == 47:
        c = Indigo_4
    if k == 48:
        c = Indigo_3
    if k == 49:
        c = Indigo_2
    if k == 50:
        c = Indigo_1
    if k == 51:
        c = Indigo_2
    if k == 52:
        c = Indigo_3
    if k == 53:
        c = Indigo_4
    if k == 54:
        c = Indigo_5
    if k == 55:
        c = Purple_5
    if k == 56:
        c = Purple_4
    if k == 57:
        c = Purple_3
    if k == 58:
        c = Purple_2
    if k == 59:
        c = Purple_1
    if k == 60:
        c = Purple_2
    if k == 61:
        c = Purple_3
    if k == 62:
        c = Purple_4
    if k == 63:
        c = Purple_5
    k = k + 1
    if k > 63:
        k = 1
    dev_threshold = ta.atr(10) / close * 100 * threshold_multiplier
    depth: int = 10
    extendLeft: Persistent = extendLeft__input
    extendRight: Persistent = extendRight__input
    extending: Persistent = extend.none
    if extendLeft and extendRight:
        extending = extend.both
    if extendLeft and (not extendRight):
        extending = extend.left
    if not extendLeft and extendRight:
        extending = extend.right
    lineLast: Persistent[Line] = na(Line)
    iLast: Persistent[int] = 0
    iPrev: Persistent[int] = 0
    pLast: Persistent[float] = 0
    isHighLast: Persistent[bool] = False
    def pivots(src: Series, length, isHigh):
        l2 = length * 2
        c2 = nz(src[length])
        ok: bool = True
        for i in pine_range(0, l2, 1):
            if isHigh and src[i] > c2:
                ok = False
            if not isHigh and src[i] < c2:
                ok = False
        __block_result__ = (na, na)
        if ok:
            __block_result__ = (bar_index[length], c2)
        else:
            __block_result__ = (NA(int), NA(float))
        return __block_result__

    iH, pH = pivots(high, cast_int(depth / 2), True)
    iL, pL = pivots(low, cast_int(depth / 2), False)
    def calc_dev(base_price, price):
        return 100 * (price - base_price) / price

    def pivotFound(dev, isHigh, index, price):
        __block_result_1__ = (na, na)
        if isHighLast == isHigh and (not na(lineLast)):
            __block_result_2__ = (na, na)
            if price > pLast if isHighLast else price < pLast:
                line.set_xy2(lineLast, index, price)
                __block_result_2__ = (lineLast, isHighLast)
            else:
                __block_result_2__ = (NA(Line), NA(bool))
            __block_result_1__ = __block_result_2__
        else:
            __block_result_3__ = (na, na)
            if math.abs(dev) > dev_threshold:
                id = line.new(iLast, pLast, index, price, color=na, width=1, style=line.style_dashed)
                __block_result_3__ = (id, isHigh)
            else:
                __block_result_3__ = (NA(Line), NA(bool))
            __block_result_1__ = __block_result_3__
        return __block_result_1__

    if not na(iH):
        dev = calc_dev(pLast, pH)
        id, isHigh = pivotFound(dev, True, iH, pH)
        if not na(id):
            if id != lineLast:
                line.delete(lineLast)
            lineLast = id
            isHighLast = isHigh
            iPrev = iLast
            iLast = iH
            pLast = pH
    else:
        if not na(iL):
            dev = calc_dev(pLast, pL)
            id, isHigh = pivotFound(dev, False, iL, pL)
            if not na(id):
                if id != lineLast:
                    line.delete(lineLast)
                lineLast = id
                isHighLast = isHigh
                iPrev = iLast
                iLast = iL
                pLast = pL
    def _draw_line(price, col):
        id: Persistent = line.new(iLast, price, bar_index, price, color=col, width=1, extend=extending)
        __block_result_4__ = na
        if not na(lineLast):
            line.set_xy1(id, line.get_x1(lineLast), price)
            __block_result_4__ = line.set_xy2(id, line.get_x2(lineLast), price)
        return __block_result_4__

    def _draw_label(price, txt, txtColor):
        x = line.get_x1(lineLast) if labelsPosition == 'Left' else line.get_x2(lineLast) if not extendRight else bar_index
        labelStyle = label.style_label_right if labelsPosition == 'Left' else label.style_label_left
        align = text.align_right if labelsPosition == 'Left' else text.align_left
        labelsAlignStrLeft = txt + '\n \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f \n'
        labelsAlignStrRight = '       ' + txt + '\n \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f  \u200f \n'
        labelsAlignStr = labelsAlignStrLeft if labelsPosition == 'Left' else labelsAlignStrRight
        id: Persistent = label.new(x=x, y=price, text=labelsAlignStr, textcolor=txtColor, style=labelStyle, textalign=align, color=color.new('#00000000'))
        label.set_xy(id, x, price)
        label.set_text(id, labelsAlignStr)
        return label.set_textcolor(id, txtColor)

    def _wrap(txt):
        return '(' + string.tostring(txt, '#.##') + ')'

    def _label_txt(level, price):
        l = string.tostring(level) + ' ' if levelsFormat == 'Values' else string.tostring(level * 100) + '% '
        return (l if levels else ' ') + (_wrap(price) if prices else ' ')

    def _crossing_level(sr: Series, r):
        return r > sr and r < sr[1] or (r < sr and r > sr[1])

    startPrice = line.get_y1(lineLast) if reverse else pLast
    endPrice = pLast if reverse else line.get_y1(lineLast)
    iHL = startPrice > endPrice
    diff = (-1 if iHL else 1) * math.abs(startPrice - endPrice)
    def processLevel(show, value, colorL):
        m: float = value
        r = startPrice + diff * m
        __block_result_5__ = na
        if show:
            _draw_line(r, colorL)
            __block_result_5__ = _draw_label(r, _label_txt(m, r), colorL)
        return __block_result_5__

    show_0: bool = True
    value_0: int = 0
    color_0: Color = color.new('#787B86')
    if afibOn:
        processLevel(show_0, value_0, color_0)
    show_0_236: bool = True
    value_0_236: float = 0.236
    color_0_236: Color = color.new('#F44336')
    if afibOn:
        processLevel(show_0_236, value_0_236, color_0_236)
    show_0_382: bool = True
    value_0_382: float = 0.382
    color_0_382: Color = color.new('#81C784')
    if afibOn:
        processLevel(show_0_382, value_0_382, color_0_382)
    show_0_5: bool = True
    value_0_5: float = 0.5
    color_0_5: Color = color.new('#4CAF50')
    if afibOn:
        processLevel(show_0_5, value_0_5, color_0_5)
    show_0_618: bool = True
    value_0_618: float = 0.618
    color_0_618: Color = color.new('#009688')
    if afibOn:
        processLevel(show_0_618, value_0_618, color_0_618)
    show_0_786: bool = True
    value_0_786: float = 0.786
    color_0_786: Color = color.new('#64B5F6')
    if afibOn:
        processLevel(show_0_786, value_0_786, color_0_786)
    show_1: bool = True
    value_1: int = 1
    color_1: Color = color.new('#787B86')
    if afibOn:
        processLevel(show_1, value_1, color_1)
    h1000 = ta.highest(1000)
    h750 = ta.highest(750)
    h500 = ta.highest(500)
    h250 = ta.highest(250)
    h100 = ta.highest(100)
    h50 = ta.highest(50)
    h10 = ta.highest(10)
    plot(h1000 if srLines else na, title='R1', color=color.green if close > h1000 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h750 if srLines else na, title='R2', color=color.green if close > h750 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h500 if srLines else na, title='R3', color=color.green if close > h500 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h250 if srLines else na, title='R4', color=color.green if close > h250 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h100 if srLines else na, title='R5', color=color.green if close > h100 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h50 if srLines else na, title='R6', color=color.green if close > h50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(h10 if srLines else na, title='R6', color=color.green if close > h50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    l1000 = ta.lowest(1000)
    l750 = ta.lowest(750)
    l500 = ta.lowest(500)
    l250 = ta.lowest(250)
    l100 = ta.lowest(100)
    l50 = ta.lowest(50)
    l10 = ta.lowest(10)
    plot(l1000 if srLines else na, title='S1', color=color.green if close > l1000 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l750 if srLines else na, title='S2', color=color.green if close > l750 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l500 if srLines else na, title='S3', color=color.green if close > l500 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l250 if srLines else na, title='S4', color=color.green if close > l250 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l100 if srLines else na, title='S5', color=color.green if close > l100 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l50 if srLines else na, title='S6', color=color.green if close > l50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    plot(l10 if srLines else na, title='S6', color=color.green if close > l50 else color.red, linewidth=1, offset=-9999, trackprice=True)
    basis = ta.sma(close, 20)
    twoDev = 2 * ta.stdev(close, 20)
    upper3 = basis + twoDev
    lower3 = basis - twoDev
    threeDev = 3 * ta.stdev(close, 20)
    upper4 = basis + threeDev
    lower4 = basis - threeDev
    plot(basis if voidLines else na, 'Basis', color.new(color.purple, 0), editable=False)
    p5 = plot(upper3 if voidLines else na, 'Upper 200%', c, editable=False)
    p6 = plot(lower3 if voidLines else na, 'Lower 200%', c, editable=False)
    p7 = plot(upper4 if voidLines else na, 'Upper 300%', c, editable=False)
    p8 = plot(lower4 if voidLines else na, 'Lower 300%', c, editable=False)
    fill(p7, p5, color.new(color.teal, 75))
    fill(p8, p6, color.new(color.purple, 75))
    colorBars = color.teal if close > basis else color.purple if close < basis else na
    ema8 = ta.ema(close, 8)
    ema200 = ta.ema(close, 200)
    barcolor(colorBars if colorBar else na)
    plot(ema8 if emaLines else na, 'EMA 8', color.new(color.white, 0), 2)
    plot(ema200 if emaLines else na, 'EMA 200', color.new(color.green, 0), 2)
    n1: int = 14
    n2: int = 21
    ap = hlc3
    esa = ta.ema(ap, n1)
    d = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)
    sell: Persistent[bool] = False
    buy: Persistent[bool] = False
    crossover_1 = ta.crossover(wt1, wt2)
    buySignal = not sell and crossover_1
    crossunder_1 = ta.crossunder(wt1, wt2)
    sellSignal = not buy and crossunder_1
    if buySignal:
        sell = True
        buy = False
    if sellSignal:
        sell = False
        buy = True
    plotshape((na if na(buySignal) else 1 if buySignal else 0) if bsSignals else na, title='Buy Signal', location=location.belowbar, color=color.new(color.green, 0), style=shape.labelup, size=size.small, textcolor=color.new(color.white, 0), text='BUY')
    plotshape((na if na(sellSignal) else 1 if sellSignal else 0) if bsSignals else na, title='Sell Signal', location=location.abovebar, color=color.new(color.red, 0), style=shape.labeldown, size=size.small, textcolor=color.new(color.white, 0), text='SELL')
    alertcondition(buySignal, 'Buy Signal', 'Buy Signal')
    alertcondition(sellSignal, 'Sell Signal', 'Sell Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
