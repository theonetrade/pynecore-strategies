"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, color, display, fill, hl2, input, label, location, math,
    na, nz, ohlc4, plot, plotshape, request, script, shape, size, strategy, ta, time, timeframe,
    timestamp, xloc, yloc
)
from pynecore.types import Label, NA, Persistent, Series


@script.strategy('PMax Explorer', shorttitle='PMEx', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(hl2, title='Source'),
    Periods=input(title='ATR Length', defval=10),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    mav=input.string(title='Moving Average Type', defval='EMA', options=('SMA', 'EMA', 'WMA', 'TMA', 'VAR', 'WWMA', 'ZLEMA', 'TSF')),
    length=input.int(10, 'Moving Average Length', minval=1),
    changeATR=input(title='Change ATR Calculation Method ?', defval=True),
    showsupport=input(title='Show Moving Average?', defval=True),
    showsignalsk=input(title='Show Crossing Signals?', defval=True),
    showsignalsc=input(title='Show Price/Pmax Crossing Signals?', defval=False),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    showscr=input(True, title='Show Screener Label'),
    posX_scr=input(20, title='Pos. Label x-axis'),
    posY_scr=input(1, title='Pos. Size Label y-axis'),
    colinput=input.string(title='Label Color', defval='Blue', options=('White', 'Black', 'Red', 'Green', 'Yellow', 'Blue')),
    dummy0=input(True, title='=Backtest Inputs='),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromYear=input.int(defval=2005, title='From Year', minval=2005),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToYear=input.int(defval=9999, title='To Year', minval=2006),
    t1=input.symbol('EURUSD', title='Symbol 01'),
    t2=input.symbol('XAUUSD', title='Symbol 02'),
    t3=input.symbol('AMZN', title='Symbol 03'),
    t4=input.symbol('TSLA', title='Symbol 04'),
    t5=input.symbol('BTCUSDT', title='Symbol 05'),
    t6=input.symbol('ETHBTC', title='Symbol 06'),
    t7=input.symbol('XBTUSD', title='Symbol 07'),
    t8=input.symbol('XRPBTC', title='Symbol 08'),
    t9=input.symbol('THYAO', title='Symbol 09'),
    t10=input.symbol('GARAN', title='Symbol 10'),
    t11=input.symbol('USDTRY', title='Symbol 11'),
    t12=input.symbol('PETKM', title='Symbol 12'),
    t13=input.symbol('AAPL', title='Symbol 13'),
    t14=input.symbol('TUPRS', title='Symbol 14'),
    t15=input.symbol('HALKB', title='Symbol 15'),
    t16=input.symbol('AVAXUSDT', title='Symbol 16'),
    t17=input.symbol('ETHUSDT', title='Symbol 17'),
    t18=input.symbol('UKOIL', title='Symbol 18'),
    t19=input.symbol('ABNB', title='Symbol 19'),
    t20=input.symbol('SISE', title='Symbol 20')
):
    atr2 = ta.sma(ta.tr, Periods)
    atr = ta.atr(Periods) if changeATR else atr2
    def Var_Func(src: Series, length):
        valpha = 2 / (length + 1)
        vud1 = src - src[1] if src > src[1] else 0
        vdd1 = src[1] - src if src < src[1] else 0
        vUD = math.sum(vud1, 9)
        vDD = math.sum(vdd1, 9)
        vCMO = nz((vUD - vDD) / (vUD + vDD))
        VAR: Series[float] = 0.0
        VAR = nz(valpha * math.abs(vCMO) * src) + (1 - valpha * math.abs(vCMO)) * nz(VAR[1])
        return VAR

    VAR = Var_Func(src, length)
    def Wwma_Func(src, length):
        wwalpha = 1 / length
        WWMA: Series[float] = 0.0
        WWMA = wwalpha * src + (1 - wwalpha) * nz(WWMA[1])
        return WWMA

    WWMA = Wwma_Func(src, length)
    def Zlema_Func(src: Series, length):
        zxLag = length / 2 if length / 2 == math.round(length / 2) else (length - 1) / 2
        zxEMAData = src + src - src[zxLag]
        ZLEMA = ta.ema(zxEMAData, length)
        return ZLEMA

    ZLEMA = Zlema_Func(src, length)
    def Tsf_Func(src, length):
        lrc = ta.linreg(src, length, 0)
        lrc1 = ta.linreg(src, length, 1)
        lrs = lrc - lrc1
        TSF = ta.linreg(src, length, 0) + lrs
        return TSF

    TSF = Tsf_Func(src, length)
    def getMA(src, length):
        ma: float = 0.0
        if mav == 'SMA':
            ma = ta.sma(src, length)
        if mav == 'EMA':
            ma = ta.ema(src, length)
        if mav == 'WMA':
            ma = ta.wma(src, length)
        if mav == 'TMA':
            ma = ta.sma(ta.sma(src, math.ceil(length / 2)), math.floor(length / 2) + 1)
        if mav == 'VAR':
            ma = VAR
        if mav == 'WWMA':
            ma = WWMA
        if mav == 'ZLEMA':
            ma = ZLEMA
        if mav == 'TSF':
            ma = TSF
        return ma

    MAvg: Series = getMA(src, length)
    def Pmax_Func(src, length):
        longStop: Series = MAvg - Multiplier * atr
        longStopPrev = nz(longStop[1], longStop)
        longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
        shortStop: Series = MAvg + Multiplier * atr
        shortStopPrev = nz(shortStop[1], shortStop)
        shortStop = math.min(shortStop, shortStopPrev) if MAvg < shortStopPrev else shortStop
        dir: Series[int] = 1
        dir = nz(dir[1], dir)
        dir = 1 if dir == -1 and MAvg > shortStopPrev else -1 if dir == 1 and MAvg < longStopPrev else dir
        PMax = longStop if dir == 1 else shortStop
        return PMax

    PMax = Pmax_Func(src, length)
    plot(MAvg if showsupport else na, color=color.new(color.new('#0585E1'), 0), linewidth=2, title='Moving Avg Line')
    pALL = plot(PMax, color=color.new(color.red, 0), linewidth=2, title='PMax')
    alertcondition(ta.cross(MAvg, PMax), title='Cross Alert', message='PMax - Moving Avg Crossing!')
    alertcondition(ta.crossover(MAvg, PMax), title='Crossover Alarm', message='Moving Avg BUY SIGNAL!')
    alertcondition(ta.crossunder(MAvg, PMax), title='Crossunder Alarm', message='Moving Avg SELL SIGNAL!')
    alertcondition(ta.cross(src, PMax), title='Price Cross Alert', message='PMax - Price Crossing!')
    alertcondition(ta.crossover(src, PMax), title='Price Crossover Alarm', message='PRICE OVER PMax - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, PMax), title='Price Crossunder Alarm', message='PRICE UNDER PMax - SELL SIGNAL!')
    buySignalk = ta.crossover(MAvg, PMax)
    plotshape(PMax * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, PMax)
    plotshape(PMax * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    buySignalc = ta.crossover(src, PMax)
    plotshape(PMax * 0.995 if buySignalc and showsignalsc else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    sellSignallc = ta.crossunder(src, PMax)
    plotshape(PMax * 1.005 if sellSignallc and showsignalsc else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)
    col = color.gray
    if colinput == 'White':
        col = color.white
    if colinput == 'Black':
        col = color.black
    if colinput == 'Red':
        col = color.red
    if colinput == 'Green':
        col = color.green
    if colinput == 'Yellow':
        col = color.yellow
    if colinput == 'Blue':
        col = color.blue
    Start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    Finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def Timerange():
        return True if time >= Start and time <= Finish else False

    if buySignalk:
        if Timerange():
            strategy.entry('Long', strategy.long)
    if sellSignallk:
        if Timerange():
            strategy.entry('Short', strategy.short)
    def Pmax(Multiplier, Periods):
        __hist_MAvg__: Series = MAvg[0]
        Up = MAvg - Multiplier * atr
        Dn = MAvg + Multiplier * atr
        TrendUp: Series[float] = 0.0
        TrendUp = math.max(Up, TrendUp[1]) if __hist_MAvg__[1] > TrendUp[1] else Up
        TrendDown: Series[float] = 0.0
        TrendDown = math.min(Dn, TrendDown[1]) if __hist_MAvg__[1] < TrendDown[1] else Dn
        Trend: Series[float] = 0.0
        Trend = 1 if MAvg > TrendDown[1] else -1 if MAvg < TrendUp[1] else nz(Trend[1], 1)
        Tsl = TrendUp if Trend == 1 else TrendDown
        S_Buy = 1 if Trend == 1 else 0
        S_Sell = 1 if Trend != 1 else 0
        return (Trend, Tsl)

    Trend: Series
    Trend, Tsl = Pmax(Multiplier, Periods)
    TrendReversal = Trend != Trend[1]
    t01: Series
    t01, s01 = request.security(t1, timeframe.period, Pmax(Multiplier, Periods))
    t02: Series
    t02, s02 = request.security(t2, timeframe.period, Pmax(Multiplier, Periods))
    t03: Series
    t03, s03 = request.security(t3, timeframe.period, Pmax(Multiplier, Periods))
    t04: Series
    t04, s04 = request.security(t4, timeframe.period, Pmax(Multiplier, Periods))
    t05: Series
    t05, s05 = request.security(t5, timeframe.period, Pmax(Multiplier, Periods))
    t06: Series
    t06, s06 = request.security(t6, timeframe.period, Pmax(Multiplier, Periods))
    t07: Series
    t07, s07 = request.security(t7, timeframe.period, Pmax(Multiplier, Periods))
    t08: Series
    t08, s08 = request.security(t8, timeframe.period, Pmax(Multiplier, Periods))
    t09: Series
    t09, s09 = request.security(t9, timeframe.period, Pmax(Multiplier, Periods))
    t010: Series
    t010, s010 = request.security(t10, timeframe.period, Pmax(Multiplier, Periods))
    t011: Series
    t011, s011 = request.security(t11, timeframe.period, Pmax(Multiplier, Periods))
    t012: Series
    t012, s012 = request.security(t12, timeframe.period, Pmax(Multiplier, Periods))
    t013: Series
    t013, s013 = request.security(t13, timeframe.period, Pmax(Multiplier, Periods))
    t014: Series
    t014, s014 = request.security(t14, timeframe.period, Pmax(Multiplier, Periods))
    t015: Series
    t015, s015 = request.security(t15, timeframe.period, Pmax(Multiplier, Periods))
    t016: Series
    t016, s016 = request.security(t16, timeframe.period, Pmax(Multiplier, Periods))
    t017: Series
    t017, s017 = request.security(t17, timeframe.period, Pmax(Multiplier, Periods))
    t018: Series
    t018, s018 = request.security(t18, timeframe.period, Pmax(Multiplier, Periods))
    t019: Series
    t019, s019 = request.security(t19, timeframe.period, Pmax(Multiplier, Periods))
    t020: Series
    t020, s020 = request.security(t20, timeframe.period, Pmax(Multiplier, Periods))
    tr01: Series = t01 != t01[1]
    up01: Series = t01 == 1
    dn01: Series = t01 == -1
    tr02: Series = t02 != t02[1]
    up02: Series = t02 == 1
    dn02: Series = t02 == -1
    tr03: Series = t03 != t03[1]
    up03: Series = t03 == 1
    dn03: Series = t03 == -1
    tr04: Series = t04 != t04[1]
    up04: Series = t04 == 1
    dn04: Series = t04 == -1
    tr05: Series = t05 != t05[1]
    up05: Series = t05 == 1
    dn05: Series = t05 == -1
    tr06: Series = t06 != t06[1]
    up06: Series = t06 == 1
    dn06: Series = t06 == -1
    tr07: Series = t07 != t07[1]
    up07: Series = t07 == 1
    dn07: Series = t07 == -1
    tr08: Series = t08 != t08[1]
    up08: Series = t08 == 1
    dn08: Series = t08 == -1
    tr09: Series = t09 != t09[1]
    up09: Series = t09 == 1
    dn09: Series = t09 == -1
    tr010: Series = t010 != t010[1]
    up010: Series = t010 == 1
    dn010: Series = t010 == -1
    tr011: Series = t011 != t011[1]
    up011: Series = t011 == 1
    dn011: Series = t011 == -1
    tr012: Series = t012 != t012[1]
    up012: Series = t012 == 1
    dn012: Series = t012 == -1
    tr013: Series = t013 != t013[1]
    up013: Series = t013 == 1
    dn013: Series = t013 == -1
    tr014: Series = t014 != t014[1]
    up014: Series = t014 == 1
    dn014: Series = t014 == -1
    tr015: Series = t015 != t015[1]
    up015: Series = t015 == 1
    dn015: Series = t015 == -1
    tr016: Series = t016 != t016[1]
    up016: Series = t016 == 1
    dn016: Series = t016 == -1
    tr017: Series = t017 != t017[1]
    up017: Series = t017 == 1
    dn017: Series = t017 == -1
    tr018: Series = t018 != t018[1]
    up018: Series = t018 == 1
    dn018: Series = t018 == -1
    tr019: Series = t019 != t019[1]
    up019: Series = t019 == 1
    dn019: Series = t019 == -1
    tr020: Series = t020 != t020[1]
    up020: Series = t020 == 1
    dn020: Series = t020 == -1
    pot_label: str = 'Potential Reversal: \n'
    pot_label = pot_label + t1 + '\n' if tr01 else pot_label
    pot_label = pot_label + t2 + '\n' if tr02 else pot_label
    pot_label = pot_label + t3 + '\n' if tr03 else pot_label
    pot_label = pot_label + t4 + '\n' if tr04 else pot_label
    pot_label = pot_label + t5 + '\n' if tr05 else pot_label
    pot_label = pot_label + t6 + '\n' if tr06 else pot_label
    pot_label = pot_label + t7 + '\n' if tr07 else pot_label
    pot_label = pot_label + t8 + '\n' if tr08 else pot_label
    pot_label = pot_label + t9 + '\n' if tr09 else pot_label
    pot_label = pot_label + t10 + '\n' if tr010 else pot_label
    pot_label = pot_label + t11 + '\n' if tr011 else pot_label
    pot_label = pot_label + t12 + '\n' if tr012 else pot_label
    pot_label = pot_label + t13 + '\n' if tr013 else pot_label
    pot_label = pot_label + t14 + '\n' if tr014 else pot_label
    pot_label = pot_label + t15 + '\n' if tr015 else pot_label
    pot_label = pot_label + t16 + '\n' if tr016 else pot_label
    pot_label = pot_label + t17 + '\n' if tr017 else pot_label
    pot_label = pot_label + t18 + '\n' if tr018 else pot_label
    pot_label = pot_label + t19 + '\n' if tr019 else pot_label
    pot_label = pot_label + t20 + '\n' if tr020 else pot_label
    scr_label: str = 'Confirmed Reversal: \n'
    scr_label = scr_label + t1 + '\n' if tr01[1] else scr_label
    scr_label = scr_label + t2 + '\n' if tr02[1] else scr_label
    scr_label = scr_label + t3 + '\n' if tr03[1] else scr_label
    scr_label = scr_label + t4 + '\n' if tr04[1] else scr_label
    scr_label = scr_label + t5 + '\n' if tr05[1] else scr_label
    scr_label = scr_label + t6 + '\n' if tr06[1] else scr_label
    scr_label = scr_label + t7 + '\n' if tr07[1] else scr_label
    scr_label = scr_label + t8 + '\n' if tr08[1] else scr_label
    scr_label = scr_label + t9 + '\n' if tr09[1] else scr_label
    scr_label = scr_label + t10 + '\n' if tr010[1] else scr_label
    scr_label = scr_label + t11 + '\n' if tr011[1] else scr_label
    scr_label = scr_label + t12 + '\n' if tr012[1] else scr_label
    scr_label = scr_label + t13 + '\n' if tr013[1] else scr_label
    scr_label = scr_label + t14 + '\n' if tr014[1] else scr_label
    scr_label = scr_label + t15 + '\n' if tr015[1] else scr_label
    scr_label = scr_label + t16 + '\n' if tr016[1] else scr_label
    scr_label = scr_label + t17 + '\n' if tr017[1] else scr_label
    scr_label = scr_label + t18 + '\n' if tr018[1] else scr_label
    scr_label = scr_label + t19 + '\n' if tr019[1] else scr_label
    scr_label = scr_label + t20 + '\n' if tr020[1] else scr_label
    up_label: str = 'Uptrend: \n'
    up_label = up_label + t1 + '\n' if up01[1] else up_label
    up_label = up_label + t2 + '\n' if up02[1] else up_label
    up_label = up_label + t3 + '\n' if up03[1] else up_label
    up_label = up_label + t4 + '\n' if up04[1] else up_label
    up_label = up_label + t5 + '\n' if up05[1] else up_label
    up_label = up_label + t6 + '\n' if up06[1] else up_label
    up_label = up_label + t7 + '\n' if up07[1] else up_label
    up_label = up_label + t8 + '\n' if up08[1] else up_label
    up_label = up_label + t9 + '\n' if up09[1] else up_label
    up_label = up_label + t10 + '\n' if up010[1] else up_label
    up_label = up_label + t11 + '\n' if up011[1] else up_label
    up_label = up_label + t12 + '\n' if up012[1] else up_label
    up_label = up_label + t13 + '\n' if up013[1] else up_label
    up_label = up_label + t14 + '\n' if up014[1] else up_label
    up_label = up_label + t15 + '\n' if up015[1] else up_label
    up_label = up_label + t16 + '\n' if up016[1] else up_label
    up_label = up_label + t17 + '\n' if up017[1] else up_label
    up_label = up_label + t18 + '\n' if up018[1] else up_label
    up_label = up_label + t19 + '\n' if up019[1] else up_label
    up_label = up_label + t20 + '\n' if up020[1] else up_label
    dn_label: str = 'Downtrend: \n'
    dn_label = dn_label + t1 + '\n' if dn01[1] else dn_label
    dn_label = dn_label + t2 + '\n' if dn02[1] else dn_label
    dn_label = dn_label + t3 + '\n' if dn03[1] else dn_label
    dn_label = dn_label + t4 + '\n' if dn04[1] else dn_label
    dn_label = dn_label + t5 + '\n' if dn05[1] else dn_label
    dn_label = dn_label + t6 + '\n' if dn06[1] else dn_label
    dn_label = dn_label + t7 + '\n' if dn07[1] else dn_label
    dn_label = dn_label + t8 + '\n' if dn08[1] else dn_label
    dn_label = dn_label + t9 + '\n' if dn09[1] else dn_label
    dn_label = dn_label + t10 + '\n' if dn010[1] else dn_label
    dn_label = dn_label + t11 + '\n' if dn011[1] else dn_label
    dn_label = dn_label + t12 + '\n' if dn012[1] else dn_label
    dn_label = dn_label + t13 + '\n' if dn013[1] else dn_label
    dn_label = dn_label + t14 + '\n' if dn014[1] else dn_label
    dn_label = dn_label + t15 + '\n' if dn015[1] else dn_label
    dn_label = dn_label + t16 + '\n' if dn016[1] else dn_label
    dn_label = dn_label + t17 + '\n' if dn017[1] else dn_label
    dn_label = dn_label + t18 + '\n' if dn018[1] else dn_label
    dn_label = dn_label + t19 + '\n' if dn019[1] else dn_label
    dn_label = dn_label + t20 + '\n' if dn020[1] else dn_label
    def f_colorscr(_valscr):
        return color.new('#00000000') if _valscr else na

    def f_printscr(_txtscr):
        _lblscr: Persistent = NA(Label)
        label.delete(_lblscr)
        _lblscr = label.new(time + (time - time[1]) * posX_scr, ohlc4[posY_scr], _txtscr, xloc.bar_time, yloc.price, f_colorscr(showscr), textcolor=col if showscr else na, size=size.normal, style=label.style_label_center)
        return _lblscr

    f_printscr(scr_label + '\n' + pot_label + '\n' + up_label + '\n' + dn_label)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
