import os
import sqlalchemy

database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url and 'postgresql' in database_url:
    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.begin() as conn:  # engine.begin() auto-commits on success
            conn.execute(sqlalchemy.text(
                'ALTER TABLE "order" ALTER COLUMN payment_status TYPE VARCHAR(100)'
            ))
            conn.execute(sqlalchemy.text(
                'ALTER TABLE "order" ALTER COLUMN payment_method TYPE VARCHAR(50)'
            ))
        print("✅ DB columns fixed successfully!")
    except Exception as e:
        print(f"Note (may already be applied): {e}")
else:
    print("Skipping — not PostgreSQL")