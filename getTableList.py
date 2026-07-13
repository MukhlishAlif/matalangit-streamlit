import sqlite3

# 1. Open a connection to your SQLite database file
conn = sqlite3.connect("outlet.db")
cursor = conn.cursor()

# 2. Query the system table for base tables
query = """
    SELECT name 
    FROM sqlite_master 
    WHERE type = 'table' 
      AND name NOT LIKE 'sqlite_%';
"""
cursor.execute(query)
table_list = [row[0] for row in cursor.fetchall()]

print(f"📦 Found Tables: {table_list}\n" + "="*60)

# 3. Iterate through each table to inspect attributes and sample data
for table_name in table_list:
    print(f"\n📋 TABLE: {table_name}")
    
    # Fetch structural attributes (Column details)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_metadata = cursor.fetchall()
    
    # Extract clean column names
    column_names = [col[1] for col in columns_metadata]
    print(f"🔹 Attributes: {column_names}")
    
    # Heuristic: Find a time-related column to sort by
    time_column = None
    time_indicators = ['created_at', 'updated_at', 'timestamp', 'date', 'time']
    
    for indicator in time_indicators:
        # Exact match check
        if indicator in column_names:
            time_column = indicator
            break
        # Partial match check (e.g., 'tap_in_time')
        found = [c for c in column_names if indicator in c.lower()]
        if found:
            time_column = found[0]
            break

    # Build the preview data select statement
    if time_column:
        order_clause = f"ORDER BY {time_column} DESC"
        print(f"⏱️ Sorting records by detected time column: '{time_column}'")
    else:
        # Fallback if no explicit time column exists in the table schema
        order_clause = "ORDER BY rowid DESC" 
        print("ℹ️ No explicit time column found. Falling back to rowid sequence sorting.")

    preview_query = f"SELECT * FROM {table_name} {order_clause} LIMIT 2000;"
    
    try:
        cursor.execute(preview_query)
        rows = cursor.fetchall()
        
        print(f"👇 Preview (Up to 5 rows):")
        if not rows:
            print("   [Table is empty]")
        for row in rows:
            print(f"   {row}")
    except sqlite3.Error as e:
        print(f"❌ Could not retrieve records from {table_name}: {e}")
        
    print("-" * 60)

# 4. Clean up connection frames
cursor.close()
conn.close()