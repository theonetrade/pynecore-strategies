"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, location, low, math, open, plot, plotshape,
    script, shape, strategy, syminfo, ta
)
from pynecore.types import Series


@script.strategy('PURE MORNING 2.0', overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, slippage=1, backtest_fill_limits_assumption=1, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    __input_0__=input.float(defval=0.09, title='MDS Tolerance', group='DOJI SETTINGS', minval=0.01, maxval=1, step=0.01),
    __input_1__=input.float(defval=0.05, title='DOJI Tolerance', group='DOJI SETTINGS', minval=0.01, maxval=1, step=0.01),
    xl_tp_percent=input.float(9, step=0.5, title='Take Profit', group='EXIT LONG'),
    sl_type_ll=input.bool(True, 'SL type Lowest Low', group='EXIT LONG'),
    sl_len=input.int(100, 'Stop Length', group='EXIT LONG'),
    max_loss_filter=input.bool(False, 'Max Loss Filter', group='Filter'),
    filter_percent=input.int(10, 'Max Loss %', group='Filter'),
    sl_type_percent=input.bool(False, 'SL type Percent', group='EXIT LONG'),
    xl_sl_percent=input.float(2, step=0.5, title='Stop Loss', group='EXIT LONG'),
    xl_ts_percent=input.float(1, step=0.5, title='Trailing theshold', group='TRAILING STOP'),
    xl_to_percent=input.float(0.5, step=0.5, title='Trailing offset', group='TRAILING STOP')
):
    rma = ta.rma(close, 60)
    mfi = ta.mfi(close, 10)
    rsi = ta.rsi(close, 14)
    atr7 = ta.atr(7)
    ema60 = ta.ema(close, 60)
    plot(ema60, 'EMA 60', color.new(color.aqua, 0))
    range1: Series = high - low
    tolerance = __input_0__ / 100
    candle1 = math.abs(close[2] - open[2]) / range1[2] > 0.6 and close[2] < open[2]
    candle2 = open[1] > close[1] and open[1] < close[1] * (1 + tolerance) or (open[1] < close[1] and open[1] > close[1] * (1 - tolerance) and (close[1] < close[2] + range1[2]))
    candle3 = close > open and close > close[2] + range1[2]
    MDS = candle1 and candle2 and candle3
    plotshape(MDS and close > ema60, text='MD', textcolor=color.yellow, offset=-1, location=location.abovebar, color=color.green, style=shape.triangleup)
    plotshape(MDS and close < ema60, text='MD', textcolor=color.olive, offset=-1, location=location.belowbar, color=color.red, style=shape.triangledown)
    tolerance1 = __input_1__ / 100
    Is_OC_Equal = open > close and open < close * (1 + tolerance1) or (open < close and open > close * (1 - tolerance1))
    plotshape(Is_OC_Equal and close < ema60, text='D', textcolor=color.red, location=location.belowbar, color=color.red)
    plotshape(Is_OC_Equal and close > ema60, text='D', textcolor=color.green, location=location.abovebar, color=color.green)
    filter_stop = close - ta.lowest(low, sl_len) < close * filter_percent / 100 if max_loss_filter == True else True
    if sl_type_percent == True:
        sl_type_ll = False
    ema_1 = ta.ema(close, 60)
    el_cond = Is_OC_Equal and close > ema_1 and filter_stop
    ema_2 = ta.ema(close, 60)
    el_cond_02 = MDS and close > ema_2 and filter_stop
    mess = '!buy ' + syminfo.ticker
    if el_cond:
        strategy.entry('EL', strategy.long, alert_message=mess, comment='EL cond 1')
    plotshape(el_cond and strategy.position_size == 0, 'el_long', shape.circle, color=color.green)
    if el_cond_02:
        strategy.entry('EL', strategy.long, alert_message=mess, comment='EL cond 2')
    plotshape(el_cond_02 and strategy.position_size == 0, 'el_long_02', shape.circle, color=color.green)
    xl_sl_price = strategy.position_avg_price * (1 - xl_sl_percent / 100)
    xl_tp_price = strategy.position_avg_price * (1 + xl_tp_percent / 100)
    if sl_type_ll == True:
        xl_sl_price = ta.lowest(low, sl_len)
    xl_ts_tick = xl_ts_percent * close / syminfo.mintick / 100
    xl_to_tick = xl_to_percent * close / syminfo.mintick / 100
    mess_sell = '!sell ' + syminfo.ticker
    strategy.exit('XL+SL/TP', 'EL', stop=xl_sl_price, limit=xl_tp_price, trail_points=xl_ts_tick, trail_offset=xl_to_tick, comment_loss='STOP', comment_profit='PROFIT', comment_trailing='TS', alert_message=mess_sell)
    xl_cond = ta.crossover(mfi, 90)
    if xl_cond:
        strategy.close('XL', alert_message=mess_sell)
    plotshape(xl_cond, 'xl_cond', shape.circle, color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
