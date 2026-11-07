"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, high, input, low, plot, script, strategy, syminfo, ta,
    time, timestamp
)


@script.strategy('Trend Surfers - Breakout + Alerts', calc_on_every_tick=False, overlay=True, initial_capital=2000, commission_value=0.1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    entry=input(100, 'ENTRY H/L'),
    exit=input(50, 'EXIT H/L'),
    FromYear=input(2015, 'Backtest Start Year'),
    FromMonth=input(1, 'Backtest Start Month'),
    FromDay=input(1, 'Backtest Start Day'),
    ToYear=input(2999, 'Backtest End Year'),
    ToMonth=input(1, 'Backtest End Month'),
    ToDay=input(1, 'Backtest End Day')
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    highestpricelong = inline_series(ta.highest(high, entry), 1)
    plot(highestpricelong, color=color.new(color.green, 0), linewidth=2)
    lowestpricelong = inline_series(ta.lowest(high, exit), 1)
    plot(lowestpricelong, color=color.new(color.green, 0), linewidth=2)
    lowestpriceshort = inline_series(ta.lowest(low, entry), 1)
    plot(lowestpriceshort, color=color.new(color.red, 0), linewidth=2)
    highestpriceshort = inline_series(ta.highest(low, exit), 1)
    plot(highestpriceshort, color=color.new(color.red, 0), linewidth=2)
    entryshort = ta.crossunder(close, lowestpriceshort)
    exitshort = ta.crossover(close, highestpriceshort)
    exitlong = ta.crossover(close, lowestpricelong)
    entrylong = ta.crossover(close, highestpricelong)
    pair = syminfo.basecurrency + syminfo.currency
    entry_long_message = '\nGo Long for ' + pair + 'NOW!' + '\nClose any short position that are open!' + '\n\nFind Trend Surfers on Google' + '\nFor automated premium signals (FREE)'
    entry_short_message = '\nGo Short for ' + pair + 'NOW!' + '\nClose any long position that are open!' + '\n\nFind Trend Surfers on Google' + '\nFor automated premium signals (FREE)'
    exit_long_message = '\nExit Long for ' + pair + 'NOW!' + '\n\nFind Trend Surfers on Google' + '\nFor automated premium signals (FREE)'
    exit_short_message = '\nExit Short for ' + pair + 'NOW!' + '\n\nFind Trend Surfers on Google' + '\nFor automated premium signals (FREE)'
    if entrylong:
        if window():
            strategy.entry('LongEntry', strategy.long, alert_message=entry_long_message)
    if exitlong or entryshort:
        if window():
            strategy.close('LongEntry', alert_message=exit_long_message)
    if entryshort:
        if window():
            strategy.entry('short', strategy.short, alert_message=entry_short_message)
    if exitshort or entrylong:
        if window():
            strategy.close('short', alert_message=exit_short_message)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
