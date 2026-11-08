"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, chart, close, color, high,
    input, line, location, low, na, open, plotcandle, plotchar, plotshape, script, shape, size, ta
)
from pynecore.types import Line, Persistent


@script.indicator("Change in State of Delivery CISD [AlgoAlpha]", "AlgoAlpha - CISD", True, max_lines_count=500, behind_chart=False)
def main(
    tolerence=input.float(0.7, "Noise Filter", group="Calculations", tooltip="Determines which levels to use as CSID triggers, a larger setting results in less noise", maxval=1, minval=0, step=0.1),
    len=input.int(12, "Swing Period", group="Calculations", tooltip="The period to detect swing points, a larger setting will detect longer term swings"),
    expiry_bars=input.int(100, "Expiry Bars", group="Calculations", tooltip="Number of bars after which old liquidity lines stop updating"),
    liquidity_lookback=input.int(10, "Liquidity Lookback", group="Calculations", tooltip="Lookback period to check if opposing liquidity was wicked before a CISD"),
    green=input.color(color.new('#00FFBB'), title="Bullish Colour", group="Appearance", tooltip="Color used for bullish visuals and positive sentiment texts."),
    red=input.color(color.new('#FF1100'), title="Bearish Colour", group="Appearance", tooltip="Color used for bearish visuals and negative sentiment texts."),
    t1=input.int(90, "Candle Body Transperency", maxval=100, minval=0, group="Appearance"),
    t2=input.int(40, "Candle Wick/Border Transperency", maxval=100, minval=0, group="Appearance"),
    hide_expired_levels=input.bool(True, "Hide Expired Levels", group="Appearance", tooltip="Delete liquidity levels once they exceed the expiry bar threshold."),
    hide_mitigated_levels=input.bool(False, "Hide Mitigated Levels", group="Appearance", tooltip="Delete liquidity levels from the chart as soon as price mitigates them.")
):
    pivlow = ta.pivotlow(len, len)
    pivhigh = ta.pivothigh(len, len)

    swinghighs: Persistent[list[Line]] = array.new_line()
    swinglows: Persistent[list[Line]] = array.new_line()

    if not na(pivhigh):
        array.unshift(swinghighs, line.new(bar_index - len, high[len], bar_index, high[len], color=color.new(chart.fg_color, 50)))
    if not na(pivlow):
        array.unshift(swinglows, line.new(bar_index - len, low[len], bar_index, low[len], color=color.new(chart.fg_color, 50)))

    last_wicked_high_level: Persistent[float] = na(float)
    last_wicked_low_level: Persistent[float] = na(float)

    wicked_high: bool = False
    wicked_low: bool = False

    if array.size(swinghighs) > 0:
        for i in pine_range(array.size(swinghighs) - 1, 0):
            if i < array.size(swinghighs):
                l = array.get(swinghighs, i)
                if bar_index - line.get_x1(l) < expiry_bars:
                    lvl = line.get_y1(l)
                    line.set_x2(l, bar_index)
                    if high >= lvl and barstate.isconfirmed:
                        if hide_mitigated_levels:
                            line.delete(l)
                        array.remove(swinghighs, i)
                        wicked_high = True
                        last_wicked_high_level = lvl
                else:
                    if hide_expired_levels:
                        line.delete(l)
                        array.remove(swinghighs, i)

    if array.size(swinglows) > 0:
        for i in pine_range(array.size(swinglows) - 1, 0):
            if i < array.size(swinglows):
                l = array.get(swinglows, i)
                if bar_index - line.get_x1(l) < expiry_bars:
                    lvl = line.get_y1(l)
                    line.set_x2(l, bar_index)
                    if low <= lvl and barstate.isconfirmed:
                        if hide_mitigated_levels:
                            line.delete(l)
                        array.remove(swinglows, i)
                        wicked_low = True
                        last_wicked_low_level = lvl
                else:
                    if hide_expired_levels:
                        line.delete(l)
                        array.remove(swinglows, i)

    while array.size(swinghighs) > 100:
        line.delete(array.pop(swinghighs))

    while array.size(swinglows) > 100:
        line.delete(array.pop(swinglows))

    bars_since_high = ta.barssince(wicked_high)
    bars_since_low = ta.barssince(wicked_low)

    potential_bull_cisd_level: Persistent[float] = 0.0
    potential_bear_cisd_level: Persistent[float] = 0.0

    o: Persistent[float] = 0.0
    c: Persistent[float] = 0.0

    bear_potential: Persistent[list[float]] = array.new_float()
    bull_potential: Persistent[list[float]] = array.new_float()

    if close[1] < open[1] and close > open:
        array.unshift(bear_potential, bar_index)
        array.unshift(bear_potential, open)

    if close[1] > open[1] and close < open:
        array.unshift(bull_potential, bar_index)
        array.unshift(bull_potential, open)

    cisd: int = 0
    origin_lvl: float = 0.0
    origin_idx: float = 0.0

    if array.size(bear_potential) > 0:
        inloop: bool = True
        while inloop:
            if close < array.first(bear_potential):
                highest: float = 0.0
                __loop_3__ = pine_loop(0)
                while __loop_3__.step(bar_index - array.get(bear_potential, 1)):
                    i = __loop_3__.value
                    if close[i] > highest:
                        highest = close[i]
                running: bool = True
                init = bar_index - array.get(bear_potential, 1) + 1
                top: float = 0.0
                while running:
                    if close[init] < open[init]:
                        top = open[init]
                        init += 1
                    else:
                        running = False
                if (highest - array.first(bear_potential)) / (top - array.first(bear_potential)) > tolerence:
                    origin_lvl = array.first(bear_potential)
                    origin_idx = array.get(bear_potential, 1)
                    array.clear(bear_potential)
                    cisd = 1
                    inloop = False
                else:
                    array.shift(bear_potential)
                    array.shift(bear_potential)
                    if array.size(bear_potential) == 0:
                        inloop = False
            else:
                inloop = False

    if array.size(bull_potential) > 0:
        inloop: bool = True
        while inloop:
            if close > array.first(bull_potential):
                lowest = close
                __loop_3__ = pine_loop(0)
                while __loop_3__.step(bar_index - array.get(bull_potential, 1)):
                    i = __loop_3__.value
                    if close[i] < lowest:
                        lowest = close[i]

                running: bool = True
                init = bar_index - array.get(bull_potential, 1) + 1
                bottom: float = 0.0

                while running:
                    if close[init] > open[init]:
                        bottom = open[init]
                        init += 1
                    else:
                        running = False

                if (array.first(bull_potential) - lowest) / (array.first(bull_potential) - bottom) > tolerence:
                    origin_lvl = array.first(bull_potential)
                    origin_idx = array.get(bull_potential, 1)
                    array.clear(bull_potential)
                    cisd = 2
                    inloop = False
                else:
                    array.shift(bull_potential)
                    array.shift(bull_potential)
                    if array.size(bull_potential) == 0:
                        inloop = False
            else:
                inloop = False

    trend: Persistent[int] = 0

    bearish_sweep: bool = False
    bullish_sweep: bool = False

    if cisd == 1:
        trend = -1
        line.new(cast_int(origin_idx), origin_lvl, bar_index, origin_lvl, color=red, width=3)
        if bars_since_high <= liquidity_lookback and close < last_wicked_high_level:
            bearish_sweep = True

    if cisd == 2:
        trend = 1
        line.new(cast_int(origin_idx), origin_lvl, bar_index, origin_lvl, color=green, width=3)
        if bars_since_low <= liquidity_lookback and close > last_wicked_low_level:
            bullish_sweep = True

    plotshape(high if bearish_sweep else na, 'Bearish CISD with Liquidity Sweep', shape.labeldown, location.abovebar, red, size=size.small, text='▼', textcolor=chart.fg_color)
    plotshape(low if bullish_sweep else na, 'Bullish CISD with Liquidity Sweep', shape.labelup, location.belowbar, green, size=size.small, text='▲', textcolor=chart.fg_color)

    plotchar(high[len] if not na(pivhigh) else na, 'Swing High', '●', location.absolute, red, size=size.tiny, offset=-len)
    plotchar(low[len] if not na(pivlow) else na, 'Swing Low', '●', location.absolute, green, size=size.tiny, offset=-len)

    candle_col = color.from_gradient(t1, 0, 100, green if trend > 0 else red, chart.bg_color)
    candle_col_ = color.from_gradient(t2, 0, 100, green if trend > 0 else red, chart.bg_color)
    plotcandle(open, high, low, close, 'Price Candles', candle_col, candle_col_, bordercolor=candle_col_)

    alertcondition(wicked_high, 'Swing High Mitigation', 'Swing High Mitigated')
    alertcondition(wicked_low, 'Swing Low Mitigation', 'Swing Low Mitigated')
    alertcondition(cisd == 1, 'Bearish Normal CISD', 'Bearish Normal CISD Detected')
    alertcondition(cisd == 2, 'Bullish Normal CISD', 'Bullish Normal CISD Detected')
    alertcondition(bearish_sweep, 'Strong Bearish CISD', 'Strong Bearish CISD Detected')
    alertcondition(bullish_sweep, 'Strong Bullish CISD', 'Strong Bullish CISD Detected')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
