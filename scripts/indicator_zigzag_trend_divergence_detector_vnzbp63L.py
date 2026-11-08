"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barcolor, barstate, close, color, dayofmonth,
    high, hour, input, label, line, low, math, minute, month, na, nz, plot, position, script,
    second, size, string, syminfo, ta, table, time, timeframe, xloc, year, yloc
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Zigzag Trend/Divergence Detector', shorttitle='Zigzag-Trend-Divergence', overlay=True, max_bars_back=1000, max_lines_count=500, max_labels_count=500)
def main(
    useClosePrices=input.bool(True, title='Close Prices', group='Zigzag', inline='price'),
    waitForConfirmation=input.bool(False, title='Confirmed Pivots', group='Zigzag', inline='price'),
    pZigzagLength=input.int(5, step=1, minval=3, title='', group='Zigzag', inline='price'),
    pZigzagColor=input.color(color.rgb(251, 192, 45, 0), title='', group='Zigzag', inline='price'),
    oscillatorSource=input.string('RSI', title='Source', options=('CCI', 'CMO', 'COG', 'DMI', 'HIST', 'MACD', 'MFI', 'MOM', 'ROC', 'RSI', 'TSI', 'WPR', 'BB', 'KC', 'DC', 'ADC', 'External'), group='Oscillator', inline='osc'),
    externalSource: Series[float] = input.source(close, title='External Source', group='Oscillator', inline='osc'),
    oscillatorLength=input.int(22, title='Length', group='Oscillator', inline='osc2'),
    oscillatorShortLength=input.int(12, title='Fast', group='Oscillator', inline='osc2'),
    oscillatorLongLength=input.int(26, title='Slow', group='Oscillator', inline='osc2'),
    considerTrendBias=input.bool(True, title='Pivot History', group='Supertrend (Trend Bias)', inline='st'),
    supertrendHistory=input.int(4, step=1, title='', group='Supertrend (Trend Bias)', inline='st'),
    atrPeriods=input.int(22, title='ATR Length', step=5, group='Supertrend (Trend Bias)'),
    atrMult=input.float(1, step=0.5, title='ATR Multiplier', group='Supertrend (Trend Bias)'),
    colorCandles=input.bool(True, title='Color Candles', group='Supertrend (Trend Bias)', inline='1'),
    showSupertrend=input.bool(True, title='Plot Supertrend', group='Supertrend (Trend Bias)', inline='1'),
    showStatTable=input.bool(True, title='Max Rows', group='Stats and Display', inline='stats'),
    max_array_size=input.int(10, title='', step=5, minval=5, group='Stats and Display', inline='stats'),
    text_size=input.string(size.small, title='Size', options=(size.tiny, size.small, size.normal, size.large, size.huge, size.auto), group='Stats and Display', inline='stats'),
    showContinuation=input.bool(True, title='Continuation', group='Stats and Display', inline='display'),
    showIndeterminate=input.bool(True, title='Indeterminate', group='Stats and Display', inline='display'),
    showDivergence=input.bool(True, title='Divergence', group='Stats and Display', inline='display'),
    showHiddenDivergence=input.bool(True, title='Hidden Divergence', group='Stats and Display', inline='display'),
    alertContinuation=input.bool(False, title='Continuation', group='Alert', inline='alert'),
    alertIndeterminate=input.bool(False, title='Indeterminate', group='Alert', inline='alert'),
    alertDivergence=input.bool(True, title='Divergence', group='Alert', inline='alert'),
    alertHiddenDivergence=input.bool(True, title='Hidden Divergence', group='Alert', inline='alert')
):
    startIndex = 1 if waitForConfirmation else 0
    def donchian(rangeLength):
        top = ta.highest(rangeLength)
        bottom = ta.lowest(rangeLength)
        middle = (top + bottom) / 2
        return (middle, top, bottom)

    def adoptive_donchian(rangeLength):
        middle: Series
        top: Series
        bottom: Series
        middle, top, bottom = donchian(rangeLength)
        channelBreak = high >= top[1] or low <= bottom[1]
        if not channelBreak:
            middle = nz(middle[1], middle)
            top = nz(top[1], top)
            bottom = nz(bottom[1], bottom)
        return (middle, top, bottom)

    macdLine, signalLine, histLine = ta.macd(close, oscillatorShortLength, oscillatorLongLength, oscillatorShortLength)
    bbmiddle, bbupper, bblower = ta.bb(close, oscillatorLength, 5)
    kcmiddle, kcupper, kclower = ta.kc(close, oscillatorLength, 5, True)
    dcmiddle, dcupper, dclower = donchian(oscillatorLength)
    adcmiddle, adcupper, adclower = adoptive_donchian(oscillatorLength)
    diplus, diminus, adx = ta.dmi(oscillatorLongLength, oscillatorShortLength)
    oscillator = ta.cci(close, oscillatorLength) if oscillatorSource == 'CCI' else ta.cmo(close, oscillatorLength) if oscillatorSource == 'CMO' else ta.cog(close, oscillatorLength) if oscillatorSource == 'COG' else adx if oscillatorSource == 'DMI' else histLine if oscillatorSource == 'HIST' else macdLine if oscillatorSource == 'MACD' else ta.mfi(close, oscillatorLength) if oscillatorSource == 'MFI' else ta.mom(close, oscillatorLength) if oscillatorSource == 'MOM' else ta.roc(close, oscillatorLength) if oscillatorSource == 'ROC' else ta.rsi(close, oscillatorLength) if oscillatorSource == 'RSI' else ta.tsi(close, oscillatorShortLength, oscillatorLongLength) if oscillatorSource == 'TSI' else ta.wpr(oscillatorLength) if oscillatorSource == 'WPR' else (close - bblower) / (bbupper - bblower) if oscillatorSource == 'BB' else (close - kclower) / (kcupper - kclower) if oscillatorSource == 'KC' else (close - dclower) / (dcupper - dclower) if oscillatorSource == 'DC' else (close - adclower) / (adcupper - adclower) if oscillatorSource == 'ADC' else externalSource
    zigzagsupertrenddirs: Persistent[list[int]] = array.new_int(1, 1)
    zigzagsupertrend: Persistent[list[float]] = array.new_float(2, na)
    pZigzagPivots: Persistent[list[float]] = array.new_float(0)
    pZigzagPivotBars: Persistent[list[int]] = array.new_int(0)
    pZigzagPivotDirs: Persistent[list[int]] = array.new_int(0)
    opZigzagPivots: Persistent[list[float]] = array.new_float(0)
    opZigzagPivotDirs: Persistent[list[int]] = array.new_int(0)
    pZigzagLines: Persistent[list[Line]] = array.new_line(0)
    pZigzagLabels: Persistent[list[Label]] = array.new_label(0)
    def f_initialize_supertrend(zigzagPivots):
        dir = array.get(zigzagsupertrenddirs, 0)
        buyStop = array.get(zigzagsupertrend, 0)
        sellStop = array.get(zigzagsupertrend, 1)
        tail = array.slice(zigzagPivots, 1, 1 + supertrendHistory) if array.size(zigzagPivots) > 1 + supertrendHistory else array.new_float()
        highest = array.max(tail)
        lowest = array.min(tail)
        atrDiff = ta.atr(atrPeriods) * atrMult
        newBuyStop = lowest - atrDiff
        newSellStop = highest + atrDiff
        newDir = -1 if dir > 0 and close[1] < buyStop else 1 if dir < 0 and close[1] > sellStop else dir
        newBuyStop = math.max(nz(buyStop, newBuyStop), newBuyStop) if newDir > 0 else newBuyStop
        newSellStop = math.min(nz(sellStop, newSellStop), newSellStop) if newDir < 0 else newSellStop
        array.set(zigzagsupertrenddirs, 0, newDir)
        array.set(zigzagsupertrend, 0, newBuyStop)
        array.set(zigzagsupertrend, 1, newSellStop)
        return (newDir, newBuyStop, newSellStop)

    supertrendDir: Series
    supertrendDir, buyStop, sellStop = f_initialize_supertrend(pZigzagPivots)
    def add_to_array(arr, val, maxItems):
        array.unshift(arr, val)
        __block_result__ = na
        if array.size(arr) > maxItems:
            __block_result__ = array.pop(arr)
        return __block_result__

    def pivots(length, useAlternativeSource, source):
        highsource = source if useAlternativeSource else high
        lowsource = source if useAlternativeSource else low
        phigh: float = highsource if ta.highestbars(highsource, length) == 0 else na
        plow: float = lowsource if ta.lowestbars(lowsource, length) == 0 else na
        return (phigh, plow, bar_index, bar_index)

    def addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, value, otherSource: Series, bar, dir):
        newDir = dir
        othDir = dir
        if array.size(zigzagpivots) >= 2:
            LastPoint = array.get(zigzagpivots, 1)
            newDir = dir * 2 if dir * value > dir * LastPoint else dir
            LastOther = array.get(zigzagother, 1)
            othDir = dir * 2 if dir * otherSource[bar_index - bar] > dir * LastOther else dir
        add_to_array(zigzagpivots, value, max_array_size + startIndex)
        add_to_array(zigzagpivotbars, bar, max_array_size + startIndex)
        add_to_array(zigzagpivotdirs, newDir, max_array_size + startIndex)
        add_to_array(zigzagother, otherSource[bar_index - bar], max_array_size + startIndex)
        return add_to_array(zigzagotherdir, othDir, max_array_size + startIndex)

    def zigzagcore(phigh, plow, phighbar, plowbar, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, otherSource):
        pDir: int = 1
        newZG: bool = False
        doubleZG = phigh and plow
        if array.size(zigzagpivots) >= 1:
            pDir = array.get(zigzagpivotdirs, 0)
            pDir = pDir / 2 if pDir % 2 == 0 else pDir
        if (pDir == 1 and phigh or (pDir == -1 and plow)) and array.size(zigzagpivots) >= 1:
            pivot = array.shift(zigzagpivots)
            pivotbar = array.shift(zigzagpivotbars)
            pivotdir = array.shift(zigzagpivotdirs)
            otherVal = array.shift(zigzagother)
            otherDir = array.shift(zigzagotherdir)
            value = phigh if pDir == 1 else plow
            bar = phighbar if pDir == 1 else plowbar
            useNewValues = value * pivotdir > pivot * pivotdir
            value = value if useNewValues else pivot
            bar = bar if useNewValues else pivotbar
            otherVal = otherSource if useNewValues else otherVal
            newZG = newZG or useNewValues
            addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, value, otherVal, bar, pDir)
        if pDir == 1 and plow or (pDir == -1 and phigh):
            value = plow if pDir == 1 else phigh
            bar = plowbar if pDir == 1 else phighbar
            dir = -1 if pDir == 1 else 1
            newZG = True
            addnewpivot(zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, value, otherSource, bar, dir)
        return (newZG, doubleZG)

    def zigzag(length, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, useAlternativeSource, source, otherSource):
        phigh, plow, phighbar, plowbar = pivots(length, useAlternativeSource, source)
        return zigzagcore(phigh, plow, phighbar, plowbar, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagother, zigzagotherdir, otherSource)

    def getSentimentByDivergenceAndBias(divergence, bias):
        sentimentColor = (color.green if bias == 1 else color.red) if divergence == 1 else (color.lime if bias == 1 else color.orange) if divergence == -1 else (color.lime if bias == 1 else color.orange) if divergence == -2 else color.silver
        sentiment = '▣' if divergence == 0 else ('⬆' if divergence == 1 else '⤴' if divergence == -1 else '↗' if divergence == -2 else '⤮') if bias > 0 else '⬇' if divergence == 1 else '⤵' if divergence == -1 else '↘' if divergence == -2 else '⤭'
        return (sentiment, sentimentColor)

    def f_get_divergence(pDir, oDir, sDir):
        divergence = (1 if pDir % 2 == 0 and pDir / 2 == sDir or (pDir % 2 != 0 and pDir != sDir) else 0) if pDir == oDir else -1 if pDir == 2 * oDir and oDir == sDir else -2 if 2 * pDir == oDir and pDir == -sDir else 0
        divergenceIdentifier = 'C' if divergence == 1 else 'D' if divergence == -1 else 'H' if divergence == -2 else 'I'
        return (divergence, divergenceIdentifier)

    def f_get_bias(pDir, oDir):
        return 1 if pDir == 2 and oDir == 2 else -1 if pDir == -2 and oDir == -2 else -1 if pDir > 0 else 1 if pDir < 0 else 0

    def draw_zg_line(idx1, idx2, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, ozigzagpivotdirs, zigzagcolor, zigzagwidth, zigzagstyle):
        __hist_supertrendDir__: Series[void] = supertrendDir[0]
        __block_result_1__ = na
        if array.size(zigzagpivots) > idx2:
            y1 = array.get(zigzagpivots, idx1)
            y2 = array.get(zigzagpivots, idx2)
            x1 = array.get(zigzagpivotbars, idx1)
            x2 = array.get(zigzagpivotbars, idx2)
            pDir = array.get(zigzagpivotdirs, idx1)
            oDir = array.get(ozigzagpivotdirs, idx1)
            sDir = __hist_supertrendDir__[bar_index - x1]
            divergence, divergenceIdentifier = f_get_divergence(pDir, oDir, sDir)
            bias = f_get_bias(pDir, oDir)
            sentiment, sentimentColor = getSentimentByDivergenceAndBias(divergence, bias)
            zline = line.new(x1=x1, y1=y1, x2=x2, y2=y2, color=zigzagcolor, width=zigzagwidth, style=zigzagstyle)
            zlabel = label.new(x=x1, y=y1, xloc=xloc.bar_index, yloc=yloc.price, text=divergenceIdentifier, color=sentimentColor, style=label.style_label_down if pDir > 0 else label.style_label_up, textcolor=color.black, size=size.small)
            if array.size(zigzaglines) >= 1:
                lastLine = array.get(zigzaglines, 0)
                if x2 == line.get_x2(lastLine) and y2 == line.get_y2(lastLine):
                    line.delete(array.shift(zigzaglines))
                    label.delete(array.shift(zigzaglabels))
            if not showIndeterminate and divergence == 0 or (not showContinuation and divergence == 1) or (not showDivergence and divergence == -1) or (not showHiddenDivergence and divergence == -2):
                label.delete(zlabel)
            array.unshift(zigzaglines, zline)
            array.unshift(zigzaglabels, zlabel)
            __block_result_2__ = na
            if array.size(zigzaglines) > 500:
                line.delete(array.pop(zigzaglines))
                __block_result_2__ = label.delete(array.pop(zigzaglabels))
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def draw_zigzag(doubleZG, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, ozigzagpivotdirs, zigzagcolor, zigzagwidth, zigzagstyle):
        if doubleZG:
            draw_zg_line(startIndex + 1, startIndex + 2, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, ozigzagpivotdirs, zigzagcolor, zigzagwidth, zigzagstyle)
        __block_result_3__ = na
        if array.size(zigzagpivots) >= startIndex + 2:
            __block_result_3__ = draw_zg_line(startIndex + 0, startIndex + 1, zigzaglines, zigzaglabels, zigzagpivots, zigzagpivotbars, zigzagpivotdirs, ozigzagpivotdirs, zigzagcolor, zigzagwidth, zigzagstyle)
        return __block_result_3__

    def getCellColorByDirection(dir):
        return color.green if dir == 2 else color.orange if dir == 1 else color.lime if dir == -1 else color.red if dir == -2 else color.silver

    def getLabelByDirection(dir):
        return '⇈' if dir == 2 else '↑' if dir == 1 else '↓' if dir == -1 else '⇊' if dir == -2 else 'NA'

    oscillator = nz(oscillator, close)
    pZG, pdZG = zigzag(pZigzagLength, pZigzagPivots, pZigzagPivotBars, pZigzagPivotDirs, opZigzagPivots, opZigzagPivotDirs, useClosePrices, close, oscillator)
    trendColor = color.lime if supertrendDir > 0 else color.orange
    barcolor(trendColor if colorCandles else na)
    plot(buyStop if supertrendDir > 0 else sellStop, title='Supertrend', color=trendColor)
    if pZG:
        draw_zigzag(pdZG, pZigzagLines, pZigzagLabels, pZigzagPivots, pZigzagPivotBars, pZigzagPivotDirs, opZigzagPivotDirs, pZigzagColor, 1, line.style_solid)
    if barstate.islast and showStatTable:
        stats = table.new(position=position.top_right, columns=5, rows=max_array_size + startIndex + 2, border_width=1)
        table.cell(table_id=stats, column=0, row=0, text='Bar Time', bgcolor=color.black, text_color=color.white, text_size=text_size)
        table.cell(table_id=stats, column=1, row=0, text='Price', bgcolor=color.black, text_color=color.white, text_size=text_size)
        table.cell(table_id=stats, column=2, row=0, text='Oscillator', bgcolor=color.black, text_color=color.white, text_size=text_size)
        table.cell(table_id=stats, column=3, row=0, text='Trend', bgcolor=color.black, text_color=color.white, text_size=text_size)
        table.cell(table_id=stats, column=4, row=0, text='Sentiment', bgcolor=color.black, text_color=color.white, text_size=text_size)
        for i in pine_range(startIndex, array.size(pZigzagPivotDirs) - 1 if array.size(pZigzagPivotDirs) > 0 else na, 1):
            pBar = array.get(pZigzagPivotBars, i)
            pDir = array.get(pZigzagPivotDirs, i)
            oDir = array.get(opZigzagPivotDirs, i)
            sDir = supertrendDir[bar_index - pBar]
            divergence, divergenceIdentifier = f_get_divergence(pDir, oDir, sDir)
            bias = f_get_bias(pDir, oDir)
            sentiment, sentimentColor = getSentimentByDivergenceAndBias(divergence, bias)
            if not showIndeterminate and divergence == 0 or (not showContinuation and divergence == 1) or (not showDivergence and divergence == -1) or (not showHiddenDivergence and divergence == -2):
                continue
            trendDirection = '⇑' if sDir > 0 else '⇓'
            trendColor__000000d7__ = color.green if sDir > 0 else color.red
            barTime = time[bar_index - pBar]
            barTimeString = string.tostring(year(barTime), '0000') + '/' + string.tostring(month(barTime), '00') + '/' + string.tostring(dayofmonth(barTime), '00') + ('-' + string.tostring(hour(barTime), '00') + ':' + string.tostring(minute(barTime), '00') + ':' + string.tostring(second(barTime), '00') if timeframe.isintraday else '')
            table.cell(table_id=stats, column=0, row=i + 1 - startIndex, text=barTimeString, bgcolor=getCellColorByDirection(pDir), text_size=text_size)
            table.cell(table_id=stats, column=1, row=i + 1 - startIndex, text=getLabelByDirection(pDir), bgcolor=getCellColorByDirection(pDir), text_size=text_size)
            table.cell(table_id=stats, column=2, row=i + 1 - startIndex, text=getLabelByDirection(oDir), bgcolor=getCellColorByDirection(oDir), text_size=text_size)
            table.cell(table_id=stats, column=3, row=i + 1 - startIndex, text=trendDirection, bgcolor=trendColor__000000d7__, text_size=text_size)
            table.cell(table_id=stats, column=4, row=i + 1 - startIndex, text=sentiment, bgcolor=sentimentColor, text_size=text_size)
    if array.size(pZigzagPivotBars) > startIndex:
        lastPivotBar: Series = array.get(pZigzagPivotBars, startIndex)
        lPivotDir = array.get(pZigzagPivotDirs, startIndex)
        lOscillatorDir = array.get(opZigzagPivotDirs, startIndex)
        sDir = supertrendDir[bar_index - lastPivotBar]
        divergence, divergenceIdentifier = f_get_divergence(lPivotDir, lOscillatorDir, sDir)
        bias = f_get_bias(lPivotDir, lOscillatorDir)
        sentiment, sentimentColor = getSentimentByDivergenceAndBias(divergence, bias)
        isAlertBar = bar_index == lastPivotBar and startIndex == 0 or (startIndex == 1 and lastPivotBar != lastPivotBar[1])
        if isAlertBar and (alertIndeterminate and divergence == 0 or (alertContinuation and divergence == 1) or (alertDivergence and divergence == -1) or (alertHiddenDivergence and divergence == -2)):
            sentimentText = ('Bullish Continuation' if bias == 1 else 'Bearish Continuation') if divergence == 1 else ('Bullish Divergence' if bias == 1 else 'Bearish Divergence') if divergence == -1 else ('Bullish Hidden Divergence' if bias == 1 else 'Bearish Hidden Divergence') if divergence == -2 else 'Indeterminate'
            alert('Sentiment alert on ' + syminfo.tickerid + ' :: ' + sentimentText)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)