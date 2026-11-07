"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barstate, bgcolor, box, close, color,
    dayofweek, high, hour, input, label, line, location, low, minute, na, open, plotshape,
    position, script, shape, size, strategy, string, ta, table, text, time, volume
)
from pynecore.types import Persistent, Table

grp1: str = "Pivot Reversals"
grp2: str = "S/D Zone"
grp3: str = "Filters"
grp4: str = "Risk Management"
grp5: str = "Session & Safety"
grp6: str = "Visuals"


@script.strategy('Ultimate Prop Firm [Artillery]', shorttitle='UPF', overlay=True, initial_capital=10000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=0.62, slippage=1, calc_on_every_tick=False, process_orders_on_close=True, margin_long=5, margin_short=5, max_labels_count=500, max_lines_count=500, max_boxes_count=500)
def main(
    piv_left=input.int(3, "Pivot Left Bars", group=grp1),
    piv_right=input.int(2, "Pivot Right Bars", group=grp1),
    atr_len=input.int(14, "ATR Length", group=grp2),
    sd_mult=input.float(1.0, "S/D Width ATR", group=grp2),
    rsi_len=input.int(14, "RSI Length", group=grp3),
    rsi_bull=input.float(40.0, "RSI Long Min", group=grp3),
    rsi_bear=input.float(60.0, "RSI Short Max", group=grp3),
    vol_len=input.int(20, "Volume MA Len", group=grp3),
    vol_mult=input.float(0.8, "Volume Mult", group=grp3),
    sl_mult=input.float(1.5, "SL ATR Mult", group=grp4),
    tp1_mult=input.float(1.0, "TP1 ATR Mult", group=grp4),
    tp2_mult=input.float(2.0, "TP2 ATR Mult", group=grp4),
    tp3_mult=input.float(3.5, "TP3 ATR Mult", group=grp4),
    sess_start=input.int(930, "Start HHMM ET", group=grp5),
    sess_end=input.int(1555, "End HHMM ET", group=grp5),
    max_trades=input.int(5, "Max Trades/Day", group=grp5),
    max_dd=input.float(3.5, "Max Daily DD %", group=grp5),
    show_levels=input.bool(True, "Entry/TP/SL levels on signals", group=grp6),
    show_zones=input.bool(True, "Supply/demand zone boxes", group=grp6),
    show_mood=input.bool(True, "Background market mood", group=grp6),
    show_dash=input.bool(True, "Dashboard", group=grp6)
):
    atr = ta.atr(atr_len)

    piv_h = ta.pivothigh(high, piv_left, piv_right)
    piv_l = ta.pivotlow(low, piv_left, piv_right)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)
    if not na(piv_h):
        last_ph = piv_h
    if not na(piv_l):
        last_pl = piv_l

    demand_hi = last_pl + atr * sd_mult
    supply_lo = last_ph - atr * sd_mult

    rsi = ta.rsi(close, rsi_len)
    vma = ta.sma(volume, vol_len)
    vol_ok = volume >= vma * vol_mult

    ch = hour(time, 'America/New_York')
    cm = minute(time, 'America/New_York')
    ct = ch * 100 + cm
    in_sess = ct >= sess_start and ct <= sess_end
    is_eod = ct >= sess_end

    dtrades: Persistent[int] = 0
    deq: Persistent[float] = strategy.equity
    if ta.change(dayofweek) != 0:
        dtrades = 0
        deq = strategy.equity
    ddd = (deq - strategy.equity) / deq * 100 if deq > 0 else 0
    can_trade = dtrades < max_trades and ddd < max_dd and in_sess

    long_go = not na(piv_l) and low <= demand_hi and (rsi >= rsi_bull) and (close > open) and vol_ok and can_trade and (strategy.position_size == 0)

    short_go = not na(piv_h) and high >= supply_lo and (rsi <= rsi_bear) and (close < open) and vol_ok and can_trade and (strategy.position_size == 0)

    e_sl: Persistent[float] = na(float)
    e_tp1: Persistent[float] = na(float)
    e_tp2: Persistent[float] = na(float)
    e_tp3: Persistent[float] = na(float)

    if long_go:
        e_sl = close - atr * sl_mult
        e_tp1 = close + atr * tp1_mult
        e_tp2 = close + atr * tp2_mult
        e_tp3 = close + atr * tp3_mult
        strategy.entry('L', strategy.long)
        strategy.exit('T1', 'L', qty_percent=40, limit=e_tp1, stop=e_sl)
        strategy.exit('T2', 'L', qty_percent=50, limit=e_tp2, stop=e_sl)
        strategy.exit('T3', 'L', limit=e_tp3, stop=e_sl)
        dtrades += 1

    if short_go:
        e_sl = close + atr * sl_mult
        e_tp1 = close - atr * tp1_mult
        e_tp2 = close - atr * tp2_mult
        e_tp3 = close - atr * tp3_mult
        strategy.entry('S', strategy.short)
        strategy.exit('T1s', 'S', qty_percent=40, limit=e_tp1, stop=e_sl)
        strategy.exit('T2s', 'S', qty_percent=50, limit=e_tp2, stop=e_sl)
        strategy.exit('T3s', 'S', limit=e_tp3, stop=e_sl)
        dtrades += 1

    if is_eod and strategy.position_size != 0:
        strategy.close_all(comment='EOD')

    ema21 = ta.ema(close, 21)
    ema55 = ta.ema(close, 55)
    dip, dim, adx_val = ta.dmi(14, 14)
    trend_up = ema21 > ema55 and close > ema21
    trend_dn = ema21 < ema55 and close < ema21
    trending = adx_val > 20

    if show_zones and (not na(piv_l)):
        box.new(bar_index - piv_right, demand_hi, bar_index + 20, last_pl - atr * sd_mult, border_color=color.new(color.green, 70), bgcolor=color.new(color.green, 90))
    if show_zones and (not na(piv_h)):
        box.new(bar_index - piv_right, last_ph + atr * sd_mult, bar_index + 20, supply_lo, border_color=color.new(color.red, 70), bgcolor=color.new(color.red, 90))

    plotshape(long_go, 'Long Entry', shape.triangleup, location.belowbar, color.green, size=size.normal)
    plotshape(short_go, 'Short Entry', shape.triangledown, location.abovebar, color.red, size=size.normal)

    if show_levels and long_go:
        line.new(bar_index, close, bar_index + 30, close, color=color.new('#00E5FF'), width=3)
        label.new(bar_index + 15, close, 'BUY @ ' + string.tostring(close, '#.##'), style=label.style_label_center, color=color.new('#00E5FF'), textcolor=color.white, size=size.normal)
        box.new(bar_index, e_tp3, bar_index + 30, close, border_color=color.new(color.new('#00E5FF'), 30), bgcolor=color.new(color.new('#00E5FF'), 90), text='TARGET ZONE', text_color=color.new('#00E5FF'), text_size=size.small, text_halign=text.align_center, text_valign=text.align_center)
        line.new(bar_index, e_tp1, bar_index + 30, e_tp1, color=color.new('#69F0AE'), width=2, style=line.style_dashed)
        label.new(bar_index + 30, e_tp1, ' TP1 ' + string.tostring(e_tp1, '#.#'), style=label.style_label_left, color=color.new('#69F0AE'), textcolor=color.white, size=size.small)
        line.new(bar_index, e_tp2, bar_index + 30, e_tp2, color=color.new('#00E676'), width=2, style=line.style_dashed)
        label.new(bar_index + 30, e_tp2, ' TP2 ' + string.tostring(e_tp2, '#.#'), style=label.style_label_left, color=color.new('#00E676'), textcolor=color.white, size=size.small)
        line.new(bar_index, e_tp3, bar_index + 30, e_tp3, color=color.new('#FFD600'), width=3, style=line.style_dashed)
        label.new(bar_index + 30, e_tp3, ' TP3 ' + string.tostring(e_tp3, '#.#'), style=label.style_label_left, color=color.new('#FFD600'), textcolor=color.black, size=size.small)
        box.new(bar_index, close, bar_index + 30, e_sl, border_color=color.new(color.new('#FF1744'), 30), bgcolor=color.new(color.new('#FF1744'), 90), text='STOP ZONE', text_color=color.new('#FF1744'), text_size=size.small, text_halign=text.align_center, text_valign=text.align_center)
        line.new(bar_index, e_sl, bar_index + 30, e_sl, color=color.new('#FF1744'), width=3)
        label.new(bar_index + 30, e_sl, ' SL ' + string.tostring(e_sl, '#.#'), style=label.style_label_left, color=color.new('#FF1744'), textcolor=color.white, size=size.small)

    if show_levels and short_go:
        line.new(bar_index, close, bar_index + 30, close, color=color.new('#E040FB'), width=3)
        label.new(bar_index + 15, close, 'SELL @ ' + string.tostring(close, '#.##'), style=label.style_label_center, color=color.new('#E040FB'), textcolor=color.white, size=size.normal)
        box.new(bar_index, close, bar_index + 30, e_tp3, border_color=color.new(color.new('#E040FB'), 30), bgcolor=color.new(color.new('#E040FB'), 90), text='TARGET ZONE', text_color=color.new('#E040FB'), text_size=size.small, text_halign=text.align_center, text_valign=text.align_center)
        line.new(bar_index, e_tp1, bar_index + 30, e_tp1, color=color.new('#69F0AE'), width=2, style=line.style_dashed)
        label.new(bar_index + 30, e_tp1, ' TP1 ' + string.tostring(e_tp1, '#.#'), style=label.style_label_left, color=color.new('#69F0AE'), textcolor=color.white, size=size.small)
        line.new(bar_index, e_tp2, bar_index + 30, e_tp2, color=color.new('#00E676'), width=2, style=line.style_dashed)
        label.new(bar_index + 30, e_tp2, ' TP2 ' + string.tostring(e_tp2, '#.#'), style=label.style_label_left, color=color.new('#00E676'), textcolor=color.white, size=size.small)
        line.new(bar_index, e_tp3, bar_index + 30, e_tp3, color=color.new('#FFD600'), width=3, style=line.style_dashed)
        label.new(bar_index + 30, e_tp3, ' TP3 ' + string.tostring(e_tp3, '#.#'), style=label.style_label_left, color=color.new('#FFD600'), textcolor=color.black, size=size.small)
        box.new(bar_index, e_sl, bar_index + 30, close, border_color=color.new(color.new('#FF1744'), 30), bgcolor=color.new(color.new('#FF1744'), 90), text='STOP ZONE', text_color=color.new('#FF1744'), text_size=size.small, text_halign=text.align_center, text_valign=text.align_center)
        line.new(bar_index, e_sl, bar_index + 30, e_sl, color=color.new('#FF1744'), width=3)
        label.new(bar_index + 30, e_sl, ' SL ' + string.tostring(e_sl, '#.#'), style=label.style_label_left, color=color.new('#FF1744'), textcolor=color.white, size=size.small)

    bg_color = color.new(color.new('#0D1B2A'), 90) if not in_sess else color.new(color.new('#00E676'), 95) if trend_up and trending else color.new(color.new('#FF1744'), 95) if trend_dn and trending else color.new(color.new('#7C4DFF'), 97)
    bgcolor(bg_color if show_mood else na)
    bgcolor(color.new(color.new('#00E5FF'), 80) if show_mood and long_go else color.new(color.new('#E040FB'), 80) if show_mood and short_go else na)

    if show_dash and barstate.islast:
        dash: Persistent[Table] = table.new(position.top_right, 2, 8, bgcolor=color.new(color.new('#0D1117'), 5), border_color=color.new(color.new('#30363D'), 5), border_width=1)
        table.cell(dash, 0, 0, '  UPF | ARTILLERY  ', text_color=color.new('#00E5FF'), text_size=size.normal, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 1, 0, '', bgcolor=color.new(color.new('#161B22'), 5))
        mkt = 'BULL' if trend_up and trending else 'BEAR' if trend_dn and trending else 'CHOP'
        mkt_c = color.new('#00E676') if trend_up and trending else color.new('#FF5252') if trend_dn and trending else color.new('#FFC107')
        table.cell(dash, 0, 1, '  Market  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        table.cell(dash, 1, 1, '  ' + mkt + '  ', text_color=mkt_c, text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        pos = 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT'
        pos_c = color.new('#00E5FF') if strategy.position_size > 0 else color.new('#E040FB') if strategy.position_size < 0 else color.gray
        table.cell(dash, 0, 2, '  Position  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 1, 2, '  ' + pos + '  ', text_color=pos_c, text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 0, 3, '  Session  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        table.cell(dash, 1, 3, '  OPEN  ' if in_sess else '  CLOSED  ', text_color=color.new('#00E676') if in_sess else color.new('#FF5252'), text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        left = max_trades - dtrades
        table.cell(dash, 0, 4, '  Trades Left  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 1, 4, '  ' + string.tostring(left) + ' / ' + string.tostring(max_trades) + '  ', text_color=color.new('#00E676') if left > 0 else color.new('#FF5252'), text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 0, 5, '  Volume  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        table.cell(dash, 1, 5, '  STRONG  ' if vol_ok else '  WEAK  ', text_color=color.new('#00E676') if vol_ok else color.new('#FF5252'), text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        ready = can_trade and vol_ok and in_sess
        table.cell(dash, 0, 6, '  Status  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        table.cell(dash, 1, 6, '  READY  ' if ready else '  WAIT  ', text_color=color.new('#00E676') if ready else color.new('#FFC107'), text_size=size.small, bgcolor=color.new(color.new('#161B22'), 5))
        if strategy.position_size != 0:
            table.cell(dash, 0, 7, '  SL / TP3  ', text_color=color.white, text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
            table.cell(dash, 1, 7, '  ' + string.tostring(e_sl, '#.#') + ' / ' + string.tostring(e_tp3, '#.#') + '  ', text_color=color.new('#FFD600'), text_size=size.small, bgcolor=color.new(color.new('#21262D'), 5))
        else:
            table.cell(dash, 0, 7, '', bgcolor=color.new(color.new('#21262D'), 5))
            table.cell(dash, 1, 7, '', bgcolor=color.new(color.new('#21262D'), 5))

    alertcondition(long_go, 'UPF Long Entry', 'Ultimate Prop Firm: long entry signal')
    alertcondition(short_go, 'UPF Short Entry', 'Ultimate Prop Firm: short entry signal')
    alertcondition(is_eod and strategy.position_size != 0, 'UPF End of Day', 'Ultimate Prop Firm: end of session - position flattened')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
