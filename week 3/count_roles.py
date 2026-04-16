import csv
from collections import Counter


def count_roles(
    input_file: str = "responses_cleaned.csv", output_file: str = "role_counts_new.csv"
) -> None:
    role_counter = Counter()

    with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            role = (row.get("role") or "").strip()
            if not role:
                continue
            normalized_role = role.lower()
            role_counter[normalized_role] += 1

    # Print counts to terminal
    print("Role counts:")
    for role, count in sorted(role_counter.items(), key=lambda item: (-item[1], item[0])):
        print(f"{role}: {count}")

    # Write counts to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["role", "count"])
        for role, count in sorted(role_counter.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow([role, count])


if __name__ == "__main__":
    count_roles()
