"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barcolor, bgcolor, chart, close, color, display,
    fixnan, high, input, label, last_bar_index, line, low, na, plot, request, script, size,
    syminfo, ta, time
)
from pynecore.types import Color, Line, NA, Persistent
from pynecore.types.chart import ChartPoint


@udt
class bin:
    lin: Line = na(Line)
    slope: float = na(float)
    active: bool = na(bool)
    cp: ChartPoint = na(ChartPoint)


sp: str = '         '


@script.indicator('Trendline Breakout Navigator [LuxAlgo]', shorttitle='LuxAlgo - Trendline Breakout Navigator', max_lines_count=500, max_labels_count=500, max_bars_back=5000, overlay=True)
def main(
    res=input.timeframe('', 'Period        '),
    i1=input.bool(True, '', inline='1', group='Swing Length'),
    i2=input.bool(True, '', inline='2', group='Swing Length'),
    i3=input.bool(True, '', inline='3', group='Swing Length'),
    l1=input.int(60, 'Long     ', minval=1, inline='1', group='Swing Length'),
    l2=input.int(30, 'Medium', minval=1, inline='2', group='Swing Length'),
    l3=input.int(10, 'Short    ', minval=1, inline='3', group='Swing Length'),
    cBull=input.color(color.new('#089981'), 'Trendline' + sp, inline='d', group='Style'),
    cBear=input.color(color.new('#F23645'), '', inline='d', group='Style', tooltip='Bullish/Bearish Trendline'),
    cWickBull=input.color(color.new('#085DEF'), 'Wick Dot' + sp, inline='w', group='Style'),
    cWickBear=input.color(color.new('#FF5D00'), '', inline='w', group='Style', tooltip='Bullish/Bearish Wick'),
    term=input.string('Long', 'Term', options=('Long', 'Medium', 'Short')),
    HHLL=input.string('None', 'HH/LL', options=('None', 'Only HH/LL', 'HH/LL & previous H/L')),
    bg=input.bool(False, 'Background Color'),
    cc=input.bool(False, 'Bar Color')
):
    lbi = last_bar_index
    n = bar_index
    INV = NA(Color)
    def draw(toggle, res, left, right, pos):
        ps = 1 if term == 'Long' else 2 if term == 'Medium' else 3
        trend: Persistent[int] = 0
        prevPh: Persistent[ChartPoint] = chart.point.from_index(na, na)
        prevPl: Persistent[ChartPoint] = chart.point.from_index(na, na)
        bn: Persistent[bin] = bin(NA(Line), 0, False)
        ph_ = ta.pivothigh(left, right)
        tH, ph = request.security(syminfo.tickerid, res, (time[2], ph_))
        pl_ = ta.pivotlow(left, right)
        tL, pl = request.security(syminfo.tickerid, res, (time[2], pl_))
        cH = ta.change(fixnan(ph))
        cL = ta.change(fixnan(pl))
        chH = cH != 0 and cL == 0
        chL = cL != 0 and cH == 0
        if toggle:
            if bn.active:
                if line.get_x2(bn.lin) - line.get_x1(bn.lin) > 5000:
                    bn.active = False
                    line.delete(bn.lin)
                else:
                    line.set_xy2(bn.lin, n, line.get_y2(bn.lin) + bn.slope)
            if chH:
                v: float = 0.0
                idx: int = 0
                for i in pine_range(0, 5000, 1):
                    Ti = time[i]
                    if high[i] > v:
                        v = high[i]
                        idx = i
                    if Ti < tH:
                        break
                x = n - idx
                c = close[idx]
                if trend < 1:
                    if v > prevPh.price and x - prevPh.index > 5 and (n - prevPl.index < 5000):
                        if pos == ps and HHLL != 'None':
                            label.new(x, v, color=NA(Color), text='HH\n', size=size.tiny, textcolor=chart.fg_color)
                            if HHLL == 'HH/LL & previous H/L':
                                label.new(prevPh.index, prevPh.price, color=NA(Color), size=size.tiny, text='●', textcolor=chart.fg_color)
                        trend = 1
                        bn = bin(line.new(prevPl.index, prevPl.price, n, prevPl.price, color=cBull, style=line.style_solid if pos == 1 else line.style_dashed if pos == 2 else line.style_dotted, width=2 if pos == 1 else 1), 0, True, chart.point.from_index(prevPl.index, prevPl.price))
                    else:
                        if bn.active:
                            slope = (v - bn.cp.price) / (x - bn.cp.index)
                            if v < line.get_y1(bn.lin) + slope and (v > line.get_y2(bn.lin) + slope or bn.slope == 0):
                                priceLin = line.get_price(bn.lin, n - idx)
                                if c < priceLin:
                                    if bn.slope != 0:
                                        label.new(n - idx, priceLin, style=label.style_label_center, text='●', color=NA(Color), textcolor=cWickBear)
                                    line.set_xy2(bn.lin, n, v + slope * idx)
                                    if bn.slope == 0:
                                        stop: bool = False
                                        while not stop:
                                            arr: list[float] = array.new_float()
                                            __loop_9__ = pine_loop(0, 1)
                                            while __loop_9__.step(n - line.get_x1(bn.lin)):
                                                i = __loop_9__.value
                                                array.push(arr, close[i] - line.get_price(bn.lin, n - i))
                                            highest_point = array.max(arr)
                                            if highest_point > 0:
                                                ix = array.indexof(arr, highest_point)
                                                x1 = n - ix
                                                y1 = high[ix]
                                                bn.cp.index = x1
                                                bn.cp.price = y1
                                                slope = (v - y1) / (x - x1)
                                                line.set_xy2(bn.lin, n, v + slope * idx)
                                                line.set_xy1(bn.lin, x1, y1)
                                                bn.slope = slope
                                            else:
                                                line.set_xy2(bn.lin, n, v + slope * idx)
                                                bn.slope = slope
                                                stop = True
                                    else:
                                        bn.slope = slope
                                else:
                                    bn.active = False
                prevPh.index = x
                prevPh.price = v
            else:
                if trend < 1:
                    if close > line.get_y2(bn.lin):
                        bn.active = False
            if chL:
                v: float = 10000000.0
                idx: int = 0
                for i in pine_range(0, 5000, 1):
                    Ti = time[i]
                    if low[i] < v:
                        v = low[i]
                        idx = i
                    if Ti < tL:
                        break
                x = n - idx
                c = close[idx]
                if trend > -1:
                    if v < prevPl.price and x - prevPl.index > 5 and (n - prevPh.index < 5000):
                        if pos == ps and HHLL != 'None':
                            label.new(x, v, color=NA(Color), text='\nLL', size=size.tiny, textcolor=chart.fg_color, style=label.style_label_up)
                            if HHLL == 'HH/LL & previous H/L':
                                label.new(prevPl.index, prevPl.price, color=NA(Color), size=size.tiny, text='●', textcolor=chart.fg_color, style=label.style_label_up)
                        trend = -1
                        bn = bin(line.new(prevPh.index, prevPh.price, n, prevPh.price, color=cBear, style=line.style_solid if pos == 1 else line.style_dashed if pos == 2 else line.style_dotted, width=2 if pos == 1 else 1), 0, True, chart.point.from_index(prevPh.index, prevPh.price))
                    else:
                        if bn.active:
                            slope = (v - bn.cp.price) / (x - bn.cp.index)
                            if v > line.get_y1(bn.lin) + slope and (v < line.get_y2(bn.lin) + slope or bn.slope == 0):
                                priceLin = line.get_price(bn.lin, n - idx)
                                if c > priceLin:
                                    if bn.slope != 0:
                                        label.new(n - idx, priceLin, style=label.style_label_center, text='●', color=NA(Color), textcolor=cWickBull)
                                    line.set_xy2(bn.lin, n, v + slope * idx)
                                    if bn.slope == 0:
                                        stop: bool = False
                                        while not stop:
                                            arr: list[float] = array.new_float()
                                            __loop_9__ = pine_loop(0, 1)
                                            while __loop_9__.step(n - line.get_x1(bn.lin)):
                                                i = __loop_9__.value
                                                array.push(arr, line.get_price(bn.lin, n - i) - close[i])
                                            deepest_point = array.max(arr)
                                            if deepest_point > 0:
                                                ix = array.indexof(arr, deepest_point)
                                                x1 = n - ix
                                                y1 = low[ix]
                                                bn.cp.index = x1
                                                bn.cp.price = y1
                                                slope = (v - y1) / (x - x1)
                                                line.set_xy2(bn.lin, n, v + slope * idx)
                                                line.set_xy1(bn.lin, x1, y1)
                                                bn.slope = slope
                                            else:
                                                line.set_xy2(bn.lin, n, v + slope * idx)
                                                bn.slope = slope
                                                stop = True
                                    else:
                                        bn.slope = slope
                                else:
                                    bn.active = False
                prevPl.index = x
                prevPl.price = v
            else:
                if trend > -1:
                    if close < line.get_y2(bn.lin):
                        bn.active = False
        return (trend, line.get_y2(bn.lin))

    trend1, value1 = draw(i1, res, l1, 1, 1)
    trend2, value2 = draw(i2, res, l2, 1, 2)
    trend3, value3 = draw(i3, res, l3, 1, 3)
    col = NA(Color)
    if cc:
        __block_result__ = na
        __switch_1__ = close > value1
        if __switch_1__ == True:
            __block_result_1__ = na
            __switch_2__ = close > value2
            if __switch_2__ == True:
                __block_result_2__ = na
                if close > value3:
                    __block_result_2__ = color.new(cBull, 20)
                else:
                    __block_result_2__ = color.new(cBull, 43)
                __block_result_1__ = __block_result_2__
            else:
                __block_result_3__ = na
                if close > value3:
                    __block_result_3__ = color.new(cBull, 66)
                else:
                    __block_result_3__ = color.new(cBull, 89)
                __block_result_1__ = __block_result_3__
            __block_result__ = __block_result_1__
        else:
            __block_result_4__ = na
            __switch_2__ = close < value2
            if __switch_2__ == True:
                __block_result_5__ = na
                if close < value3:
                    __block_result_5__ = color.new(cBear, 20)
                else:
                    __block_result_5__ = color.new(cBear, 43)
                __block_result_4__ = __block_result_5__
            else:
                __block_result_6__ = na
                if close < value3:
                    __block_result_6__ = color.new(cBear, 66)
                else:
                    __block_result_6__ = color.new(cBear, 89)
                __block_result_4__ = __block_result_6__
            __block_result__ = __block_result_4__
        col = __block_result__
    plot(value1, display=display.none)
    plot(value2, display=display.none)
    plot(value3, display=display.none)
    plot(trend1, display=display.none)
    barcolor(col if cc else na)
    isValid = bg and (i1 if term == 'Long' else i2 if term == 'Medium' else i3)
    bgcolor(color.new(cBull if close > (value1 if term == 'Long' else value2 if term == 'Medium' else value3) else cBear, 97) if isValid else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
