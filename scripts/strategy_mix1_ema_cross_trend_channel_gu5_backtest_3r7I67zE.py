"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barcolor, barmerge, barstate, bgcolor, close, color, fill, format, high,
    input, location, low, na, nz, open, plot, plotchar, plotshape, request, script, shape, size,
    strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Color, Series

o_maLen1: str = 'EMA'
o_maLen2: str = 'SMA'
o_start = timestamp('2020-01-01 00:00 GMT-3')
o_end = timestamp('2099-12-31 00:00 GMT-3')
o_posSel1: str = 'Only Long'
o_posSel2: str = 'Only Short'
o_posSel3: str = 'Both'
o_typeS1: str = 'Strategy 1'
o_typeS2: str = 'Strategy 2'
o_alert: str = '{{strategy.order.comment}}'


@script.strategy(title='Mix1 : Ema Cross + Trend Channel [Gu5] - Backtest', shorttitle='Mix01', overlay=True, initial_capital=100, default_qty_value=100, format=format.price, precision=2, process_orders_on_close=True, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    i_maSrc: Series[float] = input.source(close, 'MA Source', group='EMAs'),
    i_maFast1=input.int(26, 'EMA Fast', group='EMAs'),
    i_maFast2=input.int(50, 'EMA Medium', group='EMAs'),
    i_maLen=input.int(200, 'MA Trend', group='Trend Channel'),
    i_maLenSel=input.string(o_maLen2, 'MA Type', group='Trend Channel', options=(o_maLen1, o_maLen2), tooltip='EMA or SMA'),
    i_htf=input.timeframe('', 'Select Higher Timeframe', group='Trend Channel', tooltip='Only for MA Trend'),
    i_rangeLen=input.float(0.618, 'Channel Range Length', group='Trend Channel', tooltip='ATR of the MA Trend'),
    i_slOn=input.bool(True, '■ Stop Loss On/Off', group='Stop Loss'),
    i_sl=input.float(1.5, 'SL %', group='Stop Loss', step=0.1),
    i_periodSw=input.bool(True, '■ Period On/Off', group='Period'),
    i_periodStar=input.time(o_start, 'Start Time', group='Period'),
    i_periodEnd=input.time(o_end, 'End Time', group='Period'),
    i_posSel=input.string(o_posSel3, 'Position Type', group='Strategy', options=(o_posSel1, o_posSel2, o_posSel3), tooltip='Only Long, Only short or Both'),
    i_typeS=input.string(o_typeS2, 'Strategy Type', group='Strategy', options=(o_typeS1, o_typeS2), tooltip='Strategy 1:\nLong, when the price (close) crosses the ema.\nStrategy 2:\nLong, only when ema goes up'),
    i_barColOn=input.bool(True, '■ Bar Color On/Off', group='Display'),
    i_alertOn=input.bool(False, '■ Alert On/Off', group='Display'),
    i_channelOn=input.bool(False, '■ Channel Range On/Off', group='Display', tooltip='If the price (close) is over than the channel, the trend is bullish. If the price is under, bearish. And if the price is in the channel, it is in range'),
    i_goldenOn=input.bool(False, '■ Golden Cross On/Off'),
    i_alert=input.string(o_alert, 'Setting alert', group='Display', tooltip='For Alerts, just copy {{strategy.order.comment}} and paste in alert window.')
):
    C_GREEN: Color = color.new('#006400')
    C_GREENLIGHT: Color = color.new('#388E3C')
    C_RED: Color = color.new('#8B0000')
    C_REDLIGHT: Color = color.new('#B71C1C')
    condition: Series[float] = 0.0
    maFast1 = ta.ema(i_maSrc, i_maFast1)
    maFast2 = ta.ema(i_maSrc, i_maFast2)
    maDir = 1 if maFast1 > maFast2 else -1
    maTrend: Series = request.security(syminfo.tickerid, i_htf, inline_series(ta.sma(close, i_maLen), 1) if i_maLenSel == 'SMA' else inline_series(ta.ema(close, i_maLen), 1), lookahead=barmerge.lookahead_on)
    maTrendDir = 1 if i_maSrc >= maTrend else -1
    rangeAtr = ta.atr(i_maLen) * i_rangeLen
    rangeTop = maTrend + rangeAtr
    rangeBot = maTrend - rangeAtr
    rangeCh = (open <= rangeTop or close <= rangeTop) and (open >= rangeBot or close >= rangeBot)
    trendDir = (0 if rangeCh else 0 if maTrendDir == 1 and maDir == 1 and (maTrend > maFast2) else 0 if maTrendDir == -1 and maDir == -1 and (maTrend < maFast2) else 1 if maTrendDir == 1 and maDir == 1 else -1 if maTrendDir == -1 and maDir == -1 else 0) if i_typeS == 'Strategy 1' else 0 if rangeCh else 1 if maTrendDir == 1 and maDir == 1 else -1 if maTrendDir == -1 and maDir == -1 else 0
    GCross = ta.crossover(maFast2, maTrend) if i_goldenOn else False
    DCross = ta.crossunder(maFast2, maTrend) if i_goldenOn else False
    period = time >= i_periodStar and time <= i_periodEnd if i_periodSw else True
    entryLong = trendDir == 1 and i_posSel != 'Only Short' and period
    entryShort = trendDir == -1 and i_posSel != 'Only Long' and period
    exitLong = trendDir != 1 and i_posSel != 'Only Short' and period
    exitShort = trendDir != -1 and i_posSel != 'Only Long' and period
    slEntry = close * i_sl / 100
    slTop = close + slEntry
    slBot = close - slEntry
    slTopBuff = ta.valuewhen(condition[1] != 1 and entryLong, slBot, 0)
    slBotBuff = ta.valuewhen(condition[1] != -1 and entryShort, slTop, 0)
    slLine = slTopBuff if condition[1] == -1 and entryLong else slBotBuff if condition[1] == 1 and entryShort else slTopBuff if condition[1] == 1 or entryLong else slBotBuff if condition[1] == -1 or entryShort else na
    crossunder_1 = ta.crossunder(low, slLine)
    slTopCross = condition[1] == 1 and crossunder_1
    crossover_1 = ta.crossover(high, slLine)
    slBotCross = condition[1] == -1 and crossover_1
    slExit = slTopCross or slBotCross if i_slOn else False
    condition = 1 if condition[1] != 1 and entryLong else -1 if condition[1] != -1 and entryShort else 0 if condition[1] != 0 and slExit else 0 if condition[1] == 1 and exitLong else 0 if condition[1] == -1 and exitShort else nz(condition[1])
    long = condition[1] != 1 and condition == 1
    short = condition[1] != -1 and condition == -1
    xl = condition[1] == 1 and condition == 0 and (not slExit)
    xs = condition[1] == -1 and condition == 0 and (not slExit)
    sl = condition[1] != 0 and slExit
    c_emas = color.new(color.orange, 99) if xl else color.new(color.orange, 99) if xs else color.new(C_GREEN, 99) if trendDir == 1 and maDir == 1 else color.new(C_RED, 99) if trendDir == -1 and maDir == -1 else color.new(color.orange, 99)
    c_maFill = color.new(color.orange, 70) if xl else color.new(color.orange, 70) if xs else color.new(C_GREEN, 70) if trendDir == 1 and maDir == 1 else color.new(C_RED, 70) if trendDir == -1 and maDir == -1 else color.new(color.orange, 70)
    c_maTrend = color.new(color.orange, 0) if trendDir == 0 else color.new(C_GREEN, 0) if trendDir == 1 and maTrend[1] < maTrend else color.new(C_GREENLIGHT, 0) if trendDir == 1 and maTrend[1] >= maTrend else color.new(C_REDLIGHT, 0) if trendDir == -1 and maTrend[1] < maTrend else color.new(C_RED, 0) if trendDir == -1 and maTrend[1] >= maTrend else na
    c_ch = color.new(color.orange, 50) if trendDir == 0 else color.new(C_GREEN, 50) if trendDir == 1 else color.new(C_RED, 50) if trendDir == -1 else na
    c_slLineUp = ta.rising(slLine, 1)
    c_slLineDn = ta.falling(slLine, 1)
    c_slLine = na if c_slLineUp else na if c_slLineDn else color.red
    c_barCol = color.new(color.orange, 0) if trendDir == 0 and open <= close else color.new(color.yellow, 0) if trendDir == 0 and open > close else color.new(C_GREEN, 0) if trendDir == 1 and open <= close else color.new(C_GREENLIGHT, 0) if trendDir == 1 and open > close else color.new(C_RED, 0) if trendDir == -1 and open >= close else color.new(C_REDLIGHT, 0) if trendDir == -1 and open < close else color.new(color.orange, 0)
    p_maFast1 = plot(maFast1, title='EMA Fast 1', color=c_emas, linewidth=1)
    p_maFast2 = plot(maFast2, title='EMA Fast 2', color=c_emas, linewidth=2)
    fill(p_maFast1, p_maFast2, title='EMAs Fill', color=c_maFill)
    plot(maTrend, title='SMA Trend', color=c_maTrend, linewidth=3)
    p_chTop = plot(rangeTop if i_channelOn else na, title='Top Channel', color=c_maTrend, linewidth=1)
    p_chBot = plot(rangeBot if i_channelOn else na, title='Bottom Channel', color=c_maTrend, linewidth=1)
    fill(p_chTop, p_chBot, title='Channel', color=c_ch)
    plot(slLine if i_slOn and condition != 0 else na, title='Stop Loss Line', color=c_slLine, linewidth=1, style=plot.style_linebr)
    if long and barstate.isconfirmed:
        strategy.entry('Long', strategy.long, comment='long')
    if short and barstate.isconfirmed:
        strategy.entry('Short', strategy.short, comment='short')
    strategy.exit(id='XL', from_entry='Long', stop=slLine if i_slOn else na)
    strategy.exit(id='XS', from_entry='Short', stop=slLine if i_slOn else na)
    if xl:
        strategy.close('Long', comment='Close')
    if xs:
        strategy.close('Short', comment='Close')
    barcolor(c_barCol if i_barColOn else na)
    plotshape(high if i_alertOn and long else na, title='Long Label', text='Long', textcolor=color.white, color=color.new(C_GREEN, 0), style=shape.labelup, size=size.normal, location=location.belowbar)
    plotshape(low if i_alertOn and short else na, title='Short Label', text='Short', textcolor=color.white, color=color.new(C_RED, 0), style=shape.labeldown, size=size.normal, location=location.abovebar)
    plotshape(close if i_alertOn and (xl or xs) else na, title='Close Label', text='Close', textcolor=color.orange, color=color.new(color.orange, 0), style=shape.xcross, size=size.small, location=location.absolute)
    plotshape(slLine if i_alertOn and sl else na, title='Stop Loss', text='Stop\nLoss', textcolor=color.orange, color=color.new(color.orange, 0), style=shape.xcross, size=size.small, location=location.absolute)
    plotshape(maTrend if i_alertOn and i_goldenOn and GCross else na, title='Golden Cross Label', text='Golden\nCross', textcolor=color.white, color=color.new(color.orange, 0), style=shape.labelup, size=size.normal, location=location.absolute)
    plotshape(maTrend if i_alertOn and i_goldenOn and DCross else na, title='Death Cross Label', text='Death\nCross', textcolor=color.white, color=color.new(color.orange, 0), style=shape.labeldown, size=size.normal, location=location.absolute)
    bgcolor(color.new(color.gray, 90) if i_periodSw and (not period) else na, title='Session')
    plotchar(maTrendDir, title='maTrendDir', text='', location=location.absolute, color=color.new(color.blue, 100))
    plotchar(maDir, title='maDir', text='', location=location.absolute, color=color.new(color.blue, 100))
    plotchar(trendDir, title='trendDir', text='', location=location.absolute, color=color.new(color.blue, 100))
    plotchar(exitLong, title='exitLong', text='', location=location.absolute, color=color.new(color.blue, 100))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
