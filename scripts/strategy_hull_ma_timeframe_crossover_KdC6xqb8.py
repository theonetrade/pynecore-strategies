"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, color, input, label, math, na, nz, open, plot, request, script,
    strategy, syminfo, ta
)
from pynecore.types import Series

stfu: str = 'Select Time Frame for Candle crossover (close>close[1]=buy else sell)'
ptt: str = 'Recommended to use OPEN as source to avoid repainting (OPEN is a set value each candle, where as a CLOSE value changes with each tick for the duration of the candle)'
masmthng: str = 'Select type of Moving Average'
prdtt: str = 'Amount of candles back to use with calculation'
atrsnstt: str = 'Basicly, adjusts ATR SL distance from candles'
tph: str = 'Close order when user set % in Profit'
slh: str = 'Close order when user set % in Loss'
btt: str = 'If selected, Buying is allowed'
stt: str = 'If selected, Selling is allowed'
uatrh: str = 'If selected, StopLoss will be the ATR line'


@script.strategy('HullTimeFrameCrossOver', shorttitle='H&TF', overlay=True, currency='BTC', initial_capital=1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_value=0.1, commission_type=strategy.commission.percent, margin_long=0, margin_short=0, close_by_id=True)
def main(
    res=input.timeframe(title='Candle X Resolution', defval='D', tooltip=stfu),
    price: Series[float] = input(title='Source of Price', defval=open, tooltip=ptt),
    smoothing=input.string(title='Moving Average Type', defval='HMA', options=('ALMA', 'SMA', 'EMA', 'WMA', 'HMA'), tooltip=masmthng),
    MA_Period=input.int(title='Moving Average Period', defval=1000, minval=3, tooltip=prdtt),
    atrsens=input.float(14, title='ATR sensitivity', tooltip=atrsnstt),
    atrperiod=input.int(14, title='ATR Period', tooltip=prdtt),
    TakeProfit=input(title='Take Profit (%)', defval=1000, tooltip=tph),
    StopLoss=input(title='StopLoss (%)', defval=1000, tooltip=slh),
    UseATRSL=input.bool(defval=False, title='Use ATR SL?', tooltip=uatrh),
    AllowBuy=input.bool(defval=True, title='Allow Buy?', tooltip=btt),
    AllowSell=input.bool(defval=True, title='Allow Sell?', tooltip=stt)
):
    balance = strategy.initial_capital + strategy.netprofit
    TP = TakeProfit / 100 * balance
    SL = StopLoss / 100 * balance - StopLoss / 100 * balance * 2
    def ma_function(price, MA_Period):
        __block_result__ = na
        __switch__ = smoothing
        if __switch__ == 'ALMA':
            __block_result__ = ta.alma(price, MA_Period, 0.85, 6)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(price, MA_Period)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(price, MA_Period)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(price, MA_Period)
        else:
            __block_result__ = ta.hma(price, MA_Period)
        return __block_result__

    ma = ma_function(price, MA_Period)
    ma0 = ma_function(price, 2)
    ma1 = ma_function(price, MA_Period)
    ma2 = ma_function(price[1], MA_Period)
    D1 = request.security(syminfo.tickerid, res, price, barmerge.gaps_off, barmerge.lookahead_off)
    xATR = ta.atr(atrperiod)
    nLoss = atrsens * xATR
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = price - nLoss if price > nz(xATRTrailingStop[1], 0) else price + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), price + nLoss) if price < nz(xATRTrailingStop[1], 0) and price[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), price - nLoss) if price > nz(xATRTrailingStop[1], 0) and price[1] > nz(xATRTrailingStop[1], 0) else iff_2
    pos: Series[int] = 0
    iff_3 = -1 if price[1] > nz(xATRTrailingStop[1], 0) and price < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if price[1] < nz(xATRTrailingStop[1], 0) and price > nz(xATRTrailingStop[1], 0) else iff_3
    above = ta.crossover(ma, xATRTrailingStop)
    below = ta.crossover(xATRTrailingStop, ma)
    longCondition = ma1 > ma2 and ma0 > D1 and (ma0 > ma1)
    shortCondition = ma1 < ma2 and ma0 < D1 and (ma0 < ma1)
    clr1 = color.green if price > D1 else color.red
    clr2 = color.red if ma1 > ma2 else color.green
    plot(ma1 if ta.cross(ma1, ma2) else na, label.style_cross, color=clr2, linewidth=3)
    plot(ma1 if ta.cross(ma1, D1) else na, label.style_cross, color=clr1, linewidth=3)
    plot(D1, color=clr1, title='C_X', linewidth=2)
    plot(xATRTrailingStop, color=color.black, title='ATR SL', linewidth=3)
    if strategy.openprofit > TP:
        strategy.close('buy', comment='buy TP', alert_message='buy TP')
    if strategy.openprofit < SL:
        strategy.close('buy', comment='buy SL', alert_message='buy SL')
    if strategy.openprofit > TP:
        strategy.close('sell', comment='sell TP', alert_message='sell TP')
    if strategy.openprofit < SL:
        strategy.close('sell', comment='sell SL', alert_message='sell SL')
    if UseATRSL:
        if price > xATRTrailingStop and above or (price < xATRTrailingStop and below):
            strategy.close_all(comment='ATR SL', alert_message='ATR SL')
    if AllowBuy and longCondition and above:
        strategy.entry('buy', strategy.long, comment='buy', alert_message='buy')
    if AllowSell and shortCondition and below:
        strategy.entry('sell', strategy.short, comment='sell', alert_message='sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
