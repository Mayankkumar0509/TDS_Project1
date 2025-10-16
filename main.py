import os
import asyncio
import base64
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from github import Github, GithubException
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="LLM GitHub Pages Deployment System")

# Configuration
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_PAGES_BASE_URL = os.getenv("GITHUB_PAGES_BASE_URL")

# AI/ML API Configuration (OpenAI-compatible)
AIML_API_KEY = os.getenv("AIML_API_KEY")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://aipipe.org/openai/v1")
AIML_MODEL = os.getenv("AIML_MODEL", "gpt-4o-mini")  # or gpt-4o, claude-3-5-sonnet, etc.

# Initialize GitHub client
github_client = Github(GITHUB_TOKEN)

# Request Models
class Attachment(BaseModel):
    name: str
    url: str  # Changed from data_uri to url

class DeploymentRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str  # Added nonce field
    brief: str
    checks: List[str]
    attachments: List[Attachment]
    evaluation_url: str

# Helper Functions
def decode_data_uri(data_uri: str) -> bytes:
    """Decode a data URI to bytes."""
    if "," not in data_uri:
        raise ValueError("Invalid data URI format")
    header, encoded = data_uri.split(",", 1)
    return base64.b64decode(encoded)

def construct_llm_prompt(request: DeploymentRequest, decoded_files: Dict[str, bytes]) -> str:
    """Build comprehensive prompt for LLM."""
    prompt_parts = [
        "You are an expert web developer creating a single-page application for GitHub Pages.",
        "",
        "## Project Brief",
        request.brief,
        "",
        "## Evaluation Criteria",
        "Your implementation will be checked for:",
    ]
    
    for check in request.checks:
        prompt_parts.append(f"- {check}")
    
    prompt_parts.extend([
        "",
        "## Attached Files",
        "The following files are provided as reference:",
    ])
    
    for filename, content in decoded_files.items():
        try:
            text_content = content.decode('utf-8')
            prompt_parts.append(f"\n### {filename}\n```\n{text_content}\n```")
        except UnicodeDecodeError:
            prompt_parts.append(f"\n### {filename}\n[Binary file: {len(content)} bytes]")
    
    prompt_parts.extend([
        "",
        "## Output Requirements",
        "Generate ALL necessary files for a complete, working application.",
        "",
        "CRITICAL: Format your response EXACTLY like this:",
        "",
        "```filename: index.html",
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>...",
        "",
        "```filename: README.md",
        "# Project Title",
        "...",
        "",
        "IMPORTANT RULES:",
        "1. Each file MUST start with ```filename: <filename>",
        "2. Put the COMPLETE file content after the filename marker",
        "3. End each file with a new ```filename: line or end of response",
        "4. For HTML files, include <!DOCTYPE html> and complete structure",
        "5. NO markdown formatting INSIDE the file contents",
        "6. NO explanatory text between files",
        "",
        "Files to generate:",
        "- index.html (complete, working HTML with embedded CSS/JS or linked files)",
        "- README.md (PROFESSIONAL project documentation - this will be evaluated for quality)",
        "- Any additional CSS/JS files if needed (keep it simple - prefer embedded)",
        "",
        "README.md MUST include:",
        "- Professional project title and description",
        "- Clear feature list",
        "- Usage instructions",
        "- Technical stack details",
        "- Setup/installation steps (if any)",
        "- Live demo link mention",
        "- Professional formatting with proper sections",
        "",
        "Quality requirements:",
        "- Create a fully functional, production-ready application",
        "- Write CLEAN, WELL-COMMENTED code (will be evaluated)",
        "- Follow best practices and coding standards",
        "- The application must work immediately when deployed to GitHub Pages",
        "- Use relative paths for all resources",
        "- Make it visually appealing and responsive",
        "- Ensure all checks from the evaluation criteria are met",
        "- Handle edge cases and errors gracefully",
        "- Include accessibility features (alt text, semantic HTML, ARIA labels)",
    ])
    
    return "\n".join(prompt_parts)

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """Extract files from LLM response with improved parsing."""
    files = {}
    lines = response_text.split("\n")
    current_file = None
    current_content = []
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for filename patterns
        if "```" in line:
            # Check if this line has filename info
            if "filename:" in line.lower() or any(ext in line.lower() for ext in ['.html', '.js', '.css', '.md']):
                # Save previous file
                if current_file and current_content:
                    files[current_file] = "\n".join(current_content).strip()
                    current_content = []
                
                # Extract filename
                parts = line.split("```")
                for part in parts:
                    if "filename:" in part.lower():
                        current_file = part.lower().replace("filename:", "").strip()
                        break
                    elif any(ext in part for ext in ['.html', '.js', '.css', '.md', 'index', 'README', 'LICENSE']):
                        current_file = part.strip()
                        break
                
                in_code_block = True
                i += 1
                continue
            elif line.strip() == "```":
                # End of code block
                if current_file and current_content:
                    files[current_file] = "\n".join(current_content).strip()
                    current_file = None
                    current_content = []
                in_code_block = False
                i += 1
                continue
        
        # Look for file headers like "### index.html" or "**index.html**"
        if any(pattern in line.lower() for pattern in ['index.html', 'readme.md', 'style.css', 'script.js']):
            if not in_code_block and ('###' in line or '**' in line or 'File:' in line):
                if current_file and current_content:
                    files[current_file] = "\n".join(current_content).strip()
                    current_content = []
                
                # Extract filename
                for filename in ['index.html', 'README.md', 'style.css', 'styles.css', 'script.js', 'main.js']:
                    if filename.lower() in line.lower():
                        current_file = filename
                        break
                i += 1
                continue
        
        # Accumulate content
        if current_file and (in_code_block or not line.startswith('#')):
            current_content.append(line)
        
        i += 1
    
    # Save last file if exists
    if current_file and current_content:
        files[current_file] = "\n".join(current_content).strip()
    
    # If no files were parsed, try a more aggressive approach
    if not files and '<!DOCTYPE html>' in response_text or '<html' in response_text:
        # Extract HTML directly
        html_start = response_text.find('<!DOCTYPE html>')
        if html_start == -1:
            html_start = response_text.find('<html')
        if html_start != -1:
            # Find the end of HTML
            html_end = response_text.rfind('</html>') + 7
            if html_end > html_start:
                files['index.html'] = response_text[html_start:html_end].strip()
    
    return files

def decode_data_uri(data_uri: str) -> bytes:
    """Decode a data URI to bytes."""
    if "," not in data_uri:
        raise ValueError("Invalid data URI format")
    header, encoded = data_uri.split(",", 1)
    return base64.b64decode(encoded)

async def generate_code_with_llm(request: DeploymentRequest) -> Dict[str, str]:
    """Use LLM to generate application code."""
    # Decode attachments
    decoded_files = {}
    for attachment in request.attachments:
        decoded_files[attachment.name] = decode_data_uri(attachment.url)
    
    # Build prompt
    prompt = construct_llm_prompt(request, decoded_files)
    # Generate with an OpenAI-compatible chat completions endpoint (AIML_BASE_URL)
    def _call_chat_completion():
        url = f"{AIML_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {AIML_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": AIML_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 8000
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # extract assistant content
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                    return choice["message"]["content"]
                if "text" in choice:
                    return choice["text"]
        # fallback: return full json string
        return json.dumps(data)

    response_text = await asyncio.to_thread(_call_chat_completion)

    # Parse response
    generated_files = parse_llm_response(response_text)
    
    # Ensure we have essential files
    if "index.html" not in generated_files:
        raise ValueError("LLM did not generate index.html")
    if "README.md" not in generated_files:
        generated_files["README.md"] = f"# {request.task}\n\n{request.brief}"
    
    return generated_files

def get_mit_license() -> str:
    """Return MIT License text with proper copyright year."""
    year = time.strftime("%Y")
    return f"""MIT License

Copyright (c) {year} {GITHUB_USERNAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

async def deploy_to_github(task: str, round_num: int, files: Dict[str, str]) -> Dict[str, str]:
    """Deploy files to GitHub and enable Pages."""
    repo_name = f"llm-project-{task}"
    repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
    pages_url = f"{GITHUB_PAGES_BASE_URL.rstrip('/')}/{repo_name}"
    
    user = github_client.get_user()
    
    try:
        if round_num == 1:
            # Create new repository
            repo = await asyncio.to_thread(
                user.create_repo,
                repo_name,
                description=f"LLM-generated project for task {task}",
                private=False,
                auto_init=False
            )
        else:
            # Get existing repository
            repo = await asyncio.to_thread(user.get_repo, repo_name)
        
        # Add LICENSE
        files["LICENSE"] = get_mit_license()
        
        # Commit files
        commit_message = f"Round {round_num}: Deploy LLM-generated application"
        
        for filename, content in files.items():
            try:
                # Try to get existing file
                existing_file = await asyncio.to_thread(
                    repo.get_contents,
                    filename,
                    ref="main"
                )
                # Update existing file
                await asyncio.to_thread(
                    repo.update_file,
                    existing_file.path,
                    commit_message,
                    content,
                    existing_file.sha,
                    branch="main"
                )
            except GithubException:
                # Create new file
                await asyncio.to_thread(
                    repo.create_file,
                    filename,
                    commit_message,
                    content,
                    branch="main"
                )
        
        # Get latest commit SHA
        commits = list(repo.get_commits(sha="main"))
        commit_sha = commits[0].sha if commits else ""
        
        # Enable GitHub Pages using REST API
        try:
            # Use requests directly for Pages API as PyGithub may not have this method
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            pages_data = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            pages_response = await asyncio.to_thread(
                requests.post,
                f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages",
                json=pages_data,
                headers=headers
            )
            if pages_response.status_code not in [201, 409]:  # 201 = created, 409 = already exists
                print(f"Pages activation response: {pages_response.status_code} - {pages_response.text}")
        except Exception as e:
            print(f"Pages activation warning: {e}")
        
        return {
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }
        
    except Exception as e:
        raise Exception(f"GitHub deployment failed: {str(e)}")

async def notify_evaluation_server(evaluation_url: str, payload: Dict[str, Any], max_retries: int = 5):
    """Send notification to evaluation server with exponential backoff."""
    attempt = 0
    
    while attempt < max_retries:
        try:
            response = await asyncio.to_thread(
                requests.post,
                evaluation_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"Successfully notified evaluation server: {response.text}")
                return
            
            print(f"Attempt {attempt + 1} failed with status {response.status_code}")
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")
        
        # Exponential backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        
        attempt += 1
    
    print(f"Failed to notify evaluation server after {max_retries} attempts")

async def process_deployment(request: DeploymentRequest):
    """Main asynchronous processing pipeline."""
    try:
        print(f"Starting deployment for task {request.task}, round {request.round}")
        
        # Generate code with LLM
        print("Generating code with LLM...")
        generated_files = await generate_code_with_llm(request)
        print(f"Generated {len(generated_files)} files")
        
        # Deploy to GitHub
        print("Deploying to GitHub...")
        deployment_info = await deploy_to_github(request.task, request.round, generated_files)
        print(f"Deployed to {deployment_info['pages_url']}")
        
        # Prepare notification payload
        notification_payload = {
            "email": STUDENT_EMAIL,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,  # Include nonce in response
            "repo_url": deployment_info["repo_url"],
            "commit_sha": deployment_info["commit_sha"],
            "pages_url": deployment_info["pages_url"]
        }
        
        # Notify evaluation server
        print("Notifying evaluation server...")
        await notify_evaluation_server(request.evaluation_url, notification_payload)
        
        print(f"Deployment completed successfully for task {request.task}")
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        # In production, you might want to log this to a monitoring service

# API Endpoints
@app.post("/api-endpoint")
async def handle_deployment(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Main endpoint for handling deployment requests."""
    
    # Verify secret
    if request.secret != STUDENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    # Queue asynchronous processing
    background_tasks.add_task(process_deployment, request)
    
    # Immediate response
    return {"status": "processing"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LLM GitHub Pages Deployment"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)