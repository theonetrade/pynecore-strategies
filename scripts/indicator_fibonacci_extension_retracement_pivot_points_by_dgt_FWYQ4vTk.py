"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, close, color, display,
    extend, format, high, input, label, line, location, low, math, na, nz, open, plot, plotchar,
    position, script, size, string, syminfo, ta, table, text, time, timeframe, timenow, volume,
    xloc, yloc
)
from pynecore.types import Label, Line, NA, Persistent, Series, Table

display__ren__ = display.all - display.status_line
group_pick: str = 'Pick a Fibonacci Tool'
tooltip_fib_tool = 'Chooses which Fibonacci tool to display.\n\n' + '• Pivot Points: Static, structure-based reference levels.\n' + '• Retracements: Measures pullbacks within an existing move.\n' + '• Retracements + Pivot Points: Combines internal retracements with structural pivots.\n' + '• Extensions: Projects continuation targets beyond the current range.\n' + '• Extensions + Pivot Points: Combines projected targets with structural pivots.\n\n' + 'Use combinations to identify high-probability confluence zones.'
tooltip_fib_tz = 'Displays Fibonacci Time Zones\n\n' + 'Time Zones project potential timing windows where price reactions, accelerations, or trend changes may occur.\n\n' + 'This tool focuses on *when* a reaction may happen, rather than *where*.'
groupSwing: str = 'Swing Detection Settings'
tooltip_threshold = 'Controls how price swings are detected.\n\n' + 'Deviation:\n' + 'Defines the minimum ATR-based price movement required to confirm a new swing. Higher values filter noise and highlight more significant structure.\n\n' + 'Depth:\n' + 'Defines the minimum number of bars required to confirm a swing high or low. Higher values produce smoother structure but react more slowly.'
group_pivot: str = 'Fibonacci Pivot Points Settings'
tooltip_htf = 'Defines the timeframe used to calculate Pivot Points.\n\n' + 'Manual Selection:\n' + '• 15 Min / 1 Hour / 4 Hour → Uses the selected intraday timeframe.\n' + '• Daily → Anchors to calendar days.\n' + '• Weekly → Anchors to calendar weeks.\n' + '• Monthly → Anchors to calendar months.\n' + '• Quarterly → Anchors to calendar quarters.\n' + '• Yearly → Anchors to calendar years.\n\n' + 'Auto Mode (Default):\n' + 'Automatically selects an appropriate higher timeframe based on the chart timeframe:\n' + '• Intraday ≤ 15 min → Daily pivots\n' + '• Intraday 30-240 min → Weekly pivots\n' + '• Daily charts → Monthly pivots\n' + '• Weekly / Monthly charts → Yearly pivots\n\n' + 'Auto mode is designed to provide context-aware pivot levels without manual adjustment.'
group_fib_tool: str = 'Fibonacci Extension / Retracement Settings'
group_fib_tz: str = 'Fibonacci TimeZone Settings'
group_zigzag: str = 'ZigZag Settings'
tooltip_zigzag = 'ZigZag Structure Visualization\n\n' + 'Identifies meaningful price swings and connects them with straight lines to clarify overall price structure.\n\n' + 'By filtering out minor fluctuations and market noise, ZigZag helps highlight dominant trends and potential trend changes over time.'
tooltip_zz_swings = 'ZigZag Swing Points\n\n' + 'Displays swing highs and lows derived from the ZigZag structure.\n\n' + '• Highs: Confirmed swing highs\n' + '• Lows: Confirmed swing lows\n' + '• Temps: Temporary (unconfirmed) swings that may update as price evolves\n\n' + 'Swing points help visualize market structure, momentum shifts, and potential reaction zones.'
group_fib_levels: str = 'Fibonacci Levels'
group_vol_vol: str = 'Volatility AddOns'
tooltip_high_volatility = 'High Volatility Detection\n\n' + 'Identifies bars where price expansion is unusually large relative to recent volatility.\n\n' + 'A high-volatility bar is detected when:\n' + '• Current bar range > (ATR × Multiplier)\n\n' + 'Such conditions often accompany breakouts, news-driven moves, or volatility regime shifts.'
group_vol: str = 'Volume AddOns'
tooltip_volume_spike_sign_of_exhaustion = 'Volume Spike · Potential Exhaustion\n\n' + 'Highlights moments where volume expands significantly relative to its moving average.\n\n' + 'A spike is detected when:\n' + '• Current volume > (Volume MA × Threshold)\n\n' + 'These events often occur near climactic moves, exhaustion points, or strong participation surges.'
tooltip_volume_weighted_colored_bars = 'Volume-Weighted Colored Bars\n\n' + 'Colors price bars based on relative volume intensity.\n\n' + 'Bar colors indicate:\n' + '• High participation (above average volume)\n' + '• Normal participation\n' + '• Low participation (below average volume)\n\n' + 'Helps visually confirm momentum, conviction, and participation behind price movement.'


@script.indicator('Fibonacci Extention / Retracment / Pivot Points by DGT', 'FIBs · ☼☾', True, max_lines_count=500, max_labels_count=500)
def main(
    i_isFib=input.bool(True, 'Pick a Fibonacci Tool', inline='FIB', group=group_pick, tooltip=tooltip_fib_tool),
    i_fibTool=input.string('Pivot Points', '             ', options=('Pivot Points', 'Retracements', 'Retracements + Pivot Points', 'Extensions', 'Extensions + Pivot Points'), inline='FIB', group=group_pick, display=display__ren__),
    i_fibTime=input.bool(True, 'Fibonacci Time Zones', group=group_pick, tooltip=tooltip_fib_tz),
    __input_3__=input.float(3, 'Deviation', minval=0, inline='Pivots', group=groupSwing, tooltip=tooltip_threshold, display=display__ren__),
    i_depth=input.int(11, '       Depth', minval=1, inline='Pivots', group=groupSwing, display=display__ren__),
    htf_tf=input.string('Auto', 'Pivot Points Timeframe', options=('Auto', '15 Min', '1 Hour', '4 Hour', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'), group=group_pivot, tooltip=tooltip_htf, display=display__ren__),
    i_levelsPvt=input.string('Levels', 'Level Labels', options=('Levels', 'Prices', 'Levels + Prices', 'None'), inline='pvt', group=group_pivot, display=display__ren__),
    i_levelsPvtP=input.string('Pivot End', '', options=('Last Bar', 'Pivot End'), inline='pvt', group=group_pivot, display=display__ren__),
    i_levelsPvtS=input.string('Small', '', options=('Small', 'Normal'), inline='pvt', group=group_pivot, display=display__ren__),
    i_relevant=input.bool(False, 'Only Relevant Pivot Point Levels', group=group_pivot),
    i_histPP=input.bool(False, 'Historical Pivot Points', group=group_pivot),
    i_extend=input.bool(False, 'Extend Pivot Point Lines', inline='fLines', group=group_pivot),
    i_extendL=input.string('Dashed', '', options=('Dashed', 'Dotted', 'Solid'), inline='fLines', group=group_pivot, display=display__ren__),
    i_levels=input.string('Levels', 'Level Labels', options=('Levels', 'Prices', 'Levels + Prices', 'None'), inline='fLines', group=group_fib_tool, display=display__ren__),
    i_levelsP=input.string('Pivot Start', '', options=('Last Bar', 'Pivot Start'), inline='fLines', group=group_fib_tool, display=display__ren__),
    i_levelsS=input.string('Small', '', options=('Small', 'Normal'), inline='fLines', group=group_fib_tool, display=display__ren__),
    i_reverse=input.bool(False, 'Reverse Extension / Retracement Levels', group=group_fib_tool),
    i_extendER=input.bool(False, 'Extend Extension / Retracement Lines', inline='fLine', group=group_fib_tool),
    i_histPivot=input.int(0, 'Historical Extension / Retracement Levels', minval=0, group=group_fib_tool, display=display__ren__),
    i_fib_tzl=input.bool(True, 'Time Zone Labels', inline='tz poz', group=group_fib_tz),
    i_fib_tzlp=input.string('Left', '', options=('Right', 'Left'), inline='tz poz', group=group_fib_tz, display=display__ren__),
    i_fib_tzlp2=input.string('Bottom', '', options=('Bottom', 'Top'), inline='tz poz', group=group_fib_tz, display=display__ren__),
    i_tzColor=input.color(color.new('#2196F3'), 'Time Zone Line Color', group=group_fib_tz),
    i_histPivot2=input.int(0, 'Historical Time Zones', minval=0, group=group_fib_tz, display=display__ren__),
    i_zigZag=input.bool(False, 'Zig Zag', inline='ZZ', group=group_zigzag, tooltip=tooltip_zigzag),
    i_zzColor=input.color(color.new('#C77A08'), '', inline='ZZ', group=group_zigzag),
    i_zzStyle=input.string('Solid', '', options=('Dashed', 'Dotted', 'Solid'), inline='ZZ', group=group_zigzag, display=display__ren__),
    i_zzWidth=input.int(1, '', minval=1, inline='ZZ', group=group_zigzag, display=display__ren__),
    zzSwings=input.bool(True, 'Zig Zag Swing, ', inline='ZZ2', group=group_zigzag, tooltip=tooltip_zz_swings),
    pHighC=input.color(color.new('#D4A5A5'), 'Highs', inline='ZZ2', group=group_zigzag),
    pLowC=input.color(color.new('#8FAADC'), 'Lows', inline='ZZ2', group=group_zigzag),
    pTemC=input.color(color.new('#0000F0'), 'Temps', inline='ZZ2', group=group_zigzag),
    show_0=input.bool(True, '', inline='Level0', group=group_fib_levels),
    value_0=input.float(0.0, '', inline='Level0', group=group_fib_levels, display=display__ren__),
    color_0=input.color(color.new('#787B86'), '', inline='Level0', group=group_fib_levels),
    show_0_236=input.bool(True, '', inline='Level0', group=group_fib_levels),
    value_0_236=input.float(0.236, '', inline='Level0', group=group_fib_levels, display=display__ren__),
    color_0_236=input.color(color.new('#F44336'), '', inline='Level0', group=group_fib_levels),
    show_0_382=input.bool(True, '', inline='Level1', group=group_fib_levels),
    value_0_382=input.float(0.382, '', inline='Level1', group=group_fib_levels, display=display__ren__),
    color_0_382=input.color(color.new('#81C784'), '', inline='Level1', group=group_fib_levels),
    show_0_5=input.bool(True, '', inline='Level1', group=group_fib_levels),
    value_0_5=input.float(0.5, '', inline='Level1', group=group_fib_levels, display=display__ren__),
    color_0_5=input.color(color.new('#4CAF50'), '', inline='Level1', group=group_fib_levels),
    show_0_618=input.bool(True, '', inline='Level2', group=group_fib_levels),
    value_0_618=input.float(0.618, '', inline='Level2', group=group_fib_levels, display=display__ren__),
    color_0_618=input.color(color.new('#009688'), '', inline='Level2', group=group_fib_levels),
    show_0_65=input.bool(False, '', inline='Level2', group=group_fib_levels),
    value_0_65=input.float(0.65, '', inline='Level2', group=group_fib_levels, display=display__ren__),
    color_0_65=input.color(color.new('#009688'), '', inline='Level2', group=group_fib_levels),
    show_0_786=input.bool(True, '', inline='Level3', group=group_fib_levels),
    value_0_786=input.float(0.786, '', inline='Level3', group=group_fib_levels, display=display__ren__),
    color_0_786=input.color(color.new('#64B5F6'), '', inline='Level3', group=group_fib_levels),
    show_1=input.bool(True, '', inline='Level3', group=group_fib_levels),
    value_1=input.float(1.0, '', inline='Level3', group=group_fib_levels, display=display__ren__),
    color_1=input.color(color.new('#787B86'), '', inline='Level3', group=group_fib_levels),
    show_1_272=input.bool(False, '', inline='Level4', group=group_fib_levels),
    value_1_272=input.float(1.272, '', inline='Level4', group=group_fib_levels, display=display__ren__),
    color_1_272=input.color(color.new('#81C784'), '', inline='Level4', group=group_fib_levels),
    show_1_414=input.bool(False, '', inline='Level4', group=group_fib_levels),
    value_1_414=input.float(1.414, '', inline='Level4', group=group_fib_levels, display=display__ren__),
    color_1_414=input.color(color.new('#F44336'), '', inline='Level4', group=group_fib_levels),
    show_1_618=input.bool(True, '', inline='Level5', group=group_fib_levels),
    value_1_618=input.float(1.618, '', inline='Level5', group=group_fib_levels, display=display__ren__),
    color_1_618=input.color(color.new('#2196F3'), '', inline='Level5', group=group_fib_levels),
    show_1_65=input.bool(False, '', inline='Level5', group=group_fib_levels),
    value_1_65=input.float(1.65, '', inline='Level5', group=group_fib_levels, display=display__ren__),
    color_1_65=input.color(color.new('#2196F3'), '', inline='Level5', group=group_fib_levels),
    show_2_618=input.bool(False, '', inline='Level6', group=group_fib_levels),
    value_2_618=input.float(2.618, '', inline='Level6', group=group_fib_levels, display=display__ren__),
    color_2_618=input.color(color.new('#F44336'), '', inline='Level6', group=group_fib_levels),
    show_2_65=input.bool(False, '', inline='Level6', group=group_fib_levels),
    value_2_65=input.float(2.65, '', inline='Level6', group=group_fib_levels, display=display__ren__),
    color_2_65=input.color(color.new('#F44336'), '', inline='Level6', group=group_fib_levels),
    show_3_618=input.bool(False, '', inline='Level7', group=group_fib_levels),
    value_3_618=input.float(3.618, '', inline='Level7', group=group_fib_levels, display=display__ren__),
    color_3_618=input.color(color.new('#9C27B0'), '', inline='Level7', group=group_fib_levels),
    show_3_65=input.bool(False, '', inline='Level7', group=group_fib_levels),
    value_3_65=input.float(3.65, '', inline='Level7', group=group_fib_levels, display=display__ren__),
    color_3_65=input.color(color.new('#9C27B0'), '', inline='Level7', group=group_fib_levels),
    show_4_236=input.bool(False, '', inline='Level8', group=group_fib_levels),
    value_4_236=input.float(4.236, '', inline='Level8', group=group_fib_levels, display=display__ren__),
    color_4_236=input.color(color.new('#E91E63'), '', inline='Level8', group=group_fib_levels),
    show_4_618=input.bool(False, '', inline='Level8', group=group_fib_levels),
    value_4_618=input.float(4.618, '', inline='Level8', group=group_fib_levels, display=display__ren__),
    color_4_618=input.color(color.new('#81C784'), '', inline='Level8', group=group_fib_levels),
    show_neg_0_236=input.bool(False, '', inline='Level9', group=group_fib_levels),
    value_neg_0_236=input.float(-0.236, '', inline='Level9', group=group_fib_levels, display=display__ren__),
    color_neg_0_236=input.color(color.new('#F44336'), '', inline='Level9', group=group_fib_levels),
    show_neg_0_382=input.bool(False, '', inline='Level9', group=group_fib_levels),
    value_neg_0_382=input.float(-0.382, '', inline='Level9', group=group_fib_levels, display=display__ren__),
    color_neg_0_382=input.color(color.new('#81C784'), '', inline='Level9', group=group_fib_levels),
    show_neg_0_618=input.bool(True, '', inline='Level10', group=group_fib_levels),
    value_neg_0_618=input.float(-0.618, '', inline='Level10', group=group_fib_levels, display=display__ren__),
    color_neg_0_618=input.color(color.new('#009688'), '', inline='Level10', group=group_fib_levels),
    show_neg_0_65=input.bool(False, '', inline='Level10', group=group_fib_levels),
    value_neg_0_65=input.float(-0.65, '', inline='Level10', group=group_fib_levels, display=display__ren__),
    color_neg_0_65=input.color(color.new('#009688'), '', inline='Level10', group=group_fib_levels),
    i_hATRLb=input.bool(True, '⚡ High Volatility Detection', group=group_vol_vol, tooltip=tooltip_high_volatility),
    __input_99__=input.int(13, '  ATR Length', inline='ATR', group=group_vol_vol, display=display__ren__),
    __input_100__=input.float(2.718, 'Multiplier', minval=0.1, step=0.1, inline='ATR', group=group_vol_vol, display=display__ren__),
    __input_101__=input.int(89, 'Volume Moving Average Length', group=group_vol, display=display__ren__),
    i_vSpikeLb=input.bool(True, '🚦 Volume Spike · Potential Exhaustion', group=group_vol, tooltip=tooltip_volume_spike_sign_of_exhaustion),
    i_vSpikeThresh=input.float(4.669, '  Volume Spike Threshold', minval=0.1, step=0.1, group=group_vol, display=display__ren__),
    i_vwcb=input.bool(True, 'Volume-Weighted Colored Bars', group=group_vol, tooltip=tooltip_volume_weighted_colored_bars),
    i_vwcbHighThresh=input.float(1.618, '  Volume Threshold: High', minval=1.0, step=0.1, inline='VWC', group=group_vol, display=display__ren__),
    i_vwcbLowThresh=input.float(0.618, 'Low', minval=0.1, step=0.1, inline='VWC', group=group_vol, display=display__ren__)
):
    i_dev_thresh = ta.atr(10) / close * 100 * __input_3__



    fib_tzlp = label.style_label_left if i_fib_tzlp == 'Left' else label.style_label_right


    lineLast: Persistent[Line] = na(Line)
    iLast: Persistent[int] = 0
    iPrev: Persistent[int] = 0
    pLast: Persistent[float] = 0
    isHighLast: Persistent[bool] = False

    iPrevPivot: Persistent[int] = 0
    pPrevPivot: Persistent[float] = 0.0
    iLastPivot: Persistent[int] = 0
    pLastPivot: Persistent[float] = 0.0

    def pivots(src: Series, length, isHigh):
        l2 = length * 2
        c = nz(src[length])
        ok: bool = True

        for i in pine_range(0, l2, 1):
            if isHigh and src[i] > c:
                ok = False

            if not isHigh and src[i] < c:
                ok = False
        __block_result__ = (na, na)
        if ok:
            __block_result__ = (bar_index[length], c)
        else:
            __block_result__ = (NA(int), NA(float))
        return __block_result__

    iH, pH = pivots(high, i_depth / 2, True)
    iL, pL = pivots(low, i_depth / 2, False)

    def calc_dev(base_price, price):
        return 100 * (price - base_price) / price

    def pivotFound(dev, isHigh, index, price):
        __block_result_1__ = (na, na)
        if isHighLast == isHigh and (not na(lineLast)):
            __block_result_2__ = (na, na)
            if price > pLast if isHighLast else price < pLast:
                line.set_xy2(lineLast, index, price)
                __block_result_2__ = (lineLast, isHighLast)
            else:
                __block_result_2__ = (NA(Line), NA(bool))
            __block_result_1__ = __block_result_2__
        else:
            __block_result_3__ = (na, na)
            if math.abs(dev) > i_dev_thresh:
                __block_result_4__ = (na, na, na)
                if not i_zigZag:
                    __block_result_4__ = (na, 1, line.style_dashed)
                else:
                    __block_result_4__ = (i_zzColor, i_zzWidth, line.style_solid if i_zzStyle == 'Solid' else line.style_dotted if i_zzStyle == 'Dotted' else line.style_dashed)
                zzCol, zzWid, zzSty = __block_result_4__

                id = line.new(iLast, pLast, index, price, color=zzCol, width=zzWid, style=zzSty)
                __block_result_3__ = (id, isHigh)
            else:
                __block_result_3__ = (NA(Line), NA(bool))
            __block_result_1__ = __block_result_3__
        return __block_result_1__

    if not na(iH):
        lbTmp: Persistent[Label] = na(Label)
        dev = calc_dev(pLast, pH)
        id, isHigh = pivotFound(dev, True, iH, pH)

        if not na(id):
            if id != lineLast:
                iPrevPivot = line.get_x1(lineLast)
                pPrevPivot = line.get_y1(lineLast)
                iLastPivot = line.get_x2(lineLast)
                pLastPivot = line.get_y2(lineLast)

                if zzSwings:
                    label.new(iPrevPivot, pPrevPivot, '▼', xloc.bar_index, yloc.price, color.new(color.white, 100), label.style_label_down, pHighC, size.small, text.align_center, 'ZigZag Swing High\nPrice : ' + string.tostring(pPrevPivot, format.mintick))

                if not i_zigZag:
                    line.delete(lineLast)

            lineLast = id
            isHighLast = isHigh
            iPrev = iLast
            iLast = iH
            pLast = pH

            if zzSwings:
                label.delete(lbTmp)
                lbTmp = label.new(iLast, pLast, '●\n▼', xloc.bar_index, yloc.price, color.new(color.white, 100), label.style_label_down, pTemC, size.small, text.align_center, 'Temporary ZigZag Swing High\nPrice : ' + string.tostring(pLast, format.mintick) + '\n\n⚠ Provisional level\n' + 'Subject to repaint until structure confirms')
    else:
        if not na(iL):
            lbTmp: Persistent[Label] = na(Label)

            dev = calc_dev(pLast, pL)
            id, isHigh = pivotFound(dev, False, iL, pL)

            if not na(id):
                if id != lineLast:
                    iPrevPivot = line.get_x1(lineLast)
                    pPrevPivot = line.get_y1(lineLast)
                    iLastPivot = line.get_x2(lineLast)
                    pLastPivot = line.get_y2(lineLast)

                    if zzSwings:
                        label.new(iPrevPivot, pPrevPivot, '▲', xloc.bar_index, yloc.price, color.new(color.white, 100), label.style_label_up, pLowC, size.small, text.align_center, 'ZigZag Swing Low\nPrice : ' + string.tostring(pPrevPivot, format.mintick))

                    if not i_zigZag:
                        line.delete(lineLast)

                lineLast = id
                isHighLast = isHigh
                iPrev = iLast
                iLast = iL
                pLast = pL

                if zzSwings:
                    label.delete(lbTmp)
                    lbTmp = label.new(iLast, pLast, '▲\n●', xloc.bar_index, yloc.price, color.new(color.white, 100), label.style_label_up, pTemC, size.small, text.align_center, 'Temporary ZigZag Swing Low\nPrice : ' + string.tostring(pLast, format.mintick) + '\n\n⚠ Provisional level\n' + 'Subject to repaint until structure confirms')

    iStartBase = ta.valuewhen(ta.change(iPrevPivot) != 0, iPrevPivot, i_histPivot) if i_histPivot > 0 else ta.valuewhen(ta.change(iPrevPivot) != 0, iPrevPivot, 0)
    pStartBase = ta.valuewhen(ta.change(pPrevPivot) != 0, pPrevPivot, i_histPivot) if i_histPivot > 0 else ta.valuewhen(ta.change(pPrevPivot) != 0, pPrevPivot, 0)
    iEndBase = ta.valuewhen(ta.change(iLastPivot) != 0, iLastPivot, i_histPivot - 1) if i_histPivot > 0 else line.get_x2(lineLast)
    pEndBase = ta.valuewhen(ta.change(pLastPivot) != 0, pLastPivot, i_histPivot - 1) if i_histPivot > 0 else line.get_y2(lineLast)
    iMidPivot = ta.valuewhen(ta.change(iPrevPivot) != 0, iPrevPivot, i_histPivot - 1) if i_histPivot > 0 else line.get_x1(lineLast)
    pMidPivot = ta.valuewhen(ta.change(pPrevPivot) != 0, pPrevPivot, i_histPivot - 1) if i_histPivot > 0 else line.get_y1(lineLast)

    iEndBase2 = ta.valuewhen(ta.change(iLastPivot) != 0, iLastPivot, i_histPivot2 - 1) if i_histPivot2 > 0 else line.get_x2(lineLast)
    pEndBase2 = ta.valuewhen(ta.change(pLastPivot) != 0, pLastPivot, i_histPivot2 - 1) if i_histPivot2 > 0 else line.get_y2(lineLast)
    iMidPivot2 = ta.valuewhen(ta.change(iPrevPivot) != 0, iPrevPivot, i_histPivot2 - 1) if i_histPivot2 > 0 else line.get_x1(lineLast)
    pMidPivot2 = ta.valuewhen(ta.change(pPrevPivot) != 0, pPrevPivot, i_histPivot2 - 1) if i_histPivot2 > 0 else line.get_y1(lineLast)

    htf = '15' if htf_tf == '15 Min' else '60' if htf_tf == '1 Hour' else '240' if htf_tf == '4 Hour' else 'D' if htf_tf == 'Session' else 'D' if htf_tf == 'Daily' else 'W' if htf_tf == 'Weekly' else 'M' if htf_tf == 'Monthly' else '3M' if htf_tf == 'Quarterly' else '12M' if htf_tf == 'Yearly' else 'D' if timeframe.isintraday and (timeframe.period == '1' or timeframe.period == '3' or timeframe.period == '5' or (timeframe.period == '15')) else 'W' if timeframe.isintraday and (timeframe.period == '30' or timeframe.period == '45' or timeframe.period == '60' or (timeframe.period == '120') or (timeframe.period == '180') or (timeframe.period == '240')) else 'M' if timeframe.isdaily else '12M' if timeframe.isweekly or timeframe.ismonthly else '3M'

    def f_htf_ohlc(_htf):
        htf_o: Persistent[float] = 0.0
        htf_h: Persistent[float] = 0.0
        htf_l: Persistent[float] = 0.0
        htf_c: Series = close

        htf_ox: Persistent[float] = 0.0
        htf_hx: Persistent[float] = 0.0
        htf_lx: Persistent[float] = 0.0
        htf_cx: Persistent[float] = 0.0

        if timeframe.change(_htf):
            htf_ox = htf_o
            htf_o = open

            htf_hx = htf_h
            htf_h = high

            htf_lx = htf_l
            htf_l = low

            htf_cx = htf_c[1]
        else:
            htf_h = math.max(high, htf_h)
            htf_l = math.min(low, htf_l)

        return (htf_ox, htf_hx, htf_lx, htf_cx, htf_o, htf_h, htf_l, htf_c)

    _, htf_h1, htf_l1, htf_c1, _, _, _, _ = f_htf_ohlc(htf)

    time_x10 = ta.valuewhen(cast_bool(ta.change(time(htf))), time, 1)
    time_x11 = ta.valuewhen(cast_bool(ta.change(time(htf))), time, 0)
    time_x21 = 2 * time_x11 - time_x10

    def f_drawLineX(_x1, _y1, _x2, _y2, _xloc, _extend, _color, _style, _width):
        id: Persistent = line.new(_x1, _y1, _x2, _y2, _xloc, _extend, _color, _style, _width)

        __block_result_5__ = na
        if _y1 > 0 and _y2 > 0:
            line.set_xy1(id, _x1, _y1)
            line.set_xy2(id, _x2, _y2)
            __block_result_5__ = line.set_color(id, _color)
        else:
            line.set_xy1(id, _x1, close)
            line.set_xy2(id, _x2, close)
            __block_result_5__ = line.set_color(id, color.new('#00000000'))
        return __block_result_5__

    def f_drawLabelX(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip):
        id: Persistent = label.new(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip)
        label.set_text(id, _text + '\n\n' if i_extend or i_extendER or i_levelsP == 'Last Bar' else _text)
        label.set_tooltip(id, _tooltip)

        __block_result_6__ = na
        if _y > 0:
            label.set_xy(id, _x, _y)
            __block_result_6__ = label.set_textcolor(id, _textcolor)
        else:
            label.set_xy(id, _x, close)
            __block_result_6__ = label.set_textcolor(id, color.new('#00000000'))
        return __block_result_6__

    def f_crossingLevel(_curret: Series, _level):
        return _level > _curret and _level < _curret[1] or (_level < _curret and _level > _curret[1])

    ln: Persistent[list[Line]] = array.new_line()
    lb: Persistent[list[Label]] = array.new_label()

    if cast_bool(ta.change(time)) and array.size(ln) > 0:
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(array.size(ln)):
            i = __loop_1__.value
            line.delete(array.shift(ln))

    if cast_bool(ta.change(time)) and array.size(lb) > 0:
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(array.size(lb)):
            i = __loop_1__.value
            label.delete(array.shift(lb))

    def f_drawLineTZ(_x1, _y1, _x2, _y2, _xloc, _extend, _c, _s, _w):
        __block_result_7__ = na
        if _x1 - bar_index < 500:
            __block_result_7__ = array.push(ln, line.new(_x1, _y1, _x2, _y2, _xloc, _extend, _c, _s, _w))
        return __block_result_7__

    def f_drawLabelTZ(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip):
        __block_result_8__ = na
        if _x - bar_index < 500:
            __block_result_8__ = array.push(lb, label.new(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip))
        return __block_result_8__

    def f_drawLinePVT(_x1, _y1, _x2, _y2, _xloc, _extend, _c, _s, _w):
        __block_result_9__ = na
        if _y1 > 0:
            __block_result_9__ = array.push(ln, line.new(_x1, _y1, _x2, _y2, _xloc, _extend, _c, _s, _w))
        return __block_result_9__

    def f_drawLabelPVT(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip):
        __block_result_10__ = na
        if _y > 0:
            __block_result_10__ = array.push(lb, label.new(_x, _y, _text + '\n\n' if i_extend or i_levelsPvtP == 'Last Bar' else _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip))
        return __block_result_10__

    if i_fibTime:
        referance = math.round(iEndBase2 - iMidPivot2)

        f_drawLineTZ(iMidPivot2 - referance, pEndBase2, iMidPivot2 - referance, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2, pEndBase2, iMidPivot2, pMidPivot2, xloc.bar_index, extend.both, color.gray, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance, pEndBase2, iMidPivot2 + referance, pMidPivot2, xloc.bar_index, extend.both, color.gray, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 2, pEndBase2, iMidPivot2 + referance * 2, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 3, pEndBase2, iMidPivot2 + referance * 3, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 5, pEndBase2, iMidPivot2 + referance * 5, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 8, pEndBase2, iMidPivot2 + referance * 8, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 13, pEndBase2, iMidPivot2 + referance * 13, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 21, pEndBase2, iMidPivot2 + referance * 21, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 34, pEndBase2, iMidPivot2 + referance * 34, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 55, pEndBase2, iMidPivot2 + referance * 55, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)
        f_drawLineTZ(iMidPivot2 + referance * 89, pEndBase2, iMidPivot2 + referance * 89, pMidPivot2, xloc.bar_index, extend.both, i_tzColor, line.style_solid, 1)

        if i_fib_tzl:
            f_drawLabelTZ(iMidPivot2 + referance * -1, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '-1', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 0, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '0', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, color.gray, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 1, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '1', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, color.gray, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 2, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '2', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 3, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '3', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 5, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '5', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 8, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '8', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 13, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '13', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 21, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '21', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 34, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '34', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 55, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '55', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')
            f_drawLabelTZ(iMidPivot2 + referance * 89, math.min(pEndBase2, pMidPivot2) if i_fib_tzlp2 == 'Bottom' else math.max(pEndBase2, pMidPivot2), '89', xloc.bar_index, yloc.price, color.new('#00000000'), fib_tzlp, i_tzColor, size.normal, text.align_center, '')

    def f_processLevelX(_show, _level, _color):
        __block_result_11__ = na
        if i_isFib:
            pPivotDiff = math.abs(pMidPivot - pEndBase)
            price: float = 0.0

            if i_fibTool == 'Extensions' or i_fibTool == 'Extensions + Pivot Points':
                f_drawLineX(iStartBase, pStartBase, iMidPivot, pMidPivot, xloc.bar_index, extend.none, color.gray, line.style_dashed, 1)
                f_drawLineX(iMidPivot, pMidPivot, iEndBase, pEndBase, xloc.bar_index, extend.none, color.gray, line.style_dashed, 1)

                offset = math.abs(pMidPivot - pStartBase)
                price = pMidPivot - pPivotDiff + (-1 if i_reverse else 1) * offset * _level if pEndBase < pMidPivot else pMidPivot + pPivotDiff - (-1 if i_reverse else 1) * offset * _level

                if _show:
                    f_drawLineX(iMidPivot, price, bar_index, price, xloc.bar_index, extend.both if i_extendER else extend.right, _color, line.style_solid, 1)

                    if i_levels != 'None':
                        bar = bar_index if i_levelsP == 'Last Bar' else iMidPivot
                        style = label.style_label_left if i_levelsP == 'Last Bar' else label.style_label_right
                        size__ren__ = size.small if i_levelsS == 'Small' else size.normal
                        f_drawLabelX(bar, price, ('' if i_levels == 'Prices' else 'EXT ' + string.tostring(_level)) + (' (' + string.tostring(price, format.mintick) + ')' if i_levels == 'Levels + Prices' or i_levels == 'Prices' else ''), xloc.bar_index, yloc.price, color.new('#00000000'), style, _color, size__ren__, text.align_left, string.tostring(price, format.mintick))

                    if f_crossingLevel(close, price):
                        alert('AutoFib Extension : ' + syminfo.ticker + ' crossing level ' + string.tostring(_level))

            if i_fibTool == 'Retracements' or i_fibTool == 'Retracements + Pivot Points':
                f_drawLineX(iMidPivot, pMidPivot, iEndBase, pEndBase, xloc.bar_index, extend.none, color.gray, line.style_dashed, 1)

                price = (pEndBase if i_reverse else pMidPivot) - (-1 if i_reverse else 1) * pPivotDiff * _level if pEndBase < pMidPivot else (pEndBase if i_reverse else pMidPivot) + (-1 if i_reverse else 1) * pPivotDiff * _level

                if _show:
                    f_drawLineX(iMidPivot, price, bar_index, price, xloc.bar_index, extend.both if i_extendER else extend.right, _color, line.style_solid, 1)

                    if i_levels != 'None':
                        bar = bar_index if i_levelsP == 'Last Bar' else iMidPivot
                        style = label.style_label_left if i_levelsP == 'Last Bar' else label.style_label_right
                        size__ren__ = size.small if i_levelsS == 'Small' else size.normal
                        f_drawLabelX(bar, price, ('' if i_levels == 'Prices' else 'RET ' + string.tostring(_level)) + (' (' + string.tostring(price, format.mintick) + ')' if i_levels == 'Levels + Prices' or i_levels == 'Prices' else ''), xloc.bar_index, yloc.price, color.new('#00000000'), style, _color, size__ren__, text.align_left, string.tostring(price, format.mintick))

                    if f_crossingLevel(close, price):
                        alert('AutoFib Retracment : ' + syminfo.ticker + ' crossing level ' + string.tostring(_level))

            __block_result_12__ = na
            if i_fibTool == 'Pivot Points' or i_fibTool == 'Extensions + Pivot Points' or i_fibTool == 'Retracements + Pivot Points':
                pivot = math.avg(htf_h1, htf_l1, htf_c1)
                range_2 = htf_h1 - htf_l1

                if not i_histPP:
                    f_drawLinePVT(time_x10, pivot, time_x21, pivot, xloc.bar_time, extend.none, color.gray, line.style_dashed, 1)

                __block_result_13__ = na
                if _show and _level >= 0:
                    pvtPoints = _level == 0 or _level == 0.382 or _level == 0.618 or (_level == 1)

                    f_drawLinePVT(time_x11, pivot - range_2 * _level, time_x21, pivot - range_2 * _level, xloc.bar_time, extend.none, (_color if close < pivot else na) if i_relevant else _color, line.style_solid if pvtPoints else line.style_dashed, 2 if pvtPoints else 1)
                    f_drawLinePVT(time_x11, pivot + range_2 * _level, time_x21, pivot + range_2 * _level, xloc.bar_time, extend.none, (_color if close > pivot else na) if i_relevant else _color, line.style_solid if pvtPoints else line.style_dashed, 2 if pvtPoints else 1)

                    if i_extend:
                        style = line.style_solid if i_extendL == 'Solid' else line.style_dotted if i_extendL == 'Dotted' else line.style_dashed
                        f_drawLinePVT(time_x11, pivot - range_2 * _level, time_x21, pivot - range_2 * _level, xloc.bar_time, extend.both, (_color if close < pivot else na) if i_relevant else _color, style, 1)
                        f_drawLinePVT(time_x11, pivot + range_2 * _level, time_x21, pivot + range_2 * _level, xloc.bar_time, extend.both, (_color if close > pivot else na) if i_relevant else _color, style, 1)

                    if i_levelsPvt != 'None':
                        time_xx = timenow if i_levelsPvtP == 'Last Bar' else time_x21
                        size__ren__ = size.small if i_levelsPvtS == 'Small' else size.normal
                        if pvtPoints:
                            if _level == 0:
                                f_drawLabelPVT(time_xx, pivot, ('' if i_levelsPvt == 'Prices' else 'PP') + (' (' + string.tostring(pivot, format.mintick) + ')' if i_levelsPvt == 'Levels + Prices' or i_levelsPvt == 'Prices' else ''), xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, _color, size__ren__, text.align_left, string.tostring(pivot, format.mintick))
                            else:
                                f_drawLabelPVT(time_xx, pivot - range_2 * _level, ('' if i_levelsPvt == 'Prices' else ('S1 PP ' if _level == 0.382 else 'S2 PP ' if _level == 0.618 else 'S3 PP ') + string.tostring(_level)) + (' (' + string.tostring(pivot - range_2 * _level, format.mintick) + ')' if i_levelsPvt == 'Levels + Prices' or i_levelsPvt == 'Prices' else ''), xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, (_color if close < pivot else na) if i_relevant else _color, size__ren__, text.align_left, string.tostring(pivot - range_2 * _level, format.mintick))
                                f_drawLabelPVT(time_xx, pivot + range_2 * _level, ('' if i_levelsPvt == 'Prices' else ('R1 PP ' if _level == 0.382 else 'R2 PP ' if _level == 0.618 else 'R3 PP ') + string.tostring(_level)) + (' (' + string.tostring(pivot + range_2 * _level, format.mintick) + ')' if i_levelsPvt == 'Levels + Prices' or i_levelsPvt == 'Prices' else ''), xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, (_color if close > pivot else na) if i_relevant else _color, size__ren__, text.align_left, string.tostring(pivot + range_2 * _level, format.mintick))
                        else:
                            f_drawLabelPVT(time_xx, pivot - range_2 * _level, ('' if i_levelsPvt == 'Prices' else '\u2007\u2007\u2007PP ' + string.tostring(_level)) + (' (' + string.tostring(pivot - range_2 * _level, format.mintick) + ')' if i_levelsPvt == 'Levels + Prices' or i_levelsPvt == 'Prices' else ''), xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, (_color if close < pivot else na) if i_relevant else _color, size__ren__, text.align_left, string.tostring(pivot - range_2 * _level, format.mintick))
                            f_drawLabelPVT(time_xx, pivot + range_2 * _level, ('' if i_levelsPvt == 'Prices' else '\u2007\u2007\u2007PP ' + string.tostring(_level)) + (' (' + string.tostring(pivot + range_2 * _level, format.mintick) + ')' if i_levelsPvt == 'Levels + Prices' or i_levelsPvt == 'Prices' else ''), xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, (_color if close > pivot else na) if i_relevant else _color, size__ren__, text.align_left, string.tostring(pivot + range_2 * _level, format.mintick))

                    if f_crossingLevel(close, pivot - range_2 * _level):
                        alert('AutoFib PivotPoints : ' + syminfo.ticker + ' crossing support level ' + string.tostring(_level))

                    __block_result_14__ = na
                    if f_crossingLevel(close, pivot + range_2 * _level):
                        __block_result_14__ = alert('AutoFib PivotPoints : ' + syminfo.ticker + ' crossing resistance level ' + string.tostring(_level))
                    __block_result_13__ = __block_result_14__
                __block_result_12__ = __block_result_13__
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    f_processLevelX(show_0, value_0, color_0)
    f_processLevelX(show_0_236, value_0_236, color_0_236)
    f_processLevelX(show_0_382, value_0_382, color_0_382)
    f_processLevelX(show_0_5, value_0_5, color_0_5)
    f_processLevelX(show_0_618, value_0_618, color_0_618)
    f_processLevelX(show_0_65, value_0_65, color_0_65)
    f_processLevelX(show_0_786, value_0_786, color_0_786)
    f_processLevelX(show_1, value_1, color_1)
    f_processLevelX(show_1_272, value_1_272, color_1_272)
    f_processLevelX(show_1_414, value_1_414, color_1_414)
    f_processLevelX(show_1_618, value_1_618, color_1_618)
    f_processLevelX(show_1_65, value_1_65, color_1_65)
    f_processLevelX(show_2_618, value_2_618, color_2_618)
    f_processLevelX(show_2_65, value_2_65, color_2_65)
    f_processLevelX(show_3_618, value_3_618, color_3_618)
    f_processLevelX(show_3_65, value_3_65, color_3_65)
    f_processLevelX(show_4_236, value_4_236, color_4_236)
    f_processLevelX(show_4_618, value_4_618, color_4_618)
    f_processLevelX(show_neg_0_236, value_neg_0_236, color_neg_0_236)
    f_processLevelX(show_neg_0_382, value_neg_0_382, color_neg_0_382)
    f_processLevelX(show_neg_0_618, value_neg_0_618, color_neg_0_618)
    f_processLevelX(show_neg_0_65, value_neg_0_65, color_neg_0_65)

    i_histPP = i_histPP and (i_fibTool == 'Pivot Points' or i_fibTool == 'Extensions + Pivot Points' or i_fibTool == 'Retracements + Pivot Points')

    plot(math.avg(htf_h1, htf_l1, htf_c1) if i_histPP and show_0 else na, 'PP', na if cast_bool(ta.change(time(htf))) else color_0, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_236 if i_histPP and show_0_236 else na, 'PP 0_236', na if cast_bool(ta.change(time(htf))) else color_0_236, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_236 if i_histPP and show_0_236 else na, 'PP 0_236', na if cast_bool(ta.change(time(htf))) else color_0_236, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_382 if i_histPP and show_0_382 else na, 'PP 0_382', na if cast_bool(ta.change(time(htf))) else color_0_382, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_382 if i_histPP and show_0_382 else na, 'PP 0_382', na if cast_bool(ta.change(time(htf))) else color_0_382, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_5 if i_histPP and show_0_5 else na, 'PP 0_5  ', na if cast_bool(ta.change(time(htf))) else color_0_5, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_5 if i_histPP and show_0_5 else na, 'PP 0_5  ', na if cast_bool(ta.change(time(htf))) else color_0_5, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_618 if i_histPP and show_0_618 else na, 'PP 0_618', na if cast_bool(ta.change(time(htf))) else color_0_618, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_618 if i_histPP and show_0_618 else na, 'PP 0_618', na if cast_bool(ta.change(time(htf))) else color_0_618, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_65 if i_histPP and show_0_65 else na, 'PP 0_65 ', na if cast_bool(ta.change(time(htf))) else color_0_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_65 if i_histPP and show_0_65 else na, 'PP 0_65 ', na if cast_bool(ta.change(time(htf))) else color_0_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_0_786 if i_histPP and show_0_786 else na, 'PP 0_786', na if cast_bool(ta.change(time(htf))) else color_0_786, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_0_786 if i_histPP and show_0_786 else na, 'PP 0_786', na if cast_bool(ta.change(time(htf))) else color_0_786, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_1 if i_histPP and show_1 else na, 'PP 1    ', na if cast_bool(ta.change(time(htf))) else color_1, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_1 if i_histPP and show_1 else na, 'PP 1    ', na if cast_bool(ta.change(time(htf))) else color_1, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_1_272 if i_histPP and show_1_272 else na, 'PP 1_272', na if cast_bool(ta.change(time(htf))) else color_1_272, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_1_272 if i_histPP and show_1_272 else na, 'PP 1_272', na if cast_bool(ta.change(time(htf))) else color_1_272, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_1_414 if i_histPP and show_1_414 else na, 'PP 1_414', na if cast_bool(ta.change(time(htf))) else color_1_414, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_1_414 if i_histPP and show_1_414 else na, 'PP 1_414', na if cast_bool(ta.change(time(htf))) else color_1_414, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_1_618 if i_histPP and show_1_618 else na, 'PP 1_618', na if cast_bool(ta.change(time(htf))) else color_1_618, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_1_618 if i_histPP and show_1_618 else na, 'PP 1_618', na if cast_bool(ta.change(time(htf))) else color_1_618, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_1_65 if i_histPP and show_1_65 else na, 'PP 1_65 ', na if cast_bool(ta.change(time(htf))) else color_1_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_1_65 if i_histPP and show_1_65 else na, 'PP 1_65 ', na if cast_bool(ta.change(time(htf))) else color_1_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_2_618 if i_histPP and show_2_618 else na, 'PP 2_618', na if cast_bool(ta.change(time(htf))) else color_2_618, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_2_618 if i_histPP and show_2_618 else na, 'PP 2_618', na if cast_bool(ta.change(time(htf))) else color_2_618, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_2_65 if i_histPP and show_2_65 else na, 'PP 2_65 ', na if cast_bool(ta.change(time(htf))) else color_2_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_2_65 if i_histPP and show_2_65 else na, 'PP 2_65 ', na if cast_bool(ta.change(time(htf))) else color_2_65, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) - (htf_h1 - htf_l1) * value_3_618 if i_histPP and show_3_618 else na, 'PP 3_618', na if cast_bool(ta.change(time(htf))) else color_3_618, 1, plot.style_cross, editable=False, display=display__ren__)
    plot(math.avg(htf_h1, htf_l1, htf_c1) + (htf_h1 - htf_l1) * value_3_618 if i_histPP and show_3_618 else na, 'PP 3_618', na if cast_bool(ta.change(time(htf))) else color_3_618, 1, plot.style_cross, editable=False, display=display__ren__)

    i_weightedATR = ta.atr(__input_99__) * __input_100__

    i_vSMA = ta.sma(nz(volume), __input_101__)


    nzVolume = nz(volume)
    bullCandle = close > open
    bearCandle = close < open
    range_1 = math.abs(high - low)

    exhaustVol = nzVolume > i_vSpikeThresh * i_vSMA
    plotchar(exhaustVol if i_vSpikeLb and cast_bool(nzVolume) else False, 'Exhaustion Bar', '🚦', location.abovebar, size=size.tiny, editable=False, display=display__ren__)
    alertcondition(ta.crossover(nzVolume, i_vSMA * i_vSpikeThresh), 'Volume Spikes', 'sign of exhaustion, huge volume increase detected\n{{exchange}}:{{ticker}}->\nOpen = {{open}}, Current = {{close}},\nTime = {{time}}')

    highVolatility = range_1 > i_weightedATR
    plotchar(highVolatility if i_hATRLb else False, 'High Volatile Bar', '⚡', location.belowbar, size=size.tiny, editable=False, display=display__ren__)
    alertcondition(ta.crossover(range_1, i_weightedATR), 'High Volatility', 'high volatility detected\n{{exchange}}:{{ticker}}->\nOpen = {{open}}, Current = {{close}},\nTime = {{time}}')

    vwcbCol = (color.new('#006400') if bullCandle else color.new('#910000')) if nzVolume > i_vSMA * i_vwcbHighThresh else (color.new('#FF9800') if bearCandle else color.new('#7FFFD4')) if nzVolume < i_vSMA * i_vwcbLowThresh else na

    barcolor(vwcbCol if i_vwcb and cast_bool(nzVolume) else na, title='Volume Weighted Colored Bars', editable=False)

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
