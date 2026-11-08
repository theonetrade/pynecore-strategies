"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import array, bar_index, na, script, time
from pynecore.types import NA
from typing import Protocol, Any
import lib.aybarsm.ToolsFluent.v6 as ToolsFluent


__all__ = ['PosAction', 'PosActionType', 'PosInfo', 'PosState', 'action', 'enter', 'exit', 'reset']


class PosState(Enum):
    buy = 'buy'
    sell = 'sell'


class PosActionType(Enum):
    tp = 'tp'
    re = 're'


@udt
class PosAction:
    actionType: PosActionType = na(PosActionType)
    price: float = na(float)
    when: int = _dataclass_field(default_factory=lambda: time)
    index: int = _dataclass_field(default_factory=lambda: bar_index)
    markPrice: float = na(float)
    markWhen: int = na(int)
    markIndex: int = na(int)


@udt
class PosInfo:
    state: PosState = na(PosState)
    price: float = na(float)
    when: int = _dataclass_field(default_factory=lambda: time)
    index: int = _dataclass_field(default_factory=lambda: bar_index)
    tp: 'list[PosAction]' = na(list)
    re: 'list[PosAction]' = na(list)
    markPrice: float = na(float)
    markWhen: int = na(int)
    markIndex: int = na(int)


class _ProtocolEnter(Protocol):
    def __call__(self, this: PosInfo, state: PosState, price: float, when: int = time, index: int = bar_index, markPrice: float = na, markWhen: int = na, markIndex: int = na) -> Any: ...


class _ProtocolAction(Protocol):
    def __call__(self, this: PosInfo, actionType: PosActionType, price: float, when: int = time, index: int = bar_index, markPrice: float = na, markWhen: int = na, markIndex: int = na) -> Any: ...


class _ProtocolReset(Protocol):
    def __call__(self, this: PosInfo) -> Any: ...


class _ProtocolExit(Protocol):
    def __call__(self, this: PosInfo) -> Any: ...


enter: _ProtocolEnter = Exported()
action: _ProtocolAction = Exported()
reset: _ProtocolReset = Exported()
exit: _ProtocolExit = Exported()


@script.library("ToolsPos", overlay=False)
def main():
    @export
    @method
    def enter(this: PosInfo, state: PosState, price: float, when: int = time, index: int = bar_index, markPrice: float = na, markWhen: int = na, markIndex: int = na):
        this.state = state
        this.price = price
        this.when = when
        this.index = index
        this.tp = array.new(0, NA(PosAction))
        this.re = array.new(0, NA(PosAction))
        this.markPrice = markPrice
        this.markWhen = markWhen
        this.markIndex = markIndex
        return this.markIndex

    @export
    @method
    def action(this: PosInfo, actionType: PosActionType, price: float, when: int = time, index: int = bar_index, markPrice: float = na, markWhen: int = na, markIndex: int = na):
        newPosAction: PosAction = PosAction(actionType, price, when, index, markPrice, markWhen, markIndex)

        if actionType == PosActionType.tp:
            if na(this.tp):
                this.tp = array.new(0, NA(PosAction))
            array.push(this.tp, newPosAction)

        __block_result__ = na
        if actionType == PosActionType.re:
            if na(this.re):
                this.re = array.new(0, NA(PosAction))
            __block_result__ = array.push(this.re, newPosAction)
        return __block_result__

    @export
    @method
    def reset(this: PosInfo):
        this.state = na
        this.price = na
        this.when = na
        this.index = na
        this.tp = na
        this.re = na
        this.markPrice = na
        this.markWhen = na
        this.markIndex = na
        return this.markIndex

    @export
    @method
    def exit(this: PosInfo):
        return reset(this)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
