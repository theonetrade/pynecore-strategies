"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, fixnan, high, input, label, line, low, na,
    script, size, strategy, syminfo, ta
)
from pynecore.types import Persistent


@script.strategy(title="Smart Money Pivot Strategy [Jason Kasei]", shorttitle="SM Pivot", overlay=True, margin_long=0, margin_short=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, process_orders_on_close=True, initial_capital=10000)
def main(
    enable_long_strategy=input.bool(True, title='Enable Long Strategy', inline='1'),
    long_stoploss_value=input.float(defval=1, title='Long SL %', minval=0.1, inline='2'),
    long_takeprofit_value=input.float(defval=1.5, title='Long TP %', minval=0.1, inline='2'),
    enable_short_strategy=input.bool(True, title='Enable Short Strategy', inline='3'),
    short_stoploss_value=input.float(defval=1, title='Short SL %', minval=0.1, inline='4'),
    short_takeprofit_value=input.float(defval=1.5, title='Short TP %', minval=0.1, inline='4'),
    period=input.int(20, 'Length', group='Smart Money Pivot'),
    BullBase=input.color(color.new('#00BCD4'), title="Bull", inline="1", group='Smart Money Pivot'),
    BearBase=input.color(color.new('#FF9800'), title="Bear", inline="1", group='Smart Money Pivot')
):
    long_stoploss_percentage = close * (long_stoploss_value / 100) / syminfo.mintick
    long_takeprofit_percentage = close * (long_takeprofit_value / 100) / syminfo.mintick
    short_stoploss_percentage = close * (short_stoploss_value / 100) / syminfo.mintick
    short_takeprofit_percentage = close * (short_takeprofit_value / 100) / syminfo.mintick

    long_stoploss_price = strategy.position_avg_price * (1 - long_stoploss_value / 100)
    long_takeprofit_price = strategy.position_avg_price * (1 + long_takeprofit_value / 100)
    short_stoploss_price = strategy.position_avg_price * (1 + short_stoploss_value / 100)
    short_takeprofit_price = strategy.position_avg_price * (1 - short_takeprofit_value / 100)

    UpdatedHigh: Persistent[float] = na(float)
    UpdatedLow: Persistent[float] = na(float)
    HighIndex: Persistent[int] = na(int)
    phActive: Persistent[bool] = False
    plActive: Persistent[bool] = False
    LowIndex: Persistent[int] = na(int)
    Sync: int = bar_index
    BUY: bool = False
    SELL: bool = False

    neon_bull = color.new(BullBase, 0)
    neon_bull_glow = color.new(BullBase, 75)
    neon_bear = color.new(BearBase, 0)
    neon_bear_glow = color.new(BearBase, 75)

    CandleType: bool = 'Wicks' == 'Wicks'

    PH = ta.pivothigh(high, period, period)
    PL = ta.pivotlow(low, period, period)
    ScrHigh = high if CandleType else close
    ScrLow = low if CandleType else close

    if ta.change(fixnan(PH)) != 0:
        UpdatedHigh = PH
        phActive = True
        HighIndex = Sync - period

    if ta.change(fixnan(PL)) != 0:
        UpdatedLow = PL
        plActive = True
        LowIndex = Sync - period

    if ScrHigh > UpdatedHigh and phActive:
        BUY = True
        phActive = False

    if ScrLow < UpdatedLow and plActive:
        SELL = True
        plActive = False

    LongSMB = BUY
    ShortSMB = SELL

    if LongSMB and enable_long_strategy and (strategy.position_size <= 1):
        strategy.entry('Long', strategy.long, alert_message='Long Entry')
        strategy.exit('Long', from_entry='Long', loss=long_stoploss_percentage, profit=long_takeprofit_percentage, alert_loss='Long SL', alert_profit='Long TP', comment_loss='Long SL', comment_profit='Long TP')

    if ShortSMB and enable_short_strategy and (strategy.position_size >= -1):
        strategy.entry('Short', strategy.short, alert_message='Short Entry')
        strategy.exit('Short', from_entry='Short', loss=short_stoploss_percentage, profit=short_takeprofit_percentage, alert_loss='Short SL', alert_profit='Short TP', comment_loss='Short SL', comment_profit='Short TP')

    style = line.style_solid

    if BUY:
        line.new(HighIndex, UpdatedHigh, bar_index, UpdatedHigh, color=neon_bull, style=line.style_solid, width=1)
        line.new(HighIndex, UpdatedHigh + syminfo.mintick, bar_index, UpdatedHigh + syminfo.mintick, color=neon_bull_glow, style=line.style_solid, width=5)
        line.new(HighIndex, UpdatedHigh - syminfo.mintick, bar_index, UpdatedHigh - syminfo.mintick, color=neon_bull_glow, style=line.style_solid, width=5)
        label.new(x=HighIndex + (bar_index - HighIndex) / 2, y=UpdatedHigh + syminfo.mintick * 5, text='BoS PH', color=color.new(BullBase, 75), textcolor=BullBase, style=label.style_none, size=size.tiny)

    if SELL:
        line.new(LowIndex, UpdatedLow, bar_index, UpdatedLow, color=neon_bear, style=line.style_solid, width=1)
        line.new(LowIndex, UpdatedLow + syminfo.mintick, bar_index, UpdatedLow + syminfo.mintick, color=neon_bear_glow, style=line.style_solid, width=5)
        line.new(LowIndex, UpdatedLow - syminfo.mintick, bar_index, UpdatedLow - syminfo.mintick, color=neon_bear_glow, style=line.style_solid, width=5)
        label.new(x=LowIndex + (bar_index - LowIndex) / 2, y=UpdatedLow - syminfo.mintick * 5, text='BoS PL', color=color.new(BearBase, 75), textcolor=BearBase, style=label.style_none, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)