# MyDesk

A Flask notes manager configured for Vercel's Python runtime.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Deploying to Vercel

1. Import the GitHub repository in Vercel.
2. Keep the framework preset as Other.
3. Add a `SECRET_KEY` environment variable in Vercel.
4. Deploy.

By default, Vercel uses `/tmp` for SQLite and file uploads. That is fine for a demo, but the data can reset between serverless instances. For a real production app, add a hosted database and set `DATABASE_URL`.
