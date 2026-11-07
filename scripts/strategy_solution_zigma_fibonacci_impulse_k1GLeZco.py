"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, close, color, display, fill, high, hlc3, input, location, low,
    math, na, nz, ohlc4, plot, plotcandle, plotshape, request, script, shape, size, strategy,
    syminfo, ta, timeframe, volume
)
from pynecore.types import Color, Persistent, PersistentSeries, Series
import lib.ZoomerXeus.AutoFiboRetrace.v2 as autoFibo

ord_con_1: str = 'Original (Zigma Candle + CE + Subhag)'
ord_con_2: str = 'Original Extra (Zigma Candle with DMI + CE + Subhag)'
ord_con_3: str = 'Original 0 (Zigma + CE)'
ord_con_4: str = 'Original 0 Extra (Zigma with DMI + CE)'
ord_con_5: str = 'Original Combination (Combo since Original to Original 0)'


@script.strategy("Solution Zigma", overlay=True, calc_on_every_tick=True)
def main(
    fibo_level_source=input.string('0.5', 'Fibonaci Level source', options=('0.786', '0.618', '0.5', '0.382', '0.236'), group="General (Default setting for Binance's BTCUSDTPERP)"),
    fibo_level_session=input.timeframe('60', 'Timeframe', options=("W", "D", "240", "60", "30", "15", "5", "1"), group="General (Default setting for Binance's BTCUSDTPERP)"),
    fibo_lookback_length=input.int(12, 'Fibonaci lookback Length', minval=1, step=1, group="General (Default setting for Binance's BTCUSDTPERP)"),
    isShowCandleMode=input.bool(True, 'Show Candle Mode', group="General (Default setting for Binance's BTCUSDTPERP)"),
    isShowFilterIndicator_ce=input.bool(False, 'Show On Chart', group="Alex Orekhov (everget)'s Chandelier Exit (Filter)"),
    ce_length=input.int(1, 'ATR Chandelier Exit Length', minval=1, step=1, group="Alex Orekhov (everget)'s Chandelier Exit (Filter)"),
    ce_mult=input.float(3.0, 'ATR Chandelier Exit Multiply', minval=0.1, step=0.1, group="Alex Orekhov (everget)'s Chandelier Exit (Filter)"),
    isShowFilterIndicator_subh=input.bool(False, 'Show On Chart', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    fast_length=input(title='Fast Length', defval=3, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    slow_length=input(title='Slow Length', defval=10, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    src_sh: Series[float] = input(title='Source', defval=close, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    res_60=input('60', title='Higher Time Frame 1', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    rsi_period=input.int(14, title='RSI period', minval=1, step=1, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    source: Series[float] = input(close, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    length=input.int(100, minval=1, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    offset=input.int(0, minval=0, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    smoothing=input.int(17, minval=1, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    mtf_val=input.timeframe('', 'Resolution', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    p=input.string('Lime', 'Up Color', options=('Red', 'Lime', 'Orange', 'Teal', 'Yellow', 'White', 'Black'), group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    q=input.string('Red', 'Down Color', options=('Red', 'Lime', 'Orange', 'Teal', 'Yellow', 'White', 'Black'), group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    switchColor=input(True, 'Color Regression according to trend?', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    candleCol=input(False, title='Color candles based on Hull\'s Trend?', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    visualSwitch=input(True, title='Show as a Band?', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    thicknesSwitch=input(1, title='Line Thickness', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    transpSwitch=input.int(40, title='Band Transparency', step=5, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    n1=input.int(10, 'Channel Length', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    n2=input.int(21, 'Average Length', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    over_bought_level=input.int(53, 'Over Bought Level', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    over_sold_level=input.int(-53, 'Over Sold Level', group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    sma1length=input(5, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    sma2length=input(35, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    UsePercent=input(title='Show Dif as percent of current Candle', defval=True, group="Subhag + TSD + EWO original by subhagghosh and edit by Pumpith (Filter)"),
    conditionType=input.string(ord_con_4, "Open order type", options=(ord_con_1, ord_con_2, ord_con_3, ord_con_4, ord_con_5)),
    order_size=input.float(0.001, 'Order Size', minval=0.001, step=0.1, tooltip="order size 1:Price e.g 1:38000(BTCUSDTPERP)", group="Alert Message and order Management"),
    leverage_mult=input.int(10, 'Leverage Size', minval=1, step=1, group="Alert Message and order Management"),
    close_order_type=input.string('Condition', 'Close Order Option', options=('RR', 'Condition'), group="Alert Message and order Management"),
    rrUseAutoSL=input.bool(False, 'Use auto Calculate Stoploss', group="Alert Message and order Management"),
    rrAutoSLType=input.string('Zigma Swing H/L', "Open order type", options=('Zigma Swing H/L', 'Candle Swing H/L'), group="Alert Message and order Management"),
    rrAutoSLCalLength=input.int(5, 'Auto SL Calculate Length', tooltip="Use for fing Lowest and Highest.", step=1, minval=1, group="Alert Message and order Management"),
    __input_39__=input.float(1.0, "RR Stoploss percent", minval=0.1, step=0.1, group="Alert Message and order Management"),
    rrPer=input.float(2.0, "RR ratio", minval=0.1, step=0.1, group="Alert Message and order Management"),
    msg_open_long=input.string('Open Long', 'Alert Message Long', group="Alert Message and order Management"),
    msg_open_short=input.string('Open Short', 'Alert Message Short', group="Alert Message and order Management"),
    msg_close_long=input.string('Close Long', 'Alert Message Close Long', group="Alert Message and order Management"),
    msg_close_short=input.string('Close Short', 'Alert Message Close Short', group="Alert Message and order Management")
):
    SLPer = __input_39__ / 100

    FL236M, FL382M, FL500M, FL618M, FL786M, FL0, FL236, FL382, FL500, FL618, FL786, FL1000, FL1236, FL1382, FL1500, FL1618, FL1786, FL2 = request.security(syminfo.tickerid, fibo_level_session, autoFibo.original(fibo_lookback_length, low, high), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    __block_result__ = na
    __switch__ = fibo_level_source
    if __switch__ == '0.618':
        __block_result__ = FL618
    elif __switch__ == '0.786':
        __block_result__ = FL786
    elif __switch__ == '0.5':
        __block_result__ = FL500
    elif __switch__ == '0.382':
        __block_result__ = FL382
    elif __switch__ == '0.236':
        __block_result__ = FL236
    src = __block_result__

    open_p = ta.ema(src, 12)
    close_p = ta.ema(src, 9)
    high_p = ta.highest(close_p, 4)
    low_p = ta.lowest(close_p, 4)

    def setDMI():
        diplus: float = 0.0
        diminus: float = 0.0
        adx: float = 0.0
        diplus_4h, diminus_4h, adx_4h = request.security(syminfo.tickerid, '240', ta.dmi(14, 14), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
        diplus_1h, diminus_1h, adx_1h = request.security(syminfo.tickerid, '60', ta.dmi(14, 14), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
        diplus_15m, diminus_15m, adx_15m = request.security(syminfo.tickerid, '15', ta.dmi(14, 14), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
        if fibo_level_session == 'LongTrade(4H)':
            diplus = diplus_4h
            diminus = diminus_4h
            adx = adx_4h
        elif fibo_level_session == 'MediumTrade(1H)':
            diplus = diplus_1h
            diminus = diminus_1h
            adx = adx_1h
        else:
            diplus = diplus_15m
            diminus = diminus_15m
            adx = adx_15m
        return (diplus, diminus, adx)

    diplus, diminus, adx = setDMI()

    atr = ce_mult * ta.atr(ce_length)

    longStop: Series = ta.highest(ce_length) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if close[1] > longStopPrev else longStop

    shortStop: Series = ta.lowest(ce_length) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if close[1] < shortStopPrev else shortStop

    dir: PersistentSeries[int] = 1
    dir = 1 if close > shortStopPrev else -1 if close < longStopPrev else dir

    ha_t = syminfo.tickerid
    col_red: Color = color.new('#FF0000')
    col_green: Color = color.new('#00FF00')

    TSB: bool = True
    TSS: bool = False

    trend_60 = request.security(ha_t, res_60, (ta.ema(src_sh, fast_length) - ta.ema(src_sh, slow_length)) / src_sh * 100)
    prev_trend_60 = request.security(ha_t, res_60, (ta.ema(src_sh[5], fast_length) - ta.ema(src_sh[5], slow_length)) / src_sh[5] * 100)

    trend_status_60 = trend_60 > prev_trend_60

    myrsi = ta.rsi(close, rsi_period)
    rsi1 = ta.crossunder(myrsi, 70)
    rsi2 = myrsi > 75

    def cc(x):
        return color.red if x == 'Red' else color.lime if x == 'Lime' else color.orange if x == 'Orange' else color.teal if x == 'Teal' else color.yellow if x == 'Yellow' else color.black if x == 'Black' else color.white

    def data(x):
        return ta.ema(request.security(syminfo.tickerid, mtf_val if mtf_val != '' else timeframe.period, x), smoothing)

    linreg: Series = data(ta.linreg(source, length, offset))
    linreg_p = data(ta.linreg(source, length, offset + 1))

    ap = hlc3
    esa = ta.ema(ap, n1)
    d = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)

    mfi_upper = math.sum(volume * (0 if ta.change(hlc3) <= 0 else hlc3), 58)
    mfi_lower = math.sum(volume * (0 if ta.change(hlc3) >= 0 else hlc3), 58)
    def _mfi_rsi(mfi_upper, mfi_lower):
        if mfi_lower == 0:
            pass
        if mfi_upper == 0:
            pass
        return 100.0 - 100.0 / (1.0 + mfi_upper / mfi_lower)

    mf = _mfi_rsi(mfi_upper, mfi_lower)
    mfi = (mf - 50) * 3

    mfi_color = color.new('#4CAF50') if mfi > 0 else color.new('#FF5252')
    dot_color = color.new('#FF0000') if wt1 < wt2 else color.new('#4CAF50')

    sma_1 = ta.sma(src, sma1length)
    sma_2 = ta.sma(src, sma2length)
    sma_3 = ta.sma(src, sma1length)
    sma_4 = ta.sma(src, sma2length)
    smadif = (sma_1 - sma_2) / src * 100 if UsePercent else sma_3 - sma_4

    candle_color = color.new(color.green, 60 if isShowCandleMode else 100) if open_p < close_p else color.new(color.red, 60 if isShowCandleMode else 100) if open_p > close_p else color.new(color.white, 60 if isShowCandleMode else 100)
    line_color = color.new(color.green, 100 if isShowCandleMode else 0) if open_p < close_p else color.new(color.red, 100 if isShowCandleMode else 0) if open_p > close_p else color.new(color.white, 100 if isShowCandleMode else 0)
    plotcandle(open_p, high_p, low_p, close_p, 'Fibo Level Candle', color=candle_color, wickcolor=candle_color, bordercolor=candle_color)
    plot(open_p if close > open_p else na, title='Zigma Bull impulse', style=plot.style_linebr, linewidth=2, color=color.lime)
    plot(open_p if close < open_p else na, title='Zigma Bear impulse', style=plot.style_linebr, linewidth=2, color=color.red)

    longColor: Persistent[Color] = color.green
    shortColor: Persistent[Color] = color.red

    hullColor = (color.new('#00FF00') if linreg > linreg[1] else color.new('#FF0000')) if switchColor else color.new('#FF9800')

    Fi1 = plot(linreg if isShowFilterIndicator_subh else na, title='Regression Line', color=color.new(hullColor, 50), linewidth=thicknesSwitch)
    Fi2 = plot(linreg[3] if visualSwitch and isShowFilterIndicator_subh else na, title='RL', color=color.new(hullColor, 50), linewidth=thicknesSwitch)

    fill(Fi1, Fi2, title='Band Filler', color=color.new(hullColor, transpSwitch))

    longStopPlot = plot((longStop if dir == 1 else na) if isShowFilterIndicator_ce else na, title='Long Stop', style=plot.style_linebr, linewidth=2, color=color.new(longColor, 0))
    buySignal = dir == 1 and dir[1] == -1
    plotshape(longStop if buySignal and isShowFilterIndicator_ce else na, title='Long Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(longColor, 0))

    shortStopPlot = plot((na if dir == 1 else shortStop) if isShowFilterIndicator_ce else na, title='Short Stop', style=plot.style_linebr, linewidth=2, color=color.new(shortColor, 0))
    sellSignal = dir == -1 and dir[1] == 1
    plotshape(shortStop if sellSignal and isShowFilterIndicator_ce else na, title='Short Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(shortColor, 0))

    midPricePlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=1, display=display.none, editable=False)

    position_avg_price = strategy.position_avg_price
    position_size = strategy.position_size

    fibo_impulse_bear_over = ta.crossunder(close, open_p)
    fibo_impulse_bull_over = ta.crossover(close, open_p)

    dmi_Bull = diplus >= 25 and diplus > adx
    dmi_Bear = diminus >= 25 and diminus > adx

    ce_bull_rejection = dir == 1 and dir[1] != 1
    ce_bear_rejection = dir != 1 and dir[1] == 1
    ce_bull_controll = dir == 1
    ce_bear_controll = dir != 1

    sh_bull = close > linreg and close > linreg[3]
    sh_bear = close < linreg and close < linreg[3]

    LongCondition = fibo_impulse_bull_over and (ce_bull_controll or ce_bull_rejection) and sh_bull and (position_size == 0.0)
    ShortCondition = fibo_impulse_bear_over and (ce_bear_controll or ce_bear_rejection) and sh_bear and (position_size == 0.0)

    LongCondition_extra = fibo_impulse_bull_over and dmi_Bull and (ce_bull_controll or ce_bull_rejection) and sh_bull and (position_size == 0.0)
    ShortCondition_extra = fibo_impulse_bear_over and dmi_Bear and (ce_bear_controll or ce_bear_rejection) and sh_bear and (position_size == 0.0)

    LongCondition_std1 = fibo_impulse_bull_over and (ce_bull_controll or ce_bull_rejection) and (position_size == 0.0)
    ShortCondition_std1 = fibo_impulse_bear_over and (ce_bear_controll or ce_bear_rejection) and (position_size == 0.0)

    LongCondition_std1extra = fibo_impulse_bull_over and dmi_Bull and (ce_bull_controll or ce_bull_rejection) and (position_size == 0.0)
    ShortCondition_std1extra = fibo_impulse_bear_over and dmi_Bear and (ce_bear_controll or ce_bear_rejection) and (position_size == 0.0)

    LongCondition_Comb = LongCondition or LongCondition_extra or LongCondition_std1 or LongCondition_std1extra
    ShortCondition_Comb = ShortCondition or ShortCondition_extra or ShortCondition_std1 or ShortCondition_std1extra

    plotshape(LongCondition, title='Buy Signal Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.lime, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original (Zigma Candle + CE + Subhag)' else display.all)
    plotshape(ShortCondition, title='Sell Signal Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original (Zigma Candle + CE + Subhag)' else display.all)

    plotshape(LongCondition_extra, title='Buy Signal Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.lime, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original Extra (Zigma Candle with DMI + CE + Subhag)' else display.all)
    plotshape(ShortCondition_extra, title='Sell Signal Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original Extra (Zigma Candle with DMI + CE + Subhag)' else display.all)

    plotshape(LongCondition_std1, title='Buy Signal Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.lime, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original 0 (Zigma + CE)' else display.all)
    plotshape(ShortCondition_std1, title='Sell Signal Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original 0 (Zigma + CE)' else display.all)

    plotshape(LongCondition_std1extra, title='Buy Signal Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.lime, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original 0 Extra (Zigma with DMI + CE)' else display.all)
    plotshape(ShortCondition_std1extra, title='Sell Signal Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original 0 Extra (Zigma with DMI + CE)' else display.all)

    plotshape(LongCondition_Comb, title='Buy Signal Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.lime, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original Combination (Combo since Original to Original 0)' else display.all)
    plotshape(ShortCondition_Comb, title='Sell Signal Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.new(color.white, 0), display=display.none if conditionType != 'Original Combination (Combo since Original to Original 0)' else display.all)

    if conditionType == 'Original (Zigma Candle + CE + Subhag)':
        if LongCondition:
            strategy.order('Long', strategy.long, order_size * leverage_mult, alert_message=msg_open_long)
        if ShortCondition:
            strategy.order('Short', strategy.short, order_size * leverage_mult, alert_message=msg_open_short)
    elif conditionType == 'Original Extra (Zigma Candle with DMI + CE + Subhag)':
        if LongCondition_extra:
            strategy.order('Long', strategy.long, order_size * leverage_mult, alert_message=msg_open_long)
        if ShortCondition_extra:
            strategy.order('Short', strategy.short, order_size * leverage_mult, alert_message=msg_open_short)
    elif conditionType == 'Original 0 (Zigma + CE)':
        if LongCondition_std1:
            strategy.order('Long', strategy.long, order_size * leverage_mult, alert_message=msg_open_long)
        if ShortCondition_std1:
            strategy.order('Short', strategy.short, order_size * leverage_mult, alert_message=msg_open_short)
    elif conditionType == 'Original 0 Extra (Zigma with DMI + CE)':
        if LongCondition_std1extra:
            strategy.order('Long', strategy.long, order_size * leverage_mult, alert_message=msg_open_long)
        if ShortCondition_std1extra:
            strategy.order('Short', strategy.short, order_size * leverage_mult, alert_message=msg_open_short)
    elif conditionType == 'Original Combination (Combo since Original to Original 0)':
        if LongCondition_Comb:
            strategy.order('Long', strategy.long, order_size * leverage_mult, alert_message=msg_open_long)
        if ShortCondition_Comb:
            strategy.order('Short', strategy.short, order_size * leverage_mult, alert_message=msg_open_short)

    auto_sl_high: float = 0.0
    auto_sl_low: float = 0.0

    if rrAutoSLType == 'Zigma Swing H/L':
        auto_sl_high = ta.highest(high_p, rrAutoSLCalLength)
        auto_sl_low = ta.lowest(low_p, rrAutoSLCalLength)
    else:
        auto_sl_high = ta.highest(high, rrAutoSLCalLength)
        auto_sl_low = ta.lowest(low, rrAutoSLCalLength)

    sl_percent_bull: Series[float] = 0.0
    sl_percent_bear: Series[float] = 0.0
    sl_percent_bull_auto = (position_avg_price - auto_sl_low) / position_avg_price if sl_percent_bull[1] == 0.0 and position_size != 0 else sl_percent_bull[1] if position_size != 0 else 0.0
    sl_percent_bull_fix = SLPer if sl_percent_bull[1] == 0.0 and position_size != 0 else 0.0
    sl_percent_bull = sl_percent_bull_auto if rrUseAutoSL else sl_percent_bull_fix
    stopPriceBull = position_avg_price * (1 - sl_percent_bull)
    takeProfitBull = position_avg_price * (1 + sl_percent_bull * rrPer)

    sl_percent_bear_auto = (auto_sl_high - position_avg_price) / position_avg_price if sl_percent_bear[1] == 0.0 and position_size != 0 else sl_percent_bear[1] if position_size != 0 else 0.0
    sl_percent_bear_fix = SLPer if sl_percent_bear[1] == 0.0 and position_size != 0 else 0.0
    sl_percent_bear = sl_percent_bear_auto if rrUseAutoSL else sl_percent_bear_fix
    stopPriceBear = position_avg_price * (1 + sl_percent_bear)
    takeProfitBear = position_avg_price * (1 - sl_percent_bear * rrPer)

    plot((stopPriceBear if position_size < 0 else stopPriceBull) if close_order_type == 'RR' else na, "Short's SL Line", style=plot.style_linebr, color=color.red)
    plot((takeProfitBear if position_size < 0 else takeProfitBull) if close_order_type == 'RR' else na, "Short's TP Line", style=plot.style_linebr, color=color.green)

    closeLongCondition = (ta.crossunder(close, open_p) or close < open_p) and (ce_bear_controll or ce_bear_rejection)
    closeShortCondition = (ta.crossover(close, open_p) or close > open_p) and (ce_bull_controll or ce_bull_rejection)

    if conditionType == 'Original (Zigma Candle + CE + Subhag)' or conditionType == 'Original Extra (Zigma Candle with DMI + CE + Subhag)' or conditionType == 'Original 0 (Zigma + CE)' or (conditionType == 'Original 0 Extra (Zigma with DMI + CE)') or (conditionType == 'Original Combination (Combo since Original to Original 0)'):
        if close_order_type == 'RR':
            strategy.exit('Exit Long', 'Long', stop=stopPriceBull, limit=takeProfitBull, alert_message=msg_close_long)
            strategy.exit('Exit Short', 'Short', stop=stopPriceBear, limit=takeProfitBear, alert_message=msg_close_short)
        else:
            if closeLongCondition:
                strategy.close('Long', qty_percent=100, alert_message=msg_close_long)
            if closeShortCondition:
                strategy.close('Short', qty_percent=100, alert_message=msg_close_short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
