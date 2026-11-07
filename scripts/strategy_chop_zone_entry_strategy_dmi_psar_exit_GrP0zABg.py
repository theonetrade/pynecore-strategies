"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barcolor, bgcolor, close, color, fill, fixnan, high, hline, input,
    location, low, math, na, nz, plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Color, Persistent, Series


@script.strategy('CHOP Zone Entry Strategy + DMI/PSAR Exit', shorttitle='CHOP Zone Strategy', default_qty_value=1, overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    showChopAs=input.string(title='Show Chop Index as', defval='Colored Line (PSAR)', options=('Line', 'Colored Line (MOM)', 'Colored Line (PSAR)', 'Columns')),
    lookbackPeriod=input.int(14, title='Lookback Period', minval=1),
    smoothLength=input.int(4, title='Smooth Length', minval=1),
    offset=input.int(0, 'Offset', minval=-500, maxval=500),
    tradeType=input.string(title='Strategy Direction', defval='Follow Trend', options=('Short Only', 'Long Only', 'Both', 'Follow Trend')),
    sensitivity=input.int(title='Alert Sensitivity', defval=1, minval=1, maxval=10),
    colorBg=input(True, title='Color Background to CHOP State'),
    colorBars=input(True, title='Color Candles to CHOP State'),
    enableDMI=input(True, title='════ Enable Directional Movement Index ════'),
    adxLen=input(14, title='ADX Smoothing'),
    diLen=input(14, title='DI Length'),
    adxKeyLevel=input.int(25, title='Key Level for ADX', minval=1, maxval=100),
    enablePSAR=input(True, title='════ Enable Parabolic Stop and Reverse ════'),
    psarStart=input.float(defval=0.015, title='Start', step=0.015, minval=0),
    psarIncr=input.float(defval=0.001, title='Increment', step=0.001, minval=0),
    psarMax=input.float(defval=0.2, title='Max Value', step=0.2, minval=0)
):
    sumAtrOverLookback = math.sum(ta.atr(1), lookbackPeriod)
    maxHi = ta.highest(high if high >= close[1] else close[1], lookbackPeriod)
    minLo = ta.lowest(low if low <= close[1] else close[1], lookbackPeriod)
    chopIndex = 100 * math.log10(sumAtrOverLookback / (maxHi - minLo)) / math.log10(lookbackPeriod)
    chopIndex = ta.sma(chopIndex, smoothLength)
    condChopIndex38minus: Series = True if chopIndex <= 38.2 and close[1] > close else False
    condChopIndex38to45 = True if chopIndex >= 38.2 and chopIndex < 45 else False
    condChopIndex45to55 = True if chopIndex >= 45 and chopIndex < 55 else False
    condChopIndex55to61 = True if chopIndex >= 55 and chopIndex < 61.8 else False
    condChopIndex61plus: Series = True if chopIndex >= 61.8 and close[1] < close else False
    condChopIndex30minus = True if chopIndex <= 30 and close[1] > close else False
    condChopIndex30to38 = True if chopIndex > 30 and chopIndex < 38.2 else False
    condChopIndex61to70 = True if chopIndex >= 61.8 and chopIndex < 70 else False
    condChopIndex70plus = True if chopIndex >= 70 and close[1] < close else False
    val: Series = ta.linreg(close - math.avg(math.avg(ta.highest(high, lookbackPeriod), ta.lowest(low, lookbackPeriod)), ta.ema(close, lookbackPeriod)), lookbackPeriod, 0)
    curr_momUpTrend = val > nz(val[1])
    curr_momDnTrend = val < nz(val[1])
    momentumLineColor = color.green if curr_momUpTrend else color.maroon if curr_momDnTrend else na
    psar = ta.sar(psarStart, psarIncr, psarMax)
    psarTrendState: Series = 'up' if psar < close else 'dn'
    psarLineColor = color.green if psarTrendState == 'up' else color.maroon if psarTrendState == 'dn' else na
    hli1 = hline(38.2 if showChopAs != 'Columns' else na, linestyle=hline.style_dotted, editable=False)
    hli2 = hline(61.8 if showChopAs != 'Columns' else na, linestyle=hline.style_dotted, editable=False)
    fill(hli1, hli2, color=color.new(color.yellow, 95), editable=False)
    lineColor = psarLineColor if showChopAs == 'Colored Line (PSAR)' else momentumLineColor if showChopAs == 'Colored Line (MOM)' else color.gray
    plot(chopIndex if showChopAs != 'Columns' else na, style=plot.style_linebr, linewidth=2, color=lineColor, offset=offset, editable=False)
    candleColor: Persistent[Color] = na(Color)
    candleColor = color.new('#800080') if condChopIndex38minus else candleColor
    candleColor = color.yellow if condChopIndex38to45 else candleColor
    candleColor = color.new('#000000') if condChopIndex45to55 else candleColor
    candleColor = color.yellow if condChopIndex55to61 else candleColor
    candleColor = color.new('#0000FF') if condChopIndex61plus else candleColor
    barcolor(candleColor if colorBars else na, editable=False)
    chopZoneColor: Persistent[Color] = na(Color)
    chopZoneColor = color.new('#800080') if condChopIndex30minus else chopZoneColor
    chopZoneColor = color.purple if condChopIndex30to38 else chopZoneColor
    chopZoneColor = color.yellow if condChopIndex38to45 else chopZoneColor
    chopZoneColor = color.new('#000000') if condChopIndex45to55 else chopZoneColor
    chopZoneColor = color.yellow if condChopIndex55to61 else chopZoneColor
    chopZoneColor = color.blue if condChopIndex61to70 else chopZoneColor
    chopZoneColor = color.new('#0000FF') if condChopIndex70plus else chopZoneColor
    plot(1 if showChopAs == 'Columns' else na, color=chopZoneColor, style=plot.style_columns, editable=False)
    chopZoneColor = chopZoneColor if colorBg and showChopAs != 'Columns' else na
    bgcolor(color=chopZoneColor, editable=False)
    def dirmov(diLen):
        upMove = ta.change(high)
        downMove = -ta.change(low)
        plusDI = upMove if upMove > downMove and upMove > 0 else 0
        minusDI = downMove if downMove > upMove and downMove > 0 else 0
        trueRange = ta.ema(ta.tr, diLen)
        plusDI = fixnan(100 * ta.ema(plusDI, diLen) / trueRange)
        minusDI = fixnan(100 * ta.ema(minusDI, diLen) / trueRange)
        return (plusDI, minusDI)

    def adx(diLen, adxLen):
        plusDI, minusDI = dirmov(diLen)
        tmp = math.abs((plusDI - minusDI) / (plusDI + minusDI))
        adx__00000040__ = fixnan(100 * ta.ema(tmp, adxLen))
        return (adx__00000040__, plusDI, minusDI)

    adxSignal, plusDI, minusDI = adx(diLen, adxLen)
    goLong = condChopIndex61plus and (not condChopIndex61plus[sensitivity]) and (adxSignal > adxKeyLevel if enableDMI else True)
    goShort = condChopIndex38minus and (not condChopIndex38minus[sensitivity]) and (adxSignal > adxKeyLevel if enableDMI else True)
    if sensitivity != 1 and (goLong or goShort):
        for i in pine_range(1, sensitivity - 1, 1):
            if condChopIndex61plus[i] != condChopIndex61plus:
                goLong = False
            if condChopIndex38minus[i] != condChopIndex38minus:
                goShort = False
    if tradeType == 'Follow Trend':
        goLong = (goLong if curr_momUpTrend else na) if showChopAs == 'Colored Line (Momentum)' else goLong if psarTrendState == 'up' else False
        goShort = (goShort if curr_momDnTrend else na) if showChopAs == 'Colored Line (Momentum)' else goShort if psarTrendState == 'dn' else False
    activeLong: Persistent[bool] = False
    activeShort: Persistent[bool] = False
    dmiCloseLong = adxSignal < adxKeyLevel and minusDI > plusDI if enableDMI else False
    dmiCloseShort = adxSignal < adxKeyLevel and plusDI > minusDI if enableDMI else False
    psarCloseLong = psarTrendState == 'dn' and psarTrendState[1] == 'up' if enablePSAR else False
    psarCloseShort = psarTrendState == 'up' and psarTrendState[1] == 'dn' if enablePSAR else False
    chopCloseLong = False if enablePSAR or enableDMI else chopIndex < 38.2
    chopCloseShort = False if enablePSAR or enableDMI else chopIndex > 61.8
    closeLongState = activeLong and (psarCloseLong or dmiCloseLong or chopCloseLong or goShort)
    closeShortState = activeShort and (psarCloseShort or dmiCloseShort or chopCloseShort or goLong)
    goReverse = True if closeLongState and goShort or (closeShortState and goLong) else False
    goClose = True if not goReverse and (closeLongState or closeShortState) else False
    longSelected = True if tradeType == 'Both' or tradeType == 'Follow Trend' else True if tradeType == 'Long Only' else False
    shortSelected = True if tradeType == 'Both' or tradeType == 'Follow Trend' else True if tradeType == 'Short Only' else False
    reverseAllowed = tradeType == 'Both' or tradeType == 'Follow Trend'
    plotSeries = chopIndex if showChopAs != 'Columns' else 0
    plotshape(plotSeries if not activeLong and longSelected and goLong and (not goReverse) else na, style=shape.circle, location=location.absolute, size=size.tiny, color=color.new(color.lime, 0), text='Long', title='Long')
    plotshape(plotSeries if not activeShort and shortSelected and goShort and (not goReverse) else na, style=shape.circle, location=location.absolute, size=size.tiny, color=color.new(color.red, 0), text='Short', title='Short')
    active = activeLong or activeShort
    plotshape(plotSeries if active and goClose else na, style=shape.xcross, location=location.absolute, size=size.tiny, color=color.new(color.olive, 0), text='Close', title='Close')
    plotshape(plotSeries if active and reverseAllowed and goReverse else na, style=shape.diamond, location=location.absolute, size=size.tiny, color=color.new(color.blue, 0), text='Reverse', title='Reverse')
    if not activeLong and longSelected and goLong and (not goReverse):
        strategy.entry('Long', strategy.long, alert_message='Buy {{ticker}} from Chop Zone Strategy')
        activeLong = True
    if not activeShort and shortSelected and goShort and (not goReverse):
        strategy.entry('Short', strategy.short, alert_message='Sell {{ticker}} from Chop Zone Strategy')
        activeShort = True
    if active and reverseAllowed:
        if goLong and goReverse:
            strategy.entry('Long', strategy.long, alert_message='Reverse {{ticker}} from Chop Zone Strategy')
            activeLong = True
            activeShort = False
        if goShort and goReverse:
            strategy.entry('Short', strategy.short, alert_message='Reverse {{ticker}} from Chop Zone Strategy')
            activeShort = True
            activeLong = False
    if active and goClose:
        strategy.close('Long', alert_message='Close {{ticker}} from Chop Zone Strategy')
    if active and goClose:
        strategy.close('Short', alert_message='Close {{ticker}} from Chop Zone Strategy')
    if goClose:
        activeLong = False
        activeShort = False


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
