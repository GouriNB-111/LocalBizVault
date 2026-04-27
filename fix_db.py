import os
import psycopg2

database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url and 'postgresql' in database_url:
    try:
        # Use raw psycopg2 — bypasses SQLAlchemy transaction handling entirely
        conn = psycopg2.connect(database_url)
        conn.autocommit = True  # No transaction wrapper — DDL commits instantly
        cur = conn.cursor()

        cur.execute('ALTER TABLE "order" ALTER COLUMN payment_status TYPE VARCHAR(100)')
        print("✅ payment_status → VARCHAR(100)")

        cur.execute('ALTER TABLE "order" ALTER COLUMN payment_method TYPE VARCHAR(50)')
        print("✅ payment_method → VARCHAR(50)")

        cur.close()
        conn.close()
        print("✅ All column fixes applied!")

    except Exception as e:
        print(f"fix_db note: {e}")
else:
    print("Skipping — not PostgreSQL")