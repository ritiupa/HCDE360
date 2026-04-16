import csv


def clean_responses(
    input_file: str = "responses.csv", output_file: str = "responses_cleaned.csv"
) -> None:
    with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("Input CSV has no header row.")

        with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                name_value = (row.get("name") or "").strip()
                if not name_value:
                    continue

                if "role" in row and row["role"] is not None:
                    row["role"] = row["role"].upper()

                writer.writerow(row)


if __name__ == "__main__":
    clean_responses()
