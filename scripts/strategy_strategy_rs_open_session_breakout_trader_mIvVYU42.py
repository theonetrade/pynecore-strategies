"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, bgcolor, color, currency, fill, high, input, low, math, na, nz,
    open, plot, request, script, strategy, syminfo, ta, time
)
from pynecore.types import Series


class MMODE(Enum):
    FIXED = 'Fixed Value'
    FTRAIL = 'Fixed Trail Value'
    PTRAIL = 'Equity Percent Trail '


TITLE: str = 'Open Session Breakout Trader'
STITLE: str = 'S'


@script.strategy(TITLE, STITLE, overlay=True, default_qty_type=strategy.cash, default_qty_value=1000, initial_capital=100000, currency=currency.USD)
def main(
    trade_session=input.session('0400-0700,0900-1300', 'Trade Session:', tooltip='Use `xxxx-xxxx` or `xxxx-xxxx,xxxx-xxxx` to define a interval'),
    percent_range_multiplier=input.float(0.25, 'Percent Range Multiplier:'),
    close_at_end_of_session=input.bool(False, 'Close trades at the end of the session?'),
    use_margin_call=input.bool(True),
    margin_call_mode=input.enum(MMODE.FIXED, 'Margin call mode:'),
    margin_value=input.float(95000.0, 'Margin Value:'),
    wins_multiplier=input.float(1.0, 'Scaling Multiplier for Consecutive Wins:'),
    losses_multiplier=input.float(2.0, 'Scaling Multiplier for Consecutive Losses:'),
    trade_size=input.float(25.0, 'Base trade value:'),
    trade_leverage=input.float(400.0, 'Base Leverage value:'),
    take_profit=input.float(250.0, 'TP in ticks(1/10 of a pip):'),
    stop_loss=input.float(100.0, 'SL in ticks(1/10 of a pip):'),
    use_trailing_stop=input.bool(False, 'Use Trailing Stop?'),
    trailing_activation=input.float(100.0, 'Trailing activation distance in ticks(1/10 of a pip):'),
    trailing_offset=input.float(250.0, 'Trailing offset in ticks(1/10 of a pip):')
):
    use_trade_session: bool = True
    isinsession: bool = not na(time('1', trade_session)) if use_trade_session else True

    bgcolor(color.new('#9B27B067') if use_trade_session and isinsession else na, title='In Session BG')
    r: float = request.security(syminfo.tickerid, 'D', inline_series(ta.atr(100), 1), barmerge.gaps_off, barmerge.lookahead_off)
    open_price: Series[float] = open
    open_price = open if ta.change(1 if use_trade_session and isinsession else 0) > 0 else open_price[1]
    buy_line: float = open_price + r * percent_range_multiplier
    sel_line: float = open_price - r * percent_range_multiplier

    plot(na if not isinsession else open_price, 'Session Open Price', color.black, 1, plot.style_linebr)
    plot(na if not isinsession else buy_line, 'Buy Line', color.green, 2, plot.style_linebr)
    plot(na if not isinsession else sel_line, 'Sell Line', color.maroon, 2, plot.style_linebr)

    is_new_open: bool = ta.change(open_price) != 0
    buy_on_1st_bar: bool = is_new_open and high > buy_line
    sel_on_1st_bar: bool = is_new_open and low < sel_line

    buy_trigger: Series[bool] = ta.crossover(high, buy_line) or buy_on_1st_bar
    sel_trigger: bool = ta.crossunder(low, sel_line) or sel_on_1st_bar
    if close_at_end_of_session and (not isinsession):
        strategy.close_all()

    def f_account_margin_call(_ammount: float):
        _return: Series[bool] = False
        _return = True if strategy.equity <= _ammount else _return[1]
        return _return

    def f_account_fixed_trail_call(_ammount: float):
        _max_eq: Series[float] = strategy.equity
        _max_eq = strategy.equity if na(_max_eq[1]) else math.max(_max_eq[1], strategy.equity)
        _return: Series[bool] = False
        _return = True if strategy.equity <= _max_eq - _ammount else _return[1]
        return _return

    def f_account_percent_trail_call(_percent: float):
        _max_eq: Series = strategy.equity
        _max_eq = strategy.equity if na(_max_eq[1]) else math.max(_max_eq[1], strategy.equity)
        _return: Series[bool] = False
        _return = True if strategy.equity <= _max_eq * (_percent / 100) else _return[1]
        return _return


    account_margin_call: bool = f_account_margin_call(margin_value)
    account_fixed_trail_call: bool = f_account_fixed_trail_call(margin_value)
    account_percent_trail_call: bool = f_account_percent_trail_call(margin_value)
    __block_result__ = na
    if use_margin_call:
        __block_result_1__ = na
        __switch_1__ = margin_call_mode
        if __switch_1__ == MMODE.FIXED:
            __block_result_1__ = not account_margin_call
        elif __switch_1__ == MMODE.FTRAIL:
            __block_result_1__ = not account_fixed_trail_call
        elif __switch_1__ == MMODE.PTRAIL:
            __block_result_1__ = not account_percent_trail_call
        else:
            __block_result_1__ = False
        __block_result__ = __block_result_1__
    else:
        __block_result__ = True
    trade_if_not_margin_call = __block_result__

    buy_cond: bool = isinsession and trade_if_not_margin_call and buy_trigger and (strategy.opentrades < 1)
    sel_cond: bool = isinsession and trade_if_not_margin_call and sel_trigger and (strategy.opentrades < 1)

    C_LOSSES: int = ta.change(strategy.losstrades)
    C_WINS: int = ta.change(strategy.wintrades)
    C_EVENS: int = ta.change(strategy.eventrades)
    C_OTRADE: int = ta.change(strategy.opentrades)

    def f_martingale_wins_multiplier(_multiplier: float):
        _r: Series[float] = na(float)
        _r = 1 if na(_r[1]) else 1 if C_LOSSES > 0 else _r[1] * _multiplier if C_WINS > 0 or C_EVENS > 0 else _r[1]
        return _r

    def f_martingale_loss_multiplier(_multiplier: float):
        _r: Series[float] = na(float)
        _r = 1 if na(_r[1]) else 1 if C_LOSSES > 0 else _r[1] * _multiplier if C_WINS > 0 or C_EVENS > 0 else _r[1]
        return _r

    mode: Series[int] = na(int)
    mode = 1 if C_WINS > 0 else -1 if C_LOSSES > 0 else nz(mode[1], 1)

    martingale_wins_multiplier: float = f_martingale_wins_multiplier(wins_multiplier)
    martingale_loss_multiplier: float = f_martingale_loss_multiplier(losses_multiplier)
    trade_multiplier: float = martingale_wins_multiplier if mode > 0 else martingale_loss_multiplier
    trade_size_multiplied: float = trade_size * trade_leverage * trade_multiplier

    if buy_cond:
        strategy.entry('B', strategy.long, trade_size_multiplied)
    if sel_cond:
        strategy.entry('S', strategy.short, trade_size_multiplied)
    if use_trailing_stop:
        strategy.exit('B', 'B', profit=take_profit, loss=stop_loss, trail_points=trailing_activation, trail_offset=trailing_offset)
        strategy.exit('S', 'S', profit=take_profit, loss=stop_loss, trail_points=trailing_activation, trail_offset=trailing_offset)
    else:
        strategy.exit('B', 'B', profit=take_profit, loss=stop_loss)
        strategy.exit('S', 'S', profit=take_profit, loss=stop_loss)

    pip_digits_multiplier: float = 1e-05
    trade_open_price: Series[float] = na(float)
    trade_open_price = na(float) if strategy.opentrades == 0 else open if C_OTRADE > 0 else trade_open_price[1]
    trade_loss_price: Series[float] = na(float)
    trade_loss_price = na(float) if strategy.opentrades == 0 else (trade_open_price - stop_loss * math.round(open) * pip_digits_multiplier if buy_trigger[1] else trade_open_price + stop_loss * math.round(open) * pip_digits_multiplier) if C_OTRADE > 0 else trade_loss_price[1]
    trade_profit_price: Series[float] = na(float)
    trade_profit_price = na(float) if strategy.opentrades == 0 else (trade_open_price + take_profit * math.round(open) * pip_digits_multiplier if buy_trigger[1] else trade_open_price - take_profit * math.round(open) * pip_digits_multiplier) if C_OTRADE > 0 else trade_profit_price[1]

    t_o = plot(trade_open_price, 'Trade Open Price Line', color.black, 1, plot.style_linebr)
    t_l = plot(trade_loss_price, 'Trade Loss Price Line', color.black, 1, plot.style_linebr)
    t_p = plot(trade_profit_price, 'Trade Profit Price Line', color.black, 1, plot.style_linebr)
    fill(t_o, t_l, color=color.new(color.red, 80), title='Trade Loss Fill')
    fill(t_o, t_p, color=color.new(color.lime, 80), title='Trade Profit Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
