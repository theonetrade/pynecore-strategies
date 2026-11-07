"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barstate, close, color, format, high, input,
    label, line, location, low, math, na, plotshape, position, request, script, shape, size,
    strategy, string, syminfo, ta, table, text, time, timeframe
)
from pynecore.types import Label, Line, Persistent, Table


@script.strategy("Bmm Liberty - Strategy Elite", overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main(
    licenseID=input.string("", "License ID (optional)", group="Core Settings"),
    riskvalue=input.float(0.1, "Risk Value", group="Core Settings"),
    only_multitimeframe=input.bool(True, "Require multi-TF majority for signals", group="Core Settings"),
    min_bull=input.int(3, "Min bullish TFs for Buy", minval=1, group="Core Settings"),
    min_bear=input.int(3, "Min bearish TFs for Sell", minval=1, group="Core Settings"),
    show_dashboard=input.bool(True, "Show Dashboard", group="Visual Settings"),
    show_mtf_table=input.bool(True, "Show MTF Table", group="Visual Settings"),
    use_entry_alert=input.bool(True, "Enable Signal Alerts (JSON)", group="Alert Settings"),
    use_fill_alert=input.bool(True, "Enable Order Fill Alerts", group="Alert Settings"),
    entry_alert_text=input.string("Fill: {{strategy.order.action}} on {{ticker}}", "Order Fill Message", group="Alert Settings"),
    tradeDirection=input.string("Both", "Trade Direction", options=("Both", "Long Only", "Short Only"), group="Trade Filters"),
    sessionMode=input.string("All", "Trading Session", options=("All", "London", "New York", "Custom"), group="Trade Filters"),
    customSession=input.session("0900-1700", "Custom Time Range", group="Trade Filters"),
    rr1=input.float(1.0, "Take Profit 1 (RR)", group="Exit Levels"),
    rr2=input.float(2.0, "Take Profit 2 (RR)", group="Exit Levels"),
    lineLength=input.int(20, "Line Length (bars)", group="Exit Levels"),
    htf1=input.timeframe("1", "TF 1", group="Multi-Timeframe"),
    htf2=input.timeframe("5", "TF 2", group="Multi-Timeframe"),
    htf3=input.timeframe("15", "TF 3", group="Multi-Timeframe"),
    htf4=input.timeframe("60", "TF 4", group="Multi-Timeframe"),
    htf5=input.timeframe("240", "TF 5", group="Multi-Timeframe"),
    htf6=input.timeframe("D", "TF 6", group="Multi-Timeframe"),
    htfEmaLen=input.int(50, "HTF EMA Trend Length", group="Multi-Timeframe")
):
    rsiVal = ta.rsi(close, 14)
    macdVal = ta.ema(close, 12) - ta.ema(close, 26)
    atrVal = ta.atr(14)
    vwapVal = ta.vwap
    posChange = ta.change(strategy.position_size)

    st_val, st_dir = ta.supertrend(2.0, 1)
    base_buySignal = ta.change(st_dir) < 0
    base_sellSignal = ta.change(st_dir) > 0

    def f_htf_trend(tf):
        c = request.security(syminfo.tickerid, tf, close)
        e = request.security(syminfo.tickerid, tf, ta.ema(close, htfEmaLen))
        return 1 if c > e else -1 if c < e else 0

    t1 = f_htf_trend(htf1)
    t2 = f_htf_trend(htf2)
    t3 = f_htf_trend(htf3)
    t4 = f_htf_trend(htf4)
    t5 = f_htf_trend(htf5)
    t6 = f_htf_trend(htf6)

    bull_count = (1 if t1 == 1 else 0) + (1 if t2 == 1 else 0) + (1 if t3 == 1 else 0) + (1 if t4 == 1 else 0) + (1 if t5 == 1 else 0) + (1 if t6 == 1 else 0)
    bear_count = (1 if t1 == -1 else 0) + (1 if t2 == -1 else 0) + (1 if t3 == -1 else 0) + (1 if t4 == -1 else 0) + (1 if t5 == -1 else 0) + (1 if t6 == -1 else 0)

    __block_result__ = na
    __switch__ = sessionMode
    if __switch__ == "All":
        __block_result__ = True
    elif __switch__ == "London":
        __block_result__ = not na(time(timeframe.period, '0700-1600:1234567'))
    elif __switch__ == "New York":
        __block_result__ = not na(time(timeframe.period, '1330-2000:1234567'))
    elif __switch__ == "Custom":
        __block_result__ = not na(time(timeframe.period, customSession + ':1234567'))
    else:
        __block_result__ = True
    isAllowed = __block_result__

    enter_buy = base_buySignal and (not only_multitimeframe or bull_count >= min_bull) and isAllowed and (tradeDirection != 'Short Only')
    enter_sell = base_sellSignal and (not only_multitimeframe or bear_count >= min_bear) and isAllowed and (tradeDirection != 'Long Only')

    dashboardTable: Persistent[Table] = table.new(position.bottom_right, 2, 8, border_width=1, frame_color=color.gray, border_color=color.gray)
    mtfTable: Persistent[Table] = table.new(position.top_right, 3, 8, border_width=1, frame_color=color.gray, border_color=color.gray)

    if barstate.islast:
        table.clear(dashboardTable, 0, 0, 1, 7)
        table.clear(mtfTable, 0, 0, 2, 7)

        if show_dashboard:
            table.cell(dashboardTable, 0, 0, 'MTF BULL', bgcolor=color.new('#089981'), text_color=color.white, text_halign=text.align_left)
            table.cell(dashboardTable, 1, 0, string.tostring(bull_count) + '/6', bgcolor=color.new('#089981'), text_color=color.white)
            table.cell(dashboardTable, 0, 1, 'MTF BEAR', bgcolor=color.new('#F23645'), text_color=color.white, text_halign=text.align_left)
            table.cell(dashboardTable, 1, 1, string.tostring(bear_count) + '/6', bgcolor=color.new('#F23645'), text_color=color.white)
            table.cell(dashboardTable, 0, 2, 'VWAP Bias', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 2, 'BULL' if close > vwapVal else 'BEAR', text_color=color.green if close > vwapVal else color.red)
            table.cell(dashboardTable, 0, 3, 'RSI (14)', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 3, string.tostring(rsiVal, '#.##'), text_color=color.green if rsiVal > 50 else color.red)
            table.cell(dashboardTable, 0, 4, 'MACD Trend', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 4, 'BULL' if macdVal > 0 else 'BEAR', text_color=color.green if macdVal > 0 else color.red)
            table.cell(dashboardTable, 0, 5, 'ATR Risk', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 5, string.tostring(atrVal, format.mintick))
            table.cell(dashboardTable, 0, 6, 'Status', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 6, 'IN TRADE' if strategy.position_size != 0 else 'WAIT')
            table.cell(dashboardTable, 0, 7, 'Sniper', text_halign=text.align_left)
            table.cell(dashboardTable, 1, 7, 'BMM SNIPER', text_color=color.blue)

        if show_mtf_table:
            table.cell(mtfTable, 0, 0, 'TF', bgcolor=color.gray, text_color=color.white)
            table.cell(mtfTable, 1, 0, 'Trend', bgcolor=color.gray, text_color=color.white)
            table.cell(mtfTable, 2, 0, 'Bull?', bgcolor=color.gray, text_color=color.white)
            tfs: list[str] = array.from_items(htf1, htf2, htf3, htf4, htf5, htf6)
            trs = array.from_items(t1, t2, t3, t4, t5, t6)
            for i in pine_range(0, 5):
                tr = array.get(trs, i)
                txt = 'Bullish' if tr == 1 else 'Bearish' if tr == -1 else 'Neutral'
                clr = color.green if tr == 1 else color.red if tr == -1 else color.gray
                table.cell(mtfTable, 0, i + 1, array.get(tfs, i), bgcolor=color.new(color.gray, 80))
                table.cell(mtfTable, 1, i + 1, txt, text_color=clr, bgcolor=color.new(color.gray, 80))
                table.cell(mtfTable, 2, i + 1, 'YES' if tr == 1 else 'NO', bgcolor=color.new(color.gray, 80))
            majTxt = 'BULL' if bull_count > bear_count else 'BEAR'
            table.cell(mtfTable, 0, 7, 'Majority')
            table.cell(mtfTable, 1, 7, string.tostring(bull_count) + ' / 6')
            table.cell(mtfTable, 2, 7, majTxt, text_color=color.green if majTxt == 'BULL' else color.red)

    l_tp1: Persistent[Line] = na(Line)
    l_tp2: Persistent[Line] = na(Line)
    l_sl: Persistent[Line] = na(Line)
    l_ent: Persistent[Line] = na(Line)
    lb_tp1: Persistent[Label] = na(Label)
    lb_tp2: Persistent[Label] = na(Label)
    lb_sl: Persistent[Label] = na(Label)
    lb_ent: Persistent[Label] = na(Label)

    def f_delete_levels():
        line.delete(l_tp1)
        line.delete(l_tp2)
        line.delete(l_sl)
        line.delete(l_ent)
        label.delete(lb_tp1)
        label.delete(lb_tp2)
        label.delete(lb_sl)
        return label.delete(lb_ent)

    if enter_buy or enter_sell:
        f_delete_levels()
        isB = enter_buy
        p_ent = close
        p_sl = st_val
        dist = math.abs(p_ent - p_sl)
        p_tp1 = p_ent + dist * rr1 if isB else p_ent - dist * rr1
        p_tp2 = p_ent + dist * rr2 if isB else p_ent - dist * rr2

        l_tp1 = line.new(bar_index, p_tp1, bar_index + lineLength, p_tp1, color=color.new(color.new('#089981'), 0), style=line.style_dashed, width=1)
        l_tp2 = line.new(bar_index, p_tp2, bar_index + lineLength, p_tp2, color=color.new(color.new('#089981'), 0), style=line.style_dashed, width=1)
        l_sl = line.new(bar_index, p_sl, bar_index + lineLength, p_sl, color=color.red, style=line.style_dashed, width=1)
        l_ent = line.new(bar_index, p_ent, bar_index + lineLength, p_ent, color=color.gray, style=line.style_dashed, width=1)

        lb_tp1 = label.new(bar_index + lineLength, p_tp1, 'TP1: ' + string.tostring(p_tp1, format.mintick), color=color.new('#089981'), textcolor=color.white, style=label.style_label_left, size=size.small)
        lb_tp2 = label.new(bar_index + lineLength, p_tp2, 'TP2: ' + string.tostring(p_tp2, format.mintick), color=color.new('#089981'), textcolor=color.white, style=label.style_label_left, size=size.small)
        lb_sl = label.new(bar_index + lineLength, p_sl, 'SL: ' + string.tostring(p_sl, format.mintick), color=color.red, textcolor=color.white, style=label.style_label_left, size=size.small)
        lb_ent = label.new(bar_index + lineLength, p_ent, 'Entry: ' + string.tostring(p_ent, format.mintick), color=color.gray, textcolor=color.white, style=label.style_label_left, size=size.small)

        if isB:
            strategy.entry('Long', strategy.long, alert_message=entry_alert_text)
            label.new(bar_index, low, 'Long\n+' + string.tostring(close, format.mintick), color=color.new('#00000000'), textcolor=color.gray, style=label.style_label_up, size=size.small)
            label.new(bar_index, low * 0.998, 'BUY', color=color.new('#089981'), textcolor=color.white, style=label.style_label_up, size=size.small)
        else:
            strategy.entry('Short', strategy.short, alert_message=entry_alert_text)
            label.new(bar_index, high, 'Short\n-' + string.tostring(close, format.mintick), color=color.new('#00000000'), textcolor=color.gray, style=label.style_label_down, size=size.small)
            label.new(bar_index, high * 1.002, 'SELL', color=color.red, textcolor=color.white, style=label.style_label_down, size=size.small)

        if use_entry_alert:
            json_payload = '{"license":"' + licenseID + '","action":"' + ('buy' if isB else 'sell') + '","ticker":"' + syminfo.ticker + '","risk":' + string.tostring(riskvalue) + ',"price":' + string.tostring(p_ent) + '}'
            alert(json_payload, alert.freq_once_per_bar_close)

    if not na(l_ent):
        line.set_x2(l_tp1, bar_index + lineLength)
        line.set_x2(l_tp2, bar_index + lineLength)
        line.set_x2(l_sl, bar_index + lineLength)
        line.set_x2(l_ent, bar_index + lineLength)
        label.set_x(lb_tp1, bar_index + lineLength)
        label.set_x(lb_tp2, bar_index + lineLength)
        label.set_x(lb_sl, bar_index + lineLength)
        label.set_x(lb_ent, bar_index + lineLength)

    if ta.change(strategy.position_size != 0) and strategy.position_size == 0:
        f_delete_levels()

    if use_fill_alert and posChange != 0:
        alert('Order Fill Event: Position size is now ' + string.tostring(strategy.position_size), alert.freq_all)

    plotshape(enter_buy, 'Buy Arrow', style=shape.arrowup, location=location.belowbar, color=color.blue, size=size.normal)
    plotshape(enter_sell, 'Sell Arrow', style=shape.arrowdown, location=location.abovebar, color=color.red, size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
