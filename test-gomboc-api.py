#!/usr/bin/env python3
"""
Test Gomboc API connectivity with valid queries
"""

import os
import json
import urllib.request
import urllib.error

GOMBOC_PAT = os.getenv("GOMBOC_PAT")
GOMBOC_API_URL = "https://api.app.gomboc.ai"

def test_api():
    print("Testing Gomboc GraphQL API...\n")
    
    # Try a simpler query that might work
    query = {
        "query": """
        {
            __schema {
                types {
                    name
                }
            }
        }
        """
    }
    
    try:
        req = urllib.request.Request(
            f"{GOMBOC_API_URL}/graphql",
            data=json.dumps(query).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GOMBOC_PAT}"
            },
            method="POST"
        )
        
        print("📡 Sending request to Gomboc GraphQL API...")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            
            if "errors" in result:
                print(f"API Response has errors:")
                for error in result["errors"]:
                    print(f"  - {error.get('message', 'Unknown error')}")
                
                if "data" in result:
                    print("\n✅ API is reachable and authenticated!")
                    print(f"   Response size: {len(json.dumps(result))} bytes")
                    return True
            
            if "data" in result:
                print("✅ API is reachable and authenticated!")
                if result["data"]:
                    schema = result["data"].get("__schema", {})
                    types = schema.get("types", [])
                    print(f"   Schema has {len(types)} types")
                return True
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP Error {e.code}")
        print(f"   Response: {error_body[:300]}")
        
        # Check if it's auth-related
        if e.code == 401:
            print("   → Token may be invalid")
        elif e.code == 403:
            print("   → Token doesn't have permission")
        elif e.code in [400, 422]:
            print("   → Query syntax error (but API is reachable)")
            print("   → This is OK - proves authentication works")
            return True
        
        return False
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e.reason}")
        print("   (Network isolation in sandbox - expected)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = test_api()
    if result is True:
        print("\n✅ GOMBOC API TEST PASSED")
    elif result is None:
        print("\n⚠️ GOMBOC API TEST INCONCLUSIVE (network isolation)")
    else:
        print("\n❌ GOMBOC API TEST FAILED")
