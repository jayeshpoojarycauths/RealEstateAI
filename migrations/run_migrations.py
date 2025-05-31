import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        dbname="your_db_name",  # Replace with your database name
        user="your_user",       # Replace with your database user
        password="your_password", # Replace with your database password
        host="localhost",
        port="5432"
    )

def run_migration(conn, migration_file):
    """Run a single migration file."""
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql)
        
        logger.info(f"Successfully ran migration: {migration_file}")
    except Exception as e:
        logger.error(f"Error running migration {migration_file}: {str(e)}")
        raise

def main():
    """Run all migrations in order."""
    # Get list of migration files
    migration_files = sorted([f for f in os.listdir('.') if f.endswith('.sql')])
    
    try:
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file}")
            run_migration(conn, migration_file)
        
        logger.info("All migrations completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 