"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, barmerge, close, color, input, math, na, plot, request, script,
    strategy, syminfo, ta, timeframe
)
from pynecore.types import Series


@script.strategy('Multi Supertrend with no-repaint HTF option strategy', overlay=True, shorttitle='Multi Supertrend', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    HTFSelection=input(title='Select HTF Automatically for Additional Supertrend', defval=False),
    HTFUserSel=input.timeframe(title='Select Higher Timeframe for Additional Supertrend', defval=''),
    Mult1=input.float(title='Multiplier for Default Supertrend', defval=3.0, minval=0, maxval=10),
    Period1=input.int(title='Period for Default Supertrend', defval=10, minval=1, maxval=100),
    Mult2=input.float(title='Multiplier for Additional Supertrend', defval=2.0, minval=0, maxval=10),
    Period2=input.int(title='Period for Additional Supertrend', defval=14, minval=1, maxval=100),
    chbarcol=input(True, title='Change Bar Color'),
    vwapfilter=input(False)
):
    HTFAuto = '5' if timeframe.period == '1' else '15' if timeframe.period == '3' else '15' if timeframe.period == '5' else '60' if timeframe.period == '15' else '60' if timeframe.period == '30' else '60' if timeframe.period == '45' else '240' if timeframe.period == '60' else '240' if timeframe.period == '120' else '240' if timeframe.period == '180' else 'D' if timeframe.period == '240' else 'W' if timeframe.period == 'D' else '5W'
    HTF = HTFAuto if HTFSelection else HTFUserSel
    Trend: Series
    Trailings, Trend = ta.supertrend(Mult1, Period1)
    linecolor = color.teal if Trend == -1 and Trend[1] == -1 else color.red if Trend == 1 and Trend[1] == 1 else color.new(color.white, 100)
    plot(Trailings, color=linecolor, linewidth=2, title='SuperTrend')
    def f_Security(_symbol, _res, _src: Series):
        return request.security(_symbol, _res, _src[1], lookahead=barmerge.lookahead_on)

    def nonVectorSupertrend(Mult, Period):
        Trail_, Trend_ = ta.supertrend(Mult, Period)
        return Trail_ * Trend_

    TrendHtf: Series
    TrailingslHtf, TrendHtf = ta.supertrend(Mult2, Period2)
    if HTF != timeframe.period and HTF != '':
        CompositeTrailHtf = f_Security(syminfo.tickerid, HTF, nonVectorSupertrend(Mult2, Period2))
        TrailingslHtf = math.abs(CompositeTrailHtf)
        TrendHtf = 1 if CompositeTrailHtf > 0 else -1
    linecolorHtf = color.blue if TrendHtf == -1 and TrendHtf[1] == -1 else color.maroon if TrendHtf == 1 and TrendHtf[1] == 1 else color.new(color.white, 100)
    plot(TrailingslHtf, color=linecolorHtf, linewidth=3, title='Supertrend Higher Time Frame')
    barcolor_ = color.lime if Trend == -1 and TrendHtf == -1 else color.red if Trend == 1 and TrendHtf == 1 else color.white
    barcolor(color=barcolor_ if chbarcol else na)
    Long: Series = Trend == -1 and TrendHtf == -1
    Short: Series = Trend == 1 and TrendHtf == 1
    if Long and (not Long[1]) and (vwapfilter and close > ta.vwap or not vwapfilter):
        strategy.entry('enter long', strategy.long, 1)
    if Short and (not Short[1]) and (vwapfilter and close < ta.vwap or not vwapfilter):
        strategy.entry('enter short', strategy.short, 1)
    if Long[1] and (not Long):
        strategy.close('enter long')
    if Short[1] and (not Short):
        strategy.close('enter short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
