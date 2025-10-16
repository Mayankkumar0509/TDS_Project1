"""
Test cases for LLM GitHub Pages Deployment System
Run with: pytest test_deployment.py -v
"""
import requests
import json
import base64
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
STUDENT_SECRET = "your_shared_verification_secret_here"  # Update this

def create_data_uri(content: str, mime_type: str = "text/plain") -> str:
    """Create a data URI from string content."""
    encoded = base64.b64encode(content.encode()).decode()
    return f"data:{mime_type};base64,{encoded}"

def test_health_check():
    """Test 1: Health check endpoint."""
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ PASSED")

def test_invalid_secret():
    """Test 2: Request with invalid secret should return 401."""
    print("\n=== Test 2: Invalid Secret ===")
    payload = {
        "email": "test@example.com",
        "secret": "wrong_secret",
        "task": "test-001",
        "round": 1,
        "nonce": "test-nonce-123",
        "brief": "Create a test page",
        "checks": ["Loads correctly"],
        "attachments": [],
        "evaluation_url": "https://webhook.site/test"
    }
    
    # The 'try:' was here. Removing it and fixing indentation below.
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    
    # These lines must be un-indented or indented correctly if a try/except was used.
    # Since we removed 'try:', we un-indent them to be at the correct function level.
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 401
    print("✅ PASSED")

def test_valid_request_immediate_response():
    """Test 3: Valid request should return 200 immediately."""
    print("\n=== Test 3: Valid Request - Immediate Response ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "test-hello-world",
        "round": 1,
        "brief": "Create a simple HTML page that displays 'Hello, World!' in large, centered text with a colorful gradient background.",
        "checks": [
            "Page loads without errors",
            "Contains 'Hello, World!' text",
            "Has proper HTML5 structure"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"  # Replace with your webhook
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    elapsed = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Response time: {elapsed:.3f} seconds")
    
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert elapsed < 2.0  # Should respond in less than 2 seconds
    print("✅ PASSED")
    print("⏳ Background task is now processing...")

def test_calculator_app():
    """Test 4: Request to create a calculator application."""
    print("\n=== Test 4: Calculator Application ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "calculator-app",
        "round": 1,
        "brief": """Create a beautiful, functional calculator web application with the following features:
        - Basic operations: addition, subtraction, multiplication, division
        - Clear button to reset
        - Responsive grid layout
        - Modern design with smooth animations
        - Keyboard support
        - Display shows current calculation
        - No external dependencies (pure HTML/CSS/JS)""",
        "checks": [
            "All basic operations work correctly",
            "Clear button resets the calculator",
            "Display shows numbers as typed",
            "Responsive design works on mobile",
            "No console errors"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_with_attachments():
    """Test 5: Request with file attachments."""
    print("\n=== Test 5: Request with Attachments ===")
    
    # Create sample CSS file attachment
    css_content = """
    body {
        font-family: Arial, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 0;
        padding: 20px;
    }
    .container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    """
    
    # Create sample data file
    data_content = """
    Name,Score,Grade
    Alice,95,A
    Bob,87,B
    Charlie,92,A
    """
    
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "data-dashboard",
        "round": 1,
        "brief": """Create a data dashboard that displays the student scores from the attached CSV file.
        Requirements:
        - Use the attached styles.css for styling
        - Parse and display the CSV data in a beautiful table
        - Add a chart visualization (can use Chart.js from CDN)
        - Show summary statistics (average, highest, lowest)
        - Make it responsive and visually appealing""",
        "checks": [
            "Displays all student data correctly",
            "Shows summary statistics",
            "Includes a chart visualization",
            "Uses the provided CSS styling",
            "Responsive design"
        ],
        "attachments": [
            {
                "filename": "styles.css",
                "data_uri": create_data_uri(css_content, "text/css")
            },
            {
                "filename": "students.csv",
                "data_uri": create_data_uri(data_content, "text/csv")
            }
        ],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_round_2_update():
    """Test 6: Round 2 update to existing repository."""
    print("\n=== Test 6: Round 2 Update ===")
    
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "calculator-app",  # Same task as Test 4
        "round": 2,
        "brief": """Update the calculator application with these improvements:
        - Add a history panel showing last 5 calculations
        - Add percentage button (%)
        - Add square root button (√)
        - Improve the visual design with better colors
        - Add a dark mode toggle
        - Keep all existing functionality""",
        "checks": [
            "History shows last calculations",
            "New buttons work correctly",
            "Dark mode toggles properly",
            "All previous features still work"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_interactive_game():
    """Test 7: Create an interactive game."""
    print("\n=== Test 7: Interactive Game ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "memory-game",
        "round": 1,
        "brief": """Create a memory card matching game with:
        - 4x4 grid of cards (8 pairs)
        - Cards flip on click
        - Match checking logic
        - Score counter showing moves made
        - Timer showing elapsed time
        - Win condition with celebration
        - Restart button
        - Smooth animations
        - Colorful, modern design""",
        "checks": [
            "Cards flip properly",
            "Matching logic works",
            "Score and timer update",
            "Win condition triggers",
            "Game can be restarted",
            "No errors in console"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_portfolio_website():
    """Test 8: Create a portfolio website."""
    print("\n=== Test 8: Portfolio Website ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "portfolio-site",
        "round": 1,
        "brief": """Create a single-page portfolio website with:
        - Hero section with animated background
        - About section with bio
        - Skills section with progress bars
        - Projects section with cards (3 sample projects)
        - Contact section with form
        - Smooth scroll navigation
        - Mobile responsive
        - Modern, professional design
        - Subtle animations on scroll""",
        "checks": [
            "All sections present and styled",
            "Navigation works smoothly",
            "Responsive on mobile",
            "Animations enhance UX",
            "Form has validation",
            "Professional appearance"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_stress_long_brief():
    """Test 9: Stress test with very detailed brief."""
    print("\n=== Test 9: Stress Test - Long Brief ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "todo-app-advanced",
        "round": 1,
        "brief": """Create a feature-rich Todo List application with the following comprehensive requirements:

        CORE FEATURES:
        1. Add new todos with title and optional description
        2. Mark todos as complete/incomplete
        3. Edit existing todos
        4. Delete todos with confirmation
        5. Filter todos by: All, Active, Completed
        6. Sort todos by: Date added, Alphabetical, Priority
        7. Priority levels: High, Medium, Low (with color coding)
        8. Due dates with calendar picker
        9. Search functionality to find todos
        10. Clear all completed todos button

        UI/UX REQUIREMENTS:
        - Clean, modern Material Design inspired interface
        - Responsive layout (mobile, tablet, desktop)
        - Smooth animations for add/remove/complete actions
        - Drag and drop to reorder todos
        - Keyboard shortcuts (Enter to add, Escape to cancel edit)
        - Empty state message when no todos
        - Toast notifications for actions
        - Dark mode toggle
        - Loading states for async operations

        DATA PERSISTENCE:
        - Use localStorage to persist todos
        - Auto-save on every change
        - Load saved todos on page load
        - Export todos as JSON
        - Import todos from JSON file

        TECHNICAL REQUIREMENTS:
        - Pure vanilla JavaScript (no frameworks)
        - Semantic HTML5
        - CSS Grid/Flexbox for layout
        - CSS custom properties for theming
        - No external dependencies except CDN icons (optional)
        - Well-commented code
        - Modular function structure
        - Error handling for edge cases

        BONUS FEATURES:
        - Statistics dashboard (total, completed, pending)
        - Category/tags for todos
        - Recurring todos
        - Undo last action
        - Bulk operations (select multiple)""",
        "checks": [
            "All core features implemented",
            "UI is polished and responsive",
            "Data persists across sessions",
            "No console errors",
            "Smooth animations",
            "Keyboard shortcuts work",
            "Dark mode functions properly",
            "Code is well-structured"
        ],
        "attachments": [],
        "evaluation_url": "https://webhook.site/unique-id-here"
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ PASSED")

def test_missing_fields():
    """Test 10: Request with missing required fields."""
    print("\n=== Test 10: Missing Required Fields ===")
    payload = {
        "email": "23f1003168@ds.study.iitm.ac.in",
        "secret": STUDENT_SECRET,
        "task": "test-incomplete"
        # Missing: round, brief, checks, attachments, evaluation_url
    }
    
    response = requests.post(f"{BASE_URL}/api-endpoint", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 422  # Validation error
    print("✅ PASSED")

def run_all_tests():
    """Run all test cases."""
    print("=" * 60)
    print("LLM GITHUB PAGES DEPLOYMENT - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_health_check,
        test_invalid_secret,
        test_valid_request_immediate_response,
        test_calculator_app,
        test_with_attachments,
        test_interactive_game,
        test_portfolio_website,
        test_stress_long_brief,
        test_missing_fields,
        test_round_2_update,  # Now enabled!
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")

if __name__ == "__main__":
    print("\n⚙️  SETUP INSTRUCTIONS:")
    print("1. Make sure the FastAPI server is running (python main.py)")
    print("2. Update STUDENT_SECRET in this file to match your .env")
    print("3. Update evaluation_url to a real webhook (https://webhook.site)")
    print("4. Run: python test_deployment.py\n")
    
    input("Press Enter to start tests...")
    run_all_tests()