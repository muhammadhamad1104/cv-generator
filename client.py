"""
Simple MCP Client for testing the CV Generator MCP Server
"""

import asyncio
import json
import sys
from mcp.client.stdio import stdio_client
from mcp.client import ClientSession
from mcp.types import CallToolRequest


class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self):
        self.session: ClientSession = None
    
    async def connect(self, server_script_path: str):
        """Connect to MCP server"""
        # Start the server as a subprocess
        self.stdio_transport = await stdio_client(
            "python",
            [server_script_path]
        )
        
        # Create session
        self.session = ClientSession(
            self.stdio_transport.read,
            self.stdio_transport.write
        )
        
        # Initialize
        await self.session.initialize()
        print("✓ Connected to MCP server")
    
    async def list_tools(self):
        """List available tools"""
        response = await self.session.list_tools()
        print("\n📋 Available Tools:")
        for tool in response.tools:
            print(f"  • {tool.name}: {tool.description}")
        return response.tools
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a tool"""
        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        response = await self.session.call_tool(
            name=tool_name,
            arguments=arguments
        )
        
        print(f"\n✓ Response:")
        for content in response.content:
            if content.type == "text":
                result = json.loads(content.text)
                print(json.dumps(result, indent=2))
        
        return response
    
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()
        print("\n✓ Connection closed")


async def main():
    """Main test function"""
    print("=" * 60)
    print("CV Generator MCP Client - Interactive Test Suite")
    print("=" * 60)
    
    # Create client
    client = MCPClient()
    
    try:
        # Connect to server
        server_path = "server.py"
        await client.connect(server_path)
        
        # List available tools
        tools = await client.list_tools()
        
        # Interactive menu
        while True:
            print("\n" + "=" * 60)
            print("Select a tool to test:")
            print("=" * 60)
            print("1. generate_cv - Generate a CV PDF")
            print("2. get_profile - Get user profile")
            print("3. create_profile - Create new profile")
            print("4. update_profile - Update existing profile")
            print("5. delete_profile - Delete profile")
            print("0. Exit")
            print("=" * 60)
            
            choice = input("\nEnter choice (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                # Generate CV
                user_id = input("Enter userId: ").strip()
                template = input("Enter template (classic/modern/europass) [europass]: ").strip() or "europass"
                
                await client.call_tool("generate_cv", {
                    "userId": user_id,
                    "template": template,
                    "settings": {
                        "showPhoto": True,
                        "sections": {
                            "personalInfo": True,
                            "summary": True,
                            "workExperience": True,
                            "education": True,
                            "skills": True,
                            "languages": True
                        }
                    }
                })
            
            elif choice == "2":
                # Get profile
                user_id = input("Enter userId: ").strip()
                await client.call_tool("get_profile", {"userId": user_id})
            
            elif choice == "3":
                # Create profile
                print("\nCreate Profile - Enter details:")
                user_id = input("userId: ").strip()
                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                email = input("Email: ").strip()
                phone = input("Phone: ").strip()
                city = input("City: ").strip()
                country = input("Country: ").strip()
                
                await client.call_tool("create_profile", {
                    "userId": user_id,
                    "personalInfo": {
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "phone": phone,
                        "city": city,
                        "country": country
                    },
                    "summary": "Professional summary",
                    "skills": [],
                    "workExperience": [],
                    "education": []
                })
            
            elif choice == "4":
                # Update profile
                user_id = input("Enter userId to update: ").strip()
                print("\nWhat do you want to update?")
                print("1. Summary")
                print("2. Add skill")
                update_choice = input("Choice: ").strip()
                
                if update_choice == "1":
                    summary = input("New summary: ").strip()
                    await client.call_tool("update_profile", {
                        "userId": user_id,
                        "summary": summary
                    })
                elif update_choice == "2":
                    skill_name = input("Skill name: ").strip()
                    skill_level = input("Level (Beginner/Intermediate/Advanced/Expert): ").strip()
                    await client.call_tool("update_profile", {
                        "userId": user_id,
                        "skills": [{"name": skill_name, "level": skill_level}]
                    })
            
            elif choice == "5":
                # Delete profile
                user_id = input("Enter userId to delete: ").strip()
                confirm = input(f"Are you sure you want to delete profile for {user_id}? (yes/no): ").strip()
                if confirm.lower() == "yes":
                    await client.call_tool("delete_profile", {"userId": user_id})
                else:
                    print("Cancelled")
            
            else:
                print("Invalid choice")
        
    except Exception as error:
        print(f"\n❌ Error: {error}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        await client.close()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as error:
        print(f"\n❌ Fatal error: {error}")
        sys.exit(1)
