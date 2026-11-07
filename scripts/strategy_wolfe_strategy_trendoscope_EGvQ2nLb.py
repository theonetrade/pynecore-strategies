"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, close, color, extend, high, input, line, low, math,
    matrix, na, script, strategy, string
)
from pynecore.types import Line, Matrix, NA, Persistent
import lib.HeWhoMustNotBeNamed._matrix.v5 as ma
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa
import lib.HeWhoMustNotBeNamed.rzigzag.v10 as zigzag
import lib.HeWhoMustNotBeNamed.strategy.v3 as st

capital: float = 1000.0


@script.strategy('Wolfe Strategy [Trendoscope]', shorttitle='WS[Trendoscope]', overlay=True, initial_capital=capital, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, pyramiding=10, commission_value=0.05, close_entries_rule='ANY', max_lines_count=500, max_labels_count=500, max_boxes_count=500, use_bar_magnifier=False, margin_long=100, margin_short=100, close_by_id=True)
def main(
    tradeDirection=input.string(strategy.direction.long, 'Trade Direction', options=(strategy.direction.long, strategy.direction.short), group='Trade Settings', tooltip='Use this to filter only long or short trades'),
    minRiskReward=input.float(1.0, 'Minimum RR', group='Trade Settings', minval=0.5, step=0.1, tooltip='Minimum RR to place trade'),
    theme=input.string('Dark', title='Theme', options=('Light', 'Dark'), group='Generic', tooltip='Chart theme settings. Line and label colors are generted based on the theme settings. If dark theme is selected, ' + 'lighter colors are used and if light theme is selected, darker colors are used.'),
    avoidOverlap=input.bool(False, 'Suppress Overlap', group='Generic', tooltip='Avoids plotting wedge if there is an existing wedge at starting point. This does not avoid nesting wedges (Wedge within wedge)'),
    drawZigzag=input.bool(True, 'Draw Zigzag', group='Generic', tooltip='Draw zigzag lines and mark pivots within wedge'),
    zigzagLength=input.int(8, step=5, minval=3, title='Length', group='Zigzag', tooltip='Zigzag length'),
    zigzagDepth=input.int(250, step=50, minval=50, title='Depth', group='Zigzag', tooltip='Zigzag depth for recursive search'),
    minLevel=input.int(0, 'Min Level', group='Zigzag', minval=0, tooltip='Min Level on recursive zigzag to calculate Wolfe')
):
    maxPatternsLive: int = 10
    idArray: Persistent[list[int]] = array.from_items(1)
    themeColors: Persistent = array.from_items(color.rgb(251, 244, 109), color.rgb(141, 186, 81), color.rgb(74, 159, 245), color.rgb(255, 153, 140), color.rgb(255, 149, 0), color.rgb(0, 234, 211), color.rgb(167, 153, 183), color.rgb(255, 210, 113), color.rgb(119, 217, 112), color.rgb(95, 129, 228), color.rgb(235, 146, 190), color.rgb(198, 139, 89), color.rgb(200, 149, 149), color.rgb(196, 182, 182), color.rgb(255, 190, 15), color.rgb(192, 226, 24), color.rgb(153, 140, 235), color.rgb(206, 31, 107), color.rgb(251, 54, 64), color.rgb(194, 255, 217), color.rgb(255, 219, 197), color.rgb(121, 180, 183)) if theme == 'Dark' else array.from_items(color.rgb(61, 86, 178), color.rgb(57, 163, 136), color.rgb(250, 30, 14), color.rgb(169, 51, 58), color.rgb(225, 87, 138), color.rgb(62, 124, 23), color.rgb(244, 164, 66), color.rgb(134, 72, 121), color.rgb(113, 159, 176), color.rgb(170, 46, 230), color.rgb(161, 37, 104), color.rgb(189, 32, 0), color.rgb(16, 86, 82), color.rgb(200, 92, 92), color.rgb(63, 51, 81), color.rgb(114, 106, 149), color.rgb(171, 109, 35), color.rgb(247, 136, 18), color.rgb(51, 71, 86), color.rgb(12, 123, 147), color.rgb(195, 43, 173))
    maxPatternsReference: int = 10
    pivotBarMatrix: Persistent[Matrix[int]] = matrix.new(initial_value=NA(int))
    patternIdArray: Persistent[list[int]] = array.new_int()
    patternProjections: Persistent[Matrix[Line]] = matrix.new(initial_value=NA(Line))
    patternTradeMatrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
    def wedgeLine(l1StartX, l1StartY, l1EndX, l1EndY, l2StartX, l2StartY, l2EndX, l2EndY, zgColor, lastDir):
        l1t = line.new(l1StartX, l1StartY, l1EndX, l1EndY, color=zgColor, extend=extend.both)
        l2t = line.new(l2StartX, l2StartY, l2EndX, l2EndY, color=zgColor, extend=extend.both)
        startBar = l1StartX
        endBar = l1EndX
        l2Start = line.get_price(l2t, startBar)
        l2End = line.get_price(l2t, endBar)
        line.set_x1(l2t, startBar)
        line.set_y1(l2t, l2Start)
        line.set_x2(l2t, endBar)
        line.set_y2(l2t, l2End)
        l1Diff = l1StartY - l1EndY
        l2Diff = l2Start - l2End
        width = math.abs(endBar - startBar)
        closingEndBar = endBar
        closingEndPrice = l2End
        closingSoon: bool = False
        isContracting = math.abs(l1StartY - l2Start) > math.abs(l1EndY - l2End)
        isNotTriangle = math.sign(l1StartY - l1EndY) == math.sign(l2Start - l2End)
        isWolfeWedge = isContracting and isNotTriangle
        if isWolfeWedge:
            __loop_1__ = pine_loop(endBar, 1)
            while __loop_1__.step(endBar + math.min(500, 2 * width)):
                i = __loop_1__.value
                l1Price = line.get_price(l1t, i)
                l2Price = line.get_price(l2t, i)
                if lastDir * (l1Price - l2Price) <= 0:
                    closingEndBar = i
                    closingSoon = True
                    closingEndPrice = (l1Price + l2Price) / 2
                    break
            if closingSoon:
                line.set_x2(l2t, closingEndBar)
                line.set_y2(l2t, closingEndPrice)
                line.set_x2(l1t, closingEndBar)
                line.set_y2(l1t, closingEndPrice)
        line.set_extend(l1t, extend.none)
        line.set_extend(l2t, extend.none)
        return (l1t, l2t, closingEndBar, closingEndPrice, isWolfeWedge and closingSoon)

    def find_wedge(zigzagmatrix, startIndex):
        _5 = matrix.get(zigzagmatrix, startIndex, 0)
        _5Bar = cast_int(matrix.get(zigzagmatrix, startIndex, 1))
        lastDir = matrix.get(zigzagmatrix, startIndex, 3)
        _4 = matrix.get(zigzagmatrix, startIndex + 1, 0)
        _4Bar = cast_int(matrix.get(zigzagmatrix, startIndex + 1, 1))
        _3 = matrix.get(zigzagmatrix, startIndex + 2, 0)
        _3Bar = cast_int(matrix.get(zigzagmatrix, startIndex + 2, 1))
        _2 = matrix.get(zigzagmatrix, startIndex + 3, 0)
        _2Bar = cast_int(matrix.get(zigzagmatrix, startIndex + 3, 1))
        _1 = matrix.get(zigzagmatrix, startIndex + 4, 0)
        _1Bar = cast_int(matrix.get(zigzagmatrix, startIndex + 4, 1))
        isValidDirection = tradeDirection == strategy.direction.long and lastDir < 0 or (tradeDirection == strategy.direction.short and lastDir > 0)
        __block_result__ = na
        if isValidDirection:
            existingPattern: bool = False
            for i in pine_range(0, matrix.rows(pivotBarMatrix) - 1 if matrix.rows(pivotBarMatrix) > 0 else na, 1):
                commonPivotsCount = (1 if _1Bar == matrix.get(pivotBarMatrix, i, 0) else 0) + (1 if _2Bar == matrix.get(pivotBarMatrix, i, 1) else 0) + (1 if _3Bar == matrix.get(pivotBarMatrix, i, 2) else 0) + (1 if _4Bar == matrix.get(pivotBarMatrix, i, 3) else 0) + (1 if _5Bar == matrix.get(pivotBarMatrix, i, 4) else 0)
                if commonPivotsCount >= 3 or (avoidOverlap and _1Bar >= matrix.get(pivotBarMatrix, i, 0) and (_1Bar <= matrix.get(pivotBarMatrix, i, 4))):
                    existingPattern = True
                    break
            __block_result_1__ = na
            if not existingPattern:
                basicCondition = _2 < math.min(_1, _3, _4, _5) and _5 > math.max(_1, _2, _3, _4) and (_1 < _3) and (_1 > _4) if lastDir > 0 else _2 > math.max(_1, _3, _4, _5) and _5 < math.min(_1, _2, _3, _4) and (_1 > _3) and (_1 < _4)
                __block_result_2__ = na
                if basicCondition:
                    zgColor = array.pop(themeColors)
                    l1t, l2t, closingEndBar, closingEndPrice, isWolfeWedge = wedgeLine(_1Bar, _1, _5Bar, _5, _2Bar, _2, _4Bar, _4, zgColor, lastDir)
                    array.unshift(themeColors, zgColor)
                    delete: bool = True
                    if isWolfeWedge:
                        id = array.get(idArray, 0)
                        array.set(idArray, 0, id + 1)
                        ma.unshift(pivotBarMatrix, array.from_items(_1Bar, _2Bar, _3Bar, _4Bar, _5Bar), maxPatternsReference)
                        pa.unshift(patternIdArray, id, maxPatternsReference)
                        delete = False
                        if drawZigzag:
                            line.new(_1Bar, _1, _2Bar, _2, color=zgColor, extend=extend.none, width=0, style=line.style_dotted)
                            line.new(_2Bar, _2, _3Bar, _3, color=zgColor, extend=extend.none, width=0, style=line.style_dotted)
                            line.new(_3Bar, _3, _4Bar, _4, color=zgColor, extend=extend.none, width=0, style=line.style_dotted)
                            line.new(_4Bar, _4, _5Bar, _5, color=zgColor, extend=extend.none, width=0, style=line.style_dotted)
                        lproj = line.new(_1Bar, _1, _4Bar, _4, color=zgColor, extend=extend.right, width=0, style=line.style_dashed)
                        lProjEndPrice = line.get_price(lproj, closingEndBar)
                        line.set_x2(lproj, closingEndBar)
                        line.set_y2(lproj, lProjEndPrice)
                        line.set_extend(lproj, extend.none)
                        lclose = line.new(closingEndBar, lProjEndPrice, closingEndBar, closingEndPrice, color=zgColor, extend=extend.none, width=0, style=line.style_dashed)
                        ma.unshift(patternProjections, array.from_items(lproj, lclose, l2t), maxPatternsReference)
                        entry = line.get_price(l2t, bar_index + 1)
                        target = lProjEndPrice
                        stop = closingEndPrice
                        ma.unshift(patternTradeMatrix, array.from_items(entry, stop, target, 0), maxPatternsReference)
                        rr = math.abs(entry - target) / math.abs(entry - stop)
                        dir = 1 if entry > stop else -1
                        if rr >= minRiskReward:
                            st.bracketOrderWithoutLeverage(string.tostring(id), entry, stop, target, close * dir > entry * dir)
                    __block_result_3__ = na
                    if delete:
                        line.delete(l1t)
                        __block_result_3__ = line.delete(l2t)
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def scan_patterns(startIndex, newPivot, zigzagmatrix):
        length = matrix.rows(zigzagmatrix)
        numberOfPivots: int = 5
        __block_result_4__ = na
        if length >= startIndex + 5 and newPivot:
            __block_result_4__ = find_wedge(zigzagmatrix, startIndex)
        return __block_result_4__

    def setup(zigzagLength, zigzagDepth):
        zigzagmatrix, flags = zigzag.zigzag(zigzagLength, array.from_items(high, low), numberOfPivots=zigzagDepth)
        newPivot = array.get(flags, 1)
        doublePivot = array.get(flags, 2)
        __block_result_5__ = na
        if newPivot:
            mlzigzag = zigzagmatrix
            level: int = 1
            __block_result_6__ = na
            while matrix.rows(mlzigzag) >= 5:
                if level >= minLevel:
                    scan_patterns(1, doublePivot, zigzagmatrix)
                    scan_patterns(0, newPivot, zigzagmatrix)
                mlzigzag = zigzag.nextlevel(mlzigzag, zigzagDepth)
                level = level + 1
                __block_result_6__ = level
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    def evaluate():
        __block_result_7__ = na
        for i in pine_range(array.size(patternIdArray) - 1 if array.size(patternIdArray) > 0 else na, 0, 1):
            id = array.get(patternIdArray, i)
            l2t = matrix.get(patternProjections, i, 2)
            entry = matrix.get(patternTradeMatrix, i, 0)
            stop = matrix.get(patternTradeMatrix, i, 1)
            target = matrix.get(patternTradeMatrix, i, 2)
            status = matrix.get(patternTradeMatrix, i, 3)
            rr = math.abs(entry - target) / math.abs(entry - stop)
            dir = 1 if entry > stop else -1
            targetValue = high if dir > 0 else low
            stopValue = low if dir > 0 else high
            newStatus = 1 if status == 0 and targetValue * dir > entry * dir and (rr >= minRiskReward) else status
            __block_result_8__ = na
            if targetValue * dir > target * dir or (newStatus == 1 and close * dir < stop) or (newStatus == 0 and bar_index > line.get_x2(l2t)):
                strategy.cancel(string.tostring(id))
                array.remove(patternIdArray, i)
                matrix.remove_row(pivotBarMatrix, i)
                matrix.remove_row(patternProjections, i)
                matrix.remove_row(patternTradeMatrix, i)
                __block_result_8__ = False
            elif newStatus == 0:
                newEntry = line.get_price(l2t, bar_index + 1)
                newRR = math.abs(entry - target) / math.abs(entry - stop)
                if newRR >= minRiskReward:
                    strategy.cancel(string.tostring(id))
                    st.bracketOrderWithoutLeverage(string.tostring(id), newEntry, stop, target, close * dir > newEntry * dir)
                    matrix.set(patternTradeMatrix, i, 0, newEntry)
                matrix.set(patternTradeMatrix, i, 3, newStatus)
                __block_result_8__ = True
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    setup(zigzagLength, zigzagDepth)
    evaluate()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
