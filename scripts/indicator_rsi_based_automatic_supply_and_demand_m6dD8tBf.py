"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, fill, fixnan, high, input, low, na, nz,
    plot, script, ta
)
from pynecore.types import Series


@script.indicator(title='RSI Supply/Demand', shorttitle='RSI S/D', overlay=True, na_bool=True)
def main(
    ShowSD1=input.bool(False, 'Supply Demand Zone', group='Supply Demand 1', inline='Supply Demand 1'),
    ShowSZ1=input.bool(False, 'Support Zone', group='Supply Demand 1', inline='Supply Demand 1'),
    ShowRZ1=input.bool(False, 'Resistance Zone', group='Supply Demand 1', inline='Supply Demand 1'),
    RSI1Length=input.int(7, minval=1, title='RSI 1 Length', group='Supply Demand 1'),
    RSI1OBOSIn=input.string(defval='70 / 30', title='OB / OS', options=('70 / 30', '75 / 25', '80 / 20', '85 / 15', '90 / 10', '95 / 5'), group='Supply Demand 1'),
    NumberOfConfirmationBarsRSI1=input.int(3, title='Confirmation Bars', group='Supply Demand 1'),
    RSI1SDColorIn=input.color(color.new(color.blue, 85), 'Fill Colors - Supply Demand', group='Supply Demand 1', inline='Fill 1'),
    RSI1SupportColorIn=input.color(color.new(color.lime, 92), 'Support', group='Supply Demand 1', inline='Fill 1'),
    RSI1ResistanceColorIn=input.color(color.new(color.red, 92), 'Resistance', group='Supply Demand 1', inline='Fill 1'),
    ShowSD2=input.bool(True, 'Supply Demand Zone', group='Supply Demand 2', inline='Supply Demand 2'),
    ShowSZ2=input.bool(False, 'Support Zone', group='Supply Demand 2', inline='Supply Demand 2'),
    ShowRZ2=input.bool(False, 'Resistance Zone', group='Supply Demand 2', inline='Supply Demand 2'),
    RSI2Length=input.int(14, minval=1, title='RSI 2 Length', group='Supply Demand 2'),
    RSI2OBOSIn=input.string(defval='70 / 30', title='OB / OS', options=('70 / 30', '75 / 25', '80 / 20', '85 / 15', '90 / 10', '95 / 5'), group='Supply Demand 2'),
    NumberOfConfirmationBarsRSI2=input.int(3, title='Confirmation Bars', group='Supply Demand 2'),
    RSI2SDColorIn=input.color(color.new(color.blue, 85), 'Fill Colors - Supply Demand', group='Supply Demand 2', inline='Fill 2'),
    RSI2SupportColorIn=input.color(color.new(color.lime, 92), 'Support', group='Supply Demand 2', inline='Fill 2'),
    RSI2ResistanceColorIn=input.color(color.new(color.red, 92), 'Resistance', group='Supply Demand 2', inline='Fill 2'),
    ShowSD3=input.bool(False, 'Supply Demand Zone', group='Supply Demand 3', inline='Supply Demand 3'),
    ShowSZ3=input.bool(False, 'Support Zone', group='Supply Demand 3', inline='Supply Demand 3'),
    ShowRZ3=input.bool(False, 'Resistance Zone', group='Supply Demand 3', inline='Supply Demand 3'),
    RSI3Length=input.int(21, minval=1, title='RSI 3 Length', group='Supply Demand 3'),
    RSI3OBOSIn=input.string(defval='70 / 30', title='OB / OS', options=('70 / 30', '75 / 25', '80 / 20', '85 / 15', '90 / 10', '95 / 5'), group='Supply Demand 3'),
    NumberOfConfirmationBarsRSI3=input.int(3, title='Confirmation Bars', group='Supply Demand 3'),
    RSI3SDColorIn=input.color(color.new(color.blue, 85), 'Fill Colors - Supply Demand', group='Supply Demand 3', inline='Fill 3'),
    RSI3SupportColorIn=input.color(color.new(color.lime, 92), 'Support', group='Supply Demand 3', inline='Fill 3'),
    RSI3ResistanceColorIn=input.color(color.new(color.red, 92), 'Resistance', group='Supply Demand 3', inline='Fill 3'),
    ShowSD4=input.bool(False, 'Supply Demand Zone', group='Supply Demand 4', inline='Supply Demand 4'),
    ShowSZ4=input.bool(False, 'Support Zone', group='Supply Demand 4', inline='Supply Demand 4'),
    ShowRZ4=input.bool(False, 'Resistance Zone', group='Supply Demand 4', inline='Supply Demand 4'),
    RSI4Length=input.int(28, minval=1, title='RSI 4 Length', group='Supply Demand 4'),
    RSI4OBOSIn=input.string(defval='70 / 30', title='OB / OS', options=('70 / 30', '75 / 25', '80 / 20', '85 / 15', '90 / 10', '95 / 5'), group='Supply Demand 4'),
    NumberOfConfirmationBarsRSI4=input.int(3, title='Confirmation Bars', group='Supply Demand 4'),
    RSI4SDColorIn=input.color(color.new(color.blue, 85), 'Fill Colors - Supply Demand', group='Supply Demand 4', inline='Fill 4'),
    RSI4SupportColorIn=input.color(color.new(color.lime, 92), 'Support', group='Supply Demand 4', inline='Fill 4'),
    RSI4ResistanceColorIn=input.color(color.new(color.red, 92), 'Resistance', group='Supply Demand 4', inline='Fill 4')
):
    RSI1 = ta.rsi(close, RSI1Length)
    RSI1OB = 70 if RSI1OBOSIn == '70 / 30' else 75 if RSI1OBOSIn == '75 / 25' else 80 if RSI1OBOSIn == '80 / 20' else 90 if RSI1OBOSIn == '90 / 10' else 95 if RSI1OBOSIn == '95 / 5' else 100
    RSI1OS = 30 if RSI1OBOSIn == '70 / 30' else 25 if RSI1OBOSIn == '75 / 25' else 20 if RSI1OBOSIn == '80 / 20' else 10 if RSI1OBOSIn == '90 / 10' else 5 if RSI1OBOSIn == '95 / 5' else 0
    RSI1incrementer_up = 1 if RSI1 > RSI1OB else 0
    RSI1incrementer_down = 1 if RSI1 < RSI1OS else 0
    RSI1incrementer_both = 1 if RSI1 > RSI1OB or RSI1 < RSI1OS else 0
    RSI1rsx: Series[int] = 0
    if cast_bool(RSI1incrementer_both):
        RSI1rsx = nz(RSI1rsx[1], 0) + RSI1incrementer_both
    else:
        0
    __block_result__ = na
    if RSI1rsx >= NumberOfConfirmationBarsRSI1:
        RSI1x = high
        __block_result__ = RSI1x
    RSI1rxH = __block_result__
    __block_result_1__ = na
    if RSI1rsx >= NumberOfConfirmationBarsRSI1:
        RSI1y = low
        __block_result_1__ = RSI1y
    RSI1rxL = __block_result_1__
    RSI1rH: Series = fixnan(RSI1rxH)
    RSI1rL = fixnan(RSI1rxL)
    RSI1rsu: Series[int] = 0
    if cast_bool(RSI1incrementer_up):
        RSI1rsu = nz(RSI1rsu[1], 0) + RSI1incrementer_up
    else:
        0
    __block_result_2__ = na
    if RSI1rsu >= NumberOfConfirmationBarsRSI1:
        RSI1x = high
        __block_result_2__ = RSI1x
    RSI1rssH = __block_result_2__
    __block_result_3__ = na
    if RSI1rsu >= NumberOfConfirmationBarsRSI1:
        RSI1y = low
        __block_result_3__ = RSI1y
    RSI1rssL = __block_result_3__
    RSI1ResistanceZoneHigh: Series = fixnan(RSI1rssH)
    RSI1ResistanceZoneLow = fixnan(RSI1rssL)
    RSI1rsd: Series[int] = 0
    if cast_bool(RSI1incrementer_down):
        RSI1rsd = nz(RSI1rsd[1], 0) + RSI1incrementer_down
    else:
        0
    __block_result_4__ = na
    if RSI1rsd >= NumberOfConfirmationBarsRSI1:
        RSI1x = high
        __block_result_4__ = RSI1x
    RSI1rsrH = __block_result_4__
    __block_result_5__ = na
    if RSI1rsd >= NumberOfConfirmationBarsRSI1:
        RSI1y = low
        __block_result_5__ = RSI1y
    RSI1rsrL = __block_result_5__
    RSI1SupportZoneHigh = fixnan(RSI1rsrH)
    RSI1SupportZoneLow: Series = fixnan(RSI1rsrL)
    RSI1_ResZoneColor = na if RSI1ResistanceZoneHigh != RSI1ResistanceZoneHigh[1] else RSI1ResistanceColorIn
    RSI1_SupZoneColor = na if RSI1SupportZoneLow != RSI1SupportZoneLow[1] else RSI1SupportColorIn
    RSI1SDColor = na if RSI1rH != RSI1rH[1] else RSI1SDColorIn
    RSI1RZHigh = plot(RSI1ResistanceZoneHigh if ShowRZ1 else na, style=plot.style_cross, title='Resistance Zone - 1 - High', color=RSI1_ResZoneColor)
    RSI1RZLow = plot(RSI1ResistanceZoneLow if ShowRZ1 else na, style=plot.style_cross, title='Resistance Zone - 1 - Low')
    fill(RSI1RZHigh, RSI1RZLow, color=RSI1_ResZoneColor, title='Support Zone - 1 - Fill')
    RSI1SZHigh = plot(RSI1SupportZoneHigh if ShowSZ1 else na, style=plot.style_cross, title='Support Zone - 1 - High')
    RSI1SZLow = plot(RSI1SupportZoneLow if ShowSZ1 else na, style=plot.style_cross, title='Support Zone - 1 - Low')
    fill(RSI1SZHigh, RSI1SZLow, color=RSI1_SupZoneColor, title='Support Zone - 1 - Fill')
    PlotRSI1rH = plot(RSI1rH if ShowSD1 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 1 - High')
    PlotRSI1rL = plot(RSI1rL if ShowSD1 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 1 - Low')
    fill(PlotRSI1rH, PlotRSI1rL, color=RSI1SDColor, title='Supply Demand - 1 - Fill')
    PriceInRSI1SDZone: Series = close <= RSI1rH and close >= RSI1rL and (RSI1rH == RSI1rH[1])
    PriceEntersRSI1SDZone = PriceInRSI1SDZone and (not PriceInRSI1SDZone[1])
    alertcondition(PriceEntersRSI1SDZone, title='Alert - Price Enters S/D Zone 1', message='Price Enters S/D Zone 1 - RSI S/D')
    RSI2 = ta.rsi(close, RSI2Length)
    RSI2OB = 70 if RSI2OBOSIn == '70 / 30' else 75 if RSI2OBOSIn == '75 / 25' else 80 if RSI2OBOSIn == '80 / 20' else 90 if RSI2OBOSIn == '90 / 10' else 95 if RSI2OBOSIn == '95 / 5' else 100
    RSI2OS = 30 if RSI2OBOSIn == '70 / 30' else 25 if RSI2OBOSIn == '75 / 25' else 20 if RSI2OBOSIn == '80 / 20' else 10 if RSI2OBOSIn == '90 / 10' else 5 if RSI2OBOSIn == '95 / 5' else 0
    RSI2incrementer_up = 1 if RSI2 > RSI2OB else 0
    RSI2incrementer_down = 1 if RSI2 < RSI2OS else 0
    RSI2incrementer_both = 1 if RSI2 > RSI2OB or RSI2 < RSI2OS else 0
    RSI2rsx: Series[int] = 0
    if cast_bool(RSI2incrementer_both):
        RSI2rsx = nz(RSI2rsx[1], 0) + RSI2incrementer_both
    else:
        0
    __block_result_6__ = na
    if RSI2rsx >= NumberOfConfirmationBarsRSI2:
        RSI2x = high
        __block_result_6__ = RSI2x
    RSI2rxH = __block_result_6__
    __block_result_7__ = na
    if RSI2rsx >= NumberOfConfirmationBarsRSI2:
        RSI2y = low
        __block_result_7__ = RSI2y
    RSI2rxL = __block_result_7__
    RSI2rH: Series = fixnan(RSI2rxH)
    RSI2rL = fixnan(RSI2rxL)
    RSI2rsu: Series[int] = 0
    if cast_bool(RSI2incrementer_up):
        RSI2rsu = nz(RSI2rsu[1], 0) + RSI2incrementer_up
    else:
        0
    __block_result_8__ = na
    if RSI2rsu >= NumberOfConfirmationBarsRSI2:
        RSI2x = high
        __block_result_8__ = RSI2x
    RSI2rssH = __block_result_8__
    __block_result_9__ = na
    if RSI2rsu >= NumberOfConfirmationBarsRSI2:
        RSI2y = low
        __block_result_9__ = RSI2y
    RSI2rssL = __block_result_9__
    RSI2ResistanceZoneHigh: Series = fixnan(RSI2rssH)
    RSI2ResistanceZoneLow = fixnan(RSI2rssL)
    RSI2rsd: Series[int] = 0
    if cast_bool(RSI2incrementer_down):
        RSI2rsd = nz(RSI2rsd[1], 0) + RSI2incrementer_down
    else:
        0
    __block_result_10__ = na
    if RSI2rsd >= NumberOfConfirmationBarsRSI2:
        RSI2x = high
        __block_result_10__ = RSI2x
    RSI2rsrH = __block_result_10__
    __block_result_11__ = na
    if RSI2rsd >= NumberOfConfirmationBarsRSI2:
        RSI2y = low
        __block_result_11__ = RSI2y
    RSI2rsrL = __block_result_11__
    RSI2SupportZoneHigh = fixnan(RSI2rsrH)
    RSI2SupportZoneLow: Series = fixnan(RSI2rsrL)
    RSI2_ResZoneColor = na if RSI2ResistanceZoneHigh != RSI2ResistanceZoneHigh[1] else RSI2ResistanceColorIn
    RSI2_SupZoneColor = na if RSI2SupportZoneLow != RSI2SupportZoneLow[1] else RSI2SupportColorIn
    RSI2SDColor = na if RSI2rH != RSI2rH[1] else RSI2SDColorIn
    RSI2RZHigh = plot(RSI2ResistanceZoneHigh if ShowRZ2 else na, style=plot.style_cross, title='Resistance Zone - 2 - High')
    RSI2RZLow = plot(RSI2ResistanceZoneLow if ShowRZ2 else na, style=plot.style_cross, title='Resistance Zone - 2 - Low')
    fill(RSI2RZHigh, RSI2RZLow, color=RSI2_ResZoneColor, title='Support Zone - 2 - Fill')
    RSI2SZHigh = plot(RSI2SupportZoneHigh if ShowSZ2 else na, style=plot.style_cross, title='Support Zone - 2 - High')
    RSI2SZLow = plot(RSI2SupportZoneLow if ShowSZ2 else na, style=plot.style_cross, title='Support Zone - 2 - Low')
    fill(RSI2SZHigh, RSI2SZLow, color=RSI2_SupZoneColor, title='Support Zone - 2 - Fill')
    PlotRSI2rH = plot(RSI2rH if ShowSD2 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 2 - High')
    PlotRSI2rL = plot(RSI2rL if ShowSD2 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 2 - Low')
    fill(PlotRSI2rH, PlotRSI2rL, color=RSI2SDColor, title='Supply Demand - 2 - Fill')
    PriceInRSI2SDZone: Series = close <= RSI2rH and close >= RSI2rL and (RSI2rH == RSI2rH[1])
    PriceEntersRSI2SDZone = PriceInRSI2SDZone and (not PriceInRSI2SDZone[1])
    alertcondition(PriceEntersRSI2SDZone, title='Alert - Price Enters S/D Zone 2', message='Price Enters S/D Zone 2 - RSI S/D')
    RSI3 = ta.rsi(close, RSI3Length)
    RSI3OB = 70 if RSI3OBOSIn == '70 / 30' else 75 if RSI3OBOSIn == '75 / 25' else 80 if RSI3OBOSIn == '80 / 20' else 90 if RSI3OBOSIn == '90 / 10' else 95 if RSI3OBOSIn == '95 / 5' else 100
    RSI3OS = 30 if RSI3OBOSIn == '70 / 30' else 25 if RSI3OBOSIn == '75 / 25' else 20 if RSI3OBOSIn == '80 / 20' else 10 if RSI3OBOSIn == '90 / 10' else 5 if RSI3OBOSIn == '95 / 5' else 0
    RSI3incrementer_up = 1 if RSI3 > RSI3OB else 0
    RSI3incrementer_down = 1 if RSI3 < RSI3OS else 0
    RSI3incrementer_both = 1 if RSI3 > RSI3OB or RSI3 < RSI3OS else 0
    RSI3rsx: Series[int] = 0
    if cast_bool(RSI3incrementer_both):
        RSI3rsx = nz(RSI3rsx[1], 0) + RSI3incrementer_both
    else:
        0
    __block_result_12__ = na
    if RSI3rsx >= NumberOfConfirmationBarsRSI3:
        RSI3x = high
        __block_result_12__ = RSI3x
    RSI3rxH = __block_result_12__
    __block_result_13__ = na
    if RSI3rsx >= NumberOfConfirmationBarsRSI3:
        RSI3y = low
        __block_result_13__ = RSI3y
    RSI3rxL = __block_result_13__
    RSI3rH: Series = fixnan(RSI3rxH)
    RSI3rL = fixnan(RSI3rxL)
    RSI3rsu: Series[int] = 0
    if cast_bool(RSI3incrementer_up):
        RSI3rsu = nz(RSI3rsu[1], 0) + RSI3incrementer_up
    else:
        0
    __block_result_14__ = na
    if RSI3rsu >= NumberOfConfirmationBarsRSI3:
        RSI3x = high
        __block_result_14__ = RSI3x
    RSI3rssH = __block_result_14__
    __block_result_15__ = na
    if RSI3rsu >= NumberOfConfirmationBarsRSI3:
        RSI3y = low
        __block_result_15__ = RSI3y
    RSI3rssL = __block_result_15__
    RSI3ResistanceZoneHigh: Series = fixnan(RSI3rssH)
    RSI3ResistanceZoneLow = fixnan(RSI3rssL)
    RSI3rsd: Series[int] = 0
    if cast_bool(RSI3incrementer_down):
        RSI3rsd = nz(RSI3rsd[1], 0) + RSI3incrementer_down
    else:
        0
    __block_result_16__ = na
    if RSI3rsd >= NumberOfConfirmationBarsRSI3:
        RSI3x = high
        __block_result_16__ = RSI3x
    RSI3rsrH = __block_result_16__
    __block_result_17__ = na
    if RSI3rsd >= NumberOfConfirmationBarsRSI3:
        RSI3y = low
        __block_result_17__ = RSI3y
    RSI3rsrL = __block_result_17__
    RSI3SupportZoneHigh = fixnan(RSI3rsrH)
    RSI3SupportZoneLow: Series = fixnan(RSI3rsrL)
    RSI3_ResZoneColor = na if RSI3ResistanceZoneHigh != RSI3ResistanceZoneHigh[1] else RSI3ResistanceColorIn
    RSI3_SupZoneColor = na if RSI3SupportZoneLow != RSI3SupportZoneLow[1] else RSI3SupportColorIn
    RSI3SDColor = na if RSI3rH != RSI3rH[1] else RSI3SDColorIn
    RSI3RZHigh = plot(RSI3ResistanceZoneHigh if ShowRZ3 else na, style=plot.style_cross, title='Resistance Zone - 3 - High')
    RSI3RZLow = plot(RSI3ResistanceZoneLow if ShowRZ3 else na, style=plot.style_cross, title='Resistance Zone - 3 - Low')
    fill(RSI3RZHigh, RSI3RZLow, color=RSI3_ResZoneColor, title='Support Zone - 3 - Fill')
    RSI3SZHigh = plot(RSI3SupportZoneHigh if ShowSZ3 else na, style=plot.style_cross, title='Support Zone - 3 - High')
    RSI3SZLow = plot(RSI3SupportZoneLow if ShowSZ3 else na, style=plot.style_cross, title='Support Zone - 3 - Low')
    fill(RSI3SZHigh, RSI3SZLow, color=RSI3_SupZoneColor, title='Support Zone - 3 - Fill')
    PlotRSI3rH = plot(RSI3rH if ShowSD3 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 3 - High')
    PlotRSI3rL = plot(RSI3rL if ShowSD3 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 3 - Low')
    fill(PlotRSI3rH, PlotRSI3rL, color=RSI3SDColor, title='Supply Demand - 3 - Fill')
    PriceInRSI3SDZone: Series = close <= RSI3rH and close >= RSI3rL and (RSI3rH == RSI3rH[1])
    PriceEntersRSI3SDZone = PriceInRSI3SDZone and (not PriceInRSI3SDZone[1])
    alertcondition(PriceEntersRSI3SDZone, title='Alert - Price Enters S/D Zone 3', message='Price Enters S/D Zone 3 - RSI S/D')
    RSI4 = ta.rsi(close, RSI4Length)
    RSI4OB = 70 if RSI4OBOSIn == '70 / 30' else 75 if RSI4OBOSIn == '75 / 25' else 80 if RSI4OBOSIn == '80 / 20' else 90 if RSI4OBOSIn == '90 / 10' else 95 if RSI4OBOSIn == '95 / 5' else 100
    RSI4OS = 30 if RSI4OBOSIn == '70 / 30' else 25 if RSI4OBOSIn == '75 / 25' else 20 if RSI4OBOSIn == '80 / 20' else 10 if RSI4OBOSIn == '90 / 10' else 5 if RSI4OBOSIn == '95 / 5' else 0
    RSI4incrementer_up = 1 if RSI4 > RSI4OB else 0
    RSI4incrementer_down = 1 if RSI4 < RSI4OS else 0
    RSI4incrementer_both = 1 if RSI4 > RSI4OB or RSI4 < RSI4OS else 0
    RSI4rsx: Series[int] = 0
    if cast_bool(RSI4incrementer_both):
        RSI4rsx = nz(RSI4rsx[1], 0) + RSI4incrementer_both
    else:
        0
    __block_result_18__ = na
    if RSI4rsx >= NumberOfConfirmationBarsRSI4:
        RSI4x = high
        __block_result_18__ = RSI4x
    RSI4rxH = __block_result_18__
    __block_result_19__ = na
    if RSI4rsx >= NumberOfConfirmationBarsRSI4:
        RSI4y = low
        __block_result_19__ = RSI4y
    RSI4rxL = __block_result_19__
    RSI4rH: Series = fixnan(RSI4rxH)
    RSI4rL = fixnan(RSI4rxL)
    RSI4rsu: Series[int] = 0
    if cast_bool(RSI4incrementer_up):
        RSI4rsu = nz(RSI4rsu[1], 0) + RSI4incrementer_up
    else:
        0
    __block_result_20__ = na
    if RSI4rsu >= NumberOfConfirmationBarsRSI4:
        RSI4x = high
        __block_result_20__ = RSI4x
    RSI4rssH = __block_result_20__
    __block_result_21__ = na
    if RSI4rsu >= NumberOfConfirmationBarsRSI4:
        RSI4y = low
        __block_result_21__ = RSI4y
    RSI4rssL = __block_result_21__
    RSI4ResistanceZoneHigh: Series = fixnan(RSI4rssH)
    RSI4ResistanceZoneLow = fixnan(RSI4rssL)
    RSI4rsd: Series[int] = 0
    if cast_bool(RSI4incrementer_down):
        RSI4rsd = nz(RSI4rsd[1], 0) + RSI4incrementer_down
    else:
        0
    __block_result_22__ = na
    if RSI4rsd >= NumberOfConfirmationBarsRSI4:
        RSI4x = high
        __block_result_22__ = RSI4x
    RSI4rsrH = __block_result_22__
    __block_result_23__ = na
    if RSI4rsd >= NumberOfConfirmationBarsRSI4:
        RSI4y = low
        __block_result_23__ = RSI4y
    RSI4rsrL = __block_result_23__
    RSI4SupportZoneHigh = fixnan(RSI4rsrH)
    RSI4SupportZoneLow: Series = fixnan(RSI4rsrL)
    RSI4_ResZoneColor = na if RSI4ResistanceZoneHigh != RSI4ResistanceZoneHigh[1] else RSI4ResistanceColorIn
    RSI4_SupZoneColor = na if RSI4SupportZoneLow != RSI4SupportZoneLow[1] else RSI4SupportColorIn
    RSI4SDColor = na if RSI4rH != RSI4rH[1] else RSI4SDColorIn
    RSI4RZHigh = plot(RSI4ResistanceZoneHigh if ShowRZ4 else na, style=plot.style_cross, title='Resistance Zone - 4 - High')
    RSI4RZLow = plot(RSI4ResistanceZoneLow if ShowRZ4 else na, style=plot.style_cross, title='Resistance Zone - 4 - Low')
    fill(RSI4RZHigh, RSI4RZLow, color=RSI4_ResZoneColor, title='Support Zone - 4 - Fill')
    RSI4SZHigh = plot(RSI4SupportZoneHigh if ShowSZ4 else na, style=plot.style_cross, title='Support Zone - 4 - High')
    RSI4SZLow = plot(RSI4SupportZoneLow if ShowSZ4 else na, style=plot.style_cross, title='Support Zone - 4 - Low')
    fill(RSI4SZHigh, RSI4SZLow, color=RSI4_SupZoneColor, title='Support Zone - 4 - Fill')
    PlotRSI4rH = plot(RSI4rH if ShowSD4 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 4 - High')
    PlotRSI4rL = plot(RSI4rL if ShowSD4 else na, style=plot.style_cross, linewidth=1, title='Supply Demand - 4 - Low')
    fill(PlotRSI4rH, PlotRSI4rL, color=RSI4SDColor, title='Supply Demand - 4 - Fill')
    PriceInRSI4SDZone: Series = close <= RSI4rH and close >= RSI4rL and (RSI4rH == RSI4rH[1])
    PriceEntersRSI4SDZone = PriceInRSI4SDZone and (not PriceInRSI4SDZone[1])
    alertcondition(PriceEntersRSI4SDZone, title='Alert - Price Enters S/D Zone 4', message='Price Enters S/D Zone 4 - RSI S/D')
    alertcondition(PriceEntersRSI1SDZone or PriceEntersRSI2SDZone or PriceEntersRSI3SDZone or PriceEntersRSI4SDZone, title='Alert - Price Enters Any S/D Zone', message='Price Enters Any S/D Zone - RSI S/D')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
