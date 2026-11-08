"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, bar_index, barmerge, barstate, color, display, hline, input,
    label, location, math, na, nz, plot, plotchar, request, runtime, script, size, string, syminfo,
    ta, text, timeframe, xloc, yloc
)
from pynecore.types import Color, Label, Persistent, Series
import lib.TradingView.TechnicalRating.v3 as TVtr

BLUE: Color = color.new('#013BCA')
GOLD: Color = color.new('#CCCC00')
LIME: Color = color.new('#00FF00')
PINK: Color = color.new('#FF0080')
VIOLET: Color = color.new('#AA00FF')
WHITE: Color = color.new('#FFFFFF')
NEUTRAL: Color = color.new('#808080')
LEVEL_STRONG: float = 0.5
RT1: str = "MAs and Oscillators"
RT2: str = "MAs"
RT3: str = "Oscillators"
ON: str = "On"
OFF: str = "Off"
TD0: str = "None"
TD1: str = "Longs"
TD2: str = "Shorts"
TD3: str = "Longs and Shorts"
PS1: str = "Columns"
PS2: str = "Histogram"
PS3: str = "Area"
PS4: str = "Line"
B_TT: str = "The selected preset determines the base color for 'Buy' and 'Strong Buy' ratings."
S_TT: str = "The selected preset determines the base color for 'Sell' and 'Strong Sell' ratings."
TF_TT: str = "Select a timeframe that is higher than or equal to the chart's timeframe."
RP_TT: str = "If 'On', plotted ratings update during an open realtime bar on the specified timeframe, " + "and alerts occur as soon as possible. If the timeframe is higher than the chart's timeframe, " + 'new values that appear before an HTF bar closes become unavailable after the indicator reloads.\n\n' + "If 'Off', plotted HTF ratings update and alerts occur only after a realtime bar closes.\n\n"
MA_TT: str = 'Specifies the percentage weight of the MA rating for the total rating. The percentage weight of the oscillator ' + 'rating is 100 - MA weight. For example, if the value is 50, the MA and oscillator ratings have a weight of 50%. ' + "If the value is 60, the MA rating has 60% weight, and the oscillator rating's weight is 40% (100% - 60%)."
WD_TT: str = "The style and width of the plot. Width selection does not apply to the 'Columns' style."
DR_TT: str = "The alert direction. Visual markers for the alert conditions appear on the chart if the selection is not 'None'."
AT_TT: str = "If 'On' and the direction is 'Longs and Shorts', the indicator does not allow consecutive alerts for the same " + 'direction. A short alert must occur after a long alert before another long alert can occur. Likewise, a long ' + 'alert must occur after a short alert before another short alert can occur. This input does not affect the ' + 'other direction options.'
LU_TT: str = "The level that the rating value must cross to trigger a long alert. The default is the value for a 'Strong Buy' " + 'state. Use a value of 0 to not trigger long alerts on level crosses.'
LD_TT: str = "The level that the rating value must cross to trigger a short alert. The default is the value for a 'Strong Sell' " + 'state. Use a value of 0 to not trigger short alerts on level crosses.'
GD_TT: str = 'The cumulative advances or declines that must occur in the latest positive or negative ratings before an alert ' + "occurs. If the current rating has a 'Buy'/'Strong Buy' or 'Sell'/'Strong Sell' state, the counter " + 'increments by one if the value is less than 5 when the absolute rating rises, and decements by one when the ' + "absolute value falls. The counter value resets to 0 when the current rating has a 'Neutral' state. " + "The maximum counter value of 5 corresponds to the most opaque colors in the plot's gradients. Use a value of 0 " + 'to not trigger alerts after successive advances or declines.'
GRP1: str = "Calculations"
GRP2: str = "Ratings display"
GRP3: str = "Alerts and markers"


@script.indicator("Technical Ratings", "Ratings", precision=2)
def main(
    tfInput=input.timeframe("", "Timeframe", group=GRP1, tooltip=TF_TT),
    __input_1__=input.string(ON, "Repainting", group=GRP1, tooltip=RP_TT, options=(ON, OFF)),
    calcsInput=input.string(RT1, "Rating uses", group=GRP1, options=(RT2, RT3, RT1)),
    __input_3__=input.int(50, "Weight of MAs (%)", group=GRP1, tooltip=MA_TT, minval=0, maxval=100, step=10),
    styleInput=input.string(PS1, "Plot style", group=GRP2, inline="01", options=(PS1, PS2, PS3, PS4)),
    widthInput=input.int(1, "", group=GRP2, inline="01", minval=1, maxval=50, tooltip=WD_TT),
    presetInput1=input.string("1", "Bull color", group=GRP2, inline="02", options=("1", "2", "3"), tooltip=B_TT),
    colorInput1=input.color(LIME, "", group=GRP2, inline="02"),
    colorInput2=input.color(GOLD, "", group=GRP2, inline="02"),
    colorInput3=input.color(WHITE, "", group=GRP2, inline="02"),
    presetInput2=input.string("1", "Bear color", group=GRP2, inline="03", options=("1", "2", "3"), tooltip=S_TT),
    colorInput4=input.color(PINK, "", group=GRP2, inline="03"),
    colorInput5=input.color(VIOLET, "", group=GRP2, inline="03"),
    colorInput6=input.color(BLUE, "", group=GRP2, inline="03"),
    neutColorInput=input.color(NEUTRAL, "Neutral color", group=GRP2, inline="04"),
    dirInput=input.string(TD0, "Direction", group=GRP3, tooltip=DR_TT, options=(TD0, TD1, TD2, TD3)),
    __input_16__=input.string(ON, "Alternate longs & shorts", group=GRP3, tooltip=AT_TT, options=(ON, OFF)),
    levelUpInput=input.float(LEVEL_STRONG, "Longs level", group=GRP3, tooltip=LU_TT, minval=0, maxval=1, step=0.05),
    levelDnInput=input.float(-LEVEL_STRONG, "Shorts level", group=GRP3, tooltip=LD_TT, minval=-1, maxval=0, step=0.05),
    gradInput=input.float(0, "Cumulative adv./decl.", group=GRP3, tooltip=GD_TT, minval=0, maxval=5, step=1),
    alertUpInput=input.text_area("Long", "Alert message: Long", group=GRP3),
    alertDnInput=input.text_area("Short", "Alert message: Short", group=GRP3)
):
    GRAY: Color = color.new('#787B86')
    SILVER: Color = color.new('#B2B5BE')

    LEVEL_WEAK: float = 0.1

    FORMAT1: str = "  {0}{1}"
    FORMAT2: str = "      {0}"





    repaintInput: bool = __input_1__ == ON
    isWeighted: bool = calcsInput == RT1
    maInput: float = __input_3__ / 100

    showColorInput1: bool = presetInput1 == '1'
    showColorInput2: bool = presetInput1 == '2'
    showColorInput3: bool = presetInput1 == '3'
    showColorInput4: bool = presetInput2 == '1'
    showColorInput5: bool = presetInput2 == '2'
    showColorInput6: bool = presetInput2 == '3'

    alertsActive: bool = dirInput != TD0
    isBiDirectional: bool = dirInput == TD3
    longsActive: bool = dirInput == TD1
    shortsActive: bool = dirInput == TD2
    altInput: bool = __input_16__ == ON and dirInput == TD3

    def signalColor(gradient: int, bullColor: Color, bearColor: Color, neutralColor: Color):
        col: Color = bullColor if gradient > 0 else bearColor if gradient < 0 else neutralColor
        transp: float = 100 - math.abs(gradient) * 20
        transp = 75 if transp == 80 else transp
        return color.new(neutralColor, 75) if col == neutralColor else color.new(col, transp)

    def colorFromRating(rating: float, bullColor: Color, bearColor: Color, neutralColor: Color):
        __block_result__ = na
        if rating > LEVEL_STRONG:
            __block_result__ = color.new(bullColor, 20)
        elif rating > LEVEL_WEAK:
            __block_result__ = color.new(bullColor, 40)
        elif rating < -LEVEL_STRONG:
            __block_result__ = color.new(bearColor, 20)
        elif rating < -LEVEL_WEAK:
            __block_result__ = color.new(bearColor, 40)
        else:
            __block_result__ = color.new(neutralColor, 20)
        return __block_result__

    def textFromRating(rating: float):
        __block_result_1__ = na
        if rating > LEVEL_STRONG:
            __block_result_1__ = "Strong Buy"
        elif rating > LEVEL_WEAK:
            __block_result_1__ = "Buy"
        elif rating < -LEVEL_STRONG:
            __block_result_1__ = "Strong Sell"
        elif rating < -LEVEL_WEAK:
            __block_result_1__ = "Sell"
        else:
            __block_result_1__ = "Neutral"
        return __block_result_1__

    def print(txt: Series[str], lineNo: Series[int], txtColor: Series[Color]):
        lbl: Persistent[Label] = label.new(na, 0.0, '', xloc.bar_index, yloc.price, color.new('#00000000'), label.style_label_left, color.white, textalign=text.align_left)
        labelStr: Persistent[str] = string.repeat('\n', math.max(0, lineNo - 1)) + '{0}' + string.repeat('\n', math.max(0, 4 - lineNo))
        __block_result_2__ = na
        if barstate.islast:
            label.set_x(lbl, bar_index)
            label.set_text(lbl, string.format(labelStr, txt))
            __block_result_2__ = label.set_textcolor(lbl, txtColor)
        return __block_result_2__

    bullColor: Persistent[Color] = colorInput1 if showColorInput1 else colorInput2 if showColorInput2 else colorInput3 if showColorInput3 else color.new('#00000000')
    bearColor: Persistent[Color] = colorInput4 if showColorInput4 else colorInput5 if showColorInput5 else colorInput6 if showColorInput6 else color.new('#00000000')

    doLongs: Persistent[bool] = longsActive or isBiDirectional
    doShorts: Persistent[bool] = shortsActive or isBiDirectional

    __block_result_3__ = na
    __switch__ = styleInput
    if __switch__ == PS4:
        __block_result_3__ = plot.style_line
    elif __switch__ == PS3:
        __block_result_3__ = plot.style_area
    elif __switch__ == PS2:
        __block_result_3__ = plot.style_histogram
    else:
        __block_result_3__ = plot.style_columns
    style: Persistent = __block_result_3__

    title1: Persistent[str] = 'MAs' if calcsInput == RT2 else 'Osc' if calcsInput == RT3 else 'All'
    title2: Persistent[str] = 'Osc' if calcsInput == RT2 else 'MAs'
    title3: Persistent[str] = 'Osc' if calcsInput == RT1 else 'All'

    htfUsed: Persistent[bool] = timeframe.in_seconds(tfInput) > timeframe.in_seconds(timeframe.main_period)
    offset: Persistent[int] = 1 if htfUsed and (not repaintInput) else 0
    lookahead: Persistent = barmerge.lookahead_on if htfUsed and (not repaintInput) else barmerge.lookahead_off

    ratingOscChart: Series
    ratingMasChart: Series
    _, ratingOscChart, ratingMasChart = TVtr.calcRatingAll()

    ratingTotChart: Series[float] = nz(ratingMasChart * maInput) + nz(ratingOscChart * (1.0 - maInput))

    if barstate.isfirst and timeframe.in_seconds(timeframe.main_period) > timeframe.in_seconds(tfInput):
        errorStr: str = "The requested timeframe cannot be lower than the chart''s timeframe (''{0}'')."
        runtime.error(string.format(errorStr, timeframe.main_period))

    ratingTot, ratingOsc, ratingMas = request.security(syminfo.tickerid, tfInput, (ratingTotChart[offset], ratingOscChart[offset], ratingMasChart[offset]), lookahead=lookahead)

    totColor: Color = colorFromRating(ratingTot, bullColor, bearColor, neutColorInput)
    masColor: Color = colorFromRating(ratingMas, bullColor, bearColor, neutColorInput)
    oscColor: Color = colorFromRating(ratingOsc, bullColor, bearColor, neutColorInput)

    __block_result_4__ = (na, na, na, na, na, na)
    __switch__ = calcsInput
    if __switch__ == RT2:
        __block_result_4__ = (ratingMas, ratingOsc, ratingTot, masColor, oscColor, totColor)
    elif __switch__ == RT3:
        __block_result_4__ = (ratingOsc, ratingMas, ratingTot, oscColor, masColor, totColor)
    else:
        __block_result_4__ = (ratingTot, ratingMas, ratingOsc, totColor, masColor, oscColor)
    userRating, rating2, rating3, urColor, r2Color, r3Color = __block_result_4__

    condBuy: bool = userRating > LEVEL_WEAK
    condSell: bool = userRating < -LEVEL_WEAK
    valsBuy: float = userRating if condBuy else 0
    valsSell: float = userRating if condSell else 0
    risingBuys: int = TVtr.countRising(valsBuy)
    fallingSells: int = TVtr.countRising(valsSell)
    gradientLvl: Series[int] = risingBuys if condBuy else -fallingSells if condSell else 0
    signalColor__global__: Color = signalColor(gradientLvl, bullColor, bearColor, neutColorInput)

    plot(userRating, 'Rating', signalColor__global__, widthInput, style)

    hline(LEVEL_STRONG, 'Strong Buy level', color.new(bullColor, 50), hline.style_dashed)
    hline(LEVEL_WEAK, 'Buy level', color.new(bullColor, 65), hline.style_dashed)
    hline(0.0, 'Zero level', color.new(GRAY, 50), hline.style_dashed)
    hline(-LEVEL_WEAK, 'Sell level', color.new(bearColor, 75), hline.style_dashed)
    hline(-LEVEL_STRONG, 'Strong Sell level', color.new(bearColor, 50), hline.style_dashed)

    plot(ratingTot, 'All', totColor, display=display.data_window, editable=False)
    plot(ratingMas, 'MAs', masColor, display=display.data_window, editable=False)
    plot(ratingOsc, 'Oscillators', oscColor, display=display.data_window, editable=False)
    plot(na, '═══════', totColor, display=display.data_window, editable=False)

    print(string.format(FORMAT1, title1, ':'), 1, SILVER)
    print(string.format(FORMAT1, title2, ':'), 2, GRAY)
    print(string.format(FORMAT1, title3, ':'), 3, GRAY)
    print(string.format(FORMAT2, textFromRating(userRating)), 1, urColor)
    print(string.format(FORMAT2, textFromRating(rating2)), 2, r2Color)
    print(string.format(FORMAT2, textFromRating(rating3)), 3, r3Color)

    lastDir: Persistent[int] = 0
    xUp: bool = ta.crossover(userRating, levelUpInput) and levelUpInput != 0
    xDn: bool = ta.crossunder(userRating, levelDnInput) and levelDnInput != 0
    gUp: bool = gradInput != 0 and gradientLvl == gradInput and (gradientLvl[1] < gradInput)
    gDn: bool = gradInput != 0 and gradientLvl == -gradInput and (gradientLvl[1] > -gradInput)
    allowLong: bool = not altInput or lastDir == 0 or lastDir == -1
    allowShort: bool = not altInput or lastDir == 0 or lastDir == 1
    allowAlert: bool = repaintInput or (htfUsed and barstate.isnew) or (not htfUsed and barstate.isconfirmed)
    triggerLong: bool = allowAlert and (xUp or gUp) and allowLong and doLongs
    triggerShort: bool = allowAlert and (xDn or gDn) and allowShort and doShorts

    if triggerLong:
        alert(alertUpInput, alert.freq_once_per_bar)
        lastDir = 1
    elif triggerShort:
        alert(alertDnInput, alert.freq_once_per_bar)
        lastDir = -1

    hline(levelUpInput if doLongs else na, 'Long level', na if levelUpInput == 0 else bullColor, hline.style_dotted)
    hline(levelDnInput if doShorts else na, 'Short level', na if levelDnInput == 0 else bearColor, hline.style_dotted)

    plot(gradientLvl, 'Advances/Declines', signalColor__global__, display=display.data_window, editable=False)

    plotchar(triggerLong, 'Long marker', '▲', location.bottom, color.new(bullColor, 0), size=size.tiny)
    plotchar(triggerShort, 'Short marker', '▼', location.top, color.new(bearColor, 0), size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)