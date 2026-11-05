# assets/ — original Pine sources from the "Pyne in the Wild" corpus

[wild.pynesys.io](https://wild.pynesys.io/#scripts) is PyneSys' verification report: the 1,000
most-liked open-source Pine scripts on TradingView, converted to Python by PyneComp, run by
PyneCore and compared against TradingView's own output. Every row links to the original
publication on TradingView.

This folder keeps the **original Pine Script source** of those scripts, grouped by the corpus
category they were taken from. Files are byte-identical to what TradingView's *Source code* tab
shows, except that line endings are normalized to LF.

## Layout

```
assets/
  README.md
  <category>/                 one folder per corpus filter chip (strategies)
    links.txt                 TradingView URLs, one per line, in corpus order (most liked first)
    <slug>_<id>.pine          one file per script
  indicators/<category>/      same layout for indicators (reserved, not populated yet)
```

A `<category>` is a status chip of the corpus table, lower-cased. With a single chip active the
table shows the scripts whose primary status is that chip; the seven single-chip counts are
disjoint and add up to 1,000. The status column may add a tier label next to the status
(`bit-exact`, `libm`): the **Bit-exact** chip selects the verified scripts of the bit-exact tier,
and the **Verified** chip selects the remaining verified scripts (within the tolerance band,
including the `libm` tier).

| Folder | Corpus chip | Meaning (from the site's tooltips) | Strategies | Indicators |
|---|---|---|---|---|
| `bit-exact/` | Bit-exact | On every compared bar PyneCore produced the same IEEE-754 double as TradingView. | 406 | 461 |
| `verified/` | Verified | Output matched TradingView bar by bar and trade by trade within the published tolerance band, but not bit-exact. | **65, downloaded 2026-11-05** | 13 |
| `divergent/` | Divergent | Output differs from TradingView beyond the band. Empty on the site as of 2026-11-05. | 0 | 0 |
| `lookahead/` | Lookahead | The script's output depends on data its bars could not have had, so its TradingView reference is a lookahead result too. Kept out of the accuracy score. | 25 | 1 |
| `data-limited/` | Data-limited | Needs a feed the comparison lacks (`request.footprint`); runs with it as `na`. Excluded from the accuracy score. | 1 | 0 |
| `runs/` | Runs | Compiled and ran on real data without errors, but there was no comparable TradingView reference. | 1 | 27 |
| `failed/` | Failed | Did not compile or run. Empty on the site as of 2026-11-05. | 0 | 0 |

Counts are what the counter line showed on 2026-11-05 with exactly one chip active (corpus run
of 2026-10-24). Recheck them before downloading: the corpus is re-run periodically. After
clicking chips wait about a second before reading the counter; the table re-renders with a
delay and a too-early read returns stale text.

## File naming

`<slug>_<id>.pine`

- `id` is the 8-character TradingView script id from the URL
  (`https://www.tradingview.com/script/<id>/`). It makes names unique and lets you find the
  publication again: titles on TradingView are not unique ("TSI CCI Hull" vs "TSI CCI Hull with
  profit$$$", a dozen "Combo Backtest 123 Reversal …").
- `slug` is the TradingView page title without the trailing ` by <author>` /
  ` — Strategy by <author>`, lower-cased, Cyrillic transliterated, every run of non-alphanumerics
  replaced by `_`, trimmed. Example: `MACD ReLoaded STRATEGY by KivancOzbilgic` →
  `macd_reloaded_strategy_VO6DY8s1.pine`.
- Do not derive the slug from the redirected TradingView URL: when pages are loaded in parallel
  the client-side redirect that adds the title to the URL sometimes has not happened yet.
- One known homoglyph: a title that starts with a Cyrillic «С» ("Сalculation a position size…")
  is named with the Latin letter, `calculation_a_position_size_based_on_risk_hoCPm5UY.pine`.

## Procedure

Everything runs through a Playwright-driven browser (the Claude Code Playwright MCP tools, or a
Node Playwright script). No TradingView login is needed; open-source scripts expose their source
to anonymous visitors.

### 1. Collect the links for a category

1. Open `https://wild.pynesys.io/#scripts`.
2. In "The Corpus" section press **Strategies** (or **Indicators**).
3. All status chips are active by default. Click every chip except the one you want so that only
   it stays active. Read the counter line (`65 of 1000 scripts, showing 1 to 25`) and note the
   total.
4. The corpus table is `table#script-table`. It is **not** the first `<table>` on the page: the
   methodology section above it has its own small table.
5. Each script is a `tr.script-row` followed by a hidden `tr.detail-row`. Clicking the script row
   toggles `.open` on both and reveals the details, where
   `a.detail-link[href*="tradingview.com"]` is the "View on TradingView" link.
6. Walk the pages with the **Next page** button until it is disabled (25 rows per page).
7. Write the links to `assets/<category>/links.txt`, one per line, in table order. Check that the
   line count equals the counter total and that the lines are unique.

The loop, as run against the Playwright `page` object:

```js
const results = [];
for (;;) {
  const rows = page.locator('#script-table tbody tr.script-row');
  const n = await rows.count();
  for (let i = 0; i < n; i++) {
    const row = rows.nth(i);
    await row.scrollIntoViewIfNeeded();
    if (!(await row.evaluate(tr => tr.classList.contains('open')))) { await row.click(); await page.waitForTimeout(120); }
    results.push(await row.evaluate(tr => ({
      title: tr.querySelector('.row-title')?.textContent.trim(),
      author: tr.querySelector('.row-author')?.textContent.trim(),
      status: tr.querySelector('.status-badge')?.textContent.trim(),
      kind: tr.querySelector('.kind-chip')?.textContent.trim(),          // STR | IND
      tv: tr.nextElementSibling?.querySelector('a.detail-link[href*="tradingview.com"]')?.href,
    })));
  }
  const next = page.getByRole('button', { name: 'Next page' }).first();
  if (await next.isDisabled()) break;
  await next.click(); await page.waitForTimeout(500);
}
```

Sanity-check `status` and `kind` on every record before saving the links: they must all be the
category and type you filtered for.

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
4. Also read the rendered viewer, `.codeContainer-* .code-*` (`innerText`), and keep it for the
   cross-check. The viewer is a static Monaco render: it expands tabs to four spaces and uses
   non-breaking spaces, so it is not suitable as the saved copy.
5. Record `title` (`document.title` minus ` — TradingView`), the final URL, the API source and
   the DOM text.

Three tabs in parallel with a 400 ms pause between pages were enough for 65 scripts in about
three minutes without any rate limiting; do not go much faster.

In the Claude Code setup the browser sandbox has no file access, so a batch is stashed on a page
(`page.evaluate(b => { window.__batchN = b }, batch)` on a page that is not navigated again)
and dumped with `browser_evaluate` using its `filename` option
(`() => JSON.stringify(window.__batchN)` → `.playwright-mcp/batch_N.json`). `.playwright-mcp/`
is git-ignored; delete the batch files once the sources are written.

### 3. Write the files

For each record, in Python:

- content = `source` with `\r\n` → `\n`, trailing newlines collapsed to exactly one;
- fall back to the DOM text only if the API response was missed;
- compare `norm(api) == norm(dom)` where `norm` replaces `\r\n`→`\n`, NBSP→space, tab→4 spaces
  and strips trailing whitespace per line. Every record must match; investigate any that do not;
- file name per the rule above; assert there are no collisions;
- write with UTF-8, no BOM, no header comment: the file is the author's source and nothing else.

Keep the author's whitespace. Alignment runs, trailing spaces and NBSPs inside string literals
are part of the original and are what TradingView serves.

### 4. Verify before reporting

- number of `.pine` files == number of lines in `links.txt` == counter total on the site;
- every file contains a `//@version=` line;
- `grep -l $'\r'` finds nothing;
- spot check: SHA-256 of a local file equals SHA-256 of the current API `source` for that
  script after the same LF normalization (done for `btc_bot_DPBeZbMP.pine` on 2026-11-05).

## Adding a new category

1. Check the counter on the site for the chip and type you want.
2. `mkdir -p assets/<category>` (or `assets/indicators/<category>`).
3. Run step 1 and save `links.txt`.
4. Run steps 2 and 3; batch the download, keep batches in `.playwright-mcp/`.
5. Run the checks in step 4, add the category's row or count to the table above with the date.

`bit-exact/` for strategies (406 scripts) is the obvious next one; expect roughly 20 minutes of
browser time at the pace above.

## Licensing

Each script carries its own license in its header, typically MPL-2.0 or a Creative Commons
license, chosen by the author on TradingView. These copies are kept for conversion and
verification work with PyneCore; respect the header when redistributing or modifying a script.
