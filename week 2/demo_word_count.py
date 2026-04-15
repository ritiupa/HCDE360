# These two lines bring in tools that Python doesn't load by default.
# "csv" knows how to read spreadsheet-style files with commas separating columns.
# "Path" helps us find files on the computer without hardcoding a folder location.
import csv
from pathlib import Path


# This line figures out where the CSV file is, relative to wherever this script lives.
# __file__ means "this script", and .with_name() swaps the script name for the CSV name.
# That way the script still works even if you move the whole folder somewhere else.
filename = Path(__file__).with_name("demo_responses.csv")

# Start with an empty list — we'll fill it up with rows from the CSV one by one.
responses = []

# Open the CSV file for reading.
# newline="" and encoding="utf-8" are safety settings that prevent weird character bugs.
with open(filename, newline="", encoding="utf-8") as f:
    # DictReader reads each row as a dictionary, so we can say row["role"]
    # instead of having to remember that role is column number 2.
    reader = csv.DictReader(f)
    for row in reader:
        # Add each row (one participant's data) to our responses list.
        responses.append(row)


def count_words(response):
    """Count the number of words in a response string.

    Takes a string, splits it on whitespace, and returns the word count.
    Used to measure response length across all participants.
    """
    # .split() breaks the text apart wherever there's a space, making a list of words.
    # len() then counts how many items are in that list — that's the word count.
    return len(response.split())


# Print a header row for the table we're about to display.
# The :<6 and :<22 parts are spacing instructions — they pad each column to a fixed width
# so the output lines up neatly instead of looking jumbled.
print(f"{'ID':<6} {'Role':<22} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 75)

# This list will collect the word count from every response
# so we can do math on all of them at the end (average, min, max).
word_counts = []

# Go through every participant's row one at a time.
for row in responses:
    # Pull out the three pieces of information we care about from this row.
    participant = row["participant_id"]
    role = row["role"]
    response = row["response"]

    # Run our count_words function on this participant's response.
    count = count_words(response)
    # Save that number so we can use it in the summary later.
    word_counts.append(count)

    # Responses can be very long — we only show the first 60 characters in the table
    # so the output stays readable. The "..." signals that the text continues.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    # Print one line of the table for this participant.
    print(f"{participant:<6} {role:<22} {count:<6} {preview}")

# After the loop finishes, print overall stats across all 25 responses.
print()
print("-- Summary --------------------------------")
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
# :.1f means "show one decimal place" — so 74.333... displays as 74.3
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")