"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barstate, color, extend, high, input, label, line, low, math,
    plot, position, script, size, string, ta, table, text, time
)
from pynecore.types import Persistent


@script.indicator('Pivots High/Low Analysis & Forecast [LuxAlgo]', overlay=True, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    length=input(50),
    show_fcast=input(True, 'Show Forecasted Pivots'),
    dash_loc=input.string('Bottom Right', 'Dashboard Location', options=('Top Right', 'Bottom Right', 'Top Left', 'Bottom Left'), group='Dashboard'),
    text_size=input.string('Normal', 'Dashboard Size', options=('Tiny', 'Small', 'Normal', 'Large'), group='Dashboard'),
    txt_col=input.color(color.gray, 'Text/Frame Color', group='Dashboard')
):
    barssince_ph: int = 0
    barssince_pl: int = 0
    rchange_ph: float = 0.0
    rchange_pl: float = 0.0
    n = bar_index
    dt = math.round(time - time[1])
    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)
    ph_x2 = ta.valuewhen(cast_bool(ph), n - length, 1)
    pl_x2 = ta.valuewhen(cast_bool(pl), n - length, 1)
    ph_y2 = ta.valuewhen(cast_bool(ph), ph, 1)
    pl_y2 = ta.valuewhen(cast_bool(pl), pl, 1)
    if cast_bool(ph):
        barssince_ph = n - length - ph_x2
        rchange_ph = (ph - ph_y2) / ph_y2 * 100
        txt = string.format('Δ% : {0,number,#.##}\nΔt : {1}', rchange_ph, barssince_ph)
        css = color.new('#2157F3') if ph > ph_y2 else color.new('#FF1100')
        line.new(n - length, ph_y2, ph_x2, ph_y2, color=color.new('#FF1100'), style=line.style_dotted)
        line.new(n - length, ph, n - length, ph_y2, color=css, style=line.style_arrow_both)
        label.new(n - length, math.max(ph, ph_y2), txt, color=color.new('#00000000'), style=label.style_label_down, textcolor=color.gray, textalign=text.align_left, size=size.small)
    if cast_bool(pl):
        barssince_pl = n - length - pl_x2
        rchange_pl = (pl - pl_y2) / pl_y2 * 100
        txt = string.format('Δ% : {0,number,#.##}\nΔt : {1}', rchange_pl, barssince_pl)
        css = color.new('#2157F3') if pl > pl_y2 else color.new('#FF1100')
        line.new(n - length, pl_y2, pl_x2, pl_y2, color=color.new('#0CB51A'), style=line.style_dotted)
        line.new(n - length, pl, n - length, pl_y2, color=css, style=line.style_arrow_both)
        label.new(n - length, math.min(pl, pl_y2), txt, color=color.new('#00000000'), style=label.style_label_up, textcolor=color.gray, textalign=text.align_left, size=size.small)
    avg_barssince_ph = ta.cum(barssince_ph) / ta.cum(math.sign(barssince_ph))
    avg_barssince_pl = ta.cum(barssince_pl) / ta.cum(math.sign(barssince_pl))
    avg_rchange_ph = ta.cum(rchange_ph) / ta.cum(math.abs(math.sign(rchange_ph)))
    avg_rchange_pl = ta.cum(rchange_pl) / ta.cum(math.abs(math.sign(rchange_pl)))
    if show_fcast:
        if cast_bool(ph):
            x12 = n + math.min(cast_int(avg_barssince_ph - length), 500)
            line.delete(inline_series(line.new(x12, high, x12, low, extend=extend.both, color=color.new('#FF1100'), style=line.style_dashed), 1))
            line.delete(inline_series(line.new(n - length, ph, n, ph, extend=extend.right, color=color.new('#FF1100'), style=line.style_dotted), 1))
    if cast_bool(pl):
        x12 = n + math.min(cast_int(avg_barssince_pl - length), 500)
        line.delete(inline_series(line.new(x12, high, x12, low, extend=extend.both, color=color.new('#0CB51A'), style=line.style_dashed), 1))
        line.delete(inline_series(line.new(n - length, pl, n, pl, extend=extend.right, color=color.new('#0CB51A'), style=line.style_dotted), 1))
    table_position: Persistent = position.top_left if dash_loc == 'Top Left' else position.bottom_left if dash_loc == 'Bottom Left' else position.top_right if dash_loc == 'Top Right' else position.bottom_right
    table_text_size: Persistent = size.tiny if text_size == 'Tiny' else size.small if text_size == 'Small' else size.normal if text_size == 'Normal' else size.large
    new_table = table.new(table_position, 3, 3, border_color=txt_col, border_width=1, frame_color=txt_col, frame_width=1)
    if barstate.islast:
        table.cell(new_table, 0, 1, 'Pivot High', text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 0, 2, 'Pivot Low', text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 1, 0, 'E[Δt]', text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 2, 0, 'E[Δ%]', text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 1, 1, string.tostring(avg_barssince_ph, '#.##'), text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 1, 2, string.tostring(avg_barssince_pl, '#.##'), text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 2, 1, string.tostring(avg_rchange_ph, '#.##'), text_color=txt_col, text_size=table_text_size)
        table.cell(new_table, 2, 2, string.tostring(avg_rchange_pl, '#.##'), text_color=txt_col, text_size=table_text_size)
    plot(ph, 'Pivot High', color.new(color.new('#FF1100'), 0), 2, plot.style_circles, offset=-length)
    plot(pl, 'Pivot Low', color.new(color.new('#0CB51A'), 0), 2, plot.style_circles, offset=-length)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
