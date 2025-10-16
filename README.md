# LLM GitHub Pages Deployment System

Automated deployment system that uses LLM to generate code and deploys it to GitHub Pages.

## Features

- ✅ FastAPI-based REST API
- ✅ Asynchronous processing with background tasks
- ✅ Google Gemini LLM integration for code generation
- ✅ GitHub API integration for repository management
- ✅ Automatic GitHub Pages activation
- ✅ Exponential backoff retry mechanism
- ✅ Data URI attachment decoding
- ✅ Round 1 (create) and Round 2 (update) support

## Prerequisites

1. **Python 3.8+**
2. **GitHub Personal Access Token** with `repo` scope
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (Full control of private repositories)
   - Copy the token (starts with `ghp_`)

3. **Google Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Create a new API key
   - Copy the key

## Installation

1. **Clone or create the project directory:**
```bash
mkdir llm-deployment-system
cd llm-deployment-system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in all required values:

```bash
# Student Configuration
STUDENT_SECRET="your_shared_verification_secret_here"
STUDENT_EMAIL="your.email@example.com"

# GitHub Configuration
GITHUB_TOKEN="ghp_your_token_here"
GITHUB_USERNAME="your-github-username"
GITHUB_PAGES_BASE_URL="https://your-github-username.github.io/"

# LLM Configuration
LLM_API_KEY="your_gemini_api_key_here"
LLM_MODEL="gemini-2.0-flash-exp"
```

## Running the Application

### Development Mode

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### POST /api-endpoint

Main deployment endpoint that accepts instructor requests.

**Request Body:**
```json
{
  "email": "instructor@example.com",
  "secret": "shared_verification_secret",
  "task": "task-001",
  "round": 1,
  "brief": "Create a simple calculator app...",
  "checks": [
    "Application loads without errors",
    "UI is responsive",
    "All functions work correctly"
  ],
  "attachments": [
    {
      "filename": "design.png",
      "data_uri": "data:image/png;base64,iVBORw0KG..."
    }
  ],
  "evaluation_url": "https://evaluator.example.com/submit"
}
```

**Response:**
```json
{
  "status": "processing"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "LLM GitHub Pages Deployment"
}
```

## How It Works

1. **Request Received**: API receives POST request with task details
2. **Secret Verification**: Validates the shared secret
3. **Immediate Response**: Returns 200 OK immediately
4. **Background Processing**:
   - Decodes all attachment data URIs
   - Constructs comprehensive prompt for LLM
   - Generates code using Google Gemini
   - Parses LLM response to extract files
   - Creates/updates GitHub repository
   - Commits all files (including LICENSE)
   - Enables GitHub Pages
   - Notifies evaluation server with retry logic

## Workflow

### Round 1 (Initial Creation)
1. Creates new public repository: `llm-project-{task}`
2. Generates fresh code based on brief
3. Commits all files including LICENSE
4. Enables GitHub Pages
5. Notifies evaluation server

### Round 2 (Update)
1. Clones existing repository
2. Generates updated code based on new brief
3. Updates files via GitHub API
4. Commits changes
5. Notifies evaluation server

## Error Handling

- **Invalid Secret**: Returns 401 Unauthorized
- **LLM Errors**: Logged and processing continues
- **GitHub Errors**: Detailed error messages logged
- **Notification Failures**: Automatic retry with exponential backoff (max 5 attempts)

## Notification Retry Logic

The system implements exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Attempt 4: Wait 4 seconds
- Attempt 5: Wait 8 seconds

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit the `.env` file to version control
- Add `.env` to `.gitignore`
- Keep your API keys and tokens secure
- Use environment-specific secrets in production

## Troubleshooting

### "Invalid secret" error
- Verify `STUDENT_SECRET` matches the instructor's secret

### GitHub API errors
- Check token permissions (needs `repo` scope)
- Verify `GITHUB_USERNAME` is correct
- Ensure token hasn't expired

### LLM generation fails
- Verify `LLM_API_KEY` is valid
- Check API quota limits
- Try a different model if needed

### Pages not activating
- Wait 1-2 minutes for GitHub Pages to build
- Check repository settings manually
- Verify repository is public

## Testing

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Test deployment (replace with actual values):
```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret",
    "task": "test-001",
    "round": 1,
    "brief": "Create a simple hello world page",
    "checks": ["Loads correctly"],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-url"
  }'
```

## File Structure

```
.
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (DO NOT COMMIT)
├── .env.example         # Environment template
├── README.md           # This file
└── .gitignore          # Git ignore file
```

## License

Generated projects are deployed with MIT License.

## Support

For issues or questions, check the logs output by the application for detailed error messages.