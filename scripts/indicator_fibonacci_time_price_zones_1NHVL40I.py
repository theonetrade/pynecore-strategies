"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, bar_index, box, color, extend, fill, input, line, math, na, nz,
    plot, script, size, string, text, time, timestamp, xloc
)
from pynecore.types import Box, Color, Persistent

ttLev = 'Fibonacci Levels: Configures this Fibonacci level. \n' + ' ■ Toggle visibility, set the level value, customize the color, and adjust line thickness.'
ttPoint = 'A-B-C-D Points: Toggles the visibility of the labels for A, B, and C points on the chart. \n' + ' ■ A and B are user-defined time and price points. \n' + ' ■ C is the calculated end point of the Trend Extension. \n' + ' ■ D is the calculated end point of the Trend Retracement.'
ttFill = 'Fill %: Adjusts the transparency of the fill area. \n' + ' ■ 0% is fully transparent \n ■ 100% is fully opaque.\n'
ttTrend = 'Trendline: Toggles the visibility of the trend line connecting points A and B. \n' + ' ■ Extension: Toggles the visibility of the trend extension line connecting B-C. \n' + ' ■ Retracement: Toggles the visibility of the trend retracement line connecting B-D.'
ttLabel: str = "Labels: Toggles the visibility of the Fibonacci level labels."
ttZone: str = "ZoneType: Toggles the visibility of the Upper, Lower, or Both Fibonacci segments. \n"
ttShape = 'Shape: Selects the structure of Fibonacci plots. \n' + ' ■ Circular: Represents Fibonacci levels as arcs that incorporate both time and price dimensions. \n' + ' ■ Orthogonal: Displays L-shaped patterns combining horizontal and vertical components to reflect time and price relationships. \n' + ' ■ Slope: Aligns Fibonacci levels along the trend line, emphasizing trend direction and momentum. \n' + ' ■ Horizontal: Traditional horizontal lines for Fibonacci levels, focusing solely on price-based relationships. \n\n'
ttA: str = 'Exact Start Time/Price Point'
ttC: str = 'Exact End Time/Price Point'
gL = 'Show\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0' + 'Level\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0' + 'Color\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0' + 'Linewidth'
gS: str = 'Setup'
gV: str = 'Visual Settings'
gLab: str = 'Labels'
TP: str = 'Time/Price'


@script.indicator('Fibonacci Time-Price Zones', shorttitle='Fib Time-Price [xxattaxx]', overlay=True)
def main(
    isEnabled0=input.bool(True, '', group=gL, inline='Level0'),
    levelValue0=input.float(0.236, '', group=gL, inline='Level0'),
    levelColor0=input.color(color.new(color.new('#87CEEB'), 30), '', group=gL, inline='Level0'),
    levelThick0=input.string('▬▬▬', title='', group=gL, inline='Level0', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled1=input.bool(True, '', group=gL, inline='Level1'),
    levelValue1=input.float(0.382, '', group=gL, inline='Level1'),
    levelColor1=input.color(color.new(color.new('#4682B4'), 30), '', group=gL, inline='Level1'),
    levelThick1=input.string('▬▬▬', title='', group=gL, inline='Level1', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled2=input.bool(True, '', group=gL, inline='Level2'),
    levelValue2=input.float(0.5, '', group=gL, inline='Level2'),
    levelColor2=input.color(color.new(color.new('#32CD32'), 30), '', group=gL, inline='Level2'),
    levelThick2=input.string('▬▬▬', title='', group=gL, inline='Level2', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled3=input.bool(True, '', group=gL, inline='Level3'),
    levelValue3=input.float(0.618, '', group=gL, inline='Level3'),
    levelColor3=input.color(color.new(color.new('#FFEB3B'), 30), '', group=gL, inline='Level3'),
    levelThick3=input.string('▬▬▬', title='', group=gL, inline='Level3', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled4=input.bool(True, '', group=gL, inline='Level4'),
    levelValue4=input.float(0.786, '', group=gL, inline='Level4'),
    levelColor4=input.color(color.new(color.new('#FF8C00'), 30), '', group=gL, inline='Level4'),
    levelThick4=input.string('▬▬▬', title='', group=gL, inline='Level4', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled5=input.bool(True, '', group=gL, inline='Level5'),
    levelValue5=input.float(1.0, '', group=gL, inline='Level5'),
    levelColor5=input.color(color.new(color.new('#8B0000'), 30), '', group=gL, inline='Level5'),
    levelThick5=input.string('▬▬▬', title='', group=gL, inline='Level5', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    isEnabled6=input.bool(False, '', group=gL, inline='Level6'),
    levelValue6=input.float(1.236, '', group=gL, inline='Level6'),
    levelColor6=input.color(color.new(color.new('#6A5ACD'), 30), '', group=gL, inline='Level6'),
    levelThick6=input.string('▬▬▬', title='', group=gL, inline='Level6', options=('────', '▬▬▬', '▄▄▄▄'), tooltip=ttLev),
    ZoneType=input.string('Retracement', 'Zone Type', group=gS, inline='s1', options=('Retracement', 'Extension', 'Both'), tooltip=ttZone),
    Shape=input.string('Circular', 'Shape      ', group=gS, inline='s3', options=('Circular', 'Orthogonal ', 'Slope', 'Horizontal'), tooltip=ttShape),
    fillT=input.float(15, 'Fill %  ', maxval=100, minval=0, group=gV, inline='v1', tooltip=ttFill),
    ShowTrend=input.bool(True, 'Trendline     ', group=gV, inline='t1', tooltip=ttTrend),
    colTrend=input.color(color.new(color.aqua, 75), '', group=gV, inline='t1', tooltip=ttTrend),
    ShowExtend=input.bool(False, 'Extension     ', group=gV, inline='t2', tooltip=ttTrend),
    colExtend=input.color(color.new(color.blue, 75), '', group=gV, inline='t2', tooltip=ttTrend),
    ShowRetrace=input.bool(False, 'Retracement', group=gV, inline='t3', tooltip=ttTrend),
    colRetrace=input.color(color.new(color.blue, 75), '', group=gV, inline='t3', tooltip=ttTrend),
    ShowA=input.bool(True, 'A ', group=gLab, inline='p1', tooltip=ttPoint),
    ShowB=input.bool(True, 'B ', group=gLab, inline='p1', tooltip=ttPoint),
    ShowC=input.bool(False, 'C ', group=gLab, inline='p1', tooltip=ttPoint),
    ShowD=input.bool(False, 'D ', group=gLab, inline='p1', tooltip=ttPoint),
    ShowLabels=input.bool(True, 'Fib Levels', group=gLab, inline='l1', tooltip=ttLabel),
    A_Time_=input.time(timestamp('2024-08-12'), '', confirm=True, group=TP, inline='B'),
    A_Price_=input.price(0, '', confirm=True, group=TP, inline='B', tooltip=ttA),
    B_Time_=input.time(timestamp('2024-08-12'), '', confirm=True, group=TP, inline='C'),
    B_Price_=input.price(0, '', confirm=True, group=TP, inline='C', tooltip=ttC)
):
    ttRetr: str = "Retrace: Visibility of the trend retracement line connecting B-D. \n"




    A_Price = B_Price_ if A_Time_ > B_Time_ else A_Price_
    A_Time = B_Time_ if A_Time_ > B_Time_ else A_Time_
    B_Price = A_Price_ if A_Time_ > B_Time_ else B_Price_
    B_Time = A_Time_ if A_Time_ > B_Time_ else B_Time_

    A: float = A_Price
    B: float = B_Price
    A_Index: Persistent[int] = na(int)
    B_Index: Persistent[int] = na(int)
    C_Index: Persistent[int] = na(int)
    D_Index: Persistent[int] = na(int)
    C_Price: Persistent[float] = na(float)
    D_Price: Persistent[float] = na(float)

    if na(A_Index) and time == A_Time:
        A_Index = bar_index

    if na(B_Index) and time == B_Time:
        B_Index = bar_index
        AB_IndexDiff = B_Index - A_Index
        AB_PriceDiff = B_Price - A_Price
        C_Index = B_Index + AB_IndexDiff
        D_Index = B_Index + AB_IndexDiff
        C_Price = B_Price + AB_PriceDiff
        D_Price = B_Price - AB_PriceDiff

    After_A = time >= A_Time
    After_B = time >= B_Time
    Setup = After_A and (not After_B)
    InRange = After_A and bar_index <= C_Index

    Trend: Persistent[int] = 1 if A_Price < B_Price else -1
    U: bool = ZoneType == 'Both' or (Trend == 1 and ZoneType == 'Extension') or (Trend == -1 and ZoneType == 'Retracement')
    L: bool = ZoneType == 'Both' or (Trend == 1 and ZoneType == 'Retracement') or (Trend == -1 and ZoneType == 'Extension')
    T = 100 - fillT
    Fill = fillT > 0 and After_A

    upperArray: Persistent[list[float]] = array.new_float(7)
    lowerArray: Persistent[list[float]] = array.new_float(7)
    upperInitial: Persistent[list[float]] = array.new_float(7)
    lowerInitial: Persistent[list[float]] = array.new_float(7)

    EnablArray: list[bool] = array.from_items(isEnabled0, isEnabled1, isEnabled2, isEnabled3, isEnabled4, isEnabled5, isEnabled6)
    LevlArray: list[float] = array.from_items(levelValue0, levelValue1, levelValue2, levelValue3, levelValue4, levelValue5, levelValue6)
    ColorArray: list[Color] = array.from_items(levelColor0, levelColor1, levelColor2, levelColor3, levelColor4, levelColor5, levelColor6)
    ThickArray: list[str] = array.from_items(levelThick0, levelThick1, levelThick2, levelThick3, levelThick4, levelThick5, levelThick6)

    def f_lw(weight):
        return 1 if weight == '────' else 2 if weight == '▬▬▬' else 3 if weight == '▄▄▄▄' else 1

    def f_fib_radius(base_radius, scale_factor, fib_level):
        return base_radius * fib_level * scale_factor

    def f_calc_y_values(radius, adj_x, start_price, end_price, aspect_ratio):
        x_center = (B_Index - A_Index) * aspect_ratio
        y_offset_sq = radius * radius - math.pow(adj_x - x_center, 2)
        y_offset = math.sqrt(y_offset_sq) if y_offset_sq >= 0 else na
        y_center = B_Price
        y_upper = y_center + y_offset if not na(y_offset) else na
        y_lower = y_center - y_offset if not na(y_offset) else na
        return (y_upper, y_lower)

    def f_calc_fib(start_price, end_price, fib_level, trend, scale_factor):
        price_diff = end_price - start_price
        offset = price_diff * math.sqrt(2) * scale_factor * fib_level
        upper_fib = end_price + offset if trend == 1 else end_price - offset
        lower_fib = end_price - offset if trend == 1 else end_price + offset
        return (upper_fib, lower_fib)

    def f_slope_line(start_index, start_price, slope, index_input):
        delta_index = index_input - start_index
        slope_adj_price = start_price + slope * delta_index
        return slope_adj_price

    def f_text_box(boxtext, col, y_upper, y_lower):
        text_upper: Persistent[Box] = na(Box)
        text_lower: Persistent[Box] = na(Box)
        created: Persistent[bool] = False
        if not created and (not na(y_lower) or not na(y_upper)):
            box.new(bar_index, y_upper, bar_index, y_upper, xloc=xloc.bar_index, border_width=0, text=boxtext, text_color=col, text_size=size.normal, text_halign=text.align_right)
            box.new(bar_index, y_lower, bar_index, y_lower, xloc=xloc.bar_index, border_width=0, text=boxtext, text_color=col, text_size=size.normal, text_halign=text.align_right)
            created = True
        if na(text_lower):
            text_lower = box.new(bar_index, y_lower, bar_index, y_lower, xloc=xloc.bar_index, border_width=0, text='\xa0' + boxtext, text_color=col, text_size=size.normal, text_halign=text.align_left, text_valign=text.align_top)
        if na(text_upper):
            text_upper = box.new(bar_index, y_upper, bar_index, y_upper, xloc=xloc.bar_index, border_width=0, text='\xa0' + boxtext, text_color=col, text_size=size.normal, text_halign=text.align_left, text_valign=text.align_bottom)
        if not na(y_lower):
            box.set_right(text_lower, bar_index)
            box.set_left(text_lower, bar_index)
            box.set_top(text_lower, y_lower)
            box.set_bottom(text_lower, y_lower)
        if not na(y_upper):
            box.set_right(text_upper, bar_index)
            box.set_left(text_upper, bar_index)
            box.set_top(text_upper, y_upper)
            box.set_bottom(text_upper, y_upper)
        if na(y_upper) and na(y_lower) and (not na(text_upper)) and (not na(text_lower)):
            EndBox: Persistent = box.new(bar_index, B_Price, bar_index, B_Price, xloc=xloc.bar_index, border_width=0, text_valign=text.align_center, text=boxtext, text_color=col, text_size=size.normal, text_halign=text.align_left)
            box.delete(text_upper)
            box.delete(text_lower)
        return (text_upper, text_lower)

    scale_factor = math.log(2) if Shape == 'Circular' else math.sqrt(2) / 2
    Slope: float = na if na(A_Index) or na(B_Index) else (B_Price - A_Price) / (B_Index - A_Index)
    s_line = f_slope_line(A_Index, A_Price, Slope, bar_index)
    r_line = f_slope_line(B_Index, B_Price, -Slope, bar_index)

    radius: Persistent[float] = na(float)
    aspect_ratio: Persistent[float] = na(float)
    if time == B_Time:
        radius = 0
        aspect_ratio = 0
        delta_price = B_Price - A_Price
        delta_index = B_Index - A_Index
        aspect_ratio = nz(delta_price / delta_index if delta_index != 0 else 0)
        adj_delta: float = delta_index * aspect_ratio
        radius = math.sqrt(adj_delta * adj_delta + delta_price * delta_price)

    adj_x: float = (bar_index - A_Index) * aspect_ratio

    if time == A_Time:
        for i, level in enumerate(LevlArray):
            isEnabled = array.get(EnablArray, i)

            if isEnabled:
                initialUpper, initialLower = f_calc_fib(A_Price, B_Price, level, Trend, scale_factor)

                array.set(upperInitial, i, initialUpper)
                array.set(lowerInitial, i, initialLower)
            else:
                array.set(upperInitial, i, na)
                array.set(lowerInitial, i, na)

    if After_A:
        for i, level in enumerate(LevlArray):
            isEnabled = array.get(EnablArray, i)
            if isEnabled:
                level_radius = f_fib_radius(radius, scale_factor, level)
                aspect_radius = math.abs(math.round(level_radius / aspect_ratio))
                initial_upper = array.get(upperInitial, i)
                initial_lower = array.get(lowerInitial, i)
                inRadius = bar_index <= aspect_radius + B_Index

                if Setup:
                    upperValue = array.get(upperInitial, i)
                    lowerValue = array.get(lowerInitial, i)
                    array.set(upperArray, i, upperValue)
                    array.set(lowerArray, i, lowerValue)
                else:
                    upperCir, lowerCir = f_calc_y_values(level_radius, adj_x, A_Price, B_Price, aspect_ratio)
                    upperLin = initial_upper if Shape == 'Horizontal' or (Shape == 'Orthogonal ' and inRadius) else na
                    lowerLin = initial_lower if Shape == 'Horizontal' or (Shape == 'Orthogonal ' and inRadius) else na
                    upperSlope = f_slope_line(B_Index, initial_upper, Trend * -Slope, bar_index) if inRadius else na
                    lowerSlope = f_slope_line(B_Index, initial_lower, Trend * Slope, bar_index) if inRadius else na
                    upperValue = upperCir if Shape == 'Circular' else upperLin if Shape != 'Slope' else upperSlope
                    lowerValue = lowerCir if Shape == 'Circular' else lowerLin if Shape != 'Slope' else lowerSlope

                    array.set(upperArray, i, upperValue)
                    array.set(lowerArray, i, lowerValue)

                    if bar_index >= aspect_radius + B_Index and bar_index - 1 < aspect_radius + B_Index and (Shape != 'Circular'):
                        line_color = array.get(ColorArray, i)
                        lw = f_lw(array.get(ThickArray, i))
                        DrawUpper = Trend == 1 and ZoneType != 'Retracement' or (Trend == -1 and ZoneType != 'Extension')
                        DrawLower = Trend == 1 and ZoneType != 'Extension' or (Trend == -1 and ZoneType != 'Retracement')
                        if DrawUpper and Shape == 'Orthogonal ':
                            line.new(bar_index, upperValue, bar_index, B_Price, xloc=xloc.bar_index, color=line_color, width=lw, style=line.style_solid)
                        if DrawLower and Shape == 'Orthogonal ':
                            line.new(bar_index, lowerValue, bar_index, B_Price, xloc=xloc.bar_index, color=line_color, width=lw, style=line.style_solid)
            else:
                array.set(upperArray, i, na)
                array.set(lowerArray, i, na)

        f_text_box(string.tostring(levelValue0) if ShowLabels and isEnabled0 else '', levelColor0, array.get(upperArray, 0) if U else na, array.get(lowerArray, 0) if L else na)
        f_text_box(string.tostring(levelValue1) if ShowLabels and isEnabled1 else '', levelColor1, array.get(upperArray, 1) if U else na, array.get(lowerArray, 1) if L else na)
        f_text_box(string.tostring(levelValue2) if ShowLabels and isEnabled2 else '', levelColor2, array.get(upperArray, 2) if U else na, array.get(lowerArray, 2) if L else na)
        f_text_box(string.tostring(levelValue3) if ShowLabels and isEnabled3 else '', levelColor3, array.get(upperArray, 3) if U else na, array.get(lowerArray, 3) if L else na)
        f_text_box(string.tostring(levelValue4) if ShowLabels and isEnabled4 else '', levelColor4, array.get(upperArray, 4) if U else na, array.get(lowerArray, 4) if L else na)
        f_text_box(string.tostring(levelValue5) if ShowLabels and isEnabled5 else '', levelColor5, array.get(upperArray, 5) if U else na, array.get(lowerArray, 5) if L else na)
        f_text_box(string.tostring(levelValue6) if ShowLabels and isEnabled6 else '', levelColor6, array.get(upperArray, 6) if U else na, array.get(lowerArray, 6) if L else na)

    Mid_U = na if U else B_Price
    Mid_L = na if L else B_Price
    P0_Upper = plot(array.get(upperArray, 0) if isEnabled0 and U and After_A else Mid_U, 'Level 0 Upper', color=levelColor0 if U else na, linewidth=f_lw(levelThick0))
    P1_Upper = plot(array.get(upperArray, 1) if isEnabled1 and U and After_A else Mid_U, 'Level 1 Upper', color=levelColor1 if U else na, linewidth=f_lw(levelThick1))
    P2_Upper = plot(array.get(upperArray, 2) if isEnabled2 and U and After_A else Mid_U, 'Level 2 Upper', color=levelColor2 if U else na, linewidth=f_lw(levelThick2))
    P3_Upper = plot(array.get(upperArray, 3) if isEnabled3 and U and After_A else Mid_U, 'Level 3 Upper', color=levelColor3 if U else na, linewidth=f_lw(levelThick3))
    P4_Upper = plot(array.get(upperArray, 4) if isEnabled4 and U and After_A else Mid_U, 'Level 4 Upper', color=levelColor4 if U else na, linewidth=f_lw(levelThick4))
    P5_Upper = plot(array.get(upperArray, 5) if isEnabled5 and U and After_A else Mid_U, 'Level 5 Upper', color=levelColor5 if U else na, linewidth=f_lw(levelThick5))
    P6_Upper = plot(array.get(upperArray, 6) if isEnabled6 and U and After_A else Mid_U, 'Level 6 Upper', color=levelColor6 if U else na, linewidth=f_lw(levelThick6))
    P0_Mid = plot(B_Price if After_A else na, 'B Price', color=color.new(color.aqua, 100))
    P0_Lower = plot(array.get(lowerArray, 0) if isEnabled0 and L and After_A else Mid_L, 'Level 0 Lower', color=levelColor0 if L else na, linewidth=f_lw(levelThick0))
    P1_Lower = plot(array.get(lowerArray, 1) if isEnabled1 and L and After_A else Mid_L, 'Level 1 Lower', color=levelColor1 if L else na, linewidth=f_lw(levelThick1))
    P2_Lower = plot(array.get(lowerArray, 2) if isEnabled2 and L and After_A else Mid_L, 'Level 2 Lower', color=levelColor2 if L else na, linewidth=f_lw(levelThick2))
    P3_Lower = plot(array.get(lowerArray, 3) if isEnabled3 and L and After_A else Mid_L, 'Level 3 Lower', color=levelColor3 if L else na, linewidth=f_lw(levelThick3))
    P4_Lower = plot(array.get(lowerArray, 4) if isEnabled4 and L and After_A else Mid_L, 'Level 4 Lower', color=levelColor4 if L else na, linewidth=f_lw(levelThick4))
    P5_Lower = plot(array.get(lowerArray, 5) if isEnabled5 and L and After_A else Mid_L, 'Level 5 Lower', color=levelColor5 if L else na, linewidth=f_lw(levelThick5))
    P6_Lower = plot(array.get(lowerArray, 6) if isEnabled6 and L and After_A else Mid_L, 'Level 6 Lower', color=levelColor6 if L else na, linewidth=f_lw(levelThick6))

    fill(P6_Upper, P6_Lower, color=color.new(array.get(ColorArray, 6), T) if Fill and na(array.get(upperArray, 5)) else na)
    fill(P5_Upper, P5_Lower, color=color.new(array.get(ColorArray, 5), T) if Fill and na(array.get(upperArray, 4)) else na)
    fill(P4_Upper, P4_Lower, color=color.new(array.get(ColorArray, 4), T) if Fill and na(array.get(upperArray, 3)) else na)
    fill(P3_Upper, P3_Lower, color=color.new(array.get(ColorArray, 3), T) if Fill and na(array.get(upperArray, 2)) else na)
    fill(P2_Upper, P2_Lower, color=color.new(array.get(ColorArray, 2), T) if Fill and na(array.get(upperArray, 1)) else na)
    fill(P1_Upper, P1_Lower, color=color.new(array.get(ColorArray, 1), T) if Fill and na(array.get(upperArray, 0)) else na)
    fill(P0_Upper, P0_Lower, color=color.new(array.get(ColorArray, 0), T) if Fill and na(array.get(upperArray, 0)) else na)
    fill(P0_Upper, P1_Upper, color=color.new(array.get(ColorArray, 1), T) if Fill and (not na(array.get(upperArray, 1))) else na)
    fill(P1_Upper, P2_Upper, color=color.new(array.get(ColorArray, 2), T) if Fill and (not na(array.get(upperArray, 2))) else na)
    fill(P2_Upper, P3_Upper, color=color.new(array.get(ColorArray, 3), T) if Fill and (not na(array.get(upperArray, 3))) else na)
    fill(P3_Upper, P4_Upper, color=color.new(array.get(ColorArray, 4), T) if Fill and (not na(array.get(upperArray, 4))) else na)
    fill(P4_Upper, P5_Upper, color=color.new(array.get(ColorArray, 5), T) if Fill and (not na(array.get(upperArray, 5))) else na)
    fill(P5_Upper, P6_Upper, color=color.new(array.get(ColorArray, 6), T) if Fill and (not na(array.get(upperArray, 6))) else na)
    fill(P0_Lower, P1_Lower, color=color.new(array.get(ColorArray, 1), T) if Fill and (not na(array.get(lowerArray, 1))) else na)
    fill(P1_Lower, P2_Lower, color=color.new(array.get(ColorArray, 2), T) if Fill and (not na(array.get(lowerArray, 2))) else na)
    fill(P2_Lower, P3_Lower, color=color.new(array.get(ColorArray, 3), T) if Fill and (not na(array.get(lowerArray, 3))) else na)
    fill(P3_Lower, P4_Lower, color=color.new(array.get(ColorArray, 4), T) if Fill and (not na(array.get(lowerArray, 4))) else na)
    fill(P4_Lower, P5_Lower, color=color.new(array.get(ColorArray, 5), T) if Fill and (not na(array.get(lowerArray, 5))) else na)
    fill(P5_Lower, P6_Lower, color=color.new(array.get(ColorArray, 6), T) if Fill and (not na(array.get(lowerArray, 6))) else na)

    UpperValue: float = na(float)
    LowerValue: float = na(float)
    ExtenLine: float = na(float)
    RetraceLine: float = na(float)

    if After_B and Trend == 1:
        UpperValue = math.min(array.max(upperArray, 0), math.max(s_line, r_line))
        LowerValue = math.max(array.min(lowerArray, 0), math.min(s_line, r_line))
        ExtenLine = na if na(UpperValue) or not ShowExtend else s_line
        RetraceLine = na if na(LowerValue) or not ShowRetrace else r_line

    if After_B and Trend == -1:
        UpperValue = math.max(array.max(upperArray, 0), math.max(s_line, r_line))
        LowerValue = math.min(array.min(lowerArray, 0), math.min(s_line, r_line))
        ExtenLine = na if na(LowerValue) or not ShowExtend else s_line
        RetraceLine = na if na(UpperValue) or not ShowRetrace else r_line

    if time == B_Time and ShowTrend:
        line.new(A_Time, A_Price, B_Time, B_Price, xloc=xloc.bar_time, width=4, color=color.new(color.aqua, 60), extend=extend.none, style=line.style_dotted)

    plot(ExtenLine if ShowExtend and bar_index % 10 == 0 and InRange else na, 'Slope Line', color=colExtend, linewidth=2, style=plot.style_circles)
    plot(RetraceLine if ShowRetrace and bar_index % 10 == 0 and InRange else na, 'Retrace Line', color=colRetrace, linewidth=2, style=plot.style_circles)

    if time == A_Time and ShowA:
        box.new(A_Time, A_Price, A_Time, A_Price, xloc=xloc.bar_time, border_width=0, text_valign=text.align_center, border_color=na, text='A', text_color=color.new(color.aqua, 0), text_size=size.large, text_halign=text.align_center)
    if time == B_Time and ShowB:
        box.new(B_Time, B_Price, B_Time, B_Price, xloc=xloc.bar_time, border_width=0, text_valign=text.align_center, border_color=na, text='B', text_color=color.new(color.aqua, 0), text_size=size.large, text_halign=text.align_center)
    if bar_index == C_Index and ShowC:
        box.new(C_Index, C_Price, C_Index, C_Price, xloc=xloc.bar_index, border_width=0, text_valign=text.align_center, border_color=na, text='C', text_color=color.new(color.aqua, 0), text_size=size.large, text_halign=text.align_center)
    if bar_index == D_Index and ShowD:
        box.new(D_Index, D_Price, D_Index, D_Price, xloc=xloc.bar_index, border_width=0, text_valign=text.align_center, border_color=na, text='D', text_color=color.new(color.aqua, 0), text_size=size.large, text_halign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)