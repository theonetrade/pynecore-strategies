"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, math, na, plot, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy(title='RSI and Smoothed RSI Bull Div Strategy [BigBitsIO]', shorttitle='RSI and Smoothed RSI Bull Div Strategy [BigBitsIO]', overlay=True, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, slippage=0, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    TakeProfitPercent=input.float(3, title='Take Profit %', step=0.25),
    StopLossPercent=input.float(1.75, title='Stop Loss %', step=0.25),
    RSICurve=input.int(14, title='RSI Lookback Period', step=1),
    BuyBelowTargetPercent=input.float(0, title='Buy Below Lowest Low In RSI Divergence Lookback Target %', step=0.05),
    BuyBelowTargetSource: Series[float] = input(close, title='Source of Buy Below Target Price'),
    SRSICurve=input.int(10, title='Smoothed RSI Lookback Period', step=1),
    RSICurrentlyBelow=input.int(30, title='RSI Currently Below', step=1),
    RSIDivergenceLookback=input.int(25, title='RSI Divergence Lookback Period', step=1),
    RSILowestInDivergenceLookbackCurrentlyBelow=input.int(25, title='RSI Lowest In Divergence Lookback Currently Below', step=1),
    RSISellAbove=input.int(65, title='RSI Sell Above', step=1),
    MinimumSRSIDownTrend=input.int(3, title='Minimum SRSI Downtrend Length', step=1),
    SRSICurrentlyBelow=input.int(35, title='Smoothed RSI Currently Below', step=1),
    PlotTarget=input(False, title='Plot Target')
):
    RSI = ta.rsi(close, RSICurve)
    SRSI: Series = ta.wma(2 * ta.wma(RSI, SRSICurve / 2) - ta.wma(RSI, SRSICurve), math.round(math.sqrt(SRSICurve)))
    SRSITrendDownLength: Series[int] = 0
    if SRSI < SRSI[1]:
        SRSITrendDownLength = SRSITrendDownLength[1] + 1
    ProfitTarget = close * (TakeProfitPercent / 100) / syminfo.mintick
    LossTarget = close * (StopLossPercent / 100) / syminfo.mintick
    BuyBelowTarget = BuyBelowTargetSource[ta.lowestbars(RSI, RSIDivergenceLookback) * -1] - BuyBelowTargetSource[ta.lowestbars(RSI, RSIDivergenceLookback) * -1] * (BuyBelowTargetPercent / 100)
    plot(BuyBelowTarget if PlotTarget else na)
    lowest_1 = ta.lowest(SRSI, RSIDivergenceLookback)
    lowest_2 = ta.lowest(RSI, RSIDivergenceLookback)
    IsABuy: bool = RSI < RSICurrentlyBelow and SRSI < SRSICurrentlyBelow and (lowest_1 < RSILowestInDivergenceLookbackCurrentlyBelow) and (BuyBelowTargetSource < BuyBelowTarget) and (SRSITrendDownLength >= MinimumSRSIDownTrend) and (RSI > lowest_2)
    IsASell: bool = RSI > RSISellAbove
    if IsABuy:
        strategy.entry('Positive Trend', strategy.long)
        strategy.exit('Take Profit or Stop Loss', 'Positive Trend', profit=ProfitTarget, loss=LossTarget)
    if IsASell:
        strategy.close('Positive Trend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
