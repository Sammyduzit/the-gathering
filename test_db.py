from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://dev:password@localhost:5432/thegathering"


def test_connection():
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ PostgreSQL Connection successful!")
            print(f"✅ Database version: {version}")

        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")

        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()