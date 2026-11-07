"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    bar_index, color, last_bar_index, na, nz, position, script, size,
    strategy, string, ta, table, time, timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries, Table
from typing import Protocol, Any


__all__ = ['Count_Bar_Back_Test', 'NetProfit_Show', 'Win_Loss_Show']


class _ProtocolWinLossShow(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolNetprofitShow(Protocol):
    def __call__(self, show_Net: bool, position_: str, size_i: str, color_Net: Color) -> Any: ...


class _ProtocolCountBarBackTest(Protocol):
    def __call__(self, Back_Test: bool, Back_Test_bar_start: int, Back_Test_step_start: int, Back_Test_bar_end: int, Back_Test_step_end: int, i_dateFilter: bool, i_fromYear: int, i_fromMonth: int, i_fromDay: int, i_toYear: int, i_toMonth: int, i_toDay: int) -> Any: ...


Win_Loss_Show: _ProtocolWinLossShow = Exported()
NetProfit_Show: _ProtocolNetprofitShow = Exported()
Count_Bar_Back_Test: _ProtocolCountBarBackTest = Exported()


@script.library('Cayoshi_Library')
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
        close_Trad = string.tostring(strategy.closedtrades, '#,###') + '\n' + 'W: ' + string.tostring(strategy.wintrades) + ' |L: ' + string.tostring(strategy.losstrades)
        max_drawdown = string.tostring(strategy.max_drawdown, '#,###.##')
        tra: int = 80
        position_CH = position.bottom_right if position_ == 'bottom_right' else position.bottom_left if position_ == 'bottom_left' else position.bottom_center if position_ == 'bottom_center' else position.middle_right if position_ == 'middle_right' else position.middle_left if position_ == 'middle_left' else position.middle_center if position_ == 'middle_center' else position.top_right if position_ == 'top_right' else position.top_center if position_ == 'top_center' else position.bottom_right
        size_ = size.auto if size_i == 'auto' else size.tiny if size_i == 'tiny' else size.small if size_i == 'small' else size.normal if size_i == 'small' else size.auto
        __block_result__ = na
        if show_Net:
            table_Net: Table = table.new(position_CH, 5, 50, border_color=color.black, border_width=1)
            table.cell(table_Net, 0, 1, 'Netprofit', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 1, 1, 'CloseTrad', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 2, 1, 'Win', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 3, 1, 'Factor', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 4, 1, 'Drawdown', text_size=size_, bgcolor=color.new(color_Net, tra), text_color=color.new(color.white, 0))
            table.cell(table_Net, 0, 2, Netprofit, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(colprofit, 0))
            table.cell(table_Net, 1, 2, close_Trad, text_size=size_, bgcolor=color.new(color.black, 30), text_color=color.new(color.white, 0))
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


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
