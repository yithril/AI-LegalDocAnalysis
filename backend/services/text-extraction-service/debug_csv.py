import csv
import io

# Test content from the invalid CSV fixture
content = "This is not a valid CSV file\nIt has no proper structure\nNo commas or delimiters"

print("Content:", repr(content))

# Try different delimiters
delimiters = [',', ';', '\t', '|']
for delimiter in delimiters:
    print(f"\nTrying delimiter: {repr(delimiter)}")
    try:
        csv_reader = csv.reader(io.StringIO(content), delimiter=delimiter)
        rows = list(csv_reader)
        print(f"Rows: {rows}")
        print(f"Number of rows: {len(rows)}")
        
        if len(rows) > 0:
            for i, row in enumerate(rows):
                print(f"Row {i}: {row} (length: {len(row)})")
                if len(row) > 1:
                    print(f"  -> Multiple columns found!")
                    break
    except Exception as e:
        print(f"Error: {e}") 