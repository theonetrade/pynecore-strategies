"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, chart, close, color, display, input, location, log, map,
    math, na, plot, plotshape, position, runtime, script, shape, size, string, table
)
from pynecore.types import Color, Persistent, Series, Table
from typing import Protocol, Any
import lib.jason5480.signal_datagram.v5 as sd


__all__ = ['DealConditions', 'getDealConditions', 'getSignal']


@udt
class DealConditions:
    startLongDeal: bool = na(bool)
    startShortDeal: bool = na(bool)
    endLongDeal: bool = na(bool)
    endShortDeal: bool = na(bool)
    cnlStartLongDeal: bool = na(bool)
    cnlStartShortDeal: bool = na(bool)
    cnlEndLongDeal: bool = na(bool)
    cnlEndShortDeal: bool = na(bool)


class SignalMode(Enum):
    produce = 'PRODUCE ONLY'
    consume = 'CONSUME ONLY'
    connect = 'CONNECT'


class _ProtocolGetdealconditions(Protocol):
    def __call__(self, signal: int) -> Any: ...


class _ProtocolGetsignal(Protocol):
    def __call__(self, dealConditions: DealConditions) -> Any: ...


getDealConditions: _ProtocolGetdealconditions = Exported()
getSignal: _ProtocolGetsignal = Exported()


SCHEMA_VERSION_MIN: int = 1
SCHEMA_VERSION_MAJ: int = 0
FRAMEWORK_ID: int = 0
HANDSHAKE_NUMERIC_SYSTEM: sd.NumericSystem = sd.NumericSystem.hexadecimal
SCHEMA_VERSION_MIN_NAME: str = 'VERSION_MIN'
SCHEMA_VERSION_MAJ_NAME: str = 'VERSION_MAJ'
FRAMEWORK_NAME: str = 'TTS'
CONDITIONS_NUMERIC_SYSTEM: sd.NumericSystem = sd.NumericSystem.decimal
CONDITION_SHORT_NAME: str = 'SHORT'
CONDITION_LONG_NAME: str = 'LONG'
CONDITION_NOOP_NAME: str = 'NOOP'
CONDITION_END_NAME: str = 'END'
CONDITION_START_NAME: str = 'START'
CONDITION_CNL_END_NAME: str = 'CNL_END'
CONDITION_CNL_START_NAME: str = 'CNL_START'
LONG_OPEN_COLOR: Color = color.new('#0074BA')
SHORT_OPEN_COLOR: Color = color.new('#FF6723')
CLOSE_COLOR: Color = color.new('#C790F1')
LONG_CANCEL_OPEN_COLOR: Color = color.new('#0074BA')
SHORT_CANCEL_OPEN_COLOR: Color = color.new('#FF6723')
CANCEL_CLOSE_COLOR: Color = color.new('#C790F1')


@script.library(title='tts_convention')
def main(
    mode=input.enum(defval=SignalMode.connect, title='Mode', tooltip='Select the mode to either produce a signal as an output or consume the signal as an input or connect the produced signal as input and consume it at the same time.'),
    frId=input.int(defval=FRAMEWORK_ID, title='Framework Id', minval=0, maxval=15, tooltip='The id of the framework of the produced signal', group='Output'),
    majVer=input.int(defval=SCHEMA_VERSION_MAJ, title='Major Version', minval=0, maxval=15, tooltip='The major version number of the schema of the produced signal', group='Output'),
    minVer=input.int(defval=SCHEMA_VERSION_MIN, title='Minor Version', minval=0, maxval=15, tooltip='The minor version number of the schema of the produced signal', group='Output'),
    seed=input.int(defval=0, title='Random seed', tooltip='The seed that will be used to produce random signal', group='Output'),
    __input_5__: Series[float] = input.source(defval=close, title='🔌Signal 🛈', tooltip='Select input from an signal indicator. INFORMATION! The indicator should be added to the same chart with this strategy and the desired value that will take part in the conditions below should be plotted in the chart.', group='Input')
):
    def getHandshakeDatagramImpl(frameworkIdName: str, majorVersionName: str, minorVersionName: str):
        channelWordPosMap: sd.ChannelDesc = method_call('init', sd.ChannelDesc.new())
        method_call('add_channel', channelWordPosMap, minorVersionName, array.from_items(10))
        method_call('add_channel', channelWordPosMap, majorVersionName, array.from_items(11))
        method_call('add_channel', channelWordPosMap, frameworkIdName, array.from_items(12))
        return method_call('init', sd.Datagram.new(), HANDSHAKE_NUMERIC_SYSTEM, channelWordPosMap)

    def getHandshakeDatagram():
        return getHandshakeDatagramImpl(FRAMEWORK_NAME, SCHEMA_VERSION_MAJ_NAME, SCHEMA_VERSION_MIN_NAME)

    def getDealConditionsDatagramImpl(longChannelName: str, shortChannelName: str):
        channelWordPosMap: sd.ChannelDesc = method_call('init', sd.ChannelDesc.new())
        method_call('add_channel', channelWordPosMap, shortChannelName, array.from_items(0))
        method_call('add_channel', channelWordPosMap, longChannelName, array.from_items(1))
        return method_call('init', sd.Datagram.new(), CONDITIONS_NUMERIC_SYSTEM, channelWordPosMap)

    def getDealConditionsDatagram():
        return getDealConditionsDatagramImpl(CONDITION_LONG_NAME, CONDITION_SHORT_NAME)

    def getConditionsMap():
        CONDITIONS: Persistent[dict[str, int]] = map.new()
        map.put(CONDITIONS, CONDITION_NOOP_NAME, 0)
        map.put(CONDITIONS, CONDITION_END_NAME, 1)
        map.put(CONDITIONS, CONDITION_START_NAME, 2)
        map.put(CONDITIONS, CONDITION_CNL_END_NAME, 3)
        map.put(CONDITIONS, CONDITION_CNL_START_NAME, 4)
        return CONDITIONS

    def doVersionCheck(frameworkId: int, majorVersion: int, minorVersion: int):
        if frameworkId != FRAMEWORK_ID:
            runtime.error(string.format('The framework of the connected signal is incompatible with the {0} framework! Please contact the author for more information.', FRAMEWORK_NAME))
        if majorVersion != SCHEMA_VERSION_MAJ:
            runtime.error(string.format('The schema version of the connected signal is {0,number,integer}.{1,number,integer} and is incompatible with the current version of the {2} framework that uses schema version {3,number,integer}.{4,number,integer}! Please update your signal indicator to use the latest version of the "{5}_convention" library.', majorVersion, minorVersion, FRAMEWORK_NAME, SCHEMA_VERSION_MAJ, SCHEMA_VERSION_MIN, string.lower(FRAMEWORK_NAME)))
        __block_result__ = na
        if minorVersion < SCHEMA_VERSION_MIN:
            warn: str = string.format('⚠️ Please update your signal indicator to use the latest version of the "{5}_convention" library!\nThe schema version of the connected signal is {0,number,integer}.{1,number,integer} and the current version of the {2} framework uses schema version {3,number,integer}.{4,number,integer}.', majorVersion, minorVersion, FRAMEWORK_NAME, SCHEMA_VERSION_MAJ, SCHEMA_VERSION_MIN, string.lower(FRAMEWORK_NAME))
            __block_result__ = method_call('cell', table.new(position=position.middle_center, columns=1, rows=1, force_overlay=True), column=0, row=0, text=warn, text_color=color.orange, text_size=size.large)
        else:
            __block_result__ = log.info('The schema version of the connected signal is {0,number,integer}.{1,number,integer} and the current version of the {2} framework uses schema version {3,number,integer}.{4,number,integer}.', majorVersion, minorVersion, FRAMEWORK_NAME, SCHEMA_VERSION_MAJ, SCHEMA_VERSION_MIN)
        return __block_result__


    @export
    def getDealConditions(signal: int):
        __block_result_1__ = na
        if barstate.isfirst:
            handshakeDatagram: Persistent[sd.Datagram] = getHandshakeDatagram()
            method_call('set_signal', handshakeDatagram, signal)

            doVersionCheck(method_call('get_channel_value', handshakeDatagram, FRAMEWORK_NAME), method_call('get_channel_value', handshakeDatagram, SCHEMA_VERSION_MAJ_NAME), method_call('get_channel_value', handshakeDatagram, SCHEMA_VERSION_MIN_NAME))
            __block_result_1__ = DealConditions()
        else:
            CONDITIONS: Persistent[dict[str, int]] = getConditionsMap()
            startCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_START_NAME)
            endCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_END_NAME)
            cnlStartCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_CNL_START_NAME)
            cnlEndCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_CNL_END_NAME)

            dealConditionsDatagram: Persistent[sd.Datagram] = getDealConditionsDatagram()
            method_call('set_signal', dealConditionsDatagram, signal)

            shortCondition: int = method_call('get_channel_value', dealConditionsDatagram, CONDITION_SHORT_NAME)
            longCondition: int = method_call('get_channel_value', dealConditionsDatagram, CONDITION_LONG_NAME)

            __block_result_1__ = DealConditions(startLongDeal=longCondition == startCondition, startShortDeal=shortCondition == startCondition, endLongDeal=longCondition == endCondition, endShortDeal=shortCondition == endCondition, cnlStartLongDeal=longCondition == cnlStartCondition, cnlStartShortDeal=shortCondition == cnlStartCondition, cnlEndLongDeal=longCondition == cnlEndCondition, cnlEndShortDeal=shortCondition == cnlEndCondition)
        return __block_result_1__

    def getSignalImpl(dealConditions: DealConditions, frameworkId: int, majorVersion: int, minorVersion: int):
        if na(dealConditions):
            runtime.error('The dealConditions object cannot be na!')

        __block_result_2__ = na
        if barstate.isfirst:
            handshakeDatagram: Persistent[sd.Datagram] = getHandshakeDatagram()

            method_call('set_channel_value', handshakeDatagram, SCHEMA_VERSION_MIN_NAME, minorVersion)
            method_call('set_channel_value', handshakeDatagram, SCHEMA_VERSION_MAJ_NAME, majorVersion)
            method_call('set_channel_value', handshakeDatagram, FRAMEWORK_NAME, frameworkId)
            __block_result_2__ = method_call('get_signal', handshakeDatagram)
        else:
            CONDITIONS: Persistent[dict[str, int]] = getConditionsMap()
            startCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_START_NAME)
            endCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_END_NAME)
            cnlStartCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_CNL_START_NAME)
            cnlEndCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_CNL_END_NAME)
            noopCondition: Persistent[int] = map.get(CONDITIONS, CONDITION_NOOP_NAME)

            __block_result_3__ = na
            if dealConditions.startShortDeal:
                __block_result_3__ = startCondition
            elif dealConditions.endShortDeal:
                __block_result_3__ = endCondition
            elif dealConditions.cnlStartShortDeal:
                __block_result_3__ = cnlStartCondition
            elif dealConditions.cnlEndShortDeal:
                __block_result_3__ = cnlEndCondition
            else:
                __block_result_3__ = noopCondition
            shortCondition: int = __block_result_3__

            __block_result_4__ = na
            if dealConditions.startLongDeal:
                __block_result_4__ = startCondition
            elif dealConditions.endLongDeal:
                __block_result_4__ = endCondition
            elif dealConditions.cnlStartLongDeal:
                __block_result_4__ = cnlStartCondition
            elif dealConditions.cnlEndLongDeal:
                __block_result_4__ = cnlEndCondition
            else:
                __block_result_4__ = noopCondition
            longCondition: int = __block_result_4__

            dealConditionsDatagram: Persistent[sd.Datagram] = getDealConditionsDatagram()

            method_call('set_channel_value', dealConditionsDatagram, CONDITION_SHORT_NAME, shortCondition)
            method_call('set_channel_value', dealConditionsDatagram, CONDITION_LONG_NAME, longCondition)

            __block_result_2__ = method_call('get_signal', dealConditionsDatagram)
        return __block_result_2__

    @export
    def getSignal(dealConditions: DealConditions):
        return getSignalImpl(dealConditions, FRAMEWORK_ID, SCHEMA_VERSION_MAJ, SCHEMA_VERSION_MIN)


    isNotConsumeOnly: bool = mode != SignalMode.consume

    rand: float = math.random(0, 1, seed)
    outDealConditions = DealConditions(startLongDeal=rand < 0.1, startShortDeal=rand >= 0.1 and rand < 0.2, endLongDeal=rand >= 0.2 and rand < 0.3, endShortDeal=rand >= 0.3 and rand < 0.4, cnlStartLongDeal=rand >= 0.4 and rand < 0.5, cnlStartShortDeal=rand >= 0.5 and rand < 0.6, cnlEndLongDeal=rand >= 0.6 and rand < 0.7, cnlEndShortDeal=rand >= 0.7 and rand < 0.8) if isNotConsumeOnly else na

    outSignal: int = getSignalImpl(outDealConditions, frId, majVer, minVer) if isNotConsumeOnly else na

    buyTable: Persistent[Table] = table.new(position=position.top_right, columns=1, rows=1)
    sellTable: Persistent[Table] = table.new(position=position.bottom_right, columns=1, rows=1)
    if barstate.isfirst:
        table.cell(buyTable, column=0, row=0, text='Buy', text_color=color.blue)
        table.cell(sellTable, column=0, row=0, text='Sell', text_color=color.red)

    outSignalColor: Color = (LONG_OPEN_COLOR if outDealConditions.startLongDeal else SHORT_OPEN_COLOR if outDealConditions.startShortDeal else CLOSE_COLOR if outDealConditions.endLongDeal or outDealConditions.endShortDeal else LONG_CANCEL_OPEN_COLOR if outDealConditions.cnlStartLongDeal else SHORT_CANCEL_OPEN_COLOR if outDealConditions.cnlStartShortDeal else CANCEL_CLOSE_COLOR if outDealConditions.cnlEndLongDeal or outDealConditions.cnlEndShortDeal else chart.fg_color) if isNotConsumeOnly else na

    plot(series=outSignal if isNotConsumeOnly else na, title='🔌Output Signal to TTS', color=outSignalColor, editable=False, style=plot.style_stepline, precision=0)

    plotshape(series=outDealConditions.startLongDeal if isNotConsumeOnly else False, title='Output Start Long', style=shape.triangleup, location=location.top, color=color.new(LONG_OPEN_COLOR, 70), offset=1, size=size.small, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.endLongDeal if isNotConsumeOnly else False, title='Output End Long', style=shape.square, location=location.bottom, color=color.new(CLOSE_COLOR, 70), offset=1, size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.cnlStartLongDeal if isNotConsumeOnly else False, title='Output Cancel Start Long', style=shape.xcross, location=location.top, color=color.new(LONG_CANCEL_OPEN_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.cnlEndLongDeal if isNotConsumeOnly else False, title='Output Cancel End Long', style=shape.xcross, location=location.bottom, color=color.new(CANCEL_CLOSE_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.startShortDeal if isNotConsumeOnly else False, title='Output Start Short', style=shape.triangledown, location=location.bottom, color=color.new(SHORT_OPEN_COLOR, 70), offset=1, size=size.small, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.endShortDeal if isNotConsumeOnly else False, title='Output End Short', style=shape.square, location=location.top, color=color.new(CLOSE_COLOR, 70), offset=1, size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.cnlStartShortDeal if isNotConsumeOnly else False, title='Output Cancel Start Short', style=shape.xcross, location=location.bottom, color=color.new(SHORT_CANCEL_OPEN_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=outDealConditions.cnlEndShortDeal if isNotConsumeOnly else False, title='Output Cancel End Short', style=shape.xcross, location=location.top, color=color.new(CANCEL_CLOSE_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)

    inSignal = cast_int(__input_5__)

    isNotProduceOnly: bool = mode != SignalMode.produce
    isExternalSignalConnected: bool = mode != SignalMode.connect and inSignal != close

    inDealConditions = getDealConditions(outSignal if mode == SignalMode.connect else inSignal) if isNotProduceOnly else na

    inSignalColor: Color = (LONG_OPEN_COLOR if inDealConditions.startLongDeal else SHORT_OPEN_COLOR if inDealConditions.startShortDeal else CLOSE_COLOR if inDealConditions.endLongDeal or inDealConditions.endShortDeal else LONG_CANCEL_OPEN_COLOR if inDealConditions.cnlStartLongDeal else SHORT_CANCEL_OPEN_COLOR if inDealConditions.cnlStartShortDeal else CANCEL_CLOSE_COLOR if inDealConditions.cnlEndLongDeal or inDealConditions.cnlEndShortDeal else chart.fg_color) if isNotProduceOnly else na

    plot(series=inSignal if isNotProduceOnly and isExternalSignalConnected else na, title='🔌Input Signal from SI', color=inSignalColor, editable=False, style=plot.style_stepline, precision=0)

    plotshape(series=inDealConditions.startLongDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Start Long', style=shape.triangleup, location=location.top, color=color.new(LONG_OPEN_COLOR, 70), offset=1, size=size.small, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.endLongDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input End Long', style=shape.square, location=location.bottom, color=color.new(CLOSE_COLOR, 70), offset=1, size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.cnlStartLongDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Cancel Start Long', style=shape.xcross, location=location.top, color=color.new(LONG_CANCEL_OPEN_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.cnlEndLongDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Cancel End Long', style=shape.xcross, location=location.bottom, color=color.new(CANCEL_CLOSE_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.startShortDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Start Short', style=shape.triangledown, location=location.bottom, color=color.new(SHORT_OPEN_COLOR, 70), offset=1, size=size.small, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.endShortDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input End Short', style=shape.square, location=location.top, color=color.new(CLOSE_COLOR, 70), offset=1, size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.cnlStartShortDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Cancel Start Short', style=shape.xcross, location=location.bottom, color=color.new(SHORT_CANCEL_OPEN_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)
    plotshape(series=inDealConditions.cnlEndShortDeal if isNotProduceOnly and isExternalSignalConnected else False, title='Input Cancel End Short', style=shape.xcross, location=location.top, color=color.new(CANCEL_CLOSE_COLOR, 70), size=size.tiny, display=display.pane + display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
