"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barmerge, close, color, currency, high, hl2, input, low, math, na, nz,
    plot, request, script, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title='Tripple super Trend Strategy', shorttitle='Triple ST Strat', overlay=True, pyramiding=0, max_bars_back=5000, calc_on_order_fills=False, commission_type=strategy.commission.percent, commission_value=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=5000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    FromMonth=input.int(defval=1, title='FromMonth', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='FromDay', minval=1, maxval=31),
    FromYear=input.int(defval=2020, title='FromYear', minval=2016),
    ToMonth=input.int(defval=1, title='ToMonth', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='ToDay', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='ToYear', minval=2017),
    res=input.timeframe(title='EMA Timeframe', defval='15'),
    len1=input(title='EMA Length', defval=200),
    smoothK=input.int(3, minval=1),
    smoothD=input.int(3, minval=1),
    lengthRSI=input.int(14, minval=1),
    lengthStoch=input.int(14, minval=1),
    src: Series[float] = input(close, title='RSI Source'),
    overSold=input(28),
    overBought=input(78),
    changeATR=input(title='Change ATR Calculation Method?', defval=True),
    src1: Series[float] = input(hl2, title='Source'),
    Periods1=input(title='ATR Period1', defval=10),
    Multiplier1=input.float(title='ATR Multiplier1', step=0.1, defval=1.0),
    Periods2=input(title='ATR Period2', defval=11),
    Multiplier2=input.float(title='ATR Multiplier2', step=0.1, defval=2.0),
    Periods3=input(title='ATR Period3', defval=12),
    Multiplier3=input.float(title='ATR Multiplier3', step=0.1, defval=3.0),
    enablelong=input(True, title='Enable long?'),
    enableshort=input(True, title='Enable short?'),
    profitfactorlong=input.float(title='ProfitfactorLong', step=0.1, defval=2),
    loLen=input.int(title='Lowest Low Lookback', defval=30, minval=2),
    profitfactorshort=input.float(title='ProfitfactorShort', step=0.1, defval=1.5),
    highLen=input.int(title='highest high lookback', defval=25, minval=2)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    afterStartDate = True if time >= start and time <= finish else False
    emasrc = close
    col1 = color.yellow
    ema1 = ta.ema(emasrc, len1)
    emaSmooth = request.security(syminfo.tickerid, res, ema1, barmerge.gaps_on, barmerge.lookahead_off)
    plot(emaSmooth, title='EMA', linewidth=1, color=color.new(col1, 0))
    rsi1 = ta.rsi(src, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d: Series = ta.sma(k, smoothD)
    atr2 = ta.sma(ta.tr, Periods1)
    atr = ta.atr(Periods1) if changeATR else atr2
    up: Series = src1 - Multiplier1 * atr
    up1 = nz(up[1], up)
    up = math.max(up, up1) if close[1] > up1 else up
    dn: Series = src1 + Multiplier1 * atr
    dn1 = nz(dn[1], dn)
    dn = math.min(dn, dn1) if close[1] < dn1 else dn
    trend: Series[int] = 1
    trend = nz(trend[1], trend)
    trend = 1 if trend == -1 and close > dn1 else -1 if trend == 1 and close < up1 else trend
    upPlot = plot(up if trend == 1 else na, title='Up Trend', linewidth=2, color=color.new(color.green, 0))
    dnPlot = plot(na if trend == 1 else dn, title='Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    atr3 = ta.sma(ta.tr, Periods2)
    atr4 = ta.atr(Periods2) if changeATR else atr3
    up2: Series = src1 - Multiplier2 * atr4
    up3 = nz(up2[1], up2)
    up2 = math.max(up2, up3) if close[1] > up3 else up2
    dn2: Series = src1 + Multiplier2 * atr4
    dn3 = nz(dn2[1], dn2)
    dn2 = math.min(dn2, dn3) if close[1] < dn3 else dn2
    trend1: Series[int] = 1
    trend1 = nz(trend1[1], trend1)
    trend1 = 1 if trend1 == -1 and close > dn3 else -1 if trend1 == 1 and close < up3 else trend1
    upPlot1 = plot(up2 if trend1 == 1 else na, title='Up Trend 1', linewidth=2, color=color.new(color.green, 0))
    dnPlot1 = plot(na if trend1 == 1 else dn2, title='Down Trend 1', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    atr5 = ta.sma(ta.tr, Periods3)
    atr6 = ta.atr(Periods3) if changeATR else atr5
    up4: Series = src1 - Multiplier3 * atr6
    up5 = nz(up4[1], up4)
    up4 = math.max(up4, up5) if close[1] > up5 else up4
    dn4: Series = src1 + Multiplier3 * atr6
    dn5 = nz(dn4[1], dn4)
    dn4 = math.min(dn4, dn5) if close[1] < dn5 else dn4
    trend2: Series[int] = 1
    trend2 = nz(trend2[1], trend2)
    trend2 = 1 if trend2 == -1 and close > dn5 else -1 if trend2 == 1 and close < up5 else trend2
    upPlot2 = plot(up4 if trend2 == 1 else na, title='Up Trend 2', linewidth=2, color=color.new(color.green, 0))
    dnPlot2 = plot(na if trend2 == 1 else dn4, title='Down Trend 2', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    trendvalue = trend1 - close + trend - close + trend2 - close
    emaconditionlong = close > emaSmooth
    crossup = k > d and k[1] <= d[1]
    oversoldcondition = k < overSold
    overboughtcondition = k > overBought
    twolinesunderprice = close > trend1 and cast_bool(trend2) or (cast_bool(trend) and cast_bool(trend1)) or (cast_bool(trend) and cast_bool(trend2))
    alllinesunderprice = close > trend and cast_bool(trend1) and cast_bool(trend2)
    longcondition1 = emaconditionlong and crossup and oversoldcondition and alllinesunderprice
    longcondition2 = emaconditionlong and crossup and oversoldcondition and twolinesunderprice
    if longcondition1 and afterStartDate and (strategy.opentrades < 1) and (enablelong == True):
        strategy.entry('long1', strategy.long)
    if longcondition2 and afterStartDate and (strategy.opentrades < 1) and (enablelong == True):
        strategy.entry('long2', strategy.long)
    emaconditionshort = close < emaSmooth
    crossdown = k < d and k[1] >= d[1]
    twolinesoverprice = close < trend1 and cast_bool(trend2) or (cast_bool(trend) and cast_bool(trend1)) or (cast_bool(trend) and cast_bool(trend2))
    alllinesoverprice = close < trend and cast_bool(trend1) and cast_bool(trend2)
    shortcondition1 = emaconditionshort and crossdown and overboughtcondition and twolinesoverprice
    shortcondition2 = emaconditionshort and crossdown and overboughtcondition and alllinesoverprice
    if enableshort == True and shortcondition1 and afterStartDate and (strategy.opentrades < 1):
        strategy.entry('short1', strategy.short)
    if enableshort == True and shortcondition2 and afterStartDate and (strategy.opentrades < 1):
        strategy.entry('short2', strategy.short)
    bought = strategy.position_size[1] < strategy.position_size
    sold = strategy.position_size[1] > strategy.position_size
    stop_level_long: Series = ta.lowest(low, loLen)
    barsboughtlong = ta.barssince(bought)
    if strategy.position_size > 0 and strategy.position_entry_name == 'long1' or strategy.position_entry_name == 'long2':
        profit_level_long = strategy.position_avg_price + (strategy.position_avg_price - stop_level_long[barsboughtlong]) * profitfactorlong
        strategy.exit(id='TP/ SL', stop=stop_level_long[barsboughtlong], limit=profit_level_long)
    stop_level_short: Series = ta.highest(high, highLen)
    barsboughtshort = ta.barssince(sold)
    if strategy.position_size < 0 and strategy.position_entry_name == 'short1' or strategy.position_entry_name == 'short2':
        profit_level_short = strategy.position_avg_price - (stop_level_short[barsboughtshort] - strategy.position_avg_price) * profitfactorshort
        strategy.exit(id='TP/ SL', stop=stop_level_short[barsboughtshort], limit=profit_level_short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
