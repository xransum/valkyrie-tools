# DEVELOPMENT

## Requirements

This project uses **pyenv** for managing Python versions and **Poetry** for dependency management.

- Install pyenv: https://github.com/pyenv/pyenv#installation
  - Supported Python versions: `>=3.8,<=3.12`
- Install Poetry: https://python-poetry.org/docs/#installation

Project setup:

```bash
pyenv install <python-version>
pyenv local <python-version>
poetry install
```

## Debugging Safety Vulnerabilities

If Safety reports a vulnerable transitive dependency, use Poetry’s dependency tree to identify what pulls it in:

```bash
poetry show --tree | grep -B 5 marshmallow
poetry show --tree | grep -B 5 filelock
```

Tip: if the grep output is noisy, run `poetry show --tree` alone and search within your terminal.

## Pushing a CR for Changes

### 1. Sync main

```bash
git checkout main
git pull origin main
```

### 2. Create a branch

```bash
git checkout -b <type>/<short-description>
```

Naming conventions:

- `feature/*` – new work
- `bugfix/*` – defects
- `hotfix/*` – production issues

### 3. Make changes and commit

```bash
git status
git add -A
git commit -m "<type>: <summary>"
```

Examples:

- `bugfix: bump filelock to patched version`
- `chore: update safety ignores for dev-only tooling`

### 4. Push the branch

```bash
git push -u origin <type>/<short-description>
```

### 5. Open a PR (GitHub)

Open a Pull Request from your branch into `main` in GitHub.

```
gh pr create --base main --head feature/my-change \
  --title "feat: describe change" \
  --body "Summary:\n- ...\n\nTesting:\n- ..."
```

### 6. Address PR feedback

Make any requested changes, commit them, and push to the same branch. The PR
will update automatically.

```bash
git add -A
git commit -m "fix: address PR feedback"
git push
```
