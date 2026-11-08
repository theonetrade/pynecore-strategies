"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, bar_index, close, color, high, input, label, low, math, na, nz,
    plot, script, string, ta
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Momentum-based ZigZag', overlay=True, na_bool=True)
def main(
    color_zigzag_lines=input(True, title='Color ZigZag lines to show force direction'),
    momentum_select=input.string(title='Select Momentum Indicator:', defval='QQE', options=('MACD', 'MovingAverage', 'QQE')),
    fast_length=input.int(title='Fast Length', defval=12, group='if MACD Selected', inline='macd'),
    slow_length=input.int(title='Slow Length', defval=26, group='if MACD Selected', inline='macd'),
    src: Series[float] = input.source(title='Source', defval=close, group='if MACD Selected', inline='macd'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group='if MACD Selected', inline='macd'),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA'), group='if MACD Selected', inline='macd'),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA'), group='if MACD Selected', inline='macd'),
    smoothing_type=input.string(title='Average type', defval='SMA', options=('EMA', 'SMA', 'WMA', 'VWMA', 'HMA', 'RMA', 'DEMA'), inline='movingaverage', group='if Moving Average selected'),
    ma_length=input.int(20, title='Length', inline='movingaverage', group='if Moving Average selected'),
    RSI_Period=input.int(14, title='RSI Length', inline='qqe', group='if QQE selected'),
    qqeslow=input.float(4.238, title='QQE Factor', inline='qqe', group='if QQE selected'),
    SFslow=input.int(5, title='RSI Smoothing', inline='qqe', group='if QQE selected'),
    ThreshHold=input.int(10, title='Thresh-hold', inline='qqe', group='if QQE selected'),
    TakeProfitLevel=input(200)
):
    momentum_direction: PersistentSeries[int] = 0
    def zigzag(_momentum_direction):
        zz_goingup: Series = _momentum_direction == 1
        zz_goingdown: Series = _momentum_direction == -1
        zz_peak: PersistentSeries[float] = na(float)
        zz_bottom: PersistentSeries[float] = na(float)
        zz_peak = high if high > zz_peak[1] and zz_goingup or (zz_goingdown[1] and zz_goingup) else nz(zz_peak[1])
        zz_bottom = low if low < zz_bottom[1] and zz_goingdown or (zz_goingup[1] and zz_goingdown) else nz(zz_bottom[1])
        zigzag__00000010__ = zz_bottom[1] if zz_goingup and zz_goingdown[1] else zz_peak[1] if zz_goingup[1] and zz_goingdown else na
        return zigzag__00000010__

    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    macdUP = ta.crossover(macd, signal)
    macdDOWN = ta.crossunder(macd, signal)
    def moving_average(_series, _length, _smoothing):
        return ta.ema(_series, _length) if _smoothing == 'EMA' else ta.sma(_series, _length) if _smoothing == 'SMA' else ta.wma(_series, _length) if _smoothing == 'WMA' else ta.vwma(_series, _length) if _smoothing == 'VWMA' else ta.hma(_series, _length) if _smoothing == 'HMA' else ta.rma(_series, _length) if _smoothing == 'RMA' else 2 * ta.ema(_series, _length) - ta.ema(ta.ema(_series, _length), _length) if _smoothing == 'DEMA' else ta.ema(_series, _length)

    movingaverage: Series = moving_average(close, ma_length, smoothing_type)
    maUP = movingaverage > movingaverage[1] and movingaverage[2] > movingaverage[1]
    maDOWN = movingaverage < movingaverage[1] and movingaverage[2] < movingaverage[1]
    rsi_currenttf = ta.rsi(close, RSI_Period)
    def qqenew(_qqefactor, _smoothingfactor, _rsi, _threshold, _RSI_Period):
        RSI_Period = _RSI_Period
        SF = _smoothingfactor
        QQE = _qqefactor
        ThreshHold = _threshold
        Wilders_Period = RSI_Period * 2 - 1
        Rsi = _rsi
        RsiMa: Series = ta.ema(Rsi, SF)
        AtrRsi = math.abs(RsiMa[1] - RsiMa)
        MaAtrRsi = ta.ema(AtrRsi, Wilders_Period)
        dar = ta.ema(MaAtrRsi, Wilders_Period) * QQE
        longband: Series[float] = 0.0
        shortband: Series[float] = 0.0
        trend: Series[int] = 0
        DeltaFastAtrRsi = dar
        RSIndex: Series = RsiMa
        newshortband = RSIndex + DeltaFastAtrRsi
        newlongband = RSIndex - DeltaFastAtrRsi
        longband = math.max(longband[1], newlongband) if RSIndex[1] > longband[1] and RSIndex > longband[1] else newlongband
        shortband = math.min(shortband[1], newshortband) if RSIndex[1] < shortband[1] and RSIndex < shortband[1] else newshortband
        QQExlong: Series[int] = 0
        QQExlong = nz(QQExlong[1])
        QQExshort: Series[int] = 0
        QQExshort = nz(QQExshort[1])
        qqe_goingup: Series = ta.barssince(QQExlong == 1) < ta.barssince(QQExshort == 1)
        qqe_goingdown: Series = ta.barssince(QQExlong == 1) > ta.barssince(QQExshort == 1)
        last_qqe_high: PersistentSeries[float] = high
        last_qqe_low: PersistentSeries[float] = low
        last_qqe_high = high if high > last_qqe_high[1] and qqe_goingup or (qqe_goingdown[1] and qqe_goingup) else nz(last_qqe_high[1])
        last_qqe_low = low if low < last_qqe_low[1] and qqe_goingdown or (qqe_goingup[1] and qqe_goingdown) else nz(last_qqe_low[1])
        crossover_1 = ta.crossover(high, last_qqe_high)
        trend = 1 if ta.crossover(RSIndex, shortband[1]) or crossover_1 else -1 if ta.crossunder(RSIndex, longband[1]) or ta.crossunder(low, last_qqe_low) else nz(trend[1], 1)
        FastAtrRsiTL: Series = longband if trend == 1 else shortband
        QQExlong = QQExlong + 1 if trend == 1 and trend[1] == -1 else 0
        QQExshort = QQExshort + 1 if trend == -1 and trend[1] == 1 else 0
        qqeLong = FastAtrRsiTL[1] - 50 if QQExlong == 1 else na
        qqeShort = FastAtrRsiTL[1] - 50 if QQExshort == 1 else na
        qqenew__00000063__ = 1 if qqeLong else -1 if qqeShort else na
        return qqenew__00000063__

    qqeUP = qqenew(qqeslow, SFslow, rsi_currenttf, ThreshHold, RSI_Period) == 1
    qqeDOWN = qqenew(qqeslow, SFslow, rsi_currenttf, ThreshHold, RSI_Period) == -1
    momentumUP = macdUP if momentum_select == 'MACD' else maUP if momentum_select == 'MovingAverage' else qqeUP if momentum_select == 'QQE' else qqeUP
    momentumDOWN = macdDOWN if momentum_select == 'MACD' else maDOWN if momentum_select == 'MovingAverage' else qqeDOWN if momentum_select == 'QQE' else qqeDOWN
    momentum_direction = 1 if momentumUP else -1 if momentumDOWN else nz(momentum_direction[1])
    rsi5 = ta.rsi(close, 5)
    ob: int = 80
    os: int = 20
    barssince_momentumUP = ta.barssince(momentumUP)
    barssince_momentumDOWN = ta.barssince(momentumDOWN)
    barssince_1 = ta.barssince(rsi5 > ob)
    momentum_DOWN_was_force_up = momentumDOWN and inline_series(barssince_momentumUP >= barssince_1, 1)
    barssince_2 = ta.barssince(rsi5 < os)
    momentum_UP_was_force_down = momentumUP and inline_series(barssince_momentumDOWN >= barssince_2, 1)
    zzcolor_rsi5 = color.lime if momentum_DOWN_was_force_up else color.red if momentum_UP_was_force_down else color.black
    ZigZag = zigzag(momentum_direction)
    plot(ZigZag, linewidth=5, color=zzcolor_rsi5 if color_zigzag_lines else color.black, title='ZIGZAG', style=plot.style_line)
    GoShort = momentumDOWN and (not momentum_DOWN_was_force_up)
    GoLong = momentumUP and (not momentum_UP_was_force_down)
    if GoShort:
        label.new(bar_index, ZigZag, style=label.style_label_down, color=color.red, text=string.tostring('SHORT\n\npivot high: \n' + string.tostring(ZigZag)))
    if GoLong:
        label.new(bar_index, ZigZag, style=label.style_label_up, color=color.lime, text=string.tostring('LONG\n\npivot low: \n' + string.tostring(ZigZag)))
    stoploss_long: Persistent[float] = low
    stoploss_short: Persistent[float] = high
    pl = ta.valuewhen(momentumUP, ZigZag, 0)
    ph = ta.valuewhen(momentumDOWN, ZigZag, 0)
    if GoLong:
        stoploss_long = low if low < pl else pl
    if GoShort:
        stoploss_short = high if high > ph else ph
    if GoLong:
        alertsyntax_golong = 'long slprice=' + string.tostring(stoploss_long) + ' tp=' + string.tostring(TakeProfitLevel)
        alert(message=alertsyntax_golong, freq=alert.freq_once_per_bar_close)
    if GoShort:
        alertsyntax_goshort = 'short slprice=' + string.tostring(stoploss_short) + ' tp=' + string.tostring(TakeProfitLevel)
        alert(message=alertsyntax_goshort, freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)