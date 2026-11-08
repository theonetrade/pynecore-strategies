"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, barmerge, bgcolor, close, color, fill, high,
    input, location, low, na, nz, open, plot, plotshape, request, script, shape, size, syminfo, ta,
    time, timestamp
)
from pynecore.types import Color, Series

O_MALEN1: str = 'EMA'
O_MALEN2: str = 'SMA'
O_POSSEL1: str = 'Only Long'
O_POSSEL2: str = 'Only Short'
O_POSSEL3: str = 'Both'
O_TYPES1: str = 'Strategy 1'
O_TYPES2: str = 'Strategy 2'
O_START = timestamp('2020-01-01 00:00 GMT-3')
O_END = timestamp('2099-12-31 00:00 GMT-3')


@script.indicator(title='Mix1 : Ema Cross + Trend Channel [Gu5]', shorttitle='Mix1', overlay=True)
def main(
    i_maSrc: Series[float] = input.source(close, 'MA Source', group='EMAs'),
    i_maFast1=input.int(26, 'EMA Fast', group='EMAs'),
    i_maFast2=input.int(50, 'EMA Medium', group='EMAs'),
    i_maLen=input.int(200, 'MA Trend', group='Trend Channel'),
    i_maLenSel=input.string(O_MALEN2, 'MA Type', group='Trend Channel', options=(O_MALEN1, O_MALEN2), tooltip='EMA or SMA'),
    i_htf=input.timeframe('', 'Select Higher Timeframe', group='Trend Channel', tooltip='Only for MA Trend'),
    i_rangeLen=input.float(0.618, 'Channel Range Length', group='Trend Channel', tooltip='ATR of the MA Trend'),
    i_slOn=input.bool(False, '■ Stop Loss On/Off', group='Stop Loss'),
    i_sl=input.float(2.618, 'SL %', group='Stop Loss', step=0.1),
    i_periodSw=input.bool(False, '■ Period On/Off', group='Period'),
    i_periodStar=input.time(O_START, 'Start Time', group='Period'),
    i_periodEnd=input.time(O_END, 'End Time', group='Period'),
    i_posSel=input.string(O_POSSEL3, 'Position Type', group='Strategy', options=(O_POSSEL1, O_POSSEL2, O_POSSEL3), tooltip='Only Long, Only shortE or Both'),
    i_typeS=input.string(O_TYPES2, 'Strategy Type', group='Strategy', options=(O_TYPES1, O_TYPES2), tooltip='Strategy 1:\n Long, when the price (close) crosses the ema.\n Strategy 2:\n Long, only when ema goes up'),
    i_barColOn=input.bool(True, '■ Bar Color On/Off', group='Display'),
    i_alertOn=input.bool(True, '■ Alert On/Off', group='Display'),
    i_channelOn=input.bool(False, '■ Channel Range On/Off', group='Display', tooltip='If the price (close) is over than the channel, the trend is bullish. If the price is under, bearish. And if the price is in the channel, it is in range'),
    i_goldenOn=input.bool(False, '■ Golden Cross On/Off')
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
    entryLong = i_posSel != 'Only Short' and trendDir == 1 and period
    entryShort = i_posSel != 'Only Long' and trendDir == -1 and period
    exitLong = i_posSel != 'Only Short' and (trendDir != 1 or maDir == -1) and (condition[1] == 1) and period
    exitShort = i_posSel != 'Only Long' and (trendDir != -1 or maDir == 1) and (condition[1] == -1) and period
    slEntry = close * i_sl / 100 if i_slOn else na
    slTop = close + slEntry
    slBot = close - slEntry
    slTopBuff = ta.valuewhen(condition[1] != 1 and entryLong, slBot, 0)
    slBotBuff = ta.valuewhen(condition[1] != -1 and entryShort, slTop, 0)
    slLine = slTopBuff if condition[1] == -1 and entryLong else slBotBuff if condition[1] == 1 and entryShort else slTopBuff if condition[1] == 1 or entryLong else slBotBuff if condition[1] == -1 or entryShort else na
    crossunder_1 = ta.crossunder(close, slLine)
    slLong = condition[1] == 1 and crossunder_1 or (high > slLine and low < slLine)
    crossover_1 = ta.crossover(close, slLine)
    slShort = condition[1] == -1 and crossover_1 or (high > slLine and low < slLine)
    condition = 1 if condition[1] != 1 and entryLong else -1 if condition[1] != -1 and entryShort else 0 if condition[1] == 1 and slLong else 0 if condition[1] == -1 and slShort else 0 if condition[1] != 0 and exitLong else 0 if condition[1] != 0 and exitShort else nz(condition[1])
    longE = condition[1] != 1 and condition == 1
    shortE = condition[1] != -1 and condition == -1
    longX = condition[1] == 1 and exitLong and (not slLong)
    shortX = condition[1] == -1 and exitShort and (not slShort)
    longSL = condition[1] == 1 and slLong
    shortSL = condition[1] == -1 and slShort
    c_emas = color.new(color.orange, 99) if longX else color.new(color.orange, 99) if shortX else color.new(C_GREEN, 99) if trendDir == 1 and maDir == 1 else color.new(C_RED, 99) if trendDir == -1 and maDir == -1 else color.new(color.orange, 99)
    c_maFill = color.new(color.orange, 70) if longX else color.new(color.orange, 70) if shortX else color.new(C_GREEN, 70) if trendDir == 1 and maDir == 1 else color.new(C_RED, 70) if trendDir == -1 and maDir == -1 else color.new(color.orange, 70)
    c_maTrend = color.new(color.orange, 0) if trendDir == 0 else color.new(C_GREEN, 0) if trendDir == 1 and maTrend[1] < maTrend else color.new(C_GREENLIGHT, 0) if trendDir == 1 and maTrend[1] >= maTrend else color.new(C_REDLIGHT, 0) if trendDir == -1 and maTrend[1] < maTrend else color.new(C_RED, 0) if trendDir == -1 and maTrend[1] >= maTrend else na
    c_ch = color.new(color.orange, 75) if trendDir == 0 else color.new(C_GREEN, 75) if trendDir == 1 else color.new(C_RED, 75) if trendDir == -1 else na
    c_slLineUp = ta.rising(slLine, 1)
    c_slLineDn = ta.falling(slLine, 1)
    c_slLine = na if c_slLineUp else na if c_slLineDn else color.new(C_RED, 0)
    c_barCol = color.new(color.orange, 0) if trendDir == 0 else color.new(C_GREEN, 0) if trendDir == 1 and open <= close else color.new(C_GREENLIGHT, 0) if trendDir == 1 and open > close else color.new(C_RED, 0) if trendDir == -1 and open >= close else color.new(C_REDLIGHT, 0) if trendDir == -1 and open < close else color.new(color.orange, 0)
    p_maFast1 = plot(maFast1, title='EMA Fast 1', color=c_emas, linewidth=1)
    p_maFast2 = plot(maFast2, title='EMA Fast 2', color=c_emas, linewidth=2)
    fill(p_maFast1, p_maFast2, title='EMAs Fill', color=c_maFill)
    plot(maTrend, title='SMA Trend', color=c_maTrend, linewidth=3)
    p_chTop = plot(rangeTop if i_channelOn else na, title='Top Channel', color=c_maTrend, linewidth=1)
    p_chBot = plot(rangeBot if i_channelOn else na, title='Bottom Channel', color=c_maTrend, linewidth=1)
    fill(p_chTop, p_chBot, title='Channel', color=c_ch)
    plot(slLine if i_slOn and condition != 0 else na, title='Stop Loss Line', color=c_slLine, linewidth=1, style=plot.style_linebr)
    plotshape(high if i_alertOn and longE else na, title='Long', text='Long', textcolor=color.white, color=color.new(C_GREEN, 0), style=shape.labelup, size=size.normal, location=location.belowbar)
    plotshape(low if i_alertOn and shortE else na, title='Short', text='Short', textcolor=color.white, color=color.new(C_RED, 0), style=shape.labeldown, size=size.normal, location=location.abovebar)
    plotshape(close if i_alertOn and (longX or shortX) else na, title='Close', text='Close', textcolor=color.new(color.yellow, 0), color=color.new(color.yellow, 0), style=shape.xcross, size=size.small, location=location.absolute)
    plotshape(slLine if i_alertOn and (longSL or shortSL) else na, title='Stop Loss', text='SL', textcolor=color.new(color.yellow, 0), color=color.new(color.yellow, 0), style=shape.xcross, size=size.small, location=location.absolute)
    plotshape(maTrend if i_alertOn and i_goldenOn and GCross else na, title='Golden Cross', text='Golden\nCross', textcolor=color.white, color=color.new(color.orange, 0), style=shape.labelup, size=size.normal, location=location.absolute)
    plotshape(maTrend if i_alertOn and i_goldenOn and DCross else na, title='Death Cross', text='Death\nCross', textcolor=color.white, color=color.new(color.orange, 0), style=shape.labeldown, size=size.normal, location=location.absolute)
    barcolor(c_barCol if i_barColOn else na)
    bgcolor(color.new(color.gray, 90) if i_periodSw and (not period) else na, title='Session')
    alertcondition(longE or shortE or longX or shortX or longSL or shortSL, title='Any Alert', message='Any Alert')
    alertcondition(longE, title='Buy', message='Buy')
    alertcondition(shortE, title='Sell', message='Sell')
    alertcondition(longX, title='Buy Close', message='Buy Close')
    alertcondition(shortX, title='Sell Close', message='Sell Close')
    alertcondition(longSL, title='Stop Loss Long', message='Stop Loss Long')
    alertcondition(shortSL, title='Stop Loss Short', message='Stop Loss Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
