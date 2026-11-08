"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barcolor, barstate, box, chart, close, color,
    display, extend, format, high, input, label, last_bar_index, line, linefill, location, low,
    math, na, nz, open, plot, plotshape, position, script, shape, size, string, syminfo, ta, table,
    text, time, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Color, Line, LineFill, Persistent, PersistentSeries, Series, Table

display__ren__ = display.all - display.status_line
group_phase9: str = 'Dual-Phase Exhaustion'
tooltip_phase9 = 'Tracks sequential trend exhaustion across two distinct phases: Momentum Exhaustion and Terminal Exhaustion.\n\n' + '• Completed Only: Displays completed Momentum and Terminal phase markers.\n' + '• All Sequence Steps: Displays the full sequence as it develops.\n' + '• None: Hides phase markers.'
group_pivot: str = 'Range Pivot Settings'
tooltip_pivot: str = 'Displays higher-timeframe Support (S), Pivot (P), and Resistance (R) levels calculated from the selected range.'
tooltip_pressure: str = 'Volume Pressure Oscillator\nEstimates relative buying and selling pressure by weighting directional price movement within each bar\'s range by traded volume.\nThe resulting oscillator is normalized to a 0–100 scale, where higher values indicate greater relative buying pressure and lower values indicate greater relative selling pressure.'
group_pressure: str = 'Volume Pressure Settings'
group_volume_weighted_colored_bars: str = 'Volume-Weighted Bars'
group_dashboard: str = 'Dashboard'


@script.indicator("Dual-Phase Reversal by DGT", "DPR ☼☾", True, max_labels_count=500, max_lines_count=500, max_boxes_count=500, max_bars_back=5000)
def main(
    showPhaseMarkers=input.string('Completed Only', 'Phase Display Mode', options=('Completed Only', 'All Sequence Steps', 'None'), display=display__ren__, group=group_phase9, tooltip=tooltip_phase9),
    phaseSRLevels=input.bool(True, 'Momentum Support & Resistance Levels', group=group_phase9, tooltip='Projects dynamic Support and Resistance levels derived from completed Momentum Exhaustion phases. Levels remain active until price crosses the corresponding level.'),
    stopLevels=input.bool(False, 'Momentum & Terminal Invalidation Levels', group=group_phase9, tooltip='Displays structural invalidation levels derived from the price extremes established during Momentum and Terminal Exhaustion phases. Each level remains active until price crosses it.'),
    htf=input.string('Auto', 'Pivot Timeframe', display=display__ren__, options=('Auto', '1 Hour', '4 Hour', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'), group=group_pivot, tooltip='Selects the higher-timeframe range used to calculate Support (S), Pivot (P), and Resistance (R) levels. Auto selects the range according to the chart timeframe.'),
    i_isPivot=input.bool(True, 'Range Pivot', group=group_pivot, tooltip=tooltip_pivot),
    i_dispPVT=input.bool(False, 'Developing Range Pivot', group=group_pivot, tooltip='Projects Support, Pivot, and Resistance levels from the current, still-forming higher-timeframe range — an early preview of the next range\'s pivot, updating in real time as the range develops, before it closes.'),
    i_disphist=input.bool(False, 'Historical Range Pivot', group=group_pivot, tooltip='Displays the historical Support, Pivot, and Resistance levels of completed higher-timeframe ranges.'),
    color_r=input.color(color.red, '  Resistance', inline='col', group=group_pivot),
    color_s=input.color(color.teal, 'Support', inline='col', group=group_pivot),
    isPressureEnabled=input.bool(True, 'Volume Pressure', inline='PRS', group=group_pressure, tooltip=tooltip_pressure),
    oscColor=input.color(color.new('#00BCD4'), '', inline='PRS', group=group_pressure),
    pressureLength=input.int(13, '  Pressure Length', display=display__ren__, minval=1, group=group_pressure),
    upperBand=input.int(75, '  Pressure Upper Band', display=display__ren__, group=group_pressure),
    lowerBand=input.int(25, '  Pressure Lower Band', display=display__ren__, group=group_pressure),
    oscLookbackLength=input.int(200, '  Display Length', display=display__ren__, minval=10, step=10, maxval=475, group=group_pressure),
    oscPlacement=input.string('Bottom', '  Placement', display=display__ren__, options=('Top', 'Middle', 'Bottom'), group=group_pressure),
    __input_16__=input.int(9, '  Height', display=display__ren__, minval=1, maxval=10, group=group_pressure),
    __input_17__=input.int(5, "  Vertical Offset", display=display__ren__, minval=-3, maxval=10, group=group_pressure),
    vwcb=input.bool(True, 'Volume-Weighted Bars', group=group_volume_weighted_colored_bars, tooltip='Volume-Weighted Bars\nColors bars according to current volume relative to its Volume Moving Average.\nHigher-volume and lower-volume bars receive stronger visual emphasis.'),
    __input_19__=input.int(89, '  Volume MA Length', display=display__ren__, group=group_volume_weighted_colored_bars),
    upThesh=input.float(1.618, '  High-Volume Multiplier', display=display__ren__, minval=1.0, step=0.1, group=group_volume_weighted_colored_bars),
    __input_21__=input.float(0.618, '  Low-Volume Multiplier', display=display__ren__, minval=0.1, step=0.1, group=group_volume_weighted_colored_bars),
    showDashboard=input.bool(True, 'Dashboard', inline='DB', group=group_dashboard),
    dashboardPosition=input.string('Top Right', '', inline='DB', display=display__ren__, options=('Top Right', 'Top Left', 'Bottom Left'), group=group_dashboard)
):
    def f_drawLineX(_x1, _y1, _x2, _y2, _xloc, _extend, _color, _style, _width):
        id: Persistent = line.new(_x1, _y1, _x2, _y2, _xloc, _extend, _color, _style, _width)
        __block_result__ = na
        if _y1 > 0 and _y2 > 0:
            line.set_xy1(id, _x1, _y1)
            line.set_xy2(id, _x2, _y2)
            __block_result__ = line.set_color(id, _color)
        else:
            line.set_xy1(id, _x1, close)
            line.set_xy2(id, _x2, close)
            __block_result__ = line.set_color(id, color.new('#00000000'))
        return __block_result__

    def f_drawLabelX(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip):
        id: Persistent = label.new(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip)
        label.set_text(id, _text)
        label.set_tooltip(id, _tooltip)
        __block_result_1__ = na
        if _y > 0:
            label.set_xy(id, _x, _y)
            __block_result_1__ = label.set_textcolor(id, _textcolor)
        else:
            label.set_xy(id, _x, close)
            __block_result_1__ = label.set_textcolor(id, color.new('#00000000'))
        return __block_result_1__

    def f_crossingLevelX(_price: Series, _level):
        return not na(_level) and _level != 0 and (_level > _price and _level < _price[1] or (_level < _price and _level > _price[1]))

    def f_processPivotLevelX(_show, _x1, _y, _x2, _c, _s, _w, _lb, _tip):
        if _show:
            style = line.style_solid if _s == 'Solid' else line.style_dotted if _s == 'Dotted' else line.style_dashed
            f_drawLineX(_x1, _y, _x2, _y, xloc.bar_time, extend.none, _c, style, _w)
            f_drawLabelX(_x2, _y, _lb + ' (' + string.tostring(_y, format.mintick) + ')', xloc.bar_time, yloc.price, color.new('#00000000'), label.style_label_left, _c, size.normal, text.align_left, _tip + ' ' + _lb + '\n' + string.tostring(_y, format.mintick))
        __block_result_2__ = na
        if f_crossingLevelX(close, _y) and _tip != 'Developing Range Pivot':
            __block_result_2__ = alert(syminfo.ticker + ' crossing ' + _tip + ' ' + _lb + ' level, price ' + string.tostring(_y, format.mintick))
        return __block_result_2__

    def f_htf_ohlc(_htf):
        htf_o: Persistent[float] = 0.0
        htf_h: Persistent[float] = 0.0
        htf_l: Persistent[float] = 0.0
        htf_c: Series = close
        htf_ox: Persistent[float] = 0.0
        htf_hx: Persistent[float] = 0.0
        htf_lx: Persistent[float] = 0.0
        htf_cx: Persistent[float] = 0.0
        if ta.change(time(_htf)) != 0:
            htf_ox = htf_o
            htf_o = open
            htf_hx = htf_h
            htf_h = high
            htf_lx = htf_l
            htf_l = low
            htf_cx = htf_c[1]
            htf_c = close
        else:
            htf_h = math.max(high, htf_h)
            htf_l = math.min(low, htf_l)
        return (htf_ox, htf_hx, htf_lx, htf_cx, htf_o, htf_h, htf_l, htf_c)

    def f_get_pivot(_o, _h, _l, _c, _o0):
        r1x: Persistent[float] = 0.0
        px: Persistent[float] = 0.0
        s1x: Persistent[float] = 0.0
        x = _h + 2 * _l + _c if _c < _o else 2 * _h + _l + _c if _c > _o else _h + _l + 2 * _c
        px = x / 4
        s1x = x / 2 - _h
        r1x = x / 2 - _l
        return (r1x, px, s1x)

    def ma(_source, _length, _type):
        __block_result_3__ = na
        __switch__ = _type
        if __switch__ == "SMA":
            __block_result_3__ = ta.sma(_source, _length)
        elif __switch__ == "EMA":
            __block_result_3__ = ta.ema(_source, _length)
        elif __switch__ == "RMA":
            __block_result_3__ = ta.rma(_source, _length)
        elif __switch__ == "WMA":
            __block_result_3__ = ta.wma(_source, _length)
        elif __switch__ == "VWMA":
            __block_result_3__ = ta.vwma(_source, _length)
        return __block_result_3__



    compltedPhases = showPhaseMarkers == 'Completed Only'
    showNone = False if showPhaseMarkers == 'None' else True

    htf_user = '60' if htf == '1 Hour' else '240' if htf == '4 Hour' else 'D' if htf == 'Daily' else 'W' if htf == 'Weekly' else 'M' if htf == 'Monthly' else '3M' if htf == 'Quarterly' else '12M'
    htf_auto = '60' if timeframe.period == '1' else '60' if timeframe.period == '3' else '240' if timeframe.period == '5' else '240' if timeframe.period == '15' else 'D' if timeframe.period == '30' else 'D' if timeframe.period == '45' else 'D' if timeframe.period == '60' else 'W' if timeframe.period == '120' else 'W' if timeframe.period == '180' else 'W' if timeframe.period == '240' else 'M' if timeframe.period == '1D' else '3M' if timeframe.period == '1W' else '12M'

    i_htf = htf_auto if htf == 'Auto' else htf_user

    oscLookbackLength = last_bar_index if last_bar_index < oscLookbackLength else oscLookbackLength
    oscHight = 11 - __input_16__
    oscVerticalOffset = __input_17__ / 10
    fillColor = color.new(color.new('#2962FF'), 97)

    priceOpen: Series = open
    priceHigh: Series = high
    priceLow: Series = low
    priceClose: Series = close

    buyPhaseCondition = priceClose < priceClose[4]
    sellPhaseCondition = priceClose > priceClose[4]

    buyMomentumShift = priceClose < priceClose[4] and priceClose[1] > priceClose[5]
    sellMomentumShift = priceClose > priceClose[4] and priceClose[1] < priceClose[5]

    buyCount: Persistent[int] = 0
    sellCount: Persistent[int] = 0

    if buyPhaseCondition:
        buyCount = (1 if buyMomentumShift else 0) if buyCount == 0 or buyCount == 9 else buyCount + 1
        sellCount = 0
    elif sellPhaseCondition:
        sellCount = (1 if sellMomentumShift else 0) if sellCount == 0 or sellCount == 9 else sellCount + 1
        buyCount = 0
    else:
        buyCount = 0
        sellCount = 0

    buyPhaseQualified = priceLow <= priceLow[3] and priceLow <= priceLow[2] or (priceLow[1] <= priceLow[3] and priceLow[1] <= priceLow[2])
    sellPhaseQualified = priceHigh >= priceHigh[3] and priceHigh >= priceHigh[2] or (priceHigh[1] >= priceHigh[3] and priceHigh[1] >= priceHigh[2])

    plotshape(showNone and buyCount == 1 and (not compltedPhases), 'Buy ME 1', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₁', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 2 and (not compltedPhases), 'Buy ME 2', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₂', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 3 and (not compltedPhases), 'Buy ME 3', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₃', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 4 and (not compltedPhases), 'Buy ME 4', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₄', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 5 and (not compltedPhases), 'Buy ME 5', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₅', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 6 and (not compltedPhases), 'Buy ME 6', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₆', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 7 and (not compltedPhases), 'Buy ME 7', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₇', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 8 and (not compltedPhases) and (not buyPhaseQualified), 'Buy ME 8', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₈', color.red, False, display=display__ren__)
    plotshape(showNone and buyCount == 8 and (not compltedPhases) and buyPhaseQualified, 'Buy ME 8 Qualified', shape.labeldown, location.abovebar, color.new(color.teal, 75), 0, 'ǫ₈', color.white, False, display=display__ren__)
    plotshape(showNone and buyCount == 9 and (not buyPhaseQualified), 'Buy ME 9', shape.labelup, location.belowbar, color.new(color.teal, 25), 0, 'ᴍ', color.white, True, size.tiny, display=display__ren__)
    plotshape(showNone and buyCount == 9 and buyPhaseQualified, 'Buy ME 9 Qualified', shape.labelup, location.belowbar, color.new(color.teal, 25), 0, 'ᴍ\nǫ', color.white, True, size.tiny, display=display__ren__)

    phase9Resistance = ta.highest(9)
    buyPhaseResistance: Series[float] = 0.0
    buyPhaseResistance = phase9Resistance if buyCount == 9 else 0 if priceClose > buyPhaseResistance[1] else buyPhaseResistance[1]
    plot(buyPhaseResistance if phaseSRLevels and buyPhaseResistance > 0 else na, 'ME Resistance', color.red, 1, plot.style_linebr, display=display__ren__)

    buyPhaseHigh: Persistent[float] = 0.0
    buyPhaseLowest: Persistent[float] = 0.0

    if buyCount == 1:
        buyPhaseLowest = priceLow

    if buyCount > 0:
        buyPhaseLowest = math.min(priceLow, buyPhaseLowest)
        if priceLow == buyPhaseLowest:
            buyPhaseHigh = priceHigh

    buyPhaseStopPrice = 2 * buyPhaseLowest - buyPhaseHigh
    buyPhaseStopLevel: Series[float] = 0.0
    buyPhaseStopLevel = buyPhaseStopPrice if buyCount == 9 else 0 if priceClose < buyPhaseStopLevel[1] else buyPhaseStopLevel[1]
    plot(buyPhaseStopLevel if stopLevels and buyPhaseStopLevel > 0 else na, 'ME Buy Invalidation', color.blue, 1, plot.style_circles, display=display__ren__)

    plotshape(showNone and sellCount == 1 and (not compltedPhases), 'Sell ME 1', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₁', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 2 and (not compltedPhases), 'Sell ME 2', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₂', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 3 and (not compltedPhases), 'Sell ME 3', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₃', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 4 and (not compltedPhases), 'Sell ME 4', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₄', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 5 and (not compltedPhases), 'Sell ME 5', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₅', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 6 and (not compltedPhases), 'Sell ME 6', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₆', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 7 and (not compltedPhases), 'Sell ME 7', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₇', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 8 and (not compltedPhases) and (not sellPhaseQualified), 'Sell ME 8', shape.labeldown, location.abovebar, color.new('#00000000'), 0, '₈', color.teal, False, display=display__ren__)
    plotshape(showNone and sellCount == 8 and (not compltedPhases) and sellPhaseQualified, 'Sell ME 8 Qualified', shape.labeldown, location.abovebar, color.new(color.red, 75), 0, 'ǫ₈', color.white, False, display=display__ren__)
    plotshape(showNone and sellCount == 9 and (not sellPhaseQualified), 'Sell ME 9', shape.labeldown, location.abovebar, color.new(color.red, 25), 0, 'ᴍ', color.white, True, size.tiny, display=display__ren__)
    plotshape(showNone and sellCount == 9 and sellPhaseQualified, 'Sell ME 9 Qualified', shape.labeldown, location.abovebar, color.new(color.red, 25), 0, 'ǫ\nᴍ', color.white, True, size.tiny, display=display__ren__)

    phase9Support = ta.lowest(9)
    sellPhaseSupport: Series[float] = 0.0
    sellPhaseSupport = phase9Support if sellCount == 9 else 0 if priceClose < sellPhaseSupport[1] else sellPhaseSupport[1]
    plot(sellPhaseSupport if phaseSRLevels and sellPhaseSupport > 0 else na, 'ME Support', color.teal, 1, plot.style_linebr, display=display__ren__)

    sellPhaseHighest: Persistent[float] = 0.0
    sellPhaseLow: Persistent[float] = 0.0

    if sellCount == 1:
        sellPhaseHighest = priceHigh

    if sellCount > 0:
        sellPhaseHighest = math.max(priceHigh, sellPhaseHighest)
        if priceHigh == sellPhaseHighest:
            sellPhaseLow = priceLow

    sellPhaseStopPrice = 2 * sellPhaseHighest - sellPhaseLow
    sellPhaseStopLevel: Series[float] = 0.0
    sellPhaseStopLevel = sellPhaseStopPrice if sellCount == 9 else 0 if priceClose > sellPhaseStopLevel[1] else sellPhaseStopLevel[1]
    plot(sellPhaseStopLevel if stopLevels and sellPhaseStopLevel > 0 else na, 'ME Sell Invalidation', color.blue, 1, plot.style_circles, display=display__ren__)

    sellExhaustionCount: PersistentSeries[int] = 0
    buyExhaustionCount: PersistentSeries[int] = 0

    startBuyExhaustion13: PersistentSeries[bool] = False
    buyExhaustion13RefClose8: Persistent[float] = 0.0
    buyExhaustion13Condition = True if priceClose <= priceLow[2] else False
    buyExhaustionBar13Fails = True if priceClose <= priceLow[2] and priceLow >= buyExhaustion13RefClose8 else False

    __block_result_4__ = na
    if buyCount == 9 and buyExhaustionCount == 0:
        __block_result_4__ = True
    else:
        __block_result_5__ = na
        if sellCount == 9 or buyExhaustionCount == 13 or priceClose > buyPhaseResistance:
            __block_result_5__ = False
        else:
            __block_result_5__ = startBuyExhaustion13[1]
        __block_result_4__ = __block_result_5__
    startBuyExhaustion13 = __block_result_4__

    buyExhaustionCount = ((1 if buyExhaustion13Condition else 0) if buyCount == 9 else buyExhaustionCount + 1 if buyExhaustion13Condition else buyExhaustionCount) if startBuyExhaustion13 else 0
    buyExhaustionCount = buyExhaustionCount - 1 if buyExhaustionCount == 13 and buyExhaustionBar13Fails else buyExhaustionCount

    if buyExhaustionCount == 8 and buyExhaustionCount != buyExhaustionCount[1]:
        buyExhaustion13RefClose8 = priceClose

    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 1), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 2), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₂', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 3), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₃', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 4), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₄', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 5), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₅', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 6), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₆', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 7), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₇', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 8), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₈', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 9), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₉', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 10), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₀', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 11), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₁', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 12), 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₂', color.red, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startBuyExhaustion13 and (buyExhaustionCount == buyExhaustionCount[1]) and (buyExhaustionCount == 12) and buyExhaustionBar13Fails, 'Buy TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₊', color.red, False, display=display__ren__)
    plotshape(showNone and startBuyExhaustion13 and (buyExhaustionCount != buyExhaustionCount[1]) and (buyExhaustionCount == 13), 'Buy TE 13', shape.labelup, location.belowbar, color.new(color.new('#006400'), 25), 0, 'ᴛ', color.white, True, size.tiny, display=display__ren__)

    buyExhaustionHighest: Persistent[float] = 0.0
    buyExhaustionHigh: Persistent[float] = 0.0
    buyExhaustionLow: Persistent[float] = 0.0
    buyExhaustionLowest: Persistent[float] = 0.0
    buyExhaustionStopLevel: PersistentSeries[float] = 0.0
    buyExhaustionTargetLevel: PersistentSeries[float] = 0.0

    if buyExhaustionCount == 1:
        buyExhaustionLowest = priceLow
        buyExhaustionHighest = priceHigh

    if startBuyExhaustion13:
        buyExhaustionHighest = math.max(priceHigh, buyExhaustionHighest)
        buyExhaustionLowest = math.min(priceLow, buyExhaustionLowest)
        if priceHigh == buyExhaustionHighest:
            buyExhaustionLow = priceLow
        if priceLow == buyExhaustionLowest:
            buyExhaustionHigh = priceHigh

    buyExhaustionTargetPrice = 2 * buyExhaustionHighest - buyExhaustionLow
    buyExhaustionTargetLevel = buyExhaustionTargetPrice if buyExhaustionCount == 13 else 0.0 if priceClose > buyExhaustionTargetLevel[1] or (buyExhaustionStopLevel == 0 and sellExhaustionCount == 13) else buyExhaustionTargetLevel[1]
    plot(buyExhaustionTargetLevel if buyExhaustionTargetLevel > 0 else na, 'TE Buy Target', color.gray, 1, plot.style_circles, display=display.none)

    buyExhaustionStopPrice = 2 * buyExhaustionLowest - buyExhaustionHigh
    buyExhaustionStopLevel = buyExhaustionStopPrice if buyExhaustionCount == 13 else 0.0 if priceClose < buyExhaustionStopLevel[1] or (buyExhaustionTargetLevel == 0 and sellExhaustionCount == 13) else buyExhaustionStopLevel[1]
    plot(buyExhaustionStopLevel if stopLevels and buyExhaustionStopLevel > 0 else na, 'TE Buy Invalidation', color.blue, 1, plot.style_circles, display=display__ren__)

    startSellExhaustion13: PersistentSeries[bool] = False
    sellExhaustion13RefClose8: Persistent[float] = 0.0
    sellExhaustion13Condition = True if priceClose >= priceHigh[2] else False
    sellExhaustionBar13Fails = True if priceClose >= priceHigh[2] and priceHigh <= sellExhaustion13RefClose8 else False

    __block_result_6__ = na
    if sellCount == 9 and sellExhaustionCount == 0:
        __block_result_6__ = True
    else:
        __block_result_7__ = na
        if buyCount == 9 or sellExhaustionCount == 13 or priceClose < sellPhaseSupport:
            __block_result_7__ = False
        else:
            __block_result_7__ = startSellExhaustion13[1]
        __block_result_6__ = __block_result_7__
    startSellExhaustion13 = __block_result_6__

    sellExhaustionCount = ((1 if sellExhaustion13Condition else 0) if sellCount == 9 else sellExhaustionCount + 1 if sellExhaustion13Condition else sellExhaustionCount) if startSellExhaustion13 else 0
    sellExhaustionCount = sellExhaustionCount - 1 if sellExhaustionCount == 13 and sellExhaustionBar13Fails else sellExhaustionCount

    if sellExhaustionCount == 8 and sellExhaustionCount != sellExhaustionCount[1]:
        sellExhaustion13RefClose8 = priceClose

    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 1), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 2), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₂', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 3), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₃', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 4), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₄', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 5), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₅', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 6), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₆', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 7), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₇', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 8), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₈', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 9), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₉', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 10), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₀', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 11), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₁', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 12), 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₁₂', color.teal, False, display=display__ren__)
    plotshape(showNone and (not compltedPhases) and startSellExhaustion13 and (sellExhaustionCount == sellExhaustionCount[1]) and (sellExhaustionCount == 12) and sellExhaustionBar13Fails, 'Sell TE', shape.labeldown, location.belowbar, color.new('#00000000'), 0, '₊', color.teal, False, display=display__ren__)
    plotshape(showNone and startSellExhaustion13 and (sellExhaustionCount != sellExhaustionCount[1]) and (sellExhaustionCount == 13), 'Sell TE 13', shape.labeldown, location.abovebar, color.new(color.new('#910000'), 25), 0, 'ᴛ', color.white, True, size.tiny, display=display__ren__)

    sellExhaustionHighest: Persistent[float] = 0.0
    sellExhaustionHigh: Persistent[float] = 0.0
    sellExhaustionLow: Persistent[float] = 0.0
    sellExhaustionLowest: Persistent[float] = 0.0
    sellExhaustionStopLevel: PersistentSeries[float] = 0.0
    sellExhaustionTargetLevel: PersistentSeries[float] = 0.0

    if sellExhaustionCount == 1:
        sellExhaustionLowest = priceLow
        sellExhaustionHighest = priceHigh

    if startSellExhaustion13:
        sellExhaustionHighest = math.max(priceHigh, sellExhaustionHighest)
        sellExhaustionLowest = math.min(priceLow, sellExhaustionLowest)
        if priceHigh == sellExhaustionHighest:
            sellExhaustionLow = priceLow
        if priceLow == sellExhaustionLowest:
            sellExhaustionHigh = priceHigh

    sellExhaustionStopPrice = 2 * sellExhaustionHighest - sellExhaustionLow
    sellExhaustionStopLevel = sellExhaustionStopPrice if sellExhaustionCount == 13 else 0.0 if priceClose > sellExhaustionStopLevel[1] or (sellExhaustionTargetLevel == 0 and buyExhaustionCount == 13) else sellExhaustionStopLevel[1]
    plot(sellExhaustionStopLevel if stopLevels and sellExhaustionStopLevel > 0 else na, 'TE Sell Invalidation', color.blue, 1, plot.style_circles, display=display__ren__)

    sellExhaustionTargetPrice = 2 * sellExhaustionLowest - sellExhaustionHigh
    sellExhaustionTargetLevel = sellExhaustionTargetPrice if sellExhaustionCount == 13 else 0.0 if priceClose < sellExhaustionTargetLevel[1] or (sellExhaustionStopLevel == 0 and buyExhaustionCount == 13) else sellExhaustionTargetLevel[1]
    plot(sellExhaustionTargetLevel if sellExhaustionTargetLevel > 0 else na, 'TE Sell Target', color.gray, 1, plot.style_circles, display=display.none)

    O, H, L, C, O0, H0, L0, C0 = f_htf_ohlc(i_htf)

    time_x12 = ta.valuewhen(ta.change(time(i_htf)) != 0, time, 2)
    time_x11 = ta.valuewhen(ta.change(time(i_htf)) != 0, time, 1)
    time_x1 = ta.valuewhen(ta.change(time(i_htf)) != 0, time, 0)
    time_x2 = 2 * time_x1 - time_x11
    time_x20 = 3 * time_x1 - 2 * time_x11

    R1, P, S1 = f_get_pivot(O, H, L, C, O0)
    r1, p, s1 = f_get_pivot(O0, H0, L0, C0, O0)

    when = barstate.islast and i_isPivot
    f_processPivotLevelX(when, time_x1, S1, time_x2, color_s, 'Solid', 2, 'S', 'Range Pivot')
    f_processPivotLevelX(when, time_x1, R1, time_x2, color_r, 'Solid', 2, 'R', 'Range Pivot')
    f_processPivotLevelX(when, time_x1, P, time_x2, color.new('#2962FF'), 'Solid', 2, 'P', 'Range Pivot')

    when = barstate.islast and i_dispPVT
    f_processPivotLevelX(when, time_x2, s1, time_x20, color_s, 'Solid', 1, 'S', 'Developing Range Pivot')
    f_processPivotLevelX(when, time_x2, r1, time_x20, color_r, 'Solid', 1, 'R', 'Developing Range Pivot')
    f_processPivotLevelX(when, time_x2, p, time_x20, color.new('#2962FF'), 'Solid', 1, 'P', 'Developing Range Pivot')

    rColor = na if ta.change(time(i_htf)) != 0 else color_r
    pColor: Color = color.new('#2962FF')
    sColor = na if ta.change(time(i_htf)) != 0 else color_s

    plot(R1 if i_disphist and R1 > 0 else na, 'Historical R', rColor, 1, plot.style_linebr, editable=False, display=display__ren__)
    plot(P if i_disphist and P > 0 else na, 'Historical P', pColor, 1, plot.style_linebr, editable=False, display=display__ren__)
    plot(S1 if i_disphist and S1 > 0 else na, 'Historical S', sColor, 1, plot.style_linebr, editable=False, display=display__ren__)

    nzVolume: Series = nz(volume)

    buyPressure: float = 0.0
    sellPressure: float = 0.0
    priceDelta: float = 0.0
    priceRange: float = 0.0
    osc: Series[float] = 0.0
    dominance: float = 0.0

    if isPressureEnabled and nzVolume != 0:
        for i in pine_range(0, pressureLength - 1):
            priceDelta = priceClose[i] - priceOpen[i]
            priceRange = priceHigh[i] - priceLow[i]
            if priceRange > 0:
                if priceDelta > 0:
                    buyPressure += priceDelta / priceRange * nzVolume[i]
                if priceDelta < 0:
                    sellPressure += priceDelta / priceRange * nzVolume[i]
        dominance = buyPressure + math.abs(sellPressure)
        if dominance != 0.0:
            osc = 100 * (buyPressure / dominance)
        else:
            osc = 50

    sigLength: int = 9
    sigMaType: str = 'SMA'
    signal = ma(osc, sigLength, sigMaType)
    histogram: Series = osc - signal
    histColor: Series = (color.new('#26A69A') if histogram[1] < histogram else color.new('#B2DFDB')) if histogram >= 0 else color.new('#FFCDD2') if histogram[1] < histogram else color.new('#FF5252')

    a_lines: Persistent[list[Line]] = array.new_line()
    a_hist: Persistent[list[Box]] = array.new_box()
    a_fill: Persistent[list[LineFill]] = array.new_linefill()

    priceHighest = ta.highest(high, oscLookbackLength)
    priceLowest = ta.lowest(low, oscLookbackLength)
    priceChangeRate = (priceHighest - priceLowest) / priceHighest
    priceLowest = priceLowest if oscPlacement == 'Middle' else priceLowest * (1 - priceChangeRate * oscVerticalOffset)
    priceHighest = priceHighest if oscPlacement == 'Middle' else priceHighest * (1 + priceChangeRate * oscVerticalOffset)
    oscHighestRaw = ta.highest(osc, oscLookbackLength)
    oscLowestRaw = ta.lowest(osc, oscLookbackLength)
    oscHighest = oscHighestRaw
    oscLowest = oscLowestRaw - 1 if oscHighestRaw == oscLowestRaw else oscLowestRaw

    if barstate.islast and nzVolume != 0 and isPressureEnabled:
        if array.size(a_lines) > 0:
            aLinesSize: int = array.size(a_lines)
            for i in pine_range(1, aLinesSize):
                line.delete(array.shift(a_lines))
        if array.size(a_hist) > 0:
            aHistSize: int = array.size(a_hist)
            for i in pine_range(1, aHistSize):
                box.delete(array.shift(a_hist))
        if array.size(a_fill) > 0:
            aFillSize: int = array.size(a_fill)
            for i in pine_range(1, aFillSize):
                linefill.delete(array.shift(a_fill))

        hight = priceChangeRate / oscHight
        obLevel = priceLowest + (upperBand - oscLowest) * (priceHighest - priceLowest) / (oscHighest - oscLowest) if oscPlacement == 'Middle' else (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + upperBand / oscHighest * hight)
        osLevel = priceLowest + (lowerBand - oscLowest) * (priceHighest - priceLowest) / (oscHighest - oscLowest) if oscPlacement == 'Middle' else (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + lowerBand / oscHighest * hight)

        array.push(a_lines, line.new(bar_index[oscLookbackLength], obLevel, bar_index, obLevel, xloc.bar_index, extend.none, color.gray, line.style_dashed, 1))
        array.push(a_lines, line.new(bar_index[oscLookbackLength], osLevel, bar_index, osLevel, xloc.bar_index, extend.none, color.gray, line.style_dashed, 1))
        if oscPlacement != 'Middle':
            array.push(a_fill, linefill.new(array.get(a_lines, 0), array.get(a_lines, 1), fillColor))

        midLine: int = 50
        midLevel = priceLowest + (midLine - oscLowest) * (priceHighest - priceLowest) / (oscHighest - oscLowest) if oscPlacement == 'Middle' else (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + midLine / oscHighest * hight)
        array.push(a_lines, line.new(bar_index[oscLookbackLength], midLevel, bar_index, midLevel, xloc.bar_index, extend.none, color.new(color.gray, 50), line.style_dashed, 1))

        for barIndex in pine_range(0, oscLookbackLength - 1):
            if array.size(a_lines) < 496:
                array.push(a_hist, box.new(bar_index[barIndex], priceHighest if oscPlacement == 'Top' else priceLowest, bar_index[barIndex], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + histogram[barIndex] / oscHighest * hight), histColor[barIndex], 2, bgcolor=histColor[barIndex]))
                array.push(a_lines, line.new(bar_index[barIndex], priceLowest + (osc[barIndex] - oscLowest) * (priceHighest - priceLowest) / (oscHighest - oscLowest) if oscPlacement == 'Middle' else priceHighest * (1 + osc[barIndex] / oscHighest * hight) if oscPlacement == 'Top' else priceLowest * (1 + osc[barIndex] / oscHighest * hight), bar_index[barIndex + 1], priceLowest + (osc[barIndex + 1] - oscLowest) * (priceHighest - priceLowest) / (oscHighest - oscLowest) if oscPlacement == 'Middle' else priceHighest * (1 + osc[barIndex + 1] / oscHighest * hight) if oscPlacement == 'Top' else priceLowest * (1 + osc[barIndex + 1] / oscHighest * hight), xloc.bar_index, extend.none, oscColor, line.style_solid, 1))

    vSMA = ta.sma(nzVolume, __input_19__)
    barcolor(((color.new('#006400') if open < close else color.new('#910000')) if nzVolume > vSMA * upThesh else (color.new('#7FFFD4') if open < close else color.new('#FF9800')) if nzVolume < vSMA * __input_21__ else na) if vwcb and nzVolume != 0 else na, title='Volume-Weighted Bars', editable=False)

    dashboardPos = position.top_right if dashboardPosition == 'Top Right' else position.top_left if dashboardPosition == 'Top Left' else position.bottom_left
    dashboard: Persistent[Table] = table.new(dashboardPos, 2, 5, border_width=1, border_color=color.new(color.gray, 60))
    bgDashboard = color.new(color.black, 80)

    if showDashboard and barstate.islast:
        isBuyME: bool = buyCount > 0
        isSellME: bool = sellCount > 0

        momentumText = 'Buy-side ' + string.tostring(buyCount) + '/9' if isBuyME else 'Sell-side ' + string.tostring(sellCount) + '/9' if isSellME else '—'
        momentumColor = color.red if isBuyME else color.teal if isSellME else color.gray
        momentumTip = 'Buy-side Momentum Phase: Price is falling (Step ' + string.tostring(buyCount) + ' of 9 in progress) — a completed decline here is what the framework watches for a possible bullish reversal.' if isBuyME else 'Sell-side Momentum Phase: Price is rising (Step ' + string.tostring(sellCount) + ' of 9 in progress) — a completed rise here is what the framework watches for a possible bearish reversal.' if isSellME else 'No active Momentum Exhaustion phase'

        isBuyTE: bool = buyExhaustionCount > 0
        isSellTE: bool = sellExhaustionCount > 0
        terminalText = 'Buy-side ' + string.tostring(buyExhaustionCount) + '/13' if isBuyTE else 'Sell-side ' + string.tostring(sellExhaustionCount) + '/13' if isSellTE else '—'
        terminalColor = color.red if isBuyTE else color.teal if isSellTE else color.gray
        terminalTip = 'Buy-side Terminal Exhaustion: Price is falling (Step ' + string.tostring(buyExhaustionCount) + ' of 13 in progress) — a completed decline here is what the framework watches for a possible bullish reversal.' if isBuyTE else 'Sell-side Terminal Exhaustion: Price is rising (Step ' + string.tostring(sellExhaustionCount) + ' of 13 in progress) — a completed rise here is what the framework watches for a possible bearish reversal.' if isSellTE else 'No active Terminal Exhaustion phase'

        pivotValid = i_isPivot and R1 > 0 and (P > 0) and (S1 > 0)
        diffR = math.abs(priceClose - R1)
        diffP = math.abs(priceClose - P)
        diffS = math.abs(priceClose - S1)
        nearestIsR = diffR <= diffP and diffR <= diffS
        nearestIsP = not nearestIsR and diffP <= diffS
        nearestName = 'R' if nearestIsR else 'P' if nearestIsP else 'S'
        nearestVal = R1 if nearestIsR else P if nearestIsP else S1
        pctDist = (nearestVal - priceClose) / priceClose * 100 if pivotValid else na
        pivotText = nearestName + ' ' + ('+' if pctDist >= 0 else '') + string.tostring(pctDist, '#.##') + '%' if pivotValid else '—'
        pivotColor = color.gray if not pivotValid else color.teal if priceClose > R1 else color.red if priceClose < S1 else color.gray
        pivotTip = 'Percentage distance to nearest Range Pivot level (' + nearestName + ' at ' + string.tostring(nearestVal, format.mintick) + ')' if pivotValid else 'Range Pivots disabled or unavailable'

        pressureText = 'Off' if not isPressureEnabled else (string.tostring(math.round(osc)) + '% Bull' if osc >= 50 else string.tostring(math.round(100 - osc)) + '% Bear') if nzVolume != 0 else 'No data'
        pressureColor = color.gray if not isPressureEnabled else (color.teal if osc >= 50 else color.red) if nzVolume != 0 else color.gray
        pressureTip = 'Volume Pressure is disabled' if not isPressureEnabled else 'Volume Pressure Oscillator ratio (' + string.tostring(math.round(osc)) + '% buying / ' + string.tostring(math.round(100 - osc)) + '% selling)'

        table.merge_cells(dashboard, 0, 0, 1, 0)
        table.cell(dashboard, 0, 0, 'Dual-Phase Reversal', text_color=chart.fg_color, bgcolor=bgDashboard, tooltip='Dual-Phase Reversal Framework\nIntegrates Momentum and Terminal Exhaustion, higher-timeframe Range Pivots, and Volume Pressure analytics.')

        table.cell(dashboard, 0, 1, 'Momentum', text_color=chart.fg_color, text_halign=text.align_left, bgcolor=bgDashboard, tooltip='Momentum Exhaustion tracks the initial phase of directional overextension using a 4-bar close comparison. A new phase begins only after a Momentum Shift changes the direction of that relationship.')
        table.cell(dashboard, 1, 1, momentumText, text_color=momentumColor, text_halign=text.align_right, bgcolor=bgDashboard, tooltip=momentumTip)

        table.cell(dashboard, 0, 2, 'Terminal', text_color=chart.fg_color, text_halign=text.align_left, bgcolor=bgDashboard, tooltip='Terminal Exhaustion tracks the late-stage continuation of directional exhaustion. It begins after Momentum Exhaustion completes step 9 and progresses independently toward step 13.')
        table.cell(dashboard, 1, 2, terminalText, text_color=terminalColor, text_halign=text.align_right, bgcolor=bgDashboard, tooltip=terminalTip)

        table.cell(dashboard, 0, 3, 'Pivot', text_color=chart.fg_color, text_halign=text.align_left, bgcolor=bgDashboard, tooltip='Signed percentage distance to the nearest Range Pivot level. Positive values indicate the level is above price; negative values indicate it is below price.')
        table.cell(dashboard, 1, 3, pivotText, text_color=pivotColor, text_halign=text.align_right, bgcolor=bgDashboard, tooltip=pivotTip)

        table.cell(dashboard, 0, 4, 'Pressure', text_color=chart.fg_color, text_halign=text.align_left, bgcolor=bgDashboard, tooltip='Volume Pressure ratio based on directional price movement and traded volume. Higher values indicate greater relative buying pressure; lower values indicate greater relative selling pressure.')
        table.cell(dashboard, 1, 4, pressureText, text_color=pressureColor, text_halign=text.align_right, bgcolor=bgDashboard, tooltip=pressureTip)

    priceCloseTxt = string.tostring(priceClose, format.mintick)
    tickerTxt = syminfo.ticker

    if f_crossingLevelX(priceClose, buyPhaseResistance) and phaseSRLevels:
        alert(tickerTxt + ' crossing buy-side phase resistance level, price ' + string.tostring(buyPhaseResistance, format.mintick))

    buyPhaseStopCrossed = f_crossingLevelX(priceClose, buyPhaseStopLevel)
    sellPhaseStopCrossed = f_crossingLevelX(priceClose, sellPhaseStopLevel)
    if (buyPhaseStopCrossed or sellPhaseStopCrossed) and stopLevels:
        crossedPhaseStopLevel = buyPhaseStopLevel if buyPhaseStopCrossed else sellPhaseStopLevel
        alert(tickerTxt + ' crossing phase invalidation level, price ' + string.tostring(crossedPhaseStopLevel, format.mintick))

    if f_crossingLevelX(priceClose, sellPhaseSupport) and phaseSRLevels:
        alert(tickerTxt + ' crossing sell-side phase support level, price ' + string.tostring(sellPhaseSupport, format.mintick))

    buyExhaustionStopCrossed = f_crossingLevelX(priceClose, buyExhaustionStopLevel)
    sellExhaustionStopCrossed = f_crossingLevelX(priceClose, sellExhaustionStopLevel)
    if (buyExhaustionStopCrossed or sellExhaustionStopCrossed) and stopLevels:
        crossedExhaustionStopLevel = buyExhaustionStopLevel if buyExhaustionStopCrossed else sellExhaustionStopLevel
        alert(tickerTxt + ' crossing exhaustion invalidation level, price ' + string.tostring(crossedExhaustionStopLevel, format.mintick))

    if buyCount == 9 and compltedPhases:
        alert(tickerTxt + ' buy-side Momentum Exhaustion completed, price ' + priceCloseTxt)

    if sellCount == 9 and compltedPhases:
        alert(tickerTxt + ' sell-side Momentum Exhaustion completed, price ' + priceCloseTxt)

    if buyExhaustionCount == 13 and compltedPhases:
        alert(tickerTxt + ' buy-side Terminal Exhaustion completed, price ' + priceCloseTxt)

    if sellExhaustionCount == 13 and compltedPhases:
        alert(tickerTxt + ' sell-side Terminal Exhaustion completed, price ' + priceCloseTxt)

    if osc > upperBand and osc[1] < upperBand and isPressureEnabled:
        alert(tickerTxt + ' volume pressure crossing overbought zone, price ' + priceCloseTxt)

    if osc < lowerBand and osc[1] > lowerBand and isPressureEnabled:
        alert(tickerTxt + ' volume pressure crossing oversold zone, price ' + priceCloseTxt)

    if nzVolume > vSMA * upThesh and vwcb:
        alert(tickerTxt + ' high volume, price ' + priceCloseTxt)

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
