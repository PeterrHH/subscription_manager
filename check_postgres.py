import psycopg2
import sys

def check_postgres_connection():
    """Check if PostgreSQL is properly configured and accessible."""
    try:
        # Try to connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="postgres",  # Default database
            user="postgres",
            password="postgres",  # Use the password from settings.py
            host="localhost",
            port="5432"
        )
        conn.close()
        print("✅ PostgreSQL connection successful!")
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def create_database():
    """Create the subscription_db database if it doesn't exist."""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='subscription_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating subscription_db database...")
            cursor.execute("CREATE DATABASE subscription_db")
            print("✅ Database created successfully!")
        else:
            print("✅ Database subscription_db already exists.")
        
        cursor.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ Failed to create database: {e}")
        return False

if __name__ == "__main__":
    print("Checking PostgreSQL connection...")
    if check_postgres_connection():
        create_database()
        print("\nPostgreSQL is properly configured. You can now run:")
        print("python manage.py migrate")
        print("python manage.py runserver")
    else:
        print("\nPlease make sure PostgreSQL is installed and running.")
        print("On macOS, you can install it with: brew install postgresql")
        print("And start it with: brew services start postgresql")
        sys.exit(1) 