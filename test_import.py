"""
Minimal test to diagnose FastMCP import issues
"""
import sys
import traceback

print("=" * 50)
print("IMPORT TEST STARTING")
print("=" * 50)

try:
    print("Step 1: Importing server module...")
    import server
    print("SUCCESS: server module imported")
    
    print("\nStep 2: Checking for 'server' attribute...")
    has_server = hasattr(server, 'server')
    print(f"Has 'server' attribute: {has_server}")
    
    print("\nStep 3: Checking for 'mcp' attribute...")
    has_mcp = hasattr(server, 'mcp')
    print(f"Has 'mcp' attribute: {has_mcp}")
    
    print("\nStep 4: Checking for 'app' attribute...")
    has_app = hasattr(server, 'app')
    print(f"Has 'app' attribute: {has_app}")
    
    if has_server:
        print(f"\nStep 5: Type of server.server: {type(server.server)}")
        print(f"Module: {type(server.server).__module__}")
        print(f"Name: {type(server.server).__name__}")
    
    print("\n" + "=" * 50)
    print("IMPORT TEST PASSED")
    print("=" * 50)
    
except Exception as e:
    print("\n" + "=" * 50)
    print("IMPORT TEST FAILED")
    print("=" * 50)
    print(f"\nError: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
