"""
CV Generator MCP Server (FastMCP 2.0 Implementation)
FastMCP-compatible HTTP server for CV generation

Environment Variables Required:
- MONGO_URI: MongoDB connection string (required)
"""

import logging
import os
from typing import Any, Dict
from contextlib import asynccontextmanager

# Load environment variables (optional - FastMCP provides them via environment)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from fastmcp import FastMCP

# Import connect_db for database initialization
from config.database import connect_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# Lifespan Context Manager
# ============================================

@asynccontextmanager
async def lifespan(app):
    """Database connection lifecycle management"""
    try:
        logger.info("=" * 50)
        logger.info("CV Generator MCP Server Starting...")
        logger.info("=" * 50)
        
        # Check for MONGO_URI
        mongo_uri = os.getenv('MONGO_URI')
        if mongo_uri:
            logger.info(f"MONGO_URI found (length: {len(mongo_uri)})")
        else:
            logger.error("MONGO_URI not found in environment")
            raise ValueError("MONGO_URI environment variable is required")
        
        # Connect to database
        logger.info("Connecting to MongoDB...")
        await connect_db()
        logger.info("Database connected successfully")
        
        logger.info("=" * 50)
        logger.info("CV Generator MCP Server is running!")
        logger.info("Available tools: generate_cv, get_profile, create_profile, update_profile, delete_profile")
        logger.info("=" * 50)
        
        yield
        
    except Exception as error:
        logger.error("=" * 50)
        logger.error(f"MCP Server failed to start: {str(error)}")
        logger.error(f"Error type: {type(error).__name__}")
        logger.error("=" * 50)
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        # Cleanup on shutdown
        logger.info("CV Generator MCP Server shutting down...")
        await close_db()
        logger.info("Server stopped")


# ============================================
# FastMCP Server Setup
# ============================================

# Create FastMCP server instance with lifespan
mcp = FastMCP("cv-generator-mcp", lifespan=lifespan)

# Also expose as 'server' and 'app' for compatibility
server = mcp
app = mcp


# ============================================
# Lazy Tool Initialization
# ============================================

tools_cache = None

def get_tools():
    """Lazy initialization of tool instances"""
    global tools_cache
    if tools_cache is None:
        from tools.generate_cv import GenerateCVTool
        from tools.profile_tools import (
            GetProfileTool,
            CreateProfileTool,
            UpdateProfileTool,
            DeleteProfileTool,
        )
        
        tools_cache = {
            'generate_cv': GenerateCVTool(),
            'get_profile': GetProfileTool(),
            'create_profile': CreateProfileTool(),
            'update_profile': UpdateProfileTool(),
            'delete_profile': DeleteProfileTool(),
        }
    return tools_cache


# ============================================
# MCP Tool: Generate CV
# ============================================

@mcp.tool()
async def generate_cv(
    userId: str,
    template: str = "modern"
) -> Dict[str, Any]:
    """Generate a professional CV from user profile data. Supports Classic, Modern, and Europass templates."""
    tools = get_tools()
    tool = tools['generate_cv']
    
    arguments = {
        'userId': userId,
        'template': template
    }
    
    result = await tool.execute(arguments)
    return result


# ============================================
# MCP Tool: Get Profile
# ============================================

@mcp.tool()
async def get_profile(userId: str) -> Dict[str, Any]:
    """Retrieve user profile information by user ID"""
    tools = get_tools()
    tool = tools['get_profile']
    
    arguments = {'userId': userId}
    result = await tool.execute(arguments)
    return result


# ============================================
# MCP Tool: Create Profile
# ============================================

@mcp.tool()
async def create_profile(
    userId: str,
    name: str,
    email: str,
    phone: str,
    address: str,
    summary: str,
    experience: list,
    education: list,
    skills: list,
    languages: list = None,
    certifications: list = None,
    projects: list = None,
    profilePhoto: str = None
) -> Dict[str, Any]:
    """Create a new user profile with personal and professional information"""
    tools = get_tools()
    tool = tools['create_profile']
    
    arguments = {
        'userId': userId,
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'summary': summary,
        'experience': experience,
        'education': education,
        'skills': skills,
    }
    
    if languages is not None:
        arguments['languages'] = languages
    if certifications is not None:
        arguments['certifications'] = certifications
    if projects is not None:
        arguments['projects'] = projects
    if profilePhoto is not None:
        arguments['profilePhoto'] = profilePhoto
    
    result = await tool.execute(arguments)
    return result


# ============================================
# MCP Tool: Update Profile
# ============================================

@mcp.tool()
async def update_profile(
    userId: str,
    name: str = None,
    email: str = None,
    phone: str = None,
    address: str = None,
    summary: str = None,
    experience: list = None,
    education: list = None,
    skills: list = None,
    languages: list = None,
    certifications: list = None,
    projects: list = None,
    profilePhoto: str = None
) -> Dict[str, Any]:
    """Update an existing user profile with new information"""
    tools = get_tools()
    tool = tools['update_profile']
    
    arguments = {'userId': userId}
    
    if name is not None:
        arguments['name'] = name
    if email is not None:
        arguments['email'] = email
    if phone is not None:
        arguments['phone'] = phone
    if address is not None:
        arguments['address'] = address
    if summary is not None:
        arguments['summary'] = summary
    if experience is not None:
        arguments['experience'] = experience
    if education is not None:
        arguments['education'] = education
    if skills is not None:
        arguments['skills'] = skills
    if languages is not None:
        arguments['languages'] = languages
    if certifications is not None:
        arguments['certifications'] = certifications
    if projects is not None:
        arguments['projects'] = projects
    if profilePhoto is not None:
        arguments['profilePhoto'] = profilePhoto
    
    result = await tool.execute(arguments)
    return result


# ============================================
# MCP Tool: Delete Profile
# ============================================

@mcp.tool()
async def delete_profile(userId: str) -> Dict[str, Any]:
    """Delete a user profile by user ID"""
    tools = get_tools()
    tool = tools['delete_profile']
    
    arguments = {'userId': userId}
    result = await tool.execute(arguments)
    return result
