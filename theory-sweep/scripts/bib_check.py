#!/usr/bin/env python3
"""Check candidate citations with Crossref and OpenAlex.

Read the OpenAlex key from a file or OPENALEX_API_KEY; send it only in headers.
Network matches do not establish content accuracy or effectiveness.
"""
import argparse
import difflib
from email.utils import parsedate_to_datetime
import json
import math
import os
from pathlib import Path
import re
import runpy
import signal
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCORE = runpy.run_path(str(Path(__file__).with_name("score_format.py")))
score = SCORE["score"]
STRINGS = SCORE["STRINGS"]
STANDARD = re.compile(
    r"\b(?:ISA|ISO|IEC|ANSI|IEEE|ASTM|NIST)\s*[-/:]?\s*\d[\w./:–-]*"
    r"|\b(?:COSO|NASA|FDA)\b", re.I)
TITLE = re.compile(r'「([^」]{4,})」|["“]([^"”]{4,})["”]|『([^』]{4,})』|\*([^*]{4,})\*')
DAILY_CREDITS = 10000


class BudgetExceeded(Exception):
    pass


class RunState:
    """Share provider failures, credits, and the time budget across reports."""

    def __init__(self, max_wait=20, budget=300, providers=("crossref", "openalex"),
                 openalex_key=None):
        self.max_wait = max_wait
        self.deadline = time.monotonic() + budget
        self.blocked = set()
        self.providers = providers
        self.openalex_key = openalex_key
        self.credits_used = 0

    def redact(self, text):
        if self.openalex_key:
            for secret in (self.openalex_key,
                           urllib.parse.quote(self.openalex_key, safe=""),
                           urllib.parse.quote_plus(self.openalex_key)):
                text = text.replace(secret, "[REDACTED]")
        return text

    def redact_row(self, value):
        if isinstance(value, str):
            return self.redact(value)
        if isinstance(value, dict):
            return {self.redact(key): self.redact_row(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.redact_row(item) for item in value]
        return value

    def record_credits(self, headers):
        value = headers.get("x-ratelimit-credits-used") if headers else None
        try:
            credits = int(value)
        except (TypeError, ValueError):
            return
        if credits >= 0:
            self.credits_used += credits

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise BudgetExceeded
        return remaining

    def sleep(self, seconds):
        seconds = min(seconds, self.max_wait, self.remaining())
        if seconds > 0:
            time.sleep(seconds)
        self.remaining()

    @staticmethod
    def expire(signum, frame):
        raise BudgetExceeded

    def request(self, provider, query, user_agent, timeout):
        remaining = self.remaining()
        previous_handler = signal.getsignal(signal.SIGALRM)
        previous_timer = signal.getitimer(signal.ITIMER_REAL)
        started = time.monotonic()
        try:
            signal.signal(signal.SIGALRM, self.expire)
            signal.setitimer(signal.ITIMER_REAL, remaining)
            if provider is openalex:
                hits = provider(query, user_agent, min(timeout, remaining),
                                api_key=self.openalex_key, state=self)
            else:
                hits = provider(query, user_agent, min(timeout, remaining), state=self)
            self.remaining()
            return hits
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
            if previous_timer[0] > 0:
                signal.setitimer(signal.ITIMER_REAL,
                                 max(0.000001, previous_timer[0] - (time.monotonic() - started)),
                                 previous_timer[1])


def norm(value):
    return re.sub(r"[^\w]+", " ", value or "").lower().strip()


def parse_source(source):
    markers = [re.escape(marker) for strings in STRINGS.values()
               for marker in (strings["recheck_marker"].split("{", 1)[0],
                              strings["unverified_title_marker"], strings["unverified_item_prefix"])]
    clean = re.split("|".join(markers), source, maxsplit=1)[0].rstrip(" ·—")
    years = re.findall(r"\b(?:1[5-9]\d\d|20\d\d)\b", clean)
    match = TITLE.search(clean)
    title = next((s for s in match.groups() if s), None) if match else None
    author = re.split(r'[,(（「『*"“]', clean, maxsplit=1)[0].strip()
    author = re.split(r"[·&]|\band\b", author)[0].strip()
    return {"author": author, "years": years, "title": title}


def classification(source, parsed, standard_pattern=STANDARD):
    if standard_pattern.search(source):
        return "standard_doc"
    if not parsed["years"] and not parsed["title"]:
        return "not_a_citation"
    if not parsed["title"]:
        return "no_title"
    return None


def get(url, user_agent, timeout, *, api_key=None, state=None):
    headers = {"User-Agent": user_agent}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if state is not None:
            state.record_credits(exc.headers)
        raise
    with response:
        if state is not None:
            state.record_credits(response.headers)
        return json.load(response)


def retry_after(error, fallback):
    value = error.headers.get("Retry-After") if error.headers else None
    if value is not None:
        value = value.strip()
        if value.isascii() and value.isdigit():
            return int(value)
        try:
            return max(0, parsedate_to_datetime(value).timestamp() - time.time())
        except (TypeError, ValueError, OverflowError):
            pass
    return fallback


def crossref(query, user_agent, timeout, *, state=None):
    data = get("https://api.crossref.org/works?" + urllib.parse.urlencode({
        "rows": 2, "select": "title,DOI,issued,author", "query.bibliographic": query}),
        user_agent, timeout, state=state)
    hits = []
    for item in data["message"]["items"]:
        dates = item.get("issued", {}).get("date-parts") or [[None]]
        hits.append({"title": (item.get("title") or [""])[0], "year": dates[0][0],
                     "doi": item.get("DOI"), "first_author": (item.get("author") or [{}])[0].get("family"),
                     "provider": "crossref"})
    return hits


def openalex(query, user_agent, timeout, *, api_key, state=None):
    data = get("https://api.openalex.org/works?" + urllib.parse.urlencode({
        "per-page": 2, "select": "title,doi,publication_year,authorships", "search": query}),
        user_agent, timeout, api_key=api_key, state=state)
    return [{"title": item.get("title"), "year": item.get("publication_year"), "doi": item.get("doi"),
             "first_author": ((item.get("authorships") or [{}])[0].get("author") or {}).get("display_name"),
             "provider": "openalex"} for item in data["results"]]


def judge(parsed, hits):
    best = None
    for hit in hits:
        sim = difflib.SequenceMatcher(None, norm(parsed["title"]), norm(hit["title"])).ratio()
        year_ok = str(hit["year"]) in parsed["years"] if hit.get("year") and parsed["years"] else None
        author = norm(hit.get("first_author"))
        author_ok = bool(author) and (author in norm(parsed["author"]) or author.split()[-1] in norm(parsed["author"]).split())
        score = sim + (0.3 if year_ok else 0) + (0.2 if author_ok else 0)
        if best is None or score > best["score"]:
            best = {"score": round(score, 3), "sim": round(sim, 3), "year_ok": year_ok,
                    "author_ok": author_ok, "hit": hit}
    if best and best["sim"] >= 0.8 and best["year_ok"] is not False:
        return "match", best
    if best and (best["sim"] >= 0.5 or best["author_ok"]):
        return "partial", best
    return "nohit", best


def check_report(path, user_agent, timeout, delay, state=None, items=None, standard_pattern=STANDARD):
    state = state if state is not None else RunState()
    for item in (score(path)["items"] if items is None else items):
        name, source = item["name"], item["source"]
        parsed = parse_source(source)
        verdict = classification(source, parsed, standard_pattern)
        row = {"report": str(path), "candidate": name, "source": source,
               "flagged_unverified": item["unverified_flag"], "parsed": parsed,
               "query": None, "verdict": verdict, "best": None, "error": None,
               "network_attempts": 0, "providers_succeeded": [], "providers": {},
               "credits_used": 0}
        if "openalex" in state.providers and not state.openalex_key:
            row["providers"]["openalex"] = "skipped: no key (OPENALEX_API_KEY)"
        credits_before = state.credits_used
        try:
            state.remaining()
            if verdict is None:
                check_citation(row, parsed, user_agent, timeout, delay, state)
        except BudgetExceeded:
            row["verdict"] = "pending"
            row["error"] = "time budget exceeded"
        finally:
            row["credits_used"] = state.credits_used - credits_before
        yield state.redact_row(row)


def check_citation(row, parsed, user_agent, timeout, delay, state):
    query = " ".join(x for x in (parsed["author"], parsed["title"], next(iter(parsed["years"]), "")) if x)
    row["query"] = query
    hits, errors = [], []
    for name in state.providers:
        provider = {"crossref": crossref, "openalex": openalex}[name]
        if name == "openalex" and not state.openalex_key:
            row["providers"][name] = "skipped: no key (OPENALEX_API_KEY)"
            continue
        state.remaining()
        if provider.__name__ in state.blocked:
            row["providers"][provider.__name__] = "skipped: repeated 429/5xx failures"
            continue
        for attempt in range(4):  # One request and up to three retries.
            state.remaining()
            row["network_attempts"] += 1
            try:
                hits.extend(state.request(provider, query, user_agent, timeout))
                row["providers_succeeded"].append(provider.__name__)
                row["providers"][provider.__name__] = "ok"
                break
            except BudgetExceeded:
                raise
            except Exception as exc:
                retryable = isinstance(exc, urllib.error.HTTPError) and (
                    exc.code == 429 or 500 <= exc.code < 600)
                if retryable and attempt < 3:
                    wait = retry_after(exc, 2 ** (attempt + 1))
                    exc.close()
                    state.sleep(max(delay, wait))
                    continue
                detail = state.redact(f"{type(exc).__name__}: {exc}")
                if isinstance(exc, urllib.error.HTTPError):
                    exc.close()
                row["providers"][provider.__name__] = f"error:{detail}"
                errors.append(f"{provider.__name__}: {detail}")
                if retryable and attempt == 3:
                    state.blocked.add(provider.__name__)
                break
        if delay:
            state.sleep(delay)
    row["verdict"], row["best"] = judge(parsed, hits)
    row["error"] = "; ".join(errors) or None


def parse_providers(value):
    names = [name.strip() for name in value.split(",")]
    if any(name not in ("crossref", "openalex") for name in names):
        raise argparse.ArgumentTypeError("Providers must be comma-separated crossref,openalex")
    return tuple(dict.fromkeys(names))


def load_openalex_key(path):
    if path is not None:
        try:
            with path.open("rb") as stream:
                key = stream.readline().decode("utf-8").strip()
        except (OSError, UnicodeError):
            raise ValueError("Cannot read the first line of the OpenAlex key file") from None
    else:
        key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if any(not 33 <= ord(char) <= 126 for char in key):
        raise ValueError("OpenAlex key must be one ASCII line without whitespace")
    return key or None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--user-agent", default="theory-sweep-skill/0.2")
    parser.add_argument("--standard-pattern", default=STANDARD.pattern,
                        help="Case-insensitive regex for standard documents")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--providers", type=parse_providers, default="crossref,openalex",
                        help="Comma-separated providers (default: crossref,openalex)")
    parser.add_argument("--openalex-key-file", type=Path,
                        help="Key file (first line; overrides OPENALEX_API_KEY)")
    parser.add_argument("--max-wait", type=float, default=20,
                        help="Maximum wait per retry in seconds (default: 20)")
    parser.add_argument("--budget", type=float, default=300,
                        help="Total time budget in seconds (default: 300)")
    args = parser.parse_args()
    if (not all(math.isfinite(v) for v in (args.timeout, args.delay, args.max_wait, args.budget))
            or args.timeout <= 0 or args.budget <= 0 or args.delay < 0 or args.max_wait < 0
            or re.search(r"[\r\n]", args.user_agent)):
        parser.error("timeout and budget must be finite and positive; delay and max-wait nonnegative; User-Agent one line")
    try:
        standard_pattern = re.compile(args.standard_pattern, re.I)
    except re.error as exc:
        parser.error(f"Invalid --standard-pattern: {exc}")
    failed, output = False, None
    state = RunState(args.max_wait, args.budget, providers=args.providers)
    try:
        state.openalex_key = load_openalex_key(args.openalex_key_file)
        if args.out:
            if args.out.resolve() in {p.resolve() for p in args.reports}:
                raise ValueError("Cannot overwrite an input report with JSONL")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            output = args.out.open("w", encoding="utf-8")
        reports = []
        for path in args.reports:
            try:
                result = score(path)
                if result["language"] is None:
                    raise ValueError("unknown language")
                reports.append((path, result["items"]))
            except (OSError, UnicodeError, ValueError) as exc:
                print(state.redact(f"Error: {path}: {exc}"), file=sys.stderr)
                failed = True
        total = sum(len(items) for _, items in reports)
        number = 0
        for path, items in reports:
            for row in check_report(path, args.user_agent, args.timeout, args.delay, state, items, standard_pattern):
                number += 1
                line = json.dumps(row, ensure_ascii=False)
                print(line, flush=True)
                if output:
                    output.write(line + "\n")
                    output.flush()
                print(state.redact(f"[{number}/{total}] {path.name}: {row['verdict']}"),
                      file=sys.stderr, flush=True)
    except (OSError, ValueError) as exc:
        print(state.redact(f"Error: {exc}"), file=sys.stderr)
        failed = True
    finally:
        if output:
            output.close()
        print(f"OpenAlex credits total: {state.credits_used} / {DAILY_CREDITS} "
              f"(of daily limit {state.credits_used / DAILY_CREDITS:.2%})",
              file=sys.stderr, flush=True)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
