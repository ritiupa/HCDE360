import csv
from collections import Counter


def count_roles(
    input_file: str = "responses.csv", output_file: str = "role_counts.csv"
) -> None:
    role_counts = Counter()

    with open(input_file, mode="r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        if "role" not in reader.fieldnames:
            raise ValueError("Input CSV must include a 'role' column.")

        for row in reader:
            role_value = (row.get("role") or "").strip()
            if not role_value:
                continue

            normalized_role = role_value.upper()
            role_counts[normalized_role] += 1

    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["role", "count"])
        for role, count in sorted(role_counts.items()):
            writer.writerow([role, count])

    print("Role counts:")
    for role, count in sorted(role_counts.items()):
        print(f"{role}: {count}")


if __name__ == "__main__":
    count_roles()
