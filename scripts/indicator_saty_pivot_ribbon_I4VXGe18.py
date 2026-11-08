"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, barstate, close, color, fill, high, input, location, low, na,
    open, plot, plotcandle, plotshape, request, script, session, shape, size, syminfo, ta, ticker,
    timeframe
)
from pynecore.types import Series


@script.indicator('Saty Pivot Ribbon', 'Saty Pivot Ribbon', overlay=True, na_bool=True)
def main(
    time_warp=input.string('off', 'Time Warp', options=('off', '1m', '2m', '3m', '4m', '5m', '10m', '15m', '20m', '30m', '1h', '2h', '4h', 'D', 'W', 'M', 'Y')),
    fast_ema=input(title='Fast EMA Length', defval=8),
    pivot_ema=input(title='Pivot EMA Length', defval=21),
    slow_ema=input(title='Slow EMA Length', defval=34),
    bullish_fast_cloud_color=input(color.green, 'Bullish Fast Cloud Color'),
    bearish_fast_cloud_color=input(color.red, 'Bearish Fast Cloud Color'),
    bullish_slow_cloud_color=input(color.aqua, 'Bullish Slow Cloud Color'),
    bearish_slow_cloud_color=input(color.orange, 'Bearish Slow Cloud Color'),
    cloud_transparency=input(title='Cloud Transparency (0-100)', defval=60),
    show_fast_ema_highlight=input(False, 'Show Fast EMA Highlight'),
    fast_ema_highlight_color=input(color.white, 'Fast EMA Highlight Color'),
    show_pivot_ema_highlight=input(False, 'Show Pivot EMA Highlight'),
    pivot_ema_highlight_color=input(color.white, 'Pivot EMA Highlight Color'),
    show_slow_ema_highlight=input(False, 'Show Slow EMA Highlight'),
    slow_ema_highlight_color=input(color.white, 'Slow EMA Highlight Color'),
    show_conviction_arrows=input(True, 'Show Conviction Arrows'),
    bullish_conviction_color=input(color.aqua, 'Bullish Conviction Arrow Color'),
    bearish_conviction_color=input(color.yellow, 'Bearish Conviction Arrow Color'),
    show_fast_conviction_ema=input(True, 'Show Fast Conviction EMA'),
    fast_conviction_ema=input(13, 'Fast Conviction EMA Length'),
    fast_conviction_ema_color=input(color.silver, 'Fast Conviction EMA Color'),
    show_slow_conviction_ema=input(True, 'Show Slow Conviction EMA'),
    slow_conviction_ema=input(48, 'Slow Conviction EMA Length'),
    slow_conviction_ema_color=input(color.purple, 'Slow Conviction EMA Color'),
    show_candle_bias=input(False, 'Show Candle Bias'),
    bias_ema=input(21, 'Bias EMA')
):
    def timeframe_func():
        timeframe__ren__ = timeframe.period
        __block_result__ = na
        if time_warp == 'off':
            timeframe__ren__ = timeframe.period
            __block_result__ = timeframe__ren__
        elif time_warp == '1m':
            timeframe__ren__ = '1'
            __block_result__ = timeframe__ren__
        elif time_warp == '2m':
            timeframe__ren__ = '2'
            __block_result__ = timeframe__ren__
        elif time_warp == '3m':
            timeframe__ren__ = '3'
            __block_result__ = timeframe__ren__
        elif time_warp == '4m':
            timeframe__ren__ = '4'
            __block_result__ = timeframe__ren__
        elif time_warp == '5m':
            timeframe__ren__ = '5'
            __block_result__ = timeframe__ren__
        elif time_warp == '10m':
            timeframe__ren__ = '10'
            __block_result__ = timeframe__ren__
        elif time_warp == '15m':
            timeframe__ren__ = '15'
            __block_result__ = timeframe__ren__
        elif time_warp == '20m':
            timeframe__ren__ = '20'
            __block_result__ = timeframe__ren__
        elif time_warp == '30m':
            timeframe__ren__ = '30'
            __block_result__ = timeframe__ren__
        elif time_warp == '1h':
            timeframe__ren__ = '60'
            __block_result__ = timeframe__ren__
        elif time_warp == '2h':
            timeframe__ren__ = '120'
            __block_result__ = timeframe__ren__
        elif time_warp == '4h':
            timeframe__ren__ = '240'
            __block_result__ = timeframe__ren__
        elif time_warp == 'D':
            timeframe__ren__ = 'D'
            __block_result__ = timeframe__ren__
        elif time_warp == 'W':
            timeframe__ren__ = 'W'
            __block_result__ = timeframe__ren__
        elif time_warp == 'M':
            timeframe__ren__ = 'M'
            __block_result__ = timeframe__ren__
        elif time_warp == 'Y':
            timeframe__ren__ = '12M'
            __block_result__ = timeframe__ren__
        else:
            timeframe__ren__ = timeframe.period
            __block_result__ = timeframe__ren__
        return __block_result__

    ticker__ren__ = ticker.new(syminfo.prefix, syminfo.ticker, session=session.extended)
    price = request.security(ticker__ren__, timeframe_func(), close, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    fast_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, fast_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    pivot_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, pivot_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    slow_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, slow_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    fast_conviction_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, fast_conviction_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    slow_conviction_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, slow_conviction_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    fast_ema_plot = plot(fast_ema_value, color=fast_ema_highlight_color if show_fast_ema_highlight else na, title='Fast EMA')
    pivot_ema_plot = plot(pivot_ema_value, color=pivot_ema_highlight_color if show_pivot_ema_highlight else na, title='Pivot EMA')
    slow_ema_plot = plot(slow_ema_value, color=slow_ema_highlight_color if show_slow_ema_highlight else na, title='Slow EMA')
    fast_cloud_color = color.new(bullish_fast_cloud_color, cloud_transparency) if fast_ema_value >= pivot_ema_value else color.new(bearish_fast_cloud_color, cloud_transparency)
    fill(fast_ema_plot, pivot_ema_plot, color=fast_cloud_color, title='Fast Cloud')
    slow_cloud_color = color.new(bullish_slow_cloud_color, cloud_transparency) if pivot_ema_value >= slow_ema_value else color.new(bearish_slow_cloud_color, cloud_transparency)
    fill(pivot_ema_plot, slow_ema_plot, color=slow_cloud_color, title='Slow Cloud')
    bullish_conviction: Series = fast_conviction_ema_value >= slow_conviction_ema_value
    bearish_conviction: Series = fast_conviction_ema_value < slow_conviction_ema_value
    bullish_conviction_confirmed = bullish_conviction == True and bullish_conviction[1] == False
    bearish_conviction_confirmed = bearish_conviction == True and bearish_conviction[1] == False
    plotshape(bullish_conviction_confirmed and show_conviction_arrows, style=shape.triangleup, color=bullish_conviction_color, location=location.belowbar, size=size.small)
    plotshape(bearish_conviction_confirmed and show_conviction_arrows, style=shape.triangledown, color=bearish_conviction_color, location=location.abovebar, size=size.small)
    fast_conviction_ema_plot = plot(fast_conviction_ema_value, color=fast_conviction_ema_color if show_fast_conviction_ema else na, title='Fast Conviction EMA')
    slow_conviction_ema_plot = plot(slow_conviction_ema_value, color=slow_conviction_ema_color if show_slow_conviction_ema else na, title='Slow Conviction EMA')
    bias_ema_value = request.security(syminfo.tickerid, timeframe_func(), inline_series(ta.ema(price, bias_ema), 1 if barstate.isrealtime else 0), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    above_pivot = close >= bias_ema_value
    below_pivot = close < bias_ema_value
    up = open < close
    doji = open == close
    down = open > close
    bias_candle_color = bullish_fast_cloud_color if above_pivot and up and show_candle_bias else bearish_slow_cloud_color if below_pivot and up and show_candle_bias else bullish_slow_cloud_color if above_pivot and down and show_candle_bias else bearish_fast_cloud_color if below_pivot and down and show_candle_bias else color.gray if doji and show_candle_bias else na
    plotcandle(open, high, low, close, color=bias_candle_color, bordercolor=bias_candle_color, wickcolor=bias_candle_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
