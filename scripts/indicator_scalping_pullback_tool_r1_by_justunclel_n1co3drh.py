"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, bgcolor, close, color, fill, high, input,
    location, low, na, nz, open, plot, plotarrow, plotshape, request, script, shape, syminfo, ta,
    ticker, timeframe
)
from pynecore.types import Series


@script.indicator(title='Scalping PullBack Tool R1.1 by JustUncleL', shorttitle='SCALPTOOL R1.1', overlay=True, na_bool=True)
def main(
    HiLoLen=input.int(34, minval=2, title='High Low PAC channel Length'),
    fastEMAlength=input.int(89, minval=2),
    mediumEMAlength=input.int(200, minval=2),
    slowEMAlength=input.int(600, minval=2),
    ShowFastEMA=input(True),
    ShowMediumEMA=input(True),
    ShowSlowEMA=input(False),
    ShowHHLL=input(False),
    ShowFractals=input(True),
    filterBW=input(False, title='Show Ideal Fractals Only'),
    ShowBarColor=input(True, title='Show coloured Bars around PAC'),
    ShowBuySell=input(True, title='Show Buy/Sell Alert Arrows'),
    Lookback=input.int(3, minval=1, title='Pullback Lookback for PAC Cross Check'),
    DelayArrow=input(False, title='Show Alert Arrows Only on Closed Candles'),
    ShowTrendBGcolor=input(True),
    UseHAcandles=input(True, title='Use Heikin Ashi Candles in Algo Calculations')
):
    Delay = 1 if DelayArrow else 0
    haClose = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close) if UseHAcandles else close
    haOpen = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open) if UseHAcandles else open
    haHigh = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high) if UseHAcandles else high
    haLow = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low) if UseHAcandles else low
    def isRegularFractal(mode):
        ret = high[4] < high[3] and high[3] < high[2] and (high[2] > high[1]) and (high[1] > high) if mode == 1 else low[4] > low[3] and low[3] > low[2] and (low[2] < low[1]) and (low[1] < low) if mode == -1 else False
        return ret

    def isBWFractal(mode):
        ret = high[4] < high[2] and high[3] <= high[2] and (high[2] >= high[1]) and (high[2] > high) if mode == 1 else low[4] > low[2] and low[3] >= low[2] and (low[2] <= low[1]) and (low[2] < low) if mode == -1 else False
        return ret

    fastEMA = ta.ema(haClose, fastEMAlength)
    mediumEMA = ta.ema(haClose, mediumEMAlength)
    slowEMA = ta.ema(haClose, slowEMAlength)
    pacC = ta.ema(haClose, HiLoLen)
    pacL = ta.ema(haLow, HiLoLen)
    pacU = ta.ema(haHigh, HiLoLen)
    TrendDirection = 1 if fastEMA > mediumEMA and pacL > mediumEMA else -1 if fastEMA < mediumEMA and pacU < mediumEMA else 0
    filteredtopf = isRegularFractal(1) if filterBW else isBWFractal(1)
    filteredbotf = isRegularFractal(-1) if filterBW else isBWFractal(-1)
    valuewhen_H0 = ta.valuewhen(filteredtopf == True, high[2], 0)
    valuewhen_H1 = ta.valuewhen(filteredtopf == True, high[2], 1)
    valuewhen_H2 = ta.valuewhen(filteredtopf == True, high[2], 2)
    higherhigh = False if filteredtopf == False else valuewhen_H1 < valuewhen_H0 and valuewhen_H2 < valuewhen_H0
    lowerhigh = False if filteredtopf == False else valuewhen_H1 > valuewhen_H0 and valuewhen_H2 > valuewhen_H0
    valuewhen_L0 = ta.valuewhen(filteredbotf == True, low[2], 0)
    valuewhen_L1 = ta.valuewhen(filteredbotf == True, low[2], 1)
    valuewhen_L2 = ta.valuewhen(filteredbotf == True, low[2], 2)
    higherlow = False if filteredbotf == False else valuewhen_L1 < valuewhen_L0 and valuewhen_L2 < valuewhen_L0
    lowerlow = False if filteredbotf == False else valuewhen_L1 > valuewhen_L0 and valuewhen_L2 > valuewhen_L0
    L = plot(pacL, color=color.new(color.gray, 50), linewidth=1, title='High PAC EMA')
    U = plot(pacU, color=color.new(color.gray, 50), linewidth=1, title='Low PAC EMA')
    C = plot(pacC, color=color.new(color.red, 0), linewidth=2, title='Close PAC EMA')
    fill(L, U, color=color.new(color.gray, 90), title='Fill HiLo PAC')
    BARcolor = color.blue if haClose > pacU else color.red if haClose < pacL else color.gray
    barcolor(BARcolor if ShowBarColor else na, title='Bar Colours')
    BGcolor = color.green if TrendDirection == 1 else color.red if TrendDirection == -1 else color.yellow
    bgcolor(BGcolor if ShowTrendBGcolor else na, title='Trend BG Color')
    plot(fastEMA if ShowFastEMA else na, color=color.new(color.green, 20), linewidth=2, title='fastEMA')
    plot(mediumEMA if ShowMediumEMA else na, color=color.new(color.blue, 20), linewidth=3, title='mediumEMA')
    plot(slowEMA if ShowSlowEMA else na, color=color.new(color.black, 20), linewidth=4, title='slowEMA')
    plotshape(filteredtopf if ShowFractals else na, title='Filtered Top Fractals', style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), offset=-2)
    plotshape(filteredbotf if ShowFractals else na, title='Filtered Bottom Fractals', style=shape.triangleup, location=location.belowbar, color=color.new(color.lime, 0), offset=-2)
    plotshape(higherhigh if ShowHHLL else na, title='Higher High', style=shape.square, location=location.abovebar, color=color.new(color.maroon, 0), text='[HH]', offset=-2)
    plotshape(lowerhigh if ShowHHLL else na, title='Lower High', style=shape.square, location=location.abovebar, color=color.new(color.maroon, 0), text='[LH]', offset=-2)
    plotshape(higherlow if ShowHHLL else na, title='High Low', style=shape.square, location=location.belowbar, color=color.new(color.green, 0), text='[HL]', offset=-2)
    plotshape(lowerlow if ShowHHLL else na, title='Lower Low', style=shape.square, location=location.belowbar, color=color.new(color.green, 0), text='[LL]', offset=-2)
    TradeDirection: Series[int] = 0
    TradeDirection = nz(TradeDirection[1])
    barssince_1 = ta.barssince(haClose < pacC)
    pacExitU = haOpen < pacU and haClose > pacU and (barssince_1 <= Lookback)
    barssince_2 = ta.barssince(haClose > pacC)
    pacExitL = haOpen > pacL and haClose < pacL and (barssince_2 <= Lookback)
    plotshape(ta.barssince(haClose < pacC), color=na, location=location.bottom, title='barssince(haClose<pacC)')
    plotshape(ta.barssince(close > pacC), color=na, location=location.bottom, title='barssince(haClose>pacC)')
    Buy = TrendDirection == 1 and pacExitU
    Sell = TrendDirection == -1 and pacExitL
    TradeDirection = 0 if TradeDirection == 1 and haClose < pacC else 0 if TradeDirection == -1 and haClose > pacC else 1 if TradeDirection == 0 and Buy else -1 if TradeDirection == 0 and Sell else TradeDirection
    plotarrow(TradeDirection[Delay] if ShowBuySell and nz(TradeDirection[1 + Delay]) == 0 and (TradeDirection[Delay] != 0) else na, offset=-Delay, colorup=color.new(color.green, 20), colordown=color.new(color.maroon, 20), minheight=20, maxheight=50, title='Buy/Sell Arrow')
    Long = nz(TradeDirection[1]) == 0 and TradeDirection == 1
    Short = nz(TradeDirection[1]) == 0 and TradeDirection == -1
    alertcondition(Long, title='Buy Condition', message='BUY')
    alertcondition(Short, title='Sell Condition', message='SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
