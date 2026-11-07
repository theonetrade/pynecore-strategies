"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, close, color, high, input, label, line, low, na,
    script, strategy, ta
)
from pynecore.types import Label, Line, Persistent, PersistentSeries


@script.strategy('Quasimodo Pattern Strategy Back Test [TradingFinder] QM Trading', 'QM Strategy TFlab', overlay=True, initial_capital=1000, default_qty_type=strategy.cash, default_qty_value=10000, max_bars_back=5000, max_lines_count=500, max_labels_count=500, margin_long=0, margin_short=0, close_by_id=True)
def main(
    PP=input.int(5, 'Pivot Period'),
    TPMode=input.string('TP1', 'Take Profit Mode', options=('TP1', 'TP2', 'R/R')),
    SLMode=input.string('Original', 'Stop Loss Refine', options=('Original', 'ATR Refine')),
    RR=input.float(2.0, 'Reward to Risk Ratio', minval=0.25),
    CSL=input.float(0.5, 'Stop Loss ATR Adjustment Coefficient', minval=0.25),
    ELV=input.int(2, 'Entry Level Validity', minval=2, maxval=15, tooltip='Determines how long the Entry level remains valid. The higher the level, the longer the entry level will remain valid. By default it is 2 and it can be set between 2 and 15.')
):
    ATR = ta.atr(21)
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
    def QMDetector(TPMode, SLMode, RR, CSL):
        TH1: Persistent[str] = ''
        TH2: Persistent[str] = ''
        TH3: Persistent[str] = ''
        TH4: Persistent[str] = ''
        TH5: Persistent[str] = ''
        IH: Persistent[int] = 0
        IH1: Persistent[int] = 0
        IH2: Persistent[int] = 0
        IH3: Persistent[int] = 0
        IH4: Persistent[int] = 0
        IH5: Persistent[int] = 0
        VH1: Persistent[float] = 0.0
        VH2: Persistent[float] = 0.0
        VH3: Persistent[float] = 0.0
        VH4: Persistent[float] = 0.0
        VH5: Persistent[float] = 0.0
        BearQM: Persistent[bool] = False
        TL1: Persistent[str] = ''
        TL2: Persistent[str] = ''
        TL3: Persistent[str] = ''
        TL4: Persistent[str] = ''
        TL5: Persistent[str] = ''
        IL: Persistent[int] = 0
        IL1: Persistent[int] = 0
        IL2: Persistent[int] = 0
        IL3: Persistent[int] = 0
        IL4: Persistent[int] = 0
        IL5: Persistent[int] = 0
        VL1: Persistent[float] = 0.0
        VL2: Persistent[float] = 0.0
        VL3: Persistent[float] = 0.0
        VL4: Persistent[float] = 0.0
        VL5: Persistent[float] = 0.0
        BullQM: Persistent[bool] = False
        TPmode: Persistent[str] = TPMode
        SLmode: Persistent[str] = SLMode
        rr: Persistent[float] = RR
        Csl: Persistent[float] = CSL
        if array.size(ArrayType) > 5:
            TH1 = array.get(ArrayType, array.size(ArrayType) - 1)
            TH2 = array.get(ArrayType, array.size(ArrayType) - 2)
            TH3 = array.get(ArrayType, array.size(ArrayType) - 3)
            TH4 = array.get(ArrayType, array.size(ArrayType) - 4)
            TH5 = array.get(ArrayType, array.size(ArrayType) - 5)
            IH = array.get(ArrayIndex, array.size(ArrayType) - 1)
            IH1 = array.get(ArrayIndex, array.size(ArrayType) - 1)
            IH2 = array.get(ArrayIndex, array.size(ArrayType) - 2)
            IH3 = array.get(ArrayIndex, array.size(ArrayType) - 3)
            IH4 = array.get(ArrayIndex, array.size(ArrayType) - 4)
            IH5 = array.get(ArrayIndex, array.size(ArrayType) - 5)
            VH1 = array.get(ArrayValue, array.size(ArrayType) - 1)
            VH2 = array.get(ArrayValue, array.size(ArrayType) - 2)
            VH3 = array.get(ArrayValue, array.size(ArrayType) - 3)
            VH4 = array.get(ArrayValue, array.size(ArrayType) - 4)
            VH5 = array.get(ArrayValue, array.size(ArrayType) - 5)
        if array.size(ArrayType) > 5:
            TL1 = array.get(ArrayType, array.size(ArrayType) - 1)
            TL2 = array.get(ArrayType, array.size(ArrayType) - 2)
            TL3 = array.get(ArrayType, array.size(ArrayType) - 3)
            TL4 = array.get(ArrayType, array.size(ArrayType) - 4)
            TL5 = array.get(ArrayType, array.size(ArrayType) - 5)
            IL = array.get(ArrayIndex, array.size(ArrayType) - 1)
            IL1 = array.get(ArrayIndex, array.size(ArrayType) - 1)
            IL2 = array.get(ArrayIndex, array.size(ArrayType) - 2)
            IL3 = array.get(ArrayIndex, array.size(ArrayType) - 3)
            IL4 = array.get(ArrayIndex, array.size(ArrayType) - 4)
            IL5 = array.get(ArrayIndex, array.size(ArrayType) - 5)
            VL1 = array.get(ArrayValue, array.size(ArrayType) - 1)
            VL2 = array.get(ArrayValue, array.size(ArrayType) - 2)
            VL3 = array.get(ArrayValue, array.size(ArrayType) - 3)
            VL4 = array.get(ArrayValue, array.size(ArrayType) - 4)
            VL5 = array.get(ArrayValue, array.size(ArrayType) - 5)
        BearQM_Start: Persistent[float] = 0.0
        BearQM_End: Persistent[float] = 0.0
        BearQM_Index: Persistent[float] = 0.0
        CheckBe: Persistent[int] = 0
        if TH1 == 'LL' and TH2 == 'HH' and (TH3 == 'HL') and (TH4 == 'HH') and (VH5 < VH1) and (IH == bar_index - PP) and (CheckBe == 0):
            BearQM = True
            BearQM_Start = VH2
            BearQM_End = VH1
            BearQM_Index = IH
            CheckBe = 1
        else:
            BearQM = False
        if BearQM_Start != VH2:
            CheckBe = 0
        BullQM_Start: Persistent[float] = 0.0
        BullQM_End: Persistent[float] = 0.0
        BullQM_Index: Persistent[int] = 0
        CheckBu: Persistent[int] = 0
        if TL1 == 'HH' and TL2 == 'LL' and (TL3 == 'LH') and (TL4 == 'LL') and (VL5 > VL1) and (IL == bar_index - PP) and (CheckBu == 0):
            BullQM = True
            BullQM_Start = VL2
            BullQM_End = VL1
            BullQM_Index = IL
            CheckBu = 1
        else:
            BullQM = False
        if BullQM_Start != VL2:
            CheckBu = 0
        BuLeg1: Persistent[Line] = na(Line)
        BuLeg2: Persistent[Line] = na(Line)
        BuLeg3: Persistent[Line] = na(Line)
        BuLeg4: Persistent[Line] = na(Line)
        BuLeg5: Persistent[Line] = na(Line)
        BuEntryLine: PersistentSeries[Line] = na(Line)
        BuSLLine: Persistent[Line] = na(Line)
        BuTP1Line: Persistent[Line] = na(Line)
        BuTP2Line: Persistent[Line] = na(Line)
        BuEntryLabel: Persistent[Label] = na(Label)
        BuSLLabel: Persistent[Label] = na(Label)
        BuTP1Label: Persistent[Label] = na(Label)
        BuTP2Label: Persistent[Label] = na(Label)
        BuMove = (IL2 - IL4) / 2
        BeLeg1: Persistent[Line] = na(Line)
        BeLeg2: Persistent[Line] = na(Line)
        BeLeg3: Persistent[Line] = na(Line)
        BeLeg4: Persistent[Line] = na(Line)
        BeLeg5: Persistent[Line] = na(Line)
        BeEntryLine: PersistentSeries[Line] = na(Line)
        BeSLLine: Persistent[Line] = na(Line)
        BeTP1Line: Persistent[Line] = na(Line)
        BeTP2Line: Persistent[Line] = na(Line)
        BeEntryLabel: Persistent[Label] = na(Label)
        BeSLLabel: Persistent[Label] = na(Label)
        BeTP1Label: Persistent[Label] = na(Label)
        BeTP2Label: Persistent[Label] = na(Label)
        BeMove = (IH2 - IH4) / 2
        if BullQM:
            BuLeg1 = line.new(IL5, VL5, IL4, VL4, color=color.new('#00A740F5'), width=2)
            BuLeg2 = line.new(IL4, VL4, IL3, VL3, color=color.new('#00A740F5'), width=2)
            BuLeg3 = line.new(IL3, VL3, IL2, VL2, color=color.new('#00A740F5'), width=2)
            BuLeg4 = line.new(IL2, VL2, IL1, VL1, color=color.new('#00A740F5'), width=2)
            BuLeg5 = line.new(IL1, VL1, IL1 + BuMove - 2, VL4, color=color.new('#04D7FC'), width=2, style=line.style_arrow_right)
            BuEntryLine = line.new(IL4, VL4, IL1 + BuMove, VL4, color=color.new('#534D4D'), width=1, style=line.style_dotted)
            BuSLLine = line.new(IL2, VL2 if SLmode == 'Original' else VL2 - ATR * Csl, IL1 + BuMove, VL2 if SLmode == 'Original' else VL2 - ATR * Csl, color=color.new('#B40054'), width=1, style=line.style_dotted)
            BuTP1Line = line.new(IL3, VL3, IL1 + BuMove, VL3, color=color.new('#009E3D'), width=1, style=line.style_dotted)
            BuTP2Line = line.new(IL1, VL1, IL1 + BuMove, VL1, color=color.new('#009E3D'), width=1, style=line.style_dotted)
            BuEntryLabel = label.new(IL1 + BuMove + 1, VL4, 'Entry', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BuSLLabel = label.new(IL1 + BuMove + 1, VL2 if SLmode == 'Original' else VL2 - ATR * Csl, 'SL', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BuTP1Label = label.new(IL1 + BuMove + 1, VL3, 'TP1', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BuTP2Label = label.new(IL1 + BuMove + 1, VL1, 'TP2', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
        if BearQM:
            BeLeg1 = line.new(IH5, VH5, IH4, VH4, color=color.new('#B40054'), width=2)
            BeLeg2 = line.new(IH4, VH4, IH3, VH3, color=color.new('#B40054'), width=2)
            BeLeg3 = line.new(IH3, VH3, IH2, VH2, color=color.new('#B40054'), width=2)
            BeLeg4 = line.new(IH2, VH2, IH1, VH1, color=color.new('#B40054'), width=2)
            BeLeg5 = line.new(IH1, VH1, IH1 + BeMove - 2, VH4, color=color.new('#FCAD04'), width=2, style=line.style_arrow_right)
            BeEntryLine = line.new(IH4, VH4, IH1 + BeMove, VH4, color=color.new('#534D4D'), width=1, style=line.style_dotted)
            BeSLLine = line.new(IH2, VH2 if SLmode == 'Original' else VH2 + ATR * Csl, IH1 + BeMove, VH2 if SLmode == 'Original' else VH2 + ATR * Csl, color=color.new('#B40054'), width=1, style=line.style_dotted)
            BeTP1Line = line.new(IH3, VH3, IH1 + BeMove, VH3, color=color.new('#009E3D'), width=1, style=line.style_dotted)
            BeTP2Line = line.new(IH1, VH1, IH1 + BeMove, VH1, color=color.new('#009E3D'), width=1, style=line.style_dotted)
            BeEntryLabel = label.new(IH1 + BeMove + 1, VH4, 'Entry', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BeSLLabel = label.new(IH1 + BeMove + 1, VH2 if SLmode == 'Original' else VH2 + ATR * Csl, 'SL', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BeTP1Label = label.new(IH1 + BeMove + 1, VH3, 'TP1', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
            BeTP2Label = label.new(IH1 + BeMove + 1, VH1, 'TP2', color=color.new('#B3B1B100'), style=label.style_text_outline, textcolor=color.new('#B3B1B1'))
        BeCheck: Persistent[int] = 0
        if high >= line.get_y1(BeEntryLine) and high < line.get_y1(BeSLLine) and (BeCheck == 0) and (BearQM_Index + BeMove * ELV > bar_index):
            BeCheck = 1
            strategy.entry('Sell', strategy.short)
        if low <= (line.get_y1(BeTP1Line) if TPmode == 'TP1' else line.get_y1(BeTP2Line) if TPmode == 'TP2' else strategy.position_avg_price - (line.get_y1(BeSLLine) - strategy.position_avg_price) * rr):
            strategy.close('Sell')
        elif high >= line.get_y1(BeSLLine):
            strategy.close('Sell')
        if line.get_y1(BeEntryLine) != line.get_y1(BeEntryLine[1]):
            BeCheck = 0
        BuCheck: Persistent[int] = 0
        if low <= line.get_y1(BuEntryLine) and low > line.get_y1(BuSLLine) and (BuCheck == 0) and (BullQM_Index + BuMove * ELV > bar_index):
            strategy.entry('Buy', strategy.long)
            BuCheck = 1
        if high >= (line.get_y1(BuTP1Line) if TPmode == 'TP1' else line.get_y1(BuTP2Line) if TPmode == 'TP2' else strategy.position_avg_price + (strategy.position_avg_price - line.get_y1(BuSLLine)) * rr):
            strategy.close('Buy')
        elif low <= line.get_y1(BuSLLine):
            strategy.close('Buy')
        __block_result__ = na
        if line.get_y1(BuEntryLine) != line.get_y1(BuEntryLine[1]):
            BuCheck = 0
            __block_result__ = BuCheck
        return __block_result__

    QMDetector(TPMode, SLMode, RR, CSL)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
