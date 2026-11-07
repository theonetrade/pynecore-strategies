"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, barstate, close, color, currency, display, fill, input,
    location, na, plot, plotshape, position, script, shape, size, strategy, string, ta, table
)
from pynecore.types import Color, Persistent, Series

grp_st: str = 'Supertrend Settings (Trigger)'
grp_ema: str = 'EMA Filter (Structure)'
grp_adx: str = 'ADX Filter (Strength)'
grp_disp: str = 'Visuals'


@script.strategy('Golden Vector Trend Orchestrator (GVTO))', shorttitle='GVTO_Full', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=2, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    st_atr_len=input.int(14, minval=1, title='ATR Length', group=grp_st),
    st_factor=input.float(3.5, minval=0.1, step=0.1, title='ATR Multiplier', group=grp_st),
    ema_len=input.int(200, minval=1, title='EMA Length', group=grp_ema),
    use_ema=input.bool(True, title='เปิดใช้ EMA Filter?', group=grp_ema),
    adx_len=input.int(14, minval=1, title='ADX Length', group=grp_adx),
    adx_thresh=input.int(25, minval=1, title='ADX Threshold', group=grp_adx),
    adx_smooth=input.int(14, minval=1, title='ADX Smoothing', group=grp_adx),
    show_table=input.bool(True, title='แสดงตารางข้อมูล', group=grp_disp)
):
    ema_macro = ta.ema(close, ema_len)
    st_value, st_direction = ta.supertrend(st_factor, st_atr_len)
    di_plus, di_minus, adx_value = ta.dmi(adx_len, adx_smooth)
    is_st_bullish = st_direction == -1
    is_st_bearish = st_direction == 1
    filter_long = close > ema_macro if use_ema else True
    filter_short = close < ema_macro if use_ema else True
    filter_adx = adx_value >= adx_thresh
    momentum_long = di_plus > di_minus
    momentum_short = di_minus > di_plus
    long_condition: Series = is_st_bullish and filter_long and filter_adx and momentum_long
    short_condition: Series = is_st_bearish and filter_short and filter_adx and momentum_short
    long_trigger = long_condition and (not long_condition[1])
    short_trigger = short_condition and (not short_condition[1])
    if long_trigger:
        strategy.entry('Long Run', strategy.long, comment='GOLD BUY')
    if short_trigger:
        strategy.entry('Short Run', strategy.short, comment='GOLD SELL')
    if is_st_bearish and strategy.position_size > 0:
        strategy.close('Long Run', comment='Exit Long')
    if is_st_bullish and strategy.position_size < 0:
        strategy.close('Short Run', comment='Exit Short')
    pnl_pct: float = 0.0
    pnl_text: str = 'Waiting...'
    pnl_bg: Color = color.gray
    if strategy.position_size != 0:
        entry_price: float = strategy.position_avg_price
        if strategy.position_size > 0:
            pnl_pct = (close - entry_price) / entry_price * 100
            pnl_text = 'L: ' + string.tostring(pnl_pct, '#.00') + '%'
        else:
            pnl_pct = (entry_price - close) / entry_price * 100
            pnl_text = 'S: ' + string.tostring(pnl_pct, '#.00') + '%'
        pnl_bg = color.green if pnl_pct > 0 else color.red
    else:
        pnl_text = 'Waiting...'
        pnl_bg = color.gray
    plot(ema_macro if use_ema else na, color=color.new(color.orange, 0), title='200 EMA', linewidth=2)
    plot(st_value, color=color.green if st_direction == -1 else color.red, linewidth=2, title='Supertrend')
    plotshape(long_trigger and strategy.position_size <= 0, title='Buy Label', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, text='BUY', size=size.small)
    plotshape(short_trigger and strategy.position_size >= 0, title='Sell Label', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, text='SELL', size=size.small)
    p1 = plot(st_value, display=display.none)
    p2 = plot(close, display=display.none)
    fill(p1, p2, color=color.new(color.green, 90) if st_direction == -1 else color.new(color.red, 90), title='Trend Background')
    barcolor(color.green if is_st_bullish else color.red if is_st_bearish else na)
    if show_table:
        tbl: Persistent = table.new(position.top_right, 2, 5, frame_color=color.gray, frame_width=1, border_width=1, border_color=color.gray)
        if barstate.islast:
            table.cell(tbl, 0, 0, 'GVTO Monitor', text_color=color.white, bgcolor=color.black)
            table.cell(tbl, 1, 0, 'Status', text_color=color.white, bgcolor=color.black)
            table.cell(tbl, 0, 1, 'Trend', bgcolor=color.gray)
            table.cell(tbl, 1, 1, 'BULLISH' if is_st_bullish else 'BEARISH', bgcolor=color.green if is_st_bullish else color.red)
            table.cell(tbl, 0, 2, 'ADX Power', bgcolor=color.gray)
            table.cell(tbl, 1, 2, string.tostring(adx_value, '#.##'), bgcolor=color.green if filter_adx else color.orange)
            table.cell(tbl, 0, 3, 'Zone', bgcolor=color.gray)
            table.cell(tbl, 1, 3, 'BUY ZONE' if close > ema_macro else 'SELL ZONE', bgcolor=color.green if close > ema_macro else color.red)
            table.cell(tbl, 0, 4, 'Current P/L', bgcolor=color.gray, text_color=color.white)
            table.cell(tbl, 1, 4, pnl_text, bgcolor=pnl_bg, text_color=color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
