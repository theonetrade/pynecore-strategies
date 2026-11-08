"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, barstate, box, close, color, display, fill, high, hl2, input,
    location, low, math, na, nz, open, plot, plotshape, script, shape, size, string, ta, text,
    volume
)
from pynecore.types import Box, Color, NA, Persistent, Series

gp_st: str = 'Custom Supertrend Settings'
gp_cloud: str = 'Trend Cloud Settings'
gp_ob: str = 'Order Block Settings'
gp_filt: str = 'Retest Filter Settings'


@script.indicator('Volume-Trend Order Block Engine [BigBeluga]', overlay=True, max_boxes_count=500)
def main(
    st_len=input.int(50, title='Volatility SMA Length', tooltip='Number of candles used to calculate the average range (High - Low).', group=gp_st),
    st_mult=input.float(3.5, title='Multiplier', step=0.1, tooltip='Multiplication factor for the custom volatility band.', group=gp_st),
    show_fill=input.bool(True, title='Show Trend Cloud Fill', tooltip='Enables or disables the background color shading between the close price and the trailing stop line.', group=gp_st),
    cloud_bull_col=input.color(color.new('#00FFCC'), title='Bullish Cloud Color', group=gp_cloud),
    cloud_bear_col=input.color(color.new('#FF007F'), title='Bearish Cloud Color', group=gp_cloud),
    pivot_len=input.int(7, title='Pivot Strength', minval=1, tooltip='The number of bars required to confirm a swing high or swing low pivot (Left & Right strength).', group=gp_ob),
    bull_col=input.color(color.new('#00FFCC'), title='Bullish OB Color', tooltip='Color used for both zones inside a Bullish Order Block.', group=gp_ob),
    bear_col=input.color(color.new('#FF007F'), title='Bearish OB Color', tooltip='Color used for both zones inside a Bearish Order Block.', group=gp_ob),
    txt_col=input.color(color.new('#E0E0E0'), title='OB Text Label Color', tooltip='Color of the Buy % and Sell % text inside the order blocks.', group=gp_ob),
    delete_on_break=input.bool(True, title='Delete OB on Complete Break', tooltip='If enabled, order blocks will be automatically deleted from the chart once price completely breaks past them.', group=gp_ob),
    show_bull_retest=input.bool(True, title='Bullish Retest Signals', tooltip='Enable or disable signals when price cross above the Bullish OB top.', group=gp_filt, inline='bull_ret'),
    bull_vol_pct=input.float(50.0, title='Min Buy %', minval=0.0, maxval=100.0, step=5.0, tooltip='Minimum Buy Volume percentage required in the original pivot window.', group=gp_filt, inline='bull_ret'),
    bull_sig_col=input.color(color.new('#00FFCC'), title='Color', group=gp_filt, inline='bull_ret'),
    show_bear_retest=input.bool(True, title='Bearish Retest Signals', tooltip='Enable or disable signals when price cross below the Bearish OB bottom.', group=gp_filt, inline='bear_ret'),
    bear_vol_pct=input.float(50.0, title='Min Sell %', minval=0.0, maxval=100.0, step=5.0, tooltip='Minimum Sell Volume percentage required in the original pivot window.', group=gp_filt, inline='bear_ret'),
    bear_sig_col=input.color(color.new('#FF007F'), title='Color', group=gp_filt, inline='bear_ret')
):
    src = hl2
    custom_atr: Series = ta.sma(high - low, st_len)
    upper_band: Series = src + st_mult * custom_atr
    lower_band: Series = src - st_mult * custom_atr
    prevLowerBand = nz(lower_band[1])
    prevUpperBand = nz(upper_band[1])

    lower_band = lower_band if lower_band > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
    upper_band = upper_band if upper_band < prevUpperBand or close[1] > prevUpperBand else prevUpperBand
    market_trend: Series[int] = na(int)
    trend_stop: Series[float] = na(float)
    prevSuperTrend = trend_stop[1]
    if na(custom_atr[1]):
        market_trend = 1
    elif prevSuperTrend == prevUpperBand:
        market_trend = 1 if close > upper_band else -1
    else:
        market_trend = -1 if close < lower_band else 1
    trend_stop = lower_band if market_trend == 1 else upper_band

    pivot_low = ta.pivotlow(low, pivot_len, pivot_len)
    pivot_high = ta.pivothigh(high, pivot_len, pivot_len)

    active_top_box: Persistent[Box] = na(Box)
    active_bot_box: Persistent[Box] = na(Box)
    active_top: Persistent[float] = na(float)
    active_bot: Persistent[float] = na(float)
    active_buy_ratio: Persistent[float] = na(float)
    active_ob_trend: Persistent[int] = 0

    def is_overlapping(new_top: float, new_bot: float):
        __block_result__ = na
        if na(active_top) or na(active_bot):
            __block_result__ = False
        else:
            __block_result__ = not (new_bot > active_top or new_top < active_bot)
        return __block_result__

    p_idx = bar_index - pivot_len

    def get_window_volume_ratio(lookback_len: int):
        buy_vol: float = 0.0
        sell_vol: float = 0.0

        for i in pine_range(0, lookback_len, 1):
            if close[i] >= open[i]:
                buy_vol = buy_vol + volume[i]
            else:
                sell_vol = sell_vol + volume[i]

        total_vol = buy_vol + sell_vol
        buy_pct: float = buy_vol / total_vol if total_vol > 0 else 0.5
        return buy_pct

    ob_start_bar: Persistent[int] = na(int)

    if market_trend == 1 and (not na(pivot_low)):
        ob_top = math.min(open[pivot_len], close[pivot_len])
        ob_bot = ob_top - custom_atr

        if not is_overlapping(ob_top, ob_bot):
            if not na(active_top_box):
                box.set_right(active_top_box, p_idx)
                box.set_right(active_bot_box, p_idx)

            ob_start_bar = p_idx
            active_top = ob_top
            active_bot = ob_bot
            active_ob_trend = 1

            buy_ratio: float = get_window_volume_ratio(pivot_len)
            active_buy_ratio = buy_ratio
            sell_ratio: float = 1.0 - buy_ratio
            split_price: float = active_bot + (active_top - active_bot) * buy_ratio

            top_text: str = 'Sell: ' + string.tostring(math.round(sell_ratio * 100)) + '%'
            bot_text: str = 'Buy: ' + string.tostring(math.round(buy_ratio * 100)) + '%'

            active_top_box = box.new(left=ob_start_bar, top=active_top, right=bar_index, bottom=split_price, bgcolor=color.new(bull_col, 85), border_color=color.new(bull_col, 40), text=top_text, text_color=txt_col, text_size=size.small, text_valign=text.align_center, text_halign=text.align_right)
            active_bot_box = box.new(left=ob_start_bar, top=split_price, right=bar_index, bottom=active_bot, bgcolor=color.new(bull_col, 75), border_color=color.new(bull_col, 40), text=bot_text, text_color=txt_col, text_size=size.small, text_valign=text.align_center, text_halign=text.align_right)

    if market_trend == -1 and (not na(pivot_high)):
        ob_bot = math.max(open[pivot_len], close[pivot_len])
        ob_top = ob_bot + custom_atr

        if not is_overlapping(ob_top, ob_bot):
            if not na(active_top_box):
                box.set_right(active_top_box, p_idx)
                box.set_right(active_bot_box, p_idx)

            ob_start_bar = p_idx
            active_top = ob_top
            active_bot = ob_bot
            active_ob_trend = -1

            buy_ratio: float = get_window_volume_ratio(pivot_len)
            active_buy_ratio = buy_ratio
            sell_ratio: float = 1.0 - buy_ratio
            split_price: float = active_bot + (active_top - active_bot) * buy_ratio

            top_text: str = 'Sell: ' + string.tostring(math.round(sell_ratio * 100)) + '%'
            bot_text: str = 'Buy: ' + string.tostring(math.round(buy_ratio * 100)) + '%'

            active_top_box = box.new(left=ob_start_bar, top=active_top, right=bar_index, bottom=split_price, bgcolor=color.new(bear_col, 75), border_color=color.new(bear_col, 40), text=top_text, text_color=txt_col, text_size=size.small, text_valign=text.align_center, text_halign=text.align_right)
            active_bot_box = box.new(left=ob_start_bar, top=split_price, right=bar_index, bottom=active_bot, bgcolor=color.new(bear_col, 85), border_color=color.new(bear_col, 40), text=bot_text, text_color=txt_col, text_size=size.small, text_valign=text.align_center, text_halign=text.align_right)

    if delete_on_break and (not na(active_top)) and (not na(active_bot)):
        is_broken: bool = active_ob_trend == 1 and high < active_bot or (active_ob_trend == -1 and low > active_top)
        if is_broken:
            box.delete(active_top_box)
            box.delete(active_bot_box)
            active_top = na
            active_bot = na
            active_ob_trend = 0

    if not na(active_top_box) and (not na(active_bot_box)):
        box.set_right(active_top_box, bar_index)
        box.set_right(active_bot_box, bar_index)

    active_sell_ratio: float = 1.0 - active_buy_ratio
    bull_threshold: float = bull_vol_pct / 100.0
    bear_threshold: float = bear_vol_pct / 100.0

    marketChange = market_trend != market_trend[1]

    buy_retest: bool = ta.crossover(low, active_top) and show_bull_retest and na(pivot_low) and (not na(active_top)) and (active_buy_ratio >= bull_threshold) and (not marketChange) and barstate.isconfirmed
    sell_retest: bool = ta.crossunder(high, active_bot) and na(pivot_high) and show_bear_retest and (not na(active_bot)) and (active_sell_ratio >= bear_threshold) and (not marketChange) and barstate.isconfirmed

    st_plot = plot(NA(float) if market_trend != market_trend[1] else trend_stop, title='Trend Stop', color=cloud_bull_col if market_trend == 1 else cloud_bear_col, linewidth=1, style=plot.style_linebr)
    price_plot = plot(close, title='Close Price Reference', display=display.none)

    fill_color = (color.new(cloud_bull_col, 80) if market_trend == 1 else color.new(cloud_bear_col, 80)) if show_fill else na
    fill(price_plot, st_plot, close, trend_stop, fill_color, NA(Color))

    plotshape(buy_retest, title='Bullish OB Retest', style=shape.cross, location=location.belowbar, color=bull_sig_col, size=size.tiny)
    plotshape(sell_retest, title='Bearish OB Retest', style=shape.cross, location=location.abovebar, color=bear_sig_col, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
