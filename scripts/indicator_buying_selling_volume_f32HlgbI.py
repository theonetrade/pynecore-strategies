"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, format, high, input, low, math, na, open, plot,
    script, ta, volume
)


@script.indicator('Buying Selling Volume', format=format.volume, precision=0, overlay=False, na_bool=True)
def main(
    barColorsOnPrevClose=input(title='Color bars based on previous close', defval=False),
    Barcolor=input(False, title='Buy Sell Volume Barcolor'),
    vi=input(False, title='Volume Index'),
    VNBarcolor=input(False, title='Volume Index Barcolor'),
    Vnlen=input(1, title='Volume Index length')
):
    BV = 0 if high == low else volume * (close - low) / (high - low)
    SV = 0 if high == low else volume * (high - close) / (high - low)
    vol = volume if volume > 0 else 1
    TP = BV + SV
    BPV = BV / TP * vol
    SPV = SV / TP * vol
    TPV = BPV + SPV
    VN = vol / ta.ema(vol, 20)
    BPN = BV / ta.ema(BV, 20) * VN * 100
    SPN = SV / ta.ema(SV, 20) * VN * 100
    TPN = BPN + SPN
    BPc1 = BPV if BPV > SPV else -math.abs(BPV)
    BPc2 = BPN if BPN > SPN else -math.abs(BPN)
    SPc1 = SPV if SPV > BPV else -math.abs(SPV)
    SPc2 = SPN if SPN > BPN else -math.abs(SPN)
    BPcon = BPc2 if vi else BPc1
    SPcon = SPc2 if vi else SPc1
    palette = (color.new(color.red, 70) if close[1] > close else color.new(color.green, 70)) if barColorsOnPrevClose else color.new(color.red, 70) if open > close else color.new(color.green, 70)
    plot(na if vi else volume, color=palette, style=plot.style_columns, linewidth=3, title='Volume')
    plot(na if vi else BPcon, title='BuyVolume', color=color.new(color.green, 10), style=plot.style_columns)
    plot(na if vi else SPcon, title='SellVolume', color=color.new(color.red, 10), style=plot.style_columns)
    colors = color.blue if BPcon > SPcon else color.purple if BPcon < SPcon else color.gray
    barcolor(colors if Barcolor else na)
    BuyVolumePercent = 100 * BV / (BV + SV)
    SellVolumePercent = 100 * SV / (BV + SV)
    plot(na if vi else BuyVolumePercent, title='BuyVolume%', color=color.new(color.green, 0), style=plot.style_circles)
    plot(na if vi else SellVolumePercent, title='SellVolume%', color=color.new(color.red, 0), style=plot.style_circles)
    VNcolors = color.new('#00FFFF') if VN > Vnlen and close > open else color.new(color.gray, 10) if VN > Vnlen and close < open else color.new(color.yellow, 10)
    plot(VN, title='VolumeIndex', color=VNcolors, style=plot.style_columns)
    barcolor(VNcolors if VNBarcolor else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
