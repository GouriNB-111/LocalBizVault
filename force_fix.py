import os
import psycopg2

database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to DB...")

conn = psycopg2.connect(database_url)
conn.autocommit = True
cur = conn.cursor()

# Check current column sizes first
cur.execute("""
    SELECT column_name, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = 'order' 
    AND column_name IN ('payment_status', 'payment_method')
""")
rows = cur.fetchall()
print(f"BEFORE: {rows}")

# Force the change
cur.execute('ALTER TABLE "order" ALTER COLUMN payment_status TYPE VARCHAR(100)')
cur.execute('ALTER TABLE "order" ALTER COLUMN payment_method TYPE VARCHAR(50)')

# Verify
cur.execute("""
    SELECT column_name, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = 'order' 
    AND column_name IN ('payment_status', 'payment_method')
""")
rows = cur.fetchall()
print(f"AFTER: {rows}")

cur.close()
conn.close()
print("DONE!")