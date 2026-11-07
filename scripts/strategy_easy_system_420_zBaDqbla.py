"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barmerge, bgcolor, close, color, fixnan, high, hl2, input,
    label, line, location, low, math, na, nz, open, plot, plotshape, request, script, shape, size,
    strategy, string, syminfo, ta, time, timeframe, timenow, volume, xloc, yloc
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.strategy(title='Easy Sys 420', shorttitle='EasySys420', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.01, slippage=1, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(open, title='Source'),
    EnterPoints=input.int(15, minval=0, maxval=24, title='EnterPoints'),
    Period=input.int(14, minval=2, maxval=1000, title='Hull MA Period'),
    AF_initial=input.float(0.02, minval=0.0, maxval=1, step=0.01, title='AF_initial'),
    AF_increment=input.float(0.02, minval=0.0, maxval=1, step=0.01, title='AF_increment'),
    AF_maximum=input.float(0.2, minval=0.0, maxval=1, step=0.1, title='AF_maximum'),
    len=input(5, title='Length'),
    Depth=input(12, title='Depth'),
    Deviation=input(5, title='Deviation'),
    st_mult=input.float(3, minval=0, maxval=100, step=0.1, title='SuperTrend Multiplier'),
    st_period=input.int(7, minval=1, title='SuperTrend Period'),
    multi=input.float(0.5, minval=0.0, maxval=3.0, step=0.1, title='Divergence Channel Width Factor (Stddev)'),
    uDiv=input(True, title='Show Divergence Channel'),
    uHid=input(True, title='Show Hidden Divergence'),
    uReg=input(True, title='Show Regular Divergence'),
    disp_panels=input(True, title='Display info panels?'),
    info_label_pos=input.int(title='Info panel position', defval=-10, minval=-1000, maxval=1000),
    info_label_size=input.string(size.normal, options=(size.tiny, size.small, size.normal, size.large, size.huge), title='Info panel label size'),
    Bgcolor=input(True, title='Bgcolor')
):
    hilow = (high - low) * 100
    openclose = (close - open) * 100
    vol1 = volume / hilow
    spreadvol = openclose * vol1
    VPT = spreadvol + ta.cum(spreadvol)
    window_len: int = 28
    v_len: int = 14
    price_spread = ta.stdev(high - low, window_len)
    vp = spreadvol + ta.cum(spreadvol)
    smooth = ta.sma(vp, v_len)
    v_spread = ta.stdev(vp - smooth, window_len)
    shadow = (vp - smooth) / v_spread * price_spread
    out1 = high + shadow if shadow > 0 else low + shadow
    vpt = ta.ema(out1, len)
    uDiv = uDiv if uReg or uHid else False
    up_lev = vpt - st_mult * ta.atr(st_period)
    dn_lev = vpt + st_mult * ta.atr(st_period)
    up_trend: Series[float] = 0.0
    up_trend = math.max(up_lev, up_trend[1]) if src[1] > up_trend[1] else up_lev
    down_trend: Series[float] = 0.0
    down_trend = math.min(dn_lev, down_trend[1]) if src[1] < down_trend[1] else dn_lev
    trend10: Series[int] = 0
    trend10 = 1 if src > down_trend[1] else -1 if src < up_trend[1] else nz(trend10[1], 1)
    st_line = up_trend if trend10 == 1 else down_trend
    def f_top_fractal(_src: Series):
        return _src[4] < _src[2] and _src[3] < _src[2] and (_src[2] > _src[1]) and (_src[2] > _src)

    def f_bot_fractal(_src: Series):
        return _src[4] > _src[2] and _src[3] > _src[2] and (_src[2] < _src[1]) and (_src[2] < _src)

    def f_fractalize(_src):
        f_bot_fractal__1 = f_bot_fractal(_src)
        return 1 if f_top_fractal(_src) else -1 if f_bot_fractal__1 else 0

    ST_high: Series = st_line
    ST_low: Series = st_line
    offset_ = multi * ta.stdev(st_line, 20)
    fractal_top_ST = ST_high[2] if f_fractalize(ST_high) > 0 else na
    fractal_bot_ST = ST_low[2] if f_fractalize(ST_low) < 0 else na
    ST_high_prev = ta.valuewhen(cast_bool(fractal_top_ST), ST_high[2], 1)
    ST_high_price = ta.valuewhen(cast_bool(fractal_top_ST), high[2], 1)
    ST_low_prev = ta.valuewhen(cast_bool(fractal_bot_ST), ST_low[2], 1)
    ST_low_price = ta.valuewhen(cast_bool(fractal_bot_ST), low[2], 1)
    regular_bearish_div = cast_bool(fractal_top_ST) and high[2] > ST_high_price and (ST_high[2] < ST_high_prev) and (ST_high > 0)
    hidden_bearish_div = cast_bool(fractal_top_ST) and high[2] < ST_high_price and (ST_high[2] > ST_high_prev) and (ST_high > 0)
    regular_bullish_div = cast_bool(fractal_bot_ST) and low[2] < ST_low_price and (ST_low[2] > ST_low_prev) and (ST_low < 0)
    hidden_bullish_div = cast_bool(fractal_bot_ST) and low[2] > ST_low_price and (ST_low[2] < ST_low_prev) and (ST_low < 0)
    color1 = color.lime if trend10 == 1 else color.orange
    plot(title='ST High', series=ST_high if uDiv else na, color=color1)
    plot(title='ST Low', series=ST_low if uDiv else na, color=color1)
    plot(title='ST H F', series=fractal_top_ST + offset_ if uDiv else na, color=color.new(color.red, 0), offset=-2)
    plot(title='ST L F', series=fractal_bot_ST - offset_ if uDiv else na, color=color.new(color.green, 0), offset=-2)
    plot(title='ST H D', series=fractal_top_ST + offset_ if uDiv else na, style=plot.style_circles, color=color.maroon if regular_bearish_div and uReg or (hidden_bearish_div and uHid) else color.red, linewidth=5, offset=-2)
    plot(title='ST L D', series=fractal_bot_ST - offset_ if uDiv else na, style=plot.style_circles, color=color.green if regular_bullish_div and uReg or (hidden_bullish_div and uHid) else color.blue, linewidth=5, offset=-2)
    plotshape(title='+RBD', series=ST_high[2] + offset_ if regular_bearish_div and uReg else na, text='Regular', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='+HBD', series=ST_high[2] + offset_ if hidden_bearish_div and uHid else na, text='hidden', style=shape.labeldown, location=location.absolute, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-RBD', series=ST_low[2] - offset_ if regular_bullish_div and uReg else na, text='Regular', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    plotshape(title='-HBD', series=ST_low[2] - offset_ if hidden_bullish_div and uHid else na, text='hidden', style=shape.labelup, location=location.absolute, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), offset=-2)
    lastlow: Series[float] = 0.0
    lasthigh: Series[float] = 0.0
    lastlow = nz(lastlow[1])
    lasthigh = nz(lasthigh[1])
    def data(x):
        d = request.security(syminfo.tickerid, timeframe.period, x, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
        return d

    def getLow(x, y, z, a):
        lastlow = y
        v = data(x)
        data_1 = data(z)
        m = v == lastlow or data_1 - v > a * syminfo.mintick
        if v != lastlow:
            lastlow = v
        if m:
            v = 0.0
        return (v, lastlow)

    def getHigh(x, y, z, a):
        lasthigh = y
        v = data(x)
        data_1 = data(z)
        m = v == lasthigh or v - data_1 > a * syminfo.mintick
        if v != lasthigh:
            lasthigh = v
        if m:
            v = 0.0
        return (v, lasthigh)

    v, e = getLow(ta.lowest(Depth), lastlow, low, Deviation)
    lastlow = e
    zBB = v != 0.0
    v1, e1 = getHigh(ta.highest(Depth), lasthigh, high, Deviation)
    lasthigh = e1
    zSS = v1 != 0.0
    zigzagDirection: Series = -1
    zigzagHigh: Series[int] = 0
    zigzagLow: Series[int] = 0
    zigzagDirection = 0 if zBB else 1 if zSS else nz(zigzagDirection[1], -1)
    virtualLow = zigzagLow[1] + 1
    if not zBB or (zBB and zigzagDirection == zigzagDirection[1] and (low > low[virtualLow])):
        zigzagLow = nz(zigzagLow[1]) + 1
    virtualHigh = zigzagHigh[1] + 1
    if not zSS or (zSS and zigzagDirection == zigzagDirection[1] and (high < high[virtualHigh])):
        zigzagHigh = nz(zigzagHigh[1]) + 1
    a = bar_index - zigzagLow
    b: Series = bar_index - zigzagHigh
    c: Persistent[Color] = na(Color)
    c = fixnan(color.lime if a < b[1] else color.red if a > b[1] else na)
    zigzag: Series[Line] = line.new(bar_index - zigzagLow, low[zigzagLow], bar_index - zigzagHigh, high[zigzagHigh], color=c, style=line.style_solid, width=4)
    if zigzagDirection == zigzagDirection[1]:
        line.delete(zigzag[1])
    zzPrevHigh: Series = zigzagHigh[1]
    zzPrevLow: Series = zigzagLow[1]
    if not na(zzPrevHigh[1]):
        zzPrevHigh = zzPrevHigh[1] + 1
    if not na(zzPrevLow[1]):
        zzPrevLow = zzPrevLow[1] + 1
    if zigzagDirection != zigzagDirection[1]:
        if zigzagDirection == 1:
            zzPrevHigh = zigzagHigh[1] + 1
        if zigzagDirection == 0:
            zzPrevLow = zigzagLow[1] + 1
    sma20 = ta.sma(src, 20)
    smapoint: int = 0
    smapoint = smapoint + 1 if src > sma20 else smapoint - 1
    ao = ta.sma(hl2, 5) - ta.sma(hl2, 34)
    aopoint = 1 if ao > 0 else -1 if ao < 0 else 0
    mom = src - src[14]
    mompoint = 1 if mom > 0 else -1 if mom < 0 else 0
    fast_ma = ta.ema(src, 12)
    slow_ma = ta.ema(src, 26)
    macd = fast_ma - slow_ma
    signal = ta.ema(macd, 9)
    hist: Series = macd - signal
    histpoint = 3 if hist > hist[1] else -3
    Length: int = 30
    r1 = math.max(open - close[1], high - low) if close[1] < open else high - low
    r2 = math.max(close[1] - open, high - low) if close[1] > open else high - low
    iff_1 = math.max(high - open, close - low) if close[1] > open else r1
    iff_2 = math.max(high - close[1], close - low) if close[1] < open else high - open
    iff_3 = iff_2 if high - close > close - low else r1
    iff_4 = iff_1 if high - close == close - low else iff_3
    iff_5 = math.max(high - close[1], close - low) if close[1] < open else math.max(high - open, close - low)
    iff_6 = iff_5 if close < open else r1
    bull = iff_4 if close == open else iff_6
    iff_7 = math.max(open - low, high - close) if close[1] < open else r2
    iff_8 = math.max(close[1] - low, high - close) if close[1] > open else open - low
    iff_9 = r2 if high - close > close - low else iff_8
    iff_10 = iff_7 if high - close == close - low else iff_9
    iff_11 = math.max(close[1] - low, high - close) if close[1] > open else math.max(open - low, high - close)
    iff_12 = r2 if close < open else iff_11
    bear = iff_10 if close == open else iff_12
    sma_1 = ta.sma(bull - bear, Length)
    colors = color.green if sma_1 > 0 else color.red
    bbpoint = 1 if ta.sma(bull - bear, Length) > 0 else -1
    length7: int = 7
    length14: int = 14
    length28: int = 28
    def average(bp, tr_, length):
        return math.sum(bp, length) / math.sum(tr_, length)

    high_ = math.max(high, src[1])
    low_ = math.min(low, src[1])
    bp = src - low_
    tr_ = high_ - low_
    avg7 = average(bp, tr_, length7)
    avg14 = average(bp, tr_, length14)
    avg28 = average(bp, tr_, length28)
    uoout = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7
    uopoint = 1 if uoout > 70 else -1 if uoout < 30 else 0
    conversionPeriods: int = 9
    basePeriods: int = 26
    laggingSpan2Periods: int = 52
    displacement: int = 26
    def donchian(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    baseLine = donchian(basePeriods)
    icpoint = 2 if src > baseLine else -2
    hullma = ta.hma(src, Period)
    hmapoint = 1 if src > hullma else -1
    trendDetectionLength: int = 4
    trend: Series[float] = na(float)
    wave: Series[float] = na(float)
    vol: Series[float] = na(float)
    mov: Series = 1 if src > src[1] else -1 if src < src[1] else 0
    trend = mov if mov != 0 and mov != mov[1] else nz(trend[1])
    falling_1 = ta.falling(src, trendDetectionLength)
    isTrending = ta.rising(src, trendDetectionLength) or falling_1
    wave = trend if trend != nz(wave[1]) and isTrending else nz(wave[1])
    vol = nz(vol[1]) + volume if wave == wave[1] else volume
    up1 = vol if wave == 1 else 0
    dn1 = 0 if wave == 1 else vol
    Weis = 2 if up1 > dn1 else -2
    stochlen: int = 14
    roclen: int = 20
    ccilen: int = 21
    dilen: int = 5
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(up if up > down and up > 0 else 0, len) / truerange)
        minus = fixnan(100 * ta.rma(down if down > up and down > 0 else 0, len) / truerange)
        return (plus, minus)

    def f_draw_infopanel(_x, _y, _line, _text, _color):
        _rep_text: str = ''
        for _l in pine_range(0, _line, 1):
            _rep_text = _rep_text + '\n'
        _rep_text = _rep_text + _text
        _la: Persistent[Label] = na(Label)
        label.delete(_la)
        _la = label.new(x=_x, y=_y, text=_rep_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.black, style=label.style_label_up, textcolor=_color, size=size.normal)
        return _la

    TD: Series[int] = 0
    TS: Series[int] = 0
    TD = nz(TD[1]) + 1 if src > src[4] else 0
    TS = nz(TS[1]) + 1 if src < src[4] else 0
    TDUp = TD - ta.valuewhen(TD < TD[1], TD, 1)
    TDDn = TS - ta.valuewhen(TS < TS[1], TS, 1)
    stoch = ta.stoch(src, high, low, stochlen)
    roc = ta.roc(src, roclen)
    Roc = 1 if roc > 0 else -1
    cci = ta.cci(src, ccilen)
    CCI = 1 if cci > 0 else -1
    plus, minus = dirmov(dilen)
    dmi = plus - minus
    DMI = 2 if dmi >= 0 else -2
    Zig = 1 if a < b else -1
    STT = 3 if trend10 == 1 else -3
    uptrend: Series[bool] = True
    newtrend: Series[bool] = False
    EP: Series = high
    SAR: Series = low
    AF: Series = AF_initial
    if not na(uptrend[1]) and (not na(newtrend[1])):
        if uptrend[1]:
            EP = math.max(high, EP[1])
        else:
            EP = math.min(low, EP[1])
        if newtrend[1]:
            AF = AF_initial
        else:
            if EP != EP[1]:
                AF = math.min(AF_maximum, AF[1] + AF_increment)
            else:
                AF = AF[1]
        SAR = SAR[1] + AF * (EP - SAR[1])
        if uptrend[1]:
            if newtrend:
                SAR = math.max(high, EP[1])
                EP = math.min(low, low[1])
            else:
                SAR = math.min(SAR, low[1])
                if not na(low[2]):
                    SAR = math.min(SAR, low[2])
                if SAR > low:
                    uptrend = False
                    newtrend = True
                    SAR = math.max(high, EP[1])
                    EP = math.min(low, low[1])
                else:
                    uptrend = True
                    newtrend = False
        else:
            if newtrend:
                SAR = math.min(low, EP[1])
                EP = math.max(high, high[1])
            else:
                SAR = math.max(SAR, high[1])
                if not na(high[2]):
                    SAR = math.max(SAR, high[2])
                if SAR < high:
                    uptrend = True
                    newtrend = True
                    SAR = math.min(low, EP[1])
                    EP = math.max(high, high[1])
                else:
                    uptrend = False
                    newtrend = False
    x = src - SAR
    sar = 3 if x > 0 else -3
    totalpoints = sar + STT + Zig + Roc + DMI + CCI + Weis + smapoint + aopoint + mompoint + histpoint + bbpoint + icpoint + hmapoint
    color2 = color.lime if trend10 == 1 else color.red
    bgcolor(color2 if Bgcolor else na)
    info_panel_x = timenow - math.round(ta.change(time) * info_label_pos)
    info_panel_y = src
    BuyPoints = EnterPoints
    SellPoints = EnterPoints - EnterPoints * 2
    info_title = '-- EasySys420 --' + '\n '
    info_div1 = '\nSup Trend ' + string.tostring(trend10)
    info_div2 = '\nSAR ' + string.tostring(sar)
    info_div3 = '\nSTT ' + string.tostring(STT)
    info_div4 = '\nZig ' + string.tostring(Zig)
    info_div5 = '\nRoc ' + string.tostring(Roc)
    info_div6 = '\nDMI ' + string.tostring(DMI)
    info_div7 = '\nCCI ' + string.tostring(CCI)
    info_div8 = '\nWeis ' + string.tostring(Weis)
    info_div9 = '\nSMA ' + string.tostring(smapoint)
    info_div10 = '\nAO ' + string.tostring(aopoint)
    info_div11 = '\nMOM ' + string.tostring(mompoint)
    info_div12 = '\nHist ' + string.tostring(histpoint)
    info_div13 = '\nBB ' + string.tostring(bbpoint)
    info_div14 = '\nIchi ' + string.tostring(icpoint)
    info_div15 = '\nHMA ' + string.tostring(hmapoint)
    info_div16: str = '\n------------------'
    info_current_close = '\nTotal points: ' + string.tostring(totalpoints) + '\n------------------'
    info_current_buy = '\nBuying @: ' + string.tostring(BuyPoints)
    info_current_sell = '\nSelling @: ' + string.tostring(SellPoints)
    info_text = info_title + info_div1 + info_div2 + info_div3 + info_div4 + info_div5 + info_div6 + info_div7 + info_div8 + info_div9 + info_div10 + info_div11 + info_div12 + info_div13 + info_div14 + info_div15 + info_div16 + info_current_close + info_current_buy + info_current_sell
    info_panel: Series = label.new(x=info_panel_x, y=info_panel_y, text=info_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.yellow, style=label.style_label_up, textcolor=color.black, size=info_label_size) if disp_panels else na
    label.delete(info_panel[1])
    if totalpoints > BuyPoints and trend10 == 1 or (Zig == 1 and trend10 == 1):
        strategy.entry('BUY', strategy.long)
    if totalpoints < SellPoints and trend10 == -1 or (Zig == -1 and trend10 == -1):
        strategy.entry('SELL', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
