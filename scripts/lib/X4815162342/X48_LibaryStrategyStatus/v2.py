"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    bar_index, color, high, last_bar_index, low, math, na, nz, position,
    script, size, strategy, string, syminfo, ta, table, time, timestamp
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Table
from typing import Protocol, Any


__all__ = ['Count_Bar_Back_Test', 'NetProfit_Show', 'Win_Loss_Show', 'calcProfitTrgtPrice', 'calcStopLossPrice', 'calcTrailingAmountLevel', 'calcTrailingOffsetLevel', 'curProfitInPts', 'getCurrentStage', 'percen', 'trailing_3step']


class _ProtocolWinLossShow(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolNetprofitShow(Protocol):
    def __call__(self, show_Net: bool, position_: str, size_i: str, color_Net: Color) -> Any: ...


class _ProtocolCountBarBackTest(Protocol):
    def __call__(self, Back_Test: bool, Back_Test_bar_start: int, Back_Test_step_start: int, Back_Test_bar_end: int, Back_Test_step_end: int, i_dateFilter: bool, i_fromYear: int, i_fromMonth: int, i_fromDay: int, i_toYear: int, i_toMonth: int, i_toDay: int) -> Any: ...


class _ProtocolPercen(Protocol):
    def __call__(self, pcnt: float) -> Any: ...


class _ProtocolCurprofitinpts(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolCalcstoplossprice(Protocol):
    def __call__(self, OffsetPts: float) -> Any: ...


class _ProtocolCalcprofittrgtprice(Protocol):
    def __call__(self, OffsetPts: float) -> Any: ...


class _ProtocolGetcurrentstage(Protocol):
    def __call__(self, tp1: float, tp2: float) -> Any: ...


class _ProtocolCalctrailingamountlevel(Protocol):
    def __call__(self, points: float) -> Any: ...


class _ProtocolCalctrailingoffsetlevel(Protocol):
    def __call__(self, points: float, offset: float) -> Any: ...


class _ProtocolTrailing3Step(Protocol):
    def __call__(self, tp1_: float, tp2_: float, tp3_: float, activateTrailingOnThirdStep: bool, sl_: float) -> Any: ...


Win_Loss_Show: _ProtocolWinLossShow = Exported()
NetProfit_Show: _ProtocolNetprofitShow = Exported()
Count_Bar_Back_Test: _ProtocolCountBarBackTest = Exported()
percen: _ProtocolPercen = Exported()
curProfitInPts: _ProtocolCurprofitinpts = Exported()
calcStopLossPrice: _ProtocolCalcstoplossprice = Exported()
calcProfitTrgtPrice: _ProtocolCalcprofittrgtprice = Exported()
getCurrentStage: _ProtocolGetcurrentstage = Exported()
calcTrailingAmountLevel: _ProtocolCalctrailingamountlevel = Exported()
calcTrailingOffsetLevel: _ProtocolCalctrailingoffsetlevel = Exported()
trailing_3step: _ProtocolTrailing3Step = Exported()


@script.library('X48_LibaryStrategyStatus')
def main():
    @export
    def Win_Loss_Show():
        entryP: Persistent[float] = 0.0
        exitP: Persistent[float] = 0.0
        if cast_bool(ta.change(strategy.position_size)) and strategy.position_size == 0:
            entryP = nz(strategy.closedtrades.entry_price(strategy.closedtrades - 1))
            exitP = nz(strategy.closedtrades.exit_price(strategy.closedtrades - 1))
        buy_entryP = entryP
        sell_exitP = exitP
        buy_SELL: PersistentSeries[int] = 2
        buy_SELL = 0 if strategy.position_size > 0 else 1 if strategy.position_size < 0 else 2
        change_1 = ta.change(strategy.position_size)
        win = nz(buy_SELL[1]) == 0 and cast_bool(change_1) and (strategy.position_size == 0) and (buy_entryP < sell_exitP)
        change_2 = ta.change(strategy.position_size)
        loss = nz(buy_SELL[1]) == 0 and cast_bool(change_2) and (strategy.position_size == 0) and (buy_entryP > sell_exitP)
        change_3 = ta.change(strategy.position_size)
        equal = nz(buy_SELL[1]) == 0 and cast_bool(change_3) and (strategy.position_size == 0) and (buy_entryP == sell_exitP)
        return (win, loss, equal)

    @export
    def NetProfit_Show(show_Net: bool, position_: str, size_i: str, color_Net: Color):
        percenProfit = strategy.netprofit / strategy.initial_capital * 100
        colprofit = color.red if percenProfit < 0 else color.white
        profitFac = strategy.grossprofit / strategy.grossloss
        percenwin = strategy.wintrades / strategy.closedtrades * 100
        Netprofit = string.tostring(strategy.netprofit, '#,###.##') + '\n' + string.tostring(percenProfit, '#,###.##') + ' % '
        win = string.tostring(percenwin, '#.##') + ' % '
        profitFactor = string.tostring(profitFac, '#.###')
        close_Trade = string.tostring(strategy.closedtrades, '#,###') + '\n' + 'W: ' + string.tostring(strategy.wintrades) + ' | L: ' + string.tostring(strategy.losstrades)
        max_drawdown = string.tostring(strategy.max_drawdown, '#,###.##')
        tra: int = 80
        position_CH = position.bottom_right if position_ == 'bottom_right' else position.bottom_left if position_ == 'bottom_left' else position.bottom_center if position_ == 'bottom_center' else position.middle_right if position_ == 'middle_right' else position.middle_left if position_ == 'middle_left' else position.middle_center if position_ == 'middle_center' else position.top_right if position_ == 'top_right' else position.top_center if position_ == 'top_center' else position.bottom_right
        size_ = size.auto if size_i == 'auto' else size.tiny if size_i == 'tiny' else size.small if size_i == 'small' else size.normal if size_i == 'small' else size.auto
        __block_result__ = na
        if show_Net:
            table_Net: Table = table.new(position_CH, 5, 50, border_color=color.black, border_width=1)
            table.cell(table_Net, 0, 1, 'Netprofit', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 1, 1, 'CloseTrade', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 2, 1, 'Win', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 3, 1, 'Factor', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 4, 1, 'Drawdown', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 0, 2, Netprofit, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(colprofit, 0))
            table.cell(table_Net, 1, 2, close_Trade, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(color.white, 0))
            table.cell(table_Net, 2, 2, win, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(color.white, 0))
            table.cell(table_Net, 3, 2, profitFactor, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(colprofit, 0))
            __block_result__ = table.cell(table_Net, 4, 2, max_drawdown, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(color.red, 0))
        return __block_result__

    @export
    def Count_Bar_Back_Test(Back_Test: bool, Back_Test_bar_start: int, Back_Test_step_start: int, Back_Test_bar_end: int, Back_Test_step_end: int, i_dateFilter: bool, i_fromYear: int, i_fromMonth: int, i_fromDay: int, i_toYear: int, i_toMonth: int, i_toDay: int):
        count_backtest_bar_start = Back_Test_bar_start * Back_Test_step_start if Back_Test else 0
        count_backtest_bar_end = last_bar_index - Back_Test_bar_end * Back_Test_step_end if Back_Test else last_bar_index
        BarBackTEST = bar_index >= count_backtest_bar_start and bar_index <= count_backtest_bar_end
        maxbar = last_bar_index / Back_Test_step_start
        fromDate = timestamp(i_fromYear, i_fromMonth, i_fromDay, 0, 0)
        toDate = time if time < timestamp(i_toYear, i_toMonth, i_toDay, 23, 59) else timestamp(i_toYear, i_toMonth, i_toDay, 23, 59)
        date_start_entry = (time if fromDate < time else fromDate) if i_dateFilter else time
        begin: Persistent = date_start_entry
        days = (toDate - begin) / (24 * 60 * 60 * 1000)
        mess1 = string.tostring(days, '#.0 days /') + string.tostring(days / 30, '#.0 month  /') + string.tostring(strategy.closedtrades / days, '#.0 ') + 'ครั้งต่อวัน'
        mess2 = ('start ' + string.tostring(count_backtest_bar_start, '#,###.##') + '....Over Bar' + ' MAX:' + string.tostring(maxbar, '#,###') if count_backtest_bar_start > last_bar_index else 'start ' + string.tostring(count_backtest_bar_start, '#,###.##') + ' MAX:' + string.tostring(maxbar, '#,###')) if Back_Test else 'start 0 Bar  MAX:' + string.tostring(maxbar, '#,###')
        mess3 = ('end ' + string.tostring(last_bar_index, '#,###.##') + ' - ' + string.tostring(Back_Test_bar_end * Back_Test_step_end) + ' = ' + string.tostring(count_backtest_bar_end, '#,###.##') if Back_Test else 'end ' + string.tostring(count_backtest_bar_end, '#,###.##')) + ' Bar'
        table_countbar: Table = table.new(position.bottom_right, 1, 50, border_color=color.orange)
        table.cell(table_countbar, 0, 0, mess1, bgcolor=color.new(color.blue, 80), text_color=color.new(color.white, 0))
        table.cell(table_countbar, 0, 1, mess2, bgcolor=color.new(color.red, 80), text_color=color.new(color.red, 0) if count_backtest_bar_start > last_bar_index else color.new(color.white, 15))
        table.cell(table_countbar, 0, 2, mess3, bgcolor=color.new(color.red, 80), text_color=color.new(color.white, 0))
        x = BarBackTEST and (not i_dateFilter or (time >= fromDate and time <= toDate))
        return x

    @export
    def percen(pcnt: float):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    @export
    def curProfitInPts():
        __block_result_1__ = na
        if strategy.position_size > 0:
            __block_result_1__ = (high - strategy.position_avg_price) / syminfo.mintick
        elif strategy.position_size < 0:
            __block_result_1__ = (strategy.position_avg_price - low) / syminfo.mintick
        else:
            __block_result_1__ = 0
        return __block_result_1__

    @export
    def calcStopLossPrice(OffsetPts: float):
        price: Persistent[float] = 0.0
        __block_result_2__ = na
        if strategy.position_size > 0:
            price = strategy.position_avg_price - OffsetPts * syminfo.mintick
            __block_result_2__ = price
        elif strategy.position_size < 0:
            price = strategy.position_avg_price + OffsetPts * syminfo.mintick
            __block_result_2__ = price
        else:
            price = na
            __block_result_2__ = price
        return __block_result_2__

    @export
    def calcProfitTrgtPrice(OffsetPts: float):
        return calcStopLossPrice(-OffsetPts)

    @export
    def getCurrentStage(tp1: float, tp2: float):
        stage: Persistent[int] = 0
        if strategy.position_size == 0:
            stage = 0
        curProfitInPts_1 = curProfitInPts()
        curProfitInPts_2 = curProfitInPts()
        if stage == 0 and strategy.position_size != 0:
            stage = 1
        elif stage == 1 and curProfitInPts_1 >= tp1:
            stage = 2
        elif stage == 2 and curProfitInPts_2 >= tp2:
            stage = 3
        return stage

    @export
    def calcTrailingAmountLevel(points: float):
        level: PersistentSeries[float] = na(float)
        level = calcProfitTrgtPrice(points)
        __block_result_3__ = na
        if not na(level):
            __block_result_4__ = na
            if strategy.position_size > 0:
                if not na(level[1]):
                    level = math.max(level[1], level)
                __block_result_5__ = na
                if not na(level):
                    level = math.max(high, level)
                    __block_result_5__ = level
                __block_result_4__ = __block_result_5__
            elif strategy.position_size < 0:
                if not na(level[1]):
                    level = math.min(level[1], level)
                __block_result_6__ = na
                if not na(level):
                    level = math.min(low, level)
                    __block_result_6__ = level
                __block_result_4__ = __block_result_6__
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    @export
    def calcTrailingOffsetLevel(points: float, offset: float):
        result: float = na(float)
        amountLevel = calcTrailingAmountLevel(points)
        if strategy.position_size > 0:
            trailActiveDiff = amountLevel - calcProfitTrgtPrice(points)
            if trailActiveDiff > 0:
                result = trailActiveDiff + calcProfitTrgtPrice(offset)
        elif strategy.position_size < 0:
            trailActiveDiff = calcProfitTrgtPrice(points) - amountLevel
            if trailActiveDiff > 0:
                result = calcProfitTrgtPrice(offset) - trailActiveDiff
        return result

    @export
    def trailing_3step(tp1_: float, tp2_: float, tp3_: float, activateTrailingOnThirdStep: bool, sl_: float):
        tp1: Persistent[float] = 0.0
        tp1 = percen(tp1_)
        tp2: Persistent[float] = 0.0
        tp2 = percen(tp2_)
        tp3: Persistent[float] = 0.0
        tp3 = percen(tp3_)
        sl: Persistent[float] = 0.0
        sl = percen(sl_)
        stopLevel: float = na(float)
        trailOffsetLevel: float = na(float)
        c1: float = calcTrailingAmountLevel(tp3)
        c2: float = calcProfitTrgtPrice(tp3)
        profitLevel: float = c1 if activateTrailingOnThirdStep else c2
        curStage = getCurrentStage(tp1, tp2)
        __block_result_7__ = na
        if curStage == 1:
            stopLevel = calcStopLossPrice(sl)
            __block_result_7__ = strategy.exit('x', loss=sl, profit=tp3, comment='sl or tp3')
        elif curStage == 2:
            stopLevel = calcStopLossPrice(0)
            __block_result_7__ = strategy.exit('x', stop=stopLevel, profit=tp3, comment='breakeven or tp3')
        elif curStage == 3:
            stopLevel = calcStopLossPrice(-tp1)
            __block_result_8__ = na
            if activateTrailingOnThirdStep:
                __block_result_8__ = strategy.exit('x', stop=stopLevel, trail_points=tp3, trail_offset=tp3 - tp2, comment='stop tp1 or trailing tp3 with offset tp2')
            else:
                __block_result_8__ = strategy.exit('x', stop=stopLevel, profit=tp3, comment='tp1 or tp3')
            __block_result_7__ = __block_result_8__
        else:
            __block_result_7__ = strategy.cancel('x')
        return __block_result_7__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
