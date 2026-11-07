"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, barstate, bgcolor, close, color, fill, high, input, math, month,
    na, nz, plot, position, request, script, strategy, string, syminfo, ta, table, time, timeframe,
    timestamp, year
)
from pynecore.types import NA, Persistent, Series, Table


@script.strategy('Bollinger Bands - Breakout Strategy', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, slippage=1, backtest_fill_limits_assumption=1, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0.025, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    bbLengthInput=input.int(15, title='Length', group='Bollinger Bands', inline='BB'),
    bbDevInput=input.float(2.0, title='StdDev', group='Bollinger Bands', inline='BB'),
    trendFilterInput=input.bool(False, title='Above/Below', group='Trend Filter', inline='Trend'),
    trendFilterPeriodInput=input(223, title='', group='Trend Filter', inline='Trend'),
    trendFilterType=input.string(title='', defval='EMA', options=('EMA', 'SMA', 'RMA', 'WMA'), group='Trend Filter', inline='Trend'),
    volatilityFilterInput=input.bool(True, title='StdDev', group='Volatility Filter', inline='Vol'),
    volatilityFilterStDevLength=input(15, title='', group='Volatility Filter', inline='Vol'),
    volatilityStDevMaLength=input(15, title='>MA', group='Volatility Filter', inline='Vol'),
    roc_enable=input.bool(False, '', group='ROC Filter from CloseD', inline='roc'),
    roc_threshold=input.float(1, 'Treshold', step=0.5, group='ROC Filter from CloseD', inline='roc'),
    tradeDirectionInput=input.string('Auto', options=('Auto', 'Long&Short', 'Long Only', 'Short Only'), title='Trade', group='Direction Filter', tooltip='Auto: if a PERP is detected (in the symbol description), trade long and short\n Otherwise as per user-input'),
    start=input.time(timestamp('2017-01-01'), 'Start', group='Date Filter'),
    finish=input.time(timestamp('2050-01-01'), 'End', group='Date Filter'),
    xl_ts_percent=input.float(2, step=0.5, title='TS', group='Exit Long', inline='LTS', tooltip='Trailing Treshold %'),
    xl_to_percent=input.float(0.5, step=0.5, title='TO', group='Exit Long', inline='LTS', tooltip='Trailing Offset %'),
    xl_sl_percent=input.float(2, step=0.5, title='SL', group='Exit Long', inline='LSLTP'),
    xl_tp_percent=input.float(9, step=0.5, title='TP', group='Exit Long', inline='LSLTP'),
    xs_ts_percent=input.float(2, step=0.5, title='TS', group='Exit Short', inline='STS', tooltip='Trailing Treshold %'),
    xs_to_percent=input.float(0.5, step=0.5, title='TO', group='Exit Short', inline='STS', tooltip='Trailing Offset %'),
    xs_sl_percent=input.float(2, step=0.5, title='SL', group='Exit Short', inline='ESSLTP', tooltip='Stop Loss %'),
    xs_tp_percent=input.float(9, step=0.5, title='TP', group='Exit Short', inline='ESSLTP', tooltip='Take Profit %'),
    max_intraday_loss=input.int(10, title='Max Intraday Loss (Percent)', group='Risk Management'),
    results_prec=input(2, title='Precision', group='Results Table'),
    results_dark=input.bool(defval=True, title='Dark Mode', group='Results Table')
):
    def f_security(_sym, _res, _src: Series, _rep):
        return inline_series(request.security(_sym, _res, _src[1 if not _rep and barstate.isrealtime else 0]), 0 if _rep or barstate.isrealtime else 1)

    high_daily = f_security(syminfo.tickerid, 'D', high, False)
    closed = f_security(syminfo.tickerid, '1D', close, False)
    roc_filter = (close - closed) / closed * 100 > roc_threshold if roc_enable else True
    __block_result__ = na
    __switch__ = tradeDirectionInput
    if __switch__ == 'Auto':
        __block_result__ = strategy.direction.all if string.contains(string.lower(syminfo.description), 'perp') or string.contains(string.lower(syminfo.description), '.p') else strategy.direction.long
    elif __switch__ == 'Long&Short':
        __block_result__ = strategy.direction.all
    elif __switch__ == 'Long Only':
        __block_result__ = strategy.direction.long
    elif __switch__ == 'Short Only':
        __block_result__ = strategy.direction.short
    else:
        __block_result__ = strategy.direction.all
    tradeDirection = __block_result__
    strategy.risk.allow_entry_in(tradeDirection)
    bbMiddle, bbUpper, bbLower = ta.bb(close, bbLengthInput, bbDevInput)
    plot(bbMiddle, 'Basis', color=color.orange)
    bbUpperPlot = plot(bbUpper, 'Upper', color=color.blue)
    bbLowerrPlot = plot(bbLower, 'Lower', color=color.blue)
    fill(bbUpperPlot, bbLowerrPlot, title='Background', color=color.new(color.blue, 95))
    __block_result_1__ = na
    __switch__ = trendFilterType
    if __switch__ == 'EMA':
        __block_result_1__ = ta.ema(close, trendFilterPeriodInput)
    elif __switch__ == 'SMA':
        __block_result_1__ = ta.sma(close, trendFilterPeriodInput)
    elif __switch__ == 'RMA':
        __block_result_1__ = ta.rma(close, trendFilterPeriodInput)
    elif __switch__ == 'WMA':
        __block_result_1__ = ta.wma(close, trendFilterPeriodInput)
    else:
        __block_result_1__ = ta.wma(close, trendFilterPeriodInput)
    tradeConditionMa: float = __block_result_1__
    trendConditionLong = close > tradeConditionMa if trendFilterInput else True
    trendConditionShort = close < tradeConditionMa if trendFilterInput else True
    plot(tradeConditionMa if trendFilterInput else na, color=color.yellow)
    stdDevClose = ta.stdev(close, volatilityFilterStDevLength)
    volatilityCondition = stdDevClose > ta.sma(stdDevClose, volatilityStDevMaLength) if volatilityFilterInput else True
    bbLowerCrossUnder = ta.crossunder(close, bbLower)
    bbUpperCrossOver = ta.crossover(close, bbUpper)
    bgcolor(na if volatilityCondition else color.new(color.red, 95))
    date_filter = True if time >= start and time <= finish else False
    entryLongCondition = bbUpperCrossOver and trendConditionLong and volatilityCondition and date_filter and roc_filter
    entryShortCondition = bbLowerCrossUnder and trendConditionShort and volatilityCondition and date_filter and roc_filter
    exitLongCondition = bbLowerCrossUnder
    exitShortCondition = bbUpperCrossOver
    if entryLongCondition:
        strategy.entry('EL', strategy.long)
    if entryShortCondition:
        strategy.entry('ES', strategy.short)
    if exitLongCondition:
        strategy.close('EL')
    if exitShortCondition:
        strategy.close('ES')
    xl_ts_tick = xl_ts_percent * close / syminfo.mintick / 100
    xl_to_tick = xl_to_percent * close / syminfo.mintick / 100
    xl_sl_price = strategy.position_avg_price * (1 - xl_sl_percent / 100)
    xl_tp_price = strategy.position_avg_price * (1 + xl_tp_percent / 100)
    strategy.exit('XL+SL/TP', 'EL', stop=xl_sl_price, limit=xl_tp_price, trail_points=xl_ts_tick, trail_offset=xl_to_tick, comment_loss='XL-SL', comment_profit='XL-TP', comment_trailing='XL-TS')
    xs_ts_tick = xs_ts_percent * close / syminfo.mintick / 100
    xs_to_tick = xs_to_percent * close / syminfo.mintick / 100
    xs_sl_price = strategy.position_avg_price * (1 + xs_sl_percent / 100)
    xs_tp_price = strategy.position_avg_price * (1 - xs_tp_percent / 100)
    strategy.exit('XS+SL/TP', 'ES', stop=xs_sl_price, limit=xs_tp_price, trail_points=xs_ts_tick, trail_offset=xs_to_tick, comment_loss='XS-SL', comment_profit='XS-TP', comment_trailing='XS-TS')
    strategy.risk.max_intraday_loss(max_intraday_loss, strategy.percent_of_equity)
    def monthly_table(results_prec: int, results_dark: bool):
        new_month = month(time) != month(time[1])
        new_year = year(time) != year(time[1])
        eq: Series = strategy.equity
        bar_pnl = eq / eq[1] - 1
        cur_month_pnl: Series[float] = 0.0
        cur_year_pnl: Series[float] = 0.0
        cur_month_pnl = 0.0 if new_month else (1 + cur_month_pnl[1]) * (1 + bar_pnl) - 1
        cur_year_pnl = 0.0 if new_year else (1 + cur_year_pnl[1]) * (1 + bar_pnl) - 1
        month_pnl: Persistent[list[float]] = array.new_float(0)
        month_time: Persistent[list[int]] = array.new_int(0)
        year_pnl: Persistent[list[float]] = array.new_float(0)
        year_time: Persistent[list[int]] = array.new_int(0)
        last_computed: Series[bool] = False
        if not na(cur_month_pnl[1]) and (new_month or barstate.islast):
            if last_computed[1]:
                array.pop(month_pnl)
                array.pop(month_time)
            array.push(month_pnl, cur_month_pnl[1])
            array.push(month_time, time[1])
        if not na(cur_year_pnl[1]) and (new_year or barstate.islast):
            if last_computed[1]:
                array.pop(year_pnl)
                array.pop(year_time)
            array.push(year_pnl, cur_year_pnl[1])
            array.push(year_time, time[1])
        last_computed = True if barstate.islast else nz(last_computed[1])
        monthly_table__0000009c__: Persistent = NA(Table)
        cell_hr_bg_color = color.new('#0F0F0F') if results_dark else color.new('#F5F5F5')
        cell_hr_text_color = color.new('#D3D3D3') if results_dark else color.new('#555555')
        cell_border_color = color.new('#000000') if results_dark else color.new('#FFFFFF')
        __block_result_2__ = na
        if barstate.islast:
            monthly_table__0000009c__ = table.new(position.bottom_right, columns=14, rows=array.size(year_pnl) + 1, bgcolor=cell_hr_bg_color, border_width=1, border_color=cell_border_color)
            table.cell(monthly_table__0000009c__, 0, 0, syminfo.tickerid + ' ' + timeframe.period, text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 1, 0, 'Jan', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 2, 0, 'Feb', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 3, 0, 'Mar', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 4, 0, 'Apr', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 5, 0, 'May', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 6, 0, 'Jun', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 7, 0, 'Jul', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 8, 0, 'Aug', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 9, 0, 'Sep', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 10, 0, 'Oct', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 11, 0, 'Nov', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 12, 0, 'Dec', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            table.cell(monthly_table__0000009c__, 13, 0, 'Year', text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
            for yi in pine_range(0, array.size(year_pnl) - 1, 1):
                table.cell(monthly_table__0000009c__, 0, yi + 1, string.tostring(year(array.get(year_time, yi))), text_color=cell_hr_text_color, bgcolor=cell_hr_bg_color)
                y_color = color.lime if array.get(year_pnl, yi) > 0 else color.red if array.get(year_pnl, yi) < 0 else color.gray
                table.cell(monthly_table__0000009c__, 13, yi + 1, string.tostring(math.round(array.get(year_pnl, yi) * 100, results_prec)), bgcolor=y_color)
            __block_result_3__ = na
            for mi in pine_range(0, array.size(month_time) - 1, 1):
                m_row = year(array.get(month_time, mi)) - year(array.get(year_time, 0)) + 1
                m_col = month(array.get(month_time, mi))
                m_color = color.lime if array.get(month_pnl, mi) > 0 else color.red if array.get(month_pnl, mi) < 0 else color.gray
                __block_result_3__ = table.cell(monthly_table__0000009c__, m_col, m_row, string.tostring(math.round(array.get(month_pnl, mi) * 100, results_prec)), bgcolor=m_color)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    monthly_table(results_prec, results_dark)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
