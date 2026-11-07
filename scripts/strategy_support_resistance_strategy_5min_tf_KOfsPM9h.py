"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    barstate, close, color, currency, fixnan, high, hour, input, low, minute,
    na, open, plot, script, strategy, ta, time, timeframe, volume
)
from pynecore.types import Persistent


@script.strategy('SUPPORT RESISTANCE STRATEGY [5MIN TF]', overlay=True, commission_type=strategy.cash, commission_value=30, slippage=2, default_qty_value=40, currency=currency.NONE, pyramiding=0, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    L_Bars=input.int(defval=10, minval=1, maxval=50, step=1),
    R_Bars=input.int(defval=15, minval=1, maxval=50, step=1),
    volumeRange=input.int(20, title='Volume Break [threshold]', minval=1),
    EMA1=input.int(title='PRICE CROSS EMA', defval=150, minval=10, maxval=400),
    factor1=input.float(title='_ATR LONG', defval=3.2, minval=1, maxval=5, step=0.1, tooltip='ATR TRAIL LONG'),
    factor2=input.float(title='_ATR SHORT', defval=3.2, minval=1, maxval=5, step=0.1, tooltip='ATR TRAIL SHORT'),
    risk__global__=input.float(title='RISK', defval=200, minval=1, maxval=5000, step=50, tooltip='RISK PER TRADE')
):
    initialCapital: Persistent = strategy.equity
    t = time(timeframe.period, '0915-1445:1234567')
    time_cond = not na(t)
    ema1 = ta.ema(close, EMA1)
    plot(ema1, color=color.new(color.yellow, 0), style=plot.style_linebr, title='ema1')
    ATR_LO = ta.atr(14) * factor1
    ATR_SH = ta.atr(14) * factor2
    long_trail = close - ATR_LO
    short_trail = close + ATR_SH
    Resistance_pi = fixnan(inline_series(ta.pivothigh(L_Bars, R_Bars), 1))
    Support_pi = fixnan(inline_series(ta.pivotlow(L_Bars, R_Bars), 1))
    r1 = plot(Resistance_pi, color=na if cast_bool(ta.change(Resistance_pi)) else color.red, offset=-(R_Bars + 1), linewidth=2, title='RESISTANCE')
    s1 = plot(Support_pi, color=na if cast_bool(ta.change(Support_pi)) else color.green, offset=-(R_Bars + 1), linewidth=2, title='SUPPORT')
    vol_1 = ta.ema(volume, 5)
    vol_2 = ta.ema(volume, 10)
    osc_vol = 100 * (vol_1 - vol_2) / vol_2
    if ta.crossover(close, Resistance_pi) and osc_vol > volumeRange and (not open - low > close - open) and (strategy.opentrades == 0) and barstate.isconfirmed and time_cond and (close >= ema1):
        strategy.entry(id='Long', direction=strategy.long, comment='BUY')
    plot(long_trail, color=color.new(color.blue, 0), style=plot.style_linebr, title='long Stop')
    if strategy.position_size > 0:
        strategy.exit('long tsl', 'Long', stop=long_trail, comment='SELL')
    if ta.crossunder(close, Support_pi) and osc_vol > volumeRange and (not open - close < high - open) and (strategy.opentrades == 0) and barstate.isconfirmed and time_cond and (close <= ema1):
        strategy.entry(id='Short', direction=strategy.short, comment='SELL')
    if strategy.position_size < 0:
        strategy.exit('short tsl', 'Short', stop=short_trail, comment='BUY')
    if hour == 14 and minute == 55:
        strategy.close_all()
    strategy.risk.max_intraday_loss(type=strategy.cash, value=risk__global__)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)