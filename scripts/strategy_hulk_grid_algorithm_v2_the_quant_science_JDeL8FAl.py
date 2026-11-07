"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy(title='Hulk Grid Algorithm V2 [The Quant Science]', overlay=True, initial_capital=10000, commission_type=strategy.commission.percent, commission_value=0.7, pyramiding=10, close_entries_rule='ANY', slippage=5)
def main(
    center_price=input.price(defval=100.0, title="Center Price - Start Grid [$]", group="GRID SETTINGS", confirm=True),
    __input_1__=input.float(defval=0.6, title="Grid Step Level [%]", step=0.1, group="GRID SETTINGS"),
    base_order_usd=input.float(defval=100.0, title="Start Order Price [$]", minval=10, group="POSITION SIZING"),
    __input_3__=input.float(defval=20.0, title="Size Order Decay [%]", step=0.1, group="POSITION SIZING"),
    grid_destroyer=input.bool(defval=False, title='Grid Stop Loss', group="STOP LOSS CONFIGURATION", inline="SL"),
    stop_level=input.price(defval=0.0, title='', group="STOP LOSS CONFIGURATION", inline="SL")
):
    step_percent = __input_1__ / 100
    decay_percent = __input_3__ / 100

    grid_1 = center_price * (1 - step_percent * 5)
    grid_2 = center_price * (1 - step_percent * 4)
    grid_3 = center_price * (1 - step_percent * 3)
    grid_4 = center_price * (1 - step_percent * 2)
    grid_5 = center_price * (1 - step_percent * 1)
    grid_6 = center_price
    grid_7 = center_price * (1 + step_percent * 1)
    grid_8 = center_price * (1 + step_percent * 2)
    grid_9 = center_price * (1 + step_percent * 3)
    grid_10 = center_price * (1 + step_percent * 4)

    take_profit_target = grid_10 * 1.05

    def get_qty(lvl_price: float, grid_index: int):
        usd_amount: float = base_order_usd * math.pow(1.0 - decay_percent, grid_index)
        qty: float = usd_amount / lvl_price if not na(lvl_price) and lvl_price > 0 else 0.0
        return qty

    f1: Persistent[bool] = False
    f2: Persistent[bool] = False
    f3: Persistent[bool] = False
    f4: Persistent[bool] = False
    f5: Persistent[bool] = False
    f6: Persistent[bool] = False
    f7: Persistent[bool] = False
    f8: Persistent[bool] = False
    f9: Persistent[bool] = False
    f10: Persistent[bool] = False

    if strategy.position_size == 0 and strategy.position_size[1] != 0:
        f1 = False
        f2 = False
        f3 = False
        f4 = False
        f5 = False
        f6 = False
        f7 = False
        f8 = False
        f9 = False
        f10 = False

    if not f1:
        strategy.entry('🧪GRID#1', strategy.long, qty=get_qty(grid_1, 0), limit=grid_1 if close > grid_1 else na, stop=grid_1 if close < grid_1 else na)
        f1 = True

    if not f2:
        strategy.entry('🧪GRID#2', strategy.long, qty=get_qty(grid_2, 1), limit=grid_2 if close > grid_2 else na, stop=grid_2 if close < grid_2 else na)
        f2 = True

    if not f3:
        strategy.entry('🧪GRID#3', strategy.long, qty=get_qty(grid_3, 2), limit=grid_3 if close > grid_3 else na, stop=grid_3 if close < grid_3 else na)
        f3 = True

    if not f4:
        strategy.entry('🧪GRID#4', strategy.long, qty=get_qty(grid_4, 3), limit=grid_4 if close > grid_4 else na, stop=grid_4 if close < grid_4 else na)
        f4 = True

    if not f5:
        strategy.entry('🧪GRID#5', strategy.long, qty=get_qty(grid_5, 4), limit=grid_5 if close > grid_5 else na, stop=grid_5 if close < grid_5 else na)
        f5 = True

    if not f6:
        strategy.entry('🧪GRID#6', strategy.long, qty=get_qty(grid_6, 5), limit=grid_6 if close > grid_6 else na, stop=grid_6 if close < grid_6 else na)
        f6 = True

    if not f7:
        strategy.entry('🧪GRID#7', strategy.long, qty=get_qty(grid_7, 6), limit=grid_7 if close > grid_7 else na, stop=grid_7 if close < grid_7 else na)
        f7 = True

    if not f8:
        strategy.entry('🧪GRID#8', strategy.long, qty=get_qty(grid_8, 7), limit=grid_8 if close > grid_8 else na, stop=grid_8 if close < grid_8 else na)
        f8 = True

    if not f9:
        strategy.entry('🧪GRID#9', strategy.long, qty=get_qty(grid_9, 8), limit=grid_9 if close > grid_9 else na, stop=grid_9 if close < grid_9 else na)
        f9 = True

    if not f10:
        strategy.entry('🧪GRID#10', strategy.long, qty=get_qty(grid_10, 9), limit=grid_10 if close > grid_10 else na, stop=grid_10 if close < grid_10 else na)
        f10 = True

    stop_crossed: bool = ta.crossunder(close, stop_level)

    if close >= take_profit_target:
        strategy.close_all(comment='💎💎💎 +5%')
        f1 = False
        f2 = False
        f3 = False
        f4 = False
        f5 = False
        f6 = False
        f7 = False
        f8 = False
        f9 = False
        f10 = False

    if grid_destroyer and stop_crossed:
        strategy.close_all(comment='☄️ Grid Destroyed')
        f1 = False
        f2 = False
        f3 = False
        f4 = False
        f5 = False
        f6 = False
        f7 = False
        f8 = False
        f9 = False
        f10 = False

    p10 = plot(grid_10, 'Grid Top (L10)', color=color.new(color.new('#03FF00'), 30), linewidth=2)
    p9 = plot(grid_9, 'Grid Line 9', color=color.new(color.new('#03FF00'), 70), linewidth=1)
    p8 = plot(grid_8, 'Grid Line 8', color=color.new(color.new('#03FF00'), 75), linewidth=1)
    p7 = plot(grid_7, 'Grid Line 7', color=color.new(color.new('#03FF00'), 80), linewidth=1)
    p6 = plot(grid_6, 'Grid Center (L6)', color=color.new(color.new('#03FF00'), 10), linewidth=2)
    p5 = plot(grid_5, 'Grid Line 5', color=color.new(color.new('#03FF00'), 80), linewidth=1)
    p4 = plot(grid_4, 'Grid Line 4', color=color.new(color.new('#03FF00'), 75), linewidth=1)
    p3 = plot(grid_3, 'Grid Line 3', color=color.new(color.new('#03FF00'), 70), linewidth=1)
    p2 = plot(grid_2, 'Grid Line 2', color=color.new(color.new('#03FF00'), 65), linewidth=1)
    p1 = plot(grid_1, 'Grid Bottom (L1)', color=color.new(color.new('#03FF00'), 30), linewidth=2)

    fill(p10, p9, color=color.new(color.new('#03FF00'), 92), title='Zone 9-10')
    fill(p9, p8, color=color.new(color.new('#03FF00'), 94), title='Zone 8-9')
    fill(p8, p7, color=color.new(color.new('#03FF00'), 95), title='Zone 7-8')
    fill(p7, p6, color=color.new(color.new('#03FF00'), 97), title='Zone 6-7')
    fill(p6, p5, color=color.new(color.new('#03FF00'), 97), title='Zone 5-6')
    fill(p5, p4, color=color.new(color.new('#03FF00'), 95), title='Zone 4-5')
    fill(p4, p3, color=color.new(color.new('#03FF00'), 94), title='Zone 3-4')
    fill(p3, p2, color=color.new(color.new('#03FF00'), 93), title='Zone 2-3')
    fill(p2, p1, color=color.new(color.new('#03FF00'), 92), title='Zone 1-2')

    plot(take_profit_target, 'Take Profit', color=color.new('#03FF00'), linewidth=3, style=plot.style_linebr)
    plot(stop_level if grid_destroyer else na, 'Stop Loss', color=color.new('#FF3B30'), linewidth=2, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
