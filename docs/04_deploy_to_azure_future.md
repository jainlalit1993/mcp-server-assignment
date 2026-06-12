# Deploy RepoRadar to Azure (Future / Optional)

> **FUTURE / OPTIONAL — high-level guide.** You do **not** need this to use RepoRadar today. Railway is the main path. Keep this guide for later, when you want to run RepoRadar on Microsoft Azure. The steps below are intentionally high-level, with placeholder names like `<name>` that you fill in.

By the end of this guide you will understand the Azure options for hosting a Docker container, and you will have a high-level recipe for putting RepoRadar on **Azure Container Apps**.

## 1. Your options on Azure (pick one)

Azure has a few ways to run a container. For RepoRadar, **Azure Container Apps** is the recommended choice: it is "serverless containers", meaning Azure runs your Docker image, gives you a public URL, and scales it for you without managing servers. **Azure Container Instances (ACI)** is the simplest way to run a single container quickly, but it has fewer features (no built-in scaling or revisions). **Azure Kubernetes Service (AKS)** is full Kubernetes — very powerful, but overkill unless you are running at large scale and have a team to manage it. Start with Container Apps.

## 2. Before you begin (prerequisites)

You will need a few things ready first.

1. An **Azure account**. A free trial works fine to start.
2. The **Azure CLI** (`az`) installed on your computer.
3. **Docker** installed (so an image of RepoRadar can be built).
4. Your secrets handy: `OPENAI_API_KEY` and `GITHUB_TOKEN`.

Check that the Azure CLI is installed:

```bash
az version
```
_What this does: Prints the installed Azure CLI version, confirming it is ready to use._

## 3. Recommended path: Azure Container Apps

Follow these high-level steps in order. We use the default region **southeastasia** (Singapore) throughout.

### Step 1 — Log in to Azure

```bash
az login
```
_What this does: Opens your browser so you can sign in to your Azure account from the command line._

### Step 2 — Create a resource group

A resource group is just a named folder that holds all your Azure resources together.

```bash
az group create --name <resource-group> --location southeastasia
```
_What this does: Creates a resource group in the Singapore region to hold everything for RepoRadar._

### Step 3 — Create a container registry (ACR)

A container registry is a private home for your Docker image. Azure Container Registry (ACR) is Azure's version.

```bash
az acr create --resource-group <resource-group> --name <registry-name> --sku Basic
```
_What this does: Creates a private Azure Container Registry to store your RepoRadar image._

Then log in to it:

```bash
az acr login --name <registry-name>
```
_What this does: Signs Docker in to your registry so you can push images to it._

### Step 4 — Build and push the image

The easiest way is to let Azure build the image from your Dockerfile in the cloud.

```bash
az acr build --registry <registry-name> --image reporadar:latest .
```
_What this does: Uploads your code, builds the Docker image in Azure, and stores it in your registry as `reporadar:latest`._

Prefer to build locally instead? You can build and push by hand:

```bash
docker build -t <registry-name>.azurecr.io/reporadar:latest .
docker push <registry-name>.azurecr.io/reporadar:latest
```
_What this does: Builds the image on your computer, tags it for your registry, then uploads it to Azure._

### Step 5 — Create the Container Apps environment

An "environment" is the shared space your container app runs inside.

```bash
az containerapp env create --name <env-name> --resource-group <resource-group> --location southeastasia
```
_What this does: Creates the Container Apps environment in Singapore where your app will live._

### Step 6 — Create the container app

This is the main step: it deploys RepoRadar, opens port **8000** to the internet, and sets all the environment variables it needs.

```bash
az containerapp create \
  --name <app-name> \
  --resource-group <resource-group> \
  --environment <env-name> \
  --image <registry-name>.azurecr.io/reporadar:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server <registry-name>.azurecr.io \
  --env-vars \
    OPENAI_API_KEY=<your-openai-key> \
    GITHUB_TOKEN=<your-github-token> \
    FAST_MODEL=gpt-4o-mini \
    SMART_MODEL=gpt-4o \
    GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/ \
    GITHUB_MCP_TRANSPORT=streamable_http
```
_What this does: Deploys RepoRadar as a public container app on port 8000 with all required settings filled in._

A few notes on this command:

- `--target-port 8000` tells Azure which port the app listens on (RepoRadar serves on 8000 inside the container).
- `--ingress external` makes the app reachable from the public internet and gives you a URL.
- The `--env-vars` block matches RepoRadar's `.env.example`. Replace the `<...>` placeholders with your real values.

## 4. Verify it is running (health check)

Once Azure finishes, it gives you a public URL for the app. RepoRadar has a built-in **health check** at the path `/health`. Open it in your browser or check it from the terminal:

```bash
curl https://<your-app-url>/health
```
_What this does: Asks the running app if it is healthy; a JSON response with `status` and `checks` means RepoRadar is live._

If you see that JSON, congratulations — RepoRadar is running on Azure. The web UI is served at `/`, and reviews happen at `/review`.

## 5. A note on regions

This guide used **southeastasia** (Singapore) as the default region everywhere. You can pick a region closer to you, but keep it consistent across the resource group, the environment, and the app so they live near each other.

---

That is the high-level path. When you are ready to go deeper, the official Azure Container Apps docs are the best next stop. For now, you have everything you need to deploy RepoRadar on Azure later. Nice work!

*Agentic AI Builder Expert Bootcamp — Batch 4.0*
