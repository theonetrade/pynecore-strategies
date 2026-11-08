"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, plot, request, script, syminfo, ta, timeframe


@script.indicator('Bull Market Support Band', overlay=True, timeframe='W', timeframe_gaps=True)
def main():
    source = close
    smaLength: int = 20
    emaLength: int = 21
    sma = ta.sma(source, smaLength)
    ema = ta.ema(source, emaLength)
    outSma = request.security(syminfo.tickerid, timeframe.period, sma)
    outEma = request.security(syminfo.tickerid, timeframe.period, ema)
    smaPlot = plot(outSma, color=color.new(color.red, 0), title='20w SMA')
    emaPlot = plot(outEma, color=color.new(color.green, 0), title='21w EMA')
    fill(smaPlot, emaPlot, color=color.new(color.orange, 75), fillgaps=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
