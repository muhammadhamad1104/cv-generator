"""
CV Generator MCP Server (Python Implementation)
This is a Python version of the Node.js MCP server for CV generation

Environment Variables Required:
- MONGO_URI: MongoDB connection string (required)
"""

import asyncio
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables (optional - FastMCP provides them via environment)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # dotenv is optional, environment variables may be set directly

from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)

# Import connect_db but don't call it at module level
from config.database import connect_db
# Tools imported lazily to avoid initialization errors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# MCP Server Setup (for FastMCP Cloud)
# ============================================

# Create MCP server instance at module level
server = Server("cv-generator-mcp")
mcp = server  # Alternative name for FastMCP
app = server  # Another alternative name

# Tools will be initialized lazily
tools = None

def get_tools():
    """Lazy initialization of tools"""
    global tools
    if tools is None:
        # Import tools only when needed
        from tools.generate_cv import GenerateCVTool
        from tools.profile_tools import (
            GetProfileTool,
            CreateProfileTool,
            UpdateProfileTool,
            DeleteProfileTool,
        )
        
        tools = [
            GenerateCVTool(),
            GetProfileTool(),
            CreateProfileTool(),
            UpdateProfileTool(),
            DeleteProfileTool(),
        ]
    return tools


# ============================================
# Register MCP Handlers
# ============================================

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available tools"""
    tool_list = get_tools()
    return ListToolsResult(
        tools=[
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema
            )
            for tool in tool_list
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Execute a tool by name"""
    tool_list = get_tools()
    
    # Find the tool
    tool = next((t for t in tool_list if t.name == name), None)
    
    if not tool:
        logger.error(f"Tool not found: {name}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Tool not found: {name}"
                    }, indent=2)
                )
            ],
            isError=True
        )
    
    try:
        # Execute the tool
        result = await tool.execute(arguments)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
        )
    except Exception as error:
        logger.error(f"MCP: Error executing tool {name}: {str(error)}")
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(error)
                    }, indent=2)
                )
            ],
            isError=True
        )


# ============================================
# Legacy Class (for backward compatibility)
# ============================================

class CVGeneratorMCPServer:
    """MCP Server for CV Generation (legacy wrapper)"""
    
    def __init__(self):
        self.server = server
        self.tools = get_tools()
    
    async def start(self):
        """Start the MCP server"""
        try:
            logger.info("=" * 50)
            logger.info("CV Generator MCP Server Starting...")
            logger.info("=" * 50)
            
            # Check environment
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
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
            
            # Start MCP server with stdio transport
            logger.info("Starting MCP server with stdio transport...")
            async with stdio_server() as (read_stream, write_stream):
                logger.info("=" * 50)
                logger.info("CV Generator MCP Server is running!")
                logger.info(f"Available tools: {', '.join(t.name for t in self.tools)}")
                logger.info("=" * 50)
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as error:
            logger.error("=" * 50)
            logger.error(f"MCP Server failed to start: {str(error)}")
            logger.error(f"Error type: {type(error).__name__}")
            logger.error("=" * 50)
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)


async def main():
    """Main entry point"""
    # Verify environment variables before starting
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        logger.error("=" * 60)
        logger.error("FATAL: MONGO_URI environment variable not set!")
        logger.error("=" * 60)
        logger.error("Please set MONGO_URI in your environment variables:")
        logger.error("  - For FastMCP: Add MONGO_URI in Environment Variables section")
        logger.error("  - For local: Add MONGO_URI to .env file")
        logger.error("=" * 60)
        sys.exit(1)
    
    mcp_server = CVGeneratorMCPServer()
    await mcp_server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP Server: Shutting down...")
    except Exception as error:
        logger.error(f"MCP Server: Fatal error - {str(error)}")
        sys.exit(1)
