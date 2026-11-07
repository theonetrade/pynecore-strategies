"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, close, color, display, high, input, label, low, math, na, plot,
    request, script, strategy, string, syminfo, ta, text, time, timenow, timestamp, xloc, yloc
)
from pynecore.types import Color, Label, Persistent, Series


@script.strategy(title='Advanced VWAP-Momentum_Pullback Strategy_Trend-Template Qualifier', initial_capital=100000, pyramiding=0, default_qty_value=100, currency='USD', overlay=True, default_qty_type=strategy.percent_of_equity, margin_long=0, margin_short=0, close_by_id=True)
def main(
    cb1=input.bool(title='1. Stock price is above MA 150 and 200 ?', defval=False),
    cb2=input.bool(title='2. MA 150 is above MA 200 ?', defval=False),
    cb3=input.bool(title='3. MA 200 is trending at least 1 month(22 days) ?', defval=False),
    cb4=input.bool(title='4. MA 50 is above both MA 150 and MA 200 ?', defval=False),
    cb5=input.bool(title='5. The current stock price is trading above MA 50? ', defval=False),
    cb6=input.bool(title='6. Current stock price is 25% above 52 weeks low ?', defval=False),
    cb7=input.bool(title='7. Current Price is within 25% of 52 week high ? ', defval=False),
    cb8=input.bool(title='8. Meet Minervini\'s Criteria?', defval=False),
    cb9=input.bool(title='9. Enable IBD Qualifier?', defval=False),
    ibd_threshhold=input.float(title='IBD RS Threshhold 3Months', defval=0.5, step=0.1),
    start_date=input.int(title='Start Date', defval=1, minval=1, maxval=31, group='Date Range', inline='1'),
    end_date=input.int(title='End Date', defval=1, minval=1, maxval=31, group='Date Range', inline='1'),
    start_month=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Date Range', inline='2'),
    end_month=input.int(title='End Month', defval=1, minval=1, maxval=12, group='Date Range', inline='2'),
    start_year=input.int(title='Start Year', defval=2000, minval=1800, maxval=3000, group='Date Range', inline='3'),
    end_year=input.int(title='End Year', defval=2077, minval=1800, maxval=3000, group='Date Range', inline='3'),
    rsi_over_sold=input.int(defval=30, minval=1, title='Over Sold Level', group='RSI'),
    rsi_over_bought=input.int(defval=70, minval=1, title='Over Bought Level', group='RSI'),
    rsi_length=input.int(defval=14, minval=1, title='RSI Length', group='RSI'),
    maSource: Series[float] = input(title='SMA source', defval=close, group='VWAP'),
    maInterval=input.int(title='SMA interval', minval=0, maxval=999, step=1, defval=7, group='VWAP'),
    high_loopback=input(260, 'High Lookback Length'),
    low_loopback=input(260, 'Low Lookback Length'),
    show_52_week_high_low=input(title='Show 52 week highest/lowest', defval=True),
    bars_right=input(5, 'x bars right'),
    position__ren__: Series[float] = input(close, 'Label position'),
    one_color=input(False, 'Label only in one color'),
    lab_color=input(color.new('#FFD700'), 'Label color'),
    fastExit=input(False, title='Close Trade when opposite trading signal is triggered'),
    clrBars=input(False, title='Mark candles according to order status'),
    orderType=input.string('Only Long', title='Long/Short Strategy', options=('Long & Short', 'Only Long', 'Only Short', 'Flip')),
    isS=input(False, 'Stop Loss Enable'),
    __input_32__=input.float(defval=5, title='Stop Loss (%)', minval=0, step=0.1),
    isTS=input(False, 'Trailing Stop Loss Enable'),
    __input_34__=input.float(title='Trailing Stop Loss (%)', minval=0.0, step=0.1, defval=2),
    isTP=input(False, 'Take Profit Enable'),
    __input_36__=input.float(defval=5, title='Take Profit %', minval=0, step=0.1)
):
    src: Series = request.security(syminfo.ticker, 'D', close)
    mo_3 = 0.4 * (src / src[11]) + 0.2 * (src / src[21]) + 0.2 * (src / src[42]) + 0.2 * (src / src[63])
    plot(100 * mo_3, style=plot.style_line, linewidth=1, color=color.new(color.new('#1E90FF'), 0), display=display.none)
    in_date_range = time >= timestamp(syminfo.timezone, start_year, start_month, start_date, 0, 0) and time < timestamp(syminfo.timezone, end_year, end_month, end_date, 0, 0)
    rsi = ta.rsi(close, rsi_length)
    ma = ta.sma(maSource, maInterval)
    was_over_sold = ta.barssince(rsi <= rsi_over_sold) <= 10
    was_over_bought = ta.barssince(rsi >= rsi_over_bought) <= 10
    crossover_bull = ta.crossover(ma, ta.vwap)
    crossover_bear = ta.crossunder(ma, ta.vwap)
    sma50 = ta.sma(close, 50)
    sma150 = ta.sma(close, 150)
    sma200: Series = ta.sma(close, 200)
    sma200_22 = sma200[22]
    is_price_above_sma_150_and_200 = True if close > sma150 and close > sma200 else False
    c_1 = True if is_price_above_sma_150_and_200 else False
    is_sma_150_above_sma_200 = True if sma150 > sma200 else False
    c_2 = True if is_sma_150_above_sma_200 else False
    is_trending_at_least_1_month = True if sma200 > sma200_22 else False
    c_3 = True if is_trending_at_least_1_month else False
    is_sma_50_above_sma_150_and_200 = True if sma50 > sma150 and sma50 > sma200 else False
    c_4 = True if is_sma_50_above_sma_150_and_200 else False
    is_current_price_above_ma_50 = True if close > sma50 else False
    c_5 = True if is_current_price_above_ma_50 else False
    highest_price = ta.highest(high, high_loopback)
    lowest_price = ta.lowest(low, low_loopback)
    is_price_25_percent_above_52_weeks_low = True if (close / lowest_price - 1) * 100 >= 25 else False
    c_6 = True if is_price_25_percent_above_52_weeks_low else False
    plot(highest_price if show_52_week_high_low else na, title='52 Week High', trackprice=True, color=color.new(color.orange, 0), offset=-9999)
    plot(lowest_price if show_52_week_high_low else na, title='52 Week Low', trackprice=True, color=color.new(color.orange, 0), offset=-9999)
    is_price_within_52_high = True if (1 - close / highest_price) * 100 <= 25 else False
    c_7 = True if is_price_within_52_high else False
    three_month_rs = 0.4 * (close / close[13])
    six_month_rs = 0.2 * (close / (close[26] * 2))
    nine_month_rs = 0.2 * (close / (close[39] * 3))
    twelve_month_rs = 0.2 * (close / (close[52] * 4))
    rs_rating = (three_month_rs + six_month_rs + nine_month_rs + twelve_month_rs) * 100
    rs_rating_str = string.tostring(rs_rating, '#.00')
    is_rs_rating_more_than_seventy = rs_rating > 70
    is_meet_all_criteria = is_price_above_sma_150_and_200 and is_sma_150_above_sma_200 and is_trending_at_least_1_month and is_sma_50_above_sma_150_and_200 and is_price_25_percent_above_52_weeks_low and is_price_within_52_high and is_current_price_above_ma_50 and (mo_3 >= ibd_threshhold)
    allConditionTrue: bool = True
    if cb1 == True:
        if allConditionTrue == True and is_price_above_sma_150_and_200 == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb2 == True:
        if allConditionTrue == True and is_sma_150_above_sma_200 == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb3 == True:
        if allConditionTrue == True and is_trending_at_least_1_month == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb4 == True:
        if allConditionTrue == True and is_sma_50_above_sma_150_and_200 == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb5 == True:
        if allConditionTrue == True and is_current_price_above_ma_50 == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb6 == True:
        if allConditionTrue == True and is_price_25_percent_above_52_weeks_low == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb7 == True:
        if allConditionTrue == True and is_price_within_52_high == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb8 == True:
        if allConditionTrue == True and is_meet_all_criteria == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    if cb9 == True:
        if allConditionTrue == True and (mo_3 >= ibd_threshhold) == True:
            allConditionTrue = True
        else:
            allConditionTrue = False
    label1 = '1. Stock price is above MA 150 and 200 ? ' + ('yes' if is_price_above_sma_150_and_200 else 'no') + '\n' if cb1 == True else na
    label2 = '2. MA 150 is above MA 200 ? ' + ('yes' if is_sma_150_above_sma_200 else 'no') + '\n' if cb2 == True else na
    label3 = '3. MA 200 is trending at least 1 month(22 days) ? ' + ('yes' if is_trending_at_least_1_month else 'no') + '\n' if cb3 == True else na
    label4 = '4. MA 50 is above both MA 150 and MA 200 ? ' + ('yes' if is_sma_50_above_sma_150_and_200 else 'no') + '\n' if cb4 == True else na
    label5 = '5. The current stock price is trading above MA 50? ' + ('yes' if is_current_price_above_ma_50 else 'no') + '\n' if cb5 == True else na
    label6 = '6. Current stock price is 25% above 52 weeks low ? ' + ('yes' if is_price_25_percent_above_52_weeks_low else 'no') + '\n' if cb6 == True else na
    label7 = '7. Current Price is within 25% of 52 week high ? ' + ('yes' if is_price_within_52_high else 'no') + '\n' if cb7 == True else na
    label8 = '8. Meet Minervini Criteria? ' + ('yes' if is_meet_all_criteria else 'no') + '\n' if cb8 == True else na
    label9 = '9.IBD Qualifier? Enabled' + ' ' + ('IBD Mathed' if mo_3 >= ibd_threshhold else 'IBD not matched') + ' ' + string.tostring(mo_3) if cb9 == True else na
    text_: str = ''
    text_ = text_ + 'Minervinis Strategy' + '\n'
    text_ = text_ + '˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭' + '\n'
    text_ = text_ + 'Selected qualifiers are as below:' + '\n' + '\n'
    text_ = text_ + label1
    text_ = text_ + label2
    text_ = text_ + label3
    text_ = text_ + label4
    text_ = text_ + label5
    text_ = text_ + label6
    text_ = text_ + label7
    text_ = text_ + label8
    text_ = text_ + label9
    t = timenow + math.round(ta.change(time) * bars_right)
    lab: Persistent[Label] = na(Label)
    label.delete(lab)
    lab = label.new(t, position__ren__, text=text_, style=label.style_label_left, yloc=yloc.price, xloc=xloc.bar_time, textalign=text.align_left, color=color.new('#FFD700'), textcolor=color.black)
    buy_signal = was_over_bought and crossover_bear if orderType == 'Flip' else was_over_sold and crossover_bull
    sell_signal = was_over_sold and crossover_bull if orderType == 'Flip' else was_over_bought and crossover_bear
    AQUA: Color = color.new('#00FFFF')
    BLUE: Color = color.new('#0000FF')
    RED: Color = color.new('#FF0000')
    LIME: Color = color.new('#00FF00')
    GRAY: Color = color.new('#808080')
    DARKRED: Color = color.new('#8B0000')
    DARKGREEN: Color = color.new('#006400')
    bclr = na if not clrBars else GRAY if strategy.position_size == 0 else DARKGREEN if cast_bool(ta.change(strategy.position_size)) and strategy.position_size > 0 else LIME if strategy.position_size > 0 else DARKRED if cast_bool(ta.change(strategy.position_size)) and strategy.position_size < 0 else RED if strategy.position_size < 0 else GRAY
    barcolor(bclr, title='Trade State Bar Colouring')
    slv = __input_32__ / 100
    trailPerc = __input_34__ * 0.01
    tpv = __input_36__ / 100
    long_stoploss_price = strategy.position_avg_price * (1 - slv)
    long_takeprofit_price = strategy.position_avg_price * (1 + tpv)
    short_stoploss_price = strategy.position_avg_price * (1 + slv)
    short_takeprofit_price = strategy.position_avg_price * (1 - tpv)
    if strategy.equity > 0 and (strategy.position_size == 0 if fastExit == False else True) and buy_signal and in_date_range and (allConditionTrue == True) and (orderType == 'Only Long' or orderType == 'Long & Short' or orderType == 'Flip'):
        strategy.entry('Long', strategy.long, alert_message='Open Long Position')
    longStopPrice: Series[float] = 0.0
    __block_result__ = na
    if strategy.position_size > 0:
        stopValue = high * (1 - trailPerc)
        __block_result__ = math.max(stopValue, longStopPrice[1])
    else:
        __block_result__ = 0
    longStopPrice = __block_result__
    if strategy.position_size > 0:
        strategy.exit('LEx', 'Long', limit=long_takeprofit_price if isTP else na, stop=longStopPrice if isTS else long_stoploss_price if isS else na, alert_message='Close Long Position')
    if strategy.equity > 0 and (strategy.position_size == 0 if fastExit == False else True) and sell_signal and in_date_range and (orderType == 'Short' or orderType == 'Long & Short' or orderType == 'Flip'):
        strategy.entry('Short', strategy.short, alert_message='Open Short Position')
    shortStopPrice: Series[float] = 0.0
    __block_result_1__ = na
    if strategy.position_size < 0:
        stopValue = low * (1 + trailPerc)
        __block_result_1__ = math.min(stopValue, shortStopPrice[1])
    else:
        __block_result_1__ = 9999
    shortStopPrice = __block_result_1__
    if strategy.position_size < 0:
        strategy.exit('SEx', 'Short', limit=short_takeprofit_price if isTP else na, stop=shortStopPrice if isTS else short_stoploss_price if isS else na, alert_message='Your Short SL/TP Limit As Been Triggered.')
    plot(longStopPrice if strategy.position_size > 0 and isTS == True else na, 'Long Trailing SL', color=color.red, style=plot.style_linebr)
    plot(shortStopPrice if strategy.position_size < 0 and isTS == True else na, 'Short Trailing SL', color=color.red, style=plot.style_linebr)
    plot(long_stoploss_price if strategy.position_size > 0 and isTS == False else na, 'Long SL', color=color.red, style=plot.style_linebr)
    plot(short_stoploss_price if strategy.position_size < 0 and isTS == False else na, 'Short SL', color=color.red, style=plot.style_linebr)
    plot(long_takeprofit_price if strategy.position_size > 0 else na, 'Long TP', color=color.green, style=plot.style_linebr)
    plot(short_takeprofit_price if strategy.position_size < 0 else na, 'Short TP', color=color.green, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)