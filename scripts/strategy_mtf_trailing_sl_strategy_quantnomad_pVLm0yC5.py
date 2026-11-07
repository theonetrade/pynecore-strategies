"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, color, high, input, low, math, nz, plot, request, script,
    strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title='MTF Trailing SL Strategy [QuantNomad]', shorttitle='MTF TrailingSL [QN]', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    atr_length=input(14, title='ATR Length'),
    atr_mult=input.float(2, title='ATR Mult'),
    tf2=input('120', title='TF2'),
    tf3=input('180', title='TF3'),
    tf4=input('240', title='TF4'),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2016, title='From Year', minval=1970),
    toDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2100, title='To Year', minval=1970)
):
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate
    def tsl():
        sl_val = atr_mult * ta.atr(atr_length)
        pos: Series[int] = 0
        trailing_sl: Series[float] = 0.0
        long_signal = nz(pos[1]) != 1 and high > nz(trailing_sl[1])
        short_signal = nz(pos[1]) != -1 and low < nz(trailing_sl[1])
        trailing_sl = high + sl_val if short_signal else low - sl_val if long_signal else math.max(low - sl_val, nz(trailing_sl[1])) if nz(pos[1]) == 1 else math.min(high + sl_val, nz(trailing_sl[1])) if nz(pos[1]) == -1 else nz(trailing_sl[1])
        pos = 1 if long_signal else -1 if short_signal else nz(pos[1])
        return trailing_sl

    trailing_sl1 = tsl()
    trailing_sl2 = request.security(syminfo.tickerid, tf2, inline_series(tsl(), 1), lookahead=barmerge.lookahead_on)
    trailing_sl3 = request.security(syminfo.tickerid, tf3, inline_series(tsl(), 1), lookahead=barmerge.lookahead_on)
    trailing_sl4 = request.security(syminfo.tickerid, tf4, inline_series(tsl(), 1), lookahead=barmerge.lookahead_on)
    pos1: Series[int] = 0
    pos1 = -1 if low <= trailing_sl1 else 1 if high >= trailing_sl1 else nz(pos1[1])
    pos2: Series[int] = 0
    pos2 = -1 if low <= trailing_sl2 else 1 if high >= trailing_sl2 else nz(pos2[1])
    pos3: Series[int] = 0
    pos3 = -1 if low <= trailing_sl3 else 1 if high >= trailing_sl3 else nz(pos3[1])
    pos4: Series[int] = 0
    pos4 = -1 if low <= trailing_sl4 else 1 if high >= trailing_sl4 else nz(pos4[1])
    total_pos = pos1 + pos2 + pos3 + pos4
    plot(trailing_sl1, linewidth=2, color=color.green if pos1 == 1 else color.red, title='TSL TF1')
    plot(trailing_sl2, linewidth=2, color=color.green if pos2 == 1 else color.red, title='TSL TF2')
    plot(trailing_sl3, linewidth=2, color=color.green if pos3 == 1 else color.red, title='TSL TF3')
    plot(trailing_sl4, linewidth=2, color=color.green if pos4 == 1 else color.red, title='TSL TF4')
    if total_pos == 4 and time_cond:
        strategy.entry('long', strategy.long)
    if total_pos == -4 and time_cond:
        strategy.entry('short', strategy.short)
    if total_pos <= 0:
        strategy.close('long')
    if total_pos >= 0:
        strategy.close('short')
    if not time_cond:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
