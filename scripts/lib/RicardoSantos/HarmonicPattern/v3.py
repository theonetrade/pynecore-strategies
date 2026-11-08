"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, math, na, runtime, script
from pynecore.types import NA
from typing import Protocol, Any


__all__ = ['extract', 'is2Tap', 'is3Driver', 'is3Tap', 'is4Tap', 'is5o', 'isABCD', 'isBat', 'isButterfly', 'isConTria', 'isCrab', 'isExpTria', 'isGartley', 'isHarmonicTriangle', 'isHnS', 'isShark', 'isWolfe', 'is_inrange', 'line_price_rate', 'line_time_rate']


class _ProtocolLinePriceRate(Protocol):
    def __call__(self, point_c: float, point_b: float, point_a: float) -> Any: ...


class _ProtocolLineTimeRate(Protocol):
    def __call__(self, point_c: float, point_b: float, point_a: float) -> Any: ...


class _ProtocolIsInrange(Protocol):
    def __call__(self, value: float, min: float, max: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsharmonictriangle(Protocol):
    def __call__(self, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIs2tap(Protocol):
    def __call__(self, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIs3tap(Protocol):
    def __call__(self, rate_edc: float, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIs4tap(Protocol):
    def __call__(self, rate_gfe: float, rate_edc: float, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsabcd(Protocol):
    def __call__(self, rate_cba: float, rate_dcb: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsbat(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsbutterfly(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsgartley(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIscrab(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsshark(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIs5o(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIswolfe(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIs3driver(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIscontria(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIsexptria(Protocol):
    def __call__(self, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolIshns(Protocol):
    def __call__(self, rate_fed: float, rate_feb: float, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive') -> Any: ...


class _ProtocolExtract(Protocol):
    def __call__(self, price_g: float, price_f: float, price_e: float, price_d: float, price_c: float, price_b: float, price_a: float, margin_of_error: float) -> Any: ...


line_price_rate: _ProtocolLinePriceRate = Exported()
line_time_rate: _ProtocolLineTimeRate = Exported()
is_inrange: _ProtocolIsInrange = Exported()
isHarmonicTriangle: _ProtocolIsharmonictriangle = Exported()
is2Tap: _ProtocolIs2tap = Exported()
is3Tap: _ProtocolIs3tap = Exported()
is4Tap: _ProtocolIs4tap = Exported()
isABCD: _ProtocolIsabcd = Exported()
isBat: _ProtocolIsbat = Exported()
isButterfly: _ProtocolIsbutterfly = Exported()
isGartley: _ProtocolIsgartley = Exported()
isCrab: _ProtocolIscrab = Exported()
isShark: _ProtocolIsshark = Exported()
is5o: _ProtocolIs5o = Exported()
isWolfe: _ProtocolIswolfe = Exported()
is3Driver: _ProtocolIs3driver = Exported()
isConTria: _ProtocolIscontria = Exported()
isExpTria: _ProtocolIsexptria = Exported()
isHnS: _ProtocolIshns = Exported()
extract: _ProtocolExtract = Exported()


@script.library('HarmonicPattern')
def main():
    @export
    def line_price_rate(point_c: float, point_b: float, point_a: float):
        return (point_a - point_b) / (point_b - point_c)

    @export
    def line_time_rate(point_c: float, point_b: float, point_a: float):
        return (0 - (point_a - point_b)) / (point_b - point_c)

    @export
    def is_inrange(value: float, min: float, max: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        __block_result__ = na
        if calculation_type == 'additive':
            __block_result__ = value <= max + margin_of_error and value >= min - margin_of_error
        elif calculation_type == 'multiplicative':
            __block_result__ = value <= max * (1.0 + margin_of_error) and value >= min * (1.0 - margin_of_error)
        else:
            runtime.error('HarmonicPattern -> is_inrange(): undefined margin calcultion type.')
            __block_result__ = NA(bool)
        return __block_result__

    @export
    def isHarmonicTriangle(rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _return: bool = False
        for _i in pine_range(1, 12, 1):
            _phid: float = 0 - math.pow(math.phi, -5.0 + _i)
            if is_inrange(rate_cba, _phid, _phid, margin_of_error, calculation_type):
                _return = True
                break
        return _return

    @export
    def is2Tap(rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        return is_inrange(rate_cba, -1.0, -1.0, margin_of_error, calculation_type)

    @export
    def is3Tap(rate_edc: float, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -1.0, -1.0, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -1.0, -1.0, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_cba)

    @export
    def is4Tap(rate_gfe: float, rate_edc: float, rate_cba: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_gfe = is_inrange(rate_gfe, -1.0, -1.0, margin_of_error, calculation_type)
        _is_edc = is_inrange(rate_edc, -1.0, -1.0, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -1.0, -1.0, margin_of_error, calculation_type)
        return cast_bool(_is_gfe) and cast_bool(_is_edc) and cast_bool(_is_cba)

    @export
    def isABCD(rate_cba: float, rate_dcb: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_cba = is_inrange(rate_cba, -1.618, -1.27, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.786, -0.618, margin_of_error, calculation_type)
        return cast_bool(_is_cba) and cast_bool(_is_dcb)

    @export
    def isBat(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.5, -0.382, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.886, -0.382, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -2.618, -1.618, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -0.886, -0.886, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isButterfly(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.786, -0.786, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.886, -0.382, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -2.618, -1.618, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -1.618, -1.27, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isGartley(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.618, -0.618, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.886, -0.382, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -2.618, -1.13, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -0.786, -0.786, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isCrab(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.886, -0.886, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.886, -0.382, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -3.618, -2.0, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -1.618, -1.618, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isShark(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.886, -0.886, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -1.618, -1.13, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -2.24, -1.27, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -1.13, -0.886, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def is5o(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -1.618, -1.13, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -2.24, -1.618, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -0.5, -0.5, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -0.236, 0.236, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isWolfe(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -1.618, -1.27, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -5.0, -0.0, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -1.618, -1.27, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -5.0, -0.0, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def is3Driver(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -1.618, -1.27, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -5.0, -0.0, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -1.618, -1.27, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -5.0, -0.0, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isConTria(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -0.886, -0.236, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -0.886, -0.236, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -0.886, -0.236, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -0.886, -0.236, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isExpTria(rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_edc = is_inrange(rate_edc, -2.618, -1.125, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -2.618, -1.125, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -2.618, -1.125, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -2.618, -1.125, margin_of_error, calculation_type)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    @export
    def isHnS(rate_fed: float, rate_feb: float, rate_edc: float, rate_dcb: float, rate_cba: float, rate_eda: float, margin_of_error: float = 0.05, calculation_type: str = 'additive'):
        _is_fed = is_inrange(rate_fed, -0.618, -0.09, margin_of_error, calculation_type)
        _is_feb = is_inrange(rate_feb, -0.886, -0.09, margin_of_error, calculation_type)
        _is_edc = is_inrange(rate_edc, -9.999, -1.0, margin_of_error, calculation_type)
        _is_dcb = is_inrange(rate_dcb, -1.25, -0.75, margin_of_error, calculation_type)
        _is_cba = is_inrange(rate_cba, -0.886, -0.09, margin_of_error, calculation_type)
        _is_eda = is_inrange(rate_eda, -1.618, -0.09, margin_of_error, calculation_type)
        return cast_bool(_is_fed) and cast_bool(_is_feb) and cast_bool(_is_edc) and cast_bool(_is_eda) and cast_bool(_is_dcb) and cast_bool(_is_cba)

    @export
    def extract(price_g: float, price_f: float, price_e: float, price_d: float, price_c: float, price_b: float, price_a: float, margin_of_error: float):
        price_gfc: float = line_price_rate(price_g, price_f, price_c)
        price_gfa: float = line_price_rate(price_g, price_f, price_a)
        price_gdc: float = line_price_rate(price_g, price_d, price_c)
        price_gda: float = line_price_rate(price_g, price_d, price_a)
        price_gfe: float = line_price_rate(price_g, price_f, price_e)
        price_gba: float = line_price_rate(price_g, price_b, price_a)
        price_fed: float = line_price_rate(price_f, price_e, price_d)
        price_feb: float = line_price_rate(price_f, price_e, price_b)
        price_fcb: float = line_price_rate(price_f, price_c, price_b)
        price_edc: float = line_price_rate(price_e, price_d, price_c)
        price_eda: float = line_price_rate(price_e, price_d, price_a)
        price_eba: float = line_price_rate(price_e, price_b, price_a)
        price_dcb: float = line_price_rate(price_d, price_c, price_b)
        price_cba: float = line_price_rate(price_c, price_b, price_a)
        _isvalid_gfa: bool = price_fed >= -1 and price_feb >= -1 and (price_cba <= -1) and (price_eda <= -1)
        _isvalid_gda: bool = price_fed <= -1 and price_gfe >= -1 and (price_cba <= -1) and (price_dcb >= -1)
        _isvalid_gba: bool = price_feb <= -1 and price_gfe >= -1 and (price_cba <= -1) and (price_dcb <= -1)
        _isvalid_eba: bool = price_cba <= -1 and price_dcb <= -1
        _isvalid_eda: bool = price_cba <= -1 and price_dcb >= -1
        _isvalid_fcb: bool = price_fed >= -1 and price_edc <= -1
        _isvalid_feb: bool = price_edc >= -1 and price_dcb <= -1
        _pattern_list: list[str] = array.new_string(0)
        if isHarmonicTriangle(price_gfa, margin_of_error) and _isvalid_gfa:
            array.push(_pattern_list, '• Harmonic Triangle(GFA) •')
        if isHarmonicTriangle(price_gda, margin_of_error) and _isvalid_gda:
            array.push(_pattern_list, '• Harmonic Triangle(GDA) •')
        if isHarmonicTriangle(price_gba, margin_of_error) and _isvalid_gba:
            array.push(_pattern_list, '• Harmonic Triangle(GBA) •')
        if isHarmonicTriangle(price_eba, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Harmonic Triangle(EBA) •')
        if isHarmonicTriangle(price_eda, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Harmonic Triangle(EDA) •')
        if isHarmonicTriangle(price_cba, margin_of_error):
            array.push(_pattern_list, '• Harmonic Triangle(CBA) •')
        if is2Tap(price_cba, margin_of_error):
            array.push(_pattern_list, '• Double Tap(CBA) •')
        if is2Tap(price_eba, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Double Tap(EBA) •')
        if is2Tap(price_eda, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Double Tap(EDA) •')
        if is3Tap(price_edc, price_cba, margin_of_error):
            array.push(_pattern_list, '• Triple Tap(EDC, CBA) •')
        if is4Tap(price_gfe, price_edc, price_cba, margin_of_error):
            array.push(_pattern_list, '• Quadruple Tap(GFE, EDC, CBA) •')
        if isABCD(price_cba, price_dcb, margin_of_error):
            array.push(_pattern_list, '• AB=CD(CBA, DCB) •')
        if isABCD(price_cba, price_fcb, margin_of_error) and _isvalid_fcb:
            array.push(_pattern_list, '• AB=CD(CBA, FCB) •')
        if isABCD(price_eba, price_feb, margin_of_error) and _isvalid_feb:
            array.push(_pattern_list, '• AB=CD(EBA, FEB) •')
        if isABCD(price_eda, price_fed, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• AB=CD(EDA, FED) •')
        if isBat(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Bat(EDC, DCB, CBA, EDA) •')
        if isBat(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Bat(GFE, FEB, EBA, GFA) •')
        if isBat(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Bat(GFE, FED, EDA, GFA) •')
        if isButterfly(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Butterfly(EDC, DCB, CBA, EDA) •')
        if isButterfly(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Butterfly(GFE, FEB, EBA, GFA) •')
        if isButterfly(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Butterfly(GFE, FED, EDA, GFA) •')
        if isGartley(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Gartley(EDC, DCB, CBA, EDA) •')
        if isGartley(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Gartley(GFE, FEB, EBA, GFA) •')
        if isGartley(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Gartley(GFE, FED, EDA, GFA) •')
        if isCrab(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Crab(EDC, DCB, CBA, EDA) •')
        if isCrab(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Crab(GFE, FEB, EBA, GFA) •')
        if isCrab(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Crab(GFE, FED, EDA, GFA) •')
        if isShark(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Shark(EDC, DCB, CBA, EDA) •')
        if isShark(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Shark(GFE, FEB, EBA, GFA) •')
        if isShark(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Shark(GFE, FED, EDA, GFA) •')
        if is5o(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• 5o(EDC, DCB, CBA, EDA) •')
        if is5o(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• 5o(GFE, FEB, EBA, GFA) •')
        if is5o(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• 5o(GFE, FED, EDA, GFA) •')
        if isWolfe(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Wolf(EDC, DCB, CBA, EDA) •')
        if isWolfe(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Wolf(GFE, FEB, EBA, GFA) •')
        if isWolfe(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Wolf(GFE, FED, EDA, GFA) •')
        if isConTria(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Contracting Triangle(EDC, DCB, CBA, EDA) •')
        if isConTria(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Contracting Triangle(GFE, FEB, EBA, GFA) •')
        if isConTria(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Contracting Triangle(GFE, FED, EDA, GFA) •')
        if isExpTria(price_edc, price_dcb, price_cba, price_eda, margin_of_error):
            array.push(_pattern_list, '• Expanding Triangle(EDC, DCB, CBA, EDA) •')
        if isExpTria(price_gfe, price_feb, price_eba, price_gfa, margin_of_error) and _isvalid_eba:
            array.push(_pattern_list, '• Expanding Triangle(GFE, FEB, EBA, GFA) •')
        if isExpTria(price_gfe, price_fed, price_eda, price_gfa, margin_of_error) and _isvalid_eda:
            array.push(_pattern_list, '• Expanding Triangle(GFE, FED, EDA, GFA) •')
        if isHnS(price_fed, price_feb, price_dcb, price_edc, price_eda, price_cba, margin_of_error):
            array.push(_pattern_list, '• Head and Shoulders(FED, FEB, DCB, EDC, EDA, CBA) •')
        return _pattern_list


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
