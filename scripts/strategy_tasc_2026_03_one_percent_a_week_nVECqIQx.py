"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, color, dayofweek, low, na, open, plot, script, session,
    strategy, ta
)
from pynecore.types import Persistent


@script.strategy("TASC 2026.03 One Percent A Week", "1%/W", overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main():
    wOpen: Persistent[float] = na(float)
    pt: Persistent[float] = na(float)
    newSession: bool = dayofweek == dayofweek.monday and session.isfirstbar_regular

    if newSession:
        wOpen = open

    down1: float = wOpen * 0.99

    if newSession:
        strategy.entry('Buy', strategy.long, limit=down1)
        pt = na

    newFill: bool = ta.change(strategy.position_size) != 0
    sendPT: Persistent[bool] = False
    beSent: Persistent[bool] = False

    if strategy.position_size > 0 and newFill:
        sendPT = True
        beSent = False

    if sendPT == True and session.isfirstbar_regular and (not beSent):
        pt = strategy.position_avg_price * 1.01
        strategy.exit('profit', 'Buy', limit=pt, oca_name='Order', comment='Profit')
        sendPT = False

    bet: float = strategy.position_avg_price * 0.995

    if low < bet and (not beSent):
        pt = strategy.position_avg_price
        strategy.exit('profit', 'Buy', limit=pt, oca_name='Order', comment='Break-even')
        beSent = True

    if dayofweek == dayofweek.friday and strategy.position_size > 0 and session.islastbar_regular and barstate.isconfirmed:
        strategy.close_all('End of week', immediately=True)

    plot(na if newSession or not na(pt) else wOpen, 'Weekly Open', color.yellow, style=plot.style_linebr)

    plot(na if newSession or not na(pt) else down1, 'Weekly 1% Dip', color.blue, style=plot.style_linebr, linestyle=plot.linestyle_dashed)

    plot(bet if strategy.position_size > 0 else na, '0.5% Drawdown', color.rgb(255, 0, 0), style=plot.style_linebr, linestyle=plot.linestyle_dashed)

    plot(pt if strategy.position_size > 0 else na, 'Profit Target', color.rgb(0, 255, 0), style=plot.style_linebr, linestyle=plot.linestyle_solid)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
