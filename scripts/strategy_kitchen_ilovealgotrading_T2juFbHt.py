"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    barstate, bgcolor, close, color, display, fixnan, format, high, input,
    location, low, math, na, nz, open, plot, plotshape, position, request, script, shape, size,
    strategy, string, syminfo, ta, table, time, timeframe, timestamp, volume
)
from pynecore.types import Color, Persistent, Series


@script.strategy('Kitchen [ilovealgotrading]', overlay=True, format=format.price, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Start_Time=input.time(defval=timestamp('01 January 2017 13:30 +0000'), title='Start_Time', group=' ################# BACKTEST DATE ################ '),
    End_Time=input.time(defval=timestamp('30 April 2030 19:30 +0000'), title='End_Time', group=' ################# BACKTEST DATE ################ '),
    atrPeriod=input(10, 'ATR Length', group=' #################  Supertrend  ################ '),
    factor=input(3, 'Factor', group=' #################  Supertrend  ################ '),
    time1=input.string(title='Short Time Period', defval='07 1h', options=('01 1m', '02 3m', '03 5m', '04 15m', '05 30m', '06 45m', '07 1h', '08 2h', '09 3h', '10 4h', '11 1D', '12 1W'), group=' #################  Supertrend  ################ ', tooltip='this timeframe is the value of our short-time supertrend indicator'),
    time2=input.string(title='Long Time Period', defval='10 4h', options=('01 1m', '02 3m', '03 5m', '04 15m', '05 30m', '06 45m', '07 1h', '08 2h', '09 3h', '10 4h', '11 1D', '12 1W'), group=' #################  Supertrend  ################ ', tooltip='this timeframe is the value of our long-time supertrend indicator'),
    low_limit_stoch_rsi=input.float(title='Stoch Rsi Low Limit', step=0.5, defval=15, group=' #################  Stoch RSI   ################ ', tooltip='when Stock rsi value crossover Low Limit value we get Long'),
    up_limit_stoch_rsi=input.float(title='Stoch Rsi Up Limit', step=0.5, defval=85, group=' #################  Stoch RSI   ################ ', tooltip='when Stock rsi value crossunder Up Limit value we get Short'),
    stocrsi_back_length=input.int(20, 'Stoch Rsi retroactive length', minval=1, group=' #################  Stoch RSI   ################ ', tooltip='How many candles are left behind, even if there is a buy or sell signal, it will be valid now'),
    smoothK=input.int(3, 'Stochastic RSI K', minval=1, group=' #################  Stoch RSI   ################ '),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group=' #################  Stoch RSI   ################ '),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group=' #################  Stoch RSI   ################ '),
    src_rsi: Series[float] = input(close, title='RSI Source', group=' #################  Stoch RSI   ################ '),
    alert_Mes=input.string(title='Strategy Alert Mess', defval='{{strategy.order.alert_message}}', group=' #################  Strategy Settings  ################ '),
    dollar=input.float(title='Dollar Cost Per Position ', defval=1000, group=' #################  Strategy Settings  ################ '),
    trade_direction=input.string(title='Trade_direction', group=' #################  Strategy Settings  ################ ', options=('LONG', 'SHORT', 'BOTH'), defval='BOTH'),
    Long_message_open=input.text_area('Long Open', title='Long Open Message', group=' #################  Strategy Settings  ################ ', tooltip='if you write your alert window this code {{strategy.order.alert_message}} .When trigger Long signal you will get dynamically what you pasted here for Long Open Message '),
    Short_message_open=input.text_area('Short Open', title='Short Open Message', group=' #################  Strategy Settings  ################ ', tooltip='if you write your alert window this code {{strategy.order.alert_message}} .When trigger Long signal you will get dynamically what you pasted here for Short Open Message '),
    Long_message_close=input.text_area('Long Close', title='Long Close Message', group=' #################  Strategy Settings  ################ ', tooltip='if you write your alert window this code {{strategy.order.alert_message}} .When trigger Long signal you will get dynamically what you pasted here for Long Close Message '),
    Short_message_close=input.text_area('Short Close', title='Short Close Message', group=' #################  Strategy Settings  ################ ', tooltip='if you write your alert window this code {{strategy.order.alert_message}} .When trigger Long signal you will get dynamically what you pasted here for Short Close Message '),
    showDashboard=input(True, 'Trend Table', group=' 📅  Table Settings 📅 '),
    locationDashboard=input.string('Down Right', title='Trend Table Location', options=('Top Right', 'Top left', 'Right Middle', 'Left Middle', 'Down Right', 'Left Down'), group=' 📅  Table Settings 📅 '),
    sizeDashboard=input.string(defval='Small', options=('Very Small', 'Small', 'Middle'), title='Table Size', group=' 📅  Table Settings 📅 ')
):
    def res(Resolution):
        __block_result__ = na
        if Resolution == '00 Current':
            __block_result__ = timeframe.period
        else:
            __block_result_1__ = na
            if Resolution == '01 1m':
                __block_result_1__ = '1'
            else:
                __block_result_2__ = na
                if Resolution == '02 3m':
                    __block_result_2__ = '3'
                else:
                    __block_result_3__ = na
                    if Resolution == '03 5m':
                        __block_result_3__ = '5'
                    else:
                        __block_result_4__ = na
                        if Resolution == '04 15m':
                            __block_result_4__ = '15'
                        else:
                            __block_result_5__ = na
                            if Resolution == '05 30m':
                                __block_result_5__ = '30'
                            else:
                                __block_result_6__ = na
                                if Resolution == '06 45m':
                                    __block_result_6__ = '45'
                                else:
                                    __block_result_7__ = na
                                    if Resolution == '07 1h':
                                        __block_result_7__ = '60'
                                    else:
                                        __block_result_8__ = na
                                        if Resolution == '08 2h':
                                            __block_result_8__ = '120'
                                        else:
                                            __block_result_9__ = na
                                            if Resolution == '09 3h':
                                                __block_result_9__ = '180'
                                            else:
                                                __block_result_10__ = na
                                                if Resolution == '10 4h':
                                                    __block_result_10__ = '240'
                                                else:
                                                    __block_result_11__ = na
                                                    if Resolution == '11 1D':
                                                        __block_result_11__ = '1D'
                                                    else:
                                                        __block_result_12__ = na
                                                        if Resolution == '12 1W':
                                                            __block_result_12__ = '1W'
                                                        else:
                                                            __block_result_13__ = na
                                                            if Resolution == '13 1M':
                                                                __block_result_13__ = '1M'
                                                            __block_result_12__ = __block_result_13__
                                                        __block_result_11__ = __block_result_12__
                                                    __block_result_10__ = __block_result_11__
                                                __block_result_9__ = __block_result_10__
                                            __block_result_8__ = __block_result_9__
                                        __block_result_7__ = __block_result_8__
                                    __block_result_6__ = __block_result_7__
                                __block_result_5__ = __block_result_6__
                            __block_result_4__ = __block_result_5__
                        __block_result_3__ = __block_result_4__
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    supertrend2, direction2 = request.security(syminfo.tickerid, res(time2), ta.supertrend(factor, atrPeriod))
    supertrend1, direction1 = request.security(syminfo.tickerid, res(time1), ta.supertrend(factor, atrPeriod))
    rsi1 = request.security(syminfo.tickerid, '240', ta.rsi(src_rsi, lengthRSI))
    k = request.security(syminfo.tickerid, '240', ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK))
    Time_interval = time > Start_Time and time < End_Time
    bgcolor(color.rgb(255, 235, 59, 95) if Time_interval else na)
    back_long: int = 0
    back_short: int = 0
    for i in pine_range(1, stocrsi_back_length, 1):
        if inline_series(ta.crossover(k, low_limit_stoch_rsi), i) == True:
            back_long = back_long + i
        if inline_series(ta.crossunder(k, up_limit_stoch_rsi), i) == True:
            back_short = back_short + i
    buy_signal: Series[bool] = False
    sell_signal: Series[bool] = False
    if direction2 < 0 and direction1 < 0 and (back_long > 0):
        buy_signal = True
    if direction2 > 0 and direction1 > 0 and (back_short > 0):
        sell_signal = True
    if strategy.opentrades == 0 and Time_interval and buy_signal and (trade_direction == 'LONG' or trade_direction == 'BOTH'):
        strategy.entry('Long_Open', strategy.long, qty=dollar / close, alert_message=Long_message_open)
    if strategy.opentrades == 0 and Time_interval and sell_signal and (trade_direction == 'SHORT' or trade_direction == 'BOTH'):
        strategy.entry('Short_Open', strategy.short, qty=dollar / close, alert_message=Short_message_open)
    if close < supertrend1 and strategy.position_size > 0:
        strategy.exit('Long_Close', from_entry='Long_Open', stop=close, qty_percent=100, alert_message=Long_message_close)
    if close > supertrend1 and strategy.position_size < 0:
        strategy.exit('Short_Close', from_entry='Short_Open', stop=close, qty_percent=100, alert_message=Short_message_close)
    plotshape(supertrend2 if buy_signal[1] == False and strategy.opentrades == 0 and Time_interval and buy_signal else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white)
    plotshape(supertrend2 if sell_signal[1] == False and strategy.opentrades == 0 and Time_interval and sell_signal else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white)
    bodyMiddle4 = plot((open + close) / 2, display=display.none)
    upTrend2 = plot(supertrend2 if direction2 < 0 else na, 'Up Trend', color=color.new(color.green, 0), style=plot.style_linebr, linewidth=2)
    downTrend2 = plot(na if direction2 < 0 else supertrend2, 'Down Trend', color=color.new(color.red, 0), style=plot.style_linebr, linewidth=2)
    bodyMiddle = plot((open + close) / 2, display=display.none)
    upTrend = plot(supertrend1 if direction1 < 0 else na, 'Up Trend', color=color.new(color.yellow, 0), style=plot.style_linebr)
    downTrend = plot(na if direction1 < 0 else supertrend1, 'Down Trend', color=color.new(color.orange, 0), style=plot.style_linebr)
    tableTextColor = color.white
    tableBgColor: Color = color.new('#000659')
    dashboard_loc: Persistent = position.top_right if locationDashboard == 'Top Right' else position.top_left if locationDashboard == 'Top left' else position.middle_right if locationDashboard == 'Right Middle' else position.middle_left if locationDashboard == 'Left Middle' else position.bottom_right if locationDashboard == 'Down Right' else position.bottom_left
    dashboard_size: Persistent = size.tiny if sizeDashboard == 'Very Small' else size.small if sizeDashboard == 'Small' else size.normal
    dashboard: Persistent = table.new(dashboard_loc, 2, 36, tableBgColor, color.new('#FFFFFF'), 2, color.new('#FFFFFF'), 1) if showDashboard else na
    def dashboard_cell(column, row, txt, signal = False):
        return table.cell(dashboard, column, row, txt, 0, 0, color.new('#FFFFFF') if signal else tableTextColor, text_size=dashboard_size)

    def dashboard_cell_bg(column, row, col):
        return table.cell_set_bgcolor(dashboard, column, row, col)

    rsi = ta.rsi(close, 14)
    vosc = ta.obv - ta.ema(ta.obv, 14) if nz(cast_bool(volume), False) else 0
    bs = ta.ema(nz(math.abs((open - close) / (high - low) * 100)), 3)
    ema = ta.ema(close, 200)
    adxlen: int = 14
    dilen: int = 14
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(plusDM, len) / truerange)
        minus = fixnan(100 * ta.rma(minusDM, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__0000007c__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__0000007c__

    adx__global__ = adx(dilen, adxlen)
    if barstate.islastconfirmedhistory and showDashboard:
        dashboard_cell(0, 0, 'Table Values 📊')
        table.merge_cells(dashboard, 0, 0, 1, 0)
        dashboard_cell(0, 2, 'STOCH RSI 4 Hour')
        dashboard_cell(0, 14, 'Volume')
        dashboard_cell(0, 15, 'Volatility')
        dashboard_cell(0, 16, 'Momentum')
        dashboard_cell(1, 0, '')
        dashboard_cell_bg(1, 0, color.teal if rsi > 50 else color.maroon)
        dashboard_cell(1, 2, string.tostring(math.round(k, 1)), True)
        dashboard_cell(1, 14, 'Positive ⚡' if vosc > 0 else 'Negative ❗')
        dashboard_cell_bg(1, 14, color.teal if vosc > 0 else color.maroon)
        dashboard_cell(1, 15, 'Trend 🚀' if adx__global__ > 20 else 'Consolidation ⚠️')
        dashboard_cell_bg(1, 15, color.teal if adx__global__ > 20 else color.orange)
        dashboard_cell(1, 16, 'Positive ⚡' if rsi > 50 else 'Negative ❗')
        dashboard_cell_bg(1, 16, color.teal if rsi > 50 else color.maroon)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
