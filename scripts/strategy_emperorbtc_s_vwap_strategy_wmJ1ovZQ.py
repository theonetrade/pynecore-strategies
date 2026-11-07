"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, close, color, fill, high, input, location, low, math, na,
    ohlc4, open, plot, plotshape, request, script, shape, size, strategy, syminfo, ta, time,
    timestamp, volume
)
from pynecore.types import Series


@script.strategy(title='EmperorBTC\'s VWAP Strategy', shorttitle='EMP-VWAP', overlay=True, pyramiding=1, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    plotAveragePriceCrossedPivotPoint=input.bool(False, title='Plot Close Price Crossing Pivot Points?', group='Pivot Points'),
    plotPivotPoints=input.bool(False, title='Plot Pivot Points?', group='Pivot Points'),
    pivotPointsType=input.string(title='Pivot Points type', defval='Fibonacci', options=('Fibonacci', 'Traditional'), group='Pivot Points'),
    pivotPointCircleWidth=input.int(2, title='Width of Pivot Point circles', minval=1, group='Pivot Points'),
    plotVWAP=input.bool(True, title='Plot VWAP?', group='VWAP'),
    plotAvgPrice=input.bool(True, title='Plot Average Price?', group='VWAP'),
    plotVWAPCrossPrice=input.bool(False, title='Plot Price Crossing VWAP?', group='VWAP'),
    reso=input.timeframe(title='Period', defval='D', group='VWAP'),
    cumulativePeriod=input.int(14, 'VWAP Cumulative Period', group='VWAP'),
    plotStochRSICross=input.bool(False, title='Plot StochRSI Cross?', group='StochRSI'),
    smoothK=input.int(3, 'K', minval=1, group='StochRSI', inline='K&D'),
    smoothD=input.int(3, 'D', minval=1, group='StochRSI', inline='K&D'),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group='Stochastic-RSI', inline='length'),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group='Stochastic-RSI', inline='length'),
    rsiSrc: Series[float] = input.source(close, title='RSI Source', group='Stochastic-RSI'),
    plotLong=input.bool(True, title='Plot Long Opportunity?', group='Strategy only'),
    plotShort=input.bool(True, title='Plot Short Opportunity?', group='Strategy only'),
    tradingDirection=input.string(title='Strategy trading Direction: ', defval='L&S', options=('L&S', 'L', 'S'), group='Strategy only'),
    __input_18__=input.float(1.0, title='Take Profit %', group='Strategy only'),
    plotTP=input.bool(True, title='Plot Take Profit?', group='Strategy only'),
    startDate=input.int(title='Start Date', defval=1, minval=1, maxval=31, group='Backtesting range', inline='Start Date'),
    startMonth=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Backtesting range', inline='Start Date'),
    startYear=input.int(title='Start Year', defval=2017, minval=1800, maxval=2100, group='Backtesting range', inline='Start Date'),
    endDate=input.int(title='End Date', defval=31, minval=1, maxval=31, group='Backtesting range', inline='End Date'),
    endMonth=input.int(title='End Month', defval=12, minval=1, maxval=12, group='Backtesting range', inline='End Date'),
    endYear=input.int(title='End Year', defval=2050, minval=1800, maxval=2100, group='Backtesting range', inline='End Date')
):
    def __pc_bool_marker(b: bool):
        return na if na(b) else 1 if b else 0

    takeProfit = __input_18__ / 100
    candleHigh = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_on)
    candleLow = request.security(syminfo.tickerid, 'D', low[1], lookahead=barmerge.lookahead_on)
    candleClose = request.security(syminfo.tickerid, 'D', close[1], lookahead=barmerge.lookahead_on)
    pivotPoint = (candleHigh + candleLow + candleClose) / 3
    resistance1: float = na(float)
    resistance2: float = na(float)
    resistance3: float = na(float)
    support1: float = na(float)
    support2: float = na(float)
    support3: float = na(float)
    if pivotPointsType == 'Fibonacci':
        resistance1 = pivotPoint + 0.382 * (candleHigh - candleLow)
        resistance2 = pivotPoint + 0.618 * (candleHigh - candleLow)
        resistance3 = pivotPoint + candleHigh - candleLow
        support1 = pivotPoint - 0.382 * (candleHigh - candleLow)
        support2 = pivotPoint - 0.618 * (candleHigh - candleLow)
        support3 = pivotPoint - (candleHigh - candleLow)
    elif pivotPointsType == 'Traditional':
        resistance1 = 2 * pivotPoint - candleLow
        resistance2 = pivotPoint + candleHigh - candleLow
        resistance3 = candleHigh + 2 * (pivotPoint - candleLow)
        support1 = 2 * pivotPoint - candleHigh
        support2 = pivotPoint - (candleHigh - candleLow)
        support3 = candleLow - 2 * (candleHigh - pivotPoint)
    plot(series=support1 if plotPivotPoints else na, color=color.new(color.new('#FF0000'), 0), title='S1', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=support2 if plotPivotPoints else na, color=color.new(color.new('#800000'), 0), title='S2', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=support3 if plotPivotPoints else na, color=color.new(color.new('#330000'), 0), title='S3', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=pivotPoint if plotPivotPoints else na, color=color.new(color.new('#FFA500'), 0), title='PP', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=resistance1 if plotPivotPoints else na, color=color.new(color.new('#00FF00'), 0), title='R1', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=resistance2 if plotPivotPoints else na, color=color.new(color.new('#008000'), 0), title='R2', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    plot(series=resistance3 if plotPivotPoints else na, color=color.new(color.new('#003300'), 0), title='R3', style=plot.style_circles, linewidth=math.max(1, pivotPointCircleWidth))
    pivotPointCrossedUp: Series = low < support3 and close > support3 or (low < support2 and close > support2) or (low < support1 and close > support1) or (low < pivotPoint and close > pivotPoint)
    pivotPointCrossedDown: Series = high > support3 and close < support3 or (high > support2 and close < support2) or (high > support1 and close < support1) or (high > pivotPoint and close < pivotPoint)
    plotPPColor = color.green if pivotPointCrossedUp else color.red if pivotPointCrossedDown else na
    plotshape(series=__pc_bool_marker(pivotPointCrossedUp or pivotPointCrossedDown) if plotAveragePriceCrossedPivotPoint else na, title='PP Cross', style=shape.triangleup, location=location.belowbar, color=plotPPColor, text='PP', size=size.small)
    t: Series = time(reso)
    debut = na(t[1]) or t > t[1]
    addsource: Series = ohlc4 * volume
    addvol: Series = volume
    addsource = addsource if debut else addsource + addsource[1]
    addvol = addvol if debut else addvol + addvol[1]
    vwapValue = addsource / addvol
    pVWAP = plot(series=vwapValue if plotVWAP else na, color=color.new(color.purple, 0), title='VWAP')
    pAvgPrice = plot(series=ohlc4 if plotAvgPrice else na, color=color.new(color.blue, 0), title='PRICE')
    fill(pVWAP, pAvgPrice, color=color.red if ohlc4 > vwapValue else color.green, title='VWAP PRICE FILL')
    vwapCrossUp: Series = low < vwapValue and vwapValue < high and (close > open)
    vwapCrossDown: Series = high > vwapValue and vwapValue > low and (close < open)
    plotVWAPColor = color.green if vwapCrossUp else color.red if vwapCrossDown else na
    plotshape(series=__pc_bool_marker(vwapCrossUp or vwapCrossDown) if plotVWAPCrossPrice else na, title='VWAP Cross Price', style=shape.triangleup, location=location.belowbar, color=plotVWAPColor, text='VWAP', size=size.small)
    rsi1 = ta.rsi(rsiSrc, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d: Series = ta.sma(k, smoothD)
    sRsiCrossUp: Series = k[1] < d[1] and k > d
    sRsiCrossDown: Series = k[1] > d[1] and k < d
    plotColor = color.green if sRsiCrossUp else color.red if sRsiCrossDown else na
    plotshape(series=__pc_bool_marker(sRsiCrossUp or sRsiCrossDown) if plotStochRSICross else na, title='StochRSI Cross Up', style=shape.triangleup, location=location.belowbar, color=plotColor, text='StochRSI', size=size.small)
    sRsiCrossedUp: Series = sRsiCrossUp or sRsiCrossUp[1]
    vwapCrossedUp: Series = vwapCrossUp or vwapCrossUp[1]
    longCond1 = sRsiCrossedUp[1] and vwapCrossedUp[1]
    longCond2 = pivotPointCrossedUp[1]
    longCond3 = close[1] > open[1] and close > open
    longCond = longCond1 and longCond2 and longCond3
    plotshape(series=(na if na(longCond) else 1 if longCond else 0) if plotLong else na, title='Long', style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), text='Long', size=size.normal)
    sRsiCrossedDown: Series = sRsiCrossDown or sRsiCrossDown[1]
    vwapCrossedDown: Series = vwapCrossDown or vwapCrossDown[1]
    shortCond1 = sRsiCrossedDown[1] and vwapCrossedDown[1]
    shortCond2 = pivotPointCrossedDown[1]
    shortCond3 = close[1] < open[1] and close < open
    shortCond = shortCond1 and shortCond2 and shortCond3
    plotshape(series=(na if na(shortCond) else 1 if shortCond else 0) if plotShort else na, title='Short', style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), text='Short', size=size.normal)
    takeProfitLong = strategy.position_avg_price * (1 + takeProfit)
    takeProfitShort = strategy.position_avg_price * (1 - takeProfit)
    exitTp = strategy.position_size > 0 and close > takeProfitLong or (strategy.position_size < 0 and close < takeProfitShort)
    strategy.risk.allow_entry_in(strategy.direction.long if tradingDirection == 'L' else strategy.direction.short if tradingDirection == 'S' else strategy.direction.all)
    plot(series=takeProfitLong if plotTP and strategy.position_size > 0 else na, title='TP Level', color=color.new(color.green, 0), style=plot.style_linebr, linewidth=2)
    plot(series=takeProfitShort if plotTP and strategy.position_size < 0 else na, title='TP Level', color=color.new(color.red, 0), style=plot.style_linebr, linewidth=2)
    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    if longCond and inDateRange:
        strategy.entry('VWAP', strategy.long, comment='Long')
    if shortCond and inDateRange:
        strategy.entry('VWAP', strategy.short, comment='Short')
    if exitTp:
        strategy.close(id='VWAP')
    if not inDateRange:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
