"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, color, fill, high, input, low, math, na, plot, script, time,
    timeframe
)
from pynecore.types import Series


@script.indicator('Sessions', overlay=True)
def main(
    bgColor=input.bool(False, 'Activate High/Low View'),
    res=input.timeframe('D', 'Resolution', options=('D', 'W', 'M')),
    london=input.session('0300-1200:1234567', 'London Session'),
    ny=input.session('0800-1700:1234567', 'New York Session'),
    tokyo=input.session('2000-0400:1234567', 'Tokyo Session'),
    sydney=input.session('1700-0200:1234567', 'Sydney Session'),
    London=input.bool(True, 'London Session'),
    NY=input.bool(True, 'New York Session'),
    Tokyo=input.bool(True, 'Tokyo Session'),
    Sydney=input.bool(False, 'Sydney Session')
):
    LondonColor = color.new(color.green, 90)
    NYColor = color.new(color.red, 90)
    AsiaColor = color.new(color.yellow, 90)
    SydneyColor = color.new(color.blue, 90)
    def is_newbar(sess):
        t: Series = time(res, sess, 'America/New_York')
        return na(t[1]) and (not na(t)) or t[1] < t

    def is_session(sess):
        return not na(time(timeframe.period, sess, 'America/New_York'))

    londonNewbar = is_newbar(london)
    londonSession = is_session(london)
    londonLow: Series[float] = na(float)
    __block_result__ = na
    if londonSession:
        __block_result_1__ = na
        if londonNewbar:
            __block_result_1__ = low
        else:
            __block_result_1__ = math.min(londonLow[1], low)
        __block_result__ = __block_result_1__
    else:
        __block_result__ = londonLow
    londonLow = __block_result__
    londonHigh: Series[float] = na(float)
    __block_result_2__ = na
    if londonSession:
        __block_result_3__ = na
        if londonNewbar:
            __block_result_3__ = high
        else:
            __block_result_3__ = math.max(londonHigh[1], high)
        __block_result_2__ = __block_result_3__
    else:
        __block_result_2__ = londonHigh
    londonHigh = __block_result_2__
    plotLL = plot(londonLow, color=color.new(color.new('#000000'), 100))
    plotLH = plot(londonHigh, color=color.new(color.new('#000000'), 100))
    fill(plotLL, plotLH, color=LondonColor if londonSession and London and bgColor else na)
    bgcolor(LondonColor if londonSession and London and (not bgColor) else na)
    nyNewbar = is_newbar(ny)
    nySession = is_session(ny)
    nyLow: Series[float] = na(float)
    __block_result_4__ = na
    if nySession:
        __block_result_5__ = na
        if nyNewbar:
            __block_result_5__ = low
        else:
            __block_result_5__ = math.min(nyLow[1], low)
        __block_result_4__ = __block_result_5__
    else:
        __block_result_4__ = nyLow
    nyLow = __block_result_4__
    nyHigh: Series[float] = na(float)
    __block_result_6__ = na
    if nySession:
        __block_result_7__ = na
        if nyNewbar:
            __block_result_7__ = high
        else:
            __block_result_7__ = math.max(nyHigh[1], high)
        __block_result_6__ = __block_result_7__
    else:
        __block_result_6__ = nyHigh
    nyHigh = __block_result_6__
    plotNYL = plot(nyLow, color=color.new(color.new('#000000'), 100))
    plotNYH = plot(nyHigh, color=color.new(color.new('#000000'), 100))
    fill(plotNYL, plotNYH, color=NYColor if nySession and NY and bgColor else na)
    bgcolor(NYColor if nySession and NY and (not bgColor) else na)
    tokyoNewbar = is_newbar(tokyo)
    tokyoSession = is_session(tokyo)
    tokyoLow: Series[float] = na(float)
    __block_result_8__ = na
    if tokyoSession:
        __block_result_9__ = na
        if tokyoNewbar:
            __block_result_9__ = low
        else:
            __block_result_9__ = math.min(tokyoLow[1], low)
        __block_result_8__ = __block_result_9__
    else:
        __block_result_8__ = tokyoLow
    tokyoLow = __block_result_8__
    tokyoHigh: Series[float] = na(float)
    __block_result_10__ = na
    if tokyoSession:
        __block_result_11__ = na
        if tokyoNewbar:
            __block_result_11__ = high
        else:
            __block_result_11__ = math.max(tokyoHigh[1], high)
        __block_result_10__ = __block_result_11__
    else:
        __block_result_10__ = tokyoHigh
    tokyoHigh = __block_result_10__
    plotTL = plot(tokyoLow, color=color.new(color.new('#000000'), 100))
    plotTH = plot(tokyoHigh, color=color.new(color.new('#000000'), 100))
    fill(plotTL, plotTH, color=AsiaColor if tokyoSession and Tokyo and bgColor else na)
    bgcolor(AsiaColor if tokyoSession and Tokyo and (not bgColor) else na)
    sydneyNewbar = is_newbar(sydney)
    sydneySession = is_session(sydney)
    sydneyLow: Series[float] = na(float)
    __block_result_12__ = na
    if sydneySession:
        __block_result_13__ = na
        if sydneyNewbar:
            __block_result_13__ = low
        else:
            __block_result_13__ = math.min(sydneyLow[1], low)
        __block_result_12__ = __block_result_13__
    else:
        __block_result_12__ = sydneyLow
    sydneyLow = __block_result_12__
    sydneyHigh: Series[float] = na(float)
    __block_result_14__ = na
    if sydneySession:
        __block_result_15__ = na
        if sydneyNewbar:
            __block_result_15__ = high
        else:
            __block_result_15__ = math.max(sydneyHigh[1], high)
        __block_result_14__ = __block_result_15__
    else:
        __block_result_14__ = sydneyHigh
    sydneyHigh = __block_result_14__
    plotSL = plot(sydneyLow, color=color.new(color.new('#000000'), 100))
    plotSH = plot(sydneyHigh, color=color.new(color.new('#000000'), 100))
    fill(plotSL, plotSH, color=SydneyColor if sydneySession and Sydney and bgColor else na)
    bgcolor(SydneyColor if sydneySession and Sydney and (not bgColor) else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
