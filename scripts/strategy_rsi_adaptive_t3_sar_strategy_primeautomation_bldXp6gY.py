"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_method import method
from pynecore.lib import (
    array, chart, close, color, fill, high, hour, input, location, low, math,
    minute, na, nz, open, plot, plotchar, request, script, strategy, string, syminfo, ta, time,
    timeframe, timenow, timestamp, volume
)
from pynecore.types import NA, Persistent, PersistentSeries, Series
import lib.TradingView.ta.v7 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

OpSettings1: str = "➞ Settings 🔸"


@script.strategy("RSI-Adaptive T3 & SAR Strategy [PrimeAutomation]", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.06, initial_capital=10000, margin_long=0, margin_short=0, process_orders_on_close=True, pyramiding=0)
def main(
    startTime=input.time(timestamp('01-01-2023'), "Strategy Start Date", group=OpSettings1),
    MarketClosed=input.bool(False, "Exit before market close", group=OpSettings1),
    rsiLen=input.int(14, 'RSI Length', group="T3"),
    minLen=input.int(5, 'Min T3 Length', group="T3"),
    maxLen=input.int(50, 'Max T3 Length', group="T3"),
    v=input.float(0.7, 'T3 Volume Factor', step=0.01, maxval=2, minval=0.1, group="T3"),
    start=input.float(0.02, step=0.0001, group="SAR Filter"),
    increment=input.float(0.0002, step=0.00011, group="SAR Filter"),
    maximum=input(0.21, group="SAR Filter"),
    stopLen=input.int(10, "Stop Loss Length"),
    color_up=input.color(color.new('#21B8F3'), "", inline="col"),
    color_dn=input.color(color.new('#FD761B'), "", inline="col")
):
    OpSettings: str = "➞ Optimization Settings 🔸"

    StartTIME: Persistent[int] = 0
    totaltrades = strategy.closedtrades
    PNL = strategy.netprofit_percent + strategy.openprofit_percent
    WinRate = strategy.wintrades / totaltrades * 100
    MaxDraw = strategy.max_drawdown_percent

    Con: Series = strategy.closedtrades == 0 and strategy.opentrades == 1
    StartTIME = ta__ren__.valuewhen(Con and (not Con[1]), time, 0)

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

    def MC():
        hr = hour == 15
        min = minute == 55
        _Hr = request.security(syminfo.tickerid, '5', hr)
        _min = request.security(syminfo.tickerid, '5', min)
        MClose = _Hr and _min
        return MClose

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
    LongExitMSG: str = '{"ticker": "{{ticker}}","action": "exit_buy","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}", "per": "{{per}}", "sl": "{{sl}}", "tp": "{{tp}}","TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    ShortEntryMSG: str = '{"ticker": "{{ticker}}","action": "sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}","TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    ShortExitMSG: str = '{"ticker": "{{ticker}}","action": "exit_sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}", "per": "{{per}}", "sl": "{{sl}}", "tp": "{{tp}}","TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'

    currentSize: Persistent[float] = na(float)
    isNewTrade = strategy.opentrades > strategy.opentrades[1]

    if isNewTrade:
        currentSize = math.abs(strategy.opentrades.size(strategy.opentrades - 1))

    MarketisClose = MC()

    src = close

    rsi = ta__ren__.rsi(src, rsiLen)
    rsi_scale = 1 - rsi / 100
    len = math.round(minLen + (maxLen - minLen) * rsi_scale)

    def pine_ema(src, length):
        alpha = 2 / (length + 1)
        sum: Series[float] = 0.0
        sum = src if na(sum[1]) else alpha * src + (1 - alpha) * nz(sum[1])
        return sum

    e1 = pine_ema(src, len)
    e2 = pine_ema(e1, len)
    e3 = pine_ema(e2, len)
    e4 = pine_ema(e3, len)
    e5 = pine_ema(e4, len)
    e6 = pine_ema(e5, len)

    c1 = -v * v * v
    c2 = 3 * v * v + 3 * v * v * v
    c3 = -6 * v * v - 3 * v - 3 * v * v * v
    c4 = 1 + 3 * v + v * v * v + 3 * v * v
    t3: Series = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    t3_col = color_up if t3 > t3[2] else color_dn

    L = ta__ren__.lowest(stopLen)
    H = ta__ren__.highest(stopLen)

    sar = ta__ren__.sar(start, increment, maximum)

    Long: Series = close > sar

    Buy = ta__ren__.crossover(t3, t3[2]) and Long and (strategy.position_size <= 0)
    Sell = ta__ren__.crossunder(t3, t3[2]) and (not Long) and (strategy.position_size >= 0)

    BuyExit = ta__ren__.crossunder(t3, t3[2])
    SellExit = ta__ren__.crossover(t3, t3[2])

    plot(NA(float) if Long != Long[1] else sar, 'SAR Filter', linewidth=2, color=color_up if close > sar else color_dn, style=plot.style_circles)

    plotchar(t3 if Buy or Sell else na, '', '🞛', location.absolute, t3_col)
    pt31 = plot(t3, 'T3', color=t3_col, linewidth=1, editable=True)
    pt32 = plot(t3[2], 'T3', color=t3_col, linewidth=1, editable=True)
    fill(pt31, pt32, color.new(t3_col, 90))

    stop: PersistentSeries = NA(float)

    if time >= startTime:
        if strategy.opentrades == 0:
            stop = NA(float)

        if Buy:
            strategy.close('Short', 'Short Exit', alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Long', strategy.long, comment='Long', alert_message=parseing(LongEntryMSG, size__ren__=currentSize))
            stop = L
        if Sell:
            strategy.close('Long', 'Long Exit', alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Short', strategy.short, comment='Short', alert_message=parseing(ShortEntryMSG, size__ren__=currentSize))
            stop = H

        strategy.exit('Long Stop', 'Long', qty_percent=100, stop=stop, alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
        strategy.exit('Short Stop', 'Short', qty_percent=100, stop=stop, alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))

    plot(NA(float) if stop != stop[1] else stop, 'Stop', color=chart.fg_color, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
