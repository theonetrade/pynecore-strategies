"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barmerge, barstate, bgcolor, close, color, fill, input,
    location, na, plot, plotshape, position, request, script, shape, size, syminfo, ta, table,
    text, time, timestamp
)
from pynecore.types import NA, Persistent, Series, Table


@script.indicator('Hash Ribbons (Capriole Investments)', overlay=False, na_bool=True)
def main(
    type=input.string('Ribbons', options=('Ribbons', 'Oscillator'), title='Plot Type'),
    len_s=input(30, 'Hash Rate Short SMA (days).'),
    len_l=input(60, 'Hash Rate Long SMA (days).'),
    signals=input(True, 'Plot Signals'),
    plot_halvings=input(True, 'Plot Halvings'),
    raw=input(False, 'Plot Raw Hash Rate'),
    source=input.string('INTOTHEBLOCK:BTC_HASHRATE', options=('QUANDL:BCHAIN/HRATE', 'INTOTHEBLOCK:BTC_HASHRATE'), title='Source Hash Rate')
):
    live_HR_raw = request.security(source, 'D', close, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    live_HR_short = request.security(source, 'D', ta.sma(close, len_s), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    live_HR_long = request.security(source, 'D', ta.sma(close, len_l), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    hist_HR_raw = request.security(source, 'D', close, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    hist_HR_short = request.security(source, 'D', ta.sma(close, len_s), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    hist_HR_long = request.security(source, 'D', ta.sma(close, len_l), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    daily_s10 = request.security(syminfo.tickerid, 'D', ta.sma(close, 10), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    daily_s20 = request.security(syminfo.tickerid, 'D', ta.sma(close, 20), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    def is_newbar(res):
        t = time(res)
        return True if ta.change(t) != 0 else False

    since_new_bar: Series = ta.barssince(is_newbar('D'))
    D_total_bars: Series = NA(int)
    D_total_bars = since_new_bar[1] if since_new_bar == 0 else D_total_bars[1]
    HR_short: Series = NA(float)
    HR_long = NA(float)
    HR_raw = NA(float)
    s10: Series = NA(float)
    s20: Series = NA(float)
    HR_short = live_HR_short if barstate.isrealtime else hist_HR_short
    HR_long = live_HR_long if barstate.isrealtime else hist_HR_long
    HR_raw = live_HR_raw if barstate.isrealtime else hist_HR_raw
    s10 = (daily_s10 if since_new_bar == D_total_bars else s10[1]) if barstate.isrealtime else daily_s10
    s20 = (daily_s20 if since_new_bar == D_total_bars else s20[1]) if barstate.isrealtime else daily_s20
    capitulation = ta.crossunder(HR_short, HR_long)
    miner_capitulation = HR_short < HR_long
    recovering = HR_short > HR_short[1] and HR_short > HR_short[2] and (HR_short > HR_short[3]) and miner_capitulation
    recovered = ta.crossover(HR_short, HR_long)
    buy: Series[bool] = False
    barssince_1 = ta.barssince(recovered)
    crossunder_1 = ta.crossunder(s10, s20)
    barssince_2 = ta.barssince(crossunder_1)
    barssince_3 = ta.barssince(recovered)
    barssince_4 = ta.barssince(capitulation)
    crossover_1 = ta.crossover(HR_short, HR_long)
    buy = ta.crossover(s10, s20) and barssince_1 < barssince_2 and (barssince_3 < barssince_4) or (s10 > s20 and crossover_1)
    buy_plot = buy
    delta = HR_short - HR_long
    diff = delta / HR_short * 100
    plot(HR_raw if raw else na, color=color.new(color.green, 0), linewidth=1, style=plot.style_line, title='HR Raw')
    p1 = plot(HR_long if type == 'Ribbons' else na, color=color.new(color.gray, 0), linewidth=2, style=plot.style_line, title='HR SMA Long')
    p2 = plot(HR_short if type == 'Ribbons' else na, color=color.red if HR_short < HR_long else color.lime, linewidth=2, style=plot.style_line, title='HR SMA Short')
    fill(p1, p2, color=color.new(color.red, 30) if HR_short < HR_long else na)
    plot(diff if type == 'Oscillator' else na, style=plot.style_columns, color=color.red if diff < 0 else color.blue, title='Oscillator')
    plotshape((na if na(capitulation) else 1 if capitulation else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.gray, 50), size=size.normal, text='Capitulation', textcolor=color.new(color.black, 50), title='Capitulation')
    plotshape((na if na(miner_capitulation) else 1 if miner_capitulation else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.green, 90), size=size.normal, title='Miner Capitulation')
    plotshape((na if na(recovering) else 1 if recovering else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.green, 50), size=size.normal, title='Recovering')
    plotshape((na if na(recovered) else 1 if recovered else 0) if signals else na, style=shape.circle, location=location.top, color=color.new(color.lime, 0), size=size.normal, textcolor=color.new(color.white, 0), title='Recovered')
    plotshape(buy_plot if signals else na, style=shape.circle, location=location.top, color=color.new(color.blue, 0), size=size.normal, text='Buy', textcolor=color.new(color.blue, 0), title='Buy')
    table_source: Persistent = NA(Table)
    table_source = table.new(position=position.bottom_left, columns=1, rows=1, bgcolor=color.white, border_width=1)
    table.cell(table_source, 0, 0, text='Source: Capriole Investments Limited', bgcolor=color.white, text_color=color.black, width=20, height=7, text_size=size.normal, text_halign=text.align_left)
    halving_1 = timestamp(2012, 11, 28, 0, 0)
    halving_2 = timestamp(2016, 7, 9, 0, 0)
    halving_3 = timestamp(2020, 5, 12, 0, 0)
    band: int = 2
    h1_range = time >= halving_1 - band * 24 * 60 * 60 * 1000 and time <= halving_1 + band * 24 * 60 * 60 * 1000
    h2_range = time >= halving_2 - band * 24 * 60 * 60 * 1000 and time <= halving_2 + band * 24 * 60 * 60 * 1000
    h3_range = time >= halving_3 - band * 24 * 60 * 60 * 1000 and time <= halving_3 + band * 24 * 60 * 60 * 1000
    bgcolor(color.new(color.red, 20) if h1_range and plot_halvings else na)
    bgcolor(color.new(color.red, 20) if h2_range and plot_halvings else na)
    bgcolor(color.new(color.red, 20) if h3_range and plot_halvings else na)
    alertcondition(capitulation, title='Alert - Capitulation')
    alertcondition(recovered, title='Alert - Recovered')
    alertcondition(buy and (not buy[1]), title='Alert - Buy')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
