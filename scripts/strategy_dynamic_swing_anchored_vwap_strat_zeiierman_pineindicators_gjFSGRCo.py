"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, chart, close, color, high, hlc3, input, label, low,
    math, na, polyline, script, strategy, ta, volume
)
from pynecore.types import Label, NA, Persistent, PersistentSeries, Polyline, Series
from pynecore.types.chart import ChartPoint


@udt
class dataPoints:
    points: list[ChartPoint] = na(list)
    poly: Polyline = na(Polyline)


t1: str = "Number of bars used to detect swing highs and lows. Larger values identify bigger, more significant swings but react slower. Smaller values detect more frequent swings but may produce more noise."
t2: str = "Controls how quickly the VWAP adjusts to new price action. Lower values make the VWAP react faster (tighter to price), higher values make it smoother and slower to change."
t3: str = "When enabled, the VWAP reaction speed changes automatically based on market volatility. High volatility shortens the tracking period (more responsive), low volatility lengthens it (smoother)."
t4: str = "Controls how strongly volatility influences the VWAP reaction speed. Values above 1 increase the effect of volatility changes; values below 1 make it less sensitive to volatility."
t5: str = "Color used for swing high/low labels drawn on the chart to indicate pivot points."
t6: str = "Color used for swing low labels when marking pivot points."
t7: str = "Color used for VWAP lines when in an uptrend."
t8: str = "Color used for VWAP lines when in a downtrend."
t9: str = "Width of the VWAP lines drawn on the chart. Larger values make the lines thicker and more visible."


@script.strategy('Dynamic Swing Anchored VWAP STRATEGY (Zeiierman X PineIndicators)', overlay=True, max_bars_back=5000, max_labels_count=500, max_polylines_count=100, initial_capital=10000, commission_value=0.01, margin_long=0, margin_short=0, slippage=1)
def main(
    prd=input.int(50, title='Swing Period', minval=2, group='Swing Points', tooltip=t1),
    baseAPT=input.float(20, 'Adaptive Price Tracking', minval=1, step=1, group='Swing Points', tooltip=t2),
    useAdapt=input.bool(False, 'Adapt APT by ATR ratio', group='Swing Points', tooltip=t3),
    volBias=input.float(10.0, 'Volatility Bias', minval=0.1, step=0.1, group='Swing Points', tooltip=t4),
    highS=input.color(color.lime, title="Swing Labels", group="Style", inline="Swing", tooltip=t5),
    lowS=input.color(color.red, title="", group="Style", inline="Swing", tooltip=t6),
    S=input.color(color.lime, title="VWAP Lines", group="Style", inline="VWAP", tooltip=t7),
    R=input.color(color.red, title="", group="Style", inline="VWAP", tooltip=t8),
    xx=input.int(2, minval=1, title="", group="Style", inline="VWAP", tooltip=t9)
):
    b = bar_index

    ph: PersistentSeries = NA(float)
    pl: PersistentSeries = NA(float)
    phL: Persistent = b
    plL: Persistent = b
    lab: Persistent = NA(Label)
    prev: Persistent = NA(float)

    ph = high if ta.highestbars(high, prd) == 0 else ph
    pl = low if ta.lowestbars(low, prd) == 0 else pl
    phL = b if ta.highestbars(high, prd) == 0 else phL
    plL = b if ta.lowestbars(low, prd) == 0 else plL
    dir: Series = 1 if phL > plL else -1

    atrLen: int = 50
    atr = ta.atr(atrLen)
    atrAvg = ta.rma(atr, atrLen)
    ratio = atr / atrAvg if atrAvg > 0 else 1.0

    aptRaw = baseAPT / math.pow(ratio, volBias) if useAdapt else baseAPT
    aptClamped = math.max(5.0, math.min(300.0, aptRaw))
    aptSeries: Series = math.round(aptClamped)

    def alphaFromAPT(apt):
        decay = math.exp(-math.log(2.0) / math.max(1.0, apt))
        return 1.0 - decay

    p: Persistent = hlc3 * volume
    vol: Persistent = volume

    vwap: Persistent[dataPoints] = dataPoints(array.new(0, NA(ChartPoint)))

    if dir != dir[1]:
        x = plL if dir > 0 else phL
        y = pl if dir > 0 else ph
        loc = label.style_label_up if dir > 0 else label.style_label_down
        col = highS if dir > 0 else lowS
        txt = 'LL' if dir > 0 and pl < prev else 'HL' if dir > 0 and pl > prev else 'LH' if dir < 0 and ph < prev else 'HH' if dir < 0 and ph > prev else ''
        label.new(x, y, text=txt, style=loc, color=color.new(col, 20), textcolor=color.white)
        prev = ph[1] if dir > 0 else pl[1]

        barsback = b - x
        p = y * volume[barsback]
        vol = volume[barsback]
        vap = p / vol

        polyline.delete(vwap.poly)
        polyline.new(vwap.points, False, False, line_color=R if dir < 0 else S, line_width=xx)
        array.clear(vwap.points)

        for i in pine_range(barsback, 0, 1):
            apt_i = aptSeries[i]
            alpha = alphaFromAPT(apt_i)

            pxv = hlc3[i] * volume[i]
            v_i = volume[i]

            p = (1.0 - alpha) * p + alpha * pxv
            vol = (1.0 - alpha) * vol + alpha * v_i
            vappe = p / vol if vol > 0 else na

            array.push(vwap.points, chart.point.from_index(b - i, vappe))

        vwap.poly = polyline.new(vwap.points, False, False, line_color=R if dir < 0 else S, line_width=xx)
    else:
        apt_0 = aptSeries
        alpha = alphaFromAPT(apt_0)

        pxv = hlc3 * volume
        v0 = volume

        p = (1.0 - alpha) * p + alpha * pxv
        vol = (1.0 - alpha) * vol + alpha * v0
        vap = p / vol if vol > 0 else na

        polyline.delete(vwap.poly)
        array.push(vwap.points, chart.point.from_index(b, vap))
        vwap.poly = polyline.new(vwap.points, False, False, line_color=R if dir > 0 else S, line_width=xx)

    qty = strategy.equity / close * 5

    if dir > 0:
        strategy.entry('L', strategy.long, qty=qty)

    if dir < 0:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
