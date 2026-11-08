"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    alert, alertcondition, array, bar_index, box, chart, close, color,
    display, fill, format, high, hline, input, location, low, math, na, plot, plotchar, plotshape,
    script, shape, size, ta
)
from pynecore.types import Box, Color, Persistent, Series
import lib.HeWhoMustNotBeNamed.ta.v1 as ta__ren____lib
import lib.jason5480.tts_convention.v7 as conv


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

version: str = "v2.3"
groupSettings: str = 'Settings ' + version
mode1: str = "1 Oscillator Mode"
mode2: str = "2 Overlay Mode (top and bottom no oscillator)"
mode3: str = "3 Candle Mode"
bull_signal_loc: int = -107
bear_signal_loc: int = 5
formula1: str = "Standard (2 Period)"
formula2: str = "Average"
lookbackGroupName: str = "Dual Signal Setup (Fast/Slow Lookback)"
groupAlerts: str = "Alerts"
group_strategy: str = "Strategy (send external signal to TTS backtester)"
strategy1: str = "1 Trend Following @ Square"
strategy2: str = "2 Reversal @ Square"
strategy3: str = "3 Reversal Trade @ Triangle"
strategy4: str = "4 Re-enter Trend Trade @ Triangle"
strategy5: str = "5 Pings"
strategy6: str = "6 Zero Line Cross"


@script.indicator("%R Trend Exhaustion [upslidedown]", format=format.price, precision=2, explicit_plot_zorder=True, max_boxes_count=300)
def main(
    bullcol__input=input.color(color.new('#2466A7'), 'Cold Color', group=groupSettings, inline="col"),
    bearcol__input=input.color(color.new('#CA0017'), 'Hot Color', group=groupSettings, inline="col"),
    force_overlay=input.bool(True, title="Draw Boxes on Chart", group=groupSettings, inline='overlay'),
    max_boxes_to_print=input.int(60, title="#", minval=1, maxval=300, group=groupSettings, inline='overlay'),
    mode=input.string(mode1, "Display Mode", options=(mode1, mode2, mode3), tooltip="Modes 2 & 3 are more advanced and expect that you most likely overlay the indicator on top of price action itself or another indiciator using TradingView's object tree panel.", group=groupSettings),
    transparency=input.int(80, 'Base Transparency', minval=0, maxval=100, group=groupSettings),
    formula=input.string(formula1, "Formula", options=(formula1, formula2), group=groupSettings),
    src: Series[float] = input.source(close, "Source", group=groupSettings),
    threshold=input.int(20, title="Exhaustion Threshold", minval=1, maxval=50, group=groupSettings, tooltip="Sets the overbought/oversold zone size and offset. Lower values will produce less results, higher values towards 50 will produce many results."),
    smoothType=input.string('ema', title="Smoothing Type", options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'highlow', 'linreg', 'median', 'mom', 'percentrank'), group=groupSettings),
    average_ma=input.int(3, "Average Formula MA", group=groupSettings),
    plot_shading=input.bool(True, title="Fill Gradients in OB/OS Zone", group=groupSettings),
    plot_crosses=input.bool(False, title="Highlight Crossovers", group=groupSettings, tooltip="Experimental idea for plotting crossovers with attempted bull/bear coloring. This needs to be combined with other TA but typically crossover condition results in interesting price action during or after."),
    plot_zero_crosses=input.bool(False, title="Plot Zero Line Crosses", group=groupSettings, tooltip="Experimental idea for plotting crosses"),
    shortLength=input.int(title="Fast Length", defval=21, group=lookbackGroupName),
    shortSmoothingLength=input.int(7, title="Fast Smoothing Length", group=lookbackGroupName),
    longLength=input.int(112, title="Slow Length", minval=1, group=lookbackGroupName),
    longSmoothingLength=input.int(3, title="Slow Smoothing Length", group=lookbackGroupName),
    bullStartOn=input.bool(True, "Bull trend start ⏹", group=groupAlerts, inline="bullStart"),
    bullStartTxt=input.string("%RTE bull trend start ⏹", "", group=groupAlerts, inline="bullStart"),
    bearStartOn=input.bool(True, "Bear trend start ⏹", group=groupAlerts, inline="bearStart"),
    bearStartTxt=input.string("%RTE bear trend start ⏹", "", group=groupAlerts, inline="bearStart"),
    bullReversalOn=input.bool(True, "Bull trend break ▼", group=groupAlerts, inline="bullReversal"),
    bullReversalTxt=input.string("%RTE bull trend break ▼", "", group=groupAlerts, inline="bullReversal"),
    bearReversalOn=input.bool(True, "Bear trend break ▲", group=groupAlerts, inline="bearReversal"),
    bearReversalTxt=input.string("%RTE bear trend break ▲", "", group=groupAlerts, inline="bearReversal"),
    bullCrossOn=input.bool(False, "Bull cross ⏺", group=groupAlerts, inline="bullCross"),
    bullCrossTxt=input.string("Bullish crossover", "", group=groupAlerts, inline="bullCross"),
    bearCrossOn=input.bool(False, "Bear cross ⏺", group=groupAlerts, inline="bearCross"),
    bearCrossTxt=input.string("Bearish crossover", "", group=groupAlerts, inline="bearCross"),
    plotStrategyEntry=input.bool(False, "Plot Strategy Entries on Chart", group=group_strategy),
    longDealsEnabled=input.bool(True, "Enable Long Deals", group=group_strategy),
    shortDealsEnabled=input.bool(True, "Enable Short Deals", group=group_strategy),
    strategyEntry=input.string(strategy3, "Strategy Entry", options=(strategy1, strategy2, strategy3, strategy4, strategy5, strategy6), group=group_strategy)
):
    bullcol: Persistent = bullcol__input
    bearcol: Persistent = bearcol__input
    invisible: Persistent = color.rgb(0, 0, 0, 100)

    compact = mode == mode2
    bullcol_xlight: Persistent = color.new(bullcol, transparency)
    bearcol_xlight: Persistent = color.new(bearcol, transparency)
    bullcol_light: Persistent = color.new(bullcol, transparency - 10)
    bearcol_light: Persistent = color.new(bearcol, transparency - 10)
    bullcol_medium: Persistent = color.new(bullcol, transparency - 20)
    bearcol_medium: Persistent = color.new(bearcol, transparency - 20)
    shortcol: Persistent[Color] = chart.fg_color
    longcol: Persistent = color.rgb(139, 174, 255)
    pivotcol: Persistent = color.white

    use_average = formula == formula2

    def _pr(length):
        max: float = ta__ren__.highest(length)
        min: float = ta__ren__.lowest(length)
        return 100 * (src - max) / (max - min)

    s_percentR: float = _pr(shortLength)
    l_percentR: float = _pr(longLength)
    avg_percentR: float = math.avg(s_percentR, l_percentR)

    if shortSmoothingLength > 1:
        s_percentR = ta__ren__.ma(s_percentR, smoothType, shortSmoothingLength)
    if longSmoothingLength > 1:
        l_percentR = ta__ren__.ma(l_percentR, smoothType, longSmoothingLength)
    if average_ma > 1:
        avg_percentR = ta__ren__.ma(avg_percentR, smoothType, average_ma)

    was_ob: Persistent[bool] = False
    was_os: Persistent[bool] = False

    overbought: Series[bool] = s_percentR >= -threshold and l_percentR >= -threshold
    oversold: Series[bool] = s_percentR <= -100 + threshold and l_percentR <= -100 + threshold
    ob_reversal: bool = not overbought and overbought[1]
    os_reversal: bool = not oversold and oversold[1]
    ob_trend_start: bool = overbought and (not overbought[1])
    os_trend_start: bool = oversold and (not oversold[1])

    bool_cross_long1: bool = ta__ren__.crossover(s_percentR, -50)
    bool_cross_long2: bool = ta__ren__.crossover(l_percentR, -50)
    cross_zero_long: bool = bool_cross_long1 or bool_cross_long2
    bool_cross_short1: bool = ta__ren__.crossunder(s_percentR, -50)
    bool_cross_short2: bool = ta__ren__.crossunder(l_percentR, -50)
    cross_zero_short: bool = bool_cross_short1 or bool_cross_short2

    zero_long: bool = s_percentR > -50 and l_percentR > -50 and cross_zero_long
    zero_short: bool = s_percentR < -50 and l_percentR < -50 and cross_zero_short

    if use_average:
        overbought = avg_percentR >= -threshold
        oversold = avg_percentR <= -100 + threshold
        ob_reversal = not overbought and overbought[1]
        os_reversal = not oversold and oversold[1]
        ob_trend_start = overbought and (not overbought[1])
        os_trend_start = oversold and (not oversold[1])

    cross_bear: bool = ta__ren__.crossover(l_percentR, s_percentR)
    cross_bull: bool = ta__ren__.crossunder(l_percentR, s_percentR)

    top = hline(0 if mode == mode1 else na, 'Top', bearcol_medium, linestyle=hline.style_solid)
    band1 = hline(-threshold if mode == mode1 else na, 'Top Threshold', bearcol_medium, linestyle=hline.style_solid)
    middle = hline(-50 if mode == mode1 else na, 'Middle Line', color.new(chart.fg_color, 80), linestyle=hline.style_solid)
    band0 = hline(-100 + threshold if mode == mode1 else na, 'Bottom Threshold', bullcol_medium, linestyle=hline.style_solid)
    bottom = hline(-100 if mode == mode1 else na, 'Bottom', bullcol_medium, linestyle=hline.style_solid)

    p_fastr = plot(s_percentR if mode == mode1 and (not use_average) else na, 'Fast Period %R', color=shortcol, linewidth=1)
    p_slowr = plot(l_percentR if mode == mode1 and (not use_average) else na, 'Slow Period %R', color=longcol, linewidth=1)
    p_avgr = plot(avg_percentR if mode == mode1 and use_average else na, 'Average Formula %R', color=shortcol, linewidth=1)

    gradientBullColor = color.new(bullcol, 100) if plot_shading else invisible
    gradientBearColor = color.new(bearcol, 100) if plot_shading else invisible
    fill(p_fastr, p_slowr, 0, -30, top_color=color.new(gradientBearColor, 0), bottom_color=gradientBearColor, title='Overbought Gradient Fill')
    fill(p_fastr, p_slowr, -70, -100, top_color=gradientBullColor, bottom_color=color.new(gradientBullColor, 0), title='Oversold Gradient Fill')

    def getlocation(mode, tORb):
        location__ren__ = location.absolute
        if mode == mode2 or mode == mode3:
            if tORb == 'top':
                if mode == mode3:
                    location__ren__ = location.abovebar
                else:
                    location__ren__ = location.top
            elif tORb == 'bottom':
                if mode == mode3:
                    location__ren__ = location.belowbar
                else:
                    location__ren__ = location.bottom
        return location__ren__

    ob_box: Persistent[Box] = na(Box)
    os_box: Persistent[Box] = na(Box)
    ob_box_top: Persistent[float] = na(float)
    ob_box_bottom: Persistent[float] = na(float)
    os_box_top: Persistent[float] = na(float)
    os_box_bottom: Persistent[float] = na(float)
    printed_boxes: Persistent[list[Box]] = array.new_box()

    plotshape(bear_signal_loc if ob_reversal else na, title='Overbought Trend Reversal ▼', style=shape.triangledown, location=getlocation(mode, 'top'), color=bearcol, text='', textcolor=invisible, size=size.tiny)
    plotshape(bull_signal_loc if os_reversal else na, title='Oversold Trend Reversal ▲', style=shape.triangleup, location=getlocation(mode, 'bottom'), color=bullcol, text='', textcolor=invisible, size=size.tiny)
    plotshape(ob_box_top if force_overlay and ob_reversal and (not na(ob_box_top)) else na, title='Overbought Break Candle ▼', style=shape.triangledown, location=location.absolute, color=bearcol, text='', textcolor=invisible, size=size.tiny, force_overlay=True)
    plotshape(os_box_bottom if force_overlay and os_reversal and (not na(os_box_bottom)) else na, title='Oversold Break Candle ▲', style=shape.triangleup, location=location.absolute, color=bullcol, text='', textcolor=invisible, size=size.tiny, force_overlay=True)
    plotshape(bear_signal_loc if overbought else na, title='Overbought Trend Warning ■', style=shape.square, location=getlocation(mode, 'top'), color=bearcol_medium, text='', textcolor=invisible, size=size.tiny)
    plotshape(bull_signal_loc if oversold else na, title='Oversold Trend Warning ■', style=shape.square, location=getlocation(mode, 'bottom'), color=bullcol_medium, text='', textcolor=invisible, size=size.tiny)

    if force_overlay:
        if ob_trend_start:
            if not na(ob_box):
                box.delete(ob_box)
            ob_box_top = high
            ob_box_bottom = low
            ob_box = box.new(bar_index - 1, ob_box_top, bar_index, ob_box_bottom, bgcolor=bearcol_xlight, border_color=bearcol_medium, border_width=1, force_overlay=True)
            array.push(printed_boxes, ob_box)
            if array.size(printed_boxes) > max_boxes_to_print:
                box.delete(array.shift(printed_boxes))
        elif overbought and (not na(ob_box)):
            box.set_right(ob_box, bar_index)
            if high > ob_box_top:
                ob_box_top = high
                box.set_top(ob_box, ob_box_top)
            if low < ob_box_bottom:
                ob_box_bottom = low
                box.set_bottom(ob_box, ob_box_bottom)
        elif not overbought and (not na(ob_box)):
            box.set_right(ob_box, bar_index - 1)
            ob_box = na

        if os_trend_start:
            if not na(os_box):
                box.delete(os_box)
            os_box_top = high
            os_box_bottom = low
            os_box = box.new(bar_index - 1, os_box_top, bar_index, os_box_bottom, bgcolor=bullcol_xlight, border_color=bullcol_medium, border_width=1, force_overlay=True)
            array.push(printed_boxes, os_box)
            if array.size(printed_boxes) > max_boxes_to_print:
                box.delete(array.shift(printed_boxes))
        elif oversold and (not na(os_box)):
            box.set_right(os_box, bar_index)
            if high > os_box_top:
                os_box_top = high
                box.set_top(os_box, os_box_top)
            if low < os_box_bottom:
                os_box_bottom = low
                box.set_bottom(os_box, os_box_bottom)
        elif not oversold and (not na(os_box)):
            box.set_right(os_box, bar_index - 1)
            os_box = na

    plotshape(bear_signal_loc if zero_long and plot_zero_crosses else na, title='Zero Cross Long', style=shape.triangleup, location=getlocation(mode, 'top'), color=color.yellow, text='', textcolor=invisible, size=size.tiny)
    plotshape(bull_signal_loc if zero_short and plot_zero_crosses else na, title='Zero Cross Short', style=shape.triangledown, location=getlocation(mode, 'bottom'), color=color.yellow, text='', textcolor=invisible, size=size.tiny)

    plot(l_percentR if not compact and plot_crosses and (cross_bull or cross_bear) else na, 'Crossover Dot (small)', style=plot.style_circles, color=bullcol if cross_bull else bearcol, linewidth=4)
    plot(l_percentR if not compact and plot_crosses and (cross_bull or cross_bear) else na, 'Crossover Dot (big)', style=plot.style_circles, color=bullcol_light if cross_bull else bearcol_light, linewidth=12)

    plotchar(bear_signal_loc if ob_trend_start else na, char='◡', color=bearcol, location=getlocation(mode, 'top'))
    plotchar(bull_signal_loc if os_trend_start else na, char='◠', color=bullcol, location=getlocation(mode, 'bottom'))

    if bullStartOn and ob_trend_start:
        alert(message=bullStartTxt, freq=alert.freq_once_per_bar_close)
    if bearStartOn and os_trend_start:
        alert(message=bearStartTxt, freq=alert.freq_once_per_bar_close)
    if bullReversalOn and ob_reversal:
        alert(message=bullReversalTxt, freq=alert.freq_once_per_bar_close)
    if bearReversalOn and os_reversal:
        alert(message=bearReversalTxt, freq=alert.freq_once_per_bar_close)
    if bullCrossOn and cross_bull:
        alert(message=bullCrossTxt, freq=alert.freq_once_per_bar_close)
    if bearCrossOn and cross_bear:
        alert(message=bearCrossTxt, freq=alert.freq_once_per_bar_close)

    alertcondition(ob_reversal, 'Arrow Down (Bearish Reversal)', message='Arrow Down: Overbought trend is exhausted')
    alertcondition(os_reversal, 'Arrow Up (Bullish Reversal)', message='Arrow Up: Oversold trend is exhausted')
    alertcondition(ob_trend_start, 'Overbought Trend Started', message='Warning: Possible overbought trend exhaustion')
    alertcondition(os_trend_start, 'Oversold Trend Started', message='Warning: Possible oversold trend exhaustion')
    alertcondition(cross_bull, 'Bullish Crossover', message='Potential bullish crossover printed')
    alertcondition(cross_bear, 'Bearish Crossover', message='Potential bearish crossover printed')


    startLongDeal: bool = False
    startShortDeal: bool = False
    endLongDeal: bool = False
    endShortDeal: bool = False

    __switch__ = strategyEntry
    if __switch__ == strategy1:
        if ob_trend_start and longDealsEnabled:
            startLongDeal = True
        elif os_trend_start and shortDealsEnabled:
            startShortDeal = True
    elif __switch__ == strategy2:
        if os_trend_start and longDealsEnabled:
            startLongDeal = True
        elif ob_trend_start and shortDealsEnabled:
            startShortDeal = True
    elif __switch__ == strategy3:
        if ob_reversal and shortDealsEnabled:
            startShortDeal = True
        elif os_reversal and longDealsEnabled:
            startLongDeal = True
    elif __switch__ == strategy4:
        if os_reversal and shortDealsEnabled:
            startShortDeal = True
        elif ob_reversal and longDealsEnabled:
            startLongDeal = True
    elif __switch__ == strategy5:
        if cross_bull and longDealsEnabled:
            startLongDeal = True
        elif cross_bear and shortDealsEnabled:
            startShortDeal = True
    elif __switch__ == strategy6:
        if zero_long and longDealsEnabled:
            startLongDeal = True
        elif zero_short and shortDealsEnabled:
            startShortDeal = True

    dealConditions: conv.DealConditions = conv.DealConditions.new(startLongDeal=startLongDeal, startShortDeal=startShortDeal, endLongDeal=False, endShortDeal=False)

    plot(series=conv.getSignal(dealConditions), title='🔌Signal to TTS', color=color.new('#808000'), editable=False, display=display.data_window + display.status_line, precision=0)

    plotshape(dealConditions.startLongDeal if plotStrategyEntry else False, title='Start Long', style=shape.triangleup, location=location.belowbar, color=bullcol, size=size.tiny, text='Long', textcolor=chart.fg_color, display=display.all - display.status_line, force_overlay=True)

    plotshape(dealConditions.startShortDeal if plotStrategyEntry else False, title='Start Short', style=shape.triangledown, location=location.abovebar, color=bearcol, size=size.tiny, text='Short', textcolor=chart.fg_color, display=display.all - display.status_line, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
