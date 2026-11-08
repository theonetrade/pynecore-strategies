"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, na, nz, plot, request, script, syminfo, ta
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Predictive Ranges [LuxAlgo]', 'LuxAlgo - Predictive Ranges', overlay=True)
def main(
    length=input.int(200, 'Length', minval=2),
    mult=input.float(6.0, 'Factor', minval=0, step=0.5),
    tf=input.timeframe('', 'Timeframe'),
    src: Series[float] = input(close, 'Source')
):
    def pred_ranges(length, mult):
        avg: PersistentSeries = src
        hold_atr: Persistent[float] = 0.0
        atr = nz(ta.atr(length)) * mult
        avg = avg + atr if src - avg > atr else avg - atr if avg - src > atr else avg
        hold_atr = atr / 2 if avg != avg[1] else hold_atr
        return (avg + hold_atr * 2, avg + hold_atr, avg, avg - hold_atr, avg - hold_atr * 2)

    avg: Series
    prR2, prR1, avg, prS1, prS2 = request.security(syminfo.tickerid, tf, pred_ranges(length, mult))
    plot_pru2 = plot(prR2, 'PR Upper 2', na if avg != avg[1] else color.new('#F23645'))
    plot_pru1 = plot(prR1, 'PR Upper 1', na if avg != avg[1] else color.new('#F23645'))
    plot_pravg = plot(avg, 'PR Average', na if avg != avg[1] else color.new('#5B9CF6'))
    plot_prl1 = plot(prS1, 'PR Lower 1', na if avg != avg[1] else color.new('#089981'))
    plot_prl2 = plot(prS2, 'PR Lower 2', na if avg != avg[1] else color.new('#089981'))
    fill(plot_pru2, plot_pru1, na if avg != avg[1] else color.new(color.new('#F23645'), 95))
    fill(plot_prl1, plot_prl2, na if avg != avg[1] else color.new(color.new('#089981'), 95))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
