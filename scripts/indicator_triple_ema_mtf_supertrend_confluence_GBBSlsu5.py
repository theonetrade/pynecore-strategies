"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, close,
    color, display, fill, format, high, input, label, low, math, na, plot, position, request,
    scale, script, size, string, syminfo, ta, table, xloc, yloc
)
from pynecore.types import Label, Persistent, Series, Table

groupEMA: str = "EMA Settings"
groupST: str = "Multi-Timeframe Supertrend"
groupDisplay: str = "Display Settings"
groupConfluence: str = "Confluence Settings"
groupDashboard: str = "Dashboard Settings"


@script.indicator("Triple EMA + MTF Supertrend Confluence FIXED", overlay=True, scale=scale.none, behind_chart=False, max_labels_count=500)
def main(
    showEMA1=input.bool(True, "Show EMA 1", group=groupEMA),
    showEMA2=input.bool(True, "Show EMA 2", group=groupEMA),
    showEMA3=input.bool(True, "Show EMA 3", group=groupEMA),
    ema1Length=input.int(20, "EMA 1 Length", minval=1, group=groupEMA),
    ema2Length=input.int(50, "EMA 2 Length", minval=1, group=groupEMA),
    ema3Length=input.int(200, "EMA 3 Length", minval=1, group=groupEMA),
    emaWidth=input.int(2, "EMA Line Width", minval=1, maxval=5, group=groupEMA),
    showSupertrend=input.bool(True, "Show Supertrend", group=groupST),
    supertrendTimeframe=input.timeframe("60", "Supertrend Timeframe", group=groupST),
    supertrendFactor=input.float(3.0, "Supertrend Factor", minval=0.1, step=0.1, group=groupST),
    supertrendATRPeriod=input.int(10, "Supertrend ATR Period", minval=1, group=groupST),
    supertrendWidth=input.int(2, "Supertrend Line Width", minval=1, maxval=5, group=groupST),
    showSupertrendLabels=input.bool(True, "Show Supertrend Flip Labels", group=groupST),
    showSupertrendShading=input.bool(True, "Show Supertrend Shading", group=groupST),
    shadingTransparency=input.int(88, "Shading Transparency", minval=0, maxval=100, group=groupST),
    showFlipLabels=input.bool(True, "Show EMA Flip Labels", group=groupDisplay),
    showConfluenceLabels=input.bool(True, "Show Confluence Labels", group=groupDisplay),
    showDashboard=input.bool(True, "Show Dashboard", group=groupDisplay),
    enableLabelExpiry=input.bool(True, "Enable EMA Label Expiry", group=groupDisplay),
    labelExpiryBars=input.int(50, "EMA Label Expiry Bars", minval=1, group=groupDisplay),
    enableConfluenceExpiry=input.bool(True, "Enable Confluence Label Expiry", group=groupConfluence),
    confluenceExpiryBars=input.int(50, "Confluence Expiry Bars", minval=1, group=groupConfluence),
    keepLatestBullish=input.bool(True, "Keep Latest Bullish Confluence", group=groupConfluence),
    keepLatestBearish=input.bool(True, "Keep Latest Bearish Confluence", group=groupConfluence),
    dashboardPositionInput=input.string("Top Right", "Dashboard Position", options=("Top Left", "Top Center", "Top Right", "Middle Left", "Middle Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"), group=groupDashboard),
    showDistanceInTicks=input.bool(False, "Show Distance In Ticks", group=groupDashboard)
):
    dashboardPosition = position.top_left if dashboardPositionInput == 'Top Left' else position.top_center if dashboardPositionInput == 'Top Center' else position.top_right if dashboardPositionInput == 'Top Right' else position.middle_left if dashboardPositionInput == 'Middle Left' else position.middle_center if dashboardPositionInput == 'Middle Center' else position.middle_right if dashboardPositionInput == 'Middle Right' else position.bottom_left if dashboardPositionInput == 'Bottom Left' else position.bottom_center if dashboardPositionInput == 'Bottom Center' else position.bottom_right

    ema1 = ta.ema(close, ema1Length)
    ema2 = ta.ema(close, ema2Length)
    ema3 = ta.ema(close, ema3Length)

    ema1Bullish: Series = close > ema1
    ema1Bearish: Series = close < ema1

    ema2Bullish: Series = close > ema2
    ema2Bearish: Series = close < ema2

    ema3Bullish: Series = close > ema3
    ema3Bearish: Series = close < ema3

    plot(ema1 if showEMA1 else na, title='EMA 20', color=color.blue, linewidth=emaWidth, style=plot.style_line, force_overlay=True)

    plot(ema2 if showEMA2 else na, title='EMA 50', color=color.yellow, linewidth=emaWidth, style=plot.style_line, force_overlay=True)

    plot(ema3 if showEMA3 else na, title='EMA 200', color=color.orange, linewidth=emaWidth, style=plot.style_line, force_overlay=True)

    ema1Distance = close - ema1
    ema2Distance = close - ema2
    ema3Distance = close - ema3

    ema1DistanceTicks = ema1Distance / syminfo.mintick
    ema2DistanceTicks = ema2Distance / syminfo.mintick
    ema3DistanceTicks = ema3Distance / syminfo.mintick

    ema1DistanceText = string.tostring(ema1Distance, format.mintick) + ' pts / ' + string.tostring(math.round(ema1DistanceTicks)) + ' ticks' if showDistanceInTicks else string.tostring(ema1Distance, format.mintick) + ' pts'

    ema2DistanceText = string.tostring(ema2Distance, format.mintick) + ' pts / ' + string.tostring(math.round(ema2DistanceTicks)) + ' ticks' if showDistanceInTicks else string.tostring(ema2Distance, format.mintick) + ' pts'

    ema3DistanceText = string.tostring(ema3Distance, format.mintick) + ' pts / ' + string.tostring(math.round(ema3DistanceTicks)) + ' ticks' if showDistanceInTicks else string.tostring(ema3Distance, format.mintick) + ' pts'

    ema1DistanceColor = color.green if ema1Distance > 0 else color.red if ema1Distance < 0 else color.gray

    ema2DistanceColor = color.green if ema2Distance > 0 else color.red if ema2Distance < 0 else color.gray

    ema3DistanceColor = color.green if ema3Distance > 0 else color.red if ema3Distance < 0 else color.gray

    ema1BullishFlip = ema1Bullish and (not ema1Bullish[1])
    ema1BearishFlip = ema1Bearish and (not ema1Bearish[1])

    ema2BullishFlip = ema2Bullish and (not ema2Bullish[1])
    ema2BearishFlip = ema2Bearish and (not ema2Bearish[1])

    ema3BullishFlip = ema3Bullish and (not ema3Bullish[1])
    ema3BearishFlip = ema3Bearish and (not ema3Bearish[1])

    emaLabels: Persistent[list[Label]] = array.new_label()

    def f_createEMALabel(_x, _y, _text, _style, _bgColor, _textColor):
        newLabel: Label = label.new(x=_x, y=_y, text=_text, xloc=xloc.bar_index, yloc=yloc.price, style=_style, color=_bgColor, textcolor=_textColor, size=size.tiny, force_overlay=True)

        return array.push(emaLabels, newLabel)

    if enableLabelExpiry and array.size(emaLabels) > 0:
        for i in pine_range(array.size(emaLabels) - 1, 0):
            currentLabel: Label = array.get(emaLabels, i)

            labelAge: int = bar_index - label.get_x(currentLabel)

            if labelAge >= labelExpiryBars:
                label.delete(currentLabel)

                array.remove(emaLabels, i)

    if showFlipLabels and ema1BullishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, low, 'EMA ' + string.tostring(ema1Length) + '\nBULL', label.style_label_up, color.blue, color.white)

    if showFlipLabels and ema1BearishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, high, 'EMA ' + string.tostring(ema1Length) + '\nBEAR', label.style_label_down, color.blue, color.white)

    if showFlipLabels and ema2BullishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, low, 'EMA ' + string.tostring(ema2Length) + '\nBULL', label.style_label_up, color.yellow, color.black)

    if showFlipLabels and ema2BearishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, high, 'EMA ' + string.tostring(ema2Length) + '\nBEAR', label.style_label_down, color.yellow, color.black)

    if showFlipLabels and ema3BullishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, low, 'EMA ' + string.tostring(ema3Length) + '\nBULL', label.style_label_up, color.orange, color.black)

    if showFlipLabels and ema3BearishFlip and barstate.isconfirmed:
        f_createEMALabel(bar_index, high, 'EMA ' + string.tostring(ema3Length) + '\nBEAR', label.style_label_down, color.orange, color.black)

    def f_getSupertrend():
        return ta.supertrend(supertrendFactor, supertrendATRPeriod)

    supertrendValue, supertrendDirection = request.security(syminfo.tickerid, supertrendTimeframe, f_getSupertrend(), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    supertrendBullish: Series = supertrendDirection < 0

    supertrendBearish: Series = supertrendDirection > 0

    supertrendBullishFlip = supertrendBullish and (not supertrendBullish[1])

    supertrendBearishFlip = supertrendBearish and (not supertrendBearish[1])

    supertrendColor = color.green if supertrendBullish else color.red

    supertrendPlot = plot(supertrendValue if showSupertrend else na, title='MTF Supertrend', color=supertrendColor, linewidth=supertrendWidth, style=plot.style_linebr, force_overlay=True)

    bullishBase = plot(low if showSupertrend and showSupertrendShading and supertrendBullish else na, title='Bullish Shading Base', display=display.none, force_overlay=True)

    bearishBase = plot(high if showSupertrend and showSupertrendShading and supertrendBearish else na, title='Bearish Shading Base', display=display.none, force_overlay=True)

    fill(supertrendPlot, bullishBase, color=color.new(color.green, shadingTransparency), title='Bullish Supertrend Shading')

    fill(supertrendPlot, bearishBase, color=color.new(color.red, shadingTransparency), title='Bearish Supertrend Shading')

    if showSupertrendLabels and supertrendBullishFlip and barstate.isconfirmed:
        label.new(x=bar_index, y=low, text='ST ' + supertrendTimeframe + '\nBULL', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.green, textcolor=color.white, size=size.tiny, force_overlay=True)

    if showSupertrendLabels and supertrendBearishFlip and barstate.isconfirmed:
        label.new(x=bar_index, y=high, text='ST ' + supertrendTimeframe + '\nBEAR', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.red, textcolor=color.white, size=size.tiny, force_overlay=True)

    allBullish = ema1Bullish and ema2Bullish and ema3Bullish

    allBearish = ema1Bearish and ema2Bearish and ema3Bearish

    confluenceState: Series = 1 if allBullish else -1 if allBearish else 0

    previousConfluenceState = confluenceState[1]

    bullishConfluence = confluenceState == 1 and previousConfluenceState != 1

    bearishConfluence = confluenceState == -1 and previousConfluenceState != -1

    neutralConfluence = confluenceState == 0 and previousConfluenceState != 0

    confluenceLabels: Persistent[list[Label]] = array.new_label()

    confluenceLabelBars: Persistent[list[int]] = array.new_int()

    confluenceLabelBullish: Persistent[list[bool]] = array.new_bool()

    if showConfluenceLabels and bullishConfluence and barstate.isconfirmed:
        if keepLatestBullish and array.size(confluenceLabels) > 0:
            for i in pine_range(array.size(confluenceLabels) - 1, 0):
                existingBullish: bool = array.get(confluenceLabelBullish, i)

                if existingBullish:
                    label.delete(array.get(confluenceLabels, i))

                    array.remove(confluenceLabels, i)

                    array.remove(confluenceLabelBars, i)

                    array.remove(confluenceLabelBullish, i)

        bullishLabel: Label = label.new(x=bar_index, y=low, text='BULLISH\nCONFLUENCE', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small, force_overlay=True)

        array.push(confluenceLabels, bullishLabel)

        array.push(confluenceLabelBars, bar_index)

        array.push(confluenceLabelBullish, True)

    if showConfluenceLabels and bearishConfluence and barstate.isconfirmed:
        if keepLatestBearish and array.size(confluenceLabels) > 0:
            for i in pine_range(array.size(confluenceLabels) - 1, 0):
                existingBullish: bool = array.get(confluenceLabelBullish, i)

                if not existingBullish:
                    label.delete(array.get(confluenceLabels, i))

                    array.remove(confluenceLabels, i)

                    array.remove(confluenceLabelBars, i)

                    array.remove(confluenceLabelBullish, i)

        bearishLabel: Label = label.new(x=bar_index, y=high, text='BEARISH\nCONFLUENCE', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small, force_overlay=True)

        array.push(confluenceLabels, bearishLabel)

        array.push(confluenceLabelBars, bar_index)

        array.push(confluenceLabelBullish, False)

    if enableConfluenceExpiry and array.size(confluenceLabels) > 0:
        for i in pine_range(array.size(confluenceLabels) - 1, 0):
            createdBar: int = array.get(confluenceLabelBars, i)

            if bar_index - createdBar >= confluenceExpiryBars:
                label.delete(array.get(confluenceLabels, i))

                array.remove(confluenceLabels, i)

                array.remove(confluenceLabelBars, i)

                array.remove(confluenceLabelBullish, i)

    dashboard: Persistent[Table] = table.new(dashboardPosition, 3, 8, border_width=1)

    overallStatus = 'BULLISH' if allBullish else 'BEARISH' if allBearish else 'NEUTRAL'

    overallStatusColor = color.green if allBullish else color.red if allBearish else color.gray

    supertrendStatus = 'BULLISH' if supertrendBullish else 'BEARISH' if supertrendBearish else 'NEUTRAL'

    supertrendStatusColor = color.green if supertrendBullish else color.red if supertrendBearish else color.gray

    if barstate.islast and showDashboard:
        table.cell(dashboard, 0, 0, 'EMA', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 1, 0, 'PRICE', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 2, 0, 'DISTANCE', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 0, 1, 'EMA ' + string.tostring(ema1Length), bgcolor=color.blue, text_color=color.white)

        table.cell(dashboard, 1, 1, string.tostring(ema1, format.mintick), bgcolor=color.green if ema1Bullish else color.red, text_color=color.white)

        table.cell(dashboard, 2, 1, ema1DistanceText, bgcolor=ema1DistanceColor, text_color=color.white)

        table.cell(dashboard, 0, 2, 'EMA ' + string.tostring(ema2Length), bgcolor=color.yellow, text_color=color.black)

        table.cell(dashboard, 1, 2, string.tostring(ema2, format.mintick), bgcolor=color.green if ema2Bullish else color.red, text_color=color.white)

        table.cell(dashboard, 2, 2, ema2DistanceText, bgcolor=ema2DistanceColor, text_color=color.white)

        table.cell(dashboard, 0, 3, 'EMA ' + string.tostring(ema3Length), bgcolor=color.orange, text_color=color.black)

        table.cell(dashboard, 1, 3, string.tostring(ema3, format.mintick), bgcolor=color.green if ema3Bullish else color.red, text_color=color.white)

        table.cell(dashboard, 2, 3, ema3DistanceText, bgcolor=ema3DistanceColor, text_color=color.white)

        table.cell(dashboard, 0, 4, 'EMA OVERALL', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 1, 4, overallStatus, bgcolor=overallStatusColor, text_color=color.white)

        table.cell(dashboard, 2, 4, 'ALL ABOVE' if allBullish else 'ALL BELOW' if allBearish else 'MIXED', bgcolor=overallStatusColor, text_color=color.white)

        table.cell(dashboard, 0, 5, 'ST ' + supertrendTimeframe, bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 1, 5, supertrendStatus, bgcolor=supertrendStatusColor, text_color=color.white)

        table.cell(dashboard, 2, 5, string.tostring(supertrendValue, format.mintick), bgcolor=supertrendStatusColor, text_color=color.white)

        table.cell(dashboard, 0, 6, 'CURRENT PRICE', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 1, 6, string.tostring(close, format.mintick), bgcolor=color.gray, text_color=color.white)

        table.cell(dashboard, 2, 6, '', bgcolor=color.gray)

        table.cell(dashboard, 0, 7, 'TICK SIZE', bgcolor=color.black, text_color=color.white)

        table.cell(dashboard, 1, 7, string.tostring(syminfo.mintick, format.mintick), bgcolor=color.gray, text_color=color.white)

        table.cell(dashboard, 2, 7, '1 TICK', bgcolor=color.gray, text_color=color.white)

    if barstate.islast and (not showDashboard):
        table.clear(dashboard, 0, 0, 2, 7)

    alertcondition(ema1BullishFlip and barstate.isconfirmed, title='EMA 1 Bullish Flip', message='EMA 1 has flipped BULLISH.')

    alertcondition(ema1BearishFlip and barstate.isconfirmed, title='EMA 1 Bearish Flip', message='EMA 1 has flipped BEARISH.')

    alertcondition(ema2BullishFlip and barstate.isconfirmed, title='EMA 2 Bullish Flip', message='EMA 2 has flipped BULLISH.')

    alertcondition(ema2BearishFlip and barstate.isconfirmed, title='EMA 2 Bearish Flip', message='EMA 2 has flipped BEARISH.')

    alertcondition(ema3BullishFlip and barstate.isconfirmed, title='EMA 3 Bullish Flip', message='EMA 3 has flipped BULLISH.')

    alertcondition(ema3BearishFlip and barstate.isconfirmed, title='EMA 3 Bearish Flip', message='EMA 3 has flipped BEARISH.')

    alertcondition(supertrendBullishFlip and barstate.isconfirmed, title='MTF Supertrend Bullish Flip', message='MTF Supertrend has flipped BULLISH.')

    alertcondition(supertrendBearishFlip and barstate.isconfirmed, title='MTF Supertrend Bearish Flip', message='MTF Supertrend has flipped BEARISH.')

    alertcondition(bullishConfluence and barstate.isconfirmed, title='Bullish EMA Confluence', message='BULLISH EMA CONFLUENCE.')

    alertcondition(bearishConfluence and barstate.isconfirmed, title='Bearish EMA Confluence', message='BEARISH EMA CONFLUENCE.')

    if bullishConfluence and barstate.isconfirmed:
        alert('BULLISH EMA CONFLUENCE: EMA 20, EMA 50 and EMA 200 are all bullish.', alert.freq_once_per_bar_close)

    if bearishConfluence and barstate.isconfirmed:
        alert('BEARISH EMA CONFLUENCE: EMA 20, EMA 50 and EMA 200 are all bearish.', alert.freq_once_per_bar_close)

    if supertrendBullishFlip and barstate.isconfirmed:
        alert('MTF SUPERTREND BULLISH FLIP.', alert.freq_once_per_bar_close)

    if supertrendBearishFlip and barstate.isconfirmed:
        alert('MTF SUPERTREND BEARISH FLIP.', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)