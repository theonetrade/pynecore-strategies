"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.lib import (
    alert, barstate, close, color, currency, format, input, na, nz, plot,
    position, script, strategy, string, ta, table, text
)

bright = position.bottom_right
bleft = position.bottom_left
bcenter = position.bottom_center
tright = position.top_right
tleft = position.top_left
tcenter = position.top_center
mright = position.middle_right
mleft = position.middle_left
mcenter = position.middle_center


@script.strategy('3Commas Bot DCA Backtester & Signals FREE', shorttitle='3Commas Bot DCA Backtester & Signals FREE', overlay=True, precision=2, pyramiding=51, calc_on_every_tick=True, backtest_fill_limits_assumption=1, default_qty_type=strategy.fixed, currency=currency.USD, slippage=1, commission_type=strategy.commission.percent, commission_value=0.05, process_orders_on_close=True, initial_capital=26000, margin_long=100, margin_short=100, default_qty_value=1, close_by_id=True)
def main(
    strategy__ren__=input.string('MACD', title='Buy Signal Strategy', options=('MFI', 'RSI', 'MACD', 'Stochastic RSI'), tooltip='This is your buy signal strategy. MACD triggers a buy signal when the MACD signal line crosses above the MACD line. MFI triggers a buy signal when MFI is below your threshold level in the next setting. RSI triggers a buy signal when RSI is below your threshold level in the next setting. Stochastic RSI triggers a buy signal when the K line crosses above the D line.', group='Strategy'),
    strategyLevelTrigger=input.int(20, title='Signal Threshold Level', tooltip='This number is the threshold that MFI or RSI will need to be below to trigger a buy signal. So if you set it to 20, the MFI or RSI that you chose above will trigger a buy signal when it goes below this number. This setting has no affect on the MACD or Stochastic RSI even when a value is set.', group='Strategy'),
    strategyLength=input.int(14, title='Indicator Length', tooltip='This is the length used for RSI and MFI. MACD uses the standard 12, 26, 9 lengths and Stochastic RSI uses 3, 3, 14, 14 lengths. MACD and Stochastic RSI will not be affected by this input number.'),
    stoplossOn=input.bool(False, title='Stoploss On', group='DCA Bot Settings'),
    __input_4__=input.float(5, title='Stoploss %', minval=0.0001, step=0.001, group='DCA Bot Settings'),
    __input_5__=input.float(0.5, title='Take Profit %', minval=0.0001, step=0.001, group='DCA Bot Settings'),
    __input_6__=input.float(0.5, title='Average Down %', minval=0.0001, step=0.001, group='DCA Bot Settings'),
    percentScale=input.float(1.2, title='Avg Down % Multiplier', minval=0.0001, step=0.001, group='DCA Bot Settings'),
    multiplier=input.float(1.5, title='Volume Multiplier', minval=1, step=0.001, tooltip='Increasing this value above 1 will multiply each new orders volume by the amount you input. This makes your buys bigger every time you average down so you don\'t need as big of a bounce when it recovers to get out in profit.', group='DCA Bot Settings'),
    maxOrders=input.int(12, title='Max # Of Orders', group='DCA Bot Settings'),
    quantity=input.float(100, title='Size Of Base Order', minval=1e-09, step=1e-09, group='DCA Bot Settings'),
    dataTableOn=input.bool(True, title='Info Table On/Off', group='Info Tables'),
    orderLevelsOn=input.bool(True, title='Turn Average Down Levels On/Off', group='Average Down Levels'),
    tablePosition=input.string(bright, title='Percentage Table Position', options=(bright, bleft, bcenter, tright, tleft, tcenter, mright, mleft, mcenter), group='Info Tables')
):
    stoploss = __input_4__ / 100
    takeProfit = __input_5__ / 100
    avgDown = __input_6__ / 100
    buy: bool = False
    fastMa = ta.sma(close, 12)
    slowMa = ta.sma(close, 26)
    macd = fastMa - slowMa
    signal = ta.sma(macd, 9)
    crossover_1 = ta.crossover(macd, signal)
    if strategy__ren__ == 'MACD' and crossover_1:
        buy = True
    mfi = ta.mfi(close, strategyLength)
    if strategy__ren__ == 'MFI' and mfi <= strategyLevelTrigger:
        buy = True
    rsi = ta.rsi(close, strategyLength)
    if strategy__ren__ == 'RSI' and rsi <= strategyLevelTrigger:
        buy = True
    smoothK: int = 3
    smoothD: int = 3
    lengthRSI: int = 14
    lengthStoch: int = 14
    rsi1 = ta.rsi(close, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    crossover_2 = ta.crossover(k, d)
    if strategy__ren__ == 'Stochastic RSI' and crossover_2:
        buy = True
    if buy:
        alert('Place Open Deal Code From 3Commas Here.', alert.freq_once_per_bar_close)
    quantityConverted = quantity / close
    quantMultiplied1 = quantityConverted * multiplier
    quantMultiplied2 = quantMultiplied1 * multiplier
    quantMultiplied3 = quantMultiplied2 * multiplier
    quantMultiplied4 = quantMultiplied3 * multiplier
    quantMultiplied5 = quantMultiplied4 * multiplier
    quantMultiplied6 = quantMultiplied5 * multiplier
    quantMultiplied7 = quantMultiplied6 * multiplier
    quantMultiplied8 = quantMultiplied7 * multiplier
    quantMultiplied9 = quantMultiplied8 * multiplier
    quantMultiplied10 = quantMultiplied9 * multiplier
    quantMultiplied11 = quantMultiplied10 * multiplier
    quantMultiplied12 = quantMultiplied11 * multiplier
    quantMultiplied13 = quantMultiplied12 * multiplier
    quantMultiplied14 = quantMultiplied13 * multiplier
    quantMultiplied15 = quantMultiplied14 * multiplier
    quantMultiplied16 = quantMultiplied15 * multiplier
    quantMultiplied17 = quantMultiplied16 * multiplier
    quantMultiplied18 = quantMultiplied17 * multiplier
    quantMultiplied19 = quantMultiplied18 * multiplier
    quantMultiplied20 = quantMultiplied19 * multiplier
    quantMultiplied21 = quantMultiplied20 * multiplier
    quantMultiplied22 = quantMultiplied21 * multiplier
    quantMultiplied23 = quantMultiplied22 * multiplier
    quantMultiplied24 = quantMultiplied23 * multiplier
    quantMultiplied25 = quantMultiplied24 * multiplier
    quantMultiplied26 = quantMultiplied25 * multiplier
    quantMultiplied27 = quantMultiplied26 * multiplier
    quantMultiplied28 = quantMultiplied27 * multiplier
    quantMultiplied29 = quantMultiplied28 * multiplier
    quantMultiplied30 = quantMultiplied29 * multiplier
    quantMultiplied31 = quantMultiplied30 * multiplier
    quantMultiplied32 = quantMultiplied31 * multiplier
    quantMultiplied33 = quantMultiplied32 * multiplier
    quantMultiplied34 = quantMultiplied33 * multiplier
    quantMultiplied35 = quantMultiplied34 * multiplier
    quantMultiplied36 = quantMultiplied35 * multiplier
    quantMultiplied37 = quantMultiplied36 * multiplier
    quantMultiplied38 = quantMultiplied37 * multiplier
    quantMultiplied39 = quantMultiplied38 * multiplier
    quantMultiplied40 = quantMultiplied39 * multiplier
    quantMultiplied41 = quantMultiplied40 * multiplier
    quantMultiplied42 = quantMultiplied41 * multiplier
    quantMultiplied43 = quantMultiplied42 * multiplier
    quantMultiplied44 = quantMultiplied43 * multiplier
    quantMultiplied45 = quantMultiplied44 * multiplier
    quantMultiplied46 = quantMultiplied45 * multiplier
    quantMultiplied47 = quantMultiplied46 * multiplier
    quantMultiplied48 = quantMultiplied47 * multiplier
    quantMultiplied49 = quantMultiplied48 * multiplier
    quantMultiplied50 = quantMultiplied49 * multiplier
    avgDown1 = avgDown * percentScale + avgDown
    avgDown2 = avgDown1 * percentScale + avgDown
    avgDown3 = avgDown2 * percentScale + avgDown
    avgDown4 = avgDown3 * percentScale + avgDown
    avgDown5 = avgDown4 * percentScale + avgDown
    avgDown6 = avgDown5 * percentScale + avgDown
    avgDown7 = avgDown6 * percentScale + avgDown
    avgDown8 = avgDown7 * percentScale + avgDown
    avgDown9 = avgDown8 * percentScale + avgDown
    avgDown10 = avgDown9 * percentScale + avgDown
    avgDown11 = avgDown10 * percentScale + avgDown
    avgDown12 = avgDown11 * percentScale + avgDown
    avgDown13 = avgDown12 * percentScale + avgDown
    avgDown14 = avgDown13 * percentScale + avgDown
    avgDown15 = avgDown14 * percentScale + avgDown
    avgDown16 = avgDown15 * percentScale + avgDown
    avgDown17 = avgDown16 * percentScale + avgDown
    avgDown18 = avgDown17 * percentScale + avgDown
    avgDown19 = avgDown18 * percentScale + avgDown
    avgDown20 = avgDown19 * percentScale + avgDown
    avgDown21 = avgDown20 * percentScale + avgDown
    avgDown22 = avgDown21 * percentScale + avgDown
    avgDown23 = avgDown22 * percentScale + avgDown
    avgDown24 = avgDown23 * percentScale + avgDown
    avgDown25 = avgDown24 * percentScale + avgDown
    avgDown26 = avgDown25 * percentScale + avgDown
    avgDown27 = avgDown26 * percentScale + avgDown
    avgDown28 = avgDown27 * percentScale + avgDown
    avgDown29 = avgDown28 * percentScale + avgDown
    avgDown30 = avgDown29 * percentScale + avgDown
    avgDown31 = avgDown30 * percentScale + avgDown
    avgDown32 = avgDown31 * percentScale + avgDown
    avgDown33 = avgDown32 * percentScale + avgDown
    avgDown34 = avgDown33 * percentScale + avgDown
    avgDown35 = avgDown34 * percentScale + avgDown
    avgDown36 = avgDown35 * percentScale + avgDown
    avgDown37 = avgDown36 * percentScale + avgDown
    avgDown38 = avgDown37 * percentScale + avgDown
    avgDown39 = avgDown38 * percentScale + avgDown
    avgDown40 = avgDown39 * percentScale + avgDown
    avgDown41 = avgDown40 * percentScale + avgDown
    avgDown42 = avgDown41 * percentScale + avgDown
    avgDown43 = avgDown42 * percentScale + avgDown
    avgDown44 = avgDown43 * percentScale + avgDown
    avgDown45 = avgDown44 * percentScale + avgDown
    avgDown46 = avgDown45 * percentScale + avgDown
    avgDown47 = avgDown46 * percentScale + avgDown
    avgDown48 = avgDown47 * percentScale + avgDown
    avgDown49 = avgDown48 * percentScale + avgDown
    avgDown50 = avgDown49 * percentScale + avgDown
    if strategy.opentrades == 0 and buy and barstate.isconfirmed:
        strategy.entry('Bull #1', strategy.long, qty=quantityConverted, comment='Buy #1')
    plot(strategy.opentrades.entry_price(0), title='Order #1', color=color.white)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown) if maxOrders >= 2 and orderLevelsOn else na, title='Order #2', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown1) if maxOrders >= 3 and orderLevelsOn else na, title='Order #3', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown2) if maxOrders >= 4 and orderLevelsOn else na, title='Order #4', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown3) if maxOrders >= 5 and orderLevelsOn else na, title='Order #5', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown4) if maxOrders >= 6 and orderLevelsOn else na, title='Order #6', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown5) if maxOrders >= 7 and orderLevelsOn else na, title='Order #7', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown6) if maxOrders >= 8 and orderLevelsOn else na, title='Order #8', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown7) if maxOrders >= 9 and orderLevelsOn else na, title='Order #9', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown8) if maxOrders >= 10 and orderLevelsOn else na, title='Order #10', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown9) if maxOrders >= 11 and orderLevelsOn else na, title='Order #11', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown10) if maxOrders >= 12 and orderLevelsOn else na, title='Order #12', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown11) if maxOrders >= 13 and orderLevelsOn else na, title='Order #13', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown12) if maxOrders >= 14 and orderLevelsOn else na, title='Order #14', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown13) if maxOrders >= 15 and orderLevelsOn else na, title='Order #15', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown14) if maxOrders >= 16 and orderLevelsOn else na, title='Order #16', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown15) if maxOrders >= 17 and orderLevelsOn else na, title='Order #17', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown16) if maxOrders >= 18 and orderLevelsOn else na, title='Order #18', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown17) if maxOrders >= 19 and orderLevelsOn else na, title='Order #19', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown18) if maxOrders >= 20 and orderLevelsOn else na, title='Order #20', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown19) if maxOrders >= 21 and orderLevelsOn else na, title='Order #21', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown20) if maxOrders >= 22 and orderLevelsOn else na, title='Order #22', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown21) if maxOrders >= 23 and orderLevelsOn else na, title='Order #23', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown22) if maxOrders >= 24 and orderLevelsOn else na, title='Order #24', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown23) if maxOrders >= 25 and orderLevelsOn else na, title='Order #25', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown24) if maxOrders >= 26 and orderLevelsOn else na, title='Order #26', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown25) if maxOrders >= 27 and orderLevelsOn else na, title='Order #27', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown26) if maxOrders >= 28 and orderLevelsOn else na, title='Order #28', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown27) if maxOrders >= 29 and orderLevelsOn else na, title='Order #29', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown28) if maxOrders >= 30 and orderLevelsOn else na, title='Order #30', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown29) if maxOrders >= 31 and orderLevelsOn else na, title='Order #31', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown30) if maxOrders >= 32 and orderLevelsOn else na, title='Order #32', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown31) if maxOrders >= 33 and orderLevelsOn else na, title='Order #33', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown32) if maxOrders >= 34 and orderLevelsOn else na, title='Order #34', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown33) if maxOrders >= 35 and orderLevelsOn else na, title='Order #35', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown34) if maxOrders >= 36 and orderLevelsOn else na, title='Order #36', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown35) if maxOrders >= 37 and orderLevelsOn else na, title='Order #37', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown36) if maxOrders >= 38 and orderLevelsOn else na, title='Order #38', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown37) if maxOrders >= 39 and orderLevelsOn else na, title='Order #39', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown38) if maxOrders >= 40 and orderLevelsOn else na, title='Order #40', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown39) if maxOrders >= 41 and orderLevelsOn else na, title='Order #41', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown40) if maxOrders >= 42 and orderLevelsOn else na, title='Order #42', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown41) if maxOrders >= 43 and orderLevelsOn else na, title='Order #43', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown42) if maxOrders >= 44 and orderLevelsOn else na, title='Order #44', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown43) if maxOrders >= 45 and orderLevelsOn else na, title='Order #45', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown44) if maxOrders >= 46 and orderLevelsOn else na, title='Order #46', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown45) if maxOrders >= 47 and orderLevelsOn else na, title='Order #47', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown46) if maxOrders >= 48 and orderLevelsOn else na, title='Order #48', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown47) if maxOrders >= 49 and orderLevelsOn else na, title='Order #49', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown48) if maxOrders >= 50 and orderLevelsOn else na, title='Order #50', color=color.green)
    plot(strategy.opentrades.entry_price(0) * (1 - avgDown49) if maxOrders >= 51 and orderLevelsOn else na, title='Order #51', color=color.green)
    if strategy.opentrades == 1 and maxOrders >= 2:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied1, limit=strategy.opentrades.entry_price(0) * (1 - avgDown), comment='Buy #2 ' + string.tostring(avgDown * 100, format.percent))
    if strategy.opentrades == 2 and maxOrders >= 3:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied2, limit=strategy.opentrades.entry_price(0) * (1 - avgDown1), comment='Buy #3 ' + string.tostring(avgDown1 * 100, format.percent))
    if strategy.opentrades == 3 and maxOrders >= 4:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied3, limit=strategy.opentrades.entry_price(0) * (1 - avgDown2), comment='Buy #4 ' + string.tostring(avgDown2 * 100, format.percent))
    if strategy.opentrades == 4 and maxOrders >= 5:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied4, limit=strategy.opentrades.entry_price(0) * (1 - avgDown3), comment='Buy #5 ' + string.tostring(avgDown3 * 100, format.percent))
    if strategy.opentrades == 5 and maxOrders >= 6:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied5, limit=strategy.opentrades.entry_price(0) * (1 - avgDown4), comment='Buy #6 ' + string.tostring(avgDown4 * 100, format.percent))
    if strategy.opentrades == 6 and maxOrders >= 7:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied6, limit=strategy.opentrades.entry_price(0) * (1 - avgDown5), comment='Buy #7 ' + string.tostring(avgDown5 * 100, format.percent))
    if strategy.opentrades == 7 and maxOrders >= 8:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied7, limit=strategy.opentrades.entry_price(0) * (1 - avgDown6), comment='Buy #8 ' + string.tostring(avgDown6 * 100, format.percent))
    if strategy.opentrades == 8 and maxOrders >= 9:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied8, limit=strategy.opentrades.entry_price(0) * (1 - avgDown7), comment='Buy #9 ' + string.tostring(avgDown7 * 100, format.percent))
    if strategy.opentrades == 9 and maxOrders >= 10:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied9, limit=strategy.opentrades.entry_price(0) * (1 - avgDown8), comment='Buy #10 ' + string.tostring(avgDown8 * 100, format.percent))
    if strategy.opentrades == 10 and maxOrders >= 11:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied10, limit=strategy.opentrades.entry_price(0) * (1 - avgDown9), comment='Buy #11 ' + string.tostring(avgDown9 * 100, format.percent))
    if strategy.opentrades == 11 and maxOrders >= 12:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied11, limit=strategy.opentrades.entry_price(0) * (1 - avgDown10), comment='Buy #12 ' + string.tostring(avgDown10 * 100, format.percent))
    if strategy.opentrades == 12 and maxOrders >= 13:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied12, limit=strategy.opentrades.entry_price(0) * (1 - avgDown11), comment='Buy #13 ' + string.tostring(avgDown11 * 100, format.percent))
    if strategy.opentrades == 13 and maxOrders >= 14:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied13, limit=strategy.opentrades.entry_price(0) * (1 - avgDown12), comment='Buy #14 ' + string.tostring(avgDown12 * 100, format.percent))
    if strategy.opentrades == 14 and maxOrders >= 15:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied14, limit=strategy.opentrades.entry_price(0) * (1 - avgDown13), comment='Buy #15 ' + string.tostring(avgDown13 * 100, format.percent))
    if strategy.opentrades == 15 and maxOrders >= 16:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied15, limit=strategy.opentrades.entry_price(0) * (1 - avgDown14), comment='Buy #16 ' + string.tostring(avgDown14 * 100, format.percent))
    if strategy.opentrades == 16 and maxOrders >= 17:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied16, limit=strategy.opentrades.entry_price(0) * (1 - avgDown15), comment='Buy #17 ' + string.tostring(avgDown15 * 100, format.percent))
    if strategy.opentrades == 17 and maxOrders >= 18:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied17, limit=strategy.opentrades.entry_price(0) * (1 - avgDown16), comment='Buy #18 ' + string.tostring(avgDown16 * 100, format.percent))
    if strategy.opentrades == 18 and maxOrders >= 19:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied18, limit=strategy.opentrades.entry_price(0) * (1 - avgDown17), comment='Buy #19 ' + string.tostring(avgDown17 * 100, format.percent))
    if strategy.opentrades == 19 and maxOrders >= 20:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied19, limit=strategy.opentrades.entry_price(0) * (1 - avgDown18), comment='Buy #20 ' + string.tostring(avgDown18 * 100, format.percent))
    if strategy.opentrades == 20 and maxOrders >= 21:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied20, limit=strategy.opentrades.entry_price(0) * (1 - avgDown19), comment='Buy #21 ' + string.tostring(avgDown19 * 100, format.percent))
    if strategy.opentrades == 21 and maxOrders >= 22:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied21, limit=strategy.opentrades.entry_price(0) * (1 - avgDown20), comment='Buy #22 ' + string.tostring(avgDown20 * 100, format.percent))
    if strategy.opentrades == 22 and maxOrders >= 23:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied21, limit=strategy.opentrades.entry_price(0) * (1 - avgDown21), comment='Buy #23 ' + string.tostring(avgDown21 * 100, format.percent))
    if strategy.opentrades == 23 and maxOrders >= 24:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied22, limit=strategy.opentrades.entry_price(0) * (1 - avgDown22), comment='Buy #24 ' + string.tostring(avgDown22 * 100, format.percent))
    if strategy.opentrades == 24 and maxOrders >= 25:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied23, limit=strategy.opentrades.entry_price(0) * (1 - avgDown23), comment='Buy #25 ' + string.tostring(avgDown23 * 100, format.percent))
    if strategy.opentrades == 25 and maxOrders >= 26:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied24, limit=strategy.opentrades.entry_price(0) * (1 - avgDown24), comment='Buy #26 ' + string.tostring(avgDown24 * 100, format.percent))
    if strategy.opentrades == 26 and maxOrders >= 27:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied25, limit=strategy.opentrades.entry_price(0) * (1 - avgDown25), comment='Buy #27 ' + string.tostring(avgDown25 * 100, format.percent))
    if strategy.opentrades == 27 and maxOrders >= 28:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied26, limit=strategy.opentrades.entry_price(0) * (1 - avgDown26), comment='Buy #28 ' + string.tostring(avgDown26 * 100, format.percent))
    if strategy.opentrades == 28 and maxOrders >= 29:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied27, limit=strategy.opentrades.entry_price(0) * (1 - avgDown27), comment='Buy #29 ' + string.tostring(avgDown27 * 100, format.percent))
    if strategy.opentrades == 29 and maxOrders >= 30:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied28, limit=strategy.opentrades.entry_price(0) * (1 - avgDown28), comment='Buy #30 ' + string.tostring(avgDown28 * 100, format.percent))
    if strategy.opentrades == 30 and maxOrders >= 31:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied29, limit=strategy.opentrades.entry_price(0) * (1 - avgDown29), comment='Buy #31 ' + string.tostring(avgDown29 * 100, format.percent))
    if strategy.opentrades == 31 and maxOrders >= 32:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied30, limit=strategy.opentrades.entry_price(0) * (1 - avgDown30), comment='Buy #32 ' + string.tostring(avgDown30 * 100, format.percent))
    if strategy.opentrades == 32 and maxOrders >= 33:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied31, limit=strategy.opentrades.entry_price(0) * (1 - avgDown31), comment='Buy #33 ' + string.tostring(avgDown31 * 100, format.percent))
    if strategy.opentrades == 33 and maxOrders >= 34:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied32, limit=strategy.opentrades.entry_price(0) * (1 - avgDown32), comment='Buy #34 ' + string.tostring(avgDown32 * 100, format.percent))
    if strategy.opentrades == 34 and maxOrders >= 35:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied33, limit=strategy.opentrades.entry_price(0) * (1 - avgDown33), comment='Buy #35 ' + string.tostring(avgDown33 * 100, format.percent))
    if strategy.opentrades == 35 and maxOrders >= 36:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied34, limit=strategy.opentrades.entry_price(0) * (1 - avgDown34), comment='Buy #36 ' + string.tostring(avgDown34 * 100, format.percent))
    if strategy.opentrades == 36 and maxOrders >= 37:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied35, limit=strategy.opentrades.entry_price(0) * (1 - avgDown35), comment='Buy #37 ' + string.tostring(avgDown35 * 100, format.percent))
    if strategy.opentrades == 37 and maxOrders >= 38:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied36, limit=strategy.opentrades.entry_price(0) * (1 - avgDown36), comment='Buy #38 ' + string.tostring(avgDown36 * 100, format.percent))
    if strategy.opentrades == 38 and maxOrders >= 39:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied37, limit=strategy.opentrades.entry_price(0) * (1 - avgDown37), comment='Buy #39 ' + string.tostring(avgDown37 * 100, format.percent))
    if strategy.opentrades == 39 and maxOrders >= 40:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied38, limit=strategy.opentrades.entry_price(0) * (1 - avgDown38), comment='Buy #40 ' + string.tostring(avgDown38 * 100, format.percent))
    if strategy.opentrades == 40 and maxOrders >= 41:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied39, limit=strategy.opentrades.entry_price(0) * (1 - avgDown39), comment='Buy #41 ' + string.tostring(avgDown39 * 100, format.percent))
    if strategy.opentrades == 41 and maxOrders >= 42:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied40, limit=strategy.opentrades.entry_price(0) * (1 - avgDown40), comment='Buy #42 ' + string.tostring(avgDown40 * 100, format.percent))
    if strategy.opentrades == 42 and maxOrders >= 43:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied41, limit=strategy.opentrades.entry_price(0) * (1 - avgDown41), comment='Buy #43 ' + string.tostring(avgDown41 * 100, format.percent))
    if strategy.opentrades == 43 and maxOrders >= 44:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied42, limit=strategy.opentrades.entry_price(0) * (1 - avgDown42), comment='Buy #44 ' + string.tostring(avgDown42 * 100, format.percent))
    if strategy.opentrades == 44 and maxOrders >= 45:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied43, limit=strategy.opentrades.entry_price(0) * (1 - avgDown43), comment='Buy #45 ' + string.tostring(avgDown43 * 100, format.percent))
    if strategy.opentrades == 45 and maxOrders >= 46:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied44, limit=strategy.opentrades.entry_price(0) * (1 - avgDown44), comment='Buy #46 ' + string.tostring(avgDown44 * 100, format.percent))
    if strategy.opentrades == 46 and maxOrders >= 47:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied45, limit=strategy.opentrades.entry_price(0) * (1 - avgDown45), comment='Buy #47 ' + string.tostring(avgDown45 * 100, format.percent))
    if strategy.opentrades == 47 and maxOrders >= 48:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied46, limit=strategy.opentrades.entry_price(0) * (1 - avgDown46), comment='Buy #48 ' + string.tostring(avgDown46 * 100, format.percent))
    if strategy.opentrades == 48 and maxOrders >= 49:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied47, limit=strategy.opentrades.entry_price(0) * (1 - avgDown47), comment='Buy #49 ' + string.tostring(avgDown47 * 100, format.percent))
    if strategy.opentrades == 49 and maxOrders >= 50:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied48, limit=strategy.opentrades.entry_price(0) * (1 - avgDown48), comment='Buy #50 ' + string.tostring(avgDown48 * 100, format.percent))
    if strategy.opentrades == 50 and maxOrders >= 51:
        strategy.entry('Bull #1', strategy.long, qty=quantMultiplied49, limit=strategy.opentrades.entry_price(0) * (1 - avgDown49), comment='Buy #51 ' + string.tostring(avgDown49 * 100, format.percent))
    stoplossPrice: float = 0.0
    if stoplossOn and strategy.opentrades == maxOrders:
        stoplossPrice = strategy.opentrades.entry_price(maxOrders - 1) * (1 - stoploss)
    strategy.exit('Bull #1', limit=strategy.position_avg_price * (1 + takeProfit), stop=stoplossPrice if stoplossOn and strategy.opentrades == maxOrders else na, comment_profit='Take Profit On ' + string.tostring(strategy.opentrades) + ' Orders', comment_loss='Stoploss Hit @ -' + string.tostring(stoploss * 100, '#.##') + '% From Last Order')
    maxOrdersAtOnce = ta.highest(strategy.opentrades, 10000)
    largestOrder = 'Highest # Of Open Trades ' + string.tostring(maxOrdersAtOnce, '#.##')
    def avgBarsPerTrade():
        sumBarsPerTrade: int = 0
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.closedtrades - 1):
            tradeNo = __loop_0__.value
            sumBarsPerTrade = sumBarsPerTrade + strategy.closedtrades.exit_bar_index(tradeNo) - strategy.closedtrades.entry_bar_index(tradeNo) + 1
        result = nz(sumBarsPerTrade / strategy.closedtrades)
        return result

    stoplossText = 'SL ' + string.tostring(stoploss * 100, '#.##') + '%' if stoplossOn else 'SL Off'
    percToRecover = (strategy.position_avg_price * (1 + takeProfit) / close - 1) * 100
    avgPrice = 'Avg Price $' + string.tostring(strategy.position_avg_price, '#.##')
    pnl = 'Trade PnL ' + string.tostring((close - strategy.position_avg_price) / strategy.position_avg_price * 100, format.percent)
    tpPrice = 'TP Price $' + string.tostring(strategy.position_avg_price * (1 + takeProfit), '#.##')
    posSize = 'Pos Size ' + string.tostring(strategy.position_size, '#.##') + ' Units'
    numOrders = '# Of Open Orders ' + string.tostring(strategy.opentrades)
    percRecovery = 'From Take Profit ' + string.tostring(percToRecover, format.percent) + '￪'
    closedTrades = 'Total # Trades ' + string.tostring(strategy.closedtrades)
    initialCapital = 'Initial Capital $' + string.tostring(strategy.initial_capital)
    maxDrawdown = 'Max Drawdown $' + string.tostring(strategy.max_drawdown, '#.##')
    avgBarsPerTrade__global__ = 'Avg Bars Per Trade ' + string.tostring(avgBarsPerTrade(), '#')
    grossProfit = 'Gross Profit $' + string.tostring(strategy.grossprofit, '#.##')
    netProfit = 'Net Profit $' + string.tostring(strategy.netprofit, '#.##')
    equity = 'Portfolio Value $' + string.tostring(strategy.equity, '#.##')
    percentProfit = 'Percent Profit ' + string.tostring(strategy.netprofit / strategy.initial_capital * 100, format.percent)
    avgPriceLine = plot(strategy.position_avg_price, title='Position Average Price', color=color.aqua, linewidth=4)
    tpLevel = plot(strategy.position_avg_price * (1 + takeProfit), title='Take Profit Level', color=color.red, linewidth=4)
    stopLevel = plot(stoplossPrice if stoplossOn and strategy.opentrades == maxOrders else na, title='Stoploss Level', color=color.orange, linewidth=2, style=plot.style_cross)
    dataTable = table.new(tablePosition, columns=2, rows=19, bgcolor=color.blue, frame_color=color.white, frame_width=1, border_color=color.white, border_width=1)
    if dataTableOn:
        table.cell(table_id=dataTable, column=0, row=0, text='Current Trade', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.navy)
        table.cell(table_id=dataTable, column=0, row=1, text=avgPrice, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=2, text=tpPrice, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=3, text=pnl, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=4, text=percRecovery, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=5, text=posSize, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=6, text=numOrders, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=7, text='Overall Performance', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.navy)
        table.cell(table_id=dataTable, column=0, row=8, text=closedTrades, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=9, text=largestOrder, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=10, text=maxDrawdown, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=11, text=avgBarsPerTrade__global__, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=12, text=grossProfit, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=13, text=netProfit, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=14, text=percentProfit, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=15, text=equity, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=0, row=16, text=initialCapital, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)
        table.cell(table_id=dataTable, column=1, row=0, text='Settings', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.navy)
        table.cell(table_id=dataTable, column=1, row=1, text=stoplossText, height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=2, text='TP ' + string.tostring(takeProfit * 100) + '%', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=3, text='AD ' + string.tostring(avgDown * 100) + '%', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=4, text='AD%M ' + string.tostring(percentScale) + 'x', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=5, text='VM ' + string.tostring(multiplier) + 'x', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=6, text='M#O ' + string.tostring(maxOrders), height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
        table.cell(table_id=dataTable, column=1, row=7, text='BO $' + string.tostring(quantity), height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center, bgcolor=color.purple)
    warningTable = table.new(position.top_center, columns=1, rows=1, bgcolor=color.orange)
    if strategy.closedtrades == 0 and close > quantity:
        table.cell(table_id=warningTable, column=0, row=0, text='Share Price Is Higher Than Base Order', height=0, text_color=color.white, text_halign=text.align_left, text_valign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
