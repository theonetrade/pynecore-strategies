"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import bar_index, color, high, label, line, low, math, na, script, size, ta
from pynecore.types import Label, Line, PersistentSeries, Series
from typing import Protocol, Any


__all__ = ['LLF']


class _ProtocolLlf(Protocol):
    def __call__(self, sPP: int, dPP: int, SRs: float, SRd: float, ShowHLLs: bool, ShowLLLs: bool, ShowHLLd: bool, ShowLLLd: bool) -> Any: ...


LLF: _ProtocolLlf = Exported()


@script.library('LiquidityFinderLibrary', overlay=True)
def main():
    @export
    def LLF(sPP: int, dPP: int, SRs: float, SRd: float, ShowHLLs: bool, ShowLLLs: bool, ShowHLLd: bool, ShowLLLd: bool):
        ATR: Series = ta.atr(55)
        STSHighPivot = ta.pivothigh(sPP, sPP)
        STSLowPivot = ta.pivotlow(sPP, sPP)
        STSHVc = ta.valuewhen(STSHighPivot, high[sPP], 0)
        STSLVc = ta.valuewhen(STSLowPivot, low[sPP], 0)
        STSHIc: Series = ta.valuewhen(STSHighPivot, bar_index[sPP], 0)
        STSLIc: Series = ta.valuewhen(STSLowPivot, bar_index[sPP], 0)
        STSHVp = ta.valuewhen(STSHighPivot, high[sPP], 1)
        STSLVp = ta.valuewhen(STSLowPivot, low[sPP], 1)
        STSHIp = ta.valuewhen(STSHighPivot, bar_index[sPP], 1)
        STSLIp = ta.valuewhen(STSLowPivot, bar_index[sPP], 1)
        DTSHighPivot = ta.pivothigh(dPP, dPP)
        DTSLowPivot = ta.pivotlow(dPP, dPP)
        DTSHVc = ta.valuewhen(DTSHighPivot, high[dPP], 0)
        DTSLVc = ta.valuewhen(DTSLowPivot, low[dPP], 0)
        DTSHIc: Series = ta.valuewhen(DTSHighPivot, bar_index[dPP], 0)
        DTSLIc: Series = ta.valuewhen(DTSLowPivot, bar_index[dPP], 0)
        DTSHVp = ta.valuewhen(DTSHighPivot, high[dPP], 1)
        DTSLVp = ta.valuewhen(DTSLowPivot, low[dPP], 1)
        DTSHIp = ta.valuewhen(DTSHighPivot, bar_index[dPP], 1)
        DTSLIp = ta.valuewhen(DTSLowPivot, bar_index[dPP], 1)
        sHLL: PersistentSeries[Line] = na(Line)
        sLLL: PersistentSeries[Line] = na(Line)
        sHLLl: PersistentSeries[Label] = na(Label)
        sLLLl: PersistentSeries[Label] = na(Label)
        dHLL: PersistentSeries[Line] = na(Line)
        dLLL: PersistentSeries[Line] = na(Line)
        dHLLl: PersistentSeries[Label] = na(Label)
        dLLLl: PersistentSeries[Label] = na(Label)
        if STSHIc != STSHIc[1] and STSHVc <= STSHVp and (STSHIc - STSHIp >= 8) and ShowHLLs:
            if math.abs((STSHVp - STSHVc) / ATR[sPP]) <= SRs:
                sHLL = line.new(x1=STSHIp, y1=STSHVp, x2=STSHIc, y2=STSHVp, color=color.rgb(18, 123, 184, 43), style=line.style_dotted)
                sHLLl = label.new(x=math.round((STSHIp + STSHIc) / 2), y=STSHVp - ATR / 2, text='2 Top Liq', color=color.rgb(255, 255, 255, 100), textcolor=color.rgb(18, 123, 184), style=label.style_label_down, size=size.small)
        if STSLIc != STSLIc[1] and STSLVc >= STSLVp and (STSLIc - STSLIp >= 8) and ShowLLLs:
            if math.abs((STSLVp - STSLVc) / ATR[sPP]) <= SRs:
                sLLL = line.new(x1=STSLIp, y1=STSLVp, x2=STSLIc, y2=STSLVp, color=color.rgb(162, 10, 233, 45), style=line.style_dotted)
                sLLLl = label.new(x=math.round((STSLIp + STSLIc) / 2), y=STSLVp + ATR / 2, text='2 Bottom Liq', color=color.rgb(255, 255, 255, 100), textcolor=color.rgb(162, 10, 233), style=label.style_label_up, size=size.small)
        if DTSHIc != DTSHIc[1] and DTSHVc <= DTSHVp and (DTSHIc - DTSHIp >= 4) and ShowHLLd:
            if math.abs((DTSHVp - DTSHVc) / ATR[dPP]) >= SRd and math.abs((DTSHVp - DTSHVc) / ATR[dPP]) <= 1.95:
                dHLL = line.new(x1=DTSHIp, y1=DTSHVp, x2=DTSHIc, y2=DTSHVc, color=color.rgb(18, 123, 184, 44), style=line.style_dotted)
                dHLLl = label.new(x=math.round((DTSHIp + DTSHIc) / 2) + 2, y=(DTSHVp + DTSHVc) / 2 - ATR / 4, text='DLiq', color=color.rgb(255, 255, 255, 100), textcolor=color.rgb(18, 123, 184), style=label.style_label_down, size=size.small)
        if DTSLIc != DTSLIc[1] and DTSLVc >= DTSLVp and (DTSLIc - DTSLIp >= 4) and ShowLLLd:
            if math.abs((DTSLVp - DTSLVc) / ATR[dPP]) >= SRd and math.abs((DTSLVp - DTSLVc) / ATR[dPP]) <= 1.95:
                dLLL = line.new(x1=DTSLIp, y1=DTSLVp, x2=DTSLIc, y2=DTSLVc, color=color.rgb(162, 10, 233, 45), style=line.style_dotted)
                dLLLl = label.new(x=math.round((DTSLIp + DTSLIc) / 2) + 2, y=(DTSLVp + DTSLVp) / 2 + ATR / 4, text='DLiq', color=color.rgb(255, 255, 255, 100), textcolor=color.rgb(162, 10, 233), style=label.style_label_up, size=size.small)
        if math.abs(line.get_x2(sHLL[1]) - line.get_x1(sHLL)) <= 2:
            line.delete(sHLL)
            label.delete(sHLLl[1])
            line.set_x2(sHLL[1], STSHIc)
            label.set_text(sHLLl, '3 Top Liq')
            label.set_x(sHLLl, math.abs((line.get_x1(sHLL[1]) + line.get_x2(sHLL[1])) / 2))
        if math.abs(line.get_x2(sLLL[1]) - line.get_x1(sLLL)) <= 2:
            line.delete(sLLL)
            label.delete(sLLLl[1])
            line.set_x2(sLLL[1], STSLIc)
            label.set_text(sLLLl, '3 Top Liq')
            label.set_x(sLLLl, math.abs((line.get_x1(sLLL[1]) + line.get_x2(sLLL[1])) / 2))
        if math.abs(line.get_x2(dHLL[1]) - line.get_x1(dHLL)) <= dPP * 2 + 1:
            line.delete(dHLL)
            label.delete(dHLLl[1])
            line.set_xy2(dHLL[1], DTSHIc, DTSHVc)
            label.set_xy(dHLLl, math.abs((line.get_x1(dHLL[1]) + line.get_x2(dHLL[1])) / 2 + 2), (line.get_y1(dHLL[1]) + line.get_y2(dHLL[1])) / 2)
        __block_result__ = na
        if math.abs(line.get_x2(dLLL[1]) - line.get_x1(dLLL)) <= dPP * 2 + 1:
            line.delete(dLLL)
            label.delete(dLLLl[1])
            line.set_xy2(dLLL[1], DTSLIc, DTSLVc)
            __block_result__ = label.set_xy(dLLLl, math.abs((line.get_x1(dLLL[1]) + line.get_x2(dLLL[1])) / 2 + 2), (line.get_y1(dLLL[1]) + line.get_y2(dLLL[1])) / 2)
        return __block_result__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
