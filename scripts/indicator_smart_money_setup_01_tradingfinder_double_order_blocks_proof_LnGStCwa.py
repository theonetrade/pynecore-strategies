"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, box, close, color, high, input, location, low, open,
    plotshape, script, shape, size, ta, text, xloc
)
from pynecore.types import Box, Line, Persistent


@script.indicator('Smart Money Setup 01 [TradingFinder] Double Order Blocks Confirmation', 'SMC Setup Order Blocks 01 TFlab', overlay=True, max_bars_back=4000, max_boxes_count=500, max_labels_count=500, max_lines_count=500)
def main(
    PP=input.int(2, 'Pivot Period', minval=2)
):
    ATR = ta.atr(50)
    Open = open
    High = high
    Low = low
    Close = close
    Bar_Index = bar_index
    ArrayType: Persistent[list[str]] = array.new_string()
    ArrayValue: Persistent[list[float]] = array.new_float()
    ArrayIndex: Persistent[list[int]] = array.new_int()
    Line__ren__: Persistent[list[Line]] = array.new_line()
    HighPivot = ta.pivothigh(PP, PP)
    LowPivot = ta.pivotlow(PP, PP)
    HighValue = ta.valuewhen(cast_bool(HighPivot), high[PP], 0)
    LowValue = ta.valuewhen(cast_bool(LowPivot), low[PP], 0)
    HighIndex = ta.valuewhen(cast_bool(HighPivot), bar_index[PP], 0)
    LowIndex = ta.valuewhen(cast_bool(LowPivot), bar_index[PP], 0)
    Correct_HighPivot: float = 0.0
    Correct_LowPivot: float = 0.0
    PASS: int = 0
    if cast_bool(HighPivot) and cast_bool(LowPivot):
        if array.size(ArrayType) == 0:
            PASS = 1
        elif array.size(ArrayType) >= 1:
            if array.get(ArrayType, array.size(ArrayType) - 1) == 'L' or array.get(ArrayType, array.size(ArrayType) - 1) == 'LL':
                if LowPivot < array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                    Correct_LowPivot = LowValue
                else:
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue
            elif array.get(ArrayType, array.size(ArrayType) - 1) == 'H' or array.get(ArrayType, array.size(ArrayType) - 1) == 'HH':
                if HighPivot > array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue
                else:
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                Correct_LowPivot = LowValue
            elif array.get(ArrayType, array.size(ArrayType) - 1) == 'LH':
                if HighPivot < array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                    Correct_LowPivot = LowValue
                elif HighPivot > array.get(ArrayValue, array.size(ArrayType) - 1):
                    if close < array.get(ArrayValue, array.size(ArrayType) - 1):
                        array.remove(ArrayType, array.size(ArrayType) - 1)
                        array.remove(ArrayValue, array.size(ArrayValue) - 1)
                        array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                        array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                        array.push(ArrayValue, HighValue)
                        array.push(ArrayIndex, HighIndex)
                        Correct_HighPivot = HighValue
                    elif close > array.get(ArrayValue, array.size(ArrayType) - 1):
                        array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                        array.push(ArrayValue, LowValue)
                        array.push(ArrayIndex, LowIndex)
                        Correct_LowPivot = LowValue
            elif array.get(ArrayType, array.size(ArrayType) - 1) == 'HL':
                if LowPivot > array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue
                elif LowPivot < array.get(ArrayValue, array.size(ArrayType) - 1):
                    if close > array.get(ArrayValue, array.size(ArrayType) - 1):
                        array.remove(ArrayType, array.size(ArrayType) - 1)
                        array.remove(ArrayValue, array.size(ArrayValue) - 1)
                        array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                        array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                        array.push(ArrayValue, LowValue)
                        array.push(ArrayIndex, LowIndex)
                        Correct_LowPivot = LowValue
                    elif close < array.get(ArrayValue, array.size(ArrayType) - 1):
                        array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                        array.push(ArrayValue, HighValue)
                        array.push(ArrayIndex, HighIndex)
                        Correct_HighPivot = HighValue
    elif cast_bool(HighPivot):
        if array.size(ArrayType) == 0:
            array.insert(ArrayType, 0, 'H')
            array.insert(ArrayValue, 0, HighValue)
            array.insert(ArrayIndex, 0, HighIndex)
            Correct_HighPivot = HighValue
        elif array.size(ArrayType) >= 1:
            if array.get(ArrayType, array.size(ArrayType) - 1) == 'L' or array.get(ArrayType, array.size(ArrayType) - 1) == 'HL' or array.get(ArrayType, array.size(ArrayType) - 1) == 'LL':
                if HighPivot > array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue
                elif HighPivot < array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                    Correct_LowPivot = LowValue
            elif array.get(ArrayType, array.size(ArrayType) - 1) == 'H' or array.get(ArrayType, array.size(ArrayType) - 1) == 'HH' or array.get(ArrayType, array.size(ArrayType) - 1) == 'LH':
                if array.get(ArrayValue, array.size(ArrayValue) - 1) < HighValue:
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue
    elif cast_bool(LowPivot):
        if array.size(ArrayType) == 0:
            array.insert(ArrayType, 0, 'L')
            array.insert(ArrayValue, 0, LowValue)
            array.insert(ArrayIndex, 0, LowIndex)
            Correct_LowPivot = LowValue
        elif array.size(ArrayType) >= 1:
            if array.get(ArrayType, array.size(ArrayType) - 1) == 'H' or array.get(ArrayType, array.size(ArrayType) - 1) == 'HH' or array.get(ArrayType, array.size(ArrayType) - 1) == 'LH':
                if LowPivot < array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                    Correct_LowPivot = LowValue
                elif LowPivot > array.get(ArrayValue, array.size(ArrayType) - 1):
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HH' if array.get(ArrayValue, array.size(ArrayType) - 2) < HighValue else 'LH') if array.size(ArrayType) > 2 else 'H')
                    array.push(ArrayValue, HighValue)
                    array.push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue
            elif array.get(ArrayType, array.size(ArrayType) - 1) == 'L' or array.get(ArrayType, array.size(ArrayType) - 1) == 'HL' or array.get(ArrayType, array.size(ArrayType) - 1) == 'LL':
                if array.get(ArrayValue, array.size(ArrayValue) - 1) > LowValue:
                    array.remove(ArrayType, array.size(ArrayType) - 1)
                    array.remove(ArrayValue, array.size(ArrayValue) - 1)
                    array.remove(ArrayIndex, array.size(ArrayIndex) - 1)
                    array.push(ArrayType, ('HL' if array.get(ArrayValue, array.size(ArrayType) - 2) < LowValue else 'LL') if array.size(ArrayType) > 2 else 'L')
                    array.push(ArrayValue, LowValue)
                    array.push(ArrayIndex, LowIndex)
                    Correct_LowPivot = LowValue
    TypePoint0: Persistent[str] = ''
    TypePoint1: Persistent[str] = ''
    TypePoint2: Persistent[str] = ''
    TypePoint3: Persistent[str] = ''
    TypePoint4: Persistent[str] = ''
    TypePoint5: Persistent[str] = ''
    TypePoint6: Persistent[str] = ''
    TypePoint7: Persistent[str] = ''
    PricePoint0: Persistent[float] = 0.0
    PricePoint1: Persistent[float] = 0.0
    PricePoint2: Persistent[float] = 0.0
    PricePoint3: Persistent[float] = 0.0
    PricePoint4: Persistent[float] = 0.0
    PricePoint5: Persistent[float] = 0.0
    PricePoint6: Persistent[float] = 0.0
    PricePoint7: Persistent[float] = 0.0
    IndexPoint0: Persistent[int] = 0
    IndexPoint1: Persistent[int] = 0
    IndexPoint2: Persistent[int] = 0
    IndexPoint3: Persistent[int] = 0
    IndexPoint4: Persistent[int] = 0
    IndexPoint5: Persistent[int] = 0
    IndexPoint6: Persistent[int] = 0
    IndexPoint7: Persistent[int] = 0
    if array.size(ArrayType) > 8:
        TypePoint0 = array.get(ArrayType, array.size(ArrayType) - 1)
        TypePoint1 = array.get(ArrayType, array.size(ArrayType) - 2)
        TypePoint2 = array.get(ArrayType, array.size(ArrayType) - 3)
        TypePoint3 = array.get(ArrayType, array.size(ArrayType) - 4)
        TypePoint4 = array.get(ArrayType, array.size(ArrayType) - 5)
        TypePoint5 = array.get(ArrayType, array.size(ArrayType) - 6)
        TypePoint6 = array.get(ArrayType, array.size(ArrayType) - 7)
        TypePoint7 = array.get(ArrayType, array.size(ArrayType) - 8)
        PricePoint0 = array.get(ArrayValue, array.size(ArrayType) - 1)
        PricePoint1 = array.get(ArrayValue, array.size(ArrayType) - 2)
        PricePoint2 = array.get(ArrayValue, array.size(ArrayType) - 3)
        PricePoint3 = array.get(ArrayValue, array.size(ArrayType) - 4)
        PricePoint4 = array.get(ArrayValue, array.size(ArrayType) - 5)
        PricePoint5 = array.get(ArrayValue, array.size(ArrayType) - 6)
        PricePoint6 = array.get(ArrayValue, array.size(ArrayType) - 7)
        PricePoint7 = array.get(ArrayValue, array.size(ArrayType) - 8)
        IndexPoint0 = array.get(ArrayIndex, array.size(ArrayType) - 1)
        IndexPoint1 = array.get(ArrayIndex, array.size(ArrayType) - 2)
        IndexPoint2 = array.get(ArrayIndex, array.size(ArrayType) - 3)
        IndexPoint3 = array.get(ArrayIndex, array.size(ArrayType) - 4)
        IndexPoint4 = array.get(ArrayIndex, array.size(ArrayType) - 5)
        IndexPoint5 = array.get(ArrayIndex, array.size(ArrayType) - 6)
        IndexPoint6 = array.get(ArrayIndex, array.size(ArrayType) - 7)
        IndexPoint7 = array.get(ArrayIndex, array.size(ArrayType) - 8)
    BearSetup04: bool = False
    BullSetup04: bool = False
    BeOpen1: float = 0.0
    BeHigh1: float = 0.0
    BeLow1: float = 0.0
    BeClose1: float = 0.0
    BeOpen5: float = 0.0
    BeHigh5: float = 0.0
    BeLow5: float = 0.0
    BeClose5: float = 0.0
    BuOpen1: float = 0.0
    BuHigh1: float = 0.0
    BuLow1: float = 0.0
    BuClose1: float = 0.0
    BuOpen5: float = 0.0
    BuHigh5: float = 0.0
    BuLow5: float = 0.0
    BuClose5: float = 0.0
    if TypePoint0 == 'LL' and TypePoint1 == 'HH' and (TypePoint2 == 'HL') and (TypePoint3 == 'LH') and (TypePoint4 == 'LL') and (TypePoint5 == 'LH') and (TypePoint6 == 'LL') and (PricePoint0 > PricePoint4) and (PricePoint5 > PricePoint1) and (IndexPoint0 == bar_index - PP):
        BearSetup04 = True
        BeOpen1 = open[bar_index - IndexPoint1]
        BeHigh1 = high[bar_index - IndexPoint1]
        BeLow1 = low[bar_index - IndexPoint1]
        BeClose1 = close[bar_index - IndexPoint1]
        BeOpen5 = open[bar_index - IndexPoint5]
        BeHigh5 = high[bar_index - IndexPoint5]
        BeLow5 = low[bar_index - IndexPoint5]
        BeClose5 = close[bar_index - IndexPoint5]
    else:
        BearSetup04 = False
    if TypePoint0 == 'HH' and TypePoint1 == 'LL' and (TypePoint2 == 'LH') and (TypePoint3 == 'HL') and (TypePoint4 == 'HH') and (TypePoint5 == 'HL') and (TypePoint6 == 'HH') and (PricePoint0 < PricePoint4) and (PricePoint5 < PricePoint1) and (IndexPoint0 == bar_index - PP):
        BullSetup04 = True
        BuOpen1 = open[bar_index - IndexPoint1]
        BuHigh1 = high[bar_index - IndexPoint1]
        BuLow1 = low[bar_index - IndexPoint1]
        BuClose1 = close[bar_index - IndexPoint1]
        BuOpen5 = open[bar_index - IndexPoint5]
        BuHigh5 = high[bar_index - IndexPoint5]
        BuLow5 = low[bar_index - IndexPoint5]
        BuClose5 = close[bar_index - IndexPoint5]
    else:
        BullSetup04 = False
    plotshape(BearSetup04 and BeLow5 <= BeHigh1, 'Bear Setup04', style=shape.arrowup, location=location.belowbar, color=color.rgb(179, 2, 2), offset=-PP, text='Bear Setup04', textcolor=color.rgb(179, 2, 22))
    plotshape(BullSetup04 and BuLow1 <= BuHigh5, 'Bull Setup04', style=shape.arrowdown, location=location.abovebar, color=color.rgb(47, 156, 38), offset=-PP, text='Bull Setup04', textcolor=color.rgb(47, 156, 38))
    supply_box_HTF: Persistent[list[Box]] = array.new_box()
    supply_box_LTF: Persistent[list[Box]] = array.new_box()
    Demand_box_HTF: Persistent[list[Box]] = array.new_box()
    Demand_box_LTF: Persistent[list[Box]] = array.new_box()
    if BearSetup04 and BeLow5 <= BeHigh1:
        array.push(supply_box_HTF, box.new(left=IndexPoint5, top=BeHigh5, right=bar_index + bar_index - IndexPoint5, bottom=BeLow5, xloc=xloc.bar_index, bgcolor=color.rgb(197, 200, 202, 57), text='Supply OB', text_size=size.tiny, text_valign=text.align_center))
        array.push(supply_box_LTF, box.new(left=IndexPoint1, top=BeHigh1, right=bar_index + 20, bottom=BeLow1, xloc=xloc.bar_index, bgcolor=color.rgb(252, 231, 48, 57), text='Supply OB LTF', text_size=size.tiny, text_valign=text.align_center))
    if BullSetup04 and BuLow1 <= BuHigh5:
        array.push(Demand_box_HTF, box.new(left=IndexPoint5, top=BuHigh5, right=bar_index + bar_index - IndexPoint5, bottom=BuLow5, xloc=xloc.bar_index, bgcolor=color.rgb(197, 200, 202, 57), text='Demand OB', text_size=size.tiny, text_valign=text.align_center))
        array.push(Demand_box_LTF, box.new(left=IndexPoint1, top=BuHigh1, right=bar_index + 20, bottom=BuLow1, xloc=xloc.bar_index, bgcolor=color.rgb(48, 252, 242, 57), text='Demand OB LTF', text_size=size.tiny, text_valign=text.align_center))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
