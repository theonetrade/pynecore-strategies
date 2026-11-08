"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, barcolor, barstate, bgcolor, close, color, fill, hline,
    input, na, plot, request, runtime, script, syminfo, ta, volume
)
from pynecore.types import Persistent, Series
import lib.TradingView.LibraryCOT.v3 as cot


@script.indicator('Open Interest Stochastic Money Flow Index')
def main(
    lights=input.string(title='Barcolor I / 0 ? ', options=('ON', 'OFF'), defval='OFF'),
    adaptive=input.string(title='Market Type ', options=('FUTURES', 'OTHERS'), defval='FUTURES'),
    t_mfi=input(14, title='MFI Period'),
    OverSold=input(20, title='Oversold'),
    OverBought=input(80, title='Overbought')
):
    src = close
    reverse: bool = False

    Root_Symbol: Persistent[str] = syminfo.root
    CFTC_Code_fixed: Persistent[str] = cot.convertRootToCOTCode('Auto')
    if Root_Symbol == 'HG':
        CFTC_Code_fixed = "085692"
    elif Root_Symbol == 'LBR':
        CFTC_Code_fixed = "058644"

    def dataRequest(metricName, direction):
        tickerId = cot.COTTickerid('Legacy', CFTC_Code_fixed, False, metricName, direction, 'All')
        value = request.security(tickerId, '1D', close, ignore_invalid_symbol=True)
        if barstate.islastconfirmedhistory and na(value):
            runtime.error('Could not find relevant COT data based on the current symbol.')
        return value

    def getOpenInterest():
        return dataRequest('Open Interest', 'No direction')

    openInterest = getOpenInterest()

    _oi_futures = openInterest

    _vol_others = volume

    _switchable: float = na(float)

    if adaptive == 'FUTURES':
        _switchable = _oi_futures

    if adaptive == 'OTHERS':
        _switchable = volume

    def f_ema(_src, _length):
        _length_adjusted = 1 if _length < 1 else _length
        _multiplier = 2 / (_length_adjusted + 1)
        _return: Series[float] = 0.0
        _return = _src if na(_return[1]) else (_src - _return[1]) * _multiplier + _return[1]
        return _return

    def f_sum(_src: Series, _length):
        _output: float = 0.0

        _length_adjusted = 1 if _length < 1 else _length

        __block_result__ = na
        for i in pine_range(0, _length_adjusted - 1, 1):
            _output = _output + _src[i]
            __block_result__ = _output
        return __block_result__

    def f_highest(_src: Series, _length):
        _adjusted_length = 1 if _length < 1 else _length
        _value = _src
        for _i in pine_range(0, _adjusted_length - 1, 1):
            _value = _src[_i] if _src[_i] >= _value else _value
        _return = _value
        return _return

    def f_lowest(_src: Series, _length):
        _adjusted_length = 1 if _length < 1 else _length
        _value = _src
        for _i in pine_range(0, _adjusted_length - 1, 1):
            _value = _src[_i] if _src[_i] <= _value else _value
        _return = _value
        return _return

    zero: int = 0
    hundred: int = 100

    limit: int = 50

    upper_s = f_sum(_switchable * (0 if ta.change(src) <= 0 else src), t_mfi)
    lower_s = f_sum(_switchable * (0 if ta.change(src) >= 0 else src), t_mfi)

    _mfi = 100.0 - 100.0 / (1.0 + upper_s / lower_s)

    lengthMFI: int = 14
    lengthStoch: int = 14

    smoothK = cast_int(lengthMFI / 3)
    smoothD = cast_int(lengthStoch / 3)

    def f_stoch(_src, _length):
        return 100 * (_src - f_lowest(f_lowest(_src, 1), _length)) / (f_highest(f_highest(_src, 1), _length) - f_lowest(f_lowest(_src, 1), _length))

    k3 = f_ema(f_stoch(_mfi, lengthStoch), smoothK)
    d = f_ema(k3, smoothD)

    pos_moment = ta.crossover(k3, d)
    neg_moment = ta.crossunder(k3, d)

    col_bg = color.teal if pos_moment else color.maroon if neg_moment else na

    h1 = hline(OverSold, color=color.new('#C0C0C0'), title='Oversold Level')
    h2 = hline(OverBought, color=color.new('#C0C0C0'), title='Overbought Level')
    plot(k3, color=color.new(color.new('#0070FF'), 0), title='K-line', linewidth=1)
    plot(d, color=color.new(color.new('#FF8C00'), 0), title='D-line', linewidth=1)
    fill(h1, h2, color=color.new(color.new('#66023C'), 90), title='Border')
    bgcolor(col_bg, title='Background Color')
    plot(zero if pos_moment else na, style=plot.style_cross, color=color.new(color.green, 0), linewidth=3, title='Crossover')
    plot(zero if neg_moment else na, style=plot.style_cross, color=color.new(color.red, 0), linewidth=3, title='Crossunder')

    pos = 1 if k3 > d else -1
    iff_1 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_1

    _lights: float = 0.0
    if lights == 'ON':
        _lights = 1.0

    if lights == 'OFF':
        _lights = -1.0

    bcolor_on = _lights == 1.0
    bcolor_off = _lights == -1.0

    barcolor(color.red if possig == -1 and bcolor_on else color.green if possig == 1 and bcolor_on else na)

    alertcondition(possig == 1, title='Buy Signal', message='Buy Signal ')
    alertcondition(possig == -1, title='Sell Signal', message='Sell Signal ')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
