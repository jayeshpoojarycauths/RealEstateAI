import asyncio
import time
from sqlalchemy import text
from app.shared.db.session import SessionLocal
from app.shared.core.config import settings

async def test_connection_pool():
    """Test database connection pool settings with concurrent connections."""
    print("Testing database connection pool settings...")
    print(f"Pool size: {settings.DB_POOL_SIZE}")
    print(f"Max overflow: {settings.DB_MAX_OVERFLOW}")
    print(f"Pool timeout: {settings.DB_POOL_TIMEOUT}")
    print(f"Pool recycle: {settings.DB_POOL_RECYCLE}")
    
    # Create a list to store all sessions
    sessions = []
    start_time = time.time()
    
    try:
        # Create more connections than pool size to test overflow
        num_connections = settings.DB_POOL_SIZE + settings.DB_MAX_OVERFLOW + 5
        print(f"\nAttempting to create {num_connections} concurrent connections...")
        
        for i in range(num_connections):
            db = SessionLocal()
            sessions.append(db)
            # Execute a simple query to verify connection
            result = db.execute(text("SELECT 1"))
            print(f"Connection {i+1} established successfully")
            
        # Keep connections open for a while to test pool behavior
        print("\nHolding connections for 5 seconds...")
        await asyncio.sleep(5)
        
        # Test connection recycling
        print("\nTesting connection recycling...")
        for i, db in enumerate(sessions):
            result = db.execute(text("SELECT 1"))
            print(f"Connection {i+1} still valid after 5 seconds")
        
    except Exception as e:
        print(f"\nError during connection pool test: {str(e)}")
        raise
    finally:
        # Close all sessions
        for db in sessions:
            db.close()
        
        end_time = time.time()
        print(f"\nTest completed in {end_time - start_time:.2f} seconds")
        print(f"Successfully managed {len(sessions)} connections")

if __name__ == "__main__":
    asyncio.run(test_connection_pool()) 