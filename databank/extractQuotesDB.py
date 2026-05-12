import sqlite3

# Path to your SQLite file
db_path = 'databank/quotes.sqlite'

# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Example: list all tables in the database
'''cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)'''

table_name = 'QUOTES'  # Replace with your actual table name

# Fetch first 5 rows
cursor.execute(f"SELECT * FROM {table_name} LIMIT 40;")
rows = cursor.fetchall()
column_names= [desc[0] for desc in cursor.description]

print("Columns:", column_names)
for row in rows:
    print(row)

conn.close()