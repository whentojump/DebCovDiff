import csv
import sys

def filter_csv_by_keys(file_a_path, file_b_path):
    """
    Reads two CSV files, A and B. For each row in A, it checks if the first
    four fields exist as a key in B. If so, it prints the row from A.

    This function correctly handles comma-containing fields enclosed in quotes.
    """
    try:
        # Step 1: Create a set of keys from the first four columns of B.csv
        # A set provides O(1) average time complexity for lookups, making it very efficient.
        keys_from_b = set()
        with open(file_b_path, 'r', newline='', encoding='utf-8') as b_file:
            reader_b = csv.reader(b_file)
            for row in reader_b:
                assert len(row) >= 3
                # A tuple is used because it's hashable and can be stored in a set.
                key = tuple(row[:3])
                keys_from_b.add(key)

        # Step 2: Iterate through A.csv and check for key existence
        # Write matching rows to standard output (the console).
        with open(file_a_path, 'r', newline='', encoding='utf-8') as a_file:
            reader_a = csv.reader(a_file)
            # The writer handles proper CSV formatting, including quoting when needed.
            writer = csv.writer(sys.stdout)

            for row in reader_a:
                assert len(row) >= 3
                key = tuple(row[:3])
                # If the key from file A is in our set of keys from file B, write the row.
                if key in keys_from_b:
                    writer.writerow(row)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Check if exactly two file paths are provided as arguments
    if len(sys.argv) != 3:
        print("Usage: python filter_csv.py <input_A.csv> <input_B.csv>", file=sys.stderr)
        sys.exit(1) # Exit the script if arguments are incorrect

    # The first argument (sys.argv[1]) is the first file path (A.csv)
    # The second argument (sys.argv[2]) is the second file path (B.csv)
    file_a = sys.argv[1]
    file_b = sys.argv[2]

    filter_csv_by_keys(file_a, file_b)
