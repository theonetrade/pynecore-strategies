"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, barstate, close, color, display, fill, high, input, location, low,
    math, month, na, nz, plot, plotshape, position, script, shape, size, strategy, string, ta,
    table, time, year
)
from pynecore.types import Color, Persistent, PersistentSeries, Series, Table


@script.strategy("Gradient Trend Filter STRATEGY [ChartPrime/PineIndicators]", overlay=True, initial_capital=10000, commission_value=0.01, slippage=2, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    tradeDirection=input.string("Long Only", "Trade Direction", options=("Long Only", "Short Only", "Long & Short"), group="For help go to PineIndicators.com"),
    src: Series[float] = input.source(close, "Source"),
    length=input.int(25, "Length"),
    width=input.int(2, "Line Width"),
    color1=input.color(color.new('#22C878'), "", inline="1", group="color"),
    color2=input.color(color.new('#C8224E'), "", inline="1", group="color"),
    transp=input.int(80, "", inline="1", group="color"),
    showTable=input(True, "Show Performance Table")
):
    def noise_filter(src, length):
        alpha = 2 / (length + 1)
        nf_1: Series[float] = 0.0
        nf_2: Series[float] = 0.0
        nf_3: Series[float] = 0.0

        nf_1 = alpha * src + (1 - alpha) * nz(nf_1[1])
        nf_2 = alpha * nf_1 + (1 - alpha) * nz(nf_2[1])
        nf_3 = alpha * nf_2 + (1 - alpha) * nz(nf_3[1])

        return nf_3

    def bands(src):
        val = noise_filter(high - low, length)
        upper3 = src + val * 0.618 * 2.5
        upper2 = src + val * 0.382 * 2
        upper1 = src + val * 0.236 * 1.5
        lower1 = src - val * 0.236 * 1.5
        lower2 = src - val * 0.382 * 2
        lower3 = src - val * 0.618 * 2.5
        return (upper3, upper2, upper1, lower1, lower2, lower3)

    base: Series[float] = noise_filter(src, length)
    upper3, upper2, upper1, lower1, lower2, lower3 = bands(base)
    diff: float = base - base[2]

    signal_up: bool = ta.crossover(diff, 0) and barstate.isconfirmed
    signal_dn: bool = ta.crossunder(diff, 0) and barstate.isconfirmed

    gradient_col: Color = color.from_gradient(diff, ta.lowest(diff, 100), ta.highest(diff, 100), color2, color1)
    trend_color: Color = color.new(gradient_col, transp)

    plot(base, 'Filter', linewidth=width, color=color1 if diff >= 0 else color2)

    up3 = plot(upper3, display=display.none, editable=False)
    up2 = plot(upper2, display=display.none, editable=False)
    up1 = plot(upper1, display=display.none, editable=False)
    lw1 = plot(lower1, display=display.none, editable=False)
    lw2 = plot(lower2, display=display.none, editable=False)
    lw3 = plot(lower3, display=display.none, editable=False)

    fill(up3, lw3, trend_color)
    fill(up2, lw2, trend_color)
    fill(up1, lw1, trend_color)

    plotshape(base[1] if signal_up else na, '', shape.diamond, location.absolute, offset=-1, size=size.tiny, color=color.orange)
    plotshape(base[1] if signal_dn else na, '', shape.diamond, location.absolute, offset=-1, size=size.tiny, color=color.orange)

    if (tradeDirection == 'Long & Short' or tradeDirection == 'Long Only') and signal_up:
        strategy.entry('L', strategy.long)

    if (tradeDirection == 'Long & Short' or tradeDirection == 'Short Only') and signal_dn:
        strategy.entry('S', strategy.short)

    if signal_dn and (tradeDirection == 'Long & Short' or tradeDirection == 'Long Only'):
        strategy.close('L')

    if signal_up and (tradeDirection == 'Long & Short' or tradeDirection == 'Short Only'):
        strategy.close('S')

    font_color = color.white
    prec: int = 2

    prev_equity: Persistent[float] = strategy.equity
    eq: float = strategy.equity
    eq_prev: float = nz(prev_equity, eq)
    bar_pnl: Persistent[float] = 0.0

    bar_pnl = 0.0 if eq_prev == 0.0 else eq / eq_prev - 1
    prev_equity = eq

    month_changed: bool = month(time) != month(time[1])
    year_changed: bool = year(time) != year(time[1])

    cur_month_pnl: PersistentSeries[float] = 0.0
    cur_year_pnl: PersistentSeries[float] = 0.0

    if barstate.isfirst:
        cur_month_pnl = bar_pnl
        cur_year_pnl = bar_pnl
    else:
        if month_changed:
            cur_month_pnl = bar_pnl
        else:
            cur_month_pnl = (1 + cur_month_pnl) * (1 + bar_pnl) - 1

        if year_changed:
            cur_year_pnl = bar_pnl
        else:
            cur_year_pnl = (1 + cur_year_pnl) * (1 + bar_pnl) - 1

    month_pnl: Persistent[list[float]] = array.new_float()
    month_time: Persistent[list[int]] = array.new_int()

    year_pnl: Persistent[list[float]] = array.new_float()
    year_time: Persistent[list[int]] = array.new_int()

    if month_changed and (not barstate.isfirst):
        lastMonthFinal: float = cur_month_pnl[1]
        array.push(month_pnl, lastMonthFinal)
        array.push(month_time, time[1])

    if year_changed and (not barstate.isfirst):
        lastYearFinal: float = cur_year_pnl[1]
        array.push(year_pnl, lastYearFinal)
        array.push(year_time, time[1])

    monthly_table: Persistent[Table] = na(Table)

    if showTable:
        final_years_count_raw: int = array.size(year_pnl)
        final_year_time_count: int = array.size(year_time)
        final_years_count: int = math.min(final_years_count_raw, final_year_time_count)

        final_months_count_raw: int = array.size(month_pnl)
        final_month_time_count: int = array.size(month_time)
        final_months_count: int = math.min(final_months_count_raw, final_month_time_count)

        row_count: int = final_years_count + 1 + 1

        monthly_table = table.new(position.bottom_right, 14, row_count, border_width=1)
        table.clear(monthly_table, 0, 0)

        table.cell(monthly_table, 0, 0, 'in %', bgcolor=color.new(color.new('#252630'), 0), text_color=font_color)
        table.cell(monthly_table, 1, 0, 'Jan', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 2, 0, 'Feb', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 3, 0, 'Mar', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 4, 0, 'Apr', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 5, 0, 'May', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 6, 0, 'Jun', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 7, 0, 'Jul', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 8, 0, 'Aug', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 9, 0, 'Sep', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 10, 0, 'Oct', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 11, 0, 'Nov', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 12, 0, 'Dec', bgcolor=color.new('#252630'), text_color=font_color)
        table.cell(monthly_table, 13, 0, 'Year', bgcolor=color.new('#3C3D49'), text_color=font_color)

        if final_years_count > 0:
            for i in pine_range(0, final_years_count - 1):
                savedTime: int = array.get(year_time, i)
                yearVal: int = year(savedTime)

                table.cell(monthly_table, 0, i + 1, string.tostring(yearVal), bgcolor=color.new('#252630'), text_color=font_color)

                yPnl: float = array.get(year_pnl, i)
                yColor: Color = color.new(color.new('#0097A7'), 50) if yPnl >= 0 else color.new(color.new('#FF195F'), 50)
                table.cell(monthly_table, 13, i + 1, string.tostring(math.round(yPnl * 100, prec)), bgcolor=yColor, text_color=font_color)

        row_current_year: int = final_years_count + 1

        if final_months_count > 0:
            for m in pine_range(0, final_months_count - 1):
                mTime: int = array.get(month_time, m)
                mPnL: float = array.get(month_pnl, m)
                mYear: int = year(mTime)
                mMonth: int = month(mTime)

                rowIdx: int = na(int)
                if final_years_count > 0:
                    for y_i in pine_range(0, final_years_count - 1):
                        yTime: int = array.get(year_time, y_i)
                        if year(yTime) == mYear:
                            rowIdx = y_i + 1
                            break

                if na(rowIdx) and mYear == year(time):
                    rowIdx = row_current_year

                if not na(rowIdx):
                    mColor: Color = color.new(color.new('#0097A7'), 70) if mPnL >= 0 else color.new(color.new('#FF195F'), 70)
                    table.cell(monthly_table, mMonth, rowIdx, string.tostring(math.round(mPnL * 100, prec)), bgcolor=mColor, text_color=font_color)

        table.cell(monthly_table, 0, row_current_year, string.tostring(year(time)), bgcolor=color.new(color.new('#3C3D49'), 0), text_color=font_color)

        curMonth: int = month(time)
        moColor: Color = color.new(color.new('#0097A7'), 70) if cur_month_pnl >= 0 else color.new(color.new('#FF195F'), 70)
        table.cell(monthly_table, curMonth, row_current_year, string.tostring(math.round(cur_month_pnl * 100, prec)), bgcolor=moColor, text_color=font_color)

        yrColor: Color = color.new(color.new('#0097A7'), 50) if cur_year_pnl >= 0 else color.new(color.new('#FF195F'), 50)
        table.cell(monthly_table, 13, row_current_year, string.tostring(math.round(cur_year_pnl * 100, prec)), bgcolor=yrColor, text_color=font_color)

    if not showTable and (not na(monthly_table)):
        table.clear(monthly_table, 0, 0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
