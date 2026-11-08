"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, close, color, dayofmonth, display, extend, format,
    high, input, label, line, low, month, na, open, plot, script, string, syminfo, time,
    time_close, timestamp, xloc, year
)
from pynecore.types import Label, Line, Persistent


@script.indicator('Horizontal Ray from Specified Date', overlay=True)
def main(
    in_day=input.int(15, 'Date (D / M / Y)', minval=1, maxval=31, inline='date'),
    in_month=input.int(9, '', minval=1, maxval=12, inline='date'),
    in_year=input.int(2026, '', minval=1990, maxval=2100, inline='date'),
    src_in=input.string('High', 'Price Source', options=('High', 'Low', 'Close', 'Open')),
    col_above=input.color(color.green, 'Color: Close Above', inline='col'),
    col_below=input.color(color.red, 'Below', inline='col'),
    ray_thickness=input.int(2, 'Ray Thickness', minval=1, maxval=5),
    ray_style_in=input.string('Solid', 'Ray Style', options=('Solid', 'Dashed', 'Dotted')),
    show_text=input.bool(True, 'Show Text', inline='txt'),
    ray_text=input.string('', '', inline='txt', tooltip='Leave blank to show the date'),
    show_price=input.bool(True, 'Show Price in Text'),
    text_offset=input.int(15, 'Text Position (bars right of last candle)', minval=0, maxval=400)
):
    __block_result__ = na
    __switch__ = ray_style_in
    if __switch__ == 'Dashed':
        __block_result__ = line.style_dashed
    elif __switch__ == 'Dotted':
        __block_result__ = line.style_dotted
    else:
        __block_result__ = line.style_solid
    ray_style = __block_result__

    t0 = timestamp(syminfo.timezone, in_year, in_month, in_day, 0, 0)
    day_key = year(time) * 10000 + month(time) * 100 + dayofmonth(time)

    ray: Persistent[Line] = na(Line)
    ray_lbl: Persistent[Label] = na(Label)
    lock_key: Persistent[int] = na(int)
    lock_time: Persistent[int] = na(int)
    lvl: Persistent[float] = na(float)
    lvl_bar: Persistent[int] = na(int)

    if na(lock_key) and time_close > t0:
        lock_key = day_key
        lock_time = time
        lvl = high if src_in == 'High' else low if src_in == 'Low' else close if src_in == 'Close' else open
        lvl_bar = bar_index
        ray = line.new(lvl_bar, lvl, lvl_bar + 1, lvl, xloc=xloc.bar_index, extend=extend.right, color=col_below, width=ray_thickness, style=ray_style)
    elif not na(lock_key) and day_key == lock_key:
        if src_in == 'High' and high > lvl:
            lvl = high
            lvl_bar = bar_index
        elif src_in == 'Low' and low < lvl:
            lvl = low
            lvl_bar = bar_index
        elif src_in == 'Close':
            lvl = close
            lvl_bar = bar_index
        line.set_xy1(ray, lvl_bar, lvl)
        line.set_xy2(ray, lvl_bar + 1, lvl)

    is_above = not na(lvl) and close > lvl
    cur_col = col_above if is_above else col_below

    if barstate.islast and (not na(ray)):
        line.set_color(ray, cur_col)
        if show_text:
            date_str = string.format_time(lock_time, 'dd MMM yyyy', syminfo.timezone)
            base_txt = date_str if ray_text == '' else ray_text
            txt = base_txt + ' · ' + string.tostring(lvl, format.mintick) if show_price else base_txt
            if na(ray_lbl):
                ray_lbl = label.new(bar_index + text_offset, lvl, txt, xloc=xloc.bar_index, style=label.style_label_lower_right, color=color.new(color.white, 100), textcolor=cur_col)
            else:
                label.set_xy(ray_lbl, bar_index + text_offset, lvl)
                label.set_text(ray_lbl, txt)
                label.set_textcolor(ray_lbl, cur_col)

    plot(lvl, 'Ray Level', display=display.data_window)
    plot(na if na(lvl) else 1 if is_above else 0, 'Above Ray', display=display.data_window)
    plot(na if na(lvl) else (close - lvl) / lvl * 100, 'Distance %', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)