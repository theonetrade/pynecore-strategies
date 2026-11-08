"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, close, color, extend, fill, high, input, line,
    location, low, na, plot, plotchar, script, size, time, xloc
)
from pynecore.types import Color, Series


@script.indicator('Grid Bot Simulator', shorttitle='GridBotDir', overlay=True)
def main(
    UpperLimit=input.price(50000.0, 'Upper Limit', confirm=True),
    LowerLimit=input.price(43000.0, 'Lower Limit', confirm=True),
    __input_2__=input(10, 'Number of Grids(10)'),
    Dir=input.string('neutral', 'Market Direction', options=('up', 'neutral', 'down')),
    SS=input.string('small', 'Signal Size', options=('small', 'large')),
    ShowGrids=input(True, 'Show Grids'),
    HighLight=input(True, 'Highlight Trade Zones'),
    ShowCurrent=input(False, 'Show Only Current Grids'),
    Extremes=input(True, 'High/Low for signals')
):
    No_Grids = __input_2__ + 1
    LastSignal: Series[int] = 0
    LastSignal_Index: Series[int] = 0
    LastSignal_Time: Series = time
    SignalLine: Series[float] = 0.0
    CurrentGrid: float = 0.0
    Buy: bool = False
    Sell: bool = False
    Direction = 1 if Dir == 'up' else -1 if Dir == 'down' else 0
    RedGrid = color.new(color.red, 50)
    GreenGrid = color.new(color.green, 40)
    Crimson: Color = color.new('#DC143C')
    LimeGreen: Color = color.new('#32CD32')
    GridRange = UpperLimit - LowerLimit
    GridInterval = GridRange / (No_Grids - 1)
    a_grid: list[float] = array.new_float(No_Grids)
    for x in pine_range(0, No_Grids - 1, 1):
        array.set(a_grid, x, LowerLimit + GridInterval * x)
    def Get_Array_Values(ArrayName, index):
        value = array.get(ArrayName, index)
        return value

    def Get_BuyLine_Index():
        Index: int = 0
        BuyValue: float = 0.0
        __block_result__ = na
        for x in pine_range(0, No_Grids - 1, 1):
            BuyValue = LowerLimit + GridInterval * x
            __block_result_1__ = na
            if Extremes:
                Index = x if high[1] > BuyValue and low <= BuyValue else Index
                __block_result_1__ = Index
            else:
                Index = x if close[1] > BuyValue and close <= BuyValue else Index
                __block_result_1__ = Index
            __block_result__ = __block_result_1__
        return __block_result__

    def Get_SellLine_Index():
        Index: int = 0
        SellValue: float = 0.0
        __block_result_2__ = na
        for x in pine_range(0, No_Grids - 1, 1):
            SellValue = LowerLimit + GridInterval * x
            __block_result_3__ = na
            if Extremes:
                Index = x if low[1] < SellValue and high >= SellValue else Index
                __block_result_3__ = Index
            else:
                Index = x if close[1] < SellValue and close >= SellValue else Index
                __block_result_3__ = Index
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    BuyLine_Index = Get_BuyLine_Index()
    SellLine_Index = Get_SellLine_Index()
    Buy = True if BuyLine_Index > 0 else Buy
    Sell = True if SellLine_Index > 0 else Sell
    if Extremes:
        Buy = False if low >= SignalLine[1] - GridInterval else Buy
        Sell = False if high <= SignalLine[1] + GridInterval else Sell
    else:
        Buy = False if close >= SignalLine[1] - GridInterval else Buy
        Sell = False if close <= SignalLine[1] + GridInterval else Sell
    Buy = False if close >= UpperLimit else Buy
    Buy = False if close < LowerLimit else Buy
    Sell = False if close <= LowerLimit else Sell
    Sell = False if close > UpperLimit else Sell
    Buy = False if Direction == -1 and low >= SignalLine[1] - GridInterval * 2 else Buy
    Sell = False if Direction == 1 and high <= SignalLine[1] + GridInterval * 2 else Sell
    LastSignal = 1 if Buy else -1 if Sell else LastSignal[1]
    LastSignal_Index = BuyLine_Index if Buy else SellLine_Index if Sell else LastSignal_Index[1]
    LastSignal_Time = time if Buy or Sell else LastSignal_Time[1]
    SignalLine = LowerLimit + GridInterval * LastSignal_Index
    for i in pine_range(1, No_Grids - 1, 1):
        Array_Value = Get_Array_Values(a_grid, i)
        ClosestGrid = Array_Value - close
        linecolor: Color = RedGrid if ClosestGrid > 0 else GreenGrid if ClosestGrid < 0 else na
        linecolor = na if i == LastSignal_Index else linecolor
        if ShowGrids:
            if ShowCurrent:
                LineAbove__0000002e__ = line.new(x1=LastSignal_Time, y1=SignalLine + GridInterval, x2=time + 1000000, y2=SignalLine + GridInterval, color=color.red, width=1, extend=extend.left, xloc=xloc.bar_time)
                line.new(x1=LastSignal_Time, y1=SignalLine - GridInterval, x2=time + 1000000, y2=SignalLine - GridInterval, color=color.green, width=1, extend=extend.left, xloc=xloc.bar_time)
            else:
                colCurrent: Color = color.new(color.green, 95) if LastSignal == 1 else color.new(color.red, 95)
                GridLines = line.new(x1=time, y1=Array_Value, x2=time[1], y2=Array_Value, color=linecolor, width=1, extend=extend.right, xloc=xloc.bar_time)
                line.new(x1=LastSignal_Time, y1=SignalLine, x2=LastSignal_Time - 100000, y2=SignalLine, color=colCurrent, width=1, extend=extend.right, xloc=xloc.bar_time)
    UL = ShowGrids and (not ShowCurrent)
    plot(UpperLimit if UL else na, color=color.green if close >= UpperLimit else color.red, linewidth=3)
    plot(LowerLimit if UL else na, color=color.red if close <= LowerLimit else color.green, linewidth=3)
    LineAbove = SignalLine if SignalLine == UpperLimit else SignalLine + GridInterval
    LineBelow = SignalLine if SignalLine == LowerLimit else SignalLine - GridInterval
    a = plot(LineAbove, color=color.new(color.red, 100), style=plot.style_circles)
    b = plot(LineBelow, color=color.new(color.green, 100), style=plot.style_circles)
    boxColor = color.new(color.green, 90) if LastSignal == -1 else color.new(color.red, 90)
    boxColor = boxColor if HighLight else na
    fill(a, b, color=color.new(boxColor, 90))
    plotchar(Buy and SS == 'small', 'Buy', color=color.new(LimeGreen, 0), size=size.tiny, location=location.belowbar, char='▲')
    plotchar(Sell and SS == 'small', 'Sell', color=color.new(Crimson, 0), size=size.tiny, location=location.abovebar, char='▼')
    plotchar(Buy and SS == 'large', 'Buy', color=color.new(LimeGreen, 0), size=size.small, location=location.belowbar, char='▲')
    plotchar(Sell and SS == 'large', 'Sell', color=color.new(Crimson, 0), size=size.small, location=location.abovebar, char='▼')
    alertcondition(condition=Buy, title='buy', message='buy')
    alertcondition(condition=Sell, title='sell', message='sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)