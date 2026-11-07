"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bgcolor, color, format, hlc3, input, math, nz, plot, request, script,
    strategy, syminfo, ta, ticker, timeframe
)
from pynecore.types import Color, Series

vIndicatorName: str = 'Heikin/Kaufman Non-Repaint'
vIndicatorShortName: str = 'HKU Non-Repaint'


@script.strategy(title=vIndicatorName, shorttitle=vIndicatorShortName, overlay=True, calc_on_every_tick=True, calc_on_order_fills=True, pyramiding=0, default_qty_value=1, default_qty_type=strategy.fixed, format=format.price, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.02, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    iResolution=input.timeframe(defval='25', title='Heikin Ashi EMA Time Frame'),
    iShiftNRP=input.int(defval=1, title='Non-Repaint Candle Shift', step=1, maxval=50, minval=0),
    iPeriodSMA=input.int(defval=21, title='Slow EMA Period', step=1, maxval=200, minval=1),
    Length=input.int(defval=10, title='Length', step=1, maxval=100, minval=1),
    iSource: Series[float] = input(defval=hlc3, title='Source'),
    iPeriodFMA=input.int(defval=1, title='Source Smoothing Value', step=1, maxval=50, minval=0),
    Fastend=input.float(defval=5, title='Fast', step=0.5, maxval=100, minval=1),
    Slowend=input.int(defval=20, title='Slow', step=1, maxval=100, minval=1),
    iCandleType=input.string(defval='HeikinAshi', title='Choose Candle Type', options=('HeikinAshi', 'Japanese'))
):
    jTicker = syminfo.prefix + ':' + syminfo.ticker
    hTicker = ticker.heikinashi(syminfo.tickerid)
    vTicker = jTicker if iCandleType == 'Japanese' else hTicker
    xvnoise = math.abs(iSource - iSource[1])
    nfastend = 2 / (Fastend + 1)
    nslowend = 2 / (Slowend + 1)
    nsignal = math.abs(iSource - iSource[Length])
    nnoise = math.sum(xvnoise, Length)
    nefratio = nsignal / nnoise if nnoise != 0 else 0
    nsmooth = math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)
    def nAMA():
        nAMA__00000016__: Series[float] = 0.0
        nAMA__00000016__ = nz(nAMA__00000016__[1]) + nsmooth * (iSource - nz(nAMA__00000016__[1]))
        return nAMA__00000016__

    ha_t = ticker.heikinashi(syminfo.tickerid)
    ha_close = request.security(vTicker, timeframe.period, inline_series(nAMA(), iShiftNRP))
    mha_close = request.security(vTicker, iResolution, hlc3[iShiftNRP])
    fma = ta.ema(mha_close, iPeriodFMA)
    sma = ta.ema(ha_close, iPeriodSMA)
    golong = ta.crossover(fma, sma)
    goshort = ta.crossunder(fma, sma)
    plot(fma, title='MA', color=color.new(color.black, 0), linewidth=2, style=plot.style_line)
    plot(sma, title='SMA', color=color.new(color.red, 0), linewidth=2, style=plot.style_line)
    if golong:
        strategy.entry('Buy', strategy.long)
    if goshort:
        strategy.entry('Sell', strategy.short)
    BGLightGreen: Color = color.new('#00FF00')
    BGLightRed: Color = color.new('#FF0000')
    bgcolor(BGLightGreen if fma >= sma else BGLightRed)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
