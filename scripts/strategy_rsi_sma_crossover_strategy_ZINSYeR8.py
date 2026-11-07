"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, hline, input, plot, script, strategy, ta


@script.strategy('RSI Crossover Strategy', shorttitle='RSI Cross', default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=1000, calc_on_every_tick=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    rsiLength=input(title='RSI Length', defval=50),
    smaLength=input(title='SMA Length', defval=25)
):
    rsi = ta.rsi(close, rsiLength)
    sma = ta.sma(rsi, smaLength)
    plotColor = color.green if rsi > sma else color.red
    rsiPlot = plot(rsi, color=color.new(plotColor, 0), title='RSI')
    smaPlot = plot(sma, color=color.new(color.black, 0), title='SMA')
    fillColor = color.lime if rsi > sma else color.red
    fill(rsiPlot, smaPlot, color=color.new(fillColor, 75))
    oversoldLine = hline(30, title='Oversold level')
    overboughtLine = hline(70, title='Overbought level')
    buy = ta.crossover(rsi, sma)
    sell = ta.crossunder(rsi, sma)
    if buy == True:
        strategy.entry('Long', strategy.long, comment='Buy')
    if sell == True:
        strategy.close('Long', comment='Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
