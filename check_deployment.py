"""
Simplified Deployment Checker
Checks what's actually in your deployed GitHub repositories
"""
import os
import requests
from dotenv import load_dotenv
from github import Github

# Load environment
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

def print_header(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_single_repo(repo_name):
    """Check a single repository in detail."""
    print(f"\n{'='*60}")
    print(f"Repository: {repo_name}")
    print(f"{'='*60}\n")
    
    try:
        github = Github(GITHUB_TOKEN)
        user = github.get_user()
        repo = user.get_repo(repo_name)
        
        print(f"📦 Repo URL: {repo.html_url}")
        print(f"🌐 Pages URL: https://{GITHUB_USERNAME}.github.io/{repo_name}\n")
        
        # Get all files in root
        contents = repo.get_contents("")
        
        print("Files in repository:")
        for item in contents:
            size_kb = item.size / 1024
            print(f"  📄 {item.name:30s} {size_kb:8.2f} KB")
        
        # Check LICENSE
        print("\n" + "-"*60)
        print("LICENSE Check:")
        try:
            license_file = repo.get_contents("LICENSE")
            license_content = license_file.decoded_content.decode('utf-8')
            
            if "MIT License" in license_content:
                print("  ✅ MIT LICENSE exists")
            else:
                print("  ⚠️  LICENSE exists but may not be MIT")
                print(f"  Preview: {license_content[:100]}...")
        except:
            print("  ❌ LICENSE file NOT FOUND")
        
        # Check README
        print("\n" + "-"*60)
        print("README.md Check:")
        try:
            readme_file = repo.get_contents("README.md")
            readme_content = readme_file.decoded_content.decode('utf-8')
            length = len(readme_content)
            
            print(f"  ✅ README.md exists ({length} characters)")
            
            # Quality checks
            if "# " in readme_content:
                print("  ✅ Has markdown headers")
            else:
                print("  ⚠️  Missing markdown headers")
            
            if length < 100:
                print("  ⚠️  Seems too short")
            elif length < 500:
                print("  ℹ️  Basic README")
            else:
                print("  ✅ Comprehensive README")
            
            # Show preview
            print("\n  Preview (first 200 chars):")
            print("  " + "-"*56)
            preview = readme_content[:200].replace('\n', '\n  ')
            print(f"  {preview}")
            if length > 200:
                print(f"  ... ({length - 200} more characters)")
            print("  " + "-"*56)
            
        except:
            print("  ❌ README.md NOT FOUND")
        
        # Check index.html
        print("\n" + "-"*60)
        print("index.html Check:")
        try:
            index_file = repo.get_contents("index.html")
            index_content = index_file.decoded_content.decode('utf-8')
            length = len(index_content)
            
            print(f"  ✅ index.html exists ({length} characters)")
            
            # Validate HTML
            if '<!DOCTYPE' in index_content or '<html' in index_content:
                print("  ✅ Valid HTML structure")
            else:
                print("  ❌ Does NOT look like valid HTML")
            
            if '<style' in index_content or '<link' in index_content:
                print("  ✅ Has CSS styling")
            
            if '<script' in index_content:
                print("  ✅ Has JavaScript")
            
            if length < 100:
                print("  ❌ File is too short - likely empty!")
            
            # Show preview
            print("\n  Preview (first 300 chars):")
            print("  " + "-"*56)
            preview = index_content[:300].replace('\n', '\n  ')
            print(f"  {preview}")
            if length > 300:
                print(f"  ... ({length - 300} more characters)")
            print("  " + "-"*56)
            
        except:
            print("  ❌ index.html NOT FOUND")
        
        # Check live site
        print("\n" + "-"*60)
        print("Live Site Check:")
        pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}"
        
        try:
            response = requests.get(pages_url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ Site is LIVE and accessible")
                print(f"  ✅ Returns HTTP 200")
                print(f"  📊 Content size: {len(response.text)} characters")
                
                # Check for issues
                if len(response.text) < 100:
                    print("  ⚠️  Page content seems too short")
                
                if "404" in response.text.lower():
                    print("  ⚠️  Page may contain 404 errors")
                
                if "error" in response.text.lower():
                    print("  ⚠️  Page may contain error messages")
                
            else:
                print(f"  ❌ Site returns HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ⚠️  Site timed out (may still be building)")
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Cannot connect (GitHub Pages may not be enabled)")
        except Exception as e:
            print(f"  ⚠️  Error accessing site: {e}")
        
        print("\n" + "="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking repository: {e}")
        return False

def list_all_repos():
    """List all llm-project-* repositories."""
    print_header("FINDING DEPLOYED REPOSITORIES")
    
    try:
        github = Github(GITHUB_TOKEN)
        user = github.get_user()
        
        all_repos = list(user.get_repos())
        llm_repos = [r.name for r in all_repos if r.name.startswith('llm-project-')]
        
        if not llm_repos:
            print("⚠️  No llm-project-* repositories found")
            print("\n💡 Deploy a test project first:")
            print("   python test_instructor_format.py")
            return []
        
        print(f"\nFound {len(llm_repos)} deployed repositories:\n")
        for i, repo_name in enumerate(llm_repos, 1):
            print(f"  {i}. {repo_name}")
        
        return llm_repos
        
    except Exception as e:
        print(f"❌ Error listing repositories: {e}")
        return []

def main():
    """Main function."""
    print("\n" + "="*60)
    print("  DEPLOYMENT CHECKER")
    print("="*60)
    print("\nThis tool checks your deployed GitHub repositories")
    print("to verify they have the correct structure.\n")
    
    # List all repos
    repos = list_all_repos()
    
    if not repos:
        return
    
    # Menu
    print("\n" + "="*60)
    print("Select an option:")
    print("="*60)
    print("\n1. Check all repositories")
    print("2. Check specific repository")
    print("0. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    
    elif choice == "1":
        # Check all repos
        print_header("CHECKING ALL REPOSITORIES")
        
        for i, repo_name in enumerate(repos, 1):
            print(f"\n[{i}/{len(repos)}] Checking {repo_name}...")
            check_single_repo(repo_name)
            
            if i < len(repos):
                input("\nPress Enter to check next repository...")
    
    elif choice == "2":
        # Check specific repo
        print("\nSelect repository to check:")
        for i, repo_name in enumerate(repos, 1):
            print(f"{i}. {repo_name}")
        
        try:
            idx = int(input("\nChoice: ").strip())
            if 1 <= idx <= len(repos):
                check_single_repo(repos[idx - 1])
            else:
                print("Invalid selection!")
        except:
            print("Invalid input!")
    
    else:
        print("Invalid choice!")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("\n✅ What should be present in each repo:")
    print("  1. LICENSE file (MIT License)")
    print("  2. README.md (professional, comprehensive)")
    print("  3. index.html (valid HTML, proper structure)")
    print("  4. Live site accessible on GitHub Pages")
    print("\n💡 If any files are missing or incorrect:")
    print("  1. Redeploy using: python test_instructor_format.py")
    print("  2. Or update with Round 2: same task, round=2")
    print()

if __name__ == "__main__":
    main()
    