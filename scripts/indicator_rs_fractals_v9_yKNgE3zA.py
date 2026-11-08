"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, barmerge, color, high, input, location, low,
    math, na, plot, plotshape, request, script, shape, syminfo, ta
)
from pynecore.types import Color, Series


@script.indicator(title='[RS]Fractals V9', overlay=True)
def main(
    showPatterns=input.bool(True, 'Show Patterns?'),
    showBarColors=input.bool(False, 'Show Bar Colors?'),
    filter_bw=input.bool(False, 'Filter Bill Williams Fractals?'),
    ShowHHLL=input(False, 'Show HH/LL Pivot labels?'),
    timeframe1=input('240', 'Timeframe:', inline='tf'),
    ShowTimeFractals1=input.bool(False, 'Show Higher Timeframe Fractals?', inline='tf'),
    __input_6__=input.bool(True, 'Repaint?', inline='tf'),
    showchannel1=input.bool(False, '1, ', inline='ch'),
    showchannel2=input.bool(False, '2, ', inline='ch'),
    showchannel3=input.bool(False, '3, Show Channels?', inline='ch'),
    showZigZag=input.bool(True, 'Show ZigZag?')
):
    def isRegularFractal(mode: int):
        __block_result__ = na
        __switch__ = mode
        if __switch__ == 1:
            __block_result__ = high[4] < high[3] and high[3] < high[2] and (high[2] > high[1]) and (high[1] > high)
        elif __switch__ == -1:
            __block_result__ = low[4] > low[3] and low[3] > low[2] and (low[2] < low[1]) and (low[1] < low)
        else:
            __block_result__ = False
        return __block_result__

    def isBWFractal(mode: int):
        __block_result_1__ = na
        __switch__ = mode
        if __switch__ == 1:
            __block_result_1__ = high[4] < high[2] and high[3] <= high[2] and (high[2] >= high[1]) and (high[2] > high)
        elif __switch__ == -1:
            __block_result_1__ = low[4] > low[2] and low[3] >= low[2] and (low[2] <= low[1]) and (low[2] < low)
        else:
            __block_result_1__ = False
        return __block_result_1__

    filteredtopf: bool = isRegularFractal(1) if filter_bw else isBWFractal(1)
    filteredbotf: bool = isRegularFractal(-1) if filter_bw else isBWFractal(-1)
    plotshape(filteredtopf, 'Filtered Top Fractals', shape.triangledown, location.abovebar, color.red, offset=-2)
    plotshape(filteredbotf, 'Filtered Bottom Fractals', shape.triangleup, location.belowbar, color.lime, offset=-2)
    last_top_0: float = ta.valuewhen(filteredtopf == True, high[2], 0)
    last_top_1: float = ta.valuewhen(filteredtopf == True, high[2], 1)
    last_top_2: float = ta.valuewhen(filteredtopf == True, high[2], 2)
    last_bot_0: float = ta.valuewhen(filteredbotf == True, low[2], 0)
    last_bot_1: float = ta.valuewhen(filteredbotf == True, low[2], 1)
    last_bot_2: float = ta.valuewhen(filteredbotf == True, low[2], 2)
    higherhigh: bool = False if filteredtopf == False else last_top_1 < last_top_0 and last_top_2 < last_top_0
    lowerhigh: bool = False if filteredtopf == False else last_top_1 > last_top_0 and last_top_2 > last_top_0
    higherlow: bool = False if filteredbotf == False else last_bot_1 < last_bot_0 and last_bot_2 < last_bot_0
    lowerlow: bool = False if filteredbotf == False else last_bot_1 > last_bot_0 and last_bot_2 > last_bot_0
    plotshape(higherhigh if ShowHHLL else False, 'Higher High', shape.square, location.abovebar, color.maroon, text='[HH]', offset=-2)
    plotshape(lowerhigh if ShowHHLL else False, 'Lower High', shape.square, location.abovebar, color.maroon, text='[LH]', offset=-2)
    plotshape(higherlow if ShowHHLL else False, 'High Low', shape.square, location.belowbar, color.green, text='[HL]', offset=-2)
    plotshape(lowerlow if ShowHHLL else False, 'Lower Low', shape.square, location.belowbar, color.green, text='[LL]', offset=-2)
    __REPAINT = barmerge.lookahead_on if __input_6__ else barmerge.lookahead_off
    def isTFFractal(mode, tf):
        tfh, tfl = request.security(syminfo.tickerid, tf, (high, low), lookahead=__REPAINT)
        __block_result_2__ = na
        __switch__ = mode
        if __switch__ == 1:
            __block_result_2__ = ta.valuewhen(higherhigh == True, high[2], 0) >= tfh
        elif __switch__ == -1:
            __block_result_2__ = ta.valuewhen(lowerlow == True, low[2], 0) <= tfl
        else:
            __block_result_2__ = False
        return __block_result_2__

    ref_isTFFractal_top: bool = isTFFractal(1, timeframe1)
    ref_isTFFractal_bot: bool = isTFFractal(-1, timeframe1)
    higherhhigh: bool = False if higherhigh == False else ref_isTFFractal_top
    lowerllow: bool = False if lowerlow == False else ref_isTFFractal_bot
    plotshape(higherhhigh if ShowTimeFractals1 else na, 'Timed Top Fractals', shape.square, location.abovebar, color.maroon, text='[TH]', offset=-2)
    plotshape(lowerllow if ShowTimeFractals1 else na, 'Timed Bottom Fractals', shape.square, location.belowbar, color.green, text='[TL]', offset=-2)
    plot(na if not showchannel1 else high[2] if filteredtopf else na, 'Top Channel 1', color.black, offset=-2)
    plot(na if not showchannel1 else low[2] if filteredbotf else na, 'Bottom Channel 1', color.black, offset=-2)
    plot(na if not showchannel2 else high[2] if higherhigh else na, 'Top Channel 2', color.gray, offset=-2)
    plot(na if not showchannel2 else low[2] if lowerlow else na, 'Bottom Channel 2', color.gray, offset=-2)
    plot(na if not showchannel3 else high[2] if higherhhigh else na, 'Top Channel 3', color.silver, offset=-2)
    plot(na if not showchannel3 else low[2] if lowerllow else na, 'Bottom Channel 3', color.silver, offset=-2)
    istop: bool = (True if higherhhigh else False) if ShowTimeFractals1 else True if filteredtopf else False
    isbot: bool = (True if lowerllow else False) if ShowTimeFractals1 else True if filteredbotf else False
    topcount: Series[int] = ta.barssince(istop)
    botcount: Series[int] = ta.barssince(isbot)
    zigzag: float = high[2] if istop and topcount[1] > botcount[1] else low[2] if isbot and topcount[1] < botcount[1] else na
    plot(na if not showZigZag else zigzag, 'ZigZag', color.black, offset=-2)
    bc: Color = color.red if zigzag and high[2] == zigzag else color.lime if zigzag and low[2] == zigzag else color.silver
    barcolor(bc if showBarColors else na, offset=-2)
    x: float = ta.valuewhen(zigzag, zigzag, 4)
    a: float = ta.valuewhen(zigzag, zigzag, 3)
    b: float = ta.valuewhen(zigzag, zigzag, 2)
    c: float = ta.valuewhen(zigzag, zigzag, 1)
    d: float = ta.valuewhen(zigzag, zigzag, 0)
    xab: float = math.abs(b - a) / math.abs(x - a)
    xad: float = math.abs(a - d) / math.abs(x - a)
    abc: float = math.abs(b - c) / math.abs(a - b)
    bcd: float = math.abs(c - d) / math.abs(b - c)
    def isBat(_mode):
        _xab = xab >= 0.382 and xab <= 0.5
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 1.618 and bcd <= 2.618
        _xad = xad <= 0.886
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isAltBat(_mode):
        _xab = xab <= 0.382
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 2.0 and bcd <= 3.618
        _xad = xad <= 1.13
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isButterfly(_mode):
        _xab = xab <= 0.786
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 1.618 and bcd <= 2.618
        _xad = xad >= 1.27 and xad <= 1.618
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isABCD(_mode):
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 1.13 and bcd <= 2.618
        return _abc and _bcd and (d < c if _mode == 1 else d > c)

    def isGartley(_mode):
        _xab = xab >= 0.5 and xab <= 0.618
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 1.13 and bcd <= 2.618
        _xad = xad >= 0.75 and xad <= 0.875
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isCrab(_mode):
        _xab = xab >= 0.75 and xab <= 0.875
        _abc = abc >= 0.382 and abc <= 0.886
        _bcd = bcd >= 2.0 and bcd <= 3.618
        _xad = xad >= 1.5 and xad <= 1.625
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isShark(_mode):
        _xab = xab >= 0.5 and xab <= 0.875
        _abc = abc >= 1.13 and abc <= 1.618
        _bcd = bcd >= 1.27 and bcd <= 2.24
        _xad = xad >= 0.88 and xad <= 1.13
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def is5o(_mode):
        _xab = xab >= 1.13 and xab <= 1.618
        _abc = abc >= 1.618 and abc <= 2.24
        _bcd = bcd >= 0.5 and bcd <= 0.625
        _xad = xad >= 0.0 and xad <= 0.236
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isWolf(_mode):
        _xab = xab >= 1.27 and xab <= 1.618
        _abc = abc >= 0 and abc <= 5
        _bcd = bcd >= 1.27 and bcd <= 1.618
        _xad = xad >= 0.0 and xad <= 5
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isHnS(_mode):
        _xab = xab >= 2.0 and xab <= 10
        _abc = abc >= 0.9 and abc <= 1.1
        _bcd = bcd >= 0.236 and bcd <= 0.88
        _xad = xad >= 0.9 and xad <= 1.1
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isConTria(_mode):
        _xab = xab >= 0.382 and xab <= 0.618
        _abc = abc >= 0.382 and abc <= 0.618
        _bcd = bcd >= 0.382 and bcd <= 0.618
        _xad = xad >= 0.236 and xad <= 0.764
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    def isExpTria(_mode):
        _xab = xab >= 1.236 and xab <= 1.618
        _abc = abc >= 1.0 and abc <= 1.618
        _bcd = bcd >= 1.236 and bcd <= 2.0
        _xad = xad >= 2.0 and xad <= 2.236
        return _xab and _abc and _bcd and _xad and (d < c if _mode == 1 else d > c)

    plotshape(na if not showPatterns else isABCD(-1) and (not inline_series(isABCD(-1), 1)), text='\nAB=CD', title='Bear ABCD', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top, offset=-2)
    plotshape(na if not showPatterns else isBat(-1) and (not inline_series(isBat(-1), 1)), text='Bat', title='Bear Bat', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top, offset=-2)
    plotshape(na if not showPatterns else isAltBat(-1) and (not inline_series(isAltBat(-1), 1)), text='Alt Bat', title='Bear Alt Bat', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isButterfly(-1) and (not inline_series(isButterfly(-1), 1)), text='Butterfly', title='Bear Butterfly', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isGartley(-1) and (not inline_series(isGartley(-1), 1)), text='Gartley', title='Bear Gartley', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isCrab(-1) and (not inline_series(isCrab(-1), 1)), text='Crab', title='Bear Crab', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isShark(-1) and (not inline_series(isShark(-1), 1)), text='Shark', title='Bear Shark', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else is5o(-1) and (not inline_series(is5o(-1), 1)), text='5-O', title='Bear 5-O', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isWolf(-1) and (not inline_series(isWolf(-1), 1)), text='Wolf Wave', title='Bear Wolf Wave', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isHnS(-1) and (not inline_series(isHnS(-1), 1)), text='Head and Shoulders', title='Bear Head and Shoulders', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isConTria(-1) and (not inline_series(isConTria(-1), 1)), text='Contracting Triangle', title='Bear Contracting triangle', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isExpTria(-1) and (not inline_series(isExpTria(-1), 1)), text='Expanding Triangle', title='Bear Expanding Triangle', style=shape.labeldown, color=color.maroon, textcolor=color.white, location=location.top)
    plotshape(na if not showPatterns else isABCD(1) and (not inline_series(isABCD(1), 1)), text='AB=CD\n', title='Bull ABCD', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isBat(1) and (not inline_series(isBat(1), 1)), text='Bat', title='Bull Bat', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isAltBat(1) and (not inline_series(isAltBat(1), 1)), text='Alt Bat', title='Bull Alt Bat', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isButterfly(1) and (not inline_series(isButterfly(1), 1)), text='Butterfly', title='Bull Butterfly', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isGartley(1) and (not inline_series(isGartley(1), 1)), text='Gartley', title='Bull Gartley', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isCrab(1) and (not inline_series(isCrab(1), 1)), text='Crab', title='Bull Crab', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isShark(1) and (not inline_series(isShark(1), 1)), text='Shark', title='Bull Shark', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else is5o(1) and (not inline_series(is5o(1), 1)), text='5-O', title='Bull 5-O', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isWolf(1) and (not inline_series(isWolf(1), 1)), text='Wolf Wave', title='Bull Wolf Wave', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isHnS(1) and (not inline_series(isHnS(1), 1)), text='Head and Shoulders', title='Bull Head and Shoulders', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isConTria(1) and (not inline_series(isConTria(1), 1)), text='Contracting Triangle', title='Bull Contracting Triangle', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    plotshape(na if not showPatterns else isExpTria(1) and (not inline_series(isExpTria(1), 1)), text='Expanding Triangle', title='Bull Expanding Triangle', style=shape.labelup, color=color.green, textcolor=color.white, location=location.bottom)
    isABCD_1: Series = isABCD(-1)
    bear_abcd: bool = isABCD(-1) and (not isABCD_1[1])
    isBat_1: Series = isBat(-1)
    bear_bat: bool = isBat(-1) and (not isBat_1[1])
    isAltBat_1: Series = isAltBat(-1)
    bear_altbat: bool = isAltBat(-1) and (not isAltBat_1[1])
    isButterfly_1: Series = isButterfly(-1)
    bear_butterfly: bool = isButterfly(-1) and (not isButterfly_1[1])
    isGartley_1: Series = isGartley(-1)
    bear_gartley: bool = isGartley(-1) and (not isGartley_1[1])
    isCrab_1: Series = isCrab(-1)
    bear_crab: bool = isCrab(-1) and (not isCrab_1[1])
    isShark_1: Series = isShark(-1)
    bear_shark: bool = isShark(-1) and (not isShark_1[1])
    is5o_1: Series = is5o(-1)
    bear_5o: bool = is5o(-1) and (not is5o_1[1])
    isWolf_1: Series = isWolf(-1)
    bear_wolf: bool = isWolf(-1) and (not isWolf_1[1])
    isHnS_1: Series = isHnS(-1)
    bear_hns: bool = isHnS(-1) and (not isHnS_1[1])
    isConTria_1: Series = isConTria(-1)
    bear_contria: bool = isConTria(-1) and (not isConTria_1[1])
    isExpTria_1: Series = isExpTria(-1)
    bear_exptria: bool = isExpTria(-1) and (not isExpTria_1[1])
    isABCD_2: Series = isABCD(1)
    bull_abcd: bool = isABCD(1) and (not isABCD_2[1])
    isBat_2: Series = isBat(1)
    bull_bat: bool = isBat(1) and (not isBat_2[1])
    isAltBat_2: Series = isAltBat(1)
    bull_altbat: bool = isAltBat(1) and (not isAltBat_2[1])
    isButterfly_2: Series = isButterfly(1)
    bull_butterfly: bool = isButterfly(1) and (not isButterfly_2[1])
    isGartley_2: Series = isGartley(1)
    bull_gartley: bool = isGartley(1) and (not isGartley_2[1])
    isCrab_2: Series = isCrab(1)
    bull_crab: bool = isCrab(1) and (not isCrab_2[1])
    isShark_2: Series = isShark(1)
    bull_shark: bool = isShark(1) and (not isShark_2[1])
    is5o_2: Series = is5o(1)
    bull_5o: bool = is5o(1) and (not is5o_2[1])
    isWolf_2: Series = isWolf(1)
    bull_wolf: bool = isWolf(1) and (not isWolf_2[1])
    isHnS_2: Series = isHnS(1)
    bull_hns: bool = isHnS(1) and (not isHnS_2[1])
    isConTria_2: Series = isConTria(1)
    bull_contria: bool = isConTria(1) and (not isConTria_2[1])
    isExpTria_2: Series = isExpTria(1)
    bull_exptria: bool = isExpTria(1) and (not isExpTria_2[1])
    bear_patterns: bool = bear_abcd and bear_bat and bear_altbat and bear_butterfly and bear_gartley and bear_crab and bear_shark and bear_5o and bear_wolf and bear_hns and bear_contria and bear_exptria
    bull_patterns: bool = bull_abcd and bull_bat and bull_altbat and bull_butterfly and bull_gartley and bull_crab and bull_shark and bull_5o and bull_wolf and bull_hns and bull_contria and bull_exptria
    all_patterns: bool = bear_patterns and bull_patterns
    alertcondition(condition=all_patterns, title='all patterns', message='The Patterns')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
