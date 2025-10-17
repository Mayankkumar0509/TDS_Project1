"""
Test with exact instructor request format
"""
import requests
import json

BASE_URL = "https://tds-project1-8w6g.onrender.com/api-endpoint"
STUDENT_SECRET = "my0509"  # Update to match your .env

def test_exact_format():
    """Test with exact instructor JSON format."""
    print("="*60)
    print("TESTING WITH EXACT INSTRUCTOR FORMAT")
    print("="*60)
    
    # Example 1: Simple hello world
    payload = {
        "email": "student@example.com",
        "secret": STUDENT_SECRET,
        "task": "hello-world-v2",
        "round": 1,
        "nonce": "abc123-test-nonce",
        "brief": "Create a simple hello world page with colorful gradient background",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays Hello World text",
            "Page has gradient background"
        ],
        "evaluation_url": "https://webhook.site/unique-id-here",
        "attachments": []
    }
    
    print("\nTest 1: Simple Hello World")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Request accepted!")
        print("⏳ Check server logs for deployment progress...")
        print(f"🌐 Will be live at: https://Mayankkumar0509.github.io/llm-project-hello-world-v2")
    else:
        print(f"❌ Failed: {response.text}")

def test_captcha_solver_format():
    """Test with captcha solver example from instructor."""
    print("\n" + "="*60)
    print("TESTING CAPTCHA SOLVER FORMAT")
    print("="*60)
    
    # Create a sample image data URI (tiny 1x1 PNG)
    sample_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "email": "student@example.com",
        "secret": STUDENT_SECRET,
        "task": "captcha-solver-001",
        "round": 1,
        "nonce": "captcha-nonce-789",
        "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds"
        ],
        "evaluation_url": "https://webhook.site/unique-id-here",
        "attachments": [
            {
                "name": "sample.png",
                "url": sample_image_data
            }
        ]
    }
    
    print("\nPayload preview:")
    payload_preview = payload.copy()
    payload_preview["attachments"][0]["url"] = payload_preview["attachments"][0]["url"][:50] + "..."
    print(json.dumps(payload_preview, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Request accepted!")
        print("⏳ Check server logs for deployment progress...")
        print(f"🌐 Will be live at: https://Mayankkumar0509.github.io/llm-project-captcha-solver-001")
    else:
        print(f"❌ Failed: {response.text}")

def test_with_multiple_attachments():
    """Test with multiple attachments."""
    print("\n" + "="*60)
    print("TESTING WITH MULTIPLE ATTACHMENTS")
    print("="*60)
    
    # Create sample attachments
    import base64
    
    css_content = "body { font-family: Arial; background: #f0f0f0; }"
    css_data = f"data:text/css;base64,{base64.b64encode(css_content.encode()).decode()}"
    
    json_content = '{"colors": ["red", "blue", "green"]}'
    json_data = f"data:application/json;base64,{base64.b64encode(json_content.encode()).decode()}"
    
    payload = {
        "email": "student@example.com",
        "secret": STUDENT_SECRET,
        "task": "styled-dashboard-v2",
        "round": 1,
        "nonce": "multi-attach-999",
        "brief": "Create a dashboard using the attached CSS for styling and JSON for data.",
        "checks": [
            "Uses attached CSS file",
            "Displays data from JSON",
            "Has professional layout"
        ],
        "evaluation_url": "https://webhook.site/unique-id-here",
        "attachments": [
            {"name": "styles.css", "url": css_data},
            {"name": "data.json", "url": json_data}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Request accepted!")
        print(f"🌐 Will be live at: https://Mayankkumar0509.github.io/llm-project-styled-dashboard-v2")

def test_round_2_exact_format():
    """Test Round 2 with exact format."""
    print("\n" + "="*60)
    print("TESTING ROUND 2 WITH EXACT FORMAT")
    print("="*60)
    
    payload = {
        "email": "student@example.com",
        "secret": STUDENT_SECRET,
        "task": "hello-world-v2",
        "round": 2,
        "nonce": "round2-nonce-111",
        "brief": "Update hello world page: Add current date/time display and animated text.",
        "checks": [
            "Shows current date/time",
            "Text has animation",
            "Previous features still work"
        ],
        "evaluation_url": "https://webhook.site/unique-id-here",
        "attachments": []
    }
    
    print("Updating existing project with Round 2...")
    print()
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Round 2 update queued!")

if __name__ == "__main__":
    print("\n⚙️  SETUP:")
    print("1. Server running: uvicorn main:app --reload")
    print("2. STUDENT_SECRET updated in this file")
    print("3. Webhook URL from https://webhook.site\n")
    
    tests = {
        "1": ("Simple Hello World", test_exact_format),
        "2": ("Captcha Solver (with attachment)", test_captcha_solver_format),
        "3": ("Multiple Attachments", test_with_multiple_attachments),
        "4": ("Round 2 Update", test_round_2_exact_format),
        "5": ("Run All", None)
    }
    
    print("Select test to run:")
    for key, (name, _) in tests.items():
        print(f"{key}. {name}")
    
    choice = input("\nChoice: ")
    
    if choice == "5":
        for key, (name, func) in tests.items():
            if func:
                func()
                print("\n" + "-"*60)
    elif choice in tests and tests[choice][1]:
        tests[choice][1]()
    else:
        print("Invalid choice!")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nCheck:")
    print("1. Server logs in Terminal 1")
    print("2. Your webhook.site URL for notifications")
    print("3. GitHub repos after 2-3 minutes")
    print("4. Live sites after 3-5 minutes")
