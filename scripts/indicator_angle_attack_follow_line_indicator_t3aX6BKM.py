"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, barcolor, bgcolor, close, color, high, hline, input,
    location, low, math, na, nz, plot, plotshape, request, script, shape, size, syminfo, ta
)
from pynecore.types import Series


@script.indicator(shorttitle='AAFLI', title='Angle Attack Follow Line Indicator ', overlay=False, max_bars_back=1000, na_bool=True)
def main(
    FL=input(title='🔰🔰🔰🔰 FOLLOW LINE CURRENT CHART RESOLUTION 🔰🔰🔰🔰', defval=True),
    BBperiod=input.int(defval=21, title='Period', minval=1),
    BBdeviations=input.float(defval=1.0, title='Deviations', minval=0.1, step=0.05),
    UseATRfilter=input(defval=True, title='ATR Filter'),
    ATRperiod=input.int(defval=5, title='ATR Period', minval=1),
    FLH=input(title='🔰🔰🔰🔰🔰 FOLLOW LINE HIGHER TIME FRAME 🔰🔰🔰🔰🔰', defval=True),
    AIB=input(defval=True, title='Activate Indicator Background'),
    TYPE=input.string(title='Type Of MA', defval='SMA', options=('RMA', 'SMA', 'EMA', 'WMA', 'VWMA', 'SMMA', 'KMA', 'TMA', 'HullMA', 'DEMA', 'TEMA', 'CTI')),
    RES=input.timeframe('240', title='Resolution'),
    LEN=input(21, title='Period'),
    BBdeviations_=input.float(defval=1.0, title='Deviations', minval=0.1, step=0.05),
    ATRperiod_=input.int(defval=5, title='ATR Period', minval=1),
    SOUR: Series[float] = input(title='Source', defval=close),
    MD=input(title='🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰 MODE 🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰', defval=True),
    MODE=input.string(title='Type Of Mode', defval='NO FILTER HIGHER TIME FRAME', options=('NO FILTER HIGHER TIME FRAME', 'FILTER HIGHER TIME FRAME')),
    AC=input(title='🔰🔰🔰🔰🔰🔰🔰🔰 ANGLE CONFIGURATION 🔰🔰🔰🔰🔰🔰🔰', defval=True),
    i_lookback=input.int(8, 'Angle Period', minval=1),
    i_atrPeriod=input.int(10, 'ATR Period', minval=1),
    BSA=input(title='🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰 BUY/SELL 🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰', defval=True),
    Buy_0=input(defval=True, title='Buy Change Follow Line'),
    Sell_0=input(defval=True, title='Sell Change Follow Line'),
    OTA=input(title='🔰🔰🔰🔰🔰🔰🔰🔰🔰 OPTIONS TO ADD 🔰🔰🔰🔰🔰🔰🔰🔰', defval=True),
    Add_Buy_0=input(defval=True, title='Option 1 to Add Buy'),
    Add_Sell_0=input(defval=True, title='Option 1 to Add Sell'),
    Add_Buy_1=input(defval=False, title='Option 2 to Add Buy'),
    Add_Sell_1=input(defval=False, title='Option 2 to Add Sell'),
    Add_Buy_2=input(defval=False, title='Option 3 to Add Buy'),
    Add_Sell_2=input(defval=False, title='Option 3 to Add Sell'),
    OTR=input(title='🔰🔰🔰🔰🔰🔰🔰🔰 OPTIONS TO REDUCE 🔰🔰🔰🔰🔰🔰🔰🔰', defval=True),
    Max_level_1=input.int(defval=40, title='Max Angle Level 1', minval=1),
    Max_level_2=input.int(defval=65, title='Max Angle Level 2', minval=1),
    Min_level_1=input.int(defval=-40, title='Min Angle Level 1', minval=-100),
    Min_level_2=input.int(defval=-65, title='Min Angle Level 2', minval=-100),
    Red_Buy_0=input(defval=True, title='Option 1 to Reduce Buy Max Angle Level 1'),
    Red_Buy_1=input(defval=True, title='Option 2 to Reduce Buy Max Angle Level 2'),
    Red_Buy_2=input(defval=False, title='Option 3 to Reduce Buy 2 Bars Above Max Angle Level 2'),
    Red_Buy_3=input(defval=True, title='Option 4 to Reduce Buy 3 Bars Above Max Angle Level 2'),
    Red_Buy_4=input(defval=False, title='Option 5 to Reduce Buy 4 Bars Above Max Angle Level 2'),
    Red_Sell_0=input(defval=True, title='Option 1 to Reduce Sell Min Angle Level 1'),
    Red_Sell_1=input(defval=True, title='Option 2 to Reduce Sell Min Angle Level 1'),
    Red_Sell_2=input(defval=False, title='Option 3 to Reduce Sell 2 bars Below Min Angle Level 2'),
    Red_Sell_3=input(defval=True, title='Option 4 to Reduce Sell 3 bars Below Min Angle Level 2'),
    Red_Sell_4=input(defval=False, title='Option 5 to Reduce Sell 4 bars Below Min Angle Level 2'),
    OTH=input(title='🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰 OTHERS 🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰', defval=True),
    i_barColor=input(True, 'Bar Color?'),
    h_lables=input(False, 'Hide Labels')
):
    BBUpper = ta.sma(close, BBperiod) + ta.stdev(close, BBperiod) * BBdeviations
    BBLower = ta.sma(close, BBperiod) - ta.stdev(close, BBperiod) * BBdeviations
    TrendLine: Series[float] = 0.0
    iTrend: Series[float] = 0.0
    BBSignal = 1 if close > BBUpper else -1 if close < BBLower else 0
    if BBSignal == 1 and UseATRfilter == cast_bool(1):
        TrendLine = low - ta.atr(ATRperiod)
        if TrendLine < TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == -1 and UseATRfilter == cast_bool(1):
        TrendLine = high + ta.atr(ATRperiod)
        if TrendLine > TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == 0 and UseATRfilter == cast_bool(1):
        TrendLine = TrendLine[1]
    if BBSignal == 1 and UseATRfilter == cast_bool(0):
        TrendLine = low
        if TrendLine < TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == -1 and UseATRfilter == cast_bool(0):
        TrendLine = high
        if TrendLine > TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == 0 and UseATRfilter == cast_bool(0):
        TrendLine = TrendLine[1]
    iTrend = iTrend[1]
    if TrendLine > TrendLine[1]:
        iTrend = 1
    if TrendLine < TrendLine[1]:
        iTrend = -1
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
        smma__00000060__: Series[float] = 0.0
        smma__00000060__ = ta.sma(src, len) if na(smma__00000060__[1]) else (smma__00000060__[1] * (len - 1) + src) / len
        return smma__00000060__

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

    MA = ma(TYPE, SOUR, LEN)
    MA_MTF = request.security(syminfo.tickerid, RES, MA)
    close_ = request.security(syminfo.tickerid, RES, close)
    low_ = request.security(syminfo.tickerid, RES, low)
    high_ = request.security(syminfo.tickerid, RES, high)
    atr_ = request.security(syminfo.tickerid, RES, ta.atr(ATRperiod_))
    BBUpper_ = MA_MTF + ta.stdev(close_, LEN) * BBdeviations_
    BBLower_ = MA_MTF - ta.stdev(close_, LEN) * BBdeviations_
    TrendLine_MTF: Series[float] = 0.0
    iTrend_: Series[float] = 0.0
    BBSignal_ = 1 if close_ > BBUpper_ else -1 if close_ < BBLower_ else 0
    if BBSignal_ == 1:
        TrendLine_MTF = low_ - atr_
        if TrendLine_MTF < TrendLine_MTF[1]:
            TrendLine_MTF = TrendLine_MTF[1]
    if BBSignal_ == -1:
        TrendLine_MTF = high_ + atr_
        if TrendLine_MTF > TrendLine_MTF[1]:
            TrendLine_MTF = TrendLine_MTF[1]
    if BBSignal_ == 0:
        TrendLine_MTF = TrendLine_MTF[1]
    iTrend_ = iTrend_[1]
    if TrendLine_MTF > TrendLine_MTF[1]:
        iTrend_ = 1
    if TrendLine_MTF < TrendLine_MTF[1]:
        iTrend_ = -1
    def f_angle(_src: Series, _lookback, _atrPeriod):
        rad2degree = 180 / 3.14159265359
        ang = rad2degree * math.atan((_src - _src[_lookback]) / ta.atr(_atrPeriod))
        return ang

    _angle_fl: Series = f_angle(TrendLine, i_lookback, i_atrPeriod)
    buy_0 = 1 if iTrend[1] < 0 and iTrend > 0 and Buy_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    sell_0 = 1 if iTrend[1] > 0 and iTrend < 0 and Sell_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    buy_0_A = 1 if iTrend[1] < 0 and iTrend > 0 and Buy_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    sell_0_A = 1 if iTrend[1] > 0 and iTrend < 0 and Sell_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    add_buy_1 = 1 if _angle_fl[2] > 0 and _angle_fl[1] == 0 and (_angle_fl == 0) and (iTrend > 0) and Add_Buy_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_sell_1 = 1 if _angle_fl[2] < 0 and _angle_fl[1] == 0 and (_angle_fl == 0) and (iTrend < 0) and Add_Sell_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_buy_2 = 1 if _angle_fl[5] > 0 and _angle_fl[4] == 0 and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (iTrend > 0) and Add_Buy_1 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_sell_2 = 1 if _angle_fl[5] < 0 and _angle_fl[4] == 0 and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (iTrend < 0) and Add_Sell_1 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_buy_3 = 1 if _angle_fl[8] > 0 and _angle_fl[7] == 0 and (_angle_fl[6] == 0) and (_angle_fl[5] == 0) and (_angle_fl[4] == 0) and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (iTrend > 0) and Add_Buy_2 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_sell_3 = 1 if _angle_fl[8] < 0 and _angle_fl[7] == 0 and (_angle_fl[6] == 0) and (_angle_fl[5] == 0) and (_angle_fl[4] == 0) and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (iTrend < 0) and Add_Sell_2 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    add_buy_1_A = 1 if _angle_fl[2] > 0 and _angle_fl[1] == 0 and (_angle_fl == 0) and (iTrend > 0) and Add_Buy_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    add_sell_1_A = 1 if _angle_fl[2] < 0 and _angle_fl[1] == 0 and (_angle_fl == 0) and (iTrend < 0) and Add_Sell_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    add_buy_2_A = 1 if _angle_fl[5] > 0 and _angle_fl[4] == 0 and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) and Add_Buy_1 else 0
    add_sell_2_A = 1 if _angle_fl[5] < 0 and _angle_fl[4] == 0 and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) and Add_Sell_1 else 0
    add_buy_3_A = 1 if _angle_fl[8] > 0 and _angle_fl[7] == 0 and (_angle_fl[6] == 0) and (_angle_fl[5] == 0) and (_angle_fl[4] == 0) and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) and Add_Buy_2 else 0
    add_sell_3_A = 1 if _angle_fl[8] < 0 and _angle_fl[7] == 0 and (_angle_fl[6] == 0) and (_angle_fl[5] == 0) and (_angle_fl[4] == 0) and (_angle_fl[3] == 0) and (_angle_fl[2] == 0) and (_angle_fl[1] == 0) and (_angle_fl == 0) and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) and Add_Sell_2 else 0
    Redu_buy_1 = 1 if _angle_fl[1] < Max_level_1 and _angle_fl > Max_level_1 and Red_Buy_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_buy_2 = 1 if _angle_fl[1] < Max_level_2 and _angle_fl > Max_level_2 and Red_Buy_1 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_buy_3 = 1 if _angle_fl[2] < Max_level_2 and _angle_fl[1] > Max_level_2 and (_angle_fl > Max_level_2) and Red_Buy_2 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_buy_4 = 1 if _angle_fl[3] < Max_level_2 and _angle_fl[2] > Max_level_2 and (_angle_fl[1] > Max_level_2) and (_angle_fl > Max_level_2) and Red_Buy_3 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_buy_5 = 1 if _angle_fl[4] < Max_level_2 and _angle_fl[3] > Max_level_2 and (_angle_fl[2] > Max_level_2) and (_angle_fl[1] > Max_level_2) and (_angle_fl > Max_level_2) and Red_Buy_4 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_sell_1 = 1 if _angle_fl[1] > Min_level_1 and _angle_fl < Min_level_1 and Red_Sell_0 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_sell_2 = 1 if _angle_fl[1] > Min_level_2 and _angle_fl < Min_level_2 and Red_Sell_1 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_sell_3 = 1 if _angle_fl[2] > Min_level_2 and _angle_fl[1] < Min_level_2 and (_angle_fl < Min_level_2) and Red_Sell_2 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_sell_4 = 1 if _angle_fl[3] > Min_level_2 and _angle_fl[2] < Min_level_2 and (_angle_fl[1] < Min_level_2) and (_angle_fl < Min_level_2) and Red_Sell_3 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_sell_5 = 1 if _angle_fl[4] > Min_level_2 and _angle_fl[3] < Min_level_2 and (_angle_fl[2] < Min_level_2) and (_angle_fl[1] < Min_level_2) and (_angle_fl < Min_level_2) and Red_Sell_4 and (MODE == 'NO FILTER HIGHER TIME FRAME') else 0
    Redu_buy_1_A = 1 if _angle_fl[1] < Max_level_1 and _angle_fl > Max_level_1 and Red_Buy_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    Redu_buy_2_A = 1 if _angle_fl[1] < Max_level_2 and _angle_fl > Max_level_2 and Red_Buy_1 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    Redu_buy_3_A = 1 if _angle_fl[2] < Max_level_2 and _angle_fl[1] > Max_level_2 and (_angle_fl > Max_level_2) and Red_Buy_2 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    Redu_buy_4_A = 1 if _angle_fl[3] < Max_level_2 and _angle_fl[2] > Max_level_2 and (_angle_fl[1] > Max_level_2) and (_angle_fl > Max_level_2) and Red_Buy_3 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    Redu_buy_5_A = 1 if _angle_fl[4] < Max_level_2 and _angle_fl[3] > Max_level_2 and (_angle_fl[2] > Max_level_2) and (_angle_fl[1] > Max_level_2) and (_angle_fl > Max_level_2) and Red_Buy_4 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == 1) else 0
    Redu_sell_1_A = 1 if _angle_fl[1] > Min_level_1 and _angle_fl < Min_level_1 and Red_Sell_0 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    Redu_sell_2_A = 1 if _angle_fl[1] > Min_level_2 and _angle_fl < Min_level_2 and Red_Sell_1 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    Redu_sell_3_A = 1 if _angle_fl[2] > Min_level_2 and _angle_fl[1] < Min_level_2 and (_angle_fl < Min_level_2) and Red_Sell_2 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    Redu_sell_4_A = 1 if _angle_fl[3] > Min_level_2 and _angle_fl[2] < Min_level_2 and (_angle_fl[1] < Min_level_2) and (_angle_fl < Min_level_2) and Red_Sell_3 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    Redu_sell_5_A = 1 if _angle_fl[4] > Min_level_2 and _angle_fl[3] < Min_level_2 and (_angle_fl[2] < Min_level_2) and (_angle_fl[1] < Min_level_2) and (_angle_fl < Min_level_2) and Red_Sell_4 and (MODE == 'FILTER HIGHER TIME FRAME') and (iTrend_ == -1) else 0
    _color_fl = color.blue if iTrend > 0 else color.red
    plot(_angle_fl, 'Angle Follow Line', _color_fl, 3, plot.style_line)
    plot(_angle_fl, 'Angle Follow Line Histogram', _color_fl, 3, plot.style_histogram)
    hline(Max_level_1, title='Max Angle Level 1', color=color.blue, linestyle=hline.style_dotted, linewidth=1)
    hline(Max_level_2, title='Max Angle Level 2', color=color.blue, linestyle=hline.style_dotted, linewidth=1)
    hline(Min_level_1, title='Min Angle Level 1', color=color.red, linestyle=hline.style_dotted, linewidth=1)
    hline(Min_level_2, title='Min Angle Level 2', color=color.red, linestyle=hline.style_dotted, linewidth=1)
    plotshape(5 if h_lables == False and (cast_bool(sell_0) or cast_bool(sell_0_A)) else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(-5 if h_lables == False and (cast_bool(buy_0) or cast_bool(buy_0_A)) else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (add_sell_1 or add_sell_1_A or add_sell_2 or add_sell_3 or add_sell_2_A or add_sell_3_A) else na, title='Add Sell 1', text='Add', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (add_buy_1 or add_buy_1_A or add_buy_2 or add_buy_3 or add_buy_2_A or add_buy_3_A) else na, title='Add Buy 1', text='Add', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (Redu_buy_1 or Redu_buy_1_A) else na, title='Reduce Buy 1', text='Red', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (Redu_buy_2 or Redu_buy_2_A) else na, title='Reduce Buy 2', text='Red', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (Redu_buy_3 or Redu_buy_3_A) else na, title='Reduce Buy 3', text='Red', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (Redu_buy_4 or Redu_buy_4_A) else na, title='Reduce Buy 4', text='Red', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl + 5 if h_lables == False and (Redu_buy_5 or Redu_buy_5_A) else na, title='Reduce Buy 5', text='Red', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (Redu_sell_1 or Redu_sell_1_A) else na, title='Reduce Sell 1', text='Red', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (Redu_sell_2 or Redu_sell_2_A) else na, title='Reduce Sell 2', text='Red', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (Redu_sell_3 or Redu_sell_3_A) else na, title='Reduce Sell 3', text='Red', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (Redu_sell_4 or Redu_sell_4_A) else na, title='Reduce Sell 4', text='Red', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(_angle_fl - 5 if h_lables == False and (Redu_sell_5 or Redu_sell_5_A) else na, title='Reduce Sell 5', text='Red', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    bgcolor(color.blue if iTrend_ > 0 and AIB else color.red if iTrend_ < 0 and AIB else na)
    barcolor(color.blue if iTrend > 0 else color.red)
    alertcondition(cast_bool(sell_0) or cast_bool(sell_0_A), title='Sell', message='Sell')
    alertcondition(cast_bool(buy_0) or cast_bool(buy_0_A), title='Buy', message='Buy')
    alertcondition(add_sell_1 or add_sell_1_A or add_sell_2 or add_sell_3 or add_sell_2_A or add_sell_3_A, title='Add Sell', message='Add Sell')
    alertcondition(add_buy_1 or add_buy_1_A or add_buy_2 or add_buy_3 or add_buy_2_A or add_buy_3_A, title='Add Buy', message='Add Buy')
    alertcondition(Redu_buy_1 or Redu_buy_1_A or Redu_buy_2 or Redu_buy_2_A or Redu_buy_3 or Redu_buy_3_A or Redu_buy_4 or Redu_buy_4_A or Redu_buy_5 or Redu_buy_5_A, title='Reduce Buy', message='Reduce Buy')
    alertcondition(Redu_sell_1 or Redu_sell_1_A or Redu_sell_2 or Redu_sell_2_A or Redu_sell_3 or Redu_sell_3_A or Redu_sell_4 or Redu_sell_4_A or Redu_sell_5 or Redu_sell_5_A, title='Reduce Sell', message='Reduce Sell')
    alertcondition(sell_0 or sell_0_A or buy_0 or buy_0_A or add_sell_1 or add_sell_1_A or add_sell_2 or add_sell_3 or add_sell_2_A or add_sell_3_A or add_buy_1 or add_buy_1_A or add_buy_2 or add_buy_3 or add_buy_2_A or add_buy_3_A or Redu_buy_1 or Redu_buy_1_A or Redu_buy_2 or Redu_buy_2_A or Redu_buy_3 or Redu_buy_3_A or Redu_buy_4 or Redu_buy_4_A or Redu_buy_5 or Redu_buy_5_A or Redu_sell_1 or Redu_sell_1_A or Redu_sell_2 or Redu_sell_2_A or Redu_sell_3 or Redu_sell_3_A or Redu_sell_4 or Redu_sell_4_A or Redu_sell_5 or Redu_sell_5_A, title='Buy/Sell/Add/Reduce', message='Buy/Sell/Add/Reduce')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
