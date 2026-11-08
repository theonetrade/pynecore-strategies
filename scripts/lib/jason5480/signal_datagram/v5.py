"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, color, display, input, log, map, math, na, plot,
    runtime, script, string
)
from pynecore.types import Persistent
from typing import Protocol, Any


__all__ = ['ChannelDesc', 'Datagram', 'NumericSystem', 'Schema', 'Signal', 'WordDesc', 'WordPosArray', 'add_channel', 'get_channel_names', 'get_channel_value', 'get_signal', 'get_signal_sign', 'init', 'set_all_channels_max_value', 'set_all_channels_value', 'set_channel_value', 'set_signal', 'set_signal_sign']


class NumericSystem(Enum):
    binary = 'BIN'
    octal = 'OCT'
    decimal = 'DEC'
    hexadecimal = 'HEX'
    ducentohexaquinquagesimal = 'BYTE'


@udt
class WordDesc:
    span: int = 16


@udt
class WordPosArray:
    positions: list[int] = na(list)


@udt
class ChannelDesc:
    map__ren__: 'dict[str, WordPosArray]' = na(dict)


@udt
class Schema:
    wordDesc: 'WordDesc' = _dataclass_field(default_factory=lambda: na(WordDesc))
    channelDesc: 'ChannelDesc' = _dataclass_field(default_factory=lambda: na(ChannelDesc))


@udt
class Signal:
    value: int = 0
    isNegative: bool = False
    words: list[int] = na(list)


@udt
class Datagram:
    schema: 'Schema' = _dataclass_field(default_factory=lambda: na(Schema))
    signal: 'Signal' = _dataclass_field(default_factory=lambda: na(Signal))


class DatagramInputMode(Enum):
    signal = 'SIGNAL'
    channels = 'CHANNELS'


class _ProtocolInit(Protocol):
    def __call__(self, this: WordPosArray, positions: list[int], maxWords: int) -> Any: ...


class _ProtocolInit1(Protocol):
    def __call__(self, this: ChannelDesc) -> Any: ...


class _ProtocolAddChannel(Protocol):
    def __call__(self, this: ChannelDesc, name: str, positions: list[int]) -> Any: ...


class _ProtocolInit3(Protocol):
    def __call__(self, this: Datagram, numericSystem: NumericSystem, channelDesc: ChannelDesc) -> Any: ...


class _ProtocolSetSignal(Protocol):
    def __call__(self, this: Datagram, value: int) -> Any: ...


class _ProtocolGetSignal(Protocol):
    def __call__(self, this: Datagram) -> Any: ...


class _ProtocolSetSignalSign(Protocol):
    def __call__(self, this: Datagram, sign: int) -> Any: ...


class _ProtocolGetSignalSign(Protocol):
    def __call__(self, this: Datagram) -> Any: ...


class _ProtocolGetChannelNames(Protocol):
    def __call__(self, this: Datagram) -> Any: ...


class _ProtocolSetChannelValue(Protocol):
    def __call__(self, this: Datagram, channelName: str, value: int) -> Any: ...


class _ProtocolSetAllChannelsValue(Protocol):
    def __call__(self, this: Datagram, value: int) -> Any: ...


class _ProtocolSetAllChannelsMaxValue(Protocol):
    def __call__(self, this: Datagram) -> Any: ...


class _ProtocolGetChannelValue(Protocol):
    def __call__(self, this: Datagram, channelName: str) -> Any: ...


init: _ProtocolInit = Exported()
init: _ProtocolInit1 = Exported()
add_channel: _ProtocolAddChannel = Exported()
init: _ProtocolInit3 = Exported()
set_signal: _ProtocolSetSignal = Exported()
get_signal: _ProtocolGetSignal = Exported()
set_signal_sign: _ProtocolSetSignalSign = Exported()
get_signal_sign: _ProtocolGetSignalSign = Exported()
get_channel_names: _ProtocolGetChannelNames = Exported()
set_channel_value: _ProtocolSetChannelValue = Exported()
set_all_channels_value: _ProtocolSetAllChannelsValue = Exported()
set_all_channels_max_value: _ProtocolSetAllChannelsMaxValue = Exported()
get_channel_value: _ProtocolGetChannelValue = Exported()


CHANNEL_0_NAME: str = 'CH0'
CHANNEL_1_NAME: str = 'CH1'


@script.library(title='signal_datagram')
def main(
    numericSystem=input.enum(defval=NumericSystem.ducentohexaquinquagesimal, title='Numeric System', tooltip='The numeric system that is used. This will define what a single word represents (bit/octal/digit/nibble/hex/byte).'),
    inputMode=input.enum(defval=DatagramInputMode.signal, title='Datagram Input Mode', tooltip='The mode the datagram will operate. The SIGNAL mode will set the users signal value to the datagram and it will get back the chanel values. The CHANNELS mode will set the channel values set by the user to the datagram and it will get back the signal value.'),
    inputSignal=input.int(defval=4278190335, title='Signal Value', minval=-4503599627370495, maxval=4503599627370495, tooltip='The signal value to split into the channels that have words (octals/digits/nibbles/hexes/bytes) when SIGNAL mode is selected.', group='SIGNAL'),
    inputChannel0Value=input.int(defval=255, title='Channel 0 Value', tooltip='The value to set into the channel 0 when CHANNELS mode is selected.', group='CHANNELS'),
    inputChannel1Value=input.int(defval=255, title='Channel 1 Value', tooltip='The value to set into the channel 1 when CHANNELS mode is selected.', group='CHANNELS'),
    inputSign=input.int(defval=1, options=(1, -1), title='Sign', tooltip='The sign possitive or negative to set into the datagram when CHANNELS mode is selected.', group='CHANNELS'),
    testEnabled=input.bool(defval=False, title='Enable Test', tooltip='Test if the input and output signal and channel values are the same. If not log an error.')
):
    def log__global__(base: int, number: int):
        return math.log10(number) / math.log10(base)

    def max_words_of(span: int):
        INT_MAX_52_BITS: int = 4503599627370495
        return math.floor(log__global__(span, INT_MAX_52_BITS))



    @overload
    @method
    def init(this: WordDesc, numericSystem: NumericSystem):
        __block_result__ = na
        __switch__ = numericSystem
        if __switch__ == NumericSystem.binary:
            __block_result__ = 2
        elif __switch__ == NumericSystem.octal:
            __block_result__ = 8
        elif __switch__ == NumericSystem.decimal:
            __block_result__ = 10
        elif __switch__ == NumericSystem.hexadecimal:
            __block_result__ = 16
        elif __switch__ == NumericSystem.ducentohexaquinquagesimal:
            __block_result__ = 256
        else:
            runtime.error('Only word span of 2, 8, 10, 16 and 256 a.k.a bits, octals, digits, nibbles and bytes are supported.')
            __block_result__ = na
        this.span = __block_result__
        return this


    @overload
    @method
    def validate(this: WordPosArray, maxWords: int):
        for pos in this.positions:
            if pos >= maxWords:
                runtime.error(string.format('Position {0,number,integer} is not valid. Valid positions range from 0 to {1,number,integer}.', pos, maxWords - 1))
        return this

    @export
    @overload
    @method
    def init(this: WordPosArray, positions: list[int], maxWords: int):
        this.positions = positions
        return validate(this, maxWords)


    @overload
    @method
    def validate(this: ChannelDesc, maxWords: int):
        for _, wordPositions in this.map__ren__.items():
            validate(wordPositions, maxWords)
        return this

    @export
    @overload
    @method
    def init(this: ChannelDesc):
        this.map__ren__ = map.new()
        return this

    @method
    def num_of_channels(this: ChannelDesc):
        return map.size(this.map__ren__)

    @export
    @method
    def add_channel(this: ChannelDesc, name: str, positions: list[int]):
        if map.contains(this.map__ren__, name):
            runtime.error(string.format('The channel {0} has already been defined.', name))
        wordPosArrays: list[WordPosArray] = map.values(this.map__ren__)
        reservedPositions: list[int] = array.new_int()
        for wordPosArray in wordPosArrays:
            array.concat(reservedPositions, wordPosArray.positions)
        for pos in positions:
            for reserved in reservedPositions:
                if pos == reserved:
                    runtime.error(string.format('The position {0,number,integer} was already taken by an other channel.', pos))
        return map.put(this.map__ren__, name, WordPosArray(positions))

    @overload
    @method
    def get_channel_words_pos(this: ChannelDesc, name: str):
        if not map.contains(this.map__ren__, name):
            runtime.error(string.format('The channel {0} does not exist in the channel descriptor.', name))
        return map.get(this.map__ren__, name).positions

    @overload
    @method
    def get_channel_words_pos(this: ChannelDesc, name: str):
        if not map.contains(this.map__ren__, name):
            runtime.error(string.format('The channel {0} does not exist in the channel descriptor.', name))
        return map.get(this.map__ren__, name).positions


    @overload
    @method
    def validate(this: Schema):
        if na(this.wordDesc):
            runtime.error('The descriptor that defines what a word is has not been set.')
        if na(this.channelDesc):
            runtime.error('The map that defines the word positions of each channel has not been set.')
        numOfChannels: int = num_of_channels(this.channelDesc)
        if numOfChannels == 0:
            runtime.error('The Schema has no channels. At least one is required.')
        maxWords: int = max_words_of(this.wordDesc.span)
        if numOfChannels > maxWords:
            runtime.error(string.format('Schema has more channels {0,number,integer} than the maximum words allowed {1,number,integer}.', numOfChannels, maxWords))
        validate(this.channelDesc, maxWords)
        return this

    @overload
    @method
    def init(this: Schema, numericSystem: NumericSystem, channelDesc: ChannelDesc):
        this.wordDesc = method_call(init, WordDesc(), numericSystem)
        this.channelDesc = channelDesc
        return validate(this)


    @overload
    @method
    def init(this: Signal, wordSpan: int):
        this.words = array.new_int(max_words_of(wordSpan), 0)
        return this

    @method
    def set_value(this: Signal, value: int, wordDesc: WordDesc):
        INT_MAX_52_BITS: int = 4503599627370495
        INT_MAX_17_OCTALS: int = 2251799813685247
        INT_MAX_15_DIGITS: int = 999999999999999
        INT_MAX_13_NIBBLES: int = 4503599627370495
        INT_MAX_6_BYTES: int = 281474976710655
        wordSpan: int = wordDesc.span
        __block_result_1__ = na
        __switch__ = wordSpan
        if __switch__ == 2:
            __block_result_1__ = INT_MAX_52_BITS
        elif __switch__ == 8:
            __block_result_1__ = INT_MAX_17_OCTALS
        elif __switch__ == 10:
            __block_result_1__ = INT_MAX_15_DIGITS
        elif __switch__ == 16:
            __block_result_1__ = INT_MAX_13_NIBBLES
        elif __switch__ == 256:
            __block_result_1__ = INT_MAX_6_BYTES
        else:
            __block_result_1__ = INT_MAX_52_BITS
        INT_MAX: Persistent[int] = __block_result_1__
        INT_MIN: Persistent[int] = -INT_MAX
        if value > INT_MAX or value < INT_MIN:
            log.error('Value {0,number,integer} cannot be represented by a {1} integer (+1 sign bit)', value, '52bits' if wordSpan == 2 else '17octals' if wordSpan == 8 else '15digits' if wordSpan == 10 else '13nibbles' if wordSpan == 16 else '6bytes')
        this.value = value
        this.isNegative = value < 0
        signal: int = math.abs(value)
        size__ren__: int = array.size(this.words)
        for i in pine_range(0, size__ren__ - 1):
            array.set(this.words, i, signal % wordSpan)
            signal = cast_int(signal / wordSpan)
        return this

    @method
    def get_value(this: Signal, wordSpan: int):
        signal: int = 0
        for i, word in enumerate(this.words):
            signal = signal + word * cast_int(math.pow(wordSpan, i))
        return -1 * signal if this.isNegative else signal


    @export
    @overload
    @method
    def init(this: Datagram, numericSystem: NumericSystem, channelDesc: ChannelDesc):
        this.schema = method_call(init, Schema(), numericSystem, channelDesc)
        this.signal = method_call(init, Signal(), this.schema.wordDesc.span)
        return this

    @export
    @method
    def set_signal(this: Datagram, value: int):
        return set_value(this.signal, value, this.schema.wordDesc)

    @export
    @method
    def get_signal(this: Datagram):
        return get_value(this.signal, this.schema.wordDesc.span)

    @export
    @method
    def set_signal_sign(this: Datagram, sign: int):
        this.signal.isNegative = sign < 0
        return this.signal.isNegative

    @export
    @method
    def get_signal_sign(this: Datagram):
        return -1 if this.signal.isNegative else 1

    @export
    @method
    def get_channel_names(this: Datagram):
        return map.keys(this.schema.channelDesc.map__ren__)

    @export
    @method
    def set_channel_value(this: Datagram, channelName: str, value: int):
        wordPositions: list[int] = get_channel_words_pos(this.schema.channelDesc, channelName)
        size__ren__: int = array.size(wordPositions)
        if value < 0 or value >= math.pow(this.schema.wordDesc.span, size__ren__):
            log.error('The value {0,number,integer} cannot be expressed with {1,number,integer} word(s) of range from 0 to {2,number,integer}', value, size__ren__, this.schema.wordDesc.span - 1)
        temp: Signal = method_call(set_value, method_call(init, Signal(), this.schema.wordDesc.span), value, this.schema.wordDesc)
        __block_result_2__ = na
        for i, pos in enumerate(wordPositions):
            __block_result_2__ = array.set(this.signal.words, pos, array.get(temp.words, i))
        return __block_result_2__

    @export
    @method
    def set_all_channels_value(this: Datagram, value: int):
        __block_result_3__ = na
        for channelName in get_channel_names(this):
            wordPositions: list[int] = get_channel_words_pos(this.schema.channelDesc, channelName)
            size__ren__: int = array.size(wordPositions)
            if value < 0 or value >= math.pow(this.schema.wordDesc.span, size__ren__):
                log.error('The value {0,number,integer} cannot be expressed with {1,number,integer} word(s) of range from 0 to {2,number,integer}', value, size__ren__, this.schema.wordDesc.span - 1)
            temp: Signal = method_call(set_value, method_call(init, Signal(), this.schema.wordDesc.span), value, this.schema.wordDesc)
            __block_result_4__ = na
            for i, pos in enumerate(wordPositions):
                __block_result_4__ = array.set(this.signal.words, pos, array.get(temp.words, i))
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    @export
    @method
    def set_all_channels_max_value(this: Datagram):
        __block_result_5__ = na
        for channelName in get_channel_names(this):
            wordPositions: list[int] = get_channel_words_pos(this.schema.channelDesc, channelName)
            size__ren__: int = array.size(wordPositions)
            maximum: int = cast_int(math.pow(this.schema.wordDesc.span, size__ren__)) - 1
            temp: Signal = method_call(set_value, method_call(init, Signal(), this.schema.wordDesc.span), maximum, this.schema.wordDesc)
            __block_result_6__ = na
            for i, pos in enumerate(wordPositions):
                __block_result_6__ = array.set(this.signal.words, pos, array.get(temp.words, i))
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    @export
    @method
    def get_channel_value(this: Datagram, channelName: str):
        if na(this.signal.words):
            runtime.error('No signal has been set. Set the signal by using the "set_signal" method.')
        wordPositions: list[int] = get_channel_words_pos(this.schema.channelDesc, channelName)
        value: int = 0
        for i, pos in enumerate(wordPositions):
            value = value + array.get(this.signal.words, pos) * cast_int(math.pow(this.schema.wordDesc.span, i))
        return value



    datagram: Persistent[Datagram] = na(Datagram)
    if barstate.isfirst:
        channelWordPosMap: ChannelDesc = method_call(init, ChannelDesc())
        __block_result_7__ = na
        __switch_1__ = numericSystem
        if __switch_1__ == NumericSystem.binary:
            __block_result_7__ = array.from_items(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25)
        elif __switch_1__ == NumericSystem.octal:
            __block_result_7__ = array.from_items(0, 1, 2, 3, 4, 5, 6, 7)
        elif __switch_1__ == NumericSystem.decimal:
            __block_result_7__ = array.from_items(0, 1, 2, 3, 4, 5, 6)
        elif __switch_1__ == NumericSystem.hexadecimal:
            __block_result_7__ = array.from_items(0, 1, 2, 3, 4, 5)
        elif __switch_1__ == NumericSystem.ducentohexaquinquagesimal:
            __block_result_7__ = array.from_items(0, 1, 2)
        channel0Pos: list[int] = __block_result_7__
        add_channel(channelWordPosMap, CHANNEL_0_NAME, channel0Pos)
        __block_result_8__ = na
        __switch_1__ = numericSystem
        if __switch_1__ == NumericSystem.binary:
            __block_result_8__ = array.from_items(26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51)
        elif __switch_1__ == NumericSystem.octal:
            __block_result_8__ = array.from_items(8, 9, 10, 11, 12, 13, 14, 15, 16)
        elif __switch_1__ == NumericSystem.decimal:
            __block_result_8__ = array.from_items(7, 8, 9, 10, 11, 12, 13, 14)
        elif __switch_1__ == NumericSystem.hexadecimal:
            __block_result_8__ = array.from_items(6, 7, 8, 9, 10, 11, 12)
        elif __switch_1__ == NumericSystem.ducentohexaquinquagesimal:
            __block_result_8__ = array.from_items(3, 4, 5)
        channel1Pos: list[int] = __block_result_8__
        add_channel(channelWordPosMap, CHANNEL_1_NAME, channel1Pos)
        datagram = method_call(init, Datagram(), numericSystem, channelWordPosMap)

    if inputMode == DatagramInputMode.signal:
        set_signal(datagram, inputSignal)
    elif inputMode == DatagramInputMode.channels:
        set_channel_value(datagram, CHANNEL_0_NAME, inputChannel0Value)
        set_channel_value(datagram, CHANNEL_1_NAME, inputChannel1Value)
        set_signal_sign(datagram, inputSign)

    outputSignal: int = get_signal(datagram)
    outputChannel0Value: int = get_channel_value(datagram, CHANNEL_0_NAME)
    outputChannel1Value: int = get_channel_value(datagram, CHANNEL_1_NAME)
    outputSign: int = get_signal_sign(datagram)

    if testEnabled and barstate.islastconfirmedhistory and (inputSignal != outputSignal):
        log.error('The output signal = {0,number,integer} is different than the input signal = {1,number,integer}', outputSignal, inputSignal)
    if testEnabled and barstate.islastconfirmedhistory and (inputChannel0Value != outputChannel0Value):
        log.error('The output channel 0 value = {0,number,integer} is different than the input channel 0 value = {1,number,integer}', outputChannel0Value, inputChannel0Value)
    if testEnabled and barstate.islastconfirmedhistory and (inputChannel1Value != outputChannel1Value):
        log.error('The output channel 1 value = {0,number,integer} is different than the input channel 1 value = {1,number,integer}', outputChannel1Value, inputChannel1Value)
    if testEnabled and barstate.islastconfirmedhistory and (inputSign != outputSign):
        log.error('The output signal sign = {0,number,integer} is different than the input signal sign = {1,number,integer}', outputSign, inputSign)

    words__global__: list[int] = datagram.signal.words
    numOfWords: Persistent[int] = array.size(words__global__)

    plot(series=outputSignal, title='Output Signal', color=color.orange, display=display.all - display.price_scale - display.pane, precision=0)
    plot(series=outputChannel0Value, title=CHANNEL_0_NAME, color=color.maroon, display=display.all - display.price_scale - display.pane, precision=0)
    plot(series=outputChannel1Value, title=CHANNEL_1_NAME, color=color.teal, display=display.all - display.price_scale - display.pane, precision=0)
    plot(series=outputSign, title='Output Sign', color=color.black, display=display.all - display.price_scale - display.pane, precision=0)

    plot(series=numOfWords, title='Num of Words', color=color.navy, display=display.data_window)

    plot(series=array.get(words__global__, 5) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte5', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)
    plot(series=array.get(words__global__, 4) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte4', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)
    plot(series=array.get(words__global__, 3) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte3', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)
    plot(series=array.get(words__global__, 2) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte2', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)
    plot(series=array.get(words__global__, 1) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte1', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)
    plot(series=array.get(words__global__, 0) if numericSystem == NumericSystem.ducentohexaquinquagesimal else na, title='Byte0', color=color.olive, display=display.all - display.price_scale if numericSystem == NumericSystem.ducentohexaquinquagesimal else display.none, precision=0)

    plot(series=array.get(words__global__, 12) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble12', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 11) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble11', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 10) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble10', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 9) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble9', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 8) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble8', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 7) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble7', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 6) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble6', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 5) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble5', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 4) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble4', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 3) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble3', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 2) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble2', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 1) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble1', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)
    plot(series=array.get(words__global__, 0) if numericSystem == NumericSystem.hexadecimal else na, title='Nibble0', color=color.aqua, display=display.all - display.price_scale if numericSystem == NumericSystem.hexadecimal else display.none, precision=0)

    plot(series=array.get(words__global__, 14) if numericSystem == NumericSystem.decimal else na, title='Digit14', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 13) if numericSystem == NumericSystem.decimal else na, title='Digit13', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 12) if numericSystem == NumericSystem.decimal else na, title='Digit12', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 11) if numericSystem == NumericSystem.decimal else na, title='Digit11', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 10) if numericSystem == NumericSystem.decimal else na, title='Digit10', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 9) if numericSystem == NumericSystem.decimal else na, title='Digit9', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 8) if numericSystem == NumericSystem.decimal else na, title='Digit8', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 7) if numericSystem == NumericSystem.decimal else na, title='Digit7', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 6) if numericSystem == NumericSystem.decimal else na, title='Digit6', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 5) if numericSystem == NumericSystem.decimal else na, title='Digit5', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 4) if numericSystem == NumericSystem.decimal else na, title='Digit4', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 3) if numericSystem == NumericSystem.decimal else na, title='Digit3', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 2) if numericSystem == NumericSystem.decimal else na, title='Digit2', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 1) if numericSystem == NumericSystem.decimal else na, title='Digit1', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)
    plot(series=array.get(words__global__, 0) if numericSystem == NumericSystem.decimal else na, title='Digit0', color=color.fuchsia, display=display.all - display.price_scale if numericSystem == NumericSystem.decimal else display.none, precision=0)

    plot(series=array.get(words__global__, 16) if numericSystem == NumericSystem.octal else na, title='Octal16', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 15) if numericSystem == NumericSystem.octal else na, title='Octal15', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 14) if numericSystem == NumericSystem.octal else na, title='Octal14', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 13) if numericSystem == NumericSystem.octal else na, title='Octal13', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 12) if numericSystem == NumericSystem.octal else na, title='Octal12', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 11) if numericSystem == NumericSystem.octal else na, title='Octal11', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 10) if numericSystem == NumericSystem.octal else na, title='Octal10', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 9) if numericSystem == NumericSystem.octal else na, title='Octal9', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 8) if numericSystem == NumericSystem.octal else na, title='Octal8', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 7) if numericSystem == NumericSystem.octal else na, title='Octal7', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 6) if numericSystem == NumericSystem.octal else na, title='Octal6', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 5) if numericSystem == NumericSystem.octal else na, title='Octal5', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 4) if numericSystem == NumericSystem.octal else na, title='Octal4', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 3) if numericSystem == NumericSystem.octal else na, title='Octal3', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 2) if numericSystem == NumericSystem.octal else na, title='Octal2', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 1) if numericSystem == NumericSystem.octal else na, title='Octal1', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)
    plot(series=array.get(words__global__, 0) if numericSystem == NumericSystem.octal else na, title='Octal0', color=color.purple, display=display.all - display.price_scale if numericSystem == NumericSystem.octal else display.none, precision=0)

    plot(series=array.get(words__global__, 51) if numericSystem == NumericSystem.binary else na, title='Bit51', color=color.silver, display=display.all - display.price_scale if numericSystem == NumericSystem.binary else display.none, precision=0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
