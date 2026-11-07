"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, barstate, color, high, input, low, math, month, na, nz, plot,
    position, script, strategy, string, syminfo, ta, table, time, year
)
from pynecore.types import NA, Persistent, Series, Table


@script.strategy('Monthly Returns in PineScript Strategies', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=25, calc_on_every_tick=True, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    leftBars=input(2),
    rightBars=input(1),
    prec=input(2, title='Return Precision')
):
    swh = ta.pivothigh(leftBars, rightBars)
    swl = ta.pivotlow(leftBars, rightBars)
    hprice: Series[float] = 0.0
    hprice = swh if not na(swh) else hprice[1]
    lprice: Series[float] = 0.0
    lprice = swl if not na(swl) else lprice[1]
    le: Series[bool] = False
    le = True if not na(swh) else False if le[1] and high > hprice else le[1]
    se: Series[bool] = False
    se = True if not na(swl) else False if se[1] and low < lprice else se[1]
    if le:
        strategy.entry('PivRevLE', strategy.long, comment='PivRevLE', stop=hprice + syminfo.mintick)
    if se:
        strategy.entry('PivRevSE', strategy.short, comment='PivRevSE', stop=lprice - syminfo.mintick)
    plot(hprice, color=color.new(color.green, 0), linewidth=2)
    plot(lprice, color=color.new(color.red, 0), linewidth=2)
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
    monthly_table: Persistent = NA(Table)
    if barstate.islast:
        monthly_table = table.new(position.bottom_right, columns=14, rows=array.size(year_pnl) + 1, border_width=1)
        table.cell(monthly_table, 0, 0, '', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 1, 0, 'Jan', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 2, 0, 'Feb', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 3, 0, 'Mar', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 4, 0, 'Apr', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 5, 0, 'May', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 6, 0, 'Jun', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 7, 0, 'Jul', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 8, 0, 'Aug', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 9, 0, 'Sep', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 10, 0, 'Oct', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 11, 0, 'Nov', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 12, 0, 'Dec', bgcolor=color.new('#CCCCCC'))
        table.cell(monthly_table, 13, 0, 'Year', bgcolor=color.new('#999999'))
        for yi in pine_range(0, array.size(year_pnl) - 1, 1):
            table.cell(monthly_table, 0, yi + 1, string.tostring(year(array.get(year_time, yi))), bgcolor=color.new('#CCCCCC'))
            y_color = color.new(color.green, transp=50) if array.get(year_pnl, yi) > 0 else color.new(color.red, transp=50)
            table.cell(monthly_table, 13, yi + 1, string.tostring(math.round(array.get(year_pnl, yi) * 100, prec)), bgcolor=y_color)
        for mi in pine_range(0, array.size(month_time) - 1, 1):
            m_row = year(array.get(month_time, mi)) - year(array.get(year_time, 0)) + 1
            m_col = month(array.get(month_time, mi))
            m_color = color.new(color.green, transp=70) if array.get(month_pnl, mi) > 0 else color.new(color.red, transp=70)
            table.cell(monthly_table, m_col, m_row, string.tostring(math.round(array.get(month_pnl, mi) * 100, prec)), bgcolor=m_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
