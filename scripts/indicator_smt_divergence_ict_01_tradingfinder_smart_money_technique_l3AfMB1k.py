"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, close, color, high, input, label, line, low, na, open,
    plotcandle, request, script, size, ta, timeframe
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('SMT Divergence ICT 01 [TradingFinder] Smart Money Technique', shorttitle='TFlab SMT', overlay=False, max_bars_back=5000, max_labels_count=500, max_lines_count=500)
def main(
    Sym=input.symbol('XAUUSD', 'Second Symbol'),
    n=input.int(2, title='Divergence Fractal Periods', minval=1, group='Logic Setting'),
    Bull_Line=input.bool(True, 'Show SMT Divergence Line from the Bottom.'),
    Bull_Label=input.bool(True, 'Show SMT Divergence Label from the Bottom.'),
    Bear_Line=input.bool(True, 'Show SMT Divergence Line from the Top.'),
    Bear_Label=input.bool(True, 'Show SMT Divergence Label from the Top.')
):
    ATR = ta.atr(55)
    High: Series
    Low: Series
    Open, High, Low, Close = request.security(Sym, timeframe.period, (open, high, low, close))
    UpPivot = cast_bool(ta.pivothigh(n, n))
    DownPivot = cast_bool(ta.pivotlow(n, n))
    High_Last_Price = ta.valuewhen(cast_bool(UpPivot), high[n], 0)
    High_Per_Price = ta.valuewhen(cast_bool(UpPivot), high[n], 1)
    High_Last_Hist = ta.valuewhen(cast_bool(UpPivot), High[n], 0)
    High_Per_Hist = ta.valuewhen(cast_bool(UpPivot), High[n], 1)
    High_Last_Bar = ta.valuewhen(cast_bool(UpPivot), bar_index[n], 0)
    High_Per_Bar = ta.valuewhen(cast_bool(UpPivot), bar_index[n], 1)
    Time_Condition_Bear = High_Last_Bar + 30 > bar_index
    __block_result__ = na
    if High_Last_Hist > 0 and High_Per_Hist > 0 and Time_Condition_Bear and (High_Last_Bar - High_Per_Bar < 30):
        __block_result__ = High_Last_Price > High_Per_Price and High_Last_Hist < High_Per_Hist or (High_Last_Price < High_Per_Price and High_Last_Hist > High_Per_Hist)
    else:
        __block_result__ = False
    Last_Bearish_Divergece = __block_result__
    Low_Last_Price = ta.valuewhen(cast_bool(DownPivot), low[n], 0)
    Low_Per_Price = ta.valuewhen(cast_bool(DownPivot), low[n], 1)
    Low_Last_Hist = ta.valuewhen(cast_bool(DownPivot), Low[n], 0)
    Low_Per_Hist = ta.valuewhen(cast_bool(DownPivot), Low[n], 1)
    Low_Last_Bar = ta.valuewhen(cast_bool(DownPivot), bar_index[n], 0)
    Low_Per_Bar = ta.valuewhen(cast_bool(DownPivot), bar_index[n], 1)
    Time_Condition_Bull = Low_Last_Bar + 30 > bar_index
    __block_result_1__ = na
    if Low_Last_Hist > 0 and Low_Per_Hist > 0 and Time_Condition_Bull and (Low_Last_Bar - Low_Per_Bar < 30):
        __block_result_1__ = Low_Last_Price < Low_Per_Price and Low_Last_Hist > Low_Per_Hist or (Low_Last_Price > Low_Per_Price and Low_Last_Hist < Low_Per_Hist)
    else:
        __block_result_1__ = False
    Last_Bullish_Divergece = __block_result_1__
    CBullDive: Persistent[int] = 0
    if cast_bool(ta.change(Low_Last_Price)) and Last_Bullish_Divergece == True:
        CBullDive = CBullDive + 1
    elif Last_Bullish_Divergece == False:
        CBullDive = 0
    def Drawing(Bull_Line, Bear_Line, Bull_Label, Bear_Label):
        BeLine: Persistent[Line] = na(Line)
        BuLine: Persistent[Line] = na(Line)
        BeLabel: Persistent[Label] = na(Label)
        BuLabel: Persistent[Label] = na(Label)
        BeLine_OnChart: Persistent[Line] = na(Line)
        BuLine_OnChart: Persistent[Line] = na(Line)
        BeLabel_OnChart: Persistent[Label] = na(Label)
        BuLabel_OnChart: Persistent[Label] = na(Label)
        if Last_Bullish_Divergece:
            if Bull_Line:
                BuLine = line.new(Low_Per_Bar, Low_Per_Hist, Low_Last_Bar, Low_Last_Hist, color=color.black, width=1, style=line.style_dashed)
                BuLine_OnChart = line.new(Low_Per_Bar, low[bar_index - Low_Per_Bar], Low_Last_Bar, low[bar_index - Low_Last_Bar], color=color.black, width=1, force_overlay=True, style=line.style_dashed)
            if Bull_Label:
                BuLabel = label.new(Low_Last_Bar, Low_Last_Hist, '+SMT', color=color.green, textcolor=color.white, size=size.tiny, style=label.style_label_up)
                BuLabel_OnChart = label.new(Low_Last_Bar, low[bar_index - Low_Last_Bar], '+SMT', color=color.green, textcolor=color.white, size=size.tiny, style=label.style_label_up, force_overlay=True)
        __block_result_2__ = na
        if Last_Bearish_Divergece:
            if Bear_Line:
                BeLine = line.new(High_Per_Bar, High_Per_Hist, High_Last_Bar, High_Last_Hist, color=color.black, width=1, style=line.style_dashed)
                BeLine_OnChart = line.new(High_Per_Bar, high[bar_index - High_Per_Bar], High_Last_Bar, high[bar_index - High_Last_Bar], color=color.black, width=1, force_overlay=True, style=line.style_dashed)
            __block_result_3__ = na
            if Bear_Label:
                BeLabel = label.new(High_Last_Bar, High_Last_Hist, '-SMT', color=color.red, textcolor=color.white, size=size.tiny, style=label.style_label_down)
                BeLabel_OnChart = label.new(High_Last_Bar, high[bar_index - High_Last_Bar], '-SMT', color=color.red, textcolor=color.white, size=size.tiny, style=label.style_label_down, force_overlay=True)
                __block_result_3__ = BeLabel_OnChart
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    plotcandle(Open, High, Low, Close, color=color.new('#089981') if Close >= Open else color.new('#F23645'), wickcolor=color.new('#089981') if Close >= Open else color.new('#F23645'), bordercolor=color.new('#089981') if Close >= Open else color.new('#F23645'))
    Drawing(Bull_Line, Bear_Line, Bull_Label, Bear_Label)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
