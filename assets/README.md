# assets/ — original Pine sources from the "Pyne in the Wild" corpus

[wild.pynesys.io](https://wild.pynesys.io/#scripts) is PyneSys' verification report: the 1,000
most-liked open-source Pine scripts on TradingView, converted to Python by PyneComp, run by
PyneCore and compared against TradingView's own output. Every row links to the original
publication on TradingView.

This folder keeps the **original Pine Script source** of those scripts. Files are
byte-identical to what TradingView's *Source code* tab shows, except that line endings are
normalized to LF.

> **Scope: two types, two categories.** Strategies and indicators are kept in separate trees,
> `strategy/` and `indicator/`, and only the corpus categories **Bit-exact** and **Verified**
> are collected: the scripts whose PyneCore output provably matches TradingView. Lookahead,
> Data-limited, Runs, Divergent and Failed are out of scope.
>
> The corpus table mixes both types (`STR` / `IND` in the Type column) and the page opens on
> **All**. Before collecting links, select the tab that matches the target tree, **Strategies**
> for `strategy/` and **Indicators** for `indicator/`, and confirm it is the active one. A wrong
> tab silently produces a wrong link list, and nothing later in the pipeline will notice.

## Layout

```
assets/
  README.md
  strategy/                   scripts with Type STR (place orders, verified trade by trade)
    bit-exact/
    verified/
  indicator/                  scripts with Type IND (plots only, verified bar by bar)
    bit-exact/
    verified/

each <type>/<category>/ holds:
  links.txt                   TradingView URLs, one per line, in corpus order (most liked first)
  unavailable.txt             URLs from links.txt that could not be downloaded (removed from
                              TradingView, closed source), tab-separated: url, reason, date checked,
                              title and author; absent when every script was downloaded
  <slug>_<id>.pine            one file per script
```

`links.txt` is what the corpus lists; `.pine` files plus `unavailable.txt` lines account for every
one of its entries. The corpus was built from a snapshot of TradingView, and authors delete
publications afterwards, so a category is complete when `files + unavailable == links`, not
when `files == links`.

## Categories

A category is a status chip of the corpus table, lower-cased. With a single chip active the
table shows the scripts whose primary status is that chip; the single-chip counts are disjoint
and add up to 1,000. The status column may add a tier label next to the status (`bit-exact`,
`libm`): the **Bit-exact** chip selects the verified scripts of the bit-exact tier, and the
**Verified** chip selects the remaining verified scripts (within the tolerance band, including
the `libm` tier).

| Folder | Corpus chip | Meaning (from the site's tooltips) |
|---|---|---|
| `bit-exact/` | Bit-exact | On every compared bar PyneCore produced the same IEEE-754 double as TradingView, all 64 bits of it. |
| `verified/` | Verified | Output matched TradingView bar by bar and trade by trade within the published tolerance band, but not bit-exact. |

### Status

| Folder | On the site | Downloaded | Unavailable | Date |
|---|---|---|---|---|
| `strategy/bit-exact/` | 406 | 384 | 22 removed | 2026-11-06 |
| `strategy/verified/` | 65 | 65 | 0 | 2026-11-05 |
| `indicator/bit-exact/` | 461 | 458 | 3 removed | 2026-11-07 |
| `indicator/verified/` | 13 | 13 | 0 | 2026-11-07 |
| **Total** | 945 | **920** | 25 | |

"On the site" is the counter line with the matching type tab active and exactly one chip on
(corpus run of 2026-10-24). With **All** active the same chips count both types (Bit-exact 867,
Verified 78), which is how a wrong tab shows up in the numbers. Recheck before downloading: the
corpus is re-run periodically. After clicking a tab or a chip wait about a second before
reading the counter; the table re-renders with a delay and a too-early read returns stale text.

## File naming

`<slug>_<id>.pine`

- `id` is the 8-character TradingView script id from the URL
  (`https://www.tradingview.com/script/<id>/`). It makes names unique and lets you find the
  publication again: titles on TradingView are not unique ("TSI CCI Hull" vs "TSI CCI Hull with
  profit$$$", a dozen "Combo Backtest 123 Reversal …").
- `slug` is the TradingView page title without the trailing ` by <author>`,
  ` — Strategy by <author>` or ` — Indicator by <author>`, lower-cased, Cyrillic transliterated,
  every run of non-alphanumerics replaced by `_`, trimmed. Example:
  `MACD ReLoaded STRATEGY by KivancOzbilgic` → `macd_reloaded_strategy_VO6DY8s1.pine`.
- Only the last ` by <author>` is the page's byline. Some authors put "by …" into the script name
  itself ("Day Trading Booster by DGT — Indicator by dgtrd"), and that part stays in the slug:
  `day_trading_booster_by_dgt_bmkCcCIL.pine`.
- Do not derive the slug from the redirected TradingView URL: when pages are loaded in parallel
  the client-side redirect that adds the title to the URL sometimes has not happened yet.
- One known homoglyph: a title that starts with a Cyrillic «С» ("Сalculation a position size…")
  is named with the Latin letter, `calculation_a_position_size_based_on_risk_hoCPm5UY.pine`.

## Procedure

Everything runs through a Playwright-driven browser (the Playwright MCP server configured in
`.mcp.servers.json` at the repository root, or a Node Playwright script). No TradingView login
is needed; open-source scripts expose their source to anonymous visitors.

### 1. Collect the links for a category

1. Open `https://wild.pynesys.io/#scripts`.
2. In "The Corpus" section press the type tab: **Strategies** for `strategy/`, **Indicators**
   for `indicator/`. The page opens on **All**, and the site remembers the last tab and chips in
   the browser, so never assume the state: confirm that the right button is the highlighted one
   (`button.filter-btn.active`) and that every visible row shows the matching Type, `STR` or
   `IND`. Do not continue until both hold.
3. All status chips are active by default. Click every chip except the one you want so that only
   it stays active. Read the counter line (`65 of 1000 scripts, showing 1 to 25`) and note the
   total. It must match the "On the site" number above for that folder (or the site's current
   number with the same tab), not the larger All number.
4. The corpus table is `table#script-table`. It is **not** the first `<table>` on the page: the
   methodology section above it has its own small table.
5. Each script is a `tr.script-row` followed by a hidden `tr.detail-row`. Clicking the script row
   toggles `.open` on both and reveals the details, where
   `a.detail-link[href*="tradingview.com"]` is the "View on TradingView" link.
6. Walk the pages with the **Next page** button until it is disabled (25 rows per page). A
   category with 25 or fewer scripts has no pager at all.
7. Write the links to `assets/<type>/<category>/links.txt`, one per line, in table order. Check
   that the line count equals the counter total and that the lines are unique.

The loop, as run against the Playwright `page` object:

```js
const EXPECTED_TAB = 'Indicators';                       // or 'Strategies'
const tab = (await page.locator('button.filter-btn.active').textContent()).trim();
if (tab !== EXPECTED_TAB) throw new Error(`wrong tab: ${tab}`);

const results = [];
for (;;) {
  const rows = page.locator('#script-table tbody tr.script-row');
  const n = await rows.count();
  for (let i = 0; i < n; i++) {
    const row = rows.nth(i);
    await row.scrollIntoViewIfNeeded();
    if (!(await row.evaluate(tr => tr.classList.contains('open')))) { await row.click(); await page.waitForTimeout(60); }
    results.push(await row.evaluate(tr => ({
      title: tr.querySelector('.row-title')?.textContent.trim(),
      author: tr.querySelector('.row-author')?.textContent.trim(),
      status: tr.children[2].innerText.replace(/\s+/g, ' ').trim(), // "Verified bit-exact", "Verified libm", ...
      kind: tr.querySelector('.kind-chip')?.textContent.trim(),     // STR | IND
      tv: tr.nextElementSibling?.querySelector('a.detail-link[href*="tradingview.com"]')?.href,
    })));
  }
  const next = page.getByRole('button', { name: 'Next page' }).first();
  if (!(await next.count()) || await next.isDisabled()) break;
  await next.click(); await page.waitForTimeout(500);
}
```

Sanity-check every record before saving the links: `kind` must be the same on all of them,
`STR` for `strategy/` and `IND` for `indicator/` (anything else means the tab was wrong, start
over), and `status` must belong to the chip you selected (`Verified bit-exact` for Bit-exact;
`Verified` or `Verified libm` for Verified).

### 2. Download each script's source

For every URL in `links.txt`:

1. `page.goto(url)`; TradingView redirects to `/script/<id>-<Title-Slug>/`.
2. Wait for the round tab button whose text is exactly **Source code** and click it. Use a
   structural selector, the class hashes change with every TradingView build:
   `page.locator('button[class*="roundTabButton"]', { hasText: /^Source code$/ }).locator('visible=true').first()`.
   A plain `getByRole('button', { name: 'Source code' })` can pick a hidden duplicate and time out.
3. Opening the tab makes the page request
   `https://pine-facade.tradingview.com/pine-facade/get/<PUB;…>/<version>?no_4xx=true`, a JSON
   document whose `source` field is the exact script text (CRLF line endings, tabs preserved).
   Register `page.waitForResponse(r => r.url().includes('pine-facade/get/'))` **before**
   `goto`, in case the tab is restored from a previous visit and the request fires on load.
4. Also read the rendered viewer, `[class*="codeContainer"] [class*="code-"]` (`innerText`), and
   keep it for the cross-check. The viewer is a static Monaco render: it expands tabs to four
   spaces and uses non-breaking spaces, so it is not suitable as the saved copy.
5. Record `title` (`document.title` minus ` — TradingView`), the API source and the DOM text.

Pace: four tabs in parallel, 400 ms pause between pages, batches of about 125 URLs per call.
That is about 100 s per batch: 406 strategies took about ten minutes and 474 indicators about
six. No rate limiting was seen; do not go much faster.

#### Scripts that are gone or closed

Authors delete publications after the corpus run: 22 of 406 bit-exact strategies and 3 of 461
bit-exact indicators were gone. Classify every failure instead of retrying blindly:

| Observation | Meaning | Action |
|---|---|---|
| `goto` response status **404**, page title `Publication not found — TradingView`, body says "Publication has ghosted" | The author removed the publication. | Record in `unavailable.txt` with reason `removed`. Do not retry. |
| Status 200, badge reads `PROTECTED SCRIPT` or `INVITE-ONLY SCRIPT`, no *Source code* tab | The author closed the source after the corpus run. | Record with reason `closed_source`. Do not retry. |
| Status 200, badge `OPEN-SOURCE SCRIPT`, tabs include *Source code* but it took longer than the 30 s wait | Slow page load. | Retry once with a 45 s wait; two of 880 needed this. |

Check `resp.status()` of the `goto` call first: a 404 answers immediately, while waiting for the
tab wastes the full timeout. In code:

```js
const resp = await p.goto(url, { waitUntil: 'domcontentloaded' });
if (resp.status() >= 400) return { url, ok: false, reason: 'removed', err: `HTTP ${resp.status()}` };
try { await tab.waitFor({ state: 'visible', timeout: 30000 }); }
catch { /* read the badge text: PROTECTED / INVITE-ONLY -> closed_source, else -> retry later */ }
```

#### Running it through the Playwright MCP tools

- The browser sandbox has no file access. Keep the job list and each finished batch on the
  wild.pynesys.io page, which is never navigated during the download
  (`window.__jobs`, `window.__range = [start, end]`, `window.__batch`), and open TradingView in
  separate tabs from `page.context().newPage()`.
- Put the download function into a file under `.playwright-mcp/` and run it with
  `browser_run_code_unsafe` and its `filename` option; between batches only `window.__range`
  changes, so the code is not resent every time.
- Dump a finished batch with `browser_evaluate` and its `filename` option
  (`() => JSON.stringify(window.__batch)` → `.playwright-mcp/<type>_batch_<start>.json`).
  `.playwright-mcp/` is git-ignored; delete the batch files once the sources are written.
- A cancelled or rejected `browser_run_code_unsafe` call can still be running in the browser and
  will overwrite `window.__batch` when it finishes. Before starting the next batch, check
  `page.context().pages()`: extra TradingView tabs mean a run is still in progress. Wait until
  only the corpus page is left and read the result before reusing `window.__batch`.

### 3. Write the files

For each record, in Python:

- content = `source` with `\r\n` → `\n`, trailing newlines collapsed to exactly one. Leading
  blank lines stay: a few authors start the file with an empty line and the API keeps it;
- fall back to the DOM text only if the API response was missed;
- compare `norm(api) == norm(dom)` where `norm` replaces `\r\n`→`\n`, NBSP→space, tab→4 spaces,
  strips trailing whitespace per line and drops leading and trailing blank lines (the viewer
  trims those). Every record must match; investigate any that do not;
- write `unavailable.txt` from the failures classified `removed` or `closed_source`; anything
  else is a retry, not a result;
- file name per the rule above; assert there are no collisions;
- write with UTF-8, no BOM, no header comment: the file is the author's source and nothing else.

Keep the author's whitespace. Alignment runs, trailing spaces and NBSPs inside string literals
are part of the original and are what TradingView serves.

### 4. Verify before reporting

- number of `.pine` files + number of lines in `unavailable.txt` == number of lines in
  `links.txt` == counter total on the site;
- every line of `unavailable.txt` has a reason of `removed` or `closed_source`; a timeout is not
  a reason;
- every file contains a `//@version=` line;
- `grep -l $'\r'` finds nothing;
- spot check: SHA-256 of a local file equals SHA-256 of the current API `source` for that
  script after the same LF normalization (done for `btc_bot_DPBeZbMP.pine` on 2026-11-05).

## Refreshing a category

The corpus is re-run periodically, so a category can gain or lose scripts. To bring a folder up
to date:

1. Select the type tab that matches the folder and verify it is active (step 1.2). This is the
   step that is easiest to skip and most expensive to get wrong.
2. Leave only the target chip on and compare the counter with the Status table.
3. Run step 1 and overwrite `links.txt`; all records must have the folder's Type.
4. Run steps 2 and 3; batch the download, keep batches in `.playwright-mcp/`. Classify every
   failure (removed / closed source / slow) and retry only the slow ones.
5. Remove `.pine` files whose URL is no longer in `links.txt`.
6. Run the checks in step 4, then update the folder's row in the Status table with the counts
   and the date.

## Licensing

Each script carries its own license in its header, typically MPL-2.0 or a Creative Commons
license, chosen by the author on TradingView. These copies are kept for conversion and
verification work with PyneCore; respect the header when redistributing or modifying a script.
