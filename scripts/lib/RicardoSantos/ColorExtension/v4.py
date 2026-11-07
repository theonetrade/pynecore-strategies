"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import color, math, na, runtime, script, string
from pynecore.types import Color
from typing import Protocol, Any


__all__ = ['analog', 'color_to_hsl', 'complement', 'darken', 'desaturate', 'hsl', 'invert', 'is_cool', 'is_high_key', 'lighten', 'mix', 'rgb_to_hsl', 'saturate', 'shift_hue', 'square', 'temperature', 'tetradic', 'triadic']


class _ProtocolHsl(Protocol):
    def __call__(self, hue: float = 0.0, saturation: float = 0.0, lightness: float = 0.0, transparency: float = 0.0) -> Any: ...


class _ProtocolRgbToHsl(Protocol):
    def __call__(self, red: float = 0.0, green: float = 0.0, blue: float = 0.0) -> Any: ...


class _ProtocolColorToHsl(Protocol):
    def __call__(self, base: Color) -> Any: ...


class _ProtocolShiftHue(Protocol):
    def __call__(self, base: Color, angle: float) -> Any: ...


class _ProtocolSaturate(Protocol):
    def __call__(self, base: Color, rate: float = 0.5) -> Any: ...


class _ProtocolDesaturate(Protocol):
    def __call__(self, base: Color, rate: float = 0.5) -> Any: ...


class _ProtocolLighten(Protocol):
    def __call__(self, base: Color, rate: float = 0.5) -> Any: ...


class _ProtocolDarken(Protocol):
    def __call__(self, base: Color, rate: float = 0.5) -> Any: ...


class _ProtocolComplement(Protocol):
    def __call__(self, primary: Color) -> Any: ...


class _ProtocolInvert(Protocol):
    def __call__(self, primary: Color) -> Any: ...


class _ProtocolIsCool(Protocol):
    def __call__(self, base: Color) -> Any: ...


class _ProtocolTemperature(Protocol):
    def __call__(self, base: Color) -> Any: ...


class _ProtocolIsHighKey(Protocol):
    def __call__(self, base: Color) -> Any: ...


class _ProtocolMix(Protocol):
    def __call__(self, base: Color, mix__00000062__: Color, rate: float = 0.5) -> Any: ...


class _ProtocolAnalog(Protocol):
    def __call__(self, primary: Color) -> Any: ...


class _ProtocolTriadic(Protocol):
    def __call__(self, primary: Color) -> Any: ...


class _ProtocolTetradic(Protocol):
    def __call__(self, primary: Color) -> Any: ...


class _ProtocolSquare(Protocol):
    def __call__(self, primary: Color) -> Any: ...


hsl: _ProtocolHsl = Exported()
rgb_to_hsl: _ProtocolRgbToHsl = Exported()
color_to_hsl: _ProtocolColorToHsl = Exported()
shift_hue: _ProtocolShiftHue = Exported()
saturate: _ProtocolSaturate = Exported()
desaturate: _ProtocolDesaturate = Exported()
lighten: _ProtocolLighten = Exported()
darken: _ProtocolDarken = Exported()
complement: _ProtocolComplement = Exported()
invert: _ProtocolInvert = Exported()
is_cool: _ProtocolIsCool = Exported()
temperature: _ProtocolTemperature = Exported()
is_high_key: _ProtocolIsHighKey = Exported()
mix: _ProtocolMix = Exported()
analog: _ProtocolAnalog = Exported()
triadic: _ProtocolTriadic = Exported()
tetradic: _ProtocolTetradic = Exported()
square: _ProtocolSquare = Exported()


@script.library(title='ColorExtension')
def main():
    @export
    def hsl(hue: float = 0.0, saturation: float = 0.0, lightness: float = 0.0, transparency: float = 0.0):
        if hue < 0.0 or hue > 360.0:
            runtime.error(string.format('ColorExtension -> hsl(): "hue" parameter is out of range, expecting 0-360, received: {0}', hue))
        elif saturation < 0.0 or saturation > 100.0:
            runtime.error(string.format('ColorExtension -> hsl(): "saturation" parameter is out of range, expecting 0-100, received: {0}', saturation))
        elif lightness < 0.0 or lightness > 100.0:
            runtime.error(string.format('ColorExtension -> hsl(): "lightness" parameter is out of range, expecting 0-100, received: {0}', lightness))
        elif transparency < 0.0 or transparency > 100.0:
            runtime.error(string.format('ColorExtension -> hsl(): "transparency" parameter is out of range, expecting 0-100, received: {0}', transparency))
        _h_30: float = hue / 30.0
        _l1: float = lightness * 0.01
        _a: float = saturation * math.min(_l1, 1.0 - _l1) * 0.01
        _rk: float = _h_30 % 12.0
        _r: float = 255.0 * (_l1 - _a * math.max(math.min(_rk - 3.0, 9.0 - _rk, 1.0), -1.0))
        _gk: float = (8.0 + _h_30) % 12.0
        _g: float = 255.0 * (_l1 - _a * math.max(math.min(_gk - 3.0, 9.0 - _gk, 1.0), -1.0))
        _bk: float = (4.0 + _h_30) % 12.0
        _b: float = 255.0 * (_l1 - _a * math.max(math.min(_bk - 3.0, 9.0 - _bk, 1.0), -1.0))
        return color.rgb(_r, _g, _b, transparency)

    @export
    def rgb_to_hsl(red: float = 0.0, green: float = 0.0, blue: float = 0.0):
        if 0 > red or red > 255:
            runtime.error(string.format('ColorExtension -> rgb_to_hsl(): "red" parameter is out of range, expecting 0-255, received: {0}', red))
        elif 0 > green or green > 255:
            runtime.error(string.format('ColorExtension -> rgb_to_hsl(): "green" parameter is out of range, expecting 0-255, received: {0}', green))
        elif 0 > blue or blue > 255:
            runtime.error(string.format('ColorExtension -> rgb_to_hsl(): "blue" parameter is out of range, expecting 0-255, received: {0}', blue))
        _r1: float = red / 255.0
        _g1: float = green / 255.0
        _b1: float = blue / 255.0
        _max_color: float = math.max(_r1, _g1, _b1)
        _min_color: float = math.min(_r1, _g1, _b1)
        _diff: float = _max_color - _min_color
        _H: float = 0.0
        _S: float = 0.0
        _L: float = (_max_color + _min_color) / 2.0
        if _max_color != _min_color:
            if _L <= 0.5:
                _S = _diff / (_max_color + _min_color)
            else:
                _S = _diff / (2.0 - _max_color - _min_color)
            __switch_1__ = _max_color
            if __switch_1__ == _r1:
                _H = 60.0 * ((_g1 - _b1) / _diff)
            elif __switch_1__ == _g1:
                _H = 60.0 * (2.0 + (_b1 - _r1) / _diff)
            else:
                _H = 60.0 * (4.0 + (_r1 - _g1) / _diff)
        if _H < 0.0:
            _H = _H + 360.0
        return (_H, _S * 100.0, _L * 100.0)

    @export
    def color_to_hsl(base: Color):
        return rgb_to_hsl(color.r(base), color.g(base), color.b(base))

    @export
    def shift_hue(base: Color, angle: float):
        _h, _s, _l = color_to_hsl(base)
        return hsl((_h + angle) % 360, _s, _l, color.t(base))

    @export
    def saturate(base: Color, rate: float = 0.5):
        if rate > 1.0 or rate < 0.0:
            runtime.error('ColorExtension -> saturate(): "rate" must be between 0.0 and 1.0')
        _h, _s, _l = color_to_hsl(base)
        return hsl(_h, _s + (100 - _s) * rate, _l, color.t(base))

    @export
    def desaturate(base: Color, rate: float = 0.5):
        if rate > 1.0 or rate < 0.0:
            runtime.error('ColorExtension -> saturate(): "rate" must be between 0.0 and 1.0')
        _h, _s, _l = color_to_hsl(base)
        return hsl(_h, _s - _s * rate, _l, color.t(base))

    @export
    def lighten(base: Color, rate: float = 0.5):
        if rate > 1.0 or rate < 0.0:
            runtime.error('ColorExtension -> lighten(): "rate" must be between 0.0 and 1.0')
        _h, _s, _l = color_to_hsl(base)
        return hsl(_h, _s, _l + (100.0 - _l) * rate, color.t(base))

    @export
    def darken(base: Color, rate: float = 0.5):
        if rate > 1.0 or rate < 0.0:
            runtime.error('ColorExtension -> darken(): "rate" must be between 0.0 and 1.0')
        _h, _s, _l = color_to_hsl(base)
        return hsl(_h, _s, _l - _l * rate, color.t(base))

    @export
    def complement(primary: Color):
        return shift_hue(primary, 180.0)

    @export
    def invert(primary: Color):
        _h, _s, _l = color_to_hsl(primary)
        return hsl((360 + _h + 180.0) % 360.0, 100.0 - _l, _s, color.t(primary))

    @export
    def is_cool(base: Color):
        _h, _, _ = color_to_hsl(base)
        return _h > 120.0 and _h < 300.0

    @export
    def temperature(base: Color):
        _r: float = color.r(base)
        _g: float = color.g(base)
        _b: float = color.b(base)
        _n: float = (0.23881 * _r + 0.25499 * _g + -0.58291 * _b) / (0.11109 * _r + -0.85406 * _g + 0.52289 * _b)
        return 449.0 * math.pow(_n, 3.0) + 3525 * math.pow(_n, 2.0) + 6823.3 * _n + 5520.33

    @export
    def is_high_key(base: Color):
        _h, _, _ = color_to_hsl(base)
        return _h > 30.0 and _h < 140.0

    @export
    def mix(base: Color, mix__00000062__: Color, rate: float = 0.5):
        if rate <= 0.0 or rate >= 1.0:
            runtime.error('ColorExtension -> mix(): "rate" must be within 0.0 and 1.0')
        _t0: float = color.t(base)
        _t1: float = color.t(mix__00000062__)
        _h0, _s0, _l0 = color_to_hsl(base)
        _h1, _s1, _l1 = color_to_hsl(mix__00000062__)
        return hsl(_h0 + (_h1 - _h0) * rate, _s0 + (_s1 - _s0) * rate, _l0 + (_l1 - _l0) * rate, _t0 + (_t1 - _t0) * rate)

    @export
    def analog(primary: Color):
        return (shift_hue(primary, -45.0), shift_hue(primary, 45.0))

    @export
    def triadic(primary: Color):
        return (shift_hue(primary, -120.0), shift_hue(primary, 120.0))

    @export
    def tetradic(primary: Color):
        return (shift_hue(primary, 60.0), shift_hue(primary, 180.0), shift_hue(primary, 240.0))

    @export
    def square(primary: Color):
        return (shift_hue(primary, 90.0), shift_hue(primary, 180.0), shift_hue(primary, 270.0))

    def gradient_triangular(value: float = 0.0, mid_point: float = 50.0, min_color: Color = color.black, mid_color: Color = color.white, max_color: Color = color.black):
        _col: Color = na(Color)
        if value <= mid_point:
            _col = color.from_gradient(value, 0.0, mid_point, min_color, mid_color)
        else:
            _col = color.from_gradient(value, mid_point, 100.0, mid_color, max_color)
        return _col


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
