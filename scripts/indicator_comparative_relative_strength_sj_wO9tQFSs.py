"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, input, location, na, plot,
    plotshape, request, script, shape, size, ta, timeframe
)


@script.indicator("Comparative Relative Strength - SJ", shorttitle="CRS-SJ", overlay=False)
def main(
    benchSym=input.symbol("NASDAQ:NDX", "Benchmark index"),
    maLen=input.int(22, "Smoothing length", minval=1, tooltip="22 = one trading month on daily"),
    maType=input.string("EMA", "Smoothing type", options=("EMA", "SMA")),
    mode=input.string("Ratio", "Mode", options=("Ratio", "ROC")),
    rocLen=input.int(22, "ROC length", minval=1),
    showTurn=input.bool(True, "Mark the turns")
):
    benchRaw = request.security(benchSym, timeframe.period, close, ignore_invalid_symbol=True)

    benchOk = not na(benchRaw) and benchRaw != 0
    bench = benchRaw if benchOk else na

    crs = close / bench

    crsMa = ta.ema(crs, maLen) if maType == 'EMA' else ta.sma(crs, maLen)

    crsRoc = ta.roc(crs, rocLen)
    crsRocMa = ta.ema(crsRoc, maLen) if maType == 'EMA' else ta.sma(crsRoc, maLen)

    isRoc = mode == 'ROC'

    lineRaw = crsRoc if isRoc else crs
    lineMa = crsRocMa if isRoc else crsMa

    pRaw = plot(lineRaw, 'CRS', color=color.new(color.gray, 0))
    pMa = plot(lineMa, 'CRS smoothed', color=color.navy, linewidth=2)

    plot(0.0 if isRoc else na, 'Zero', color=color.new(color.gray, 40))

    fill(pRaw, pMa, color=color.new(color.green, 88) if lineRaw > lineMa else color.new(color.red, 88))

    outperforming = lineRaw > lineMa
    turnUp = ta.crossover(lineRaw, lineMa)
    turnDn = ta.crossunder(lineRaw, lineMa)

    plotshape(showTurn and turnUp, 'CRS turns up', shape.circle, location.bottom, color.new(color.green, 0), size=size.tiny)
    plotshape(showTurn and turnDn, 'CRS turns down', shape.circle, location.top, color.new(color.red, 0), size=size.tiny)

    alertcondition(turnUp, 'CRS turn up', 'CRS crossed above its average - stock beginning to beat the index')
    alertcondition(turnDn, 'CRS turn down', 'CRS crossed below its average - stock beginning to lag the index')

    plot(crsRoc, 'SCAN: CRS ROC %', color=color.new(color.gray, 100), display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)