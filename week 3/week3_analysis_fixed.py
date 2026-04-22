import csv
from collections import defaultdict
from pathlib import Path

# Load the survey data from a CSV file
filename = Path(__file__).resolve().parent / "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

word_to_number = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def parse_experience_years(value):
    cleaned = value.strip().lower()
    if not cleaned:
        return None

    if cleaned.isdigit():
        return int(cleaned)

    return word_to_number.get(cleaned)


def analyze_tool_satisfaction(rows):
    """
    Group survey rows by primary_tool and summarize satisfaction.

    For each tool, computes the average numeric satisfaction_score, sorts tools
    from highest to lowest average, and labels sentiment from score ranges on a
    1–5 scale: high (>=4), moderate (3–<4), low (<3).

    Args:
        rows: Iterable of dict-like rows with keys 'primary_tool' and
            'satisfaction_score'. Scores should be parseable as non-negative
            integers (e.g. from a cleaned dataset).

    Returns:
        A list of dictionaries, one per tool, each with keys:
        primary_tool, response_count, average_satisfaction, sentiment_summary.
        The list is ordered by average_satisfaction descending.
    """
    by_tool = defaultdict(list)
    for row in rows:
        tool = (row.get("primary_tool") or "").strip() or "Unknown"
        score_text = str(row.get("satisfaction_score", "")).strip()
        if not score_text.isdigit():
            continue
        by_tool[tool].append(int(score_text))

    results = []
    for tool, scores in by_tool.items():
        n = len(scores)
        avg = sum(scores) / n
        if avg >= 4.0:
            sentiment = "high satisfaction"
        elif avg >= 3.0:
            sentiment = "moderate satisfaction"
        else:
            sentiment = "low satisfaction"
        results.append(
            {
                "primary_tool": tool,
                "response_count": n,
                "average_satisfaction": round(avg, 3),
                "sentiment_summary": sentiment,
            }
        )

    results.sort(key=lambda r: r["average_satisfaction"], reverse=True)
    return results


def write_tool_satisfaction_summary_csv(summary_rows, output_path):
    """Write tool satisfaction analysis to a CSV file."""
    fieldnames = [
        "primary_tool",
        "response_count",
        "average_satisfaction",
        "sentiment_summary",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)


# Build cleaned rows: name, role, parseable experience, numeric satisfaction
cleaned_rows = []
for row in rows:
    participant_name = row["participant_name"].strip()
    role = row["role"].strip().title()
    years = parse_experience_years(row["experience_years"])
    score_text = row["satisfaction_score"].strip()
    if not participant_name or not role or years is None or not score_text.isdigit():
        continue
    cleaned_rows.append(
        {
            "response_id": row["response_id"].strip(),
            "participant_name": participant_name,
            "role": role,
            "department": row["department"].strip().title(),
            "age_range": row["age_range"].strip(),
            "experience_years": str(years),
            "satisfaction_score": score_text,
            "primary_tool": row["primary_tool"].strip().title(),
            "response_text": row["response_text"].strip(),
        }
    )

tool_summary = analyze_tool_satisfaction(cleaned_rows)
tool_summary_path = Path(__file__).resolve().parent / "tool_satisfaction_summary.csv"
write_tool_satisfaction_summary_csv(tool_summary, tool_summary_path)

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}
for row in cleaned_rows:
    role = row["role"]
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
for row in cleaned_rows:
    total_experience += int(row["experience_years"])

if cleaned_rows:
    avg_experience = total_experience / len(cleaned_rows)
    print(f"\nAverage years of experience: {avg_experience:.1f}")
else:
    print("\nAverage years of experience: N/A (no valid values)")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in cleaned_rows:
    scored_rows.append((row["participant_name"], int(row["satisfaction_score"])))

scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]

print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")

print("\nSatisfaction by primary tool (highest to lowest average):")
for entry in tool_summary:
    print(
        f"  {entry['primary_tool']}: avg {entry['average_satisfaction']:.2f} "
        f"({entry['sentiment_summary']}, n={entry['response_count']})"
    )
print(f"\nWrote tool satisfaction summary to: {tool_summary_path}")
