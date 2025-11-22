"""
Test script to verify server startup without MCP transport
"""

import asyncio
import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_startup():
    """Test server components startup"""
    
    try:
        logger.info("=" * 60)
        logger.info("Testing CV Generator MCP Server Components")
        logger.info("=" * 60)
        
        # 1. Test environment variables
        logger.info("\n1️⃣ Testing environment variables...")
        from dotenv import load_dotenv
        load_dotenv()
        
        mongo_uri = os.getenv('MONGO_URI')
        if mongo_uri:
            logger.info(f"✅ MONGO_URI found (length: {len(mongo_uri)})")
        else:
            logger.error("❌ MONGO_URI not found")
            return False
        
        # 2. Test imports
        logger.info("\n2️⃣ Testing imports...")
        try:
            from config.database import connect_db, get_collection
            from services.cv_service import CVService
            from services.storage_service import StorageService
            from tools.generate_cv import GenerateCVTool
            from tools.profile_tools import GetProfileTool, CreateProfileTool
            logger.info("✅ All imports successful")
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            return False
        
        # 3. Test database connection
        logger.info("\n3️⃣ Testing database connection...")
        try:
            await connect_db()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
        
        # 4. Test tool initialization
        logger.info("\n4️⃣ Testing tool initialization...")
        try:
            tools = [
                GenerateCVTool(),
                GetProfileTool(),
                CreateProfileTool(),
            ]
            logger.info(f"✅ Initialized {len(tools)} tools")
        except Exception as e:
            logger.error(f"❌ Tool initialization failed: {e}")
            return False
        
        # 5. Test services
        logger.info("\n5️⃣ Testing services...")
        try:
            cv_service = CVService()
            storage_service = StorageService()
            logger.info(f"✅ CV Service templates dir: {cv_service.templates_dir}")
            logger.info(f"✅ Storage Service upload dir: {storage_service.upload_base_dir}")
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 ALL TESTS PASSED - Server components are ready!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = asyncio.run(test_startup())
    sys.exit(0 if result else 1)
