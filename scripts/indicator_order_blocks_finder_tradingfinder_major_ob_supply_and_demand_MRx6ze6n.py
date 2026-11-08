"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, extend, high, input, line, linefill, low, math,
    na, open, plot, script, ta
)
from pynecore.types import Line, LineFill, Persistent, PersistentSeries, Series
import lib.TFlab.AlertSenderLibrary_TradingFinder.v1 as Alert


@script.indicator('Order Blocks Finder [TradingFinder] Major OB + Supply and Demand Zones', ' OB Finder/ Major OB / Supply & Demand', overlay=True, max_bars_back=5000, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    OBRefine=input.string('On', 'Order Block Refine', options=('On', 'Off'), tooltip='If Order Block Refine is Turned on,' + 'an Attempt is made to Detect the Optimal Range' + 'for the Order Block Using an Error Ccorrection Algorithm.', group='Order Block Setting'),
    RefineType=input.string('Defensive', 'Refine Type', options=('Defensive', 'Aggressive'), tooltip='By Using Aggressive Error Correction Algorithm,' + 'a Large Range is Identified as Block Order.' + 'The Defensive Algorithm Detect a Small Range.', group='Order Block Setting'),
    Show_High=input.string('No', 'Show High Level', options=('No', 'Yes'), tooltip='High Major Levels', group='Major Levels'),
    Show_Low=input.string('No', 'Show Low Level', options=('No', 'Yes'), tooltip='Low Major Levels', group='Major Levels'),
    Show_Support=input.string('No', 'Show Last Support', options=('No', 'Yes'), tooltip='Last Support', group='Support and Resistance'),
    Show_Resistance=input.string('No', 'Show Last Resistance', options=('No', 'Yes'), tooltip='Last Resistance', group='Support and Resistance'),
    DemBxColor=input.color(color.rgb(105, 191, 111, 50), 'Demand Zone Color', group=' Color Setting'),
    SupBxColor=input.color(color.rgb(242, 34, 51, 60), 'Supply Zone Color', group=' Color Setting'),
    Alert__global__=input.string('On', 'Alert', options=('On', 'Off'), tooltip='If you turn on the Alert, you can receive alerts and notifications after setting the "Alert".', group='Alert'),
    AlertName=input.string('Order Blocks Finder [TradingFinder]', 'Alert Name', group='Alert'),
    Frequncy=input.string('Once Per Bar', 'Message Frequency', options=('All', 'Once Per Bar', 'Per Bar Close'), tooltip='The triggering frequency. Possible values are: All' + ' (all function calls trigger the alert), Once Per Bar (the first function call during the bar triggers the alert), ' + ' Per Bar Close (the function call triggers the alert only when it occurs during the last script iteration of the real-time bar,' + ' when it closes). The default is alert.freq_once_per_bar.)', group='Alert'),
    UTC=input.string('UTC', 'Show Alert time by Time Zone', group='Alert'),
    MoreInfo=input.string('On', 'Display More Info', options=('On', 'Off'), group='Alert'),
    MessageBull=input.text_area('Long Position', 'Long Signal Message', group='Alert'),
    MessageBear=input.text_area('Short Position', 'Short Signal Message', group='Alert')
):
    Candle_Range: Series = high - low
    Candle_Body: Series = close - open
    __block_result__ = na
    if Candle_Body > 0:
        __block_result__ = 'Candle Positive'
    elif Candle_Body < 0:
        __block_result__ = 'Candle Negative'
    else:
        __block_result__ = 'Candle no Trend'
    Candle_Trend = __block_result__
    __block_keep_1__: PersistentSeries = na
    if close > high[1]:
        __block_keep_1__ = 'Candle Bull Break'
    elif close < low[1]:
        __block_keep_1__ = 'Candle Bear Break'
    Candle_Break: Series = __block_keep_1__
    bar_index_bull = ta.valuewhen(close > high[1], bar_index, 0)
    bar_index_bear = ta.valuewhen(close < low[1], bar_index, 0)
    start_bar_index_high: Persistent[int] = 0
    start_bar_index_low: Persistent[int] = 0
    lenHighest = bar_index - bar_index_bear + 5
    lenLowest = bar_index - bar_index_bull + 5
    lenHighest1 = bar_index - bar_index_bear + 3
    lenLowest1 = bar_index - bar_index_bull + 3
    __block_result_2__ = na
    if not na(lenHighest):
        __block_result_2__ = lenHighest
    else:
        __block_result_2__ = 1
    HighestLen = __block_result_2__
    __block_result_3__ = na
    if not na(lenLowest):
        __block_result_3__ = lenLowest
    else:
        __block_result_3__ = 1
    LowestLen = __block_result_3__
    __block_result_4__ = na
    if not na(lenHighest1):
        __block_result_4__ = lenHighest1
    else:
        __block_result_4__ = 1
    HighestLen1 = __block_result_4__
    __block_result_5__ = na
    if not na(lenLowest1):
        __block_result_5__ = lenLowest1
    else:
        __block_result_5__ = 1
    LowestLen1 = __block_result_5__
    High_first = ta.highest(high, HighestLen)
    Low_first = ta.lowest(low, LowestLen)
    High_first1 = ta.highest(high, HighestLen1)
    Low_first1 = ta.lowest(low, LowestLen1)
    High_Correct: PersistentSeries[float] = 0.0
    Low_Correct: PersistentSeries[float] = 0.0
    __block_keep_2__: PersistentSeries = na
    if Candle_Break == 'Candle Bear Break' and Candle_Break[1] == 'Candle Bull Break':
        start_bar_index_high = bar_index
        __block_result_7__ = na
        if High_Correct[1] == High_first:
            __block_result_7__ = High_first1
        else:
            __block_result_7__ = High_first
        __block_keep_2__ = __block_result_7__
    High_sec: Series = __block_keep_2__
    __block_keep_3__: PersistentSeries = na
    if Candle_Break == 'Candle Bull Break' and Candle_Break[1] == 'Candle Bear Break':
        start_bar_index_low = bar_index
        __block_result_9__ = na
        if Low_Correct[1] == Low_first:
            __block_result_9__ = Low_first1
        else:
            __block_result_9__ = Low_first
        __block_keep_3__ = __block_result_9__
    Low_sec: Series = __block_keep_3__
    __block_result_10__ = na
    if not na(High_sec):
        __block_result_10__ = High_sec
    else:
        __block_result_10__ = High_sec[1]
    High_Correct = __block_result_10__
    __block_result_11__ = na
    if not na(Low_sec):
        __block_result_11__ = Low_sec
    else:
        __block_result_11__ = Low_sec[1]
    Low_Correct = __block_result_11__
    bar_index_bull_BoS: PersistentSeries[int] = 0
    bar_index_bear_BoS: PersistentSeries[int] = 0
    BoS: Persistent[str] = 'Hi'
    High_Correct_f: PersistentSeries[float] = 0.0
    Low_Correct_f: PersistentSeries[float] = 0.0
    __block_result_12__ = na
    if High_Correct_f == 0:
        __block_result_12__ = High_Correct
    elif High_Correct > High_Correct_f[1] and High_Correct_f != 0:
        __block_result_12__ = High_Correct
    elif High_Correct < High_Correct_f[1]:
        __block_result_13__ = na
        if BoS == 'Bear BoS' and bar_index_bear_BoS >= start_bar_index_high:
            __block_result_13__ = High_Correct
        else:
            __block_result_13__ = High_Correct_f
        __block_result_12__ = __block_result_13__
    elif High_Correct_f == High_Correct_f[1] and High_Correct_f != 0:
        __block_result_12__ = High_Correct_f
    else:
        __block_result_12__ = High_Correct
    High_Correct_f = __block_result_12__
    __block_result_14__ = na
    if Low_Correct_f == 0:
        __block_result_14__ = Low_Correct
    elif Low_Correct < Low_Correct_f[1] and Low_Correct_f != 0:
        __block_result_14__ = Low_Correct
    elif Low_Correct > Low_Correct_f[1]:
        __block_result_15__ = na
        if BoS == 'Bull BoS' and bar_index_bull_BoS >= start_bar_index_low:
            __block_result_15__ = Low_Correct
        else:
            __block_result_15__ = Low_Correct_f
        __block_result_14__ = __block_result_15__
    elif Low_Correct_f == Low_Correct_f[1] and Low_Correct_f != 0:
        __block_result_14__ = Low_Correct_f
    else:
        __block_result_14__ = Low_Correct
    Low_Correct_f = __block_result_14__
    Sline: PersistentSeries[Line] = na(Line)
    Rline: PersistentSeries[Line] = na(Line)
    LV: Series[float] = Low_Correct_f
    LI: int = 0
    HV: Series[float] = High_Correct_f
    HI: int = 0
    if LV != LV[1] and Show_Support == 'Yes':
        line.delete(Sline[1])
        LI = bar_index
        Sline = line.new(LI, LV, LI + 1, LV, extend=extend.right, style=line.style_dotted, color=color.rgb(0, 82, 3))
    if HV != HV[1] and Show_Resistance == 'Yes':
        line.delete(Rline[1])
        HI = bar_index
        Rline = line.new(HI, HV, HI + 1, HV, extend=extend.right, style=line.style_dotted, color=color.rgb(146, 33, 33))
    color_High = color.rgb(5, 148, 10) if High_Correct_f == High_Correct_f[1] else na
    color_Low = color.rgb(184, 0, 0) if Low_Correct_f == Low_Correct_f[1] else na
    plot(High_Correct_f, 'Major High Levels', color=color_High if Show_High == 'Yes' else na)
    plot(Low_Correct_f, 'Major Low Levels', color=color_Low if Show_Low == 'Yes' else na)
    if close > High_Correct_f and close[1] <= High_Correct_f:
        BoS = 'Bull BoS'
        bar_index_bull_BoS = bar_index
    elif close < Low_Correct_f and close[1] >= Low_Correct_f:
        BoS = 'Bear BoS'
        bar_index_bear_BoS = bar_index
    else:
        BoS = '0'
    Trend: Persistent[str] = 'Hi'
    if BoS == 'Bull BoS' and bar_index_bull_BoS[1] > bar_index_bear_BoS:
        Trend = 'Up Trend'
    elif BoS == 'Bear BoS' and bar_index_bear_BoS[1] > bar_index_bull_BoS:
        Trend = 'Down Trend'
    elif Trend == 'Up Trend' and close < Low_Correct_f or (Trend == 'Down Trend' and close > High_Correct_f):
        Trend = 'No Trend'
    else:
        Trend = Trend
    bar_index_Supply_OB = ta.valuewhen(High_Correct != High_Correct[1], bar_index[1], 0)
    bar_index_Demand_OB = ta.valuewhen(Low_Correct != Low_Correct[1], bar_index[1], 0)
    DOB_index: Persistent[int] = 0
    SOB_index: Persistent[int] = 0
    PerDOB_index: Persistent[int] = 0
    PerSOB_index: Persistent[int] = 0
    DemandCheck: Persistent[int] = 0
    SupplyCheck: Persistent[int] = 0
    DOB_index = ta.valuewhen(BoS == 'Bull BoS' and bar_index_bull_BoS[1] > bar_index_bear_BoS or (BoS == 'Bull BoS' and bar_index_bull_BoS > bar_index_bear_BoS), bar_index, 0)
    SOB_index = ta.valuewhen(BoS == 'Bear BoS' and bar_index_bear_BoS[1] > bar_index_bull_BoS or (BoS == 'Bear BoS' and bar_index_bear_BoS > bar_index_bull_BoS), bar_index, 0)
    PerDOB_index = ta.valuewhen(BoS == 'Bull BoS' and bar_index_bull_BoS[1] > bar_index_bear_BoS or (BoS == 'Bull BoS' and bar_index_bull_BoS > bar_index_bear_BoS), bar_index, 1)
    PerSOB_index = ta.valuewhen(BoS == 'Bear BoS' and bar_index_bear_BoS[1] > bar_index_bull_BoS or (BoS == 'Bear BoS' and bar_index_bear_BoS > bar_index_bull_BoS), bar_index, 1)
    Demand_OB_Condition = (BoS == 'Bull BoS' and bar_index_bull_BoS[1] > bar_index_bear_BoS or (BoS == 'Bull BoS' and bar_index_bull_BoS > bar_index_bear_BoS)) and DemandCheck != bar_index_Demand_OB
    Supply_OB_Condition = (BoS == 'Bear BoS' and bar_index_bear_BoS[1] > bar_index_bull_BoS or (BoS == 'Bear BoS' and bar_index_bear_BoS > bar_index_bull_BoS)) and SupplyCheck != bar_index_Supply_OB
    YDp12: PersistentSeries[float] = 0.0
    XDp1: Persistent[int] = 0
    XDp2: Persistent[int] = 0
    YDd12: Persistent[float] = 0.0
    XDd1: Persistent[int] = 0
    XDd2: Persistent[int] = 0
    YSp12: PersistentSeries[float] = 0.0
    XSp1: Persistent[int] = 0
    XSp2: Persistent[int] = 0
    YSd12: Persistent[float] = 0.0
    XSd1: Persistent[int] = 0
    XSd2: Persistent[int] = 0
    ATR = ta.atr(55)
    DCRa1: Persistent[float] = 0.0
    DCRO: Persistent[float] = 0.0
    DCRb1: Persistent[float] = 0.0
    if bar_index >= bar_index_Demand_OB + 1:
        DCRa1 = Candle_Range[bar_index - bar_index_Demand_OB + 1]
        DCRO = Candle_Range[bar_index - bar_index_Demand_OB]
        DCRb1 = Candle_Range[bar_index - bar_index_Demand_OB - 1]
    DminOpen: Persistent[float] = 0.0
    DminHigh: Persistent[float] = 0.0
    DminLow: Persistent[float] = 0.0
    DminClose: Persistent[float] = 0.0
    DmaxOpen: Persistent[float] = 0.0
    DmaxHigh: Persistent[float] = 0.0
    DmaxLow: Persistent[float] = 0.0
    DmaxClose: Persistent[float] = 0.0
    if bar_index > bar_index_Demand_OB + 1:
        DminOpen = math.min(open[bar_index - bar_index_Demand_OB - 2], open[bar_index - bar_index_Demand_OB + 1], open[bar_index - bar_index_Demand_OB], open[bar_index - bar_index_Demand_OB - 1])
        DminHigh = math.min(high[bar_index - bar_index_Demand_OB - 2], high[bar_index - bar_index_Demand_OB + 1], high[bar_index - bar_index_Demand_OB], high[bar_index - bar_index_Demand_OB - 1])
        DminLow = math.min(low[bar_index - bar_index_Demand_OB - 2], low[bar_index - bar_index_Demand_OB + 1], low[bar_index - bar_index_Demand_OB], low[bar_index - bar_index_Demand_OB - 1])
        DminClose = math.min(close[bar_index - bar_index_Demand_OB - 2], close[bar_index - bar_index_Demand_OB + 1], close[bar_index - bar_index_Demand_OB], close[bar_index - bar_index_Demand_OB - 1])
    elif bar_index >= bar_index_Demand_OB:
        DminOpen = math.min(open[bar_index - bar_index_Demand_OB + 1], open[bar_index - bar_index_Demand_OB], open[bar_index - bar_index_Demand_OB - 1])
        DminHigh = math.min(high[bar_index - bar_index_Demand_OB + 1], high[bar_index - bar_index_Demand_OB], high[bar_index - bar_index_Demand_OB - 1])
        DminLow = math.min(low[bar_index - bar_index_Demand_OB + 1], low[bar_index - bar_index_Demand_OB], low[bar_index - bar_index_Demand_OB - 1])
        DminClose = math.min(close[bar_index - bar_index_Demand_OB + 1], close[bar_index - bar_index_Demand_OB], close[bar_index - bar_index_Demand_OB - 1])
    if bar_index > bar_index_Demand_OB + 1:
        DmaxOpen = math.max(open[bar_index - bar_index_Demand_OB - 2], open[bar_index - bar_index_Demand_OB + 1], open[bar_index - bar_index_Demand_OB], open[bar_index - bar_index_Demand_OB - 1])
        DmaxHigh = math.max(high[bar_index - bar_index_Demand_OB - 2], high[bar_index - bar_index_Demand_OB + 1], high[bar_index - bar_index_Demand_OB], high[bar_index - bar_index_Demand_OB - 1])
        DmaxLow = math.max(low[bar_index - bar_index_Demand_OB - 2], low[bar_index - bar_index_Demand_OB + 1], low[bar_index - bar_index_Demand_OB], low[bar_index - bar_index_Demand_OB - 1])
        DmaxClose = math.max(close[bar_index - bar_index_Demand_OB - 2], close[bar_index - bar_index_Demand_OB + 1], close[bar_index - bar_index_Demand_OB], close[bar_index - bar_index_Demand_OB - 1])
    elif bar_index >= bar_index_Demand_OB:
        DmaxOpen = math.max(open[bar_index - bar_index_Demand_OB + 1], open[bar_index - bar_index_Demand_OB], open[bar_index - bar_index_Demand_OB - 1])
        DmaxHigh = math.max(high[bar_index - bar_index_Demand_OB + 1], high[bar_index - bar_index_Demand_OB], high[bar_index - bar_index_Demand_OB - 1])
        DmaxLow = math.max(low[bar_index - bar_index_Demand_OB + 1], low[bar_index - bar_index_Demand_OB], low[bar_index - bar_index_Demand_OB - 1])
        DmaxClose = math.max(close[bar_index - bar_index_Demand_OB + 1], close[bar_index - bar_index_Demand_OB], close[bar_index - bar_index_Demand_OB - 1])
    DDA: Persistent[float] = 0.0
    DPA: Persistent[float] = 0.0
    if DCRO <= ATR * 0.5:
        DPA = high[bar_index - bar_index_Demand_OB]
        DDA = DminLow
    elif DCRO > ATR * 0.5 and DCRO <= ATR:
        if Candle_Body > 0 or Candle_Body == 0:
            DPA = close[bar_index - bar_index_Demand_OB]
            DDA = DminLow
        elif Candle_Body < 0:
            DPA = open[bar_index - bar_index_Demand_OB]
            DDA = DminLow
    elif DCRO > ATR:
        if low[bar_index - bar_index_Demand_OB + 1] < high[bar_index - bar_index_Demand_OB]:
            if low[bar_index - bar_index_Demand_OB + 1] > low[bar_index - bar_index_Demand_OB]:
                DPA = low[bar_index - bar_index_Demand_OB + 1]
                DDA = low[bar_index - bar_index_Demand_OB]
            elif low[bar_index - bar_index_Demand_OB + 1] <= low[bar_index - bar_index_Demand_OB]:
                if Candle_Body[bar_index - bar_index_Demand_OB + 1] > 0 or Candle_Body[bar_index - bar_index_Demand_OB + 1] == 0:
                    if DCRa1 > ATR:
                        DPA = DmaxOpen
                        DDA = DminLow
                    elif DCRa1 < ATR:
                        DPA = DmaxClose
                        DDA = DminLow
                elif Candle_Body[bar_index - bar_index_Demand_OB + 1] < 0:
                    if DCRa1 > ATR:
                        DPA = DmaxOpen
                        DDA = DminLow
                    elif DCRa1 < ATR:
                        DPA = DmaxOpen
                        DDA = DminLow
        elif not low[bar_index - bar_index_Demand_OB + 1] < high[bar_index - bar_index_Demand_OB]:
            if DminLow - DminOpen > DminLow - DminClose and DminLow - DminOpen <= ATR and (DminLow - DminOpen >= ATR * 0.5):
                DPA = DminOpen
                DDA = DminLow
            elif DminLow - DminOpen < DminLow - DminClose and DminLow - DminClose <= ATR and (DminLow - DminClose >= ATR * 0.5):
                DPA = DminClose
                DDA = DminLow
    else:
        if Candle_Body > 0:
            DPA = DmaxHigh
            DDA = DminLow
        elif Candle_Body < 0:
            DPA = DmaxHigh
            DDA = DmaxLow
    SCRa1: Persistent[float] = 0.0
    SCRO: Persistent[float] = 0.0
    SCRb1: Persistent[float] = 0.0
    SCRa1 = high[bar_index - bar_index_Supply_OB + 1] - low[bar_index - bar_index_Supply_OB + 1]
    SCRO = high[bar_index - bar_index_Supply_OB] - low[bar_index - bar_index_Supply_OB]
    SCRb1 = high[bar_index - bar_index_Supply_OB - 1] - low[bar_index - bar_index_Supply_OB - 1]
    SminOpen: Persistent[float] = 0.0
    SminHigh: Persistent[float] = 0.0
    SminLow: Persistent[float] = 0.0
    SminClose: Persistent[float] = 0.0
    SmaxOpen: Persistent[float] = 0.0
    SmaxHigh: Persistent[float] = 0.0
    SmaxLow: Persistent[float] = 0.0
    SmaxClose: Persistent[float] = 0.0
    if bar_index > bar_index_Supply_OB + 1:
        SminOpen = math.min(open[bar_index - bar_index_Supply_OB - 2], open[bar_index - bar_index_Supply_OB + 1], open[bar_index - bar_index_Supply_OB], open[bar_index - bar_index_Supply_OB - 1])
        SminHigh = math.min(high[bar_index - bar_index_Supply_OB - 2], high[bar_index - bar_index_Supply_OB + 1], high[bar_index - bar_index_Supply_OB], high[bar_index - bar_index_Supply_OB - 1])
        SminLow = math.min(low[bar_index - bar_index_Supply_OB - 2], low[bar_index - bar_index_Supply_OB + 1], low[bar_index - bar_index_Supply_OB], low[bar_index - bar_index_Supply_OB - 1])
        SminClose = math.min(close[bar_index - bar_index_Supply_OB - 2], close[bar_index - bar_index_Supply_OB + 1], close[bar_index - bar_index_Supply_OB], close[bar_index - bar_index_Supply_OB - 1])
    elif bar_index >= bar_index_Supply_OB:
        SminOpen = math.min(open[bar_index - bar_index_Supply_OB + 1], open[bar_index - bar_index_Supply_OB], open[bar_index - bar_index_Supply_OB - 1])
        SminHigh = math.min(high[bar_index - bar_index_Supply_OB + 1], high[bar_index - bar_index_Supply_OB], high[bar_index - bar_index_Supply_OB - 1])
        SminLow = math.min(low[bar_index - bar_index_Supply_OB + 1], low[bar_index - bar_index_Supply_OB], low[bar_index - bar_index_Supply_OB - 1])
        SminClose = math.min(close[bar_index - bar_index_Supply_OB + 1], close[bar_index - bar_index_Supply_OB], close[bar_index - bar_index_Supply_OB - 1])
    if bar_index > bar_index_Supply_OB + 1:
        SmaxOpen = math.max(open[bar_index - bar_index_Supply_OB - 2], open[bar_index - bar_index_Supply_OB + 1], open[bar_index - bar_index_Supply_OB], open[bar_index - bar_index_Supply_OB - 1])
        SmaxHigh = math.max(high[bar_index - bar_index_Supply_OB - 2], high[bar_index - bar_index_Supply_OB + 1], high[bar_index - bar_index_Supply_OB], high[bar_index - bar_index_Supply_OB - 1])
        SmaxLow = math.max(low[bar_index - bar_index_Supply_OB - 2], low[bar_index - bar_index_Supply_OB + 1], low[bar_index - bar_index_Supply_OB], low[bar_index - bar_index_Supply_OB - 1])
        SmaxClose = math.max(close[bar_index - bar_index_Supply_OB - 2], close[bar_index - bar_index_Supply_OB + 1], close[bar_index - bar_index_Supply_OB], close[bar_index - bar_index_Supply_OB - 1])
    elif bar_index >= bar_index_Supply_OB:
        SmaxOpen = math.max(open[bar_index - bar_index_Supply_OB + 1], open[bar_index - bar_index_Supply_OB], open[bar_index - bar_index_Supply_OB - 1])
        SmaxHigh = math.max(high[bar_index - bar_index_Supply_OB + 1], high[bar_index - bar_index_Supply_OB], high[bar_index - bar_index_Supply_OB - 1])
        SmaxLow = math.max(low[bar_index - bar_index_Supply_OB + 1], low[bar_index - bar_index_Supply_OB], low[bar_index - bar_index_Supply_OB - 1])
        SmaxClose = math.max(close[bar_index - bar_index_Supply_OB + 1], close[bar_index - bar_index_Supply_OB], close[bar_index - bar_index_Supply_OB - 1])
    SDA: Persistent[float] = 0.0
    SPA: Persistent[float] = 0.0
    if SCRO <= ATR * 0.5:
        SPA = low[bar_index - bar_index_Supply_OB]
        SDA = SmaxHigh
    elif SCRO > ATR * 0.5 and SCRO <= ATR:
        if Candle_Body > 0 or Candle_Body == 0:
            SPA = close[bar_index - bar_index_Supply_OB]
            SDA = SmaxHigh
        elif Candle_Body < 0:
            SPA = open[bar_index - bar_index_Supply_OB]
            SDA = SmaxHigh
    elif SCRO > ATR:
        if high[bar_index - bar_index_Supply_OB - 1] > low[bar_index - bar_index_Supply_OB]:
            if high[bar_index - bar_index_Supply_OB - 1] > high[bar_index - bar_index_Supply_OB]:
                SPA = high[bar_index - bar_index_Supply_OB - 1]
                SDA = high[bar_index - bar_index_Supply_OB]
            elif high[bar_index - bar_index_Supply_OB - 1] <= high[bar_index - bar_index_Supply_OB]:
                if Candle_Body[bar_index - bar_index_Supply_OB - 1] > 0 or Candle_Body[bar_index - bar_index_Supply_OB - 1] == 0:
                    if SCRa1 > ATR:
                        SPA = SminClose
                        SDA = SmaxHigh
                    elif SCRa1 < ATR:
                        SPA = SminOpen
                        SDA = SmaxHigh
                elif Candle_Body[bar_index - bar_index_Supply_OB - 1] < 0:
                    if SCRa1 > ATR:
                        SPA = SminOpen
                        SDA = SmaxHigh
                    elif SCRa1 < ATR:
                        SPA = SmaxHigh
                        SDA = high[bar_index - bar_index_Supply_OB - 1]
        elif not high[bar_index - bar_index_Supply_OB + 1] > low[bar_index - bar_index_Supply_OB]:
            if SmaxHigh - SminOpen > SmaxHigh - SminClose and SmaxHigh - SminOpen <= ATR and (SmaxHigh - SminOpen >= ATR * 0.5):
                SPA = SminOpen
                SDA = SmaxHigh
            elif SmaxHigh - DminOpen < SmaxHigh - DminClose and SmaxHigh - DminClose <= ATR and (SmaxHigh - DminClose >= ATR * 0.5):
                SPA = SminClose
                SDA = SmaxHigh
    else:
        if Candle_Body > 0:
            SPA = SminLow
            SDA = SmaxHigh
        elif Candle_Body < 0:
            SPA = SminLow
            SDA = SmaxHigh
    DProximal: Persistent[float] = 0.0
    DDistal: Persistent[float] = 0.0
    SProximal: Persistent[float] = 0.0
    SDistal: Persistent[float] = 0.0
    if RefineType == 'Defensive':
        if DPA - DDA >= ATR * 3:
            DDistal = DDA
            DProximal = DPA - (DPA - DDA) * 0.7
        elif DPA - DDA < ATR * 3 and DPA - DDA >= ATR * 2:
            DDistal = DDA
            DProximal = DPA - (DPA - DDA) * 0.6
        elif DPA - DDA < ATR * 2 and DPA - DDA >= ATR * 1.6:
            DDistal = DDA
            DProximal = DPA - (DPA - DDA) * 0.5
        elif DPA - DDA < ATR * 1.6 and DPA - DDA > ATR:
            DDistal = DDA
            DProximal = DPA - (DPA - DDA) * 0.25
        elif DPA - DDA <= ATR:
            DDistal = DDA
            DProximal = DPA
    elif RefineType == 'Aggressive':
        DDistal = DDA
        DProximal = DPA
    if RefineType == 'Defensive':
        if SDA - SPA >= ATR * 3:
            SDistal = SDA
            SProximal = SPA + (SDA - SPA) * 0.7
        elif SDA - SPA < ATR * 3 and SDA - SPA >= ATR * 2:
            SDistal = SDA
            SProximal = SPA + (SDA - SPA) * 0.6
        elif SDA - SPA < ATR * 2 and SDA - SPA >= ATR * 1.6:
            SDistal = SDA
            SProximal = SPA + (SDA - SPA) * 0.5
        elif SDA - SPA < ATR * 1.6 and SDA - SPA > ATR:
            SDistal = SDA
            SProximal = SPA + (SDA - SPA) * 0.25
        elif SDA - SPA <= ATR:
            SDistal = SDA
            SProximal = SPA
    elif RefineType == 'Aggressive':
        SDistal = SDA
        SProximal = SPA
    if Demand_OB_Condition:
        DemandCheck = bar_index_Demand_OB
        YDp12 = DProximal if OBRefine == 'On' else high[bar_index - bar_index_Demand_OB]
        XDp1 = bar_index_Demand_OB
        XDp2 = bar_index_Demand_OB + 1
        YDd12 = DDistal if OBRefine == 'On' else low[bar_index - bar_index_Demand_OB]
        XDd1 = bar_index_Demand_OB
        XDd2 = bar_index_Demand_OB + 1
    if Supply_OB_Condition:
        SupplyCheck = bar_index_Supply_OB
        YSp12 = SProximal if OBRefine == 'On' else low[bar_index - bar_index_Supply_OB]
        XSp1 = bar_index_Supply_OB
        XSp2 = bar_index_Supply_OB + 1
        YSd12 = SDistal if OBRefine == 'On' else high[bar_index - bar_index_Supply_OB]
        XSd1 = bar_index_Supply_OB
        XSd2 = bar_index_Supply_OB + 1
    def LinerFunctionDem(Xd1, Yd1, Xd2, Yd2, Xp1, Yp1, Xp2, Yp2, Xn):
        __hist_YDp12__: Series[float] = YDp12[0]
        xd1 = Xd1
        xd2 = Xd2
        yd1 = Yd1
        yd2 = Yd2
        xdn = Xn
        xdnz = Xn
        md = (yd2 - yd1) / (xd2 - xd1)
        bd = yd1 - md * xd1
        Ydnz = md * xdnz + bd
        Ydn = md * xdn + bd
        xp1 = Xp1
        xp2 = Xp2
        yp1 = Yp1
        yp2 = Yp2
        xpn = Xn
        xpnz = Xn
        mp = (yp2 - yp1) / (xp2 - xp1)
        bp = yp1 - mp * xp1
        Ypnz = mp * xpnz + bp
        Ypn = mp * xpn + bp
        DemCheck: Persistent[bool] = True
        DemCounter: Persistent[int] = 1
        Distal: Persistent[Line] = na(Line)
        Proximal: Persistent[Line] = na(Line)
        DLine50per: Persistent[Line] = na(Line)
        fillline: Persistent[LineFill] = na(LineFill)
        if Demand_OB_Condition:
            Distal = line.new(xd1, yd1, xd2, yd1, color=color.rgb(0, 0, 0, 45), style=line.style_dashed, width=1)
            Proximal = line.new(xp1, yp1, xd2, yp1, color=color.rgb(0, 0, 0, 45), style=line.style_dashed, width=1)
            DLine50per = line.new(xp1, (yp1 + yd1) / 2, xd2, (yp1 + yd1) / 2, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            fillline = linefill.new(Distal, Proximal, color=DemBxColor)
        if (low > YDp12 or xd1 == __hist_YDp12__[1]) and DemCheck == True:
            DemCounter = DemCounter + 1
            line.set_x2(Distal, bar_index + 1)
            line.set_x2(Proximal, bar_index + 1)
            line.set_x2(DLine50per, bar_index + 1)
        if low < YDd12 and low[1] > YDd12:
            DemCounter = DemCounter
            DemCheck = False
        if Demand_OB_Condition:
            DemCounter = 1
            DemCheck = True
        return (xd1, xd2, yd1, yd2, xdnz, md, bd, Ydnz, xdn, Ydn, xp1, xp2, yp1, yp2, xpnz, mp, bp, Ypnz, xpn, Ypn)

    def LinerFunctionSup(Xd1, Yd1, Xd2, Yd2, Xp1, Yp1, Xp2, Yp2, Xn):
        __hist_YSp12__: Series[float] = YSp12[0]
        xd1 = Xd1
        xd2 = Xd2
        yd1 = Yd1
        yd2 = Yd2
        xdn = Xn
        xdnz = Xn
        md = (yd2 - yd1) / (xd2 - xd1)
        bd = yd1 - md * xd1
        Ydnz = md * xdnz + bd
        Ydn = md * xdn + bd
        xp1 = Xp1
        xp2 = Xp2
        yp1 = Yp1
        yp2 = Yp2
        xpn = Xn
        xpnz = Xn
        mp = (yp2 - yp1) / (xp2 - xp1)
        bp = yp1 - mp * xp1
        Ypnz = mp * xpnz + bp
        Ypn = mp * xpn + bp
        SupCheck: Persistent[bool] = True
        SupCounter: Persistent[int] = 1
        Distal: Persistent[Line] = na(Line)
        Proximal: Persistent[Line] = na(Line)
        SLine50per: Persistent[Line] = na(Line)
        fillline: Persistent[LineFill] = na(LineFill)
        if Supply_OB_Condition:
            Distal = line.new(xd1, yd1, xdnz, yd1, color=color.rgb(0, 0, 0, 45), style=line.style_dashed, width=1)
            Proximal = line.new(xp1, yp1, xpnz, yp1, color=color.rgb(0, 0, 0, 45), style=line.style_dashed, width=1)
            SLine50per = line.new(xp1, (yp1 + yd1) / 2, xpnz, (yp1 + yd1) / 2, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            fillline = linefill.new(Distal, Proximal, color=SupBxColor)
        if (high < YSp12 or xd1 == __hist_YSp12__[1]) and SupCheck == True:
            SupCounter = SupCounter + 1
            line.set_x2(Distal, bar_index + 1)
            line.set_x2(Proximal, bar_index + 1)
            line.set_x2(SLine50per, bar_index + 1)
        if high > YSd12 and high[1] < YSd12:
            SupCounter = SupCounter
            SupCheck = False
        if Supply_OB_Condition:
            SupCounter = 1
            SupCheck = True
        return (xd1, xd2, yd1, yd2, xdnz, md, bd, Ydnz, xdn, Ydn, xp1, xp2, yp1, yp2, xpnz, mp, bp, Ypnz, xpn, Ypn)

    DPy1: Series
    DDx1, DDx2, DDy1, DDy2, DDxz, DDm, DDb, DDyz, DDxn, DDyn, DPx1, DPx2, DPy1, DPy2, DPxz, DPm, DPb, DPyz, DPxn, DPyn = LinerFunctionDem(XDd1, YDd12, XDd2, YDd12, XDp1, YDp12, XDp2, YDp12, bar_index)
    SPy1: Series
    SDx1, SDx2, SDy1, SDy2, SDxz, SDm, SDb, SDyz, SDxn, SDyn, SPx1, SPx2, SPy1, SPy2, SPxz, SPm, SPb, SPyz, SPxn, SPyn = LinerFunctionSup(XSd1, YSd12, XSd2, YSd12, XSp1, YSp12, XSp2, YSp12, bar_index)
    LongSignal: Persistent[bool] = False
    ShortSignal: Persistent[bool] = False
    LockAlertBull: Persistent[int] = 0
    if low <= YDp12 and low[1] > YDp12 and (LockAlertBull == 0):
        LockAlertBull = 1
        LongSignal = True
    else:
        LongSignal = False
    if DPy1 != DPy1[1]:
        LockAlertBull = 0
    LockAlertBear: Persistent[int] = 0
    if high >= YSp12 and high[1] < YSp12 and (LockAlertBear == 0):
        LockAlertBear = 1
        ShortSignal = True
    else:
        ShortSignal = False
    if SPy1 != SPy1[1]:
        LockAlertBear = 0
    Alert.AlertSender(LongSignal, Alert__global__, AlertName, 'Bullish', 'Order Block Signal', 'Full', Frequncy, UTC, MoreInfo, MessageBull, open, high, low, close, 0, 0, 0, YDd12, YDp12)
    Alert.AlertSender(ShortSignal, Alert__global__, AlertName, 'Bearish', 'Order Block Signal', 'Full', Frequncy, UTC, MoreInfo, MessageBear, open, high, low, close, 0, 0, 0, YSd12, YSp12)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
