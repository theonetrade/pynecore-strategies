"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, color, extend, high, input, label, line,
    location, low, math, na, nz, plot, plotshape, script, shape, string, ta
)
from pynecore.types import Line, NA, Persistent, Series


@script.indicator('Auto Fib Retracement Alerts', overlay=True, na_bool=True)
def main(
    dev_threshold=input.float(title='Deviation', defval=5, minval=0),
    depth=input.int(title='Depth', defval=10, minval=1),
    extendLeft__input=input(False, 'Extend Lines Left'),
    extendRight__input=input(True, 'Extend Lines Right'),
    retracement=input(0.618),
    reverse=input(False, 'Reverse'),
    prices=input(True, 'Prices'),
    levels=input(True, 'Levels'),
    levelsFormat=input.string('Values', 'Levels Format', options=('Values', 'Percent')),
    sl1__input=input(True, '0'),
    sl2__input=input(True, '0.236'),
    sl3__input=input(True, '0.382'),
    sl4__input=input(True, '0.5'),
    sl5__input=input(True, '0.618'),
    sl6__input=input(True, '0.786'),
    sl7__input=input(True, '1'),
    sl8__input=input(True, '1.272'),
    sl9__input=input(True, '1.414'),
    sl10__input=input(True, '1.618'),
    sl11__input=input(False, '2.618'),
    sl12__input=input(False, '3.618'),
    sl13__input=input(False, '4.236')
):
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
        c = nz(src[length])
        ok: bool = True
        for i in pine_range(0, l2, 1):
            if isHigh and src[i] > c:
                ok = False
            if not isHigh and src[i] < c:
                ok = False
        __block_result__ = (na, na)
        if ok:
            __block_result__ = (bar_index[length], c)
        else:
            __block_result__ = (NA(int), NA(float))
        return __block_result__

    iH, pH = pivots(high, depth / 2, True)
    iL, pL = pivots(low, depth / 2, False)
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
                id = line.new(iLast, pLast, index, price, color=color.gray, width=1, style=line.style_dashed)
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
        id: Persistent = label.new(x=line.get_x1(lineLast), y=price, text=txt, textcolor=txtColor, style=label.style_none)
        label.set_xy(id, line.get_x1(lineLast), price)
        label.set_text(id, txt)
        return label.set_textcolor(id, txtColor)

    def _wrap(txt):
        return '(' + string.tostring(txt, '#.##') + ')'

    def _label_txt(level, price):
        l = string.tostring(level) if levelsFormat == 'Values' else string.tostring(level * 100) + '%'
        return (l if levels else '') + (_wrap(price) if prices else '')

    sl1: Persistent = sl1__input
    vall1: Persistent[float] = 0.0
    sl2: Persistent = sl2__input
    vall2: Persistent[float] = 0.236
    sl3: Persistent = sl3__input
    vall3: Persistent[float] = 0.382
    sl4: Persistent = sl4__input
    vall4: Persistent[float] = 0.5
    sl5: Persistent = sl5__input
    vall5: Persistent[float] = 0.618
    sl6: Persistent = sl6__input
    vall6: Persistent[float] = 0.786
    sl7: Persistent = sl7__input
    vall7: Persistent[int] = 1
    sl8: Persistent = sl8__input
    vall8: Persistent[float] = 1.272
    sl9: Persistent = sl9__input
    vall9: Persistent[float] = 1.414
    sl10: Persistent = sl10__input
    vall10: Persistent[float] = 1.618
    sl11: Persistent = sl11__input
    vall11: Persistent[float] = 2.618
    sl12: Persistent = sl12__input
    vall12: Persistent[float] = 3.618
    sl13: Persistent = sl13__input
    vall13: Persistent[float] = 4.236
    def _draw_retracement(startPrice, endPrice):
        iHL = startPrice > endPrice
        diff = (-1 if iHL else 1) * math.abs(startPrice - endPrice)
        if sl1:
            l1 = startPrice + diff * vall1
            _draw_line(l1, color.new('#808080'))
            _draw_label(l1, _label_txt(vall1, l1), color.new('#808080'))
        if sl2:
            l2 = startPrice + diff * vall2
            _draw_line(l2, color.new('#A61C00'))
            _draw_label(l2, _label_txt(vall2, l2), color.new('#A61C00'))
        if sl3:
            l3 = startPrice + diff * vall3
            _draw_line(l3, color.new('#95CC28'))
            _draw_label(l3, _label_txt(vall3, l3), color.new('#95CC28'))
        if sl4:
            l4 = startPrice + diff * vall4
            _draw_line(l4, color.new('#28CC28'))
            _draw_label(l4, _label_txt(vall4, l4), color.new('#28CC28'))
        if sl5:
            l5 = startPrice + diff * vall5
            _draw_line(l5, color.new('#28CC95'))
            _draw_label(l5, _label_txt(vall5, l5), color.new('#28CC95'))
        if sl6:
            l6 = startPrice + diff * vall6
            _draw_line(l6, color.new('#2895CC'))
            _draw_label(l6, _label_txt(vall6, l6), color.new('#2895CC'))
        if sl7:
            l7 = startPrice + diff * vall7
            _draw_line(l7, color.new('#808080'))
            _draw_label(l7, _label_txt(vall7, l7), color.new('#808080'))
        if sl8:
            l8 = startPrice + diff * vall8
            _draw_line(l8, color.new('#82CA89'))
            _draw_label(l8, _label_txt(vall8, l8), color.new('#82CA89'))
        if sl9:
            l9 = startPrice + diff * vall9
            _draw_line(l9, color.new('#F32C42'))
            _draw_label(l9, _label_txt(vall9, l9), color.new('#F32C42'))
        if sl10:
            l10 = startPrice + diff * vall10
            _draw_line(l10, color.new('#2796ED'))
            _draw_label(l10, _label_txt(vall10, l10), color.new('#2796ED'))
        if sl11:
            l11 = startPrice + diff * vall11
            _draw_line(l11, color.new('#A61C00'))
            _draw_label(l11, _label_txt(vall11, l11), color.new('#A61C00'))
        if sl12:
            l12 = startPrice + diff * vall12
            _draw_line(l12, color.new('#9B03AE'))
            _draw_label(l12, _label_txt(vall12, l12), color.new('#9B03AE'))
        if sl13:
            l13 = startPrice + diff * vall13
            _draw_line(l13, color.new('#E80065'))
            _draw_label(l13, _label_txt(vall13, l13), color.new('#E80065'))
        return diff

    p1: Series = pLast if reverse else line.get_y1(lineLast)
    p2: Series = line.get_y1(lineLast) if reverse else pLast
    diff = _draw_retracement(p1, p2)
    level: Series = p1 + diff * retracement
    plot(p1, 'Start', color.red if p1 == p1[1] else na, 3, plot.style_line)
    plot(p2, 'End', color.lime if p2 == p2[1] else na, 3, plot.style_line)
    plot(level, 'Target', color.purple if level == level[1] else na, 3, plot.style_line)
    buy = p1 < p2 and low <= level and (high > level)
    barssince_1: Series = ta.barssince(buy)
    barssince_2 = ta.barssince(p2 != p2[1])
    buy_alert = buy and barssince_1[1] > barssince_2
    sell = p1 > p2 and high >= level and (low < level)
    barssince_3: Series = ta.barssince(sell)
    barssince_4 = ta.barssince(p2 != p2[1])
    sell_alert = sell and barssince_3[1] > barssince_4
    plotshape(buy_alert, 'Buy Retrace', shape.labelup, location.belowbar, color.new(color.lime, 0), text='Buy Retrace', textcolor=color.new(color.black, 0))
    plotshape(sell_alert, 'Sell Retrace', shape.labeldown, color=color.new(color.red, 0), text='Sell Retrace', textcolor=color.new(color.white, 0))
    alertcondition(buy_alert, 'Buy Retrace')
    alertcondition(sell_alert, 'Sell Retrace')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
