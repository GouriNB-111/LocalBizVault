import os
import sqlalchemy

database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url and 'postgresql' in database_url:
    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(
                'ALTER TABLE "order" ALTER COLUMN payment_status TYPE VARCHAR(50)'
            ))
            conn.commit()
            print("✅ payment_status column fixed!")
    except Exception as e:
        print(f"Note: {e}")
else:
    print("Skipping — not PostgreSQL")