"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.lib import (
    bar_index, barstate, close, color, input, label, math, script, string,
    syminfo, yloc
)
from pynecore.types import Persistent
from typing import Protocol, Any


__all__ = ['ceil', 'ceil_to_mintick', 'clamp', 'clamp_down', 'clamp_up', 'floor', 'floor_to_mintick', 'num_of_decimal_digits', 'num_of_non_decimal_digits']


class _ProtocolNumOfNonDecimalDigits(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolNumOfNonDecimalDigits1(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolNumOfDecimalDigits(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolNumOfDecimalDigits3(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolFloor(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolFloor5(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolFloor6(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolFloor7(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolFloorToMintick(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolCeil(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolCeil10(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolCeil11(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolCeil12(Protocol):
    def __call__(self, this: float, precision: int) -> Any: ...


class _ProtocolCeilToMintick(Protocol):
    def __call__(self, this: float) -> Any: ...


class _ProtocolClampUp(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampUp15(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampUp16(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampUp17(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampDown(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampDown19(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampDown20(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClampDown21(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClamp(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClamp23(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClamp24(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


class _ProtocolClamp25(Protocol):
    def __call__(self, this: float, lower: float, higher: float, precision: int) -> Any: ...


num_of_non_decimal_digits: _ProtocolNumOfNonDecimalDigits = Exported()
num_of_non_decimal_digits: _ProtocolNumOfNonDecimalDigits1 = Exported()
num_of_decimal_digits: _ProtocolNumOfDecimalDigits = Exported()
num_of_decimal_digits: _ProtocolNumOfDecimalDigits3 = Exported()
floor: _ProtocolFloor = Exported()
floor: _ProtocolFloor5 = Exported()
floor: _ProtocolFloor6 = Exported()
floor: _ProtocolFloor7 = Exported()
floor_to_mintick: _ProtocolFloorToMintick = Exported()
ceil: _ProtocolCeil = Exported()
ceil: _ProtocolCeil10 = Exported()
ceil: _ProtocolCeil11 = Exported()
ceil: _ProtocolCeil12 = Exported()
ceil_to_mintick: _ProtocolCeilToMintick = Exported()
clamp_up: _ProtocolClampUp = Exported()
clamp_up: _ProtocolClampUp15 = Exported()
clamp_up: _ProtocolClampUp16 = Exported()
clamp_up: _ProtocolClampUp17 = Exported()
clamp_down: _ProtocolClampDown = Exported()
clamp_down: _ProtocolClampDown19 = Exported()
clamp_down: _ProtocolClampDown20 = Exported()
clamp_down: _ProtocolClampDown21 = Exported()
clamp: _ProtocolClamp = Exported()
clamp: _ProtocolClamp23 = Exported()
clamp: _ProtocolClamp24 = Exported()
clamp: _ProtocolClamp25 = Exported()


@script.library(title='math_utils')
def main(
    contracts=input.int(defval=1, title='Contracts', minval=1, tooltip='The fixed number of contracts to enter in every trade when no leverage is used.', group='Quantity'),
    minOrderSize=input.float(defval=10.0, title='Minimum Order Size', minval=0.0, step=1.0, tooltip='The minimum trade size in quote currency that is allowed in the exchange for a valid new position (e.g. in Binance you cannot trade amounts that are equal or less than 10 USD).', group='Quantity'),
    leverage=input.int(defval=1, title='Leverage', minval=1, tooltip='Leverage factor used to multiply the initial risk quantity of each trade (by borrowing the remaining amount). Thus, the profits and losses are multiplied respectively. INFORMATION! The margin for long/short positions value in the "Settings/Properties" should be adjusted accoridngly to correctly trigger margin calls.', group='Quantity')
):
    @export
    @overload
    @method
    def num_of_non_decimal_digits(this: float):
        return math.max(math.floor(math.log10(this) + 1), 0)

    @export
    @overload
    @method
    def num_of_non_decimal_digits(this: float):
        return math.max(math.floor(math.log10(this) + 1), 0)

    @export
    @overload
    @method
    def num_of_decimal_digits(this: float):
        n: float = this - math.floor(this) if this > 1.0 else this
        return math.max(math.ceil(-1 * math.log10(n)), 0)

    @export
    @overload
    @method
    def num_of_decimal_digits(this: float):
        n: float = this - math.floor(this) if this > 1.0 else this
        return math.max(math.ceil(-1 * math.log10(n)), 0)

    @export
    @overload
    @method
    def floor(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.floor(num) / fact

    @export
    @overload
    @method
    def floor(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.floor(num) / fact

    @export
    @overload
    @method
    def floor(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.floor(num) / fact

    @export
    @overload
    @method
    def floor(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.floor(num) / fact

    @export
    @method
    def floor_to_mintick(this: float):
        precision: Persistent[int] = num_of_decimal_digits(syminfo.mintick)
        return floor(this, precision)

    @export
    @overload
    @method
    def ceil(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.ceil(num) / fact

    @export
    @overload
    @method
    def ceil(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.ceil(num) / fact

    @export
    @overload
    @method
    def ceil(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.ceil(num) / fact

    @export
    @overload
    @method
    def ceil(this: float, precision: int):
        fact: float = math.pow(10, precision)
        num: float = this * fact
        return math.ceil(num) / fact

    @export
    @method
    def ceil_to_mintick(this: float):
        precision: Persistent[int] = num_of_decimal_digits(syminfo.mintick)
        return ceil(this, precision)

    @export
    @overload
    @method
    def clamp_up(this: float, lower: float, higher: float, precision: int):
        return floor(math.min(ceil(math.max(this, lower), precision), higher), precision)

    @export
    @overload
    @method
    def clamp_up(this: float, lower: float, higher: float, precision: int):
        return floor(math.min(ceil(math.max(this, lower), precision), higher), precision)

    @export
    @overload
    @method
    def clamp_up(this: float, lower: float, higher: float, precision: int):
        return floor(math.min(ceil(math.max(this, lower), precision), higher), precision)

    @export
    @overload
    @method
    def clamp_up(this: float, lower: float, higher: float, precision: int):
        return floor(math.min(ceil(math.max(this, lower), precision), higher), precision)

    @export
    @overload
    @method
    def clamp_down(this: float, lower: float, higher: float, precision: int):
        return ceil(math.max(floor(math.min(this, higher), precision), lower), precision)

    @export
    @overload
    @method
    def clamp_down(this: float, lower: float, higher: float, precision: int):
        return ceil(math.max(floor(math.min(this, higher), precision), lower), precision)

    @export
    @overload
    @method
    def clamp_down(this: float, lower: float, higher: float, precision: int):
        return ceil(math.max(floor(math.min(this, higher), precision), lower), precision)

    @export
    @overload
    @method
    def clamp_down(this: float, lower: float, higher: float, precision: int):
        return ceil(math.max(floor(math.min(this, higher), precision), lower), precision)

    @export
    @overload
    @method
    def clamp(this: float, lower: float, higher: float, precision: int):
        return math.max(math.min(math.round(this, precision), higher), lower)

    @export
    @overload
    @method
    def clamp(this: float, lower: float, higher: float, precision: int):
        return math.max(math.min(math.round(this, precision), higher), lower)

    @export
    @overload
    @method
    def clamp(this: float, lower: float, higher: float, precision: int):
        return math.max(math.min(math.round(this, precision), higher), lower)

    @export
    @overload
    @method
    def clamp(this: float, lower: float, higher: float, precision: int):
        return math.max(math.min(math.round(this, precision), higher), lower)

    minQuotePrice: Persistent[float] = syminfo.mintick * syminfo.pointvalue
    quoteDecimalDigits: Persistent[int] = num_of_decimal_digits(minQuotePrice) + 1
    entryQuoteQuantity: float = clamp_down(contracts * close * leverage, minOrderSize, 100000 * leverage, quoteDecimalDigits)
    minBasePrice: float = minOrderSize / close
    baseDecimalDigits: int = num_of_decimal_digits(minBasePrice) + 1
    entryBaseQuantity: float = floor(entryQuoteQuantity / close, baseDecimalDigits)

    if barstate.islastconfirmedhistory or barstate.islast:
        label.new(x=bar_index, y=close, text='[' + string.tostring(minQuotePrice) + ', ' + string.tostring(quoteDecimalDigits) + ', ' + string.tostring(entryQuoteQuantity) + ']\n[' + string.tostring(minBasePrice) + ', ' + string.tostring(baseDecimalDigits) + ', ' + string.tostring(entryBaseQuantity) + ']', yloc=yloc.abovebar, color=color.black, style=label.style_label_down, textcolor=color.white, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
