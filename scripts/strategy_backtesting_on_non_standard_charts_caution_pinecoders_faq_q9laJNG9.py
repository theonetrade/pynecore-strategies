"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barmerge, bgcolor, close, color, high, input, label, location,
    low, math, na, nz, open, plot, plotcandle, plotchar, request, script, size, strategy, string,
    syminfo, ta, ticker, timeframe, xloc, yloc
)
from pynecore.types import Color, Label, NA, Persistent, PersistentSeries, Series

ST1: str = 'Second reversal bar'
ST2: str = 'MA crosses'


@script.strategy('Backtesting on Non-Standard Charts: Caution! [PineCoders]', '', True, precision=8, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strategy__ren__=input.string(ST1, 'Strategy used', options=(ST1, ST2)),
    useHA=input(False, 'Use Heikin Ashi instead of chart prices to calculate strategy'),
    noRepaint=input(True, 'No repainting (delays signals one bar)'),
    showMas=input(False, 'Show MAs'),
    showMarkers=input(False, 'Show entry/exit markers'),
    showFills=input(True, 'Show market fills'),
    showCandles=input(False, 'Show market price candlesticks'),
    showOpen=input(False, 'Show market open as line'),
    showBg=input(False, 'Show background on fill delta'),
    fastLength=input.int(5, 'Fast MA length', minval=2),
    slowLength=input.int(25, 'Slow MA length', minval=3)
):
    def f_roundToTick(_price):
        return math.round(_price / syminfo.mintick) * syminfo.mintick

    def f_round(_val, _decimals):
        _p = math.pow(10, _decimals)
        return math.round(_val * _p) / _p

    ticker__ren__ = ticker.new(syminfo.prefix, syminfo.ticker)
    realOpen = request.security(ticker__ren__, timeframe.period, open, lookahead=barmerge.lookahead_on)
    realHigh = request.security(ticker__ren__, timeframe.period, high, lookahead=barmerge.lookahead_on)
    realLow = request.security(ticker__ren__, timeframe.period, low, lookahead=barmerge.lookahead_on)
    realClose = request.security(ticker__ren__, timeframe.period, close, lookahead=barmerge.lookahead_on)
    haClose_: Series[float] = 0.0
    haOpen_: Series[float] = 0.0
    haClose_ = math.avg(realOpen, realHigh, realLow, realClose)
    haOpen_ = math.avg(nz(haOpen_[1], realOpen), nz(haClose_[1], realClose))
    haHigh_ = math.max(math.max(realHigh, haOpen_), haClose_)
    haLow_ = math.min(math.min(realLow, haOpen_), haClose_)
    haOpen = f_roundToTick(haOpen_)
    haHigh = f_roundToTick(haHigh_)
    haLow = f_roundToTick(haLow_)
    haClose = f_roundToTick(haClose_)
    chartOpen = f_roundToTick(open)
    chartHigh = f_roundToTick(high)
    chartLow = f_roundToTick(low)
    chartClose = f_roundToTick(close)
    calcOpen = haOpen if useHA else chartOpen
    calcClose = haClose if useHA else chartClose
    idx = 1 if noRepaint else 0
    upBar: Series = calcClose > calcOpen
    fastMa = ta.sma(calcClose, fastLength)
    slowMa = ta.sma(calcClose, slowLength)
    longCondition = upBar[idx] and upBar[idx + 1] and (not upBar[idx + 2]) if strategy__ren__ == ST1 else inline_series(ta.crossover(fastMa, slowMa), idx)
    shortCondition = not upBar[idx] and (not upBar[idx + 1]) and upBar[idx + 2] if strategy__ren__ == ST1 else inline_series(ta.crossunder(fastMa, slowMa), idx)
    inLong: Persistent[bool] = False
    goLong: Series[bool] = False
    goShort: Series[bool] = False
    if not inLong and longCondition and (strategy.equity > 0) and (not goShort[1]) and (not na(realOpen)):
        goLong = True
        inLong = True
    if inLong and shortCondition and (strategy.equity > 0) and (not goLong[1]) and (not na(realOpen)):
        goShort = True
        inLong = False
    chartFill: Persistent[float] = na(float)
    marketFill: Persistent[float] = na(float)
    previousChartFill: Persistent[float] = na(float)
    previousMarketFill: Persistent[float] = na(float)
    contracts: PersistentSeries[float] = na(float)
    onOrderBar = goLong or goShort
    onFillBar = goLong[1] or goShort[1]
    if onOrderBar:
        previousChartFill = chartFill
        previousMarketFill = marketFill
        if goLong:
            strategy.entry('Long', strategy.long)
        else:
            if goShort:
                strategy.entry('Short', strategy.short)
    if onFillBar:
        chartFill = strategy.position_avg_price
        marketFill = realOpen
        contracts = math.abs(strategy.position_size)
    marketNetProfit: Persistent[float] = 0.0
    chartProfit: float = 0.0
    chartPctProfit: float = 0.0
    marketProfit: float = 0.0
    marketPctProfit: float = 0.0
    marketTradeProfit: float = 0.0
    if onFillBar and (not na(previousChartFill)):
        chartProfit = (chartFill - previousChartFill) * (1 if goShort[1] else -1)
        chartPctProfit = chartProfit / previousChartFill
        marketProfit = (marketFill - previousMarketFill) * (1 if goShort[1] else -1)
        marketPctProfit = marketProfit / previousMarketFill
        marketTradeProfit = contracts[1] * marketProfit
        marketNetProfit = marketNetProfit + marketTradeProfit
    chartNetProfit = strategy.netprofit
    deltaImpactPct = 100 * (marketNetProfit - chartNetProfit) / math.abs(chartNetProfit)
    def f_color(_val):
        return color.green if _val > 0 else color.red if _val < 0 else color.blue

    invisible: Color = color.new('#00000000')
    plotchar(False, '═══════════ Cumulative Results', '', location.top, invisible)
    plotchar(f_round(chartNetProfit, 2), 'Chart Net Profit', '', location.top, f_color(chartNetProfit))
    plotchar(f_round(marketNetProfit, 2), 'Market Net Profit', '', location.top, f_color(marketNetProfit))
    plotchar(f_round(deltaImpactPct, 2), 'Delta Net Profit %', '', location.top, f_color(deltaImpactPct))
    plotchar(False, '═══════════ Trade Fills', '', location.top, invisible)
    plotchar(previousChartFill if onFillBar else na, 'Chart Previous Fill', '', location.top)
    plotchar(chartFill if onFillBar else na, 'Chart Current Fill', '', location.top)
    plotchar(previousMarketFill if onFillBar else na, 'Market Previous Fill', '', location.top, f_color((previousMarketFill - previousChartFill) * (-1 if goShort[1] else 1)))
    plotchar(marketFill if onFillBar else na, 'Market Current Fill', '', location.top, f_color((marketFill - chartFill) * (1 if goShort[1] else -1)))
    plotchar(False, '═══════════ Trade Results', '', location.top, invisible)
    plotchar(f_round(100 * chartPctProfit, 2) if onFillBar else na, 'Chart Trade Profit %', '', location.top, f_color(chartPctProfit))
    plotchar(f_round(100 * marketPctProfit, 2) if onFillBar else na, 'Market Trade Profit %', '', location.top, f_color(marketPctProfit))
    plotchar(f_round(100 * (marketPctProfit - chartPctProfit), 2) if onFillBar else na, 'Delta Trade Profit %', '', location.top, f_color(marketPctProfit - chartPctProfit))
    plotchar(False, '══════════════════════', '', location.top, invisible)
    plot(fastMa if strategy__ren__ == ST2 and showMas else na, 'Fast MA', color.new(color.fuchsia, 0))
    plot(slowMa if strategy__ren__ == ST2 and showMas else na, 'Slow MA')
    plotchar(showMarkers and goLong, 'goLong', '▲', location.bottom, color.green, size=size.tiny)
    plotchar(showMarkers and goShort, 'goShort', '▼', location.top, color.red, size=size.tiny)
    change_1 = ta.change(marketFill)
    plot(marketFill if showFills and (not change_1) else na, 'Market Fills', color.new(color.gray, 0), style=plot.style_linebr, offset=-1)
    plot(realOpen if showOpen else na, 'Market open', color=color.new(color.gray, 0), linewidth=3, trackprice=True)
    plotcandle(realOpen if showCandles else na, realHigh if showCandles else na, realLow if showCandles else na, realClose if showCandles else na, 'Candles', color.orange if realClose > realOpen else color.fuchsia, color.orange)
    lbl: Persistent = NA(Label)
    label.delete(lbl)
    labelText = 'Chart Net Profit (currency) = ' + string.tostring(chartNetProfit, '###,###,###.00') + '\nMarket Net Profit (currency) = ' + string.tostring(marketNetProfit, '###,###,###.00') + '\nDelta % = ' + string.tostring(deltaImpactPct, '#.##') + ' %'
    labelType = label.style_label_down if deltaImpactPct < 0 else label.style_label_up
    lbl = label.new(bar_index, ta.highest(20), labelText, xloc.bar_index, yloc.price, f_color(deltaImpactPct), size=size.normal, style=labelType)
    bgcolor(color.red if showBg and onFillBar and (chartFill != marketFill) else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
