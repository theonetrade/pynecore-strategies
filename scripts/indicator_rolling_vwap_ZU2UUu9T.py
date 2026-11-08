"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    barstate, color, fill, hlc3, input, math, na, nz, plot, runtime, script,
    string, ta, table, timeframe, volume
)
from pynecore.types import Series, Table
import lib.PineCoders.ConditionalAverages.v2 as pc

TT_SRC: str = "The source series for which to calculate the RVWAP. The default is the average of the high, low, and close prices."
TT_WIN: str = "By default, the indicator selects the rolling period for the RVWAP automatically based on the chart's timeframe. " + 'When this checkbox is selected, the rolling period is the total span from the days, hours, and minutes ' + 'specified in the fields below.'
TT_MB: str = 'The minimum number of recent values to preserve in the moving window, even if they are outside the ' + 'specified time window. Keeping a minimum number of bars in the calculation helps avoid situations where a ' + 'large time gap between bars causes an empty period.'
TT_STD: str = 'Sets the multiplier for standard deviation bands offset above and below the RVWAP, and their color. ' + 'For example, with a multiplier of 1, the distance from the RVWAP to the bands is 100% of the standard deviation.' + '\n\nTo hide the bands, use a value of 0.'
GRP2: str = "Time period"
GRP3: str = "Deviation bands"
GRP4: str = "Minimum window size"


@script.indicator("Rolling VWAP", "RVWAP", True)
def main(
    srcInput: Series[float] = input.source(hlc3, "Source", tooltip=TT_SRC),
    fixedTfInput=input.bool(False, "Use a fixed time period", group=GRP2, tooltip=TT_WIN),
    __input_2__=input.int(1, "Days", group=GRP2, minval=0),
    __input_3__=input.int(0, "Hours", group=GRP2, minval=0, maxval=23),
    __input_4__=input.int(0, "Minutes", group=GRP2, minval=0, maxval=59),
    showInfoBoxInput=input.bool(True, "Show time period", group=GRP2),
    infoBoxSizeInput=input.string("small", "Size ", inline="21", group=GRP2, options=("tiny", "small", "normal", "large", "huge", "auto")),
    infoBoxYPosInput=input.string("bottom", "↕", inline="21", group=GRP2, options=("top", "middle", "bottom")),
    infoBoxXPosInput=input.string("right", "↔", inline="21", group=GRP2, options=("left", "center", "right")),
    infoBoxColorInput=input.color(color.new('#787B86'), "", inline="21", group=GRP2),
    infoBoxTxtColorInput=input.color(color.new('#FFFFFF'), "T", inline="21", group=GRP2),
    stdevMult1=input.float(0.0, "Bands multiplier 1", inline="31", group=GRP3, minval=0.0, step=0.5, tooltip=TT_STD),
    stdevMult2=input.float(0.0, "Bands multiplier 2", inline="32", group=GRP3, minval=0.0, step=0.5, tooltip=TT_STD),
    stdevMult3=input.float(0.0, "Bands multiplier 3", inline="33", group=GRP3, minval=0.0, step=0.5, tooltip=TT_STD),
    stdevColor1=input.color(color.new('#4CAF50'), "", inline="31", group=GRP3),
    stdevColor2=input.color(color.new('#FFEB3B'), "", inline="32", group=GRP3),
    stdevColor3=input.color(color.new('#FF5252'), "", inline="33", group=GRP3),
    minBarsInput=input.int(10, "Bars", group=GRP4, tooltip=TT_MB)
):
    MS_IN_MIN: int = 60 * 1000
    MS_IN_HOUR: int = MS_IN_MIN * 60
    MS_IN_DAY: int = MS_IN_HOUR * 24

    daysInput: int = __input_2__ * MS_IN_DAY
    hoursInput: int = __input_3__ * MS_IN_HOUR
    minsInput: int = __input_4__ * MS_IN_MIN


    def timeStep():
        tfInMs: int = timeframe.in_seconds() * 1000
        __block_result__ = na
        if tfInMs <= MS_IN_MIN:
            __block_result__ = MS_IN_HOUR
        elif tfInMs <= MS_IN_MIN * 5:
            __block_result__ = MS_IN_HOUR * 4
        elif tfInMs <= MS_IN_HOUR:
            __block_result__ = MS_IN_DAY * 1
        elif tfInMs <= MS_IN_HOUR * 4:
            __block_result__ = MS_IN_DAY * 3
        elif tfInMs <= MS_IN_HOUR * 12:
            __block_result__ = MS_IN_DAY * 7
        elif tfInMs <= MS_IN_DAY:
            __block_result__ = MS_IN_DAY * 30.4375
        elif tfInMs <= MS_IN_DAY * 7:
            __block_result__ = MS_IN_DAY * 90
        else:
            __block_result__ = MS_IN_DAY * 365
        step: float = __block_result__
        return cast_int(step)

    def tfString(timeInMs: Series[int]):
        s: int = timeInMs / 1000
        m: int = s / 60
        h: int = m / 60
        tm: int = math.floor(m % 60)
        th: int = math.floor(h % 24)
        d: int = math.floor(h / 24)
        __block_result_1__ = na
        if d == 30 and th == 10 and (tm == 30):
            __block_result_1__ = "1M"
        elif d == 7 and th == 0 and (tm == 0):
            __block_result_1__ = "1W"
        else:
            dStr: str = string.tostring(d) + 'D' if d > 0 else ''
            hStr: str = string.tostring(th) + 'H' if th > 0 else ''
            mStr: str = string.tostring(tm) + 'min' if tm > 0 else ''
            hasHours: bool = hStr != ''
            hasMins: bool = mStr != ''
            __block_result_1__ = dStr + (' ' if hasHours or hasMins else '') + hStr + (' ' if hasMins else '') + mStr
        return __block_result_1__

    if ta.cum(nz(volume)) == 0 and barstate.islast:
        runtime.error('No volume is provided by the data vendor.')

    timeInMs: int = minsInput + hoursInput + daysInput if fixedTfInput else timeStep()

    sumSrcVol: float = pc.totalForTimeWhen(srcInput * volume, timeInMs, True, minBarsInput)
    sumVol: float = pc.totalForTimeWhen(volume, timeInMs, True, minBarsInput)
    sumSrcSrcVol: float = pc.totalForTimeWhen(volume * math.pow(srcInput, 2), timeInMs, True, minBarsInput)

    rollingVWAP: float = sumSrcVol / sumVol

    variance: float = math.max(sumSrcSrcVol / sumVol - math.pow(rollingVWAP, 2), 0.0)

    stDev: float = math.sqrt(variance)

    upperBand1: float = rollingVWAP + stDev * stdevMult1
    lowerBand1: float = rollingVWAP - stDev * stdevMult1
    upperBand2: float = rollingVWAP + stDev * stdevMult2
    lowerBand2: float = rollingVWAP - stDev * stdevMult2
    upperBand3: float = rollingVWAP + stDev * stdevMult3
    lowerBand3: float = rollingVWAP - stDev * stdevMult3

    plot(rollingVWAP, 'Rolling VWAP', color.orange)

    p1 = plot(upperBand1 if stdevMult1 != 0 else na, 'Upper band 1', stdevColor1)
    p2 = plot(lowerBand1 if stdevMult1 != 0 else na, 'Lower band 1', stdevColor1)
    p3 = plot(upperBand2 if stdevMult2 != 0 else na, 'Upper band 2', stdevColor2)
    p4 = plot(lowerBand2 if stdevMult2 != 0 else na, 'Lower band 2', stdevColor2)
    p5 = plot(upperBand3 if stdevMult3 != 0 else na, 'Upper band 3', stdevColor3)
    p6 = plot(lowerBand3 if stdevMult3 != 0 else na, 'Lower band 3', stdevColor3)

    fill(p1, p2, color.new(color.green, 95), 'Bands fill')
    fill(p3, p4, color.new(color.green, 95), 'Bands fill')
    fill(p5, p6, color.new(color.green, 95), 'Bands fill')

    if showInfoBoxInput and barstate.islastconfirmedhistory:
        tfDisplay: Table = table.new(infoBoxYPosInput + '_' + infoBoxXPosInput, 1, 1)

        table.cell(tfDisplay, 0, 0, tfString(timeInMs), bgcolor=infoBoxColorInput, text_color=infoBoxTxtColorInput, text_size=infoBoxSizeInput)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)