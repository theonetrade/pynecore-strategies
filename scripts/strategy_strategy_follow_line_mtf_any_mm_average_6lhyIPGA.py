"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, input, location, low, math, max_bars_back,
    na, nz, plot, plotshape, request, script, shape, size, strategy, syminfo, ta, time, timeframe,
    timestamp
)
from pynecore.types import Series


@script.strategy(title='Strategy Follow Line MTF Any MM Average', shorttitle='S-FLI_PLUS', overlay=True, precision=8, calc_on_order_fills=True, calc_on_every_tick=True, backtest_fill_limits_assumption=0, default_qty_type=strategy.fixed, default_qty_value=2, initial_capital=10000, pyramiding=1, currency=currency.USD, linktoseries=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    backTestSectionFrom=input(title='═══════════════ From ═══════════════', defval=True),
    FromMonth=input.int(defval=1, title='Month', minval=1),
    FromDay=input.int(defval=1, title='Day', minval=1),
    FromYear=input.int(defval=2014, title='Year', minval=2000),
    backTestSectionTo=input(title='════════════════ To ════════════════', defval=True),
    ToMonth=input.int(defval=31, title='Month', minval=1),
    ToDay=input.int(defval=12, title='Day', minval=1),
    ToYear=input.int(defval=9999, title='Year', minval=2000),
    Config=input(title='══════════════ Config ══════════════', defval=True),
    UCCR=input(True, title='Use Current Chart Resolution?'),
    TYPE=input.string(title='Type Of MA', defval='EMA', options=('RMA', 'SMA', 'EMA', 'WMA', 'VWMA', 'SMMA', 'KMA', 'TMA', 'HullMA', 'DEMA', 'TEMA', 'CTI')),
    RES=input.timeframe('60', title='Resolution'),
    LEN=input(21, title='Period'),
    BBdeviations=input.float(defval=1.0, title='Deviations', minval=0.1, step=0.05),
    ATRperiod=input.int(defval=5, title='ATR Period', minval=1),
    SOUR: Series[float] = input(title='Source', defval=close),
    hl=input(defval=False, title='Hide Labels')
):
    def backTestPeriod():
        return time > timestamp(FromYear, FromMonth, FromDay, 0, 0) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59)

    cd: float = 0.0
    def cti(sm, src, cd):
        di = (sm - 1.0) / 2.0 + 1.0
        c1 = 2 / (di + 1.0)
        c2 = 1 - c1
        c3 = 3.0 * (cd * cd + cd * cd * cd)
        c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
        c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
        i1: Series[float] = 0.0
        i2: Series[float] = 0.0
        i3: Series[float] = 0.0
        i4: Series[float] = 0.0
        i5: Series[float] = 0.0
        i6: Series[float] = 0.0
        i1 = c1 * src + c2 * nz(i1[1])
        i2 = c1 * i1 + c2 * nz(i2[1])
        i3 = c1 * i2 + c2 * nz(i3[1])
        i4 = c1 * i3 + c2 * nz(i4[1])
        i5 = c1 * i4 + c2 * nz(i5[1])
        i6 = c1 * i5 + c2 * nz(i6[1])
        bfr = -cd * cd * cd * i6 + c3 * i5 + c4 * i4 + c5 * i3
        return bfr

    def smma(src, len):
        smma__00000027__: Series[float] = 0.0
        smma__00000027__ = ta.sma(src, len) if na(smma__00000027__[1]) else (smma__00000027__[1] * (len - 1) + src) / len
        return smma__00000027__

    def ma(smoothing, src, length):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(src, length)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(src, length)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(src, length)
                else:
                    __block_result_3__ = na
                    if smoothing == 'WMA':
                        __block_result_3__ = ta.wma(src, length)
                    else:
                        __block_result_4__ = na
                        if smoothing == 'VWMA':
                            __block_result_4__ = ta.vwma(src, length)
                        else:
                            __block_result_5__ = na
                            if smoothing == 'SMMA':
                                __block_result_5__ = smma(src, length)
                            else:
                                __block_result_6__ = na
                                if smoothing == 'HullMA':
                                    __block_result_6__ = ta.wma(2 * ta.wma(src, length / 2) - ta.wma(src, length), math.round(math.sqrt(length)))
                                else:
                                    __block_result_7__ = na
                                    if smoothing == 'LSMA':
                                        __block_result_7__ = src
                                    else:
                                        __block_result_8__ = na
                                        if smoothing == 'KMA':
                                            xPrice: Series = src
                                            xvnoise = math.abs(xPrice - xPrice[1])
                                            nfastend: float = 0.666
                                            nslowend: float = 0.0645
                                            nsignal = math.abs(xPrice - xPrice[length])
                                            nnoise = math.sum(xvnoise, length)
                                            nefratio = nsignal / nnoise if nnoise != 0 else 0
                                            nsmooth = math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)
                                            nAMA: Series[float] = 0.0
                                            nAMA = nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))
                                            __block_result_8__ = nAMA
                                        else:
                                            __block_result_9__ = na
                                            if smoothing == 'TMA':
                                                __block_result_9__ = ta.sma(ta.sma(close, length), length)
                                            else:
                                                __block_result_10__ = na
                                                if smoothing == 'DEMA':
                                                    emaValue = ta.ema(src, length)
                                                    __block_result_10__ = 2 * emaValue - ta.ema(emaValue, length)
                                                else:
                                                    __block_result_11__ = na
                                                    if smoothing == 'TEMA':
                                                        ema1 = ta.ema(src, length)
                                                        ema2 = ta.ema(ema1, length)
                                                        ema3 = ta.ema(ema2, length)
                                                        __block_result_11__ = 3 * ema1 - 3 * ema2 + ema3
                                                    else:
                                                        __block_result_12__ = na
                                                        if smoothing == 'CTI':
                                                            __block_result_12__ = cti(length, src, cd)
                                                        else:
                                                            __block_result_12__ = src
                                                        __block_result_11__ = __block_result_12__
                                                    __block_result_10__ = __block_result_11__
                                                __block_result_9__ = __block_result_10__
                                            __block_result_8__ = __block_result_9__
                                        __block_result_7__ = __block_result_8__
                                    __block_result_6__ = __block_result_7__
                                __block_result_5__ = __block_result_6__
                            __block_result_4__ = __block_result_5__
                        __block_result_3__ = __block_result_4__
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    final_res = timeframe.period if UCCR else RES
    MA = ma(TYPE, SOUR, LEN)
    MA_MTF = request.security(syminfo.tickerid, final_res, MA)
    close_ = request.security(syminfo.tickerid, final_res, close)
    low_ = request.security(syminfo.tickerid, final_res, low)
    high_ = request.security(syminfo.tickerid, final_res, high)
    atr_ = request.security(syminfo.tickerid, final_res, ta.atr(ATRperiod))
    BBUpper = MA_MTF + ta.stdev(close_, LEN) * BBdeviations
    BBLower = MA_MTF - ta.stdev(close_, LEN) * BBdeviations
    v = atr_
    max_bars_back(v, 1000)
    TrendLine: Series[float] = 0.0
    iTrend: Series[float] = 0.0
    buy: float = 0.0
    sell: float = 0.0
    BBSignal = 1 if close_ > BBUpper else -1 if close_ < BBLower else 0
    if BBSignal == 1:
        TrendLine = low_ - v
        if TrendLine < TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == -1:
        TrendLine = high_ + v
        if TrendLine > TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == 0:
        TrendLine = TrendLine[1]
    iTrend = iTrend[1]
    if TrendLine > TrendLine[1]:
        iTrend = 1
    if TrendLine < TrendLine[1]:
        iTrend = -1
    buy = 1 if iTrend[1] == -1 and iTrend == 1 else na
    sell = 1 if iTrend[1] == 1 and iTrend == -1 else na
    plot(TrendLine, color=color.blue if iTrend > 0 else color.red, style=plot.style_line, linewidth=2, title='Trend Line')
    plotshape(TrendLine - v if buy == 1 and hl == False else na, text='💣', style=shape.labelup, location=location.absolute, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    plotshape(TrendLine + v if sell == 1 and hl == False else na, text='🔨', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    if backTestPeriod():
        if buy == 1:
            strategy.entry('long', strategy.long, 1)
        if sell == 1:
            strategy.entry('short', strategy.short, 1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
