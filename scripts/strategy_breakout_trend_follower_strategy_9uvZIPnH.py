"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barmerge, barstate, close, color, extend, fixnan, high, input, line, low,
    math, na, plot, position, request, script, strategy, string, syminfo, ta, table, time,
    timestamp, xloc
)
from pynecore.types import Line, Persistent, Series, Table


@script.strategy('Breakout Trend Follower', overlay=True, initial_capital=10000, currency='USD', calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True)
def main(
    Start=input.time(defval=timestamp('01 Jan 2019 06:00 +0000'), title='Backtest Start Date', group='backtest window'),
    Finish=input.time(defval=timestamp('01 Jan 2100 00:00 +0000'), title='Backtest End Date', group='backtest window'),
    pvtLb=input.int(defval=3, title='Pivot Lookback', minval=1, group='support & resistance levels', tooltip='Number of bars to left and right to deterine local pivot.'),
    showPivotPoints=input.bool(title='Show Historical Pivot Points?', defval=False, group='support & resistance levels', tooltip='Toggle this on to see the historical pivot points that were used.'),
    currentColorS=input.color(color.new(color.orange, 50), title='Current Range S/R Colors:    Support', group='support & resistance levels', inline='lineColor'),
    currentColorR=input.color(color.new(color.blue, 50), title=' Resistance', group='support & resistance levels', inline='lineColor'),
    useMaFilter=input.bool(title='Use Current Timeframe Moving Average for Filtering?', defval=True, group='moving average filters', tooltip='Signals will be ignored when price is under this moving average.  The intent is to keep you out of bear periods and only buying when  price is showing strength.'),
    maType=input.string(defval='SMA', options=('EMA', 'SMA'), group='moving average filters', title='MA Type For Filtering'),
    maLength=input.int(defval=50, title='MA Period for Filtering', minval=1, group='moving average filters', inline='1ma'),
    ma1Color=input.color(color.new(color.purple, 60), title=' Color', group='moving average filters', inline='1ma'),
    useMaFilter2=input.bool(title='Use Multi-Timeframe Moving Average for Filtering?', defval=False, group='moving average filters', tooltip='Signals will be ignored when price is under this moving average.  The intent is to keep you out of bear periods and only buying when  price is showing strength. Other timeframe allows you to use Daily moving average for higher level view of market strength.'),
    tfSet=input.timeframe(defval='D', title='Moving Average Time Frame', group='moving average filters', tooltip='Allows you to set a different time frame moving average to filter your signals by.'),
    ma2Type=input.string(defval='SMA', options=('EMA', 'SMA'), title='MA Type For Filtering', group='moving average filters'),
    ma2Length=input.int(defval=50, title='MA Period for Filtering', minval=1, group='moving average filters', inline='2ma'),
    ma2Color=input.color(color.new(color.yellow, 60), title=' Color', group='moving average filters', inline='2ma'),
    useRsiFilter=input.bool(title='Use RSI for Filtering?', defval=False, group='rsi filtering', tooltip='Signals will be ignored if the RSI level is above a user-defined level for overbought.  This allows the user to ensure they are not buying something that is too extended and instead focus on names that are consolidating more.'),
    rsiTf=input.timeframe(defval='', title='RSI Timeframe', group='rsi filtering', tooltip='Allows you to set a different time frame for RSI to filter your signals by.'),
    rsiOB=input.int(defval=70, title='RSI Overbought Level', minval=1, group='rsi filtering'),
    useAdrFilter=input.bool(title='Use ADR for Filtering?', defval=False, group='adr filtering', tooltip='Signals will be ignored if the distance between support and resistance is larger than a user-defined percentage of ADR (or monthly volatility in the stock screener). This allows the user to ensure they are not buying something that is too extended and instead focus on names that are consolidating more.'),
    adrPerc=input.int(defval=120, title='% of ADR Value', minval=1, group='adr filtering'),
    tableLocation=input.string(defval='Bottom', options=('Top', 'Bottom'), title='ADR Table Visibility', group='adr filtering', tooltip='Place ADR table on the top of the pane, the bottom of the pane, or off.')
):
    def ma(maType, src, length):
        return ta.ema(src, length) if maType == 'EMA' else ta.sma(src, length)

    maFilter = ma(maType, close, maLength)
    maFilter2 = request.security(syminfo.tickerid, tfSet, ma(ma2Type, close, ma2Length))
    plot(maFilter if useMaFilter else na, title='Trend Filter MA', color=ma1Color, linewidth=2, style=plot.style_line)
    plot(maFilter2 if useMaFilter2 else na, title='Trend Filter MA', color=ma2Color, linewidth=2, style=plot.style_line)
    rsiVal: Series = request.security(syminfo.tickerid, rsiTf, ta.rsi(close, 14))
    ph = ta.pivothigh(high, pvtLb, pvtLb)
    pl = ta.pivotlow(low, pvtLb, pvtLb)
    highLevel = ta.valuewhen(cast_bool(ph), high[pvtLb], 0)
    lowLevel = ta.valuewhen(cast_bool(pl), low[pvtLb], 0)
    barsSinceHigh = ta.barssince(cast_bool(ph)) + pvtLb
    barsSinceLow = ta.barssince(cast_bool(pl)) + pvtLb
    timeSinceHigh = time[barsSinceHigh]
    timeSinceLow = time[barsSinceLow]
    pvthis = fixnan(ph)
    pvtlos = fixnan(pl)
    hipc = na if ta.change(pvthis) != 0 else color.maroon
    lopc = na if ta.change(pvtlos) != 0 else color.green
    plot(pvthis if showPivotPoints else na, color=hipc, linewidth=1, offset=-pvtLb, title='Top Levels')
    plot(pvthis if showPivotPoints else na, color=hipc, linewidth=1, offset=0, title='Top Levels 2')
    plot(pvtlos if showPivotPoints else na, color=lopc, linewidth=1, offset=-pvtLb, title='Bottom Levels')
    plot(pvtlos if showPivotPoints else na, color=lopc, linewidth=1, offset=0, title='Bottom Levels 2')
    def f_line(x1, y1, y2, _color):
        id: Persistent[Line] = na(Line)
        line.delete(id)
        id = line.new(x1, y1, time, y2, xloc.bar_time, extend.right, _color)
        return id

    highLine = f_line(timeSinceHigh, highLevel, highLevel, currentColorR)
    lowLine = f_line(timeSinceLow, lowLevel, lowLevel, currentColorS)
    adrValue = request.security(syminfo.tickerid, 'D', ta.sma((high - low) / math.abs(low) * 100, 21), barmerge.gaps_off, barmerge.lookahead_on)
    adrCompare = adrPerc * adrValue / 100
    tablePos = position.top_right if tableLocation == 'Top' else position.bottom_right
    adrTable: Persistent[Table] = table.new(tablePos, 2, 1, border_width=3)
    lightTransp: int = 90
    avgTransp: int = 80
    heavyTransp: int = 70
    posColor = color.rgb(38, 166, 154)
    negColor = color.rgb(240, 83, 80)
    volColor = color.new(color.new('#999999'), 0)
    def f_fillCellVol(_table, _column, _row, _value):
        _transp = heavyTransp if math.abs(_value) > 7 else avgTransp if math.abs(_value) > 4 else lightTransp
        _cellText = string.tostring(_value, '0.00') + '%\n' + 'ADR'
        return table.cell(_table, _column, _row, _cellText, bgcolor=color.new(volColor, _transp), text_color=volColor, width=6)

    srDistance = (highLevel - lowLevel) / highLevel * 100
    def f_fillCellCalc(_table, _column, _row, _value):
        _c_color = negColor if _value >= adrCompare else posColor
        _transp = lightTransp if _value >= adrCompare * 0.8 and _value <= adrCompare * 1.2 else avgTransp if _value >= adrCompare * 0.5 and _value < adrCompare * 0.8 else heavyTransp if _value < adrCompare * 0.5 else avgTransp if _value > adrCompare * 1.2 and _value <= adrCompare * 1.5 else heavyTransp if _value > adrCompare * 1.5 else na
        _cellText = string.tostring(_value, '0.00') + '%\n' + 'Range'
        return table.cell(_table, _column, _row, _cellText, bgcolor=color.new(_c_color, _transp), text_color=_c_color, width=6)

    if barstate.islast:
        f_fillCellVol(adrTable, 0, 0, adrValue)
        f_fillCellCalc(adrTable, 1, 0, srDistance)
    buyConditions = (highLevel > maFilter if useMaFilter else True) and (highLevel > maFilter2 if useMaFilter2 else True) and (highLevel - lowLevel < adrValue if useAdrFilter else True) and (rsiVal[1] < rsiOB if useRsiFilter else True) and (time > Start) and (time < Finish)
    if buyConditions:
        strategy.entry('Long', strategy.long, stop=highLevel)
    strategy.exit('Exit Long', from_entry='Long', stop=lowLevel)
    if not buyConditions:
        strategy.cancel('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
