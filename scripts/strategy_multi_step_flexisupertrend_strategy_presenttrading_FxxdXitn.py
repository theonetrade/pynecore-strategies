"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, chart, color, currency, display, fill, hl2, hlc3, input,
    location, math, na, nz, plot, plotshape, script, shape, strategy, ta, time
)
from pynecore.types import Color, NA, Persistent, Series


@udt
class supertrend:
    upper: float = _dataclass_field(default_factory=lambda: hl2)
    lower: float = _dataclass_field(default_factory=lambda: hl2)
    output: float = na(float)
    perf: float = 0
    factor: float = na(float)
    trend: int = 0


@udt
class bar:
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)


@udt
class supertrend_:
    s: float = na(float)
    d: int = na(int)


g1: str = 'Entry/Exit: SuperTrend Settings'
gu: str = 'UI Options'


@script.strategy('Multi-Step FlexiSuperTrend - Strategy [presentTrading]', shorttitle='Multi-Step FlexiST-VT - Strategy [presentTrading]', overlay=False, precision=3, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirectionChoice=input.string('Both', 'Trading Direction', options=('Both', 'Long', 'Short')),
    indicatorSource: Series[float] = input.source(hlc3, title='Indicator Source'),
    indicatorLength=input.int(10, minval=2, title='Indicator Length'),
    startingFactor=input.float(0.618, title='Starting Factor', minval=0),
    incrementFactor_1=input.float(0.382, minval=0, step=0.1, title='Increment Factor'),
    normalizeMethod=input.string('None', options=('None', 'Max-Min', 'Absolute Sum'), title='Normalization Method'),
    tp_level1=input.float(title='Take Profit Level 1 (%)', defval=2.0),
    tp_level2=input.float(title='Take Profit Level 2 (%)', defval=8.0),
    tp_level3=input.float(title='Take Profit Level 3 (%)', defval=18.0),
    tp_percent1=input.float(title='Take Profit Percent 1 (%)', defval=30.0),
    tp_percent2=input.float(title='Take Profit Percent 2 (%)', defval=20.0),
    tp_percent3=input.float(title='Take Profit Percent 3 (%)', defval=15.0),
    mesh=input(True, inline='mesh', group='Style'),
    upCss=input.color(color.new(color.new('#089981'), 90), '', inline='mesh', group='Style'),
    dnCss=input.color(color.new(color.new('#F23645'), 90), '', inline='mesh', group='Style'),
    len=input.int(10, 'Length', inline='1', group=g1),
    mlt=input.float(15.0, 'Factor', minval=1, maxval=20, step=0.5, inline='1', group=g1),
    clbl=input.bool(True, 'Contrarian Signals', group=gu),
    colu=input.color(color.new('#008CFF'), 'Bull Color', group=gu),
    cold=input.color(color.new('#FF4800'), 'Bear Color', group=gu)
):
    longEntryTime: Persistent[float] = na(float)
    shortEntryTime: Persistent[float] = na(float)
    recentlyExitedLong: Persistent[bool] = False
    recentlyExitedShort: Persistent[bool] = False
    def norm(value, diffs, den):
        __block_result__ = na
        __switch__ = normalizeMethod
        if __switch__ == 'Max-Min':
            __block_result__ = (value - method_call('min', diffs)) / method_call('range', diffs)
        elif __switch__ == 'Absolute Sum':
            __block_result__ = value / den
        else:
            __block_result__ = value
        normalizeMethod_local = __block_result__
        return normalizeMethod_local

    def SuperTrendPolyfactorOscillator(indicatorSource: Series, indicatorLength, startingFactor, incrementFactor, normalizeMethod):
        holder: Persistent[list[supertrend]] = array.new(0, NA(supertrend))
        diffs: list[float] = array.new_float(0)
        den: float = 0.0
        factor = startingFactor
        if barstate.isfirst:
            for i__00000019__ in pine_range(0, 19, 1):
                array.push(holder, supertrend())
        atr__00000029__ = ta.atr(indicatorLength)
        for i__00000024__ in pine_range(0, 19, 1):
            get_spt = array.get(holder, i__00000024__)
            atr__00000024__ = ta.atr(indicatorLength)
            up__00000024__ = hl2 + atr__00000024__ * factor
            dn__00000024__ = hl2 - atr__00000024__ * factor
            get_spt.trend = 1 if indicatorSource > get_spt.upper else 0 if indicatorSource < get_spt.lower else get_spt.trend
            get_spt.upper = math.min(up__00000024__, get_spt.upper) if indicatorSource[1] < get_spt.upper else up__00000024__
            get_spt.lower = math.max(dn__00000024__, get_spt.lower) if indicatorSource[1] > get_spt.lower else dn__00000024__
            get_spt.output = get_spt.lower if get_spt.trend == 1 else get_spt.upper
            array.push(diffs, indicatorSource - get_spt.output)
            den = den + math.abs(indicatorSource - get_spt.output)
            factor = factor + incrementFactor
        median = norm(array.median(diffs), diffs, den)
        stdev = norm(array.stdev(diffs), diffs, den) if normalizeMethod != 'Max-Min' else na
        return (median, stdev, diffs, den)

    medianValue, stdevValue, diffs, den = SuperTrendPolyfactorOscillator(indicatorSource, indicatorLength, startingFactor, incrementFactor_1, normalizeMethod)
    plot(norm(array.get(diffs, 0), diffs, den) if mesh else na, 'Deviation 1', color=upCss if array.get(diffs, 0) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 1), diffs, den) if mesh else na, 'Deviation 2', color=upCss if array.get(diffs, 1) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 2), diffs, den) if mesh else na, 'Deviation 3', color=upCss if array.get(diffs, 2) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 3), diffs, den) if mesh else na, 'Deviation 4', color=upCss if array.get(diffs, 3) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 4), diffs, den) if mesh else na, 'Deviation 5', color=upCss if array.get(diffs, 4) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 5), diffs, den) if mesh else na, 'Deviation 6', color=upCss if array.get(diffs, 5) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 6), diffs, den) if mesh else na, 'Deviation 7', color=upCss if array.get(diffs, 6) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 7), diffs, den) if mesh else na, 'Deviation 8', color=upCss if array.get(diffs, 7) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 8), diffs, den) if mesh else na, 'Deviation 9', color=upCss if array.get(diffs, 8) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 9), diffs, den) if mesh else na, 'Deviation 10', color=upCss if array.get(diffs, 9) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 10), diffs, den) if mesh else na, 'Deviation 11', color=upCss if array.get(diffs, 10) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 11), diffs, den) if mesh else na, 'Deviation 12', color=upCss if array.get(diffs, 11) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 12), diffs, den) if mesh else na, 'Deviation 13', color=upCss if array.get(diffs, 12) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 13), diffs, den) if mesh else na, 'Deviation 14', color=upCss if array.get(diffs, 13) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 14), diffs, den) if mesh else na, 'Deviation 15', color=upCss if array.get(diffs, 14) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 15), diffs, den) if mesh else na, 'Deviation 16', color=upCss if array.get(diffs, 15) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 16), diffs, den) if mesh else na, 'Deviation 17', color=upCss if array.get(diffs, 16) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 17), diffs, den) if mesh else na, 'Deviation 18', color=upCss if array.get(diffs, 17) > 0 else dnCss, style=plot.style_histogram)
    plot(norm(array.get(diffs, 18), diffs, den) if mesh else na, 'Deviation 19', color=upCss if array.get(diffs, 18) > 0 else dnCss, style=plot.style_histogram)
    plot(medianValue, 'Median', color.new('#90BFF9') if medianValue > (0.5 if normalizeMethod == 'Max-Min' else 0) else color.new('#FFCC80'))
    up = plot(stdevValue, color=na, editable=False)
    dn = plot(-stdevValue, color=na, editable=False)
    fill(up, dn, color.new(color.new('#90BFF9'), 80), title='Stdev Area')
    @method
    def src(b: bar, src__0000008d__: str):
        __block_result_1__ = na
        __switch__ = src__0000008d__
        if __switch__ == 'oc2':
            __block_result_1__ = math.avg(b.o, b.c)
        elif __switch__ == 'hl2':
            __block_result_1__ = math.avg(b.h, b.l)
        elif __switch__ == 'hlc3':
            __block_result_1__ = math.avg(b.h, b.l, b.c)
        elif __switch__ == 'ohlc4':
            __block_result_1__ = math.avg(b.o, b.h, b.l, b.c)
        elif __switch__ == 'hlcc4':
            __block_result_1__ = math.avg(b.h, b.l, b.c, b.c)
        x: float = __block_result_1__
        return x

    @method
    def atr(b: bar, len: int):
        field_0: Series[float] = b.h
        field_1: Series[float] = b.c
        field_2: Series[float] = b.c
        tr: float = b.h - b.l if na(field_0[1]) else math.max(math.max(b.h - b.l, math.abs(b.h - field_1[1])), math.abs(b.l - field_2[1]))
        return tr if len == 1 else ta.rma(tr, len)

    @method
    def st(b: bar, factor: float, len: int):
        atr__000000b2__: Series[float] = atr(b, len)
        up: Series[float] = src(b, 'hl2') + factor * atr__000000b2__
        field_3: Series[float] = b.c
        up = up if up < nz(up[1]) or field_3[1] > nz(up[1]) else nz(up[1])
        dn: Series[float] = src(b, 'hl2') - factor * atr__000000b2__
        field_4: Series[float] = b.c
        dn = dn if dn > nz(dn[1]) or field_4[1] < nz(dn[1]) else nz(dn[1])
        st__000000b2__: Series[float] = na(float)
        dir: int = na(int)
        __block_result_2__ = na
        if na(atr__000000b2__[1]):
            __block_result_2__ = 1
        elif st__000000b2__[1] == nz(up[1]):
            dir = -1 if b.c > up else 1
            __block_result_2__ = dir
        else:
            dir = 1 if b.c < dn else -1
            __block_result_2__ = dir
        dir = __block_result_2__
        st__000000b2__ = dn if dir == -1 else up
        return supertrend_(st__000000b2__, dir)

    tp: Persistent[str] = 'Choose an indicator source of which to base the SuperTrend on.'
    src__global__: Series = medianValue
    b: bar = bar(nz(src__global__[1]), math.max(nz(src__global__[1]), src__global__), math.min(nz(src__global__[1]), src__global__), src__global__)
    tr: float = atr(b, len)
    st__global__: supertrend_ = st(b, mlt, len)
    __block_result_3__ = na
    __switch__ = st__global__.d
    if __switch__ == 1:
        __block_result_3__ = cold
    elif __switch__ == -1:
        __block_result_3__ = colu
    cst: Color = __block_result_3__
    t = plot(st__global__.s if st__global__.d > 0 else na, 'Bear ST', cst, 1, plot.style_linebr)
    d = plot(st__global__.s if st__global__.d < 0 else na, 'Bull ST', cst, 1, plot.style_linebr)
    i = plot(st__global__.d, 'Direction', display=display.none)
    c = plot(src(b, 'oc2'), 'Filler', display=display.none)
    fill(t, c, color.new(cold, 90))
    fill(d, c, color.new(colu, 90))
    change_1 = ta.change(st__global__.d)
    scon: bool = True if clbl and math.sign(change_1) == 1 else False
    change_2 = ta.change(st__global__.d)
    bcon: bool = True if clbl and math.sign(change_2) == -1 else False
    plotshape(st__global__.s + tr / 3 if scon else na, 'Sell Signal', shape.labeldown, location.absolute, color.new(cold, 60), 0, '𝓢', chart.fg_color)
    plotshape(st__global__.s - tr / 3 if bcon else na, 'Buy Signal', shape.labelup, location.absolute, color.new(colu, 60), 0, '𝓑', chart.fg_color)
    enterLongCondition = st__global__.d < 0 and medianValue > 0
    enterShortCondition = st__global__.d > 0 and medianValue < 0
    if enterLongCondition and (tradeDirectionChoice == 'Long' or tradeDirectionChoice == 'Both') and (strategy.equity > 0):
        if strategy.position_size < 0:
            strategy.close('Short Position')
        strategy.entry('Long Position', strategy.long)
        longEntryTime = time
        recentlyExitedLong = False
        recentlyExitedShort = False
    if enterShortCondition and (tradeDirectionChoice == 'Short' or tradeDirectionChoice == 'Both') and (strategy.equity > 0):
        if strategy.position_size > 0:
            strategy.close('Long Position')
        strategy.entry('Short Position', strategy.short)
        shortEntryTime = time
        recentlyExitedShort = False
        recentlyExitedLong = False
    tp_price1_long = strategy.position_avg_price * (1 + tp_level1 / 100)
    tp_price2_long = strategy.position_avg_price * (1 + tp_level2 / 100)
    tp_price3_long = strategy.position_avg_price * (1 + tp_level3 / 100)
    tp_price1_short = strategy.position_avg_price * (1 - tp_level1 / 100)
    tp_price2_short = strategy.position_avg_price * (1 - tp_level2 / 100)
    tp_price3_short = strategy.position_avg_price * (1 - tp_level3 / 100)
    if strategy.position_size > 0:
        strategy.exit('Take Profit 1', from_entry='Long Position', qty_percent=tp_percent1, limit=tp_price1_long)
        strategy.exit('Take Profit 2', from_entry='Long Position', qty_percent=tp_percent2, limit=tp_price2_long)
        strategy.exit('Take Profit 3', from_entry='Long Position', qty_percent=tp_percent3, limit=tp_price3_long)
    if strategy.position_size < 0:
        strategy.exit('Take Profit 1', from_entry='Short Position', qty_percent=tp_percent1, limit=tp_price1_short)
        strategy.exit('Take Profit 2', from_entry='Short Position', qty_percent=tp_percent2, limit=tp_price2_short)
        strategy.exit('Take Profit 3', from_entry='Short Position', qty_percent=tp_percent3, limit=tp_price3_short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
