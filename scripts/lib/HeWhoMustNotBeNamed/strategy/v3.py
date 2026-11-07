"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import math, nz, script, strategy, string
from typing import Protocol, Any


__all__ = ['bracketOrder', 'bracketOrderWithoutLeverage', 'getQty', 'order__ren__']


class _ProtocolGetqty(Protocol):
    def __call__(self, entry: float, stop: float, riskPercentage: float = 1.0) -> Any: ...


class _ProtocolBracketorder(Protocol):
    def __call__(self, id: str, entry: float, stop: float, target: float, maxLeverage: int = 100, isLimitOrder: bool = False, riskPercentage: float = 1.0) -> Any: ...


class _ProtocolBracketorderwithoutleverage(Protocol):
    def __call__(self, id: str, entry: float, stop: float, target: float, isLimitOrder: bool = False) -> Any: ...


class _ProtocolOrder(Protocol):
    def __call__(self, id: str, entry: float, stop: float, maxLeverage: int = 100, isLimitOrder: bool = False, riskPercentage: float = 1.0) -> Any: ...


getQty: _ProtocolGetqty = Exported()
bracketOrder: _ProtocolBracketorder = Exported()
bracketOrderWithoutLeverage: _ProtocolBracketorderwithoutleverage = Exported()
order__ren__: _ProtocolOrder = Exported()


@script.library('strategy')
def main():
    @export
    def getQty(entry: float, stop: float, riskPercentage: float = 1.0):
        cashInHand = strategy.initial_capital + strategy.netprofit
        risk = cashInHand * riskPercentage / 100
        quantity = risk / (entry - stop)
        existingPosition = nz(strategy.position_avg_price * strategy.position_size)
        newPosition = math.abs(existingPosition + quantity)
        leverage = math.ceil(newPosition / cashInHand)
        return (math.abs(quantity), leverage)

    @export
    def bracketOrder(id: str, entry: float, stop: float, target: float, maxLeverage: int = 100, isLimitOrder: bool = False, riskPercentage: float = 1.0):
        dir = 1 if entry > stop and entry < target else -1 if entry < stop and entry > target else 0
        qty, leverage = getQty(entry, stop, riskPercentage)
        orderPlaced: bool = False
        if dir != 0 and leverage <= maxLeverage:
            if isLimitOrder:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, qty, limit=entry)
            else:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, qty, stop=entry)
            strategy.exit('Exit ' + string.tostring(id), string.tostring(id), stop=stop, limit=target)
            orderPlaced = True
        return orderPlaced

    @export
    def bracketOrderWithoutLeverage(id: str, entry: float, stop: float, target: float, isLimitOrder: bool = False):
        dir = 1 if entry > stop and entry < target else -1 if entry < stop and entry > target else 0
        orderPlaced: bool = False
        if dir != 0:
            if isLimitOrder:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, limit=entry)
            else:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, stop=entry)
            strategy.exit('Exit ' + string.tostring(id), string.tostring(id), stop=stop, limit=target)
            orderPlaced = True
        return orderPlaced

    @export
    def order__ren__(id: str, entry: float, stop: float, maxLeverage: int = 100, isLimitOrder: bool = False, riskPercentage: float = 1.0):
        dir = 1 if entry > stop else -1 if entry < stop else 0
        qty, leverage = getQty(entry, stop, riskPercentage)
        orderPlaced: bool = False
        if leverage <= maxLeverage and dir != 0:
            if isLimitOrder:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, qty, limit=entry)
            else:
                strategy.entry(string.tostring(id), strategy.long if dir > 0 else strategy.short, qty, stop=entry)
            strategy.exit('Exit ' + string.tostring(id), string.tostring(id), stop=stop)
            orderPlaced = True
        return orderPlaced


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
