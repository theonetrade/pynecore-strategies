"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hlc3, hline, input, plot, script, strategy, ta

okay: str = 'Okay'
good: str = 'Good'
veryGood: str = 'Very good'


@script.strategy('Crypto Crew University', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    rsi_length=input.int(14, minval=1),
    mfi_lenght=input.int(14, minval=1),
    smoothK=input.int(3, minval=1),
    smoothD=input.int(3, minval=1),
    lengthRSI=input.int(14, minval=1),
    lengthStoch=input.int(14, minval=1),
    tradingOpportunity=input.string(title='Opportunity', defval=veryGood, options=(okay, good, veryGood))
):
    source = hlc3
    longThreshhold = 40 if tradingOpportunity == okay else 30 if tradingOpportunity == good else 20 if tradingOpportunity == veryGood else 0
    shortThreshhold = 60 if tradingOpportunity == okay else 70 if tradingOpportunity == good else 80 if tradingOpportunity == veryGood else 0
    mfi = ta.mfi(source, mfi_lenght)
    rsi = ta.rsi(source, rsi_length)
    rsi1 = ta.rsi(close, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    longSignal = 1 if mfi < longThreshhold and rsi < longThreshhold and (k < longThreshhold) and (d < longThreshhold) else -1
    shortSignal = 1 if mfi > shortThreshhold and rsi > shortThreshhold and (k > shortThreshhold) and (d > shortThreshhold) else -1
    if longSignal > 0:
        strategy.entry('Long', strategy.long)
        strategy.exit(id='Long Stop Loss', stop=strategy.position_avg_price * 0.8)
    if shortSignal > 0:
        strategy.entry('Short', strategy.short)
        strategy.exit(id='Short Stop Loss', stop=strategy.position_avg_price * 1.2)
    plot(k, color=color.new(color.blue, 0))
    plot(d, color=color.new(color.red, 0))
    plot(rsi, color=color.new(color.yellow, 0))
    plot(mfi, color=color.new(color.blue, 0))
    hline(longThreshhold, color=color.gray, linestyle=hline.style_dashed)
    hline(shortThreshhold, color=color.gray, linestyle=hline.style_dashed)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
