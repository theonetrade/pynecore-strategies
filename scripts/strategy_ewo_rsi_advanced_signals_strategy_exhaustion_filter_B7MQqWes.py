"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, close, color, currency, high, hl2, hlc3, input, location, math,
    na, plot, plotshape, script, shape, size, strategy, string, ta, volume
)
from pynecore.types import Persistent, Series


@script.strategy("EWO,RSI advanced Signals Strategy - Exhaustion Filter[Pridarasx]", overlay=True, initial_capital=10000, currency=currency.USD)
def main(
    ewo_fast=input.int(5, title="EWO Fast"),
    ewo_slow=input.int(34, title="EWO Slow"),
    rsi_len=input.int(14, title="RSI Length"),
    mfi_len=input.int(14, title="MFI Length"),
    vol_ma_len=input.int(20, title="Volume MA Length"),
    lookback_len=input.int(10, title="Breakout Lookback Bars", tooltip="Requires price to break the highest high of this many bars before buying to avoid falling knives."),
    rsi_oversold=input.int(30, title="Exhaustion RSI Level", tooltip="The deep oversold level that triggers a potential trend reset zone."),
    alert_pre_buy=input.bool(True, title="Alert: Pre-Buy Signal", group="Alert Settings"),
    alert_buy=input.bool(True, title="Alert: BUY NOW Signal", group="Alert Settings"),
    alert_pre_sell=input.bool(True, title="Alert: Pre-Sell Signal", group="Alert Settings"),
    alert_sell=input.bool(True, title="Alert: SELL NOW Signal", group="Alert Settings"),
    alert_entry=input.bool(True, title="Alert: Strategy Entry", group="Alert Settings"),
    alert_exit=input.bool(True, title="Alert: Strategy Exit", group="Alert Settings")
):
    ewo: Series = ta.sma(hl2, ewo_fast) - ta.sma(hl2, ewo_slow)

    rsi = ta.rsi(close, rsi_len)

    mfi = ta.mfi(hlc3, mfi_len)

    vol_ma = ta.sma(volume, vol_ma_len)
    vol_ok = volume > vol_ma * 0.8

    oversold_zone: Persistent[bool] = False
    if rsi < rsi_oversold:
        oversold_zone = True

    breakout_barrier = inline_series(ta.highest(high, lookback_len), 1)
    price_breaking_out = close > breakout_barrier

    pre_buy = rsi < 40 and ewo > ewo[1] and (ewo < 0)

    raw_buy = ta.crossover(rsi, 40) and mfi > 30 and (ewo > ewo[1]) and vol_ok and (price_breaking_out or oversold_zone)

    pre_sell = rsi > 60 and ewo < ewo[1] and (ewo > 0)

    raw_sell = ta.crossunder(rsi, 60) and mfi < 70 and (ewo < ewo[1]) and vol_ok

    if raw_buy:
        oversold_zone = False

    last_signal: Persistent[int] = 0

    buy_signal: bool = False
    sell_signal: bool = False

    if raw_buy and last_signal != 1:
        buy_signal = True
        last_signal = 1

    if raw_sell and last_signal != -1:
        sell_signal = True
        last_signal = -1

    if buy_signal:
        strategy.entry('Long', strategy.long, alert_message='EWO/RSI Strategy: BUY NOW - Long Entry Triggered. Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | EWO: ' + string.tostring(ewo, '#.###'))

    if sell_signal:
        strategy.entry('Short', strategy.short, alert_message='EWO/RSI Strategy: SELL NOW - Short Entry Triggered. Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | EWO: ' + string.tostring(ewo, '#.###'))

    if pre_buy and alert_pre_buy:
        alert('EWO/RSI Strategy: PRE-BUY Signal Detected. Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | EWO turning up from negative.', alert.freq_once_per_bar_close)

    if buy_signal and alert_buy:
        alert('EWO/RSI Strategy: BUY NOW Signal Confirmed! Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | MFI: ' + string.tostring(mfi, '#.#') + ' | Volume OK: ' + string.tostring(vol_ok), alert.freq_once_per_bar_close)

    if pre_sell and alert_pre_sell:
        alert('EWO/RSI Strategy: PRE-SELL Signal Detected. Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | EWO turning down from positive.', alert.freq_once_per_bar_close)

    if sell_signal and alert_sell:
        alert('EWO/RSI Strategy: SELL NOW Signal Confirmed! Price: ' + string.tostring(close) + ' | RSI: ' + string.tostring(rsi, '#.#') + ' | MFI: ' + string.tostring(mfi, '#.#') + ' | Volume OK: ' + string.tostring(vol_ok), alert.freq_once_per_bar_close)

    if strategy.position_size > strategy.position_size[1] and alert_entry:
        alert('EWO/RSI Strategy: POSITION ENTERED. Direction: ' + ('LONG' if strategy.position_size > 0 else 'SHORT') + ' | Size: ' + string.tostring(math.abs(strategy.position_size)) + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar_close)

    if strategy.position_size < strategy.position_size[1] and strategy.position_size[1] != 0 and alert_exit:
        alert('EWO/RSI Strategy: POSITION EXITED/REVERSED. Price: ' + string.tostring(close) + ' | P&L: ' + string.tostring(strategy.closedtrades.profit(strategy.closedtrades - 1), '#.##'), alert.freq_once_per_bar_close)

    plot(na if price_breaking_out else breakout_barrier, title='Breakout Barrier', color=color.purple, style=plot.style_linebr)

    plotshape(pre_buy, title='Pre-Buy', style=shape.triangleup, location=location.belowbar, color=color.blue, size=size.small, text='Pre-Buy')
    plotshape(buy_signal, title='BUY NOW', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, size=size.normal, text='BUY')

    plotshape(pre_sell, title='Pre-Sell', style=shape.triangledown, location=location.abovebar, color=color.orange, size=size.small, text='Pre-Sell')
    plotshape(sell_signal, title='SELL NOW', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, size=size.normal, text='SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
