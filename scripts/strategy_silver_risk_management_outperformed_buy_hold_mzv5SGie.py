"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barmerge, barstate, bgcolor, close, color, display, high, input,
    location, low, na, open, plot, plotshape, position, request, script, shape, size, strategy,
    string, ta, table, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series, Table


@script.strategy("Silver Always Long + Macro Exit + Flush Protection v2", overlay=True, initial_capital=10000, commission_type=strategy.commission.percent, commission_value=0.1, slippage=2, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0, calc_on_every_tick=False, process_orders_on_close=True)
def main(
    startDate=input.time(timestamp('2021-01-01 00:00 +0000'), "Start date"),
    useDateFilter=input.bool(True, "Use start date filter"),
    silverSlowLen=input.int(150, "Silver EMA slow", minval=1),
    silverRecoveryLen=input.int(75, "Silver recovery EMA", minval=1),
    useSilverTrendExit=input.bool(True, "Use silver trend exit"),
    silverExitBufferPct=input.float(0.0, "Silver exit buffer % under EMA", minval=0.0, step=0.1),
    dxySymbol=input.symbol("TVC:DXY", "DXY symbol"),
    useDxyExit=input.bool(False, "Use DXY exit"),
    dxyLen=input.int(50, "DXY EMA length", minval=1),
    dxyBreakoutLookback=input.int(20, "DXY breakout lookback", minval=2),
    dxyMaxAboveEmaPct=input.float(1.0, "DXY % above EMA for exit", minval=0.0, step=0.1),
    us10ySymbol=input.symbol("TVC:US10Y", "US10Y symbol"),
    useUs10yExit=input.bool(True, "Use US10Y exit"),
    us10yLen=input.int(50, "US10Y EMA length", minval=1),
    us10yBreakoutLookback=input.int(20, "US10Y breakout lookback", minval=2),
    us10yMaxAboveEmaPct=input.float(1.35, "US10Y % above EMA for exit", minval=0.0, step=0.05),
    macroExitBars=input.int(3, "Bars macro stress before exit", minval=1),
    reEntryBars=input.int(1, "Bars calm before re entry", minval=1),
    useFlushExit=input.bool(True, "Use silver flush exit"),
    oneDayFlushPct=input.float(4.5, "One day flush %", minval=0.1, step=0.1),
    twoDayFlushPct=input.float(8.0, "Two day flush %", minval=0.1, step=0.1),
    atrLen=input.int(14, "ATR length", minval=1),
    atrShockMult=input.float(1.8, "ATR shock multiplier", minval=0.1, step=0.1),
    flushCooldownBars=input.int(3, "Bars after flush before normal entry", minval=1),
    volCalmBars=input.int(2, "Bars volatility calm before re entry", minval=1),
    showTable=input.bool(True, "Show status table"),
    showBenchmark=input.bool(True, "Show own Buy & Hold benchmark"),
    showBenchmarkPlot=input.bool(False, "Plot Buy & Hold % in data window")
):
    def f_persist(cond: Series, bars):
        ok: bool = True
        for i in pine_range(0, bars - 1):
            ok = ok and cond[i] == True
        return ok

    inTradeWindow = not useDateFilter or time >= startDate

    silverEmaSlow = ta.ema(close, silverSlowLen)
    silverRecoveryEma = ta.ema(close, silverRecoveryLen)
    silverBelowSlow = close < silverEmaSlow * (1.0 - silverExitBufferPct / 100.0)
    silverTrendExit = useSilverTrendExit and silverBelowSlow

    dxyClose = request.security(dxySymbol, timeframe.period, close, barmerge.gaps_off, barmerge.lookahead_off)
    dxyEma = request.security(dxySymbol, timeframe.period, ta.ema(close, dxyLen), barmerge.gaps_off, barmerge.lookahead_off)
    dxyHighPrev = request.security(dxySymbol, timeframe.period, ta.highest(high[1], dxyBreakoutLookback), barmerge.gaps_off, barmerge.lookahead_off)

    us10yClose = request.security(us10ySymbol, timeframe.period, close, barmerge.gaps_off, barmerge.lookahead_off)
    us10yEma = request.security(us10ySymbol, timeframe.period, ta.ema(close, us10yLen), barmerge.gaps_off, barmerge.lookahead_off)
    us10yHighPrev = request.security(us10ySymbol, timeframe.period, ta.highest(high[1], us10yBreakoutLookback), barmerge.gaps_off, barmerge.lookahead_off)

    dxyAbovePct = (dxyClose - dxyEma) / dxyEma * 100.0 if dxyEma != 0 else 0.0
    us10yAbovePct = (us10yClose - us10yEma) / us10yEma * 100.0 if us10yEma != 0 else 0.0

    dxyStress = useDxyExit and dxyClose > dxyEma and (dxyAbovePct > dxyMaxAboveEmaPct) and (dxyClose > dxyHighPrev)
    us10yStress = useUs10yExit and us10yClose > us10yEma and (us10yAbovePct > us10yMaxAboveEmaPct) and (us10yClose > us10yHighPrev)

    macroStressNow = dxyStress or us10yStress
    macroStressPersist = f_persist(macroStressNow, macroExitBars)

    dxyCalm = not useDxyExit or dxyClose <= dxyEma or dxyAbovePct <= dxyMaxAboveEmaPct
    us10yCalm = not useUs10yExit or us10yClose <= us10yEma or us10yAbovePct <= us10yMaxAboveEmaPct
    macroCalmNow = dxyCalm and us10yCalm
    macroCalmPersist = f_persist(macroCalmNow, reEntryBars)

    oneDayMovePct = (close / close[1] - 1.0) * 100.0 if close[1] != 0 else 0.0
    twoDayMovePct = (close / close[2] - 1.0) * 100.0 if close[2] != 0 else 0.0

    silverAtr = ta.atr(atrLen)
    silverAtrPct = silverAtr / close * 100.0 if close != 0 else 0.0
    rangePct = (high - low) / close * 100.0 if close != 0 else 0.0

    oneDayFlush = oneDayMovePct <= -oneDayFlushPct
    twoDayFlush = twoDayMovePct <= -twoDayFlushPct
    atrShock = rangePct > silverAtrPct * atrShockMult and close < open

    flushShockNow = useFlushExit and (oneDayFlush or twoDayFlush or atrShock)

    barsSinceFlush = ta.barssince(flushShockNow)
    flushRecently = useFlushExit and (not na(barsSinceFlush)) and (barsSinceFlush <= flushCooldownBars)

    volCalmNow = not useFlushExit or rangePct <= silverAtrPct * atrShockMult
    volCalmPersist = f_persist(volCalmNow, volCalmBars)

    flushRecoveryReady = not useFlushExit or not flushRecently or (close > silverRecoveryEma and volCalmPersist)

    exitCondition = inTradeWindow and (silverTrendExit or macroStressPersist or flushShockNow)

    entryCondition = inTradeWindow and strategy.position_size == 0 and (not silverTrendExit) and macroCalmPersist and flushRecoveryReady

    if strategy.position_size > 0 and exitCondition:
        strategy.close('Long')

    if entryCondition:
        strategy.entry('Long', strategy.long)

    bhStartPrice: Persistent[float] = na(float)
    bhStartTime: Persistent[int] = na(int)

    if inTradeWindow and na(bhStartPrice):
        bhStartPrice = close
        bhStartTime = time

    buyHoldReturnPct = (close / bhStartPrice - 1.0) * 100.0 if not na(bhStartPrice) else na

    strategyReturnPct = (strategy.equity / strategy.initial_capital - 1.0) * 100.0
    strategyVsHoldPct = strategyReturnPct - buyHoldReturnPct if not na(buyHoldReturnPct) else na

    plot(silverEmaSlow, 'Silver EMA slow', color=color.blue, linewidth=2)
    plot(silverRecoveryEma, 'Silver recovery EMA', color=color.orange, linewidth=1)

    plotshape(entryCondition, title='Long entry', style=shape.triangleup, location=location.belowbar, color=color.lime, size=size.small, text='Long')
    plotshape(exitCondition and strategy.position_size > 0, title='Exit', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, text='Exit')

    plotshape(flushShockNow, title='Silver flush shock', style=shape.diamond, location=location.abovebar, color=color.yellow, size=size.small, text='Flush')

    bgcolor(color.new(color.red, 88) if macroStressNow else na, title='Macro stress background')
    bgcolor(color.new(color.orange, 88) if flushRecently else na, title='Flush cooldown background')

    plot(buyHoldReturnPct if showBenchmarkPlot else na, 'Own Buy & Hold %', color=color.gray, display=display.data_window)
    plot(strategyReturnPct if showBenchmarkPlot else na, 'Strategy return %', color=color.green, display=display.data_window)
    plot(strategyVsHoldPct if showBenchmarkPlot else na, 'Strategy minus Buy & Hold %', color=color.orange, display=display.data_window)

    statusTable: Persistent[Table] = table.new(position.top_right, 2, 13, border_width=1)

    if showTable and barstate.islast:
        table.cell(statusTable, 0, 0, 'Status', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 0, 'Long' if strategy.position_size > 0 else 'Flat', text_color=color.white, bgcolor=color.green if strategy.position_size > 0 else color.red)

        table.cell(statusTable, 0, 1, 'Strategy return', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 1, string.tostring(strategyReturnPct, '#.##') + '%', text_color=color.white, bgcolor=color.black)

        table.cell(statusTable, 0, 2, 'Own Buy & Hold', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 2, string.tostring(buyHoldReturnPct, '#.##') + '%' if showBenchmark and (not na(buyHoldReturnPct)) else 'na', text_color=color.white, bgcolor=color.black)

        table.cell(statusTable, 0, 3, 'Strategy vs Hold', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 3, string.tostring(strategyVsHoldPct, '#.##') + '%' if showBenchmark and (not na(strategyVsHoldPct)) else 'na', text_color=color.white, bgcolor=color.green if not na(strategyVsHoldPct) and strategyVsHoldPct >= 0 else color.red)

        table.cell(statusTable, 0, 4, 'BH start', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 4, string.format('{0,date,yyyy-MM-dd}', bhStartTime) if not na(bhStartTime) else 'na', text_color=color.white, bgcolor=color.black)

        table.cell(statusTable, 0, 5, 'Silver trend', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 5, 'Weak' if silverTrendExit else 'OK', text_color=color.white, bgcolor=color.red if silverTrendExit else color.green)

        table.cell(statusTable, 0, 6, 'Macro stress', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 6, 'Yes' if macroStressNow else 'No', text_color=color.white, bgcolor=color.red if macroStressNow else color.green)

        table.cell(statusTable, 0, 7, 'DXY stress', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 7, 'Yes' if dxyStress else 'No', text_color=color.white, bgcolor=color.red if dxyStress else color.green)

        table.cell(statusTable, 0, 8, 'US10Y stress', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 8, 'Yes' if us10yStress else 'No', text_color=color.white, bgcolor=color.red if us10yStress else color.green)

        table.cell(statusTable, 0, 9, 'Flush shock', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 9, 'Yes' if flushShockNow else 'No', text_color=color.white, bgcolor=color.orange if flushShockNow else color.green)

        table.cell(statusTable, 0, 10, 'Flush cooldown', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 10, 'Active' if flushRecently else 'No', text_color=color.white, bgcolor=color.orange if flushRecently else color.green)

        table.cell(statusTable, 0, 11, 'Re entry ready', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 11, 'Yes' if flushRecoveryReady and macroCalmPersist else 'No', text_color=color.white, bgcolor=color.green if flushRecoveryReady and macroCalmPersist else color.red)

        table.cell(statusTable, 0, 12, 'US10Y above EMA', text_color=color.white, bgcolor=color.black)
        table.cell(statusTable, 1, 12, string.tostring(us10yAbovePct, '#.##') + '%', text_color=color.white, bgcolor=color.black)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
