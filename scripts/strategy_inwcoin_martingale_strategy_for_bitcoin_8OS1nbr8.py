"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, input, math, nz, plot, script, strategy, syminfo, ta, time,
    timestamp
)
from pynecore.types import Color, Persistent, Series


@script.strategy('inwCoin Martingale Strategy ( for Bitcoin )', shorttitle='INWCOIN_MARTINGALE_BTC', overlay=True, pyramiding=100, initial_capital=20000, commission_type=strategy.commission.percent, commission_value=0.0, slippage=0, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    price: Series[float] = input(defval=close),
    fixed_position_size_bool=input(False, title='Fixed position size ( Unchecked for percent of initial capital )'),
    start_position_size=input(10.0, title='Start Position Size ( Fixed or Percent )'),
    first_position_logic=input.string(defval='MACD Line > 0', options=('MACD Line > 0', 'STO RSI cross up', 'ATR Channel'), title='Start Position Logic'),
    take_profit_percent=input(5.0, title='Take Profit Percent'),
    martingale_percent=input(10.0, title='Start Martingale if price drop with this Percent'),
    martingale_mult=input(2.0, title='Martingale Multiplier'),
    trade_side=input.string(defval='Long Only', options=('Long Only',), title='Trade direction'),
    use_date_range=input(True),
    FromYear=input.int(defval=2018, title='From Year', minval=1950),
    FromMonth=input.int(defval=1, title='From Month', minval=1),
    FromDay=input.int(defval=1, title='From Day', minval=1),
    ToYear=input.int(defval=9999, title='To Year', minval=1950),
    ToMonth=input.int(defval=1, title='To Month', minval=1),
    ToDay=input.int(defval=1, title='To Day', minval=1)
):
    color_blue: Color = color.new('#0000FF')
    color_green: Color = color.new('#00FF00')
    color_red: Color = color.new('#FF0000')
    color_yellow: Color = color.new('#FFFF00')
    in_date_range = time > timestamp(FromYear, FromMonth, FromDay, 0, 0) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59) if use_date_range else True
    takeProfit = price * take_profit_percent / 100 / syminfo.mintick
    smoothK: int = 3
    smoothD: int = 3
    lengthRSI: int = 14
    lengthStoch: int = 14
    top_line: int = 80
    bottom_line: int = 20
    rsi1 = ta.rsi(price, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    crossover_1 = ta.crossover(d, bottom_line)
    stoBuy = k > bottom_line and crossover_1
    prd1: int = 12
    prd2: int = 26
    AP = ta.ema(price, 2)
    Fast = ta.ema(AP, prd1)
    Slow = ta.ema(AP, prd2)
    ema18 = ta.ema(price, 18)
    Bullish = Fast > Slow
    Bearish = Fast < Slow
    Green: Series = Bullish and AP > Fast
    Red = Bearish and AP < Fast
    Yellow = Bullish and AP < Fast
    Blue = Bearish and AP > Fast
    macdBuy = Green and Green[1] == cast_bool(0)
    SC: Series = price
    AP1: int = 5
    AF1: float = 0.5
    AP2: int = 10
    AF2: float = 2.3
    MUL_Trailing: float = 0.275
    SL1 = AF1 * ta.atr(AP1)
    Trail1: Series[float] = 0.0
    iff_1 = SC - SL1 if SC > nz(Trail1[1], 0) else SC + SL1
    iff_2 = math.min(nz(Trail1[1], 0), SC + SL1) if SC < nz(Trail1[1], 0) and SC[1] < nz(Trail1[1], 0) else iff_1
    Trail1 = math.max(nz(Trail1[1], 0), SC - SL1) if SC > nz(Trail1[1], 0) and SC[1] > nz(Trail1[1], 0) else iff_2
    SL2 = AF2 * ta.atr(AP2)
    SL3 = MUL_Trailing * AF2 * ta.atr(AP2)
    Trail2: Series[float] = 0.0
    iff_3 = SC - SL2 if SC > nz(Trail2[1], 0) else SC + SL2
    iff_4 = math.min(nz(Trail2[1], 0), SC + SL2) if SC < nz(Trail2[1], 0) and SC[1] < nz(Trail2[1], 0) else iff_3
    Trail2 = math.max(nz(Trail2[1], 0), SC - SL2) if SC > nz(Trail2[1], 0) and SC[1] > nz(Trail2[1], 0) else iff_4
    Trail3: Series[float] = 0.0
    iff_5 = SC + SL3 if SC > nz(Trail2[1], 0) else SC + SL3
    iff_6 = math.min(nz(Trail3[1], 0), SC - SL3) if SC < nz(Trail2[1], 0) and SC[1] < nz(Trail2[1], 0) else iff_5
    Trail3 = math.max(nz(Trail3[1], 0), SC + SL3) if SC > nz(Trail2[1], 0) and SC[1] > nz(Trail2[1], 0) else iff_6
    Hst = Trail1 - Trail2
    Sig = ta.ema(Hst, 9)
    atrBlue = Hst < 0 and Hst > Sig
    atrGreen = Hst > 0 and Hst > Sig
    atrGray = Hst > 0 and Hst < Sig
    atrRed = Hst < 0 and Hst < Sig
    atrBull = ta.barssince(atrGreen) < ta.barssince(atrRed)
    atrBear: Series = ta.barssince(atrRed) < ta.barssince(atrGreen)
    atrBuy = atrGreen and atrBear[1]
    Buy: bool = False
    Sell: bool = False
    if first_position_logic == 'MACD Line > 0':
        Buy = macdBuy
    if first_position_logic == 'STO RSI cross up':
        Buy = stoBuy
    if first_position_logic == 'ATR Channel':
        Buy = atrBuy
    pricePercent = (price - strategy.position_avg_price) * 100 / strategy.position_avg_price
    if pricePercent > take_profit_percent:
        Sell = True
    BuyMore = pricePercent <= martingale_percent * -1
    countMartingale: Persistent[float] = 0.0
    startUnitSize: Persistent[float] = 0.0
    unit_size: Persistent[float] = 0.0
    unit_size_martingale: Persistent[float] = 0.0
    if fixed_position_size_bool:
        unit_size = start_position_size
    else:
        unit_size = strategy.equity * (start_position_size / 100) / price
    startUnitSize = unit_size
    unit_size_martingale = startUnitSize * math.pow(martingale_mult, countMartingale)
    liquidate_price: Persistent[float] = 0.0
    current_leverage: Persistent[float] = 0.0
    current_loss: Persistent[float] = 0.0
    current_capital: Persistent[float] = 0.0
    current_capital = strategy.initial_capital + strategy.netprofit
    current_leverage = current_capital / strategy.equity
    liquidate_price = strategy.position_avg_price - strategy.position_avg_price / (current_leverage + 1)
    if Buy and in_date_range and (trade_side == 'Both' or trade_side == 'Long Only') and (countMartingale == 0.0) and (strategy.equity >= 0):
        if strategy.position_size <= 0:
            strategy.entry('Long', strategy.long, qty=unit_size)
        countMartingale = 1
        Sell = False
    if BuyMore and countMartingale > 0:
        if strategy.position_size > 0 and strategy.equity >= 0:
            strategy.entry('Long', strategy.long, qty=unit_size_martingale)
        countMartingale = countMartingale + 1
        Sell = False
    if Sell or strategy.equity <= 0:
        strategy.close('Long')
        countMartingale = 0
    plot(strategy.equity, color=color.new(color.orange, 0))
    plot(strategy.position_avg_price, color=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
