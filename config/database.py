"""
Database configuration and connection
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables (optional - may be set directly in container)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # dotenv is optional

logger = logging.getLogger(__name__)

# Database client
db_client: AsyncIOMotorClient = None
database = None


async def connect_db():
    """Connect to MongoDB database"""
    global db_client, database
    
    try:
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            logger.error("MONGO_URI not found in environment variables")
            logger.error("Available env vars: " + ", ".join(os.environ.keys()))
            raise ValueError("MONGO_URI environment variable is required")
        
        logger.info(f"Connecting to MongoDB (URI length: {len(mongo_uri)})")
        
        db_client = AsyncIOMotorClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Get database name from URI or use default
        database = db_client.get_default_database()
        
        # Test connection
        await db_client.admin.command('ping')
        
        logger.info(f"Connected to MongoDB database: {database.name}")
        
    except Exception as error:
        logger.error(f"Database connection error: {str(error)}")
        logger.error(f"Error type: {type(error).__name__}")
        raise


async def close_db():
    """Close database connection"""
    global db_client
    
    if db_client:
        db_client.close()
        logger.info("Database connection closed")


def get_database():
    """Get database instance"""
    return database


def get_collection(name: str):
    """Get a collection by name"""
    return database[name]
