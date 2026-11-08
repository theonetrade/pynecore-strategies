"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, bar_index, barcolor, barstate, close, color, fill,
    high, hlc3, input, label, low, math, na, open, plot, script, size, ta
)
from pynecore.types import Color, Persistent

grpS: str = "Signals"
grpB: str = "Reversal bands"
grpC: str = "Trend candles"
grpD: str = "Look"


@script.indicator("Reversal Master [SimpleAlgo]", "Reversal Master", overlay=True, max_labels_count=500)
def main(
    showSig=input.bool(True, "Reversal signals", group=grpS, tooltip="Momentum leaves an extreme after a stretch. Marked Strong when price reached the outer bands during that stretch."),
    showReady=input.bool(True, "Ready alerts", group=grpS, tooltip="Momentum has entered an extreme. A reversal signal may follow when it leaves."),
    volLen=input.int(10, "Momentum length", minval=2, maxval=100, group=grpS),
    volSmooth=input.int(14, "Momentum smoothing", minval=1, maxval=100, group=grpS),
    hiLvl=input.int(80, "Extreme high", minval=51, maxval=99, group=grpS),
    loLvl=input.int(20, "Extreme low", minval=1, maxval=49, group=grpS),
    minGap=input.int(5, "Min bars between same-direction signals", minval=0, maxval=200, group=grpS),
    readyGap=input.int(8, "Min bars between Ready tags", minval=0, maxval=200, group=grpS),
    showBands=input.bool(True, "Show bands", group=grpB),
    bandLen=input.int(34, "Band length", minval=5, maxval=300, group=grpB),
    bandMult=input.float(2.0, "Band distance", minval=0.5, maxval=10.0, step=0.1, group=grpB, tooltip="Distance of the first band from the center, in volatility units. The second and third bands sit further out."),
    showCandles=input.bool(True, "Color candles by trend angle", group=grpC),
    angLen=input.int(34, "Trend angle length", minval=5, maxval=300, group=grpC),
    colUp=input.color(color.new('#3DDC97'), "Up", inline="c", group=grpD),
    colDn=input.color(color.new('#F2607A'), "Down", inline="c", group=grpD),
    colMid=input.color(color.new('#6B7280'), "Flat", inline="c", group=grpD)
):
    sd: float = ta.stdev(close, volLen)
    chg: float = ta.change(close)
    upV: float = ta.ema(sd if chg > 0 else 0.0, volSmooth)
    dnV: float = ta.ema(sd if chg <= 0 else 0.0, volSmooth)
    rvi: float = 100 * upV / (upV + dnV) if upV + dnV > 0 else 50.0

    basis: float = ta.ema(hlc3, bandLen)
    unit: float = ta.ema(math.avg(ta.stdev(close, bandLen), ta.atr(bandLen)), 5)
    u1: float = basis + unit * bandMult
    u2: float = basis + unit * (bandMult + 0.75)
    u3: float = basis + unit * (bandMult + 1.5)
    l1: float = basis - unit * bandMult
    l2: float = basis - unit * (bandMult + 0.75)
    l3: float = basis - unit * (bandMult + 1.5)

    pU1 = plot(u1 if showBands else na, 'Upper 1', color=color.new(colDn, 80))
    pU2 = plot(u2 if showBands else na, 'Upper 2', color=color.new(colDn, 65))
    pU3 = plot(u3 if showBands else na, 'Upper 3', color=color.new(colDn, 40))
    pL1 = plot(l1 if showBands else na, 'Lower 1', color=color.new(colUp, 80))
    pL2 = plot(l2 if showBands else na, 'Lower 2', color=color.new(colUp, 65))
    pL3 = plot(l3 if showBands else na, 'Lower 3', color=color.new(colUp, 40))
    fill(pU1, pU2, color=color.new(colDn, 93), title='Upper zone 1')
    fill(pU2, pU3, color=color.new(colDn, 86), title='Upper zone 2')
    fill(pL1, pL2, color=color.new(colUp, 93), title='Lower zone 1')
    fill(pL2, pL3, color=color.new(colUp, 86), title='Lower zone 2')

    slope: float = ta.linreg(close, angLen, 0) - ta.linreg(close, angLen, 1)
    atrA: float = ta.atr(angLen)
    steep: float = ta.ema(slope / atrA * angLen if atrA > 0 else 0.0, 5)
    deg: float = math.atan(steep) * 180 / math.pi
    angCol: Color = color.from_gradient(deg, 0, 60, colMid, colUp) if deg >= 0 else color.from_gradient(deg, -60, 0, colDn, colMid)
    candleC: Color = angCol if close >= open else color.from_gradient(0.45, 0.0, 1.0, angCol, color.new('#0F1117'))
    barcolor(candleC if showCandles else na, title='Trend candles')

    enterHi: bool = ta.crossover(rvi, hiLvl)
    leaveHi: bool = ta.crossunder(rvi, hiLvl)
    enterLo: bool = ta.crossunder(rvi, loLvl)
    leaveLo: bool = ta.crossover(rvi, loLvl)
    atr30: float = ta.atr(30)

    readyDn: Persistent[bool] = False
    tierDn: Persistent[int] = 0
    lastDnBar: Persistent[int] = -100000
    readyUp: Persistent[bool] = False
    tierUp: Persistent[int] = 0
    lastUpBar: Persistent[int] = -100000
    lastReadyBar: Persistent[int] = -100000
    lastSigBar: Persistent[int] = -100000
    sigUpNow: bool = False
    sigDnNow: bool = False
    readyUpNow: bool = False
    readyDnNow: bool = False

    if barstate.isconfirmed and (not na(atr30)):
        if readyDn:
            tierDn = math.max(tierDn, 3 if high > u3 else 2 if high > u2 else 1 if high > u1 else 0)
        if readyUp:
            tierUp = math.max(tierUp, 3 if low < l3 else 2 if low < l2 else 1 if low < l1 else 0)

        if enterHi:
            readyDn = True
            tierDn = 3 if high > u3 else 2 if high > u2 else 1 if high > u1 else 0
            readyDnNow = True
            if showReady and bar_index - lastReadyBar >= readyGap:
                lastReadyBar = bar_index
                label.new(bar_index, high + atr30 * (1.3 if bar_index - lastSigBar <= 3 else 0.15), 'Ready ▼', style=label.style_label_down, color=color.new(colDn, 100), textcolor=color.new(colDn, 20), size=size.small, tooltip='Upside momentum is stretched. A sell-side reversal signal may follow.')
        if enterLo:
            readyUp = True
            tierUp = 3 if low < l3 else 2 if low < l2 else 1 if low < l1 else 0
            readyUpNow = True
            if showReady and bar_index - lastReadyBar >= readyGap:
                lastReadyBar = bar_index
                label.new(bar_index, low - atr30 * (1.3 if bar_index - lastSigBar <= 3 else 0.15), 'Ready ▲', style=label.style_label_up, color=color.new(colUp, 100), textcolor=color.new(colUp, 20), size=size.small, tooltip='Downside momentum is stretched. A buy-side reversal signal may follow.')

        if leaveHi and readyDn:
            if showSig and bar_index - lastDnBar >= minGap:
                strong: bool = tierDn >= 2
                label.new(bar_index, high + atr30 * 0.8, '▼ Strong' if strong else '▼', style=label.style_label_down, color=colDn, textcolor=color.new('#0F1117'), size=size.normal, tooltip='Upside momentum has left its extreme.' + ('\nPrice stretched into the outer bands during the move.' if strong else '\nPrice did not reach the outer bands.'))
                lastDnBar = bar_index
                lastSigBar = bar_index
                sigDnNow = True
                alert('Reversal Master: sell-side reversal' + (' (strong)' if strong else ''), alert.freq_once_per_bar_close)
            readyDn = False
        if leaveLo and readyUp:
            if showSig and bar_index - lastUpBar >= minGap:
                strong: bool = tierUp >= 2
                label.new(bar_index, low - atr30 * 0.8, '▲ Strong' if strong else '▲', style=label.style_label_up, color=colUp, textcolor=color.new('#0F1117'), size=size.normal, tooltip='Downside momentum has left its extreme.' + ('\nPrice stretched into the outer bands during the move.' if strong else '\nPrice did not reach the outer bands.'))
                lastUpBar = bar_index
                lastSigBar = bar_index
                sigUpNow = True
                alert('Reversal Master: buy-side reversal' + (' (strong)' if strong else ''), alert.freq_once_per_bar_close)
            readyUp = False

    alertcondition(sigUpNow, 'Buy-side reversal', 'Reversal Master: buy-side reversal')
    alertcondition(sigDnNow, 'Sell-side reversal', 'Reversal Master: sell-side reversal')
    alertcondition(readyUpNow, 'Ready: buy side', 'Reversal Master: downside momentum stretched')
    alertcondition(readyDnNow, 'Ready: sell side', 'Reversal Master: upside momentum stretched')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)