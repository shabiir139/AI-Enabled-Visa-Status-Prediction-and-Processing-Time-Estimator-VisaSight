import requests
import sys
import time

def check_backend(url):
    print(f"\n🔍 Checking Backend at: {url}")
    
    # Clean URL
    url = url.rstrip('/')
    
    # 1. Check Health
    try:
        print("   Testing /health endpoint...", end="", flush=True)
        r = requests.get(f"{url}/health", timeout=10)
        if r.status_code == 200:
            print(" ✅ OK")
            print(f"   Status: {r.json()}")
        else:
            print(f" ❌ FAILED ({r.status_code})")
            print(f"   Response: {r.text}")
            return False
    except Exception as e:
        print(f" ❌ ERROR: {e}")
        return False

    # 2. Check Root
    try:
        print("   Testing root / endpoint...", end="", flush=True)
        r = requests.get(f"{url}/", timeout=10)
        if r.status_code == 200:
            print(" ✅ OK")
        else:
            print(f" ❌ FAILED ({r.status_code})")
            return False
    except:
        print(" ❌ ERROR")
        return False
        
    return True

if __name__ == "__main__":
    print("VisaSight Deployment Verifier")
    print("=============================")
    
    url = input("Enter your Railway Backend URL (e.g., https://xxx.up.railway.app): ").strip()
    
    if not url:
        print("❌ URL is required")
        sys.exit(1)
        
    if not url.startswith("http"):
        url = "https://" + url
        
    success = check_backend(url)
    
    if success:
        print("\n✅ Backend is UP and reachable!")
        print("👉 Make sure this URL is set as NEXT_PUBLIC_API_URL in Vercel.")
    else:
        print("\n❌ Backend seems down or unreachable.")
        print("👉 Check Railway logs for errors.")
