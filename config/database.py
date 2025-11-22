"""
Database configuration and connection
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            raise ValueError("MONGO_URI not found in environment variables")
        
        db_client = AsyncIOMotorClient(mongo_uri)
        
        # Get database name from URI or use default
        database = db_client.get_default_database()
        
        # Test connection
        await db_client.admin.command('ping')
        
        logger.info(f"Connected to MongoDB database: {database.name}")
        
    except Exception as error:
        logger.error(f"Database connection error: {str(error)}")
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
