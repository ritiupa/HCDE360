import csv
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests
from requests.exceptions import RequestException, Timeout

# The Wikipedia Pageviews API is completely free and requires no API key.
# It returns how many times a Wikipedia article was viewed on any given day.
# When a design trend is popular, people look it up -- so page traffic
# is a reliable proxy for public interest in that trend.
WIKIPEDIA_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"

CATEGORIES = [
    "Category:Human\u2013computer_interaction",  # en dash in title
    "Category:User_interfaces",
    "Category:Interaction_design",
    "Category:User_experience",
]

DISCOVERY_POOL_SIZE = 50
TOP_TRENDS = 50

DAYS_TO_ANALYZE = 90
AVG_DAYS_PER_MONTH = 30.436875

REQUEST_TIMEOUT_SECONDS = 15
MAX_TRANSPORT_RETRIES = 4
MAX_HTTP_ROUNDS = 12
HTTP_429_BASE_WAIT = 2.0
REQUEST_DELAY_SECONDS = 0.65

USER_AGENT = "HCDE530-student-project/1.0"


def title_for_pageviews_api(title: str) -> str:
    return title.replace(" ", "_")


def iter_category_members(cmtitle: str):
    cmcontinue = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cmtitle,
            "cmnamespace": "0",
            "cmtype": "page",
            "cmlimit": "500",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        try:
            response = requests.get(
                MEDIAWIKI_API,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except RequestException as err:
            print(f"Category API error for {cmtitle!r}: {err}")
            return

        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            yield m["title"]

        cont = data.get("continue", {})
        if "cmcontinue" in cont:
            cmcontinue = cont["cmcontinue"]
        else:
            break


def discover_ux_candidate_titles(limit: int) -> list[str]:
    titles: list[str] = []
    seen: set[str] = set()
    for cmtitle in CATEGORIES:
        for title in iter_category_members(cmtitle):
            if title in seen:
                continue
            if "/" in title:
                continue
            seen.add(title)
            titles.append(title)
            if len(titles) >= limit:
                return titles
    return titles


def get_pageviews(article, start_date, end_date):
    """
    Fetch daily Wikipedia pageview counts for a given article title.
    Retries on 429 (rate limit) and transient 5xx with exponential backoff.
    """
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    url = f"{WIKIPEDIA_API}/en.wikipedia/all-access/user/{article}/daily/{start_str}/{end_str}"

    transport_failures = 0
    last_status = None

    for round_i in range(MAX_HTTP_ROUNDS):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except Timeout:
            transport_failures += 1
            if transport_failures >= MAX_TRANSPORT_RETRIES:
                print(f"  Timeout limit for '{article}' — skipping.")
                return []
            wait = min(45.0, HTTP_429_BASE_WAIT * (2 ** min(round_i, 5)))
            print(f"  Timeout for '{article}', sleeping {wait:.1f}s (retry)...")
            time.sleep(wait)
            continue
        except RequestException as err:
            print(f"  Network error for '{article}': {err}")
            return []

        last_status = response.status_code

        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get("items", []):
                date_str = item["timestamp"][:8]
                date = datetime.strptime(date_str, "%Y%m%d")
                views = item["views"]
                results.append((date, views))
            return results

        if response.status_code == 429:
            wait = min(60.0, HTTP_429_BASE_WAIT * (2 ** min(round_i, 5)))
            print(f"  Rate limited (429) for '{article}', sleeping {wait:.1f}s...")
            time.sleep(wait)
            continue

        if response.status_code in (404, 410):
            return []

        if response.status_code in (500, 502, 503, 504):
            wait = min(45.0, 2.0 * (2 ** min(round_i, 4)))
            print(f"  HTTP {response.status_code} for '{article}', sleeping {wait:.1f}s...")
            time.sleep(wait)
            continue

        print(f"  Could not fetch data for '{article}' (status {response.status_code})")
        return []

    print(f"  Gave up on '{article}' after {MAX_HTTP_ROUNDS} rounds (last HTTP {last_status})")
    return []


def momentum_detail(views_list):
    if len(views_list) < 60:
        return "Insufficient data", None, None, None

    sorted_views = sorted(views_list, key=lambda x: x[0])
    recent = sorted_views[-30:]
    prior = sorted_views[-60:-30]

    recent_avg = sum(v for _, v in recent) / len(recent)
    prior_avg = sum(v for _, v in prior) / len(prior)

    if prior_avg == 0:
        return "Insufficient data", None, round(recent_avg, 2), round(prior_avg, 2)

    change = (recent_avg - prior_avg) / prior_avg
    pct = round(change * 100, 1)

    if change > 0.10:
        label = "Rising"
    elif change < -0.10:
        label = "Fading"
    else:
        label = "Peaked / Stable"

    return label, pct, round(recent_avg, 2), round(prior_avg, 2)


def trend_status_slug(momentum_label: str) -> str:
    return {
        "Rising": "rising",
        "Fading": "fading",
        "Peaked / Stable": "peaked_or_stable",
        "Insufficient data": "insufficient_data",
    }.get(momentum_label, "unknown")


def build_raw_and_monthly_rows(scored, window_start: datetime, window_end: datetime):
    """Daily long-form rows plus monthly rollup per article (matches week 4 raw layout)."""
    ws = window_start.strftime("%Y-%m-%d")
    we = window_end.strftime("%Y-%m-%d")
    daily_rows = []
    month_totals: dict[tuple[str, str], int] = defaultdict(int)

    for display_title, views, _total in scored:
        for dt, v in views:
            day_s = dt.strftime("%Y-%m-%d")
            ym = dt.strftime("%Y-%m")
            month_totals[(display_title, ym)] += v
            daily_rows.append(
                {
                    "granularity": "daily",
                    "calendar_period": day_s,
                    "article_title": display_title,
                    "views": v,
                    "window_start": ws,
                    "window_end": we,
                }
            )

    monthly_rows = []
    for (title, ym), total in sorted(month_totals.items()):
        monthly_rows.append(
            {
                "granularity": "monthly",
                "calendar_period": ym,
                "article_title": title,
                "views": total,
                "window_start": ws,
                "window_end": we,
            }
        )

    daily_rows.sort(key=lambda r: (r["article_title"], r["calendar_period"]))
    monthly_rows.sort(key=lambda r: (r["article_title"], r["calendar_period"]))
    return daily_rows + monthly_rows


def build_summary_row(
    display_title: str,
    views: list,
    rank: int,
    window_start: datetime,
    window_end: datetime,
) -> dict:
    momentum, pct_chg, recent_avg, prior_avg = momentum_detail(views)
    total_views = sum(v for _, v in views)
    days_n = len(views)
    avg_day = total_views / days_n if days_n else 0.0
    est_month = avg_day * AVG_DAYS_PER_MONTH
    peak_day = max(views, key=lambda x: x[1])
    peak_ratio = round(peak_day[1] / avg_day, 2) if avg_day else ""

    return {
        "rank": rank,
        "trend": display_title,
        "window_start": window_start.strftime("%Y-%m-%d"),
        "window_end": window_end.strftime("%Y-%m-%d"),
        "days_with_data": days_n,
        "total_views_in_window": total_views,
        "avg_views_per_day": round(avg_day, 2),
        "est_views_per_month": round(est_month, 1),
        "peak_date": peak_day[0].strftime("%Y-%m-%d"),
        "peak_views": peak_day[1],
        "peak_to_mean_daily_ratio": peak_ratio,
        "recent_30d_avg_views": recent_avg if recent_avg is not None else "",
        "prior_30d_avg_views": prior_avg if prior_avg is not None else "",
        "pct_change_recent_vs_prior_30d": pct_chg if pct_chg is not None else "",
        "momentum": momentum,
        "trend_status": trend_status_slug(momentum),
        "lcd_line1": display_title[:16],
        "lcd_line2": f"Status: {momentum}"[:16],
    }


end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
start_date = end_date - timedelta(days=DAYS_TO_ANALYZE)

print(
    f"Discovering up to {DISCOVERY_POOL_SIZE} UX-related article titles from "
    f"{len(CATEGORIES)} Wikipedia categories...\n"
)
candidates = discover_ux_candidate_titles(DISCOVERY_POOL_SIZE)
print(f"Found {len(candidates)} candidates. Fetching pageviews to rank top {TOP_TRENDS}...\n")

scored: list[tuple[str, list, int]] = []
for i, display_title in enumerate(candidates, start=1):
    article = title_for_pageviews_api(display_title)
    print(f"[{i}/{len(candidates)}] {display_title}")
    views = get_pageviews(article, start_date, end_date)
    if views:
        total_views = sum(v for _, v in views)
        scored.append((display_title, views, total_views))
    time.sleep(REQUEST_DELAY_SECONDS)

scored.sort(key=lambda x: -x[2])
top_scored = scored[:TOP_TRENDS]

raw_rows = build_raw_and_monthly_rows(scored, start_date, end_date)
raw_path = Path(__file__).with_name("design_trends_raw.csv")
raw_fieldnames = [
    "granularity",
    "calendar_period",
    "article_title",
    "views",
    "window_start",
    "window_end",
]
with open(raw_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=raw_fieldnames)
    writer.writeheader()
    writer.writerows(raw_rows)
print(f"Saved {len(raw_rows)} raw rows (daily + monthly) to {raw_path}\n")

results = []
print(f"\nTop {len(top_scored)} articles by {DAYS_TO_ANALYZE}-day views — summary columns...\n")

for rank, (display_title, views, total_views) in enumerate(top_scored, start=1):
    print(f"Rank {rank}: {display_title} ({total_views:,} views in window)")
    row = build_summary_row(display_title, views, rank, start_date, end_date)
    results.append(row)
    print(f"  avg/day {row['avg_views_per_day']}, est/mo {row['est_views_per_month']}, {row['momentum']}\n")

output_path = Path(__file__).with_name("design_trends.csv")
fieldnames = [
    "rank",
    "trend",
    "window_start",
    "window_end",
    "days_with_data",
    "total_views_in_window",
    "avg_views_per_day",
    "est_views_per_month",
    "peak_date",
    "peak_views",
    "peak_to_mean_daily_ratio",
    "recent_30d_avg_views",
    "prior_30d_avg_views",
    "pct_change_recent_vs_prior_30d",
    "momentum",
    "trend_status",
    "lcd_line1",
    "lcd_line2",
]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Saved results for {len(results)} trends to {output_path}")
print("\nLCD display strings for Arduino sketch (first 10 rows):")
for r in results[:10]:
    print(f"  Line 1: '{r['lcd_line1']}'")
    print(f"  Line 2: '{r['lcd_line2']}'")
if len(results) > 10:
    print(f"  ... ({len(results) - 10} more rows in CSV)")
