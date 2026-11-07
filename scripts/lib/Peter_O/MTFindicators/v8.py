"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.series import inline_series
from pynecore.lib import close, color, fixnan, high, input, low, math, na, nz, plot, script, ta
from pynecore.types import Series
from typing import Protocol, Any


__all__ = ['adx_mtf', 'bollingerbands_mtf', 'keltnerchannels_mtf', 'macd_mtf', 'moving_average_mtf', 'rsi_mtf', 'stoch_mtf']


class _ProtocolAdxMtf(Protocol):
    def __call__(self, _mtf: int, _lenadx: int, _lensig: int) -> Any: ...


class _ProtocolRsiMtf(Protocol):
    def __call__(self, _mtf: int, _source: float, _len: int) -> Any: ...


class _ProtocolStochMtf(Protocol):
    def __call__(self, _mtf: int, _periodK: int, _smoothK: int, _periodD: int) -> Any: ...


class _ProtocolMovingAverageMtf(Protocol):
    def __call__(self, _mtf: int, _smoothing: str, _series: float, _length: int) -> Any: ...


class _ProtocolBollingerbandsMtf(Protocol):
    def __call__(self, _mtf: int, _length: int, _src: float, _mult: float) -> Any: ...


class _ProtocolKeltnerchannelsMtf(Protocol):
    def __call__(self, _mtf: int, _source: float, _keltnerlength: int, _atr4keltnerlength: int, _keltnermult: float) -> Any: ...


class _ProtocolMacdMtf(Protocol):
    def __call__(self, _mtf: int, _source: float, _fast_length: int, _slow_length: int, _signal_length: int) -> Any: ...


adx_mtf: _ProtocolAdxMtf = Exported()
rsi_mtf: _ProtocolRsiMtf = Exported()
stoch_mtf: _ProtocolStochMtf = Exported()
moving_average_mtf: _ProtocolMovingAverageMtf = Exported()
bollingerbands_mtf: _ProtocolBollingerbandsMtf = Exported()
keltnerchannels_mtf: _ProtocolKeltnerchannelsMtf = Exported()
macd_mtf: _ProtocolMacdMtf = Exported()


@script.library(title='MTFindicators', overlay=False)
def main(
    mtf4adx=input(15, title='MTF x', inline='adx', group='ADX MTF'),
    lenadx=input.int(14, minval=1, title='DI Length', inline='adx', group='ADX MTF'),
    lensig=input.int(14, title='Smoothing', minval=1, maxval=50, inline='adx', group='ADX MTF'),
    mtf4rsi=input(15, title='MTF x', inline='rsi', group='RSI MTF'),
    sourcersi: Series[float] = input.source(close, title='Source', inline='rsi', group='RSI MTF'),
    lenrsi=input(14, title='lookback', inline='rsi', group='RSI MTF'),
    mtf4stoch=input(15, title='MTF x', inline='stoch', group='Stochastic MTF'),
    periodK=input.int(14, title='%K Length', minval=1, inline='stoch', group='Stochastic MTF'),
    smoothK=input.int(3, title='%K Smoothing', minval=1, inline='stoch', group='Stochastic MTF'),
    periodD=input.int(3, title='%D Smoothing', minval=1, inline='stoch', group='Stochastic MTF'),
    mtf4ma=input(15, title='MTF x', inline='ma', group='Moving Average'),
    ma_type=input.string(title='Type', defval='EMA', options=('EMA', 'SMA', 'WMA', 'VWMA', 'HMA', 'RMA', 'DEMA'), inline='ma', group='Moving Average'),
    ma_series: Series[float] = input.source(close, title='Source', inline='ma', group='Moving Average'),
    ma_length=input.int(9, title='Length', inline='ma', group='Moving Average'),
    mtf4bb=input.int(5, title='MTF x', inline='bbands', group='Bollinger Bands MTF'),
    bblength=input.int(20, minval=1, inline='bbands', group='Bollinger Bands MTF'),
    bbsrc: Series[float] = input(close, title='Source', inline='bbands', group='Bollinger Bands MTF'),
    bbmult=input.float(2.0, minval=0.001, maxval=50, title='StdDev', inline='bbands', group='Bollinger Bands MTF'),
    mtf4keltner=input.int(5, title='MTF x', inline='keltner', group='Keltner Channel MTF'),
    keltnersource: Series[float] = input.source(close, title='Source', inline='keltner', group='Keltner Channel MTF'),
    keltnerlength=input.int(13, minval=1, title='EMA Length', inline='keltner', group='Keltner Channel MTF'),
    keltneratrlength=input.int(13, minval=1, title='ATR Length', inline='keltner', group='Keltner Channel MTF'),
    keltnermult=input.float(1.5, minval=0.01, maxval=50, title='Keltner Multiplier', inline='keltner', group='Keltner Channel MTF'),
    mtf4macd=input.int(5, title='MTF x', inline='macd', group='MACD MTF'),
    macd_source: Series[float] = input.source(close, title='Source', inline='macd', group='MACD MTF'),
    macd_fast_length=input.int(12, title='Fast Length', inline='macd', group='MACD MTF'),
    macd_slow_length=input.int(26, title='Slow Length', inline='macd', group='MACD MTF'),
    macd_signal_length=input.int(9, title='Signal Smoothing', minval=1, maxval=50, inline='macd', group='MACD MTF')
):
    @export
    def adx_mtf(_mtf: int, _lenadx: int, _lensig: int):
        up_mtf = ta.highest(high, _mtf) - inline_series(ta.highest(high, _mtf), _mtf)
        down_mtf = -(ta.lowest(low, _mtf) - inline_series(ta.lowest(low, _mtf), _mtf))
        plusDM_mtf = na if na(up_mtf) else up_mtf if up_mtf > down_mtf and up_mtf > 0 else 0
        minusDM_mtf = na if na(down_mtf) else down_mtf if down_mtf > up_mtf and down_mtf > 0 else 0
        tr_mtf = math.max(math.max(high - low, math.abs(high - nz(close[_mtf]))), math.abs(low - nz(close[_mtf])))
        trur_mtf = ta.rma(tr_mtf, _lenadx * _mtf)
        plus_mtf = fixnan(100 * ta.rma(plusDM_mtf, _lenadx * _mtf) / trur_mtf)
        minus_mtf = fixnan(100 * ta.rma(minusDM_mtf, _lenadx * _mtf) / trur_mtf)
        sum_mtf = plus_mtf + minus_mtf
        adx_mtf__00000019__ = 100 * ta.rma(math.abs(plus_mtf - minus_mtf) / (1 if sum_mtf == 0 else sum_mtf), _lensig * _mtf)
        return (adx_mtf__00000019__, plus_mtf, minus_mtf)

    @export
    def rsi_mtf(_mtf: int, _source: Series[float], _len: int):
        change_mtf = _source - _source[_mtf]
        up_mtf = ta.rma(math.max(change_mtf, 0), _len * _mtf)
        down_mtf = ta.rma(-math.min(change_mtf, 0), _len * _mtf)
        rsi_mtf__0000001f__ = 100 if down_mtf == 0 else 0 if up_mtf == 0 else 100 - 100 / (1 + up_mtf / down_mtf)
        return rsi_mtf__0000001f__

    @export
    def stoch_mtf(_mtf: int, _periodK: int, _smoothK: int, _periodD: int):
        stoch_k_mtf = ta.sma(100 * (close - ta.lowest(low, _periodK * _mtf)) / (ta.highest(high, _periodK * _mtf) - ta.lowest(low, _periodK * _mtf)), _smoothK * _mtf)
        stoch_d_mtf = ta.sma(stoch_k_mtf, _periodD * _mtf)
        return (stoch_k_mtf, stoch_d_mtf)

    @export
    def moving_average_mtf(_mtf: int, _smoothing: str, _series: float, _length: int):
        return ta.ema(_series, _length * _mtf) if _smoothing == 'EMA' else ta.sma(_series, _length * _mtf) if _smoothing == 'SMA' else ta.wma(_series, _length * _mtf) if _smoothing == 'WMA' else ta.vwma(_series, _length * _mtf) if _smoothing == 'VWMA' else ta.hma(_series, _length * _mtf) if _smoothing == 'HMA' else ta.rma(_series, _length * _mtf) if _smoothing == 'RMA' else 2 * ta.ema(_series, _length * _mtf) - ta.ema(ta.ema(_series, _length * _mtf), _length * _mtf) if _smoothing == 'DEMA' else ta.ema(_series, _length * _mtf)

    @export
    def bollingerbands_mtf(_mtf: int, _length: int, _src: float, _mult: float):
        basis = ta.sma(_src, _length * _mtf)
        dev = _mult * ta.stdev(_src, _length * _mtf)
        upper = basis + dev
        lower = basis - dev
        return (basis, upper, lower)

    @export
    def keltnerchannels_mtf(_mtf: int, _source: float, _keltnerlength: int, _atr4keltnerlength: int, _keltnermult: float):
        ma = ta.ema(_source, _keltnerlength * _mtf)
        range_ = ta.tr
        rangema = ta.ema(range_, _atr4keltnerlength * _mtf)
        upper = ma + rangema * _keltnermult
        lower = ma - rangema * _keltnermult
        return (upper, lower)

    @export
    def macd_mtf(_mtf: int, _source: float, _fast_length: int, _slow_length: int, _signal_length: int):
        fast_ma = ta.ema(_source, _fast_length * _mtf)
        slow_ma = ta.ema(_source, _slow_length * _mtf)
        macd = fast_ma - slow_ma
        signal = ta.ema(macd, _signal_length * _mtf)
        hist = macd - signal
        return (macd, signal, hist)

    adxmtf, plusmtf, minusmtf = adx_mtf(mtf4adx, lenadx, lensig)
    rsimtf = rsi_mtf(mtf4rsi, sourcersi, lenrsi)
    stochmtf_k, stochmtf_d = stoch_mtf(mtf4stoch, periodK, smoothK, periodD)
    mamtf = moving_average_mtf(mtf4ma, ma_type, ma_series, ma_length)
    bbbasismtf, bbuppermtf, bblowermtf = bollingerbands_mtf(mtf4bb, bblength, bbsrc, bbmult)
    upper, lower = keltnerchannels_mtf(mtf4keltner, keltnersource, keltnerlength, keltneratrlength, keltnermult)
    macd, signal, hist = macd_mtf(mtf4macd, macd_source, macd_fast_length, macd_slow_length, macd_signal_length)
    plot(rsimtf, color=color.new(color.orange, 0), title='RSI MTF', linewidth=2)
    plot(adxmtf, color=color.new(color.black, 0), title='ADX MTF', linewidth=2)
    plot(plusmtf, color=color.new(color.lime, 0), title='DI Plus MTF')
    plot(minusmtf, color=color.new(color.red, 0), title='DI Minus MTF')
    plot(stochmtf_k, color=color.new('#2962FF'), title='Stochastic %K MTF')
    plot(stochmtf_d, color=color.new('#FF6D00'), title='Stochastic %D MTF')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
