"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, currency, display, fill, high, input, label,
    low, math, na, nz, plot, script, strategy, ta
)
from pynecore.types import Series


@script.strategy('Kaufman Adaptive Moving Average (KAMA) Strategy [TradeDots]', overlay=True, max_lines_count=500, max_boxes_count=100, initial_capital=10000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.01, default_qty_type=strategy.percent_of_equity, default_qty_value=80, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    lookback_period=input.int(10, title='Length', group='KAMA'),
    ma_source: Series[float] = input(close, 'KAMA Soruce', group='KAMA'),
    fastma_length=input.int(5, 'Fast MA Legnth', minval=1, group='KAMA'),
    slowma_length=input.int(50, 'Slow MA Legnth', minval=1, group='KAMA'),
    input_order_direction=input.string('Long', options=('Long', 'Short', 'Long and Short'), title='Order Direction', group='Strategy'),
    kama_rising_perid=input.int(10, title='Rising Period', group='Strategy'),
    kama_falling_perid=input.int(10, title='Falling Period', group='Strategy')
):
    def pine_kama(source: Series):
        price_change = math.abs(source - source[lookback_period])
        sum_price_change = math.sum(math.abs(source - source[1]), lookback_period)
        fastest = 2 / (fastma_length + 1)
        slowest = 2 / (slowma_length + 1)
        ER = price_change / sum_price_change
        SC = math.pow(ER * (fastest - slowest) + slowest, 2)
        alpha = SC
        sum: Series[float] = 0.0
        sum = source if na(sum[1]) else sum[1] + SC * (close - nz(sum[1]))
        return sum

    kama = pine_kama(ma_source)
    if ta.rising(kama, kama_rising_perid):
        strategy.close('Short')
        if input_order_direction != 'Short' and strategy.opentrades == 0:
            strategy.entry('Long', strategy.long)
            label.new(bar_index, low, '🟢 Long', color=color.new('#9CFF87'), style=label.style_label_up)
    elif ta.falling(kama, kama_falling_perid):
        strategy.close('Long')
        if input_order_direction != 'Long' and strategy.opentrades == 0:
            strategy.entry('Short', strategy.short)
            label.new(bar_index, high, '🔴 Short', color=color.new('#F9396A'), style=label.style_label_down, textcolor=color.white)
    is_pos_closed = strategy.position_size[1] != 0 and strategy.position_size == 0
    is_short: Series = strategy.position_size < 0
    is_long: Series = strategy.position_size > 0
    if is_pos_closed and is_short[1]:
        label.new(bar_index, low, '🟢 Close Short', color=color.new('#9CFF87'), style=label.style_label_up)
    elif is_pos_closed and is_long[1]:
        label.new(bar_index, high, '🔴 Close Long', color=color.new('#F9396A'), style=label.style_label_down, textcolor=color.white)
    closelinePlot = plot(close, '', display=display.none)
    kamaPlot = plot(kama, title='KAMA', color=color.new('#FFFFFF'))
    fill(kamaPlot, closelinePlot, math.max(kama, close), kama, color.new(color.new('#9CFF87'), 75), color.new(color.new('#9CFF87'), 60))
    fill(kamaPlot, closelinePlot, kama, math.min(kama, close), color.new(color.new('#F9396A'), 60), color.new(color.new('#F9396A'), 75))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
