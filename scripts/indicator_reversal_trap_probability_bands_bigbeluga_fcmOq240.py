"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, bar_index, close, color, fill, high, input, label, last_bar_index,
    line, low, math, na, plot, script, size, string, ta
)
from pynecore.types import Line, Persistent, PersistentSeries


@script.indicator("Reversal Trap Probability Bands [BigBeluga]", overlay=True, max_labels_count=100, max_lines_count=500)
def main(
    envelope_len=input.int(55, "Envelope Smoothness", minval=1, group="Envelope Settings", tooltip="Changes the length of the central moving average line. Higher values create a smoother, slower channel."),
    multiplier=input.float(4.0, "Envelope Width", minval=0.1, step=0.1, group="Envelope Settings", tooltip="Determines how far the outer bands stretch away from the center baseline based on market volatility."),
    trap_window=input.int(10, "Trap Window (Candles)", minval=1, group="Strategy Settings", tooltip="The maximum number of candles allowed to close completely outside the bands before a reversal is disqualified as a fakeout trap."),
    signal_gap=input.int(10, "Minimum Bars Between Signals", minval=1, group="Strategy Settings", tooltip="Cooldown period. The minimum number of bars required between signal triggers to avoid cluttering your charts."),
    stop_mult=input.float(0.5, "ATR Stop Multiplier", minval=0.1, step=0.1, group="Strategy Settings", tooltip="Multiplies the Average True Range (ATR) value to add safety padding above or below structural key levels."),
    max_bars=input.int(5000, "Max Lookback Bars", minval=1, group="Database Limits", tooltip="Limits the script's historical memory. It will only search and record trades from the last X number of bars."),
    max_trades=input.int(500, "Max Total Trades", minval=1, group="Database Limits", tooltip="Database limit guardrail. Stops saving new trades to memory once the total historical trade counter hits this number."),
    colorDn=input.color(color.rgb(236, 51, 51), "Bearish Theme Color", group="Color Styling", tooltip="Changes the color of the upper envelope boundary, bearish labels, and shading effects."),
    colorUp=input.color(color.rgb(18, 175, 159), "Bullish Theme Color", group="Color Styling", tooltip="Changes the color of the lower envelope boundary, bullish labels, and shading effects."),
    colormid=input.color(color.rgb(120, 123, 134, 50), "MidLine Color", group="Color Styling", tooltip="Changes the color of the middle envelope boundary"),
    label_size_setting=input.string("Small", "Label Size", options=("Auto", "Tiny", "Small", "Normal", "Large", "Huge"), group="Color Styling", tooltip="Adjusts the size of the signal labels displayed on the chart.")
):
    rsi_len: int = 20
    target_source: str = "Basis Line"

    basis = ta.ema(close, envelope_len)
    vola = ta.atr(envelope_len)
    rsi = ta.rsi(close, rsi_len)

    upper_band = basis + multiplier * vola
    lower_band = basis - multiplier * vola

    rsi_bucket = math.max(0, math.min(10, math.round(rsi / 10)))
    atr = ta.atr(100) * stop_mult

    def get_label_size(size_str):
        __block_result__ = na
        __switch__ = size_str
        if __switch__ == "Auto":
            __block_result__ = size.auto
        elif __switch__ == "Tiny":
            __block_result__ = size.tiny
        elif __switch__ == "Small":
            __block_result__ = size.small
        elif __switch__ == "Normal":
            __block_result__ = size.normal
        elif __switch__ == "Large":
            __block_result__ = size.large
        elif __switch__ == "Huge":
            __block_result__ = size.huge
        else:
            __block_result__ = size.small
        return __block_result__

    selected_label_size = get_label_size(label_size_setting)

    bull_total: Persistent[list[int]] = array.new_int(11, 0)
    bull_wins: Persistent[list[int]] = array.new_int(11, 0)
    bear_total: Persistent[list[int]] = array.new_int(11, 0)
    bear_wins: Persistent[list[int]] = array.new_int(11, 0)

    total_trades_count: Persistent[int] = 0
    bars_from_live = last_bar_index - bar_index
    allowed_by_limits = bars_from_live <= max_bars and total_trades_count < max_trades

    close_above_envelope_count: PersistentSeries[int] = 0
    close_below_envelope_count: PersistentSeries[int] = 0

    raw_bear_trap: bool = False
    if close < upper_band:
        if high > upper_band and close[1] < upper_band and (close_above_envelope_count[1] <= trap_window):
            raw_bear_trap = True
        elif close[1] > upper_band and close_above_envelope_count[1] <= trap_window:
            raw_bear_trap = True

    if high > upper_band:
        close_above_envelope_count += 1
    else:
        close_above_envelope_count = 0

    raw_bull_trap: bool = False
    if close > lower_band:
        if low < lower_band and close[1] > lower_band and (close_below_envelope_count[1] <= trap_window):
            raw_bull_trap = True
        elif close[1] < lower_band and close_below_envelope_count[1] <= trap_window:
            raw_bull_trap = True

    if low < lower_band:
        close_below_envelope_count += 1
    else:
        close_below_envelope_count = 0

    last_signal_bar: Persistent[int] = -1000
    can_fire = bar_index - last_signal_bar >= signal_gap

    bull_trap = raw_bull_trap and can_fire
    bear_trap = raw_bear_trap and can_fire

    if bull_trap or bear_trap:
        last_signal_bar = bar_index

    active_bull: Persistent[bool] = False
    bull_target: Persistent[Line] = na(Line)
    bull_stop: Persistent[Line] = na(Line)
    bull_bucket: Persistent[int] = na(int)
    potentialTarget: Persistent[Line] = na(Line)
    Bull_Stop = ta.lowest(low, 2) - atr

    if bull_trap and (not active_bull) and allowed_by_limits:
        active_bull = True
        bull_bucket = rsi_bucket
        total_trades_count += 1

        calculated_target: float = basis if target_source == 'Basis Line' else upper_band

        bull_target = line.new(bar_index, calculated_target, bar_index + 10, calculated_target, color=colorUp, style=line.style_dashed)
        bull_stop = line.new(bar_index, Bull_Stop, bar_index + 10, Bull_Stop, color=colorUp, style=line.style_dashed)
        potentialTarget = line.new(x1=bar_index, y1=low, x2=bar_index + 10, y2=calculated_target, color=colorUp, style=line.style_arrow_right)

        total_attempts = array.get(bull_total, rsi_bucket)
        total_success = array.get(bull_wins, rsi_bucket)
        prob_text: str = "Tracking..."
        rate: float = 0.0

        if total_attempts > 0:
            rate = math.round(total_success / total_attempts * 100)
            prob_text = string.tostring(rate) + '% WIN PROB'

        label.new(x=bar_index, y=low - atr, text='⬆\nTRAP\n' + prob_text + '\n(RSI: ' + string.tostring(math.round(rsi)) + ')', style=label.style_label_up, color=color.new(colorUp, 100), textcolor=colorUp, size=selected_label_size, tooltip='Win Probability: ' + string.tostring(rate) + '%')

    if active_bull:
        line.set_x2(bull_stop, bar_index + 10)
        line.set_x2(bull_target, bar_index + 10)
        line.set_x2(potentialTarget, bar_index + 10)

        if high >= line.get_price(bull_target, bar_index) and bar_index - last_signal_bar > 1:
            array.set(bull_total, bull_bucket, array.get(bull_total, bull_bucket) + 1)
            array.set(bull_wins, bull_bucket, array.get(bull_wins, bull_bucket) + 1)
            active_bull = False
            label.new(bar_index, high, '✓', style=label.style_label_down, color=color.new(colorDn, 100), textcolor=colorUp, size=selected_label_size)
            line.set_x2(bull_stop, bar_index)
            line.set_x2(bull_target, bar_index)
            line.set_x2(potentialTarget, bar_index)
        elif low < line.get_price(bull_stop, bar_index) and bar_index - last_signal_bar > 1:
            array.set(bull_total, bull_bucket, array.get(bull_total, bull_bucket) + 1)
            active_bull = False
            line.set_x2(bull_stop, bar_index)
            line.set_x2(bull_target, bar_index)
            line.set_x2(potentialTarget, bar_index)

    active_bear: Persistent[bool] = False
    bear_target: Persistent[Line] = na(Line)
    bear_stop: Persistent[Line] = na(Line)
    bear_bucket: Persistent[int] = na(int)
    potentialTargetBear: Persistent[Line] = na(Line)
    Bear_Stop = ta.highest(high, 2) + atr

    if bear_trap and (not active_bear) and allowed_by_limits:
        active_bear = True
        bear_bucket = rsi_bucket
        total_trades_count += 1

        calculated_target: float = basis if target_source == 'Basis Line' else lower_band

        bear_target = line.new(bar_index, calculated_target, bar_index + 10, calculated_target, color=colorDn, style=line.style_dashed)
        bear_stop = line.new(bar_index, Bear_Stop, bar_index + 10, Bear_Stop, color=colorDn, style=line.style_dashed)
        potentialTargetBear = line.new(x1=bar_index, y1=high, x2=bar_index + 10, y2=calculated_target, color=colorDn, style=line.style_arrow_right)

        total_attempts = array.get(bear_total, rsi_bucket)
        total_success = array.get(bear_wins, rsi_bucket)
        prob_text: str = "Tracking..."
        rate: float = 0.0

        if total_attempts > 0:
            rate = math.round(total_success / total_attempts * 100)
            prob_text = string.tostring(rate) + '% WIN PROB'

        label.new(x=bar_index, y=high + atr, text=prob_text + '\n(RSI: ' + string.tostring(math.round(rsi)) + ')' + '\nTRAP\n⬇', style=label.style_label_down, color=color.new(colorUp, 100), textcolor=colorDn, size=selected_label_size, tooltip='Win Probability: ' + string.tostring(rate) + '%')

    if active_bear:
        line.set_x2(bear_stop, bar_index + 10)
        line.set_x2(potentialTargetBear, bar_index + 10)
        line.set_x2(bear_target, bar_index + 10)

        if low <= line.get_price(bear_target, bar_index) and bar_index - last_signal_bar > 1:
            array.set(bear_total, bear_bucket, array.get(bear_total, bear_bucket) + 1)
            array.set(bear_wins, bear_bucket, array.get(bear_wins, bear_bucket) + 1)
            active_bear = False
            label.new(bar_index, low, '✓', style=label.style_label_up, color=color.new(colorDn, 100), textcolor=colorDn, size=selected_label_size)
            line.set_x2(bear_stop, bar_index)
            line.set_x2(bear_target, bar_index)
            line.set_x2(potentialTargetBear, bar_index)
        elif high > line.get_price(bear_stop, bar_index) and bar_index - last_signal_bar > 1:
            array.set(bear_total, bear_bucket, array.get(bear_total, bear_bucket) + 1)
            active_bear = False
            line.set_x2(bear_stop, bar_index)
            line.set_x2(bear_target, bar_index)
            line.set_x2(potentialTargetBear, bar_index)

    plot_upper = plot(upper_band, 'Envelope Ceiling', color=color.new(colorDn, 50), linewidth=3)
    plot_lower = plot(lower_band, 'Envelope Floor', color=color.new(colorUp, 50), linewidth=3)
    plot_basis = plot(basis, 'Envelope Baseline', color=colormid, linestyle=plot.linestyle_dashed)

    fill(plot1=plot_upper, plot2=plot_basis, top_value=upper_band, bottom_value=basis, top_color=color.new(colorDn, 90), bottom_color=color.new(colorDn, 100), title='Upper Band Gradient')

    fill(plot1=plot_basis, plot2=plot_lower, top_value=basis, bottom_value=lower_band, top_color=color.new(colorUp, 100), bottom_color=color.new(colorUp, 90), title='Lower Band Gradient')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
