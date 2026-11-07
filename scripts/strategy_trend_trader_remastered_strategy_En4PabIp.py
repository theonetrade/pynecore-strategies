"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, close, color, currency, high, input,
    location, low, math, na, open, plot, plotshape, script, shape, size, strategy, ta, time,
    timestamp
)
from pynecore.types import Persistent, Series
import lib.aybarsm.ToolsFluent.v6 as ToolsFluent
import lib.aybarsm.ToolsPos.v10 as ToolsPos
import lib.aybarsm.tac.v21 as Tac


@script.strategy("Trend Trader-Remastered Strategy", shorttitle='TTR-Strategy', overlay=True, process_orders_on_close=True, calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, initial_capital=10000, default_qty_value=10, currency=currency.USD, commission_value=0.05, commission_type=strategy.commission.percent)
def main(
    posDir=input.string(title='Direction', defval='Buy & Sell', options=('Buy & Sell', 'Buy Only', 'Sell Only'), group='Position', inline='position'),
    showEntryBuy=input.bool(title='Buy: Entry', defval=True, group='Show Signals', inline='signalsBuy'),
    showTpBuy=input.bool(title='Buy: TP', defval=True, group='Show Signals', inline='signalsBuy'),
    showReBuy=input.bool(title='Buy: RE', defval=True, group='Show Signals', inline='signalsBuy'),
    showExitBuy=input.bool(title='Buy: Exit', defval=False, group='Show Signals', inline='signalsBuy'),
    showEntrySell=input.bool(title='Sell: Entry', defval=True, group='Show Signals', inline='signalsSell'),
    showTpSell=input.bool(title='Sell: TP', defval=True, group='Show Signals', inline='signalsSell'),
    showReSell=input.bool(title='Sell: RE', defval=True, group='Show Signals', inline='signalsSell'),
    showExitSell=input.bool(title='Sell: Exit', defval=False, group='Show Signals', inline='signalsSell'),
    psarStart=input.float(title='Start', minval=0.001, defval=0.02, group='PSAR', inline='psar'),
    psarIncrement=input.float(title='Inc', minval=0.001, defval=0.02, group='PSAR', inline='psar'),
    psarMax=input.float(title='Max', minval=0.0001, defval=0.025, group='PSAR', inline='psar'),
    fracSrcHigh: Series[float] = input.source(title='High Source', defval=high, group='BW Fractals', tooltip='Important: This setting affects take profit and re-entry signals. It determines the source of high mark BW fractals.'),
    fracSrcLow: Series[float] = input.source(title='Low Source', defval=low, group='BW Fractals', tooltip='Important: This setting affects take profit and re-entry signals. It determines the source of high mark BW fractals.'),
    fracLbHigh=input.int(title='High Lookback', defval=2, group='BW Fractals', tooltip='Important: This setting affects take profit and re-entry signals. It determines the amount of lookback higher high BW fractals breakout.'),
    fracLbLow=input.int(title='Low Lookback', defval=2, group='BW Fractals', tooltip='Important: This setting affects take profit and re-entry signals. It determines the amount of lookback lower low BW fractals breakout.'),
    sigReMinProximity=input.float(defval=0, minval=0, step=0.01, maxval=99.99, title='Minimum Re-Entry Proximity Ratio', group='Signal Fine-Tuning: Re Proximity', tooltip='Important: This setting affects re-entry signals. Minimum required proximity ratio to PSAR for re-entry signal'),
    sigReBuyNoTp=input.bool(title='For Buy', defval=False, group='Signal Fine-Tuning: Allow Re-Entry Without TP', inline='AllowReNoTp', tooltip='Important: This setting affects re-entry signals. It allows BUY re-entry signals even if there hasn\'t been a take profit signal. (This setting does not affect minimum required proximity setting.)'),
    sigReSellNoTp=input.bool(title='For Sell', defval=False, group='Signal Fine-Tuning: Allow Re-Entry Without TP', inline='AllowReNoTp', tooltip='Important: This setting affects re-entry signals. It allows SELL re-entry signals even if there hasn\'t been a take profit signal. (This setting does not affect minimum required proximity setting.)'),
    showPsar=input.bool(title='PSAR', defval=False, group='Show Informative', inline='informative'),
    showPsarLagging=input.bool(title='Lagging PSAR', defval=True, group='Show Informative', inline='informative'),
    showStrategyAvgPrice=input.bool(title='Strategy Avg Price', defval=False, group='Show Informative', inline='informative'),
    sFrom=input.time(title="From", defval=timestamp('01 Jan 2000 00:00'), group='Strategy'),
    sTo=input.time(title="To", defval=timestamp('31 Dec 2050 23:59'), group='Strategy'),
    tpReductionRate=input.float(title='TP Reduce', minval=0.0, defval=10, maxval=100, group='Strategy', tooltip='The percentage of progressive reduction on active position size for take profit signals.\n\nExample:\nTP Reduce: 10%\nEntry Position Size: 100\nTP1: 100-10=90\nTP2: 90-9=81'),
    reWhenRate=input.float(title='RE When', minval=0.0, defval=50, maxval=100, group='Strategy', tooltip='The percentage of position size on initial entry of the signal to determine re-entry.\n\nExample:\nRE When: 50%\nEntry Position Size: 100\nRe-Entry Condition: Active Position Size < 50'),
    reFillRate=input.float(title='RE Fill', minval=0.0, defval=75, maxval=100, group='Strategy', inline='signal', tooltip='The percentage of position size on initial entry of the signal to be completed.\n\nExample:\nRE Fill: 75%\nEntry Position Size: 100\nActive Position Size: 50\nRe Order Size: 25\nFinal Active Position Size:75\n\nImportant: Even RE When condition is met, the active position size required to drop below RE Fill rate to trigger re-entry order.')
):
    pos: Persistent[ToolsPos.PosInfo] = ToolsPos.PosInfo.new()
    fracs: Persistent[Tac.BWFractals] = Tac.BWFractals.new()
    marksTP: Persistent[list[int]] = na(list[int])
    marksRE: Persistent[list[int]] = na(list[int])

    psar_lagging: Series
    psar, psar_lagging, psar_fast = Tac.sar(psarStart, psarIncrement, psarMax)
    psarProximity: float = math.round(math.abs(close - psar_lagging) / psar_lagging * 100, 2)
    psarCrossHigh: bool = ta.crossover(high, psar_lagging)
    psarCrossLow: bool = ta.crossunder(low, psar_lagging)
    psarLagCross: int = 1 if psar_lagging[1] > high[1] and psarCrossHigh else -1 if psar_lagging[1] < low[1] and psarCrossLow else 0
    posActionFrac: Tac.BWFractal = na(Tac.BWFractal)
    posAllowBuy: bool = posDir == 'Buy & Sell' or posDir == 'Buy Only'
    posAllowSell: bool = posDir == 'Buy & Sell' or posDir == 'Sell Only'
    posEnter: str = 'buy' if posAllowBuy and psarLagCross == 1 else 'sell' if posAllowSell and psarLagCross == -1 else na
    posExit: str = 'buy' if not na(pos.state) and pos.state == ToolsPos.PosState.buy and (psarLagCross == -1) else 'sell' if not na(pos.state) and pos.state == ToolsPos.PosState.sell and (psarLagCross == 1) else na
    posSide: str = ('buy' if pos.state == ToolsPos.PosState.buy else 'sell') if na(posEnter) and na(posExit) and (not na(pos.state)) else na
    posTP: str = na(str)
    posRE: str = na(str)
    posAction: ToolsPos.PosActionType = na(ToolsPos.PosActionType)
    posLastTP: ToolsPos.PosAction = na(ToolsPos.PosAction)
    posLastRE: ToolsPos.PosAction = na(ToolsPos.PosAction)
    upBoEligible: bool = close[1] > open[1] and close <= open
    downBoEligible: bool = close[1] < open[1] and close >= open

    if not na(posExit):
        method_call('exit', pos)
        marksTP = na
        marksRE = na

    if not na(posEnter):
        method_call('enter', pos, ToolsPos.PosState.buy if posEnter == 'buy' else ToolsPos.PosState.sell, psar_lagging)
        marksTP = array.new_int()
        marksRE = array.new_int()

    method_call('eval', fracs, fracSrcHigh, fracSrcLow, fracLbHigh, fracLbLow, pos.when if not na(pos.when) else time, pos.when if not na(pos.when) else time)

    if not na(posSide):
        posLastTP = array.last(pos.tp) if array.size(pos.tp) > 0 else na
        posLastRE = array.last(pos.re) if array.size(pos.re) > 0 else na

        if array.size(fracs.hh) > 0 and upBoEligible and (posSide == 'buy' or (posSide == 'sell' and (sigReSellNoTp or not na(posLastTP)))):
            fracHHFrom: int = math.max(0, array.size(fracs.hh) - fracLbHigh)
            fracHHTo: int = array.size(fracs.hh) - 1
            for i in pine_range(fracHHFrom, fracHHTo, 1):
                fracHH: Tac.BWFractal = method_call('get', fracs.hh, i)
                if na(fracHH.boPrice) or fracHH.boTime < pos.when:
                    continue

                posTP = 'buy' if posSide == 'buy' and close > pos.price and (array.binary_search(marksTP, fracHH.when) == -1) and (na(posLastTP) or close > posLastTP.price) else na
                posRE = 'sell' if posSide == 'sell' and psarProximity > sigReMinProximity and (array.binary_search(marksRE, fracHH.when) == -1) and (not na(posLastTP) or sigReSellNoTp) and (na(posLastRE) or close > posLastRE.price) else na
                if posTP == 'buy' or posRE == 'sell':
                    posActionFrac = fracHH
                    break

        if array.size(fracs.ll) > 0 and downBoEligible and (posSide == 'sell' or (posSide == 'buy' and (sigReBuyNoTp or not na(posLastTP)))):
            fracLLFrom: int = math.max(0, array.size(fracs.ll) - fracLbLow)
            fracLLTo: int = array.size(fracs.ll) - 1
            for i in pine_range(fracLLFrom, fracLLTo, 1):
                fracLL: Tac.BWFractal = array.get(fracs.ll, i)
                if na(fracLL.boPrice) or fracLL.boTime < pos.when:
                    continue

                posTP = 'sell' if posSide == 'sell' and close < pos.price and (array.binary_search(marksTP, fracLL.when) == -1) and (na(posLastTP) or close < posLastTP.price) else na
                posRE = 'buy' if posSide == 'buy' and psarProximity > sigReMinProximity and (array.binary_search(marksRE, fracLL.when) == -1) and (not na(posLastTP) or sigReSellNoTp) and (na(posLastRE) or close < posLastRE.price) else na
                if posTP == 'sell' or posRE == 'buy':
                    posActionFrac = fracLL
                    break

    if not na(posTP) or not na(posRE):
        posAction = ToolsPos.PosActionType.re if na(posTP) else ToolsPos.PosActionType.tp
        method_call('action', pos, posAction, close, time, bar_index, posActionFrac.price, posActionFrac.when, posActionFrac.index)

        if posAction == ToolsPos.PosActionType.tp:
            array.push(marksTP, posActionFrac.when)

        if posAction == ToolsPos.PosActionType.re:
            array.push(marksRE, posActionFrac.when)

    sInitSize: Persistent[float] = na(float)
    sInitId: Persistent[str] = na(str)
    sExitId: Persistent[str] = na(str)
    sReTrigger: Persistent[float] = na(float)

    isInTimeRange: bool = time >= sFrom and time <= sTo
    prepEnterBuy: bool = isInTimeRange and psar_lagging[1] > high[1] and posAllowBuy
    prepEnterSell: bool = isInTimeRange and psar_lagging[1] < low[1] and posAllowSell
    sSize: float = math.abs(strategy.position_size)

    if prepEnterBuy or prepEnterSell:
        strategy.entry('Long' if prepEnterBuy else 'Short', strategy.long if prepEnterBuy else strategy.short, stop=psar_fast)

    if strategy.opentrades > 0 and strategy.opentrades.entry_time(strategy.opentrades - 1) == time:
        sInitSize = math.abs(strategy.position_size)
        sInitId = strategy.opentrades.entry_id(strategy.opentrades - 1)
        sExitId = 'Short' if sInitId == 'Long' else 'Long'
        sReTrigger = (sInitSize if reWhenRate == 100 else sInitSize / 100 * reWhenRate) if reWhenRate > 0 and reFillRate > 0 else na

    if strategy.opentrades > 0 and barstate.isconfirmed:
        if not na(posTP) and tpReductionRate > 0:
            strategy.close(sInitId, comment='TP', qty=sSize / 100 * tpReductionRate, immediately=True)
        elif not na(posRE) and (not na(sReTrigger)) and (sSize < sReTrigger) and (sSize < sInitSize / 100 * reFillRate):
            sReQty: float = sInitSize if reFillRate == 100 else sInitSize / 100 * reFillRate - sSize
            strategy.order('RE-' + sInitId, comment='RE', direction=strategy.long if sInitId == 'Long' else strategy.short, stop=close, qty=sReQty)

    if strategy.opentrades > 0 and strategy.opentrades.entry_time(strategy.opentrades - 1) < time and (posDir != 'Buy & Sell'):
        strategy.exit('Exit-' + sInitId, from_entry=sInitId, stop=psar_fast, qty=sSize)

    plotshape(showEntryBuy and posEnter == 'buy', style=shape.labelup, location=location.belowbar, color=color.green, size=size.tiny, title='BUY', text='BUY', textcolor=color.white, force_overlay=True)
    plotshape(showExitBuy and posExit == 'buy', style=shape.labelup, location=location.belowbar, color=color.green, size=size.tiny, title='EXIT BUY', text='EXIT BUY', textcolor=color.white, force_overlay=True)
    plotshape(showTpBuy and posTP == 'buy', style=shape.labeldown, location=location.abovebar, color=color.teal, size=size.tiny, title='BUY TP', text='TP', textcolor=color.white, force_overlay=True)
    plotshape(showReBuy and posRE == 'buy', style=shape.labelup, location=location.belowbar, color=color.olive, size=size.tiny, title='BUY RE', text='RE', textcolor=color.white, force_overlay=True)

    plotshape(showEntrySell and posEnter == 'sell', style=shape.labeldown, location=location.abovebar, color=color.red, size=size.tiny, title='SELL', text='SELL', textcolor=color.white, force_overlay=True)
    plotshape(showExitSell and posExit == 'sell', style=shape.labeldown, location=location.abovebar, color=color.red, size=size.tiny, title='EXIT SELL', text='EXIT SELL', textcolor=color.white, force_overlay=True)
    plotshape(showTpSell and posTP == 'sell', style=shape.labelup, location=location.belowbar, color=color.maroon, size=size.tiny, title='SELL TP', text='TP', textcolor=color.white, force_overlay=True)
    plotshape(showReSell and posRE == 'sell', style=shape.labeldown, location=location.abovebar, color=color.purple, size=size.tiny, title='SELL RE', text='RE', textcolor=color.white, force_overlay=True)

    plot(psar if showPsar else na, title='PSAR', style=plot.style_line, color=color.lime if psar < low else color.red)
    plot(psar_lagging if showPsarLagging else na, title='Lagging PSAR', color=color.yellow if psar_lagging < low else color.fuchsia, style=plot.style_line)
    plot(strategy.position_avg_price if showStrategyAvgPrice else na, title='Strategy Avg Price', color=color.white, style=plot.style_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
