"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    bar_index, close, color, high, label, line, linefill, low, math, na,
    open, script, size, ta, text
)
from pynecore.types import Label, Line, LineFill, Persistent, PersistentSeries
from typing import Protocol, Any


__all__ = ['FVGDetector']


class _ProtocolFvgdetector(Protocol):
    def __call__(self, FVGFilter: str, FVGFilterType: str, ShowDeFVG: bool, ShowSuFVG: bool) -> Any: ...


FVGDetector: _ProtocolFvgdetector = Exported()


@script.library('FVGDetectorLibrary', overlay=True, na_bool=True)
def main():
    @export
    def FVGDetector(FVGFilter: str, FVGFilterType: str, ShowDeFVG: bool, ShowSuFVG: bool):
        DDFVG: PersistentSeries[float] = 0.0
        DPFVG: Persistent[float] = 0.0
        SDFVG: PersistentSeries[float] = 0.0
        SPFVG: Persistent[float] = 0.0
        BarDFVG: Persistent[int] = 0
        BarSFVG: Persistent[int] = 0
        DDistal: Persistent[Line] = na(Line)
        DProximal: Persistent[Line] = na(Line)
        Dfillline: Persistent[LineFill] = na(LineFill)
        SDistal: Persistent[Line] = na(Line)
        SProximal: Persistent[Line] = na(Line)
        Sfillline: Persistent[LineFill] = na(LineFill)
        DFVGLabel: Persistent[Label] = na(Label)
        SFVGLabel: Persistent[Label] = na(Label)
        DMitigated: Persistent[bool] = True
        SMitigated: Persistent[bool] = True
        ATR = ta.atr(55)
        __block_result__ = na
        if FVGFilter == 'Off':
            __block_result__ = low > high[2]
        elif FVGFilter == 'On':
            __block_result_1__ = na
            __switch_1__ = FVGFilterType
            if __switch_1__ == 'Very Aggressive':
                __block_result_1__ = low > high[2] and high > high[1]
            elif __switch_1__ == 'Aggressive':
                __block_result_1__ = low > high[2] and high[1] - low[1] >= 1.0 * ATR and (high > high[1])
            elif __switch_1__ == 'Defensive':
                __block_result_1__ = low > high[2] and high[1] - low[1] >= 1.5 * ATR and (high > high[1]) and (close[2] - open[2] > 0 and close[1] - open[1] > 0 or math.abs((close[1] - open[1]) / (high[1] - low[1])) > 0.7)
            elif __switch_1__ == 'Very Defensive':
                __block_result_1__ = low > high[2] and high[1] - low[1] >= 1.5 * ATR and (high > high[1]) and (close[2] - open[2] > 0) and (close[1] - open[1] > 0) and (math.abs((close[1] - open[1]) / (high[1] - low[1])) > 0.7) and (math.abs((close[2] - open[2]) / (high[2] - low[2])) > 0.35) and (math.abs((close - open) / (high - low)) > 0.35)
            __block_result__ = __block_result_1__
        DConditionFVG = __block_result__
        __block_result_2__ = na
        if FVGFilter == 'Off':
            __block_result_2__ = high < low[2]
        elif FVGFilter == 'On':
            __block_result_3__ = na
            __switch_1__ = FVGFilterType
            if __switch_1__ == 'Very Aggressive':
                __block_result_3__ = high < low[2] and low[1] > low
            elif __switch_1__ == 'Aggressive':
                __block_result_3__ = high < low[2] and high[1] - low[1] >= 1.0 * ATR and (low[1] > low)
            elif __switch_1__ == 'Defensive':
                __block_result_3__ = high < low[2] and high[1] - low[1] >= 1.5 * ATR and (low[1] > low) and (close[2] - open[2] < 0 and close[1] - open[1] < 0 or math.abs((close[1] - open[1]) / (high[1] - low[1])) > 0.7)
            elif __switch_1__ == 'Very Defensive':
                __block_result_3__ = high < low[2] and high[1] - low[1] >= 1.5 * ATR and (low[1] > low) and (close[2] - open[2] < 0) and (close[1] - open[1] < 0) and (math.abs((close[1] - open[1]) / (high[1] - low[1])) > 0.7) and (math.abs((close[2] - open[2]) / (high[2] - low[2])) > 0.35) and (math.abs((close - open) / (high - low)) > 0.35)
            __block_result_2__ = __block_result_3__
        SConditionFVG = __block_result_2__
        if DConditionFVG and ShowDeFVG:
            DDFVG = high[2]
            DPFVG = low
            BarDFVG = bar_index
            DDistal = line.new(BarDFVG, DDFVG, BarDFVG, DDFVG, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            DProximal = line.new(BarDFVG, DPFVG, BarDFVG, DPFVG, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            Dfillline = linefill.new(DDistal, DProximal, color=color.new('#A9D60580'))
            DFVGLabel = label.new(BarDFVG, DDFVG, text='FVG', style=label.style_label_up, color=color.rgb(255, 255, 255, 100), textcolor=color.new('#000000'), textalign=text.align_center, size=size.small)
        if (low > DDFVG or DDFVG == DDFVG[1]) and DMitigated == True:
            line.set_x2(DDistal, bar_index + 1)
            line.set_x2(DProximal, bar_index + 1)
            label.set_x(DFVGLabel, math.round((BarDFVG + bar_index) / 2))
        if low[1] >= DPFVG and low <= DPFVG:
            DMitigated = False
        if DConditionFVG:
            DMitigated = True
        if SConditionFVG and ShowSuFVG:
            SDFVG = low[2]
            SPFVG = high
            BarSFVG = bar_index
            SDistal = line.new(BarSFVG, SDFVG, BarSFVG + 10, SDFVG, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            SProximal = line.new(BarSFVG, SPFVG, BarSFVG + 10, SPFVG, color=color.rgb(0, 0, 0), style=line.style_dotted, width=1)
            Sfillline = linefill.new(SDistal, SProximal, color=color.new('#FF7D044D'))
            SFVGLabel = label.new(BarSFVG, SDFVG, text='FVG', style=label.style_label_down, color=color.rgb(255, 255, 255, 100), textcolor=color.new('#000000'), textalign=text.align_center, size=size.small)
        if (high < SDFVG or SDFVG == SDFVG[1]) and SMitigated == True:
            line.set_x2(SDistal, bar_index + 1)
            line.set_x2(SProximal, bar_index + 1)
            label.set_x(SFVGLabel, math.round((BarSFVG + bar_index) / 2))
        if high >= SPFVG and high[1] <= SPFVG:
            SMitigated = False
        __block_result_4__ = na
        if SConditionFVG:
            SMitigated = True
            __block_result_4__ = SMitigated
        return __block_result_4__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
