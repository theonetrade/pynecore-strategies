"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy('RSI Trend Crypto', overlay=False, pyramiding=1, commission_value=0.2, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    UseEmergency=input(False, 'Use Emergency Exit?'),
    RSIlong=input(35, 'RSI Long Cross'),
    RSIclose=input(75, 'RSI Close Position'),
    Emergencyclose=input(10, 'RSI Emergency Close Position')
):
    rsi = ta.rsi(close, 14)
    long = ta.crossover(rsi, RSIlong)
    longclose = ta.crossunder(rsi, RSIclose)
    emergency = ta.crossunder(rsi, Emergencyclose)
    plot(rsi, color=color.new(color.white, 0), linewidth=2)
    plot(RSIlong, color=color.new(color.green, 0))
    plot(RSIclose, color=color.new(color.red, 0))
    LongAlert: str = 'RSI Long Cross: LONG'
    CloseAlert: str = 'RSI Close Position'
    EmergencyAlert: str = 'RSI Emergency Close'
    if long:
        strategy.entry('Long', strategy.long, alert_message=LongAlert)
    if longclose:
        strategy.close('Long', alert_message=CloseAlert)
    if emergency and UseEmergency == True:
        strategy.close('Long', alert_message=EmergencyAlert)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
