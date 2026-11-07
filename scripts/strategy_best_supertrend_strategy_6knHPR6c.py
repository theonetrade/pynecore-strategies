"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barmerge, close, color, currency, hl2, input, label, math, na, nz, plot,
    plotshape, request, script, shape, size, strategy, string, syminfo, ta, time, timenow, xloc,
    yloc
)
from pynecore.types import Color, Label, Persistent, Series


@script.strategy(title='BEST Supertrend Strategy', shorttitle='Supertrend Strategy', overlay=True, pyramiding=0, default_qty_value=100, precision=7, currency=currency.USD, commission_value=0.2, commission_type=strategy.commission.percent, initial_capital=1000000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    orderType=input.string('Longs+Shorts', title='What type of Orders', options=('Longs+Shorts', 'LongsOnly', 'ShortsOnly')),
    fastLength=input(7, title='Fast Length SMA'),
    slowLength=input(20, title='Slow Length SMA'),
    Factor=input.float(3, title='[ST] Factor', minval=1, maxval=100),
    Pd=input.int(3, title='[ST] PD', minval=1, maxval=100),
    TF=input.string('daily', title='Supertrend timeframe', options=('daily', 'weekly', 'monthly', 'quartly', 'yearly'))
):
    isLong = orderType != 'ShortsOnly'
    isShort = orderType != 'LongsOnly'
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
    def f_supertrend(Factor, Pd):
        Up = hl2 - Factor * ta.atr(Pd)
        Dn = hl2 + Factor * ta.atr(Pd)
        TrendUp: Series[float] = 0.0
        TrendUp = math.max(Up, TrendUp[1]) if close[1] > TrendUp[1] else Up
        TrendDown: Series[float] = 0.0
        TrendDown = math.min(Dn, TrendDown[1]) if close[1] < TrendDown[1] else Dn
        Trend: Series[float] = 0.0
        Trend = 1 if close > TrendDown[1] else -1 if close < TrendUp[1] else nz(Trend[1], 1)
        Tsl = TrendUp if Trend == 1 else TrendDown
        return Tsl

    st_tsl = f_supertrend(Factor, Pd)
    def f_securitys(_ticker, _source: Series):
        daily = request.security(_ticker, 'D', _source[1], lookahead=barmerge.lookahead_on)
        weekly = request.security(_ticker, 'W', _source[1], lookahead=barmerge.lookahead_on)
        montly = request.security(_ticker, 'M', _source[1], lookahead=barmerge.lookahead_on)
        quarterly = request.security(_ticker, '3M', _source[1], lookahead=barmerge.lookahead_on)
        yearly = request.security(_ticker, '12M', _source[1], lookahead=barmerge.lookahead_on)
        return (daily, weekly, montly, quarterly, yearly)

    st_daily, st_weekly, st_monthly, st_quarterly, st_yearly = f_securitys(syminfo.tickerid, st_tsl)
    lapos_x = timenow + math.round(ta.change(time) * 50)
    lapos_y = close
    down_arrows_text = '▼' + ' ' + '▼' + ' ' + '▼' + ' ' + '▼' + ' ' + '▼' + ' ' + '▼' + ' ' + '▼' + '\n'
    def f_draw_infopanel(_x, _y, _color, _line, _text):
        _rep_text: str = ''
        for _l in pine_range(0, _line, 1):
            _rep_text = _rep_text + '\n'
        _rep_text = _rep_text + _text
        _la: Persistent[Label] = na(Label)
        label.delete(_la)
        _la = label.new(x=_x, y=_y, text=_rep_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.new('#C1CADE'), style=label.style_label_up, textcolor=_color, size=size.normal)
        return _la

    f_draw_infopanel(lapos_x, lapos_y, color.olive, 12, '╚═══════════════════════╝')
    f_draw_infopanel(lapos_x, lapos_y, color.new(color.red, 20), 10, 'Yearly : ' + string.tostring(math.round(st_yearly)))
    f_draw_infopanel(lapos_x, lapos_y, color.new(color.purple, 20), 8, 'Quarterly : ' + string.tostring(math.round(st_quarterly)))
    f_draw_infopanel(lapos_x, lapos_y, color.new(color.green, 20), 6, 'Monthly : ' + string.tostring(math.round(st_monthly)))
    f_draw_infopanel(lapos_x, lapos_y, color.new(color.blue, 20), 4, 'Weekly : ' + string.tostring(math.round(st_weekly)))
    f_draw_infopanel(lapos_x, lapos_y, color.new(color.green, 20), 2, 'Daily : ' + string.tostring(math.round(st_daily)))
    f_draw_infopanel(lapos_x, lapos_y, color.olive, 0, '╔═════ Supertrend (' + string.tostring(Factor) + ',' + string.tostring(Pd) + ') ═════╗')
    IS_DAILY = TF == 'daily'
    IS_WEEKLY = TF == 'weekly'
    IS_MONTHLY = TF == 'monthly'
    IS_QUARTERLY = TF == 'quarterly'
    IS_YEARLY = TF == 'yearly'
    iff_1 = st_yearly if IS_YEARLY else st_daily
    iff_2 = st_quarterly if IS_QUARTERLY else iff_1
    iff_3 = st_monthly if IS_MONTHLY else iff_2
    iff_4 = st_weekly if IS_WEEKLY else iff_3
    st_tsl_TF = st_daily if IS_DAILY else iff_4
    sma_fast = ta.sma(close, fastLength)
    sma_slow = ta.sma(close, slowLength)
    long_exit = ta.crossunder(sma_fast, sma_slow)
    short_exit = ta.crossover(sma_fast, sma_slow)
    curr = 0 - ta.barssince(long_exit) + ta.barssince(short_exit)
    cross_buy = 1 if curr < 0 else 0
    cross_sell = 1 if curr > 0 else 0
    bull = close >= st_tsl_TF and cast_bool(cross_buy)
    bear = close <= st_tsl_TF and cast_bool(cross_sell)
    entry_price = ta.valuewhen(bull or bear, close, 0)
    plot(sma_fast, 'SMA fastLength', color=color.new(color.aqua, 0), linewidth=2)
    plot(sma_slow, 'SMA slowLength', color=color.new(color.purple, 0), linewidth=2)
    plotshape(ta.crossover(sma_fast, sma_slow), color=color.new(color.aqua, 0), style=shape.circle, size=size.small)
    plotshape(ta.crossunder(sma_fast, sma_slow), color=color.new(color.purple, 0), style=shape.circle, size=size.small)
    linecolor = color.green if close >= st_tsl_TF else color.red
    plot(st_tsl_TF, color=linecolor, linewidth=4, title='SuperTrend')
    if isLong:
        if bull:
            strategy.entry('Long', strategy.long)
        if long_exit:
            strategy.close('Long')
    if isShort:
        if bear:
            strategy.entry('Short', strategy.short)
        if short_exit:
            strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
