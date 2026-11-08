"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import bar_index, close, high, low, math, open, script, ta
from pynecore.types import Persistent, Series
from typing import Protocol, Any


__all__ = ['OBRefiner']


class _ProtocolObrefiner(Protocol):
    def __call__(self, OBType: str, OBRefine: str, RefineMethod: str, TriggerCondition: bool, Index: int) -> Any: ...


OBRefiner: _ProtocolObrefiner = Exported()


@script.library('OrderBlockRefiner_TradingFinder', overlay=True)
def main():
    @export
    def OBRefiner(OBType: str, OBRefine: str, RefineMethod: str, TriggerCondition: bool, Index: int):
        oBType: str = OBType
        oBRefine: str = OBRefine
        refineMethod: str = RefineMethod
        triggerCondition: bool = TriggerCondition
        index: int = Index
        ATR = ta.atr(55)
        PosIndex = bar_index - index if bar_index - index < 4999 else 2
        Range: Series = high - low
        Body: Series = close - open
        Yp12: Persistent[float] = 0.0
        Xp1: Persistent[int] = 0
        Xp2: Persistent[int] = 0
        Yd12: Persistent[float] = 0.0
        Xd1: Persistent[int] = 0
        Xd2: Persistent[int] = 0
        DCRa1: Persistent[float] = 0.0
        DCRO: Persistent[float] = 0.0
        DCRb1: Persistent[float] = 0.0
        SCRa1: Persistent[float] = 0.0
        SCRO: Persistent[float] = 0.0
        SCRb1: Persistent[float] = 0.0
        DminOpen: Persistent[float] = 0.0
        DminHigh: Persistent[float] = 0.0
        DminLow: Persistent[float] = 0.0
        DminClose: Persistent[float] = 0.0
        DmaxOpen: Persistent[float] = 0.0
        DmaxHigh: Persistent[float] = 0.0
        DmaxLow: Persistent[float] = 0.0
        DmaxClose: Persistent[float] = 0.0
        SminOpen: Persistent[float] = 0.0
        SminHigh: Persistent[float] = 0.0
        SminLow: Persistent[float] = 0.0
        SminClose: Persistent[float] = 0.0
        SmaxOpen: Persistent[float] = 0.0
        SmaxHigh: Persistent[float] = 0.0
        SmaxLow: Persistent[float] = 0.0
        SmaxClose: Persistent[float] = 0.0
        DDA: Persistent[float] = 0.0
        DPA: Persistent[float] = 0.0
        SDA: Persistent[float] = 0.0
        SPA: Persistent[float] = 0.0
        ProximalRefine: Persistent[float] = 0.0
        DistalRefine: Persistent[float] = 0.0
        DCRa1 = Range[PosIndex + 1]
        DCRO = Range[PosIndex]
        DCRb1 = Range[PosIndex - 1]
        SCRa1 = Range[PosIndex + 1]
        SCRO = Range[PosIndex]
        SCRb1 = Range[PosIndex - 1]
        if oBType == 'Demand' and bar_index > 4:
            if bar_index > index + 1:
                DminOpen = math.min(open[PosIndex - 2], open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                DminHigh = math.min(high[PosIndex - 2], high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                DminLow = math.min(low[PosIndex - 2], low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                DminClose = math.min(close[PosIndex - 2], close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index + 1:
                DminOpen = math.min(open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                DminHigh = math.min(high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                DminLow = math.min(low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                DminClose = math.min(close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index:
                DminOpen = math.min(open[PosIndex + 1], open[PosIndex])
                DminHigh = math.min(high[PosIndex + 1], high[PosIndex])
                DminLow = math.min(low[PosIndex + 1], low[PosIndex])
                DminClose = math.min(close[PosIndex + 1], close[PosIndex])
            if bar_index > index + 1:
                DmaxOpen = math.max(open[PosIndex - 2], open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                DmaxHigh = math.max(high[PosIndex - 2], high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                DmaxLow = math.max(low[PosIndex - 2], low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                DmaxClose = math.max(close[PosIndex - 2], close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index + 1:
                DmaxOpen = math.max(open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                DmaxHigh = math.max(high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                DmaxLow = math.max(low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                DmaxClose = math.max(close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index:
                DmaxOpen = math.max(open[PosIndex + 1], open[PosIndex])
                DmaxHigh = math.max(high[PosIndex + 1], high[PosIndex])
                DmaxLow = math.max(low[PosIndex + 1], low[PosIndex])
                DmaxClose = math.max(close[PosIndex + 1], close[PosIndex])
            if DCRO <= ATR * 0.5:
                DPA = high[PosIndex]
                DDA = DminLow
            elif DCRO > ATR * 0.5 and DCRO <= ATR:
                if Body > 0 or Body == 0:
                    DPA = close[PosIndex]
                    DDA = DminLow
                elif Body < 0:
                    DPA = open[PosIndex]
                    DDA = DminLow
            elif DCRO > ATR:
                if bar_index > Index:
                    if low[PosIndex + 1] < high[PosIndex]:
                        if low[PosIndex + 1] > low[PosIndex]:
                            DPA = low[PosIndex + 1]
                            DDA = low[PosIndex]
                        elif low[PosIndex + 1] <= low[PosIndex]:
                            if Body[PosIndex + 1] > 0 or Body[PosIndex + 1] == 0:
                                if DCRa1 > ATR:
                                    DPA = DmaxOpen
                                    DDA = DminLow
                                elif DCRa1 <= ATR:
                                    DPA = DmaxClose
                                    DDA = DminLow
                            elif Body[PosIndex + 1] < 0:
                                if DCRa1 > ATR:
                                    DPA = DmaxOpen
                                    DDA = DminLow
                                elif DCRa1 <= ATR:
                                    DPA = DmaxOpen
                                    DDA = DminLow
                        else:
                            DPA = DmaxOpen
                            DDA = DminLow
                    elif not low[PosIndex + 1] < high[PosIndex]:
                        if DminLow - DminOpen > DminLow - DminClose and DminLow - DminOpen <= ATR and (DminLow - DminOpen >= ATR * 0.5):
                            DPA = DminOpen
                            DDA = DminLow
                        elif DminLow - DminOpen < DminLow - DminClose and DminLow - DminClose <= ATR and (DminLow - DminClose >= ATR * 0.5):
                            DPA = DminClose
                            DDA = DminLow
                        else:
                            DPA = DminClose
                            DDA = DminLow
                    else:
                        DPA = DminClose
                        DDA = DminLow
                elif DCRa1 > ATR:
                    DPA = DmaxOpen
                    DDA = DminLow
                else:
                    DPA = DmaxClose
                    DDA = DminLow
            else:
                if Body > 0:
                    DPA = DmaxHigh
                    DDA = DminLow
                elif Body < 0:
                    DPA = DmaxHigh
                    DDA = DmaxLow
        if refineMethod == 'Defensive':
            if DPA - DDA >= ATR * 4:
                DistalRefine = DDA
                ProximalRefine = DPA - (DPA - DDA) * 0.8
            elif DPA - DDA >= ATR * 3 and DPA - DDA < ATR * 4:
                DistalRefine = DDA
                ProximalRefine = DPA - (DPA - DDA) * 0.7
            elif DPA - DDA < ATR * 3 and DPA - DDA >= ATR * 2:
                DistalRefine = DDA
                ProximalRefine = DPA - (DPA - DDA) * 0.6
            elif DPA - DDA < ATR * 2 and DPA - DDA >= ATR * 1.6:
                DistalRefine = DDA
                ProximalRefine = DPA - (DPA - DDA) * 0.5
            elif DPA - DDA < ATR * 1.6 and DPA - DDA > ATR:
                DistalRefine = DDA
                ProximalRefine = DPA - (DPA - DDA) * 0.25
            elif DPA - DDA <= ATR:
                DistalRefine = DDA
                ProximalRefine = DPA
        elif refineMethod == 'Aggressive':
            DistalRefine = DDA
            ProximalRefine = DPA
        if triggerCondition:
            Yp12 = ProximalRefine if OBRefine == 'On' else high[PosIndex]
            Xp1 = index
            Xp2 = index + 1
            Yd12 = DistalRefine if OBRefine == 'On' else low[PosIndex]
            Xd1 = index
            Xd2 = index + 1
        if oBType == 'Supply' and bar_index > 4:
            if bar_index > index + 1:
                SminOpen = math.min(open[PosIndex - 2], open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                SminHigh = math.min(high[PosIndex - 2], high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                SminLow = math.min(low[PosIndex - 2], low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                SminClose = math.min(close[PosIndex - 2], close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index + 1:
                SminOpen = math.min(open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                SminHigh = math.min(high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                SminLow = math.min(low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                SminClose = math.min(close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index:
                SminOpen = math.min(open[PosIndex + 1], open[PosIndex])
                SminHigh = math.min(high[PosIndex + 1], high[PosIndex])
                SminLow = math.min(low[PosIndex + 1], low[PosIndex])
                SminClose = math.min(close[PosIndex + 1], close[PosIndex])
            if bar_index > index + 1:
                SmaxOpen = math.max(open[PosIndex - 2], open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                SmaxHigh = math.max(high[PosIndex - 2], high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                SmaxLow = math.max(low[PosIndex - 2], low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                SmaxClose = math.max(close[PosIndex - 2], close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index + 1:
                SmaxOpen = math.max(open[PosIndex + 1], open[PosIndex], open[PosIndex - 1])
                SmaxHigh = math.max(high[PosIndex + 1], high[PosIndex], high[PosIndex - 1])
                SmaxLow = math.max(low[PosIndex + 1], low[PosIndex], low[PosIndex - 1])
                SmaxClose = math.max(close[PosIndex + 1], close[PosIndex], close[PosIndex - 1])
            elif bar_index == index:
                SmaxOpen = math.max(open[PosIndex + 1], open[PosIndex])
                SmaxHigh = math.max(high[PosIndex + 1], high[PosIndex])
                SmaxLow = math.max(low[PosIndex + 1], low[PosIndex])
                SmaxClose = math.max(close[PosIndex + 1], close[PosIndex])
            if SCRO <= ATR * 0.5:
                SPA = low[PosIndex]
                SDA = SmaxHigh
            elif SCRO > ATR * 0.5 and SCRO <= ATR:
                if Body > 0 or Body == 0:
                    SPA = close[PosIndex]
                    SDA = SmaxHigh
                elif Body < 0:
                    SPA = open[PosIndex]
                    SDA = SmaxHigh
            elif SCRO > ATR:
                if bar_index > Index:
                    if high[PosIndex - 1] > low[PosIndex]:
                        if high[PosIndex - 1] > high[PosIndex]:
                            SPA = high[PosIndex - 1]
                            SDA = high[PosIndex]
                        elif high[PosIndex - 1] <= high[PosIndex]:
                            if Body[PosIndex - 1] > 0 or Body[PosIndex - 1] == 0:
                                if SCRa1 > ATR:
                                    SPA = SminClose
                                    SDA = SmaxHigh
                                elif SCRa1 <= ATR:
                                    SPA = SminOpen
                                    SDA = SmaxHigh
                            elif Body[PosIndex - 1] < 0:
                                if SCRa1 > ATR:
                                    SPA = SminOpen
                                    SDA = SmaxHigh
                                elif SCRa1 <= ATR:
                                    SPA = SmaxClose
                                    SDA = SmaxHigh
                        else:
                            SPA = SminOpen
                            SDA = SmaxHigh
                    elif not high[PosIndex + 1] > low[PosIndex]:
                        if SmaxHigh - SminOpen > SmaxHigh - SminClose and SmaxHigh - SminOpen <= ATR and (SmaxHigh - SminOpen >= ATR * 0.5):
                            SPA = SminOpen
                            SDA = SmaxHigh
                        elif SmaxHigh - DminOpen < SmaxHigh - DminClose and SmaxHigh - DminClose <= ATR and (SmaxHigh - DminClose >= ATR * 0.5):
                            SPA = SminClose
                            SDA = SmaxHigh
                        else:
                            SPA = SminClose
                            SDA = SmaxHigh
                    else:
                        SPA = SminClose
                        SDA = SmaxHigh
                elif SCRa1 > ATR:
                    SPA = SminClose
                    SDA = SmaxHigh
                else:
                    SPA = SminOpen
                    SDA = SmaxHigh
            else:
                if Body > 0:
                    SPA = SminLow
                    SDA = SmaxHigh
                elif Body < 0:
                    SPA = SminLow
                    SDA = SmaxHigh
            if refineMethod == 'Defensive':
                if SDA - SPA >= ATR * 4:
                    DistalRefine = SDA
                    ProximalRefine = SPA + (SDA - SPA) * 0.8
                elif SDA - SPA >= ATR * 3 and SDA - SPA < ATR * 4:
                    DistalRefine = SDA
                    ProximalRefine = SPA + (SDA - SPA) * 0.7
                elif SDA - SPA < ATR * 3 and SDA - SPA >= ATR * 2:
                    DistalRefine = SDA
                    ProximalRefine = SPA + (SDA - SPA) * 0.6
                elif SDA - SPA < ATR * 2 and SDA - SPA >= ATR * 1.6:
                    DistalRefine = SDA
                    ProximalRefine = SPA + (SDA - SPA) * 0.5
                elif SDA - SPA < ATR * 1.6 and SDA - SPA > ATR:
                    DistalRefine = SDA
                    ProximalRefine = SPA + (SDA - SPA) * 0.25
                elif SDA - SPA <= ATR:
                    DistalRefine = SDA
                    ProximalRefine = SPA
            elif refineMethod == 'Aggressive':
                DistalRefine = SDA
                ProximalRefine = SPA
            if triggerCondition:
                Yp12 = ProximalRefine if OBRefine == 'On' else low[PosIndex]
                Xp1 = index
                Xp2 = index + 1
                Yd12 = DistalRefine if OBRefine == 'On' else high[PosIndex]
                Xd1 = index
                Xd2 = index + 1
        return (Xd1, Xd2, Yd12, Xp1, Xp2, Yp12)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
