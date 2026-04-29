import requests
import csv
from datetime import datetime, timedelta
from pathlib import Path

# The Wikipedia Pageviews API is completely free and requires no API key.
# It returns how many times a Wikipedia article was viewed on any given day.
# When a design trend is popular, people look it up -- so page traffic
# is a reliable proxy for public interest in that trend.
WIKIPEDIA_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"

# These are the UX/UI design trends we are tracking.
# Each name matches the exact Wikipedia article title for that trend.
TRENDS = [
    "Glassmorphism",
    "Neumorphism",
    "Flat_design",
    "Dark_mode",
    "Skeuomorphism",
]

# We will pull the last 90 days of pageview data to see the trend arc --
# whether interest is rising, peaked, or fading.
DAYS_TO_ANALYZE = 90

def get_pageviews(article, start_date, end_date):
    """
    Fetch daily Wikipedia pageview counts for a given article title.

    Calls the Wikimedia REST API and returns a list of (date, views) tuples.
    Returns an empty list if the article is not found or the request fails.
    """
    # Format dates as YYYYMMDD strings, which is what the API expects.
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    # Build the full URL. The structure is:
    # /metrics/pageviews/per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}
    url = f"{WIKIPEDIA_API}/en.wikipedia/all-access/user/{article}/daily/{start_str}/{end_str}"

    response = requests.get(url, headers={"User-Agent": "HCDE530-student-project/1.0"})

    # If Wikipedia returns anything other than 200, the article probably
    # does not exist or was titled differently -- skip it gracefully.
    if response.status_code != 200:
        print(f"  Could not fetch data for '{article}' (status {response.status_code})")
        return []

    data = response.json()

    # The API returns a list of items under the "items" key.
    # Each item has a "timestamp" and "views" field.
    results = []
    for item in data.get("items", []):
        date_str = item["timestamp"][:8]  # e.g. "20250101"
        date = datetime.strptime(date_str, "%Y%m%d")
        views = item["views"]
        results.append((date, views))

    return results


def classify_momentum(views_list):
    """
    Given a list of (date, views) tuples, classify the trend's momentum.

    Compares the average views in the most recent 30 days against the
    30 days before that. If recent views are 10% higher, it is Rising.
    If they are 10% lower, it is Fading. Otherwise, it is Stable or Peaked.
    """
    if len(views_list) < 60:
        return "Insufficient data"

    # Sort by date to make sure we are comparing the right windows.
    sorted_views = sorted(views_list, key=lambda x: x[0])

    # Split into two 30-day windows: recent and prior.
    recent = sorted_views[-30:]
    prior = sorted_views[-60:-30]

    recent_avg = sum(v for _, v in recent) / len(recent)
    prior_avg = sum(v for _, v in prior) / len(prior)

    # Avoid dividing by zero if there were no views in the prior period.
    if prior_avg == 0:
        return "Insufficient data"

    # Calculate percentage change between the two windows.
    change = (recent_avg - prior_avg) / prior_avg

    if change > 0.10:
        return "Rising"
    elif change < -0.10:
        return "Fading"
    else:
        return "Peaked / Stable"


# Set the date range: today going back 90 days.
end_date = datetime.today()
start_date = end_date - timedelta(days=DAYS_TO_ANALYZE)

results = []

print(f"Fetching Wikipedia pageview data for {len(TRENDS)} design trends...\n")

for trend in TRENDS:
    print(f"Fetching: {trend}")
    views = get_pageviews(trend, start_date, end_date)

    if not views:
        continue

    total_views = sum(v for _, v in views)
    avg_daily = total_views / len(views)
    peak_day = max(views, key=lambda x: x[1])
    momentum = classify_momentum(views)

    # Format the trend name for display -- replace underscores with spaces.
    display_name = trend.replace("_", " ")

    results.append({
        "trend": display_name,
        "total_views_90d": total_views,
        "avg_daily_views": round(avg_daily, 1),
        "peak_date": peak_day[0].strftime("%Y-%m-%d"),
        "peak_views": peak_day[1],
        "momentum": momentum,
        # LCD-formatted strings truncated to 16 characters for the Arduino display.
        "lcd_line1": display_name[:16],
        "lcd_line2": f"Status: {momentum}"[:16],
    })

    print(f"  Total views (90d): {total_views:,}")
    print(f"  Avg daily: {avg_daily:.1f}")
    print(f"  Peak: {peak_day[1]:,} views on {peak_day[0].strftime('%Y-%m-%d')}")
    print(f"  Momentum: {momentum}\n")

# Save results to CSV in the same folder as this script.
output_path = Path(__file__).with_name("design_trends.csv")
fieldnames = ["trend", "total_views_90d", "avg_daily_views", "peak_date", "peak_views", "momentum", "lcd_line1", "lcd_line2"]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Saved results for {len(results)} trends to {output_path}")
print("\nLCD display strings for Arduino sketch:")
for r in results:
    print(f"  Line 1: '{r['lcd_line1']}'")
    print(f"  Line 2: '{r['lcd_line2']}'")
