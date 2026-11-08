"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import alertcondition, close, color, input, na, plot, script, ta
from pynecore.types import Series


@script.indicator('MavilimW', overlay=True, na_bool=True)
def main(
    mavilimold=input(False, title='Show Previous Version of MavilimW?'),
    fmal=input(3, 'First Moving Average length'),
    smal=input(5, 'Second Moving Average length')
):
    tmal = fmal + smal
    Fmal = smal + tmal
    Ftmal = tmal + Fmal
    Smal = Fmal + Ftmal
    M1 = ta.wma(close, fmal)
    M2 = ta.wma(M1, smal)
    M3 = ta.wma(M2, tmal)
    M4 = ta.wma(M3, Fmal)
    M5 = ta.wma(M4, Ftmal)
    MAVW: Series = ta.wma(M5, Smal)
    col1 = MAVW > MAVW[1]
    col3 = MAVW < MAVW[1]
    colorM = color.blue if col1 else color.red if col3 else color.yellow
    plot(MAVW, color=colorM, linewidth=2, title='MAVW')
    M12 = ta.wma(close, 3)
    M22 = ta.wma(M12, 5)
    M32 = ta.wma(M22, 8)
    M42 = ta.wma(M32, 13)
    M52 = ta.wma(M42, 21)
    MAVW2 = ta.wma(M52, 34)
    plot(MAVW2 if mavilimold and cast_bool(MAVW2) else na, color=color.new(color.blue, 0), linewidth=2, title='MavWOld')
    alertcondition(ta.crossover(MAVW, MAVW[1]), title='MAVW BUY', message='MAVW BUY!')
    alertcondition(ta.crossunder(MAVW, MAVW[1]), title='MAVW SELL', message='MAVW SELL!')
    alertcondition(ta.cross(MAVW, MAVW[1]), title='Color ALARM', message='MavilimW has changed color!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
