"""
Simplified Pre-Submission Validation Script
Checks if your system is ready for instructor evaluation
"""
import os
import requests
import time
from dotenv import load_dotenv
from github import Github

load_dotenv()

BASE_URL = "http://localhost:8000"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
STUDENT_SECRET = os.getenv("STUDENT_SECRET")

print("="*60)
print("PRE-SUBMISSION VALIDATION")
print("="*60)

# Test 1: Server Running
print("\n1. Checking server...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Server is running")
    else:
        print(f"❌ Server returned {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Server not reachable: {e}")
    print("Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    exit(1)

# Test 2: Response Time
print("\n2. Checking response time...")
payload = {
    "email": "test@test.com",
    "secret": STUDENT_SECRET,
    "task": "test",
    "round": 1,
    "nonce": "test-nonce",
    "brief": "Test",
    "checks": [],
    "attachments": [],
    "evaluation_url": "https://test.com"
}

start = time.time()
response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
elapsed = time.time() - start

if response.status_code == 200 and elapsed < 2.0:
    print(f"✅ Response time: {elapsed:.3f}s (< 2s)")
else:
    print(f"⚠️  Response time: {elapsed:.3f}s")

# Test 3: Secret Validation
print("\n3. Checking secret validation...")
payload["secret"] = "WRONG_SECRET"
response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
if response.status_code == 401:
    print("✅ Returns 401 for invalid secret")
else:
    print(f"❌ Should return 401, got {response.status_code}")

# Test 4: GitHub Access
print("\n4. Checking GitHub access...")
try:
    github = Github(GITHUB_TOKEN)
    user = github.get_user()
    if user.login == GITHUB_USERNAME:
        print(f"✅ GitHub token valid (username: {user.login})")
    else:
        print(f"❌ Username mismatch: {user.login} != {GITHUB_USERNAME}")
except Exception as e:
    print(f"❌ GitHub auth failed: {e}")

# Test 5: Check Existing Repos
print("\n5. Checking deployed repositories...")
try:
    repos = [r.name for r in user.get_repos() if r.name.startswith('llm-project-')]
    if repos:
        print(f"✅ Found {len(repos)} deployed repositories")
        
        # Check first repo in detail
        repo = user.get_repo(repos[0])
        print(f"\n   Checking: {repos[0]}")
        
        # Check LICENSE
        try:
            license_file = repo.get_contents("LICENSE")
            if "MIT License" in license_file.decoded_content.decode('utf-8'):
                print(f"   ✅ MIT LICENSE exists")
            else:
                print(f"   ⚠️  LICENSE may not be MIT")
        except:
            print(f"   ❌ LICENSE not found")
        
        # Check README
        try:
            readme = repo.get_contents("README.md")
            content = readme.decoded_content.decode('utf-8')
            if len(content) > 100 and "# " in content:
                print(f"   ✅ README.md exists and looks good ({len(content)} chars)")
            else:
                print(f"   ⚠️  README may need improvement")
        except:
            print(f"   ❌ README.md not found")
        
        # Check index.html
        try:
            index = repo.get_contents("index.html")
            content = index.decoded_content.decode('utf-8')
            if len(content) > 100 and '<!DOCTYPE' in content:
                print(f"   ✅ index.html exists and valid")
            else:
                print(f"   ⚠️  index.html may be incomplete")
        except:
            print(f"   ❌ index.html not found")
        
        # Check live site
        pages_url = f"https://{GITHUB_USERNAME}.github.io/{repos[0]}"
        print(f"\n   Testing: {pages_url}")
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Site is live")
            else:
                print(f"   ❌ Site returns {response.status_code}")
        except:
            print(f"   ⚠️  Site not accessible yet")
    else:
        print("⚠️  No repositories found. Deploy a test project:")
        print("   python test_instructor_format.py")
except Exception as e:
    print(f"❌ Error checking repos: {e}")

# Summary
print("\n" + "="*60)
print("VALIDATION COMPLETE")
print("="*60)
print("\nIf all checks passed, you're ready!")
print("If any failed, fix them before submission.")
print("\nNext steps:")
print("1. Deploy a test: python test_instructor_format.py")
print("2. Wait 5 minutes")
print("3. Run this validation again")