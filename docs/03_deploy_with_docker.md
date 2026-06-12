# Run RepoRadar with Docker

In this guide you will package RepoRadar into a single Docker image and run it on your own computer. By the end, you will have the app live at `http://localhost:8000` with no manual setup of Python or Node.

## 1. What is Docker?

Think of Docker as a way to put your whole app — the code, Python, Node, and every setting it needs — into one neat, portable box called an **image**. When you run that image, it becomes a **container**: a tiny, isolated computer that behaves the same on your laptop, your friend's laptop, or a cloud server. No more "but it works on my machine." You build the box once, and it runs anywhere Docker is installed. That is the magic we will use for RepoRadar.

## 2. Prerequisite: Install Docker Desktop

Before anything else, you need Docker installed and running.

1. Download **Docker Desktop** from [docker.com](https://www.docker.com/products/docker-desktop/).
2. Install it like any other app, then open it. Wait until the whale icon shows "Docker Desktop is running."
3. Confirm it works by checking the version.

```bash
docker --version
```
_What this does: prints the installed Docker version, proving Docker is set up correctly._

If you see a version number (for example `Docker version 24.0.0`), you are good to go. If you get an error, make sure Docker Desktop is open and fully started.

## 3. Create your .env file with real keys

The app needs secret keys to talk to OpenAI and GitHub. These live in a file named `.env`. The repo ships with a template called `.env.example` — copy it, then fill in your real values.

Run this from inside the `reporadar/` folder.

```bash
cp .env.example .env
```
_What this does: makes a new `.env` file by copying the example template._

Now open `.env` in a text editor and set the required values:

```bash
OPENAI_API_KEY=sk-your-real-openai-key
GITHUB_TOKEN=ghp-your-read-only-github-token
FAST_MODEL=gpt-4o-mini
SMART_MODEL=gpt-4o
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
GITHUB_MCP_TRANSPORT=streamable_http
```
_What this does: tells RepoRadar which API keys and models to use. `OPENAI_API_KEY` and `GITHUB_TOKEN` are required; a read-only GitHub PAT is enough._

Keep this file private. Never commit `.env` to GitHub.

## 4. Understanding the multi-stage Dockerfile

The repo already includes a **multi-stage** `Dockerfile`. You do not need to edit it, but it helps to know what it does. It builds in three stages:

1. **Build the UI** — uses Node to compile the React + Vite frontend into static files.
2. **Install Python deps** — installs everything from `requirements.txt` for the FastAPI backend.
3. **Slim runtime** — copies only what is needed into a lightweight `python:3.11-slim` image and runs as a **non-root user**.

Why bother with multiple stages? Because the heavy build tools (Node, compilers) stay behind in the early stages and never reach the final image. The result is a **smaller** image that downloads and starts faster, and a **safer** one that runs as a non-root user. The final container serves the built UI at `/` and the API at `/health` and `/review`.

## 5. Build the image

Now turn the project into a Docker image. Run this from the `reporadar/` folder (note the dot at the end — it means "use the current folder").

```bash
docker build -t reporadar .
```
_What this does: reads the `Dockerfile` and builds an image named `reporadar`. The first build takes a few minutes; later builds are faster._

When it finishes, you will see a success message. Your image is ready.

## 6. Run the container

Start the app from your image, passing in the secrets from your `.env` file.

```bash
docker run -p 8000:8000 --env-file .env reporadar
```
_What this does: launches the `reporadar` image, loads your environment variables from `.env`, and connects port 8000 inside the container to port 8000 on your computer._

Leave this terminal window open — it is running the app. You will see startup logs scroll by.

## 7. Open the app in your browser

With the container running, visit these two URLs:

- **The UI:** [http://localhost:8000](http://localhost:8000) — this is the RepoRadar web interface.
- **The health check:** [http://localhost:8000/health](http://localhost:8000/health) — this returns JSON like `{status, checks}`.

If the UI loads and `/health` shows a healthy status, congratulations — RepoRadar is running inside Docker.

## 8. View logs and stop the container

### View the logs

To watch what the app is doing, first find your container, then read its logs.

```bash
docker ps
```
_What this does: lists all running containers, showing each one's ID and name._

```bash
docker logs <id>
```
_What this does: prints the logs for the container with that ID. Replace `<id>` with the real ID from `docker ps` (the first few characters are enough)._

### Stop the container

When you are done, stop the container cleanly.

```bash
docker stop <id>
```
_What this does: gracefully shuts down the running container. Replace `<id>` with the ID from `docker ps`._

You can also stop it by pressing `Ctrl + C` in the terminal where it is running.

## 9. (Optional) Push to Docker Hub

Want to share your image or pull it onto a server? You can publish it to **Docker Hub** (a free public registry). You will need a free Docker Hub account first.

Step 1 — log in:

```bash
docker login
```
_What this does: signs you into Docker Hub from the command line (it will prompt for your username and password)._

Step 2 — tag the image with your Docker Hub username:

```bash
docker tag reporadar <user>/reporadar:latest
```
_What this does: gives your local image a Docker Hub name. Replace `<user>` with your Docker Hub username._

Step 3 — push it up:

```bash
docker push <user>/reporadar:latest
```
_What this does: uploads the tagged image to your Docker Hub account so anyone can pull and run it._

That's it — your image now lives in the cloud, ready to deploy anywhere.

---

You have built a portable image, run RepoRadar in a container, checked its health, read its logs, and even learned how to share it. Nicely done.

*Agentic AI Builder Expert Bootcamp — Batch 4.0*
