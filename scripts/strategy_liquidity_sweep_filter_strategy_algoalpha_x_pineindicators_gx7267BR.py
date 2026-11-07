"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    format, high, input, label, line, location, low, math, na, nz, plot, plotchar, plotshape,
    script, shape, size, strategy, string, ta, table, volume, xloc, yloc
)
from pynecore.types import Box, Color, Line, Persistent, Series, Table


@script.strategy("Liquidity Sweep Filter Strategy [AlgoAlpha X PineIndicators]", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, max_boxes_count=500, max_labels_count=500, max_lines_count=500, commission_value=0.05, process_orders_on_close=True, margin_long=20, margin_short=20, slippage=2)
def main(
    tradeMode=input.string(title="Trade Mode", defval="Long Only", options=("Long & Short", "Long Only", "Short Only"), group="Strategy Settings"),
    len=input.int(12, "Length", minval=1, tooltip="The number of periods used for trend calculations. A longer length creates a smoother and longer term signal", group="Trend Settings"),
    mult=input.float(2.0, "Multiplier", minval=0.1, step=0.1, tooltip="Multiplier for the standard deviation calculation. Higher values create wider bands and makes the indicator more resistant to noise", group="Trend Settings"),
    src: Series[float] = input.source(close, "Source", tooltip="The price data used for calculations. Close is most common, but you can also use open, high, low, hl2 (high+low)/2, hlc3 (high+low+close)/3, or ohlc4 (open+high+low+close)/4", group="Trend Settings"),
    major_sweep_thresh=input.float(50, "Major Sweep Threshold", minval=0, tooltip="Threshold value that determines what constitutes a major liquidation sweep. Higher values mean only larger price movements will be considered major sweeps. Can only be 0-100, larger values will make it harder for sweeps to be considered 'major'", group="Trend Settings"),
    shw_mjr=input.bool(True, "Show Major Liquidations", tooltip="Toggle the display of major liquidation levels. These represent significant price levels where large position liquidations occurred", group="Trend Settings"),
    shw_mnr=input.bool(True, "Show Minor Liquidations", tooltip="Toggle the display of minor liquidation levels. These represent smaller price levels where position liquidations occurred", group="Trend Settings"),
    show_profile=input.bool(True, "Show Volume Profile", tooltip="Toggle the display of the volume profile visualization. When enabled, shows the distribution of trading volume across price levels", group="Profile Settings"),
    show_bounds=input.bool(True, "Show Bounding Box", tooltip="Toggle the display of the bounding box around the volume profile. Helps to clearly define the profile's boundaries", group="Profile Settings"),
    res=input.int(40, "Resolution", minval=1, tooltip="Number of bars in the volume profile. Higher values create more detailed profiles but may increase visual noise. Each bar represents a price range where volume occurred", group="Profile Settings"),
    scale__ren__=input.int(30, "Scale", minval=1, tooltip="Controls the horizontal width of the volume profile display. Higher values make the profile wider and more visible, while lower values make it more compact", group="Profile Settings"),
    dismiss=input.bool(False, "Dismiss No Volume Warning", tooltip="Dismisses a warning that pops up when there is no volume data for the ticker", group="Appearance Settings"),
    bullColor=input.color(color.new('#00FFBB'), "Bullish Color", tooltip="Color used for bullish trends and indicators. This color appears when price action or indicators suggest upward momentum", group="Appearance Settings"),
    bearColor=input.color(color.new('#FF1100'), "Bearish Color", tooltip="Color used for bearish trends and indicators. This color appears when price action or indicators suggest downward momentum", group="Appearance Settings"),
    pc1=input.color(color.gray, "Profile Color", tooltip="Color of the volume profile visualization. This shows the distribution of trading volume across different price levels", group="Appearance Settings")
):
    def profileCalculation(start_index, end_index, res, scale__ren__):
        top_boundaries: list[float] = array.new_float(res)
        bottom_boundaries: list[float] = array.new_float(res)
        binlen: list[float] = array.new_float(res)
        highs: list[float] = array.new_float()
        lows: list[float] = array.new_float()
        volumes: list[float] = array.new_float()

        for i in pine_range(bar_index - start_index, bar_index - end_index):
            array.push(highs, high[i])
            array.push(lows, low[i])
            array.push(volumes, volume[i])

        maxx = array.max(highs)
        minn = array.min(lows)
        size__ren__ = array.size(highs)
        poc: float = 0.0

        if size__ren__ > 0:
            step = (maxx - minn) / res
            granularity = res
            for i in pine_range(0, granularity - 1):
                bin_size: float = 0.0
                bottom = minn + i * step
                top = minn + (i + 1) * step
                array.insert(bottom_boundaries, i, bottom)
                array.insert(top_boundaries, i, top)
                for j in pine_range(0, array.size(highs) - 1):
                    candle_above_hbar = array.get(lows, j) > top
                    candle_below_hbar = array.get(highs, j) < bottom
                    is_candle_in_bucket = not (candle_above_hbar or candle_below_hbar)
                    bin_size += array.get(volumes, j) if is_candle_in_bucket else 0
                array.insert(binlen, i, bin_size)
            boc = array.max(binlen)
            boci = array.indexof(binlen, boc) if array.indexof(binlen, boc) > 0 else 0
            poc = math.avg(array.get(top_boundaries, boci), array.get(bottom_boundaries, boci))
        return (top_boundaries, bottom_boundaries, binlen, poc)

    cumVol: Persistent[float] = 0.0
    cumVol += nz(volume)
    if barstate.islast and cumVol == 0 and (not dismiss):
        WHITE: Color = color.new(color.white, 20)
        BLUE: Color = color.new(color.new('#747474'), 50)
        ST_1: str = "⚠️This ticker does not have volume data, please try another ticker or\n open settings to dismiss this warning"
        textInput1: str = ST_1
        infoBoxSizeInput: str = "huge"
        infoBoxYPosInput: str = "middle"
        infoBoxXPosInput: str = "center"
        heightInput: int = 12
        widthInput: int = 80
        textColorInput: Color = WHITE
        bgColorInput: Color = BLUE
        watermark: Persistent[Table] = table.new(infoBoxYPosInput + '_' + infoBoxXPosInput, 1, 1)
        txt: str = textInput1
        table.cell(watermark, 0, 0, txt, widthInput, heightInput, textColorInput, text_size=infoBoxSizeInput, bgcolor=bgColorInput)

    basis = ta.sma(ta.ema(src, len), len)
    deviation = ta.ema(math.abs(close - basis), len * 3) * mult
    upper = basis + deviation
    lower = basis - deviation

    length = cast_int(len * mult)
    nvol: Series = (volume - ta.lowest(volume, length)) / (ta.highest(volume, length) - ta.lowest(volume, length)) * 100

    trend: Persistent[float] = 0.0
    if close > upper:
        trend = 1
    if close < lower:
        trend = -1

    peakform = high[1] > high and high[2] < high[1]
    valleyform = low[1] < low and low[2] > low[1]

    aPeakLines: Persistent[list[Line]] = array.new_line()
    aValleyLines: Persistent[list[Line]] = array.new_line()
    aPeakVols: Persistent[list[float]] = array.new_float()
    aValleyVols: Persistent[list[float]] = array.new_float()
    aPeakNVols: Persistent[list[float]] = array.new_float()
    aValleyNVols: Persistent[list[float]] = array.new_float()

    if trend < 0:
        if peakform and high[1] < upper:
            l = line.new(bar_index - 1, high[1], bar_index, high[1], color=color.new(bearColor, 100 - nvol[1]), width=2)
            array.push(aPeakLines, l)
            array.push(aPeakVols, volume[1])
            array.push(aPeakNVols, nvol[1])
    elif trend > 0 and low[1] > lower:
        if valleyform:
            l = line.new(bar_index - 1, low[1], bar_index, low[1], color=color.new(bullColor, 100 - nvol[1]), width=2)
            array.push(aValleyLines, l)
            array.push(aValleyVols, volume[1])
            array.push(aValleyNVols, nvol[1])

    bullliq: float = 0.0
    bearliq: float = 0.0
    Nbullliq: float = 0.0
    Nbearliq: float = 0.0

    if array.size(aPeakLines) > 0:
        qt = array.size(aPeakLines)
        for ln in pine_range(qt - 1, 0):
            if ln < array.size(aPeakLines):
                currentLine = array.get(aPeakLines, ln)
                lineLevel = method_call('get_y1', currentLine)
                if high > lineLevel or upper < lineLevel:
                    if high > lineLevel:
                        bearliq += array.get(aPeakVols, ln)
                        Nbearliq += array.get(aPeakNVols, ln)
                    array.remove(aPeakLines, ln)
                    array.remove(aPeakVols, ln)
                    array.remove(aPeakNVols, ln)
                else:
                    method_call('set_x2', currentLine, bar_index)
        if array.size(aPeakLines) > 500:
            method_call('delete', array.shift(aPeakLines))
            array.shift(aPeakVols)
            array.shift(aPeakNVols)

    if array.size(aValleyLines) > 0:
        qt = array.size(aValleyLines)
        for ln in pine_range(qt - 1, 0):
            if ln < array.size(aValleyLines):
                currentLine = array.get(aValleyLines, ln)
                lineLevel = method_call('get_y1', currentLine)
                if low < lineLevel or lower > lineLevel:
                    if low < lineLevel:
                        bullliq += array.get(aValleyVols, ln)
                        Nbullliq += array.get(aValleyNVols, ln)
                    array.remove(aValleyLines, ln)
                    array.remove(aValleyVols, ln)
                    array.remove(aValleyNVols, ln)
                else:
                    method_call('set_x2', currentLine, bar_index)
        if array.size(aValleyLines) > 500:
            method_call('delete', array.shift(aValleyLines))
            array.shift(aValleyVols)
            array.shift(aValleyNVols)

    if bullliq > 0:
        if Nbullliq < major_sweep_thresh and shw_mnr:
            label.new(bar_index, lower, string.tostring(bullliq, format.volume), xloc.bar_index, yloc.price, color.new(bullColor, 70), label.style_label_up, size=size.tiny)
        elif Nbullliq > major_sweep_thresh and shw_mjr:
            label.new(bar_index, lower, string.tostring(bullliq, format.volume), xloc.bar_index, yloc.price, color.new(bullColor, 70), label.style_label_up, size=size.tiny)

    if bearliq > 0:
        if Nbearliq < major_sweep_thresh and shw_mnr:
            label.new(bar_index, upper, string.tostring(bearliq, format.volume), xloc.bar_index, yloc.price, color.new(bearColor, 70), label.style_label_down, size=size.tiny)
        elif Nbearliq > major_sweep_thresh and shw_mjr:
            label.new(bar_index, upper, string.tostring(bearliq, format.volume), xloc.bar_index, yloc.price, color.new(bearColor, 70), label.style_label_down, size=size.tiny)

    volatility = ta.atr(14) / 2

    timer = ta.barssince(ta.cross(trend, 0))

    profile_upper = ta.highest(math.max(1, nz(timer)))
    profile_lower = ta.lowest(math.max(1, nz(timer)))

    end_index = bar_index
    start_index = bar_index - timer + (1 if end_index > bar_index - timer else 0)

    top_boundaries, bottom_boundaries, binlen, poc = profileCalculation(start_index, end_index, res, scale__ren__)

    boxes: Persistent[list[Box]] = array.new_box()
    br: Persistent[list[Box]] = array.new_box()

    while array.size(boxes) > 0:
        method_call('delete', array.shift(boxes))

    while array.size(br) > 0:
        method_call('delete', array.shift(br))

    for i in pine_range(0, res - 1):
        if show_profile and (not (barstate.islast and cumVol == 0)):
            box_right = bar_index + 7 + scale__ren__
            box_left = box_right - math.round(method_call('get', binlen, i)) / math.round(method_call('max', binlen)) * scale__ren__
            box_top = array.get(top_boundaries, i)
            box_bottom = array.get(bottom_boundaries, i)
            gradient_color = color.from_gradient(math.sin(method_call('get', binlen, i) * math.pi / method_call('max', binlen)) * method_call('max', binlen), 0, method_call('max', binlen), bullColor if trend > 0 else bearColor, pc1)
            array.push(boxes, box.new(box_left, box_top, box_right, box_bottom, border_style=line.style_solid, border_color=gradient_color, border_width=1, bgcolor=color.new(gradient_color, 10)))

    if show_bounds and (not (barstate.islast and cumVol == 0)):
        array.push(br, box.new(start_index, profile_upper, end_index + scale__ren__ + 7, profile_lower, border_style=line.style_solid, border_color=color.new(chart.fg_color, 90), border_width=1, bgcolor=color.new(chart.fg_color, 95)))

    plot(upper if trend < 0 else na, color=color.new(bearColor, 30), style=plot.style_linebr, title='Downtrend Line', linewidth=3)
    plot(lower if trend > 0 else na, color=color.new(bullColor, 30), style=plot.style_linebr, title='Uptrend Line', linewidth=3)

    plotchar(low - volatility if bullliq != 0 and Nbullliq > major_sweep_thresh else na, 'Strong Bullish Sweep', '▲', location.absolute, bullColor, size=size.tiny)
    plotchar(high + volatility if bearliq != 0 and Nbearliq > major_sweep_thresh else na, 'Strong Bearish Sweep', '▼', location.absolute, bearColor, size=size.tiny)
    plotchar(low - volatility if bullliq != 0 and Nbullliq > 0 else na, 'Bullish Sweep', '△', location.absolute, bullColor)
    plotchar(high + volatility if bearliq != 0 and Nbearliq > 0 else na, 'Bearish Sweep', '▽', location.absolute, bearColor)

    plotshape(lower if ta.crossover(trend, 0) else na, 'Bullish Trend', shape.labelup, location.absolute, color.new(bullColor, 50), text='▲', textcolor=chart.fg_color, size=size.small)
    plotshape(upper if ta.crossunder(trend, 0) else na, 'Bearish Trend', shape.labeldown, location.absolute, color.new(bearColor, 50), text='▼', textcolor=chart.fg_color, size=size.small)

    alertcondition(ta.crossover(trend, 0), title='Bullish Trend', message='Bullish Trend')
    alertcondition(ta.crossunder(trend, 0), title='Bearish Trend', message='Bearish Trend')
    alertcondition(bullliq != 0 and Nbullliq > major_sweep_thresh, title='Strong Bullish Sweep', message='Strong Bullish Sweep')
    alertcondition(bearliq != 0 and Nbearliq > major_sweep_thresh, title='Strong Bearish Sweep', message='Strong Bearish Sweep')
    alertcondition(bullliq != 0 and Nbullliq > 0, title='Bullish Sweep', message='Bullish Sweep')
    alertcondition(bearliq != 0 and Nbearliq > 0, title='Bearish Sweep', message='Bearish Sweep')

    bullishTrend = ta.crossover(trend, 0)
    bearishTrend = ta.crossunder(trend, 0)

    if bullishTrend:
        if tradeMode == 'Long & Short' or tradeMode == 'Long Only':
            if strategy.position_size < 0:
                strategy.close('Short', comment='Close Short on Bullish Trend')
            if strategy.position_size <= 0:
                strategy.entry('Long', strategy.long, comment='Enter Long on Bullish Trend')
        if tradeMode == 'Short Only':
            if strategy.position_size < 0:
                strategy.close('Short', comment='Close Short on Bullish Trend')

    if bearishTrend:
        if tradeMode == 'Long & Short' or tradeMode == 'Short Only':
            if strategy.position_size > 0:
                strategy.close('Long', comment='Close Long on Bearish Trend')
            if strategy.position_size >= 0:
                strategy.entry('Short', strategy.short, comment='Enter Short on Bearish Trend')
        if tradeMode == 'Long Only':
            if strategy.position_size > 0:
                strategy.close('Long', comment='Close Long on Bearish Trend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
