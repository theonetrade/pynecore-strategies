"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, fill, high, hline, input, location, low, math,
    na, nz, plot, plotshape, script, shape, strategy, string, ta
)
from pynecore.types import Series


@script.strategy(title='RSI Divergence Indicator', overlay=False, pyramiding=2, default_qty_value=2, default_qty_type=strategy.fixed, initial_capital=10000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    len=input.int(title='RSI Period', minval=1, defval=9),
    src: Series[float] = input(title='RSI Source', defval=close),
    lbR=input(title='Pivot Lookback Right', defval=3),
    lbL=input(title='Pivot Lookback Left', defval=1),
    takeProfitRSILevel=input.int(title='Take Profit at RSI Level', minval=70, defval=80),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=True),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False),
    sl_type=input.string('NONE', title='Trailing StopLoss Type', options=('ATR', 'PERC', 'NONE')),
    stopLoss=input.int(title='Stop Loss%', defval=5, minval=1),
    atrLength=input(14, title='ATR Length (for Trailing stop loss)'),
    atrMultiplier=input(3.5, title='ATR Multiplier (for Trailing stop loss)')
):
    bearColor = color.purple
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    osc: Series = ta.rsi(src, len)
    plot(osc, title='RSI', linewidth=2, color=color.new(color.new('#8D1699'), 0))
    hline(50, title='Middle Line', linestyle=hline.style_dotted)
    obLevel = hline(70, title='Overbought', linestyle=hline.style_dotted)
    osLevel = hline(30, title='Oversold', linestyle=hline.style_dotted)
    fill(obLevel, osLevel, title='Background', color=color.new(color.new('#9915FF'), 90))
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(osc[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(osc[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    longCondition = bullCond or hiddenBullCond
    if longCondition:
        strategy.entry(id='RSIDivLE', direction=strategy.long)
    sl_val = stopLoss * ta.atr(atrLength) if sl_type == 'ATR' else close * stopLoss / 100 if sl_type == 'PERC' else 0.0
    trailing_sl: Series[float] = 0.0
    trailing_sl = math.max(low - sl_val, nz(trailing_sl[1])) if strategy.position_size >= 1 else na
    _inRange_3 = _inRange(phFound[1])
    oscLH = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(osc[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(osc[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    longCloseCondition = ta.crossover(osc, takeProfitRSILevel) or bearCond
    if math.abs(strategy.position_size) >= 1 and sl_type == 'NONE' and longCloseCondition:
        strategy.close(id='RSIDivLE', comment='Close All=' + string.tostring(close - strategy.position_avg_price, '####.##'))
    crossunder_1 = ta.crossunder(close, trailing_sl)
    if math.abs(strategy.position_size) >= 1 and (sl_type == 'PERC' or sl_type == 'ATR') and crossunder_1:
        strategy.close(id='RSIDivLE', comment='TSL=' + string.tostring(close - strategy.position_avg_price, '####.##'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
