"""Compile the Pine sources in assets/ to Pyne scripts in scripts/ through the PyneSys API.

    .venv/bin/python tools/compile_assets.py --status     # progress and quota, uses no quota
    .venv/bin/python tools/compile_assets.py              # compile until done or until the quota runs out
    .venv/bin/python tools/compile_assets.py --limit 50   # compile at most 50 files this run
    .venv/bin/python tools/compile_assets.py --retry-failed

Sources : assets/<kind>/<category>/<name>.pine   kind = strategy | indicator, category = verified | bit-exact
          assets/lib/<Publisher>/<Name>/v<N>.pine   Pine libraries imported as <Publisher>/<Name>/<N>
Targets : scripts/<kind>_<name>.py
          scripts/lib/<Publisher>/<Name>/v<N>.py    where the compiled `import lib.<Publisher>.<Name>.v<N>`
                                                    looks for it; "-" in a publisher becomes "_"
Order   : strategies, then libraries, then indicators
Key     : config/api.toml ([api] api_key), as for `pyne compile`
State   : assets/compile_state.json, tracked in git

Stopping and resuming
    The run can stop at any moment and be started again later with the same command; it picks
    up where it stopped.
    * Quota used up (hourly or daily): the run saves its state and exits with code 3, printing
      the time the quota resets. Run it again after that time.
    * API key rejected or expired: exit code 2. Put a valid key into config/api.toml and run again.
    * Killed (Ctrl+C, closed terminal, session ended): a file is written to scripts/ only after it
      compiled and passed a Python syntax check, via an atomic rename, so no half-written script
      is ever left behind. Ctrl+C finishes the current file first.
    A file counts as done when the state has it as "ok", the script exists, and the SHA-256 of
    the source is the one that was compiled. Editing a .pine file therefore recompiles it; file
    modification times play no role, so a fresh clone does not recompile anything.
    A source that failed with a compilation error is skipped on later runs unless --retry-failed
    is given, so deterministic failures do not use quota twice.

Exit codes: 0 everything compiled or failed for good, 3 quota exhausted, 2 authentication error,
1 other error, 130 interrupted.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import signal
import sys
import tomllib
from pathlib import Path

from pynecore.pynesys.api import APIError, AuthError, CompilationError, RateLimitError
from pynecore.pynesys.compiler import PyneComp

ROOT = Path(__file__).resolve().parent.parent
ORDER = [("strategy", "verified"), ("strategy", "bit-exact"), ("lib", ""), ("indicator", "verified"), ("indicator", "bit-exact")]
STATE = ROOT / "assets" / "compile_state.json"
TMP = ROOT / "cache" / "compile_tmp"
RESUME = ".venv/bin/python tools/compile_assets.py"

stop_requested = False


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def say(msg: str) -> None:
    print(f"{now():%H:%M:%S} {msg}", flush=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save_state(state: dict) -> None:
    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(dict(sorted(state.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, STATE)


def lib_target(src: Path) -> Path:
    """assets/lib/Trading-IQ/ICTlibrary/v1.pine -> scripts/lib/Trading_IQ/ICTlibrary/v1.py"""
    publisher, name = src.parent.parent.name, src.parent.name
    return ROOT / "scripts" / "lib" / publisher.replace("-", "_") / name / f"{src.stem}.py"


def jobs() -> list[tuple[Path, Path, str]]:
    out, seen = [], {}
    for kind, cat in ORDER:
        if kind == "lib":
            pairs = [(src, lib_target(src), "lib") for src in sorted((ROOT / "assets" / "lib").glob("*/*/v*.pine"))]
        else:
            pairs = [(src, ROOT / "scripts" / f"{kind}_{src.stem}.py", f"{kind}/{cat}")
                     for src in sorted((ROOT / "assets" / kind / cat).glob("*.pine"))]
        for src, dst, grp in pairs:
            assert dst not in seen, f"name collision: {src} and {seen[dst]}"
            seen[dst] = src
            out.append((src, dst, grp))
    return out


def classify(state: dict, src: Path, dst: Path) -> str:
    """done | failed | todo"""
    rec = state.get(str(src.relative_to(ROOT)))
    if not rec or rec.get("sha256") != sha256(src):
        return "todo"
    if rec["status"] == "ok":
        return "done" if dst.exists() else "todo"
    if rec["status"] == "compile_error":
        return "failed"
    return "todo"


def quota_line(u) -> str:
    return (f"hourly {u.hourly.remaining}/{u.hourly.limit} left (resets {u.hourly.reset_at:%Y-%m-%d %H:%M} UTC), "
            f"daily {u.daily.remaining}/{u.daily.limit} left (resets {u.daily.reset_at:%Y-%m-%d %H:%M} UTC)")


def quota_exhausted(u) -> dt.datetime | None:
    """Reset time of the exhausted period, or None while both periods have room."""
    empty = [p.reset_at for p in (u.hourly, u.daily) if p.remaining <= 0]
    return max(empty) if empty else None


def stop_for_quota(reset: dt.datetime | None, state: dict, done_now: int) -> int:
    save_state(state)
    when = f"{reset:%Y-%m-%d %H:%M} UTC" if reset else "the next quota reset"
    say(f"quota exhausted after {done_now} files this run; progress saved. Resume after {when}:  {RESUME}")
    return 3


def on_signal(signum, frame):
    global stop_requested
    if stop_requested:
        raise KeyboardInterrupt
    stop_requested = True
    say("stop requested; finishing the current file (press Ctrl+C again to abort it)")


def main(argv: list[str] | None = None, comp: PyneComp | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--status", action="store_true", help="print progress and quota, compile nothing")
    ap.add_argument("--limit", type=int, default=0, help="compile at most N files this run (0 = until done or out of quota)")
    ap.add_argument("--retry-failed", action="store_true", help="compile sources that failed before once more")
    args = ap.parse_args(argv)

    if comp is None:
        cfg = tomllib.loads((ROOT / "config" / "api.toml").read_text(encoding="utf-8"))["api"]
        comp = PyneComp(cfg["api_key"], timeout=int(cfg.get("timeout", 30)) * 3)

    state = load_state()
    all_jobs = jobs()
    kinds = {j: classify(state, j[0], j[1]) for j in all_jobs}

    if args.status:
        groups: dict[str, dict[str, int]] = {}
        for (src, dst, grp), k in kinds.items():
            groups.setdefault(grp, {"done": 0, "failed": 0, "todo": 0})[k] += 1
        print(f"{'group':20} {'done':>6} {'failed':>7} {'todo':>6}")
        for grp, c in groups.items():
            print(f"{grp:20} {c['done']:>6} {c['failed']:>7} {c['todo']:>6}")
        tot = {k: sum(c[k] for c in groups.values()) for k in ("done", "failed", "todo")}
        print(f"{'total':20} {tot['done']:>6} {tot['failed']:>7} {tot['todo']:>6}")
        try:
            print("quota:", quota_line(comp.get_usage()))
        except AuthError as e:
            print(f"quota: API key rejected ({e})")
        return 0

    todo = [j for j, k in kinds.items() if k == "todo" or (k == "failed" and args.retry_failed)]
    say(f"{len(all_jobs)} sources: {sum(k == 'done' for k in kinds.values())} done, "
        f"{sum(k == 'failed' for k in kinds.values())} failed before, {len(todo)} to compile")
    if not todo:
        return 0

    try:
        usage = comp.get_usage()
    except AuthError as e:
        say(f"API key rejected: {e}. Put a valid key into config/api.toml and run again.")
        return 2
    say("quota: " + quota_line(usage))
    reset = quota_exhausted(usage)
    if reset:
        return stop_for_quota(reset, state, 0)
    budget = min(usage.hourly.remaining, usage.daily.remaining)

    TMP.mkdir(parents=True, exist_ok=True)
    for leftover in TMP.glob("*.py"):
        leftover.unlink()
    global stop_requested
    stop_requested = False
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    stats = {"ok": 0, "compile_error": 0, "syntax_error": 0, "error": 0}
    calls = 0
    for n, (src, dst, grp) in enumerate(todo, 1):
        if stop_requested:
            save_state(state)
            say(f"stopped on request; progress saved. Resume with:  {RESUME}")
            return 130
        if args.limit and calls >= args.limit:
            say(f"--limit {args.limit} reached; progress saved. Continue with:  {RESUME}")
            break
        if calls >= budget:
            usage = comp.get_usage()
            reset = quota_exhausted(usage)
            if reset:
                return stop_for_quota(reset, state, stats["ok"])
            budget = calls + min(usage.hourly.remaining, usage.daily.remaining)

        rel, digest = str(src.relative_to(ROOT)), sha256(src)
        tmp = TMP / str(dst.relative_to(ROOT / "scripts")).replace(os.sep, "__")  # library files are all named v<N>.py
        tag = f"[{n}/{len(todo)}]"
        calls += 1
        try:
            comp.compile(src, tmp, force=True)
            compile(tmp.read_text(encoding="utf-8"), str(dst), "exec")  # Python syntax check, writes nothing
        except RateLimitError:
            usage = comp.get_usage()
            return stop_for_quota(quota_exhausted(usage), state, stats["ok"])
        except AuthError as e:
            save_state(state)
            say(f"API key rejected: {e}. Progress saved. Put a valid key into config/api.toml and run:  {RESUME}")
            return 2
        except CompilationError as e:
            stats["compile_error"] += 1
            state[rel] = {"dst": dst.name, "sha256": digest, "status": "compile_error",
                          "message": str(e)[:2000], "at": now().isoformat(timespec="seconds")}
            save_state(state)
            say(f"{tag} FAIL   {grp} {src.name}: {str(e)[:160]}")
            continue
        except (SyntaxError, ValueError) as e:
            stats["syntax_error"] += 1
            state[rel] = {"dst": dst.name, "sha256": digest, "status": "syntax_error",
                          "message": str(e)[:2000], "at": now().isoformat(timespec="seconds")}
            save_state(state)
            tmp.unlink(missing_ok=True)
            say(f"{tag} SYNTAX {grp} {dst.name}: {str(e)[:160]}")
            continue
        except APIError as e:  # network or server trouble: leave it for the next run
            stats["error"] += 1
            say(f"{tag} ERROR  {grp} {src.name}: {e} (will be retried on the next run)")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp, dst)
        state[rel] = {"dst": dst.name, "sha256": digest, "status": "ok", "at": now().isoformat(timespec="seconds")}
        save_state(state)
        stats["ok"] += 1
        say(f"{tag} ok     {grp} {dst.relative_to(ROOT / 'scripts')}")

    save_state(state)
    left = sum(classify(state, s, d) == "todo" for s, d, _ in all_jobs)
    say(f"run finished: {stats}; {left} sources still to compile" + (f". Continue with:  {RESUME}" if left else ""))
    return 0 if not left or args.limit else 1


if __name__ == "__main__":
    sys.exit(main())
