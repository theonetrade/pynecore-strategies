"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, close, color, display, hlc3, input, label, math, na, plot,
    request, script, size, strategy, string, syminfo, ta, time, timenow, xloc, yloc
)
from pynecore.types import Label, NA, Persistent


@script.strategy(title='Take profit Multi timeframe', overlay=True, pyramiding=0, initial_capital=10000, default_qty_type=strategy.fixed, default_qty_value=1, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0, margin_long=0, margin_short=0, close_by_id=True)
def main(
    takepercent=input.bool(title='Take profit %', defval=True, group='Set up take profit'),
    takemtf=input.bool(title='Take profit Multi timeframe', defval=False, group='Set up take profit'),
    n1=input(10, 'Channel Length', group='Example Strategy'),
    n2=input(21, 'Average Length', group='Example Strategy'),
    oblv1=input(60, 'Over Bought Lv 1', group='Example Strategy'),
    oblv2=input(53, 'Over Bought Lv 2', group='Example Strategy'),
    oslv1=input(-60, 'Over Sold Lv 1', group='Example Strategy'),
    oslv2=input(-53, 'Over Sold Lv 2', group='Example Strategy'),
    TP1=input.float(3, title='TP1 %', step=0.1, group='Take profit %', inline='1'),
    TP2=input.float(5, title='TP2 %', step=1, group='Take profit %', inline='1'),
    TP3=input.float(8, title='TP3 %', step=1, group='Take profit %', inline='2'),
    TP4=input.float(10, title='TP4 %', step=1, group='Take profit %', inline='2'),
    SL=input.float(5, title='Stop Loss %', step=1, group='Take profit %'),
    qty1=input.float(5, title='% Close At TP1', step=1, group='Take profit %', inline='3'),
    qty2=input.float(5, title='% Close At TP2', step=1, group='Take profit %', inline='3'),
    qty3=input.float(5, title='% Close At TP3', step=1, group='Take profit %', inline='4'),
    qty4=input.float(5, title='% Close At TP4', step=1, group='Take profit %', inline='4'),
    ema_len1=input.int(title='EMA1', defval=100, group='Take profit Mtf'),
    ema_len2=input.int(title='EMA2', defval=200, group='Take profit Mtf'),
    tf1=input.timeframe(title='Timeframe 1', defval='240', group='Take profit Mtf'),
    tf2=input.timeframe(title='Timeframe 2', defval='D', group='Take profit Mtf')
):
    ap = hlc3
    esa = ta.ema(ap, n1)
    d = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)
    buy = ta.crossover(wt1, wt2) and wt1 < -20
    closebuy = ta.crossunder(wt1, wt2) and wt1 > 0
    if buy:
        strategy.entry('Long', strategy.long)
    def percent(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    lossSTL = percent(SL)
    src = close
    htf_ma1 = ta.ema(src, ema_len1)
    htf_ma2 = ta.ema(src, ema_len2)
    ema1 = request.security(syminfo.tickerid, tf1, htf_ma1)
    ema2 = request.security(syminfo.tickerid, tf1, htf_ma2)
    ema3 = request.security(syminfo.tickerid, tf2, htf_ma1)
    ema4 = request.security(syminfo.tickerid, tf2, htf_ma2)
    a = array.from_items(ema1, ema2, ema3, ema4)
    tpmtf1 = array.min(a)
    tpmtf2 = array.min(a, 2)
    tpmtf3 = array.min(a, 3)
    tpmtf4 = array.min(a, 4)
    long_sl_lv = strategy.position_avg_price - lossSTL * syminfo.mintick
    if takepercent == True:
        strategy.exit('TP1%', 'Long', qty_percent=qty1, profit=percent(TP1), loss=lossSTL)
        strategy.exit('TP2%', 'Long', qty_percent=qty2, profit=percent(TP2), loss=lossSTL)
        strategy.exit('TP3%', 'Long', qty_percent=qty3, profit=percent(TP3), loss=lossSTL)
        strategy.exit('TP4%', 'Long', qty_percent=qty3, profit=percent(TP4), loss=lossSTL)
        if closebuy:
            strategy.close_all(comment='Close All')
    if takemtf == True and array.max(a, 1) > strategy.position_avg_price:
        strategy.exit('TP1Mtf', 'Long', qty_percent=qty1, limit=tpmtf1, stop=long_sl_lv)
        strategy.exit('TP2Mtf', 'Long', qty_percent=qty2, limit=tpmtf2, stop=long_sl_lv)
        strategy.exit('TP3Mtf', 'Long', qty_percent=qty3, limit=tpmtf3, stop=long_sl_lv)
        if closebuy:
            strategy.close_all(comment='Close All')
    long_tp1_lv = strategy.position_avg_price + percent(TP1) * syminfo.mintick
    long_tp2_lv = strategy.position_avg_price + percent(TP2) * syminfo.mintick
    long_tp3_lv = strategy.position_avg_price + percent(TP3) * syminfo.mintick
    long_tp4_lv = strategy.position_avg_price + percent(TP4) * syminfo.mintick
    plot(long_sl_lv if strategy.position_size > 0 else na, color=color.red, style=plot.style_linebr, title='SL Long')
    plot(long_tp1_lv if strategy.position_size > 0 else na, color=color.lime, style=plot.style_linebr, title='Long TP1%')
    plot(long_tp2_lv if strategy.position_size > 0 else na, color=color.lime, style=plot.style_linebr, title='Long TP2%')
    plot(long_tp3_lv if strategy.position_size > 0 else na, color=color.lime, style=plot.style_linebr, title='Long TP3%')
    plot(long_tp4_lv if strategy.position_size > 0 else na, color=color.lime, style=plot.style_linebr, title='Long TP4%')
    plot(tpmtf1 if strategy.position_size > 0 else na, color=color.orange, style=plot.style_linebr, title='Long TP1Mtf', display=display.none)
    plot(tpmtf2 if strategy.position_size > 0 else na, color=color.orange, style=plot.style_linebr, title='Long TP2Mtf', display=display.none)
    plot(tpmtf3 if strategy.position_size > 0 else na, color=color.orange, style=plot.style_linebr, title='Long TP3Mtf', display=display.none)
    plotema1 = plot(ema1, color=color.new(color.silver, 0), style=plot.style_line, linewidth=1, offset=0, title='Ema100 4h', display=display.none)
    plotema2 = plot(ema2, color=color.new(color.silver, 0), style=plot.style_line, linewidth=1, offset=0, title='Ema200 4h', display=display.none)
    plotema3 = plot(ema3, color=color.new(color.orange, 20), style=plot.style_line, linewidth=1, offset=0, title='Ema100 D', display=display.none)
    plotema4 = plot(ema4, color=color.new(color.orange, 20), style=plot.style_line, linewidth=1, offset=0, title='Ema200 D', display=display.none)
    _x = timenow + math.round(ta.change(time) * 2)
    labelema1: Persistent[Label] = na(Label)
    label.delete(labelema1)
    labelema1 = label.new(x=_x, y=ema1, text='Ema' + string.tostring(ema_len1) + ' ' + string.tostring(tf1) + ': ' + string.tostring(math.round(ema1, 4)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.yellow, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
    labelema2: Persistent[Label] = na(Label)
    label.delete(labelema2)
    labelema2 = label.new(x=_x, y=ema2, text='Ema' + string.tostring(ema_len2) + ' ' + string.tostring(tf1) + ': ' + string.tostring(math.round(ema2, 4)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.yellow, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
    labelema3: Persistent[Label] = na(Label)
    label.delete(labelema3)
    labelema3 = label.new(x=_x, y=ema3, text='Ema' + string.tostring(ema_len1) + ' ' + string.tostring(tf2) + ': ' + string.tostring(math.round(ema3, 4)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.yellow, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
    labelema4: Persistent[Label] = na(Label)
    label.delete(labelema4)
    labelema4 = label.new(x=_x, y=ema4, text='Ema' + string.tostring(ema_len2) + ' ' + string.tostring(tf2) + ': ' + string.tostring(math.round(ema4, 4)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.yellow, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
    if strategy.position_size > 0:
        labellongtp1: Persistent[Label] = na(Label)
        label.delete(labellongtp1)
        labellongtp1 = label.new(x=_x, y=long_tp1_lv, text='TP1: ' + string.tostring(math.round(long_tp1_lv, 2)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.lime, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labellongtp2: Persistent[Label] = na(Label)
        label.delete(labellongtp2)
        labellongtp2 = label.new(x=_x, y=long_tp2_lv, text='TP2: ' + string.tostring(math.round(long_tp2_lv, 2)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.lime, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labellongtp3: Persistent[Label] = na(Label)
        label.delete(labellongtp3)
        labellongtp3 = label.new(x=_x, y=long_tp3_lv, text='TP3: ' + string.tostring(math.round(long_tp3_lv, 2)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.lime, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labellongtp4: Persistent[Label] = na(Label)
        label.delete(labellongtp4)
        labellongtp4 = label.new(x=_x, y=long_tp4_lv, text='TP4: ' + string.tostring(math.round(long_tp4_lv, 2)) + '', color=color.new(color.new('#000000'), 100), textcolor=color.lime, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
