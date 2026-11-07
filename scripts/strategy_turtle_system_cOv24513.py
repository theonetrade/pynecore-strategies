"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, close, color, fill, high, input, low, math, na, plot,
    plotarrow, plotshape, script, shape, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy(title='Turtle Strategy', overlay=True, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.0, pyramiding=100, process_orders_on_close=True, calc_on_every_tick=True, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    stopInput=input.float(2, 'Stop N', step=0.05),
    riskPercent=input.float(0.01, 'Risk % of capital', step=0.0025),
    pyramidInput=input.float(0.5, 'Pyramid N', step=0.05),
    maxUnits=input.int(5, 'Max Pyramid Units', step=1),
    atrPeriod=input(14, 'ATR period'),
    l1LongInput=input.int(20, 'L1 Long', minval=2),
    l2LongInput=input.int(55, 'L2 Long', minval=2),
    l1LongExitInput=input.int(10, 'L1 Long Exit', minval=2),
    l2LongExitInput=input.int(20, 'L2 Long Exit', minval=2),
    FromYear=input.int(2012, 'From Year', minval=1900),
    FromMonth=input.int(1, 'From Month', minval=1, maxval=12),
    FromDay=input.int(1, 'From Day', minval=1, maxval=31),
    ToYear=input.int(9999, 'To Year', minval=1900),
    ToMonth=input.int(1, 'To Month', minval=1, maxval=12),
    ToDay=input.int(1, 'To Day', minval=1, maxval=31)
):
    l1LongInput: int = 10
    l2LongInput: int = 20
    l1LongExitInput: int = 20
    l2LongExitInput: int = 40
    l1LongInput = input.int(20, 'L1 Long', minval=2)
    l2LongInput = input.int(55, 'L2 Long', minval=2)
    l1LongExitInput = input.int(10, 'L1 Long Exit', minval=2)
    l2LongExitInput = input.int(20, 'L2 Long Exit', minval=2)
    FromDate = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    ToDate = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def TradeDateIsAllowed():
        return time >= FromDate and time <= ToDate

    l1Long: Series = ta.highest(l1LongInput)
    l1LongExit: Series = ta.lowest(l1LongExitInput)
    l2Long: Series = ta.highest(l2LongInput)
    l2LongExit: Series = ta.lowest(l2LongExitInput)
    win: Series[bool] = False
    buyPrice: Series[float] = 0.0
    nextBuyPrice: Series[float] = 0.0
    stopPrice: Series[float] = na(float)
    totalBuys: Series[int] = 0
    inBuy: Series[bool] = False
    l1LongPlot: Series[float] = ta.highest(l1LongInput)
    l2LongPlot: Series[float] = ta.highest(l2LongInput)
    n: float = ta.atr(atrPeriod)
    mode: Series[str] = 'L1'
    fake: Series[bool] = na(bool)
    longLevel: str = na(str)
    capitalLeft: Series[float] = strategy.initial_capital
    shares: Persistent[int] = 0
    fakeBuyPrice: Series[float] = 0.0
    buyPrice = buyPrice[1]
    totalBuys = totalBuys[1]
    nextBuyPrice = nextBuyPrice[1]
    stopPrice = stopPrice[1]
    win = win[1]
    capitalLeft = capitalLeft[1]
    inBuy = inBuy[1]
    n = ta.atr(atrPeriod)
    fakeBuyPrice = fakeBuyPrice[1]
    if not inBuy[1] and (high > l1Long[1] or high > l2Long[1]):
        inBuy = True
    else:
        inBuy = False if inBuy[1] and low < stopPrice[1] else inBuy
        inBuy = False if inBuy[1] and mode[1] == 'L1' and (low < l1LongExit[1]) else inBuy
        inBuy = False if inBuy[1] and mode[1] == 'L2' and (low < l2LongExit[1]) else inBuy
    if not inBuy[1] and high > l1Long[1] and win[1]:
        fake = True
        fakeBuyPrice = close
    else:
        fake = fake[1]
    if fake[1] and inBuy[1] and (not inBuy):
        fake = False
        win = close >= fakeBuyPrice
    fake = False if high > l2Long[1] else fake
    l1LongPlot = l1Long[1] if not inBuy[1] or (inBuy[1] and mode == 'L1' and fake[1]) else l1LongPlot[1]
    l2LongPlot = l2Long[1] if not inBuy[1] or (inBuy[1] and mode == 'L1' and fake[1]) else l2LongPlot[1]
    longLevel = 'L1' if not inBuy[1] and high > l1Long[1] else na
    longLevel = 'L2' if (not inBuy[1] or (inBuy[1] and fake[1])) and high > l2Long[1] else longLevel
    mode = mode[1] if na(longLevel) else longLevel
    if longLevel == 'L1' or longLevel == 'L2':
        buyPrice = close
        totalBuys = 1
        stopPrice = close - stopInput * n
        nextBuyPrice = close + pyramidInput * n
    TradeDateIsAllowed_1 = TradeDateIsAllowed()
    longLevel = 'P' if na(longLevel) and inBuy[1] and (high > nextBuyPrice) and TradeDateIsAllowed_1 and (totalBuys < maxUnits) else longLevel
    if longLevel == 'P':
        buyPrice = close
        totalBuys = totalBuys[1] + 1
        stopPrice = close - stopInput * n
        nextBuyPrice = close + pyramidInput * n
    longLevel = 'SG' if na(longLevel) and inBuy[1] and (low < stopPrice) and (close >= strategy.position_avg_price) else longLevel
    longLevel = 'SR' if na(longLevel) and inBuy[1] and (low < stopPrice) and (close < strategy.position_avg_price) else longLevel
    longLevel = 'SG' if na(longLevel) and mode[1] == 'L1' and inBuy[1] and (low < l1LongExit[1]) and (close >= strategy.position_avg_price) else longLevel
    longLevel = 'SG' if na(longLevel) and mode[1] == 'L2' and inBuy[1] and (low < l2LongExit[1]) and (close >= strategy.position_avg_price) else longLevel
    longLevel = 'SR' if na(longLevel) and mode[1] == 'L1' and inBuy[1] and (low < l1LongExit[1]) and (close < strategy.position_avg_price) else longLevel
    longLevel = 'SR' if na(longLevel) and mode[1] == 'L2' and inBuy[1] and (low < l2LongExit[1]) and (close < strategy.position_avg_price) else longLevel
    win = True if longLevel == 'SG' else win
    win = False if longLevel == 'SR' else win
    TradeDateIsAllowed_2 = TradeDateIsAllowed()
    enterLong = (longLevel == 'L1' or longLevel == 'L2' or longLevel == 'P') and (not fake) and TradeDateIsAllowed_2
    TradeDateIsAllowed_3 = TradeDateIsAllowed()
    exitLong = (longLevel == 'SG' or longLevel == 'SR') and (not fake) and TradeDateIsAllowed_3
    p1 = plot(l1LongPlot, title='l1 long', linewidth=3, style=plot.style_stepline, color=color.new(color.green, 0))
    p2 = plot(l1LongExit[1], title='l1 exit', linewidth=3, style=plot.style_stepline, color=color.new(color.red, 0))
    p3 = plot(l2LongPlot, title='l2 long', linewidth=2, style=plot.style_stepline, color=color.new(color.green, 0))
    p4 = plot(l2LongExit[1], title='l2 exit', linewidth=2, style=plot.style_stepline, color=color.new(color.red, 0))
    color1 = color.new(color.black, 0)
    color2 = color.new(color.black, 100)
    col = color1 if inBuy else color2
    p5 = plot(stopPrice, title='stop', linewidth=2, style=plot.style_circles, join=True, color=color.new(color.black, 0))
    p6 = plot(nextBuyPrice, title='next buy', linewidth=2, style=plot.style_circles, join=True, color=color.new(color.blue, 0))
    fill(p1, p3, color=color.new(color.green, 90))
    fill(p2, p4, color=color.new(color.red, 90))
    risk = (strategy.initial_capital + strategy.netprofit) * riskPercent
    shares = math.floor(risk / (stopInput * n))
    capitalLeft = strategy.initial_capital + strategy.netprofit - strategy.position_size * strategy.position_avg_price
    if shares * close > capitalLeft:
        shares = math.max(0, math.floor(cast_int(capitalLeft / close)))
    shares = math.max(0, shares)
    plotshape(True if longLevel == 'L1' and (not fake) and (strategy.position_size == 0) else False, color=color.new(color.green, 40), style=shape.triangleup, text='L1 ')
    plotshape(True if not fake[1] and fake and (longLevel == 'L1') and (strategy.position_size == 0) else False, color=color.new(color.gray, 40), style=shape.triangleup, text='L1')
    plotshape(True if longLevel == 'L2' and strategy.position_size == 0 else False, color=color.new(color.green, 40), style=shape.triangleup, text='L2')
    plotshape(True if (mode == 'L1' or mode == 'L2') and shares > 0 and enterLong and (strategy.position_size > 0) else False, color=color.new(color.green, 40), style=shape.triangleup, text='P')
    plotarrow(1 if strategy.position_size == 0 and longLevel == 'L1' and enterLong else 0, colordown=color.new(color.black, 40), colorup=color.new(color.green, 40))
    plotarrow(1 if strategy.position_size == 0 and longLevel == 'L2' and enterLong else 0, colordown=color.new(color.black, 40), colorup=color.new(color.green, 40))
    plotarrow(-1 if strategy.position_size > 0 and longLevel == 'SR' and exitLong else 0, colordown=color.new(color.red, 40), colorup=color.new(color.purple, 40))
    plotarrow(-1 if strategy.position_size > 0 and longLevel == 'SG' and exitLong else 0, colordown=color.new(color.green, 40), colorup=color.new(color.purple, 40))
    plotshape(na(longLevel) and inBuy[1] and (not inBuy), color=color.new(color.gray, 40), style=shape.triangleup, text='Exit')
    plot(ta.atr(atrPeriod), title='ATR', color=color.new(color.new('#991515'), 0))
    plot(strategy.position_avg_price, title='Average Price', color=color.new(color.new('#991515'), 0))
    alertcondition(low < stopPrice, title='crosses under stop price', message='price crossed under stop price')
    alertcondition(high > l1Long, title='crosses over L1 price', message='price crossed over L1 price')
    alertcondition(high > l2Long, title='crosses over L2 price', message='price crossed over L2 price')
    alertcondition(low < l1LongExit, title='crosses under L1 exit price', message='price crossed under L1 exit price')
    alertcondition(low < l2LongExit, title='crosses under L2 exit price', message='price crossed under L2 exit price')
    if enterLong:
        strategy.entry('long', strategy.long, qty=shares, comment='long')
    if exitLong:
        strategy.close('long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
