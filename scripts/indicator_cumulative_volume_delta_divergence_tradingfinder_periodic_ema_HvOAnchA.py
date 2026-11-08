"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, close, color, high, input, label, line, low, math, na, nz,
    plot, request, script, size, syminfo, ta, timeframe, volume
)
from pynecore.types import Label, Line, Persistent, PersistentSeries, Series


@script.indicator('Cumulative Volume Delta Divergence [TradingFinder] Periodic EMA', shorttitle='CVD Divergence Oscillator', overlay=False, max_bars_back=5000, max_labels_count=500, max_lines_count=500)
def main(
    n=input.int(2, title='Divergence Fractal Periods', minval=1, group='Logic Setting'),
    Period=input.int(21, 'CVD Period', group='Logic Setting'),
    CumMode=input.string('Periodic', 'Cumulative Mode', options=('Periodic', 'EMA'), group='Logic Setting'),
    UltraData=input.bool(False, '', inline='Data', group='Logic Setting'),
    Market=input.string('Forex', 'Market Ultra Data', options=('Forex', 'Crypto', 'Stock'), inline='Data', group='Logic Setting'),
    Show_Label=input.string('Yes', 'Show Label', options=('Yes', 'No'), group='display Setting')
):
    ATR = ta.atr(55)
    aa: Persistent[str] = ''
    b: Persistent[str] = ''
    c: Persistent[str] = ''
    d: Persistent[str] = ''
    e: Persistent[str] = ''
    f: Persistent[str] = ''
    g: Persistent[str] = ''
    h: Persistent[str] = ''
    i: Persistent[str] = ''
    j: Persistent[str] = ''
    k: Persistent[str] = ''
    l: Persistent[str] = ''
    m: Persistent[str] = ''
    nn: Persistent[str] = ''
    o: Persistent[str] = ''
    p: Persistent[str] = ''
    q: Persistent[str] = ''
    r: Persistent[str] = ''
    s: Persistent[str] = ''
    t: Persistent[str] = ''
    u: Persistent[str] = ''
    v: Persistent[str] = ''
    w: Persistent[str] = ''
    x: Persistent[str] = ''
    y: Persistent[str] = ''
    z: Persistent[str] = ''
    __switch__ = Market
    if __switch__ == 'Forex':
        aa = 'FX'
        b = 'OANDA'
        c = 'FOREXCOM'
        d = 'FX_IDC'
        e = 'PEPPERSTONE'
        f = 'CAPITALCOM'
        g = 'ICMARKETS'
        h = 'EIGHTCAP'
        i = 'SAXO'
        j = 'BLACKBULL'
        k = 'VANTAGE'
        l = 'FUSIONMARKETS'
        m = 'FPMARKETS'
        nn = 'GBEBROKERS'
        o = 'IBKR'
        p = 'ACTIVTRADES'
        q = 'EASYMARKETS'
        r = 'FXOPEN'
        s = 'CITYINDEX'
        t = 'AFTERPRIME'
        u = 'SKILLING'
        v = 'WHSELFINVEST'
        w = 'TRADENATION'
        x = 'THINKMARKETS'
        y = 'CFI'
        z = 'PHILLIPNOVA'
    elif __switch__ == 'Crypto':
        aa = 'BITSTAMP'
        b = 'COINBASE'
        c = 'INDEX'
        d = 'CRYPTO'
        e = 'BINANCE'
        f = 'BITFINEX'
        g = 'KRAKEN'
        h = 'OANDA'
        i = 'PEPPERSTONE'
        j = 'GEMINI'
        k = 'EIGHTCAP'
        l = 'ICMARKETS'
        m = 'VANTAGE'
        nn = 'CAPITALCOM'
        o = 'FOREXCOM'
        p = 'FX'
        q = 'BLACKBULL'
        r = 'SAXO'
        s = 'FUSIONMARKETS'
        t = 'CRYPTOCOM'
        u = 'EASYMARKETS'
        v = 'OKCOIN'
        w = 'FPMARKETS'
        x = 'AFTERPRIME'
        y = 'ACTIVTRADES'
        z = 'BTSE'
    elif __switch__ == 'Stock':
        aa = '-'
        b = '-'
        c = '-'
        d = '-'
        e = '-'
        f = '-'
        g = '-'
        h = '-'
        i = '-'
        j = '-'
        k = '-'
        l = '-'
        m = '-'
        nn = '-'
        o = '-'
        p = '-'
        q = '-'
        r = '-'
        s = '-'
        t = '-'
        u = '-'
        v = '-'
        w = '-'
        x = '-'
        y = '-'
        z = '-'
    V = nz(request.security(syminfo.tickerid, timeframe.period, volume, ignore_invalid_symbol=True))
    Va = nz(request.security(aa + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vb = nz(request.security(b + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vc = nz(request.security(c + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vd = nz(request.security(d + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Ve = nz(request.security(e + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vf = nz(request.security(f + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vg = nz(request.security(g + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vh = nz(request.security(h + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vi = nz(request.security(i + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vj = nz(request.security(j + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vk = nz(request.security(k + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vl = nz(request.security(l + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vm = nz(request.security(m + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vn = nz(request.security(nn + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vo = nz(request.security(o + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vp = nz(request.security(p + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vq = nz(request.security(q + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vr = nz(request.security(r + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vs = nz(request.security(s + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vt = nz(request.security(t + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vu = nz(request.security(u + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vv = nz(request.security(v + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vw = nz(request.security(w + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vx = nz(request.security(x + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vy = nz(request.security(y + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vz = nz(request.security(z + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol=True))
    Vsum = V + Va + Vb + Vc + Vd + Ve + Vf + Vg + Vh + Vi + Vj + Vk + Vl + Vm + Vn + Vo + Vp + Vq + Vr + Vs + Vt + Vu + Vv + Vw + Vx + Vy + Vz
    __block_result__ = na
    if UltraData:
        __block_result__ = Vsum
    else:
        __block_result__ = volume
    Volume = __block_result__
    Buying = Volume * ((close - low) / (high - low))
    Selling = Volume * ((high - close) / (high - low))
    delta = Buying - Selling
    __block_keep_1__: PersistentSeries = na
    if CumMode == 'Periodic':
        __block_keep_1__ = math.sum(delta, Period)
    elif CumMode == 'EMA':
        __block_keep_1__ = ta.ema(delta, Period)
    Hist: Series = __block_keep_1__
    EMA = ta.ema(close, 50)
    up_trend = close[n] > EMA
    down_trend = close[n] < EMA
    UpPivot = ta.pivothigh(n, n)
    downPivot = ta.pivotlow(n, n)
    upFractal = cast_bool(UpPivot) and up_trend
    downFractal = cast_bool(downPivot) and down_trend
    High_Last_Price = ta.valuewhen(upFractal, high[n], 0)
    High_Per_Price = ta.valuewhen(upFractal, high[n], 1)
    High_Last_Hist = ta.valuewhen(upFractal, Hist[n], 0)
    High_Per_Hist = ta.valuewhen(upFractal, Hist[n], 1)
    High_Last_Bar = ta.valuewhen(upFractal, bar_index[n], 0)
    High_Per_Bar = ta.valuewhen(upFractal, bar_index[n], 1)
    Time_Condition_Bear = High_Last_Bar + 30 > bar_index
    __block_result_2__ = na
    if High_Last_Hist > 0 and High_Per_Hist > 0 and Time_Condition_Bear and (High_Last_Bar - High_Per_Bar < 30):
        __block_result_2__ = High_Last_Price > High_Per_Price and High_Last_Hist < High_Per_Hist
    else:
        __block_result_2__ = False
    Last_Bearish_Divergece = __block_result_2__
    CBearDive: Persistent[int] = 0
    if cast_bool(ta.change(High_Last_Price)) and Last_Bearish_Divergece == True:
        CBearDive = CBearDive + 1
    elif Last_Bearish_Divergece == False:
        CBearDive = 0
    Bear_Phase: Persistent[bool] = na(bool)
    __block_result_3__ = na
    if not na(High_Last_Bar - High_Per_Bar):
        __block_result_3__ = High_Last_Bar - High_Per_Bar
    else:
        __block_result_3__ = 1
    len_back_for_Bear_Phase_check = __block_result_3__
    if cast_bool(ta.change(High_Last_Price)) and Last_Bearish_Divergece == True:
        for i__00000064__ in pine_range(n + 1, n + 1 + len_back_for_Bear_Phase_check, 1):
            if Hist[i__00000064__] < 0:
                Bear_Phase = True
    elif Last_Bearish_Divergece == False:
        Bear_Phase = False
    Low_Last_Price = ta.valuewhen(downFractal, low[n], 0)
    Low_Per_Price = ta.valuewhen(downFractal, low[n], 1)
    Low_Last_Hist = ta.valuewhen(downFractal, Hist[n], 0)
    Low_Per_Hist = ta.valuewhen(downFractal, Hist[n], 1)
    Low_Last_Bar = ta.valuewhen(downFractal, bar_index[n], 0)
    Low_Per_Bar = ta.valuewhen(downFractal, bar_index[n], 1)
    Time_Condition_Bull = Low_Last_Bar + 30 > bar_index
    __block_result_4__ = na
    if Low_Last_Hist < 0 and Low_Per_Hist < 0 and Time_Condition_Bull and (Low_Last_Bar - Low_Per_Bar < 30):
        __block_result_4__ = Low_Last_Price < Low_Per_Price and Low_Last_Hist > Low_Per_Hist
    else:
        __block_result_4__ = False
    Last_Bullish_Divergece = __block_result_4__
    CBullDive: Persistent[int] = 0
    if cast_bool(ta.change(Low_Last_Price)) and Last_Bullish_Divergece == True:
        CBullDive = CBullDive + 1
    elif Last_Bullish_Divergece == False:
        CBullDive = 0
    Bull_Phase: Persistent[bool] = na(bool)
    __block_result_5__ = na
    if not na(Low_Last_Bar - Low_Per_Bar):
        __block_result_5__ = Low_Last_Bar - Low_Per_Bar
    else:
        __block_result_5__ = 1
    len_back_for_Bull_Phase_check = __block_result_5__
    if cast_bool(ta.change(Low_Last_Price)) and Last_Bullish_Divergece == True:
        for i__0000007e__ in pine_range(n + 1, n + 1 + len_back_for_Bull_Phase_check, 1):
            if Hist[i__0000007e__] > 0:
                Bull_Phase = True
    elif Last_Bullish_Divergece == False:
        Bull_Phase = False
    __block_result_6__ = na
    if CBullDive == 1:
        __block_result_6__ = 'Normal Bull Dive'
    elif CBullDive == 2:
        __block_result_6__ = 'Good Bull Dive'
    elif CBullDive >= 3:
        __block_result_6__ = 'Strong Bull Dive'
    else:
        __block_result_6__ = '-'
    text_power_bull = __block_result_6__
    __block_result_7__ = na
    if CBearDive == 1:
        __block_result_7__ = 'Normal Bear Dive'
    elif CBearDive == 2:
        __block_result_7__ = 'Good Bear Dive'
    elif CBearDive >= 3:
        __block_result_7__ = 'Strong Bear Dive'
    else:
        __block_result_7__ = '-'
    text_power_bear = __block_result_7__
    def Drawing():
        BeLine: Persistent[Line] = na(Line)
        BuLine: Persistent[Line] = na(Line)
        BeLabel: Persistent[Label] = na(Label)
        BuLabel: Persistent[Label] = na(Label)
        BeLine_OnChart: Persistent[Line] = na(Line)
        BuLine_OnChart: Persistent[Line] = na(Line)
        BeLabel_OnChart: Persistent[Label] = na(Label)
        BuLabel_OnChart: Persistent[Label] = na(Label)
        if Last_Bullish_Divergece:
            BuLine = line.new(Low_Per_Bar, Low_Per_Hist, Low_Last_Bar, Low_Last_Hist, color=color.rgb(21, 151, 25), width=2)
            if Show_Label == 'Yes':
                BuLabel = label.new(Low_Last_Bar, Low_Last_Hist, '+RD', color=color.green, textcolor=color.white, size=size.tiny, style=label.style_label_up)
            BuLine_OnChart = line.new(Low_Per_Bar, low[bar_index - Low_Per_Bar], Low_Last_Bar, low[bar_index - Low_Last_Bar], color=color.rgb(21, 151, 25), width=2, force_overlay=True)
            if Show_Label == 'Yes':
                BuLabel_OnChart = label.new(Low_Last_Bar, low[bar_index - Low_Last_Bar], '+RD', color=color.green, textcolor=color.white, size=size.tiny, style=label.style_label_up, force_overlay=True)
        __block_result_8__ = na
        if Last_Bearish_Divergece:
            BeLine = line.new(High_Per_Bar, High_Per_Hist, High_Last_Bar, High_Last_Hist, color=color.rgb(212, 44, 44), width=2)
            if Show_Label == 'Yes':
                BeLabel = label.new(High_Last_Bar, High_Last_Hist, '-RD', color=color.red, textcolor=color.white, size=size.tiny, style=label.style_label_down)
            BeLine_OnChart = line.new(High_Per_Bar, high[bar_index - High_Per_Bar], High_Last_Bar, high[bar_index - High_Last_Bar], color=color.rgb(212, 44, 44), width=2, force_overlay=True)
            __block_result_9__ = na
            if Show_Label == 'Yes':
                BeLabel_OnChart = label.new(High_Last_Bar, high[bar_index - High_Last_Bar], '-RD', color=color.red, textcolor=color.white, size=size.tiny, style=label.style_label_down, force_overlay=True)
                __block_result_9__ = BeLabel_OnChart
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    __block_result_10__ = na
    if Hist > 0:
        __block_result_10__ = color.rgb(76, 175, 79, 50)
    elif Hist < 0:
        __block_result_10__ = color.rgb(255, 82, 82, 50)
    Hist_Color = __block_result_10__
    plot(Hist, 'Show Cumulative Vol Delta', color=Hist_Color, style=plot.style_columns)
    Drawing()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
