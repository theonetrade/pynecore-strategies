"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, box, close, color, high, input, label, low, math,
    na, nz, open, plot, position, script, size, strategy, string, table, time, timeframe
)
from pynecore.types import Box, Persistent, Series, Table


@script.strategy("EE Sweep Return — STRATEGY v1", "STRATEGY SCRIPT Sweep Return v1", overlay=True, process_orders_on_close=True, calc_on_every_tick=False, pyramiding=0, initial_capital=50000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=2.0, slippage=1, margin_long=0, margin_short=0, max_boxes_count=500, max_labels_count=500)
def main(
    tz=input.string("America/Chicago", "Timezone", group="Session"),
    orSess=input.session("0830-0930", "Opening range", group="Session"),
    winSess=input.session("0930-1500", "Signal window", group="Session"),
    sameBar=input.bool(True, "Allow same-bar break and return", group="Logic"),
    strictBox=input.bool(True, "Require close back INSIDE the box", group="Logic"),
    flatOnly=input.bool(True, "Only enter when flat", group="Logic"),
    entryMode=input.string("Signal bar close", "Enter at", options=("Signal bar close", "Next bar close"), group="Trade"),
    tpPts=input.float(50.0, "Target (points)", minval=0.25, step=0.25, group="Trade"),
    slPts=input.float(25.0, "Stop (points)", minval=0.25, step=0.25, group="Trade"),
    eodFlat=input.bool(True, "Flatten at end of signal window", group="Trade"),
    showBox=input.bool(True, "Show opening range box", group="Visuals"),
    showLbl=input.bool(True, "Show signal labels", group="Visuals"),
    diagOn=input.bool(True, "Show status panel", group="Visuals")
):
    orH: Persistent[float] = na(float)
    orL: Persistent[float] = na(float)
    orOK: Persistent[bool] = False
    armUp: Persistent[bool] = False
    armDn: Persistent[bool] = False
    lastBreak: Persistent[int] = 0
    pend: Persistent[int] = 0
    orBox: Persistent[Box] = na(Box)
    sigCount: Persistent[int] = 0

    inOR: Series = not na(time(timeframe.period, orSess, tz))
    inWin: Series = not na(time(timeframe.period, winSess, tz))

    orStart = inOR and (not inOR[1])
    orEnd = not inOR and inOR[1]
    winEnd = not inWin and inWin[1]

    if orStart:
        orH = na
        orL = na
        orOK = False
        armUp = False
        armDn = False
        lastBreak = 0
        pend = 0
        orBox = na

    if inOR:
        orH = high if na(orH) else math.max(orH, high)
        orL = low if na(orL) else math.min(orL, low)
        if showBox:
            if na(orBox):
                orBox = box.new(bar_index, orH, bar_index, orL, border_color=color.new(color.gray, 30), bgcolor=color.new(color.gray, 90))
            else:
                box.set_top(orBox, orH)
                box.set_bottom(orBox, orL)
                box.set_right(orBox, bar_index)

    if orEnd:
        orOK = True

    if orOK and inWin and showBox and (not na(orBox)):
        box.set_right(orBox, bar_index)

    active = orOK and inWin and (not na(orH)) and (not na(orL))
    orWidth = orH - orL if not na(orH) and (not na(orL)) else na

    armUpPrev = armUp
    armDnPrev = armDn
    lbPrev = lastBreak

    if active:
        brokeUp = high > orH
        brokeDn = low < orL
        if brokeUp:
            armUp = True
        if brokeDn:
            armDn = True
        if brokeUp and brokeDn:
            lastBreak = 1 if close >= open else -1
        elif brokeUp:
            lastBreak = 1
        elif brokeDn:
            lastBreak = -1

    canShort = armUp if sameBar else armUpPrev
    canLong = armDn if sameBar else armDnPrev
    lb = lastBreak if sameBar else lbPrev

    insideBox = active and close < orH and (close > orL)
    retShort = insideBox if strictBox else close < orH
    retLong = insideBox if strictBox else close > orL

    rawShort = active and canShort and retShort
    rawLong = active and canLong and retLong

    shortSig = rawShort and (not rawLong or lb == 1)
    longSig = rawLong and (not rawShort or lb == -1)

    if shortSig or longSig:
        armUp = False
        armDn = False
        lastBreak = 0
        sigCount += 1

    canTrade = strategy.position_size == 0 if flatOnly else True
    delayed = entryMode == 'Next bar close'
    tag = string.tostring(nz(orWidth), '#.##')

    def goLong():
        strategy.entry('SR Long', strategy.long, comment='L w' + tag)
        return strategy.exit('X L', from_entry='SR Long', limit=close + tpPts, stop=close - slPts)

    def goShort():
        strategy.entry('SR Short', strategy.short, comment='S w' + tag)
        return strategy.exit('X S', from_entry='SR Short', limit=close - tpPts, stop=close + slPts)

    if delayed and pend != 0:
        if canTrade:
            if pend == 1:
                goLong()
            else:
                goShort()
        pend = 0

    if shortSig:
        if delayed:
            pend = -1
        elif canTrade:
            goShort()

    if longSig:
        if delayed:
            pend = 1
        elif canTrade:
            goLong()

    if eodFlat and winEnd and (strategy.position_size != 0):
        strategy.close_all(comment='EOD flat')

    if showLbl and shortSig:
        label.new(bar_index, high, 'SHORT', style=label.style_label_down, color=color.new(color.red, 15), textcolor=color.white, size=size.small)

    if showLbl and longSig:
        label.new(bar_index, low, 'LONG', style=label.style_label_up, color=color.new(color.teal, 15), textcolor=color.white, size=size.small)

    plot(orH if orOK else na, 'OR high', color=color.new(color.gray, 20), style=plot.style_linebr, linewidth=1)
    plot(orL if orOK else na, 'OR low', color=color.new(color.gray, 20), style=plot.style_linebr, linewidth=1)

    diag: Persistent[Table] = na(Table)
    if diagOn and barstate.islast:
        if na(diag):
            diag = table.new(position.top_right, 2, 4, border_width=1)
        tot = strategy.closedtrades + strategy.opentrades
        table.cell(diag, 0, 0, 'SR STRAT v2', text_color=color.white, bgcolor=color.new(color.purple, 10), text_size=size.small)
        table.cell(diag, 1, 0, 'LIVE', text_color=color.white, bgcolor=color.new(color.purple, 10), text_size=size.small)
        table.cell(diag, 0, 1, 'Signals', text_color=color.white, bgcolor=color.new(color.black, 20), text_size=size.small)
        table.cell(diag, 1, 1, string.tostring(sigCount), text_color=color.white, bgcolor=color.new(color.black, 20), text_size=size.small)
        table.cell(diag, 0, 2, 'Trades', text_color=color.white, bgcolor=color.new(color.black, 20), text_size=size.small)
        table.cell(diag, 1, 2, string.tostring(tot), text_color=color.orange if tot == 0 and sigCount > 0 else color.white, bgcolor=color.new(color.black, 20), text_size=size.small)
        table.cell(diag, 0, 3, 'OR width', text_color=color.white, bgcolor=color.new(color.black, 20), text_size=size.small)
        table.cell(diag, 1, 3, string.tostring(nz(orWidth), '#.##'), text_color=color.white, bgcolor=color.new(color.black, 20), text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
