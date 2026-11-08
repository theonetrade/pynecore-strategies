"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, high, input, label,
    location, low, math, na, nz, open, plot, plotshape, request, script, shape, size, string, ta,
    text, time, time_close, timenow, volume, xloc, yloc
)
from pynecore.types import Label, Persistent, PersistentSeries, Series


@script.indicator('Machine Learning: Logistic Regression (v.3)', '', True, na_bool=True)
def main(
    ptype=input.string('Close', 'Price Type', options=('Open', 'High', 'Low', 'Close', 'HL2', 'OC2', 'OHL3', 'HLC3', 'OHLC4')),
    reso=input.timeframe('', 'Resolution'),
    lookback=input.int(3, 'Lookback Window Size |2..n| (2)', minval=2),
    nlbk=input.int(2, 'Normalization Lookback |2..240| (120)', minval=2, maxval=240),
    lrate=input.float(0.0009, 'Learning Rate |0.0001..0.01|', minval=0.0001, maxval=0.01, step=0.0001),
    iterations=input.int(1000, 'Training Iterations |50..20000|', minval=50),
    ftype=input.string('None', 'Filter Signals by', options=('Volatility', 'Volume', 'Both', 'None')),
    curves=input(False, 'Show Loss & Prediction Curves?'),
    easteregg=input(True, 'Optional Calculation?'),
    useprice=input(True, 'Use Price Data for Signal Generation?'),
    holding_p=input.int(5, 'Holding Period |1..n|', minval=1),
    lot_size=input.float(0.01, 'Lot Size', options=(0.01, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100, 1000)),
    show_info=input(True, 'Show Info?')
):
    BUY: Persistent[int] = 1
    SELL: Persistent = -1
    HOLD: Persistent[int] = 0
    signal: PersistentSeries = HOLD
    hp_counter: Persistent[int] = 0
    def cAqua(g):
        return color.new('#0080FF') if g > 9 else color.new('#0080FFE5') if g > 8 else color.new('#0080FFCC') if g > 7 else color.new('#0080FFB2') if g > 6 else color.new('#0080FF99') if g > 5 else color.new('#0080FF7F') if g > 4 else color.new('#0080FF66') if g > 3 else color.new('#0080FF4C') if g > 2 else color.new('#0080FF33') if g > 1 else color.new('#00C0FF19')

    def cPink(g):
        return color.new('#FF0080') if g > 9 else color.new('#FF0080E5') if g > 8 else color.new('#FF0080CC') if g > 7 else color.new('#FF0080B2') if g > 6 else color.new('#FF008099') if g > 5 else color.new('#FF00807F') if g > 4 else color.new('#FF008066') if g > 3 else color.new('#FF00804C') if g > 2 else color.new('#FF008033') if g > 1 else color.new('#FF008019')

    def volumeBreak(thres):
        rsivol = ta.rsi(volume, 14)
        osc = ta.hma(rsivol, 10)
        return osc > thres

    def volatilityBreak(volmin, volmax):
        return ta.atr(volmin) > ta.atr(volmax)

    def dot(v, w, p):
        return math.sum(v * w, p)

    def sigmoid(z):
        return 1.0 / (1.0 + math.exp(-z))

    def logistic_regression(X, Y, p, lr, iterations):
        w: float = 0.0
        loss: float = 0.0
        for i in pine_range(1, iterations, 1):
            hypothesis = sigmoid(dot(X, 0.0, p))
            loss = -1.0 / p * dot(dot(Y, math.log(hypothesis) + 1.0 - Y, p), math.log(1.0 - hypothesis), p)
            gradient = 1.0 / p * dot(X, hypothesis - Y, p)
            w = w - lr * gradient
        return (loss, sigmoid(dot(X, w, p)))

    def minimax(ds, p, min, max):
        hi = ta.highest(ds, p)
        lo = ta.lowest(ds, p)
        return (max - min) * (ds - lo) / (hi - lo) + min

    ds: Series = open if ptype == 'Open' else high if ptype == 'High' else low if ptype == 'Low' else close if ptype == 'Close' else (high + low) / 2 if ptype == 'HL2' else (open + close) / 2 if ptype == 'OC2' else (open + high + low) / 3 if ptype == 'OHL3' else (high + low + close) / 3 if ptype == 'HLC3' else (open + high + low + close) / 4
    base_ds = request.security('', reso, ds[0 if barstate.ishistory else 1])
    synth_ds = math.log(math.abs(math.pow(base_ds, 2) - 1) + 0.5)
    base = time if easteregg else base_ds
    synth = base_ds if easteregg else synth_ds
    loss, prediction = logistic_regression(base, synth, lookback, lrate, iterations)
    scaled_loss = minimax(loss, nlbk, ta.lowest(base_ds, nlbk), ta.highest(base_ds, nlbk))
    scaled_prediction = minimax(prediction, nlbk, ta.lowest(base_ds, nlbk), ta.highest(base_ds, nlbk))
    filter = volatilityBreak(1, 10) if ftype == 'Volatility' else volumeBreak(49) if ftype == 'Volume' else volatilityBreak(1, 10) and volumeBreak(49) if ftype == 'Both' else True
    signal = (SELL if base_ds < scaled_loss and filter else BUY if base_ds > scaled_loss and filter else nz(signal[1])) if useprice else SELL if ta.crossunder(scaled_loss, scaled_prediction) and filter else BUY if ta.crossover(scaled_loss, scaled_prediction) and filter else nz(signal[1])
    changed = ta.change(signal)
    hp_counter = 0 if cast_bool(changed) else hp_counter + 1
    startLongTrade = changed and signal == BUY
    startShortTrade = changed and signal == SELL
    endLongTrade = signal == BUY and hp_counter == holding_p and (not changed) or (changed and signal == SELL)
    endShortTrade = signal == SELL and hp_counter == holding_p and (not changed) or (changed and signal == BUY)
    plot(scaled_loss if curves else na, '', color.new(color.blue, 0), 3)
    plot(scaled_prediction if curves else na, '', color.new(color.lime, 0), 3)
    plotshape(low if startLongTrade else na, 'Buy', shape.labelup, location.belowbar, cAqua(10), size=size.small)
    plotshape(high if startShortTrade else na, 'Sell', shape.labeldown, location.abovebar, cPink(10), size=size.small)
    plot(high if endLongTrade else na, 'StopBuy', cAqua(6), 2, plot.style_cross)
    plot(low if endShortTrade else na, 'StopSell', cPink(6), 2, plot.style_cross)
    alertcondition(startLongTrade, 'Buy', 'Go long!')
    alertcondition(startShortTrade, 'Sell', 'Go short!')
    alertcondition(startLongTrade or startShortTrade, 'Alert', 'Deal Time!')
    ohl3 = (open + high + low) / 3
    start_long_trade: Persistent[float] = 0.0
    long_trades: Persistent[float] = 0.0
    start_short_trade: Persistent[float] = 0.0
    short_trades: Persistent[float] = 0.0
    wins: Persistent[int] = 0
    trade_count: Persistent[int] = 0
    if startLongTrade:
        start_long_trade = ohl3
    if endLongTrade:
        trade_count = 1
        ldiff = ohl3 - start_long_trade
        wins = 1 if ldiff > 0 else 0
        long_trades = ldiff * lot_size
    if startShortTrade:
        start_short_trade = ohl3
    if endShortTrade:
        trade_count = 1
        sdiff = start_short_trade - ohl3
        wins = 1 if sdiff > 0 else 0
        short_trades = sdiff * lot_size
    cumreturn = ta.cum(long_trades) + ta.cum(short_trades)
    totaltrades = ta.cum(trade_count)
    totalwins = ta.cum(wins)
    totallosses = 1 if totaltrades - totalwins == 0 else totaltrades - totalwins
    lbl: PersistentSeries[Label] = na(Label)
    tbase = (time - time[1]) / 1000
    tcurr = (timenow - time_close[1]) / 1000
    info = 'CR=' + string.tostring(cumreturn, '#.#') + '\nTrades: ' + string.tostring(totaltrades, '#') + '\nWin/Loss: ' + string.tostring(totalwins / totallosses, '#.##') + '\nWinrate: ' + string.tostring(totalwins / totaltrades, '#.#%') + '\nBar Time: ' + string.tostring(tcurr / tbase, '#.#%')
    if show_info and barstate.islast:
        lbl = label.new(bar_index, close, info, xloc.bar_index, yloc.price, color.new(color.blue, 100), label.style_label_left, color.black, size.small, text.align_left)
        label.delete(lbl[1])


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)