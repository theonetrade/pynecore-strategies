"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, format, high, input, low, math, na, plot, position, script,
    string, ta, table
)
from pynecore.types import Persistent, Series


@script.indicator('ATR Bands', overlay=True)
def main(
    atrPeriod=input.int(title='ATR Period', defval=3, minval=1, group='ATR Bands Standard Settings', tooltip='This setting is used in the raw ATR value calculation.  Lower values will be more reactive to recent price movement, while higher values will better indicate loger-term trend.\n\n' + 'Most often this is set at either 14 or 21.\nDefault: 3'),
    atrMultiplier=input.float(title='ATR Band Scale Factor', defval=2.5, step=0.1, minval=0.01, group='ATR Bands Standard Settings', tooltip='Scaling factor (aka multiplier) for the ATR to use for plotting the ATR bands.  ' + 'This will usually be between 1 and 3.\n\nDefault: 2.5'),
    showTPBands=input.bool(title='Show opposite bands for take-profit zones', defval=False, tooltip="If enalbled, the existing ATR bands will be treated as 'stop-loss' bands, and 'take-profit' bands will be plotted " + "to depict potential take-profit targets that are scaled based on the 'stop-loss' band and an additional reward/risk scaling factor (see below).\n\nDefault: Unchecked", group='Take-Profit Settings'),
    tpScaleFactor=input.float(title='Take-Profit Scale Factor', defval=1.5, minval=1, step=0.1, tooltip="This is a secondary scaling factor used based on the 'stop-loss' ATR bands to calculate and plot a potential take-profit target.\n\n" + 'The easiest way to think of this is as a desired reward/risk ratio, where the primary ATR Bands represent the risk/stop-loss.\n\nDefault: 1.5'),
    showTable=input.bool(title='Show Table for Stops and Targets', defval=False, group='Table Settings', tooltip='If enabled, a table will be placed on-chart showing exact values for both stop bands, as well as optional take-profit bands/targets.\n\n' + "Note: Take-profit values are based on the 'Take-Profit Scale Factor' setting above.\n\nDefault: Unchecked"),
    allowTableRepainting=input.bool(title='Allow Table Repainting', defval=False, group='Table Settings', tooltip='If enabled, table data will show real-time values, which will inherently repaint.  This may be desirable for people preparing to enter prior ' + 'to candle close, but should be used with extreme caution.\n\nDefault: Unchecked'),
    showTPinTable=input.bool(title='Include additional rows/columns to display take-profit values.', defval=False, group='Table Settings', tooltip='If enabled, additional table rows/columns will be drawn and populated with take-profit band/target values.\n\n' + "Note: Take-profit values are based on the 'Take-Profit Scale Factor' setting above.\n\nDefault: Unchecked"),
    alignTableVertically=input.bool(title='Align Table Vertically', defval=True, group='Table Settings', tooltip='If enabled, the table will be re-aligned to display vertically (headers to the left) instead of horizontally (headers on top).\n\nDefault: Checked'),
    tablePosition=input.string(title='Table Location', defval='Bottom Right', options=('Top Right', 'Top Left', 'Top Center', 'Middle Right', 'Middle Left', 'Middle Center', 'Bottom Right', 'Bottom Left', 'Bottom Center'), group='Table Settings', tooltip='This setting controls the position on the chart where the table will be located.\n\nDefault: Bottom Right'),
    tableColor=input.color(title='Table Color: ', defval=color.rgb(0, 175, 200, 20), group='Table Settings', inline='A'),
    tableTextHeaderColor=input.color(title='Table Header Color: ', defval=color.rgb(255, 255, 0, 0), group='Table Settings', tooltip='These settings determine the colors used for the table cell borders/outlines, and the text inside the table cells used as data headers.', inline='A'),
    tableTextColor=input.color(title='Table Text Color: ', defval=color.rgb(255, 255, 255, 0), group='Table Settings', tooltip='This setting determines the color used for the text inside the table cells.', inline='B'),
    tableLongBGColor=input.color(title='Table Background Color - Long: ', defval=color.rgb(0, 255, 0, 90), group='Table Settings', inline='C'),
    tableShortBGColor=input.color(title='Short: ', defval=color.rgb(255, 0, 0, 80), group='Table Settings', tooltip='These settings determine the background fill colors used for long/short position info.', inline='C')
):
    atrSourceRef: str = 'close'
    def getBandOffsetSource(srcIn, isUpperBand):
        ret = close
        __switch__ = srcIn
        if __switch__ == 'close':
            ret = close
        elif __switch__ == 'wicks':
            ret = high if isUpperBand else low
        else:
            ret = close
        return ret

    def getTablePosition(posIn):
        posOut = position.bottom_right
        __switch__ = posIn
        if __switch__ == 'Top Right':
            posOut = position.top_right
        elif __switch__ == 'Top Left':
            posOut = position.top_left
        elif __switch__ == 'Top Center':
            posOut = position.top_center
        elif __switch__ == 'Middle Right':
            posOut = position.middle_right
        elif __switch__ == 'Middle Left':
            posOut = position.middle_left
        elif __switch__ == 'Middle Center':
            posOut = position.middle_center
        elif __switch__ == 'Bottom Right':
            posOut = position.bottom_right
        elif __switch__ == 'Bottom Left':
            posOut = position.bottom_left
        elif __switch__ == 'Bottom Center':
            posOut = position.bottom_center
        else:
            posOut = position.bottom_right
        return posOut

    atr = ta.atr(atrPeriod)
    scaledATR: Series = atr * atrMultiplier
    upperATRBand: Series = getBandOffsetSource(atrSourceRef, True) + scaledATR
    lowerATRBand: Series = getBandOffsetSource(atrSourceRef, False) - scaledATR
    scaledTPLong: Series = close + (close - lowerATRBand) * tpScaleFactor
    scaledTPShort: Series = close - (upperATRBand - close) * tpScaleFactor
    plot(upperATRBand, title='Upper ATR Band', color=color.rgb(0, 255, 0, 50), linewidth=2)
    plot(lowerATRBand, title='Lower ATR Band', color=color.rgb(255, 0, 0, 50), linewidth=2)
    plot(scaledTPLong if showTPBands else na, title='Upper Take-Profit Band', color=color.rgb(255, 255, 255, 80), linewidth=1)
    plot(scaledTPShort if showTPBands else na, title='Lower Take-Profit Band', color=color.rgb(255, 255, 0, 80), linewidth=1)
    if showTable:
        atrTable: Persistent = table.new(position=getTablePosition(tablePosition), columns=8, rows=8)
        table.set_border_width(atrTable, 1)
        table.set_frame_width(atrTable, 1)
        table.set_border_color(atrTable, tableColor)
        table.set_frame_color(atrTable, tableColor)
        if alignTableVertically:
            table.cell(atrTable, 0, 0, text='Long ATR Stop', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor, tooltip='Test')
            table.cell(atrTable, 0, 1, text='Long ATR Stop Dist', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
            if showTPinTable:
                table.cell(atrTable, 0, 2, text='Long ATR TP', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 0, 3, text='Long ATR TP Dist', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
            table.cell(atrTable, 0, 4, text='Short ATR Stop', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            table.cell(atrTable, 0, 5, text='Short ATR Stop Dist', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            if showTPinTable:
                table.cell(atrTable, 0, 6, text='Short ATR TP', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 0, 7, text='Short ATR TP Dist', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            table.cell(atrTable, 1, 0, text=string.tostring(lowerATRBand if allowTableRepainting else lowerATRBand[1], format.mintick), text_color=tableTextColor, bgcolor=tableLongBGColor, tooltip='Test')
            table.cell(atrTable, 1, 1, text=string.tostring(math.round_to_mintick(close - lowerATRBand if allowTableRepainting else close[1] - lowerATRBand[1])), text_color=tableTextColor, bgcolor=tableLongBGColor)
            if showTPinTable:
                table.cell(atrTable, 1, 2, text=string.tostring(scaledTPLong if allowTableRepainting else scaledTPLong[1], format.mintick), text_color=tableTextColor, bgcolor=tableLongBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 1, 3, text=string.tostring(math.round_to_mintick(scaledATR * tpScaleFactor if allowTableRepainting else scaledATR[1] * tpScaleFactor)), text_color=tableTextColor, bgcolor=tableLongBGColor)
            table.cell(atrTable, 1, 4, text=string.tostring(upperATRBand if allowTableRepainting else upperATRBand[1], format.mintick), text_color=tableTextColor, bgcolor=tableShortBGColor, tooltip='Test 2')
            table.cell(atrTable, 1, 5, text=string.tostring(math.round_to_mintick(upperATRBand - close if allowTableRepainting else upperATRBand[1] - close[1])), text_color=tableTextColor, bgcolor=tableShortBGColor)
            if showTPinTable:
                table.cell(atrTable, 1, 6, text=string.tostring(scaledTPShort if allowTableRepainting else scaledTPShort[1], format.mintick), text_color=tableTextColor, bgcolor=tableShortBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 1, 7, text=string.tostring(math.round_to_mintick(scaledATR * tpScaleFactor if allowTableRepainting else scaledATR[1] * tpScaleFactor)), text_color=tableTextColor, bgcolor=tableShortBGColor)
        else:
            table.cell(atrTable, 0, 0, text='Long ATR Stop', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor, tooltip='Test')
            table.cell(atrTable, 1, 0, text='Long ATR Stop Dist', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
            if showTPinTable:
                table.cell(atrTable, 2, 0, text='Long ATR TP', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 3, 0, text='Long ATR TP Dist', text_color=tableTextHeaderColor, bgcolor=tableLongBGColor)
            table.cell(atrTable, 4, 0, text='Short ATR Stop', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            table.cell(atrTable, 5, 0, text='Short ATR Stop Dist', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            if showTPinTable:
                table.cell(atrTable, 6, 0, text='Short ATR TP', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 7, 0, text='Short ATR TP Dist', text_color=tableTextHeaderColor, bgcolor=tableShortBGColor)
            table.cell(atrTable, 0, 1, text=string.tostring(lowerATRBand if allowTableRepainting else lowerATRBand[1], format.mintick), text_color=tableTextColor, bgcolor=tableLongBGColor, tooltip='Test')
            table.cell(atrTable, 1, 1, text=string.tostring(math.round_to_mintick(close - lowerATRBand if allowTableRepainting else close[1] - lowerATRBand[1])), text_color=tableTextColor, bgcolor=tableLongBGColor)
            if showTPinTable:
                table.cell(atrTable, 2, 1, text=string.tostring(scaledTPLong if allowTableRepainting else scaledTPLong[1], format.mintick), text_color=tableTextColor, bgcolor=tableLongBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 3, 1, text=string.tostring(math.round_to_mintick(scaledATR * tpScaleFactor if allowTableRepainting else scaledATR[1] * tpScaleFactor)), text_color=tableTextColor, bgcolor=tableLongBGColor)
            table.cell(atrTable, 4, 1, text=string.tostring(upperATRBand if allowTableRepainting else upperATRBand[1], format.mintick), text_color=tableTextColor, bgcolor=tableShortBGColor, tooltip='Test 2')
            table.cell(atrTable, 5, 1, text=string.tostring(math.round_to_mintick(upperATRBand - close if allowTableRepainting else upperATRBand[1] - close[1])), text_color=tableTextColor, bgcolor=tableShortBGColor)
            if showTPinTable:
                table.cell(atrTable, 6, 1, text=string.tostring(scaledTPShort if allowTableRepainting else scaledTPShort[1], format.mintick), text_color=tableTextColor, bgcolor=tableShortBGColor)
                if tpScaleFactor != 1:
                    table.cell(atrTable, 7, 1, text=string.tostring(math.round_to_mintick(scaledATR * tpScaleFactor if allowTableRepainting else scaledATR[1] * tpScaleFactor)), text_color=tableTextColor, bgcolor=tableShortBGColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
