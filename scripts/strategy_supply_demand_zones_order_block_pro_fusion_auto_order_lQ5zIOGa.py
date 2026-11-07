"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, box, close, color, high, input, label,
    location, low, math, na, nz, open, plot, plotshape, script, shape, size, strategy, syminfo, ta,
    volume
)
from pynecore.types import Persistent, Series


@script.strategy('Supply & Demand Zones + Order Block (Pro Fusion) - Auto Order', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    length=input.int(20, title='Swing Lookback Period', minval=5),
    zone_padding=input.float(0.5, title='Zone Padding (in price)', minval=0.1),
    max_zones=input.int(3, title='Max Zones to Display', minval=1),
    show_signals=input.bool(True, title='Show Breakout Signals'),
    show_ema=input.bool(True, title='Show EMA 50'),
    periods=input.int(5, title='Order Block Periods'),
    threshold=input.float(0.0, title='Min % Move for OB', step=0.1),
    usewicks=input.bool(False, 'Use Wick Range for OB'),
    len_fast=input.float(8, minval=1, title='Fast Line'),
    len_slow=input.float(10, minval=1, title='Slow Line'),
    len_macd_smooth=input.float(8, minval=1, title='Smoothness')
):
    ema50 = ta.ema(close, 50)
    plot(ema50 if show_ema else na, color=color.orange, linewidth=2, title='EMA 50')
    trendUp = close > ema50
    trendDown = close < ema50
    def isStrongHigh(i):
        return high[i] > high[i - 1] and high[i] > high[i + 1] and (high[i] > high[i - 2]) and (high[i] > high[i + 2])

    def isStrongLow(i):
        return low[i] < low[i - 1] and low[i] < low[i + 1] and (low[i] < low[i - 2]) and (low[i] < low[i + 2])

    demandLevels: Persistent[list[float]] = array.new_float()
    supplyLevels: Persistent[list[float]] = array.new_float()
    if bar_index > length:
        for i in pine_range(2, length, 1):
            if isStrongLow(i):
                array.unshift(demandLevels, low[i])
                label.new(x=bar_index - i, y=low[i], text='Demand', style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)
            if isStrongHigh(i):
                array.unshift(supplyLevels, high[i])
                label.new(x=bar_index - i, y=high[i], text='Supply', style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)
    latest_demand = array.get(demandLevels, 0) if array.size(demandLevels) > 0 else na
    latest_supply = array.get(supplyLevels, 0) if array.size(supplyLevels) > 0 else na
    volumeSpike = volume > ta.sma(volume, 20) * 1.5
    bullish_breakout = not na(latest_demand) and low <= latest_demand and (close > latest_demand) and trendUp and volumeSpike
    bearish_breakout = not na(latest_supply) and high >= latest_supply and (close < latest_supply) and trendDown and volumeSpike
    sl_level: Persistent[float] = na(float)
    trailing_start: Persistent[float] = na(float)
    trailing_sl: Persistent[float] = na(float)
    sl_pips = 1000 * syminfo.mintick
    trail_start_pips = 2000 * syminfo.mintick
    long_trade = bullish_breakout
    short_trade = bearish_breakout
    if long_trade:
        sl_level = close - sl_pips
        trailing_start = close + trail_start_pips
        trailing_sl = na
    if short_trade:
        sl_level = close + sl_pips
        trailing_start = close - trail_start_pips
        trailing_sl = na
    if not na(trailing_start):
        if long_trade and close > trailing_start:
            trailing_sl = math.max(close - sl_pips if na(trailing_sl) else trailing_sl, close - sl_pips)
        if short_trade and close < trailing_start:
            trailing_sl = math.min(close + sl_pips if na(trailing_sl) else trailing_sl, close + sl_pips)
    plot(sl_level, color=color.red, title='Stop Loss', style=plot.style_linebr, linewidth=2)
    plot(trailing_sl, color=color.blue, title='Trailing SL', style=plot.style_linebr, linewidth=2)
    plotshape(show_signals and bullish_breakout, title='Strong Buy', location=location.belowbar, color=color.lime, style=shape.labelup, text='BUY')
    plotshape(show_signals and bearish_breakout, title='Strong Sell', location=location.abovebar, color=color.red, style=shape.labeldown, text='SELL')
    if bullish_breakout:
        strategy.entry('Buy', strategy.long)
        strategy.exit('TP/SL', from_entry='Buy', stop=sl_level, trail_price=trailing_sl)
    if bearish_breakout:
        strategy.entry('Sell', strategy.short)
        strategy.exit('TP/SL', from_entry='Sell', stop=sl_level, trail_price=trailing_sl)
    tpBase: float = 20.0
    alertcondition(bullish_breakout, title='Breakout Buy Alert', message='Strong BUY breakout from demand zone')
    alertcondition(bearish_breakout, title='Breakout Sell Alert', message='Strong SELL breakout from supply zone')
    ob_period = periods + 1
    absmove = math.abs(close[ob_period] - close[1]) / close[ob_period] * 100
    relmove = absmove >= threshold
    bullishOB = close[ob_period] < open[ob_period]
    bearishOB = close[ob_period] > open[ob_period]
    upcandles: int = 0
    for i in pine_range(1, periods, 1):
        upcandles = upcandles + (1 if close[i] > open[i] else 0)
    OB_bull = bullishOB and upcandles == periods and relmove
    OB_bull_high = (high[ob_period] if usewicks else open[ob_period]) if OB_bull else na
    OB_bull_low = low[ob_period] if OB_bull else na
    downcandles: int = 0
    for i in pine_range(1, periods, 1):
        downcandles = downcandles + (1 if close[i] < open[i] else 0)
    OB_bear = bearishOB and downcandles == periods and relmove
    OB_bear_high = high[ob_period] if OB_bear else na
    OB_bear_low = (low[ob_period] if usewicks else open[ob_period]) if OB_bear else na
    plotshape(OB_bull, title='Bullish OB', style=shape.triangleup, color=color.green, location=location.belowbar, offset=-ob_period, size=size.tiny)
    plotshape(OB_bear, title='Bearish OB', style=shape.triangledown, color=color.red, location=location.abovebar, offset=-ob_period, size=size.tiny)
    if OB_bull:
        box.new(left=bar_index - ob_period, right=bar_index + 50, top=OB_bull_high, bottom=OB_bull_low, border_color=color.green, bgcolor=color.new(color.green, 85))
        label.new(x=bar_index - ob_period, y=OB_bull_high, text='Order Block (Bullish)', style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)
    if OB_bear:
        box.new(left=bar_index - ob_period, right=bar_index + 50, top=OB_bear_high, bottom=OB_bear_low, border_color=color.red, bgcolor=color.new(color.red, 85))
        label.new(x=bar_index - ob_period, y=OB_bear_low, text='Order Block (Bearish)', style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)
    p: Series = close
    f1 = 1.414 * 3.14159 / len_fast
    a = math.exp(-f1)
    c2 = 2 * a * math.cos(f1)
    c3 = -a * a
    c1 = 1 - c2 - c3
    ssmooth: Series[float] = 0.0
    ssmooth = c1 * (p + p[1]) * 0.5 + c2 * nz(ssmooth[1]) + c3 * nz(ssmooth[2])
    f2 = 1.414 * 3.14159 / len_slow
    a2 = math.exp(-f2)
    c22 = 2 * a2 * math.cos(f2)
    c32 = -a2 * a2
    c12 = 1 - c22 - c32
    ssmooth2: Series[float] = 0.0
    ssmooth2 = c12 * (p + p[1]) * 0.5 + c22 * nz(ssmooth2[1]) + c32 * nz(ssmooth2[2])
    macd: Series = (ssmooth - ssmooth2) * 10000000
    f3 = 1.414 * 3.14159 / len_macd_smooth
    a3 = math.exp(-f3)
    c23 = 2 * a3 * math.cos(f3)
    c33 = -a3 * a3
    c13 = 1 - c23 - c33
    ssmooth3: Series[float] = 0.0
    ssmooth3 = c13 * (macd + macd[1]) * 0.5 + c23 * nz(ssmooth3[1]) + c33 * nz(ssmooth3[2])
    buy = ta.crossover(macd, ssmooth3)
    sell = ta.crossunder(macd, ssmooth3)
    plotshape(buy, title='BUY', text='Buy', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, size=size.tiny)
    plotshape(sell, title='SELL', text='Sell', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, size=size.tiny)
    alertcondition(buy, title='Alış!', message='Alış Zamanı')
    alertcondition(sell, title='Satış', message='Satış Zamanı')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
