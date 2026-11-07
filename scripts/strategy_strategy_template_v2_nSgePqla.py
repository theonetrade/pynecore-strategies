"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, color, fill, high, input, low, plot, request, script, strategy,
    syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Strategy Template - V2', overlay=True, initial_capital=20000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.11, max_lines_count=500, max_labels_count=500, max_boxes_count=500, margin_long=0, margin_short=0, close_by_id=True)
def main(
    i_entryType=input.string('Stop', title='Entry Type', options=('Market', 'Stop', 'Limit', 'Stop-Limit'), group='Entry Parameters'),
    i_dcLength=input.int(40, step=10, title='Donchian Length', group='Entry Parameters'),
    i_htfResolution=input.timeframe('W', title='Higher Timeframe', group='Entry Parameters'),
    i_stopType=input.string('Stop', title='Stop Type', options=('Market', 'Stop'), group='Exit Parameters'),
    i_takeProfit=input.bool(False, title='Take Initial Profit', group='Exit Parameters'),
    i_takeProfitRR=input.float(10, step=0.5, title='Risk/Reward (Take Profit)', group='Exit Parameters'),
    i_takeProfitQty=input.int(30, step=5, minval=5, maxval=100, title='Take Profit Percent', group='Exit Parameters'),
    i_atrMaType=input.string('sma', title='ATR MA Type (Stop-Limit)', options=('sma', 'ema', 'hma', 'rma', 'vwma', 'wma'), group='Exit Parameters'),
    i_atrLength=input.int(22, title='ATR Length (Stop-Limit', step=5, group='Exit Parameters'),
    i_atrMultStop=input.float(0.5, step=0.5, title='ATR Multiplier (Stop-Limit)', group='Exit Parameters'),
    i_tradeDirection=input.string(title='Trade Direction', defval=strategy.direction.all, options=(strategy.direction.all, strategy.direction.long, strategy.direction.short), group='Trade Filters'),
    i_startTime=input.time(defval=timestamp('01 Jan 2010 00:00 +0000'), title='Start Time', group='Trade Filters'),
    i_endTime=input.time(defval=timestamp('01 Jan 2099 00:00 +0000'), title='End Time', group='Trade Filters')
):
    strategy.risk.allow_entry_in(i_tradeDirection)
    inDateRange = time >= i_startTime and time <= i_endTime
    def f_secureSecurity(_symbol, _res, _src: Series, _offset):
        return request.security(_symbol, _res, _src[_offset], lookahead=barmerge.lookahead_on)

    def f_getMovingAverage(source, MAType, MALength):
        ma = ta.sma(source, MALength)
        if MAType == 'ema':
            ma = ta.ema(source, MALength)
        if MAType == 'hma':
            ma = ta.hma(source, MALength)
        if MAType == 'rma':
            ma = ta.rma(source, MALength)
        if MAType == 'vwma':
            ma = ta.vwma(source, MALength)
        if MAType == 'wma':
            ma = ta.wma(source, MALength)
        return ma

    def f_getCustomAtr(MAType, MALength):
        return f_getMovingAverage(ta.tr, MAType, MALength)

    def f_get_donchian(dcLength, resolution):
        top = ta.highest(dcLength) if resolution == '' else f_secureSecurity(syminfo.tickerid, resolution, ta.highest(dcLength), 1)
        bottom = ta.lowest(dcLength) if resolution == '' else f_secureSecurity(syminfo.tickerid, resolution, ta.lowest(dcLength), 1)
        mid = (top + bottom) / 2
        return (mid, top, bottom)

    top: Series
    bottom: Series
    mid, top, bottom = f_get_donchian(i_dcLength, '')
    hmid, htop, hbottom = f_get_donchian(i_dcLength, i_htfResolution)
    atrStop = f_getCustomAtr(i_atrMaType, i_atrLength) * i_atrMultStop
    p_top = plot(top, 'TOP', color=color.new(color.lime, 80))
    p_bottom = plot(bottom, 'BOTTOM', color=color.new(color.orange, 80))
    p_mid = plot(mid, 'MID', color=color.new(color.blue, 80))
    fill(p_top, p_mid, title='Upper', color=color.new(color.lime, 80))
    fill(p_bottom, p_mid, title='Lower', color=color.new(color.orange, 80))
    p_htop = plot(htop, 'HTOP', color=color.new(color.green, 80))
    p_hbottom = plot(hbottom, 'HBOTTOM', color=color.new(color.red, 80))
    p_hmid = plot(hmid, 'HMID', color=color.new(color.purple, 80))
    fill(p_htop, p_hmid, title='HTF Upper', color=color.new(color.green, 80))
    fill(p_hbottom, p_hmid, title='HTF Lower', color=color.new(color.red, 80))
    longBias = bottom > hmid and inDateRange
    shortBias = top < hmid and inDateRange
    closeBuyCondition = strategy.position_size > 0
    closeSellCondition = strategy.position_size < 0
    buyMarketCondition = ta.crossover(high, top[1]) and i_entryType == 'Market'
    sellMarketCondition = ta.crossunder(low, bottom[1]) and i_entryType == 'Market'
    closeBuyMarketCondition = ta.crossunder(low, bottom[1]) and i_stopType == 'Market' and (not longBias)
    closeSellMarketCondition = ta.crossover(high, top[1]) and i_stopType == 'Market' and (not shortBias)
    buySellStopCondition = i_entryType == 'Stop'
    closeBuySellStopCondition = i_stopType == 'Stop'
    buyLimitCondition = i_entryType == 'Limit' and high > mid
    sellLimitCondition = i_entryType == 'Limit' and low < mid
    crossover_1 = ta.crossover(high, top[1])
    buyStopLimitCondition = i_entryType == 'Stop-Limit' and crossover_1
    crossunder_1 = ta.crossunder(low, bottom[1])
    sellStopLimitCondition = i_entryType == 'Stop-Limit' and crossunder_1
    buyLevel = top
    sellLevel = bottom
    buyStopLimit = top + atrStop
    sellStopLimit = bottom - atrStop
    closeBuyStop = bottom
    closeSellStop = top
    takeProfitBuyCondition = longBias and strategy.position_size > 0 and i_takeProfit
    takeProfitSellCondition = shortBias and strategy.position_size < 0 and i_takeProfit
    profitLong: Series = top + i_takeProfitRR * (top - bottom)
    profitShort: Series = bottom - i_takeProfitRR * (top - bottom)
    profitLong = profitLong if strategy.position_size <= 0 else profitLong[1] + i_takeProfitRR * (top - bottom) if high[1] > profitLong[1] else profitLong[1]
    profitShort = profitShort if strategy.position_size >= 0 else profitShort[1] - i_takeProfitRR * (top - bottom) if low[1] < profitShort[1] else profitShort[1]
    if longBias:
        strategy.cancel('Short')
        strategy.close('Short')
        if buyMarketCondition:
            strategy.entry('Long', strategy.long, comment='Long-Market-Order')
        if buySellStopCondition:
            strategy.entry('Long', strategy.long, stop=buyLevel, oca_name='oca_buy', oca_type=strategy.oca.cancel, comment='Long-Stop-Order')
        if buyLimitCondition:
            strategy.entry('Long', strategy.long, limit=buyLevel, oca_name='oca_buy', oca_type=strategy.oca.cancel, comment='Long-Limit-Order')
        if buyStopLimitCondition:
            strategy.entry('Long', strategy.long, limit=buyStopLimit, stop=buyLevel, oca_name='oca_buy', oca_type=strategy.oca.cancel, comment='Long-Stop-Limit-Order')
    if shortBias:
        strategy.cancel('Long')
        strategy.close('Long')
        if sellMarketCondition:
            strategy.entry('Short', strategy.short, comment='Short-Market-Order')
        if buySellStopCondition:
            strategy.entry('Short', strategy.short, stop=sellLevel, oca_name='oca_sell', oca_type=strategy.oca.cancel, comment='Short-Stop-Order')
        if sellLimitCondition:
            strategy.entry('Short', strategy.short, limit=sellLevel, oca_name='oca_sell', oca_type=strategy.oca.cancel, comment='Short-Limit-Order')
        if sellStopLimitCondition:
            strategy.entry('Short', strategy.short, limit=sellStopLimit, stop=sellLevel, oca_name='oca_sell', oca_type=strategy.oca.cancel, comment='Short-Stop-Limit-Order')
    if closeBuyCondition and closeBuyMarketCondition:
        strategy.close('Long', comment='Close-Long-Market')
    if closeSellCondition and closeSellMarketCondition:
        strategy.close('Short', comment='Close-Short-Market')
    if closeBuySellStopCondition:
        if closeBuyCondition:
            strategy.exit('StopLong', 'Long', stop=closeBuyStop, comment='Close-Buy-Stop')
        if closeSellCondition:
            strategy.exit('StopShort', 'Short', stop=closeSellStop, comment='Close-Sell-Stop')
    if takeProfitBuyCondition:
        strategy.exit('ProfitLong', 'Long', limit=profitLong, qty_percent=i_takeProfitQty, comment='Close-Buy-Profit')
    if takeProfitSellCondition:
        strategy.exit('ProfitShort', 'Short', limit=profitShort, qty_percent=i_takeProfitQty, comment='Close-Sell-Profit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
