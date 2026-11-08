"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barstate, box, close, color, display, fill, input, label,
    location, math, open, plot, plotchar, position, script, string, syminfo, ta, table, text
)
from pynecore.types import Persistent, Series


@script.indicator('Risk Management Tool [LuxAlgo]', overlay=True, na_bool=True)
def main(
    pos_type=input.string('Long', 'Position Type', options=('Long', 'Short')),
    acc_size=input.float(1000.0, 'Account Size', minval=0),
    risk=input.float(2.0, 'Risk               ', minval=0, inline='risk'),
    risk_type=input.string('%', '', options=('%', 'USD'), inline='risk'),
    entry_price=input.float(40000.0, 'Entry Price', confirm=True),
    entry_cross=input.bool(False, 'Entry From Cross', inline='entry'),
    cross_src: Series[float] = input.source(open, '', inline='entry'),
    tp=input.float(5.0, 'Take Profit', minval=0, group='Take Profit/Stop Loss', inline='tp', confirm=True),
    tp_type=input.string('%', '', options=('ATR', '%', 'Price', 'Range'), group='Take Profit/Stop Loss', inline='tp', confirm=True),
    sl=input.float(5.0, 'Stop Loss  ', minval=0, group='Take Profit/Stop Loss', inline='sl', confirm=True),
    sl_type=input.string('%', '', options=('ATR', '%', 'Price', 'Range'), group='Take Profit/Stop Loss', inline='sl', confirm=True),
    profit_col=input.color(color.new(color.new('#009688'), 80), 'Profit Color', group='Style', inline='col'),
    loss_col=input.color(color.new(color.new('#F44336'), 80), 'Loss Color', group='Style', inline='col')
):
    tp_val: float = 0.0
    sl_val: float = 0.0
    entry: float = 0.0
    pos = 1 if pos_type == 'Long' else -1
    if entry_cross:
        entry = ta.valuewhen(inline_series(ta.cross(close, cross_src), 1), open, 0)
    else:
        entry = entry_price
    tp_range = ta.highest(math.max(math.round(tp), 1)) - ta.lowest(math.max(math.round(tp), 1))
    sl_range = ta.highest(math.max(math.round(sl), 1)) - ta.lowest(math.max(math.round(sl), 1))
    if tp_type == 'ATR':
        tp_val = entry + ta.atr(math.max(math.round(tp), 1)) * pos
    elif tp_type == '%':
        tp_val = entry + tp / 100 * entry * pos
    elif tp_type == 'Price':
        tp_val = tp
    elif tp_type == 'Range':
        tp_val = entry + tp_range * pos
    if sl_type == 'ATR':
        sl_val = entry - ta.atr(math.max(math.round(sl), 1)) * pos
    elif sl_type == '%':
        sl_val = entry - sl / 100 * entry * pos
    elif sl_type == 'Price':
        sl_val = sl
    elif sl_type == 'Range':
        sl_val = entry - sl_range * pos
    open_pl = (close - entry) * pos
    position_size: float = 0.0
    RR = math.abs((tp_val - entry) / (sl_val - entry))
    if risk_type == '%':
        position_size = risk / 100 * acc_size / ((entry - sl_val) * pos)
    else:
        position_size = risk / ((entry - sl_val) * pos)
    n = bar_index
    tbl: Persistent = table.new(position.bottom_right, 2, 3)
    if barstate.islast:
        box.delete(inline_series(box.new(n, tp_val, n + 100, entry, bgcolor=profit_col, border_width=0), 1))
        box.delete(inline_series(box.new(n, entry, n + 100, sl_val, bgcolor=loss_col, border_width=0), 1))
        label.delete(inline_series(label.new(n + 100, entry, string.format('P&L : {0} {1} ({2,number,percent})', open_pl, syminfo.currency, open_pl / entry), color=profit_col if open_pl > 0 else loss_col, style=label.style_label_left, textcolor=color.gray, textalign=text.align_left), 1))
        if cast_bool(tp):
            label.delete(inline_series(label.new(n + 100, tp_val, string.format('TP : {0} ({1,number,percent})', tp_val, (tp_val - entry) / entry), color=profit_col, style=label.style_label_left, textcolor=color.gray, textalign=text.align_left), 1))
        if cast_bool(sl):
            label.delete(inline_series(label.new(n + 100, sl_val, string.format('TSL : {0} ({1,number,percent})', sl_val, (entry - sl_val) / entry), color=loss_col, style=label.style_label_left, textcolor=color.gray, textalign=text.align_left), 1))
        table.cell(tbl, 0, 0, 'Risk/Reward', text_color=color.gray, text_halign=text.align_center)
        table.cell(tbl, 1, 0, string.tostring(RR, '#.####'), text_color=color.gray, text_halign=text.align_center)
        table.cell(tbl, 0, 1, 'Position Size', text_color=color.gray, text_halign=text.align_center)
        table.cell(tbl, 1, 1, string.tostring(position_size, '#.####') + ' ' + syminfo.basecurrency, text_color=color.gray, text_halign=text.align_center)
    Close = plot(close, editable=False, display=display.none)
    Entry = plot(entry, editable=False, display=display.none)
    fill(Close, Entry, color=profit_col if open_pl > 0 else loss_col)
    plotchar(open_pl, 'Rolling Open PL%', '', location.abovebar, profit_col if open_pl > 0 else loss_col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
