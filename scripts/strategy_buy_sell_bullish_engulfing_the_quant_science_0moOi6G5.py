"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, currency, input, location, math, na, open,
    plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Persistent, Series

t_ordersize: str = "Percentage size of each order calculated based on starting initial capital."
trend_rule_1: str = "SMA50"
trend_rule_2: str = "SMA50, SMA200"


@script.strategy("Buy&Sell Bullish Engulfing Strategy [The Quant Science]", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=1, currency=currency.USDT, initial_capital=10000, commission_type=strategy.commission.percent, commission_value=0.07, process_orders_on_close=True, close_entries_rule="ANY")
def main(
    profit=input.float(2.0, title="Target profit [%]", minval=0, step=0.1, group="Settings"),
    stoploss=input.float(2.0, title="Stop Loss [%]", minval=0, step=0.1, group="Settings"),
    orders_size=input.float(30.0, title="Position Order Size [%]", minval=0.1, maxval=100, step=0.1, group="Settings", tooltip=t_ordersize),
    show_bg=input.bool(True, title="Highlight Pattern Background", group="Design Settings"),
    color_bull=input.color(color.rgb(59, 255, 69), title="Color: Bullish Signal", group="Design Settings"),
    color_bg=input.color(color.new(color.rgb(59, 255, 69), 85), title="Background Color Pattern", group="Design Settings"),
    trend_rule=input.string(trend_rule_1, title="Detect Trends Based On", options=(trend_rule_1, trend_rule_2, "No detection"), group="Design Settings")
):
    equity_trades: Persistent[float] = strategy.initial_capital
    qty_order = equity_trades * orders_size / 100 / close

    c_down_trend: bool = True
    c_up_trend: bool = True

    if trend_rule == trend_rule_1:
        price_avg = ta.sma(close, 50)
        c_down_trend = close < price_avg
        c_up_trend = close > price_avg
    elif trend_rule == trend_rule_2:
        sma200 = ta.sma(close, 200)
        sma50 = ta.sma(close, 50)
        c_down_trend = close < sma50 and sma50 < sma200
        c_up_trend = close > sma50 and sma50 > sma200

    c_len: int = 14
    c_shadow_percent: float = 5.0

    c_body_hi = math.max(close, open)
    c_body_lo = math.min(close, open)
    c_body = c_body_hi - c_body_lo
    c_body_avg = ta.ema(c_body, c_len)

    c_small_body: Series = c_body < c_body_avg
    c_long_body = c_body > c_body_avg
    c_white_body = open < close
    c_black_body: Series = open > close

    engulfing_bullish = c_down_trend and c_white_body and c_long_body and c_black_body[1] and c_small_body[1] and (close >= open[1]) and (open <= close[1]) and (close > open[1] or open < close[1])

    equity: Persistent[float] = 0.0
    o_price: Persistent[float] = 0.0
    c_exit: Persistent[float] = 0.0
    c_stopl: Persistent[float] = 0.0

    if engulfing_bullish and strategy.opentrades == 0:
        equity = strategy.equity
        o_price = close
        c_exit = equity + equity * profit / 100
        c_stopl = equity - equity * stoploss / 100
        strategy.entry('#ENTRY', strategy.long, qty=qty_order, limit=o_price)

    if ta.crossover(strategy.equity, c_exit):
        strategy.exit('#TP', from_entry='#ENTRY', limit=close)

    if ta.crossunder(strategy.equity, c_stopl):
        strategy.exit('#SL', from_entry='#ENTRY', limit=close)

    plotshape(engulfing_bullish and strategy.opentrades == 0, title='Bullish Engulfing Detection', style=shape.triangledown, location=location.abovebar, color=color_bull, size=size.tiny, text='BULLISH ENGULFING', textcolor=color_bull)

    bgcolor(color_bg if show_bg and engulfing_bullish and (strategy.opentrades == 0) else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
