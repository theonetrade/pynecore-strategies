"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barstate, close, color, display, input, math, na, nz,
    plot, request, runtime, script, string, syminfo, ta, table, timeframe
)
from pynecore.types import Color, Persistent, Series, Table
from typing import Protocol, Any
import lib.PineCoders.Time.v4 as PCtime


__all__ = ['ltf', 'ltfStats']


class _ProtocolLtf(Protocol):
    def __call__(self, userSelection: Series[str], choice1: str, choice2: str, choice3: str, choice4: str, choice5: str, choice6: str, choice7: str, choice8: str, choice9: str, choice10: str) -> Any: ...


class _ProtocolLtfstats(Protocol):
    def __call__(self, intrabarValues: list[float]) -> Any: ...


ltf: _ProtocolLtf = Exported()
ltfStats: _ProtocolLtfstats = Exported()

WHITE: Color = color.white
GRAY: Color = color.gray
LTF1: str = "Covering most chart bars (least precise)"
LTF2: str = "Covering some chart bars (less precise)"
LTF3: str = "Covering less chart bars (more precise)"
LTF4: str = "Covering few chart bars (very precise)"
LTF5: str = "Covering the least chart bars (most precise)"
LTF6: str = "~12 intrabars per chart bar"
LTF7: str = "~24 intrabars per chart bar"
LTF8: str = "~50 intrabars per chart bar"
LTF9: str = "~100 intrabars per chart bar"
LTF10: str = "~250 intrabars per chart bar"
TT_LTF: str = "This selection determines the approximate number of intrabars analyzed per chart bar. Higher numbers of     intrabars produce more granular data at the cost of less historical bar coverage, because the maximum number of     available intrabars is 200K.     \n\nThe first five options set the lower timeframe based on a specified relative level of chart bar coverage.     The last five options set the lower timeframe based on an approximate number of intrabars per chart bar."


@script.library("lower_tf")
def main(
    ltfModeInput=input.string(LTF3, "Intrabar precision", options=(LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10), tooltip=TT_LTF),
    showInfoBoxInput=input.bool(True, "Show information box "),
    infoBoxSizeInput=input.string("normal", "Size ", inline="01", options=("tiny", "small", "normal", "large", "huge", "auto")),
    infoBoxYPosInput=input.string("bottom", "↕", inline="01", options=("top", "middle", "bottom")),
    infoBoxXPosInput=input.string("right", "↔", inline="01", options=("left", "center", "right")),
    infoBoxColorInput=input.color(GRAY, "", inline="01"),
    infoBoxTxtColorInput=input.color(WHITE, "T", inline="01")
):
    def filterSmallTfs(tfInSeconds: int):
        return 1 if tfInSeconds < 5 else tfInSeconds

    @export
    def ltf(userSelection: Series[str], choice1: str, choice2: str, choice3: str, choice4: str, choice5: str, choice6: str, choice7: str, choice8: str, choice9: str, choice10: str):
        ONE_MIN: int = 1
        ONE_SEC: int = ONE_MIN / 60
        ONE_HOUR: int = ONE_MIN * 60
        ONE_DAY: int = ONE_HOUR * 24
        ONE_WEEK: int = ONE_DAY * 7

        chartTfInMinutes: float = timeframe.in_seconds() / 60.0
        marketIs24Hours: bool = syminfo.type == 'crypto' or syminfo.type == 'forex'
        mktFactor: float = 0.25 if marketIs24Hours else 1.0

        leastPrecise: bool = False
        lessPrecise: bool = False
        morePrecise: bool = False
        veryPrecise: bool = False
        mostPrecise: bool = False
        intrabars12: bool = False
        intrabars24: bool = False
        intrabars50: bool = False
        intrabars100: bool = False
        intrabars250: bool = False
        __switch__ = userSelection
        if __switch__ == choice1:
            leastPrecise = True
        elif __switch__ == choice2:
            lessPrecise = True
        elif __switch__ == choice3:
            morePrecise = True
        elif __switch__ == choice4:
            veryPrecise = True
        elif __switch__ == choice5:
            mostPrecise = True
        elif __switch__ == choice6:
            intrabars12 = True
        elif __switch__ == choice7:
            intrabars24 = True
        elif __switch__ == choice8:
            intrabars50 = True
        elif __switch__ == choice9:
            intrabars100 = True
        elif __switch__ == choice10:
            intrabars250 = True

        __block_result__ = na
        if leastPrecise:
            __block_result__ = timeframe.from_seconds(timeframe.in_seconds() / 4)
        elif veryPrecise:
            __block_result_1__ = na
            if chartTfInMinutes <= ONE_HOUR:
                __block_result_1__ = "5S"
            elif chartTfInMinutes <= ONE_HOUR * 2:
                __block_result_1__ = "15S"
            elif chartTfInMinutes <= ONE_HOUR * 4:
                __block_result_1__ = "30S"
            elif chartTfInMinutes <= ONE_HOUR * 12:
                __block_result_1__ = '1' if marketIs24Hours else '30S'
            elif chartTfInMinutes <= ONE_DAY:
                __block_result_1__ = '2' if marketIs24Hours else '1'
            elif chartTfInMinutes <= ONE_WEEK:
                __block_result_1__ = '15' if marketIs24Hours else '5'
            else:
                __block_result_1__ = '60' if marketIs24Hours else '30'
            __block_result__ = __block_result_1__
        elif mostPrecise:
            __block_result_2__ = na
            if chartTfInMinutes <= ONE_HOUR:
                __block_result_2__ = "1S"
            elif chartTfInMinutes <= ONE_HOUR * 2:
                __block_result_2__ = "5S"
            elif chartTfInMinutes <= ONE_HOUR * 4:
                __block_result_2__ = "15S"
            elif chartTfInMinutes <= ONE_HOUR * 12:
                __block_result_2__ = '30S' if marketIs24Hours else '15S'
            elif chartTfInMinutes <= ONE_DAY:
                __block_result_2__ = '1' if marketIs24Hours else '30S'
            elif chartTfInMinutes <= ONE_WEEK:
                __block_result_2__ = '10' if marketIs24Hours else '3'
            else:
                __block_result_2__ = '30' if marketIs24Hours else '15'
            __block_result__ = __block_result_2__
        elif lessPrecise:
            __block_result_3__ = na
            if chartTfInMinutes <= ONE_MIN:
                __block_result_3__ = "5S"
            elif chartTfInMinutes <= ONE_MIN * 2:
                __block_result_3__ = "10S"
            elif chartTfInMinutes <= ONE_MIN * 3:
                __block_result_3__ = "15S"
            elif chartTfInMinutes <= ONE_MIN * 5:
                __block_result_3__ = "30S"
            elif chartTfInMinutes <= ONE_MIN * 15:
                __block_result_3__ = "1"
            elif chartTfInMinutes <= ONE_HOUR:
                __block_result_3__ = "3"
            elif chartTfInMinutes < ONE_HOUR * 2:
                __block_result_3__ = "5"
            elif chartTfInMinutes < ONE_HOUR * 4:
                __block_result_3__ = "15"
            elif chartTfInMinutes < ONE_HOUR * 6:
                __block_result_3__ = "30"
            elif chartTfInMinutes < ONE_HOUR * 12:
                __block_result_3__ = '60' if marketIs24Hours else '30'
            elif chartTfInMinutes < ONE_DAY:
                __block_result_3__ = '120' if marketIs24Hours else '30'
            elif chartTfInMinutes < ONE_WEEK:
                __block_result_3__ = '720' if marketIs24Hours else '120'
            else:
                __block_result_3__ = "D"
            __block_result__ = __block_result_3__
        elif morePrecise:
            __block_result_4__ = na
            if chartTfInMinutes <= ONE_MIN:
                __block_result_4__ = "1S"
            elif chartTfInMinutes <= ONE_MIN * 2:
                __block_result_4__ = "5S"
            elif chartTfInMinutes <= ONE_MIN * 3:
                __block_result_4__ = "10S"
            elif chartTfInMinutes <= ONE_MIN * 5:
                __block_result_4__ = "15S"
            elif chartTfInMinutes <= ONE_MIN * 15:
                __block_result_4__ = "30S"
            elif chartTfInMinutes <= ONE_HOUR:
                __block_result_4__ = "1"
            elif chartTfInMinutes < ONE_HOUR * 2:
                __block_result_4__ = "2"
            elif chartTfInMinutes < ONE_HOUR * 4:
                __block_result_4__ = "3"
            elif chartTfInMinutes < ONE_HOUR * 6:
                __block_result_4__ = "5"
            elif chartTfInMinutes < ONE_HOUR * 12:
                __block_result_4__ = '10' if marketIs24Hours else '5'
            elif chartTfInMinutes < ONE_DAY:
                __block_result_4__ = '15' if marketIs24Hours else '5'
            elif chartTfInMinutes < ONE_WEEK:
                __block_result_4__ = '120' if marketIs24Hours else '30'
            else:
                __block_result_4__ = "720"
            __block_result__ = __block_result_4__
        elif intrabars12:
            __block_result__ = timeframe.from_seconds(filterSmallTfs(timeframe.in_seconds() / cast_int(48 * mktFactor)))
        elif intrabars24:
            __block_result__ = timeframe.from_seconds(filterSmallTfs(timeframe.in_seconds() / cast_int(96 * mktFactor)))
        elif intrabars50:
            __block_result__ = timeframe.from_seconds(filterSmallTfs(timeframe.in_seconds() / cast_int(200 * mktFactor)))
        elif intrabars100:
            __block_result__ = timeframe.from_seconds(filterSmallTfs(timeframe.in_seconds() / cast_int(400 * mktFactor)))
        elif intrabars250:
            __block_result__ = timeframe.from_seconds(filterSmallTfs(timeframe.in_seconds() / cast_int(1000 * mktFactor)))
        else:
            __block_result__ = "1S"
        return __block_result__

    @export
    def ltfStats(intrabarValues: list[float]):
        intrabarsInChartBar: int = array.size(intrabarValues)

        chartBarsCovered: int = cast_int(ta.cum(math.sign(intrabarsInChartBar)))

        avgIntrabars: float = nz(ta.cum(intrabarsInChartBar) / chartBarsCovered)
        return (intrabarsInChartBar, chartBarsCovered, avgIntrabars)


    TAB_TXT: str = "Uses intrabars at the {0} timeframe.\nAvg intrabars per chart bar:     {1,number,#.#}\nChart bars covered: {2} of {3} ({4,number,#.##}%)"
    ERR_TXT: str = "No intrabar information exists at the {1}{0}{1} timeframe."

    ltfString: Persistent[str] = ltf(ltfModeInput, LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10)

    intrabarCloses: list[float] = request.security_lower_tf(syminfo.tickerid, ltfString, close)
    intrabars, chartBarsCovered, avgIntrabars = ltfStats(intrabarCloses)
    chartBars: int = bar_index + 1
    plot(avgIntrabars, 'Average intrabars', color.silver, 6)
    plot(intrabars, 'Intrabars', color.blue, 2)

    plot(chartBarsCovered, 'Chart bars covered', display=display.data_window + display.status_line)
    plot(chartBars, 'Chart bars total', display=display.data_window + display.status_line)

    if showInfoBoxInput:
        infoBox: Persistent[Table] = table.new(infoBoxYPosInput + '_' + infoBoxXPosInput, 1, 1)

        formattedLtf: str = PCtime.formattedNoOfPeriods(timeframe.in_seconds(ltfString) * 1000)
        txt: str = string.format(TAB_TXT, formattedLtf, avgIntrabars, chartBarsCovered, chartBars, chartBarsCovered / chartBars * 100, "'")
        if barstate.isfirst:
            table.cell(infoBox, 0, 0, txt, text_color=infoBoxTxtColorInput, text_size=infoBoxSizeInput, bgcolor=infoBoxColorInput)
        elif barstate.islast:
            table.cell_set_text(infoBox, 0, 0, txt)
    if ta.cum(intrabars) == 0 and barstate.islast:
        runtime.error(string.format(ERR_TXT, ltfString, "'"))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
