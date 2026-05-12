import sqlite3
import csv
import re

# Path to your SQLite file
db_path = '../databank/quotes.sqlite'

# Output CSV file path
csv_path = '../databank/books_and_authors.csv'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define the table and columns
table_name = 'QUOTES'
columns_to_extract = ['title', 'author']

# Fetch distinct titles with one corresponding author
cursor.execute(f"""
    SELECT title, MIN(author) as author
    FROM {table_name}
    WHERE title IS NOT NULL AND author IS NOT NULL
    GROUP BY title;
""")
rows = cursor.fetchall()

# Clean up author spacing
def clean_author(author):
    # Collapse multiple whitespace characters into a single space
    return re.sub(r'\s+', ' ', author.strip())

cleaned_rows = [(title, clean_author(author)) for title, author in rows]

# Write to CSV
with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(columns_to_extract)  # Write header
    writer.writerows(cleaned_rows)       # Write cleaned data

print(f"Cleaned data saved to {csv_path}")

# Close the connection
conn.close()
