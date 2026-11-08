"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, high, input, label, line,
    low, math, matrix, na, open, plot, script, size, string, ta, table, text, yloc
)
from pynecore.types import Box, Color, Label, Line, Matrix, NA, Persistent, Series


@script.indicator('R:R Trading System Framework', overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    Backtest_A=input.string('0. Stochastic', '     A)', options=('None', '0. Stochastic', '1. 2x MA Cross', '2. MACD', '3. Bollinger Bands', '4. Supertrend', '5. Stochastic (Short)', '6. 2x MA Cross (Short)', '7. MACD (Short)', '8. Bollinger Bands (Short)', '9. Supertrend (Short)'), group='📈 BACKTESTING BOXES / LABELS / TRAILING STOP', inline='1'),
    Backtest_B=input.string('1. 2x MA Cross', '  B)', options=('None', '0. Stochastic', '1. 2x MA Cross', '2. MACD', '3. Bollinger Bands', '4. Supertrend', '5. Stochastic (Short)', '6. 2x MA Cross (Short)', '7. MACD (Short)', '8. Bollinger Bands (Short)', '9. Supertrend (Short)'), group='📈 BACKTESTING BOXES / LABELS / TRAILING STOP', inline='1', tooltip='Display 2 different trade types.\n\nCompare and contrast all the different components of the trades and their relationships with one another.\n\nThis system is designed to force you to consider Risk:Reward at all times throughout the trading process. Get creative but try your best to only include things that improve your decision-making process, create consistency, improve risk:reward concepts, and are realsitic once met with the brutal truth of the trading world.'),
    TTT_Activated=input.bool(True, 'Active', group='📊 TRADE TRACKING TABLE', inline='1'),
    TTT_textSize=input.string('normal', '', group='📊 TRADE TRACKING TABLE', inline='1', options=('tiny', 'small', 'normal', 'large')),
    TTT_tableYpos=input.string('top', '', group='📊 TRADE TRACKING TABLE', inline='1', options=('top', 'middle', 'bottom')),
    TTT_tableXpos=input.string('center', '', group='📊 TRADE TRACKING TABLE', inline='1', options=('left', 'center', 'right'), tooltip='- Activate Table\n- Text Size\n- Table Position (Y)\n- Table Position (X)'),
    RRT_Activated=input.bool(True, 'Active', group='📊 RISK:REWARD TABLE', inline='1', tooltip=''),
    RRT_textSize=input.string('normal', '', group='📊 RISK:REWARD TABLE', inline='1', options=('tiny', 'small', 'normal', 'large')),
    RRT_tableYpos=input.string('bottom', '', group='📊 RISK:REWARD TABLE', inline='1', options=('top', 'middle', 'bottom')),
    RRT_tableXpos=input.string('left', '', group='📊 RISK:REWARD TABLE', inline='1', options=('left', 'center', 'right'), tooltip='- Activate Table\n- Text Size\n- Table Position (Y)\n- Table Position (X)'),
    L0_Activated=input.bool(True, 'Active |  ', group='▷ 0. Stochastic', inline='1'),
    L0_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 0. Stochastic', inline='1', tooltip='% of price. The Trailing Stop is built to only become active once the Trailing Stop is above the Entry price and uses the same % set here for the Entry Stop.'),
    L0_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 0. Stochastic', inline='2'),
    L0_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 0. Stochastic', inline='2', tooltip='Multiple of the Stop % above. This represents your risk:reward ratio for each TP level.'),
    L0_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 0. Stochastic', inline='3'),
    L0_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 0. Stochastic', inline='3', tooltip='Multiple of the Stop % above. This represents your risk:reward ratio for each TP level.'),
    L1_Activated=input.bool(True, 'Active |  ', group='▷ 1. 2x MA Cross', inline='1'),
    L1_SL_Value=input.float(2.5, 'Stop %', step=0.25, group='▷ 1. 2x MA Cross', inline='1'),
    L1_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 1. 2x MA Cross', inline='2'),
    L1_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 1. 2x MA Cross', inline='2'),
    L1_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 1. 2x MA Cross', inline='3'),
    L1_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 1. 2x MA Cross', inline='3'),
    L2_Activated=input.bool(True, 'Active |  ', group='▷ 2. MACD', inline='1'),
    L2_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 2. MACD', inline='1'),
    L2_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 2. MACD', inline='2'),
    L2_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 2. MACD', inline='2'),
    L2_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 2. MACD', inline='3'),
    L2_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 2. MACD', inline='3'),
    L3_Activated=input.bool(True, 'Active |  ', group='▷ 3. Bollinger Bands', inline='1'),
    L3_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 3. Bollinger Bands', inline='1'),
    L3_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 3. Bollinger Bands', inline='2'),
    L3_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 3. Bollinger Bands', inline='2'),
    L3_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 3. Bollinger Bands', inline='3'),
    L3_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 3. Bollinger Bands', inline='3'),
    L4_Activated=input.bool(True, 'Active |  ', group='▷ 4. Supertrend', inline='1'),
    L4_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 4. Supertrend', inline='1'),
    L4_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 4. Supertrend', inline='2'),
    L4_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 4. Supertrend', inline='2'),
    L4_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 4. Supertrend', inline='3'),
    L4_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 4. Supertrend', inline='3'),
    S5_Activated=input.bool(True, 'Active |  ', group='▷ 5. Stochastic (Short)', inline='1'),
    S5_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 5. Stochastic (Short)', inline='1'),
    S5_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 5. Stochastic (Short)', inline='2'),
    S5_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 5. Stochastic (Short)', inline='2'),
    S5_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 5. Stochastic (Short)', inline='3'),
    S5_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 5. Stochastic (Short)', inline='3'),
    S6_Activated=input.bool(True, 'Active |  ', group='▷ 6. 2x MA Cross (Short)', inline='1'),
    S6_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 6. 2x MA Cross (Short)', inline='1'),
    S6_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 6. 2x MA Cross (Short)', inline='2'),
    S6_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 6. 2x MA Cross (Short)', inline='2'),
    S6_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 6. 2x MA Cross (Short)', inline='3'),
    S6_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 6. 2x MA Cross (Short)', inline='3'),
    S7_Activated=input.bool(True, 'Active |  ', group='▷ 7. MACD (Short)', inline='1'),
    S7_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 7. MACD (Short)', inline='1'),
    S7_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 7. MACD (Short)', inline='2'),
    S7_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 7. MACD (Short)', inline='2'),
    S7_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 7. MACD (Short)', inline='3'),
    S7_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 7. MACD (Short)', inline='3'),
    S8_Activated=input.bool(True, 'Active |  ', group='▷ 8. Bollinger Bands (Short)', inline='1'),
    S8_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 8. Bollinger Bands (Short)', inline='1'),
    S8_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 8. Bollinger Bands (Short)', inline='2'),
    S8_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 8. Bollinger Bands (Short)', inline='2'),
    S8_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 8. Bollinger Bands (Short)', inline='3'),
    S8_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 8. Bollinger Bands (Short)', inline='3'),
    S9_Activated=input.bool(True, 'Active |  ', group='▷ 9. Supertrend (Short)', inline='1'),
    S9_SL_Value=input.float(2.0, 'Stop %', step=0.25, group='▷ 9. Supertrend (Short)', inline='1'),
    S9_TP1_Value=input.float(1.0, '    TP 1', step=0.25, group='▷ 9. Supertrend (Short)', inline='2'),
    S9_TP2_Value=input.float(2.0, 'TP 2', step=0.25, group='▷ 9. Supertrend (Short)', inline='2'),
    S9_TP3_Value=input.float(3.0, '    TP 3', step=0.25, group='▷ 9. Supertrend (Short)', inline='3'),
    S9_TP4_Value=input.float(4.0, 'TP 4', step=0.25, group='▷ 9. Supertrend (Short)', inline='3')
):
    C_BLUE: Color = color.new('#00E5FF')
    C_ORANGE: Color = color.new('#FFA300')
    C_LIME_GREEN: Color = color.new('#14FF00')
    C_PURPLE: Color = color.new('#E757FF')
    C_YELLOW: Color = color.new('#FDFF5F')
    C_DARK_BLUE: Color = color.new('#005AE6')
    C_LIME_YELLOW: Color = color.new('#C9FF00')
    C_DARK_PURPLE: Color = color.new('#A600FF')
    C_MINT: Color = color.new('#00FFA9')
    C_BURNT_ORANGE: Color = color.new('#FF5F00')
    C_PINK: Color = color.new('#FF0078')
    C_WHITE: Color = color.new('#FFFFFF')
    C_BLACK: Color = color.new('#000000')
    C_TV_GRAY_OUTLINE: Color = color.new('#434651')
    C_LIGHT_GRAY: Color = color.new('#D1D4DC')
    C_MEDIUM_GRAY: Color = color.new('#787B86')
    C_TV_BLACK: Color = color.new('#131722')
    def f_gradientColor(_col, _val, _max, _min):
        return color.from_gradient(_val, _min, _max, color.new(_col, 80), color.new(_col, 0))

    matrix__ren__: Persistent[Matrix[float]] = na(Matrix[float])
    row__global__: Persistent[list[int]] = array.from_items(0)
    col__global__: Persistent[list[int]] = array.from_items(0)
    matrixLine: Persistent[Matrix[Line]] = na(Matrix[Line])
    colLine: Persistent[list[int]] = array.from_items(0)
    matrixLabel: Persistent[Matrix[Label]] = na(Matrix[Label])
    colLabel: Persistent[list[int]] = array.from_items(0)
    def row(row__00000053__):
        __block_result__ = na
        if barstate.isfirst:
            get = array.get(row__00000053__, 0)
            array.set(row__00000053__, 0, get + 1)
            __block_result__ = get
        return __block_result__

    def col(col__00000057__):
        __block_result_1__ = na
        if barstate.isfirst:
            get = array.get(col__00000057__, 0)
            array.set(col__00000057__, 0, get + 1)
            __block_result_1__ = get
        return __block_result_1__

    L0: Persistent = row(row__global__)
    L1: Persistent = row(row__global__)
    L2: Persistent = row(row__global__)
    L3: Persistent = row(row__global__)
    L4: Persistent = row(row__global__)
    S5: Persistent = row(row__global__)
    S6: Persistent = row(row__global__)
    S7: Persistent = row(row__global__)
    S8: Persistent = row(row__global__)
    S9: Persistent = row(row__global__)
    Entry_Price: Persistent = col(col__global__)
    Exit_Price: Persistent = col(col__global__)
    Stop_Price: Persistent = col(col__global__)
    TP1_Price: Persistent = col(col__global__)
    TP2_Price: Persistent = col(col__global__)
    TP3_Price: Persistent = col(col__global__)
    TP4_Price: Persistent = col(col__global__)
    Bullish_Price: Persistent = col(col__global__)
    Bearish_Price: Persistent = col(col__global__)
    TSL_Price: Persistent = col(col__global__)
    Max_Reached: Persistent = col(col__global__)
    Min_Reached: Persistent = col(col__global__)
    Entry_Count: Persistent = col(col__global__)
    In_Trade_Bar_Count: Persistent = col(col__global__)
    TSL_Hit_Count: Persistent = col(col__global__)
    TP1_Hit_Count: Persistent = col(col__global__)
    TP2_Hit_Count: Persistent = col(col__global__)
    TP3_Hit_Count: Persistent = col(col__global__)
    TP4_Hit_Count: Persistent = col(col__global__)
    Fail_Hit_Count: Persistent = col(col__global__)
    Bullish_Hit_Count: Persistent = col(col__global__)
    Bearish_Hit_Count: Persistent = col(col__global__)
    TSL_Bars_Count: Persistent = col(col__global__)
    TP1_Bars_Count: Persistent = col(col__global__)
    TP2_Bars_Count: Persistent = col(col__global__)
    TP3_Bars_Count: Persistent = col(col__global__)
    TP4_Bars_Count: Persistent = col(col__global__)
    Fail_Bars_Count: Persistent = col(col__global__)
    Entry_is_Active: Persistent = col(col__global__)
    TP1_Hit: Persistent = col(col__global__)
    TP2_Hit: Persistent = col(col__global__)
    TP3_Hit: Persistent = col(col__global__)
    TP4_Hit: Persistent = col(col__global__)
    TSL_Hit: Persistent = col(col__global__)
    Fail_Hit: Persistent = col(col__global__)
    Win_RR_Ratio_Sum: Persistent = col(col__global__)
    Loss_RR_Ratio_Sum: Persistent = col(col__global__)
    Bullish_Amount_Sum: Persistent = col(col__global__)
    Bearish_Amount_Sum: Persistent = col(col__global__)
    Bullish_to_Min_Amount: Persistent = col(col__global__)
    Bearish_to_Max_Amount: Persistent = col(col__global__)
    PL_Amount: Persistent = col(col__global__)
    Stop_Amount: Persistent = col(col__global__)
    Trade_RR_Ratio: Persistent = col(col__global__)
    Number_of_Wins: Persistent = col(col__global__)
    Number_of_Losses: Persistent = col(col__global__)
    Win_Percent: Persistent = col(col__global__)
    Loss_Percent: Persistent = col(col__global__)
    Avg_Win_RR: Persistent = col(col__global__)
    Avg_Loss_RR: Persistent = col(col__global__)
    Avg_Risk_Reward: Persistent = col(col__global__)
    Avg_Bullish_Dev: Persistent = col(col__global__)
    Avg_Bearish_Dev: Persistent = col(col__global__)
    Avg_Bullish_RR: Persistent = col(col__global__)
    Avg_Bearish_RR: Persistent = col(col__global__)
    RRT_Fail_Hit_Percentage: Persistent = col(col__global__)
    RRT_TP1_Hit_Percentage: Persistent = col(col__global__)
    RRT_TP2_Hit_Percentage: Persistent = col(col__global__)
    RRT_TP3_Hit_Percentage: Persistent = col(col__global__)
    RRT_TP4_Hit_Percentage: Persistent = col(col__global__)
    RRT_TSL_Hit_Percentage: Persistent = col(col__global__)
    RRT_Avg_Fail_Bars: Persistent = col(col__global__)
    RRT_Avg_TP1_Bars: Persistent = col(col__global__)
    RRT_Avg_TP2_Bars: Persistent = col(col__global__)
    RRT_Avg_TP3_Bars: Persistent = col(col__global__)
    RRT_Avg_TP4_Bars: Persistent = col(col__global__)
    RRT_Avg_TSL_Bars: Persistent = col(col__global__)
    a_entryPriceLabel: Persistent[list[Label]] = array.new_label()
    a_newLine: Persistent[list[Line]] = array.new_line()
    a_newLabel: Persistent[list[Label]] = array.new_label()
    a_newBox_0: Persistent[list[Box]] = array.new_box()
    a_newBox_1: Persistent[list[Box]] = array.new_box()
    a_newBox_2: Persistent[list[Box]] = array.new_box()
    a_newBox_3: Persistent[list[Box]] = array.new_box()
    a_newBox_4: Persistent[list[Box]] = array.new_box()
    a_newBox_5: Persistent[list[Box]] = array.new_box()
    a_newBox_6: Persistent[list[Box]] = array.new_box()
    a_newBox_7: Persistent[list[Box]] = array.new_box()
    a_newBox_8: Persistent[list[Box]] = array.new_box()
    a_newBox_9: Persistent[list[Box]] = array.new_box()
    if array.size(a_entryPriceLabel) > 50:
        label.delete(array.pop(a_entryPriceLabel))
    if array.size(a_newLabel) > 350:
        label.delete(array.pop(a_newLabel))
    def cleanBox(bx):
        __block_result_2__ = na
        if array.size(bx) > 450:
            __block_result_2__ = box.delete(array.pop(bx))
        return __block_result_2__

    cleanBox(a_newBox_0)
    cleanBox(a_newBox_1)
    cleanBox(a_newBox_2)
    cleanBox(a_newBox_3)
    cleanBox(a_newBox_4)
    cleanBox(a_newBox_5)
    cleanBox(a_newBox_6)
    cleanBox(a_newBox_7)
    cleanBox(a_newBox_8)
    cleanBox(a_newBox_9)
    Entry_Line: Persistent = col(colLine)
    SL_Line: Persistent = col(colLine)
    TP1_Line: Persistent = col(colLine)
    TP2_Line: Persistent = col(colLine)
    TP3_Line: Persistent = col(colLine)
    TP4_Line: Persistent = col(colLine)
    TSL_Line: Persistent = col(colLine)
    Entry_Label: Persistent = col(colLabel)
    SL_Label: Persistent = col(colLabel)
    TP1_Label: Persistent = col(colLabel)
    TP2_Label: Persistent = col(colLabel)
    TP3_Label: Persistent = col(colLabel)
    TP4_Label: Persistent = col(colLabel)
    TSL_Label: Persistent = col(colLabel)
    if barstate.isfirst:
        matrix__ren__ = matrix.new(array.get(row__global__, 0), array.get(col__global__, 0), 0.0)
        matrixLine = matrix.new(array.get(row__global__, 0), array.get(colLine, 0), NA(Line))
        matrixLabel = matrix.new(array.get(row__global__, 0), array.get(colLabel, 0), NA(Label))
        __loop_1__ = pine_loop(0, 1)
        while __loop_1__.step(array.get(row__global__, 0) - 1):
            i = __loop_1__.value
            __loop_2__ = pine_loop(0, 1)
            while __loop_2__.step(array.get(colLine, 0) - 1):
                j = __loop_2__.value
                matrix.set(matrixLine, i, j, line.new(bar_index, close, bar_index, close, width=3))
            __loop_2__ = pine_loop(0, 1)
            while __loop_2__.step(array.get(colLabel, 0) - 1):
                j = __loop_2__.value
                matrix.set(matrixLabel, i, j, label.new(bar_index, close, color=na))
    a_priceBox: Persistent[list[Box]] = array.new_box()
    if barstate.isfirst:
        for i in pine_range(0, 9, 1):
            array.unshift(a_priceBox, box.new(bar_index, close, bar_index, close, border_color=na, bgcolor=na))
    Risk_Reward_Table: Persistent = table.new(position=RRT_tableYpos + '_' + RRT_tableXpos, columns=30, rows=20, bgcolor=C_TV_BLACK, border_color=C_TV_GRAY_OUTLINE, border_width=2, frame_color=C_TV_GRAY_OUTLINE, frame_width=4)
    Trade_Tracking_Table: Persistent = table.new(position=TTT_tableYpos + '_' + TTT_tableXpos, columns=20, rows=20, bgcolor=C_TV_BLACK, border_color=C_TV_GRAY_OUTLINE, border_width=2, frame_color=C_TV_GRAY_OUTLINE, frame_width=4)
    length: int = 14
    OverBought: int = 80
    OverSold: int = 20
    smoothK: int = 3
    smoothD: int = 3
    k = ta.sma(ta.stoch(close, high, low, length), smoothK)
    d = ta.sma(k, smoothD)
    co = ta.crossover(k, d)
    cu = ta.crossunder(k, d)
    stochBull = not na(k) and (not na(d)) and co and (k < OverSold)
    stochBear = not na(k) and (not na(d)) and cu and (k > OverBought)
    price = close
    fastLength: int = 9
    slowLength: int = 18
    mafast = ta.sma(price, fastLength)
    maslow = ta.sma(price, slowLength)
    XoverFastSlow = ta.crossover(mafast, maslow)
    XunderFastSlow = ta.crossunder(mafast, maslow)
    MACD, aMACD, delta = ta.macd(close, 12, 26, 9)
    XoverDt = ta.crossover(delta, 0)
    XunderDt = ta.crossunder(delta, 0)
    basis, upper, lower = ta.bb(close, 20, 2)
    buyEntry = ta.crossover(close, lower)
    sellEntry = ta.crossunder(close, upper)
    atrPeriod: int = 10
    factor: float = 3.0
    _, STdirection = ta.supertrend(factor, atrPeriod)
    chDir = ta.change(STdirection)
    sma200 = ta.sma(close, 200)
    aboveSma200 = close > sma200
    belowSma200 = close < sma200
    L0_Entry = matrix.get(matrix__ren__, L0, Entry_is_Active) == 0 and L0_Activated and stochBull and aboveSma200
    L1_Entry = matrix.get(matrix__ren__, L1, Entry_is_Active) == 0 and L1_Activated and XoverFastSlow and aboveSma200
    L2_Entry = matrix.get(matrix__ren__, L2, Entry_is_Active) == 0 and L2_Activated and XoverDt and aboveSma200
    L3_Entry = matrix.get(matrix__ren__, L3, Entry_is_Active) == 0 and L3_Activated and buyEntry and aboveSma200
    L4_Entry = matrix.get(matrix__ren__, L4, Entry_is_Active) == 0 and L4_Activated and (chDir < 0) and aboveSma200
    S5_Entry = matrix.get(matrix__ren__, S5, Entry_is_Active) == 0 and S5_Activated and stochBear and belowSma200
    S6_Entry = matrix.get(matrix__ren__, S6, Entry_is_Active) == 0 and S6_Activated and XunderFastSlow and belowSma200
    S7_Entry = matrix.get(matrix__ren__, S7, Entry_is_Active) == 0 and S7_Activated and XunderDt and belowSma200
    S8_Entry = matrix.get(matrix__ren__, S8, Entry_is_Active) == 0 and S8_Activated and sellEntry and belowSma200
    S9_Entry = matrix.get(matrix__ren__, S9, Entry_is_Active) == 0 and S9_Activated and (chDir > 0) and belowSma200
    L0_Entry_Bullish = L0_Activated and stochBull and aboveSma200
    L1_Entry_Bullish = L1_Activated and XoverFastSlow and aboveSma200
    L2_Entry_Bullish = L2_Activated and XoverDt and aboveSma200
    L3_Entry_Bullish = L3_Activated and buyEntry and aboveSma200
    L4_Entry_Bullish = L4_Activated and chDir < 0 and aboveSma200
    S5_Entry_Bearish = S5_Activated and stochBear and belowSma200
    S6_Entry_Bearish = S6_Activated and XunderFastSlow and belowSma200
    S7_Entry_Bearish = S7_Activated and XunderDt and belowSma200
    S8_Entry_Bearish = S8_Activated and sellEntry and belowSma200
    S9_Entry_Bearish = S9_Activated and chDir > 0 and belowSma200
    L0_Entry_Bearish = L0_Activated and stochBear
    L1_Entry_Bearish = L1_Activated and XunderFastSlow
    L2_Entry_Bearish = L2_Activated and XunderDt
    L3_Entry_Bearish = L3_Activated and sellEntry
    L4_Entry_Bearish = L4_Activated and chDir > 0
    S5_Entry_Bullish = S5_Activated and stochBull
    S6_Entry_Bullish = S6_Activated and XoverFastSlow
    S7_Entry_Bullish = S7_Activated and XoverDt
    S8_Entry_Bullish = S8_Activated and buyEntry
    S9_Entry_Bullish = S9_Activated and chDir < 0
    def f_TP_Hit(direction, tradeColor, trade, TP_Price, TP_Hit_Count, TP_Bars_Count, TP_Hit, TPtext, entryText):
        gTP_Price = matrix.get(matrix__ren__, trade, TP_Price)
        f_TP_Hit__00000121__ = high > gTP_Price and matrix.get(matrix__ren__, trade, TP_Hit) == 0 if direction == 'L' else low < gTP_Price and matrix.get(matrix__ren__, trade, TP_Hit) == 0
        __block_result_3__ = na
        if f_TP_Hit__00000121__:
            gTP_Hit_Count = matrix.get(matrix__ren__, trade, TP_Hit_Count)
            gTP_Bars_Count = matrix.get(matrix__ren__, trade, TP_Bars_Count)
            matrix.set(matrix__ren__, trade, TP_Hit_Count, gTP_Hit_Count + 1)
            matrix.set(matrix__ren__, trade, TP_Bars_Count, gTP_Bars_Count + matrix.get(matrix__ren__, trade, In_Trade_Bar_Count))
            matrix.set(matrix__ren__, trade, TP_Hit, 1)
            __block_result_4__ = na
            if Backtest_A == entryText or Backtest_B == entryText:
                __block_result_4__ = array.unshift(a_newLabel, label.new(bar_index, gTP_Price, text=TPtext, color=color.new(tradeColor, 0), style=label.style_label_lower_right if direction == 'L' else label.style_label_upper_right, textcolor=C_BLACK, size=size.small, tooltip=string.tostring(gTP_Price)))
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def f_Entry(direction, entryActivated, tradeColor, offset, entry: Series, bullishTrigger, bearishTrigger, trade, stopLossValue, takeProfit_1_value, takeProfit_2_value, takeProfit_3_value, takeProfit_4_value, entryText, box__ren__, i):
        __block_result_5__ = na
        if entryActivated:
            matrix.set(matrix__ren__, trade, Max_Reached, math.max(matrix.get(matrix__ren__, trade, Max_Reached), high))
            matrix.set(matrix__ren__, trade, Min_Reached, math.min(matrix.get(matrix__ren__, trade, Min_Reached), low))
            maxReached = matrix.get(matrix__ren__, trade, Max_Reached)
            minReached = matrix.get(matrix__ren__, trade, Min_Reached)
            if entry[1]:
                matrix.set(matrix__ren__, trade, Entry_is_Active, 1)
                stopPrice = open - open * (stopLossValue / 100) if direction == 'L' else open + open * (stopLossValue / 100)
                matrix.set(matrix__ren__, trade, Stop_Price, stopPrice)
                matrix.set(matrix__ren__, trade, TP1_Price, open + open * (stopLossValue * takeProfit_1_value / 100) if direction == 'L' else open - open * (stopLossValue * takeProfit_1_value / 100))
                matrix.set(matrix__ren__, trade, TP2_Price, open + open * (stopLossValue * takeProfit_2_value / 100) if direction == 'L' else open - open * (stopLossValue * takeProfit_2_value / 100))
                matrix.set(matrix__ren__, trade, TP3_Price, open + open * (stopLossValue * takeProfit_3_value / 100) if direction == 'L' else open - open * (stopLossValue * takeProfit_3_value / 100))
                matrix.set(matrix__ren__, trade, TP4_Price, open + open * (stopLossValue * takeProfit_4_value / 100) if direction == 'L' else open - open * (stopLossValue * takeProfit_4_value / 100))
                matrix.set(matrix__ren__, trade, Entry_Price, open)
                matrix.set(matrix__ren__, trade, Exit_Price, 0)
                matrix.set(matrix__ren__, trade, TP1_Hit, 0)
                matrix.set(matrix__ren__, trade, TP2_Hit, 0)
                matrix.set(matrix__ren__, trade, TP3_Hit, 0)
                matrix.set(matrix__ren__, trade, TP4_Hit, 0)
                matrix.set(matrix__ren__, trade, TSL_Hit, 0)
                matrix.set(matrix__ren__, trade, Trade_RR_Ratio, 0)
                matrix.set(matrix__ren__, trade, Stop_Amount, open - stopPrice)
                matrix.set(matrix__ren__, trade, Entry_Count, matrix.get(matrix__ren__, trade, Entry_Count) + 1)
                if Backtest_A == entryText or Backtest_B == entryText:
                    array.unshift(a_entryPriceLabel, label.new(bar_index, open, text='ENTRY', color=color.new(tradeColor, 0), style=label.style_label_right, textcolor=C_BLACK, size=size.small, tooltip=string.tostring(open)))
                    array.unshift(box__ren__, box.new(bar_index, open, bar_index, open, border_color=color.new(tradeColor, 0), bgcolor=color.new(tradeColor, 90)))
                    array.unshift(box__ren__, box.new(bar_index, high, bar_index, low, border_color=color.new(tradeColor, 70), bgcolor=color.new(tradeColor, 98)))
            gActive = matrix.get(matrix__ren__, trade, Entry_is_Active) == 1
            trailingStop = matrix.get(matrix__ren__, trade, TSL_Price)
            trailingStopMax = math.max(open - open * (stopLossValue / 100), trailingStop) if gActive else 0
            trailingStopMin = math.min(open + open * (stopLossValue / 100), trailingStop) if gActive else 10000000.0
            matrix.set(matrix__ren__, trade, TSL_Price, trailingStopMax if direction == 'L' else trailingStopMin)
            gEntry_Line = matrix.get(matrixLine, trade, Entry_Line)
            gEntry_Price = matrix.get(matrix__ren__, trade, Entry_Price)
            gExit_Price = matrix.get(matrix__ren__, trade, Exit_Price)
            gSL_Line = matrix.get(matrixLine, trade, SL_Line)
            gStop_Price = matrix.get(matrix__ren__, trade, Stop_Price)
            gTrade_RR_Ratio = matrix.get(matrix__ren__, trade, Trade_RR_Ratio)
            gTP1_Line = matrix.get(matrixLine, trade, TP1_Line)
            gTP1_Price = matrix.get(matrix__ren__, trade, TP1_Price)
            gIn_Trade_Bar_Count = matrix.get(matrix__ren__, trade, In_Trade_Bar_Count)
            gTP2_Line = matrix.get(matrixLine, trade, TP2_Line)
            gTP2_Price = matrix.get(matrix__ren__, trade, TP2_Price)
            gPL_Amount = matrix.get(matrix__ren__, trade, PL_Amount)
            gTP3_Line = matrix.get(matrixLine, trade, TP3_Line)
            gTP3_Price = matrix.get(matrix__ren__, trade, TP3_Price)
            gTP4_Line = matrix.get(matrixLine, trade, TP4_Line)
            gTP4_Price = matrix.get(matrix__ren__, trade, TP4_Price)
            gTSL_Line = matrix.get(matrixLine, trade, SL_Line)
            gStop_amount = matrix.get(matrix__ren__, trade, Stop_Amount)
            gEntry_Label = matrix.get(matrixLabel, trade, Entry_Label)
            gSL_Label = matrix.get(matrixLabel, trade, SL_Label)
            gTP1_Label = matrix.get(matrixLabel, trade, TP1_Label)
            gTP2_Label = matrix.get(matrixLabel, trade, TP2_Label)
            gTP3_Label = matrix.get(matrixLabel, trade, TP3_Label)
            gTP4_Label = matrix.get(matrixLabel, trade, TP4_Label)
            gTSL_Label = matrix.get(matrixLabel, trade, SL_Label)
            if gActive:
                trailingStop = matrix.get(matrix__ren__, trade, TSL_Price)
                if direction == 'L':
                    line.set_xy1(gEntry_Line, bar_index + offset, gEntry_Price)
                    line.set_xy2(gEntry_Line, bar_index + offset + 8, gEntry_Price)
                    line.set_color(gEntry_Line, tradeColor if close > gEntry_Price else color.new(tradeColor, 50))
                    line.set_xy1(gSL_Line, bar_index + offset, gStop_Price)
                    line.set_xy2(gSL_Line, bar_index + offset + 8, gStop_Price)
                    line.set_color(gSL_Line, color.new(tradeColor, 50))
                    line.set_xy1(gTP1_Line, bar_index + offset, gTP1_Price)
                    line.set_xy2(gTP1_Line, bar_index + offset + 8, gTP1_Price)
                    line.set_color(gTP1_Line, tradeColor if close > gTP1_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP2_Line, bar_index + offset, gTP2_Price)
                    line.set_xy2(gTP2_Line, bar_index + offset + 8, gTP2_Price)
                    line.set_color(gTP2_Line, tradeColor if close > gTP2_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP3_Line, bar_index + offset, gTP3_Price)
                    line.set_xy2(gTP3_Line, bar_index + offset + 8, gTP3_Price)
                    line.set_color(gTP3_Line, tradeColor if close > gTP3_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP4_Line, bar_index + offset, gTP4_Price)
                    line.set_xy2(gTP4_Line, bar_index + offset + 8, gTP4_Price)
                    line.set_color(gTP4_Line, tradeColor if close > gTP4_Price else color.new(tradeColor, 50))
                    if trailingStop > gEntry_Price:
                        line.set_xy1(gTSL_Line, bar_index + offset, trailingStop)
                        line.set_xy2(gTSL_Line, bar_index + offset + 8, trailingStop)
                        line.set_color(gTSL_Line, color.new(tradeColor, 50))
                    label.set_xy(gEntry_Label, bar_index + offset + 4, gEntry_Price)
                    label.set_text(gEntry_Label, string.upper(entryText) + '\n\u2003')
                    label.set_textcolor(gEntry_Label, tradeColor)
                    label.set_xy(gSL_Label, bar_index + offset + 4, gStop_Price)
                    label.set_text(gSL_Label, 'STOP\n\u2003')
                    label.set_textcolor(gSL_Label, color.new(tradeColor, 50))
                    label.set_xy(gTP1_Label, bar_index + offset + 4, gTP1_Price)
                    label.set_text(gTP1_Label, 'TP 1\n\u2003')
                    label.set_textcolor(gTP1_Label, tradeColor if close > gTP1_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP2_Label, bar_index + offset + 4, gTP2_Price)
                    label.set_text(gTP2_Label, 'TP 2\n\u2003')
                    label.set_textcolor(gTP2_Label, tradeColor if close > gTP2_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP3_Label, bar_index + offset + 4, gTP3_Price)
                    label.set_text(gTP3_Label, 'TP 3\n\u2003')
                    label.set_textcolor(gTP3_Label, tradeColor if close > gTP3_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP4_Label, bar_index + offset + 4, gTP4_Price)
                    label.set_text(gTP4_Label, 'TP 4\n\u2003')
                    label.set_textcolor(gTP4_Label, tradeColor if close > gTP4_Price else color.new(tradeColor, 50))
                    if trailingStop > gEntry_Price:
                        label.set_xy(gTSL_Label, bar_index + offset + 4, trailingStop)
                        label.set_text(gTSL_Label, 'STOP\n\u2003')
                        label.set_textcolor(gTSL_Label, color.new(tradeColor, 50))
                    label.set_tooltip(gEntry_Label, string.tostring(gEntry_Price))
                    label.set_tooltip(gSL_Label, string.tostring(gStop_Price))
                    label.set_tooltip(gTP1_Label, string.tostring(gTP1_Price))
                    label.set_tooltip(gTP2_Label, string.tostring(gTP2_Price))
                    label.set_tooltip(gTP3_Label, string.tostring(gTP3_Price))
                    label.set_tooltip(gTP4_Label, string.tostring(gTP4_Price))
                    label.set_tooltip(gTSL_Label, string.tostring(trailingStop))
                if direction == 'S':
                    line.set_xy1(gEntry_Line, bar_index + offset, gEntry_Price)
                    line.set_xy2(gEntry_Line, bar_index + offset + 8, gEntry_Price)
                    line.set_color(gEntry_Line, tradeColor if close < gEntry_Price else color.new(tradeColor, 50))
                    line.set_xy1(gSL_Line, bar_index + offset, gStop_Price)
                    line.set_xy2(gSL_Line, bar_index + offset + 8, gStop_Price)
                    line.set_color(gSL_Line, color.new(tradeColor, 50))
                    line.set_xy1(gTP1_Line, bar_index + offset, gTP1_Price)
                    line.set_xy2(gTP1_Line, bar_index + offset + 8, gTP1_Price)
                    line.set_color(gTP1_Line, tradeColor if close < gTP1_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP2_Line, bar_index + offset, gTP2_Price)
                    line.set_xy2(gTP2_Line, bar_index + offset + 8, gTP2_Price)
                    line.set_color(gTP2_Line, tradeColor if close < gTP2_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP3_Line, bar_index + offset, gTP3_Price)
                    line.set_xy2(gTP3_Line, bar_index + offset + 8, gTP3_Price)
                    line.set_color(gTP3_Line, tradeColor if close < gTP3_Price else color.new(tradeColor, 50))
                    line.set_xy1(gTP4_Line, bar_index + offset, gTP4_Price)
                    line.set_xy2(gTP4_Line, bar_index + offset + 8, gTP4_Price)
                    line.set_color(gTP4_Line, tradeColor if close < gTP4_Price else color.new(tradeColor, 50))
                    if trailingStop < gEntry_Price:
                        line.set_xy1(gTSL_Line, bar_index + offset, trailingStop)
                        line.set_xy2(gTSL_Line, bar_index + offset + 8, trailingStop)
                        line.set_color(gTSL_Line, color.new(tradeColor, 50))
                    label.set_xy(gEntry_Label, bar_index + offset + 4, gEntry_Price)
                    label.set_text(gEntry_Label, string.upper(entryText) + '\n\u2003')
                    label.set_textcolor(gEntry_Label, tradeColor)
                    label.set_xy(gSL_Label, bar_index + offset + 4, gStop_Price)
                    label.set_text(gSL_Label, 'STOP\n\u2003')
                    label.set_textcolor(gSL_Label, color.new(tradeColor, 50))
                    label.set_xy(gTP1_Label, bar_index + offset + 4, gTP1_Price)
                    label.set_text(gTP1_Label, 'TP 1\n\u2003')
                    label.set_textcolor(gTP1_Label, tradeColor if close < gTP1_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP2_Label, bar_index + offset + 4, gTP2_Price)
                    label.set_text(gTP2_Label, 'TP 2\n\u2003')
                    label.set_textcolor(gTP2_Label, tradeColor if close < gTP2_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP3_Label, bar_index + offset + 4, gTP3_Price)
                    label.set_text(gTP3_Label, 'TP 3\n\u2003')
                    label.set_textcolor(gTP3_Label, tradeColor if close < gTP3_Price else color.new(tradeColor, 50))
                    label.set_xy(gTP4_Label, bar_index + offset + 4, gTP4_Price)
                    label.set_text(gTP4_Label, 'TP 4\n\u2003')
                    label.set_textcolor(gTP4_Label, tradeColor if close < gTP4_Price else color.new(tradeColor, 50))
                    if trailingStop < gEntry_Price:
                        label.set_xy(gTSL_Label, bar_index + offset + 4, trailingStop)
                        label.set_text(gTSL_Label, 'STOP\n\u2003')
                        label.set_textcolor(gTSL_Label, color.new(tradeColor, 50))
                    label.set_tooltip(gEntry_Label, string.tostring(gEntry_Price))
                    label.set_tooltip(gSL_Label, string.tostring(gStop_Price))
                    label.set_tooltip(gTP1_Label, string.tostring(gTP1_Price))
                    label.set_tooltip(gTP2_Label, string.tostring(gTP2_Price))
                    label.set_tooltip(gTP3_Label, string.tostring(gTP3_Price))
                    label.set_tooltip(gTP4_Label, string.tostring(gTP4_Price))
                    label.set_tooltip(gTSL_Label, string.tostring(trailingStop))
                f_TP_Hit(direction, tradeColor, trade, TP1_Price, TP1_Hit_Count, TP1_Bars_Count, TP1_Hit, 'TP1', entryText)
                f_TP_Hit(direction, tradeColor, trade, TP2_Price, TP2_Hit_Count, TP2_Bars_Count, TP2_Hit, 'TP2', entryText)
                f_TP_Hit(direction, tradeColor, trade, TP3_Price, TP3_Hit_Count, TP3_Bars_Count, TP3_Hit, 'TP3', entryText)
                f_TP_Hit(direction, tradeColor, trade, TP4_Price, TP4_Hit_Count, TP4_Bars_Count, TP4_Hit, 'TP4', entryText)
                if bullishTrigger:
                    matrix.set(matrix__ren__, trade, Bullish_Price, close)
                    gBullish_Price = matrix.get(matrix__ren__, trade, Bullish_Price)
                    if gBullish_Price < gEntry_Price:
                        matrix.set(matrix__ren__, trade, Bullish_to_Min_Amount, gBullish_Price - minReached)
                    else:
                        matrix.set(matrix__ren__, trade, Bullish_to_Min_Amount, gBullish_Price - trailingStop)
                    matrix.set(matrix__ren__, trade, Bullish_Amount_Sum, matrix.get(matrix__ren__, trade, Bullish_Amount_Sum) + matrix.get(matrix__ren__, trade, Bullish_to_Min_Amount))
                    matrix.set(matrix__ren__, trade, Bullish_Hit_Count, matrix.get(matrix__ren__, trade, Bullish_Hit_Count) + 1)
                    matrix.set(matrix__ren__, trade, Avg_Bullish_Dev, matrix.get(matrix__ren__, trade, Bullish_Amount_Sum) / matrix.get(matrix__ren__, trade, Bullish_Hit_Count))
                    matrix.set(matrix__ren__, trade, Avg_Bullish_RR, matrix.get(matrix__ren__, trade, Avg_Bullish_Dev) / gStop_amount)
                    if Backtest_A == entryText or Backtest_B == entryText:
                        array.unshift(a_newLabel, label.new(bar_index, close, yloc=yloc.belowbar, text='', color=color.new(C_LIME_GREEN, 0), style=label.style_triangleup, textcolor=na, size=size.tiny, tooltip=entryText + ' - ' + string.tostring(close)))
                if bearishTrigger:
                    matrix.set(matrix__ren__, trade, Bearish_Price, close)
                    gBearish_Price = matrix.get(matrix__ren__, trade, Bearish_Price)
                    if gBearish_Price > gEntry_Price:
                        matrix.set(matrix__ren__, trade, Bearish_to_Max_Amount, gBearish_Price - maxReached)
                    else:
                        matrix.set(matrix__ren__, trade, Bearish_to_Max_Amount, gBearish_Price - trailingStop)
                    matrix.set(matrix__ren__, trade, Bearish_Amount_Sum, matrix.get(matrix__ren__, trade, Bearish_Amount_Sum) + matrix.get(matrix__ren__, trade, Bearish_to_Max_Amount))
                    matrix.set(matrix__ren__, trade, Bearish_Hit_Count, matrix.get(matrix__ren__, trade, Bearish_Hit_Count) + 1)
                    matrix.set(matrix__ren__, trade, Avg_Bearish_Dev, matrix.get(matrix__ren__, trade, Bearish_Amount_Sum) / matrix.get(matrix__ren__, trade, Bearish_Hit_Count))
                    matrix.set(matrix__ren__, trade, Avg_Bearish_RR, matrix.get(matrix__ren__, trade, Avg_Bearish_Dev) / gStop_amount)
                    if Backtest_A == entryText or Backtest_B == entryText:
                        array.unshift(a_newLabel, label.new(bar_index, close, yloc=yloc.abovebar, text='', color=color.new(C_PINK, 0), style=label.style_triangledown, textcolor=na, size=size.tiny, tooltip=entryText + ' - ' + string.tostring(close)))
                posLab = label.style_label_upper_left if direction == 'L' else label.style_label_lower_left
                gTP1_Hit = matrix.get(matrix__ren__, trade, TP1_Hit)
                failed = (low < gStop_Price if direction == 'L' else high > gStop_Price) and gTP1_Hit == 0
                if failed:
                    matrix.set(matrix__ren__, trade, Exit_Price, gStop_Price)
                    matrix.set(matrix__ren__, trade, Fail_Hit_Count, matrix.get(matrix__ren__, trade, Fail_Hit_Count) + 1)
                    matrix.set(matrix__ren__, trade, Fail_Bars_Count, matrix.get(matrix__ren__, trade, Fail_Bars_Count) + matrix.get(matrix__ren__, trade, In_Trade_Bar_Count))
                    matrix.set(matrix__ren__, trade, Number_of_Losses, matrix.get(matrix__ren__, trade, Number_of_Losses) + 1)
                    matrix.set(matrix__ren__, trade, PL_Amount, matrix.get(matrix__ren__, trade, Exit_Price) - gEntry_Price)
                    matrix.set(matrix__ren__, trade, Trade_RR_Ratio, matrix.get(matrix__ren__, trade, PL_Amount) / gStop_amount)
                    matrix.set(matrix__ren__, trade, Loss_RR_Ratio_Sum, matrix.get(matrix__ren__, trade, Loss_RR_Ratio_Sum) + matrix.get(matrix__ren__, trade, Trade_RR_Ratio))
                    matrix.set(matrix__ren__, trade, Entry_is_Active, 0)
                    if Backtest_A == entryText or Backtest_B == entryText:
                        array.unshift(a_newLabel, label.new(bar_index, gStop_Price, text='FAIL', color=color.new(tradeColor, 0), style=posLab, textcolor=C_BLACK, size=size.small, tooltip=string.tostring(gStop_Price)))
                trailingStop = matrix.get(matrix__ren__, trade, TSL_Price)
                trailingStopHit = (low < trailingStop and trailingStop > gEntry_Price if direction == 'L' else high > trailingStop and trailingStop < gEntry_Price) and matrix.get(matrix__ren__, trade, TSL_Hit) == 0
                if trailingStopHit:
                    matrix.set(matrix__ren__, trade, Exit_Price, trailingStop)
                    matrix.set(matrix__ren__, trade, TSL_Hit_Count, matrix.get(matrix__ren__, trade, TSL_Hit_Count) + 1)
                    matrix.set(matrix__ren__, trade, TSL_Hit, 1)
                    matrix.set(matrix__ren__, trade, TSL_Bars_Count, matrix.get(matrix__ren__, trade, TSL_Bars_Count) + gIn_Trade_Bar_Count)
                    matrix.set(matrix__ren__, trade, Number_of_Wins, matrix.get(matrix__ren__, trade, Number_of_Wins) + 1)
                    matrix.set(matrix__ren__, trade, PL_Amount, matrix.get(matrix__ren__, trade, Exit_Price) - gEntry_Price)
                    matrix.set(matrix__ren__, trade, Trade_RR_Ratio, matrix.get(matrix__ren__, trade, PL_Amount) / gStop_amount)
                    matrix.set(matrix__ren__, trade, Win_RR_Ratio_Sum, matrix.get(matrix__ren__, trade, Win_RR_Ratio_Sum) + matrix.get(matrix__ren__, trade, Trade_RR_Ratio))
                    matrix.set(matrix__ren__, trade, Entry_is_Active, 0)
                    if Backtest_A == entryText or Backtest_B == entryText:
                        array.unshift(a_newLabel, label.new(bar_index, trailingStop, text='TSL', color=color.new(tradeColor, 0), style=posLab, textcolor=C_BLACK, size=size.small, tooltip=string.tostring(trailingStop)))
                stopHit = (low < gStop_Price if direction == 'L' else high > gStop_Price) and gTP1_Hit == 1
                if stopHit:
                    matrix.set(matrix__ren__, trade, Exit_Price, gStop_Price)
                    matrix.set(matrix__ren__, trade, Number_of_Losses, matrix.get(matrix__ren__, trade, Number_of_Losses) + 1)
                    matrix.set(matrix__ren__, trade, PL_Amount, matrix.get(matrix__ren__, trade, Exit_Price) - gEntry_Price)
                    matrix.set(matrix__ren__, trade, Trade_RR_Ratio, matrix.get(matrix__ren__, trade, PL_Amount) / gStop_amount)
                    matrix.set(matrix__ren__, trade, Loss_RR_Ratio_Sum, matrix.get(matrix__ren__, trade, Loss_RR_Ratio_Sum) + matrix.get(matrix__ren__, trade, Trade_RR_Ratio))
                    matrix.set(matrix__ren__, trade, Entry_is_Active, 0)
                    if Backtest_A == entryText or Backtest_B == entryText:
                        array.unshift(a_newLabel, label.new(bar_index, gStop_Price, text='STOP', color=color.new(tradeColor, 0), style=posLab, textcolor=C_BLACK, size=size.small, tooltip=string.tostring(gStop_Price)))
                box.set_lefttop(array.get(a_priceBox, i), bar_index + offset, gStop_Price)
                box.set_rightbottom(array.get(a_priceBox, i), bar_index + offset + 8, (trailingStop if trailingStop > gTP4_Price else gTP4_Price) if direction == 'L' else trailingStop if trailingStop < gTP4_Price else gTP4_Price)
                box.set_bgcolor(array.get(a_priceBox, i), color.new(tradeColor, 97))
                if array.size(box__ren__) > 0:
                    box.set_rightbottom(array.get(box__ren__, 1), bar_index, gStop_Price if failed else gStop_Price if stopHit else trailingStop if trailingStopHit else close)
                    box.set_top(array.get(box__ren__, 1), gEntry_Price)
                    box.set_rightbottom(array.get(box__ren__, 0), bar_index, (minReached if minReached > gStop_Price else gStop_Price) if direction == 'L' else minReached if minReached < gStop_Price else gStop_Price)
                    box.set_top(array.get(box__ren__, 0), maxReached)
                matrix.set(matrix__ren__, trade, In_Trade_Bar_Count, gIn_Trade_Bar_Count + 1)
            else:
                line.set_xy1(gEntry_Line, na, na)
                label.set_x(gEntry_Label, na)
                line.set_xy1(gSL_Line, na, na)
                label.set_x(gSL_Label, na)
                line.set_xy1(gTP1_Line, na, na)
                label.set_x(gTP1_Label, na)
                line.set_xy1(gTP2_Line, na, na)
                label.set_x(gTP2_Label, na)
                line.set_xy1(gTP3_Line, na, na)
                label.set_x(gTP3_Label, na)
                line.set_xy1(gTP4_Line, na, na)
                label.set_x(gTP4_Label, na)
                line.set_xy1(gTSL_Line, na, na)
                label.set_x(gTSL_Label, na)
                matrix.set(matrix__ren__, trade, Max_Reached, low if direction == 'L' else high)
                matrix.set(matrix__ren__, trade, Min_Reached, high if direction == 'L' else low)
                matrix.set(matrix__ren__, trade, In_Trade_Bar_Count, 0)
                box.set_bgcolor(array.get(a_priceBox, i), color.new(tradeColor, 100))
                if array.size(box__ren__) > 0:
                    box.set_bgcolor(array.get(box__ren__, 1), color.new(C_PINK, 90) if direction == 'L' and gExit_Price < gEntry_Price else color.new(C_PINK, 90) if direction == 'S' and gExit_Price > gEntry_Price else color.new(tradeColor, 90))
            gNumber_of_Wins = matrix.get(matrix__ren__, trade, Number_of_Wins)
            gNumber_of_Losses = matrix.get(matrix__ren__, trade, Number_of_Losses)
            gLoss_Percent = matrix.get(matrix__ren__, trade, Loss_Percent)
            gWin_RR_Ratio_Sum = matrix.get(matrix__ren__, trade, Win_RR_Ratio_Sum)
            gLoss_RR_Ratio_Sum = matrix.get(matrix__ren__, trade, Loss_RR_Ratio_Sum)
            gEntry_Count = matrix.get(matrix__ren__, trade, Entry_Count)
            gFail_Hit_Count = matrix.get(matrix__ren__, trade, Fail_Hit_Count)
            gFail_Bars_Count = matrix.get(matrix__ren__, trade, Fail_Bars_Count)
            gTP1_Hit_Count = matrix.get(matrix__ren__, trade, TP1_Hit_Count)
            gTP2_Hit_Count = matrix.get(matrix__ren__, trade, TP2_Hit_Count)
            gTP3_Hit_Count = matrix.get(matrix__ren__, trade, TP3_Hit_Count)
            gTP4_Hit_Count = matrix.get(matrix__ren__, trade, TP4_Hit_Count)
            gTSL_Hit_Count = matrix.get(matrix__ren__, trade, TSL_Hit_Count)
            gIn_Trade_Bar_Count = matrix.get(matrix__ren__, trade, In_Trade_Bar_Count)
            matrix.set(matrix__ren__, trade, Win_Percent, gNumber_of_Wins / gEntry_Count)
            matrix.set(matrix__ren__, trade, Loss_Percent, gNumber_of_Losses / gEntry_Count)
            gWin_Percent = matrix.get(matrix__ren__, trade, Win_Percent)
            RRT_Win_Percent = math.round(gWin_Percent * 100)
            matrix.set(matrix__ren__, trade, Avg_Win_RR, gWin_RR_Ratio_Sum / gNumber_of_Wins)
            matrix.set(matrix__ren__, trade, Avg_Loss_RR, gLoss_RR_Ratio_Sum / gNumber_of_Losses)
            matrix.set(matrix__ren__, trade, Avg_Risk_Reward, gWin_Percent * matrix.get(matrix__ren__, trade, Avg_Win_RR) - gLoss_Percent * matrix.get(matrix__ren__, trade, Avg_Loss_RR))
            RRT_ARRR = math.round(matrix.get(matrix__ren__, trade, Avg_Risk_Reward), 2)
            matrix.set(matrix__ren__, trade, RRT_Fail_Hit_Percentage, math.round(gFail_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_TP1_Hit_Percentage, math.round(gTP1_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_TP2_Hit_Percentage, math.round(gTP2_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_TP3_Hit_Percentage, math.round(gTP3_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_TP4_Hit_Percentage, math.round(gTP4_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_TSL_Hit_Percentage, math.round(gTSL_Hit_Count / gEntry_Count * 100))
            matrix.set(matrix__ren__, trade, RRT_Avg_Fail_Bars, math.round(gFail_Bars_Count / gFail_Hit_Count))
            matrix.set(matrix__ren__, trade, RRT_Avg_TP1_Bars, math.round(matrix.get(matrix__ren__, trade, TP1_Bars_Count) / gTP1_Hit_Count))
            matrix.set(matrix__ren__, trade, RRT_Avg_TP2_Bars, math.round(matrix.get(matrix__ren__, trade, TP2_Bars_Count) / gTP2_Hit_Count))
            matrix.set(matrix__ren__, trade, RRT_Avg_TP3_Bars, math.round(matrix.get(matrix__ren__, trade, TP3_Bars_Count) / gTP3_Hit_Count))
            matrix.set(matrix__ren__, trade, RRT_Avg_TP4_Bars, math.round(matrix.get(matrix__ren__, trade, TP4_Bars_Count) / gTP4_Hit_Count))
            matrix.set(matrix__ren__, trade, RRT_Avg_TSL_Bars, math.round(matrix.get(matrix__ren__, trade, TSL_Bars_Count) / gTSL_Hit_Count))
            if RRT_Activated:
                table.cell(table_id=Risk_Reward_Table, column=1, row=0, text='#', text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=C_TV_BLACK, tooltip='')
                table.cell(table_id=Risk_Reward_Table, column=2, row=0, text='Fail', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=C_PINK, tooltip='Fail means that this strategy failed to hit at least TP 1 before being stopped out.')
                table.cell(table_id=Risk_Reward_Table, column=5, row=0, text='TP 1', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='Price crossed above/below TP 1')
                table.cell(table_id=Risk_Reward_Table, column=8, row=0, text='TP 2', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='Price crossed above/below TP 2')
                table.cell(table_id=Risk_Reward_Table, column=11, row=0, text='TP 3', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='Price crossed above/below TP 3')
                table.cell(table_id=Risk_Reward_Table, column=14, row=0, text='TP 4', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='Price crossed above/below TP 4')
                table.cell(table_id=Risk_Reward_Table, column=17, row=0, text='TSL', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=C_BLUE, tooltip='Price crossed above/below the Trailing Stop Loss (TSL)')
                table.cell(table_id=Risk_Reward_Table, column=20, row=0, text='▲', text_color=C_LIME_GREEN, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 92), tooltip='Bullish condition Triangle Signal')
                table.cell(table_id=Risk_Reward_Table, column=22, row=0, text='▼', text_color=C_PINK, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 92), tooltip='Bearish condition Triangle Signal')
                table.cell(table_id=Risk_Reward_Table, column=24, row=0, text='Win %', text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=C_TV_BLACK, tooltip='Winning % of this trade type.\n\n* Of Note - If a trade does not FAIL, but still hits the STOP, it was more than likely due to a large price move occuring after entry, which caused you to hit TP1, but not have the TSL rise above your entry price, and then price reversing to hit your STOP. This does not happen very often and your R:R calculations do account for it, however it is important to note if you notice what looks like a small discrepancy in your Win % and/or Fail %...this explains why because it is still a losing trade when this occurs but is not considered a FAIL due to hitting at least 1 profit taking scenario (TP1).')
                table.cell(table_id=Risk_Reward_Table, column=25, row=0, text='ARRR', text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=C_TV_BLACK, tooltip="ARRR - Average Risk:Reward Return of this trade type shown as a multiple of Risk, where a losing trade's risk ratio always equals -1 based on the design of this system.\n\nReturns greater than 1.0 are generally winning systems and less than 1 is a generally losing. For example, if the ARRR was .75, you would expect to only win .75 times (or 75%) the amount you risked on each trade. This is more accurate than profit factor, in my opinion, due to the influence of win/loss percentage and the size of those wins/losses.\n\nFormula:\n\nARRR = (Win % * Avg Winning Trade's R:R Ratio) - (Loss % * Avg Losing Trade's R:R Ratio)")
                table.cell(table_id=Risk_Reward_Table, column=0, row=trade + 1, text=entryText, text_halign=text.align_left, text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(tradeColor, 0), tooltip='Enter Trade criteria or other useful info here')
                table.cell(table_id=Risk_Reward_Table, column=1, row=trade + 1, text=string.tostring(gEntry_Count), text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=color.new(C_TV_BLACK, 0), tooltip='# of entries of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=2, row=trade + 1, text=string.tostring(gFail_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 30), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=3, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Fail_Hit_Percentage)) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 30), tooltip='% of trades it occured on of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=4, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_Fail_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 30), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=5, row=trade + 1, text=string.tostring(gTP1_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=6, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_TP1_Hit_Percentage)) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='% of trades it occured on of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=7, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_TP1_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=8, row=trade + 1, text=string.tostring(gTP2_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=9, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_TP2_Hit_Percentage)) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='% of trades it occured on of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=10, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_TP2_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=11, row=trade + 1, text=string.tostring(gTP3_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=12, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_TP3_Hit_Percentage)) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='% of trades it occured on of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=13, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_TP3_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 15), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=14, row=trade + 1, text=string.tostring(gTP4_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=15, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_TP4_Hit_Percentage)) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='% of trades it occured on of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=16, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_TP4_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 30), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=17, row=trade + 1, text=string.tostring(gTSL_Hit_Count), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_BLUE, 15), tooltip='# total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=18, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, RRT_Avg_TSL_Bars)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_BLUE, 15), tooltip='Avg age when it occured on this trade type')
                table.cell(table_id=Risk_Reward_Table, column=19, row=trade + 1, text=string.tostring(math.round(matrix.get(matrix__ren__, trade, Avg_Win_RR), 2)), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=color.new(C_BLUE, 15), tooltip='Since the TSL is not active until its over your Entry price it can be counted as a winning trade. This number represents the Avg Risk:Reward Ratio for trades of this type that hit your TSL.')
                table.cell(table_id=Risk_Reward_Table, column=20, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, Bullish_Hit_Count)), text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 95), tooltip='- # total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=21, row=trade + 1, text=string.tostring(math.round(matrix.get(matrix__ren__, trade, Avg_Bullish_RR), 2)), text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=color.new(C_LIME_GREEN, 95), tooltip='Risk:Reward Ratio of where the Avg Green Arrow occurs in relation to either the min-reached price when occuring below (above for Short) the Entry Price or the Trailing Stop when occuring above (below for Short)')
                table.cell(table_id=Risk_Reward_Table, column=22, row=trade + 1, text=string.tostring(matrix.get(matrix__ren__, trade, Bearish_Hit_Count)), text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 95), tooltip='- # total hit of this trade type')
                table.cell(table_id=Risk_Reward_Table, column=23, row=trade + 1, text=string.tostring(math.round(matrix.get(matrix__ren__, trade, Avg_Bearish_RR), 2)), text_color=C_LIGHT_GRAY, text_size=RRT_textSize, bgcolor=color.new(C_PINK, 95), tooltip='Risk:Reward Ratio of where the Avg Red Arrow occurs in relation to either the max-reached price when occuring above (below for Long) the Entry Price or the Trailing Stop when occuring below (above for Long)')
                table.cell(table_id=Risk_Reward_Table, column=24, row=trade + 1, text=string.tostring(RRT_Win_Percent) + '%', text_color=C_BLACK, text_size=RRT_textSize, bgcolor=tradeColor, tooltip='Winning % of this trade type.\n\n* Of Note - If a trade does not FAIL, but still hits the STOP, it was more than likely due to a large price move occuring after entry, which caused you to hit TP1, but not have the TSL rise above your entry price, and then price reversing to hit your STOP. This does not happen very often and your R:R calculations do account for it, however it is important to note if you notice what looks like a small discrepancy in your Win % and/or Fail %...this explains why because it is still a losing trade when this occurs but is not considered a FAIL due to hitting at least 1 profit taking scenario (TP1).')
                table.cell(table_id=Risk_Reward_Table, column=25, row=trade + 1, text=string.tostring(RRT_ARRR), text_color=C_BLACK, text_size=RRT_textSize, bgcolor=tradeColor, tooltip="ARRR - Average Risk:Reward Return of this trade type shown as a multiple of Risk, where a losing trade's risk always equals -1 based on the design of this system.\n\nReturns greater than 1.0 are generally winning systems and less than 1 is a generally losing. For example, if the ARRR was .75, you would expect to only win .75 times (or 75%) the amount you risked on each trade. This is more accurate than profit factor, in my opinion, due to the influence of win/loss percentage and the size of those wins/losses.\n\nFormula:\n\nARRR = (Win % * Avg Winning Trade's R:R Ratio) - (Loss % * Avg Losing Trade's R:R Ratio)")
                table.merge_cells(Risk_Reward_Table, 2, 0, 4, 0)
                table.merge_cells(Risk_Reward_Table, 5, 0, 7, 0)
                table.merge_cells(Risk_Reward_Table, 8, 0, 10, 0)
                table.merge_cells(Risk_Reward_Table, 11, 0, 13, 0)
                table.merge_cells(Risk_Reward_Table, 14, 0, 16, 0)
                table.merge_cells(Risk_Reward_Table, 17, 0, 19, 0)
                table.merge_cells(Risk_Reward_Table, 20, 0, 21, 0)
                table.merge_cells(Risk_Reward_Table, 22, 0, 23, 0)
            __block_result_6__ = na
            if TTT_Activated:
                table.cell(table_id=Trade_Tracking_Table, column=0, row=0, text='Trade Name', text_color=C_LIGHT_GRAY, text_size=TTT_textSize, bgcolor=C_TV_BLACK)
                table.cell(table_id=Trade_Tracking_Table, column=1, row=0, text='Side', text_color=C_LIGHT_GRAY, text_size=TTT_textSize, bgcolor=C_TV_BLACK, tooltip='Side of Trade, Long is Green and Short is Red by default')
                table.cell(table_id=Trade_Tracking_Table, column=2, row=0, text='Entry', text_color=C_LIGHT_GRAY, text_size=TTT_textSize, bgcolor=C_TV_BLACK)
                table.cell(table_id=Trade_Tracking_Table, column=3, row=0, text='Stop', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to the Entry Stop's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=4, row=0, text='TP 1', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to TP1's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=5, row=0, text='TP 2', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to TP2's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=6, row=0, text='TP 3', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to TP3's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=7, row=0, text='TP 4', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to TP4's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=8, row=0, text='TSL', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_MEDIUM_GRAY, tooltip="Color brightens as the trade gets closer to TSL's Avg age in RRT")
                table.cell(table_id=Trade_Tracking_Table, column=9, row=0, text='Age', text_color=C_LIGHT_GRAY, text_size=TTT_textSize, bgcolor=C_TV_BLACK, tooltip='Age (# of bars) of this specific trade')
                __block_result_7__ = na
                if gActive:
                    table.cell(table_id=Trade_Tracking_Table, column=0, row=trade + 1, text=entryText, text_color=C_BLACK, text_size=TTT_textSize, bgcolor=tradeColor, text_halign=text.align_left)
                    table.cell(table_id=Trade_Tracking_Table, column=1, row=trade + 1, text='Long' if direction == 'L' else 'Short', text_color=C_BLACK, text_size=TTT_textSize, bgcolor=C_LIME_GREEN if direction == 'L' else C_PINK, tooltip='Side of Trade, Long is Green and Short is Red by default')
                    table.cell(table_id=Trade_Tracking_Table, column=2, row=trade + 1, text=('☑️' + string.tostring(math.round_to_mintick(gEntry_Price)) if close > gEntry_Price else string.tostring(math.round_to_mintick(gEntry_Price))) if direction == 'L' else ('☑️' + string.tostring(math.round_to_mintick(gEntry_Price)) if close < gEntry_Price else string.tostring(math.round_to_mintick(gEntry_Price))) if direction == 'S' else string.tostring(math.round_to_mintick(gEntry_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=tradeColor)
                    table.cell(table_id=Trade_Tracking_Table, column=3, row=trade + 1, text=string.tostring(math.round_to_mintick(gStop_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_Fail_Bars), 0), tooltip="Color brightens as the trade gets closer to the inital Stop's Avg age in RRT")
                    table.cell(table_id=Trade_Tracking_Table, column=4, row=trade + 1, text=('☑️' + string.tostring(math.round_to_mintick(gTP1_Price)) if close > gTP1_Price else string.tostring(math.round_to_mintick(gTP1_Price))) if direction == 'L' else ('☑️' + string.tostring(math.round_to_mintick(gTP1_Price)) if close < gTP1_Price else string.tostring(math.round_to_mintick(gTP1_Price))) if direction == 'S' else string.tostring(math.round_to_mintick(gTP1_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_TP1_Bars), 0), tooltip="Color brightens as the trade gets closer to TP1's Avg age in RRT")
                    table.cell(table_id=Trade_Tracking_Table, column=5, row=trade + 1, text=('☑️' + string.tostring(math.round_to_mintick(gTP2_Price)) if close > gTP2_Price else string.tostring(math.round_to_mintick(gTP2_Price))) if direction == 'L' else ('☑️' + string.tostring(math.round_to_mintick(gTP2_Price)) if close < gTP2_Price else string.tostring(math.round_to_mintick(gTP2_Price))) if direction == 'S' else string.tostring(math.round_to_mintick(gTP2_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_TP2_Bars), 0), tooltip="Color brightens as the trade gets closer to TP2's Avg age in RRT")
                    table.cell(table_id=Trade_Tracking_Table, column=6, row=trade + 1, text=('☑️' + string.tostring(math.round_to_mintick(gTP3_Price)) if close > gTP3_Price else string.tostring(math.round_to_mintick(gTP3_Price))) if direction == 'L' else ('☑️' + string.tostring(math.round_to_mintick(gTP3_Price)) if close < gTP3_Price else string.tostring(math.round_to_mintick(gTP3_Price))) if direction == 'S' else string.tostring(math.round_to_mintick(gTP3_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_TP3_Bars), 0), tooltip="Color brightens as the trade gets closer to TP3's Avg age in RRT")
                    table.cell(table_id=Trade_Tracking_Table, column=7, row=trade + 1, text=('☑️' + string.tostring(math.round_to_mintick(gTP4_Price)) if close > gTP4_Price else string.tostring(math.round_to_mintick(gTP4_Price))) if direction == 'L' else ('☑️' + string.tostring(math.round_to_mintick(gTP4_Price)) if close < gTP4_Price else string.tostring(math.round_to_mintick(gTP4_Price))) if direction == 'S' else string.tostring(math.round_to_mintick(gTP4_Price)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_TP4_Bars), 0), tooltip="Color brightens as the trade gets closer to TP4's Avg age in RRT")
                    table.cell(table_id=Trade_Tracking_Table, column=8, row=trade + 1, text=string.tostring(math.round_to_mintick(trailingStop)), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=f_gradientColor(tradeColor, gIn_Trade_Bar_Count, matrix.get(matrix__ren__, trade, RRT_Avg_TSL_Bars), 0), tooltip="Color brightens as the trade gets closer to TSL's Avg age in RRT")
                    __block_result_7__ = table.cell(table_id=Trade_Tracking_Table, column=9, row=trade + 1, text=string.tostring(gIn_Trade_Bar_Count), text_color=C_BLACK, text_size=TTT_textSize, bgcolor=tradeColor, tooltip='Age (# of bars) of this specific trade')
                else:
                    __block_result_7__ = table.clear(Trade_Tracking_Table, 0, trade + 1, 9, trade + 1)
                __block_result_6__ = __block_result_7__
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    f_Entry('L', L0_Activated, C_BLUE, 2, L0_Entry, L0_Entry_Bullish, L0_Entry_Bearish, L0, L0_SL_Value, L0_TP1_Value, L0_TP2_Value, L0_TP3_Value, L0_TP4_Value, '0. Stochastic', a_newBox_0, 0)
    f_Entry('L', L1_Activated, C_ORANGE, 11, L1_Entry, L1_Entry_Bullish, L1_Entry_Bearish, L1, L1_SL_Value, L1_TP1_Value, L1_TP2_Value, L1_TP3_Value, L1_TP4_Value, '1. 2x MA Cross', a_newBox_1, 1)
    f_Entry('L', L2_Activated, C_LIME_GREEN, 20, L2_Entry, L2_Entry_Bullish, L2_Entry_Bearish, L2, L2_SL_Value, L2_TP1_Value, L2_TP2_Value, L2_TP3_Value, L2_TP4_Value, '2. MACD', a_newBox_2, 2)
    f_Entry('L', L3_Activated, C_PURPLE, 29, L3_Entry, L3_Entry_Bullish, L3_Entry_Bearish, L3, L3_SL_Value, L3_TP1_Value, L3_TP2_Value, L3_TP3_Value, L3_TP4_Value, '3. Bollinger Bands', a_newBox_3, 3)
    f_Entry('L', L4_Activated, C_YELLOW, 38, L4_Entry, L4_Entry_Bullish, L4_Entry_Bearish, L4, L4_SL_Value, L4_TP1_Value, L4_TP2_Value, L4_TP3_Value, L4_TP4_Value, '4. Supertrend', a_newBox_4, 4)
    f_Entry('S', S5_Activated, C_DARK_BLUE, 47, S5_Entry, S5_Entry_Bullish, S5_Entry_Bearish, S5, S5_SL_Value, S5_TP1_Value, S5_TP2_Value, S5_TP3_Value, S5_TP4_Value, '5. Stochastic (Short)', a_newBox_5, 5)
    f_Entry('S', S6_Activated, C_LIME_YELLOW, 56, S6_Entry, S6_Entry_Bullish, S6_Entry_Bearish, S6, S6_SL_Value, S6_TP1_Value, S6_TP2_Value, S6_TP3_Value, S6_TP4_Value, '6. 2x MA Cross (Short)', a_newBox_6, 6)
    f_Entry('S', S7_Activated, C_DARK_PURPLE, 65, S7_Entry, S7_Entry_Bullish, S7_Entry_Bearish, S7, S7_SL_Value, S7_TP1_Value, S7_TP2_Value, S7_TP3_Value, S7_TP4_Value, '7. MACD (Short)', a_newBox_7, 7)
    f_Entry('S', S8_Activated, C_MINT, 74, S8_Entry, S8_Entry_Bullish, S8_Entry_Bearish, S8, S8_SL_Value, S8_TP1_Value, S8_TP2_Value, S8_TP3_Value, S8_TP4_Value, '8. Bollinger Bands (Short)', a_newBox_8, 8)
    f_Entry('S', S9_Activated, C_BURNT_ORANGE, 83, S9_Entry, S9_Entry_Bullish, S9_Entry_Bearish, S9, S9_SL_Value, S9_TP1_Value, S9_TP2_Value, S9_TP3_Value, S9_TP4_Value, '9. Supertrend (Short)', a_newBox_9, 9)
    gL0_TSL_Price = matrix.get(matrix__ren__, L0, TSL_Price)
    gL0_Entry_Price = matrix.get(matrix__ren__, L0, Entry_Price)
    gL1_TSL_Price = matrix.get(matrix__ren__, L1, TSL_Price)
    gL1_Entry_Price = matrix.get(matrix__ren__, L1, Entry_Price)
    gL2_TSL_Price = matrix.get(matrix__ren__, L2, TSL_Price)
    gL2_Entry_Price = matrix.get(matrix__ren__, L2, Entry_Price)
    gL3_TSL_Price = matrix.get(matrix__ren__, L3, TSL_Price)
    gL3_Entry_Price = matrix.get(matrix__ren__, L3, Entry_Price)
    gL4_TSL_Price = matrix.get(matrix__ren__, L4, TSL_Price)
    gL4_Entry_Price = matrix.get(matrix__ren__, L4, Entry_Price)
    gS5_TSL_Price = matrix.get(matrix__ren__, S5, TSL_Price)
    gS5_Entry_Price = matrix.get(matrix__ren__, S5, Entry_Price)
    gS6_TSL_Price = matrix.get(matrix__ren__, S6, TSL_Price)
    gS6_Entry_Price = matrix.get(matrix__ren__, S6, Entry_Price)
    gS7_TSL_Price = matrix.get(matrix__ren__, S7, TSL_Price)
    gS7_Entry_Price = matrix.get(matrix__ren__, S7, Entry_Price)
    gS8_TSL_Price = matrix.get(matrix__ren__, S8, TSL_Price)
    gS8_Entry_Price = matrix.get(matrix__ren__, S8, Entry_Price)
    gS9_TSL_Price = matrix.get(matrix__ren__, S9, TSL_Price)
    gS9_Entry_Price = matrix.get(matrix__ren__, S9, Entry_Price)
    plot(gL0_TSL_Price if (Backtest_A == '0. Stochastic' or Backtest_B == '0. Stochastic') and matrix.get(matrix__ren__, L0, Entry_is_Active) == 1 else na, title='L0 TSL', color=C_BLUE if gL0_TSL_Price > gL0_Entry_Price else color.new(C_BLUE, 50), style=plot.style_linebr, linewidth=2)
    plot(gL1_TSL_Price if (Backtest_A == '1. 2x MA Cross' or Backtest_B == '1. 2x MA Cross') and matrix.get(matrix__ren__, L1, Entry_is_Active) == 1 else na, title='L1 TSL', color=C_ORANGE if gL1_TSL_Price > gL1_Entry_Price else color.new(C_ORANGE, 50), style=plot.style_linebr, linewidth=2)
    plot(gL2_TSL_Price if (Backtest_A == '2. MACD' or Backtest_B == '2. MACD') and matrix.get(matrix__ren__, L2, Entry_is_Active) == 1 else na, title='L2 TSL', color=C_LIME_GREEN if gL2_TSL_Price > gL2_Entry_Price else color.new(C_LIME_GREEN, 50), style=plot.style_linebr, linewidth=2)
    plot(gL3_TSL_Price if (Backtest_A == '3. Bollinger Bands' or Backtest_B == '3. Bollinger Bands') and matrix.get(matrix__ren__, L3, Entry_is_Active) == 1 else na, title='L3 TSL', color=C_PURPLE if gL3_TSL_Price > gL3_Entry_Price else color.new(C_PURPLE, 50), style=plot.style_linebr, linewidth=2)
    plot(gL4_TSL_Price if (Backtest_A == '4. Supertrend' or Backtest_B == '4. Supertrend') and matrix.get(matrix__ren__, L4, Entry_is_Active) == 1 else na, title='L4 TSL', color=C_YELLOW if gL4_TSL_Price > gL4_Entry_Price else color.new(C_YELLOW, 50), style=plot.style_linebr, linewidth=2)
    plot(gS5_TSL_Price if (Backtest_A == '5. Stochastic (Short)' or Backtest_B == '5. Stochastic (Short)') and matrix.get(matrix__ren__, S5, Entry_is_Active) == 1 else na, title='S5 TSL', color=C_DARK_BLUE if gS5_TSL_Price < gS5_Entry_Price else color.new(C_DARK_BLUE, 50), style=plot.style_linebr, linewidth=2)
    plot(gS6_TSL_Price if (Backtest_A == '6. 2x MA Cross (Short)' or Backtest_B == '6. 2x MA Cross (Short)') and matrix.get(matrix__ren__, S6, Entry_is_Active) == 1 else na, title='S6 TSL', color=C_LIME_YELLOW if gS6_TSL_Price < gS6_Entry_Price else color.new(C_LIME_YELLOW, 50), style=plot.style_linebr, linewidth=2)
    plot(gS7_TSL_Price if (Backtest_A == '7. MACD (Short)' or Backtest_B == '7. MACD (Short)') and matrix.get(matrix__ren__, S7, Entry_is_Active) == 1 else na, title='S7 TSL', color=C_DARK_PURPLE if gS7_TSL_Price < gS7_Entry_Price else color.new(C_DARK_PURPLE, 50), style=plot.style_linebr, linewidth=2)
    plot(gS8_TSL_Price if (Backtest_A == '8. Bollinger Bands (Short)' or Backtest_B == '8. Bollinger Bands (Short)') and matrix.get(matrix__ren__, S8, Entry_is_Active) == 1 else na, title='S8 TSL', color=C_MINT if gS8_TSL_Price < gS8_Entry_Price else color.new(C_MINT, 50), style=plot.style_linebr, linewidth=2)
    plot(gS9_TSL_Price if (Backtest_A == '9. Supertrend (Short)' or Backtest_B == '9. Supertrend (Short)') and matrix.get(matrix__ren__, S9, Entry_is_Active) == 1 else na, title='S9 TSL', color=C_BURNT_ORANGE if gS9_TSL_Price < gS9_Entry_Price else color.new(C_BURNT_ORANGE, 50), style=plot.style_linebr, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)