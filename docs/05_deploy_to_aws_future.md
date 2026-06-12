# Deploy RepoRadar to AWS (Future / Optional)

> **Heads up:** This is a **FUTURE / OPTIONAL** guide, and it stays **high-level**. You do **not** need AWS to run RepoRadar. If you are just starting out, use the simpler deployment guides first. Come back here later when you want to host RepoRadar on Amazon Web Services (AWS). The commands below are **illustrative** — they show you the shape of the journey, not a copy-paste script.

By the end of this guide you will understand your AWS hosting options and the high-level steps to deploy RepoRadar's Docker container to AWS using **AWS Copilot**.

## What You Will Achieve

You will learn which AWS service fits RepoRadar, what to install first, and the rough steps to ship the container to the cloud. Take it slow. There is no rush.

## 1. Your Options on AWS (Overview)

AWS gives you several ways to run a container, and RepoRadar is already a Docker container, so you have good choices. **ECS Fargate via AWS Copilot is RECOMMENDED** — it runs "serverless containers," meaning AWS manages the servers for you and you just hand it your Dockerfile, which is the easiest path for a beginner. **AWS Lambda** (using a container image) is a good fit for **light or occasional traffic** because you only pay when a request comes in, though it suits short bursty work more than long-running sessions. **Amazon EKS** (managed Kubernetes) is built for **large scale and many services**, but it is complex and overkill while you are learning — skip it unless you truly need it. For RepoRadar, start with AWS Copilot.

## 2. Prerequisites

Before you begin, make sure you have these ready. Take your time setting each one up.

- An **AWS account** (the sign-up is free; some services cost money once running).
- The **AWS CLI** installed and configured with your credentials.
- **Docker** installed and running on your computer.
- Optionally, the **AWS Copilot CLI** (we install it in the next section).

Check that the AWS CLI is configured:

```bash
aws sts get-caller-identity
```
_What this does: Confirms the AWS CLI can see your account. If it prints your account ID, you are good to go._

```bash
aws configure
```
_What this does: Walks you through setting your AWS access key, secret key, and default region if you have not done so yet._

## 3. Recommended Path: Deploy with AWS Copilot

AWS Copilot turns your Dockerfile into a running service with very few commands. Follow these steps in order.

### Step 1: Install the Copilot CLI

```bash
brew install aws/tap/copilot-cli
```
_What this does: Installs the Copilot CLI on macOS using Homebrew. (On other systems, download the binary from the AWS Copilot website.)_

```bash
copilot --version
```
_What this does: Prints the installed version so you know the install worked._

### Step 2: Initialize Your App and Service

Run this from inside the **reporadar/** folder, where the Dockerfile lives.

```bash
copilot init
```
_What this does: Starts an interactive wizard. When prompted, choose **Load Balanced Web Service**, point it at the **Dockerfile** in this folder, and set the port to **8000**._

When the wizard asks, pick these answers:

- Service type: **Load Balanced Web Service** (gives you a public URL).
- Dockerfile: the **Dockerfile** in the reporadar/ folder.
- Port: **8000** (the port the container listens on).

### Step 3: Store Your Secrets Safely

Never put API keys directly in code or config. Copilot stores them in **AWS Secrets Manager** for you.

```bash
copilot secret init --name OPENAI_API_KEY
```
_What this does: Securely saves your OpenAI API key in AWS Secrets Manager so the running service can read it._

```bash
copilot secret init --name GITHUB_TOKEN
```
_What this does: Securely saves your read-only GitHub token (PAT) the same way._

Then reference those secrets in your service manifest so the container receives them as environment variables. Copilot creates a manifest file at `copilot/<service-name>/manifest.yml`. Add a `secrets:` section like this:

```yaml
secrets:
  OPENAI_API_KEY: OPENAI_API_KEY
  GITHUB_TOKEN: GITHUB_TOKEN
```
_What this does: Tells the service to pull these secrets at startup and expose them as environment variables, without ever printing the values._

### Step 4: Set the Non-Secret Environment Variables

The remaining variables are not secret, so you can put them straight into the same `manifest.yml` under a `variables:` section.

```yaml
variables:
  FAST_MODEL: gpt-4o-mini
  SMART_MODEL: gpt-4o
  GITHUB_MCP_URL: https://api.githubcopilot.com/mcp/
  GITHUB_MCP_TRANSPORT: streamable_http
```
_What this does: Provides RepoRadar's model choices and GitHub MCP settings as plain environment variables for the container._

### Step 5: Set the Health Check Path

RepoRadar exposes a health endpoint at **`/health`**. Point the load balancer at it in `manifest.yml` so AWS knows when the app is ready.

```yaml
http:
  path: '/'
  healthcheck: '/health'
```
_What this does: Serves your app at the root URL and tells the load balancer to check `/health` to confirm the container is healthy._

### Step 6: Deploy

```bash
copilot deploy
```
_What this does: Builds your Docker image, pushes it to AWS, and launches the service. The first run also creates the environment._

For later updates after you change code, you can run:

```bash
copilot svc deploy
```
_What this does: Rebuilds and redeploys just the service with your latest changes._

When it finishes, Copilot prints a public URL. Open it in your browser to see RepoRadar live. 

## 4. Alternative: The Manual ECR Path (Brief)

If you prefer to manage the container image yourself, you can push it to **Amazon ECR** (Elastic Container Registry) and run it later with ECS or Lambda. This is more hands-on, so only use it if you want the extra control.

```bash
aws ecr create-repository --repository-name reporadar
```
_What this does: Creates a private container registry named `reporadar` to hold your Docker images._

```bash
docker build -t reporadar .
```
_What this does: Builds the RepoRadar image from the Dockerfile in the current folder._

```bash
docker tag reporadar:latest <account-id>.dkr.ecr.ap-southeast-1.amazonaws.com/reporadar:latest
```
_What this does: Labels your local image with the full ECR address so it knows where to be pushed. Replace `<account-id>` with your AWS account ID._

```bash
docker push <account-id>.dkr.ecr.ap-southeast-1.amazonaws.com/reporadar:latest
```
_What this does: Uploads the image to your ECR repository, ready for a service to run it._

> Tip: Before pushing, you usually log Docker into ECR with `aws ecr get-login-password`. The AWS docs show the exact one-liner for your account.

## 5. A Note on Region

These examples use **`ap-southeast-1`** (Singapore) as the default region, because it is close and a sensible starting point. You can choose a region nearer to you — just keep it the same across the AWS CLI, Copilot, and ECR so all your resources live together.

## 6. Quick Recap

You learned that **AWS Copilot + ECS Fargate** is the easiest, recommended path, with **Lambda** for light traffic and **EKS** for large scale. You set up prerequisites, stored secrets safely, configured non-secret env vars, pointed the health check at **`/health`**, and deployed. Whenever you are ready to try it for real, the AWS Copilot docs will walk you through each prompt in detail. You have got this.

*Agentic AI Builder Expert Bootcamp — Batch 4.0*
