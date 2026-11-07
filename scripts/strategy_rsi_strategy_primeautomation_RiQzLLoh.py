"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.lib import (
    array, bar_index, chart, close, color, fill, high, hour, input, label,
    low, math, minute, na, open, plot, request, script, strategy, string, syminfo, ta, time,
    timeframe, timenow, timestamp, volume
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series

OpSettings: str = "➞ Optimization Settings 🔸"
OpSettings1: str = "➞ Settings 🔸"


@script.strategy("RSI Strategy [PrimeAutomation]", overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.06, initial_capital=10000, margin_long=0, margin_short=0, process_orders_on_close=True, pyramiding=0)
def main(
    startTime=input.time(timestamp('01-01-2023'), "Strategy Start Date", group=OpSettings1),
    MarketClosed=input.bool(False, "Exit before market close", group=OpSettings1),
    len=input.int(40, minval=1, title="RSI Length", group=OpSettings),
    upper=input.int(60, "Upper", group=OpSettings),
    lower=input.int(35, "Lower", group=OpSettings),
    multiStop=input.float(4, "Trail Stop", step=0.1, group="TP/SL"),
    useTP=input.bool(True, "Take Profit", group="TP/SL", inline="tp"),
    multiTP=input.float(7, "", step=0.1, group="TP/SL", inline="tp")
):
    StartTIME: Persistent[int] = 0
    totaltrades = strategy.closedtrades
    PNL = strategy.netprofit_percent + strategy.openprofit_percent
    WinRate = strategy.wintrades / totaltrades * 100
    MaxDraw = strategy.max_drawdown_percent

    Con: Series = strategy.closedtrades == 0 and strategy.opentrades == 1
    StartTIME = ta.valuewhen(Con and (not Con[1]), time, 0)

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

    newDay = ta.change(time('D')) != 0
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
    ShortEntryMSG: str = '{"ticker": "{{ticker}}","action": "sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}" ,"TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'
    ShortExitMSG: str = '{"ticker": "{{ticker}}","action": "exit_sell","price": "{{close}}", "time": "{{timenow}}", "size": "{{size}}", "per": "{{per}}", "sl": "{{sl}}", "tp": "{{tp}}" ,"TotalTrades":  "{{TotalTrades}}" ,"PNL": "{{PNL}}", "WinRate":  "{{WinRate}}", "MaxDraw": "{{MaxDraw}}", "StartDate":  "{{StartDate}}", "DailyPNL": "{{DailyPnl}}"}'

    currentSize: Persistent[float] = na(float)
    isNewTrade = strategy.opentrades > strategy.opentrades[1]

    if isNewTrade:
        currentSize = math.abs(strategy.opentrades.size(strategy.opentrades - 1))

    MarketisClose = MC()

    rsi: Series = ta.rsi(close, len)

    trend: PersistentSeries[bool] = False

    tp1: Persistent = NA(float)
    stop: Persistent = NA(float)
    stop1: Persistent = NA(float)

    enter: Persistent = NA(float)
    isLong: Persistent = NA(bool)

    atr = ta.atr(200) * multiStop
    atr1 = ta.atr(200) * multiTP

    inTrade: Persistent[bool] = False
    startL: Persistent[int] = 0

    Buy = ta.crossover(rsi, upper)
    Sell = ta.crossunder(rsi, lower)

    trailActivation = close - atr
    trailDistance = atr

    BuyExit = low < stop and isLong
    SellExit = high > stop and (not isLong)

    TPLong = ta.crossover(high, tp1) and isLong
    TPShort = ta.crossunder(low, tp1) and (not isLong)

    isTrailing: bool = True

    if time >= startTime and bar_index > 200:
        if strategy.opentrades == 0:
            stop = NA(float)
            tp1 = NA(float)
            enter = NA(float)
            inTrade = False
            stop1 = NA(float)

        if Buy and (not inTrade if useTP or isTrailing else True):
            label.new(bar_index - 1, rsi[1], '◆\nLONG', color=NA(Color), textcolor=chart.fg_color, style=label.style_label_up)

            stop = NA(float)
            stop = close - atr
            stop1 = stop
            isLong = True

            if useTP:
                tp1 = close + atr1

            enter = close
            inTrade = True

            strategy.close('Short', 'Short Exit', alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Long', strategy.long, comment='Long', alert_message=parseing(LongEntryMSG, size__ren__=currentSize))

        if Sell and (not inTrade if useTP or isTrailing else True):
            label.new(bar_index - 1, rsi[1], 'SHORT\n◆', color=NA(Color), textcolor=chart.fg_color, style=label.style_label_down)

            stop = NA(float)
            stop = close + atr
            stop1 = stop
            isLong = False

            if useTP:
                tp1 = close - atr1

            enter = close
            inTrade = True

            strategy.close('Long', 'Long Exit', alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
            strategy.entry('Short', strategy.short, comment='Short', alert_message=parseing(ShortEntryMSG, size__ren__=currentSize))

        txtStopL: str = "Long Exit"
        txtStopS: str = "Short Exit"

        strategy.exit(txtStopL, 'Long', stop=stop1, qty_percent=100, alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
        strategy.exit(txtStopS, 'Short', stop=stop1, qty_percent=100, alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))

        strategy.exit(txtStopL, 'Long', limit=tp1, stop=stop, qty_percent=100, alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
        strategy.exit(txtStopS, 'Short', limit=tp1, stop=stop, qty_percent=100, alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))

        if BuyExit:
            strategy.close('Long', txtStopL, alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)), immediately=True)

        if SellExit:
            strategy.close('Short', txtStopS, alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)), immediately=True)

        if inTrade and isTrailing:
            if isLong:
                stop = math.max(stop, low - atr)
            else:
                stop = math.min(stop, high + atr)

    if MarketClosed and MarketClosed:
        if strategy.position_size > 0:
            strategy.close('Long', 'Long Exit', alert_message=parseing(LongExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))
        else:
            strategy.close('Short', 'Short Exit', alert_message=parseing(ShortExitMSG, per=100, size__ren__=math.abs(strategy.position_size)))

    ps = plot(na if trend != trend[1] else stop, 'Trail Stop', color=color.red, style=plot.style_linebr, force_overlay=True)
    pt = plot(na if trend != trend[1] else tp1, 'Take Profit', color=color.green, style=plot.style_linebr, force_overlay=True)
    pe = plot(na if trend != trend[1] else enter, 'Entery Price', color=chart.fg_color, style=plot.style_linebr, force_overlay=True)

    fill(pe, pt, tp1, enter, NA(Color), color.new(color.green, 80))
    fill(pe, ps, stop, enter, NA(Color), color.new(color.red, 80))

    plot(rsi, 'RSI', color=color.purple, linewidth=2)

    pu = plot(upper, 'Upper threshold', color=color.green)
    pl = plot(lower, 'Lower threshold', color=color.red)
    pm = plot(50, 'Mid Line', color=chart.fg_color)

    fill(pm, pu, upper, 50, NA(Color), color.new(color.green, 80))
    fill(pm, pl, lower, 50, NA(Color), color.new(color.red, 80))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
