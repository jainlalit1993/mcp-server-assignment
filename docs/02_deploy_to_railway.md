# Deploy RepoRadar to Railway

In this guide you will put your RepoRadar app on the internet using Railway. By the end, you will have a public web address (URL) that anyone can open, and it will update itself every time you push new code.

## 1. What is Railway?

Railway is a cloud platform that builds and hosts your app straight from your code. You connect your GitHub repository, Railway reads your project, builds it, and runs it on a server it manages for you. You do not have to rent servers, install operating systems, or configure web hosting by hand. You point Railway at your repo, set a few secrets, and it takes care of the rest. Think of it as a friendly robot that turns your code into a live website.

## 2. Before You Start: Push Your Code to GitHub

Railway deploys from a GitHub repository, so your RepoRadar code must already live on GitHub.

If you have not done that yet, follow the previous guide first: **`01_push_to_github.md`**. Come back here once your `reporadar/` project is visible on GitHub.

You should also have these two secrets ready, because you will need them later:

- An `OPENAI_API_KEY` (from your OpenAI account).
- A `GITHUB_TOKEN` (a read-only GitHub Personal Access Token is enough).

Keep them somewhere safe. Never paste secrets into your code or share them publicly.

## 3. Sign Up at Railway With GitHub

1. Open [railway.app](https://railway.app) in your browser.
2. Click **Login** (or **Start a New Project**).
3. Choose **Login with GitHub**.
4. Approve the permissions GitHub asks for.

_Why use GitHub to sign in? It links your account so Railway can see and deploy your repositories._

You now have a Railway account. Next, you will deploy. There are two paths. **Path A** uses the website (easiest for beginners). **Path B** uses the command line. Pick whichever you prefer. You only need one.

## 4. Path A — Deploy From the Dashboard (Recommended)

This path uses only your browser. No commands needed.

### Step 1: Create a New Project

1. On the Railway dashboard, click **New Project**.
2. Choose **Deploy from GitHub repo**.

_What this does: tells Railway you want to build an app directly from a GitHub repository._

### Step 2: Pick the RepoRadar Repo

1. If asked, click **Configure GitHub App** and give Railway access to your repositories.
2. From the list, select your **reporadar** repository.

_What this does: connects that specific repo so Railway can pull your code and build it._

### Step 3: Let Railway Detect the Dockerfile

RepoRadar already includes a `railway.toml` file and a `Dockerfile`. Because of this, Railway automatically knows to build your app using Docker. You do not need to choose a language or framework. Railway reads `railway.toml`, sees `builder = "dockerfile"`, and starts building.

_What this does: Railway builds your multi-stage Docker image (it builds the React UI, installs Python, and creates a slim runtime) all on its own._

Watch the build logs scroll by. The first build can take a few minutes. That is normal. When it finishes, your app is running, but it still needs its secrets and a public address. Continue to Section 6.

## 5. Path B — Deploy With the Railway CLI

Prefer the terminal? Use the Railway CLI instead. (If you already finished Path A, skip this section.)

### Step 1: Install the CLI

```bash
npm i -g @railway/cli
```

_What this does: installs the Railway command-line tool globally so you can run `railway` anywhere._

### Step 2: Log In

```bash
railway login
```

_What this does: opens your browser so you can sign in to Railway and link your terminal to your account._

### Step 3: Create a Project

Run this from inside your `reporadar/` folder:

```bash
railway init
```

_What this does: creates a new Railway project and links it to your current folder._

### Step 4: Deploy Your Code

```bash
railway up
```

_What this does: uploads your project to Railway, which then builds your Dockerfile and starts your app._

## 6. Set Your Environment Variables

Your app needs some secrets and settings to run. These are called **environment variables**. RepoRadar uses six of them:

| Variable | Value |
| --- | --- |
| `OPENAI_API_KEY` | your OpenAI key (required) |
| `GITHUB_TOKEN` | your read-only GitHub PAT (required) |
| `FAST_MODEL` | `gpt-4o-mini` |
| `SMART_MODEL` | `gpt-4o` |
| `GITHUB_MCP_URL` | `https://api.githubcopilot.com/mcp/` |
| `GITHUB_MCP_TRANSPORT` | `streamable_http` |

You can set them in the Dashboard, with the CLI, or both. Pick whichever matches the path you used above.

### Option A: Dashboard Variables Tab

1. Open your project in Railway.
2. Click your service, then open the **Variables** tab.
3. Click **New Variable** and add each name and value from the table above, one at a time.

_What this does: stores your secrets and settings securely so your running app can read them._

### Option B: Railway CLI

Run each command from inside your `reporadar/` folder:

```bash
railway variables --set "OPENAI_API_KEY=your-openai-key-here"
railway variables --set "GITHUB_TOKEN=your-github-token-here"
railway variables --set "FAST_MODEL=gpt-4o-mini"
railway variables --set "SMART_MODEL=gpt-4o"
railway variables --set "GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/"
railway variables --set "GITHUB_MCP_TRANSPORT=streamable_http"
```

_What this does: sets each environment variable on your Railway service from the terminal._

After changing variables, Railway will redeploy your app so the new values take effect. Give it a moment.

## 7. Understanding `railway.toml`

RepoRadar ships with a `railway.toml` file in the repo. This file tells Railway exactly how to build and run your app, so you do not have to click through settings. Here is what it contains:

```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 5
```

Here is what each key means, in plain words:

- **`builder = "dockerfile"`** — Build the app using the `Dockerfile` in the repo (not an auto-detected language).
- **`startCommand`** — The command that starts the app. It runs the FastAPI server and reads the port from `$PORT`, which Railway provides automatically. Never hardcode the port.
- **`healthcheckPath = "/health"`** — After deploying, Railway visits this URL to confirm the app is alive and healthy.
- **`healthcheckTimeout = 300`** — Railway will wait up to 300 seconds (5 minutes) for the app to become healthy before giving up. This gives the app time to start up.
- **`restartPolicyType = "on_failure"`** — If the app crashes, restart it.
- **`restartPolicyMaxRetries = 5`** — Try restarting up to 5 times before stopping.

_Good news: this file is already correct. You do not need to edit it._

## 8. Generate a Public Domain

Right now your app runs, but it has no public address yet. Let's create one.

1. In Railway, open your project and click your service.
2. Go to **Settings**.
3. Find the **Networking** section.
4. Click **Generate Domain**.

_What this does: gives your app a public web address, like `reporadar-production.up.railway.app`, that anyone can open._

Copy the domain Railway gives you. You will use it in the next step.

## 9. Verify Your Deployment

Let's make sure everything works. RepoRadar has a built-in health check.

1. Open a new browser tab.
2. Go to your domain followed by `/health`:

```
https://<your-domain>/health
```

_What this does: asks your app to report its status. Replace `<your-domain>` with the address from Step 8._

You should see a JSON response that looks something like this:

```json
{ "status": "ok", "checks": { ... } }
```

If you see a `status` field, congratulations: your app is live and healthy! You can also open `https://<your-domain>/` to see the RepoRadar web UI itself.

If you see an error instead, check that all six environment variables from Section 6 are set correctly, then look at the deploy logs in the Railway dashboard.

## 10. Auto-Deploy on Every Git Push

Here is the best part. Railway watches your GitHub repository. Every time you push new code to your main branch, Railway automatically rebuilds and redeploys your app. You do not have to do anything special.

```bash
git add .
git commit -m "Update RepoRadar"
git push
```

_What this does: sends your latest code to GitHub, which triggers Railway to build and deploy the new version automatically._

Within a minute or two, your live site reflects your changes. You can watch each deployment happen in the Railway dashboard.

That's it! You have deployed RepoRadar to the cloud, given it a public URL, secured it with environment variables, verified its health, and set up automatic deployments. Nicely done.

*Agentic AI Builder Expert Bootcamp — Batch 4.0*
