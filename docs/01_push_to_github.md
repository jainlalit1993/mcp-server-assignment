# Push RepoRadar to GitHub

Welcome! In this guide you will put your RepoRadar project onto GitHub for the very first time. By the end, your code will live safely online and you will know how to push future changes. No prior experience needed — we start from the basics.

## 1. Check that Git is installed

Git is the tool that tracks your code and talks to GitHub. Let's make sure you have it.

```bash
git --version
```

_What this does: Prints the installed Git version. If you see a number like `git version 2.43.0`, you are ready._

If you instead see an error like "command not found", you need to install Git first:

- **macOS:** Run `xcode-select --install`, or install from [git-scm.com/download/mac](https://git-scm.com/download/mac).
- **Windows:** Download the installer from [git-scm.com/download/win](https://git-scm.com/download/win) and click through it.
- **Linux (Debian/Ubuntu):** Run `sudo apt-get install git`.

After installing, run `git --version` again to confirm.

## 2. Tell Git who you are (first time only)

Git stamps every save with your name and email. You only need to set this once per computer.

```bash
git config --global user.name "Your Name"
```

_What this does: Sets the name attached to your commits. Replace `Your Name` with your real name._

```bash
git config --global user.email "you@example.com"
```

_What this does: Sets the email attached to your commits. Use the same email as your GitHub account._

## 3. Go to the project folder and start Git

Open your terminal and move into the `reporadar/` folder (the one with `requirements.txt` and `Dockerfile` inside). Then start tracking it with Git.

```bash
git init
```

_What this does: Creates a hidden `.git` folder so Git can start tracking this project. Run this from inside the `reporadar/` folder._

## 4. Confirm the .gitignore is there (and protect your secrets)

Your project already includes a `.gitignore` file. This file tells Git which things to **never** upload — like your local `.env` file (which holds secret keys) and the huge `node_modules/` folder.

```bash
cat .gitignore
```

_What this does: Prints the contents of `.gitignore` so you can confirm it exists and is keeping `.env` and `node_modules/` out._

> **VERY IMPORTANT — never commit your real `.env` file.** It contains secrets like your `OPENAI_API_KEY` and `GITHUB_TOKEN`. Anyone who sees them could misuse your accounts. Only the safe template file, `.env.example`, should ever go to GitHub. The `.gitignore` already blocks the real `.env` — please do not remove that line.

## 5. Stage and make your first commit

A "commit" is a saved snapshot of your project. Let's create the first one.

```bash
git add .
```

_What this does: Stages all your files (everything except what `.gitignore` blocks) so they are ready to be saved._

```bash
git commit -m "Initial commit"
```

_What this does: Saves your staged files as the first snapshot, with the message "Initial commit"._

## 6. Create the repository on GitHub

Now we make a home for your code on GitHub. Pick **one** of the two options below.

### Option A — Use the GitHub website (easiest for beginners)

1. Go to [github.com](https://github.com) and sign in.
2. Click the **+** icon in the top-right corner, then choose **New repository**.
3. Name it `reporadar`.
4. Choose **Public** (or Private if you prefer).
5. **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license." You already have these files locally, and adding them here would cause a conflict.
6. Click **Create repository**.
7. On the next page, copy the repository URL. It looks like `https://github.com/your-username/reporadar.git`.

Then continue to **Step 7** below.

### Option B — Use the GitHub CLI (`gh`)

If you have the `gh` command installed, you can create the repo without leaving the terminal.

```bash
gh auth login
```

_What this does: Logs you into GitHub from the terminal. Follow the prompts (choose GitHub.com, then log in via your browser)._

```bash
gh repo create reporadar --public --source=. --remote=origin
```

_What this does: Creates a public `reporadar` repo on GitHub, links it to your local folder, and names the link `origin`. Because this sets up the remote for you, you can skip Step 7 and go straight to Step 8._

## 7. Connect your local folder to GitHub (Website path only)

If you used **Option A** (the website), tell your local Git where the GitHub repo lives. Replace the URL with the one you copied.

```bash
git remote add origin https://github.com/your-username/reporadar.git
```

_What this does: Links your local project to the GitHub repo and nicknames that link `origin`._

```bash
git branch -M main
```

_What this does: Renames your current branch to `main`, the standard default branch name on GitHub._

## 8. Push your code to GitHub

Time to upload! This sends your commit to GitHub.

```bash
git push -u origin main
```

_What this does: Pushes your `main` branch to `origin` (GitHub). The `-u` flag remembers this connection, so next time you can just type `git push`._

Refresh your repository page on GitHub — your files should now appear. Congratulations, your code is online!

## 9. Push changes later

Every time you edit your project, repeat this simple three-step cycle to save and upload your work.

```bash
git add -A
```

_What this does: Stages every change you made — new files, edits, and deletions._

```bash
git commit -m "Describe what you changed"
```

_What this does: Saves a snapshot with a short message. Write something clear, like "Add health check docs"._

```bash
git push
```

_What this does: Uploads your new commit to GitHub. Thanks to the `-u` flag earlier, you don't need to type the branch name again._

That's it — you now know the full loop. Make changes, `add`, `commit`, and `push`. Great work!

*Agentic AI Builder Expert Bootcamp — Batch 4.0*
