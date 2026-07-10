# Contributing to NextMove

Thank you for helping improve NextMove. Keep changes focused, tested, and easy
to review.

## Development setup

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Backend

Create and activate a Python 3.13 virtual environment, then install the
development dependencies:

```bash
cd backend
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

## Quality checks

Run these checks before opening a pull request:

```bash
npm --prefix frontend run lint
npm --prefix frontend run format:check
ruff check backend
cd backend
python -m unittest discover -s tests -v
cd ..
```

Activate the backend virtual environment so `ruff` is available, then install
the repository hooks once per clone:

```bash
pre-commit install
```

You can run every configured hook manually with:

```bash
pre-commit run --all-files
```

## Pull requests

- Keep each pull request limited to one clear concern.
- Add or update tests when behavior changes.
- Do not commit secrets, local environment files, uploaded resumes, build
  output, or virtual environments.
- Confirm that frontend and backend checks pass locally.
- Describe what changed, why it changed, and how it was verified.
