"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barcolor, barstate, close, color, extend, input, line,
    na, open, script, string
)
from pynecore.types import Color
from typing import Protocol, Any


__all__ = ['frankenthaler_flood', 'frankenthaler_thebay', 'gogh_cafeterrace', 'gogh_crows', 'gogh_tarascon', 'gruvbox', 'guardians', 'monokai', 'monokaipro', 'okeeffe_lake', 'okeeffe_music', 'okeeffe_reflection', 'okeeffe_sun', 'package', 'panda', 'spacemacs_dark', 'spacemacs_light', 'st3', 'st4', 'tradingview', 'tradingview_flag']


class _ProtocolMonokai(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolMonokaipro(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolPanda(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolTradingview(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolTradingviewFlag(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolGoghTarascon(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolGoghCrows(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolGoghCafeterrace(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolFrankenthalerFlood(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolFrankenthalerThebay(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolOkeeffeMusic(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolOkeeffeLake(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolOkeeffeReflection(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolOkeeffeSun(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolSpacemacsDark(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolSpacemacsLight(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolGruvbox(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolGuardians(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolSt3(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolSt4(Protocol):
    def __call__(self, _color: str) -> Any: ...


class _ProtocolPackage(Protocol):
    def __call__(self, _name: str, _color: str, _fallback: Color = na) -> Any: ...


monokai: _ProtocolMonokai = Exported()
monokaipro: _ProtocolMonokaipro = Exported()
panda: _ProtocolPanda = Exported()
tradingview: _ProtocolTradingview = Exported()
tradingview_flag: _ProtocolTradingviewFlag = Exported()
gogh_tarascon: _ProtocolGoghTarascon = Exported()
gogh_crows: _ProtocolGoghCrows = Exported()
gogh_cafeterrace: _ProtocolGoghCafeterrace = Exported()
frankenthaler_flood: _ProtocolFrankenthalerFlood = Exported()
frankenthaler_thebay: _ProtocolFrankenthalerThebay = Exported()
okeeffe_music: _ProtocolOkeeffeMusic = Exported()
okeeffe_lake: _ProtocolOkeeffeLake = Exported()
okeeffe_reflection: _ProtocolOkeeffeReflection = Exported()
okeeffe_sun: _ProtocolOkeeffeSun = Exported()
spacemacs_dark: _ProtocolSpacemacsDark = Exported()
spacemacs_light: _ProtocolSpacemacsLight = Exported()
gruvbox: _ProtocolGruvbox = Exported()
guardians: _ProtocolGuardians = Exported()
st3: _ProtocolSt3 = Exported()
st4: _ProtocolSt4 = Exported()
package: _ProtocolPackage = Exported()


@script.library('AwesomeColor', overlay=False)
def main(
    i_color=input.string('Guardians', 'Color', options=('TradingView', 'monokai', 'monokaipro', 'panda', 'Gruvbox', 'Spacemacs_light', 'Spacemacs_dark', 'Guardians', 'st3', 'st4')),
    i_bar_color=input.string('TradingView', options=('TradingView', 'monokai', 'monokaipro', 'panda', 'Gruvbox', 'Spacemacs_light', 'Spacemacs_dark', 'Guardians', 'st3', 'st4', 'gogh_tarascon', 'gogh_crows', 'gogh_cafeterrace', 'frankenthaler_flood', 'frankenthaler_thebay', 'okeeffe_sun', 'okeeffe_reflection', 'okeeffe_lake', 'okeeffe_music'))
):
    @export
    def monokai(_color: str):
        __block_result__ = na
        __switch__ = _color
        if __switch__ == 'purple':
            __block_result__ = color.new('#AE81FF')
        elif __switch__ == 'blue':
            __block_result__ = color.new('#66D9EF')
        elif __switch__ == 'green':
            __block_result__ = color.new('#A6E22E')
        elif __switch__ == 'yellow':
            __block_result__ = color.new('#E6DB74')
        elif __switch__ == 'orange':
            __block_result__ = color.new('#FD971F')
        elif __switch__ == 'black':
            __block_result__ = color.new('#272822')
        elif __switch__ == 'red':
            __block_result__ = color.new('#F92472')
        elif __switch__ == 'pink':
            __block_result__ = color.new('#FB71A3')
        elif __switch__ == 'white':
            __block_result__ = color.new('#FFFFFF')
        elif __switch__ == 'gray':
            __block_result__ = color.new('#74756F')
        elif __switch__ == 'up':
            __block_result__ = color.new('#A6E22E')
        elif __switch__ == 'down':
            __block_result__ = color.new('#F92472')
        else:
            __block_result__ = na
        return __block_result__

    @export
    def monokaipro(_color: str):
        __block_result_1__ = na
        __switch__ = _color
        if __switch__ == 'purple':
            __block_result_1__ = color.new('#AB9DF2')
        elif __switch__ == 'blue':
            __block_result_1__ = color.new('#78DCE8')
        elif __switch__ == 'green':
            __block_result_1__ = color.new('#A9DC76')
        elif __switch__ == 'yellow':
            __block_result_1__ = color.new('#FFD866')
        elif __switch__ == 'orange':
            __block_result_1__ = color.new('#FC9867')
        elif __switch__ == 'red':
            __block_result_1__ = color.new('#FE6188')
        elif __switch__ == 'pink':
            __block_result_1__ = color.new('#FFADC2')
        elif __switch__ == 'black':
            __block_result_1__ = color.new('#2D2A2E')
        elif __switch__ == 'white':
            __block_result_1__ = color.new('#FFFFFF')
        elif __switch__ == 'gray':
            __block_result_1__ = color.new('#7A7A7A')
        elif __switch__ == 'up':
            __block_result_1__ = color.new('#A9DC76')
        elif __switch__ == 'down':
            __block_result_1__ = color.new('#FE6188')
        else:
            __block_result_1__ = na
        return __block_result_1__

    @export
    def panda(_color: str):
        __block_result_2__ = na
        __switch__ = _color
        if __switch__ == 'verylightgray':
            __block_result_2__ = color.new('#E6E6E6')
        elif __switch__ == 'lightergray':
            __block_result_2__ = color.new('#CDCDCD')
        elif __switch__ == 'lightgray':
            __block_result_2__ = color.new('#757575')
        elif __switch__ == 'gray':
            __block_result_2__ = color.new('#373B41')
        elif __switch__ == 'darkgray':
            __block_result_2__ = color.new('#2E2F30')
        elif __switch__ == 'verydarkgray':
            __block_result_2__ = color.new('#292A2B')
        elif __switch__ == 'black':
            __block_result_2__ = color.new('#292A2B')
        elif __switch__ == 'white':
            __block_result_2__ = color.new('#F3F3F3')
        elif __switch__ == 'lightmidnight':
            __block_result_2__ = color.new('#676B79')
        elif __switch__ == 'blue':
            __block_result_2__ = color.new('#45A9F9')
        elif __switch__ == 'bluelight':
            __block_result_2__ = color.new('#6FC1FF')
        elif __switch__ == 'purple':
            __block_result_2__ = color.new('#B084EB')
        elif __switch__ == 'green':
            __block_result_2__ = color.new('#19F9D8')
        elif __switch__ == 'red':
            __block_result_2__ = color.new('#FF2C6D')
        elif __switch__ == 'orange':
            __block_result_2__ = color.new('#FFB86C')
        elif __switch__ == 'lightorange':
            __block_result_2__ = color.new('#FFCC95')
        elif __switch__ == 'pink':
            __block_result_2__ = color.new('#FF75B5')
        elif __switch__ == 'lightpink':
            __block_result_2__ = color.new('#FF9AC1')
        elif __switch__ == 'yellow':
            __block_result_2__ = color.new('#FFF145')
        elif __switch__ == 'up':
            __block_result_2__ = color.new('#19F9D8')
        elif __switch__ == 'down':
            __block_result_2__ = color.new('#FF2C6D')
        else:
            __block_result_2__ = na
        return __block_result_2__

    @export
    def tradingview(_color: str):
        __block_result_3__ = na
        __switch__ = _color
        if __switch__ == 'blue':
            __block_result_3__ = color.new('#2962FF')
        elif __switch__ == 'red':
            __block_result_3__ = color.new('#F23645')
        elif __switch__ == 'green':
            __block_result_3__ = color.new('#22AB94')
        elif __switch__ == 'orange':
            __block_result_3__ = color.new('#FF9800')
        elif __switch__ == 'yellow':
            __block_result_3__ = color.new('#FFCA3B')
        elif __switch__ == 'purple':
            __block_result_3__ = color.new('#673AB7')
        elif __switch__ == 'lightgray':
            __block_result_3__ = color.new('#9598A1')
        elif __switch__ == 'gray':
            __block_result_3__ = color.new('#5D606B')
        elif __switch__ == 'black':
            __block_result_3__ = color.new('#131722')
        elif __switch__ == 'white':
            __block_result_3__ = color.new('#B2B5BE')
        elif __switch__ == 'pink':
            __block_result_3__ = color.new('#F47F89')
        elif __switch__ == 'buy':
            __block_result_3__ = color.new('#1F44FF')
        elif __switch__ == 'sell':
            __block_result_3__ = color.new('#E21E34')
        elif __switch__ == 'up':
            __block_result_3__ = color.new('#22AB94')
        elif __switch__ == 'down':
            __block_result_3__ = color.new('#F23645')
        else:
            __block_result_3__ = color.new('#131722')
        return __block_result_3__

    @export
    def tradingview_flag(_color: str):
        __block_result_4__ = na
        __switch__ = _color
        if __switch__ == 'red':
            __block_result_4__ = color.new('#FF5252')
        elif __switch__ == 'blue':
            __block_result_4__ = color.new('#2979FF')
        elif __switch__ == 'green':
            __block_result_4__ = color.new('#4CAF50')
        elif __switch__ == 'orange':
            __block_result_4__ = color.new('#FF9100')
        elif __switch__ == 'purple':
            __block_result_4__ = color.new('#AB47BC')
        elif __switch__ == 'cyan':
            __block_result_4__ = color.new('#00E5FF')
        elif __switch__ == 'pink':
            __block_result_4__ = color.new('#FF80AB')
        elif __switch__ == 'black':
            __block_result_4__ = color.new('#131722')
        elif __switch__ == 'white':
            __block_result_4__ = color.new('#B2B5BE')
        elif __switch__ == 'up':
            __block_result_4__ = color.new('#4CAF50')
        elif __switch__ == 'down':
            __block_result_4__ = color.new('#FF5252')
        else:
            __block_result_4__ = na
        return __block_result_4__

    @export
    def gogh_tarascon(_color: str):
        __block_result_5__ = na
        __switch__ = _color
        if __switch__ == 'lightgreen':
            __block_result_5__ = color.new('#75B27F')
        elif __switch__ == 'green':
            __block_result_5__ = color.new('#4C7B3D')
        elif __switch__ == 'yellow':
            __block_result_5__ = color.new('#D39E2E')
        elif __switch__ == 'blue':
            __block_result_5__ = color.new('#27749A')
        elif __switch__ == 'black':
            __block_result_5__ = color.new('#2E3428')
        elif __switch__ == 'up':
            __block_result_5__ = color.new('#4C7B3D')
        elif __switch__ == 'down':
            __block_result_5__ = color.new('#D39E2E')
        else:
            __block_result_5__ = na
        return __block_result_5__

    @export
    def gogh_crows(_color: str):
        __block_result_6__ = na
        __switch__ = _color
        if __switch__ == 'navy':
            __block_result_6__ = color.new('#072945')
        elif __switch__ == 'blue':
            __block_result_6__ = color.new('#2E68B1')
        elif __switch__ == 'maroon':
            __block_result_6__ = color.new('#5F292A')
        elif __switch__ == 'yellow':
            __block_result_6__ = color.new('#E7BB3C')
        elif __switch__ == 'green':
            __block_result_6__ = color.new('#4E683D')
        elif __switch__ == 'up':
            __block_result_6__ = color.new('#E7BB3C')
        elif __switch__ == 'down':
            __block_result_6__ = color.new('#2E68B1')
        else:
            __block_result_6__ = na
        return __block_result_6__

    @export
    def gogh_cafeterrace(_color: str):
        __block_result_7__ = na
        __switch__ = _color
        if __switch__ == 'blue':
            __block_result_7__ = color.new('#1F3FA0')
        elif __switch__ == 'lightblue':
            __block_result_7__ = color.new('#5581C6')
        elif __switch__ == 'orange':
            __block_result_7__ = color.new('#DD862E')
        elif __switch__ == 'yellow':
            __block_result_7__ = color.new('#F7DA44')
        elif __switch__ == 'black':
            __block_result_7__ = color.new('#172128')
        elif __switch__ == 'up':
            __block_result_7__ = color.new('#DD862E')
        elif __switch__ == 'down':
            __block_result_7__ = color.new('#5581C6')
        else:
            __block_result_7__ = na
        return __block_result_7__

    @export
    def frankenthaler_flood(_color: str):
        __block_result_8__ = na
        __switch__ = _color
        if __switch__ == 'maroon':
            __block_result_8__ = color.new('#2C0F0C')
        elif __switch__ == 'red':
            __block_result_8__ = color.new('#88231A')
        elif __switch__ == 'green':
            __block_result_8__ = color.new('#2B371F')
        elif __switch__ == 'yellow':
            __block_result_8__ = color.new('#F59009')
        elif __switch__ == 'blue':
            __block_result_8__ = color.new('#0A1467')
        elif __switch__ == 'up':
            __block_result_8__ = color.new('#0A1467')
        elif __switch__ == 'down':
            __block_result_8__ = color.new('#88231A')
        else:
            __block_result_8__ = na
        return __block_result_8__

    @export
    def frankenthaler_thebay(_color: str):
        __block_result_9__ = na
        __switch__ = _color
        if __switch__ == 'lilac':
            __block_result_9__ = color.new('#949BCD')
        elif __switch__ == 'green':
            __block_result_9__ = color.new('#5F7660')
        elif __switch__ == 'purple':
            __block_result_9__ = color.new('#443D8E')
        elif __switch__ == 'white':
            __block_result_9__ = color.new('#FEF8CB')
        elif __switch__ == 'black':
            __block_result_9__ = color.new('#03000E')
        elif __switch__ == 'up':
            __block_result_9__ = color.new('#5F7660')
        elif __switch__ == 'down':
            __block_result_9__ = color.new('#443D8E')
        else:
            __block_result_9__ = na
        return __block_result_9__

    @export
    def okeeffe_music(_color: str):
        __block_result_10__ = na
        __switch__ = _color
        if __switch__ == 'green':
            __block_result_10__ = color.new('#9EC6BE')
        elif __switch__ == 'icegreen':
            __block_result_10__ = color.new('#9EC6BE')
        elif __switch__ == 'cyan':
            __block_result_10__ = color.new('#359BC9')
        elif __switch__ == 'blue':
            __block_result_10__ = color.new('#0E6CA5')
        elif __switch__ == 'pink':
            __block_result_10__ = color.new('#D890CC')
        elif __switch__ == 'peach':
            __block_result_10__ = color.new('#FDC7AE')
        elif __switch__ == 'down':
            __block_result_10__ = color.new('#359BC9')
        elif __switch__ == 'up':
            __block_result_10__ = color.new('#D890CC')
        else:
            __block_result_10__ = na
        return __block_result_10__

    @export
    def okeeffe_lake(_color: str):
        __block_result_11__ = na
        __switch__ = _color
        if __switch__ == 'skyblue':
            __block_result_11__ = color.new('#99B6D0')
        elif __switch__ == 'horizonblue':
            __block_result_11__ = color.new('#6D8BAC')
        elif __switch__ == 'jayblue':
            __block_result_11__ = color.new('#41628A')
        elif __switch__ == 'smalt':
            __block_result_11__ = color.new('#203E62')
        elif __switch__ == 'indigo':
            __block_result_11__ = color.new('#10214C')
        elif __switch__ == 'up':
            __block_result_11__ = color.new('#203E62')
        elif __switch__ == 'down':
            __block_result_11__ = color.new('#6D8BAC')
        else:
            __block_result_11__ = na
        return __block_result_11__

    @export
    def okeeffe_reflection(_color: str):
        __block_result_12__ = na
        __switch__ = _color
        if __switch__ == 'black':
            __block_result_12__ = color.new('#060C09')
        elif __switch__ == 'red':
            __block_result_12__ = color.new('#8F0A11')
        elif __switch__ == 'cyan':
            __block_result_12__ = color.new('#4086C5')
        elif __switch__ == 'lightblue':
            __block_result_12__ = color.new('#D0F1E4')
        elif __switch__ == 'blue':
            __block_result_12__ = color.new('#2415C1')
        elif __switch__ == 'up':
            __block_result_12__ = color.new('#8F0A11')
        elif __switch__ == 'down':
            __block_result_12__ = color.new('#2415C1')
        else:
            __block_result_12__ = na
        return __block_result_12__

    @export
    def okeeffe_sun(_color: str):
        __block_result_13__ = na
        __switch__ = _color
        if __switch__ == 'yellow':
            __block_result_13__ = color.new('#E5D67C')
        elif __switch__ == 'blue':
            __block_result_13__ = color.new('#94C4D1')
        elif __switch__ == 'lightgreen':
            __block_result_13__ = color.new('#8BB48F')
        elif __switch__ == 'green':
            __block_result_13__ = color.new('#1A413A')
        elif __switch__ == 'pink':
            __block_result_13__ = color.new('#FCE7D9')
        elif __switch__ == 'up':
            __block_result_13__ = color.new('#E5D67C')
        elif __switch__ == 'down':
            __block_result_13__ = color.new('#94C4D1')
        else:
            __block_result_13__ = na
        return __block_result_13__

    @export
    def spacemacs_dark(_color: str):
        __block_result_14__ = na
        __switch__ = _color
        if __switch__ == 'aqua':
            __block_result_14__ = color.new('#2D9574')
        elif __switch__ == 'aqua-bg':
            __block_result_14__ = color.new('#293235')
        elif __switch__ == 'green':
            __block_result_14__ = color.new('#67B11D')
        elif __switch__ == 'green-bg':
            __block_result_14__ = color.new('#293235')
        elif __switch__ == 'green-bg-s':
            __block_result_14__ = color.new('#29422D')
        elif __switch__ == 'cyan':
            __block_result_14__ = color.new('#28DEF0')
        elif __switch__ == 'red':
            __block_result_14__ = color.new('#F2241F')
        elif __switch__ == 'red-bg':
            __block_result_14__ = color.new('#3C2A2C')
        elif __switch__ == 'red-bg-s':
            __block_result_14__ = color.new('#512E31')
        elif __switch__ == 'blue':
            __block_result_14__ = color.new('#4F97D7')
        elif __switch__ == 'blue-bg':
            __block_result_14__ = color.new('#293239')
        elif __switch__ == 'blue-bg-s':
            __block_result_14__ = color.new('#2D4252')
        elif __switch__ == 'magenta':
            __block_result_14__ = color.new('#A31DB1')
        elif __switch__ == 'purple':
            __block_result_14__ = color.new('#A31DB1')
        elif __switch__ == 'yellow':
            __block_result_14__ = color.new('#B1951D')
        elif __switch__ == 'yellow-bg':
            __block_result_14__ = color.new('#32322C')
        elif __switch__ == 'black':
            __block_result_14__ = color.new('#1E2023')
        elif __switch__ == 'gray':
            __block_result_14__ = color.new('#808777')
        elif __switch__ == 'pink':
            __block_result_14__ = color.new('#EF74C3')
        elif __switch__ == 'orange':
            __block_result_14__ = color.new('#F2692C')
        elif __switch__ == 'white':
            __block_result_14__ = color.new('#DCD6D5')
        elif __switch__ == 'up':
            __block_result_14__ = color.new('#67B11D')
        elif __switch__ == 'down':
            __block_result_14__ = color.new('#F2241F')
        else:
            __block_result_14__ = na
        return __block_result_14__

    @export
    def spacemacs_light(_color: str):
        __block_result_15__ = na
        __switch__ = _color
        if __switch__ == 'aqua':
            __block_result_15__ = color.new('#2D9574')
        elif __switch__ == 'aqua-bg':
            __block_result_15__ = color.new('#EDF2E9')
        elif __switch__ == 'green':
            __block_result_15__ = color.new('#67B11D')
        elif __switch__ == 'green-bg':
            __block_result_15__ = color.new('#EDF2E9')
        elif __switch__ == 'green-bg-s':
            __block_result_15__ = color.new('#DAE6D0')
        elif __switch__ == 'cyan':
            __block_result_15__ = color.new('#21B8C7')
        elif __switch__ == 'red':
            __block_result_15__ = color.new('#F2241F')
        elif __switch__ == 'red-bg':
            __block_result_15__ = color.new('#FAEDE4')
        elif __switch__ == 'red-bg-s':
            __block_result_15__ = color.new('#EED9D2')
        elif __switch__ == 'blue':
            __block_result_15__ = color.new('#3A81C3')
        elif __switch__ == 'blue-bg':
            __block_result_15__ = color.new('#EDF1ED')
        elif __switch__ == 'blue-bg-s':
            __block_result_15__ = color.new('#D1DCDF')
        elif __switch__ == 'magenta':
            __block_result_15__ = color.new('#A31DB1')
        elif __switch__ == 'purple':
            __block_result_15__ = color.new('#A31DB1')
        elif __switch__ == 'yellow':
            __block_result_15__ = color.new('#B1951D')
        elif __switch__ == 'yellow-bg':
            __block_result_15__ = color.new('#F6F1E1')
        elif __switch__ == 'black':
            __block_result_15__ = color.new('#0E0A10')
        elif __switch__ == 'white':
            __block_result_15__ = color.new('#F9F7FB')
        elif __switch__ == 'gray':
            __block_result_15__ = color.new('#796384')
        elif __switch__ == 'orange':
            __block_result_15__ = color.new('#F95B14')
        elif __switch__ == 'pink':
            __block_result_15__ = color.new('#F46B69')
        elif __switch__ == 'up':
            __block_result_15__ = color.new('#2D9574')
        elif __switch__ == 'down':
            __block_result_15__ = color.new('#F2241F')
        else:
            __block_result_15__ = na
        return __block_result_15__

    @export
    def gruvbox(_color: str):
        __block_result_16__ = na
        __switch__ = _color
        if __switch__ == 'bright_red':
            __block_result_16__ = color.new('#FB4934')
        elif __switch__ == 'bright_green':
            __block_result_16__ = color.new('#B8BB26')
        elif __switch__ == 'bright_yellow':
            __block_result_16__ = color.new('#FABD2F')
        elif __switch__ == 'bright_blue':
            __block_result_16__ = color.new('#83A598')
        elif __switch__ == 'bright_purple':
            __block_result_16__ = color.new('#D3869B')
        elif __switch__ == 'bright_aqua':
            __block_result_16__ = color.new('#8EC07C')
        elif __switch__ == 'bright_orange':
            __block_result_16__ = color.new('#FE8019')
        elif __switch__ == 'neutral_red':
            __block_result_16__ = color.new('#CC241D')
        elif __switch__ == 'neutral_green':
            __block_result_16__ = color.new('#98971A')
        elif __switch__ == 'neutral_yellow':
            __block_result_16__ = color.new('#D79921')
        elif __switch__ == 'neutral_blue':
            __block_result_16__ = color.new('#458588')
        elif __switch__ == 'neutral_purple':
            __block_result_16__ = color.new('#B16286')
        elif __switch__ == 'neutral_aqua':
            __block_result_16__ = color.new('#689D6A')
        elif __switch__ == 'neutral_orange':
            __block_result_16__ = color.new('#D65D0E')
        elif __switch__ == 'faded_red':
            __block_result_16__ = color.new('#9D0006')
        elif __switch__ == 'faded_green':
            __block_result_16__ = color.new('#79740E')
        elif __switch__ == 'faded_yellow':
            __block_result_16__ = color.new('#B57614')
        elif __switch__ == 'faded_blue':
            __block_result_16__ = color.new('#076678')
        elif __switch__ == 'faded_purple':
            __block_result_16__ = color.new('#8F3F71')
        elif __switch__ == 'faded_aqua':
            __block_result_16__ = color.new('#427B58')
        elif __switch__ == 'faded_orange':
            __block_result_16__ = color.new('#AF3A03')
        elif __switch__ == 'red':
            __block_result_16__ = color.new('#CC241D')
        elif __switch__ == 'pink':
            __block_result_16__ = color.new('#D5615E')
        elif __switch__ == 'green':
            __block_result_16__ = color.new('#98971A')
        elif __switch__ == 'yellow':
            __block_result_16__ = color.new('#D79921')
        elif __switch__ == 'blue':
            __block_result_16__ = color.new('#458588')
        elif __switch__ == 'purple':
            __block_result_16__ = color.new('#B16286')
        elif __switch__ == 'aqua':
            __block_result_16__ = color.new('#689D6A')
        elif __switch__ == 'orange':
            __block_result_16__ = color.new('#D65D0E')
        elif __switch__ == 'black':
            __block_result_16__ = color.new('#1D2021')
        elif __switch__ == 'verydarkgray':
            __block_result_16__ = color.new('#282828')
        elif __switch__ == 'darkgray':
            __block_result_16__ = color.new('#32302F')
        elif __switch__ == 'gray':
            __block_result_16__ = color.new('#928374')
        elif __switch__ == 'white':
            __block_result_16__ = color.new('#F9F5D7')
        elif __switch__ == 'veryrightgray':
            __block_result_16__ = color.new('#FBF1C7')
        elif __switch__ == 'lightergray':
            __block_result_16__ = color.new('#F2E5BC')
        elif __switch__ == 'lightgray':
            __block_result_16__ = color.new('#EBDBB2')
        elif __switch__ == 'up':
            __block_result_16__ = color.new('#98971A')
        elif __switch__ == 'down':
            __block_result_16__ = color.new('#CC241D')
        else:
            __block_result_16__ = na
        return __block_result_16__

    @export
    def guardians(_color: str):
        __block_result_17__ = na
        __switch__ = _color
        if __switch__ == 'green':
            __block_result_17__ = color.new('#41802A')
        elif __switch__ == 'red':
            __block_result_17__ = color.new('#75091E')
        elif __switch__ == 'purple':
            __block_result_17__ = color.new('#8C5094')
        elif __switch__ == 'orange':
            __block_result_17__ = color.new('#E17431')
        elif __switch__ == 'blue':
            __block_result_17__ = color.new('#385A99')
        elif __switch__ == 'yellow':
            __block_result_17__ = color.new('#DAC23A')
        elif __switch__ == 'black':
            __block_result_17__ = color.new('#000000')
        elif __switch__ == 'white':
            __block_result_17__ = color.new('#FFFFFF')
        elif __switch__ == 'pink':
            __block_result_17__ = color.new('#C7207A')
        elif __switch__ == 'gray':
            __block_result_17__ = color.new('#493D52')
        elif __switch__ == 'up':
            __block_result_17__ = color.new('#385A99')
        elif __switch__ == 'down':
            __block_result_17__ = color.new('#75091E')
        else:
            __block_result_17__ = na
        return __block_result_17__

    @export
    def st3(_color: str):
        __block_result_18__ = na
        __switch__ = _color
        if __switch__ == 'black':
            __block_result_18__ = color.new('#090922')
        elif __switch__ == 'white':
            __block_result_18__ = color.new('#E0DFE5')
        elif __switch__ == 'navy':
            __block_result_18__ = color.new('#080247')
        elif __switch__ == 'blue':
            __block_result_18__ = color.new('#096EBF')
        elif __switch__ == 'darkpurple':
            __block_result_18__ = color.new('#382895')
        elif __switch__ == 'purple':
            __block_result_18__ = color.new('#8768E0')
        elif __switch__ == 'cyan':
            __block_result_18__ = color.new('#30BAE3')
        elif __switch__ == 'green':
            __block_result_18__ = color.new('#12B083')
        elif __switch__ == 'pink':
            __block_result_18__ = color.new('#C70A95')
        elif __switch__ == 'red':
            __block_result_18__ = color.new('#B1002A')
        elif __switch__ == 'yellow':
            __block_result_18__ = color.new('#B0A612')
        elif __switch__ == 'orange':
            __block_result_18__ = color.new('#E34417')
        elif __switch__ == 'brown':
            __block_result_18__ = color.new('#694E2B')
        elif __switch__ == 'darkbrown':
            __block_result_18__ = color.new('#51363B')
        elif __switch__ == 'gray':
            __block_result_18__ = color.new('#5A595E')
        elif __switch__ == 'up':
            __block_result_18__ = color.new('#12B083')
        elif __switch__ == 'down':
            __block_result_18__ = color.new('#B1002A')
        else:
            __block_result_18__ = na
        return __block_result_18__

    @export
    def st4(_color: str):
        __block_result_19__ = na
        __switch__ = _color
        if __switch__ == 'black':
            __block_result_19__ = color.new('#0D0D0D')
        elif __switch__ == 'white':
            __block_result_19__ = color.new('#E0DFE5')
        elif __switch__ == 'blue':
            __block_result_19__ = color.new('#0578A6')
        elif __switch__ == 'purple':
            __block_result_19__ = color.new('#9632A6')
        elif __switch__ == 'green':
            __block_result_19__ = color.new('#0DA667')
        elif __switch__ == 'pink':
            __block_result_19__ = color.new('#F25093')
        elif __switch__ == 'red':
            __block_result_19__ = color.new('#D93611')
        elif __switch__ == 'yellow':
            __block_result_19__ = color.new('#F2A341')
        elif __switch__ == 'orange':
            __block_result_19__ = color.new('#FC5E35')
        elif __switch__ == 'gray':
            __block_result_19__ = color.new('#5C504D')
        elif __switch__ == 'up':
            __block_result_19__ = color.new('#0DA667')
        elif __switch__ == 'down':
            __block_result_19__ = color.new('#D93611')
        else:
            __block_result_19__ = na
        return __block_result_19__

    @export
    def package(_name: str, _color: str, _fallback: Color = na):
        switch_var_20 = string.lower(_name)
        __block_result_20__ = na
        __switch__ = switch_var_20
        if __switch__ == 'monokai':
            __block_result_20__ = monokai(_color)
        elif __switch__ == 'monokaipro':
            __block_result_20__ = monokaipro(_color)
        elif __switch__ == 'panda':
            __block_result_20__ = panda(_color)
        elif __switch__ == 'tradingview':
            __block_result_20__ = tradingview(_color)
        elif __switch__ == 'spacemacs_dark':
            __block_result_20__ = spacemacs_dark(_color)
        elif __switch__ == 'spacemacs_light':
            __block_result_20__ = spacemacs_light(_color)
        elif __switch__ == 'gruvbox':
            __block_result_20__ = gruvbox(_color)
        elif __switch__ == 'guardians':
            __block_result_20__ = guardians(_color)
        elif __switch__ == 'st3':
            __block_result_20__ = st3(_color)
        elif __switch__ == 'st4':
            __block_result_20__ = st4(_color)
        elif __switch__ == 'okeeffe_sun':
            __block_result_20__ = okeeffe_sun(_color)
        elif __switch__ == 'okeeffe_reflection':
            __block_result_20__ = okeeffe_reflection(_color)
        elif __switch__ == 'okeeffe_lake':
            __block_result_20__ = okeeffe_lake(_color)
        elif __switch__ == 'okeeffe_music':
            __block_result_20__ = okeeffe_music(_color)
        elif __switch__ == 'frankenthaler_thebay':
            __block_result_20__ = frankenthaler_thebay(_color)
        elif __switch__ == 'frankenthaler_flood':
            __block_result_20__ = frankenthaler_flood(_color)
        elif __switch__ == 'gogh_cafeterrace':
            __block_result_20__ = gogh_cafeterrace(_color)
        elif __switch__ == 'gogh_crows':
            __block_result_20__ = gogh_crows(_color)
        elif __switch__ == 'gogh_tarascon':
            __block_result_20__ = gogh_tarascon(_color)
        else:
            __block_result_20__ = _fallback
        return __block_result_20__

    if barstate.islast:
        a_colors: list[str] = array.from_items('red', 'pink', 'orange', 'yellow', 'green', 'blue', 'purple', 'gray', 'black', 'white')
        for i in pine_range(0, array.size(a_colors) - 1, 1):
            line.new(bar_index, i * -10, bar_index + 10, i * -10, extend=extend.both, color=package(i_color, array.get(a_colors, i)), width=10)
    barcolor(package(string.lower(i_bar_color), 'up') if close > open else package(string.lower(i_bar_color), 'down'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
