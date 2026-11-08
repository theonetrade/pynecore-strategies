"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, high, hl2,
    input, low, math, na, nz, open, plot, plotcandle, position, script, string, ta, table, time,
    timestamp
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@udt
class TrendData:
    change: list[float] = na(list)
    t: list[int] = na(list)


t1: str = 'Maximum Length: This parameter sets the upper limit for the number of bars considered in the dynamic moving average. A higher value smooths out the trend line, making it less reactive to minor fluctuations but slower to adapt to sudden price movements. Use higher values for long-term trend analysis and lower values for faster-moving markets.'
t2: str = 'Accelerator Multiplier: Adjusts the responsiveness of the dynamic moving average to price changes. A larger value makes the trend more reactive but can introduce noise in choppy markets. Lower values create a smoother trend but may lag behind rapid price movements. This is particularly useful in volatile markets where precise sensitivity is needed.'
t5: str = 'Enable Candles: When enabled, the candlesticks on the chart will be color-coded based on the calculated trend speed. This provides a visual representation of momentum, making it easier to spot shifts in market dynamics. Disable this if you prefer the standard candlestick colors.'
t6: str = 'Collection Period: Defines the number of bars used to normalize trend speed values. A higher value includes a broader historical range, smoothing out the speed calculation. Lower values make the speed analysis more sensitive to recent price changes, ideal for short-term trading.'
t7: str = 'Enable Table: Activates a statistical table that provides an overview of key metrics, such as average wave height, maximum wave height, dominance, and wave ratios. Useful for traders who want numerical insights to complement visual trend analysis.'
t8: str = 'Lookback Period: Determines how many historical bars are used for calculating bullish and bearish wave data. A longer lookback period provides a more comprehensive view of market trends but may dilute sensitivity to recent market conditions. Shorter periods focus on recent data.'
t9: str = 'Start Date: Sets the starting point for all calculations. This allows you to analyze data only from a specific date onward, which is useful for isolating trends within a certain period or avoiding historical noise.'
t10: str = 'Timer Option: Select between using a custom start date or starting from the first available bar on the chart. The \'Custom\' option works with the Start Date setting, while \'From start\' includes all available data.'


@script.indicator('Trend Speed Analyzer (Zeiierman)', overlay=False)
def main(
    max_length=input.int(50, minval=1, title='Maximum Length', group='Dynamic Moving Average', tooltip=t1),
    accel_multiplier=input.float(5.0, minval=0.0, step=1.1, title='Accelerator Multiplier', group='Dynamic Moving Average', tooltip=t2),
    tbl_=input.bool(True, title='Enable Table', group='Wave Analysis', tooltip=t7),
    lookback_period=input.int(100, minval=1, step=1, title='Lookback Period', group='Wave Analysis', tooltip=t8),
    candle=input.bool(True, title='Enable Candles', group='Trend Visualization', tooltip=t5),
    collen=input.int(100, step=10, minval=5, title='Collection Period', group='Trend Visualization', tooltip=t6),
    up_col=input.color(color.lime, title='Dynamic Trend', group='Trend Visualization', inline='Trend'),
    dn_col=input.color(color.red, title='', group='Trend Visualization', inline='Trend'),
    up_hist_col=input.color(color.new('#82FFC3'), title='Trend Speed Up', group='Trend Visualization', inline='up'),
    up_hist_col_=input.color(color.lime, title='', group='Trend Visualization', inline='up'),
    dn_hist_col=input.color(color.red, title='Trend Speed Dn', group='Trend Visualization', inline='dn'),
    dn_hist_col_=input.color(color.new('#F78C8C'), title='', group='Trend Visualization', inline='dn'),
    start=input.time(timestamp('1 Jan 2020 00:00 +0000'), title='Start Date', group='Time Settings', tooltip=t9, inline='startdate'),
    timer=input.string('From start', title='Timer Option', options=('Custom', 'From start'), group='Time Settings', tooltip=t10, inline='startdate')
):
    tt1: str = 'Average Wave: Shows the average size of bullish or bearish waves during the lookback period. Use this to assess overall market strength. Larger values indicate stronger trends, and comparing bullish vs bearish averages can reveal market bias. For instance, a higher bullish average suggests a stronger uptrend.'
    tt2: str = 'Max Wave: Displays the largest bullish or bearish wave during the lookback period. Use this to identify peak market momentum. A significantly higher bullish or bearish max wave indicates where the market may have shown extreme trend strength in that direction.'
    tt3: str = 'Current Wave Ratio (Average): Compares the current wave\'s size to the average wave size for both bullish and bearish trends. A value above 1 indicates the current wave is stronger than the historical average, which may signal increased market momentum. Use this to evaluate if the current move is significant compared to past trends.'
    tt4: str = 'Current Wave Ratio (Max): Compares the current wave\'s size to the maximum wave size for both bullish and bearish trends. A value above 1 suggests the current wave is setting new highs in strength, which could indicate a breakout or strong momentum in the trend direction.'
    tt5: str = 'Dominance (Average): The net difference between the average bullish and bearish wave sizes. Positive values suggest bullish dominance over time, while negative values indicate bearish dominance. Use this to determine which side (bulls or bears) has had consistent control of the market over the lookback period.'
    tt6: str = 'Dominance (Max): The net difference between the largest bullish and bearish wave sizes. Positive values suggest bulls have dominated with stronger individual waves, while negative values indicate bears have produced stronger waves. Use this to gauge the most significant power shifts in the market.'

    counts_diff: Series = close
    max_abs_counts_diff = ta.highest(math.abs(counts_diff), 200)
    counts_diff_norm = (counts_diff + max_abs_counts_diff) / (2 * max_abs_counts_diff)
    dyn_length = 5 + counts_diff_norm * (max_length - 5)

    def calc_accel_factor(counts_diff: float, prev_counts_diff: float):
        delta_counts_diff = math.abs(counts_diff - prev_counts_diff)

        max_delta_counts_diff: float = ta.highest(delta_counts_diff, 200)
        max_delta_counts_diff = 1 if max_delta_counts_diff == 0 else max_delta_counts_diff

        accel_factor: float = delta_counts_diff / max_delta_counts_diff

        return accel_factor

    def adjust_alpha(dyn_length: float, accel_factor: float, accel_multiplier: float):
        alpha_base = 2 / (dyn_length + 1)
        alpha = alpha_base * (1 + accel_factor * accel_multiplier)
        alpha = math.min(1, alpha)

        return alpha

    accel_factor = calc_accel_factor(counts_diff, nz(counts_diff[1]))
    alpha = adjust_alpha(dyn_length, accel_factor, accel_multiplier)

    dyn_ema: PersistentSeries[float] = na(float)
    dyn_ema = close if na(dyn_ema[1]) else alpha * close + (1 - alpha) * dyn_ema[1]

    trend = dyn_ema
    bullsrc: Series = close
    bearsrc: Series = close

    def StartTime():
        return time > start

    bullish: Persistent[TrendData] = TrendData(array.new_float(), array.new_int())
    bearish: Persistent[TrendData] = TrendData(array.new_float(), array.new_int())
    x1: Persistent = NA(int)
    y1: Persistent = NA(float)
    pos: Persistent[int] = 0
    speed: Persistent[float] = 0.0
    c = ta.rma(close, 10)
    o = ta.rma(open, 10)

    if na(x1) and StartTime() or (na(x1) and timer == 'From start'):
        x1 = bar_index
        y1 = o

    if StartTime() or timer == 'From start':
        if bullsrc > trend and bullsrc[1] <= trend:
            array.unshift(bearish.change, ta.lowest(speed, bar_index - x1))
            array.unshift(bearish.t, bar_index - x1)
            x1 = bar_index
            y1 = bullsrc
            pos = 1
            speed = c - o
        if bearsrc < trend and bearsrc[1] >= trend:
            array.unshift(bullish.change, ta.highest(speed, bar_index - x1))
            array.unshift(bullish.t, bar_index - x1)
            x1 = bar_index
            y1 = bearsrc
            pos = -1
            speed = c - o
    speed = speed + c - o
    speedGradient = color.from_gradient(speed, ta.min(-speed / 3), ta.max(speed / 3), color.red, color.lime)
    trendspeed = ta.hma(speed, 5)

    def rma_dyn_ema(x, p):
        __hist_dyn_ema__: Series[float] = dyn_ema[0]
        average = ta.rma(__hist_dyn_ema__[x], p)
        return average

    colour = up_col if ta.wma(close, 2) > dyn_ema else dn_col
    fillColor = color.new(up_col, 70) if rma_dyn_ema(0, 5) > rma_dyn_ema(1, 5) else color.new(dn_col, 70)
    p1 = plot(dyn_ema, color=colour, linewidth=2, title='Dynamic Trend', force_overlay=True)
    p2 = plot(ta.rma(hl2, 50), display=display.none, editable=False, force_overlay=True)

    min_speed = ta.lowest(speed, collen)
    max_speed = ta.highest(speed, collen)
    normalized_speed = (speed - min_speed) / (max_speed - min_speed)
    speedGradient1 = color.from_gradient(normalized_speed, 0.0, 0.5, dn_hist_col, dn_hist_col_) if speed < 0 else color.from_gradient(normalized_speed, 0.5, 1.0, up_hist_col, up_hist_col_)

    plot(trendspeed if StartTime() or timer == 'From start' else na, title='Trend Speed', color=speedGradient1, style=plot.style_columns)
    plotcandle(open, high, low, close, color=speedGradient1 if candle else na, wickcolor=speedGradient1 if candle else na, bordercolor=speedGradient1 if candle else na, force_overlay=True)

    if barstate.islast and tbl_:
        bullish_recent = array.slice(bullish.change, 0, math.min(lookback_period, array.size(bullish.change)))
        bearish_recent = array.slice(bearish.change, 0, math.min(lookback_period, array.size(bearish.change)))

        bull_max = method_call('max', bullish_recent)
        bear_max = method_call('min', bearish_recent)
        bull_avg = method_call('avg', bullish_recent)
        bear_avg = method_call('avg', bearish_recent)

        wave_size_ratio_avg = bull_avg / math.abs(bear_avg)
        wave_size_text_avg = string.tostring(math.round(wave_size_ratio_avg, 2)) + 'x'
        wave_size_color_avg = color.lime if wave_size_ratio_avg > 0 else color.red

        wave_size_ratio_max = bull_max / math.abs(bear_max)
        wave_size_text_max = string.tostring(math.round(wave_size_ratio_max, 2)) + 'x'
        wave_size_color_max = color.lime if wave_size_ratio_max > 0 else color.red

        dominance_avg_value = bull_avg - math.abs(bear_avg)
        dominance_avg_text = 'Bullish +' + string.tostring(math.round(wave_size_ratio_avg, 2)) + 'x' if dominance_avg_value > 0 else 'Bearish -' + string.tostring(math.round(1 / wave_size_ratio_avg, 2)) + 'x'
        dominance_avg_color = color.lime if dominance_avg_value > 0 else color.red

        dominance_max_value = bull_max - math.abs(bear_max)
        dominance_max_text = 'Bullish +' + string.tostring(math.round(wave_size_ratio_max, 2)) + 'x' if dominance_max_value > 0 else 'Bearish -' + string.tostring(math.round(1 / wave_size_ratio_max, 2)) + 'x'
        dominance_max_color = color.lime if dominance_max_value > 0 else color.red

        current_wave = speed
        current_wave_color = color.lime if current_wave > 0 else color.red

        current_ratio_avg = current_wave / bull_avg if current_wave > 0 else current_wave / math.abs(bear_avg)
        current_ratio_max = current_wave / bull_max if current_wave > 0 else current_wave / math.abs(bear_max)

        current_text_avg = string.tostring(math.round(current_ratio_avg, 2)) + 'x'
        current_text_max = string.tostring(math.round(current_ratio_max, 2)) + 'x'

        current_color_avg = color.lime if current_ratio_avg > 0 else color.red
        current_color_max = color.lime if current_ratio_max > 0 else color.red

        tbl: Persistent = table.new(position.top_right, 3, 3, force_overlay=True)

        table.cell(tbl, 0, 0, '', text_color=chart.fg_color, tooltip='')
        table.cell(tbl, 0, 1, 'Average Wave', text_color=chart.fg_color, tooltip=tt1)
        table.cell(tbl, 0, 2, 'Max Wave', text_color=chart.fg_color, tooltip=tt2)

        table.cell(tbl, 1, 0, 'Current Wave Ratio', text_color=chart.fg_color, tooltip='')
        table.cell(tbl, 1, 1, current_text_avg, text_color=current_color_avg, tooltip=tt3)
        table.cell(tbl, 1, 2, current_text_max, text_color=current_color_max, tooltip=tt4)

        table.cell(tbl, 2, 0, 'Dominance', text_color=chart.fg_color, tooltip='')
        table.cell(tbl, 2, 1, dominance_avg_text, text_color=dominance_avg_color, tooltip=tt5)
        table.cell(tbl, 2, 2, dominance_max_text, text_color=dominance_max_color, tooltip=tt6)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
