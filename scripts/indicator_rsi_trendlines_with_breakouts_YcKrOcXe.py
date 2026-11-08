"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt_copy
from pynecore.lib import (
    alertcondition, bar_index, barmerge, barstate, close, color, fixnan,
    hline, input, label, line, na, plot, request, script, size, syminfo, ta
)
from pynecore.types import Color, Persistent, Series
import lib.HoanGhetti.SimpleTrendlines.v3 as tl

g_trendlines: str = 'Trendline Settings'
g_conditions: str = 'Conditions'
g_styling: str = 'Styling'
g_timeframe: str = 'Timeframe'


@script.indicator('RSI Trendlines with Breakouts [HG]', precision=2, max_labels_count=500, max_lines_count=500, na_bool=True)
def main(
    input_timeframe=input.timeframe(defval='', title='Timeframe', group=g_timeframe),
    input_pLen=input.int(defval=4, title='Lookback Range', minval=1, group=g_trendlines, tooltip='How many bars to determine when a swing high/low is detected.'),
    input_rLen=input.int(defval=14, title='RSI Length', minval=1, group=g_trendlines),
    input_rSrc: Series[float] = input.source(defval=close, title='RSI Source', group=g_trendlines),
    input_repaint=input.string(defval='On', title='Repainting', group=g_conditions, options=('On', 'Off: Bar Confirmation'), tooltip='Bar Confirmation: Generates alerts when candle closes. (1 Candle Later)'),
    input_rsiDiff=input.int(defval=3, title='RSI Difference', group=g_conditions, tooltip='The difference between the current RSI value and the breakout value.\n\nHow much higher in value should the current RSI be compared to the breakout value in order to detect a breakout?'),
    input_rsiCol=input.color(defval=color.blue, title='RSI Color', group=g_styling),
    input_width=input.int(defval=2, title='Line Width', minval=1, group=g_styling),
    input_lblType=input.string(defval='Simple', title='Label Type', group=g_styling, options=('Full', 'Simple')),
    input_lblSize=input.string(defval=size.small, title='Label Size', group=g_styling, options=(size.huge, size.large, size.normal, size.small, size.tiny)),
    input_pLowCol=input.color(defval=color.red, title='Pivot Low', inline='col', group=g_styling),
    input_pHighCol=input.color(defval=color.new('#089981'), title='Pivot High', inline='col', group=g_styling),
    input_override=input.bool(defval=False, title='Override Text Color', group=g_styling, inline='override'),
    input_overCol=input.color(defval=color.white, title=' ', group=g_styling, inline='override')
):
    __block_result__ = na
    __switch__ = input_lblType
    if __switch__ == 'Simple':
        __block_result__ = 'Br'
    elif __switch__ == 'Full':
        __block_result__ = 'Break'
    lblText = __block_result__
    __block_result_1__ = na
    __switch__ = input_repaint
    if __switch__ == 'On':
        __block_result_1__ = True
    elif __switch__ == 'Off: Bar Confirmation':
        __block_result_1__ = False
    repaint = __block_result_1__
    rsi_v = ta.rsi(input_rSrc, input_rLen)
    rsi = rsi_v if input_timeframe == '' else request.security(syminfo.tickerid, input_timeframe, rsi_v, lookahead=barmerge.lookahead_on)
    pl = fixnan(ta.pivotlow(rsi, 1, input_pLen))
    ph = fixnan(ta.pivothigh(rsi, 1, input_pLen))
    def pivot(pType: float):
        pivot__00000023__ = pl if pType == pl else ph
        xAxis = ta.valuewhen(cast_bool(ta.change(pivot__00000023__)), bar_index, 0) - ta.valuewhen(cast_bool(ta.change(pivot__00000023__)), bar_index, 1)
        prevPivot = ta.valuewhen(cast_bool(ta.change(pivot__00000023__)), pivot__00000023__, 1)
        pivotCond = cast_bool(ta.change(pivot__00000023__)) and (pivot__00000023__ > prevPivot if pType == pl else pivot__00000023__ < prevPivot)
        pData: tl.tl = tl.new(x_axis=xAxis, offset=input_pLen, strictMode=True, strictType=0 if pType == pl else 1)
        method_call('drawLine', pData, pivotCond, prevPivot, pivot__00000023__, rsi)
        return pData

    def breakout(this: tl.Trendline, pType: float):
        hasCrossed: Persistent[bool] = False
        if cast_bool(ta.change(method_call('get_y1', this.lines.startline))):
            hasCrossed = False
        method_call('drawTrendline', this, not hasCrossed)
        condType = (rsi < method_call('get_y2', this.lines.trendline) - input_rsiDiff if pType == pl else rsi > method_call('get_y2', this.lines.trendline) + input_rsiDiff) and (not hasCrossed)
        condition = condType if repaint else condType and barstate.isconfirmed
        if condition:
            hasCrossed = True
            method_call('set_xy2', this.lines.startline, method_call('get_x2', this.lines.trendline), method_call('get_y2', this.lines.trendline))
            method_call('set_xy2', this.lines.trendline, na, na)
            udt_copy(this.lines.startline)
            label.new(bar_index, method_call('get_y2', this.lines.startline), text=lblText, color=color.new(input_pLowCol, 50) if pType == pl else color.new(input_pHighCol, 50), size=input_lblSize, style=label.style_label_lower_left if pType == pl else label.style_label_upper_left, textcolor=(input_overCol if input_override else input_pLowCol) if pType == pl else input_overCol if input_override else input_pHighCol)
        return hasCrossed

    @method
    def style(this: tl.Trendline, col: Color):
        method_call('set_color', this.lines.startline, col)
        method_call('set_width', this.lines.startline, input_width)
        method_call('set_color', this.lines.trendline, col)
        method_call('set_width', this.lines.trendline, input_width)
        return method_call('set_style', this.lines.trendline, line.style_dashed)

    plData = pivot(pl)
    phData = pivot(ph)
    method_call(style, plData, input_pLowCol)
    method_call(style, phData, input_pHighCol)
    cu = breakout(plData, pl)
    co = breakout(phData, ph)
    hline(70, title='Overbought', color=input_pHighCol, linestyle=hline.style_dotted)
    hline(30, title='Oversold', color=input_pLowCol, linestyle=hline.style_dotted)
    plot(rsi, title='Relative Strength Index', linewidth=2, color=input_rsiCol)
    alertcondition(cast_bool(ta.change(method_call('get_y1', plData.lines.startline))), 'New Pivot Low Trendline')
    alertcondition(ta.change(cu) and cu, 'Pivot Low Breakout')
    alertcondition(cast_bool(ta.change(method_call('get_y1', phData.lines.startline))), 'New Pivot High Trendline')
    alertcondition(ta.change(co) and co, 'Pivot High Breakout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
