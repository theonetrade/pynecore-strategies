"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bgcolor, close, color, dayofmonth, dayofweek, fill,
    input, location, month, na, open, plot, plotshape, script, shape, size, ta, time, timestamp,
    year
)
from pynecore.types import Series


@script.indicator(title='TMA Overlay', shorttitle='TMA Overlay', overlay=True, na_bool=True)
def main(
    h100=input.bool(title='Show 100 Line', defval=True, group='Smoothed MA Inputs'),
    trendFill=input.bool(title='Show Trend Fill', defval=True, group='Smoothed MA Inputs'),
    bearS=input.bool(title='Show Bearish 3 Line Strike', defval=True, group='3 Line Strike'),
    bullS=input.bool(title='Show Bullish 3 Line Strike', defval=True, group='3 Line Strike'),
    bearE=input.bool(title='Show Bearish Big A$$ Candles', defval=True, group='Big A$$ Candles'),
    bullE=input.bool(title='Show Bullish Big A$$ Candles', defval=True, group='Big A$$ Candles'),
    ts=input.bool(title='Show Trade Session', defval=True, group='Trade Session'),
    tz=input.string(title='Timezone', defval='America/Chicago', options=('Asia/Sydney', 'Asia/Tokyo', 'Europe/Frankfurt', 'Europe/London', 'UTC', 'America/New_York', 'America/Chicago'), group='Trade Session'),
    label__ren__=input.string(title='Label', defval='CME Open', tooltip='For easy identification', group='Trade Session'),
    startHour=input.int(title='analysis Start hour', defval=7, minval=0, maxval=23, group='Trade Session'),
    startMinute=input.int(title='analysis Start minute', defval=0, minval=0, maxval=59, group='Trade Session'),
    startHour2=input.int(title='Session Start hour', defval=8, minval=0, maxval=23, group='Trade Session'),
    startMinute2=input.int(title='Session Start minute', defval=30, minval=0, maxval=59, group='Trade Session'),
    endHour2=input.int(title='Session End hour', defval=12, minval=0, maxval=23, group='Trade Session'),
    endMinute2=input.int(title='Session End minute', defval=0, minval=0, maxval=59, group='Trade Session'),
    rangeColor=input.color(title='Color', defval=color.new('#1976D21F'), group='Trade Session'),
    showMon=input.bool(title='Monday', defval=True, group='Trade Session'),
    showTue=input.bool(title='Tuesday', defval=True, group='Trade Session'),
    showWed=input.bool(title='Wednesday', defval=True, group='Trade Session'),
    showThu=input.bool(title='Thursday', defval=True, group='Trade Session'),
    showFri=input.bool(title='Friday', defval=True, group='Trade Session'),
    showSat=input.bool(title='Saturday', defval=False, group='Trade Session'),
    showSun=input.bool(title='Sunday', defval=False, group='Trade Session')
):
    len1: int = 21
    src1 = close
    smma1: Series[float] = 0.0
    sma_1 = ta.sma(src1, len1)
    smma1 = sma_1 if na(smma1[1]) else (smma1[1] * (len1 - 1) + src1) / len1
    plot(smma1, color=color.new(color.white, 0), linewidth=2, title='21 SMMA')
    len2: int = 50
    src2 = close
    smma2: Series[float] = 0.0
    sma_2 = ta.sma(src2, len2)
    smma2 = sma_2 if na(smma2[1]) else (smma2[1] * (len2 - 1) + src2) / len2
    plot(smma2, color=color.new(color.new('#6AFF00'), 0), linewidth=2, title='50 SMMA')
    len3: int = 100
    src3 = close
    smma3: Series[float] = 0.0
    sma_3 = ta.sma(src3, len3)
    smma3 = sma_3 if na(smma3[1]) else (smma3[1] * (len3 - 1) + src3) / len3
    sma3plot = plot(smma3 if h100 else na, color=color.new(color.yellow, 0), linewidth=2, title='100 SMMA')
    len4: int = 200
    src4 = close
    smma4: Series[float] = 0.0
    sma_4 = ta.sma(src4, len4)
    smma4 = sma_4 if na(smma4[1]) else (smma4[1] * (len4 - 1) + src4) / len4
    sma4plot = plot(smma4, color=color.new(color.new('#FF0500'), 0), linewidth=2, title='200 SMMA')
    ema2 = ta.ema(close, 2)
    ema2plot = plot(ema2, color=color.new(color.new('#2ECC71'), 100), style=plot.style_line, linewidth=1, title='EMA(2)', editable=False)
    fill(ema2plot, sma4plot, color=color.new(color.green if ema2 > smma4 and trendFill else color.red if ema2 < smma4 and trendFill else na, 85), title='Trend Fill')
    bearSig = close[3] > open[3] and close[2] > open[2] and (close[1] > open[1]) and (close < open[1])
    bullSig = close[3] < open[3] and close[2] < open[2] and (close[1] < open[1]) and (close > open[1])
    plotshape((na if na(bullSig) else 1 if bullSig else 0) if bullS else na, style=shape.triangleup, color=color.new(color.green, 0), location=location.belowbar, size=size.small, text='3s-Bull', title='3 Line Strike Up')
    plotshape((na if na(bearSig) else 1 if bearSig else 0) if bearS else na, style=shape.triangledown, color=color.new(color.red, 0), location=location.abovebar, size=size.small, text='3s-Bear', title='3 Line Strike Down')
    openBarPrevious = open[1]
    closeBarPrevious = close[1]
    openBarCurrent = open
    closeBarCurrent = close
    bullishEngulfing = openBarCurrent <= closeBarPrevious and openBarCurrent < openBarPrevious and (closeBarCurrent > openBarPrevious)
    bearishEngulfing = openBarCurrent >= closeBarPrevious and openBarCurrent > openBarPrevious and (closeBarCurrent < openBarPrevious)
    plotshape((na if na(bullishEngulfing) else 1 if bullishEngulfing else 0) if bullE else na, style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), size=size.tiny, title='Big Ass Candle Up')
    plotshape((na if na(bearishEngulfing) else 1 if bearishEngulfing else 0) if bearE else na, style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), size=size.tiny, title='Big Ass Candle Down')
    alertcondition(bullishEngulfing, title='Bullish Engulfing', message='[CurrencyPair] [TimeFrame], Bullish candle engulfing previous candle')
    alertcondition(bearishEngulfing, title='Bearish Engulfing', message='[CurrencyPair] [TimeFrame], Bearish candle engulfing previous candle')
    tzYear = year(time, tz)
    tzMonth = month(time, tz)
    tzDay = dayofmonth(time, tz)
    tzDayOfWeek = dayofweek(time, tz)
    startTime = timestamp(tz, tzYear, tzMonth, tzDay, startHour, startMinute)
    endTime = timestamp(tz, tzYear, tzMonth, tzDay, endHour2, endMinute2)
    __block_result__ = na
    if startTime <= time and time <= endTime and ts:
        __block_result_1__ = na
        if tzDayOfWeek == dayofweek.monday and showMon:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.tuesday and showTue:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.wednesday and showWed:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.thursday and showThu:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.friday and showFri:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.saturday and showSat:
            __block_result_1__ = True
        elif tzDayOfWeek == dayofweek.sunday and showSun:
            __block_result_1__ = True
        else:
            __block_result_1__ = False
        __block_result__ = __block_result_1__
    else:
        __block_result__ = False
    active = __block_result__
    bgcolor(color=rangeColor if active else na, title='Session Background')
    startTime2 = timestamp(tz, tzYear, tzMonth, tzDay, startHour2, startMinute2)
    endTime2 = timestamp(tz, tzYear, tzMonth, tzDay, endHour2, endMinute2)
    __block_result_2__ = na
    if startTime2 <= time and time <= endTime2 and ts:
        __block_result_3__ = na
        if tzDayOfWeek == dayofweek.monday and showMon:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.tuesday and showTue:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.wednesday and showWed:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.thursday and showThu:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.friday and showFri:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.saturday and showSat:
            __block_result_3__ = True
        elif tzDayOfWeek == dayofweek.sunday and showSun:
            __block_result_3__ = True
        else:
            __block_result_3__ = False
        __block_result_2__ = __block_result_3__
    else:
        __block_result_2__ = False
    active2 = __block_result_2__
    bgcolor(color=rangeColor if active2 else na, title='Session Background')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
