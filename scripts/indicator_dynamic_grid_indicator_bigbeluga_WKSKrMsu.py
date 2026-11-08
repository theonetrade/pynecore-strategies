"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    bar_index, barstate, chart, close, color, fill, high, hl2, hlc3, hlcc4,
    input, label, low, math, na, open, plot, position, script, size, string, ta, table, xloc, yloc
)
from pynecore.types import Color, Label, NA, Persistent, PersistentSeries, Series, Table

G_MA: str = 'Trend & Base Channel Settings'
G_GRID: str = 'Grid Settings'
G_SIG: str = 'Signal Settings'
G_STYLE: str = 'Style Settings'
G_DASH: str = 'Dashboard Settings'


@script.indicator("Dynamic Grid Indicator [BigBeluga]", overlay=False, max_bars_back=5000, max_labels_count=500, calc_bars_count=3000)
def main(
    hmaLength=input.int(150, 'HMA Length', minval=1, group=G_MA, tooltip='Period length for the central Hull Moving Average baseline.'),
    atrLength=input.int(100, 'ATR Length', minval=1, group=G_MA, tooltip='Period length used to measure average true range volatility.'),
    atrMult=input.float(1.6, 'ATR Multiplier Step', minval=0.1, step=0.1, group=G_MA, tooltip='Multiplier step distance applied to each grid channel level.'),
    numLevels=input.int(3, 'Grid Levels (Each Side)', minval=1, maxval=5, group=G_GRID, tooltip='Number of channel levels projected above and below the baseline (1 to 5).'),
    thresholdP=input.float(0.5, 'Proximity Sensitivity (% of Step)', minval=0.01, maxval=1.0, step=0.1, group=G_GRID, tooltip='Defines proximity distance to hide line segment when price is near.'),
    minGap=input.int(10, 'Minimum Bar Gap Between Signals', minval=1, group=G_SIG, tooltip='Minimum number of bars required between consecutive crossover signals.'),
    baseTeal=input.color(color.new('#1ECC75'), 'Bullish Color', group=G_STYLE, tooltip='Primary color used for bullish levels, oscillator lines, and buy signals.'),
    baseMaroon=input.color(color.new('#C04020'), 'Bearish Color', group=G_STYLE, tooltip='Primary color used for bearish levels, oscillator lines, and sell signals.'),
    sigLblSizeInput=input.string('normal', 'Signal Label Size', options=('auto', 'tiny', 'small', 'normal', 'large', 'huge'), group=G_STYLE, tooltip='Font size applied to signal crossover annotations on both chart and oscillator.'),
    edgeLblSizeInput=input.string('normal', 'Right-Edge Label Size', options=('auto', 'tiny', 'small', 'normal', 'large', 'huge'), group=G_STYLE, tooltip='Font size for right-edge grid level indicators.'),
    showDash=input.bool(True, 'Show Position Dashboard', group=G_DASH, tooltip='Toggle vertical scale dashboard visibility.'),
    dashPos=input.string('middle_right', 'Dashboard Position', options=('top_right', 'middle_right', 'bottom_right'), group=G_DASH),
    dashSizeInput=input.string('normal', 'Dashboard Size', options=('auto', 'tiny', 'small', 'normal', 'large', 'huge'), group=G_DASH, tooltip='Controls the text size of the dashboard.')
):
    def getLabelSize(sz: str):
        __block_result__ = na
        __switch__ = sz
        if __switch__ == 'auto':
            __block_result__ = size.auto
        elif __switch__ == 'tiny':
            __block_result__ = size.tiny
        elif __switch__ == 'small':
            __block_result__ = size.small
        elif __switch__ == 'normal':
            __block_result__ = size.normal
        elif __switch__ == 'large':
            __block_result__ = size.large
        elif __switch__ == 'huge':
            __block_result__ = size.huge
        else:
            __block_result__ = size.small
        return __block_result__

    sigLblSize = getLabelSize(sigLblSizeInput)
    edgeLblSize = getLabelSize(edgeLblSizeInput)
    dashSize = getLabelSize(dashSizeInput)

    centerLine: Series = ta.hma(close, hmaLength)
    atrVal = ta.atr(atrLength) * atrMult
    proxDist = atrVal * thresholdP
    oscValue = (close - centerLine) / atrVal if atrVal != 0 else 0.0

    upper1 = centerLine + atrVal * 1
    lower1 = centerLine - atrVal * 1
    upper2 = centerLine + atrVal * 2
    lower2 = centerLine - atrVal * 2
    upper3 = centerLine + atrVal * 3
    lower3 = centerLine - atrVal * 3
    upper4 = centerLine + atrVal * 4
    lower4 = centerLine - atrVal * 4
    upper5 = centerLine + atrVal * 5
    lower5 = centerLine - atrVal * 5

    def getGridColor(gridLevel: float, levelIdx: int, isUpper: bool):
        diff: float = math.abs(close - gridLevel)
        diff1: float = math.abs(open - gridLevel)
        diff2: float = math.abs(hl2 - gridLevel)
        diff3: float = math.abs(hlc3 - gridLevel)
        diff4: float = math.abs(hlcc4 - gridLevel)

        isClose: bool = diff <= proxDist or diff1 <= proxDist or diff2 <= proxDist or (diff3 <= proxDist) or (diff4 <= proxDist)

        stepNorm: float = levelIdx / cast_float(numLevels)
        targetBase: Color = baseTeal if isUpper else baseMaroon
        startColor: Color = color.new(targetBase, 85)
        endColor: Color = color.new(targetBase, 20)

        computedColor: Color = color.from_gradient(stepNorm, 0.0, 1.0, startColor, endColor)
        return NA(Color) if isClose else computedColor

    def getOscGridColor(levelIdx: int, isUpper: bool):
        stepNorm: float = levelIdx / cast_float(numLevels)
        targetBase: Color = baseTeal if isUpper else baseMaroon
        startColor: Color = color.new(targetBase, 80)
        endColor: Color = color.new(targetBase, 0)
        return color.from_gradient(stepNorm, 0.0, 1.0, startColor, endColor)

    def drawOverlayLabel(yVal: float, labelText: str, txtColor: Color):
        lbl: PersistentSeries[Label] = na(Label)
        __block_result_1__ = na
        if barstate.islast:
            lbl = label.new(bar_index + 2, yVal, labelText, xloc=xloc.bar_index, yloc=yloc.price, color=NA(Color), textcolor=txtColor, style=label.style_label_left, size=edgeLblSize, force_overlay=True)
            __block_result_1__ = label.delete(lbl[1])
        return __block_result_1__

    def drawOscLabel(yVal: float, labelText: str, txtColor: Color):
        lbl: PersistentSeries[Label] = na(Label)
        __block_result_2__ = na
        if barstate.islast:
            lbl = label.new(bar_index + 2, yVal, labelText, xloc=xloc.bar_index, yloc=yloc.price, color=NA(Color), textcolor=txtColor, style=label.style_label_left, size=edgeLblSize, force_overlay=False)
            __block_result_2__ = label.delete(lbl[1])
        return __block_result_2__

    crossBear1: bool = ta.crossunder(close, upper1)
    crossBear2: bool = ta.crossunder(close, upper2)
    crossBear3: bool = ta.crossunder(close, upper3)
    crossBear4: bool = ta.crossunder(close, upper4)
    crossBear5: bool = ta.crossunder(close, upper5)

    crossBull1: bool = ta.crossover(close, lower1)
    crossBull2: bool = ta.crossover(close, lower2)
    crossBull3: bool = ta.crossover(close, lower3)
    crossBull4: bool = ta.crossover(close, lower4)
    crossBull5: bool = ta.crossover(close, lower5)

    rawBear1: bool = crossBear1 and numLevels >= 1
    rawBear2: bool = crossBear2 and numLevels >= 2
    rawBear3: bool = crossBear3 and numLevels >= 3
    rawBear4: bool = crossBear4 and numLevels >= 4
    rawBear5: bool = crossBear5 and numLevels >= 5

    rawBull1: bool = crossBull1 and numLevels >= 1
    rawBull2: bool = crossBull2 and numLevels >= 2
    rawBull3: bool = crossBull3 and numLevels >= 3
    rawBull4: bool = crossBull4 and numLevels >= 4
    rawBull5: bool = crossBull5 and numLevels >= 5

    rawBearSignal: bool = rawBear1 or rawBear2 or rawBear3 or rawBear4 or rawBear5
    rawBullSignal: bool = rawBull1 or rawBull2 or rawBull3 or rawBull4 or rawBull5

    def getBearLevelStr():
        return '-5' if rawBear5 else '-4' if rawBear4 else '-3' if rawBear3 else '-2' if rawBear2 else '-1' if rawBear1 else ''

    def getBullLevelStr():
        return '+5' if rawBull5 else '+4' if rawBull4 else '+3' if rawBull3 else '+2' if rawBull2 else '+1' if rawBull1 else ''

    lastSigBar: Persistent[int] = -999
    bearSignal: bool = False
    bullSignal: bool = False

    if barstate.isconfirmed and (rawBearSignal or rawBullSignal) and (bar_index - lastSigBar >= minGap):
        bearSignal = rawBearSignal
        bullSignal = rawBullSignal
        lastSigBar = bar_index

    if bearSignal:
        label.new(bar_index, high, text=getBearLevelStr() + '\n▼', xloc=xloc.bar_index, yloc=yloc.abovebar, color=color.new(chart.bg_color, 100), textcolor=baseMaroon, style=label.style_label_down, size=sigLblSize, force_overlay=True)

    if bullSignal:
        label.new(bar_index, low, text='▲\n' + getBullLevelStr(), xloc=xloc.bar_index, yloc=yloc.belowbar, color=color.new(chart.bg_color, 100), textcolor=baseTeal, style=label.style_label_up, size=sigLblSize, force_overlay=True)

    if bearSignal:
        label.new(bar_index, oscValue, text=getBearLevelStr() + '\n▼', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(chart.bg_color, 100), textcolor=baseMaroon, style=label.style_label_down, size=sigLblSize, force_overlay=False)

    if bullSignal:
        label.new(bar_index, oscValue, text='▲\n' + getBullLevelStr(), xloc=xloc.bar_index, yloc=yloc.price, color=color.new(chart.bg_color, 100), textcolor=baseTeal, style=label.style_label_up, size=sigLblSize, force_overlay=False)

    def getDashPos(p: str):
        __block_result_3__ = na
        __switch__ = p
        if __switch__ == 'top_right':
            __block_result_3__ = position.top_right
        elif __switch__ == 'middle_right':
            __block_result_3__ = position.middle_right
        elif __switch__ == 'bottom_right':
            __block_result_3__ = position.bottom_right
        else:
            __block_result_3__ = position.middle_right
        return __block_result_3__

    dash: Persistent[Table] = table.new(getDashPos(dashPos), 2, 12, bgcolor=color.new(color.new('#20273A'), 10), border_width=2, border_color=chart.bg_color, force_overlay=True)

    if showDash and barstate.islast:
        table.cell(dash, 0, 0, 'Level', text_color=color.gray, text_size=dashSize)
        table.cell(dash, 1, 0, 'Scale', text_color=color.gray, text_size=dashSize)

        for i in pine_range(numLevels, -numLevels, 1):
            rowIdx: int = 6 - i
            levelVal: float = i
            isCurrentRow: bool = math.round(oscValue) == levelVal or (i == 5 and oscValue >= 5) or (i == -5 and oscValue <= -5)

            if math.abs(i) > numLevels:
                table.cell(dash, 0, rowIdx, '', text_size=dashSize)
                table.cell(dash, 1, rowIdx, '', text_size=dashSize)
            else:
                lvlStr: str = '+' + string.tostring(i) if i > 0 else string.tostring(i)
                lvlColor: Color = baseTeal if i > 0 else baseMaroon if i < 0 else color.gray

                valFormatted: str = string.tostring(oscValue, '#.##')
                marker: str = '◄ [' + valFormatted + ']' if isCurrentRow else '│'
                markerColor: Color = (baseTeal if oscValue >= 0 else baseMaroon) if isCurrentRow else color.new(color.gray, 60)

                table.cell(dash, 0, rowIdx, lvlStr, text_color=lvlColor, text_size=dashSize)
                table.cell(dash, 1, rowIdx, marker, text_color=markerColor, text_size=dashSize)

    trendColor = baseTeal if centerLine > centerLine[1] else baseMaroon
    plot(centerLine, 'Central HMA', color=trendColor, linewidth=2, force_overlay=True)
    plot(centerLine, 'Central HMA Glow', color=color.new(trendColor, 80), linewidth=10, force_overlay=True)

    plot(upper1 if numLevels >= 1 else na, 'Upper 1', color=getGridColor(upper1, 1, True), linewidth=1, force_overlay=True)
    plot(lower1 if numLevels >= 1 else na, 'Lower 1', color=getGridColor(lower1, 1, False), linewidth=1, force_overlay=True)
    if numLevels >= 1:
        drawOverlayLabel(upper1, '+1', baseTeal)
        drawOverlayLabel(lower1, '-1', baseMaroon)

    plot(upper2 if numLevels >= 2 else na, 'Upper 2', color=getGridColor(upper2, 2, True), linewidth=1, force_overlay=True)
    plot(lower2 if numLevels >= 2 else na, 'Lower 2', color=getGridColor(lower2, 2, False), linewidth=1, force_overlay=True)
    if numLevels >= 2:
        drawOverlayLabel(upper2, '+2', baseTeal)
        drawOverlayLabel(lower2, '-2', baseMaroon)

    plot(upper3 if numLevels >= 3 else na, 'Upper 3', color=getGridColor(upper3, 3, True), linewidth=2, force_overlay=True)
    plot(lower3 if numLevels >= 3 else na, 'Lower 3', color=getGridColor(lower3, 3, False), linewidth=2, force_overlay=True)
    if numLevels >= 3:
        drawOverlayLabel(upper3, '+3', baseTeal)
        drawOverlayLabel(lower3, '-3', baseMaroon)

    plot(upper4 if numLevels >= 4 else na, 'Upper 4', color=getGridColor(upper4, 4, True), linewidth=2, force_overlay=True)
    plot(lower4 if numLevels >= 4 else na, 'Lower 4', color=getGridColor(lower4, 4, False), linewidth=2, force_overlay=True)
    if numLevels >= 4:
        drawOverlayLabel(upper4, '+4', baseTeal)
        drawOverlayLabel(lower4, '-4', baseMaroon)

    plot(upper5 if numLevels >= 5 else na, 'Upper 5', color=getGridColor(upper5, 5, True), linewidth=2, force_overlay=True)
    plot(lower5 if numLevels >= 5 else na, 'Lower 5', color=getGridColor(lower5, 5, False), linewidth=2, force_overlay=True)
    if numLevels >= 5:
        drawOverlayLabel(upper5, '+5', baseTeal)
        drawOverlayLabel(lower5, '-5', baseMaroon)

    pZero = plot(0, 'Osc Zero Line', color=color.new(color.gray, 50), linewidth=1)

    pOscU1 = plot(1.0 if numLevels >= 1 else na, 'Osc +1', color=getOscGridColor(1, True), linewidth=1)
    pOscL1 = plot(-1.0 if numLevels >= 1 else na, 'Osc -1', color=getOscGridColor(1, False), linewidth=1)
    if numLevels >= 1:
        drawOscLabel(1.0, '+1', baseTeal)
        drawOscLabel(-1.0, '-1', baseMaroon)

    pOscU2 = plot(2.0 if numLevels >= 2 else na, 'Osc +2', color=getOscGridColor(2, True), linewidth=1)
    pOscL2 = plot(-2.0 if numLevels >= 2 else na, 'Osc -2', color=getOscGridColor(2, False), linewidth=1)
    if numLevels >= 2:
        drawOscLabel(2.0, '+2', baseTeal)
        drawOscLabel(-2.0, '-2', baseMaroon)

    pOscU3 = plot(3.0 if numLevels >= 3 else na, 'Osc +3', color=getOscGridColor(3, True), linewidth=1)
    pOscL3 = plot(-3.0 if numLevels >= 3 else na, 'Osc -3', color=getOscGridColor(3, False), linewidth=1)
    if numLevels >= 3:
        drawOscLabel(3.0, '+3', baseTeal)
        drawOscLabel(-3.0, '-3', baseMaroon)

    pOscU4 = plot(4.0 if numLevels >= 4 else na, 'Osc +4', color=getOscGridColor(4, True), linewidth=1)
    pOscL4 = plot(-4.0 if numLevels >= 4 else na, 'Osc -4', color=getOscGridColor(4, False), linewidth=1)
    if numLevels >= 4:
        drawOscLabel(4.0, '+4', baseTeal)
        drawOscLabel(-4.0, '-4', baseMaroon)

    pOscU5 = plot(5.0 if numLevels >= 5 else na, 'Osc +5', color=getOscGridColor(5, True), linewidth=1)
    pOscL5 = plot(-5.0 if numLevels >= 5 else na, 'Osc -5', color=getOscGridColor(5, False), linewidth=1)
    if numLevels >= 5:
        drawOscLabel(5.0, '+5', baseTeal)
        drawOscLabel(-5.0, '-5', baseMaroon)

    oscColor = baseTeal if oscValue >= 0 else baseMaroon
    pOscLine = plot(oscValue, 'Channel Oscillator', color=oscColor, linewidth=1)

    fill(pOscLine, pZero, 4, 0.0, oscColor, NA(Color), title='Oscillator Gradient Fill')
    fill(pOscLine, pZero, 0.0, -4, NA(Color), oscColor, title='Oscillator Gradient Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
