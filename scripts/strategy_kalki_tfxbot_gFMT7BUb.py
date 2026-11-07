"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, box, close, color, high, input, low, na, open, plot,
    position, script, strategy, string, ta, table
)
from pynecore.types import Box, Persistent, Table

G_RISK: str = "🛡️ CARTEL RISK MANAGEMENT"
G_FILT: str = "⚡ SMC FILTERS"


@script.strategy('KALKI TFXBOT', shorttitle='KALKI TFX BOT', overlay=True, initial_capital=100, default_qty_type=strategy.fixed, default_qty_value=1, margin_long=0, margin_short=0, process_orders_on_close=True, max_boxes_count=500)
def main(
    i_rr=input.float(3.0, "Risk to Reward Ratio (e.g. 3 = 1:3 RR)", step=0.5, group=G_RISK),
    i_slBuffer=input.float(0.5, "Stop Loss Buffer (Pips)", step=0.1, group=G_RISK, tooltip="Adds a tiny gap below the wick so you don't get perfectly stopped out."),
    i_emaTrend=input.int(200, "EMA Trend Guard", group=G_FILT),
    i_pivotL=input.int(10, "Swing Left Lookback", group=G_FILT),
    i_pivotR=input.int(3, "Swing Right Lookback", group=G_FILT)
):
    c_slBox = color.new(color.rgb(156, 156, 156), 80)
    c_tpBuy = color.new(color.rgb(77, 208, 225), 80)
    c_tpSell = color.new(color.rgb(247, 82, 95), 80)
    c_entry = color.new(color.blue, 85)

    ema200 = ta.ema(close, i_emaTrend)

    pl: float = ta.pivotlow(low, i_pivotL, i_pivotR)
    ph: float = ta.pivothigh(high, i_pivotL, i_pivotR)

    current_sup: Persistent[float] = na(float)
    current_res: Persistent[float] = na(float)

    if not na(pl):
        current_sup = pl
    if not na(ph):
        current_res = ph

    plot(current_sup, color=color.new(color.blue, 50), style=plot.style_circles, linewidth=1, title='Liquidity Floor')
    plot(current_res, color=color.new(color.red, 50), style=plot.style_circles, linewidth=1, title='Liquidity Ceiling')

    sweep_buy: bool = low < current_sup and close > current_sup and (close > open) and (close > ema200)
    sweep_sell: bool = high > current_res and close < current_res and (close < open) and (close < ema200)

    b_entry: Persistent[Box] = na(Box)
    b_sl: Persistent[Box] = na(Box)
    b_tp: Persistent[Box] = na(Box)

    if sweep_buy and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('Short', comment='REVERSAL')
            box.set_right(b_entry, bar_index)
            box.set_right(b_sl, bar_index)
            box.set_right(b_tp, bar_index)

        entry_price: float = close
        sl_price: float = low - i_slBuffer / 10
        risk_amt: float = entry_price - sl_price
        tp_price: float = entry_price + risk_amt * i_rr

        b_entry = box.new(bar_index, entry_price, bar_index + 15, entry_price, border_width=1, border_color=color.blue, bgcolor=c_entry)
        b_sl = box.new(bar_index, entry_price, bar_index + 15, sl_price, border_width=0, bgcolor=c_slBox)
        b_tp = box.new(bar_index, tp_price, bar_index + 15, entry_price, border_width=0, bgcolor=c_tpBuy)

        strategy.entry('Long', strategy.long, comment='SWEEP BUY')
        strategy.exit('Exit Long', 'Long', stop=sl_price, limit=tp_price)

    if sweep_sell and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('Long', comment='REVERSAL')
            box.set_right(b_entry, bar_index)
            box.set_right(b_sl, bar_index)
            box.set_right(b_tp, bar_index)

        entry_price: float = close
        sl_price: float = high + i_slBuffer / 10
        risk_amt: float = sl_price - entry_price
        tp_price: float = entry_price - risk_amt * i_rr

        b_entry = box.new(bar_index, entry_price, bar_index + 15, entry_price, border_width=1, border_color=color.blue, bgcolor=c_entry)
        b_sl = box.new(bar_index, sl_price, bar_index + 15, entry_price, border_width=0, bgcolor=c_slBox)
        b_tp = box.new(bar_index, entry_price, bar_index + 15, tp_price, border_width=0, bgcolor=c_tpSell)

        strategy.entry('Short', strategy.short, comment='SWEEP SELL')
        strategy.exit('Exit Short', 'Short', stop=sl_price, limit=tp_price)

    hud: Persistent[Table] = table.new(position.top_right, 2, 4, bgcolor=color.rgb(20, 20, 20), border_width=1, frame_color=color.white)
    if barstate.islast:
        table.cell(hud, 0, 0, 'KALKI TFXBOT', text_color=color.rgb(229, 207, 15))
        table.cell(hud, 1, 0, 'KALKIC ARTEL CORE', text_color=color.white)
        table.cell(hud, 0, 1, 'ENGINE', text_color=color.white)
        table.cell(hud, 1, 1, 'LIQUIDITY SWEEP', text_color=color.rgb(77, 208, 225))
        table.cell(hud, 0, 2, 'CURRENT R:R', text_color=color.white)
        table.cell(hud, 1, 2, '1 : ' + string.tostring(i_rr), text_color=color.rgb(229, 207, 15))
        table.cell(hud, 0, 3, 'EMA TREND GUARD', text_color=color.white)
        table.cell(hud, 1, 3, 'ACTIVE', text_color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)