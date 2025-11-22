"""
CV Generator MCP Server (Python Implementation)
This is a Python version of the Node.js MCP server for CV generation
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)

from config.database import connect_db
from tools.generate_cv import GenerateCVTool
from tools.profile_tools import (
    GetProfileTool,
    CreateProfileTool,
    UpdateProfileTool,
    DeleteProfileTool,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class CVGeneratorMCPServer:
    """MCP Server for CV Generation"""
    
    def __init__(self):
        self.server = Server("cv-generator-mcp")
        self.tools = [
            GenerateCVTool(),
            GetProfileTool(),
            CreateProfileTool(),
            UpdateProfileTool(),
            DeleteProfileTool(),
        ]
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name=tool.name,
                        description=tool.description,
                        inputSchema=tool.input_schema
                    )
                    for tool in self.tools
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Execute a tool by name"""
            # Find the tool
            tool = next((t for t in self.tools if t.name == name), None)
            
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
    
    async def start(self):
        """Start the MCP server"""
        try:
            # Connect to database
            await connect_db()
            logger.info("MCP Server: Database connected")
            
            # Start MCP server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                logger.info("CV Generator MCP Server running on stdio")
                logger.info(f"Available tools: {', '.join(t.name for t in self.tools)}")
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as error:
            logger.error(f"MCP Server: Failed to start - {str(error)}")
            sys.exit(1)


async def main():
    """Main entry point"""
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
