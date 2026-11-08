"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, barstate, close, color, fill, high, input,
    location, low, math, na, nz, open, plot, plotarrow, plotshape, position, script, shape, size,
    string, ta, table
)
from pynecore.types import NA, Persistent, Series, Table


@script.indicator("SSL Hybrid", overlay=True)
def main(
    display_mode=input.string("Full Display", title="Display Mode", options=("Baseline Only", "Baseline + SSL", "SSL Only", "Entry/Exit Only", "Full Display"), group="Display Controls"),
    color_bars=input.bool(True, title="Color Bars", group="Display Controls"),
    show_signals=input.bool(True, title="Show Signal Diamonds", tooltip="Candle > 1 ATR within baseline range - Potential false breakout warning", group="Display Controls"),
    show_risk_table=input.bool(True, title="Show Risk Table", group="Display Controls"),
    master_bullish_color=input.color(color.new('#00C3FF'), title="Bullish Color", group="Colors"),
    master_bearish_color=input.color(color.new('#FF0062'), title="Bearish Color", group="Colors"),
    maType=input.string("HMA", title="Baseline Type", options=("SMA", "EMA", "DEMA", "TEMA", "LSMA", "WMA", "MF", "VAMA", "TMA", "HMA", "JMA", "Kijun v2", "EDSMA", "McGinley"), group="Baseline Settings"),
    len=input.int(60, title="Baseline Length", group="Baseline Settings"),
    src: Series[float] = input(close, title="Source", group="Baseline Settings"),
    show_baseline_channel=input.bool(True, title="Show Baseline Channel", group="Baseline Settings"),
    multy=input.float(0.2, step=0.05, title="Channel Multiplier", group="Baseline Settings"),
    useTrueRange=input.bool(True, title="Use True Range for Channel", group="Baseline Settings"),
    SSL2Type=input.string("JMA", title="SSL2 Type", options=("SMA", "EMA", "DEMA", "TEMA", "WMA", "MF", "VAMA", "TMA", "HMA", "JMA", "McGinley"), group="SSL Settings"),
    len2=input.int(5, title="SSL2 Length", group="SSL Settings"),
    atr_crit=input.float(0.9, step=0.1, title="Continuation ATR Criteria", group="SSL Settings"),
    SSL3Type=input.string("HMA", title="Exit Type", options=("DEMA", "TEMA", "LSMA", "VAMA", "TMA", "HMA", "JMA", "Kijun v2", "McGinley", "MF"), group="Exit Settings"),
    len3=input.int(15, title="Exit Length", group="Exit Settings"),
    atrlen=input.int(14, title="ATR Period", group="ATR Settings"),
    mult=input.float(1.0, title="ATR Multiplier", step=0.1, group="ATR Settings"),
    smoothing=input.string("WMA", title="ATR Smoothing", options=("RMA", "SMA", "EMA", "WMA"), group="ATR Settings"),
    show_atr_bands=input.bool(False, title="Show ATR Bands", group="ATR Settings"),
    risk_lookback=input.int(100, title="Risk Lookback Period", minval=50, maxval=500, group="Risk Assessment"),
    risk_sensitivity=input.float(2, title="Risk Sensitivity", minval=0.2, maxval=3.0, step=0.1, group="Risk Assessment"),
    enable_risk_gradient=input.bool(True, title="Enable Risk Gradient", group="Risk Assessment"),
    jurik_phase=input.int(3, title="Phase", group="Jurik (JMA) Settings"),
    jurik_power=input.int(1, title="Power", group="Jurik (JMA) Settings"),
    kidiv=input.int(1, maxval=4, title="Kijun MOD Divider", group="Kijun Settings"),
    volatility_lookback=input.int(10, title="Volatility Lookback Length", group="VAMA Settings"),
    beta=input.float(0.8, minval=0, maxval=1, step=0.1, title="Beta", group="Modular Filter Settings"),
    feedback=input.bool(False, title="Feedback", group="Modular Filter Settings"),
    z=input.float(0.5, title="Feedback Weighting", step=0.1, minval=0, maxval=1, group="Modular Filter Settings"),
    ssfLength=input.int(20, title="Super Smoother Filter Length", minval=1, group="EDSMA Settings"),
    ssfPoles=input.int(2, title="Super Smoother Filter Poles", options=(2, 3), group="EDSMA Settings")
):
    def ma_function(source, atrlen):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, atrlen)
        elif smoothing == 'SMA':
            __block_result__ = ta.sma(source, atrlen)
        elif smoothing == 'EMA':
            __block_result__ = ta.ema(source, atrlen)
        else:
            __block_result__ = ta.wma(source, atrlen)
        return __block_result__

    atr_slen = ma_function(ta.tr(True), atrlen)
    upper_band = atr_slen * mult + close
    lower_band = close - atr_slen * mult

    atr_percentile = ta.percentrank(atr_slen, risk_lookback)

    __block_result_1__ = na
    if not enable_risk_gradient:
        __block_result_1__ = 0
    else:
        adjusted_percentile = math.pow(atr_percentile / 100, risk_sensitivity) * 100

        __block_result_2__ = na
        if adjusted_percentile <= 25:
            __block_result_2__ = 0
        elif adjusted_percentile <= 50:
            __block_result_2__ = 10
        else:
            base_transparency: int = 25
            extra_fade = (adjusted_percentile - 50) / 50 * 25
            __block_result_2__ = math.round(base_transparency + extra_fade)
        __block_result_1__ = __block_result_2__
    risk_saturation = __block_result_1__

    bullish_color = color.new(master_bullish_color, risk_saturation)
    bearish_color = color.new(master_bearish_color, risk_saturation)
    neutral_color = color.new(color.new('#666666'), 0)
    transparent_bull = color.new(master_bullish_color, math.max(80, risk_saturation + 20))
    transparent_bear = color.new(master_bearish_color, math.max(80, risk_saturation + 20))
    transparent_neutral = color.new(color.new('#666666'), 80)

    def tema(src, len):
        ema1 = ta.ema(src, len)
        ema2 = ta.ema(ema1, len)
        ema3 = ta.ema(ema2, len)
        return 3 * ema1 - 3 * ema2 + ema3

    def get2PoleSSF(src, length):
        PI = 2 * math.asin(1)
        arg = math.sqrt(2) * PI / length
        a1 = math.exp(-arg)
        b1 = 2 * a1 * math.cos(arg)
        c2 = b1
        c3 = -math.pow(a1, 2)
        c1 = 1 - c2 - c3

        ssf: Series[float] = 0.0
        ssf = c1 * src + c2 * nz(ssf[1]) + c3 * nz(ssf[2])
        return ssf

    def get3PoleSSF(src, length):
        PI = 2 * math.asin(1)
        arg = PI / length
        a1 = math.exp(-arg)
        b1 = 2 * a1 * math.cos(1.738 * arg)
        c1 = math.pow(a1, 2)

        coef2 = b1 + c1
        coef3 = -(c1 + b1 * c1)
        coef4 = math.pow(c1, 2)
        coef1 = 1 - coef2 - coef3 - coef4

        ssf: Series[float] = 0.0
        ssf = coef1 * src + coef2 * nz(ssf[1]) + coef3 * nz(ssf[2]) + coef4 * nz(ssf[3])
        return ssf

    def ma(type, src: Series, len):
        result: float = na(float)
        if type == 'TMA':
            result = ta.sma(ta.sma(src, math.ceil(len / 2)), math.floor(len / 2) + 1)
        if type == 'MF':
            ts: Series[float] = 0.0
            b: Series[float] = 0.0
            c: Series[float] = 0.0
            os: Series[float] = 0.0
            alpha = 2 / (len + 1)
            a = z * src + (1 - z) * nz(ts[1], src) if feedback else src
            b = a if a > alpha * a + (1 - alpha) * nz(b[1], a) else alpha * a + (1 - alpha) * nz(b[1], a)
            c = a if a < alpha * a + (1 - alpha) * nz(c[1], a) else alpha * a + (1 - alpha) * nz(c[1], a)
            os = 1 if a == b else 0 if a == c else os[1]
            upper = beta * b + (1 - beta) * c
            lower = beta * c + (1 - beta) * b
            ts = os * upper + (1 - os) * lower
            result = ts
        if type == 'LSMA':
            result = ta.linreg(src, len, 0)
        if type == 'SMA':
            result = ta.sma(src, len)
        if type == 'EMA':
            result = ta.ema(src, len)
        if type == 'DEMA':
            e = ta.ema(src, len)
            result = 2 * e - ta.ema(e, len)
        if type == 'TEMA':
            e = ta.ema(src, len)
            result = 3 * (e - ta.ema(e, len)) + ta.ema(ta.ema(e, len), len)
        if type == 'WMA':
            result = ta.wma(src, len)
        if type == 'VAMA':
            mid = ta.ema(src, len)
            dev = src - mid
            vol_up = ta.highest(dev, volatility_lookback)
            vol_down = ta.lowest(dev, volatility_lookback)
            result = mid + math.avg(vol_up, vol_down)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'JMA':
            phaseRatio = 0.5 if jurik_phase < -100 else 2.5 if jurik_phase > 100 else jurik_phase / 100 + 1.5
            beta__00000091__ = 0.45 * (len - 1) / (0.45 * (len - 1) + 2)
            alpha = math.pow(beta__00000091__, jurik_power)
            jma: Series[float] = 0.0
            e0: Series[float] = 0.0
            e0 = (1 - alpha) * src + alpha * nz(e0[1])
            e1: Series[float] = 0.0
            e1 = (src - e0) * (1 - beta__00000091__) + beta__00000091__ * nz(e1[1])
            e2: Series[float] = 0.0
            e2 = (e0 + phaseRatio * e1 - nz(jma[1])) * math.pow(1 - alpha, 2) + math.pow(alpha, 2) * nz(e2[1])
            jma = e2 + nz(jma[1])
            result = jma
        if type == 'Kijun v2':
            kijun = math.avg(ta.lowest(len), ta.highest(len))
            conversionLine = math.avg(ta.lowest(len / kidiv), ta.highest(len / kidiv))
            delta = (kijun + conversionLine) / 2
            result = delta
        if type == 'McGinley':
            mg: Series[float] = 0.0
            mg = ta.ema(src, len) if na(mg[1]) else mg[1] + (src - mg[1]) / (len * math.pow(src / mg[1], 4))
            result = mg
        if type == 'EDSMA':
            zeros: Series = src - nz(src[2])
            avgZeros = (zeros + zeros[1]) / 2
            ssf = get2PoleSSF(avgZeros, ssfLength) if ssfPoles == 2 else get3PoleSSF(avgZeros, ssfLength)
            stdev = ta.stdev(ssf, len)
            scaledFilter = ssf / stdev if stdev != 0 else 0
            alpha = 5 * math.abs(scaledFilter) / len
            edsma: Series[float] = 0.0
            edsma = alpha * src + (1 - alpha) * nz(edsma[1])
            result = edsma
        return result

    BBMC = ma(maType, close, len)
    Keltma = ma(maType, src, len)
    rangeValue = ta.tr if useTrueRange else high - low
    rangema = ta.ema(rangeValue, len)
    upperk = Keltma + rangema * multy
    lowerk = Keltma - rangema * multy

    emaHigh = ma(maType, high, len)
    emaLow = ma(maType, low, len)
    Hlv: Series = NA(int)
    Hlv = 1 if close > emaHigh else -1 if close < emaLow else Hlv[1]
    sslDown = emaHigh if Hlv < 0 else emaLow

    maHigh = ma(SSL2Type, high, len2)
    maLow = ma(SSL2Type, low, len2)
    Hlv2: Series = NA(int)
    Hlv2 = 1 if close > maHigh else -1 if close < maLow else Hlv2[1]
    sslDown2 = maHigh if Hlv2 < 0 else maLow

    ExitHigh = ma(SSL3Type, high, len3)
    ExitLow = ma(SSL3Type, low, len3)
    Hlv3: Series = NA(int)
    Hlv3 = 1 if close > ExitHigh else -1 if close < ExitLow else Hlv3[1]
    sslExit = ExitHigh if Hlv3 < 0 else ExitLow

    distance_from_baseline = math.abs(close - BBMC) / atr_slen
    entry_distance = 'Near' if distance_from_baseline < 1 else 'Extended' if distance_from_baseline < 2 else 'Far'

    risk_level = 'High' if atr_percentile > 75 else 'Low' if atr_percentile < 25 else 'Normal'

    base_cross_Long = ta.crossover(close, sslExit)
    base_cross_Short = ta.crossover(sslExit, close)
    codiff = 1 if base_cross_Long else -1 if base_cross_Short else na

    difference = math.abs(close - open)
    atr_violation = difference > atr_slen
    InRange = upper_band > BBMC and lower_band < BBMC
    candlesize_violation = atr_violation and InRange

    upper_half = atr_slen * atr_crit + close
    lower_half = close - atr_slen * atr_crit
    buy_inatr = lower_half < sslDown2
    sell_inatr = upper_half > sslDown2
    sell_cont = close < BBMC and close < sslDown2
    buy_cont = close > BBMC and close > sslDown2
    sell_atr: Series = sell_inatr and sell_cont
    buy_atr: Series = buy_inatr and buy_cont

    baseline_color = bullish_color if close > upperk else bearish_color if close < lowerk else neutral_color
    ssl_color = bullish_color if close > sslDown else bearish_color if close < sslDown else neutral_color
    ssl2_color = bullish_color if buy_atr else bearish_color if sell_atr else neutral_color
    channel_fill_color = transparent_bull if close > upperk else transparent_bear if close < lowerk else transparent_neutral

    show_baseline = display_mode == 'Baseline Only' or display_mode == 'Baseline + SSL' or display_mode == 'Full Display'
    show_ssl1 = display_mode == 'SSL Only' or display_mode == 'Baseline + SSL' or display_mode == 'Full Display'
    show_ssl2 = display_mode == 'SSL Only' or display_mode == 'Full Display'
    show_exit = display_mode == 'Entry/Exit Only' or display_mode == 'Full Display'

    baseline_plot = plot(BBMC if show_baseline else na, color=baseline_color, linewidth=3, title='Baseline')
    upper_channel = plot(upperk if show_baseline and show_baseline_channel else na, color=baseline_color, title='Upper Channel')
    lower_channel = plot(lowerk if show_baseline and show_baseline_channel else na, color=baseline_color, title='Lower Channel')
    fill(upper_channel, lower_channel, color=channel_fill_color if show_baseline and show_baseline_channel else na, title='Baseline Channel')

    ssl1_plot = plot(sslDown if show_ssl1 else na, title='SSL1', linewidth=2, color=ssl_color)
    ssl2_plot = plot(sslDown2 if show_ssl2 else na, title='SSL2', linewidth=2, color=ssl2_color, style=plot.style_circles)

    atr_upper = plot(upper_band if show_atr_bands else na, '+ATR', color=neutral_color, linewidth=1)
    atr_lower = plot(lower_band if show_atr_bands else na, '-ATR', color=neutral_color, linewidth=1)

    plotarrow(codiff if show_exit else na, colorup=bullish_color, colordown=bearish_color, title='Exit Arrows', maxheight=20)
    plotshape(show_signals and candlesize_violation, color=color.white, size=size.tiny, style=shape.diamond, location=location.top, title='Signal Diamonds')

    barcolor(baseline_color if color_bars else na, title='Bar Colors')

    if barstate.islast and show_risk_table:
        riskTable: Persistent[Table] = table.new(position.bottom_right, 2, 4, bgcolor=color.new(color.new('#1A1A1A'), 5), border_width=1)

        table.cell(riskTable, 0, 0, 'Risk Level', text_color=color.white, text_size=size.small)
        risk_color = bearish_color if risk_level == 'High' else bullish_color if risk_level == 'Low' else neutral_color
        table.cell(riskTable, 1, 0, risk_level, text_color=risk_color, text_size=size.small)

        table.cell(riskTable, 0, 1, 'Entry Distance', text_color=color.white, text_size=size.small)
        entry_color = bullish_color if entry_distance == 'Near' else color.yellow if entry_distance == 'Extended' else bearish_color
        table.cell(riskTable, 1, 1, entry_distance, text_color=entry_color, text_size=size.small)

        table.cell(riskTable, 0, 2, 'Vol %ile', text_color=color.white, text_size=size.small)
        table.cell(riskTable, 1, 2, string.tostring(math.round(atr_percentile, 1)) + '%', text_color=color.white, text_size=size.small)

        table.cell(riskTable, 0, 3, 'ATR', text_color=color.white, text_size=size.small)
        table.cell(riskTable, 1, 3, string.tostring(atr_slen, '#.####'), text_color=color.white, text_size=size.small)

    exit_long = ta.crossunder(close, sslExit)
    exit_short = ta.crossover(close, sslExit)

    ssl2_buy_signal = buy_atr and (not buy_atr[1])
    ssl2_sell_signal = sell_atr and (not sell_atr[1])

    baseline_bullish = ta.crossover(close, upperk)
    baseline_bearish = ta.crossunder(close, lowerk)
    price_above_baseline = close > BBMC and close[1] <= BBMC
    price_below_baseline = close < BBMC and close[1] >= BBMC

    high_risk_entry = risk_level == 'High' and entry_distance == 'Far'
    false_breakout_warning = candlesize_violation
    extreme_volatility = atr_percentile > 90

    alertcondition(exit_long, title='EXIT LONG Signal', message='EXIT LONG Signal – see chart for price and risk details')

    alertcondition(exit_short, title='EXIT SHORT Signal', message='EXIT SHORT Signal – see chart for price and risk details')

    alertcondition(ssl2_buy_signal, title='SSL2 BUY Continuation', message='SSL2 BUY Continuation – see chart for ATR details')

    alertcondition(ssl2_sell_signal, title='SSL2 SELL Continuation', message='SSL2 SELL Continuation – see chart for ATR details')

    alertcondition(baseline_bullish, title='Price Above Upper Channel', message='Price Above Upper Channel – price has broken above upper band')

    alertcondition(baseline_bearish, title='Price Below Lower Channel', message='Price Below Lower Channel – price has broken below lower band')

    alertcondition(price_above_baseline, title='Price Crossed Above Baseline', message='Price Crossed Above Baseline')

    alertcondition(price_below_baseline, title='Price Crossed Below Baseline', message='Price Crossed Below Baseline')

    alertcondition(high_risk_entry, title='HIGH RISK Entry Conditions', message='HIGH RISK Entry – check chart for context')

    alertcondition(false_breakout_warning, title='FALSE BREAKOUT WARNING', message='FALSE BREAKOUT WARNING – possible trap candle')

    alertcondition(extreme_volatility, title='EXTREME VOLATILITY', message='EXTREME VOLATILITY – check ATR levels on chart')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
