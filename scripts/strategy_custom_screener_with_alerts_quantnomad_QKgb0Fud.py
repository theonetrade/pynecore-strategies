"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.lib import (
    bar_index, barstate, close, color, dayofmonth, input, label, math, month,
    plot, request, script, strategy, string, ta, time, timeframe, timenow, timestamp, year, yloc
)
from pynecore.types import Series


@script.strategy('Custom Screener with Alerts [QuantNomad]', shorttitle='AlertsScreener[QN]', overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    rsi_length=input(14, title='RSI Length'),
    rsi_overbought=input(70, title='RSI Overbought Level'),
    s01=input.symbol('AAPL'),
    s02=input.symbol('MSFT'),
    s03=input.symbol('AMZN'),
    s04=input.symbol('GOOGL'),
    s05=input.symbol('BABA'),
    s06=input.symbol('FB'),
    s07=input.symbol('BRK.A'),
    s08=input.symbol('V'),
    s09=input.symbol('JNJ'),
    s10=input.symbol('WMT'),
    s11=input.symbol('TSM'),
    s12=input.symbol('PG'),
    s13=input.symbol('MA'),
    s14=input.symbol('JPM'),
    s15=input.symbol('TSLA'),
    s16=input.symbol('UNH'),
    s17=input.symbol('HD'),
    s18=input.symbol('NVDA'),
    s19=input.symbol('INTC'),
    s20=input.symbol('NFLX'),
    s21=input.symbol('VZ'),
    s22=input.symbol('ADBE'),
    s23=input.symbol('DIS'),
    s24=input.symbol('T'),
    s25=input.symbol('PYPL'),
    s26=input.symbol('BAC'),
    s27=input.symbol('NVS'),
    s28=input.symbol('CSCO'),
    s29=input.symbol('KO'),
    s30=input.symbol('MRK'),
    s31=input.symbol('PFE'),
    s32=input.symbol('PEP'),
    s33=input.symbol('CMCSA'),
    s34=input.symbol('SAP'),
    s35=input.symbol('XOM'),
    s36=input.symbol('CRM'),
    s37=input.symbol('ORCL'),
    s38=input.symbol('TM'),
    s39=input.symbol('ABBV'),
    s40=input.symbol('ASML')
):
    def screenerFunc():
        rsi = ta.rsi(close, rsi_length)
        cond = rsi > rsi_overbought
        return (rsi, cond)

    def roundn(x, n):
        mult: int = 1
        if n != 0:
            __loop_1__ = pine_loop(1, 1)
            while __loop_1__.step(math.abs(n)):
                i = __loop_1__.value
                mult = mult * 10
        return math.round(x * mult) / mult if n >= 0 else math.round(x / mult) * mult

    v01, c01 = request.security(s01, timeframe.period, screenerFunc())
    v02, c02 = request.security(s02, timeframe.period, screenerFunc())
    v03, c03 = request.security(s03, timeframe.period, screenerFunc())
    v04, c04 = request.security(s04, timeframe.period, screenerFunc())
    v05, c05 = request.security(s05, timeframe.period, screenerFunc())
    v06, c06 = request.security(s06, timeframe.period, screenerFunc())
    v07, c07 = request.security(s07, timeframe.period, screenerFunc())
    v08, c08 = request.security(s08, timeframe.period, screenerFunc())
    v09, c09 = request.security(s09, timeframe.period, screenerFunc())
    v10, c10 = request.security(s10, timeframe.period, screenerFunc())
    v11, c11 = request.security(s11, timeframe.period, screenerFunc())
    v12, c12 = request.security(s12, timeframe.period, screenerFunc())
    v13, c13 = request.security(s13, timeframe.period, screenerFunc())
    v14, c14 = request.security(s14, timeframe.period, screenerFunc())
    v15, c15 = request.security(s15, timeframe.period, screenerFunc())
    v16, c16 = request.security(s16, timeframe.period, screenerFunc())
    v17, c17 = request.security(s17, timeframe.period, screenerFunc())
    v18, c18 = request.security(s18, timeframe.period, screenerFunc())
    v19, c19 = request.security(s19, timeframe.period, screenerFunc())
    v20, c20 = request.security(s20, timeframe.period, screenerFunc())
    v21, c21 = request.security(s21, timeframe.period, screenerFunc())
    v22, c22 = request.security(s22, timeframe.period, screenerFunc())
    v23, c23 = request.security(s23, timeframe.period, screenerFunc())
    v24, c24 = request.security(s24, timeframe.period, screenerFunc())
    v25, c25 = request.security(s25, timeframe.period, screenerFunc())
    v26, c26 = request.security(s26, timeframe.period, screenerFunc())
    v27, c27 = request.security(s27, timeframe.period, screenerFunc())
    v28, c28 = request.security(s28, timeframe.period, screenerFunc())
    v29, c29 = request.security(s29, timeframe.period, screenerFunc())
    v30, c30 = request.security(s30, timeframe.period, screenerFunc())
    v31, c31 = request.security(s31, timeframe.period, screenerFunc())
    v32, c32 = request.security(s32, timeframe.period, screenerFunc())
    v33, c33 = request.security(s33, timeframe.period, screenerFunc())
    v34, c34 = request.security(s34, timeframe.period, screenerFunc())
    v35, c35 = request.security(s35, timeframe.period, screenerFunc())
    v36, c36 = request.security(s36, timeframe.period, screenerFunc())
    v37, c37 = request.security(s37, timeframe.period, screenerFunc())
    v38, c38 = request.security(s38, timeframe.period, screenerFunc())
    v39, c39 = request.security(s39, timeframe.period, screenerFunc())
    v40, c40 = request.security(s40, timeframe.period, screenerFunc())
    scr_label: str = 'Screener: \n##########\n'
    scr_label = scr_label + s01 + ' ' + string.tostring(roundn(v01, 3)) + '\n' if c01 else scr_label
    scr_label = scr_label + s02 + ' ' + string.tostring(roundn(v02, 3)) + '\n' if c02 else scr_label
    scr_label = scr_label + s03 + ' ' + string.tostring(roundn(v03, 3)) + '\n' if c03 else scr_label
    scr_label = scr_label + s04 + ' ' + string.tostring(roundn(v04, 3)) + '\n' if c04 else scr_label
    scr_label = scr_label + s05 + ' ' + string.tostring(roundn(v05, 3)) + '\n' if c05 else scr_label
    scr_label = scr_label + s06 + ' ' + string.tostring(roundn(v06, 3)) + '\n' if c06 else scr_label
    scr_label = scr_label + s07 + ' ' + string.tostring(roundn(v07, 3)) + '\n' if c07 else scr_label
    scr_label = scr_label + s08 + ' ' + string.tostring(roundn(v08, 3)) + '\n' if c08 else scr_label
    scr_label = scr_label + s09 + ' ' + string.tostring(roundn(v09, 3)) + '\n' if c09 else scr_label
    scr_label = scr_label + s10 + ' ' + string.tostring(roundn(v10, 3)) + '\n' if c10 else scr_label
    scr_label = scr_label + s11 + ' ' + string.tostring(roundn(v11, 3)) + '\n' if c11 else scr_label
    scr_label = scr_label + s12 + ' ' + string.tostring(roundn(v12, 3)) + '\n' if c12 else scr_label
    scr_label = scr_label + s13 + ' ' + string.tostring(roundn(v13, 3)) + '\n' if c13 else scr_label
    scr_label = scr_label + s14 + ' ' + string.tostring(roundn(v14, 3)) + '\n' if c14 else scr_label
    scr_label = scr_label + s15 + ' ' + string.tostring(roundn(v15, 3)) + '\n' if c15 else scr_label
    scr_label = scr_label + s16 + ' ' + string.tostring(roundn(v16, 3)) + '\n' if c16 else scr_label
    scr_label = scr_label + s17 + ' ' + string.tostring(roundn(v17, 3)) + '\n' if c17 else scr_label
    scr_label = scr_label + s18 + ' ' + string.tostring(roundn(v18, 3)) + '\n' if c18 else scr_label
    scr_label = scr_label + s19 + ' ' + string.tostring(roundn(v19, 3)) + '\n' if c19 else scr_label
    scr_label = scr_label + s20 + ' ' + string.tostring(roundn(v20, 3)) + '\n' if c20 else scr_label
    scr_label = scr_label + s21 + ' ' + string.tostring(roundn(v21, 3)) + '\n' if c21 else scr_label
    scr_label = scr_label + s22 + ' ' + string.tostring(roundn(v22, 3)) + '\n' if c22 else scr_label
    scr_label = scr_label + s23 + ' ' + string.tostring(roundn(v23, 3)) + '\n' if c23 else scr_label
    scr_label = scr_label + s24 + ' ' + string.tostring(roundn(v24, 3)) + '\n' if c24 else scr_label
    scr_label = scr_label + s25 + ' ' + string.tostring(roundn(v25, 3)) + '\n' if c25 else scr_label
    scr_label = scr_label + s26 + ' ' + string.tostring(roundn(v26, 3)) + '\n' if c26 else scr_label
    scr_label = scr_label + s27 + ' ' + string.tostring(roundn(v27, 3)) + '\n' if c27 else scr_label
    scr_label = scr_label + s28 + ' ' + string.tostring(roundn(v28, 3)) + '\n' if c28 else scr_label
    scr_label = scr_label + s29 + ' ' + string.tostring(roundn(v29, 3)) + '\n' if c29 else scr_label
    scr_label = scr_label + s30 + ' ' + string.tostring(roundn(v30, 3)) + '\n' if c30 else scr_label
    scr_label = scr_label + s31 + ' ' + string.tostring(roundn(v31, 3)) + '\n' if c31 else scr_label
    scr_label = scr_label + s32 + ' ' + string.tostring(roundn(v32, 3)) + '\n' if c32 else scr_label
    scr_label = scr_label + s33 + ' ' + string.tostring(roundn(v33, 3)) + '\n' if c33 else scr_label
    scr_label = scr_label + s34 + ' ' + string.tostring(roundn(v34, 3)) + '\n' if c34 else scr_label
    scr_label = scr_label + s35 + ' ' + string.tostring(roundn(v35, 3)) + '\n' if c35 else scr_label
    scr_label = scr_label + s36 + ' ' + string.tostring(roundn(v36, 3)) + '\n' if c36 else scr_label
    scr_label = scr_label + s37 + ' ' + string.tostring(roundn(v37, 3)) + '\n' if c37 else scr_label
    scr_label = scr_label + s38 + ' ' + string.tostring(roundn(v38, 3)) + '\n' if c38 else scr_label
    scr_label = scr_label + s39 + ' ' + string.tostring(roundn(v39, 3)) + '\n' if c39 else scr_label
    scr_label = scr_label + s40 + ' ' + string.tostring(roundn(v40, 3)) + '\n' if c40 else scr_label
    scr_label = scr_label + '\n #telegram'
    lab_l: Series = label.new(bar_index, 0, scr_label, color=color.gray, textcolor=color.black, style=label.style_label_down, yloc=yloc.price)
    label.delete(lab_l[1])
    plot(0)
    year_1 = year(timenow)
    month_1 = month(timenow)
    dayofmonth_1 = dayofmonth(timenow)
    if timeframe.isintraday and time >= timestamp(year_1, month_1, dayofmonth_1, 0, 0):
        if strategy.position_size[1] == 0 and barstate.isconfirmed:
            strategy.entry('dummy_long', strategy.long, alert_message=scr_label)
        if strategy.position_size[1] != 0 and barstate.isconfirmed:
            strategy.close('dummy_long', alert_message=scr_label)
    if not timeframe.isintraday and time >= timenow - 30 * 1000 * 60 * 60 * 24:
        if strategy.position_size[1] == 0 and barstate.isconfirmed:
            strategy.entry('dummy_long', strategy.long, alert_message=scr_label)
        if strategy.position_size[1] != 0 and barstate.isconfirmed:
            strategy.close('dummy_long', alert_message=scr_label)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
