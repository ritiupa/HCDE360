import csv
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

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

for row in rows:
    role = row["role"].strip().title()
    if not role:
        continue
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
valid_experience_rows = 0
for row in rows:
    years = parse_experience_years(row["experience_years"])
    if years is not None:
        total_experience += years
        valid_experience_rows += 1

if valid_experience_rows > 0:
    avg_experience = total_experience / valid_experience_rows
    print(f"\nAverage years of experience: {avg_experience:.1f}")
else:
    print("\nAverage years of experience: N/A (no valid values)")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in rows:
    participant_name = row["participant_name"].strip()
    if not participant_name:
        continue
    score_text = row["satisfaction_score"].strip()
    if not score_text:
        continue
    if not score_text.isdigit():
        continue
    scored_rows.append((participant_name, int(score_text)))

scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]

print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")
