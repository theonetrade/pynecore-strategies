"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, high, hline, input,
    label, line, location, low, na, open, plot, plotshape, position, script, shape, size, string,
    ta, table
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series, Table


@udt
class BlockLevel:
    lvlLine: Line = na(Line)
    lvlLabel: Label = na(Label)
    topPrice: float = na(float)
    botPrice: float = na(float)
    isBull: bool = na(bool)


@script.indicator("RSI Core Levels Heatmap [BigBeluga]", overlay=False, max_lines_count=500)
def main(
    maxActiveLevels=input.int(5, title="Max Active Levels & Labels", minval=1, tooltip="Maximum number of active lines and labels allowed on the price chart simultaneously before old ones are removed on the last bar.", group="Core Settings"),
    rsiLength=input.int(14, title="RSI Length", minval=1, tooltip="RSI Line Length.", group="Core Settings"),
    sigLength=input.int(14, title="Signal Line Length", minval=1, tooltip="The smoothing period used to calculate the RSI Signal Line.", group="Core Settings"),
    sigColor=input.color(color.orange, title="Signal Line Color", tooltip="The color used to display the RSI Signal Line.", group="Core Settings"),
    bullBaseColor=input.color(color.rgb(4, 195, 112), title="Bullish Base Color", tooltip="The intense color used when RSI is heavily oversold.", group="Color Theme"),
    bearBaseColor=input.color(color.new('#FF0000'), title="Bearish Base Color", tooltip="The intense color used when RSI is heavily overbought.", group="Color Theme"),
    showMidZone=input.bool(True, title="Show Midline Squeeze Zone", tooltip="Toggle the visibility of the neutral compression gradient area around the 50 line.", group="Midline Settings"),
    midZoneColorInput=input.color(color.yellow, title="Midline Zone Color", tooltip="Choose the color for the neutral compression zone gradient.", group="Midline Settings"),
    showTable=input.bool(True, title="Show Dashboard Table", tooltip="Toggle the visibility of the closest levels dashboard.", group="Dashboard Settings"),
    tablePos=input.string("top_right", title="Table Position", options=("top_right", "bottom_right", "top_left", "bottom_left"), group="Dashboard Settings")
):
    rsiValue: Series = ta.rsi(close, rsiLength)
    sigline = ta.sma(rsiValue, sigLength)

    activeBlocks: Persistent[list[BlockLevel]] = array.new(0, NA(BlockLevel))

    def is_overlapping_existing_block(high_val, low_val):
        overlap: bool = False
        if array.size(activeBlocks) > 0:
            for i in pine_range(0, array.size(activeBlocks) - 1):
                item: BlockLevel = array.get(activeBlocks, i)

                if high_val <= item.topPrice and high_val >= item.botPrice or (low_val >= item.botPrice and low_val <= item.topPrice) or (high_val >= item.topPrice and low_val <= item.botPrice):
                    overlap = True
                    break
        return overlap

    bullBlock = ta.crossover(rsiValue, sigline) and rsiValue < 50
    bearBlock = ta.crossunder(rsiValue, sigline) and rsiValue > 50

    if barstate.isconfirmed:
        if bullBlock:
            for i in pine_range(0, 10):
                bear = close[i] < open[i]
                if bear:
                    box_top = open[i]
                    box_bot = low[i]

                    if not is_overlapping_existing_block(box_top, box_bot):
                        dynamicGreen: Color = color.from_gradient(rsiValue[i], 15.0, 50.0, bullBaseColor, color.new(bullBaseColor, 80))

                        new_line = line.new(x1=bar_index[i], y1=box_bot, x2=bar_index, y2=box_bot, color=dynamicGreen, width=2, force_overlay=True)
                        new_label = label.new(x=bar_index, y=box_bot, text='RSI: ' + string.tostring(rsiValue[i], '#.##'), color=color.new(color.black, 100), textcolor=dynamicGreen, style=label.style_label_left, force_overlay=True)

                        array.push(activeBlocks, BlockLevel(new_line, new_label, box_top, box_bot, True))
                    break

        if bearBlock:
            for i in pine_range(0, 10):
                bull = close[i] > open[i]
                if bull:
                    box_top = high[i]
                    box_bot = open[i]

                    if not is_overlapping_existing_block(box_top, box_bot):
                        dynamicRed: Color = color.from_gradient(rsiValue[i], 50.0, 85.0, color.new(bearBaseColor, 80), bearBaseColor)

                        new_line = line.new(x1=bar_index[i], y1=box_top, x2=bar_index, y2=box_top, color=dynamicRed, width=2, force_overlay=True)
                        new_label = label.new(x=bar_index, y=box_top, text='RSI: ' + string.tostring(rsiValue[i], '#.##'), color=color.new(color.black, 100), textcolor=dynamicRed, style=label.style_label_left, force_overlay=True)

                        array.push(activeBlocks, BlockLevel(new_line, new_label, box_top, box_bot, False))
                    break

    if array.size(activeBlocks) > 0:
        for i in pine_range(array.size(activeBlocks) - 1, 0):
            item: BlockLevel = array.get(activeBlocks, i)

            broken: bool = close < item.botPrice if item.isBull else close > item.topPrice

            if broken:
                label.delete(item.lvlLabel)
                line.set_style(item.lvlLine, line.style_dashed)
                line.set_color(item.lvlLine, color.gray)
                line.set_width(item.lvlLine, 1)
                array.remove(activeBlocks, i)
            else:
                line.set_x2(item.lvlLine, bar_index)
                label.set_x(item.lvlLabel, bar_index)

        if barstate.islast and array.size(activeBlocks) > maxActiveLevels:
            items_to_delete: int = array.size(activeBlocks) - maxActiveLevels
            for i in pine_range(0, items_to_delete - 1):
                old_item: BlockLevel = array.shift(activeBlocks)
                line.delete(old_item.lvlLine)
                label.delete(old_item.lvlLabel)

    closest_sup: float = na(float)
    closest_res: float = na(float)
    min_sup_dist: float = na(float)
    min_res_dist: float = na(float)

    if array.size(activeBlocks) > 0:
        for i in pine_range(0, array.size(activeBlocks) - 1):
            item: BlockLevel = array.get(activeBlocks, i)
            if item.isBull:
                dist: float = close - item.botPrice
                if dist >= 0 and (na(min_sup_dist) or dist < min_sup_dist):
                    min_sup_dist = dist
                    closest_sup = item.botPrice
            else:
                dist: float = item.topPrice - close
                if dist >= 0 and (na(min_res_dist) or dist < min_res_dist):
                    min_res_dist = dist
                    closest_res = item.topPrice

    rsiColor = color.from_gradient(rsiValue, 30.0, 70.0, bullBaseColor, bearBaseColor)
    plot(rsiValue, color=rsiColor, title='RSI (Gradiented)', linewidth=2)
    plot(sigline, color=sigColor, title='Signal')
    hline(50, 'Middle Line', color=color.gray, linestyle=hline.style_dashed)

    isOverbought: bool = rsiValue >= 70.0
    isOversold: bool = rsiValue <= 30.0
    isSqueeze: bool = showMidZone and rsiValue >= 40.0 and (rsiValue <= 60.0)

    shapeColorOB: Color = color.from_gradient(rsiValue, 70.0, 100.0, color.new(bearBaseColor, 90), color.new(bearBaseColor, 0))
    shapeColorOS: Color = color.from_gradient(rsiValue, 0.0, 30.0, color.new(bullBaseColor, 0), color.new(bullBaseColor, 90))
    shapeColorSq1: Color = color.from_gradient(rsiValue, 45.0, 50.0, color.new(midZoneColorInput, 100), color.new(midZoneColorInput, 0))
    shapeColorSq2: Color = color.from_gradient(rsiValue, 50.0, 55.0, color.new(midZoneColorInput, 0), color.new(midZoneColorInput, 100))

    plotshape(95 if isOverbought else na, title='Overbought Track', style=shape.square, location=location.absolute, color=shapeColorOB, size=size.tiny)
    plotshape(50 if isSqueeze else na, title='Midline Squeeze Track', style=shape.square, location=location.absolute, color=shapeColorSq1 if rsiValue < 50 else shapeColorSq2, size=size.tiny)
    plotshape(5 if isOversold else na, title='Oversold Track', style=shape.square, location=location.absolute, color=shapeColorOS, size=size.tiny)

    plotshape(isOverbought, title='Main Chart Overbought', style=shape.square, location=location.abovebar, color=shapeColorOB, size=size.tiny, force_overlay=True)
    plotshape(isOversold, title='Main Chart Oversold', style=shape.square, location=location.belowbar, color=shapeColorOS, size=size.tiny, force_overlay=True)

    d_table: Persistent[Table] = na(Table)
    t_pos = position.top_right if tablePos == 'top_right' else position.bottom_right if tablePos == 'bottom_right' else position.top_left if tablePos == 'top_left' else position.bottom_left

    if showTable and barstate.islast:
        d_table = table.new(position=t_pos, columns=3, rows=4, bgcolor=color.new(color.black, 30), border_width=1, border_color=chart.bg_color)

        table.cell(d_table, 0, 0, 'Level Type', text_color=color.white, text_size=size.normal, bgcolor=color.new('#4F5569'))
        table.cell(d_table, 1, 0, 'Price Value', text_color=color.white, text_size=size.normal, bgcolor=color.new('#4F5569'))
        table.cell(d_table, 2, 0, 'Distance (Points / %)', text_color=color.white, text_size=size.normal, bgcolor=color.new('#4F5569'))

        table.cell(d_table, 0, 1, 'Current Close', text_color=color.white, text_size=size.normal)
        table.cell(d_table, 1, 1, string.tostring(close, '#.##'), text_color=color.white, text_size=size.normal)
        table.cell(d_table, 2, 1, 'Pivot Center', text_color=color.white, text_size=size.normal)

        if not na(closest_res):
            res_dist_points: float = closest_res - close
            res_dist_per: float = res_dist_points / close * 100
            table.cell(d_table, 0, 2, 'Nearest Resistance', text_color=bearBaseColor, text_size=size.normal)
            table.cell(d_table, 1, 2, string.tostring(closest_res, '#.##'), text_color=color.white, text_size=size.normal)
            table.cell(d_table, 2, 2, string.tostring(res_dist_points, '#.##') + ' (' + string.tostring(res_dist_per, '#.##') + '%)', text_color=bearBaseColor, text_size=size.normal)
        else:
            table.cell(d_table, 0, 2, 'Nearest Resistance', text_color=bearBaseColor, text_size=size.normal)
            table.cell(d_table, 1, 2, 'None Active', text_color=color.white, text_size=size.normal)
            table.cell(d_table, 2, 2, '-', text_color=bearBaseColor, text_size=size.normal)

        if not na(closest_sup):
            sup_dist_points: float = close - closest_sup
            sup_dist_per: float = sup_dist_points / close * 100
            table.cell(d_table, 0, 3, 'Nearest Support', text_color=bullBaseColor, text_size=size.normal)
            table.cell(d_table, 1, 3, string.tostring(closest_sup, '#.##'), text_color=color.white, text_size=size.normal)
            table.cell(d_table, 2, 3, string.tostring(sup_dist_points, '#.##') + ' (' + string.tostring(sup_dist_per, '#.##') + '%)', text_color=bullBaseColor, text_size=size.normal)
        else:
            table.cell(d_table, 0, 3, 'Nearest Support', text_color=bullBaseColor, text_size=size.normal)
            table.cell(d_table, 1, 3, 'None Active', text_color=color.white, text_size=size.normal)
            table.cell(d_table, 2, 3, '-', text_color=bullBaseColor, text_size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
