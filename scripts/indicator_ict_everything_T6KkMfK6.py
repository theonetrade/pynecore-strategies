"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, barmerge, barstate, box, close, color, dayofmonth, dayofweek,
    extend, high, hour, input, label, line, linefill, location, low, math, minute, month, na, open,
    plotchar, position, request, script, size, string, syminfo, ta, table, text, time, timeframe,
    timenow, timestamp, weekofyear, xloc, year
)
from pynecore.types import Box, Color, Label, Line, Persistent, PersistentSeries, Series, Table


@script.indicator('ICT Everything @coldbrewrosh', overlay=True, max_lines_count=500, max_labels_count=5, max_boxes_count=500)
def main(
    TZI=input.string(defval='UTC -5', title='Timezone Selection', options=('UTC -10', 'UTC -7', 'UTC -6', 'UTC -5', 'UTC -4', 'UTC -3', 'UTC +0', 'UTC +1', 'UTC +2', 'UTC +3', 'UTC +3:30', 'UTC +4', 'UTC +5', 'UTC +5:30', 'UTC +6', 'UTC +7', 'UTC +8', 'UTC +9', 'UTC +9:30', 'UTC +10', 'UTC +10:30', 'UTC +11', 'UTC +13', 'UTC +13:45'), tooltip='Select the Timezone. ( Shifts Chart Elements )', group='Global Settings'),
    inputMaxInterval=input.int(31, title='Hide Indicator Above Specified Minutes', tooltip='Above 30Min, Chart Will Become Messy & Unreadable', group='Global Settings'),
    ShowTSO=input.bool(True, title='Show Today\'s Session Only', group='Session Options', tooltip='Hide Historical Sessions'),
    ShowTWO=input.bool(True, title='Show Current Week\'s Sessions Only', group='Session Options', tooltip='Show All Sessions from the current week'),
    SL4W=input.bool(True, title='Show Last 4 Week Sessions', group='Session Options', tooltip='Show All Sessions from Last Four Weeks \nShould Disable Current Week Session to Work'),
    ShowSFill=input.bool(False, title='Show Session Highlighting', group='Session Options', tooltip='Highlights Session from Top of the Chart to Bottom'),
    ShowMOPL=input.bool(title='Midnight Historical Price Lines', defval=False, group='Historical Lines', tooltip='Shows Historical Midnight Price Lines'),
    MOLHist=input.bool(title='Midnight Historical Vertical Lines', defval=True, group='Historical Lines', tooltip='Shows Historical Midnight Vertical Lines'),
    ShowPrev=input.bool(False, title='Misc. Historical Price Lines', group='Historical Lines', tooltip='Makes Chart Cluttered, Use For Backtesting Only'),
    ShowLondon=input.bool(True, '', inline='LONDON', group='Sessions', tooltip='01:00 to 05:00'),
    ShowNY=input.bool(True, '', inline='NY', group='Sessions', tooltip='07:00 to 10:00'),
    ShowLC=input.bool(True, '', inline='LC', group='Sessions', tooltip='10:00 to 12:00'),
    ShowPM=input.bool(True, '', inline='PM', group='Sessions', tooltip='13:00 to 16:00'),
    ShowAsian=input.bool(False, '', inline='ASIA2', group='Sessions', tooltip='20:00 to 00:00'),
    ShowFreeSesh=input.bool(False, '', inline='FREE', group='Sessions', tooltip='Custom Session'),
    txt2=input.string('LONDON', title='', inline='LONDON', group='Sessions'),
    txt3=input.string('NEW YORK', title='', inline='NY', group='Sessions'),
    txt4=input.string('LDN CLOSE', title='', inline='LC', group='Sessions'),
    txt5=input.string('AFTERNOON', title='', inline='PM', group='Sessions'),
    txt6=input.string('ASIA', title='', inline='ASIA2', group='Sessions'),
    txt9=input.string('FREE SESH', title='', inline='FREE', group='Sessions'),
    LDNsesh=input.session('0200-0500:1234567', '', inline='LONDON', group='Sessions'),
    NYsesh=input.session('0700-1000:1234567', '', inline='NY', group='Sessions'),
    LCsesh=input.session('1000-1200:1234567', '', inline='LC', group='Sessions'),
    PMsesh=input.session('1300-1600:1234567', '', inline='PM', group='Sessions'),
    ASIA2sesh=input.session('2000-2359:1234567', '', inline='ASIA2', group='Sessions'),
    FreeSesh=input.session('0000-0000:1234567', '', inline='FREE', group='Sessions'),
    LSFC=input.color(color.new(color.new('#787B86'), 90), '', inline='LONDON', group='Sessions'),
    NYSFC=input.color(color.new(color.new('#787B86'), 90), '', inline='NY', group='Sessions'),
    LCSFC=input.color(color.new(color.new('#787B86'), 90), '', inline='LC', group='Sessions'),
    PMSFC=input.color(color.new(color.new('#787B86'), 90), '', inline='PM', group='Sessions'),
    ASFC=input.color(color.new(color.new('#787B86'), 90), '', inline='ASIA2', group='Sessions'),
    FSFC=input.color(color.new(color.new('#787B86'), 90), '', inline='FREE', group='Sessions'),
    ShowMOP=input.bool(title='', defval=True, inline='MOP', group='Vertical Lines', tooltip='00:00 AM'),
    txt12=input.string('MIDNIGHT', title='', inline='MOP', group='Vertical Lines'),
    ShowLOP=input.bool(title='', defval=False, inline='LOP', group='Vertical Lines', tooltip='03:00 AM'),
    txt14=input.string('LONDON', title='', inline='LOP', group='Vertical Lines'),
    ShowNYOP=input.bool(title='', defval=True, inline='NYOP', group='Vertical Lines', tooltip='08:30 AM'),
    txt15=input.string('NEW YORK', title='', inline='NYOP', group='Vertical Lines'),
    ShowEOP=input.bool(title='', defval=False, inline='EOP', group='Vertical Lines', tooltip='09:30 AM'),
    txt16=input.string('EQUITIES', title='', inline='EOP', group='Vertical Lines'),
    MOPColor=input.color(color.new(color.new('#787B86'), 0), '', inline='MOP', group='Vertical Lines'),
    LOPColor=input.color(color.rgb(0, 128, 128, 60), '', inline='LOP', group='Vertical Lines'),
    NYOPColor=input.color(color.rgb(0, 128, 128, 60), '', inline='NYOP', group='Vertical Lines'),
    EOPColor=input.color(color.rgb(0, 128, 128, 60), '', inline='EOP', group='Vertical Lines'),
    Midnight_Open_LS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='MOP', group='Vertical Lines'),
    london_Open_LS=input.string('Solid', '', options=('Solid', 'Dashed', 'Dotted'), inline='LOP', group='Vertical Lines'),
    NY_Open_LS=input.string('Solid', '', options=('Solid', 'Dashed', 'Dotted'), inline='NYOP', group='Vertical Lines'),
    Equities_Open_LS=input.string('Solid', '', options=('Solid', 'Dashed', 'Dotted'), inline='EOP', group='Vertical Lines'),
    Midnight_Open_LW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='MOP', group='Vertical Lines'),
    London_Open_LW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='LOP', group='Vertical Lines'),
    NY_Open_LW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='NYOP', group='Vertical Lines'),
    Equities_Open_LW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='EOP', group='Vertical Lines'),
    ShowMOPP=input.bool(title='', defval=True, inline='MOPP', group='Opening Price Lines', tooltip='00:00 AM'),
    txt13=input.string('MIDNIGHT', title='', inline='MOPP', group='Opening Price Lines'),
    ShowNYOPP=input.bool(title='', defval=False, inline='NYOPP', group='Opening Price Lines', tooltip='08:30 AM'),
    txt17=input.string('NEW YORK', title='', inline='NYOPP', group='Opening Price Lines'),
    ShowEOPP=input.bool(title='', defval=False, inline='EOPP', group='Opening Price Lines', tooltip='09:30 AM'),
    txt18=input.string('EQUITIES', title='', inline='EOPP', group='Opening Price Lines'),
    ShowAFTPP=input.bool(title='', defval=False, inline='AFTOPP', group='Opening Price Lines', tooltip='01:30 PM'),
    txt1330=input.string('AFTERNOON', title='', inline='AFTOPP', group='Opening Price Lines'),
    MOPColP=input.color(color.new(color.new('#787B86'), 0), '', inline='MOPP', group='Opening Price Lines'),
    NYOPColP=input.color(color.new(color.new('#787B86'), 0), '', inline='NYOPP', group='Opening Price Lines'),
    EOPColP=input.color(color.new(color.new('#787B86'), 0), '', inline='EOPP', group='Opening Price Lines'),
    AFTOPColP=input.color(color.new(color.new('#787B86'), 0), '', inline='AFTOPP', group='Opening Price Lines'),
    MOPLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='MOPP', group='Opening Price Lines'),
    NYOPLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='NYOPP', group='Opening Price Lines'),
    EOPLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='EOPP', group='Opening Price Lines'),
    AFTOPLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='AFTOPP', group='Opening Price Lines'),
    i_MOPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='MOPP', group='Opening Price Lines'),
    i_NYOPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='NYOPP', group='Opening Price Lines'),
    i_EOPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='EOPP', group='Opening Price Lines'),
    i_AFTOPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='AFTOPP', group='Opening Price Lines'),
    ShowWeekOpen=input.bool(defval=False, title='', tooltip='Draw Weekly Open Price Line', group='HTF Opening Price Lines', inline='WO'),
    showMonthOpen=input.bool(defval=False, title='', tooltip='Draw Monthly Open Price Line', group='HTF Opening Price Lines', inline='MO'),
    txt19=input.string('WEEKLY', title='', inline='WO', group='HTF Opening Price Lines'),
    txt20=input.string('MONTHLY', title='', inline='MO', group='HTF Opening Price Lines'),
    i_WeekOpenCol=input.color(title='', defval=color.new(color.new('#787B86'), 0), group='HTF Opening Price Lines', inline='WO'),
    i_MonthOpenCol=input.color(title='', tooltip='', defval=color.new(color.new('#787B86'), 0), group='HTF Opening Price Lines', inline='MO'),
    WOLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='WO', group='HTF Opening Price Lines'),
    MOLS=input.string('Dotted', '', options=('Solid', 'Dashed', 'Dotted'), inline='MO', group='HTF Opening Price Lines'),
    i_WOPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='WO', group='HTF Opening Price Lines'),
    i_MONPLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='MO', group='HTF Opening Price Lines'),
    ShowCBDR=input.bool(True, '', inline='CBDR', group='CBDR, ASIA & FLOUT'),
    ShowASIA=input.bool(True, '', inline='ASIA', group='CBDR, ASIA & FLOUT'),
    ShowFLOUT=input.bool(False, '', inline='FLOUT', group='CBDR, ASIA & FLOUT'),
    txt0=input.string('CBDR', title='', inline='CBDR', group='CBDR, ASIA & FLOUT', tooltip='16:00 to 20:00 \nSD Increments of 1'),
    txt1=input.string('ASIA', title='', inline='ASIA', group='CBDR, ASIA & FLOUT', tooltip='20:00 to 00:00 \nSD Increments of 1'),
    txt7=input.string('FLOUT', title='', inline='FLOUT', group='CBDR, ASIA & FLOUT', tooltip='16:00 to 00:00 \nSD Increments of 0.5'),
    CBDRBoxCol=input.color(color.new(color.new('#787B86'), 0), '', inline='CBDR', group='CBDR, ASIA & FLOUT'),
    ASIABoxCol=input.color(color.new(color.new('#787B86'), 0), '', inline='ASIA', group='CBDR, ASIA & FLOUT'),
    FLOUTBoxCol=input.color(color.new(color.new('#787B86'), 0), '', inline='FLOUT', group='CBDR, ASIA & FLOUT'),
    box_text_cbdr=input.bool(True, 'Show Text', inline='CBDR', group='CBDR, ASIA & FLOUT'),
    box_text_cbdr_col=input.color(color.new(color.gray, 80), '', inline='CBDR', group='CBDR, ASIA & FLOUT'),
    bool_cbdr_dev=input.bool(True, 'SD', inline='CBDR', group='CBDR, ASIA & FLOUT'),
    box_text_asia=input.bool(True, 'Show Text', inline='ASIA', group='CBDR, ASIA & FLOUT'),
    box_text_asia_col=input.color(color.new(color.gray, 80), '', inline='ASIA', group='CBDR, ASIA & FLOUT'),
    bool_asia_dev=input.bool(True, 'SD', inline='ASIA', group='CBDR, ASIA & FLOUT'),
    box_text_flout=input.bool(True, 'Show Text', inline='FLOUT', group='CBDR, ASIA & FLOUT'),
    box_text_flout_col=input.color(color.new(color.gray, 80), '', inline='FLOUT', group='CBDR, ASIA & FLOUT'),
    bool_flout_dev=input.bool(True, 'SD', inline='FLOUT', group='CBDR, ASIA & FLOUT'),
    ShowDevLN=input.bool(title='', defval=True, inline='DEVLN', group='Standard Deviation', tooltip='Deviation Lines'),
    DEVLNTXT=input.string('SD LINES', title='', inline='DEVLN', group='Standard Deviation'),
    DevLNCol=input.color(color.new(color.new('#787B86'), 0), '', inline='DEVLN', group='Standard Deviation'),
    DEVLS=input.string('Solid', '', options=('Solid', 'Dashed', 'Dotted'), inline='DEVLN', group='Standard Deviation'),
    i_DEVLW=input.string('1px', '', options=('1px', '2px', '3px', '4px', '5px'), inline='DEVLN', group='Standard Deviation'),
    ShowDev=input.bool(False, '', inline='DEV', group='Standard Deviation'),
    txt8=input.string('SD COUNT', title='', inline='DEV', group='Standard Deviation'),
    SDCountCol=input.color(color.new(color.new('#787B86'), 0), '', inline='DEV', group='Standard Deviation'),
    DevInput=input.string('2 SD', '', options=('1 SD', '2 SD', '3 SD', '4 SD'), inline='DEV', group='Standard Deviation'),
    DevDirection=input.string('Both', '', options=('Upside Only', 'Both', 'Downside Only'), inline='DEV', group='Standard Deviation', tooltip='SD Count, NULL, SD Count, SD Direction'),
    Auto_Select=input.bool(False, '', group='Standard Deviation', inline='AUTOSD', tooltip='Auto SD Selection | Charter Content, Range Table \nMight Bug Out On Mondays'),
    txtSD=input.string('AUTO SD', '', group='Standard Deviation', inline='AUTOSD'),
    Tab1txtCol=input.color(color.new(color.new('#808080'), 0), '', inline='AUTOSD', group='Standard Deviation'),
    TabOptionShow=input.string('Show Table', '', options=('Show Table', 'Hide Table'), inline='AUTOSD', group='Standard Deviation'),
    TabOption1=input.string('Top Right', '', options=('Top Left', 'Top Center', 'Top Right', 'Middle Left', 'Middle Right', 'Bottom Left', 'Bottom Center', 'Bottom Right'), inline='AUTOSD', group='Standard Deviation'),
    ShowLabel=input.bool(True, title='', inline='Glabel', group='Day Of Week & Labels'),
    txt21=input.string('LABEL', title='', inline='Glabel', group='Day Of Week & Labels'),
    LabelColor=input.color(color.rgb(0, 0, 0, 100), '', inline='Glabel', group='Day Of Week & Labels'),
    LabelSizeInput=input.string('Normal', '', options=('Auto', 'Tiny', 'Small', 'Normal', 'Large', 'Huge'), inline='Glabel', group='Day Of Week & Labels'),
    Terminusinp=input.string('Terminus @ Current Time +1hr', '', options=('Terminus @ Next Midnight', 'Terminus @ Current Time', 'Terminus @ Current Time +15min', 'Terminus @ Current Time +30min', 'Terminus @ Current Time +45min', 'Terminus @ Current Time +1hr', 'Terminus @ Current Time +2hr', 'Terminus @ Current Time +3hr'), inline='Glabel', group='Day Of Week & Labels', tooltip='Select Label Size & Color & Terminus \nHistorical Price Lines needs to be toggled off for using Terminus'),
    ShowLabelText=input.bool(True, title='', inline='label', group='Day Of Week & Labels'),
    txt22=input.string('LABEL TEXT', title='', inline='label', group='Day Of Week & Labels'),
    LabelTextColor=input.color(color.new(color.new('#787B86'), 0), title='', inline='label', group='Day Of Week & Labels'),
    LabelTextOptioninput=input.string('Time', '', options=('Time', 'Text'), inline='label', group='Day Of Week & Labels', tooltip='Choose Between Descriptive Text as Label or Time \nShow/Hide Prices on Labels'),
    ShowPricesBool=input.string('Hide Prices', title='', options=('Show Prices', 'Hide Prices'), group='Day Of Week & Labels', inline='label'),
    showDOW=input.bool(True, title='', inline='DOW', group='Day Of Week & Labels'),
    txt24=input.string('DAY OF WEEK', title='', inline='DOW', group='Day Of Week & Labels'),
    i_DOWCol=input.color(color.new(color.new('#787B86'), 0), title='', inline='DOW', group='Day Of Week & Labels'),
    DOWTime=input.int(defval=12, title='', inline='DOW', group='Day Of Week & Labels'),
    DOWLoc_inpt=input.string('Bottom', '', options=('Top', 'Bottom'), inline='DOW', group='Day Of Week & Labels', tooltip='DOW Color, Time Alignment, Vertical Location'),
    BIAS_M_Bool=input.bool(False, '', group='BIAS & NOTES PRECONFIG', inline='stats'),
    txt100=input.string('BIAS', title='', inline='stats', group='BIAS & NOTES PRECONFIG'),
    Tab2txtCol=input.color(color.new(color.new('#787B86'), 0), '', inline='stats', group='BIAS & NOTES PRECONFIG'),
    TabOption2=input.string('Bottom Right', '', options=('Top Left', 'Top Center', 'Top Right', 'Middle Left', 'Middle Right', 'Bottom Left', 'Bottom Center', 'Bottom Right'), inline='stats', group='BIAS & NOTES PRECONFIG'),
    NOTES_M_Bool=input.bool(True, '', group='BIAS & NOTES PRECONFIG', inline='stats2'),
    txt101=input.string('NOTES', title='', inline='stats2', group='BIAS & NOTES PRECONFIG'),
    Tab3txtCol=input.color(color.new(color.new('#787B86'), 0), '', inline='stats2', group='BIAS & NOTES PRECONFIG'),
    TabOption3=input.string('Top Center', '', options=('Top Left', 'Top Center', 'Top Right', 'Middle Left', 'Middle Right', 'Bottom Left', 'Bottom Center', 'Bottom Right'), inline='stats2', group='BIAS & NOTES PRECONFIG'),
    BIASbool1=input.bool(True, '', inline='BIAS1', group='BIAS & NOTES'),
    txt52=input.string('DXY ', title='', inline='BIAS1', group='BIAS & NOTES'),
    BIASOption1=input.string('Bullish', options=('Bullish', 'Bearish', 'Consolidating', 'Unclear'), title='', inline='BIAS1', group='BIAS & NOTES'),
    BIASbool2=input.bool(True, '', inline='BIAS2', group='BIAS & NOTES'),
    txt53=input.string('EURGBP ', title='', inline='BIAS2', group='BIAS & NOTES'),
    BIASOption2=input.string('Bearish', options=('Bullish', 'Bearish', 'Consolidating', 'Unclear'), title='', inline='BIAS2', group='BIAS & NOTES'),
    BIASbool3=input.bool(True, '', inline='BIAS3', group='BIAS & NOTES'),
    txt54=input.string('AUDNZD ', title='', inline='BIAS3', group='BIAS & NOTES'),
    BIASOption3=input.string('Bullish', options=('Bullish', 'Bearish', 'Consolidating', 'Unclear'), title='', inline='BIAS3', group='BIAS & NOTES'),
    BIASbool4=input.bool(True, '', inline='BIAS4', group='BIAS & NOTES'),
    txt55=input.string('NASDAQ ', title='', inline='BIAS4', group='BIAS & NOTES'),
    BIASOption4=input.string('Bearish', options=('Bullish', 'Bearish', 'Consolidating', 'Unclear'), title='', inline='BIAS4', group='BIAS & NOTES'),
    notes=input.text_area('@coldbrewrosh', 'Notes', group='BIAS & NOTES')
):
    Timezone = 'GMT-10:00' if TZI == 'UTC -10' else 'GMT-07:00' if TZI == 'UTC -7' else 'GMT-06:00' if TZI == 'UTC -6' else 'GMT-05:00' if TZI == 'UTC -5' else 'GMT-04:00' if TZI == 'UTC -4' else 'GMT-03:00' if TZI == 'UTC -3' else 'GMT+00:00' if TZI == 'UTC +0' else 'GMT+01:00' if TZI == 'UTC +1' else 'GMT+02:00' if TZI == 'UTC +2' else 'GMT+03:00' if TZI == 'UTC +3' else 'GMT+03:30' if TZI == 'UTC +3:30' else 'GMT+04:00' if TZI == 'UTC +4' else 'GMT+05:00' if TZI == 'UTC +5' else 'GMT+05:30' if TZI == 'UTC +5:30' else 'GMT+06:00' if TZI == 'UTC +6' else 'GMT+07:00' if TZI == 'UTC +7' else 'GMT+08:00' if TZI == 'UTC +8' else 'GMT+09:00' if TZI == 'UTC +9' else 'GMT+09:30' if TZI == 'UTC +9:30' else 'GMT+10:00' if TZI == 'UTC +10' else 'GMT+10:30' if TZI == 'UTC +10:30' else 'GMT+11:00' if TZI == 'UTC +11' else 'GMT+13:00' if TZI == 'UTC +13' else 'GMT+13:45'
    DEVLSS = line.style_solid if DEVLS == 'Solid' else line.style_dotted if DEVLS == 'Dotted' else line.style_dashed
    DEVLW = 1 if i_DEVLW == '1px' else 2 if i_DEVLW == '2px' else 3 if i_DEVLW == '3px' else 4 if i_DEVLW == '4px' else 5
    DevCount = 1 if DevInput == '1 SD' else 2 if DevInput == '2 SD' else 3 if DevInput == '3 SD' else 4
    Stats = True if TabOptionShow == 'Show Table' else False
    tabinp1 = position.top_left if TabOption1 == 'Top Left' else position.top_center if TabOption1 == 'Top Center' else position.top_right if TabOption1 == 'Top Right' else position.middle_left if TabOption1 == 'Middle Left' else position.middle_right if TabOption1 == 'Middle Right' else position.bottom_left if TabOption1 == 'Bottom Left' else position.bottom_center if TabOption1 == 'Bottom Center' else position.bottom_right
    L_Prof: bool = True
    CellBG = color.new(color.new('#131722'), 100)
    ShowPrices = True if ShowPricesBool == 'Show Prices' else False
    DOWLoc = location.bottom if DOWLoc_inpt == 'Bottom' else location.top
    TableBG2 = color.new(color.new('#131722'), 100)
    tabinp2 = position.top_left if TabOption2 == 'Top Left' else position.top_center if TabOption2 == 'Top Center' else position.top_right if TabOption2 == 'Top Right' else position.middle_left if TabOption2 == 'Middle Left' else position.middle_right if TabOption2 == 'Middle Right' else position.bottom_left if TabOption2 == 'Bottom Left' else position.bottom_center if TabOption2 == 'Bottom Center' else position.bottom_right
    notesbool: bool = False
    tabinp3 = position.top_left if TabOption3 == 'Top Left' else position.top_center if TabOption3 == 'Top Center' else position.top_right if TabOption3 == 'Top Right' else position.middle_left if TabOption3 == 'Middle Left' else position.middle_right if TabOption3 == 'Middle Right' else position.bottom_left if TabOption3 == 'Bottom Left' else position.bottom_center if TabOption3 == 'Bottom Center' else position.bottom_right
    DOM = timeframe.multiplier <= inputMaxInterval and timeframe.isintraday
    newDay = ta.change(dayofweek)
    newWeek = ta.change(weekofyear)
    newMonth = ta.change(time('M'))
    transparentcol = color.rgb(255, 255, 255, 100)
    LSVLC = color.rgb(255, 255, 255, 100)
    NYSVLC = color.rgb(255, 255, 255, 100)
    PMSVLC = color.rgb(255, 255, 255, 100)
    ASVLC = color.rgb(255, 255, 255, 100)
    LSVLS: str = 'dotted'
    NYSVLS: str = 'dotted'
    PMSVLS: str = 'dotted'
    ASVLS: str = 'dotted'
    isToday: bool = False
    month_1 = month(timenow)
    month_2 = month(time)
    dayofmonth_1 = dayofmonth(timenow)
    dayofmonth_2 = dayofmonth(time)
    if year(timenow) == year(time) and month_1 == month_2 and (dayofmonth_1 == dayofmonth_2):
        isToday = True
    weekofyear_1 = weekofyear(timenow)
    weekofyear_2 = weekofyear(time)
    thisweek = year(timenow) == year(time) and weekofyear_1 == weekofyear_2
    weekofyear_3 = weekofyear(timenow - 604800000)
    weekofyear_4 = weekofyear(time)
    LastOneWeek = year(timenow) == year(time) and weekofyear_3 == weekofyear_4
    weekofyear_5 = weekofyear(timenow - 1209600000)
    weekofyear_6 = weekofyear(time)
    LastTwoWeek = year(timenow) == year(time) and weekofyear_5 == weekofyear_6
    weekofyear_7 = weekofyear(timenow - 1814400000)
    weekofyear_8 = weekofyear(time)
    LastThreeWeek = year(timenow) == year(time) and weekofyear_7 == weekofyear_8
    weekofyear_9 = weekofyear(timenow - 2419200000)
    weekofyear_10 = weekofyear(time)
    LastFourWeek = year(timenow) == year(time) and weekofyear_9 == weekofyear_10
    Last4Weeks: bool = False
    if thisweek == True or LastOneWeek == True or LastTwoWeek == True or (LastThreeWeek == True) or (LastFourWeek == True):
        Last4Weeks = True
    def vline(Start, Color__ren__, linestyle, LineWidth):
        return line.new(x1=Start, y1=low - ta.tr, x2=Start, y2=high + ta.tr, xloc=xloc.bar_time, extend=extend.both, color=Color__ren__, style=linestyle, width=LineWidth)

    atr = ta.atr(14)
    def toWhole(number):
        __block_result__ = na
        if syminfo.type == 'forex':
            _return = number / syminfo.mintick / 10 if atr < 1.0 else number
            _return = _return * 100 if atr >= 1.0 and atr < 100.0 and (syminfo.currency == 'JPY') else _return
            __block_result__ = _return
        else:
            __block_result__ = number
        return __block_result__

    def SessionBegins(sess):
        t: Series = time('', sess, Timezone)
        return DOM and (not barstate.isfirst) and na(t[1]) and (not na(t))

    def BarInSession(sess):
        return time(timeframe.period, sess, Timezone) != 0

    SFistrue: Persistent[bool] = True
    if LabelTextOptioninput == 'Time':
        SFistrue = True
    else:
        SFistrue = False
    def SeshStartHour(Session):
        return math.round(string.tonumber(string.substring(Session, 0, 2)))

    def SeshStartMins(Session):
        return math.round(string.tonumber(string.substring(Session, 2, 4)))

    def SeshEndHour(Session):
        return math.round(string.tonumber(string.substring(Session, 5, 7)))

    def SeshEndMins(Session):
        return math.round(string.tonumber(string.substring(Session, 7, 9)))

    CBDR: str = '1600-2000:1234567'
    ASIA: str = '2000-0000:1234567'
    FLOUT: str = '1600-0000:1234567'
    midsesh: str = '0000-1600:1234567'
    cbdrOpenTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(CBDR), SeshStartMins(CBDR), 0)
    cbdrEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(CBDR), SeshEndMins(CBDR), 0)
    asiaOpenTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(ASIA), SeshStartMins(ASIA), 0)
    asiaEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(ASIA), SeshEndMins(ASIA), 0) + 86400000
    floutOpenTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(FLOUT), SeshStartMins(FLOUT), 0)
    floutEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(FLOUT), SeshEndMins(FLOUT), 0) + 86400000
    CBDRTime = time(timeframe.period, CBDR, Timezone)
    ASIATime = time(timeframe.period, ASIA, Timezone)
    FLOUTTime = time(timeframe.period, FLOUT, Timezone)
    LabelOnlyToday: bool = True
    LondonStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(LDNsesh), SeshStartMins(LDNsesh), 0)
    LondonEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(LDNsesh), SeshEndMins(LDNsesh), 0)
    NYStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(NYsesh), SeshStartMins(NYsesh), 0)
    NYEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(NYsesh), SeshEndMins(NYsesh), 0)
    LCStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(LCsesh), SeshStartMins(LCsesh), 0)
    LCEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(LCsesh), SeshEndMins(LCsesh), 0)
    PMStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(PMsesh), SeshStartMins(PMsesh), 0)
    PMEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(PMsesh), SeshEndMins(PMsesh), 0)
    AsianStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(ASIA2sesh), SeshStartMins(ASIA2sesh), 0)
    AsianEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(ASIA2sesh), SeshEndMins(ASIA2sesh), 0)
    FreeStartTime = timestamp(Timezone, year, month, dayofmonth, SeshStartHour(FreeSesh), SeshStartMins(FreeSesh), 0)
    FreeEndTime = timestamp(Timezone, year, month, dayofmonth, SeshEndHour(FreeSesh), SeshEndMins(FreeSesh), 0)
    MidnightOpenTime = timestamp(Timezone, year, month, dayofmonth, 0, 0, 0)
    CLEANUPTIME = timestamp(Timezone, year, month, dayofmonth, 0, 0, 0) - 16200000
    LondonOpenTime = timestamp(Timezone, year, month, dayofmonth, 3, 0, 0)
    NYOpenTime = timestamp(Timezone, year, month, dayofmonth, 8, 30, 0)
    EquitiesOpenTime = timestamp(Timezone, year, month, dayofmonth, 9, 30, 0)
    AfternoonOpenTime = timestamp(Timezone, year, month, dayofmonth, 13, 30, 0)
    tMidnight: Series = time('1', '0000-0001:1234567', Timezone)
    def Cleanup(days):
        removal_timestamp = CLEANUPTIME - days * 86400000
        a_allLines: list[Line] = line.all
        a_allLabels: list[Label] = label.all
        a_allboxes: list[Box] = box.all
        if array.size(a_allLines) > 0:
            for i in pine_range(0, array.size(a_allLines) - 1, 1):
                line_x2 = line.get_x2(array.get(a_allLines, i))
                if line_x2 < removal_timestamp:
                    line.delete(array.get(a_allLines, i))
        if array.size(a_allLabels) > 0:
            for i in pine_range(0, array.size(a_allLabels) - 1, 1):
                label_x = label.get_x(array.get(a_allLabels, i))
                if label_x < removal_timestamp:
                    label.delete(array.get(a_allLabels, i))
        __block_result_1__ = na
        if array.size(a_allboxes) > 0:
            __block_result_2__ = na
            for i in pine_range(0, array.size(a_allboxes) - 1, 1):
                box_x = box.get_right(array.get(a_allboxes, i))
                __block_result_3__ = na
                if box_x < removal_timestamp - 86400000:
                    __block_result_3__ = box.delete(array.get(a_allboxes, i))
                __block_result_2__ = __block_result_3__
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def Terminus(Terminus_Inp):
        __block_result_4__ = na
        if Terminus_Inp == 'Terminus @ Current Time':
            _return = timenow
            __block_result_4__ = _return
        elif Terminus_Inp == 'Terminus @ Current Time +15min':
            _return = timenow + 900000
            __block_result_4__ = _return
        elif Terminus_Inp == 'Terminus @ Current Time +30min':
            _return = timenow + 1800000
            __block_result_4__ = _return
        elif Terminus_Inp == 'Terminus @ Current Time +45min':
            _return = timenow + 2700000
            __block_result_4__ = _return
        elif Terminus_Inp == 'Terminus @ Current Time +1hr':
            _return = timenow + 3600000
            __block_result_4__ = _return
        elif Terminus_Inp == 'Terminus @ Current Time +2hr':
            _return = timenow + 7200000
            __block_result_4__ = _return
        else:
            _return = timenow + 10800000
            __block_result_4__ = _return
        return __block_result_4__

    MNOPLS = line.style_solid if Midnight_Open_LS == 'Solid' else line.style_dotted if Midnight_Open_LS == 'Dotted' else line.style_dashed
    LNOPLS = line.style_solid if london_Open_LS == 'Solid' else line.style_dotted if london_Open_LS == 'Dotted' else line.style_dashed
    NWYOPLS = line.style_solid if NY_Open_LS == 'Solid' else line.style_dotted if NY_Open_LS == 'Dotted' else line.style_dashed
    EQOPLS = line.style_solid if Equities_Open_LS == 'Solid' else line.style_dotted if Equities_Open_LS == 'Dotted' else line.style_dashed
    MOPLSS = line.style_solid if MOPLS == 'Solid' else line.style_dotted if MOPLS == 'Dotted' else line.style_dashed
    NYOPLSS = line.style_solid if NYOPLS == 'Solid' else line.style_dotted if NYOPLS == 'Dotted' else line.style_dashed
    EOPLSS = line.style_solid if EOPLS == 'Solid' else line.style_dotted if EOPLS == 'Dotted' else line.style_dashed
    AFTOPLSS = line.style_solid if AFTOPLS == 'Solid' else line.style_dotted if AFTOPLS == 'Dotted' else line.style_dashed
    WeekOpenLS = line.style_solid if WOLS == 'Solid' else line.style_dotted if WOLS == 'Dotted' else line.style_dashed
    MonthOpenLS = line.style_solid if MOLS == 'Solid' else line.style_dotted if MOLS == 'Dotted' else line.style_dashed
    MOPLW = 1 if Midnight_Open_LW == '1px' else 2 if Midnight_Open_LW == '2px' else 3 if Midnight_Open_LW == '3px' else 4 if Midnight_Open_LW == '4px' else 5
    LOPLW = 1 if London_Open_LW == '1px' else 2 if London_Open_LW == '2px' else 3 if London_Open_LW == '3px' else 4 if London_Open_LW == '4px' else 5
    NYOPLW = 1 if NY_Open_LW == '1px' else 2 if NY_Open_LW == '2px' else 3 if NY_Open_LW == '3px' else 4 if NY_Open_LW == '4px' else 5
    EOPLW = 1 if Equities_Open_LW == '1px' else 2 if Equities_Open_LW == '2px' else 3 if Equities_Open_LW == '3px' else 4 if Equities_Open_LW == '4px' else 5
    MOPPLW = 1 if i_MOPLW == '1px' else 2 if i_MOPLW == '2px' else 3 if i_MOPLW == '3px' else 4 if i_MOPLW == '4px' else 5
    NYOPPLW = 1 if i_NYOPLW == '1px' else 2 if i_NYOPLW == '2px' else 3 if i_NYOPLW == '3px' else 4 if i_NYOPLW == '4px' else 5
    EOPPLW = 1 if i_EOPLW == '1px' else 2 if i_EOPLW == '2px' else 3 if i_EOPLW == '3px' else 4 if i_EOPLW == '4px' else 5
    AFTOPLW = 1 if i_AFTOPLW == '1px' else 2 if i_AFTOPLW == '2px' else 3 if i_AFTOPLW == '3px' else 4 if i_AFTOPLW == '4px' else 5
    WEEKOPPLW = 1 if i_WOPLW == '1px' else 2 if i_WOPLW == '2px' else 3 if i_WOPLW == '3px' else 4 if i_WOPLW == '4px' else 5
    MONTHOPPLW = 1 if i_MONPLW == '1px' else 2 if i_MONPLW == '2px' else 3 if i_MONPLW == '3px' else 4 if i_MONPLW == '4px' else 5
    LabelSize = size.auto if LabelSizeInput == 'Auto' else size.tiny if LabelSizeInput == 'Tiny' else size.small if LabelSizeInput == 'Small' else size.normal if LabelSizeInput == 'Normal' else size.large if LabelSizeInput == 'Large' else size.huge
    London_Start_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=LSVLC, width=1)
    London_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=LSVLC, width=1)
    LondonFill: PersistentSeries = linefill.new(London_Start_Vline, London_End_Vline, LSFC)
    NY_Start_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=NYSVLC, width=1)
    NY_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=NYSVLC, width=1)
    NYFill: PersistentSeries = linefill.new(NY_Start_Vline, NY_End_Vline, NYSFC)
    LC_Start_Vline: Persistent = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=NYSVLC, width=1)
    LC_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=NYSVLC, width=1)
    LCFill: PersistentSeries = linefill.new(LC_Start_Vline, LC_End_Vline, LCSFC)
    PM_Start_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=PMSVLC, width=1)
    PM_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=PMSVLC, width=1)
    PMFill: PersistentSeries = linefill.new(PM_Start_Vline, PM_End_Vline, PMSFC)
    Asian_Start_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=ASVLC, width=1)
    Asian_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=ASVLC, width=1)
    AsianFill: PersistentSeries = linefill.new(Asian_Start_Vline, Asian_End_Vline, ASFC)
    Free_Start_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=ASVLC, width=1)
    Free_End_Vline: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=ASVLC, width=1)
    FreeFill: PersistentSeries = linefill.new(Free_Start_Vline, Free_End_Vline, FSFC)
    Midnight_Open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=MOPColor, width=1)
    London_Open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=LOPColor, width=1)
    NY_Open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=NYOPColor, width=1)
    Equities_Open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=EOPColor, width=1)
    if cast_bool(newDay) and dayofweek != dayofweek.sunday:
        if ShowLondon and DOM:
            if ShowTSO:
                line.delete(London_Start_Vline[1])
                line.delete(London_End_Vline[1])
                linefill.delete(LondonFill[1])
            London_Start_Vline = vline(LondonStartTime, transparentcol, line.style_solid, 1)
            London_End_Vline = vline(LondonEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                LondonFill = linefill.new(London_Start_Vline, London_End_Vline, LSFC)
        if ShowNY and DOM:
            if ShowTSO:
                line.delete(NY_Start_Vline[1])
                line.delete(NY_End_Vline[1])
                linefill.delete(NYFill[1])
            NY_Start_Vline = vline(NYStartTime, transparentcol, line.style_solid, 1)
            NY_End_Vline = vline(NYEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                NYFill = linefill.new(NY_Start_Vline, NY_End_Vline, NYSFC)
        if ShowLC and DOM:
            if ShowTSO:
                line.delete(LC_End_Vline[1])
                linefill.delete(LCFill[1])
            LC_Start_Vline = vline(LCStartTime, transparentcol, line.style_solid, 1)
            LC_End_Vline = vline(LCEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                LCFill = linefill.new(LC_Start_Vline, LC_End_Vline, LCSFC)
        if ShowPM and DOM:
            if ShowTSO:
                line.delete(PM_Start_Vline[1])
                line.delete(PM_End_Vline[1])
                linefill.delete(PMFill[1])
            PM_Start_Vline = vline(PMStartTime, transparentcol, line.style_solid, 1)
            PM_End_Vline = vline(PMEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                PMFill = linefill.new(PM_Start_Vline, PM_End_Vline, PMSFC)
        if ShowAsian and DOM:
            if ShowTSO:
                line.delete(Asian_Start_Vline[1])
                line.delete(Asian_End_Vline[1])
                linefill.delete(AsianFill[1])
            Asian_Start_Vline = vline(AsianStartTime, transparentcol, line.style_solid, 1)
            Asian_End_Vline = vline(AsianEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                AsianFill = linefill.new(Asian_Start_Vline, Asian_End_Vline, ASFC)
        if ShowFreeSesh and DOM:
            if ShowTSO:
                line.delete(Free_Start_Vline[1])
                line.delete(Free_End_Vline[1])
                linefill.delete(FreeFill[1])
            Free_Start_Vline = vline(FreeStartTime, transparentcol, line.style_solid, 1)
            Free_End_Vline = vline(FreeEndTime, transparentcol, line.style_solid, 1)
            if ShowSFill:
                FreeFill = linefill.new(Free_Start_Vline, Free_End_Vline, FSFC)
        if ShowMOP and DOM:
            if MOLHist == False:
                line.delete(Midnight_Open[1])
            Midnight_Open = vline(MidnightOpenTime, MOPColor, MNOPLS, MOPLW)
        if ShowLOP and DOM:
            if ShowTSO:
                line.delete(London_Open[1])
            London_Open = vline(LondonOpenTime, LOPColor, LNOPLS, LOPLW)
        if ShowNYOP and DOM:
            if ShowTSO:
                line.delete(NY_Open[1])
            NY_Open = vline(NYOpenTime, NYOPColor, NWYOPLS, NYOPLW)
        if ShowEOP and DOM:
            if ShowTSO:
                line.delete(Equities_Open[1])
            Equities_Open = vline(EquitiesOpenTime, EOPColor, EQOPLS, EOPLW)
    MOPLB: PersistentSeries[Label] = na(Label)
    MOPLN: PersistentSeries[Line] = na(Line)
    NYOPLB: PersistentSeries[Label] = na(Label)
    NYOPLN: PersistentSeries[Line] = na(Line)
    EOPLB: PersistentSeries[Label] = na(Label)
    EOPLN: PersistentSeries[Line] = na(Line)
    AFTLN: PersistentSeries[Line] = na(Line)
    AFTLB: PersistentSeries[Label] = na(Label)
    openMidnight: PersistentSeries[float] = 0.0
    if cast_bool(tMidnight):
        if not tMidnight[1]:
            openMidnight = open
        else:
            openMidnight = math.max(open, openMidnight)
    if ShowMOPP and openMidnight != openMidnight[1] and DOM and barstate.isconfirmed:
        label.delete(MOPLB[1])
        if ShowMOPL == False:
            line.delete(MOPLN[1])
        MOPLN = line.new(x1=tMidnight, y1=openMidnight, x2=tMidnight + 86400000, xloc=xloc.bar_time, y2=openMidnight, color=MOPColP, style=MOPLSS, width=MOPPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(MOPLN, tMidnight + 259200000)
        if ShowLabel:
            MOPLB = label.new(x=tMidnight + 86400000, y=openMidnight, xloc=xloc.bar_time, color=LabelColor, textcolor=MOPColP, style=label.style_label_left, size=LabelSize, tooltip='Midnight Opening Price')
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(MOPLB, tMidnight + 259200000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(MOPLB, ' 00:00  |  ' + string.tostring(open))
                    else:
                        label.set_text(MOPLB, ' 00:00 ')
                    label.set_tooltip(MOPLB, 'Midnight Opening Price')
                else:
                    if ShowPrices == True:
                        label.set_text(MOPLB, ' Midnight Opening Price  |  ' + string.tostring(open))
                    else:
                        label.set_text(MOPLB, ' Midnight Opening Price ')
                    label.set_tooltip(MOPLB, '')
                label.set_textcolor(MOPLB, LabelTextColor)
                label.set_size(MOPLB, LabelSize)
        if time > PMEndTime and time < MidnightOpenTime + 86400000:
            line.delete(MOPLN)
    if Terminusinp != 'Terminus @ Next Midnight' and ShowMOPL == False:
        line.set_x2(MOPLN, Terminus(Terminusinp))
        label.set_x(MOPLB, Terminus(Terminusinp))
    if ShowNYOPP and time == NYOpenTime and DOM:
        label.delete(NYOPLB[1])
        if ShowPrev == False:
            line.delete(NYOPLN[1])
        NYOPLN = line.new(x1=NYOpenTime, y1=open, x2=NYOpenTime + 55800000, xloc=xloc.bar_time, y2=open, color=NYOPColP, style=NYOPLSS, width=NYOPPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(NYOPLN, NYOpenTime + 228600000)
        if ShowLabel:
            NYOPLB = label.new(x=NYOpenTime + 55800000, y=open, xloc=xloc.bar_time, color=LabelColor, textcolor=NYOPColP, style=label.style_label_left, size=LabelSize, tooltip='New York Opening Price')
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(NYOPLB, NYOpenTime + 228600000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(NYOPLB, ' 08:30  |  ' + string.tostring(open))
                    else:
                        label.set_text(NYOPLB, ' 08:30 ')
                    label.set_tooltip(NYOPLB, 'New York Opening Price')
                else:
                    if ShowPrices == True:
                        label.set_text(NYOPLB, ' New York Opening Price  |  ' + string.tostring(open))
                    else:
                        label.set_text(NYOPLB, ' New York Opening Price ')
                    label.set_tooltip(NYOPLB, '')
                label.set_textcolor(NYOPLB, LabelTextColor)
                label.set_size(NYOPLB, LabelSize)
    if Terminusinp != 'Terminus @ Next Midnight' and ShowPrev == False:
        line.set_x2(NYOPLN, Terminus(Terminusinp))
        label.set_x(NYOPLB, Terminus(Terminusinp))
    if ShowEOPP and time == EquitiesOpenTime and DOM:
        label.delete(EOPLB[1])
        if ShowPrev == False:
            line.delete(EOPLN[1])
        EOPLN = line.new(x1=EquitiesOpenTime, y1=open, x2=EquitiesOpenTime + 52200000, xloc=xloc.bar_time, y2=open, color=EOPColP, style=EOPLSS, width=EOPPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(EOPLN, EquitiesOpenTime + 225000000)
        if ShowLabel:
            EOPLB = label.new(x=EquitiesOpenTime + 52200000, y=open, xloc=xloc.bar_time, color=LabelColor, textcolor=EOPColP, style=label.style_label_left, size=LabelSize, tooltip='Equities Opening Price')
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(EOPLB, EquitiesOpenTime + 225000000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(EOPLB, ' 09:30  |  ' + string.tostring(open))
                    else:
                        label.set_text(EOPLB, ' 09:30 ')
                    label.set_tooltip(EOPLB, 'Equities Opening Price')
                else:
                    if ShowPrices == True:
                        label.set_text(EOPLB, ' Equities Opening Price  |  ' + string.tostring(open))
                    else:
                        label.set_text(EOPLB, ' Equities Opening Price ')
                    label.set_tooltip(EOPLB, '')
                label.set_textcolor(EOPLB, LabelTextColor)
                label.set_size(EOPLB, LabelSize)
    if Terminusinp != 'Terminus @ Next Midnight' and ShowPrev == False:
        line.set_x2(EOPLN, Terminus(Terminusinp))
        label.set_x(EOPLB, Terminus(Terminusinp))
    if ShowAFTPP and time == AfternoonOpenTime and DOM:
        label.delete(AFTLB[1])
        if ShowPrev == False:
            line.delete(AFTLN[1])
        AFTLN = line.new(x1=AfternoonOpenTime, y1=open, x2=EquitiesOpenTime + 52200000, xloc=xloc.bar_time, y2=open, color=AFTOPColP, style=AFTOPLSS, width=AFTOPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(AFTLN, EquitiesOpenTime + 225000000)
        if ShowLabel:
            AFTLB = label.new(x=EquitiesOpenTime + 52200000, y=open, xloc=xloc.bar_time, color=LabelColor, textcolor=AFTOPColP, style=label.style_label_left, size=LabelSize, tooltip='Equities Opening Price')
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(AFTLB, EquitiesOpenTime + 225000000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(AFTLB, ' 01:30  |  ' + string.tostring(open))
                    else:
                        label.set_text(AFTLB, ' 01:30 ')
                    label.set_tooltip(AFTLB, ' Afternoon Opening Price')
                else:
                    if ShowPrices == True:
                        label.set_text(AFTLB, ' Afternoon Opening Price  |  ' + string.tostring(open))
                    else:
                        label.set_text(AFTLB, ' Afternoon Opening Price ')
                    label.set_tooltip(AFTLB, '')
                label.set_textcolor(AFTLB, LabelTextColor)
                label.set_size(AFTLB, LabelSize)
    if Terminusinp != 'Terminus @ Next Midnight' and ShowPrev == False:
        line.set_x2(AFTLN, Terminus(Terminusinp))
        label.set_x(AFTLB, Terminus(Terminusinp))
    Weekly_open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=i_WeekOpenCol, style=WeekOpenLS, width=1)
    Weekly_openlbl: PersistentSeries = label.new(x=na, y=na, xloc=xloc.bar_time, color=LabelColor, textcolor=LabelTextColor, style=label.style_label_left, size=LabelSize)
    WeeklyOpenTime: Persistent = time
    Monthly_open: PersistentSeries = line.new(x1=na, y1=na, x2=na, xloc=xloc.bar_time, y2=close, color=i_MonthOpenCol, style=MonthOpenLS, width=1)
    Monthly_openlbl: PersistentSeries = label.new(x=na, y=na, xloc=xloc.bar_time, color=LabelColor, textcolor=LabelTextColor, style=label.style_label_left, size=LabelSize)
    MonthlyOpenTime: Persistent = time
    WeeklyOpen = request.security(syminfo.tickerid, 'W', open, lookahead=barmerge.lookahead_on)
    MonthlyOpen = request.security(syminfo.tickerid, 'M', open, lookahead=barmerge.lookahead_on)
    if cast_bool(newWeek):
        WeeklyOpenTime = time
    if ShowWeekOpen and cast_bool(newDay) and Last4Weeks:
        label.delete(Weekly_openlbl[1])
        line.delete(Weekly_open[1])
        Weekly_open = line.new(x1=WeeklyOpenTime - 25200000, y1=WeeklyOpen, x2=EquitiesOpenTime + 52200000, xloc=xloc.bar_time, y2=WeeklyOpen, color=i_WeekOpenCol, style=WeekOpenLS, width=WEEKOPPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(Weekly_open, EquitiesOpenTime + 225000000)
        if ShowLabel:
            Weekly_openlbl = label.new(x=EquitiesOpenTime + 52200000, y=WeeklyOpen, xloc=xloc.bar_time, color=LabelColor, textcolor=LabelTextColor, style=label.style_label_left, size=LabelSize, tooltip='Weekly Open: ' + string.tostring(WeeklyOpen))
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(Weekly_openlbl, EquitiesOpenTime + 225000000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(Weekly_openlbl, ' W.O.   |  ' + string.tostring(WeeklyOpen))
                    else:
                        label.set_text(Weekly_openlbl, ' W.O. ')
                    label.set_tooltip(Weekly_openlbl, ' Weekly Opening Price ')
                else:
                    if ShowPrices == True:
                        label.set_text(Weekly_openlbl, ' Weekly Open  |  ' + string.tostring(WeeklyOpen))
                    else:
                        label.set_text(Weekly_openlbl, ' Weekly Open ')
                    label.set_tooltip(Weekly_openlbl, '')
                label.set_textcolor(Weekly_openlbl, LabelTextColor)
                label.set_size(Weekly_openlbl, LabelSize)
    if timeframe.multiplier > 60:
        line.set_x2(Weekly_open, AsianEndTime + 232000000)
        label.set_x(Weekly_openlbl, AsianEndTime + 232000000)
    if timeframe.period == 'D':
        line.set_x2(Weekly_open, AsianEndTime + 832000000)
        label.set_x(Weekly_openlbl, AsianEndTime + 832000000)
    if timeframe.period == 'M':
        line.delete(Weekly_open)
        label.delete(Weekly_openlbl)
    if Terminusinp != 'Terminus @ Next Midnight' and DOM:
        line.set_x2(Weekly_open, Terminus(Terminusinp))
        label.set_x(Weekly_openlbl, Terminus(Terminusinp))
    if cast_bool(newMonth):
        MonthlyOpenTime = time
    if showMonthOpen and cast_bool(newDay):
        line.delete(Monthly_open[1])
        label.delete(Monthly_openlbl[1])
        Monthly_open = line.new(x1=MonthlyOpenTime, y1=MonthlyOpen, x2=AsianEndTime, xloc=xloc.bar_time, y2=MonthlyOpen, color=i_MonthOpenCol, style=MonthOpenLS, width=MONTHOPPLW)
        if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
            line.set_x2(Monthly_open, EquitiesOpenTime + 225000000)
        if ShowLabel:
            Monthly_openlbl = label.new(x=AsianEndTime, y=MonthlyOpen, xloc=xloc.bar_time, color=LabelColor, textcolor=LabelTextColor, style=label.style_label_left, size=LabelSize, tooltip='Monthly Open: ' + string.tostring(MonthlyOpen))
            if dayofweek == dayofweek.friday and syminfo.type != 'crypto':
                label.set_x(Monthly_openlbl, EquitiesOpenTime + 225000000)
            if ShowLabelText:
                if SFistrue:
                    if ShowPrices == True:
                        label.set_text(Monthly_openlbl, ' M.O.   |  ' + string.tostring(MonthlyOpen))
                    else:
                        label.set_text(Monthly_openlbl, ' M.O. ')
                    label.set_tooltip(Monthly_openlbl, ' Monthly Opening Price ')
                else:
                    if ShowPrices == True:
                        label.set_text(Monthly_openlbl, ' Monthly Open  |  ' + string.tostring(MonthlyOpen))
                    else:
                        label.set_text(Monthly_openlbl, ' Monthly Open ')
                    label.set_tooltip(Monthly_openlbl, '')
                label.set_textcolor(Monthly_openlbl, LabelTextColor)
                label.set_size(Monthly_openlbl, LabelSize)
    if timeframe.multiplier > 60:
        line.set_x2(Monthly_open, AsianEndTime + 232000000)
        label.set_x(Monthly_openlbl, AsianEndTime + 232000000)
    if timeframe.period == 'D':
        line.set_x2(Monthly_open, AsianEndTime + 832000000)
        label.set_x(Monthly_openlbl, AsianEndTime + 832000000)
    if timeframe.period == 'W':
        line.set_x2(Monthly_open, AsianEndTime + 2592000000)
        label.set_x(Monthly_openlbl, AsianEndTime + 2592000000)
    if timeframe.period == 'M':
        line.delete(Monthly_open)
        label.delete(Monthly_openlbl)
    if Terminusinp != 'Terminus @ Next Midnight' and DOM:
        line.set_x2(Monthly_open, Terminus(Terminusinp))
        label.set_x(Monthly_openlbl, Terminus(Terminusinp))
    cbdr_hi: PersistentSeries[float] = na(float)
    cbdr_lo: PersistentSeries[float] = na(float)
    cbdr_diff: Persistent[float] = na(float)
    cbdrbox: PersistentSeries[Box] = na(Box)
    cbdr_hi_line: Persistent[Line] = na(Line)
    cbdr_lo_line: Persistent[Line] = na(Line)
    dev01negline: PersistentSeries[Line] = na(Line)
    dev02negline: PersistentSeries[Line] = na(Line)
    dev03negline: PersistentSeries[Line] = na(Line)
    dev04negline: PersistentSeries[Line] = na(Line)
    dev01posline: PersistentSeries[Line] = na(Line)
    dev02posline: PersistentSeries[Line] = na(Line)
    dev03posline: PersistentSeries[Line] = na(Line)
    dev04posline: PersistentSeries[Line] = na(Line)
    if SessionBegins(CBDR) and DOM:
        cbdr_hi = high
        cbdr_lo = low
        cbdr_diff = cbdr_hi - cbdr_lo
        if ShowTSO:
            box.delete(cbdrbox[1])
            line.delete(dev01posline[1])
            line.delete(dev01negline[1])
            line.delete(dev02posline[1])
            line.delete(dev02negline[1])
            line.delete(dev03posline[1])
            line.delete(dev03negline[1])
            line.delete(dev04posline[1])
            line.delete(dev04negline[1])
        if ShowCBDR:
            cbdrbox = box.new(cbdrOpenTime, cbdr_hi, cbdrEndTime, cbdr_lo, color.new(CBDRBoxCol, 90), 1, line.style_solid, extend.none, xloc.bar_time, color.new(CBDRBoxCol, 90), txt0, size.auto, color.new(box_text_cbdr_col, 80), text_wrap=text.wrap_auto)
            if dayofweek == dayofweek.friday:
                box.set_right(cbdrbox, cbdrOpenTime + 187200000)
                line.set_x2(cbdr_hi_line, cbdrOpenTime + 187200000)
                line.set_x2(cbdr_lo_line, cbdrOpenTime + 187200000)
        if box_text_cbdr == False:
            box.set_text(cbdrbox, '')
        if ShowDev and ShowCBDR and bool_cbdr_dev:
            for i in pine_range(1, DevCount, 1):
                if i == 1:
                    dev01posline = line.new(cbdrOpenTime, cbdr_hi + cbdr_diff * i, cbdrEndTime, cbdr_hi + cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev01negline = line.new(cbdrOpenTime, cbdr_hi - cbdr_diff * i, cbdrEndTime, cbdr_lo - cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev01posline, cbdrOpenTime + 187200000)
                        line.set_x2(dev01negline, cbdrOpenTime + 187200000)
                if i == 2:
                    dev02posline = line.new(cbdrOpenTime, cbdr_hi + cbdr_diff * i, cbdrEndTime, cbdr_lo + cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev02negline = line.new(cbdrOpenTime, cbdr_hi - cbdr_diff * i, cbdrEndTime, cbdr_lo - cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev02posline, cbdrOpenTime + 187200000)
                        line.set_x2(dev02negline, cbdrOpenTime + 187200000)
                if i == 3:
                    dev03posline = line.new(cbdrOpenTime, cbdr_hi + cbdr_diff * i, cbdrEndTime, cbdr_lo + cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev03negline = line.new(cbdrOpenTime, cbdr_hi - cbdr_diff * i, cbdrEndTime, cbdr_lo - cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev03posline, cbdrOpenTime + 187200000)
                        line.set_x2(dev03negline, cbdrOpenTime + 187200000)
                if i == 4:
                    dev04posline = line.new(cbdrOpenTime, cbdr_hi + cbdr_diff * i, cbdrEndTime, cbdr_lo + cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev04negline = line.new(cbdrOpenTime, cbdr_hi - cbdr_diff * i, cbdrEndTime, cbdr_lo - cbdr_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev04posline, cbdrOpenTime + 187200000)
                        line.set_x2(dev04negline, cbdrOpenTime + 187200000)
    elif cast_bool(CBDRTime):
        cbdr_hi = math.max(high, cbdr_hi)
        cbdr_lo = math.min(low, cbdr_lo)
        cbdr_diff = cbdr_hi - cbdr_lo
        for i in pine_range(1, DevCount, 1):
            if i == 1 and ShowDev:
                line.set_y1(dev01posline, cbdr_hi + cbdr_diff * i)
                line.set_y2(dev01posline, cbdr_hi + cbdr_diff * i)
                line.set_y1(dev01negline, cbdr_lo - cbdr_diff * i)
                line.set_y2(dev01negline, cbdr_lo - cbdr_diff * i)
            if i == 2 and ShowDev:
                line.set_y1(dev02posline, cbdr_hi + cbdr_diff * i)
                line.set_y2(dev02posline, cbdr_hi + cbdr_diff * i)
                line.set_y1(dev02negline, cbdr_lo - cbdr_diff * i)
                line.set_y2(dev02negline, cbdr_lo - cbdr_diff * i)
            if i == 3 and ShowDev:
                line.set_y1(dev03posline, cbdr_hi + cbdr_diff * i)
                line.set_y2(dev03posline, cbdr_hi + cbdr_diff * i)
                line.set_y1(dev03negline, cbdr_lo - cbdr_diff * i)
                line.set_y2(dev03negline, cbdr_lo - cbdr_diff * i)
            if i == 4 and ShowDev:
                line.set_y1(dev04posline, cbdr_hi + cbdr_diff * i)
                line.set_y2(dev04posline, cbdr_hi + cbdr_diff * i)
                line.set_y1(dev04negline, cbdr_lo - cbdr_diff * i)
                line.set_y2(dev04negline, cbdr_lo - cbdr_diff * i)
        if cbdr_hi > cbdr_hi[1]:
            if ShowCBDR:
                box.set_top(cbdrbox, cbdr_hi)
        if cbdr_lo < cbdr_lo[1]:
            if ShowCBDR:
                box.set_bottom(cbdrbox, cbdr_lo)
    if DevDirection == 'Upside Only':
        line.delete(dev01negline)
        line.delete(dev02negline)
        line.delete(dev03negline)
        line.delete(dev04negline)
    elif DevDirection == 'Downside Only':
        line.delete(dev01posline)
        line.delete(dev02posline)
        line.delete(dev03posline)
        line.delete(dev04posline)
    asia_hi: PersistentSeries[float] = na(float)
    asia_lo: PersistentSeries[float] = na(float)
    asia_diff: Persistent[float] = na(float)
    asia_box: PersistentSeries[Box] = na(Box)
    asia_hi_line: Persistent[Line] = na(Line)
    asia_lo_line: Persistent[Line] = na(Line)
    dev01negline_asia: PersistentSeries[Line] = na(Line)
    dev02negline_asia: PersistentSeries[Line] = na(Line)
    dev03negline_asia: PersistentSeries[Line] = na(Line)
    dev04negline_asia: PersistentSeries[Line] = na(Line)
    dev01posline_asia: PersistentSeries[Line] = na(Line)
    dev02posline_asia: PersistentSeries[Line] = na(Line)
    dev03posline_asia: PersistentSeries[Line] = na(Line)
    dev04posline_asia: PersistentSeries[Line] = na(Line)
    if SessionBegins(ASIA) and DOM:
        asia_hi = high
        asia_lo = low
        asia_diff = asia_hi - asia_lo
        if ShowTSO:
            box.delete(asia_box[1])
            line.delete(dev01posline_asia[1])
            line.delete(dev01negline_asia[1])
            line.delete(dev02posline_asia[1])
            line.delete(dev02negline_asia[1])
            line.delete(dev03posline_asia[1])
            line.delete(dev03negline_asia[1])
            line.delete(dev04posline_asia[1])
            line.delete(dev04negline_asia[1])
        if ShowASIA:
            asia_box = box.new(asiaOpenTime, asia_hi, asiaEndTime, asia_lo, color.new(ASIABoxCol, 90), 1, line.style_solid, extend.none, xloc.bar_time, color.new(ASIABoxCol, 90), txt1, size.auto, color.new(box_text_asia_col, 80), text_wrap=text.wrap_auto)
        if box_text_asia == False:
            box.set_text(asia_box, '')
        if ShowDev and ShowASIA and bool_asia_dev:
            for i in pine_range(1, DevCount, 1):
                if i == 1:
                    dev01posline_asia = line.new(asiaOpenTime, asia_hi + asia_diff * i, asiaEndTime, asia_hi + asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev01negline_asia = line.new(asiaOpenTime, asia_hi - asia_diff * i, asiaEndTime, asia_lo - asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                if i == 2:
                    dev02posline_asia = line.new(asiaOpenTime, asia_hi + asia_diff * i, asiaEndTime, asia_lo + asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev02negline_asia = line.new(asiaOpenTime, asia_hi - asia_diff * i, asiaEndTime, asia_lo - asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                if i == 3:
                    dev03posline_asia = line.new(asiaOpenTime, asia_hi + asia_diff * i, asiaEndTime, asia_lo + asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev03negline_asia = line.new(asiaOpenTime, asia_hi - asia_diff * i, asiaEndTime, asia_lo - asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                if i == 4:
                    dev04posline_asia = line.new(asiaOpenTime, asia_hi + asia_diff * i, asiaEndTime, asia_lo + asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev04negline_asia = line.new(asiaOpenTime, asia_hi - asia_diff * i, asiaEndTime, asia_lo - asia_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
    elif cast_bool(ASIATime):
        asia_hi = math.max(high, asia_hi)
        asia_lo = math.min(low, asia_lo)
        asia_diff = asia_hi - asia_lo
        for i in pine_range(1, DevCount, 1):
            if i == 1 and ShowDev:
                line.set_y1(dev01posline_asia, asia_hi + asia_diff * i)
                line.set_y2(dev01posline_asia, asia_hi + asia_diff * i)
                line.set_y1(dev01negline_asia, asia_lo - asia_diff * i)
                line.set_y2(dev01negline_asia, asia_lo - asia_diff * i)
            if i == 2 and ShowDev:
                line.set_y1(dev02posline_asia, asia_hi + asia_diff * i)
                line.set_y2(dev02posline_asia, asia_hi + asia_diff * i)
                line.set_y1(dev02negline_asia, asia_lo - asia_diff * i)
                line.set_y2(dev02negline_asia, asia_lo - asia_diff * i)
            if i == 3 and ShowDev:
                line.set_y1(dev03posline_asia, asia_hi + asia_diff * i)
                line.set_y2(dev03posline_asia, asia_hi + asia_diff * i)
                line.set_y1(dev03negline_asia, asia_lo - asia_diff * i)
                line.set_y2(dev03negline_asia, asia_lo - asia_diff * i)
            if i == 4 and ShowDev:
                line.set_y1(dev04posline_asia, asia_hi + asia_diff * i)
                line.set_y2(dev04posline_asia, asia_hi + asia_diff * i)
                line.set_y1(dev04negline_asia, asia_lo - asia_diff * i)
                line.set_y2(dev04negline_asia, asia_lo - asia_diff * i)
        if asia_hi > asia_hi[1]:
            box.set_top(asia_box, asia_hi)
        if asia_lo < asia_lo[1]:
            box.set_bottom(asia_box, asia_lo)
    if DevDirection == 'Upside Only':
        line.delete(dev01negline_asia)
        line.delete(dev02negline_asia)
        line.delete(dev03negline_asia)
        line.delete(dev04negline_asia)
    elif DevDirection == 'Downside Only':
        line.delete(dev01posline_asia)
        line.delete(dev02posline_asia)
        line.delete(dev03posline_asia)
        line.delete(dev04posline_asia)
    flout_hi: PersistentSeries[float] = na(float)
    flout_lo: PersistentSeries[float] = na(float)
    flout_diff: Persistent[float] = na(float)
    floutbox: PersistentSeries[Box] = na(Box)
    flout_hi_line: Persistent[Line] = na(Line)
    flout_lo_line: Persistent[Line] = na(Line)
    dev01negline_flout: PersistentSeries[Line] = na(Line)
    dev02negline_flout: PersistentSeries[Line] = na(Line)
    dev03negline_flout: PersistentSeries[Line] = na(Line)
    dev04negline_flout: PersistentSeries[Line] = na(Line)
    dev01posline_flout: PersistentSeries[Line] = na(Line)
    dev02posline_flout: PersistentSeries[Line] = na(Line)
    dev03posline_flout: PersistentSeries[Line] = na(Line)
    dev04posline_flout: PersistentSeries[Line] = na(Line)
    if SessionBegins(FLOUT) and DOM:
        flout_hi = high
        flout_lo = low
        flout_diff = flout_hi - flout_lo
        if ShowTSO:
            box.delete(floutbox[1])
            line.delete(dev01posline_flout[1])
            line.delete(dev01negline_flout[1])
            line.delete(dev02posline_flout[1])
            line.delete(dev02negline_flout[1])
            line.delete(dev03posline_flout[1])
            line.delete(dev03negline_flout[1])
            line.delete(dev04posline_flout[1])
            line.delete(dev04negline_flout[1])
        if ShowFLOUT:
            floutbox = box.new(floutOpenTime, flout_hi, floutEndTime, flout_lo, color.new(FLOUTBoxCol, 90), 1, line.style_solid, extend.none, xloc.bar_time, color.new(FLOUTBoxCol, 90), txt7, size.auto, color.new(box_text_flout_col, 80), text_wrap=text.wrap_auto)
            if dayofweek == dayofweek.friday:
                box.set_right(floutbox, floutOpenTime + 201600000)
                line.set_x2(flout_hi_line, floutOpenTime + 201600000)
                line.set_x2(flout_lo_line, floutOpenTime + 201600000)
        if box_text_cbdr == False:
            box.set_text(floutbox, '')
        if ShowDev and ShowFLOUT and bool_flout_dev:
            for i in pine_range(0.5, DevCount, 0.5):
                if i == 0.5:
                    dev01posline_flout = line.new(floutOpenTime, flout_hi + flout_diff * i, floutEndTime, flout_hi + flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev01negline_flout = line.new(floutOpenTime, flout_hi - flout_diff * i, floutEndTime, flout_lo - flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev01posline_flout, floutOpenTime + 201600000)
                        line.set_x2(dev01negline_flout, floutOpenTime + 201600000)
                if i == 1:
                    dev02posline_flout = line.new(floutOpenTime, flout_hi + flout_diff * i, floutEndTime, flout_lo + flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev02negline_flout = line.new(floutOpenTime, flout_hi - flout_diff * i, floutEndTime, flout_lo - flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev02posline_flout, floutOpenTime + 201600000)
                        line.set_x2(dev02negline_flout, floutOpenTime + 201600000)
                if i == 1.5:
                    dev03posline_flout = line.new(floutOpenTime, flout_hi + flout_diff * i, floutEndTime, flout_lo + flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev03negline_flout = line.new(floutOpenTime, flout_hi - flout_diff * i, floutEndTime, flout_lo - flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev03posline_flout, floutOpenTime + 201600000)
                        line.set_x2(dev03negline_flout, floutOpenTime + 201600000)
                if i == 2:
                    dev04posline_flout = line.new(floutOpenTime, flout_hi + flout_diff * i, floutEndTime, flout_lo + flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    dev04negline_flout = line.new(floutOpenTime, flout_hi - flout_diff * i, floutEndTime, flout_lo - flout_diff * i, xloc=xloc.bar_time, color=DevLNCol, style=DEVLSS, width=DEVLW)
                    if dayofweek == dayofweek.friday:
                        line.set_x2(dev04posline_flout, floutOpenTime + 201600000)
                        line.set_x2(dev04negline_flout, floutOpenTime + 201600000)
    elif cast_bool(FLOUTTime):
        flout_hi = math.max(high, flout_hi)
        flout_lo = math.min(low, flout_lo)
        flout_diff = flout_hi - flout_lo
        for i in pine_range(0.5, DevCount, 0.5):
            if i == 0.5 and ShowDev:
                line.set_y1(dev01posline_flout, flout_hi + flout_diff * i)
                line.set_y2(dev01posline_flout, flout_hi + flout_diff * i)
                line.set_y1(dev01negline_flout, flout_lo - flout_diff * i)
                line.set_y2(dev01negline_flout, flout_lo - flout_diff * i)
            if i == 1 and ShowDev:
                line.set_y1(dev02posline_flout, flout_hi + flout_diff * i)
                line.set_y2(dev02posline_flout, flout_hi + flout_diff * i)
                line.set_y1(dev02negline_flout, flout_lo - flout_diff * i)
                line.set_y2(dev02negline_flout, flout_lo - flout_diff * i)
            if i == 1.5 and ShowDev:
                line.set_y1(dev03posline_flout, flout_hi + flout_diff * i)
                line.set_y2(dev03posline_flout, flout_hi + flout_diff * i)
                line.set_y1(dev03negline_flout, flout_lo - flout_diff * i)
                line.set_y2(dev03negline_flout, flout_lo - flout_diff * i)
            if i == 2 and ShowDev:
                line.set_y1(dev04posline_flout, flout_hi + flout_diff * i)
                line.set_y2(dev04posline_flout, flout_hi + flout_diff * i)
                line.set_y1(dev04negline_flout, flout_lo - flout_diff * i)
                line.set_y2(dev04negline_flout, flout_lo - flout_diff * i)
        if flout_hi > flout_hi[1]:
            box.set_top(floutbox, flout_hi)
        if flout_lo < flout_lo[1]:
            box.set_bottom(floutbox, flout_lo)
    if DevDirection == 'Upside Only':
        line.delete(dev01negline_flout)
        line.delete(dev02negline_flout)
        line.delete(dev03negline_flout)
        line.delete(dev04negline_flout)
    elif DevDirection == 'Downside Only':
        line.delete(dev01posline_flout)
        line.delete(dev02posline_flout)
        line.delete(dev03posline_flout)
        line.delete(dev04posline_flout)
    cbdrpipc = toWhole(cbdr_diff)
    asiapipc = toWhole(asia_diff)
    cbdr_cellt_col: Persistent[Color] = na(Color)
    asia_cellt_col: Persistent[Color] = na(Color)
    L_profile_col: Persistent[Color] = na(Color)
    comp_green: Persistent[Color] = color.new(color.new('#1CAC78'), 0)
    comp_red: Persistent[Color] = color.new(color.new('#FF4040'), 0)
    comp_gray: Persistent[Color] = color.new(color.new('#808080'), 0)
    L_Profile: Persistent[str] = ''
    if cbdrpipc > 15 and cbdrpipc < 40:
        cbdr_cellt_col = color.new(color.new('#1CAC78'), 0)
    else:
        cbdr_cellt_col = color.new(color.new('#FF4040'), 0)
    if asiapipc >= 20 and asiapipc <= 40:
        asia_cellt_col = color.new(color.new('#1CAC78'), 0)
    else:
        asia_cellt_col = color.new(color.new('#FF4040'), 0)
    if cbdrpipc > 15 and cbdrpipc < 40:
        L_Profile = 'CBDR'
        L_profile_col = Tab1txtCol
    elif asiapipc >= 20 and asiapipc <= 40:
        L_Profile = 'ASIA'
        L_profile_col = Tab1txtCol
    else:
        L_Profile = 'FLOUT'
        L_profile_col = Tab1txtCol
    if BarInSession(midsesh) and Auto_Select == True and (syminfo.type == 'forex'):
        if cbdrpipc > 15 and cbdrpipc < 40:
            box.delete(asia_box)
            line.delete(dev01posline_asia)
            line.delete(dev01negline_asia)
            line.delete(dev02posline_asia)
            line.delete(dev02negline_asia)
            line.delete(dev03posline_asia)
            line.delete(dev03negline_asia)
            line.delete(dev04posline_asia)
            line.delete(dev04negline_asia)
            box.delete(floutbox)
            line.delete(dev01posline_flout)
            line.delete(dev01negline_flout)
            line.delete(dev02posline_flout)
            line.delete(dev02negline_flout)
            line.delete(dev03posline_flout)
            line.delete(dev03negline_flout)
            line.delete(dev04posline_flout)
            line.delete(dev04negline_flout)
        elif asiapipc >= 20 and asiapipc <= 40:
            box.delete(cbdrbox)
            line.delete(dev01posline)
            line.delete(dev01negline)
            line.delete(dev02posline)
            line.delete(dev02negline)
            line.delete(dev03posline)
            line.delete(dev03negline)
            line.delete(dev04posline)
            line.delete(dev04negline)
            box.delete(floutbox)
            line.delete(dev01posline_flout)
            line.delete(dev01negline_flout)
            line.delete(dev02posline_flout)
            line.delete(dev02negline_flout)
            line.delete(dev03posline_flout)
            line.delete(dev03negline_flout)
            line.delete(dev04posline_flout)
            line.delete(dev04negline_flout)
        else:
            box.delete(cbdrbox)
            line.delete(dev01posline)
            line.delete(dev01negline)
            line.delete(dev02posline)
            line.delete(dev02negline)
            line.delete(dev03posline)
            line.delete(dev03negline)
            line.delete(dev04posline)
            line.delete(dev04negline)
            box.delete(asia_box)
            line.delete(dev01posline_asia)
            line.delete(dev01negline_asia)
            line.delete(dev02posline_asia)
            line.delete(dev02negline_asia)
            line.delete(dev03posline_asia)
            line.delete(dev03negline_asia)
            line.delete(dev04posline_asia)
            line.delete(dev04negline_asia)
    ICTInfo: Persistent[Table] = table.new(tabinp1, 2, 3, border_width=1)
    if barstate.islast and syminfo.type == 'forex' and Stats and DOM and (dayofweek != dayofweek.sunday):
        CBDR_cell: str = 'CBDR '
        Asia_cell: str = 'Asian Range '
        CBDR_cell_pipc = '     ' + string.tostring(cbdrpipc) + ' pips'
        ASIA_cell_pipc = '     ' + string.tostring(asiapipc) + ' pips'
        if L_Prof == True:
            table.cell(ICTInfo, 0, 0, text=' Suggested SD ', bgcolor=CellBG, text_color=Tab1txtCol, text_halign=text.align_left, text_size=size.auto)
        table.cell(ICTInfo, 0, 1, text=' Asian Range ', bgcolor=CellBG, text_color=Tab1txtCol, text_halign=text.align_left, text_size=size.auto)
        table.cell(ICTInfo, 0, 2, text=' CBDR ', bgcolor=CellBG, text_color=Tab1txtCol, text_halign=text.align_left, text_size=size.auto)
        if L_Prof == True:
            table.cell(ICTInfo, 1, 0, text=' ' + L_Profile + ' ', bgcolor=CellBG, text_color=L_profile_col, text_halign=text.align_right, text_size=size.auto)
        table.cell(ICTInfo, 1, 1, text=ASIA_cell_pipc, bgcolor=CellBG, text_color=asia_cellt_col, text_size=size.auto, text_halign=text.align_right)
        table.cell(ICTInfo, 1, 2, text=CBDR_cell_pipc, bgcolor=CellBG, text_color=cbdr_cellt_col, text_size=size.auto, text_halign=text.align_right)
    Option1CC: Persistent[Color] = na(Color)
    Option2CC: Persistent[Color] = na(Color)
    Option3CC: Persistent[Color] = na(Color)
    Option4CC: Persistent[Color] = na(Color)
    if BIASOption1 == 'Bullish':
        Option1CC = comp_green
    elif BIASOption1 == 'Bearish':
        Option1CC = comp_red
    else:
        Option1CC = Tab2txtCol
    if BIASOption2 == 'Bullish':
        Option2CC = comp_green
    elif BIASOption2 == 'Bearish':
        Option2CC = comp_red
    else:
        Option2CC = Tab2txtCol
    if BIASOption3 == 'Bullish':
        Option3CC = comp_green
    elif BIASOption3 == 'Bearish':
        Option3CC = comp_red
    else:
        Option3CC = Tab2txtCol
    if BIASOption4 == 'Bullish':
        Option4CC = comp_green
    elif BIASOption4 == 'Bearish':
        Option4CC = comp_red
    else:
        Option4CC = Tab2txtCol
    BIAS_Table: Persistent[Table] = table.new(tabinp2, 2, 20, bgcolor=TableBG2, border_width=1)
    if barstate.islast and BIAS_M_Bool:
        if BIASbool1:
            table.cell(BIAS_Table, 0, 1, text=txt52, text_color=Tab2txtCol, text_halign=text.align_left)
            table.cell(BIAS_Table, 1, 1, text=BIASOption1, text_size=size.normal, text_color=Option1CC, text_halign=text.align_right)
        if BIASbool2:
            table.cell(BIAS_Table, 0, 2, text=txt53, text_color=Tab2txtCol, text_halign=text.align_left)
            table.cell(BIAS_Table, 1, 2, text=BIASOption2, text_size=size.normal, text_color=Option2CC, text_halign=text.align_right)
        if BIASbool3:
            table.cell(BIAS_Table, 0, 3, text=txt54, text_color=Tab2txtCol, text_halign=text.align_left)
            table.cell(BIAS_Table, 1, 3, text=BIASOption3, text_size=size.normal, text_color=Option3CC, text_halign=text.align_right)
        if BIASbool4:
            table.cell(BIAS_Table, 0, 4, text=txt55, text_color=Tab2txtCol, text_halign=text.align_left)
            table.cell(BIAS_Table, 1, 4, text=BIASOption4, text_size=size.normal, text_color=Option4CC, text_halign=text.align_right)
    NOTES_Table: Persistent[Table] = table.new(tabinp3, 1, 20, bgcolor=TableBG2, border_width=1)
    if barstate.islast and NOTES_M_Bool:
        table.cell(NOTES_Table, 0, 0, text=notes, text_size=size.normal, text_color=Tab3txtCol, text_halign=text.align_center)
    txtMon: str = 'M O N'
    txtTue: str = 'T U E'
    txtWed: str = 'W E D'
    txtThu: str = 'T H U'
    txtFri: str = 'F R I'
    txtSat: str = 'S A T'
    txtSun: str = 'S U N'
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.monday) if showDOW and DOM and SL4W and Last4Weeks and (not ShowTWO) else False, offset=0, char='\xa0', text=txtMon, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.tuesday) if showDOW and DOM and SL4W and Last4Weeks and (not ShowTWO) else False, offset=0, char='\xa0', text=txtTue, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.wednesday) if showDOW and DOM and SL4W and Last4Weeks and (not ShowTWO) else False, offset=0, char='\xa0', text=txtWed, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.thursday) if showDOW and DOM and SL4W and Last4Weeks and (not ShowTWO) else False, offset=0, char='\xa0', text=txtThu, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.friday) if showDOW and DOM and SL4W and Last4Weeks and (not ShowTWO) else False, offset=0, char='\xa0', text=txtFri, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.monday) if showDOW and DOM and ShowTWO and thisweek else False, offset=0, char='\xa0', text=txtMon, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.tuesday) if showDOW and DOM and ShowTWO and thisweek else False, offset=0, char='\xa0', text=txtTue, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.wednesday) if showDOW and DOM and ShowTWO and thisweek else False, offset=0, char='\xa0', text=txtWed, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.thursday) if showDOW and DOM and ShowTWO and thisweek else False, offset=0, char='\xa0', text=txtThu, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.friday) if showDOW and DOM and ShowTWO and thisweek else False, offset=0, char='\xa0', text=txtFri, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.monday) if showDOW and DOM and (not ShowTWO) and (not SL4W) else False, offset=0, char='\xa0', text=txtMon, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.tuesday) if showDOW and DOM and (not ShowTWO) and (not SL4W) else False, offset=0, char='\xa0', text=txtTue, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.wednesday) if showDOW and DOM and (not ShowTWO) and (not SL4W) else False, offset=0, char='\xa0', text=txtWed, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.thursday) if showDOW and DOM and (not ShowTWO) and (not SL4W) else False, offset=0, char='\xa0', text=txtThu, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    plotchar(hour == DOWTime and minute == 0 and (dayofweek == dayofweek.friday) if showDOW and DOM and (not ShowTWO) and (not SL4W) else False, offset=0, char='\xa0', text=txtFri, color=color.new(i_DOWCol, 100), location=DOWLoc, textcolor=i_DOWCol, editable=False)
    daycount: Persistent[int] = 0
    SL4WC: Persistent[int] = 0
    if SL4W == True:
        if dayofweek == dayofweek.monday:
            SL4WC = 0 + 28
        if dayofweek == dayofweek.tuesday:
            SL4WC = 1 + 28
        if dayofweek == dayofweek.wednesday:
            SL4WC = 2 + 28
        if dayofweek == dayofweek.thursday:
            SL4WC = 3 + 28
        if dayofweek == dayofweek.friday:
            SL4WC = 4 + 28
        if dayofweek == dayofweek.saturday:
            SL4WC = 5 + 28
        if dayofweek == dayofweek.sunday:
            SL4WC = 6 + 28
    if SL4W:
        Cleanup(SL4WC)
    if ShowTWO:
        if dayofweek == dayofweek.monday:
            daycount = 0
        if dayofweek == dayofweek.tuesday:
            daycount = 1
        if dayofweek == dayofweek.wednesday:
            daycount = 2
        if dayofweek == dayofweek.thursday:
            daycount = 3
        if dayofweek == dayofweek.friday:
            daycount = 4
        if dayofweek == dayofweek.saturday:
            daycount = 5
        if dayofweek == dayofweek.sunday:
            daycount = 6
    if ShowTWO:
        Cleanup(daycount)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
