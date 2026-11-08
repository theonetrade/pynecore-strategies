"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, barcolor, barmerge, barstate, close, color,
    dayofmonth, extend, fill, format, high, input, label, line, low, month, na, open, plot,
    request, script, string, syminfo, ta, table, text, time, time_close, timeframe, timenow,
    volume, weekofyear, xloc, year
)
from pynecore.types import Box, Persistent, Series, Table
import lib.TradersReality.Traders_Reality_Lib.v2 as trLib


@script.indicator(title='Traders Reality Main', shorttitle='TR_MAIN', overlay=True, max_bars_back=300, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    labelOffsetInput=input.int(group='Label offsets', title='General', defval=12, inline='labeloffset1'),
    pivotOffsetInput=input.int(group='Label offsets', title='Pivots', defval=6, inline='labeloffset1'),
    adrOffsetInput=input.int(group='Label offsets', title='ADR', defval=12, inline='labeloffset1'),
    adrOffsetInput50=input.int(group='Label offsets', title='50% ADR', defval=12, inline='labeloffset1'),
    rdOffsetInput=input.int(group='Label offsets', title='RD/W', defval=24, inline='labeloffset1'),
    rdOffsetInput50=input.int(group='Label offsets', title='50% RD/W', defval=24, inline='labeloffset1'),
    redVectorColor=input.color(title='Vector: Red', group='PVSRA Colors', defval=color.red, inline='vectors'),
    greenVectorColor=input.color(title='Green', group='PVSRA Colors', defval=color.lime, inline='vectors'),
    violetVectorColor=input.color(title='Violet', group='PVSRA Colors', defval=color.fuchsia, inline='vectors'),
    blueVectorColor=input.color(title='Blue', group='PVSRA Colors', defval=color.blue, inline='vectors', tooltip='Bull bars are green and bear bars are red when the bar is with volume >= 200% of the average volume of the 10 previous bars, or bars where the product of candle spread x candle volume is >= the highest for the 10 previous bars.\n Bull bars are blue and bear are violet when the bar is with with volume >= 150% of the average volume of the 10 previous bars.'),
    regularCandleUpColor=input.color(title='Regular: Up Candle', group='PVSRA Colors', defval=color.new('#999999'), inline='nonVectors'),
    regularCandleDownColor=input.color(title='Down Candle', group='PVSRA Colors', defval=color.new('#4D4D4D'), inline='nonVectors', tooltip='Bull bars are light gray and bear are dark gray when none of the red/green/blue/violet vector conditions are met.'),
    showEmas=input.bool(group='EMAs', title='Show EMAs?', defval=True, inline='showemas'),
    labelEmas=input.bool(group='EMAs', title='EMA Labels?', defval=False, inline='showemas'),
    oneEmaColor=input.color(group='EMAs', title='EMA Color: 5', defval=color.rgb(254, 234, 74, 0), inline='emacolors'),
    twoEmaColor=input.color(group='EMAs', title='13', defval=color.rgb(253, 84, 87, 0), inline='emacolors'),
    threeEmaColor=input.color(group='EMAs', title='50', defval=color.rgb(31, 188, 211, 0), inline='emacolors'),
    fourEmaColor=input.color(group='EMAs', title='200', defval=color.rgb(255, 255, 255, 0), inline='emacolors'),
    fiveEmaColor=input.color(group='EMAs', title='800', defval=color.rgb(50, 34, 144, 0), inline='emacolors'),
    emaCloudColor=input.color(group='EMAs', title='EMA Cloud', defval=color.rgb(155, 47, 174, 60), inline='emacloud'),
    emaCloudBorderColor=input.color(group='EMAs', title='Border', defval=color.rgb(18, 137, 123, 100), inline='emacloud'),
    showLevelOnePivotPoints=input.bool(group='Pivot Points', title='Show Level: 1 R/S?', defval=False, inline='pivotlevels'),
    showLevelTwoPivotPoints=input.bool(group='Pivot Points', title='2 R/S?', defval=False, inline='pivotlevels'),
    showLevelThreePivotPoints=input.bool(group='Pivot Points', title=' 3 R/S?', defval=False, inline='pivotlevels'),
    showPivotLabels=input.bool(group='Pivot Points', title='Show labels?', defval=True, inline='pivotlevels'),
    rsStyleX=input.string(group='Pivot Points', defval='Dashed', title='R/S Levels Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='pivotcolorsRS'),
    activeM=input.bool(group='Pivot Points', title='Show M levels?', defval=True, inline='mlevels'),
    showMLabels=input.bool(group='Pivot Points', title='Labels?', defval=True, inline='mlevels'),
    extendPivots=input.bool(group='Pivot Points', title='Extend lines in both directions?', defval=False),
    pivotColor=input.color(group='Pivot Points', title='Colors: Pivot Point', defval=color.rgb(254, 234, 78, 50), inline='pivotcolors'),
    pivotLabelColor=input.color(group='Pivot Points', title='Pivot Point Label', defval=color.rgb(254, 234, 78, 50), inline='pivotcolors'),
    mColor=input.color(group='Pivot Points', title='Colors: M Levels', defval=color.rgb(255, 255, 255, 50), inline='pivotcolors1'),
    mLabelColor=input.color(group='Pivot Points', title='M Levels Label', defval=color.rgb(255, 255, 255, 50), inline='pivotcolors1'),
    mStyleX=input.string(group='Pivot Points', defval='Dashed', title='M Levels Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='pivotcolors2'),
    showDayHighLow=input.bool(group='Yesterday\'s and Last Week\'s High/low', title='Show Hi/Lo: Daily?', defval=True, inline='highlow'),
    showWeekHighLow=input.bool(group='Yesterday\'s and Last Week\'s High/low', title='Weekly?', defval=True, inline='highlow'),
    showDayHighLowLabels=input.bool(group='Yesterday\'s and Last Week\'s High/low', title='Show labels?', defval=True, inline='highlow'),
    showADR=input.bool(group='Average Daily Range - ADR', title='Show ADR?', defval=True, inline='adr'),
    showADRDO=input.bool(group='Average Daily Range - ADR', title='Use Daily Open (DO) calc?', defval=False, inline='adr', tooltip='Measure the ADR from the daily open. This will make the ADR static throughout the day. ADR is usually measured taking today high and low. Since todays high and low will change throughout the day, some might prefer to have a static range instead.'),
    showADRLabels=input.bool(group='Average Daily Range - ADR', title='Labels?', defval=True, inline='adr1'),
    showADRRange=input.bool(group='Average Daily Range - ADR', title='Range label?', defval=False, inline='adr1'),
    showADR50=input.bool(group='Average Daily Range - ADR', title='Show 50% ADR?', defval=False, inline='adr1'),
    aDRRange=input.int(group='Average Daily Range - ADR', title='ADR length (days)?', defval=14, minval=1, maxval=31, step=1, inline='adr2', tooltip='Defaults taken from mt4. This defines how many days back to take into consideration when calculating the ADR'),
    adrColor=input.color(group='Average Daily Range - ADR', title='ADR Color', defval=color.new(color.silver, 50), inline='adr3'),
    adrStyleX=input.string(group='Average Daily Range - ADR', defval='Dotted', title='ADR Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='adr3'),
    showAWR=input.bool(group='Average Weekly Range - AWR', title='Show AWR?', defval=False, inline='awr'),
    showAWRWO=input.bool(group='Average Weekly Range - AWR', title='Use Weekly Open (WO) calc?', defval=False, inline='awr', tooltip='Measure the AWR from the weekly open. This will make the AWR static throughout the week. AWR is usually measured taking this weeks high and low. Since this weeks high and low will change throughout the week, some might prefer to have a static range instead.'),
    showAWRLabels=input.bool(group='Average Weekly Range - AWR', title='Labels?', defval=True, inline='awr1'),
    showAWRRange=input.bool(group='Average Weekly Range - AWR', title='Range label?', defval=False, inline='awr1'),
    showAWR50=input.bool(group='Average Weekly Range - AWR', title='Show 50% AWR?', defval=False, inline='awr1'),
    aWRRange=input.int(group='Average Weekly Range - AWR', title='AWR length (weeks)?', defval=4, minval=1, maxval=52, step=1, inline='awr2', tooltip='Defaults taken from mt4. This defines how many weeks back to take into consideration when calculating the AWR'),
    awrColor=input.color(group='Average Weekly Range - AWR', title='AWR Color', defval=color.new(color.orange, 50), inline='awr3'),
    awrStyleX=input.string(group='Average Weekly Range - AWR', defval='Dotted', title='AWR Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='awr3'),
    showAMR=input.bool(group='Average Monthly Range - AMR', title='Show AMR?', defval=False, inline='amr'),
    showAMRMO=input.bool(group='Average Monthly Range - AMR', title='Use Monthly Open (MO) calc?', defval=False, inline='amr', tooltip='Measure the AMR from the monthly open. This will make the AMR static throughout the month. AMR is usually measured taking this months high and low. Since this months high and low will change throughout the month, some might prefer to have a static range instead.'),
    showAMRLabels=input.bool(group='Average Monthly Range - AMR', title='Labels?', defval=True, inline='amr1'),
    showAMRRange=input.bool(group='Average Monthly Range - AMR', title='Range label?', defval=False, inline='amr1'),
    showAMR50=input.bool(group='Average Monthly Range - AMR', title='Show 50% AMR?', defval=False, inline='amr1'),
    aMRRange=input.int(group='Average Monthly Range - AMR', title='AMR length (months)?', defval=6, minval=1, maxval=12, step=1, inline='amr2', tooltip='Defaults taken from mt4. This defines how many months back to take into consideration when calculating the AMR'),
    amrColor=input.color(group='Average Monthly Range - AMR', title='AMR Color', defval=color.new(color.red, 50), inline='amr3'),
    amrStyleX=input.string(group='Average Monthly Range - AMR', defval='Dotted', title='AMR Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='amr3'),
    showRD=input.bool(group='Range Daily Hi/Lo - RD Hi/Lo', title='Show RD?', defval=False, inline='rd'),
    showRDDO=input.bool(group='Range Daily Hi/Lo - RD Hi/Lo', title='Use Daily Open (DO) calc?', defval=False, inline='rd', tooltip='Measure the RD from the daily open. This will make the RD static throughout the day. RD is usually measured taking todays high and low. Since today high and low will change throughout the day, some might prefer to have a static range instead.'),
    showRDLabels=input.bool(group='Range Daily Hi/Lo - RD Hi/Lo', title='Labels?', defval=True, inline='rd1'),
    showRDRange=input.bool(group='Range Daily Hi/Lo - RD Hi/Lo', title='Range label?', defval=False, inline='rd1'),
    showRD50=input.bool(group='Range Daily Hi/Lo - RD Hi/Lo', title='Show 50% RD?', defval=False, inline='rd1'),
    rdRange=input.int(group='Range Daily Hi/Lo - RD Hi/Lo', title='RD length (days)?', defval=15, minval=1, maxval=31, step=1, inline='rd2', tooltip='Defaults taken from Trader At Home PVSRA documentation. This defines how many days back to take into consideration when calculating the RD'),
    rdColor=input.color(group='Range Daily Hi/Lo - RD Hi/Lo', title='RD Color', defval=color.new(color.red, 30), inline='rd3'),
    rdStyleX=input.string(group='Range Daily Hi/Lo - RD Hi/Lo', defval='Solid', title='RD Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='rd3'),
    showRW=input.bool(group='Range Weekly Hi/Lo - RW Hi/Lo', title='Show RW?', defval=False, inline='rw'),
    showRWWO=input.bool(group='Range Weekly Hi/Lo - RW Hi/Lo', title='Use Weekly Open (WO) calc?', defval=False, inline='rw', tooltip='Measure the RW from the weekly open. This will make the RW static throughout the week. RW is usually measured taking this weeks high and low. Since this weeks high and low will change throughout the week, some might prefer to have a static range instead.'),
    showRWLabels=input.bool(group='Range Weekly Hi/Lo - RW Hi/Lo', title='Labels?', defval=True, inline='rw1'),
    showRWRange=input.bool(group='Range Weekly Hi/Lo - RW Hi/Lo', title='Range label?', defval=False, inline='rw1'),
    showRW50=input.bool(group='Range Weekly Hi/Lo - RW Hi/Lo', title='Show 50% RW?', defval=False, inline='rw1'),
    rwRange=input.int(group='Range Weekly Hi/Lo - RW Hi/Lo', title='RW length (weeks)?', defval=13, minval=1, maxval=52, step=1, inline='rw2', tooltip='Defaults taken from Trader At Home PVSRA documentation. This defines how many weeks back to take into consideration when calculating the RW'),
    rwColor=input.color(group='Range Weekly Hi/Lo - RW Hi/Lo', title='RW Color', defval=color.new(color.blue, 30), inline='rw3'),
    rwStyleX=input.string(group='Range Weekly Hi/Lo - RW Hi/Lo', defval='Solid', title='RW Line Style', options=('Dotted', 'Dashed', 'Solid'), inline='rw3'),
    showAdrTable=input.bool(group='ADR/ADRx3/AWR/AMR Table', title='Show ADR Table', inline='adrt', defval=True),
    __input_78__=input.bool(group='ADR/ADRx3/AWR/AMR Table', title='Show ADR PIPS', inline='adrt', defval=True),
    __input_79__=input.bool(group='ADR/ADRx3/AWR/AMR Table', title='Show ADR Currency', inline='adrt', defval=False),
    __input_80__=input.bool(group='ADR/ADRx3/AWR/AMR Table', title='Show RD PIPS', inline='adrt', defval=False),
    __input_81__=input.bool(group='ADR/ADRx3/AWR/AMR Table', title='Show RD Currency', inline='adrt', defval=False),
    choiceAdrTable=input.string(group='ADR/ADRx3/AWR/AMR Table', title='ADR Table postion', inline='adrt', defval='top_right', options=('top_right', 'top_left', 'top_center', 'bottom_right', 'bottom_left', 'bottom_center')),
    adrTableBgColor=input.color(group='ADR/ADRx3/AWR/AMR Table', title='ADR Table: Background Color', inline='adrtc', defval=color.rgb(93, 96, 107, 70)),
    adrTableTxtColor=input.color(group='ADR/ADRx3/AWR/AMR Table', title='Text Color', inline='adrtc', defval=color.rgb(31, 188, 211, 0)),
    __input_85__=input.bool(group='Daily Open', defval=True, title='Show: line ?', inline='dopenconf'),
    __input_86__=input.bool(group='Daily Open', defval=True, title='Label?', inline='dopenconf'),
    showallDly=input.bool(group='Daily Open', defval=False, title='Show historical daily opens?', inline='dopenconf'),
    sess9col=input.color(group='Daily Open', title='Daily Open Color', defval=color.rgb(254, 234, 78, 0), inline='dopenconf1'),
    overrideSym=input.bool(group='PVSRA Override', title='Override chart symbol?', defval=False, inline='pvsra'),
    pvsraSym=input.string(group='PVSRA Override', title='', defval='INDEX:BTCUSD', tooltip='You can use INDEX:BTCUSD or you can combine multiple feeds, for example BINANCE:BTCUSDT+COINBASE:BTCUSD. Note that adding too many will slow things down.', inline='pvsra'),
    showVCZ=input.bool(True, 'Show VCZ?', group='Vector Candle Zones', inline='vczOn'),
    zonesMax=input.int(500, 'Maximum zones to draw', group='Vector Candle Zones', inline='vczOn'),
    zoneType=input.string(group='Vector Candle Zones', defval='Body only', title='Zone top/bottom is defined with: ', options=('Body only', 'Body with wicks')),
    zoneUpdateType=input.string(group='Vector Candle Zones', defval='Body with wicks', title='Zones are cleared using candle: ', options=('Body only', 'Body with wicks')),
    borderWidth=input.int(0, 'Zone border width', group='Vector Candle Zones'),
    colorOverride=input.bool(True, 'Override color?', group='Vector Candle Zones', inline='vcz1'),
    zoneColor=input.color(title='Color', group='Vector Candle Zones', defval=color.rgb(255, 230, 75, 90), inline='vcz1', tooltip='the vector candle zones color to use if you dont not want to use the PVSRA Candle Colors.'),
    transperancy=input.int(90, 'Zone Transperancy', minval=0, maxval=100, group='Vector Candle Zones', tooltip='If the vector candle zones color is not overriden, then we want to set the transparancy of the vector candle colors as defined by the PBSRA candle colors. This setting only affects the candle zone colors not the candle colors themselves.'),
    rectStyle=input.string(group='Market sessions', defval='Dashed', title='Line style of Market Session hi/lo line', options=('Dashed', 'Solid')),
    __input_100__=input.bool(True, group='Market sessions', title='Show Market Sessions?', tooltip='Turn on or off all market sessions'),
    __input_101__=input.bool(False, group='Market sessions', title='Show Market Session on Weekends?', tooltip='Turn on or off market sessions in the weekends. Note do not turn this on for exchanges that dont have weekend data like OANDA'),
    __input_102__=input.bool(group='Market session: London (0800-1630 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session1conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_103__=input.bool(group='Market session: London (0800-1630 UTC+0) - DST Aware', defval=True, title='Label?', inline='session1conf'),
    __input_104__=input.bool(group='Market session: London (0800-1630 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session1conf', tooltip='This controls the shaded area for the session'),
    sess1Label=input.string(group='Market session: London (0800-1630 UTC+0) - DST Aware', defval='London', title='Name:', inline='session1style'),
    sess1col=input.color(group='Market session: London (0800-1630 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(120, 123, 134, 75), inline='session1style'),
    sess1colLabel=input.color(group='Market session: London (0800-1630 UTC+0) - DST Aware', title='Label', defval=color.rgb(120, 123, 134, 0), inline='session1style'),
    __input_108__=input.bool(group='Market session: New York (1430-2100 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session2conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_109__=input.bool(group='Market session: New York (1430-2100 UTC+0) - DST Aware', defval=True, title='Label?', inline='session2conf'),
    __input_110__=input.bool(group='Market session: New York (1430-2100 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session2conf', tooltip='This controls the shaded area for the session'),
    sess2Label=input.string(group='Market session: New York (1430-2100 UTC+0) - DST Aware', defval='NewYork', title='Name:', inline='session2style'),
    sess2col=input.color(group='Market session: New York (1430-2100 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(251, 86, 91, 75), inline='session2style'),
    sess2colLabel=input.color(group='Market session: New York (1430-2100 UTC+0) - DST Aware', title='Label', defval=color.rgb(253, 84, 87, 25), inline='session2style'),
    __input_114__=input.bool(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session3conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_115__=input.bool(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', defval=True, title='Label?', inline='session3conf'),
    __input_116__=input.bool(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session3conf', tooltip='This controls the shaded area for the session'),
    sess3Label=input.string(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', defval='Tokyo', title='Name:', inline='session3style'),
    sess3col=input.color(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(80, 174, 85, 75), inline='session3style'),
    sess3colLabel=input.color(group='Market session: Tokyo (0000-0600 UTC+0) - DST Aware', title='Label', defval=color.rgb(80, 174, 85, 25), inline='session3style'),
    __input_120__=input.bool(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session4conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_121__=input.bool(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', defval=True, title='Label?', inline='session4conf'),
    __input_122__=input.bool(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session4conf', tooltip='This controls the shaded area for the session'),
    sess4Label=input.string(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', defval='HongKong', title='Name:', inline='session4style'),
    sess4col=input.color(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(128, 127, 23, 75), inline='session4style'),
    sess4colLabel=input.color(group='Market session: Hong Kong (0130-0800 UTC+0) - DST Aware', title='Label', defval=color.rgb(128, 127, 23, 25), inline='session4style'),
    __input_126__=input.bool(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session5conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_127__=input.bool(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', defval=True, title='Label?', inline='session5conf'),
    __input_128__=input.bool(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session5conf', tooltip='This controls the shaded area for the session'),
    sess5Label=input.string(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', defval='Sydney', title='Name:', inline='session5style'),
    sess5col=input.color(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(37, 228, 123, 75), inline='session5style'),
    sess5colLabel=input.color(group='Market session: Sydney (NZX+ASX 2200-0600 UTC+0) - DST Aware', title='Label', defval=color.rgb(37, 228, 123, 25), inline='session5style'),
    __input_132__=input.bool(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session6conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_133__=input.bool(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', defval=True, title='Label?', inline='session6conf'),
    __input_134__=input.bool(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session6conf', tooltip='This controls the shaded area for the session'),
    sess6Label=input.string(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', defval='EU Brinks', title='Name:', inline='session6style'),
    sess6col=input.color(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(255, 255, 255, 65), inline='session6style'),
    sess6colLabel=input.color(group='Market session: EU Brinks (0800-0900 UTC+0) - DST Aware', title='Label', defval=color.rgb(255, 255, 255, 25), inline='session6style'),
    __input_138__=input.bool(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', defval=True, title='Show: session?', inline='session7conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_139__=input.bool(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', defval=True, title='Label?', inline='session7conf'),
    __input_140__=input.bool(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session7conf', tooltip='This controls the shaded area for the session'),
    sess7Label=input.string(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', defval='US Brinks', title='Name:', inline='session7style'),
    sess7col=input.color(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(255, 255, 255, 65), inline='session7style'),
    sess7colLabel=input.color(group='Market session: US Brinks (1400-1500 UTC+0) - DST Aware', title='Label', defval=color.rgb(255, 255, 255, 25), inline='session7style'),
    __input_144__=input.bool(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', defval=False, title='Show: session?', inline='session8conf', tooltip='If this checkbox is off, Label and Open Range have no effect'),
    __input_145__=input.bool(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', defval=True, title='Label?', inline='session8conf'),
    __input_146__=input.bool(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', defval=True, title='Opening Range?', inline='session8conf', tooltip='This controls the shaded area for the session'),
    sess8Label=input.string(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', defval='Frankfurt', title='Name:', inline='session8style'),
    sess8col=input.color(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', title='Color: Box', defval=color.rgb(253, 152, 39, 75), inline='session8style'),
    sess8colLabel=input.color(group='Market session: Frankfurt (0700-1630 UTC+0) - DST Aware', title='Label', defval=color.rgb(253, 152, 39, 25), inline='session8style'),
    __input_150__=input.bool(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', defval=True, title='Show: Levels?', inline='psyconf'),
    __input_151__=input.bool(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', defval=True, title='Labels?', inline='psyconf', tooltip='The Psy High/Low will only show on these timeframes: 1h/30min/15min/5min/3min/1min. It is disabled on all others. This is because the calculation requires a candle to start at the correct time for Sydney/Tokyo but in other timeframes the data does not have values at the designated time for the Sydney/Tokyo sessions.'),
    __input_152__=input.bool(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', defval=False, title='Show historical psy levels?', inline='psyconf'),
    psyColH=input.color(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', title='Psy Hi Color', defval=color.new(color.orange, 30), inline='psyconf1'),
    psyColL=input.color(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', title='Psy Low Color', defval=color.new(color.orange, 30), inline='psyconf1'),
    overridePsyType=input.bool(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', defval=False, title='Override PsyType', inline='psyconf12'),
    psyTypeX=input.string(group='Weekly Psy Levels (valid tf 1h/30min/15min/5min/3min/1min)', defval='crypto', title='Psy calc type', options=('crypto', 'forex'), inline='psyconf12', tooltip='Selecting the override psy type lets you manually adjust the psy type otherwise it will be automatic. If the override psy type checkbox is of then this setting has no effect. usAre you looking at Crypto or Forex? Crypto calculations start with the Sydney session on Saturday night. Forex calculations start with the Tokyo session on Monday morning. Note some exchanges like Oanda do not have sessions on the weekends so you might be forced to select Forex for exchanges like Oanda even when looking at symbols like BITCOIN on Oanda.'),
    showDstTable=input.bool(group='Daylight Saving Time Info (DST)', title='Show DST Table : ', inline='dstt', defval=False),
    choiceDstTable=input.string(group='Daylight Saving Time Info (DST)', title='DST Table postion', inline='dstt', defval='bottom_center', options=('top_right', 'top_left', 'top_center', 'bottom_right', 'bottom_left', 'bottom_center')),
    dstTableBgColor=input.color(group='Daylight Saving Time Info (DST)', title='DST Table: Background Color', inline='dsttc', defval=color.rgb(93, 96, 107, 70)),
    dstTableTxtColor=input.color(group='Daylight Saving Time Info (DST)', title='Text Color', inline='dsttc', defval=color.rgb(31, 188, 211, 0))
):
    rsStyle = line.style_dotted if rsStyleX == 'Dotted' else line.style_dashed if rsStyleX == 'Dashed' else line.style_solid if rsStyleX == 'Solid' else line.style_dashed
    mStyle = line.style_dotted if mStyleX == 'Dotted' else line.style_dashed if mStyleX == 'Dashed' else line.style_solid if mStyleX == 'Solid' else line.style_dashed
    dailyHiLoColor = color.new(color.blue, 50)
    weeklyHiLoColor = color.new(color.green, 60)
    adrStyle = line.style_dotted if adrStyleX == 'Dotted' else line.style_dashed if adrStyleX == 'Dashed' else line.style_solid if adrStyleX == 'Solid' else line.style_dotted
    awrStyle = line.style_dotted if awrStyleX == 'Dotted' else line.style_dashed if awrStyleX == 'Dashed' else line.style_solid if awrStyleX == 'Solid' else line.style_dotted
    amrStyle = line.style_dotted if amrStyleX == 'Dotted' else line.style_dashed if amrStyleX == 'Dashed' else line.style_solid if amrStyleX == 'Solid' else line.style_dotted
    rdStyle = line.style_dotted if rdStyleX == 'Dotted' else line.style_dashed if rdStyleX == 'Dashed' else line.style_solid if rdStyleX == 'Solid' else line.style_dotted
    rwStyle = line.style_dotted if rwStyleX == 'Dotted' else line.style_dashed if rwStyleX == 'Dashed' else line.style_solid if rwStyleX == 'Solid' else line.style_dotted
    showAdrPips = __input_78__ and showAdrTable
    showAdrCurrency = __input_79__ and showAdrTable
    showRDPips = __input_80__ and showAdrTable
    showRDCurrency = __input_81__ and showAdrTable
    show: bool = timeframe.isminutes and timeframe.multiplier <= 240 and (timeframe.multiplier >= 1)
    showDly: bool = timeframe.isminutes
    showRectangle9: bool = __input_85__ and showDly
    showLabel9: bool = __input_86__ and showRectangle9 and showDly
    showMarkets: bool = __input_100__ and show
    showMarketsWeekends: bool = __input_101__ and show
    weekendSessions: str = ':1234567'
    noWeekendSessions: str = ':23456'
    showRectangle1: bool = __input_102__ and showMarkets
    showLabel1: bool = __input_103__ and showRectangle1 and showMarkets
    showOr1: bool = __input_104__ and showRectangle1 and showMarkets
    sess1TimeX: str = '0800-1630'
    sess1Time = sess1TimeX + weekendSessions if showMarketsWeekends else sess1TimeX + noWeekendSessions
    showRectangle2: bool = __input_108__ and showMarkets
    showLabel2: bool = __input_109__ and showRectangle2 and showMarkets
    showOr2: bool = __input_110__ and showRectangle2 and showMarkets
    sess2TimeX: str = '1430-2100'
    sess2Time = sess2TimeX + weekendSessions if showMarketsWeekends else sess2TimeX + noWeekendSessions
    showRectangle3: bool = __input_114__ and showMarkets
    showLabel3: bool = __input_115__ and showRectangle3 and showMarkets
    showOr3: bool = __input_116__ and showRectangle3 and showMarkets
    sess3TimeX: str = '0000-0600'
    sess3Time = sess3TimeX + weekendSessions if showMarketsWeekends else sess3TimeX + noWeekendSessions
    showRectangle4: bool = __input_120__ and showMarkets
    showLabel4: bool = __input_121__ and showRectangle4 and showMarkets
    showOr4: bool = __input_122__ and showRectangle4 and showMarkets
    sess4TimeX: str = '0130-0800'
    sess4Time = sess4TimeX + weekendSessions if showMarketsWeekends else sess4TimeX + noWeekendSessions
    showRectangle5: bool = __input_126__ and showMarkets
    showLabel5: bool = __input_127__ and showRectangle5 and showMarkets
    showOr5: bool = __input_128__ and showRectangle5 and showMarkets
    sess5TimeX: str = '2200-0600'
    sess5Time = sess5TimeX + weekendSessions if showMarketsWeekends else sess5TimeX + noWeekendSessions
    showRectangle6: bool = __input_132__ and showMarkets
    showLabel6: bool = __input_133__ and showRectangle6 and showMarkets
    showOr6: bool = __input_134__ and showRectangle6 and showMarkets
    sess6TimeX: str = '0800-0900'
    sess6Time = sess6TimeX + weekendSessions if showMarketsWeekends else sess6TimeX + noWeekendSessions
    showRectangle7: bool = __input_138__ and showMarkets
    showLabel7: bool = __input_139__ and showRectangle7 and showMarkets
    showOr7: bool = __input_140__ and showRectangle7 and showMarkets
    sess7TimeX: str = '1400-1500'
    sess7Time = sess7TimeX + weekendSessions if showMarketsWeekends else sess7TimeX + noWeekendSessions
    showRectangle8: bool = __input_144__ and showMarkets
    showLabel8: bool = __input_145__ and showRectangle8 and showMarkets
    showOr8: bool = __input_146__ and showRectangle8 and showMarkets
    sess8TimeX: str = '0700-1630'
    sess8Time = sess8TimeX + weekendSessions if showMarketsWeekends else sess8TimeX + noWeekendSessions
    showPsy: bool = timeframe.isminutes and (timeframe.multiplier == 60 or timeframe.multiplier == 30 or timeframe.multiplier == 15 or (timeframe.multiplier == 5) or (timeframe.multiplier == 3) or (timeframe.multiplier == 1))
    showPsylevels: bool = __input_150__ and showPsy
    showPsylabel: bool = __input_151__ and showPsylevels
    showAllPsy: bool = __input_152__ and showPsylevels
    psyType: str = psyTypeX if overridePsyType else 'forex' if syminfo.type == 'forex' else 'crypto'
    def f_security(_symbol, _res, _src: Series, _repaint):
        return inline_series(request.security(_symbol, _res, _src[0 if _repaint else 1 if barstate.isrealtime else 0]), 0 if _repaint else 0 if barstate.isrealtime else 1)

    validTimeFrame = timeframe.isintraday == True
    levelStart = time('D') if timeframe.isseconds == True or (timeframe.isminutes == True and timeframe.multiplier < 5) else time('D') - 86400 * 1000
    pivotLabelXOffset = time_close + pivotOffsetInput * timeframe.multiplier * 60 * 1000
    labelXOffset = time_close + labelOffsetInput * timeframe.multiplier * 60 * 1000
    adrLabelXOffset = time_close + adrOffsetInput * timeframe.multiplier * 60 * 1000
    adrLabelXOffset50 = time_close + adrOffsetInput50 * timeframe.multiplier * 60 * 1000
    rdLabelXOffset = time_close + rdOffsetInput * timeframe.multiplier * 60 * 1000
    rdLabelXOffset50 = time_close + rdOffsetInput50 * timeframe.multiplier * 60 * 1000
    oneEmaLength: int = 5
    twoEmaLength: int = 13
    threeEmaLength: int = 50
    fourEmaLength: int = 200
    fiveEmaLength: int = 800
    oneEma = ta.ema(close, oneEmaLength)
    plot(oneEma if showEmas else na, color=oneEmaColor, title='5 Ema')
    twoEma = ta.ema(close, twoEmaLength)
    plot(twoEma if showEmas else na, color=twoEmaColor, title='13 Ema')
    threeEma = ta.ema(close, threeEmaLength)
    plot(threeEma if showEmas else na, color=threeEmaColor, title='50 Ema')
    fourEma = ta.ema(close, fourEmaLength)
    plot(fourEma if showEmas else na, color=fourEmaColor, title='200 Ema')
    fiveEma = ta.ema(close, fiveEmaLength)
    plot(fiveEma if showEmas else na, color=fiveEmaColor, linewidth=2, title='800 Ema')
    cloudSize = ta.stdev(close, threeEmaLength * 2) / 4
    p1 = plot(threeEma + cloudSize if showEmas else na, 'Upper 50 Ema Cloud', color=emaCloudBorderColor, offset=0)
    p2 = plot(threeEma - cloudSize if showEmas else na, 'Lower 50 Ema Cloud', color=emaCloudBorderColor, offset=0)
    fill(p1, p2, title='EMA 50 Cloud', color=emaCloudColor)
    trLib.rLabel(oneEma, '5 Ema', label.style_none, oneEmaColor, labelEmas, labelXOffset)
    trLib.rLabel(twoEma, '13 Ema', label.style_none, twoEmaColor, labelEmas, labelXOffset)
    trLib.rLabel(threeEma, '50 Ema', label.style_none, threeEmaColor, labelEmas, labelXOffset)
    trLib.rLabel(fourEma, '200 Ema', label.style_none, fourEmaColor, labelEmas, labelXOffset)
    trLib.rLabel(fiveEma, '800 Ema', label.style_none, fiveEmaColor, labelEmas, labelXOffset)
    dayHigh = f_security(syminfo.tickerid, 'D', high, False)
    dayLow = f_security(syminfo.tickerid, 'D', low, False)
    dayOpen = f_security(syminfo.tickerid, 'D', open, False)
    dayClose = f_security(syminfo.tickerid, 'D', close, False)
    pivotPoint = (dayHigh + dayLow + dayClose) / 3
    pivR1 = 2 * pivotPoint - dayLow
    pivS1 = 2 * pivotPoint - dayHigh
    pivR2 = pivotPoint - pivS1 + pivR1
    pivS2 = pivotPoint - pivR1 + pivS1
    pivR3 = 2 * pivotPoint + dayHigh - 2 * dayLow
    pivS3 = 2 * pivotPoint - (2 * dayHigh - dayLow)
    pivline = trLib.drawPivot(pivotPoint if validTimeFrame and (showLevelOnePivotPoints or showLevelTwoPivotPoints or showLevelThreePivotPoints or activeM) else na, 'D', 'PP', pivotColor, pivotLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivr1line = trLib.drawPivot(pivR1 if validTimeFrame and showLevelOnePivotPoints else na, 'D', 'R1', color.new(color.green, 50), color.new(color.green, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelOnePivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivs1line = trLib.drawPivot(pivS1 if validTimeFrame and showLevelOnePivotPoints else na, 'D', 'S1', color.new(color.red, 50), color.new(color.red, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelOnePivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivr2line = trLib.drawPivot(pivR2 if validTimeFrame and showLevelTwoPivotPoints else na, 'D', 'R2', color.new(color.green, 50), color.new(color.green, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelTwoPivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivs2line = trLib.drawPivot(pivS2 if validTimeFrame and showLevelTwoPivotPoints else na, 'D', 'S2', color.new(color.red, 50), color.new(color.red, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelTwoPivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivr3line = trLib.drawPivot(pivR3 if validTimeFrame and showLevelThreePivotPoints else na, 'D', 'R3', color.new(color.green, 50), color.new(color.green, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelThreePivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    pivs3line = trLib.drawPivot(pivS3 if validTimeFrame and showLevelThreePivotPoints else na, 'D', 'S3', color.new(color.red, 50), color.new(color.red, 50), rsStyle, 1, extend.both if extendPivots else extend.right, showLevelThreePivotPoints and showPivotLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    weekHigh = f_security(syminfo.tickerid, 'W', high, False)
    weekLow = f_security(syminfo.tickerid, 'W', low, False)
    validDHLTimeFrame = timeframe.isintraday == True
    validWHLTimeFrame = timeframe.isintraday == True or timeframe.isdaily == True
    month_1 = month(timenow)
    month_2 = month(time)
    dayofmonth_1 = dayofmonth(timenow)
    dayofmonth_2 = dayofmonth(time)
    isToday = year(timenow) == year(time) and month_1 == month_2 and (dayofmonth_1 == dayofmonth_2)
    weekofyear_1 = weekofyear(timenow)
    weekofyear_2 = weekofyear(time)
    isThisWeek = year(timenow) == year(time) and weekofyear_1 == weekofyear_2
    plot(dayHigh if validDHLTimeFrame and showDayHighLow and (True if showDayHighLow else isToday) else na, linewidth=2, color=dailyHiLoColor, style=plot.style_stepline, title='YDay Hi', editable=True)
    plot(dayLow if validDHLTimeFrame and showDayHighLow and (True if showDayHighLow else isToday) else na, linewidth=2, color=dailyHiLoColor, style=plot.style_stepline, title='YDay Lo', editable=True)
    trLib.rLabel(dayHigh, 'YDay Hi', label.style_none, color.new(dailyHiLoColor, 0), validDHLTimeFrame and showDayHighLow and showDayHighLowLabels, labelXOffset)
    trLib.rLabel(dayLow, 'YDay Lo', label.style_none, color.new(dailyHiLoColor, 0), validDHLTimeFrame and showDayHighLow and showDayHighLowLabels, labelXOffset)
    plot(weekHigh if validWHLTimeFrame and showWeekHighLow and (True if showWeekHighLow else isThisWeek) else na, linewidth=2, color=weeklyHiLoColor, style=plot.style_stepline, title='LWeek Hi', editable=True)
    plot(weekLow if validWHLTimeFrame and showWeekHighLow and (True if showWeekHighLow else isThisWeek) else na, linewidth=2, color=weeklyHiLoColor, style=plot.style_stepline, title='LWeek Lo', editable=True)
    trLib.rLabel(weekHigh, 'LWeek Hi', label.style_none, color.new(weeklyHiLoColor, 0), validWHLTimeFrame and showWeekHighLow and showDayHighLowLabels, labelXOffset)
    trLib.rLabel(weekLow, 'LWeek Lo', label.style_none, color.new(weeklyHiLoColor, 0), validWHLTimeFrame and showWeekHighLow and showDayHighLowLabels, labelXOffset)
    trLib.rLabel(high - (high - low) / 2, 'PVSRA Override Active!', label.style_none, color.orange, overrideSym, labelXOffset)
    def pvsraVolume(overrideSymbolX, pvsraSymbolX, tickerIdX):
        return request.security(pvsraSymbolX if overrideSymbolX else tickerIdX, '', (volume, high, low, close, open), barmerge.gaps_off, barmerge.lookahead_off)

    pvsraVolume__global__, pvsraHigh, pvsraLow, pvsraClose, pvsraOpen = pvsraVolume(overrideSym, pvsraSym, syminfo.tickerid)
    pvsraColor: Series
    pvsraColor, alertFlag, averageVolume, volumeSpread, highestVolumeSpread = trLib.calcPvsra(pvsraVolume__global__, pvsraHigh, pvsraLow, pvsraClose, pvsraOpen, redVectorColor, greenVectorColor, violetVectorColor, blueVectorColor, regularCandleDownColor, regularCandleUpColor)
    barcolor(pvsraColor)
    alertcondition(alertFlag, title='Alert on Any Vector Candle', message='{{ticker}} Vector Candle on the {{interval}}')
    alertcondition(pvsraColor == greenVectorColor, title='Green Vector Candle', message='{{ticker}} Green Vector Candle on the {{interval}} Note: alert triggers in real time before the candle is closed unless you choose "once per bar close" option - ie the alert might trigger at some point and the pa after that could change the vector color completely. Use with caution.')
    alertcondition(pvsraColor == redVectorColor, title='Red Vector Candle', message='{{ticker}} Red Vector Candle on the {{interval}} Note: alert triggers in real time before the candle is closed unless you choose "once per bar close" option- ie the alert might trigger at some point and the pa after that could change the vector color completely. Use with caution.')
    alertcondition(pvsraColor == blueVectorColor, title='Blue Vector Candle', message='{{ticker}} Blue Vector Candle on the {{interval}} Note: alert triggers in real time before the candle is closed unless you choose "once per bar close" option- ie the alert might trigger at some point and the pa after that could change the vector color completely. Use with caution.')
    alertcondition(pvsraColor == violetVectorColor, title='Purple Vector Candle', message='{{ticker}} Purple Vector Candle on the {{interval}} Note: alert triggers in real time before the candle is closed unless you choose "once per bar close" option- ie the alert might trigger at some point and the pa after that could change the vector color completely. Use with caution.')
    redGreen = pvsraColor == greenVectorColor and pvsraColor[1] == redVectorColor
    greenRed = pvsraColor == redVectorColor and pvsraColor[1] == greenVectorColor
    redBlue = pvsraColor == blueVectorColor and pvsraColor[1] == redVectorColor
    blueRed = pvsraColor == redVectorColor and pvsraColor[1] == blueVectorColor
    greenPurpule = pvsraColor == violetVectorColor and pvsraColor[1] == greenVectorColor
    purpleGreen = pvsraColor == greenVectorColor and pvsraColor[1] == violetVectorColor
    bluePurpule = pvsraColor == violetVectorColor and pvsraColor[1] == blueVectorColor
    purpleBlue = pvsraColor == blueVectorColor and pvsraColor[1] == violetVectorColor
    alertcondition(redGreen, title='Red/Green Vector Candle Pattern', message='{{ticker}} Red/Green Vector Candle Pattern on the {{interval}}')
    alertcondition(greenRed, title='Green/Red Vector Candle Pattern', message='{{ticker}} Green/Red Vector Candle Pattern on the {{interval}}')
    alertcondition(redBlue, title='Red/Blue Vector Candle Pattern', message='{{ticker}} Red/Blue Vector Candle Pattern on the {{interval}}')
    alertcondition(blueRed, title='Blue/Red Vector Candle Pattern', message='{{ticker}} Blue/Red Vector Candle Pattern on the {{interval}}')
    alertcondition(greenPurpule, title='Green/Purple Vector Candle Pattern', message='{{ticker}} Green/Purple Vector Candle Pattern on the {{interval}}')
    alertcondition(purpleGreen, title='Purple/Green Vector Candle Pattern', message='{{ticker}} Purple/Green Vector Candle Pattern on the {{interval}}')
    alertcondition(bluePurpule, title='Blue/Purple Vector Candle Pattern', message='{{ticker}} Blue/Purple Vector Candle Pattern on the {{interval}}')
    alertcondition(purpleBlue, title='Purple/Blue Vector Candle Pattern', message='{{ticker}} Purple/Blue Vector Candle Pattern on the {{interval}}')
    dayAdr, dayAdrHigh, dayAdrLow = request.security(syminfo.tickerid, 'D', trLib.adrHiLo(aDRRange, 1, showADRDO), lookahead=barmerge.lookahead_on)
    dayAdrHigh50 = dayAdrHigh - dayAdr / 2
    dayAdrLow50 = dayAdrLow + dayAdr / 2
    if showADR:
        hl: str = 'Hi-ADR' + ('(DO)' if showADRDO else '')
        ll: str = 'Lo-ADR' + ('(DO)' if showADRDO else '')
        trLib.drawLine(dayAdrHigh, 'D', hl, adrColor, adrStyle, 2, extend.right, showADRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.drawLine(dayAdrLow, 'D', ll, adrColor, adrStyle, 2, extend.right, showADRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.rLabelOffset((dayAdrHigh + dayAdrLow) / 2, 'ADR ' + string.format('{0,number,#.##}', trLib.toPips(dayAdr)) + 'PIPS|' + string.tostring(dayAdr, format.mintick) + syminfo.currency, label.style_none, adrColor, showADRLabels and validTimeFrame and showADRRange, adrLabelXOffset)
    if showADR and showADR50:
        hl: str = '50% Hi-ADR' + ('(DO)' if showADRDO else '')
        ll: str = '50% Lo-ADR' + ('(DO)' if showADRDO else '')
        trLib.drawLine(dayAdrHigh50, 'D', hl, adrColor, adrStyle, 2, extend.right, showADRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.drawLine(dayAdrLow50, 'D', ll, adrColor, adrStyle, 2, extend.right, showADRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.rLabelOffset((dayAdrHigh50 + dayAdrLow50) / 2, '50% ADR ' + string.format('{0,number,#.##}', trLib.toPips(dayAdr / 2)) + 'PIPS|' + string.tostring(dayAdr / 2, format.mintick) + syminfo.currency, label.style_none, adrColor, showADRLabels and validTimeFrame and showADRRange, adrLabelXOffset50)
    alertcondition(ta.crossover(close, dayAdrHigh) and dayAdrHigh != 0.0, 'ADR High reached', 'PA has reached the calculated ADR High')
    alertcondition(ta.crossunder(close, dayAdrLow) and dayAdrLow != 0.0, 'ADR Low reached', 'PA has reached the calculated ADR Low')
    alertcondition(ta.crossover(close, dayAdrHigh50) and dayAdrHigh50 != 0.0, '50% of ADR High reached', 'PA has reached 50% of the calculated ADR High')
    alertcondition(ta.crossunder(close, dayAdrLow50) and dayAdrLow50 != 0.0, '50% ADR Low reached', 'PA has reached 50% the calculated ADR Low')
    weekAdr, weekAdrHigh, weekAdrLow = request.security(syminfo.tickerid, 'W', trLib.adrHiLo(aWRRange, 1, showAWRWO), lookahead=barmerge.lookahead_on)
    weekAdrHigh50 = weekAdrHigh - weekAdr / 2
    weekAdrLow50 = weekAdrLow + weekAdr / 2
    if showAWR:
        hl: str = 'Hi-AWR' + ('(WO)' if showAWRWO else '')
        ll: str = 'Lo-AWR' + ('(WO)' if showAWRWO else '')
        trLib.drawLine(weekAdrHigh, 'W', hl, awrColor, awrStyle, 1, extend.right, showAWRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.drawLine(weekAdrLow, 'W', ll, awrColor, awrStyle, 1, extend.right, showAWRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.rLabelOffset((weekAdrHigh + weekAdrLow) / 2, 'AWR ' + string.format('{0,number,#.##}', trLib.toPips(weekAdr)) + 'PIPS|' + string.tostring(weekAdr, format.mintick) + syminfo.currency, label.style_none, awrColor, showAWRLabels and validTimeFrame and showAWRRange, adrLabelXOffset)
    if showAWR and showAWR50:
        hl: str = '50% Hi-AWR' + ('(WO)' if showAWRWO else '')
        ll: str = '50% Lo-AWR' + ('(WO)' if showAWRWO else '')
        trLib.drawLine(weekAdrHigh50, 'W', hl, awrColor, awrStyle, 1, extend.right, showAWRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.drawLine(weekAdrLow50, 'W', ll, awrColor, awrStyle, 1, extend.right, showAWRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.rLabelOffset((weekAdrHigh50 + weekAdrLow50) / 2, '50% AWR ' + string.format('{0,number,#.##}', trLib.toPips(weekAdr / 2)) + 'PIPS|' + string.tostring(weekAdr / 2, format.mintick) + syminfo.currency, label.style_none, awrColor, showAWRLabels and validTimeFrame and showAWRRange, adrLabelXOffset50)
    alertcondition(ta.crossover(close, weekAdrHigh) and weekAdrHigh != 0, 'AWR High reached', 'PA has reached the calculated AWR High')
    alertcondition(ta.crossunder(close, weekAdrLow) and weekAdrLow != 0, 'AWR Low reached', 'PA has reached the calculated AWR Low')
    alertcondition(ta.crossover(close, weekAdrHigh50) and weekAdrHigh50 != 0, '50% of AWR High reached', 'PA has reached 50% of the calculated AWR High')
    alertcondition(ta.crossunder(close, weekAdrLow50) and weekAdrLow50 != 0, '50% AWR Low reached', 'PA has reached 50% of the calculated AWR Low')
    monthAdr, monthAdrHigh, monthAdrLow = request.security(syminfo.tickerid, 'M', trLib.adrHiLo(aMRRange, 1, showAMRMO), lookahead=barmerge.lookahead_on)
    monthAdrHigh50 = monthAdrHigh - monthAdr / 2
    monthAdrLow50 = monthAdrLow + monthAdr / 2
    if showAMR and timeframe.isminutes and (timeframe.multiplier >= 3):
        hl: str = 'Hi-AMR' + ('(MO)' if showAMRMO else '')
        ll: str = 'Lo-AMR' + ('(MO)' if showAMRMO else '')
        trLib.drawLine(monthAdrHigh, 'M', hl, amrColor, amrStyle, 1, extend.right, showAMRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.drawLine(monthAdrLow, 'M', ll, amrColor, amrStyle, 1, extend.right, showAMRLabels and validTimeFrame, adrLabelXOffset, validTimeFrame)
        trLib.rLabelOffset((monthAdrHigh + monthAdrLow) / 2, 'AMR ' + string.format('{0,number,#.##}', trLib.toPips(monthAdr)) + 'PIPS|' + string.tostring(monthAdr, format.mintick) + syminfo.currency, label.style_none, amrColor, showAMRLabels and validTimeFrame and showAMRRange, adrLabelXOffset)
    if showAMR and showAMR50 and timeframe.isminutes and (timeframe.multiplier >= 3):
        hl: str = '50% Hi-AMR' + ('(MO)' if showAMRMO else '')
        ll: str = '50% Lo-AMR' + ('(MO)' if showAMRMO else '')
        trLib.drawLine(monthAdrHigh50, 'M', hl, amrColor, amrStyle, 1, extend.right, showAMRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.drawLine(monthAdrLow50, 'M', ll, amrColor, amrStyle, 1, extend.right, showAMRLabels and validTimeFrame, adrLabelXOffset50, validTimeFrame)
        trLib.rLabelOffset((monthAdrHigh50 + monthAdrLow50) / 2, '50% AMR ' + string.format('{0,number,#.##}', trLib.toPips(monthAdr / 2)) + 'PIPS|' + string.tostring(monthAdr / 2, format.mintick) + syminfo.currency, label.style_none, amrColor, showAMRLabels and validTimeFrame and showAMRRange, adrLabelXOffset50)
    alertcondition(ta.crossover(close, monthAdrHigh) and monthAdrHigh != 0, 'AMR High reached', 'PA has reached the calculated AMR High')
    alertcondition(ta.crossunder(close, monthAdrLow) and monthAdrLow != 0, 'AMR Low reached', 'PA has reached the calculated AMR Low')
    alertcondition(ta.crossover(close, monthAdrHigh50) and monthAdrHigh50 != 0, '50% of AMR High reached', 'PA has reached 50% of the calculated AMR High')
    alertcondition(ta.crossunder(close, monthAdrLow50) and monthAdrLow50 != 0, '50% of AMR Low reached', 'PA has reached 50% of the calculated AMR Low')
    dayRd, dayRangeHigh, dayRangeLow = request.security(syminfo.tickerid, 'D', trLib.adrHiLo(rdRange, 1, showRDDO), lookahead=barmerge.lookahead_on)
    dayRangeHigh50 = dayRangeHigh - dayRd / 2
    dayRangeLow50 = dayRangeLow + dayRd / 2
    if showRD:
        hl: str = 'RD-Hi' + ('(DO)' if showRDDO else '')
        ll: str = 'RD-Lo' + ('(DO)' if showRDDO else '')
        trLib.drawLine(dayRangeHigh, 'D', hl, rdColor, rdStyle, 2, extend.right, showRDLabels and validTimeFrame, rdLabelXOffset, validTimeFrame)
        trLib.drawLine(dayRangeLow, 'D', ll, rdColor, rdStyle, 2, extend.right, showRDLabels and validTimeFrame, rdLabelXOffset, validTimeFrame)
        trLib.rLabelOffset((dayRangeHigh + dayRangeLow) / 2, 'RD ' + string.format('{0,number,#.##}', trLib.toPips(dayRd)) + 'PIPS|' + string.tostring(dayRd / 2, format.mintick) + syminfo.currency, label.style_none, rdColor, showRDLabels and validTimeFrame and showRDRange, rdLabelXOffset)
    if showRD and showRD50:
        hl: str = '50% RD-Hi' + ('(DO)' if showRDDO else '')
        ll: str = '50% RD-Lo' + ('(DO)' if showRDDO else '')
        trLib.drawLine(dayRangeHigh50, 'D', hl, rdColor, rdStyle, 2, extend.right, showRDLabels and validTimeFrame, rdLabelXOffset50, validTimeFrame)
        trLib.drawLine(dayRangeLow50, 'D', ll, rdColor, rdStyle, 2, extend.right, showRDLabels and validTimeFrame, rdLabelXOffset50, validTimeFrame)
        trLib.rLabelOffset((dayRangeHigh50 + dayRangeHigh50) / 2, '50% RD ' + string.format('{0,number,#.##}', trLib.toPips(dayRd / 2)) + 'PIPS|' + string.tostring(dayRd / 2, format.mintick) + syminfo.currency, label.style_none, rdColor, showRDLabels and validTimeFrame and showRDRange, rdLabelXOffset50)
    alertcondition(ta.crossover(close, dayRangeHigh) and dayRangeHigh != 0, 'Range Daily High reached', 'PA has reached the calculated Range Daily High')
    alertcondition(ta.crossunder(close, dayRangeLow) and dayRangeLow != 0, 'Range Daily Low reached', 'PA has reached the calculated Range Daily Low')
    alertcondition(ta.crossover(close, dayRangeHigh50) and dayRangeHigh50 != 0, '50% of Range Daily High reached', 'PA has reached 50% of the calculated Range Daily High')
    alertcondition(ta.crossunder(close, dayRangeLow50) and dayRangeLow50 != 0, '50% of Range Daily Low reached', 'PA has reached 50% of the calculated Range Daily Low')
    weekRd, weekRangeHigh, weekRangeLow = request.security(syminfo.tickerid, 'W', trLib.adrHiLo(rwRange, 1, showRWWO), lookahead=barmerge.lookahead_on)
    weekRangeHigh50 = weekRangeHigh - weekRd / 2
    weekRangeLow50 = weekRangeLow + weekRd / 2
    if showRW:
        hl: str = 'RW-Hi' + ('(WO)' if showRWWO else '')
        ll: str = 'RW-Lo' + ('(WO)' if showRWWO else '')
        trLib.drawLine(weekRangeHigh, 'D', hl, rwColor, rwStyle, 2, extend.right, showRWLabels and validTimeFrame, rdLabelXOffset, validTimeFrame)
        trLib.drawLine(weekRangeLow, 'D', ll, rwColor, rwStyle, 2, extend.right, showRWLabels and validTimeFrame, rdLabelXOffset, validTimeFrame)
        trLib.rLabelOffset((weekRangeHigh + weekRangeLow) / 2, 'RW ' + string.format('{0,number,#.##}', trLib.toPips(weekRd)) + 'PIPS|' + string.tostring(weekRd / 2, format.mintick) + syminfo.currency, label.style_none, rwColor, showRWLabels and validTimeFrame and showRWRange, rdLabelXOffset)
    if showRW and showRW50:
        hl: str = '50% RW-Hi' + ('(WO)' if showRWWO else '')
        ll: str = '50% RW-Lo' + ('(WO)' if showRWWO else '')
        trLib.drawLine(weekRangeHigh50, 'D', hl, rwColor, rwStyle, 2, extend.right, showRWLabels and validTimeFrame, rdLabelXOffset50, validTimeFrame)
        trLib.drawLine(weekRangeLow50, 'D', ll, rwColor, rwStyle, 2, extend.right, showRWLabels and validTimeFrame, rdLabelXOffset50, validTimeFrame)
        trLib.rLabelOffset((weekRangeHigh50 + weekRangeLow50) / 2, '50% RW ' + string.format('{0,number,#.##}', trLib.toPips(weekRd / 2)) + 'PIPS|' + string.tostring(weekRd / 2, format.mintick) + syminfo.currency, label.style_none, rwColor, showRWLabels and validTimeFrame and showRWRange, rdLabelXOffset50)
    alertcondition(ta.crossover(close, weekRangeHigh) and weekRangeHigh != 0, 'Range Weekly High reached', 'PA has reached the calculated Range Weekly High')
    alertcondition(ta.crossunder(close, weekRangeLow) and weekRangeLow != 0, 'Range Weekly Low reached', 'PA has reached the calculated Range Weekly Low')
    alertcondition(ta.crossover(close, weekRangeHigh50) and weekRangeHigh50 != 0, '50% of Range Weekly High reached', 'PA has reached 50% of the calculated Range Weekly High')
    alertcondition(ta.crossunder(close, weekRangeLow50) and weekRangeLow50 != 0, '50% of Range Weekly Low reached', 'PA has reached 50% of the calculated Range Weekly Low')
    if barstate.islast and showAdrTable and validTimeFrame:
        if showAdrPips or showAdrCurrency:
            panel: Persistent[Table] = table.new(choiceAdrTable, 2, 16, bgcolor=adrTableBgColor)
            table.cell(panel, 0, 0, '')
            table.cell(panel, 1, 0, '')
            if showAdrPips:
                table.cell(panel, 0, 2, 'ADR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 2, string.format('{0,number,#.##}', trLib.toPips(dayAdr)) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 3, 'ADRx3', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 3, string.format('{0,number,#.##}', trLib.toPips(dayAdr) * 3) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 4, 'AWR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 4, string.format('{0,number,#.##}', trLib.toPips(weekAdr)) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 5, 'AMR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 5, string.format('{0,number,#.##}', trLib.toPips(monthAdr)) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
            if showAdrCurrency:
                table.cell(panel, 0, 6, 'ADR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 6, string.tostring(dayAdr, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 7, 'ADRx3', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 7, string.tostring(dayAdr * 3, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 8, 'AWR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 8, string.tostring(weekAdr, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 9, 'AMR', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 9, string.tostring(monthAdr, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
            if showRDPips:
                table.cell(panel, 0, 10, 'RD', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 10, string.format('{0,number,#.##}', trLib.toPips(dayRd)) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 11, 'RDx3', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 11, string.format('{0,number,#.##}', trLib.toPips(dayRd) * 3) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 12, 'RW', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 12, string.format('{0,number,#.##}', trLib.toPips(weekRd)) + 'PIPS', text_color=adrTableTxtColor, text_halign=text.align_left)
            if showRDCurrency:
                table.cell(panel, 0, 13, 'RD', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 13, string.tostring(dayRd, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 14, 'RDx3', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 14, string.tostring(dayRd * 3, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 0, 15, 'RW', text_color=adrTableTxtColor, text_halign=text.align_left)
                table.cell(panel, 1, 15, string.tostring(weekRd, format.mintick) + syminfo.currency, text_color=adrTableTxtColor, text_halign=text.align_left)
    m0C = (pivS2 + pivS3) / 2
    m1C = (pivS1 + pivS2) / 2
    m2C = (pivotPoint + pivS1) / 2
    m3C = (pivotPoint + pivR1) / 2
    m4C = (pivR1 + pivR2) / 2
    m5C = (pivR2 + pivR3) / 2
    trLib.drawPivot(m0C if validTimeFrame and activeM and m0C else na, 'D', 'M0', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    trLib.drawPivot(m1C if validTimeFrame and activeM and m1C else na, 'D', 'M1', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    trLib.drawPivot(m2C if validTimeFrame and activeM and m2C else na, 'D', 'M2', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    trLib.drawPivot(m3C if validTimeFrame and activeM and m3C else na, 'D', 'M3', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    trLib.drawPivot(m4C if validTimeFrame and activeM and m4C else na, 'D', 'M4', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    trLib.drawPivot(m5C if validTimeFrame and activeM and m5C else na, 'D', 'M5', mColor, mLabelColor, mStyle, 1, extend.both if extendPivots else extend.right, showMLabels and validTimeFrame, validTimeFrame, levelStart, pivotLabelXOffset)
    nyDST, ukDST, sydDST = trLib.calcDst()
    if ukDST:
        trLib.drawOpenRange(sess1Time, sess1col, showOr1, 'GMT+1')
        trLib.drawSessionHiLo(sess1Time, showRectangle1, showLabel1, sess1colLabel, sess1Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess1Time, sess1col, showOr1, 'GMT+0')
        trLib.drawSessionHiLo(sess1Time, showRectangle1, showLabel1, sess1colLabel, sess1Label, 'GMT+0', rectStyle)
    if nyDST:
        trLib.drawOpenRange(sess2Time, sess2col, showOr2, 'GMT+1')
        trLib.drawSessionHiLo(sess2Time, showRectangle2, showLabel2, sess2colLabel, sess2Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess2Time, sess2col, showOr2, 'GMT+0')
        trLib.drawSessionHiLo(sess2Time, showRectangle2, showLabel2, sess2colLabel, sess2Label, 'GMT+0', rectStyle)
    trLib.drawOpenRange(sess3Time, sess3col, showOr3, 'GMT+0')
    trLib.drawSessionHiLo(sess3Time, showRectangle3, showLabel3, sess3colLabel, sess3Label, 'GMT+0', rectStyle)
    trLib.drawOpenRange(sess4Time, sess4col, showOr4, 'GMT+0')
    trLib.drawSessionHiLo(sess4Time, showRectangle4, showLabel4, sess4colLabel, sess4Label, 'GMT+0', rectStyle)
    if sydDST:
        trLib.drawOpenRange(sess5Time, sess5col, showOr5, 'GMT+1')
        trLib.drawSessionHiLo(sess5Time, showRectangle5, showLabel5, sess5colLabel, sess5Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess5Time, sess5col, showOr5, 'GMT+0')
        trLib.drawSessionHiLo(sess5Time, showRectangle5, showLabel5, sess5colLabel, sess5Label, 'GMT+0', rectStyle)
    if ukDST:
        trLib.drawOpenRange(sess6Time, sess6col, showOr6, 'GMT+1')
        trLib.drawSessionHiLo(sess6Time, showRectangle6, showLabel6, sess6colLabel, sess6Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess6Time, sess6col, showOr6, 'GMT+0')
        trLib.drawSessionHiLo(sess6Time, showRectangle6, showLabel6, sess6colLabel, sess6Label, 'GMT+0', rectStyle)
    if nyDST:
        trLib.drawOpenRange(sess7Time, sess7col, showOr7, 'GMT+1')
        trLib.drawSessionHiLo(sess7Time, showRectangle7, showLabel7, sess7colLabel, sess7Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess7Time, sess7col, showOr7, 'GMT+0')
        trLib.drawSessionHiLo(sess7Time, showRectangle7, showLabel7, sess7colLabel, sess7Label, 'GMT+0', rectStyle)
    if ukDST:
        trLib.drawOpenRange(sess8Time, sess8col, showOr8, 'GMT+1')
        trLib.drawSessionHiLo(sess8Time, showRectangle8, showLabel8, sess8colLabel, sess8Label, 'GMT+1', rectStyle)
    else:
        trLib.drawOpenRange(sess8Time, sess8col, showOr8, 'GMT+0')
        trLib.drawSessionHiLo(sess8Time, showRectangle8, showLabel8, sess8colLabel, sess8Label, 'GMT+0', rectStyle)
    oneWeekMillis: Persistent[int] = 7 * 24 * 60 * 60 * 1000
    psyHi, psyLo, psyHiLabel, psyLoLabel, psySessionStartTime = trLib.calcPsyLevels(oneWeekMillis, showPsylevels, psyType, sydDST)
    if barstate.islast and (not showAllPsy) and showPsylevels:
        psyHiLine: Series = line.new(time, psyHi, psySessionStartTime, psyHi, xloc.bar_time, extend.none, psyColH)
        line.delete(psyHiLine[1])
        psyLoLine: Series = line.new(time, psyLo, psySessionStartTime, psyLo, xloc.bar_time, extend.none, psyColL)
        line.delete(psyLoLine[1])
    trLib.rLabelLastBar(psyHi, psyHiLabel, label.style_none, psyColH, showPsylabel, labelXOffset)
    trLib.rLabelLastBar(psyLo, psyLoLabel, label.style_none, psyColL, showPsylabel, labelXOffset)
    plot(psyHi if showPsy and showPsylevels and showAllPsy else na, color=psyColH, style=plot.style_stepline, linewidth=2, editable=False, title='Psy-Hi')
    plot(psyLo if showPsy and showPsylevels and showAllPsy else na, color=psyColL, style=plot.style_stepline, linewidth=2, editable=False, title='Psy-Lo')
    alertcondition(ta.crossunder(close, psyHi) and (not na(psyHi)) and (psyHi != 0), 'PA crossed under Psy Hi', 'PA has crossed under the Psy Hi')
    alertcondition(ta.crossover(close, psyHi) and (not na(psyHi)) and (psyHi != 0), 'PA crossed over Psy Hi', 'PA has crossed over the Psy Hi')
    alertcondition(ta.crossunder(close, psyLo) and (not na(psyLo)) and (psyLo != 0), 'PA crossed under Psy Lo', 'PA has crossed under the Psy Lo')
    alertcondition(ta.crossover(close, psyLo) and (not na(psyLo)) and (psyLo != 0), 'PA crossed over Psy Lo', 'PA has crossed over the Psy Lo')
    dailyOpen = trLib.getdayOpen()
    plot(dailyOpen if showRectangle9 and validTimeFrame and showallDly else na, color=sess9col, style=plot.style_stepline, linewidth=2, editable=False, title='Daily Open')
    if showallDly:
        trLib.rLabel(dailyOpen, 'Daily Open', label.style_none, sess9col, validTimeFrame and showLabel9, labelXOffset)
    else:
        if showRectangle9:
            trLib.drawLineDO(dailyOpen, 'D', 'Daily Open', sess9col, line.style_solid, 1, extend.none, validTimeFrame and showLabel9, labelXOffset, validTimeFrame)
    alertcondition(ta.cross(close, dailyOpen) and (not na(dailyOpen)) and (dailyOpen != 0), 'PA crossed Daily open', 'PA has crossed the Daily open')
    if barstate.islast and showDstTable:
        dstTable: Persistent[Table] = table.new(choiceDstTable, 2, 8, bgcolor=dstTableBgColor)
        table.cell(dstTable, 0, 0, 'London DST Starts Last Sunday of March | DST Ends Last Sunday of October', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 1, 'New York DST Starts 2nd Sunday of March | DST Ends 1st Sunday of November', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 2, 'Tokyo does not observe DST', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 3, 'Hong Kong does not observe DST', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 4, 'Sydney DST Start on 1st Sunday of October | DST Ends 1st Sunday of Arpil', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 5, 'EU Brinks DST Starts Last Sunday of March | DST Ends Last Sunday of October', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 6, 'US Brinks DST Starts 2nd Sunday of March | DST Ends 1st Sunday of November', text_color=adrTableTxtColor, text_halign=text.align_left)
        table.cell(dstTable, 0, 7, 'Frankfurt DST Starts Last Sunday of March | DST Ends Last Sunday of October', text_color=adrTableTxtColor, text_halign=text.align_left)
    zoneBoxesAbove: Persistent[list[Box]] = array.new_box()
    zoneBoxesBelow: Persistent[list[Box]] = array.new_box()
    if showVCZ:
        pvsra = trLib.getPvsraFlagByColor(pvsraColor, redVectorColor, greenVectorColor, violetVectorColor, blueVectorColor, regularCandleUpColor)
        trLib.updateZones(pvsra, 0, zoneBoxesBelow, zonesMax, pvsraHigh, pvsraLow, pvsraOpen, pvsraClose, transperancy, zoneUpdateType, zoneColor, zoneType, borderWidth, colorOverride, redVectorColor, greenVectorColor, violetVectorColor, blueVectorColor)
        trLib.updateZones(pvsra, 1, zoneBoxesAbove, zonesMax, pvsraHigh, pvsraLow, pvsraOpen, pvsraClose, transperancy, zoneUpdateType, zoneColor, zoneType, borderWidth, colorOverride, redVectorColor, greenVectorColor, violetVectorColor, blueVectorColor)
        trLib.cleanarr(zoneBoxesAbove)
        trLib.cleanarr(zoneBoxesBelow)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
