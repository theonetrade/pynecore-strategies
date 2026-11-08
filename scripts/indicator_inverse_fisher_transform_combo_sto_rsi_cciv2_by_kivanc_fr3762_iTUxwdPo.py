"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, high, hlc3, hline, input, low, math, na, plot, script, ta,
    volume
)


@script.indicator('Inverse Fisher Transform COMBO', shorttitle='IFTCOMBO', timeframe='')
def main(
    STO=input(False, title='Show INVERSE FISHER TRANSFORM on STOCHASTIC Line?'),
    RSI=input(False, title='Show INVERSE FISHER TRANSFORM on RSI Line?'),
    CCI=input(True, title='Show INVERSE FISHER TRANSFORM on CCI Line?'),
    MFI=input(False, title='Show INVERSE FISHER TRANSFORM on MFI Line?'),
    AVERAGE=input(False, title='Show INVERSE FISHER TRANSFORM AVERAGE Line?'),
    ccilength=input(5, 'CCI Length'),
    wmalength=input(9, title='Smoothing Length'),
    rsilength=input(5, 'RSI Length'),
    stochlength=input(5, 'STOCH Length'),
    mfilength=input(5, 'MFI Length')
):
    v11 = 0.1 * (ta.cci(close, ccilength) / 4)
    v21 = ta.wma(v11, wmalength)
    INV1 = (math.exp(2 * v21) - 1) / (math.exp(2 * v21) + 1)
    v12 = 0.1 * (ta.rsi(close, rsilength) - 50)
    v22 = ta.wma(v12, wmalength)
    INV2 = (math.exp(2 * v22) - 1) / (math.exp(2 * v22) + 1)
    v1 = 0.1 * (ta.stoch(close, high, low, stochlength) - 50)
    v2 = ta.wma(v1, wmalength)
    INVLine = (math.exp(2 * v2) - 1) / (math.exp(2 * v2) + 1)
    source = hlc3
    up = math.sum(volume * (0 if ta.change(source) <= 0 else source), mfilength)
    lo = math.sum(volume * (0 if ta.change(source) >= 0 else source), mfilength)
    mfi = 100.0 - 100.0 / (1.0 + up / lo)
    v13 = 0.1 * (mfi - 50)
    v23 = ta.wma(v13, wmalength)
    INV3 = (math.exp(2 * v23) - 1) / (math.exp(2 * v23) + 1)
    AVINV = (INV1 + INV2 + INVLine + INV3) / 4
    plot(AVINV if AVERAGE and cast_bool(AVINV) else na, color=color.new(color.purple, 0), linewidth=3, title='AVERAGE')
    plot(INVLine if STO and cast_bool(INVLine) else na, color=color.new(color.blue, 0), linewidth=1, title='STOCH')
    plot(INV1 if CCI and cast_bool(INV1) else na, color=color.new(color.red, 0), linewidth=3, title='CCIv2')
    plot(INV2 if RSI and cast_bool(INV2) else na, color=color.new(color.black, 0), linewidth=2, title='RSI')
    plot(INV3 if MFI and cast_bool(INV3) else na, color=color.new(color.purple, 0), linewidth=2, title='MFI')
    hline(0.5, color=color.red)
    hline(-0.5, color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
