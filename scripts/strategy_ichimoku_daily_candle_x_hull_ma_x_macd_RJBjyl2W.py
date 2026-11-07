"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, color, input, math, open, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy('Ichimoku + Daily-Candle_X + HULL-MA_X + MacD', shorttitle='٩(̾●̮̮̃̾•̃̾)۶', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, max_bars_back=2999, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.25, slippage=1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    Period=input.int(title='Double HullMA X Period', defval=14, minval=1),
    res=input.timeframe(title='Candle X Resolution', defval='D'),
    price: Series[float] = input(title='Source of Price', defval=open),
    conversionPeriod=input.int(9, minval=1, title='Conversion Line Period'),
    basePeriod=input.int(26, minval=1, title='Base Line Period'),
    laggingSpanPeriod=input.int(52, minval=1, title='Lagging Span 2 Period'),
    displacement=input.int(26, minval=1, title='Displacement'),
    MACD_Length=input(9),
    MACD_fastLength=input(12),
    MACD_slowLength=input(26)
):
    hma1 = ta.hma(price, Period)
    hma2 = ta.hma(price[1], Period)
    b = color.lime if hma1 > hma2 else color.red
    c = color.green if hma1 > hma2 else color.red
    d = color.red if hma1 > hma2 else color.green
    D1 = request.security(syminfo.tickerid, res, price, barmerge.gaps_off, barmerge.lookahead_off)
    D2 = request.security(syminfo.tickerid, res, price[1], barmerge.gaps_off, barmerge.lookahead_off)
    def donchian(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    conversionLine = donchian(conversionPeriod)
    baseLine = donchian(basePeriod)
    leadLine1 = math.avg(conversionLine, baseLine)
    leadLine2 = donchian(laggingSpanPeriod)
    LS = price
    offset = -displacement
    MACD = ta.hma(price, MACD_fastLength) - ta.hma(price, MACD_slowLength)
    aMACD = ta.hma(MACD, MACD_Length)
    longCondition = hma1 > hma2 and D1 > D2 and (price > hma2) and (leadLine1 > leadLine2) and (MACD > aMACD)
    if longCondition:
        strategy.entry('Long', strategy.long)
    shortCondition = hma1 < hma2 and D1 < D2 and (price < hma2) and (leadLine1 < leadLine2) and (MACD < aMACD)
    if shortCondition:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
