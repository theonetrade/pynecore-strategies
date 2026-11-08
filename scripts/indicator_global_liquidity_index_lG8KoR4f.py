"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, close, color, currency, input, math, na, plot, position,
    request, scale, script, string, syminfo, ta, table
)
from pynecore.types import Persistent, Series, Table


@script.indicator(title='Global Liquidity Index', shorttitle='GLI', overlay=True, scale=scale.left)
def main(
    fed_active=input.bool(True, title='FED Balance Sheet'),
    tga_active=input.bool(True, title='Treasury General Account'),
    rrp_active=input.bool(True, title='Reverse Repo Facility'),
    ecb_active=input.bool(True, title='ECB Balance Sheet'),
    pbc_active=input.bool(True, title='PBC Balance Sheet'),
    boj_active=input.bool(True, title='BOJ Balance Sheet'),
    boe_active=input.bool(True, title='BOE Balance Sheet'),
    other_active=input.bool(True, title='Other Balance Sheets'),
    us_active=input.bool(True, title='US Money Supply'),
    europe_active=input.bool(True, title='Euro Area Money Supply'),
    china_active=input.bool(True, title='China Money Supply'),
    japan_active=input.bool(True, title='Japan Money Supply'),
    uk_active=input.bool(True, title='UK Money Supply'),
    other_ms_active=input.bool(True, title='Other Money Supplies'),
    sma_input_raw=input.int(0, title='SMA Length', minval=0),
    roc_input=input.int(0, title='ROC Length', minval=0),
    offset_input=input.int(0, title='Offset Bars'),
    strategy_type=input.string('EMA', title='Trend Type', options=('EMA', 'SMA', 'RMA', 'WMA')),
    fast_length=input.int(30, title='Fast Length', minval=1),
    slow_length=input.int(60, title='Slow Length', minval=2),
    change_length=input.int(30, title='Change Period', minval=1),
    change_sma=input.int(10, title='Change SMA', minval=1),
    beta_input=input.string('1Y', title='Beta Length', options=('3M', '6M', '9M', '1Y', '3Y', '5Y')),
    max_offset=input.int(150, title='Max Offset'),
    min_offset=input.int(-150, title='Min Offset'),
    corr_input=input.string('6M', title='Offset Corr', options=('1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y')),
    r2_threshold_input=input.float(25.0, title='R² Threshold', minval=0.0),
    width_input=input.int(10, title='Table Width', minval=1),
    table_input=input.string('Low', title='Table Position', options=('High', 'Middle', 'Low'))
):
    table_position = position.top_right if table_input == 'High' else position.middle_right if table_input == 'Middle' else position.bottom_right
    fed = request.security('ECONOMICS:USCBBS', 'D', close, currency=currency.USD) if fed_active else 0
    rrp = request.security('FRED:RRPONTSYD', 'D', close, currency=currency.USD) if rrp_active else 0
    tga = request.security('FRED:WTREGEN', 'D', close, currency=currency.USD) if tga_active else 0
    ecb = request.security('ECONOMICS:EUCBBS * FX_IDC:EURUSD', 'D', close, currency=currency.USD) if ecb_active else 0
    pbc = request.security('ECONOMICS:CNCBBS * FX_IDC:CNYUSD', 'D', close, currency=currency.USD) if pbc_active else 0
    boj = request.security('ECONOMICS:JPCBBS * FX_IDC:JPYUSD', 'D', close, currency=currency.USD) if boj_active else 0
    boe = request.security('ECONOMICS:GBCBBS * FX_IDC:GBPUSD', 'D', close, currency=currency.USD) if boe_active else 0
    rbi = request.security('ECONOMICS:INCBBS * FX_IDC:INRUSD', 'D', close, currency=currency.USD) if other_active else 0
    bok = request.security('ECONOMICS:KRCBBS * FX_IDC:KRWUSD', 'D', close, currency=currency.USD) if other_active else 0
    bcb = request.security('ECONOMICS:BRCBBS * FX_IDC:BRLUSD', 'D', close, currency=currency.USD) if other_active else 0
    boc = request.security('ECONOMICS:CACBBS * FX_IDC:CADUSD', 'D', close, currency=currency.USD) if other_active else 0
    rba = request.security('ECONOMICS:AUCBBS * FX_IDC:AUDUSD', 'D', close, currency=currency.USD) if other_active else 0
    snb = request.security('ECONOMICS:CHCBBS * FX_IDC:CHFUSD', 'D', close, currency=currency.USD) if other_active else 0
    cbr = request.security('ECONOMICS:RUCBBS * FX_IDC:RUBUSD', 'D', close, currency=currency.USD) if other_active else 0
    bx = request.security('ECONOMICS:MXCBBS * FX_IDC:MXNUSD', 'D', close, currency=currency.USD) if other_active else 0
    bot = request.security('ECONOMICS:THCBBS * FX_IDC:THBUSD', 'D', close, currency=currency.USD) if other_active else 0
    nbp = request.security('ECONOMICS:PLCBBS * FX_IDC:PLNUSD', 'D', close, currency=currency.USD) if other_active else 0
    bnm = request.security('ECONOMICS:MYCBBS * FX_IDC:MYRUSD', 'D', close, currency=currency.USD) if other_active else 0
    sr = request.security('ECONOMICS:SECBBS * FX_IDC:SEKUSD', 'D', close, currency=currency.USD) if other_active else 0
    sarb = request.security('ECONOMICS:ZACBBS * FX_IDC:ZARUSD', 'D', close, currency=currency.USD) if other_active else 0
    rbzn = request.security('ECONOMICS:NZCBBS * FX_IDC:NZDUSD', 'D', close, currency=currency.USD) if other_active else 0
    us = request.security('ECONOMICS:USM2', 'D', close, currency=currency.USD) if us_active else 0
    eu = request.security('ECONOMICS:EUM3 * FX_IDC:EURUSD', 'D', close, currency=currency.USD) if europe_active else 0
    china = request.security('ECONOMICS:CNM2 * FX_IDC:CNYUSD', 'D', close, currency=currency.USD) if china_active else 0
    japan = request.security('ECONOMICS:JPM3 * FX_IDC:JPYUSD', 'D', close, currency=currency.USD) if japan_active else 0
    uk = request.security('ECONOMICS:GBM3 * FX_IDC:GBPUSD', 'D', close, currency=currency.USD) if uk_active else 0
    india = request.security('ECONOMICS:INM3 * FX_IDC:INRUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    korea = request.security('ECONOMICS:KRM2 * FX_IDC:KRWUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    brazil = request.security('ECONOMICS:BRM3 * FX_IDC:BRLUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    canada = request.security('ECONOMICS:CAM3 * FX_IDC:CADUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    australia = request.security('ECONOMICS:AUM3 * FX_IDC:AUDUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    switzerland = request.security('ECONOMICS:CHM3 * FX_IDC:CHFUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    russia = request.security('ECONOMICS:RUM2 * FX_IDC:RUBUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    mexico = request.security('ECONOMICS:MXM2 * FX_IDC:MXNUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    thailand = request.security('ECONOMICS:THM3 * FX_IDC:THBUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    poland = request.security('ECONOMICS:PLM3 * FX_IDC:PLNUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    malaysia = request.security('ECONOMICS:MYM3 * FX_IDC:MYRUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    sweden = request.security('ECONOMICS:SEM3 * FX_IDC:SEKUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    sa = request.security('ECONOMICS:ZAM3 * FX_IDC:ZARUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    nz__ren__ = request.security('ECONOMICS:NZM3 * FX_IDC:NZDUSD', 'D', close, currency=currency.USD) if other_ms_active else 0
    total: Series = (fed - rrp - tga + ecb + pbc + boj + boe + rbi + bok + bcb + boc + rba + snb + cbr + bx + bot + nbp + bnm + sr + sarb + rbzn + us + eu + china + japan + uk + india + korea + brazil + canada + australia + switzerland + russia + mexico + thailand + poland + malaysia + sweden + sa + nz__ren__) / 1000000000000
    sma_input = 1 if sma_input_raw == 0 else sma_input_raw
    def ma(source, length):
        return ta.sma(source, length) if strategy_type == 'SMA' else ta.wma(source, length) if strategy_type == 'WMA' else ta.rma(source, length) if strategy_type == 'RMA' else ta.ema(source, length)

    total_sma = ta.sma(total, sma_input)
    roc_sma: Series = total_sma if roc_input == 0 else ta.sma(ta.roc(total, roc_input), sma_input)
    plot(roc_sma, title='GLI Line', color=color.yellow, linewidth=2, offset=offset_input)
    fast = ma(total, fast_length)
    slow = ma(total, slow_length)
    bull: Series = fast >= slow
    bear: Series = fast < slow
    price_sma = ta.sma(close, sma_input)
    roc_price_sma: Series = price_sma if roc_input == 0 else ta.sma(ta.roc(close, roc_input), sma_input)
    gli_table = roc_sma[math.abs(offset_input)] if offset_input > 0 else roc_sma
    price_table = roc_price_sma[math.abs(offset_input)] if offset_input < 0 else roc_price_sma
    is_crypto = syminfo.type == 'crypto'
    trading_days = 30 if is_crypto else 21
    gli_diff = total - total[change_length]
    asset_diff = close - close[change_length]
    gli_change_smooth = ta.sma(gli_diff, change_sma)
    asset_change_smooth = ta.sma(asset_diff, change_sma)
    gli_change: Series = gli_change_smooth / ta.stdev(gli_diff, change_length)
    asset_change: Series = asset_change_smooth / ta.stdev(asset_diff, change_length)
    gli_track = gli_change[math.abs(offset_input)] if offset_input > 0 else gli_change
    asset_track = asset_change[math.abs(offset_input)] if offset_input < 0 else asset_change
    gli_base_smooth = ta.sma(total[change_length], change_sma)
    change_pct = gli_change_smooth / gli_base_smooth
    tracking = asset_track - gli_track
    ahead: Series = tracking >= 0
    behind: Series = tracking < 0
    corr_1m = ta.correlation(price_table, gli_table, trading_days * 1)
    corr_3m = ta.correlation(price_table, gli_table, trading_days * 3)
    corr_6m = ta.correlation(price_table, gli_table, trading_days * 6)
    corr_12m = ta.correlation(price_table, gli_table, trading_days * 12)
    corr_3y = ta.correlation(price_table, gli_table, trading_days * 36)
    beta_length = trading_days * 6 if beta_input == '6M' else trading_days * 9 if beta_input == '9M' else trading_days * 12 if beta_input == '1Y' else trading_days * 36 if beta_input == '3Y' else trading_days * 60 if beta_input == '5Y' else trading_days * 3
    corr_beta = ta.correlation(price_table, gli_table, beta_length)
    std_asset_beta = ta.stdev(math.log(close / close[1]), beta_length)
    std_gli_beta = ta.stdev(math.log(total / total[1]), beta_length)
    beta = corr_beta * std_asset_beta / std_gli_beta
    corr_length = trading_days * 3 if corr_input == '3M' else trading_days * 6 if corr_input == '6M' else trading_days * 9 if corr_input == '9M' else trading_days * 12 if corr_input == '1Y' else trading_days * 24 if corr_input == '2Y' else trading_days * 36 if corr_input == '3Y' else trading_days * 60 if corr_input == '5Y' else trading_days * 1
    def manual_corr(gli_src: Series, price_src: Series, offset_value, length_value):
        abs_offset = math.abs(offset_value)
        sum_x: float = 0.0
        sum_y: float = 0.0
        sum_x2: float = 0.0
        sum_y2: float = 0.0
        sum_xy: float = 0.0
        count: int = 0
        for j in pine_range(0, length_value - 1):
            x = gli_src[j + abs_offset] if offset_value > 0 else gli_src[j]
            y = price_src[j + abs_offset] if offset_value < 0 else price_src[j]
            if not na(x) and (not na(y)):
                sum_x += x
                sum_y += y
                sum_x2 += x * x
                sum_y2 += y * y
                sum_xy += x * y
                count += 1
        numerator = count * sum_xy - sum_x * sum_y
        denominator = math.sqrt((count * sum_x2 - sum_x * sum_x) * (count * sum_y2 - sum_y * sum_y))
        return numerator / denominator if count > 1 and denominator != 0 else na

    best_corr: Persistent[float] = na(float)
    best_offset: Persistent[int] = na(int)
    best_corr = -1.0
    best_offset = 0
    for offset_i in pine_range(min_offset, max_offset, 10):
        offset_corr = manual_corr(total_sma, price_sma, offset_i, corr_length)
        if not na(offset_corr) and offset_corr > best_corr:
            best_corr = offset_corr
            best_offset = offset_i
    change_final = string.tostring(change_pct, '#.#%')
    corr_1m_final = string.tostring(corr_1m, '#.#')
    corr_3m_final = string.tostring(corr_3m, '#.#')
    corr_6m_final = string.tostring(corr_6m, '#.#')
    corr_12m_final = string.tostring(corr_12m, '#.#')
    corr_3y_final = string.tostring(corr_3y, '#.#')
    beta_final = string.tostring(beta, '#.#')
    offset_final = '+' + string.tostring(best_offset) if best_offset > 0 else string.tostring(best_offset)
    offset_corr_final = string.tostring(best_corr, '#.#')
    r2_threshold = r2_threshold_input if r2_threshold_input < 1 else r2_threshold_input / 100.0
    corr_threshold = math.sqrt(r2_threshold)
    t: Persistent[Table] = table.new(table_position, 2, 11, frame_color=color.white, frame_width=1, border_color=color.white, border_width=1)
    table.cell(t, 0, 0, text='Trend', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 1, text='Change', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 2, text='Tracking', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 3, text='1M Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 4, text='3M Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 5, text='6M Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 6, text='1Y Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 7, text='3Y Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 8, text='Beta (β)', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 9, text='Best Offset', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 0, 10, text='Offset Corr', width=width_input, text_color=color.white, bgcolor=color.rgb(0, 0, 0))
    table.cell(t, 1, 0, text='Bullish' if bull else 'Bearish', width=width_input, text_color=color.white, bgcolor=color.green if bull else color.red if bear else color.gray)
    table.cell(t, 1, 1, text=change_final, width=width_input, text_color=color.white, bgcolor=color.green if change_pct > 0 else color.red if change_pct < 0 else color.gray)
    table.cell(t, 1, 2, text='Ahead' if ahead else 'Behind', width=width_input, text_color=color.white, bgcolor=color.green if behind else color.red if ahead else color.gray)
    table.cell(t, 1, 3, text=corr_1m_final, width=width_input, text_color=color.white, bgcolor=color.green if corr_1m > corr_threshold else color.red if corr_1m < -corr_threshold else color.gray)
    table.cell(t, 1, 4, text=corr_3m_final, width=width_input, text_color=color.white, bgcolor=color.green if corr_3m > corr_threshold else color.red if corr_3m < -corr_threshold else color.gray)
    table.cell(t, 1, 5, text=corr_6m_final, width=width_input, text_color=color.white, bgcolor=color.green if corr_6m > corr_threshold else color.red if corr_6m < -corr_threshold else color.gray)
    table.cell(t, 1, 6, text=corr_12m_final, width=width_input, text_color=color.white, bgcolor=color.green if corr_12m > corr_threshold else color.red if corr_12m < -corr_threshold else color.gray)
    table.cell(t, 1, 7, text=corr_3y_final, width=width_input, text_color=color.white, bgcolor=color.green if corr_3y > corr_threshold else color.red if corr_3y < -corr_threshold else color.gray)
    table.cell(t, 1, 8, text=beta_final, width=width_input, text_color=color.white, bgcolor=color.green if beta > 1 else color.red if beta < 0 else color.gray)
    table.cell(t, 1, 9, text=offset_final, width=width_input, text_color=color.white, bgcolor=color.gray)
    table.cell(t, 1, 10, text=offset_corr_final, width=width_input, text_color=color.white, bgcolor=color.green if best_corr > corr_threshold else color.red if best_corr < -corr_threshold else color.gray)
    is_bull = bull and (not bull[1])
    is_bear = bear and (not bear[1])
    is_ahead = ahead and (not ahead[1])
    is_behind = behind and (not behind[1])
    alertcondition(is_bull, title='Trend Bullish', message='Global Liquidity Bullish!')
    alertcondition(is_bear, title='Trend Bearish', message='Global Liquidity Bearish!')
    alertcondition(is_ahead, title='Tracking Ahead', message='{{ticker}}' + ' Leading Global Liquidity!')
    alertcondition(is_behind, title='Tracking Behind', message='{{ticker}}' + ' Lagging Global Liquidity!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
