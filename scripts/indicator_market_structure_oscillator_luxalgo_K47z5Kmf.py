"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore.core.overload import overload
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, box, close, color, display, fill, format, high, input, label,
    line, log, low, math, na, nz, open, plot, plotcandle, script, size, ta, text
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@udt
class BAR:
    open: float = _dataclass_field(default_factory=lambda: open)
    high: float = _dataclass_field(default_factory=lambda: high)
    low: float = _dataclass_field(default_factory=lambda: low)
    close: float = _dataclass_field(default_factory=lambda: close)
    index: int = _dataclass_field(default_factory=lambda: bar_index)


@udt
class SWINGS:
    lastPrice: float = na(float)
    midPrice: float = na(float)
    prevPrice: float = na(float)
    lastIndex: int = na(int)
    midIndex: int = na(int)
    prevIndex: int = na(int)
    isCrossed: bool = na(bool)


@udt
class MS:
    type: int = 0


display__ren__ = display.all - display.status_line
msOsc_Group: str = 'Market Structure Oscillator'
cyc_Group: str = 'Cycle Oscillator'
genericGroup: str = 'Market Structures on Chart'
msOscCG: str = 'Oscillator Components'


@script.indicator('Market Structure Oscillator [LuxAlgo]', 'LuxAlgo - Market Structure Oscillator', False, format.price, max_lines_count=500, max_boxes_count=500, max_labels_count=500)
def main(
    msOsc_Show=input(True, 'Market Structure Oscillator', group=msOsc_Group),
    msWeightK1=input.float(1, '  Short Term Weight', minval=0, group=msOsc_Group, step=0.1, display=display__ren__),
    msWeightK2=input.float(3, '  Intermediate Term Weight', minval=0, group=msOsc_Group, step=0.1, display=display__ren__),
    msWeightK3=input.float(2, '  Long Term Weight', minval=0, group=msOsc_Group, step=0.1, display=display__ren__),
    norm_Smooth=input.int(4, '  Oscillator Smoothing', minval=1, group=msOsc_Group, display=display__ren__),
    msBullColor=input.color(color.new('#3179F5'), '  Gradient Colors: Bullish', inline='MS', group=msOsc_Group),
    msBearColor=input.color(color.new('#FFA726'), 'Bearish', inline='MS', group=msOsc_Group),
    oscSig=input(False, 'Market Structure Oscillator - Crosses (Signals)', group=msOsc_Group),
    oBullColor=input.color(color.new('#3179F5'), '  Signal Colors: Bullish', inline='SIG', group=msOsc_Group),
    oBearColor=input.color(color.new('#FFA726'), 'Bearish', inline='SIG', group=msOsc_Group),
    cycleOpt=input(True, 'Cycle Oscillator - Histogram', group=cyc_Group),
    cyc_Smooth=input.int(7, '  Cycle Signal Length', minval=1, group=cyc_Group, display=display__ren__),
    cBullColor=input.color(color.new(color.new('#90BFF9'), 25), '  Histogram Colors: Bullish', inline='CYC', group=cyc_Group),
    cBearColor=input.color(color.new(color.new('#FFCC80'), 25), 'Bearish', inline='CYC', group=cyc_Group),
    cycleSig=input(False, 'Cycle Oscillator - Crosses (Signals)', group=cyc_Group),
    sBullColor=input.color(color.new(color.new('#90BFF9'), 25), '  Signal Colors: Bullish', inline='SIG', group=cyc_Group),
    sBearColor=input.color(color.new(color.new('#FFCC80'), 25), 'Bearish', inline='SIG', group=cyc_Group),
    msOnChart1=input(False, 'Short Term Structures', group=genericGroup),
    msOnChartK1=input.string('Dotted', '  Line', options=('Solid', 'Dashed', 'Dotted'), group=genericGroup, inline='K1', display=display__ren__),
    stMSLblK1T=input.string('Disabled', 'Labels', options=('Enabled', 'Disabled'), group=genericGroup, inline='K1', display=display__ren__),
    cBullColorK1=input.color(color.new('#089981'), '  Colors: Bullish', inline='K1c', group=genericGroup),
    cBearColorK1=input.color(color.new('#F23645'), 'Bearish', inline='K1c', group=genericGroup),
    msOnChart2=input(False, 'Intermediate Term Structures', group=genericGroup),
    msOnChartK2=input.string('Dashed', '  Line', options=('Solid', 'Dashed', 'Dotted'), group=genericGroup, inline='K2', display=display__ren__),
    stMSLblK2T=input.string('Disabled', 'Labels', options=('Enabled', 'Disabled'), group=genericGroup, inline='K2', display=display__ren__),
    cBullColorK2=input.color(color.new('#089981'), '  Colors: Bullish', inline='K2c', group=genericGroup),
    cBearColorK2=input.color(color.new('#F23645'), 'Bearish', inline='K2c', group=genericGroup),
    msOnChart3=input(False, 'Long Term Structures', group=genericGroup),
    msOnChartK3=input.string('Solid', '  Line', options=('Solid', 'Dashed', 'Dotted'), group=genericGroup, inline='K3', display=display__ren__),
    stMSLblK3T=input.string('Enabled', 'Labels', options=('Enabled', 'Disabled'), group=genericGroup, inline='K3', display=display__ren__),
    cBullColorK3=input.color(color.new('#089981'), '  Colors: Bullish', inline='K3c', group=genericGroup),
    cBearColorK3=input.color(color.new('#F23645'), 'Bearish', inline='K3c', group=genericGroup),
    msDataK1=input(False, 'Short Term Oscillator', group=msOscCG, inline='k1w'),
    msColorK1=input(color.new(color.gray, 50), '', group=msOscCG, inline='k1w'),
    msDataK2=input(False, 'Intermediate Term Oscillator', group=msOscCG, inline='k2w'),
    msColorK2=input(color.new(color.gray, 50), '', group=msOscCG, inline='k2w'),
    msDataK3=input(False, 'Long Term Oscillator', group=msOscCG, inline='k3w'),
    msColorK3=input(color.new(color.gray, 50), '', group=msOscCG, inline='k3w')
):
    stMSLblK1 = stMSLblK1T == 'Enabled'
    stMSLblK2 = stMSLblK2T == 'Enabled'
    stMSLblK3 = stMSLblK3T == 'Enabled'
    bar: BAR = BAR()
    stLow: Persistent[SWINGS] = SWINGS()
    stHigh: Persistent[SWINGS] = SWINGS()
    stMS: Persistent[MS] = MS()
    itLow: Persistent[SWINGS] = SWINGS()
    itHigh: Persistent[SWINGS] = SWINGS()
    itMS: Persistent[MS] = MS()
    ltLow: Persistent[SWINGS] = SWINGS()
    ltHigh: Persistent[SWINGS] = SWINGS()
    ltMS: Persistent[MS] = MS()
    def lineStyle(styleInText):
        __block_result__ = na
        __switch__ = styleInText
        if __switch__ == 'Dotted':
            __block_result__ = line.style_dotted
        elif __switch__ == 'Dashed':
            __block_result__ = line.style_dashed
        else:
            __block_result__ = line.style_solid
        return __block_result__

    @overload
    def queryPatterns(lastPrice, midPrice, prevPrice, isSwingHigh):
        __block_result_1__ = na
        if isSwingHigh:
            __block_result_1__ = prevPrice < midPrice and midPrice >= lastPrice
        else:
            __block_result_1__ = prevPrice > midPrice and midPrice <= lastPrice
        return __block_result_1__

    @overload
    @method
    def queryPatterns(this: SWINGS, isSwingHigh):
        __block_result_2__ = na
        if isSwingHigh:
            __block_result_2__ = this.prevPrice < this.midPrice and this.midPrice >= this.lastPrice
        else:
            __block_result_2__ = this.prevPrice > this.midPrice and this.midPrice <= this.lastPrice
        return __block_result_2__

    @method
    def updatePattern(this: SWINGS, price, index):
        this.isCrossed = False
        this.prevPrice = this.midPrice
        this.midPrice = this.lastPrice
        this.lastPrice = price
        this.prevIndex = this.midIndex
        this.midIndex = this.lastIndex
        this.lastIndex = index
        return this.lastIndex

    @method
    def setType(this: MS, value):
        this.type = value
        return this.type

    def normalize(buy, sell, smooth):
        os: PersistentSeries[int] = 0
        max: Persistent[float] = na(float)
        min: Persistent[float] = na(float)
        os = 1 if buy else -1 if sell else os
        max = bar.close if os > os[1] else max if os < os[1] else math.max(bar.close, max)
        min = bar.close if os < os[1] else min if os > os[1] else math.min(bar.close, min)
        return ta.sma((bar.close - min) / (max - min), smooth) * 100

    def shortMarketStructure():
        bull: bool = False
        bear: bool = False
        if queryPatterns(high, high[1], high[2], True):
            updatePattern(stHigh, high[1], bar_index[1])
            stHigh.isCrossed = False
        if bar.close > stHigh.lastPrice and (not stHigh.isCrossed):
            stHigh.isCrossed = True
            bull = True
        if queryPatterns(low, low[1], low[2], False):
            stLow.isCrossed = False
            updatePattern(stLow, low[1], bar_index[1])
        if bar.close < stLow.lastPrice and (not stLow.isCrossed):
            stLow.isCrossed = True
            bear = True
        return normalize(bull, bear, norm_Smooth)

    def marketStructure(hSwingHigh: SWINGS, hSwingLow: SWINGS, lSwingHigh: SWINGS, lSwingLow: SWINGS):
        bull: bool = False
        bear: bool = False
        cSwingHigh: Series = queryPatterns(lSwingHigh, True)
        if cSwingHigh and cSwingHigh != cSwingHigh[1]:
            updatePattern(hSwingHigh, lSwingHigh.midPrice, lSwingHigh.midIndex)
            hSwingHigh.isCrossed = False
        if bar.close > hSwingHigh.lastPrice and (not hSwingHigh.isCrossed):
            hSwingHigh.isCrossed = True
            bull = True
        cSwingLow: Series = queryPatterns(lSwingLow, False)
        if cSwingLow and cSwingLow != cSwingLow[1]:
            updatePattern(hSwingLow, lSwingLow.midPrice, lSwingLow.midIndex)
            hSwingLow.isCrossed = False
        if bar.close < hSwingLow.lastPrice and (not hSwingLow.isCrossed):
            hSwingLow.isCrossed = True
            bear = True
        return normalize(bull, bear, norm_Smooth)

    def collectData():
        return (shortMarketStructure(), marketStructure(itHigh, itLow, stHigh, stLow), marketStructure(ltHigh, ltLow, itHigh, itLow))

    log.info('yaz_kizim {0} {1}', ltHigh.lastPrice, ltHigh.isCrossed)
    if msOnChart1:
        if bar.close > stHigh.lastPrice and (not stHigh.isCrossed):
            line.new(stHigh.lastIndex, stHigh.lastPrice, bar.index, stHigh.lastPrice, color=cBullColorK1, style=lineStyle(msOnChartK1), width=1, force_overlay=True)
            if stMSLblK1:
                box.new(stHigh.lastIndex, stHigh.lastPrice, bar.index, stHigh.lastPrice, NA(Color), text='CHoCH' if stMS.type < 0 else 'BoS', text_color=cBullColorK1, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_bottom, force_overlay=True)
                setType(stMS, 1)
        if bar.close < stLow.lastPrice and (not stLow.isCrossed):
            line.new(stLow.lastIndex, stLow.lastPrice, bar.index, stLow.lastPrice, color=cBearColorK1, style=lineStyle(msOnChartK1), width=1, force_overlay=True)
            if stMSLblK1:
                box.new(stLow.lastIndex, stLow.lastPrice, bar.index, stLow.lastPrice, NA(Color), text='CHoCH' if stMS.type > 0 else 'BoS', text_color=cBearColorK1, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_top, force_overlay=True)
                setType(stMS, -1)
    if msOnChart2:
        if bar.close > itHigh.lastPrice and (not itHigh.isCrossed):
            line.new(itHigh.lastIndex, itHigh.lastPrice, bar.index, itHigh.lastPrice, color=cBullColorK2, style=lineStyle(msOnChartK2), width=1, force_overlay=True)
            if stMSLblK2:
                box.new(itHigh.lastIndex, itHigh.lastPrice, bar.index, itHigh.lastPrice, NA(Color), text='CHoCH' if itMS.type < 0 else 'BoS', text_color=cBullColorK2, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_bottom, force_overlay=True)
                setType(itMS, 1)
        if bar.close < itLow.lastPrice and (not itLow.isCrossed):
            line.new(itLow.lastIndex, itLow.lastPrice, bar.index, itLow.lastPrice, color=cBearColorK2, style=lineStyle(msOnChartK2), width=1, force_overlay=True)
            if stMSLblK2:
                box.new(itLow.lastIndex, itLow.lastPrice, bar.index, itLow.lastPrice, NA(Color), text='CHoCH' if itMS.type > 0 else 'BoS', text_color=cBearColorK2, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_top, force_overlay=True)
                setType(itMS, -1)
    if msOnChart3:
        if bar.close > ltHigh.lastPrice and (not ltHigh.isCrossed):
            line.new(ltHigh.lastIndex, ltHigh.lastPrice, bar.index, ltHigh.lastPrice, color=cBullColorK3, style=lineStyle(msOnChartK3), width=1, force_overlay=True)
            if stMSLblK3:
                box.new(ltHigh.lastIndex, ltHigh.lastPrice, bar.index, ltHigh.lastPrice, NA(Color), text='CHoCH' if ltMS.type < 0 else 'BoS', text_color=cBullColorK3, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_bottom, force_overlay=True)
                setType(ltMS, 1)
        if bar.close < ltLow.lastPrice and (not ltLow.isCrossed):
            line.new(ltLow.lastIndex, ltLow.lastPrice, bar.index, ltLow.lastPrice, color=cBearColorK3, style=lineStyle(msOnChartK3), width=1, force_overlay=True)
            if stMSLblK3:
                box.new(ltLow.lastIndex, ltLow.lastPrice, bar.index, ltLow.lastPrice, NA(Color), text='CHoCH' if ltMS.type > 0 else 'BoS', text_color=cBearColorK3, text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_top, force_overlay=True)
                setType(ltMS, -1)
    oscTop = plot(100 if msOsc_Show or msDataK1 or msDataK2 or msDataK3 else na, 'OSC Top', NA(Color), display=display.none, editable=False)
    upperBand = plot(85 if msOsc_Show or msDataK1 or msDataK2 or msDataK3 else na, 'Overbought Level', NA(Color), display=display.none, editable=False)
    midLine = plot(50 if msOsc_Show or msDataK1 or msDataK2 or msDataK3 else na, 'Equilibrium Level', color.new(color.new('#787B86'), 50), display=display__ren__, editable=False)
    lowerBand = plot(15 if msOsc_Show or msDataK1 or msDataK2 or msDataK3 else na, 'Oversold Level', NA(Color), display=display.none, editable=False)
    oscBtm = plot(0 if msOsc_Show or msDataK1 or msDataK2 or msDataK3 else na, 'OSC Bottom', NA(Color), display=display.none, editable=False)
    fill(oscTop, upperBand, 100, 85, top_color=color.new(msBearColor, 100), bottom_color=color.new(msBearColor, 73), title='Overbought Fill')
    fill(lowerBand, oscBtm, 15, 0, top_color=color.new(msBullColor, 73), bottom_color=color.new(msBullColor, 100), title='Oversold Fill')
    stValue1, stValue2, stValue3 = collectData()
    msOSC = (msWeightK1 * nz(stValue1, 0) + msWeightK2 * nz(stValue2, 0) + msWeightK3 * nz(stValue3, 0)) / (msWeightK1 * (0 if na(stValue1) else 1) + msWeightK2 * (0 if na(stValue2) else 1) + msWeightK3 * (0 if na(stValue3) else 1))
    msPlot = plot(msOSC if msOsc_Show else na, 'Market Structure Oscillator', color.from_gradient(msOSC, 0, 100, msBearColor, msBullColor), 1, display=display__ren__)
    change_1 = ta.change(math.sign(msOSC - 50))
    if oscSig and change_1 > 0:
        label.new(bar.index, bar.low, '⦁', color=NA(Color), textcolor=oBullColor, style=label.style_label_up, force_overlay=True)
    change_2 = ta.change(math.sign(msOSC - 50))
    if oscSig and change_2 < 0:
        label.new(bar.index, bar.high, '⦁', color=NA(Color), textcolor=oBearColor, style=label.style_label_down, force_overlay=True)
    plot(stValue1 if msDataK1 else na, 'Short Term Oscillator', msColorK1, 1, display=display__ren__)
    plot(stValue2 if msDataK2 else na, 'Intermediate Term Oscillator', msColorK2, 1, display=display__ren__)
    plot(stValue3 if msDataK3 else na, 'Long Term Oscillator', msColorK3, 1, display=display__ren__)
    cycleFast = msOSC - ta.ema(msOSC, cyc_Smooth) + 50 if cycleOpt else 50
    plotcandle(50.0, 50.0, 50.0, cycleFast, 'Cycle Histogram', cBullColor if cycleFast > 50 else cBearColor, display=display__ren__, bordercolor=(cBullColor if cycleFast > 50 else cBearColor) if cycleOpt else color.gray)
    change_3 = ta.change(math.sign(cycleFast - 50))
    if cycleSig and change_3 > 0:
        label.new(bar.index, bar.low, '⦁', color=NA(Color), textcolor=sBullColor, style=label.style_label_up, force_overlay=True)
    change_4 = ta.change(math.sign(cycleFast - 50))
    if cycleSig and change_4 < 0:
        label.new(bar.index, bar.high, '⦁', color=NA(Color), textcolor=sBearColor, style=label.style_label_down, force_overlay=True)
    fill(msPlot, midLine, 100, 60 if cycleOpt else 50, top_color=color.new(msBullColor, 0), bottom_color=color.new(msBullColor, 100), title='Bullish Gradient Fill')
    fill(msPlot, midLine, 40 if cycleOpt else 50, 0, top_color=color.new(msBearColor, 100), bottom_color=color.new(msBearColor, 0), title='Bearish Gradient Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
