"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, bar_index, barmerge, bgcolor, close, color, dayofmonth,
    dayofweek, extend, fill, high, hour, input, label, line, low, math, minute, month, na, plot,
    request, script, size, string, syminfo, ta, time, timeframe, timenow, timestamp, xloc, year,
    yloc
)
from pynecore.types import Label, NA, Persistent, Series


@script.indicator('FXN - Asian Session Range', shorttitle='Asian Session Range', overlay=True, na_bool=True)
def main(
    user_ssth=input.string(title='Start Session Hour (EST)', defval='20', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    user_sstm=input.string(title='Start Session Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    user_esth=input.string(title='End Session Hour (EST)', defval='02', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    user_estm=input.string(title='End Session Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    user_elth=input.string(title='Extend Session Lines Until Hour (EST)', defval='11', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    user_eltm=input.string(title='Extend Session Lines Until Minute (EST)', defval='30', options=('00', '15', '30', '45')),
    user_box_line_color=input.string(title='Asian Range Border Color', defval='blue', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    boxLineWidth=input.int(title='Asian Box Line Width', defval=1, minval=0, maxval=10),
    user_box_line_style=input.string(title='Asian Box Line Style', defval='solid', options=('solid', 'dashed', 'dotted')),
    sessionLineWidth=input.int(title='Session High / Low / Mid Line Width', defval=2, minval=0, maxval=20),
    user_upperlower_line_style=input.string(title='Session High / Low Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    user_midline_color=input.string(title='Middle Range Line Color', defval='orange', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    user_middle_line_style=input.string(title='Middle Range Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    user_text_color=input.string(title='Text Color', defval='blue', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    user_label_size=input.string(title='Text Size', defval='normal', options=('tiny', 'small', 'normal', 'large')),
    show_london_session=input(defval=True, title='Show London Session Box'),
    show_london_session_rng=input(defval=True, title='Show London Session Range Pips'),
    london_ssth=input.string(title='London Start Hour (EST)', defval='03', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    london_sstm=input.string(title='London Start Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    london_esth=input.string(title='London End Hour (EST)', defval='07', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    london_estm=input.string(title='London End Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    luser_box_line_color=input.string(title='London Range Border Color', defval='teal', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    lboxLineWidth=input.int(title='London Box Line Width', defval=1, minval=0, maxval=10),
    luser_box_line_style=input.string(title='London Box Line Style', defval='solid', options=('solid', 'dashed', 'dotted')),
    lsessionLineWidth=input.int(title='Session High / Low / Mid Line Width', defval=2, minval=0, maxval=20),
    luser_upperlower_line_style=input.string(title='Session High / Low Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    luser_midline_color=input.string(title='Middle Range Line Color', defval='teal', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    luser_middle_line_style=input.string(title='Middle Range Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    luser_text_color=input.string(title='Text Color', defval='teal', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    luser_label_size=input.string(title='Text Size', defval='normal', options=('tiny', 'small', 'normal', 'large')),
    show_ny_session=input(defval=True, title='Show New York Session Box'),
    show_ny_session_rng=input(defval=True, title='Show New York Session Range Pips'),
    ny_ssth=input.string(title='New York Start Hour (EST)', defval='08', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    ny_sstm=input.string(title='New York Start Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    ny_esth=input.string(title='New York End Hour (EST)', defval='12', options=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')),
    ny_estm=input.string(title='New York End Minute (EST)', defval='00', options=('00', '15', '30', '45')),
    nuser_box_line_color=input.string(title='New York Range Border Color', defval='silver', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    nboxLineWidth=input.int(title='New York Box Line Width', defval=1, minval=0, maxval=10),
    nuser_box_line_style=input.string(title='New York Box Line Style', defval='solid', options=('solid', 'dashed', 'dotted')),
    nsessionLineWidth=input.int(title='Session High / Low / Mid Line Width', defval=2, minval=0, maxval=20),
    nuser_upperlower_line_style=input.string(title='Session High / Low Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    nuser_midline_color=input.string(title='Middle Range Line Color', defval='silver', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    nuser_middle_line_style=input.string(title='Middle Range Line Style', defval='dotted', options=('solid', 'dashed', 'dotted')),
    nuser_text_color=input.string(title='Text Color', defval='silver', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    nuser_label_size=input.string(title='Text Size', defval='normal', options=('tiny', 'small', 'normal', 'large')),
    showADR=input(defval=True, title='Show Average Daily Range'),
    is_forex_pips=input(title='Display average range as forex pips?', defval=True),
    daily_adr_user=input.int(title='Show ADR for x days', defval=1, minval=0),
    daily_adr_length=input.int(title='ADR Length parameter (Days - default 3 weeks, 21 days)', defval=21, minval=0),
    showPreviousDayHiLo=input(defval=True, title='Show Previous Days High / Low'),
    previousDayHiLoColor=input.string(title='Previous Days Line Color', defval='yellow', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    supportLineWidth=input.int(title='Previous Days Line Width', defval=1, minval=0, maxval=10),
    previousDayHiLoLineStyle=input.string(title='Previous Days Line Style', defval='dashed', options=('solid', 'dashed', 'dotted')),
    showHiLoPriceRange=input(defval=False, title='Show Previous Days Range'),
    showHiLoPriceLabel=input(defval=False, title='Show Line Label (YH / YL)'),
    showLastWeeklyHiLo=input(defval=True, title='Show Last Weeks High / Low'),
    lastWeeklyHiLoColor=input.string(title='Last Week Line Color', defval='orange', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    supportLastWeekLineWidth=input.int(title='Last Week Line Width', defval=1, minval=0, maxval=10),
    lastWeeklyHiLoStyle=input.string(title='Last Week Line Style', defval='dashed', options=('solid', 'dashed', 'dotted')),
    lastWeeklyHiLoShowLabel=input(defval=True, title='Show Line Label (PWH / PWL)'),
    showWeeklyHiLo=input(defval=False, title='Show This Weeks High / Low'),
    weeklyHiLoColor=input.string(title='This Weeks Line Color', defval='olive', options=('aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white', 'yellow')),
    supportWeekLineWidth=input.int(title='This Weeks Line Width', defval=1, minval=0, maxval=10),
    weeklyHiLoStyle=input.string(title='This Weeks Line Style', defval='dashed', options=('solid', 'dashed', 'dotted')),
    weeklyHiLoShowLabel=input(defval=False, title='Show Line Label (WH / WL)'),
    showHiLoTime=input(defval=False, title='Show Hi / Low Time of Day (Always Displays Eastern Standard Time)')
):
    line_color = color.aqua if user_box_line_color == 'aqua' else color.black if user_box_line_color == 'black' else color.blue if user_box_line_color == 'blue' else color.fuchsia if user_box_line_color == 'fuchsia' else color.gray if user_box_line_color == 'gray' else color.green if user_box_line_color == 'green' else color.lime if user_box_line_color == 'lime' else color.maroon if user_box_line_color == 'maroon' else color.navy if user_box_line_color == 'navy' else color.olive if user_box_line_color == 'olive' else color.orange if user_box_line_color == 'orange' else color.purple if user_box_line_color == 'purple' else color.red if user_box_line_color == 'red' else color.silver if user_box_line_color == 'silver' else color.teal if user_box_line_color == 'teal' else color.white if user_box_line_color == 'white' else color.yellow if user_box_line_color == 'yellow' else color.black
    midline_color = color.aqua if user_midline_color == 'aqua' else color.black if user_midline_color == 'black' else color.blue if user_midline_color == 'blue' else color.fuchsia if user_midline_color == 'fuchsia' else color.gray if user_midline_color == 'gray' else color.green if user_midline_color == 'green' else color.lime if user_midline_color == 'lime' else color.maroon if user_midline_color == 'maroon' else color.navy if user_midline_color == 'navy' else color.olive if user_midline_color == 'olive' else color.orange if user_midline_color == 'orange' else color.purple if user_midline_color == 'purple' else color.red if user_midline_color == 'red' else color.silver if user_midline_color == 'silver' else color.teal if user_midline_color == 'teal' else color.white if user_midline_color == 'white' else color.yellow if user_midline_color == 'yellow' else color.black
    text_color = color.aqua if user_text_color == 'aqua' else color.black if user_text_color == 'black' else color.blue if user_text_color == 'blue' else color.fuchsia if user_text_color == 'fuchsia' else color.gray if user_text_color == 'gray' else color.green if user_text_color == 'green' else color.lime if user_text_color == 'lime' else color.maroon if user_text_color == 'maroon' else color.navy if user_text_color == 'navy' else color.olive if user_text_color == 'olive' else color.orange if user_text_color == 'orange' else color.purple if user_text_color == 'purple' else color.red if user_text_color == 'red' else color.silver if user_text_color == 'silver' else color.teal if user_text_color == 'teal' else color.white if user_text_color == 'white' else color.yellow if user_text_color == 'yellow' else color.black
    box_line_style = line.style_solid if user_box_line_style == 'solid' else line.style_dashed if user_box_line_style == 'dashed' else line.style_dotted if user_box_line_style == 'dotted' else line.style_solid
    upperlower_line_style = line.style_solid if user_upperlower_line_style == 'solid' else line.style_dashed if user_upperlower_line_style == 'dashed' else line.style_dotted if user_upperlower_line_style == 'dotted' else line.style_solid
    middle_line_style = line.style_solid if user_middle_line_style == 'solid' else line.style_dashed if user_middle_line_style == 'dashed' else line.style_dotted if user_middle_line_style == 'dotted' else line.style_solid
    labelsize = size.tiny if user_label_size == 'tiny' else size.small if user_label_size == 'small' else size.normal if user_label_size == 'normal' else size.large if user_label_size == 'large' else size.normal
    lline_color = color.aqua if luser_box_line_color == 'aqua' else color.black if luser_box_line_color == 'black' else color.blue if luser_box_line_color == 'blue' else color.fuchsia if luser_box_line_color == 'fuchsia' else color.gray if luser_box_line_color == 'gray' else color.green if luser_box_line_color == 'green' else color.lime if luser_box_line_color == 'lime' else color.maroon if luser_box_line_color == 'maroon' else color.navy if luser_box_line_color == 'navy' else color.olive if luser_box_line_color == 'olive' else color.orange if luser_box_line_color == 'orange' else color.purple if luser_box_line_color == 'purple' else color.red if luser_box_line_color == 'red' else color.silver if luser_box_line_color == 'silver' else color.teal if luser_box_line_color == 'teal' else color.white if luser_box_line_color == 'white' else color.yellow if luser_box_line_color == 'yellow' else color.black
    lmidline_color = color.aqua if luser_midline_color == 'aqua' else color.black if luser_midline_color == 'black' else color.blue if luser_midline_color == 'blue' else color.fuchsia if luser_midline_color == 'fuchsia' else color.gray if luser_midline_color == 'gray' else color.green if luser_midline_color == 'green' else color.lime if luser_midline_color == 'lime' else color.maroon if luser_midline_color == 'maroon' else color.navy if luser_midline_color == 'navy' else color.olive if luser_midline_color == 'olive' else color.orange if luser_midline_color == 'orange' else color.purple if luser_midline_color == 'purple' else color.red if luser_midline_color == 'red' else color.silver if luser_midline_color == 'silver' else color.teal if luser_midline_color == 'teal' else color.white if luser_midline_color == 'white' else color.yellow if luser_midline_color == 'yellow' else color.black
    ltext_color = color.aqua if luser_text_color == 'aqua' else color.black if luser_text_color == 'black' else color.blue if luser_text_color == 'blue' else color.fuchsia if luser_text_color == 'fuchsia' else color.gray if luser_text_color == 'gray' else color.green if luser_text_color == 'green' else color.lime if luser_text_color == 'lime' else color.maroon if luser_text_color == 'maroon' else color.navy if luser_text_color == 'navy' else color.olive if luser_text_color == 'olive' else color.orange if luser_text_color == 'orange' else color.purple if luser_text_color == 'purple' else color.red if luser_text_color == 'red' else color.silver if luser_text_color == 'silver' else color.teal if luser_text_color == 'teal' else color.white if luser_text_color == 'white' else color.yellow if luser_text_color == 'yellow' else color.black
    lbox_line_style = line.style_solid if luser_box_line_style == 'solid' else line.style_dashed if luser_box_line_style == 'dashed' else line.style_dotted if luser_box_line_style == 'dotted' else line.style_solid
    lupperlower_line_style = line.style_solid if luser_upperlower_line_style == 'solid' else line.style_dashed if luser_upperlower_line_style == 'dashed' else line.style_dotted if luser_upperlower_line_style == 'dotted' else line.style_solid
    lmiddle_line_style = line.style_solid if luser_middle_line_style == 'solid' else line.style_dashed if luser_middle_line_style == 'dashed' else line.style_dotted if luser_middle_line_style == 'dotted' else line.style_solid
    llabelsize = size.tiny if luser_label_size == 'tiny' else size.small if luser_label_size == 'small' else size.normal if luser_label_size == 'normal' else size.large if luser_label_size == 'large' else size.normal
    nline_color = color.aqua if nuser_box_line_color == 'aqua' else color.black if nuser_box_line_color == 'black' else color.blue if nuser_box_line_color == 'blue' else color.fuchsia if nuser_box_line_color == 'fuchsia' else color.gray if nuser_box_line_color == 'gray' else color.green if nuser_box_line_color == 'green' else color.lime if nuser_box_line_color == 'lime' else color.maroon if nuser_box_line_color == 'maroon' else color.navy if nuser_box_line_color == 'navy' else color.olive if nuser_box_line_color == 'olive' else color.orange if nuser_box_line_color == 'orange' else color.purple if nuser_box_line_color == 'purple' else color.red if nuser_box_line_color == 'red' else color.silver if nuser_box_line_color == 'silver' else color.teal if nuser_box_line_color == 'teal' else color.white if nuser_box_line_color == 'white' else color.yellow if nuser_box_line_color == 'yellow' else color.black
    nmidline_color = color.aqua if nuser_midline_color == 'aqua' else color.black if nuser_midline_color == 'black' else color.blue if nuser_midline_color == 'blue' else color.fuchsia if nuser_midline_color == 'fuchsia' else color.gray if nuser_midline_color == 'gray' else color.green if nuser_midline_color == 'green' else color.lime if nuser_midline_color == 'lime' else color.maroon if nuser_midline_color == 'maroon' else color.navy if nuser_midline_color == 'navy' else color.olive if nuser_midline_color == 'olive' else color.orange if nuser_midline_color == 'orange' else color.purple if nuser_midline_color == 'purple' else color.red if nuser_midline_color == 'red' else color.silver if nuser_midline_color == 'silver' else color.teal if nuser_midline_color == 'teal' else color.white if nuser_midline_color == 'white' else color.yellow if nuser_midline_color == 'yellow' else color.black
    ntext_color = color.aqua if nuser_text_color == 'aqua' else color.black if nuser_text_color == 'black' else color.blue if nuser_text_color == 'blue' else color.fuchsia if nuser_text_color == 'fuchsia' else color.gray if nuser_text_color == 'gray' else color.green if nuser_text_color == 'green' else color.lime if nuser_text_color == 'lime' else color.maroon if nuser_text_color == 'maroon' else color.navy if nuser_text_color == 'navy' else color.olive if nuser_text_color == 'olive' else color.orange if nuser_text_color == 'orange' else color.purple if nuser_text_color == 'purple' else color.red if nuser_text_color == 'red' else color.silver if nuser_text_color == 'silver' else color.teal if nuser_text_color == 'teal' else color.white if nuser_text_color == 'white' else color.yellow if nuser_text_color == 'yellow' else color.black
    nbox_line_style = line.style_solid if nuser_box_line_style == 'solid' else line.style_dashed if nuser_box_line_style == 'dashed' else line.style_dotted if nuser_box_line_style == 'dotted' else line.style_solid
    nupperlower_line_style = line.style_solid if nuser_upperlower_line_style == 'solid' else line.style_dashed if nuser_upperlower_line_style == 'dashed' else line.style_dotted if nuser_upperlower_line_style == 'dotted' else line.style_solid
    nmiddle_line_style = line.style_solid if nuser_middle_line_style == 'solid' else line.style_dashed if nuser_middle_line_style == 'dashed' else line.style_dotted if nuser_middle_line_style == 'dotted' else line.style_solid
    nlabelsize = size.tiny if nuser_label_size == 'tiny' else size.small if nuser_label_size == 'small' else size.normal if nuser_label_size == 'normal' else size.large if nuser_label_size == 'large' else size.normal
    daily_adr = daily_adr_user
    if dayofweek.sunday:
        daily_adr = daily_adr + 1
    if dayofweek.saturday:
        daily_adr = daily_adr + 1
    lblTP: int = 70
    support_line_color = color.aqua if previousDayHiLoColor == 'aqua' else color.black if previousDayHiLoColor == 'black' else color.blue if previousDayHiLoColor == 'blue' else color.fuchsia if previousDayHiLoColor == 'fuchsia' else color.gray if previousDayHiLoColor == 'gray' else color.green if previousDayHiLoColor == 'green' else color.lime if previousDayHiLoColor == 'lime' else color.maroon if previousDayHiLoColor == 'maroon' else color.navy if previousDayHiLoColor == 'navy' else color.olive if previousDayHiLoColor == 'olive' else color.orange if previousDayHiLoColor == 'orange' else color.purple if previousDayHiLoColor == 'purple' else color.red if previousDayHiLoColor == 'red' else color.silver if previousDayHiLoColor == 'silver' else color.teal if previousDayHiLoColor == 'teal' else color.white if previousDayHiLoColor == 'white' else color.yellow if previousDayHiLoColor == 'yellow' else color.black
    support_line_label_color = color.new(color.aqua, lblTP) if previousDayHiLoColor == 'aqua' else color.new(color.black, lblTP) if previousDayHiLoColor == 'black' else color.new(color.blue, lblTP) if previousDayHiLoColor == 'blue' else color.new(color.fuchsia, lblTP) if previousDayHiLoColor == 'fuchsia' else color.new(color.gray, lblTP) if previousDayHiLoColor == 'gray' else color.new(color.green, lblTP) if previousDayHiLoColor == 'green' else color.new(color.lime, lblTP) if previousDayHiLoColor == 'lime' else color.new(color.maroon, lblTP) if previousDayHiLoColor == 'maroon' else color.new(color.navy, lblTP) if previousDayHiLoColor == 'navy' else color.new(color.olive, lblTP) if previousDayHiLoColor == 'olive' else color.new(color.orange, lblTP) if previousDayHiLoColor == 'orange' else color.new(color.purple, lblTP) if previousDayHiLoColor == 'purple' else color.new(color.red, lblTP) if previousDayHiLoColor == 'red' else color.new(color.silver, lblTP) if previousDayHiLoColor == 'silver' else color.new(color.teal, lblTP) if previousDayHiLoColor == 'teal' else color.new(color.white, lblTP) if previousDayHiLoColor == 'white' else color.new(color.yellow, lblTP) if previousDayHiLoColor == 'yellow' else color.new(color.black, lblTP)
    support_line_style = line.style_solid if previousDayHiLoLineStyle == 'solid' else line.style_dashed if previousDayHiLoLineStyle == 'dashed' else line.style_dotted if previousDayHiLoLineStyle == 'dotted' else line.style_solid
    support_last_week_line_color = color.aqua if lastWeeklyHiLoColor == 'aqua' else color.black if lastWeeklyHiLoColor == 'black' else color.blue if lastWeeklyHiLoColor == 'blue' else color.fuchsia if lastWeeklyHiLoColor == 'fuchsia' else color.gray if lastWeeklyHiLoColor == 'gray' else color.green if lastWeeklyHiLoColor == 'green' else color.lime if lastWeeklyHiLoColor == 'lime' else color.maroon if lastWeeklyHiLoColor == 'maroon' else color.navy if lastWeeklyHiLoColor == 'navy' else color.olive if lastWeeklyHiLoColor == 'olive' else color.orange if lastWeeklyHiLoColor == 'orange' else color.purple if lastWeeklyHiLoColor == 'purple' else color.red if lastWeeklyHiLoColor == 'red' else color.silver if lastWeeklyHiLoColor == 'silver' else color.teal if lastWeeklyHiLoColor == 'teal' else color.white if lastWeeklyHiLoColor == 'white' else color.yellow if lastWeeklyHiLoColor == 'yellow' else color.black
    support_last_week_line_label_color = color.new(color.aqua, lblTP) if lastWeeklyHiLoColor == 'aqua' else color.new(color.black, lblTP) if lastWeeklyHiLoColor == 'black' else color.new(color.blue, lblTP) if lastWeeklyHiLoColor == 'blue' else color.new(color.fuchsia, lblTP) if lastWeeklyHiLoColor == 'fuchsia' else color.new(color.gray, lblTP) if lastWeeklyHiLoColor == 'gray' else color.new(color.green, lblTP) if lastWeeklyHiLoColor == 'green' else color.new(color.lime, lblTP) if lastWeeklyHiLoColor == 'lime' else color.new(color.maroon, lblTP) if lastWeeklyHiLoColor == 'maroon' else color.new(color.navy, lblTP) if lastWeeklyHiLoColor == 'navy' else color.new(color.olive, lblTP) if lastWeeklyHiLoColor == 'olive' else color.new(color.orange, lblTP) if lastWeeklyHiLoColor == 'orange' else color.new(color.purple, lblTP) if lastWeeklyHiLoColor == 'purple' else color.new(color.red, lblTP) if lastWeeklyHiLoColor == 'red' else color.new(color.silver, lblTP) if lastWeeklyHiLoColor == 'silver' else color.new(color.teal, lblTP) if lastWeeklyHiLoColor == 'teal' else color.new(color.white, lblTP) if lastWeeklyHiLoColor == 'white' else color.new(color.yellow, lblTP) if lastWeeklyHiLoColor == 'yellow' else color.new(color.black, lblTP)
    support_last_week_line_style = line.style_solid if lastWeeklyHiLoStyle == 'solid' else line.style_dashed if lastWeeklyHiLoStyle == 'dashed' else line.style_dotted if lastWeeklyHiLoStyle == 'dotted' else line.style_solid
    wlineTP: int = 30
    support_week_line_color = color.new(color.aqua, wlineTP) if weeklyHiLoColor == 'aqua' else color.new(color.black, wlineTP) if weeklyHiLoColor == 'black' else color.new(color.blue, wlineTP) if weeklyHiLoColor == 'blue' else color.new(color.fuchsia, wlineTP) if weeklyHiLoColor == 'fuchsia' else color.new(color.gray, wlineTP) if weeklyHiLoColor == 'gray' else color.new(color.green, wlineTP) if weeklyHiLoColor == 'green' else color.new(color.lime, wlineTP) if weeklyHiLoColor == 'lime' else color.new(color.maroon, wlineTP) if weeklyHiLoColor == 'maroon' else color.new(color.navy, wlineTP) if weeklyHiLoColor == 'navy' else color.new(color.olive, wlineTP) if weeklyHiLoColor == 'olive' else color.new(color.orange, wlineTP) if weeklyHiLoColor == 'orange' else color.new(color.purple, wlineTP) if weeklyHiLoColor == 'purple' else color.new(color.red, wlineTP) if weeklyHiLoColor == 'red' else color.new(color.silver, wlineTP) if weeklyHiLoColor == 'silver' else color.new(color.teal, wlineTP) if weeklyHiLoColor == 'teal' else color.new(color.white, wlineTP) if weeklyHiLoColor == 'white' else color.new(color.yellow, wlineTP) if weeklyHiLoColor == 'yellow' else color.new(color.black, wlineTP)
    support_week_line_style = line.style_solid if weeklyHiLoStyle == 'solid' else line.style_dashed if weeklyHiLoStyle == 'dashed' else line.style_dotted if weeklyHiLoStyle == 'dotted' else line.style_solid
    chart_time_period_int = 1 if timeframe.period == '1' else 3 if timeframe.period == '3' else 5 if timeframe.period == '5' else 15 if timeframe.period == '15' else 30 if timeframe.period == '30' else 45 if timeframe.period == '45' else 15
    tickerExchangeOffset: int = 4
    start_session_hour_int: int = 0
    end_session_hour_int: int = 0
    end_line_hour_int: int = 0
    start_session_hour_int = 0 if user_ssth == '00' else 1 if user_ssth == '01' else 2 if user_ssth == '02' else 3 if user_ssth == '03' else 4 if user_ssth == '04' else 5 if user_ssth == '05' else 6 if user_ssth == '06' else 7 if user_ssth == '07' else 8 if user_ssth == '08' else 9 if user_ssth == '09' else 10 if user_ssth == '10' else 11 if user_ssth == '11' else 12 if user_ssth == '12' else 13 if user_ssth == '13' else 14 if user_ssth == '14' else 15 if user_ssth == '15' else 16 if user_ssth == '16' else 17 if user_ssth == '17' else 18 if user_ssth == '18' else 19 if user_ssth == '19' else 20 if user_ssth == '20' else 21 if user_ssth == '21' else 22 if user_ssth == '22' else 23 if user_ssth == '23' else 0
    start_session_minute_int = 0 if user_sstm == '00' else 15 if user_sstm == '15' else 30 if user_sstm == '30' else 45 if user_sstm == '45' else 0
    end_session_hour_int = 0 if user_esth == '00' else 1 if user_esth == '01' else 2 if user_esth == '02' else 3 if user_esth == '03' else 4 if user_esth == '04' else 5 if user_esth == '05' else 6 if user_esth == '06' else 7 if user_esth == '07' else 8 if user_esth == '08' else 9 if user_esth == '09' else 10 if user_esth == '10' else 11 if user_esth == '11' else 12 if user_esth == '12' else 13 if user_esth == '13' else 14 if user_esth == '14' else 15 if user_esth == '15' else 16 if user_esth == '16' else 17 if user_esth == '17' else 18 if user_esth == '18' else 19 if user_esth == '19' else 20 if user_esth == '20' else 21 if user_esth == '21' else 22 if user_esth == '22' else 23 if user_esth == '23' else 0
    end_session_minute_int = 0 if user_estm == '00' else 15 if user_estm == '15' else 30 if user_estm == '30' else 45 if user_estm == '45' else 0
    end_line_hour_int = 0 if user_elth == '00' else 1 if user_elth == '01' else 2 if user_elth == '02' else 3 if user_elth == '03' else 4 if user_elth == '04' else 5 if user_elth == '05' else 6 if user_elth == '06' else 7 if user_elth == '07' else 8 if user_elth == '08' else 9 if user_elth == '09' else 10 if user_elth == '10' else 11 if user_elth == '11' else 12 if user_elth == '12' else 13 if user_elth == '13' else 14 if user_elth == '14' else 15 if user_elth == '15' else 16 if user_elth == '16' else 17 if user_elth == '17' else 18 if user_elth == '18' else 19 if user_elth == '19' else 20 if user_elth == '20' else 21 if user_elth == '21' else 22 if user_elth == '22' else 23 if user_elth == '23' else 0
    end_line_minute_int = 0 if user_eltm == '00' else 15 if user_eltm == '15' else 30 if user_eltm == '30' else 45 if user_eltm == '45' else 0
    end_session_minute_int_offset = end_session_minute_int + chart_time_period_int
    london_start_session_hour_int: int = 0
    london_end_session_hour_int: int = 0
    london_start_session_hour_int = 0 if london_ssth == '00' else 1 if london_ssth == '01' else 2 if london_ssth == '02' else 3 if london_ssth == '03' else 4 if london_ssth == '04' else 5 if london_ssth == '05' else 6 if london_ssth == '06' else 7 if london_ssth == '07' else 8 if london_ssth == '08' else 9 if london_ssth == '09' else 10 if london_ssth == '10' else 11 if london_ssth == '11' else 12 if london_ssth == '12' else 13 if london_ssth == '13' else 14 if london_ssth == '14' else 15 if london_ssth == '15' else 16 if london_ssth == '16' else 17 if london_ssth == '17' else 18 if london_ssth == '18' else 19 if london_ssth == '19' else 20 if london_ssth == '20' else 21 if london_ssth == '21' else 22 if london_ssth == '22' else 23 if london_ssth == '23' else 0
    london_start_session_minute_int = 0 if london_sstm == '00' else 15 if london_sstm == '15' else 30 if london_sstm == '30' else 45 if london_sstm == '45' else 0
    london_end_session_hour_int = 0 if london_esth == '00' else 1 if london_esth == '01' else 2 if london_esth == '02' else 3 if london_esth == '03' else 4 if london_esth == '04' else 5 if london_esth == '05' else 6 if london_esth == '06' else 7 if london_esth == '07' else 8 if london_esth == '08' else 9 if london_esth == '09' else 10 if london_esth == '10' else 11 if london_esth == '11' else 12 if london_esth == '12' else 13 if london_esth == '13' else 14 if london_esth == '14' else 15 if london_esth == '15' else 16 if london_esth == '16' else 17 if london_esth == '17' else 18 if london_esth == '18' else 19 if london_esth == '19' else 20 if london_esth == '20' else 21 if london_esth == '21' else 22 if london_esth == '22' else 23 if london_esth == '23' else 0
    london_end_session_minute_int = 0 if london_estm == '00' else 15 if london_estm == '15' else 30 if london_estm == '30' else 45 if london_estm == '45' else 0
    london_end_session_minute_int_offset = london_end_session_minute_int + chart_time_period_int
    def isValidResolution():
        return 0 if timeframe.isdwm == True or timeframe.period == '120' or timeframe.period == '240' or (timeframe.period == '180') or (timeframe.period == '360') else 1

    ny_start_session_hour_int: int = 0
    ny_end_session_hour_int: int = 0
    ny_start_session_hour_int = 0 if ny_ssth == '00' else 1 if ny_ssth == '01' else 2 if ny_ssth == '02' else 3 if ny_ssth == '03' else 4 if ny_ssth == '04' else 5 if ny_ssth == '05' else 6 if ny_ssth == '06' else 7 if ny_ssth == '07' else 8 if ny_ssth == '08' else 9 if ny_ssth == '09' else 10 if ny_ssth == '10' else 11 if ny_ssth == '11' else 12 if ny_ssth == '12' else 13 if ny_ssth == '13' else 14 if ny_ssth == '14' else 15 if ny_ssth == '15' else 16 if ny_ssth == '16' else 17 if ny_ssth == '17' else 18 if ny_ssth == '18' else 19 if ny_ssth == '19' else 20 if ny_ssth == '20' else 21 if ny_ssth == '21' else 22 if ny_ssth == '22' else 23 if ny_ssth == '23' else 0
    ny_start_session_minute_int = 0 if ny_sstm == '00' else 15 if ny_sstm == '15' else 30 if ny_sstm == '30' else 45 if ny_sstm == '45' else 0
    ny_end_session_hour_int = 0 if ny_esth == '00' else 1 if ny_esth == '01' else 2 if ny_esth == '02' else 3 if ny_esth == '03' else 4 if ny_esth == '04' else 5 if ny_esth == '05' else 6 if ny_esth == '06' else 7 if ny_esth == '07' else 8 if ny_esth == '08' else 9 if ny_esth == '09' else 10 if ny_esth == '10' else 11 if ny_esth == '11' else 12 if ny_esth == '12' else 13 if ny_esth == '13' else 14 if ny_esth == '14' else 15 if ny_esth == '15' else 16 if ny_esth == '16' else 17 if ny_esth == '17' else 18 if ny_esth == '18' else 19 if ny_esth == '19' else 20 if ny_esth == '20' else 21 if ny_esth == '21' else 22 if ny_esth == '22' else 23 if ny_esth == '23' else 0
    ny_end_session_minute_int = 0 if ny_estm == '00' else 15 if ny_estm == '15' else 30 if ny_estm == '30' else 45 if ny_estm == '45' else 0
    ny_end_session_minute_int_offset = ny_end_session_minute_int + chart_time_period_int
    start_support_hour_int: int = 17
    start_support_minute_int: int = 0
    end_support_hour_int: int = 17
    end_support_minute_int: int = 0
    if syminfo.timezone == 'Etc/UTC':
        start_session_hour_int = start_session_hour_int + tickerExchangeOffset
        end_session_hour_int = end_session_hour_int + tickerExchangeOffset
        end_line_hour_int = end_line_hour_int + tickerExchangeOffset
        london_start_session_hour_int = london_start_session_hour_int + tickerExchangeOffset
        london_end_session_hour_int = london_end_session_hour_int + tickerExchangeOffset
        ny_start_session_hour_int = ny_start_session_hour_int + tickerExchangeOffset
        ny_end_session_hour_int = ny_end_session_hour_int + tickerExchangeOffset
        start_support_hour_int = start_support_hour_int + tickerExchangeOffset
        end_support_hour_int = end_support_hour_int + tickerExchangeOffset
        if start_session_hour_int >= 24:
            if start_session_hour_int == 24:
                user_ssth = '00'
            else:
                user_ssth = '0' + string.tostring(start_session_hour_int - 24)
        else:
            if start_session_hour_int < 10:
                user_ssth = '0' + string.tostring(start_session_hour_int)
            else:
                user_ssth = string.tostring(start_session_hour_int)
        if end_session_hour_int >= 24:
            if end_session_hour_int == 24:
                user_esth = '00'
            else:
                user_esth = '0' + string.tostring(end_session_hour_int - 24)
        else:
            if end_session_hour_int < 10:
                user_esth = '0' + string.tostring(end_session_hour_int)
            else:
                user_esth = string.tostring(end_session_hour_int)
        if london_start_session_hour_int >= 24:
            if london_start_session_hour_int == 24:
                london_ssth = '00'
            else:
                london_ssth = '0' + string.tostring(london_start_session_hour_int - 24)
        else:
            if london_start_session_hour_int < 10:
                london_ssth = '0' + string.tostring(london_start_session_hour_int)
            else:
                london_ssth = string.tostring(london_start_session_hour_int)
        if london_end_session_hour_int >= 24:
            if london_end_session_hour_int == 24:
                london_esth = '00'
            else:
                london_esth = '0' + string.tostring(london_end_session_hour_int - 24)
        else:
            if london_end_session_hour_int < 10:
                london_esth = '0' + string.tostring(london_end_session_hour_int)
            else:
                london_esth = string.tostring(london_end_session_hour_int)
        if ny_start_session_hour_int >= 24:
            if ny_start_session_hour_int == 24:
                ny_ssth = '00'
            else:
                ny_ssth = '0' + string.tostring(ny_start_session_hour_int - 24)
        else:
            if ny_start_session_hour_int < 10:
                ny_ssth = '0' + string.tostring(ny_start_session_hour_int)
            else:
                ny_ssth = string.tostring(ny_start_session_hour_int)
        if ny_end_session_hour_int >= 24:
            if ny_end_session_hour_int == 24:
                ny_esth = '00'
            else:
                ny_esth = '0' + string.tostring(ny_end_session_hour_int - 24)
        else:
            if ny_end_session_hour_int < 10:
                ny_esth = '0' + string.tostring(ny_end_session_hour_int)
            else:
                ny_esth = string.tostring(ny_end_session_hour_int)
    trd_ses = user_esth + user_estm + '-' + ny_esth + ny_estm
    rth_ses: str = ''
    london_rth_ses: str = ''
    ny_rth_ses: str = ''
    rth_fill_ses: str = ''
    london_rth_fill_ses: str = ''
    ny_rth_fill_ses: str = ''
    rth_ses = user_ssth + user_sstm + '-' + user_esth + user_estm
    london_rth_ses = london_ssth + london_sstm + '-' + london_esth + london_estm
    ny_rth_ses = ny_ssth + ny_sstm + '-' + ny_esth + ny_estm
    if (timeframe.period == '5' or timeframe.period == '3' or timeframe.period == '1') and end_session_minute_int == 0:
        rth_fill_ses = user_ssth + user_sstm + '-' + user_esth + '0' + string.tostring(end_session_minute_int_offset)
    else:
        rth_fill_ses = user_ssth + user_sstm + '-' + user_esth + string.tostring(end_session_minute_int_offset)
    if (timeframe.period == '5' or timeframe.period == '3' or timeframe.period == '1') and london_end_session_minute_int == 0:
        london_rth_fill_ses = london_ssth + london_sstm + '-' + london_esth + '0' + string.tostring(london_end_session_minute_int_offset)
    else:
        london_rth_fill_ses = london_ssth + london_sstm + '-' + london_esth + string.tostring(london_end_session_minute_int_offset)
    if (timeframe.period == '5' or timeframe.period == '3' or timeframe.period == '1') and ny_end_session_minute_int == 0:
        ny_rth_fill_ses = ny_ssth + ny_sstm + '-' + ny_esth + '0' + string.tostring(ny_end_session_minute_int_offset)
    else:
        ny_rth_fill_ses = ny_ssth + ny_sstm + '-' + ny_esth + string.tostring(ny_end_session_minute_int_offset)
    def open_bar(ses):
        t: Series = time('D', ses if ses == '' else ses + ('23456' if string.endswith(ses, ':') else '' if string.contains(ses, ':') else ':23456'))
        return na(t[1]) and (not na(t)) or t[1] < t

    def is_open(ses):
        return not na(time(timeframe.period, ses if ses == '' else ses + ('23456' if string.endswith(ses, ':') else '' if string.contains(ses, ':') else ':23456')))

    def is_end_day():
        return True if hour == 16 and minute == 45 else False

    def is_new_day():
        return True if syminfo.timezone == 'Etc/UTC' and hour == 0 and (minute == 0) else True if syminfo.timezone != 'Etc/UTC' and hour == 20 and (minute == 0) else False

    def get_label_offset(session__ren__):
        return time[180] if timeframe.period == '1' else time[60] if timeframe.period == '3' else time[36] if timeframe.period == '5' else time[12] if timeframe.period == '15' else time[3] if timeframe.period == '60' else time[12]

    def is_new_day_switch_period():
        return True if hour >= 20 and minute == 0 and (hour <= 23) and (minute <= 59) else False

    def timerange(res, sess):
        return 1 if not na(time(res, sess if sess == '' else sess + ('23456' if string.endswith(sess, ':') else '' if string.contains(sess, ':') else ':23456'))) else 0

    def adr(length):
        range_2: Series = high - low
        return ta.sma(range_2[1], length)

    def to_pips(val):
        return math.round(val / syminfo.mintick / 10) if is_forex_pips else math.round(val / syminfo.mintick)

    day_adr = request.security(syminfo.tickerid, 'D', adr(daily_adr_length), lookahead=barmerge.lookahead_on)
    one_day = 1000 * 60 * 60 * 24
    srcHi = high
    srcLo = low
    hi: Persistent[float] = 1e-09
    lo: Persistent[float] = 100000000000.0
    startTimeDelta = 24 - start_session_hour_int + 1
    endTimeDelta = 24 - start_session_hour_int + 1
    def startTimeAlignment():
        return 0 if hour + startTimeDelta > 24 else 1

    isStartTimeAlignment = startTimeAlignment()
    def endBoxTimeAlignment():
        return 1 if start_session_hour_int >= end_session_hour_int and hour + startTimeDelta > 24 else 0 if start_session_hour_int >= end_session_hour_int and hour + startTimeDelta <= 24 else 0 if start_session_hour_int < end_session_hour_int and hour + startTimeDelta > 24 else -1

    isEndBoxTimeAlignment = endBoxTimeAlignment()
    def endTimeAlignment():
        return 1 if start_session_hour_int >= end_session_hour_int and hour + startTimeDelta > 24 else 0 if start_session_hour_int >= end_session_hour_int and hour + startTimeDelta <= 24 else 1 if start_session_hour_int < end_session_hour_int and isEndBoxTimeAlignment == 0 else -1 if start_session_hour_int < end_session_hour_int and hour + endTimeDelta > 24 else 0

    isEndTimeAlignment = endTimeAlignment()
    FromDate = timestamp(year, month, dayofmonth - isStartTimeAlignment, start_session_hour_int, start_session_minute_int)
    ToDate = timestamp(year, month, dayofmonth + isEndBoxTimeAlignment, end_session_hour_int, end_session_minute_int) - chart_time_period_int
    LineFromDate = timestamp(year, month, dayofmonth + isEndBoxTimeAlignment, end_session_hour_int, end_session_minute_int) - chart_time_period_int
    LineToDate = timestamp(year, month, dayofmonth + isEndTimeAlignment, end_line_hour_int, end_line_minute_int)
    hi = srcHi if cast_bool(ta.change(FromDate)) else math.max(srcHi, hi)
    lo = srcLo if cast_bool(ta.change(FromDate)) else math.min(srcLo, lo)
    inSession: Series = not na(time(timeframe.period, rth_ses if rth_ses == '' else rth_ses + ('23456' if string.endswith(rth_ses, ':') else '' if string.contains(rth_ses, ':') else ':23456')))
    rth_open_bar = open_bar(rth_ses)
    rth_is_open = is_open(rth_ses)
    rth_low: Series = NA(float)
    rth_low = (low if rth_open_bar else math.min(rth_low[1], low)) if rth_is_open else rth_low[1]
    rth_high: Series = NA(float)
    rth_high = (high if rth_open_bar else math.max(rth_high[1], high)) if rth_is_open else rth_high[1]
    rth_mid = math.avg(rth_low, rth_high)
    range_1: float = na(float)
    trl: Series = line.new(FromDate, rth_low, ToDate, rth_low, xloc=xloc.bar_time, color=line_color, style=box_line_style, width=boxLineWidth)
    line.delete(trl[1])
    trh: Series = line.new(FromDate, rth_high, ToDate, rth_high, xloc=xloc.bar_time, color=line_color, style=box_line_style, width=boxLineWidth)
    line.delete(trh[1])
    trm: Series = line.new(FromDate, rth_mid, ToDate, rth_mid, xloc=xloc.bar_time, color=midline_color, style=middle_line_style, width=sessionLineWidth)
    line.delete(trm[1])
    startBox: Series = line.new(FromDate, rth_high, FromDate, rth_low, extend=extend.none, xloc=xloc.bar_time, color=line_color, style=box_line_style, width=boxLineWidth)
    line.delete(startBox[1])
    endBox: Series = line.new(ToDate, rth_high, ToDate, rth_low, extend=extend.none, xloc=xloc.bar_time, color=line_color, style=box_line_style, width=boxLineWidth)
    line.delete(endBox[1])
    tl: Series = line.new(LineFromDate, rth_low, LineToDate, rth_low, xloc=xloc.bar_time, color=line_color, style=upperlower_line_style, width=sessionLineWidth)
    line.delete(tl[1])
    th: Series = line.new(LineFromDate, rth_high, LineToDate, rth_high, xloc=xloc.bar_time, color=line_color, style=upperlower_line_style, width=sessionLineWidth)
    line.delete(th[1])
    tm: Series = line.new(LineFromDate, rth_mid, LineToDate, rth_mid, xloc=xloc.bar_time, color=midline_color, style=middle_line_style, width=sessionLineWidth)
    line.delete(tm[1])
    highRes = rth_high
    lowRes = rth_low
    lineColor = color.new(color.white, 100)
    isValidResolution_1 = isValidResolution()
    openRangeHigh = plot(highRes if timerange(timeframe.period, rth_fill_ses) > 0 and isValidResolution_1 else na, color=lineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_2 = isValidResolution()
    openRangeLow = plot(lowRes if timerange(timeframe.period, rth_fill_ses) > 0 and isValidResolution_2 else na, color=lineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_3 = isValidResolution()
    bgcolor(color.silver if time(timeframe.period, rth_ses if rth_ses == '' else rth_ses + ('23456' if string.endswith(rth_ses, ':') else '' if string.contains(rth_ses, ':') else ':23456')) > 0 and isValidResolution_3 else na, title='Asian Session Background Color')
    fill(openRangeHigh, openRangeLow, color=color.new(color.blue if isValidResolution() else na, 90), title='Fill Asian Range Color')
    isValidResolution_4 = isValidResolution()
    if not inSession and inSession[1] and isValidResolution_4:
        range_1 = (rth_high[1] - rth_low[1]) / syminfo.mintick / 10
        labelTime = get_label_offset(inSession)
        if (timeframe.isintraday or timeframe.isdaily) and showADR and (timenow - time < one_day * daily_adr):
            label.new(labelTime, rth_low[1], 'A = ' + string.tostring(range_1) + '\nADR = ' + string.tostring(to_pips(day_adr)), xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_label_up, text_color, labelsize)
        else:
            label.new(labelTime, rth_low[1], 'A = ' + string.tostring(range_1), xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_label_up, text_color, labelsize)
    london_hi: Persistent[float] = 1e-09
    london_lo: Persistent[float] = 100000000000.0
    londonStartTimeDelta = 24 - london_start_session_hour_int + 1
    londonEndTimeDelta = 24 - london_end_session_hour_int + 1
    def startLondonTimeAlignment():
        return 0 if hour + londonStartTimeDelta > 24 else 1

    isLondonStartTimeAlignment = startLondonTimeAlignment()
    def endLondonTimeAlignment():
        return 0 if hour >= london_start_session_hour_int and isLondonStartTimeAlignment == 0 else 1

    isLondonEndTimeAlignment = endLondonTimeAlignment()
    london_range: float = na(float)
    LondonFromDate = timestamp(year, month, dayofmonth - isLondonStartTimeAlignment, london_start_session_hour_int, london_start_session_minute_int)
    LondonToDate = timestamp(year, month, dayofmonth - isLondonEndTimeAlignment, london_end_session_hour_int, london_end_session_minute_int) - chart_time_period_int
    london_hi = srcHi if cast_bool(ta.change(LondonFromDate)) else math.max(srcHi, london_hi)
    london_lo = srcLo if cast_bool(ta.change(LondonFromDate)) else math.min(srcLo, london_lo)
    inLondonSession: Series = not na(time(timeframe.period, london_rth_ses if london_rth_ses == '' else london_rth_ses + ('23456' if string.endswith(london_rth_ses, ':') else '' if string.contains(london_rth_ses, ':') else ':23456')))
    london_rth_open_bar = open_bar(london_rth_ses)
    london_rth_is_open = is_open(london_rth_ses)
    london_rth_low: Series = NA(float)
    london_rth_low = (low if london_rth_open_bar else math.min(london_rth_low[1], low)) if london_rth_is_open else london_rth_low[1]
    london_rth_high: Series = NA(float)
    london_rth_high = (high if london_rth_open_bar else math.max(london_rth_high[1], high)) if london_rth_is_open else london_rth_high[1]
    london_rth_mid = math.avg(london_rth_low, london_rth_high)
    isValidResolution_5 = isValidResolution()
    if show_london_session and isValidResolution_5:
        ltrl: Series = line.new(LondonFromDate, london_rth_low, LondonToDate, london_rth_low, xloc=xloc.bar_time, color=lline_color, style=lbox_line_style, width=lboxLineWidth)
        line.delete(ltrl[1])
        ltrh: Series = line.new(LondonFromDate, london_rth_high, LondonToDate, london_rth_high, xloc=xloc.bar_time, color=lline_color, style=lbox_line_style, width=lboxLineWidth)
        line.delete(ltrh[1])
        ltrm: Series = line.new(LondonFromDate, london_rth_mid, LondonToDate, london_rth_mid, xloc=xloc.bar_time, color=lmidline_color, style=lmiddle_line_style, width=lsessionLineWidth)
        line.delete(ltrm[1])
        londonStartBox: Series = line.new(LondonFromDate, london_rth_high, LondonFromDate, london_rth_low, extend=extend.none, xloc=xloc.bar_time, color=lline_color, style=lbox_line_style, width=lboxLineWidth)
        line.delete(londonStartBox[1])
        londonEndBox: Series = line.new(LondonToDate, london_rth_high, LondonToDate, london_rth_low, extend=extend.none, xloc=xloc.bar_time, color=lline_color, style=lbox_line_style, width=lboxLineWidth)
        line.delete(londonEndBox[1])
    londonHighRes = london_rth_high
    londonLowRes = london_rth_low
    LondonLineColor = color.new(color.white, 100)
    isValidResolution_6 = isValidResolution()
    londonOpenRangeHigh = plot(londonHighRes if timerange(timeframe.period, london_rth_fill_ses) > 0 and show_london_session and isValidResolution_6 else na, color=LondonLineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_7 = isValidResolution()
    londonOpenRangeLow = plot(londonLowRes if timerange(timeframe.period, london_rth_fill_ses) > 0 and show_london_session and isValidResolution_7 else na, color=LondonLineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_8 = isValidResolution()
    bgcolor(color.silver if time(timeframe.period, london_rth_fill_ses if london_rth_fill_ses == '' else london_rth_fill_ses + ('23456' if string.endswith(london_rth_fill_ses, ':') else '' if string.contains(london_rth_fill_ses, ':') else ':23456')) > 0 and show_london_session and isValidResolution_8 else na, title='London Session Background Color')
    isValidResolution_9 = isValidResolution()
    fill(londonOpenRangeHigh, londonOpenRangeLow, color=color.new(color.teal if show_london_session and isValidResolution_9 else na, 90), title='Fill London Range Color')
    isValidResolution_10 = isValidResolution()
    if show_london_session_rng and (not inLondonSession) and inLondonSession[1] and isValidResolution_10:
        london_range = (london_rth_high[1] - london_rth_low[1]) / syminfo.mintick / 10
        londonLabelTime = get_label_offset(inLondonSession)
        label.new(londonLabelTime, london_rth_low[1], 'L = ' + string.tostring(london_range), xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_label_up, ltext_color, llabelsize)
    ny_hi: Persistent[float] = 1e-09
    ny_lo: Persistent[float] = 100000000000.0
    nyStartTimeDelta = 24 - ny_start_session_hour_int + 1
    nyEndTimeDelta = 24 - ny_end_session_hour_int + 1
    def startNyTimeAlignment():
        return 0 if hour + nyStartTimeDelta > 24 else 1

    isNyStartTimeAlignment = startNyTimeAlignment()
    def endNyTimeAlignment():
        return 0 if hour >= ny_start_session_hour_int and isNyStartTimeAlignment == 0 else 1

    isNyEndTimeAlignment = endNyTimeAlignment()
    ny_range: float = na(float)
    NyFromDate = timestamp(year, month, dayofmonth - isNyStartTimeAlignment, ny_start_session_hour_int, ny_start_session_minute_int)
    NyToDate = timestamp(year, month, dayofmonth - isNyEndTimeAlignment, ny_end_session_hour_int, ny_end_session_minute_int) - chart_time_period_int
    ny_hi = srcHi if cast_bool(ta.change(NyFromDate)) else math.max(srcHi, ny_hi)
    ny_lo = srcLo if cast_bool(ta.change(NyFromDate)) else math.min(srcLo, ny_lo)
    inNySession: Series = not na(time(timeframe.period, ny_rth_ses if ny_rth_ses == '' else ny_rth_ses + ('23456' if string.endswith(ny_rth_ses, ':') else '' if string.contains(ny_rth_ses, ':') else ':23456')))
    ny_rth_open_bar = open_bar(ny_rth_ses)
    ny_rth_is_open = is_open(ny_rth_ses)
    ny_rth_low: Series = NA(float)
    ny_rth_low = (low if ny_rth_open_bar else math.min(ny_rth_low[1], low)) if ny_rth_is_open else ny_rth_low[1]
    ny_rth_high: Series = NA(float)
    ny_rth_high = (high if ny_rth_open_bar else math.max(ny_rth_high[1], high)) if ny_rth_is_open else ny_rth_high[1]
    ny_rth_mid = math.avg(ny_rth_low, ny_rth_high)
    isValidResolution_11 = isValidResolution()
    if show_ny_session and isValidResolution_11:
        ntrl: Series = line.new(NyFromDate, ny_rth_low, NyToDate, ny_rth_low, xloc=xloc.bar_time, color=nline_color, style=nbox_line_style, width=nboxLineWidth)
        line.delete(ntrl[1])
        ntrh: Series = line.new(NyFromDate, ny_rth_high, NyToDate, ny_rth_high, xloc=xloc.bar_time, color=nline_color, style=nbox_line_style, width=nboxLineWidth)
        line.delete(ntrh[1])
        ntrm: Series = line.new(NyFromDate, ny_rth_mid, NyToDate, ny_rth_mid, xloc=xloc.bar_time, color=nmidline_color, style=nmiddle_line_style, width=nsessionLineWidth)
        line.delete(ntrm[1])
        nyStartBox: Series = line.new(NyFromDate, ny_rth_high, NyFromDate, ny_rth_low, extend=extend.none, xloc=xloc.bar_time, color=nline_color, style=nbox_line_style, width=nboxLineWidth)
        line.delete(nyStartBox[1])
        nyEndBox: Series = line.new(NyToDate, ny_rth_high, NyToDate, ny_rth_low, extend=extend.none, xloc=xloc.bar_time, color=nline_color, style=nbox_line_style, width=nboxLineWidth)
        line.delete(nyEndBox[1])
    nyHighRes = ny_rth_high
    nyLowRes = ny_rth_low
    NyLineColor = color.new(color.white, 100)
    isValidResolution_12 = isValidResolution()
    nyOpenRangeHigh = plot(nyHighRes if timerange(timeframe.period, ny_rth_fill_ses) > 0 and show_ny_session and isValidResolution_12 else na, color=NyLineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_13 = isValidResolution()
    nyOpenRangeLow = plot(nyLowRes if timerange(timeframe.period, ny_rth_fill_ses) > 0 and show_ny_session and isValidResolution_13 else na, color=NyLineColor, style=plot.style_line, linewidth=math.max(1, 0), show_last=5, editable=False)
    isValidResolution_14 = isValidResolution()
    bgcolor(color.silver if time(timeframe.period, ny_rth_fill_ses if ny_rth_fill_ses == '' else ny_rth_fill_ses + ('23456' if string.endswith(ny_rth_fill_ses, ':') else '' if string.contains(ny_rth_fill_ses, ':') else ':23456')) > 0 and show_ny_session and isValidResolution_14 else na, title='New York Session Background Color')
    isValidResolution_15 = isValidResolution()
    fill(nyOpenRangeHigh, nyOpenRangeLow, color=color.new(color.silver if show_ny_session and isValidResolution_15 else na, 90), title='Fill New York Range Color')
    isValidResolution_16 = isValidResolution()
    if show_ny_session_rng and (not inNySession) and inNySession[1] and isValidResolution_16:
        ny_range = (ny_rth_high[1] - ny_rth_low[1]) / syminfo.mintick / 10
        nyLabelTime = get_label_offset(inNySession)
        label.new(nyLabelTime, ny_rth_low[1], 'N = ' + string.tostring(ny_range), xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_label_up, ntext_color, nlabelsize)
    def getData(r, s):
        return request.security(syminfo.tickerid, r, s, barmerge.gaps_off, barmerge.lookahead_on)

    pdh = getData('D', high[1])
    pdl = getData('D', low[1])
    wh = getData('1W', high)
    wl = getData('1W', low)
    lwh = getData('1W', high[1])
    lwl = getData('1W', low[1])
    pdh_label_price: float = na(float)
    pdl_label_price: float = na(float)
    checkSwitch: int = 1
    if is_new_day_switch_period():
        pdh_label_price = getData('D', high[1])
        pdl_label_price = getData('D', low[1])
        0
    else:
        pdh_label_price = getData('D', high)
        pdl_label_price = getData('D', low)
        1
    supportStartTimeDelta = 24 - start_session_hour_int + 1
    supportEndTimeDelta = 24 - start_session_hour_int + 1
    def supportStartTimeAlignment():
        return 0 if hour + supportStartTimeDelta > 24 else 1

    isSupportStartTimeAlignment = supportStartTimeAlignment()
    def supportEndTimeAlignment():
        return 1 if hour + supportEndTimeDelta > 24 else 0

    isSupportEndTimeAlignment = supportEndTimeAlignment()
    SupportFromStartWeekDate = timestamp(year, month, dayofmonth - isSupportStartTimeAlignment, start_support_hour_int, start_support_minute_int)
    SupportFromDate = timestamp(year, month, dayofmonth - isSupportStartTimeAlignment, start_support_hour_int, start_support_minute_int)
    SupportToDate = timestamp(year, month, dayofmonth + isSupportEndTimeAlignment, end_support_hour_int, end_support_minute_int) - chart_time_period_int
    isValidResolution_17 = isValidResolution()
    if showPreviousDayHiLo and isValidResolution_17:
        yesterdayHighLine: Series = line.new(SupportFromDate, pdh, SupportToDate, pdh, xloc=xloc.bar_time, extend=extend.none, color=support_line_color, style=support_line_style, width=supportLineWidth)
        line.delete(yesterdayHighLine[1])
        yesterdayLowLine: Series = line.new(SupportFromDate, pdl, SupportToDate, pdl, xloc=xloc.bar_time, extend=extend.none, color=support_line_color, style=support_line_style, width=supportLineWidth)
        line.delete(yesterdayLowLine[1])
        pdCheckIsNewDay = is_new_day()
        if showHiLoPriceRange and pdCheckIsNewDay:
            if showHiLoPriceLabel:
                pdHi_label: Series[Label] = label.new(time - (time - time[1]) * 15, pdh_label_price, 'YH (' + string.tostring((pdh_label_price - pdl_label_price) / syminfo.mintick / 10) + ')', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_line_label_color, nlabelsize)
                label.delete(pdHi_label[1])
                pdLow_label: Series[Label] = label.new(time - (time - time[1]) * 14, pdl_label_price, 'YL', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_line_label_color, nlabelsize)
                label.delete(pdLow_label[1])
            else:
                pdHi_label: Series[Label] = label.new(time - (time - time[1]) * 15, pdh_label_price, string.tostring((pdh_label_price - pdl_label_price) / syminfo.mintick / 10), xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_line_label_color, nlabelsize)
                label.delete(pdHi_label[1])
        if showHiLoPriceLabel and (not showHiLoPriceRange) and pdCheckIsNewDay:
            pdHi_label: Series[Label] = label.new(time - (time - time[1]) * 14, pdh_label_price, 'YH', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_line_label_color, nlabelsize)
            label.delete(pdHi_label[1])
            pdLow_label: Series[Label] = label.new(time - (time - time[1]) * 14, pdl_label_price, 'YL', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_line_label_color, nlabelsize)
            label.delete(pdLow_label[1])
    isValidResolution_18 = isValidResolution()
    if showWeeklyHiLo and isValidResolution_18:
        weekHighLine: Series = line.new(SupportFromStartWeekDate, wh, SupportToDate, wh, xloc=xloc.bar_time, extend=extend.none, color=support_week_line_color, style=support_line_style, width=supportLineWidth)
        line.delete(weekHighLine[1])
        weekLowLine: Series = line.new(SupportFromStartWeekDate, wl, SupportToDate, wl, xloc=xloc.bar_time, extend=extend.none, color=support_week_line_color, style=support_line_style, width=supportLineWidth)
        line.delete(weekLowLine[1])
        is_new_day_1 = is_new_day()
        if weeklyHiLoShowLabel and is_new_day_1:
            wkHi_label: Series[Label] = label.new(time - (time - time[1]) * 14, wh, 'WH', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_week_line_color, nlabelsize)
            label.delete(wkHi_label[1])
            wkLow_label: Series[Label] = label.new(time - (time - time[1]) * 14, wl, 'WL', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_week_line_color, nlabelsize)
            label.delete(wkLow_label[1])
    isValidResolution_19 = isValidResolution()
    if showLastWeeklyHiLo and isValidResolution_19:
        weekLastHighLine: Series = line.new(SupportFromStartWeekDate, lwh, SupportToDate, lwh, xloc=xloc.bar_time, extend=extend.none, color=support_last_week_line_color, style=support_last_week_line_style, width=supportLastWeekLineWidth)
        line.delete(weekLastHighLine[1])
        weekLastLowLine: Series = line.new(SupportFromStartWeekDate, lwl, SupportToDate, lwl, xloc=xloc.bar_time, extend=extend.none, color=support_last_week_line_color, style=support_last_week_line_style, width=supportLastWeekLineWidth)
        line.delete(weekLastLowLine[1])
        is_new_day_1 = is_new_day()
        if lastWeeklyHiLoShowLabel and is_new_day_1:
            lwkHi_label: Series[Label] = label.new(time - (time - time[1]) * 14, lwh, 'PWH', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_last_week_line_label_color, nlabelsize)
            label.delete(lwkHi_label[1])
            lwkLow_label: Series[Label] = label.new(time - (time - time[1]) * 14, lwl, 'PWL', xloc.bar_time, yloc.price, color.new(color.black, 100), label.style_none, support_last_week_line_label_color, nlabelsize)
            label.delete(lwkLow_label[1])
    endOfDay = is_end_day()
    highOfDayHour: Persistent[float] = 1e-09
    highOfDayMinute: Persistent[float] = 1e-09
    lowOfDayHour: Persistent[float] = 1e-09
    lowOfDayMinute: Persistent[float] = 1e-09
    lookbackLength: int = 95
    hb = ta.highestbars(lookbackLength)
    highBarIndex = -hb
    highBarTime = time[highBarIndex]
    highBarHour = hour[highBarIndex]
    highBarMinute = minute[highBarIndex]
    lb = ta.lowestbars(lookbackLength)
    lowBarIndex = -lb
    lowBarTime = time[lowBarIndex]
    lowBarHour = hour[lowBarIndex]
    lowBarMinute = minute[lowBarIndex]
    isValidResolution_20 = isValidResolution()
    if showHiLoTime and isValidResolution_20 and endOfDay:
        highOfDayHour__00000242__ = highBarHour
        lowOfDayHour__00000242__ = lowBarHour
        label.new(bar_index[10], high[highBarIndex], 'HOD: ' + string.tostring(highOfDayHour__00000242__) + ':' + string.tostring(highBarMinute), style=label.style_none, textcolor=color.silver)
        label.new(bar_index[10], low[lowBarIndex], 'LOD: ' + string.tostring(lowOfDayHour__00000242__) + ':' + string.tostring(lowBarMinute), style=label.style_none, textcolor=color.silver)
        ta.valuewhen(not na(highOfDayHour__00000242__), highOfDayHour__00000242__, 0)
    inTradableSession = not na(time(timeframe.period, trd_ses if trd_ses == '' else trd_ses + ('23456' if string.endswith(trd_ses, ':') else '' if string.contains(trd_ses, ':') else ':23456')))
    isCloseBelow: bool = False
    isCloseAbove: bool = False
    if inTradableSession and close[1] >= rth_low and (close < rth_low):
        isCloseBelow = True
    if inTradableSession and close[1] <= rth_high and (close > rth_high):
        isCloseAbove = True
    alertcondition(isCloseBelow or isCloseAbove, title='Asian Range Break', message='Price has closed outside the Asian Session Range.')
    def f_print(_txt):
        _lbl: Persistent = NA(Label)
        label.delete(_lbl)
        _lbl = label.new(time + (time - time[1]) * 3, high, _txt, xloc.bar_time, yloc.price, size=size.large)
        return _lbl


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
