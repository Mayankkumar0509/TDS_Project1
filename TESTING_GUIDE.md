# Manual Testing Guide

Quick reference for testing the deployment system manually.

## Prerequisites

1. Server is running: `python main.py`
2. Get a webhook URL: https://webhook.site (copy your unique URL)
3. Know your `STUDENT_SECRET` from `.env`

## Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "LLM GitHub Pages Deployment"
}
```

---

## Test 2: Invalid Secret (Should Fail)

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "wrong_secret",
    "task": "test-001",
    "round": 1,
    "brief": "Create a test page",
    "checks": ["Loads correctly"],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

**Expected:** `401 Unauthorized`

---

## Test 3: Simple Hello World (Round 1)

**REPLACE:** `your_secret_here` and webhook URL

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "hello-world",
    "round": 1,
    "brief": "Create a simple HTML page with \"Hello, World!\" in large centered text on a gradient background.",
    "checks": [
      "Page loads without errors",
      "Contains Hello World text",
      "Has proper HTML5 structure"
    ],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

**Expected Response:**
```json
{
  "status": "processing"
}
```

**Check:**
- Response should be immediate (< 1 second)
- Watch server logs for progress
- Wait 2-3 minutes for deployment
- Check your webhook.site for notification
- Visit: `https://your-github-username.github.io/llm-project-hello-world`

---

## Test 4: Calculator App

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "calculator",
    "round": 1,
    "brief": "Create a beautiful calculator with basic operations (+, -, *, /), clear button, responsive grid layout, and modern design.",
    "checks": [
      "All operations work correctly",
      "Clear button resets calculator",
      "Responsive design",
      "No console errors"
    ],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

---

## Test 5: With Attachments

First, create a base64 encoded file:

```bash
# Create a sample CSS file
echo "body { background: linear-gradient(135deg, #667eea, #764ba2); }" | base64
```

Then use in request:

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "styled-page",
    "round": 1,
    "brief": "Create a landing page using the attached CSS file for styling. Add a hero section, features section, and footer.",
    "checks": [
      "Uses attached CSS",
      "All sections present",
      "Responsive design"
    ],
    "attachments": [
      {
        "filename": "styles.css",
        "data_uri": "data:text/css;base64,Ym9keSB7IGJhY2tncm91bmQ6IGxpbmVhci1ncmFkaWVudCgxMzVkZWcsICM2NjdlZWEsICM3NjRiYTIpOyB9Cg=="
      }
    ],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

---

## Test 6: Round 2 Update

**Run this AFTER Test 4 completes (wait 3-5 minutes)**

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "calculator",
    "round": 2,
    "brief": "Update the calculator to add: percentage button (%), square root (√), and a history panel showing last 5 calculations. Keep all existing features.",
    "checks": [
      "New buttons work",
      "History shows calculations",
      "Previous features still work"
    ],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

---

## Test 7: Interactive Game

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "memory-game",
    "round": 1,
    "brief": "Create a memory card matching game: 4x4 grid, cards flip on click, match checking, score counter, timer, win condition, restart button, smooth animations.",
    "checks": [
      "Cards flip properly",
      "Matching logic works",
      "Score and timer update",
      "Win condition triggers",
      "Can restart game"
    ],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

---

## Test 8: Complex Todo App

```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_here",
    "task": "todo-app",
    "round": 1,
    "brief": "Create a feature-rich todo app: add/edit/delete todos, mark complete, filter (all/active/completed), priority levels, due dates, search, localStorage persistence, dark mode, responsive design.",
    "checks": [
      "CRUD operations work",
      "Filtering functions properly",
      "Data persists in localStorage",
      "Dark mode toggles",
      "Responsive layout",
      "No console errors"
    ],
    "attachments": [],
    "evaluation_url": "https://webhook.site/your-unique-id"
  }'
```

---

## Monitoring Deployment

### Watch Server Logs
```bash
# The server will output:
# - "Starting deployment for task..."
# - "Generating code with LLM..."
# - "Generated X files"
# - "Deploying to GitHub..."
# - "Deployed to https://..."
# - "Notifying evaluation server..."
# - "Deployment completed successfully"
```

### Check Webhook
Go to your webhook.site URL to see the notification payload:
```json
{
  "email": "your-email@example.com",
  "task": "hello-world",
  "round": 1,
  "repo_url": "https://github.com/username/llm-project-hello-world",
  "commit_sha": "abc123...",
  "pages_url": "https://username.github.io/llm-project-hello-world"
}
```

### Check GitHub
1. Go to `https://github.com/your-username/llm-project-{task}`
2. Verify files are committed
3. Go to Settings → Pages
4. Confirm Pages is enabled and deployed

### View Live Site
Visit: `https://your-username.github.io/llm-project-{task}`

**Note:** GitHub Pages may take 1-2 minutes to build and deploy.

---

## Troubleshooting

### "Processing" but nothing happens
- Check server terminal for errors
- Verify `.env` variables are correct
- Check GitHub token permissions

### 401 Unauthorized
- Secret doesn't match `.env` file
- Update `your_secret_here` in curl commands

### LLM generation fails
- Check Gemini API key
- Verify API quota
- Try a different model in `.env`

### GitHub errors
- Check token hasn't expired
- Verify `repo` scope enabled
- Ensure username is correct

### Pages not live
- Wait 2-3 minutes for GitHub Pages build
- Check repo Settings → Pages
- Verify repo is public

---

## Quick Reference

| Test | Task Name | What It Tests |
|------|-----------|---------------|
| 1 | N/A | Health check |
| 2 | N/A | Auth failure |
| 3 | hello-world | Simple page, Round 1 |
| 4 | calculator | Interactive app |
| 5 | styled-page | File attachments |
| 6 | calculator | Round 2 updates |
| 7 | memory-game | Game logic |
| 8 | todo-app | Complex app |

---

## Success Criteria

✅ Server responds within 1 second  
✅ Returns `{"status": "processing"}`  
✅ Server logs show progress  
✅ Webhook receives notification in 2-5 minutes  
✅ GitHub repo created with files  
✅ GitHub Pages is live  
✅ Application works as expected
