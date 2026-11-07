"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, fill, high, hline, input, location, low, na,
    open, plot, plotshape, request, script, shape, strategy, syminfo, ta, ticker, time, timeframe,
    timestamp
)
from pynecore.types import Color, Series


@script.strategy('[BACKTEST]Traders Dynamic Index Indicator Alert by JustUncleL', shorttitle='[BACKTEST]TDIALT', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    lengthrsi=input(13),
    lengthband=input(34),
    lengthrsipl=input(2),
    lengthtradesl=input(7),
    lenH=input.int(5, minval=1, title='Price Action Channel Length'),
    rsiOSL=input.int(22, minval=0, maxval=49, title='RSI Oversold Level'),
    rsiOBL=input.int(78, minval=51, maxval=100, title='RSI Overbought Level'),
    strength=input.int(2, minval=1, maxval=3, step=1, title='Strength Level: (1)Strong (2)Medium (3)All'),
    sgb=input(False, title='Check Box To Turn Bars Gray'),
    sbr=input(True, title='Highlight TDI Alert Bars'),
    sal=input(True, title='Show Alert Condition Status'),
    uha=input(False, title='Use Heikin Ashi Candles for Calculations'),
    umacd=input(False, title='Use MACD Filtering'),
    fastMA=input.int(title='MACD Fast MA Length', defval=8, minval=2),
    slowMA=input.int(title='MACD Slow MA Length', defval=16, minval=7),
    signal=input.int(title='MACD Signal Length', defval=1, minval=1),
    tradeType=input.string('BOTH', title='What trades should be taken : ', options=('LONG', 'SHORT', 'BOTH', 'NONE')),
    slPoints=input.int(defval=0, title='Initial Stop Loss Points (zero to disable)', minval=0),
    tpPoints=input.int(defval=0, title='Initial Target Profit Points (zero for disable)', minval=0),
    testStartYear=input.int(2018, 'Backtest Start Year', minval=1980),
    testStartMonth=input.int(1, 'Backtest Start Month', minval=1, maxval=12),
    testStartDay=input.int(1, 'Backtest Start Day', minval=1, maxval=31),
    testStopYear=input.int(9999, 'Backtest Stop Year', minval=1980),
    testStopMonth=input.int(12, 'Backtest Stop Month', minval=1, maxval=12),
    testStopDay=input.int(31, 'Backtest Stop Day', minval=1, maxval=31)
):
    lenL = lenH
    blue100: Color = color.new('#0000FF')
    aqua100: Color = color.new('#00FFFF')
    fuchsia100: Color = color.new('#FF00FF')
    purple100: Color = color.new('#800080')
    gray100: Color = color.new('#808080')
    gold100: Color = color.new('#FFD700')
    white100: Color = color.new('#FFFFFF')
    black100: Color = color.new('#000000')
    gold: Color = color.new('#FFD700')
    security_1 = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
    security_2 = request.security(syminfo.ticker, timeframe.period, close)
    srcClose = security_1 if uha else security_2
    security_3 = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open)
    security_4 = request.security(syminfo.ticker, timeframe.period, open)
    srcOpen = security_3 if uha else security_4
    security_5 = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high)
    security_6 = request.security(syminfo.ticker, timeframe.period, high)
    srcHigh = security_5 if uha else security_6
    security_7 = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low)
    security_8 = request.security(syminfo.ticker, timeframe.period, low)
    srcLow = security_7 if uha else security_8
    r = ta.rsi(srcClose, lengthrsi)
    ma = ta.sma(r, lengthband)
    offs = 1.6185 * ta.stdev(r, lengthband)
    upZone = ma + offs
    dnZone = ma - offs
    mid = (upZone + dnZone) / 2
    mab = ta.sma(r, lengthrsipl)
    mbb = ta.sma(r, lengthtradesl)
    hline(rsiOSL, color=color.red, linewidth=1)
    hline(50, color=color.black, linewidth=1)
    hline(rsiOBL, color=color.lime, linewidth=1)
    upl = plot(upZone, color=color.new(color.blue, 0), title='VB Channel High', linewidth=2)
    dnl = plot(dnZone, color=color.new(color.blue, 0), title='VB Channel Low', linewidth=2)
    midl = plot(mid, color=color.new(color.orange, 0), linewidth=2, title='MBL')
    mabl = plot(mab, color=color.new(color.green, 0), linewidth=2, title='RSI PL')
    mbbl = plot(mbb, color=color.new(color.red, 0), linewidth=2, title='TSL Signal')
    fill(mabl, mbbl, color=color.new(color.green if mab > mbb else color.red, 90))
    smmaH: Series[float] = 0.0
    smmaL: Series[float] = 0.0
    sma_1 = ta.sma(srcHigh, lenH)
    smmaH = sma_1 if na(smmaH[1]) else (smmaH[1] * (lenH - 1) + srcHigh) / lenH
    sma_2 = ta.sma(srcLow, lenL)
    smmaL = sma_2 if na(smmaL[1]) else (smmaL[1] * (lenL - 1) + srcLow) / lenL
    currMacd, _, _ = ta.macd(srcClose, fastMA, slowMA, signal)
    rising_1 = ta.rising(currMacd, 2)
    falling_1 = ta.falling(currMacd, 2)
    macdH = (color.green if rising_1 else color.red) if currMacd > 0 else color.red if falling_1 else color.green
    long: Series = (1 if mbb > mid else 2 if mab > mid and mbb < mid else 3 if mab < mid and mbb < mid else 0) if (not umacd or macdH == color.green) and mab > mbb and (mab < rsiOBL) and (mab > rsiOSL) and (srcHigh > smmaH) and (srcClose > srcOpen) else 0
    short: Series = (1 if mbb < mid else 2 if mab < mid and mbb > mid else 3 if mab > mid and mbb > mid else 0) if (not umacd or macdH == color.red) and mab < mbb and (mab < rsiOBL) and (mab > rsiOSL) and (srcLow < smmaL) and (srcClose < srcOpen) else 0
    bcolor = na if not sbr else gold100 if long == 1 else aqua100 if long == 2 and strength > 1 else blue100 if long == 3 and strength > 2 else fuchsia100 if short == 1 else purple100 if short == 2 and strength > 1 else black100 if short == 3 and strength > 2 else gray100 if sgb else na
    barcolor(color=bcolor, title='Bars Colours')
    longCond: Series = long > 0 and long != long[1] and (long <= strength)
    shortCond: Series = short > 0 and short != short[1] and (short <= strength)
    plotshape(sal and (longCond[1] or shortCond[1]), title='Alert Indicator', location=location.bottom, color=gold if long[1] == 1 else color.aqua if long[1] == 2 else color.blue if long[1] == 3 else color.fuchsia if short[1] == 1 else color.purple if short[1] == 2 else color.black if short[1] == 3 else na, style=shape.circle, offset=-1)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    TP = tpPoints if tpPoints > 0 else na
    SL = slPoints if slPoints > 0 else na
    if testPeriod() and tradeType != 'NONE':
        if longCond == True and tradeType != 'SHORT':
            strategy.entry('long', strategy.long)
        if shortCond == True and tradeType != 'LONG':
            strategy.entry('short', strategy.short)
        if shortCond == True and tradeType == 'LONG':
            strategy.close('long')
        if longCond == True and tradeType == 'SHORT':
            strategy.close('short')
        strategy.exit('XL', from_entry='long', profit=TP, loss=SL)
        strategy.exit('XS', from_entry='short', profit=TP, loss=SL)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
