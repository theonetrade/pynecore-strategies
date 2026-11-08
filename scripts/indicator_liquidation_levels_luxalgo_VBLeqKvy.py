"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, close, color, high, hl2, hlc3, hlcc4, input, line,
    location, low, math, na, nz, ohlc4, open, plotshape, script, shape, size, ta, volume
)
from pynecore.types import Line, Persistent


@udt
class bar:
    h: float = _dataclass_field(default_factory=lambda: high)
    l: float = _dataclass_field(default_factory=lambda: low)
    v: float = _dataclass_field(default_factory=lambda: volume)
    i: int = _dataclass_field(default_factory=lambda: bar_index)


rpTT = 'Liquidation Levels are estimates of potential price levels where liquidation events may occur\n' + ' - The reference price option defines the base price in calculating liquidation price levels'
vlTT = 'Liquidation data is closely tied in with trading volumes in the market and the movement in the underlying asset’s price\n' + ' -  The volume threshold option is the primary factor in detecting the significant trading activities that could potentially lead to liquidating leveraged positions\n' + ' -  The volatility threshold option (below) is the secondary factor that aims at detecting significant movement in the underlying asset’s price with relatively lower trading activities that could potentially also lead to liquidating high-leveraged positions'


@script.indicator('Liquidation Levels [LuxAlgo]', 'LuxAlgo - Liquidation Levels', True, max_lines_count=500, max_bars_back=5000)
def main(
    refPL=input.string('open', 'Reference Price', options=('open', 'close', 'oc2', 'hl2', 'hlc3', 'ohlc4', 'hlcc4'), tooltip=rpTT),
    vbHT=input.float(1.7, 'Volume Threshold', minval=1.0, step=0.1, tooltip=vlTT),
    lqTH=input.int(10, 'Volatility Threshold', minval=0, step=5),
    lqL1=input.bool(True, 'Leverage', inline='L1'),
    lgL1V=input.int(25, '', minval=1, inline='L1'),
    lqL1L=input.color(color.new(color.new('#5B9CF6'), 50), '', inline='L1'),
    lqL1S=input.color(color.new(color.new('#F06292'), 50), '', inline='L1'),
    lqL2=input.bool(True, 'Leverage', inline='L2'),
    lgL2V=input.int(50, '', minval=1, inline='L2'),
    lqL2L=input.color(color.new(color.new('#4DD0E1'), 50), '', inline='L2'),
    lqL2S=input.color(color.new(color.new('#BA68C8'), 50), '', inline='L2'),
    lqL3=input.bool(True, 'Leverage', inline='L3'),
    lgL3V=input.int(100, '', minval=1, inline='L3'),
    lqL3L=input.color(color.new(color.new('#42BDA8'), 50), '', inline='L3'),
    lqL3S=input.color(color.new(color.new('#9575CD'), 50), '', inline='L3'),
    lqBB=input.bool(False, 'Hide Liquidation Bubbles'),
    lqLN=input.bool(False, 'Hide Liquidation Levels')
):
    b: bar = bar()
    aLQ: Persistent[list[Line]] = array.new_line()
    nzV = nz(b.v)
    def f_gSRC(_s):
        __block_result__ = na
        __switch__ = _s
        if __switch__ == 'open':
            __block_result__ = open
        elif __switch__ == 'close':
            __block_result__ = close
        elif __switch__ == 'hl2':
            __block_result__ = hl2
        elif __switch__ == 'oc2':
            __block_result__ = math.avg(open, close)
        elif __switch__ == 'hlc3':
            __block_result__ = hlc3
        elif __switch__ == 'ohlc4':
            __block_result__ = ohlc4
        elif __switch__ == 'hlcc4':
            __block_result__ = hlcc4
        return __block_result__

    refP = f_gSRC(refPL)
    vbMA = ta.sma(nzV, 13)
    nzVd2 = nzV > vbMA * (2 + vbHT)
    nzVd1 = nzV > vbMA * (1 + vbHT)
    nzVd0 = nzV > vbMA * (0 + vbHT)
    lT = b.l != refP and refP / (refP - b.l) <= lqTH or (b.h != refP and refP / (b.h - refP) <= lqTH)
    eC = refP * (1 + 1.0 / 333) < b.h or refP * (1 - 1.0 / 333) > b.l
    l1PL = refP * (1 + 1.0 / lgL1V)
    plotshape(l1PL if not lqBB and lqL1 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL1L, editable=False, size=size.normal)
    plotshape(l1PL if not lqBB and lqL1 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL1L, editable=False, size=size.small)
    plotshape(l1PL if not lqBB and lqL1 and nzVd0 and eC else l1PL if not lqBB and lqL1 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL1L, editable=False, size=size.tiny)
    if not lqLN and lqL1 and (lT or nzVd0) and (l1PL > b.h) and eC:
        array.push(aLQ, line.new(b.i, l1PL, b.i + 1, l1PL, color=lqL1L, width=3 if nzVd2 else 2 if nzVd1 else 1))
    l1PS = refP * (1 - 1.0 / lgL1V)
    plotshape(l1PS if not lqBB and lqL1 and nzVd0 and eC else l1PS if not lqBB and lqL1 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL1S, editable=False, size=size.tiny)
    plotshape(l1PS if not lqBB and lqL1 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL1S, editable=False, size=size.small)
    plotshape(l1PS if not lqBB and lqL1 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL1S, editable=False, size=size.normal)
    if not lqLN and lqL1 and (lT or nzVd0) and (l1PS < b.l) and eC:
        array.push(aLQ, line.new(b.i, l1PS, b.i + 1, l1PS, color=lqL1S, width=3 if nzVd2 else 2 if nzVd1 else 1))
    l2PL = refP * (1 + 1.0 / lgL2V)
    plotshape(l2PL if not lqBB and lqL2 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL2L, editable=False, size=size.normal)
    plotshape(l2PL if not lqBB and lqL2 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL2L, editable=False, size=size.small)
    plotshape(l2PL if not lqBB and lqL2 and nzVd0 and eC else l2PL if not lqBB and lqL2 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL2L, editable=False, size=size.tiny)
    if not lqLN and lqL2 and (lT or nzVd0) and (l2PL > b.h) and eC:
        array.push(aLQ, line.new(b.i, l2PL, b.i + 1, l2PL, color=lqL2L, width=3 if nzVd2 else 2 if nzVd1 else 1))
    l2PS = refP * (1 - 1.0 / lgL2V)
    plotshape(l2PS if not lqBB and lqL2 and nzVd0 and eC else l2PS if not lqBB and lqL2 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL2S, editable=False, size=size.tiny)
    plotshape(l2PS if not lqBB and lqL2 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL2S, editable=False, size=size.small)
    plotshape(l2PS if not lqBB and lqL2 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL2S, editable=False, size=size.normal)
    if not lqLN and lqL2 and (lT or nzVd0) and (l2PS < b.l) and eC:
        array.push(aLQ, line.new(b.i, l2PS, b.i + 1, l2PS, color=lqL2S, width=3 if nzVd2 else 2 if nzVd1 else 1))
    l3PL = refP * (1 + 1.0 / lgL3V)
    plotshape(l3PL if not lqBB and lqL3 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL3L, editable=False, size=size.normal)
    plotshape(l3PL if not lqBB and lqL3 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL3L, editable=False, size=size.small)
    plotshape(l3PL if not lqBB and lqL3 and nzVd0 and eC else l3PL if not lqBB and lqL3 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL3L, editable=False, size=size.tiny)
    if not lqLN and lqL3 and (lT or nzVd0) and (l3PL > b.h) and eC:
        array.push(aLQ, line.new(b.i, l3PL, b.i + 1, l3PL, color=lqL3L, width=3 if nzVd2 else 2 if nzVd1 else 1))
    l3PS = refP * (1 - 1.0 / lgL3V)
    plotshape(l3PS if not lqBB and lqL3 and nzVd0 and eC else l3PS if not lqBB and lqL3 and lT else na, 'Bubbles', shape.circle, location.absolute, lqL3S, editable=False, size=size.tiny)
    plotshape(l3PS if not lqBB and lqL3 and nzVd1 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL3S, editable=False, size=size.small)
    plotshape(l3PS if not lqBB and lqL3 and nzVd2 and eC else na, 'Bubbles', shape.circle, location.absolute, lqL3S, editable=False, size=size.normal)
    if not lqLN and lqL3 and (lT or nzVd0) and (l3PS < b.l) and eC:
        array.push(aLQ, line.new(b.i, l3PS, b.i + 1, l3PS, color=lqL3S, width=3 if nzVd2 else 2 if nzVd1 else 1))
    if array.size(aLQ) > 0:
        qt = array.size(aLQ)
        for ln in pine_range(qt - 1, 0, 1):
            if ln < array.size(aLQ):
                cL = array.get(aLQ, ln)
                yL = method_call('get_y1', cL)
                if b.h > yL and b.l < yL:
                    array.remove(aLQ, ln)
                else:
                    method_call('set_x2', cL, b.i + 1)
        if array.size(aLQ) > 500:
            method_call('delete', array.shift(aLQ))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
