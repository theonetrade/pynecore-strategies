"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_method import method
from pynecore.lib import (
    array, barstate, chart, close, color, fill, high, hour, input, low, math,
    minute, na, nz, open, plot, request, script, strategy, string, syminfo, ta, time, timeframe,
    timenow, timestamp, volume
)
from pynecore.types import Persistent, PersistentSeries, Series
import lib.TradingView.ta.v7 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

OpSettings1: str = "➞ Settings 🔸"
gTP: str = "Take Profit"


@script.strategy(title="DEMA ATR Strategy [PrimeAutomation]", shorttitle="DEMA ATR Strategy [PrimeAutomation]", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.06, initial_capital=10000, margin_long=0, margin_short=0, process_orders_on_close=True, pyramiding=0)
def main(
    startTime=input.time(timestamp('01-01-2023'), "Strategy Start Date", group=OpSettings1),
    MarketClosed=input.bool(False, "Exit before market close", group=OpSettings1),
    periodDema=input.int(75, "Dema Period", group="Dema Atr"),
    periodAtr=input.int(20, "ATR Period", group="Dema Atr", step=1),
    factorAtr=input.float(1.2, "ATR Factor", step=0.05, group="Dema Atr"),
    useTP=input.bool(True, "Take Profit", group=gTP, inline="tp"),
    factorTP=input.float(3, "", step=0.1, group=gTP, inline="tp"),
    tp1Size=input.int(30, "TP1 Size Exit", group=gTP),
    tp2Size=input.int(30, "TP2 Size Exit", group=gTP),
    tp3Size=input.int(40, "TP3 Size Exit", group=gTP)
):
    OpSettings: str = "➞ Optimization Settings 🔸"

    StartTIME: Persistent[int] = 0
    totaltrades = strategy.closedtrades
    PNL = strategy.netprofit_percent + strategy.openprofit_percent
    WinRate = strategy.wintrades / totaltrades * 100
    MaxDraw = strategy.max_drawdown_percent

    Con: Series = strategy.closedtrades == 0 and strategy.opentrades == 1
    StartTIME = ta__ren__.valuewhen(Con and (not Con[1]), time, 0)

    def MC():
        hr = hour == 15
        min = minute == 55
        _Hr = request.security(syminfo.tickerid, '5', hr)
        _min = request.security(syminfo.tickerid, '5', min)
        MClose = _Hr and _min
        return MClose

    dailyPNL: Persistent[float] = na(float)
    maxDays: Persistent[int] = 60
    lastNetProfit: Persistent[float] = na(float)
    PNLS: Persistent[list[str]] = array.new_string()

    newDay = ta__ren__.change(time('D')) != 0
    currentNetProfit = strategy.netprofit

    if newDay:
        if not na(lastNetProfit):
            dailyPNL = currentNetProfit - lastNetProfit

            if dailyPNL != 0:
                dateStr = string.format('{0,date,MM-dd}', time)
                combined = dateStr + ':' + string.tostring(dailyPNL, '#.##')
                array.unshift(PNLS, combined)

                if array.size(PNLS) > maxDays:
                    array.pop(PNLS)

        lastNetProfit = currentNetProfit

    tradesCount = strategy.closedtrades

    LastPNL: float = 0.0
    if tradesCount > 0:
        LastPNL = strategy.closedtrades.profit(tradesCount - 1)

    @method
    def parseing(st: str, tp = 0, sl = 0, size__ren__ = 0, per = 0.0):
        ret: str = st
        ret = string.replace_all(ret, '{{tickerid}}', syminfo.tickerid)
        ret = string.replace_all(ret, '{{ticker}}', syminfo.ticker)
        ret = string.replace_all(ret, '{{exchange}}', syminfo.prefix)
        ret = string.replace_all(ret, '{{close}}', string.tostring(close))
        ret = string.replace_all(ret, '{{open}}', string.tostring(open))
        ret = string.replace_all(ret, '{{high}}', string.tostring(high))
        ret = string.replace_all(ret, '{{low}}', string.tostring(low))
        ret = string.replace_all(ret, '{{time}}', string.format_time(time, 'yyyy-MM-dd HH:mm', syminfo.timezone))
        ret = string.replace_all(ret, '{{timenow}}', string.format_time(timenow, 'yyyy-MM-dd HH:mm', syminfo.timezone))
        ret = string.replace_all(ret, '{{volume}}', string.tostring(volume))
        ret = string.replace_all(ret, '{{interval}}', timeframe.period)
        ret = string.replace_all(ret, '{{country}}', syminfo.country)
        ret = string.replace_all(ret, '{{description}}', syminfo.description)
        ret = string.replace_all(ret, '{{root}}', syminfo.root)
        ret = string.replace_all(ret, '{{industry}}', syminfo.industry)
        ret = string.replace_all(ret, '{{type}}', syminfo.type)
        ret = string.replace_all(ret, '{{tp}}', string.tostring(tp))
        ret = string.replace_all(ret, '{{sl}}', string.tostring(sl))
        ret = string.replace_all(ret, '{{size}}', string.tostring(size__ren__))
        ret = string.replace_all(ret, '{{per}}', string.tostring(per))
        ret = string.replace_all(ret, '{{TotalTrades}}', string.tostring(strategy.closedtrades))
        ret = string.replace_all(ret, '{{PNL}}', string.tostring(strategy.netprofit_percent + strategy.openprofit_percent, '#.##'))
        ret = string.replace_all(ret, '{{WinRate}}', string.tostring(strategy.wintrades / totaltrades * 100, '#.##'))
        ret = string.replace_all(ret, '{{MaxDraw}}', string.tostring(strategy.max_drawdown_percent, '#.##'))
        ret = string.replace_all(ret, '{{StartDate}}', string.format('{0,date,medium}', StartTIME))
        ret = string.replace_all(ret, '{{DailyPnl}}', string.tostring(dailyPNL, '#.##'))
        ret = string.replace_all(ret, '{{historyPNL}}', string.tostring(PNLS))
        ret = string.replace_all(ret, '{{LastPNL}}', string.tostring(LastPNL))
        return ret

    LongEntryMSG: str = '{"ticker": "{{ticker}}","action": "buy","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}","TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    LongExitMSG: str = '{"ticker": "{{ticker}}","action": "exit_buy","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}", "per": "{{per}}", "sl": "{{sl}}", "tp": "{{tp}}" ,"TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    ShortEntryMSG: str = '{"ticker": "{{ticker}}","action": "sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}","TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    ShortExitMSG: str = '{"ticker": "{{ticker}}","action": "exit_sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}", "per": "{{per}}", "sl": "{{sl}}", "tp": "{{tp}}" ,"TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'

    currentSize: Persistent[float] = na(float)
    isNewTrade = strategy.opentrades > strategy.opentrades[1]

    if isNewTrade:
        currentSize = math.abs(strategy.opentrades.size(strategy.opentrades - 1))

    MarketisClose = MC()

    demaOut = ta__ren__.dema(close, periodDema)

    trueRange = ta__ren__.atr(periodAtr) * factorAtr

    DemaAtr: Series = demaOut
    DemaAtr = nz(DemaAtr[1], DemaAtr)

    trueRangeUpper = demaOut + trueRange
    trueRangeLower = demaOut - trueRange

    if trueRangeLower > DemaAtr:
        DemaAtr = trueRangeLower
    if trueRangeUpper < DemaAtr:
        DemaAtr = trueRangeUpper

    color__ren__ = color.lime if DemaAtr > DemaAtr[2] else color.new('#E42C2C') if DemaAtr < DemaAtr[2] else color.orange

    longCondition = ta__ren__.crossover(DemaAtr, DemaAtr[2]) and barstate.isconfirmed
    shortCondition = ta__ren__.crossunder(DemaAtr, DemaAtr[2]) and barstate.isconfirmed

    atr = ta__ren__.atr(200) * factorTP

    tp1: Persistent[float] = na(float)
    tp2: Persistent[float] = na(float)
    tp3: Persistent[float] = na(float)

    tp11: Persistent[float] = na(float)
    tp22: Persistent[float] = na(float)
    tp33: Persistent[float] = na(float)
    entr: PersistentSeries[float] = na(float)

    if time >= startTime:
        if longCondition and strategy.position_size <= 0:
            strategy.close('Short', 'Short Exit', alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Long', strategy.long, comment='Long', alert_message=parseing(LongEntryMSG, size__ren__=currentSize))

            if useTP:
                tp1 = close + atr
                tp2 = close + atr * 2
                tp3 = close + atr * 3
                tp11 = na
                tp22 = na
                tp33 = na
                entr = close

        if shortCondition and strategy.position_size > 0:
            strategy.close('Long', 'Long Exit', alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Short', strategy.short, comment='Short', alert_message=parseing(ShortEntryMSG, size__ren__=currentSize))

            if useTP:
                tp11 = close - atr
                tp22 = close - atr * 2
                tp33 = close - atr * 3
                tp1 = na
                tp2 = na
                tp3 = na
                entr = close

        if strategy.position_size > 0:
            if high > tp1:
                strategy.close('Long', 'Long TP1', alert_message=parseing(LongExitMSG, per=tp1Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp1Size)
                tp1 = na

            if high > tp2:
                strategy.close('Long', 'Long TP2', alert_message=parseing(LongExitMSG, per=tp2Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp2Size)
                tp2 = na

            if high > tp3:
                strategy.close('Long', 'Long TP3', alert_message=parseing(LongExitMSG, per=tp3Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp3Size)
                tp3 = na
                entr = na
        else:
            if low < tp11:
                strategy.close('Short', 'Short TP1', alert_message=parseing(ShortExitMSG, per=tp1Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp1Size)
                tp11 = na

            if low < tp22:
                strategy.close('Short', 'Short TP2', alert_message=parseing(ShortExitMSG, per=tp2Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp2Size)
                tp22 = na

            if low < tp33:
                strategy.close('Short', 'Short TP3', alert_message=parseing(ShortExitMSG, per=tp3Size, size__ren__=math.abs(strategy.position_size)), qty_percent=tp3Size)
                tp33 = na
                entr = na

    if MarketClosed and MarketClosed:
        if strategy.position_size > 0:
            strategy.close('Long', 'Long Exit', alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
        else:
            strategy.close('Short', 'Short Exit', alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))

    tpCol = color.lime if strategy.position_size > 0 else color.new('#E42C2C')
    plot(tp1, 'TP1 Long', style=plot.style_linebr, color=tpCol)
    plot(tp2, 'TP2 Long', style=plot.style_linebr, color=tpCol)
    p3 = plot(tp3, 'TP3 Long', style=plot.style_linebr, color=tpCol)

    plot(tp11, 'TP1 Short', style=plot.style_linebr, color=tpCol)
    plot(tp22, 'TP2 Short', style=plot.style_linebr, color=tpCol)
    p33 = plot(tp33, 'TP3 Short', style=plot.style_linebr, color=tpCol)

    pe = plot(na if entr != entr[1] else entr, 'Enter', color=chart.fg_color, style=plot.style_linebr)

    fill(pe, p3, color.new(tpCol, 90))
    fill(pe, p33, color.new(tpCol, 90))

    plot(DemaAtr, color=color__ren__, linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
