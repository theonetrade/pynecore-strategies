"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, close, color, high, input, label, line, low, math, na,
    script, size, string, ta, yloc
)
from pynecore.types import Color, Label, Line, Persistent, Series
from typing import Protocol, Any


__all__ = ['czigzag', 'drawzigzag', 'zigzag']


class _ProtocolZigzag(Protocol):
    def __call__(self, length: int, numberOfPivots: int = 20, useAlternativeSource: bool = False, source: float = close, oscillatorSource: float = close, oscillatorHighSource: float = high, oscillatorLowSource: float = close, directionBias: int = 1) -> Any: ...


class _ProtocolCzigzag(Protocol):
    def __call__(self, length: int, numberOfPivots: int = 20, highSource: float = high, lowSource: float = low, oscillatorHighSource: float = high, oscillatorLowSource: float = low, directionBias: int = 1) -> Any: ...


class _ProtocolDrawzigzag(Protocol):
    def __call__(self, length: int, numberOfPivots: int = 20, useAlternativeSource: bool = False, source: float = close, linecolor: Color = color.blue, linewidth: int = 1, linestyle: str = line.style_solid, oscillatorSource: float = close, oscillatorHighSource: float = high, oscillatorLowSource: float = close, directionBias: int = 1, showHighLow: bool = False, showRatios: bool = False, showDivergence: bool = False) -> Any: ...


zigzag: _ProtocolZigzag = Exported()
czigzag: _ProtocolCzigzag = Exported()
drawzigzag: _ProtocolDrawzigzag = Exported()


@script.library('zigzag', overlay=True)
def main(
    operation=input.string('Draw Zigzag', 'Operation', options=('Draw Zigzag', 'Get Zigzag'), group='Zigzag', inline='z'),
    zigzagLength=input.int(5, '', group='Zigzag', inline='z'),
    useAlternativeSource=input.bool(False, 'Use Alternative Source', group='Alternate Source', inline='s'),
    source: Series[float] = input.source(close, '', group='Alternate Source', inline='s'),
    useDifferentLineStyle=input.bool(False, 'Use Different Line Style', group='Line Style', inline='l'),
    linecolor=input.color(color.maroon, '', group='Line Style', inline='l'),
    linewidth=input.int(3, '', group='Line Style', inline='l'),
    linestyle=input.string(line.style_dashed, '', options=(line.style_solid, line.style_dashed, line.style_dotted), group='Line Style', inline='l'),
    showHighLow=input.bool(False, 'HHLL', group='Display Labels', inline='lb'),
    showRatios=input.bool(False, 'Ratios', group='Display Labels', inline='lb'),
    showDivergence=input.bool(False, 'Divergence', group='Display Labels', inline='lb')
):
    def add_to_array(arr, val, maxItems):
        array.insert(arr, 0, val)
        __block_result__ = na
        if array.size(arr) > maxItems:
            __block_result__ = array.pop(arr)
        return __block_result__

    def pivots(length, highSource = high, lowSource = low):
        phigh: float = highSource if ta.highestbars(highSource, length) == 0 else na
        plow: float = lowSource if ta.lowestbars(lowSource, length) == 0 else na
        return (phigh, plow, bar_index, bar_index)

    def getSentiment(pDir, oDir, sDir):
        sentiment = (-sDir if sDir == pDir or sDir * 2 == -pDir else sDir * 4) if pDir == oDir else 0 if sDir == pDir or sDir == -oDir else (sDir if math.abs(oDir) > math.abs(pDir) else -sDir) * (2 if sDir == oDir else 3)
        return sentiment

    def getSentimentDetails(sentiment):
        sentimentSymbol = '⬆' if sentiment == 4 else '⬇' if sentiment == -4 else '↗' if sentiment == 3 else '↘' if sentiment == -3 else '⤴' if sentiment == 2 else '⤵' if sentiment == -2 else '⤒' if sentiment == 1 else '⤓' if sentiment == -1 else '▣'
        sentimentColor = color.green if sentiment == 4 else color.red if sentiment == -4 else color.lime if sentiment == 3 else color.orange if sentiment == -3 else color.rgb(202, 224, 13, 0) if sentiment == 2 else color.rgb(250, 128, 114, 0) if sentiment == -2 else color.silver
        sentimentLabel = 'C' if math.abs(sentiment) == 4 else 'H' if math.abs(sentiment) == 3 else 'D' if math.abs(sentiment) == 2 else 'I'
        return (sentimentSymbol, sentimentLabel, sentimentColor)

    def addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, value, bar, dir, numberOfPivots, oscHigh: Series, oscLow: Series, directionBias: Series):
        newDir = dir
        oscDir = dir
        ratio: float = 1.0
        oscillatorSource = oscHigh[bar_index - bar] if dir > 0 else oscLow[bar_index - bar]
        if array.size(zigzagpivots) >= 2:
            lastPoint = array.get(zigzagpivots, 0)
            llastPoint = array.get(zigzagpivots, 1)
            newDir = dir * 2 if dir * value > dir * llastPoint else dir
            ratio = math.round(math.abs(value - lastPoint) / math.abs(llastPoint - lastPoint), 2)
            llastOsc = array.get(zigzagoscillators, 1)
            oscDir = dir * 2 if dir * oscillatorSource > dir * llastOsc else dir
        sentiment = getSentiment(newDir, oscDir, directionBias[bar_index - bar])
        add_to_array(zigzagpivots, value, numberOfPivots)
        add_to_array(zigzagpivotbars, bar, numberOfPivots)
        add_to_array(zigzagpivotdirs, newDir, numberOfPivots)
        add_to_array(zigzagpivotratios, ratio, numberOfPivots)
        add_to_array(zigzagoscillators, oscillatorSource, numberOfPivots)
        add_to_array(zigzagoscillatordirs, oscDir, numberOfPivots)
        add_to_array(zigzagtrendbias, directionBias[bar_index - bar], numberOfPivots)
        return add_to_array(zigzagdivergence, sentiment, numberOfPivots)

    def zigzagcore(phigh, plow, phighbar, plowbar, numberOfPivots, oscHigh, oscLow, directionBias, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence):
        pDir: int = 1
        newZG: bool = False
        doubleZG = phigh and plow
        if array.size(zigzagpivots) >= 1:
            pDir = array.get(zigzagpivotdirs, 0)
            pDir = pDir / 2 if pDir % 2 == 0 else pDir
        if (pDir == 1 and phigh or (pDir == -1 and plow)) and array.size(zigzagpivots) >= 1:
            pivot = array.remove(zigzagpivots, 0)
            pivotbar = array.remove(zigzagpivotbars, 0)
            pivotdir = array.remove(zigzagpivotdirs, 0)
            array.remove(zigzagpivotratios, 0)
            array.remove(zigzagoscillators, 0)
            array.remove(zigzagoscillatordirs, 0)
            array.remove(zigzagtrendbias, 0)
            array.remove(zigzagdivergence, 0)
            value = phigh if pDir == 1 else plow
            bar = phighbar if pDir == 1 else plowbar
            useNewValues = value * pivotdir > pivot * pivotdir
            value = value if useNewValues else pivot
            bar = bar if useNewValues else pivotbar
            newZG = newZG or useNewValues
            addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, value, bar, pDir, numberOfPivots, oscHigh, oscLow, directionBias)
        if pDir == 1 and plow or (pDir == -1 and phigh):
            value = plow if pDir == 1 else phigh
            bar = plowbar if pDir == 1 else phighbar
            dir = -1 if pDir == 1 else 1
            newZG = True
            addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, value, bar, dir, numberOfPivots, oscHigh, oscLow, directionBias)
        return (newZG, doubleZG)

    def draw_zg_line(idx1, idx2, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagdivergence, zigzagcolor, zigzagwidth, zigzagstyle, showHighLow, showRatios, showDivergence):
        __block_result_1__ = na
        if array.size(zigzagpivots) > 2:
            y1 = array.get(zigzagpivots, idx1)
            y2 = array.get(zigzagpivots, idx2)
            x1 = array.get(zigzagpivotbars, idx1)
            x2 = array.get(zigzagpivotbars, idx2)
            zline = line.new(x1=x1, y1=y1, x2=x2, y2=y2, color=zigzagcolor, width=zigzagwidth, style=zigzagstyle)
            currentDir = 1 if y1 > y2 else -1
            zlabel: Label = na(Label)
            if showHighLow or showRatios or showDivergence:
                dir = array.get(zigzagpivotdirs, idx1)
                ratio = array.get(zigzagpivotratios, idx1)
                sentiment = array.get(zigzagdivergence, idx1)
                sentimentSymbol, sentimentLabel, sentimentColor = getSentimentDetails(sentiment)
                __block_result_2__ = (na, na)
                __switch_2__ = dir
                if __switch_2__ == 1:
                    __block_result_2__ = ('LH', color.orange)
                elif __switch_2__ == 2:
                    __block_result_2__ = ('HH', color.green)
                elif __switch_2__ == -1:
                    __block_result_2__ = ('HL', color.lime)
                elif __switch_2__ == -2:
                    __block_result_2__ = ('LL', color.red)
                else:
                    __block_result_2__ = ('NA', color.silver)
                hhllText, labelColor = __block_result_2__
                labelText = (hhllText if showHighLow else '') + (' - ' if showHighLow and showRatios else '') + (string.tostring(ratio) if showRatios else '') + (' : ' if (showHighLow or showRatios) and showDivergence else '') + (sentimentSymbol if showDivergence else '')
                labelStyle = label.style_label_down if dir >= 0 else label.style_label_up
                zlabel = label.new(x=x1, y=y1, yloc=yloc.price, color=sentimentColor if showDivergence else labelColor, style=labelStyle, text=labelText, textcolor=color.black, size=size.small, tooltip=hhllText)
            if array.size(zigzaglines) > 0:
                lastLine = array.get(zigzaglines, 0)
                if line.get_x2(lastLine) == x2 and line.get_x1(lastLine) <= x1:
                    line.delete(array.shift(zigzaglines))
                    label.delete(array.shift(zigzaglabels))
            array.unshift(zigzaglines, zline)
            array.unshift(zigzaglabels, zlabel)
            __block_result_3__ = na
            if array.size(zigzaglines) > 500:
                line.delete(array.pop(zigzaglines))
                __block_result_3__ = label.delete(array.pop(zigzaglabels))
            __block_result_1__ = __block_result_3__
        return __block_result_1__

    @export
    def zigzag(length: int, numberOfPivots: int = 20, useAlternativeSource: bool = False, source: float = close, oscillatorSource: float = close, oscillatorHighSource: float = high, oscillatorLowSource: float = close, directionBias: int = 1):
        zigzagpivots: Persistent[list[float]] = array.new_float(0)
        zigzagpivotbars: Persistent[list[int]] = array.new_int(0)
        zigzagpivotdirs: Persistent[list[int]] = array.new_int(0)
        zigzagpivotratios: Persistent[list[float]] = array.new_float(0)
        zigzagoscillators: Persistent[list[float]] = array.new_float(0)
        zigzagoscillatordirs: Persistent[list[int]] = array.new_int(0)
        zigzagtrendbias: Persistent[list[int]] = array.new_int(0)
        zigzagdivergence: Persistent[list[int]] = array.new_int(0)
        oscHigh = oscillatorHighSource if not useAlternativeSource and oscillatorHighSource != source else oscillatorSource
        oscLow = oscillatorLowSource if not useAlternativeSource and oscillatorLowSource != source else oscillatorSource
        highSource = source if useAlternativeSource else high
        lowSource = source if useAlternativeSource else low
        phigh, plow, phighbar, plowbar = pivots(length, highSource, lowSource)
        newPivot, doublePivot = zigzagcore(phigh, plow, phighbar, plowbar, numberOfPivots, oscHigh, oscLow, directionBias, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence)
        return (zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot)

    @export
    def czigzag(length: int, numberOfPivots: int = 20, highSource: float = high, lowSource: float = low, oscillatorHighSource: float = high, oscillatorLowSource: float = low, directionBias: int = 1):
        zigzagpivots: Persistent[list[float]] = array.new_float(0)
        zigzagpivotbars: Persistent[list[int]] = array.new_int(0)
        zigzagpivotdirs: Persistent[list[int]] = array.new_int(0)
        zigzagpivotratios: Persistent[list[float]] = array.new_float(0)
        zigzagoscillators: Persistent[list[float]] = array.new_float(0)
        zigzagoscillatordirs: Persistent[list[int]] = array.new_int(0)
        zigzagtrendbias: Persistent[list[int]] = array.new_int(0)
        zigzagdivergence: Persistent[list[int]] = array.new_int(0)
        phigh, plow, phighbar, plowbar = pivots(length, highSource, lowSource)
        newPivot, doublePivot = zigzagcore(phigh, plow, phighbar, plowbar, numberOfPivots, oscillatorHighSource, oscillatorLowSource, directionBias, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence)
        return (zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot)

    @export
    def drawzigzag(length: int, numberOfPivots: int = 20, useAlternativeSource: bool = False, source: float = close, linecolor: Color = color.blue, linewidth: int = 1, linestyle: str = line.style_solid, oscillatorSource: float = close, oscillatorHighSource: float = high, oscillatorLowSource: float = close, directionBias: int = 1, showHighLow: bool = False, showRatios: bool = False, showDivergence: bool = False):
        zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot = zigzag(length, numberOfPivots, useAlternativeSource, source, oscillatorSource, oscillatorHighSource, oscillatorLowSource, directionBias)
        zigzaglines: Persistent[list[Line]] = array.new_line(0)
        zigzaglabels: Persistent[list[Label]] = array.new_label(0)
        if newPivot:
            if doublePivot:
                draw_zg_line(1, 2, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagdivergence, linecolor, linewidth, linestyle, showHighLow, showRatios, showDivergence)
            if array.size(zigzagpivots) >= 2:
                draw_zg_line(0, 1, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagdivergence, linecolor, linewidth, linestyle, showHighLow, showRatios, showDivergence)
        return (zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, zigzaglines, zigzaglabels)

    if operation == 'Draw Zigzag':
        if not useAlternativeSource and (not useDifferentLineStyle) and (not showDivergence) and (not showHighLow) and (not showRatios):
            drawzigzag(zigzagLength)
        elif useAlternativeSource and (not useDifferentLineStyle) and (not showDivergence) and (not showHighLow) and (not showRatios):
            drawzigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source)
        elif not useAlternativeSource and useDifferentLineStyle and (not showDivergence) and (not showHighLow) and (not showRatios):
            drawzigzag(zigzagLength, linecolor=linecolor, linewidth=math.max(1, linewidth), linestyle=linestyle)
        elif not useAlternativeSource and (not useDifferentLineStyle) and (not showDivergence):
            drawzigzag(zigzagLength, showHighLow=showHighLow, showRatios=showRatios)
        elif useAlternativeSource and (not useDifferentLineStyle) and (not showDivergence):
            drawzigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source, showHighLow=showHighLow, showRatios=showRatios)
        elif not showDivergence:
            drawzigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source, linecolor=linecolor, linewidth=math.max(1, linewidth), linestyle=linestyle, showHighLow=showHighLow, showRatios=showRatios)
        else:
            rsi = ta.rsi(close, 14)
            rsiHigh = ta.rsi(high, 14)
            rsiLow = ta.rsi(low, 14)
            supertrend, dir = ta.supertrend(4, 22)
            directionBias = cast_int(-dir)
            if not useDifferentLineStyle:
                drawzigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source, oscillatorSource=rsi, oscillatorHighSource=rsiHigh, oscillatorLowSource=rsiLow, directionBias=directionBias, showHighLow=showHighLow, showRatios=showRatios, showDivergence=showDivergence)
            else:
                drawzigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source, linecolor=linecolor, linewidth=math.max(1, linewidth), linestyle=linestyle, oscillatorSource=rsi, oscillatorHighSource=rsiHigh, oscillatorLowSource=rsiLow, directionBias=directionBias, showHighLow=showHighLow, showRatios=showRatios, showDivergence=showDivergence)
    else:
        if not useAlternativeSource and (not showDivergence):
            zigzag(zigzagLength)
        elif useAlternativeSource and (not showDivergence):
            zigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source)
        else:
            rsi = ta.rsi(close, 14)
            supertrend, dir = ta.supertrend(4, 22)
            directionBias = cast_int(-dir)
            zigzag(zigzagLength, useAlternativeSource=useAlternativeSource, source=source, oscillatorSource=rsi, directionBias=directionBias)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
