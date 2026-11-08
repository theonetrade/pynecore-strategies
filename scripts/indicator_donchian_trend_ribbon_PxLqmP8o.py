"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, nz, plot, script, ta
from pynecore.types import Series


@script.indicator('Donchian Trend Ribbon', precision=0, na_bool=True)
def main(
    dlen=input.int(defval=20, title='Donchian Channel Period', minval=10)
):
    def dchannel(len):
        hh: Series[float] = ta.highest(len)
        ll: Series[float] = ta.lowest(len)
        trend: Series[int] = 0
        trend = 1 if close > hh[1] else -1 if close < ll[1] else nz(trend[1])
        return trend

    def dchannelalt(len, maintrend):
        hh: Series[float] = ta.highest(len)
        ll: Series[float] = ta.lowest(len)
        trend: Series[int] = 0
        trend = 1 if close > hh[1] else -1 if close < ll[1] else nz(trend[1])
        return (color.new('#00FF00') if trend == 1 else color.new('#00FF009F')) if maintrend == 1 else (color.new('#FF0000') if trend == -1 else color.new('#FF00009F')) if maintrend == -1 else na

    maintrend = dchannel(dlen)
    plot(5, color=dchannelalt(dlen - 0, maintrend), style=plot.style_columns, histbase=0)
    plot(10, color=dchannelalt(dlen - 1, maintrend), style=plot.style_columns, histbase=5)
    plot(15, color=dchannelalt(dlen - 2, maintrend), style=plot.style_columns, histbase=10)
    plot(20, color=dchannelalt(dlen - 3, maintrend), style=plot.style_columns, histbase=15)
    plot(25, color=dchannelalt(dlen - 4, maintrend), style=plot.style_columns, histbase=20)
    plot(30, color=dchannelalt(dlen - 5, maintrend), style=plot.style_columns, histbase=25)
    plot(35, color=dchannelalt(dlen - 6, maintrend), style=plot.style_columns, histbase=30)
    plot(40, color=dchannelalt(dlen - 7, maintrend), style=plot.style_columns, histbase=35)
    plot(45, color=dchannelalt(dlen - 8, maintrend), style=plot.style_columns, histbase=40)
    plot(50, color=dchannelalt(dlen - 9, maintrend), style=plot.style_columns, histbase=45)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
