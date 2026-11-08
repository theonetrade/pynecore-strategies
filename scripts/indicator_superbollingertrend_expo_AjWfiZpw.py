"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, chart, close, color, format,
    high, input, label, line, low, math, na, plot, position, script, size, string, ta, table
)
from pynecore.types import Color, NA, Persistent, Table


@udt
class ZigZag:
    x1: list[int] = na(list)
    y1: list[float] = na(list)
    diff: list[float] = na(list)


@udt
class SuperBollingerTrend:
    s: float = na(float)
    c: Color = na(Color)


@udt
class Alerts:
    Long: bool = False
    Short: bool = False
    LongTp: bool = False
    ShortTp: bool = False


@script.indicator('SuperBollingerTrend (Expo)', '', True, max_labels_count=500)
def main(
    prd=input.int(12, 'Period', minval=1, inline='setting'),
    mult=input.float(2.0, 'Mult', minval=0.1, step=0.1, inline='setting', tooltip='Set the Bollinger Band period. \n\nSet the multiplier.'),
    showZigZag=input.bool(True, 'ZigZag', inline='zigzag'),
    signal=input.string('Signal', '', options=('Signal', 'Peak Distance'), inline='zigzag'),
    dev=input.string('ZigZag', '', options=('ZigZag', 'High/Low', 'Close'), inline='zigzag', tooltip='Enable the ZigZag Bollinger Signals. \n\nSelect if you only want to display the signals or the Peak Signal Distance between each signal. \n\nThe Signal Distance can be calculated using the ZigZag, High/Low, or Close.'),
    showTable=input.bool(False, 'Average/Median Distance', inline='', tooltip='Enable the Table that displays the Average or Median ZigZag move.'),
    showTP=input.bool(False, 'Take Profit', inline='tp'),
    Tp=input.string('Median', '', options=('Median', 'Average'), inline='tp', tooltip='Enable the Take-Profit line. \n\nSelect if the TP should be based on the Average or Median move.')
):
    zz: Persistent[ZigZag] = ZigZag(array.new_int(), array.new_float(), array.new_float())
    sbt: Persistent[SuperBollingerTrend] = SuperBollingerTrend(0.0, na)
    alerted: Alerts = Alerts()
    b: int = bar_index
    bbup: float = ta.sma(high, prd) + ta.stdev(high, prd) * mult
    bbdn: float = ta.sma(low, prd) - ta.stdev(low, prd) * mult
    @method
    def zigzag(z: ZigZag, c, p, l):
        y2 = sbt.s if dev == 'ZigZag' else p if dev == 'High/Low' else close
        if array.size(z.x1) > 0:
            x1__00000020__ = array.get(z.x1, 0)
            y1__00000020__ = array.get(z.y1, 0)
            array.unshift(z.diff, math.abs(y2 - y1__00000020__))
            line.new(x1__00000020__, y1__00000020__, b, y2, color=color.new(color.gray, 0), style=line.style_dashed)
            style = (label.style_triangleup if l else label.style_triangledown) if signal == 'Signal' else label.style_label_up if l else label.style_label_down
            txt = na if signal == 'Signal' else string.tostring(y2 - y1__00000020__, format.mintick) + 'p'
            label.new(b, sbt.s, txt, color=c, size=size.small, style=style, textcolor=chart.bg_color)
        array.unshift(z.x1, b)
        return array.unshift(z.y1, y2)

    @method
    def SBT(s: SuperBollingerTrend, cond, val, col, p, l):
        s.s = 0.0 if na(bbdn) or na(bbup) else math.max(sbt.s, bbdn) if close > sbt.s else math.min(sbt.s, bbup) if close < sbt.s else 0.0
        __block_result__ = na
        if cond:
            s.s = val
            s.c = col
            if showZigZag:
                zigzag(zz, col, p, l)
            alerted.Long = True if l else False
            alerted.Short = False if l else True
            __block_result__ = alerted.Short
        return __block_result__

    SBT(sbt, ta.crossover(close, sbt.s), bbdn, color.lime, low, True)
    SBT(sbt, ta.crossunder(close, sbt.s), bbup, color.red, high, False)
    plot(sbt.s, 'SuperBollingerTrend', sbt.c)
    tp: Persistent = line.new(na, na, na, na, color=color.lime)
    ltp: Persistent = label.new(na, na, 'TP', color=NA(Color), style=label.style_label_left, textcolor=chart.fg_color, size=size.normal)
    dist = array.median(zz.diff) if Tp == 'Median' else array.avg(zz.diff)
    if showTP and array.size(zz.y1) > 0:
        pos = True if close > sbt.s else False
        x = array.get(zz.x1, 0)
        y = array.get(zz.y1, 0) + dist if pos else array.get(zz.y1, 0) - dist
        method_call('set_xy1', tp, x, y)
        method_call('set_xy2', tp, b + 10, y)
        method_call('set_xy', ltp, b + 10, y)
        alerted.LongTp = high >= y and high[1] < y if pos else False
        alerted.ShortTp = False if pos else low <= y and low[1] > y
    tbl: Persistent[Table] = na(Table)
    if barstate.islast and showZigZag and showTable:
        tbl = table.new(position.top_right, 1, 1, chart.bg_color, frame_color=color.new(color.gray, 50), frame_width=3, border_width=1)
        table.cell(tbl, 0, 0, 'Median ZigZag Distance: ' + string.tostring(dist, format.mintick) + 'p' if Tp == 'Median' else 'Avg ZigZag Distance: ' + string.tostring(dist, format.mintick) + 'p', text_color=chart.fg_color)
    alertcondition(alerted.Long, 'Long Alert', 'Long Signal')
    alertcondition(alerted.Short, 'Short Alert', 'Short Signal')
    alertcondition(alerted.LongTp, 'Long TP Alert', 'Long TP')
    alertcondition(alerted.ShortTp, 'Short TP Alert', 'Short TP')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
