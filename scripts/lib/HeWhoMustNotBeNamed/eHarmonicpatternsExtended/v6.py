"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, math, na, script
from typing import Protocol, Any


__all__ = ['getSupportedPatterns', 'get_projection_range', 'get_prz_range', 'get_prz_range_xad', 'isHarmonicPattern', 'isHarmonicProjection']


class _ProtocolGetsupportedpatterns(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetPrzRange(Protocol):
    def __call__(self, x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0) -> Any: ...


class _ProtocolGetPrzRangeXad(Protocol):
    def __call__(self, x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0) -> Any: ...


class _ProtocolGetProjectionRange(Protocol):
    def __call__(self, x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0) -> Any: ...


class _ProtocolIsharmonicpattern(Protocol):
    def __call__(self, x: float, a: float, b: float, c: float, d: float, flags: list[bool], defaultEnabled: bool = True, errorPercent: int = 8) -> Any: ...


class _ProtocolIsharmonicprojection(Protocol):
    def __call__(self, x: float, a: float, b: float, c: float, flags: list[bool], defaultEnabled: bool = True, errorPercent: int = 8) -> Any: ...


getSupportedPatterns: _ProtocolGetsupportedpatterns = Exported()
get_prz_range: _ProtocolGetPrzRange = Exported()
get_prz_range_xad: _ProtocolGetPrzRangeXad = Exported()
get_projection_range: _ProtocolGetProjectionRange = Exported()
isHarmonicPattern: _ProtocolIsharmonicpattern = Exported()
isHarmonicProjection: _ProtocolIsharmonicprojection = Exported()


@script.library('eHarmonicpatternsExtended')
def main():
    def isInRange(ratio, min, max):
        return ratio >= min and ratio <= max

    def getadj(p1, p2, adj):
        return math.max(0, p2 - (p2 - p1) * adj)

    @overload
    def getrange(p1: float, p2: float, min: float, max: float, ep: float, adjs: float, adje: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int):
        returnval: bool = False
        if array.get(pArray, index):
            eamin = (100 - (ep + adjs)) / 100
            eamax = (100 + ep + adje) / 100
            start = getadj(p1, p2, min * eamin)
            end = getadj(p1, p2, max * eamax)
            array.set(startRange, index, start)
            array.set(endRange, index, end)
            returnval = True
        return returnval

    @overload
    def getrange(p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int):
        returnval: bool = False
        if array.get(pArray, index):
            start1 = getadj(p1, p2, min1)
            end1 = getadj(p1, p2, max1)
            start2 = getadj(p3, p4, min2)
            end2 = getadj(p3, p4, max2)
            start = math.min(start1, start2) if start1 > end1 else math.max(start1, start2)
            end = math.max(end1, end2) if start1 > end1 else math.min(end1, end2)
            d1 = 1 if start1 > end1 else -1
            d2 = 1 if start2 > end2 else -1
            d = 1 if start > end else -1
            if d1 == d2 and d == d1 and (start > 0 or end > 0):
                returnval = True
                array.set(startRange, index, start)
                array.set(endRange, index, end)
            else:
                array.set(pArray, index, False)
        return returnval

    @overload
    def getrange(p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, ep1: float, ep2: float, adjs: float, adje: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int):
        returnval: bool = False
        if array.get(pArray, index):
            eamin1 = (100 - (ep1 + adjs)) / 100
            eamax1 = (100 + ep1 + adje) / 100
            eamin2 = (100 - (ep2 + adjs)) / 100
            eamax2 = (100 + ep2 + adje) / 100
            start1 = getadj(p1, p2, min1 * eamin1)
            end1 = getadj(p1, p2, max1 * eamax1)
            start2 = getadj(p3, p4, min2 * eamin2)
            end2 = getadj(p3, p4, max2 * eamax2)
            start = math.min(start1, start2) if start1 > end1 else math.max(start1, start2)
            end = math.max(end1, end2) if start1 > end1 else math.min(end1, end2)
            d1 = 1 if start1 > end1 else -1
            d2 = 1 if start2 > end2 else -1
            d = 1 if start > end else -1
            if d1 == d2 and d == d1 and (start > 0 or end > 0):
                returnval = True
                array.set(startRange, index, start)
                array.set(endRange, index, end)
            else:
                array.set(pArray, index, False)
        return returnval

    def isCypherProjection(xabRatio: float, axcRatio: float, err_min: float = 0.92, err_max: float = 1.08, enable: bool = True):
        xabMin = 0.382 * err_min
        xabMax = 0.618 * err_max
        axcMin = 1.13 * err_min
        axcMax = 1.414 * err_max
        isInRange_1 = isInRange(xabRatio, xabMin, xabMax)
        isInRange_2 = isInRange(axcRatio, axcMin, axcMax)
        return enable and isInRange_1 and isInRange_2

    def isCypherPattern(xabRatio: float, axcRatio: float, xcdRatio: float, err_min: float = 0.92, err_max: float = 1.08, enable = True):
        xabMin = 0.382 * err_min
        xabMax = 0.618 * err_max
        axcMin = 1.13 * err_min
        axcMax = 1.414 * err_max
        xcdMin = 0.786 * err_min
        xcdMax = 0.786 * err_max
        isInRange_1 = isInRange(xabRatio, xabMin, xabMax)
        isInRange_2 = isInRange(axcRatio, axcMin, axcMax)
        isInRange_3 = isInRange(xcdRatio, xcdMin, xcdMax)
        return enable and isInRange_1 and isInRange_2 and isInRange_3

    def getNumberOfSupportedPatterns():
        return 25

    @export
    def getSupportedPatterns():
        patternLabelArray: list[str] = array.new_string()
        array.push(patternLabelArray, 'Gartley')
        array.push(patternLabelArray, 'Crab')
        array.push(patternLabelArray, 'DeepCrab')
        array.push(patternLabelArray, 'Bat')
        array.push(patternLabelArray, 'Butterfly')
        array.push(patternLabelArray, 'Shark')
        array.push(patternLabelArray, 'Cypher')
        array.push(patternLabelArray, 'NenStar')
        array.push(patternLabelArray, 'Anti NenStar')
        array.push(patternLabelArray, 'Anti Shark')
        array.push(patternLabelArray, 'Anti Cypher')
        array.push(patternLabelArray, 'Anti Crab')
        array.push(patternLabelArray, 'Anti Butterfly')
        array.push(patternLabelArray, 'Anti Bat')
        array.push(patternLabelArray, 'Anti Gartley')
        array.push(patternLabelArray, 'Navarro200')
        array.push(patternLabelArray, 'Five Zero')
        array.push(patternLabelArray, 'Three Drives')
        array.push(patternLabelArray, 'White Swan')
        array.push(patternLabelArray, 'Black Swan')
        array.push(patternLabelArray, 'Sea Pony')
        array.push(patternLabelArray, 'Leonardo')
        array.push(patternLabelArray, '121')
        array.push(patternLabelArray, 'Snorm')
        array.push(patternLabelArray, 'Total')
        return patternLabelArray

    def scan_xab(xabRatio: float, err_min: float, err_max: float, patternArray: list[bool]):
        __block_result__ = na
        if array.includes(patternArray, True):
            is_0_382_to_0_618 = isInRange(xabRatio, 0.382 * err_min, 0.618 * err_max)
            is_0_446_to_0_618 = isInRange(xabRatio, 0.446 * err_min, 0.618 * err_max)
            is_0_500_to_0_786 = isInRange(xabRatio, 0.5 * err_min, 0.786 * err_max)
            is_0_618_to_0_786 = isInRange(xabRatio, 0.618 * err_min, 0.786 * err_max)
            is_1_270_to_1_618 = isInRange(xabRatio, 1.27 * err_min, 1.618 * err_max)
            isInRange_1 = isInRange(xabRatio, 0.618 * err_min, 0.618 * err_max)
            array.set(patternArray, 0, array.get(patternArray, 0) and isInRange_1)
            array.set(patternArray, 1, array.get(patternArray, 1) and cast_bool(is_0_382_to_0_618))
            isInRange_2 = isInRange(xabRatio, 0.886 * err_min, 0.886 * err_max)
            array.set(patternArray, 2, array.get(patternArray, 2) and isInRange_2)
            isInRange_3 = isInRange(xabRatio, 0.382 * err_min, 0.5 * err_max)
            array.set(patternArray, 3, array.get(patternArray, 3) and isInRange_3)
            isInRange_4 = isInRange(xabRatio, 0.786 * err_min, 0.786 * err_max)
            array.set(patternArray, 4, array.get(patternArray, 4) and isInRange_4)
            array.set(patternArray, 5, array.get(patternArray, 5) and cast_bool(is_0_446_to_0_618))
            array.set(patternArray, 6, array.get(patternArray, 6) and cast_bool(is_0_382_to_0_618))
            array.set(patternArray, 7, array.get(patternArray, 7) and cast_bool(is_0_382_to_0_618))
            array.set(patternArray, 8, array.get(patternArray, 8) and cast_bool(is_0_500_to_0_786))
            array.set(patternArray, 9, array.get(patternArray, 9) and cast_bool(is_0_446_to_0_618))
            array.set(patternArray, 10, array.get(patternArray, 10) and cast_bool(is_0_500_to_0_786))
            isInRange_5 = isInRange(xabRatio, 0.276 * err_min, 0.446 * err_max)
            array.set(patternArray, 11, array.get(patternArray, 11) and isInRange_5)
            array.set(patternArray, 12, array.get(patternArray, 12) and cast_bool(is_0_382_to_0_618))
            array.set(patternArray, 13, array.get(patternArray, 13) and cast_bool(is_0_382_to_0_618))
            array.set(patternArray, 14, array.get(patternArray, 14) and cast_bool(is_0_618_to_0_786))
            isInRange_6 = isInRange(xabRatio, 0.382 * err_min, 0.786 * err_max)
            array.set(patternArray, 15, array.get(patternArray, 15) and isInRange_6)
            array.set(patternArray, 16, array.get(patternArray, 16) and cast_bool(is_1_270_to_1_618))
            isInRange_7 = isInRange(xabRatio, 0.618 * err_min, 0.786 * err_max)
            array.set(patternArray, 17, array.get(patternArray, 17) and isInRange_7)
            isInRange_8 = isInRange(xabRatio, 0.382 * err_min, 0.786 * err_max)
            array.set(patternArray, 18, array.get(patternArray, 18) and isInRange_8)
            isInRange_9 = isInRange(xabRatio, 1.382 * err_min, 2.618 * err_max)
            array.set(patternArray, 19, array.get(patternArray, 19) and isInRange_9)
            isInRange_10 = isInRange(xabRatio, 0.128 * err_min, 3.618 * err_max)
            array.set(patternArray, 20, array.get(patternArray, 20) and isInRange_10)
            isInRange_11 = isInRange(xabRatio, 0.5 * err_min, 0.5 * err_max)
            array.set(patternArray, 21, array.get(patternArray, 21) and isInRange_11)
            isInRange_12 = isInRange(xabRatio, 0.5 * err_min, 0.786 * err_max)
            array.set(patternArray, 22, array.get(patternArray, 22) and isInRange_12)
            isInRange_13 = isInRange(xabRatio, 0.9 * err_min, 1.1 * err_max)
            array.set(patternArray, 23, array.get(patternArray, 23) and isInRange_13)
            isInRange_14 = isInRange(xabRatio, 0.236 * err_min, 0.786 * err_max)
            __block_result__ = array.set(patternArray, 24, array.get(patternArray, 24) and isInRange_14)
        return __block_result__

    def scan_abc_axc(abcRatio: float, axcRatio: float, err_min: float, err_max: float, patternArray: list[bool]):
        __block_result_1__ = na
        if array.includes(patternArray, True):
            is_0_382_to_0_886 = isInRange(abcRatio, 0.382 * err_min, 0.886 * err_max)
            is_0_467_to_0_707 = isInRange(abcRatio, 0.467 * err_min, 0.707 * err_max)
            is_1_128_to_2_618 = isInRange(abcRatio, 1.128 * err_min, 2.618 * err_max)
            array.set(patternArray, 0, array.get(patternArray, 0) and cast_bool(is_0_382_to_0_886))
            array.set(patternArray, 1, array.get(patternArray, 1) and cast_bool(is_0_382_to_0_886))
            array.set(patternArray, 2, array.get(patternArray, 2) and cast_bool(is_0_382_to_0_886))
            array.set(patternArray, 3, array.get(patternArray, 3) and cast_bool(is_0_382_to_0_886))
            array.set(patternArray, 4, array.get(patternArray, 4) and cast_bool(is_0_382_to_0_886))
            isInRange_1 = isInRange(abcRatio, 1.13 * err_min, 1.618 * err_max)
            array.set(patternArray, 5, array.get(patternArray, 5) and isInRange_1)
            isInRange_2 = isInRange(axcRatio, 1.13 * err_min, 1.414 * err_max)
            array.set(patternArray, 6, array.get(patternArray, 6) and isInRange_2)
            isInRange_3 = isInRange(abcRatio, 1.414 * err_min, 2.14 * err_max)
            array.set(patternArray, 7, array.get(patternArray, 7) and isInRange_3)
            array.set(patternArray, 8, array.get(patternArray, 8) and cast_bool(is_0_467_to_0_707))
            isInRange_4 = isInRange(abcRatio, 0.618 * err_min, 0.886 * err_max)
            array.set(patternArray, 9, array.get(patternArray, 9) and isInRange_4)
            array.set(patternArray, 10, array.get(patternArray, 10) and cast_bool(is_0_467_to_0_707))
            array.set(patternArray, 11, array.get(patternArray, 11) and cast_bool(is_1_128_to_2_618))
            array.set(patternArray, 12, array.get(patternArray, 12) and cast_bool(is_1_128_to_2_618))
            array.set(patternArray, 13, array.get(patternArray, 13) and cast_bool(is_1_128_to_2_618))
            array.set(patternArray, 14, array.get(patternArray, 14) and cast_bool(is_1_128_to_2_618))
            isInRange_5 = isInRange(abcRatio, 0.886 * err_min, 1.127 * err_max)
            array.set(patternArray, 15, array.get(patternArray, 15) and isInRange_5)
            isInRange_6 = isInRange(abcRatio, 1.168 * err_min, 2.24 * err_max)
            array.set(patternArray, 16, array.get(patternArray, 16) and isInRange_6)
            isInRange_7 = isInRange(abcRatio, 1.272 * err_min, 1.618 * err_max)
            array.set(patternArray, 17, array.get(patternArray, 17) and isInRange_7)
            isInRange_8 = isInRange(abcRatio, 2.0 * err_min, 4.237 * err_max)
            array.set(patternArray, 18, array.get(patternArray, 18) and isInRange_8)
            isInRange_9 = isInRange(abcRatio, 0.236 * err_min, 0.5 * err_max)
            array.set(patternArray, 19, array.get(patternArray, 19) and isInRange_9)
            isInRange_10 = isInRange(abcRatio, 0.382 * err_min, 0.5 * err_max)
            array.set(patternArray, 20, array.get(patternArray, 20) and isInRange_10)
            isInRange_11 = isInRange(abcRatio, 0.382 * err_min, 0.886 * err_max)
            array.set(patternArray, 21, array.get(patternArray, 21) and isInRange_11)
            isInRange_12 = isInRange(abcRatio, 1.128 * err_min, 3.618 * err_max)
            array.set(patternArray, 22, array.get(patternArray, 22) and isInRange_12)
            isInRange_13 = isInRange(abcRatio, 0.9 * err_min, 1.1 * err_max)
            array.set(patternArray, 23, array.get(patternArray, 23) and isInRange_13)
            isInRange_14 = isInRange(abcRatio, 0.382 * err_min, 2.618 * err_max)
            __block_result_1__ = array.set(patternArray, 24, array.get(patternArray, 24) and isInRange_14)
        return __block_result_1__

    def scan_bcd(bcdRatio: float, err_min: float, err_max: float, patternArray: list[bool]):
        __block_result_2__ = na
        if array.includes(patternArray, True):
            is_1_618_to_2_618 = isInRange(bcdRatio, 1.618 * err_min, 2.618 * err_max)
            is_1_272_to_1_618 = isInRange(bcdRatio, 1.272 * err_min, 1.618 * err_max)
            is_1_272_to_2_000 = isInRange(bcdRatio, 1.272 * err_min, 2.0 * err_max)
            array.set(patternArray, 0, array.get(patternArray, 0) and is_1_272_to_1_618)
            isInRange_1 = isInRange(bcdRatio, 2.24 * err_min, 3.618 * err_max)
            array.set(patternArray, 1, array.get(patternArray, 1) and isInRange_1)
            isInRange_2 = isInRange(bcdRatio, 2.0 * err_min, 3.618 * err_max)
            array.set(patternArray, 2, array.get(patternArray, 2) and isInRange_2)
            array.set(patternArray, 3, array.get(patternArray, 3) and is_1_618_to_2_618)
            array.set(patternArray, 4, array.get(patternArray, 4) and is_1_618_to_2_618)
            isInRange_3 = isInRange(bcdRatio, 1.618 * err_min, 2.236 * err_max)
            array.set(patternArray, 5, array.get(patternArray, 5) and isInRange_3)
            array.set(patternArray, 7, array.get(patternArray, 7) and is_1_272_to_2_000)
            array.set(patternArray, 8, array.get(patternArray, 8) and is_1_618_to_2_618)
            array.set(patternArray, 9, array.get(patternArray, 9) and is_1_618_to_2_618)
            array.set(patternArray, 10, array.get(patternArray, 10) and is_1_618_to_2_618)
            array.set(patternArray, 11, array.get(patternArray, 11) and is_1_618_to_2_618)
            isInRange_4 = isInRange(bcdRatio, 1.272 * err_min, 1.272 * err_max)
            array.set(patternArray, 12, array.get(patternArray, 12) and isInRange_4)
            isInRange_5 = isInRange(bcdRatio, 2.0 * err_min, 2.618 * err_max)
            array.set(patternArray, 13, array.get(patternArray, 13) and isInRange_5)
            isInRange_6 = isInRange(bcdRatio, 1.618 * err_min, 1.618 * err_max)
            array.set(patternArray, 14, array.get(patternArray, 14) and isInRange_6)
            isInRange_7 = isInRange(bcdRatio, 0.886 * err_min, 3.618 * err_max)
            array.set(patternArray, 15, array.get(patternArray, 15) and isInRange_7)
            isInRange_8 = isInRange(bcdRatio, 0.5 * err_min, 0.5 * err_max)
            array.set(patternArray, 16, array.get(patternArray, 16) and isInRange_8)
            isInRange_9 = isInRange(bcdRatio, 0.618 * err_min, 0.786 * err_max)
            array.set(patternArray, 17, array.get(patternArray, 17) and isInRange_9)
            isInRange_10 = isInRange(bcdRatio, 0.5 * err_min, 0.886 * err_max)
            array.set(patternArray, 18, array.get(patternArray, 18) and isInRange_10)
            isInRange_11 = isInRange(bcdRatio, 1.128 * err_min, 2.0 * err_max)
            array.set(patternArray, 19, array.get(patternArray, 19) and isInRange_11)
            isInRange_12 = isInRange(bcdRatio, 1.618 * err_min, 2.618 * err_max)
            array.set(patternArray, 20, array.get(patternArray, 20) and isInRange_12)
            isInRange_13 = isInRange(bcdRatio, 1.128 * err_min, 2.618 * err_max)
            array.set(patternArray, 21, array.get(patternArray, 21) and isInRange_13)
            isInRange_14 = isInRange(bcdRatio, 0.382 * err_min, 0.786 * err_max)
            array.set(patternArray, 22, array.get(patternArray, 22) and isInRange_14)
            isInRange_15 = isInRange(bcdRatio, 0.9 * err_min, 1.1 * err_max)
            array.set(patternArray, 23, array.get(patternArray, 23) and isInRange_15)
            isInRange_16 = isInRange(bcdRatio, 1.272 * err_min, 4.236 * err_max)
            __block_result_2__ = array.set(patternArray, 24, array.get(patternArray, 24) and isInRange_16)
        return __block_result_2__

    def scan_xad_xcd(xadRatio: float, xcdRatio: float, err_min: float, err_max: float, patternArray: list[bool]):
        __block_result_3__ = na
        if array.includes(patternArray, True):
            is_1_618_to_1_618 = isInRange(xadRatio, 1.618 * err_min, 1.618 * err_max)
            is_0_786_to_0_786 = isInRange(xadRatio, 0.786 * err_min, 0.786 * err_max)
            is_0_886_to_0_886 = isInRange(xadRatio, 0.886 * err_min, 0.886 * err_max)
            is_1_272_to_1_272 = isInRange(xadRatio, 1.272 * err_min, 1.272 * err_max)
            array.set(patternArray, 0, array.get(patternArray, 0) and is_0_786_to_0_786)
            array.set(patternArray, 1, array.get(patternArray, 1) and is_1_618_to_1_618)
            array.set(patternArray, 2, array.get(patternArray, 2) and is_1_618_to_1_618)
            array.set(patternArray, 3, array.get(patternArray, 3) and is_0_886_to_0_886)
            isInRange_1 = isInRange(xadRatio, 1.272, 1.618)
            array.set(patternArray, 4, array.get(patternArray, 4) and isInRange_1)
            array.set(patternArray, 5, array.get(patternArray, 5) and is_0_886_to_0_886)
            isInRange_2 = isInRange(xcdRatio, 0.786 * err_min, 0.786 * err_max)
            array.set(patternArray, 6, array.get(patternArray, 6) and isInRange_2)
            array.set(patternArray, 7, array.get(patternArray, 7) and is_1_272_to_1_272)
            array.set(patternArray, 8, array.get(patternArray, 8) and is_0_786_to_0_786)
            isInRange_3 = isInRange(xadRatio, 1.13 * err_min, 1.13 * err_max)
            array.set(patternArray, 9, array.get(patternArray, 9) and isInRange_3)
            array.set(patternArray, 10, array.get(patternArray, 10) and is_1_272_to_1_272)
            isInRange_4 = isInRange(xadRatio, 0.618 * err_min, 0.618 * err_max)
            array.set(patternArray, 11, array.get(patternArray, 11) and isInRange_4)
            isInRange_5 = isInRange(xadRatio, 0.618 * err_min, 0.786 * err_max)
            array.set(patternArray, 12, array.get(patternArray, 12) and isInRange_5)
            isInRange_6 = isInRange(xadRatio, 1.128 * err_min, 1.128 * err_max)
            array.set(patternArray, 13, array.get(patternArray, 13) and isInRange_6)
            isInRange_7 = isInRange(xadRatio, 1.272 * err_min, 1.272 * err_max)
            array.set(patternArray, 14, array.get(patternArray, 14) and isInRange_7)
            isInRange_8 = isInRange(xadRatio, 0.886, 1.127)
            array.set(patternArray, 15, array.get(patternArray, 15) and isInRange_8)
            isInRange_9 = isInRange(xadRatio, 0.886, 1.13)
            array.set(patternArray, 16, array.get(patternArray, 16) and isInRange_9)
            isInRange_10 = isInRange(xadRatio, 0.13, 0.886)
            array.set(patternArray, 17, array.get(patternArray, 17) and isInRange_10)
            isInRange_11 = isInRange(xadRatio, 0.236, 0.886)
            array.set(patternArray, 18, array.get(patternArray, 18) and isInRange_11)
            isInRange_12 = isInRange(xadRatio, 1.128, 2.618)
            array.set(patternArray, 19, array.get(patternArray, 19) and isInRange_12)
            isInRange_13 = isInRange(xadRatio, 0.618, 3.618)
            array.set(patternArray, 20, array.get(patternArray, 20) and isInRange_13)
            isInRange_14 = isInRange(xadRatio, 0.786 * err_min, 0.786 * err_max)
            array.set(patternArray, 21, array.get(patternArray, 21) and isInRange_14)
            isInRange_15 = isInRange(xadRatio, 0.382, 0.786)
            array.set(patternArray, 22, array.get(patternArray, 22) and isInRange_15)
            isInRange_16 = isInRange(xadRatio, 0.618, 1.618)
            array.set(patternArray, 23, array.get(patternArray, 23) and isInRange_16)
            isInRange_17 = isInRange(xadRatio, 0.618, 1.618)
            __block_result_3__ = array.set(patternArray, 24, array.get(patternArray, 24) and isInRange_17)
        return __block_result_3__

    @export
    def get_prz_range(x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0):
        startRange: list[float] = array.new_float(array.size(patternArray), na)
        endRange: list[float] = array.new_float(array.size(patternArray), na)
        if array.includes(patternArray, True):
            getrange(x, a, 0.786, 0.786, b, c, 1.272, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 0)
            getrange(x, a, 1.618, 1.618, b, c, 2.24, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 1)
            getrange(x, a, 1.618, 1.618, b, c, 2.0, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 2)
            getrange(x, a, 0.886, 0.886, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 3)
            getrange(x, a, 1.272, 1.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 4)
            getrange(x, a, 0.886, 0.886, b, c, 1.618, 2.236, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 5)
            getrange(x, c, 0.786, 0.786, x, c, 0.786, 0.786, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 6)
            getrange(x, a, 1.272, 1.272, b, c, 1.272, 2.0, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 7)
            getrange(x, a, 0.786, 0.786, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 8)
            getrange(x, a, 1.13, 1.13, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 9)
            getrange(x, a, 1.272, 1.272, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 10)
            getrange(x, a, 0.618, 0.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 11)
            getrange(x, a, 0.618, 0.786, b, c, 1.272, 1.272, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 12)
            getrange(x, a, 1.128, 1.128, b, c, 2.0, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 13)
            getrange(x, a, 1.272, 1.272, b, c, 1.618, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 14)
            getrange(x, a, 0.886, 1.127, b, c, 0.886, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 15)
            getrange(x, a, 0.886, 1.13, b, c, 0.5, 0.5, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 16)
            getrange(x, a, 0.13, 1.886, b, c, 0.618, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 17)
            getrange(x, a, 0.236, 0.886, b, c, 0.5, 0.886, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 18)
            getrange(x, a, 1.128, 2.618, b, c, 1.128, 2.0, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 19)
            getrange(x, a, 0.618, 3.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 20)
            getrange(x, a, 0.786, 0.786, b, c, 1.128, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 21)
            getrange(x, a, 0.382, 0.786, b, c, 0.382, 0.786, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 22)
            getrange(x, a, 0.618, 1.618, b, c, 0.9, 1.1, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 23)
            getrange(x, a, 0.618, 1.618, b, c, 1.272, 4.236, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 24)
        dStart = array.min(startRange) if b > c else array.max(startRange)
        dEnd = array.max(endRange) if b > c else array.min(endRange)
        return (dStart, dEnd)

    @export
    def get_prz_range_xad(x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0):
        startRange: list[float] = array.new_float(array.size(patternArray), na)
        endRange: list[float] = array.new_float(array.size(patternArray), na)
        if array.includes(patternArray, True):
            getrange(x, a, 0.786, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 0)
            getrange(x, a, 1.618, 1.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 1)
            getrange(x, a, 1.618, 1.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 2)
            getrange(x, a, 0.886, 0.886, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 3)
            getrange(x, a, 1.272, 1.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 4)
            getrange(x, a, 0.886, 0.886, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 5)
            getrange(x, c, 0.786, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 6)
            getrange(x, a, 1.272, 1.272, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 7)
            getrange(x, a, 0.786, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 8)
            getrange(x, a, 1.13, 1.13, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 9)
            getrange(x, a, 1.272, 1.272, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 10)
            getrange(x, a, 0.618, 0.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 11)
            getrange(x, a, 0.618, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 12)
            getrange(x, a, 1.128, 1.128, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 13)
            getrange(x, a, 1.272, 1.272, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 14)
            getrange(x, a, 0.886, 1.127, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 15)
            getrange(x, a, 0.886, 1.13, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 16)
            getrange(x, a, 0.13, 1.886, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 17)
            getrange(x, a, 0.236, 0.886, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 18)
            getrange(x, a, 1.128, 2.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 19)
            getrange(x, a, 0.618, 3.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 20)
            getrange(x, a, 0.786, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 21)
            getrange(x, a, 0.382, 0.786, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 22)
            getrange(x, a, 0.618, 1.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 23)
            getrange(x, a, 0.618, 1.618, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 24)
        dStart = array.min(startRange) if b > c else array.max(startRange)
        dEnd = array.max(endRange) if b > c else array.min(endRange)
        return (dStart, dEnd)

    @export
    def get_projection_range(x: float, a: float, b: float, c: float, patternArray: list[bool], errorPercent: float = 8, start_adj: float = 0, end_adj: float = 0):
        startRange: list[float] = array.new_float(array.size(patternArray), na)
        endRange: list[float] = array.new_float(array.size(patternArray), na)
        if array.includes(patternArray, True):
            getrange(x, a, 0.786, 0.786, b, c, 1.272, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 0)
            getrange(x, a, 1.618, 1.618, b, c, 2.24, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 1)
            getrange(x, a, 1.618, 1.618, b, c, 2.0, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 2)
            getrange(x, a, 0.886, 0.886, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 3)
            getrange(x, a, 1.272, 1.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 4)
            getrange(x, a, 0.886, 0.886, b, c, 1.618, 2.236, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 5)
            getrange(x, c, 0.786, 0.786, x, c, 0.786, 0.786, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 6)
            getrange(x, a, 1.272, 1.272, b, c, 1.272, 2.0, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 7)
            getrange(x, a, 0.786, 0.786, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 8)
            getrange(x, a, 1.13, 1.13, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 9)
            getrange(x, a, 1.272, 1.272, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 10)
            getrange(x, a, 0.618, 0.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 11)
            getrange(x, a, 0.618, 0.786, b, c, 1.272, 1.272, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 12)
            getrange(x, a, 1.128, 1.128, b, c, 2.0, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 13)
            getrange(x, a, 1.272, 1.272, b, c, 1.618, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 14)
            getrange(x, a, 0.886, 1.127, b, c, 0.886, 3.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 15)
            getrange(x, a, 0.886, 1.13, b, c, 0.5, 0.5, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 16)
            getrange(x, a, 0.13, 1.886, b, c, 0.618, 1.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 17)
            getrange(x, a, 0.236, 0.886, b, c, 0.5, 0.886, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 18)
            getrange(x, a, 1.128, 2.618, b, c, 1.128, 2.0, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 19)
            getrange(x, a, 0.618, 3.618, b, c, 1.618, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 20)
            getrange(x, a, 0.786, 0.786, b, c, 1.128, 2.618, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 21)
            getrange(x, a, 0.382, 0.786, b, c, 0.382, 0.786, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 22)
            getrange(x, a, 0.618, 1.618, b, c, 0.9, 1.1, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 23)
            getrange(x, a, 0.618, 1.618, b, c, 1.272, 4.236, errorPercent, errorPercent, start_adj, end_adj, patternArray, startRange, endRange, 24)
        return (startRange, endRange)

    @export
    def isHarmonicPattern(x: float, a: float, b: float, c: float, d: float, flags: list[bool], defaultEnabled: bool = True, errorPercent: int = 8):
        numberOfPatterns = getNumberOfSupportedPatterns()
        err_min = (100 - errorPercent) / 100
        err_max = (100 + errorPercent) / 100
        xabRatio = (b - a) / (x - a)
        abcRatio = (c - b) / (a - b)
        axcRatio = (c - x) / (a - x)
        bcdRatio = (d - c) / (b - c)
        xadRatio = (d - a) / (x - a)
        xcdRatio = (d - c) / (x - c)
        patternArray: list[bool] = array.new_bool()
        for i in pine_range(0, numberOfPatterns - 1, 1):
            array.push(patternArray, array.get(flags, i) if array.size(flags) > i else defaultEnabled)
        scan_xab(xabRatio, err_min, err_max, patternArray)
        scan_abc_axc(abcRatio, axcRatio, err_min, err_max, patternArray)
        scan_bcd(bcdRatio, err_min, err_max, patternArray)
        scan_xad_xcd(xadRatio, xcdRatio, err_min, err_max, patternArray)
        return patternArray

    @export
    def isHarmonicProjection(x: float, a: float, b: float, c: float, flags: list[bool], defaultEnabled: bool = True, errorPercent: int = 8):
        numberOfPatterns = getNumberOfSupportedPatterns()
        err_min = (100 - errorPercent) / 100
        err_max = (100 + errorPercent) / 100
        xabRatio = (b - a) / (x - a)
        abcRatio = (c - b) / (a - b)
        axcRatio = (c - x) / (a - x)
        patternArray: list[bool] = array.new_bool()
        for i in pine_range(0, numberOfPatterns - 1, 1):
            array.push(patternArray, array.get(flags, i) if array.size(flags) > i else defaultEnabled)
        scan_xab(xabRatio, err_min, err_max, patternArray)
        scan_abc_axc(abcRatio, axcRatio, err_min, err_max, patternArray)
        return patternArray


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
