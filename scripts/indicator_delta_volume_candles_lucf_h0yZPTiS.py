"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, close, color, display, fill,
    fixnan, high, input, label, low, math, na, nz, open, plot, plotcandle, request, script, string,
    syminfo, ta, table, timeframe, volume
)
from pynecore.types import Color, NA, Persistent, Series, Table
import lib.LucF.ta.v3 as LucfTa
import lib.PineCoders.Time.v2 as PCtime
import lib.PineCoders.lower_tf.v4 as PCltf

GRAY: Color = color.new('#808080')
GREEN: Color = color.new('#008000')
LIME: Color = color.new('#00FF00')
MAROON: Color = color.new('#800000')
ORANGE: Color = color.new('#FF8000')
PINK: Color = color.new('#FF0080')
RED: Color = color.new('#FF0000')
REDLITE: Color = color.new('#EF535018')
YELLOW: Color = color.new('#FFFF00')
CB0: str = 'None'
CB1: str = 'Bar Balance'
CB2: str = 'Average Balance'
CB3: str = 'Momentum Balance'
CB4: str = 'Relative Balance'
CB5: str = 'Percent Balance'
CB6: str = 'Combined Balances'
CB8: str = 'Bar polarity (like normal candles)'
TB0: str = 'None'
TB1: str = 'Up volume on top, down volume at bottom'
TB2: str = 'Volume delta on winning side only'
TB3: str = 'Momentum Balance on winning side only'
SR0: str = 'Each candle\'s body size'
SR1: str = 'Average body size of last 100 bars'
DL0: str = 'None'
DL1: str = 'Body divergences'
DL2: str = 'Top and bottom divergences'
DL3: str = 'Both divergences'
HL0: str = 'Full Range'
HL1: str = 'Top and Bottom'
HL2: str = 'Open and Close'
HL3: str = 'High and Low'
DV0: str = 'Range: Full'
DV1: str = 'Range: Top to Bottom'
DV2: str = 'Range: Open to Close'
DV3: str = 'Range: High to Low'
DV4: str = 'Level: Top or Bottom'
DV5: str = 'Level: High or Low'
DV6: str = 'Level: Close'
LTF1: str = 'Covering most chart bars (least precise)'
LTF2: str = 'Covering some chart bars (less precise)'
LTF3: str = 'Covering less chart bars (more precise)'
LTF4: str = 'Covering few chart bars (very precise)'
LTF5: str = 'Covering the least chart bars (most precise)'
LTF6: str = '~12 intrabars per chart bar'
LTF7: str = '~24 intrabars per chart bar'
LTF8: str = '~50 intrabars per chart bar'
LTF9: str = '~100 intrabars per chart bar'
LTF10: str = '~250 intrabars per chart bar'
TD1: str = 'Both'
TD2: str = 'Longs Only'
TD3: str = 'Shorts Only'
TT_BODIES: str = "These choices determine the coloring scheme used for candle bodies only, i.e., not the wicks nor the tops and bottoms.  \n\nWhen 'Gradient' is selected, a color gradient is calculated on the advances/declines of the signal used. The gradient has no effect when '" + CB8 + "' is selected). \n\nUse 'None' if you do not want the indicator to display candle bodies and wicks so you can use your own candles on charts."
TT_BODY_DIVS: str = 'Body divergences occur on discrepancies between the polarity of the bar and that of the specified balance,  which is independent from the one used above to determine the color of bodies.'
TT_EMPTY_BODIES: str = 'Coloring only the body of bars where volume increases can help you identify more significant bars. \n\nIf you choose to color bodies on divergences, that setting has precedence over this one.'
TT_BORDERS: str = 'Borders and wicks are always colored using the bar\'s polarity.'
TT_TB: str = ''
TT_TB_SIZE: str = 'This determines the baseline from which the size of tops and bottoms is calculated. \n\nWith the first choice, the body size of each candle is used as the baseline. With the second choice an average is used, making it easier to appraise the relative size of consecutive tops and bottomes, as their size will be calculated from a more stable baseline.'
TT_TB_DIVS: str = 'Top and bottom divergences occur on discrepancies between the polarity of the bar and that of the specified balance.'
TT_DL: str = 'This controls the type of divergences that will trigger the creation of a new set of levels if the previous levels were breached, or the expansion of the current levels if they were not breached yet.'
TT_DL_LEVELS: str = 'The first selection here controls the levels used to establish or resize levels when a divergence occurs. The second choice determines which values must reach outside divergence levels for them to be breached. \n\nTogether, these settings control the sensitivity of the levels.'
TT_BRITE: str = '0 (darkest) — 100 (brightest).'
TT_LTF: str = 'Your selection here controls how many intrabars will be analyzed for each chart bar.  The more intrabars you analyze, the more precise the calculations will be, but the less chart bars will be covered by the indicator\'s calculations because a maximum of 100K intrabars can be analyzed. \n\nThe first five choices determine the lower timeframe used for intrabars using how much chart coverage you want. The last five choices allow you to select approximately how many intrabars you want analyzed per chart bar.'
TT_LTF_BOX: str = 'Displays the lower timeframe used to access intrabars and intrabar statistics in a configurable position and color.'
TT_MARKER1: str = 'A bump up occurs when:  \n• The bar\'s polarity is up. \n• The `close` is higher than the previous bar\'s `close`. \n• Bar Balance (VD) is positive. \n• Up volume is greater than the EMA of up volume calculated in the Average Balance. \n• Up volume is greater than the previous bar\'s up volume. \n\nA bump down occurs when: \n• The bar\'s polarity is down. \n• The `close` is lower than the previous bar\'s `close`. \n• Bar Balance (VD) is negative. \n• Down volume is greater than the EMA of down volume calculated in the Average Balance. \n• Down volume is greater (more negative) than the previous bar\'s down volume.'
TT_MARKER2: str = 'A double bump is two consecutive bumps up or down.'
TT_MARKER3: str = 'A divergence is confirmed up/dn when the chosen balance is up/dn on the previous bar when that bar was dn/up, and this bar is up/dn.'
TT_MARKER4: str = 'Balance shifts occur when the chosen balance crosses into bull/bear territory.'
TT_MARKER5: str = 'Marker bias shifts occur when it crosses into bull/bear territory.'
TT_MARKER6: str = 'All balances are bull or bear.'
TT_TEXT_UP: str = 'This text will replace the alert message for up alerts.'
TT_TEXT_DN: str = 'This text will replace the alert message for down alerts.'
TT_VOL_DISC: str = 'This displays a background coloron historical bars to indicate that the volume from the chart\'s timeframe does not match the sum of intrabar volume. \n\nDiscrepancies occur when the two values differ by more than the percentage in the \'Tolerance\' field, where \'1\' indicates 1%. \n\nSee my \'Volume X-ray\' indicator\'s description for an explanation of why this occurs.'
GP00: str = 'Normal Candles'
GP01: str = 'Volume Tops & Bottoms'
GP02: str = 'Divergence Channel'
GP03: str = 'Background'
GP04: str = 'Intrabars'
GP05: str = 'Markers'
GP06: str = 'Periods'


@script.indicator('Delta Volume Candles [LucF]', 'Delta Volume Candles', True, max_labels_count=500, linktoseries=True, na_bool=True)
def main(
    bodyColorCalcInput=input.string(CB8, 'Color bodies on', inline='bodies', group=GP00, options=(CB0, CB8, CB1, CB2, CB3, CB4, CB5, CB6)),
    bodyUpColorInput=input.color(GREEN, '', inline='bodies', group=GP00),
    bodyDnColorInput=input.color(MAROON, '', inline='bodies', group=GP00, tooltip=TT_BODIES),
    bodyGradientInput=input.bool(False, 'Gradient', inline='bodies', group=GP00),
    bodyShowDivInput=input.bool(False, 'Body divergences calculated on', inline='bodyDivs', group=GP00),
    bodyDivModeInput=input.string(CB1, '', inline='bodyDivs', group=GP00, options=(CB0, CB1, CB2, CB3, CB4, CB5, CB6)),
    bodyDivColorInput=input.color(YELLOW, '', inline='bodyDivs', group=GP00, tooltip=TT_BODY_DIVS),
    bodyHollowOnDecVolInput=input.bool(True, 'Empty bodies on decreasing volume', group=GP00, tooltip=TT_EMPTY_BODIES),
    borderWickUpColorInput=input.color(GREEN, 'Borders & wicks ', inline='b&w', group=GP00),
    borderWickDnColorInput=input.color(MAROON, '', inline='b&w', group=GP00, tooltip=TT_BORDERS),
    topBotRefModeInput=input.string(SR1, 'Size tops and bottoms relative to', inline='ref', group=GP01, options=(SR0, SR1), tooltip=TT_TB_SIZE),
    topBotModeInput=input.string(TB2, 'Display', inline='tbCalc', group=GP01, options=(TB0, TB1, TB2, TB3)),
    topBotBodyUpColorInput=input.color(LIME, 'Fills: ', inline='tbCalc', group=GP01),
    topBotBodyDnColorInput=input.color(RED, '', inline='tbCalc', group=GP01),
    topBotWickUpColorInput=input.color(LIME, 'Borders: ', inline='tbCalc', group=GP01),
    topBotWickDnColorInput=input.color(PINK, '', inline='tbCalc', group=GP01, tooltip=TT_TB),
    topBotShowDivInput=input.bool(False, 'Top & bottom divergences calculated on', inline='tbDivs', group=GP01),
    topBotDivModeInput=input.string(CB2, '', inline='tbDivs', group=GP01, options=(CB0, CB1, CB2, CB3, CB4, CB5, CB6)),
    topBotDivColorInput=input.color(ORANGE, '', inline='tbDivs', group=GP01, tooltip=TT_TB_DIVS),
    showMasInput=input.bool(False, 'Show EMAs of tops/bottoms', inline='mas', group=GP01),
    maUpColorInput=input.color(GREEN, '', inline='mas', group=GP01),
    maDnColorInput=input.color(MAROON, '', inline='mas', group=GP01),
    maFillCalcInput=input.string(CB1, 'Color the EMA channel on', inline='masColor', group=GP01, options=(CB0, CB1, CB2, CB3, CB4, CB5, CB6)),
    maFillUpColorInput=input.color(GREEN, '', inline='masColor', group=GP01),
    maFillDnColorInput=input.color(MAROON, '', inline='masColor', group=GP01),
    divLevelsModeInput=input.string(DL0, 'Draw levels on', inline='divsLevels', group=GP02, options=(DL0, DL1, DL2, DL3)),
    divLevelsBullColorInput=input.color(GREEN, '', inline='divsLevels', group=GP02),
    divLevelsBearColorInput=input.color(MAROON, '', inline='divsLevels', group=GP02),
    divLevelsNeutColorInput=input.color(GRAY, '', inline='divsLevels', group=GP02, tooltip=TT_DL),
    divLevelsModeHiLoInput=input.string(HL2, 'Hi/Lo levels', inline='hiLoLevels', group=GP02, options=(HL0, HL1, HL2, HL3)),
    divLevelsModeHiLoRefInput=input.string(DV6, 'Breach reference', inline='hiLoLevels', group=GP02, options=(DV0, DV1, DV2, DV3, DV4, DV5, DV6), tooltip=TT_DL_LEVELS),
    divLevelsFillInput=input.bool(False, 'Fill', inline='fillLevels', group=GP02),
    __input_32__=input.int(50, '🔆', inline='fillLevels', group=GP02, minval=0, maxval=100, step=5, tooltip=TT_BRITE),
    bgCalcInput=input.string(CB0, 'Color On', inline='31', group=GP03, options=(CB0, CB1, CB2, CB3, CB4, CB5, CB6)),
    bgUpColorInput=input.color(GREEN, '', inline='31', group=GP03),
    bgDnColorInput=input.color(MAROON, '', inline='31', group=GP03),
    __input_36__=input.int(30, '🔆', inline='31', group=GP03, minval=0, maxval=100, step=5, tooltip=TT_BRITE),
    volDiscShowInput=input.bool(True, 'Show volume discrepancies', inline='volDiscs', group=GP03),
    volDiscColorInput=input.color(REDLITE, '', inline='volDiscs', group=GP03),
    __input_39__=input.float(1.0, 'Tolerance (%)', inline='volDiscs', group=GP03, minval=0.0, step=0.25, tooltip=TT_VOL_DISC),
    ltfModeInput=input.string(LTF9, 'Intrabar precision', options=(LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10), group=GP04, tooltip=TT_LTF),
    showInfoBoxInput=input.bool(True, 'Show information box', group=GP04, tooltip=TT_LTF_BOX),
    infoBoxSizeInput=input.string('small', 'Size ', inline='infoBox', group=GP04, options=('tiny', 'small', 'normal', 'large', 'huge', 'auto')),
    infoBoxYPosInput=input.string('bottom', '↕', inline='infoBox', group=GP04, options=('top', 'middle', 'bottom')),
    infoBoxXPosInput=input.string('right', '↔', inline='infoBox', group=GP04, options=('left', 'center', 'right')),
    infoBoxColorInput=input.color(color.gray, '', inline='infoBox', group=GP04),
    infoBoxTxtColorInput=input.color(color.black, 'T', inline='infoBox', group=GP04),
    markerDirInput=input.string(TD1, 'Direction', inline='dir', group=GP05, options=(TD1, TD2, TD3)),
    showMarker1Input=input.bool(False, 'Marker 1: bumps', group=GP05, tooltip=TT_MARKER1),
    showMarker2Input=input.bool(False, 'Marker 2: double bumps', group=GP05, tooltip=TT_MARKER2),
    showMarker3Input=input.bool(False, 'Marker 3: divergence confirmations', inline='m3', group=GP05, tooltip=TT_MARKER3),
    marker3ModeInput=input.string(CB1, 'on', inline='m3', group=GP05, options=(CB1, CB2, CB3, CB4, CB5, CB6)),
    showMarker4Input=input.bool(False, 'Marker 4: Balance shifts', inline='m4', group=GP05, tooltip=TT_MARKER4),
    marker4ModeInput=input.string(CB2, 'on', inline='m4', group=GP05, options=(CB2, CB3, CB4, CB5, CB6)),
    showMarker5Input=input.bool(False, 'Marker 5: Markers Bias shifts', group=GP05, tooltip=TT_MARKER5),
    showMarker6Input=input.bool(False, 'Marker 6: All balances agree', group=GP05, tooltip=TT_MARKER6),
    alertMsgUpInput=input.text_area('', 'Up alert message', group=GP05, tooltip=TT_TEXT_UP),
    alertMsgDnInput=input.text_area('', 'Down alert message', group=GP05, tooltip=TT_TEXT_DN),
    balAvgPeriodInput=input.int(50, 'Average Balance', group=GP06, minval=2),
    balMomPeriodInput=input.int(14, 'Momentum Balance', group=GP06, minval=2),
    balRelPeriodInput=input.int(14, 'Relative Balance', group=GP06, minval=1),
    balPctPeriodInput=input.int(14, 'Percent Balance', group=GP06, minval=1),
    biasPeriodInput=input.int(14, 'Markers Bias', group=GP06, minval=2),
    topBotMasPeriodInput=input.int(14, 'Tops/Bottoms EMAs', group=GP06, minval=1)
):
    GENERAL_UP_HI: Color = LIME
    GENERAL_DN_HI: Color = RED
    GENERAL_UP_LO: Color = GREEN
    GENERAL_DN_LO: Color = MAROON
    GENERAL_NT: Color = GRAY
    ON: str = 'On'
    OFF: str = 'Off'
    CB7: str = 'Markers Bias'
    divLevelsFillBriteInput: float = 100 - __input_32__
    bgBriteInput: float = 100 - __input_36__
    volDiscToleranceInput: float = __input_39__ / 100
    intrabarTf: str = PCltf.ltf(ltfModeInput, LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10)
    ltfVolumesUp, ltfVolumesDn = request.security_lower_tf(syminfo.tickerid, intrabarTf, LucfTa.upDnIntrabarVolumesByPolarity())
    ltfVolUp: float = nz(array.sum(ltfVolumesUp))
    ltfVolDn: float = nz(array.sum(ltfVolumesDn))
    intrabars, chartBarsCovered, avgIntrabars = PCltf.ltfStats(ltfVolumesUp)
    chartBars: int = bar_index + 1
    barUp: bool = close > open
    barDn: bool = close < open
    closeUp: bool = ta.rising(close, 1)
    closeDn: bool = ta.falling(close, 1)
    volUp: bool = ta.rising(volume, 1)
    volB: float = ltfVolUp
    volS: float = -ltfVolDn
    volT: float = volB + volS
    intrabarVolumeIsAvailable: bool = ta.cum(nz(volT)) != 0
    balBar: float = volB - volS
    balBarBull: bool = balBar > 0
    balBarBear: bool = balBar < 0
    balAvgBMa: float = ta.ema(volB, balAvgPeriodInput)
    balAvgSMa: float = ta.ema(volS, balAvgPeriodInput)
    balAvg: float = balAvgBMa - balAvgSMa
    balAvgBull: bool = balAvg > 0
    balAvgBear: bool = balAvg < 0
    balMomBMa: float = ta.sma(volB, balAvgPeriodInput * 2)
    balMomSMa: float = ta.sma(volS, balAvgPeriodInput * 2)
    balMomBMaDelta: float = balAvgBMa - balMomBMa
    balMomSMaDelta: float = balAvgSMa - balMomSMa
    balMomDeltaDelta: float = balMomBMaDelta - balMomSMaDelta
    balMom: float = ta.rsi(balMomDeltaDelta, balMomPeriodInput) - 50
    balMomBull: bool = balMom > 0
    balMomBear: bool = balMom < 0
    volUpDelta: float = math.max(0, volB - balAvgBMa)
    volDnDelta: float = math.max(0, volS - balAvgSMa)
    balRel: float = ta.alma(volUpDelta - volDnDelta, balRelPeriodInput, 0.85, 6)
    balRelBull: bool = balRel > 0
    balRelBear: bool = balRel < 0
    balPct: float = ta.alma(100 * balBar / volume, balPctPeriodInput, 0.85, 6)
    balPctBull: bool = balPct > 0
    balPctBear: bool = balPct < 0
    BALANCES_QTY: int = 5
    balAll: float = LucfTa.zeroOne(balBarBull) + LucfTa.zeroOne(balAvgBull) + LucfTa.zeroOne(balMomBull) + LucfTa.zeroOne(balRelBull) + LucfTa.zeroOne(balPctBull) - LucfTa.zeroOne(balBarBear) - LucfTa.zeroOne(balAvgBear) - LucfTa.zeroOne(balMomBear) - LucfTa.zeroOne(balRelBear) - LucfTa.zeroOne(balPctBear)
    balAllBull: bool = balAll > 0
    balAllBear: bool = balAll < 0
    bodyTop: float = math.max(close, open)
    bodyBot: float = math.min(close, open)
    bodySize: float = bodyTop - bodyBot
    __block_result__ = na
    __switch__ = topBotRefModeInput
    if __switch__ == SR0:
        __block_result__ = bodySize
    elif __switch__ == SR1:
        __block_result__ = ta.sma(bodySize, 100)
    else:
        __block_result__ = na
    referenceSize: float = __block_result__
    __block_result_1__ = na
    __switch__ = topBotModeInput
    if __switch__ == TB1:
        __block_result_1__ = volB / volT
    elif __switch__ == TB2:
        __block_result_1__ = balBar / volT if balBar > 0 else na
    elif __switch__ == TB3:
        __block_result_1__ = balAll / BALANCES_QTY if balAll > 0 else na
    else:
        __block_result_1__ = na
    topFactor: float = __block_result_1__
    __block_result_2__ = na
    __switch__ = topBotModeInput
    if __switch__ == TB1:
        __block_result_2__ = volS / volT
    elif __switch__ == TB2:
        __block_result_2__ = math.abs(balBar / volT) if balBar < 0 else na
    elif __switch__ == TB3:
        __block_result_2__ = math.abs(balAll / BALANCES_QTY) if balAll < 0 else na
    else:
        __block_result_2__ = na
    botFactor: float = __block_result_2__
    volTop: float = bodyTop + referenceSize * topFactor
    volBot: float = bodyBot - referenceSize * botFactor
    def markerSignal(balance: str):
        __block_result_3__ = na
        __switch__ = balance
        if __switch__ == CB1:
            __block_result_3__ = balBar
        elif __switch__ == CB2:
            __block_result_3__ = balAvg
        elif __switch__ == CB3:
            __block_result_3__ = balMom
        elif __switch__ == CB4:
            __block_result_3__ = balRel
        elif __switch__ == CB5:
            __block_result_3__ = balPct
        elif __switch__ == CB6:
            __block_result_3__ = balAll
        else:
            __block_result_3__ = na
        result: float = __block_result_3__
        return result

    def divFromMode(balance: str):
        result: bool = math.sign(markerSignal(balance)) != math.sign(close - open)
        return result

    doLongs: bool = markerDirInput == TD1 or markerDirInput == TD2
    doShorts: bool = markerDirInput == TD1 or markerDirInput == TD3
    rising_1 = ta.rising(volB, 1)
    bumpUp: Series[bool] = barUp and closeUp and balBarBull and (volB > balAvgBMa) and rising_1
    rising_2 = ta.rising(volS, 1)
    bumpDn: Series[bool] = barDn and closeDn and balBarBear and (volS > balAvgSMa) and rising_2
    div: Series[bool] = divFromMode(marker3ModeInput)
    c1U: bool = bumpUp
    c1D: bool = bumpDn
    c2U: bool = bumpUp and bumpUp[1]
    c2D: bool = bumpDn and bumpDn[1]
    c3U: bool = div[1] and barUp and (not div)
    c3D: bool = div[1] and barDn and (not div)
    c4U: bool = ta.crossover(markerSignal(marker4ModeInput), 0)
    c4D: bool = ta.crossunder(markerSignal(marker4ModeInput), 0)
    cUps: float = LucfTa.zeroOne(c1U) + LucfTa.zeroOne(c2U) + LucfTa.zeroOne(c3U) + LucfTa.zeroOne(c4U)
    cDns: float = LucfTa.zeroOne(c1D) + LucfTa.zeroOne(c2D) + LucfTa.zeroOne(c3D) + LucfTa.zeroOne(c4D)
    balMrk: float = math.sum(cUps - cDns, biasPeriodInput)
    balMrkBull: bool = balMrk > 0
    balMrkBear: bool = balMrk < 0
    c5U: bool = ta.crossover(balMrk, 0)
    c5D: bool = ta.crossunder(balMrk, 0)
    c6U: bool = balAll == BALANCES_QTY
    c6D: bool = balAll == -BALANCES_QTY
    a1U: bool = showMarker1Input and doLongs and c1U
    a1D: bool = showMarker1Input and doShorts and c1D
    a2U: bool = showMarker2Input and doLongs and c2U
    a2D: bool = showMarker2Input and doShorts and c2D
    a3U: bool = showMarker3Input and doLongs and c3U
    a3D: bool = showMarker3Input and doShorts and c3D
    a4U: bool = showMarker4Input and doLongs and c4U
    a4D: bool = showMarker4Input and doShorts and c4D
    a5U: bool = showMarker5Input and doLongs and c5U
    a5D: bool = showMarker5Input and doShorts and c5D
    a6U: bool = showMarker6Input and doLongs and c6U
    a6D: bool = showMarker6Input and doShorts and c6D
    divFromMode_1 = divFromMode(bodyDivModeInput)
    bodyDiv: bool = intrabarVolumeIsAvailable and divFromMode_1
    divFromMode_2 = divFromMode(topBotDivModeInput)
    topBotDiv: bool = intrabarVolumeIsAvailable and divFromMode_2
    __block_result_4__ = na
    __switch__ = divLevelsModeInput
    if __switch__ == DL1:
        __block_result_4__ = bodyDiv
    elif __switch__ == DL2:
        __block_result_4__ = topBotDiv
    elif __switch__ == DL3:
        __block_result_4__ = bodyDiv or topBotDiv
    else:
        __block_result_4__ = False
    divLevelsDiv: bool = __block_result_4__
    __block_result_5__ = na
    __switch__ = divLevelsModeHiLoInput
    if __switch__ == HL0:
        __block_result_5__ = math.max(nz(volTop, high), high)
    elif __switch__ == HL1:
        __block_result_5__ = nz(volTop, high)
    elif __switch__ == HL2:
        __block_result_5__ = bodyTop
    elif __switch__ == HL3:
        __block_result_5__ = high
    else:
        __block_result_5__ = high
    divLevelsHiNew: float = __block_result_5__
    __block_result_6__ = na
    __switch__ = divLevelsModeHiLoInput
    if __switch__ == HL0:
        __block_result_6__ = math.min(nz(volBot, low), low)
    elif __switch__ == HL1:
        __block_result_6__ = nz(volBot, low)
    elif __switch__ == HL2:
        __block_result_6__ = bodyBot
    elif __switch__ == HL3:
        __block_result_6__ = low
    else:
        __block_result_6__ = low
    divLevelsLoNew: float = __block_result_6__
    __block_result_7__ = na
    __switch__ = divLevelsModeHiLoRefInput
    if __switch__ == DV0:
        __block_result_7__ = math.min(nz(volBot, low), low)
    elif __switch__ == DV1:
        __block_result_7__ = nz(volBot, low)
    elif __switch__ == DV2:
        __block_result_7__ = bodyBot
    elif __switch__ == DV3:
        __block_result_7__ = low
    elif __switch__ == DV4:
        __block_result_7__ = nz(volTop, high)
    elif __switch__ == DV5:
        __block_result_7__ = high
    elif __switch__ == DV6:
        __block_result_7__ = close
    else:
        __block_result_7__ = close
    divLevelsHiRef: float = __block_result_7__
    __block_result_8__ = na
    __switch__ = divLevelsModeHiLoRefInput
    if __switch__ == DV0:
        __block_result_8__ = math.max(nz(volTop, high), high)
    elif __switch__ == DV1:
        __block_result_8__ = nz(volTop, high)
    elif __switch__ == DV2:
        __block_result_8__ = bodyTop
    elif __switch__ == DV3:
        __block_result_8__ = high
    elif __switch__ == DV4:
        __block_result_8__ = nz(volBot, low)
    elif __switch__ == DV5:
        __block_result_8__ = low
    elif __switch__ == DV6:
        __block_result_8__ = close
    else:
        __block_result_8__ = close
    divLevelsLoRef: float = __block_result_8__
    divLevelsHi, divLevelsLo, divLevelsHState, divLevelsLState, divLevelsBreached, divLevelsChanged, _, _ = LucfTa.divergenceChannel(divLevelsDiv, divLevelsHiNew, divLevelsLoNew, divLevelsHiRef, divLevelsLoRef)
    divLevelsNState: bool = not (divLevelsHState or divLevelsLState)
    def gradientSteps(signalCalc: str):
        result: int = 4 if signalCalc == CB8 else 8
        return result

    def signal(signalCalc: str):
        __block_result_9__ = na
        __switch__ = signalCalc
        if __switch__ == CB1:
            __block_result_9__ = balBar
        elif __switch__ == CB2:
            __block_result_9__ = balAvg
        elif __switch__ == CB3:
            __block_result_9__ = balMom
        elif __switch__ == CB4:
            __block_result_9__ = balRel
        elif __switch__ == CB5:
            __block_result_9__ = balPct
        elif __switch__ == CB6:
            __block_result_9__ = balAll
        elif __switch__ == CB7:
            __block_result_9__ = balMrk
        elif __switch__ == CB8:
            __block_result_9__ = close - open
        else:
            __block_result_9__ = na
        result: float = __block_result_9__
        return result

    plotLocations = display.data_window + display.status_line
    plot(balBar, 'Volume Delta', GENERAL_UP_HI if balBarBull else GENERAL_DN_HI, display=plotLocations)
    plot(100 * balBar / volT, 'Volume Delta %', GENERAL_UP_HI if balBarBull else GENERAL_DN_HI, display=plotLocations)
    plot(volB, 'Up Volume', GENERAL_UP_HI if balBarBull else GENERAL_UP_LO, display=plotLocations)
    plot(volS, 'Dn Volume', GENERAL_DN_HI if balBarBear else GENERAL_DN_LO, display=plotLocations)
    plot(volT, 'Intrabar Volume', GENERAL_UP_HI if balBarBull else GENERAL_DN_HI, display=plotLocations)
    plot(volume, 'Chart bar Volume', GENERAL_UP_HI if balBarBull else GENERAL_DN_HI, display=plotLocations)
    plot(na, '═════════════', GENERAL_NT, display=plotLocations)
    plot(balBar, 'Bar Balance', GENERAL_UP_HI if balBarBull else GENERAL_DN_HI, display=plotLocations)
    plot(balAvg, 'Average Balance', GENERAL_UP_HI if balAvgBull else GENERAL_DN_HI, display=plotLocations)
    plot(balMom, 'Momentum Balance ', GENERAL_UP_HI if balMomBull else GENERAL_DN_HI, display=plotLocations)
    plot(balRel, 'Relative Balance', GENERAL_UP_HI if balRelBull else GENERAL_DN_HI, display=plotLocations)
    plot(balPct, 'Percent Balance', GENERAL_UP_HI if balPctBull else GENERAL_DN_HI, display=plotLocations)
    plot(balAll, 'Combined Balances', GENERAL_UP_HI if balAllBull else GENERAL_DN_HI, display=plotLocations)
    plot(balMrk, 'Marker Bias', GENERAL_UP_HI if balMrkBull else GENERAL_DN_HI, display=plotLocations)
    plot(na, '═════════════', GENERAL_NT, display=plotLocations)
    plot(volTop, 'Top', GENERAL_UP_HI, display=plotLocations)
    plot(volBot, 'Bottom', GENERAL_DN_HI, display=plotLocations)
    divLevelsColor: Color = divLevelsBullColorInput if divLevelsHState else divLevelsBearColorInput if divLevelsLState else divLevelsNeutColorInput
    divLevelsHiPlot = plot(divLevelsHi if divLevelsModeInput != CB0 else na, 'Divergence Hi Level', na if divLevelsChanged else divLevelsColor)
    divLevelsLoPlot = plot(divLevelsLo if divLevelsModeInput != CB0 else na, 'Divergence Lo Level', na if divLevelsChanged else divLevelsColor)
    fill(divLevelsHiPlot, divLevelsLoPlot, color.new(divLevelsColor, divLevelsFillBriteInput) if divLevelsFillInput and (not divLevelsChanged) else na)
    borderBriteTop: Persistent[Color] = color.new(topBotBodyUpColorInput, 0)
    borderBriteBot: Persistent[Color] = color.new(topBotBodyDnColorInput, 0)
    buyWins: bool = nz(topFactor) > nz(botFactor)
    topsColor: Color = topBotDivColorInput if topBotShowDivInput and topBotDiv else topBotBodyUpColorInput if buyWins else na
    botsColor: Color = topBotDivColorInput if topBotShowDivInput and topBotDiv else na if buyWins else topBotBodyDnColorInput
    topsBorderColor: Color = topBotDivColorInput if topBotShowDivInput and topBotDiv else borderBriteTop if buyWins else topBotBodyUpColorInput
    botsBorderColor: Color = topBotDivColorInput if topBotShowDivInput and topBotDiv else topBotBodyDnColorInput if buyWins else borderBriteBot
    plotcandle(bodyTop, volTop, bodyTop, volTop, 'Tops', topsColor if buyWins else na, bordercolor=topBotWickUpColorInput, display=display.pane)
    plotcandle(bodyBot, volBot, bodyBot, volBot, 'Bottoms', na if buyWins else botsColor, bordercolor=topBotWickDnColorInput, display=display.pane)
    masFillColor: Color = LucfTa.gradientAdvDecPro(signal(maFillCalcInput), 0, gradientSteps(maFillCalcInput), color.new(maFillDnColorInput, 90), maFillDnColorInput, color.new(maFillUpColorInput, 90), maFillUpColorInput)
    topsPlot = plot(ta.ema(fixnan(volTop), topBotMasPeriodInput) if showMasInput else na, 'Tops MA', maUpColorInput)
    botsPlot = plot(ta.ema(fixnan(volBot), topBotMasPeriodInput) if showMasInput else na, 'Botttoms MA', maDnColorInput)
    fill(topsPlot, botsPlot, masFillColor)
    bodySignal: float = signal(bodyColorCalcInput)
    bodyBull: bool = bodySignal > 0
    bodyBear: bool = bodySignal < 0
    bodyGradientColor: Color = LucfTa.gradientAdvDecPro(bodySignal, 0, gradientSteps(bodyColorCalcInput), color.new(bodyDnColorInput, 90), bodyDnColorInput, color.new(bodyUpColorInput, 90), bodyUpColorInput)
    __block_result_10__ = na
    if bodyColorCalcInput == CB0:
        __block_result_10__ = na
    elif bodyShowDivInput and bodyDiv:
        __block_result_10__ = bodyDivColorInput
    elif bodyHollowOnDecVolInput and (not volUp):
        __block_result_10__ = na
    elif bodyColorCalcInput != CB8 and bodyGradientInput:
        __block_result_10__ = bodyGradientColor
    elif bodyBull:
        __block_result_10__ = bodyUpColorInput
    elif bodyBear:
        __block_result_10__ = bodyDnColorInput
    else:
        __block_result_10__ = na
    bodyColor: Color = __block_result_10__
    __block_result_11__ = na
    if bodyColorCalcInput == CB0:
        __block_result_11__ = na
    elif barUp:
        __block_result_11__ = borderWickUpColorInput
    else:
        __block_result_11__ = borderWickDnColorInput
    bordersAndWicksColor: Color = __block_result_11__
    plotcandle(open, high, low, close, 'Candle Structure', color=bodyColor, wickcolor=bordersAndWicksColor, bordercolor=bordersAndWicksColor, display=display.pane)
    bgUpLoColor: Persistent[Color] = color.new(bgUpColorInput, math.max(90, bgBriteInput))
    bgUpHiColor: Persistent[Color] = color.new(bgUpColorInput, bgBriteInput)
    bgDnLoColor: Persistent[Color] = color.new(bgDnColorInput, math.max(90, bgBriteInput))
    bgDnHiColor: Persistent[Color] = color.new(bgDnColorInput, bgBriteInput)
    bgFillColor: Color = LucfTa.gradientAdvDecPro(signal(bgCalcInput), 0, gradientSteps(bgCalcInput), bgDnLoColor, bgDnHiColor, bgUpLoColor, bgUpHiColor)
    volDiscrepancy: bool = math.abs(volT - volume) / volume > volDiscToleranceInput
    bgcolor(volDiscColorInput if not barstate.isrealtime and volDiscShowInput and volDiscrepancy and (color.t(volDiscColorInput) != 100) else bgFillColor)
    if showInfoBoxInput and barstate.islastconfirmedhistory:
        infoBox: Persistent[Table] = table.new(infoBoxYPosInput + '_' + infoBoxXPosInput, 1, 1)
        infoBoxBgColor: Color = infoBoxColorInput
        txt: str = string.format('Uses intrabars at {0}\nAvg intrabars per chart bar: {1,number,#.##}\nChart bars covered: {2}\u200a/\u200a{3} ({4,number,percent})', PCtime.formattedNoOfPeriods(timeframe.in_seconds(intrabarTf) * 1000), avgIntrabars, chartBarsCovered, bar_index + 1, chartBarsCovered / (bar_index + 1))
        if avgIntrabars < 5:
            txt = 'This quantity of intrabars is dangerously small.\nResults will not be as reliable with so few.\n\n' + txt
            infoBoxBgColor = color.red
        elif not intrabarVolumeIsAvailable:
            txt = 'No intrabar volume exists for the symbol.\nCannot calculate values.\n\n' + txt
            infoBoxBgColor = color.red
        table.cell(infoBox, 0, 0, txt, text_color=infoBoxTxtColorInput, text_size=infoBoxSizeInput, bgcolor=infoBoxBgColor)
    if barstate.isconfirmed:
        topPos = math.max(nz(volTop), high)
        botPos = math.min(nz(volBot, 1e+16), low)
        markerCondUps: list[bool] = array.from_items(a1U, a2U, a3U, a4U, a5U, a6U)
        markerCondDns: list[bool] = array.from_items(a1D, a2D, a3D, a4D, a5D, a6D)
        labelMsgUp: str = ''
        labelMsgDn: str = ''
        triggerLong: bool = False
        triggerShort: bool = False
        for markerNo in pine_range(0, array.size(markerCondUps) - 1, 1):
            cUp: bool = array.get(markerCondUps, markerNo)
            cDn: bool = array.get(markerCondDns, markerNo)
            triggerLong = triggerLong or cUp
            triggerShort = triggerShort or cDn
            labelMsgUp = LucfTa.addTextIf(cUp, labelMsgUp, 'M' + string.tostring(markerNo + 1) + '▲', '\n')
            labelMsgDn = LucfTa.addTextIf(cDn, labelMsgDn, 'M' + string.tostring(markerNo + 1) + '▼', '\n')
        if triggerLong:
            alert(labelMsgUp if alertMsgUpInput == '' else alertMsgUpInput, alert.freq_once_per_bar)
            label.new(bar_index, botPos, labelMsgUp, style=label.style_label_up, color=NA(Color), textcolor=GENERAL_UP_HI)
        if triggerShort:
            alert(labelMsgDn if alertMsgDnInput == '' else alertMsgDnInput, alert.freq_once_per_bar)
            label.new(bar_index, topPos, labelMsgDn, style=label.style_label_down, color=NA(Color), textcolor=GENERAL_DN_HI)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)