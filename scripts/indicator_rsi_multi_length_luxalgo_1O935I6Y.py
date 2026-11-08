"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, barstate, close, color, display, fill, hline, input, math, na, nz,
    plot, position, script, string, table
)
from pynecore.types import Persistent, Series


@script.indicator('RSI Multi Length [LuxAlgo]')
def main(
    max=input(20, 'Maximum Length'),
    min=input(10, 'Minimum Length'),
    overbought=input.float(70, step=10),
    oversold=input.float(30, step=10),
    src: Series[float] = input(close),
    rsi_avg_dn_css=input(color.new('#FF5D00'), 'Average RSI Gradient', group='Style', inline='inline1'),
    rsi_avg_up_css=input(color.new('#2157F3'), '', group='Style', inline='inline1'),
    upper_css=input(color.new('#0CB51A'), 'Upper Level', group='Style'),
    lower_css=input(color.new('#FF1100'), 'Lower Level', group='Style'),
    ob_area=input(color.new(color.new('#0CB51A'), 70), 'Overbought Area', group='Style'),
    os_area=input(color.new(color.new('#FF1100'), 70), 'Oversold Area', group='Style')
):
    N = max - min + 1
    diff = nz(src - src[1])
    num: Persistent[list[float]] = array.new_float(N, 0)
    den: Persistent[list[float]] = array.new_float(N, 0)
    k: int = 0
    overbuy: int = 0
    oversell: int = 0
    avg: float = 0.0
    for i in pine_range(min, max, 1):
        alpha = 1 / i
        num_rma = alpha * diff + (1 - alpha) * array.get(num, k)
        den_rma = alpha * math.abs(diff) + (1 - alpha) * array.get(den, k)
        rsi = 50 * num_rma / den_rma + 50
        avg = avg + rsi
        overbuy = overbuy + 1 if rsi > overbought else overbuy
        oversell = oversell + 1 if rsi < oversold else oversell
        array.set(num, k, num_rma)
        array.set(den, k, den_rma)
        k = k + 1
    avg_rsi = avg / N
    buy_rsi_ma: Series[float] = 0.0
    sell_rsi_ma: Series[float] = 0.0
    buy_rsi_ma = nz(buy_rsi_ma[1] + overbuy / N * (avg_rsi - buy_rsi_ma[1]), avg_rsi)
    sell_rsi_ma = nz(sell_rsi_ma[1] + oversell / N * (avg_rsi - sell_rsi_ma[1]), avg_rsi)
    tb: Persistent = table.new(position.top_right, 2, 2)
    if barstate.islast:
        table.cell(tb, 0, 0, 'Overbought', text_color=color.gray, bgcolor=na)
        table.cell(tb, 1, 0, 'Oversold', text_color=color.gray, bgcolor=na)
        table.cell(tb, 0, 1, string.tostring(overbuy / N * 100, '#.##') + ' %', text_color=color.new('#26A69A'), bgcolor=color.new(color.new('#26A69A'), 80))
        table.cell(tb, 1, 1, string.tostring(oversell / N * 100, '#.##') + ' %', text_color=color.new('#EF5350'), bgcolor=color.new(color.new('#EF5350'), 80))
    css = color.from_gradient(avg_rsi, sell_rsi_ma, buy_rsi_ma, rsi_avg_dn_css, rsi_avg_up_css)
    plot(avg_rsi, 'Average Multi Length RSI', color=css)
    up = plot(buy_rsi_ma, 'Upper Channel', color=upper_css)
    dn = plot(sell_rsi_ma, 'Lower Channel', color=lower_css)
    per_over = plot(overbuy / N * 100, 'Overbought Area', color=color.new(ob_area, 100), editable=False)
    per_under = plot(100 - oversell / N * 100, 'Oversold Area', color=color.new(os_area, 100), editable=False)
    upper = plot(100, color=na, editable=False, display=display.none)
    lower = plot(0, color=na, editable=False, display=display.none)
    fill(per_over, lower, ob_area)
    fill(upper, per_under, os_area)
    fill(up, dn, color.new(css, 90))
    hline(50, color=color.new(color.gray, 50))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
