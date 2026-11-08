"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, close, color, input, label, math, plot, request,
    script, string, timeframe
)


@script.indicator(title='MF Global Money Supply M2 by MigueFinance', shorttitle='MF Global M2 by MigueFinance')
def main(
    labels_condition=input(True, 'Label'),
    _offset=input.int(0, 'Offset (move the chart horizontally in time -time shift-)', tooltip='For BTC as of 2025 the best correlation is on 107 days of offset ')
):
    EUM2D = request.security('ECONOMICS:EUM2*FX:EURUSD', timeframe.period, close)
    USM2D = request.security('ECONOMICS:USM2', timeframe.period, close)
    CAM2D = request.security('ECONOMICS:CAM2*FX_IDC:CADUSD', timeframe.period, close)
    CHM2D = request.security('ECONOMICS:CHM2*FX_IDC:CHFUSD', timeframe.period, close)
    GBM2D = request.security('ECONOMICS:GBM2*FX:GBPUSD', timeframe.period, close)
    FIPOP = request.security('ECONOMICS:FIM2/FX_IDC:USDFIM', timeframe.period, close)
    RUM2D = request.security('ECONOMICS:RUM2*FX_IDC:RUBUSD', timeframe.period, close)
    NZM2D = request.security('ECONOMICS:NZM2*FX_IDC:NZDUSD', timeframe.period, close)
    CNM2D = request.security('ECONOMICS:CNM2*FX_IDC:CNYUSD', timeframe.period, close)
    TWM2D = request.security('ECONOMICS:TWM2*FX_IDC:TWDUSD', timeframe.period, close)
    HKM2D = request.security('ECONOMICS:HKM2*FX_IDC:HKDUSD', timeframe.period, close)
    INM2D = request.security('ECONOMICS:INM2*FX_IDC:INRUSD', timeframe.period, close)
    JPM2D = request.security('ECONOMICS:JPM2*FX_IDC:JPYUSD', timeframe.period, close)
    PHM2D = request.security('ECONOMICS:PHM2*FX_IDC:PHPUSD', timeframe.period, close)
    SGM2D = request.security('ECONOMICS:SGM2*FX_IDC:SGDUSD', timeframe.period, close)
    BRM2D = request.security('ECONOMICS:BRM2*FX_IDC:BRLUSD', timeframe.period, close)
    COM2D = request.security('ECONOMICS:COM2*FX_IDC:COPUSD', timeframe.period, close)
    MXM2D = request.security('ECONOMICS:MXM2*FX_IDC:MXNUSD', timeframe.period, close)
    AEM2D = request.security('ECONOMICS:AEM2*FX_IDC:AEDUSD', timeframe.period, close)
    TRM2D = request.security('ECONOMICS:TRM2*FX_IDC:TRYUSD', timeframe.period, close)
    ZAM2D = request.security('ECONOMICS:ZAM2*FX_IDC:ZARUSD', timeframe.period, close)
    GLM2 = EUM2D + USM2D + CAM2D + CHM2D + GBM2D + FIPOP + RUM2D + NZM2D + CNM2D + TWM2D + HKM2D + INM2D + JPM2D + PHM2D + SGM2D + BRM2D + COM2D + MXM2D + AEM2D + TRM2D + ZAM2D
    plot(GLM2, color=color.blue, title='Global (World) Money Supply M2', linewidth=2, offset=_offset)
    if labels_condition and barstate.islast:
        _text = 'Global M2: ' + string.tostring(math.round(GLM2 / 1000000000000, 2)) + 'T' + (', Offset= ' + string.tostring(_offset) if _offset != 0 else '')
        label.new(bar_index + 10 + _offset, GLM2, text=_text, color=color.blue, textcolor=color.white, style=label.style_label_left)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
