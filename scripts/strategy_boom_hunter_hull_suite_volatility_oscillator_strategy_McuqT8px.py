"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, close, color, currency, high, input, label, low, math, na, nz,
    open, plot, request, script, strategy, string, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Boom Hunter + Hull Suite + Volatility Oscillator Strategy', overlay=False, initial_capital=1000, currency=currency.NONE, max_labels_count=500, default_qty_type=strategy.cash, commission_type=strategy.commission.percent, commission_value=0.01, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    swingLength=input.int(20, 'Swing High/Low Lookback Length', group='Strategy: Risk Management', tooltip='Stop Loss is calculated by the swing high or low over the previous X candles'),
    accountRiskPercent=input.float(3, 'Account percent loss per trade', step=0.1, group='Strategy: Risk Management', tooltip='Each trade will risk X% of the account balance'),
    profitFactor=input.float(3, 'Profit Factor (R:R Ratio)', step=0.1, group='Strategy: Risk Management'),
    start_year=input.int(title='Start Date', defval=2022, minval=2010, maxval=3000, group='Strategy: Date Range', inline='1'),
    start_month=input.int(title='', defval=1, group='Strategy: Date Range', inline='1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    start_date=input.int(title='', defval=1, group='Strategy: Date Range', inline='1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    end_year=input.int(title='End Date', defval=2030, minval=1800, maxval=3000, group='Strategy: Date Range', inline='2'),
    end_month=input.int(title='', defval=1, group='Strategy: Date Range', inline='2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    end_date=input.int(title='', defval=1, group='Strategy: Date Range', inline='2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    square=input.bool(True, title='Square Line?', group='Main Settings'),
    LPPeriod=input.int(6, title='Quotient | LPPeriod', inline='quotient', group='EOT 1 (Main Oscillator)'),
    K1=input.int(0, title='K1', inline='quotient', group='EOT 1 (Main Oscillator)'),
    trigno=input.int(1, 'Trigger Length', group='EOT 1 (Main Oscillator)', inline='quotient2'),
    trigcol=input.color(color.white, title='Trigger Color:', group='EOT 1 (Main Oscillator)', inline='q2'),
    LPPeriod2=input.int(28, title='LPPeriod2', group='EOT 2 (Red Wave)', inline='q2'),
    K22=input.float(0.3, title='K2', group='EOT 2 (Red Wave)', inline='q2'),
    src: Series[float] = input(close, title='Source'),
    modeSwitch=input.string('Hma', title='Hull Variation', options=('Hma', 'Thma', 'Ehma')),
    length=input(200, title='Length(180-200 for floating S/R , 55 for swing entry)'),
    lengthMult=input(2.4, title='Length multiplier (Used to view higher timeframes with straight band)'),
    useHtf=input(False, title='Show Hull MA from X timeframe? (good for scalping)'),
    htf=input.timeframe('240', title='Higher timeframe'),
    volLength=input(80)
):
    in_date_range = time >= timestamp(syminfo.timezone, start_year, start_month, start_date, 0, 0) and time < timestamp(syminfo.timezone, end_year, end_month, end_date, 0, 0)
    esize: int = 60
    ey: int = 50
    alpha1: float = 0.0
    HP: Series[float] = 0.0
    a1: float = 0.0
    b1: float = 0.0
    c1: float = 0.0
    c2: float = 0.0
    c3: float = 0.0
    Filt: Series[float] = 0.0
    Peak: Series[float] = 0.0
    X: float = 0.0
    Quotient1: float = 0.0
    pi = 2 * math.asin(1)
    alpha1 = (math.cos(0.707 * 2 * pi / 100) + math.sin(0.707 * 2 * pi / 100) - 1) / math.cos(0.707 * 2 * pi / 100)
    HP = (1 - alpha1 / 2) * (1 - alpha1 / 2) * (close - 2 * nz(close[1]) + nz(close[2])) + 2 * (1 - alpha1) * nz(HP[1]) - (1 - alpha1) * (1 - alpha1) * nz(HP[2])
    a1 = math.exp(-1.414 * pi / LPPeriod)
    b1 = 2 * a1 * math.cos(1.414 * pi / LPPeriod)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    Filt = c1 * (HP + nz(HP[1])) / 2 + c2 * nz(Filt[1]) + c3 * nz(Filt[2])
    Peak = 0.991 * nz(Peak[1])
    if math.abs(Filt) > Peak:
        Peak = math.abs(Filt)
    if Peak != 0:
        X = Filt / Peak
    Quotient1 = (X + K1) / (K1 * X + 1)
    alpha1222: float = 0.0
    HP2: Series[float] = 0.0
    a12: float = 0.0
    b12: float = 0.0
    c12: float = 0.0
    c22: float = 0.0
    c32: float = 0.0
    Filt2: Series[float] = 0.0
    Peak2: Series[float] = 0.0
    X2: float = 0.0
    Quotient4: float = 0.0
    alpha1222 = (math.cos(0.707 * 2 * pi / 100) + math.sin(0.707 * 2 * pi / 100) - 1) / math.cos(0.707 * 2 * pi / 100)
    HP2 = (1 - alpha1222 / 2) * (1 - alpha1222 / 2) * (close - 2 * nz(close[1]) + nz(close[2])) + 2 * (1 - alpha1222) * nz(HP2[1]) - (1 - alpha1222) * (1 - alpha1222) * nz(HP2[2])
    a12 = math.exp(-1.414 * pi / LPPeriod2)
    b12 = 2 * a12 * math.cos(1.414 * pi / LPPeriod2)
    c22 = b12
    c32 = -a12 * a12
    c12 = 1 - c22 - c32
    Filt2 = c12 * (HP2 + nz(HP2[1])) / 2 + c22 * nz(Filt2[1]) + c32 * nz(Filt2[2])
    Peak2 = 0.991 * nz(Peak2[1])
    if math.abs(Filt2) > Peak2:
        Peak2 = math.abs(Filt2)
    if Peak2 != 0:
        X2 = Filt2 / Peak2
    Quotient4 = (X2 + K22) / (K22 * X2 + 1)
    q4 = Quotient4 * esize + ey
    q1 = Quotient1 * esize + ey
    trigger = ta.sma(q1, trigno)
    Plot3 = plot(trigger, color=trigcol, linewidth=2, title='Quotient 1')
    Plot44 = plot(q4, color=color.new(color.red, 0), linewidth=2, title='Quotient 2')
    def HMA(_src, _length):
        return ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))

    def EHMA(_src, _length):
        return ta.ema(2 * ta.ema(_src, _length / 2) - ta.ema(_src, _length), math.round(math.sqrt(_length)))

    def THMA(_src, _length):
        return ta.wma(ta.wma(_src, _length / 3) * 3 - ta.wma(_src, _length / 2) - ta.wma(_src, _length), _length)

    def Mode(modeSwitch, src, len):
        return HMA(src, len) if modeSwitch == 'Hma' else EHMA(src, len) if modeSwitch == 'Ehma' else THMA(src, len / 2) if modeSwitch == 'Thma' else na

    _hull = Mode(modeSwitch, src, cast_int(length * lengthMult))
    HULL: Series = request.security(syminfo.ticker, htf, _hull) if useHtf else _hull
    MHULL = HULL
    SHULL = HULL[2]
    hullColor = color.green if MHULL > SHULL else color.red
    Fi1 = plot(-10, title='MHULL', color=hullColor, linewidth=2)
    spike = close - open
    x = ta.stdev(spike, volLength)
    y = ta.stdev(spike, volLength) * -1
    volOscCol = color.green if spike > x else color.red if spike < y else color.gray
    plot(-30, color=color.new(volOscCol, transp=0), linewidth=2)
    boomLong = ta.crossover(trigger, q4)
    boomShort = ta.crossunder(trigger, q4)
    hullLong = MHULL > SHULL and close > MHULL
    hullShort = MHULL < SHULL and close < SHULL
    volLong = spike > x
    volShort = spike < y
    inLong = strategy.position_size > 0
    inShort = strategy.position_size < 0
    longCondition = boomLong and hullLong and volLong and in_date_range
    shortCondition = boomShort and hullShort and volShort and in_date_range
    swingLow = ta.lowest(source=low, length=swingLength)
    swingHigh = ta.highest(source=high, length=swingLength)
    atr = ta.atr(14)
    longSl = math.min(close - atr, swingLow)
    shortSl = math.max(close + atr, swingHigh)
    longStopPercent = math.abs((1 - longSl / close) * 100)
    shortStopPercent = math.abs((1 - shortSl / close) * 100)
    longTpPercent = longStopPercent * profitFactor
    shortTpPercent = shortStopPercent * profitFactor
    longTp = close + close * (longTpPercent / 100)
    shortTp = close - close * (shortTpPercent / 100)
    riskAmt = strategy.equity * accountRiskPercent / 100
    longQty = math.abs(riskAmt / longStopPercent * 100) / close
    shortQty = math.abs(riskAmt / shortStopPercent * 100) / close
    if longCondition and (not inLong):
        strategy.entry('Long', strategy.long, qty=longQty)
        strategy.exit('Long  SL/TP', from_entry='Long', stop=longSl, limit=longTp, alert_message='Long SL Hit')
        buyLabel = label.new(x=bar_index, y=high[1], color=color.green, style=label.style_label_up)
        label.set_y(id=buyLabel, y=-40)
        label.set_tooltip(id=buyLabel, tooltip='Risk Amt: ' + string.tostring(riskAmt) + ' Qty: ' + string.tostring(longQty) + ' Swing low: ' + string.tostring(swingLow) + ' Stop Percent: ' + string.tostring(longStopPercent) + ' TP Percent: ' + string.tostring(longTpPercent))
    if shortCondition and (not inShort):
        strategy.entry('Short', strategy.short, qty=shortQty)
        strategy.exit('Short  SL/TP', from_entry='Short', stop=shortSl, limit=shortTp, alert_message='Short SL Hit')
        sellLabel = label.new(x=bar_index, y=high[1], color=color.red, style=label.style_label_up)
        label.set_y(id=sellLabel, y=-40)
        label.set_tooltip(id=sellLabel, tooltip='Risk Amt: ' + string.tostring(riskAmt) + ' Qty: ' + string.tostring(shortQty) + ' Swing high: ' + string.tostring(swingHigh) + ' Stop Percent: ' + string.tostring(shortStopPercent) + ' TP Percent: ' + string.tostring(shortTpPercent))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
