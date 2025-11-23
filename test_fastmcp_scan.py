"""
Simulate what FastMCP does when scanning for server object
"""
import sys
import importlib.util

print("=" * 60)
print("SIMULATING FASTMCP IMPORT SCAN")
print("=" * 60)

# This is similar to what FastMCP does
try:
    print("\n1. Loading module spec...")
    spec = importlib.util.spec_from_file_location("server", "server.py")
    if spec is None:
        print("ERROR: Could not load module spec")
        sys.exit(1)
    
    print("2. Creating module from spec...")
    module = importlib.util.module_from_spec(spec)
    
    print("3. Adding to sys.modules...")
    sys.modules["server"] = module
    
    print("4. Executing module...")
    spec.loader.exec_module(module)
    
    print("5. Checking for server variables...")
    
    found_vars = []
    for var_name in ['server', 'mcp', 'app']:
        if hasattr(module, var_name):
            obj = getattr(module, var_name)
            obj_type = type(obj).__name__
            print(f"   ✓ Found '{var_name}': {obj_type}")
            found_vars.append(var_name)
        else:
            print(f"   ✗ Missing '{var_name}'")
    
    if found_vars:
        print(f"\n{'='*60}")
        print(f"SUCCESS: Found {len(found_vars)} variable(s)")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("ERROR: No server variables found!")
        print(f"{'='*60}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n{'='*60}")
    print("ERROR: Module import failed")
    print(f"{'='*60}")
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
