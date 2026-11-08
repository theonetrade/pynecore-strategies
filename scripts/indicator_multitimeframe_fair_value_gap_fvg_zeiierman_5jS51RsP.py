"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barmerge, box, chart, close, color, extend, fill, high,
    input, line, low, math, na, nz, ohlc4, open, plot, request, script, string, syminfo, ta, time,
    timeframe, volume, xloc
)
from pynecore.types import Box, Color, Line, NA, Persistent, PersistentSeries, Series


@udt
class Data:
    fvg: list[Box] = na(list)
    bv: list[Box] = na(list)
    sv: list[Box] = na(list)
    mid: list[Line] = na(list)


t1: str = "Select the timeframe for calculating Fair Value Gaps (FVGs).\n\nThis setting controls which candle data  is used to identify FVGs. For example, selecting '15' uses the 15-minute chart even if you’re viewing a different timeframe. \n\nA higher timeframe (e.g., 1H, 4H) can show more significant institutional gaps, while a lower timeframe (e.g., 5min)  can detect intraday inefficiencies."
t2: str = "Adjusts the minimum required candle body size (relative to average) to validate a Fair Value Gap. \n\n**How it works:**\nA wick is considered significant only if it is greater than or equal to the average body size  multiplied by this sensitivity.\n\n- Increase to only show strong, impulsive moves (fewer but more powerful FVGs). \n- Decrease to detect more FVGs, including minor ones (may include noise)."
t3: str = "Enable this to consider a Fair Value Gap 'mitigated' when price reaches the midpoint of the gap. \n\n**Without this**, mitigation requires full price fill from top to bottom of the gap.\n**With this**,  a touch of the midpoint is enough to consider the imbalance resolved.\n\nMidpoint logic allows earlier detection of  mitigation for traders seeking speed over precision."
t4: str = "Toggle the visibility of the Fair Value Gap summary table on the chart.\n\nThis table shows each FVG’s  placement and context. Turning it off hides the visual output (but the logic still runs)."
t5: str = "Adjust the horizontal distance from the current bar to where the FVG info table begins.\n\n**Increase**  to move the table further to the left (away from price).\n**Decrease** to pull the table closer to price action.\nUseful  for positioning the overlay in non-intrusive areas."
t6: str = "Set how far the FVG data table extends to the right of each row.\n\n**Larger values** give more space  per FVG block, useful for long labels or wide screens.\n**Smaller values** create a more compact layout, saving screen real estate."
t7: str = "Control how far each Fair Value Gap box extends into the future.\n\nThis determines the horizontal  length (in bars) of the visual box representing the FVG.\n\n- A higher value keeps unfilled gaps visible longer  (good for swing traders).\n- A lower value limits clutter on active charts (better for scalpers)."
t8: str = "Set the background color used to display **buy-side Fair Value Gaps** (bullish direction).\n\nA more  transparent color makes it subtle, while a more opaque shade makes it prominent."
t9: str = "Set the background color used to display **sell-side Fair Value Gaps** (bearish direction).\n\nUse  this to visually distinguish bearish gaps from bullish ones."
t10: str = "Set the base color used for all FVG boxes and borders.\n\nThis neutral tone is used before the price  fills the gap, or for the general FVG zone display.\nCombine with bullish/bearish highlights for a multi-layered visual effect."
t11: str = "Toggle the display of a trendline based on the average direction of valid Fair Value Gaps. \n\n**Enabled:** You'll see a dynamic line that updates based on confirmed FVGs, giving directional context. \n**Disabled:** No trendline is shown, only individual FVGs are plotted."
t12: str = "Sets the ripple level (in decibels) for the low-pass trend filter that processes FVG trend direction. \n\nHigher values allow more fluctuations (more sensitive).\nLower values produce smoother, slower trend transitions. \n\nRecommended: Start with 10dB and adjust based on market noise."
t13: str = "Sets the cutoff frequency for the trend filter (range: 0 to 0.5).\n\n**Lower values** filter out  more noise (slower trend reaction).\n**Higher values** allow faster reaction to price changes.\n\nSet based on how  reactive you want the FVG trendline to be."
t14: str = "Set the color of the **bullish trendline** when the FVG trend is rising. \n\nUse a vibrant green or lime for clear uptrend confirmation."
t15: str = "Set the color of the **bearish trendline** when the FVG trend is falling. \n\nUse a strong red to clearly highlight downtrends based on FVGs."


@script.indicator('Multitimeframe Fair Value Gap – FVG (Zeiierman)', shorttitle="MTF FVG (Zeiierman)", overlay=True, max_bars_back=5000, max_boxes_count=500)
def main(
    tf=input.timeframe('', title='Timeframe', group="FVG Timeframe", inline='tf'),
    BodySens=input.float(1.0, title='Sensativity', step=0.1, minval=0, group="FVG Timeframe", inline='tf', tooltip=t1 + t2),
    mit=input.bool(True, "Mitigated on mid", group="FVG Mitigation", tooltip=t3),
    showActive=input.bool(False, title='Show FVG table', group="FVG Table", tooltip=t4),
    __input_4__=input.int(5, title='Table Left', minval=0, maxval=30, group="FVG Table", inline='Tab'),
    __input_5__=input.int(10, title='Right', minval=10, maxval=50, group="FVG Table", inline='Tab', tooltip=t5 + t6),
    extendLength=input.int(10, "Extend Boxes", group="FVG Style", tooltip=t7),
    UpCol=input.color(color.new(color.new('#00FFBB'), 50), title='', group="FVG Style", inline='FVG'),
    DnCol=input.color(color.new(color.new('#FF1100'), 50), title='', group="FVG Style", inline='FVG'),
    Col=input.color(color.new(color.gray, 85), title='', group="FVG Style", inline='FVG', tooltip=t8 + t9 + t10),
    showTrend=input.bool(True, title='Show FVG Trend', group="Trend", tooltip=t11),
    rp=input.float(10.0, "Passband Ripple (dB)", group="Trend", minval=0.1, step=0.1, tooltip=t12),
    fc=input.float(0.1, "Cutoff Frequency (0 to 0.5)", group="Trend", minval=0.001, maxval=0.5, step=0.01, tooltip=t13),
    TUpCol=input.color(color.lime, title='', group="Trend", inline='Trend'),
    TDnCol=input.color(color.red, title='', group="Trend", inline='Trend', tooltip=t14 + t15)
):
    TableLeft = __input_4__ * 10
    TableRight = __input_5__ * 10

    bv__global__: Persistent[Data] = Data(array.new_box(), array.new_box(), array.new_box(), array.new_line())
    sv__global__: Persistent[Data] = Data(array.new_box(), array.new_box(), array.new_box(), array.new_line())
    save: Persistent[list[float]] = array.new_float(0)
    FVGs: Persistent[list[Box]] = array.new_box()
    TLine: Persistent[list[float]] = array.new_float(1, 0.0)
    def getMTF():
        return (close, high, low, high[2], low[2], volume)

    def getCandle():
        wick = math.max(close, open) - math.min(close, open)
        array.push(save, wick)
        avgFVG = array.avg(save)
        return (wick, avgFVG)

    def getBarTime(t, barsOffset):
        return t + barsOffset * timeframe.in_seconds(timeframe.period) * 1000

    def BarsBack(val, hl: Series):
        back = time
        for i in pine_range(0, 4999, 1):
            if val == hl[i]:
                back = time[i]
                break
        return back

    def VolumePower(v, c, l, h, ca):
        return math.round(math.round(v * (c - l) / (h - l)) / v * 100) if ca else math.round(math.round(v * (h - c) / (h - l)) / v * 100)

    @method
    def Cleaner(d: Data, cond):
        __block_result__ = na
        if array.size(d.fvg) > 0:
            __block_result_1__ = na
            for i, e in enumerate(d.fvg):
                top = box.get_top(e)
                bot = box.get_bottom(e)
                mid__00000046__ = math.avg(top, bot)
                Cond = (low <= mid__00000046__ if cond else high >= mid__00000046__) if mit else low <= bot if cond else high >= top
                __block_result_2__ = na
                if Cond:
                    box.delete(e)
                    method_call('delete', array.get(d.mid, i))
                    method_call('delete', array.get(d.bv, i))
                    method_call('delete', array.get(d.sv, i))
                    array.remove(d.fvg, i)
                    array.remove(d.mid, i)
                    array.remove(d.bv, i)
                    __block_result_2__ = array.remove(d.sv, i)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def UpdateFVG(Box__ren__):
        __block_result_3__ = na
        if method_call('size', Box__ren__) > 0:
            __block_result_4__ = na
            for e in Box__ren__:
                date = string.format_time(method_call('get_left', e), 'yyyy-MM-dd HH:mm', syminfo.timezone)
                b = box.new(bar_index + TableLeft, method_call('get_top', e), bar_index + TableRight, method_call('get_bottom', e), bgcolor=DnCol if close < method_call('get_bottom', e) else UpCol, border_color=NA(Color), text=date, text_color=chart.fg_color)

                __block_result_4__ = array.push(FVGs, b)
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def FVG(l, l2, h, h2, c1, LBack, L2Back, HBack, H2Back, wick, avgFVG, buyVol, sellVol):
        BullFVG: Series = l > h2 and c1 > h2
        BearFVG: Series = h < l2 and c1 < l2
        if BullFVG and (not BullFVG[1]) and (wick >= avgFVG * BodySens):
            prev = array.get(TLine, 0)
            array.unshift(TLine, math.avg(ohlc4, prev))
            future = getBarTime(HBack, extendLength)
            b = box.new(H2Back, l, future, h2, bgcolor=Col, border_color=Col, extend=extend.none, xloc=xloc.bar_time)
            array.unshift(bv__global__.fvg, b)
            mid__00000062__ = math.avg(l, h2)
            m = line.new(H2Back, mid__00000062__, future, mid__00000062__, xloc=xloc.bar_time, color=color.white, style=line.style_dashed)
            array.unshift(bv__global__.mid, m)
            dist = future - H2Back
            bb = box.new(H2Back, mid__00000062__, cast_int(H2Back + dist * (buyVol / 100)), l, bgcolor=UpCol, border_color=UpCol, extend=extend.none, xloc=xloc.bar_time)
            sb = box.new(H2Back, h2, cast_int(H2Back + dist * (sellVol / 100)), mid__00000062__, bgcolor=DnCol, border_color=DnCol, extend=extend.none, xloc=xloc.bar_time)
            array.unshift(bv__global__.bv, bb)
            array.unshift(bv__global__.sv, sb)
        __block_result_5__ = na
        if BearFVG and (not BearFVG[1]) and (wick >= avgFVG * BodySens):
            prev = array.get(TLine, 0)
            array.unshift(TLine, math.avg(ohlc4, prev))

            future = getBarTime(LBack, extendLength)
            b = box.new(L2Back, l2, future, h, bgcolor=Col, border_color=Col, extend=extend.none, xloc=xloc.bar_time)
            array.unshift(sv__global__.fvg, b)

            mid__00000071__ = math.avg(l2, h)
            m = line.new(L2Back, mid__00000071__, future, mid__00000071__, xloc=xloc.bar_time, color=color.white, style=line.style_dashed)
            array.unshift(sv__global__.mid, m)

            dist = future - L2Back
            bb = box.new(L2Back, mid__00000071__, cast_int(L2Back + dist * (buyVol / 100)), l2, bgcolor=UpCol, border_color=UpCol, extend=extend.none, xloc=xloc.bar_time)
            sb = box.new(L2Back, h, cast_int(L2Back + dist * (sellVol / 100)), mid__00000071__, bgcolor=DnCol, border_color=DnCol, extend=extend.none, xloc=xloc.bar_time)
            array.unshift(sv__global__.bv, bb)
            __block_result_5__ = array.unshift(sv__global__.sv, sb)
        else:
            prev = array.get(TLine, 0)
            __block_result_5__ = array.unshift(TLine, prev)
        return __block_result_5__

    c1, h, l, h2, l2, v = request.security(syminfo.tickerid, tf, getMTF(), lookahead=barmerge.lookahead_on)
    wick, avgFVG = request.security(syminfo.tickerid, tf, getCandle(), lookahead=barmerge.lookahead_on)
    HBack = BarsBack(h, high)
    LBack = BarsBack(l, low)
    H2Back = BarsBack(h2, high)
    L2Back = BarsBack(l2, low)
    buyVol = VolumePower(v, c1, l, h, True)
    sellVol = VolumePower(v, c1, l, h, False)

    FVG(l, l2, h, h2, c1, LBack, L2Back, HBack, H2Back, wick, avgFVG, buyVol, sellVol)
    Cleaner(bv__global__, True)
    Cleaner(sv__global__, False)

    if showActive:
        b: Series = box.new(bar_index + TableLeft, ta.max(high), bar_index + TableRight, ta.min(low), bgcolor=color.new(color.gray, 100), border_color=color.gray, extend=extend.none)
        box.delete(b[1])
        for e in FVGs:
            box.delete(e)
        array.clear(FVGs)
        UpdateFVG(bv__global__.fvg)
        UpdateFVG(sv__global__.fvg)
    TCol: PersistentSeries = color.gray
    Trend: Series = array.get(TLine, 0)
    TCol = TUpCol if Trend > Trend[1] else TDnCol if Trend < Trend[1] else TCol[1]
    src: Series = math.avg(h, l, Trend)
    epsilon = math.sqrt(math.pow(10, rp / 10) - 1)
    d = math.sqrt(1 + epsilon * epsilon)
    c = 1 / math.tan(math.pi * fc)
    norm = 1 / (1 + d * c + c * c)
    b0 = norm
    b1 = 2 * norm
    b2 = norm
    a1 = 2 * norm * (1 - c * c)
    a2 = norm * (1 - d * c + c * c)
    trend: Series[float] = 0.0
    trend = src if bar_index < 2 else b0 * src + b1 * src[1] + b2 * src[2] - a1 * nz(trend[1]) - a2 * nz(trend[2])
    Trend_ = plot(trend if showTrend else na, color=TCol, title='FVG Trend Filter')
    visualclose = ta.ema(Trend, 10)
    visualclose_ = plot(visualclose, color=color.new(color.blue, 100), title='visualtrend', editable=False)
    fill(Trend_, visualclose_, trend, visualclose, color.new(TCol, 70), na, title='Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)