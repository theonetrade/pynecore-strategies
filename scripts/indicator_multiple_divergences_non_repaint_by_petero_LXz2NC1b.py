"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fixnan, high, input, location, low, na, plotshape, script,
    shape, syminfo, ta, volume
)
from pynecore.types import Series


@script.indicator('Multiple divergences rework NON-REPAINT by PeterO', overlay=True, na_bool=True)
def main(
    offset=input(False, 'Repaint or not?'),
    mindivcount=input.int(2, minval=1, maxval=10, title='Minimum Div Count to Display'),
    lbR=input(title='Pivot Lookback Right', defval=1),
    lbL=input(title='Pivot Lookback Left', defval=3),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=1),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=True),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=True),
    calcmacd=input(True, title='MACD'),
    calcmacda=input(True, title='MACD Histogram'),
    calcrsi=input(True, title='RSI'),
    calcstoc=input(True, title='Stochastic'),
    calccci=input(True, title='CCI'),
    calcmom=input(True, title='Momentum'),
    calcobv=input(True, title='OBV'),
    calcdi=input(True, title='Diosc'),
    calcvwmacd=input(True, title='VWmacd'),
    calccmf=input(True, title='Chaikin Money Flow')
):
    off = lbR if offset else 0
    rsi = ta.rsi(close, 14)
    macd, signal, deltamacd = ta.macd(close, 12, 26, 9)
    moment = ta.mom(close, 10)
    cci = ta.cci(close, 10)
    obv = ta.cum(volume if ta.change(close) > 0 else -volume if ta.change(close) < 0 else 0 * volume)
    stk = ta.sma(ta.stoch(close, high, low, 14), 3)
    DI = ta.change(high) - -ta.change(low)
    trur = ta.rma(ta.tr, 14)
    diosc = fixnan(100 * ta.rma(DI, 14) / trur)
    maFast = ta.vwma(close, 12)
    maSlow = ta.vwma(close, 26)
    vwmacd = maFast - maSlow
    Cmfm = (close - low - (high - close)) / (high - low)
    Cmfv = Cmfm * volume
    cmf = ta.sma(Cmfv, 21) / ta.sma(volume, 21)
    def plFound(_osc):
        return not na(ta.pivotlow(_osc, lbL, lbR))

    def phFound(_osc):
        return not na(ta.pivothigh(_osc, lbL, lbR))

    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    def oscHL(_osc: Series):
        plFound_1: Series = plFound(_osc)
        _inRange_1 = _inRange(plFound_1[1])
        return _osc[lbR] > ta.valuewhen(plFound(_osc), _osc[lbR], 1) and _inRange_1

    def priceLL(_osc):
        return low[lbR] < ta.valuewhen(plFound(_osc), low[lbR], 1)

    def bullCond(_osc):
        priceLL_1 = priceLL(_osc)
        oscHL_1 = oscHL(_osc)
        plFound_1 = plFound(_osc)
        return plotBull and priceLL_1 and oscHL_1 and plFound_1

    def oscLH(_osc: Series):
        phFound_1: Series = phFound(_osc)
        _inRange_1 = _inRange(phFound_1[1])
        return _osc[lbR] < ta.valuewhen(phFound(_osc), _osc[lbR], 1) and _inRange_1

    def priceHH(_osc):
        return high[lbR] > ta.valuewhen(phFound(_osc), high[lbR], 1)

    def bearCond(_osc):
        priceHH_1 = priceHH(_osc)
        oscLH_1 = oscLH(_osc)
        phFound_1 = phFound(_osc)
        return plotBear and priceHH_1 and oscLH_1 and phFound_1

    def oscLL(_osc: Series):
        plFound_1: Series = plFound(_osc)
        _inRange_1 = _inRange(plFound_1[1])
        return _osc[lbR] < ta.valuewhen(plFound(_osc), _osc[lbR], 1) and _inRange_1

    def priceHL(_osc):
        return low[lbR] > ta.valuewhen(plFound(_osc), low[lbR], 1)

    def hiddenBullCond(_osc):
        priceHL_1 = priceHL(_osc)
        oscLL_1 = oscLL(_osc)
        plFound_1 = plFound(_osc)
        return plotHiddenBull and priceHL_1 and oscLL_1 and plFound_1

    def oscHH(_osc: Series):
        phFound_1: Series = phFound(_osc)
        _inRange_1 = _inRange(phFound_1[1])
        return _osc[lbR] > ta.valuewhen(phFound(_osc), _osc[lbR], 1) and _inRange_1

    def priceLH(_osc):
        return high[lbR] < ta.valuewhen(phFound(_osc), high[lbR], 1)

    def hiddenBearCond(_osc):
        priceLH_1 = priceLH(_osc)
        oscHH_1 = oscHH(_osc)
        phFound_1 = phFound(_osc)
        return plotHiddenBear and priceLH_1 and oscHH_1 and phFound_1

    negdivergence: int = 0
    bearCond_1 = bearCond(rsi)
    if calcrsi and bearCond_1:
        negdivergence = 1
    bearCond_2 = bearCond(macd)
    if calcmacd and bearCond_2:
        negdivergence = negdivergence + 1
    bearCond_3 = bearCond(deltamacd)
    if calcmacda and bearCond_3:
        negdivergence = negdivergence + 1
    bearCond_4 = bearCond(moment)
    if calcmom and bearCond_4:
        negdivergence = negdivergence + 1
    bearCond_5 = bearCond(cci)
    if calccci and bearCond_5:
        negdivergence = negdivergence + 1
    bearCond_6 = bearCond(obv)
    if calcobv and bearCond_6:
        negdivergence = negdivergence + 1
    bearCond_7 = bearCond(stk)
    if calcstoc and bearCond_7:
        negdivergence = negdivergence + 1
    bearCond_8 = bearCond(diosc)
    if calcdi and bearCond_8:
        negdivergence = negdivergence + 1
    bearCond_9 = bearCond(vwmacd)
    if calcvwmacd and bearCond_9:
        negdivergence = negdivergence + 1
    bearCond_10 = bearCond(cmf)
    if calccmf and bearCond_10:
        negdivergence = negdivergence + 1
    posdivergence: int = 0
    bullCond_1 = bullCond(rsi)
    if calcrsi and bullCond_1:
        posdivergence = 1
    bullCond_2 = bullCond(macd)
    if calcmacd and bullCond_2:
        posdivergence = posdivergence + 1
    bullCond_3 = bullCond(deltamacd)
    if calcmacda and bullCond_3:
        posdivergence = posdivergence + 1
    bullCond_4 = bullCond(moment)
    if calcmom and bullCond_4:
        posdivergence = posdivergence + 1
    bullCond_5 = bullCond(cci)
    if calccci and bullCond_5:
        posdivergence = posdivergence + 1
    bullCond_6 = bullCond(obv)
    if calcobv and bullCond_6:
        posdivergence = posdivergence + 1
    bullCond_7 = bullCond(stk)
    if calcstoc and bullCond_7:
        posdivergence = posdivergence + 1
    bullCond_8 = bullCond(diosc)
    if calcdi and bullCond_8:
        posdivergence = posdivergence + 1
    bullCond_9 = bullCond(vwmacd)
    if calcvwmacd and bullCond_9:
        posdivergence = posdivergence + 1
    bullCond_10 = bullCond(cmf)
    if calccmf and bullCond_10:
        posdivergence = posdivergence + 1
    negdivergencehidden: int = 0
    hiddenBearCond_1 = hiddenBearCond(rsi)
    if calcrsi and hiddenBearCond_1:
        negdivergencehidden = 1
    hiddenBearCond_2 = hiddenBearCond(macd)
    if calcmacd and hiddenBearCond_2:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_3 = hiddenBearCond(deltamacd)
    if calcmacda and hiddenBearCond_3:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_4 = hiddenBearCond(moment)
    if calcmom and hiddenBearCond_4:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_5 = hiddenBearCond(cci)
    if calccci and hiddenBearCond_5:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_6 = hiddenBearCond(obv)
    if calcobv and hiddenBearCond_6:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_7 = hiddenBearCond(stk)
    if calcstoc and hiddenBearCond_7:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_8 = hiddenBearCond(diosc)
    if calcdi and hiddenBearCond_8:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_9 = hiddenBearCond(vwmacd)
    if calcvwmacd and hiddenBearCond_9:
        negdivergencehidden = negdivergencehidden + 1
    hiddenBearCond_10 = hiddenBearCond(cmf)
    if calccmf and hiddenBearCond_10:
        negdivergencehidden = negdivergencehidden + 1
    posdivergencehidden: int = 0
    hiddenBullCond_1 = hiddenBullCond(rsi)
    if calcrsi and hiddenBullCond_1:
        posdivergencehidden = 1
    hiddenBullCond_2 = hiddenBullCond(macd)
    if calcmacd and hiddenBullCond_2:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_3 = hiddenBullCond(deltamacd)
    if calcmacda and hiddenBullCond_3:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_4 = hiddenBullCond(moment)
    if calcmom and hiddenBullCond_4:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_5 = hiddenBullCond(cci)
    if calccci and hiddenBullCond_5:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_6 = hiddenBullCond(obv)
    if calcobv and hiddenBullCond_6:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_7 = hiddenBullCond(stk)
    if calcstoc and hiddenBullCond_7:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_8 = hiddenBullCond(diosc)
    if calcdi and hiddenBullCond_8:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_9 = hiddenBullCond(vwmacd)
    if calcvwmacd and hiddenBullCond_9:
        posdivergencehidden = posdivergencehidden + 1
    hiddenBullCond_10 = hiddenBullCond(cmf)
    if calccmf and hiddenBullCond_10:
        posdivergencehidden = posdivergencehidden + 1
    voffset = 5 * syminfo.mintick
    plotshape(low[lbR] - voffset if posdivergence == 1 and mindivcount < 2 else na, offset=-off, title='1 Regular Bullish Div found', text='1', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 2 and mindivcount < 3 else na, offset=-off, title='2 Regular Bullish Divs found', text='2', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 3 and mindivcount < 4 else na, offset=-off, title='3 Regular Bullish Divs found', text='3', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 4 and mindivcount < 5 else na, offset=-off, title='4 Regular Bullish Divs found', text='4', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 5 and mindivcount < 6 else na, offset=-off, title='5 Regular Bullish Divs found', text='5', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 6 and mindivcount < 7 else na, offset=-off, title='6 Regular Bullish Divs found', text='6', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 7 and mindivcount < 8 else na, offset=-off, title='7 Regular Bullish Divs found', text='7', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence == 8 and mindivcount < 9 else na, offset=-off, title='8 Regular Bullish Divs found', text='8', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergence > 8 and mindivcount < 11 else na, offset=-off, title='8+ Regular Bullish Divs found', text='8+', style=shape.labelup, location=location.absolute, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 1 and mindivcount < 2 else na, offset=-off, title='1 Regular Bearish Div found', text='1', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 2 and mindivcount < 3 else na, offset=-off, title='2 Regular Bearish Divs found', text='2', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 3 and mindivcount < 4 else na, offset=-off, title='3 Regular Bearish Divs found', text='3', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 4 and mindivcount < 5 else na, offset=-off, title='4 Regular Bearish Divs found', text='4', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 5 and mindivcount < 6 else na, offset=-off, title='5 Regular Bearish Divs found', text='5', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 6 and mindivcount < 7 else na, offset=-off, title='6 Regular Bearish Divs found', text='6', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 7 and mindivcount < 8 else na, offset=-off, title='7 Regular Bearish Divs found', text='7', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence == 8 and mindivcount < 9 else na, offset=-off, title='8 Regular Bearish Divs found', text='8', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergence > 8 and mindivcount < 11 else na, offset=-off, title='8+ Regular Bearish Divs found', text='8+', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 1 and mindivcount < 2 else na, offset=-off, title='1 Hidden Bullish Div found', text='1', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 2 and mindivcount < 3 else na, offset=-off, title='2 Hidden Bullish Divs found', text='2', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 3 and mindivcount < 4 else na, offset=-off, title='3 Hidden Bullish Divs found', text='3', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 4 and mindivcount < 5 else na, offset=-off, title='4 Hidden Bullish Divs found', text='4', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 5 and mindivcount < 6 else na, offset=-off, title='5 Hidden Bullish Divs found', text='5', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 6 and mindivcount < 7 else na, offset=-off, title='6 Hidden Bullish Divs found', text='6', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 7 and mindivcount < 8 else na, offset=-off, title='7 Hidden Bullish Divs found', text='7', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden == 8 and mindivcount < 9 else na, offset=-off, title='8 Hidden Bullish Divs found', text='8', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(low[lbR] - voffset if posdivergencehidden > 8 and mindivcount < 11 else na, offset=-off, title='8+ Hidden Bullish Divs found', text='8+', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 1 and mindivcount < 2 else na, offset=-off, title='1 Hidden Bearish Div found', text='1', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 2 and mindivcount < 3 else na, offset=-off, title='2 Hidden Bearish Divs found', text='2', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 3 and mindivcount < 4 else na, offset=-off, title='3 Hidden Bearish Divs found', text='3', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 4 and mindivcount < 5 else na, offset=-off, title='4 Hidden Bearish Divs found', text='4', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 5 and mindivcount < 6 else na, offset=-off, title='5 Hidden Bearish Divs found', text='5', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 6 and mindivcount < 7 else na, offset=-off, title='6 Hidden Bearish Divs found', text='6', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 7 and mindivcount < 8 else na, offset=-off, title='7 Hidden Bearish Divs found', text='7', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden == 8 and mindivcount < 9 else na, offset=-off, title='8 Hidden Bearish Divs found', text='8', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))
    plotshape(high[lbR] + voffset if negdivergencehidden > 8 and mindivcount < 11 else na, offset=-off, title='8+ Hidden Bearish Divs found', text='8+', style=shape.labeldown, location=location.absolute, color=color.new(color.orange, 0), textcolor=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
