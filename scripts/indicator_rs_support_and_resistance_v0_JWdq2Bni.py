"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, barstate, close, color, fill, fixnan, high, input, low, na, plot,
    script, ta
)
from pynecore.types import Color, Series

TITLE: str = 'Support and Resistance'
STITLE: str = 'SR'
tt_altsrc: str = 'Use a alternative series source as the input.'


@script.indicator(TITLE, STITLE, True)
def main(
    use_alt_series=input.bool(False, 'Alternative source:', inline='SRC'),
    alt_src: Series[float] = input.source(close, '', inline='SRC', tooltip=tt_altsrc),
    window1=input.int(8, 'lookback window 1:'),
    window2=input.int(21, 'lookback window 2:'),
    __input_4__=input.float(25.0, 'Percent of the diff to use for trade zone:'),
    use_alerts=input.bool(False, 'Use Alert Signals?')
):
    h: float = alt_src if use_alt_series else high
    l: float = alt_src if use_alt_series else low
    percent_of_range_for_trade_zone: float = 0.01 * __input_4__

    short_term_top: float = ta.valuewhen(h >= ta.highest(h, window1), h, 0)
    short_term_bot: float = ta.valuewhen(l <= ta.lowest(l, window1), l, 0)
    long_term_top: float = ta.valuewhen(h >= ta.highest(h, window2), h, 0)
    long_term_bot: float = ta.valuewhen(l <= ta.lowest(l, window2), l, 0)

    is_new_short_term_resist: bool = not ta.change(short_term_top) != 0 and short_term_top != long_term_top
    is_new_short_term_suport: bool = not ta.change(short_term_bot) != 0 and short_term_bot != long_term_bot
    short_term_resist: Series[float] = short_term_top if is_new_short_term_resist else na
    short_term_suport: Series[float] = short_term_bot if is_new_short_term_suport else na

    long_term_resist: float = na if ta.change(long_term_top) != 0 else long_term_top
    long_term_suport: float = na if ta.change(long_term_bot) != 0 else long_term_bot

    is_new_long_term_resist: bool = ta.change(fixnan(long_term_resist)) != 0
    is_new_long_term_suport: bool = ta.change(fixnan(long_term_suport)) != 0
    long_term_resist_marker: float = long_term_resist if is_new_long_term_resist else na
    long_term_suport_marker: float = long_term_suport if is_new_long_term_suport else na

    col_shrt_term: Color = color.navy
    col_long_term: Color = color.rgb(33, 150, 243, 70)
    col_long_mark: Color = color.blue
    col_bg_resist: Color = color.rgb(255, 152, 0, 80)
    col_bg_suport: Color = color.rgb(128, 128, 0, 80)

    short_term_resist_plot = plot(short_term_resist, 'STR', col_shrt_term, 1, plot.style_linebr)
    short_term_suport_plot = plot(short_term_suport, 'STS', col_shrt_term, 1, plot.style_linebr)
    long_term_resist_plot = plot(long_term_resist, 'LTR', col_long_term, 4, plot.style_linebr)
    long_term_suport_plot = plot(long_term_suport, 'LTS', col_long_term, 4, plot.style_linebr)
    long_term_resist_marker_plot = plot(long_term_resist_marker, '.R', col_long_mark, 4, plot.style_circles)
    long_term_suport_marker_plot = plot(long_term_suport_marker, '.S', col_long_mark, 4, plot.style_circles)

    fill(short_term_resist_plot, long_term_resist_plot, col_bg_resist, 'Resistance')
    fill(short_term_suport_plot, long_term_suport_plot, col_bg_suport, 'Support')

    short_term_resist_trade_limit: Series[float] = na(float)
    short_term_suport_trade_limit: Series[float] = na(float)

    diff: float = fixnan(short_term_resist) - fixnan(short_term_suport)

    if not na(short_term_resist):
        if not na(short_term_resist_trade_limit[1]):
            short_term_resist_trade_limit = short_term_resist_trade_limit[1]
        else:
            short_term_resist_trade_limit = short_term_resist - diff * percent_of_range_for_trade_zone

    if not na(short_term_suport):
        if not na(short_term_suport_trade_limit[1]):
            short_term_suport_trade_limit = short_term_suport_trade_limit[1]
        else:
            short_term_suport_trade_limit = short_term_suport + diff * percent_of_range_for_trade_zone

    short_term_resist_trade_limit_plot = plot(short_term_resist_trade_limit, 'L', color.red, 1, plot.style_linebr)
    short_term_suport_trade_limit_plot = plot(short_term_suport_trade_limit, 'L', color.lime, 1, plot.style_linebr)

    if barstate.isconfirmed:
        if is_new_short_term_resist and na(short_term_resist[1]):
            alert('New short term resistance formed!', alert.freq_once_per_bar_close)
        if is_new_short_term_suport and na(short_term_suport[1]):
            alert('New short term support formed!', alert.freq_once_per_bar_close)
        if is_new_long_term_resist:
            alert('New long term resistance formed!', alert.freq_once_per_bar_close)
        if is_new_long_term_suport:
            alert('New long term support formed!', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
