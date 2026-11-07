"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, currency, hl2, input, math, nz, plot, script,
    strategy, ta
)
from pynecore.types import Color, Series

StrategyName: str = 'Best Supertrend CCI Strategy'
ShortStrategyName: str = 'Best Supertrend CCI Strategy'


@script.strategy(title=StrategyName, shorttitle=ShortStrategyName, overlay=True, pyramiding=0, default_qty_value=100, precision=7, currency=currency.USD, commission_value=0.2, commission_type=strategy.commission.percent, initial_capital=10000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    source: Series[float] = input(close),
    i_alert_mode=input(defval=alert.freq_once_per_bar_close, title='Alerts Mode', options=(alert.freq_once_per_bar_close, alert.freq_once_per_bar, alert.freq_all)),
    cci_period=input(28, 'CCI Period'),
    ML=input(0, 'CCI Mid Line pivot'),
    Factor=input.float(3, title='[ST] Factor', minval=1, maxval=100),
    Pd=input.int(3, title='[ST] PD', minval=1, maxval=100)
):
    AQUA: Color = color.new('#00FFFF')
    BLUE: Color = color.new('#0000FF')
    RED: Color = color.new('#FF0000')
    LIME: Color = color.new('#00FF00')
    GRAY: Color = color.new('#808080')
    DARKRED: Color = color.new('#8B0000')
    DARKGREEN: Color = color.new('#006400')
    GOLD: Color = color.new('#FFD700')
    WHITE = color.white
    GREEN_LIGHT = color.new(color.green, 40)
    RED_LIGHT = color.new(color.red, 40)
    BLUE_LIGHT = color.new(color.aqua, 40)
    PURPLE_LIGHT = color.new(color.purple, 40)
    cci: Series = ta.cci(source, cci_period)
    def f_supertrend(Factor, Pd):
        __hist_cci__: Series = cci[0]
        Up = hl2 - Factor * ta.atr(Pd)
        Dn = hl2 + Factor * ta.atr(Pd)
        TrendUp: Series[float] = 0.0
        TrendUp = math.max(Up, TrendUp[1]) if __hist_cci__[1] > ML else Up
        TrendDown: Series[float] = 0.0
        TrendDown = math.min(Dn, TrendDown[1]) if __hist_cci__[1] < ML else Dn
        Trend: Series[float] = 0.0
        Trend = 1 if cci > ML else -1 if cci < ML else nz(Trend[1], 1)
        Tsl = TrendUp if Trend == 1 else TrendDown
        return (Trend, Tsl)

    st_trend, st_tsl = f_supertrend(Factor, Pd)
    linecolor = color.green if close >= st_tsl else color.red
    plot(st_tsl, color=linecolor, linewidth=3, title='SuperTrend')
    isLong: Series = st_trend == 1
    isShort: Series = st_trend == -1
    longClose = isLong[1] and isShort
    shortClose = isShort[1] and isLong
    if isLong:
        strategy.entry('Long', strategy.long, alert_message='Long')
    if longClose:
        strategy.close('Long', alert_message='Long Close')
    if isShort:
        strategy.entry('Short', strategy.short, alert_message='Short')
    if shortClose:
        strategy.close('Short', alert_message='Short Close')
    if isLong:
        alert('Long', i_alert_mode)
    if longClose:
        alert('Long Close', i_alert_mode)
    if isShort:
        alert('Short', i_alert_mode)
    if shortClose:
        alert('Short Close', i_alert_mode)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
