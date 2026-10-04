# Deploy live (public URL)

## 1. Push to GitHub

Repo root: `Infosys-Springboard-Internship-main/`

Large files are **not** in Git (full CSV, `.env`, 4GB model). The repo includes a **22MB deploy model** and `sample_dataset.csv`.

```bash
git init
git add .
git commit -m "Add medical symptom web app with deploy config"
git branch -M main
git remote add origin https://github.com/sandeep8689/Infosys-Springboard-Internship.git
git push -u origin main
```

**Do not send your GitHub password in chat.** Use one of:

- **GitHub Desktop** — File → Add local repository → Publish repository  
- **Browser login** — when `git push` opens a sign-in window, use your GitHub account  
- **Personal Access Token** — GitHub → Settings → Developer settings → [Fine-grained tokens](https://github.com/settings/tokens?type=beta) → use token as password when Git asks

If the repo `Infosys-Springboard-Internship` does not exist yet, create it on GitHub first (empty repo, no README).

## 2. Render (recommended — free public URL)

1. Sign up at [render.com](https://render.com) with GitHub.
2. **New → Blueprint** → select your repo (Render reads `webapp/render.yaml`).
3. In the service **Environment** tab, add:
   - `GROQ_API_KEY` = your Groq key (do not commit this)
4. Deploy. Your live URL will look like:
   `https://medical-symptom-analysis.onrender.com`

First request after idle may take ~30s (free tier cold start).

## 3. Optional: Groq on production

In Render dashboard → Environment:

| Key | Value |
|-----|--------|
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | your key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |

## 4. Local vs live

| | Local | Live (Render) |
|---|--------|----------------|
| URL | http://localhost:8000 | https://….onrender.com |
| Secrets | `webapp/.env` | Render Environment |

## 5. Re-train full model locally (optional)

Place full CSV in `webapp/data/Diseases_and_Symptoms_dataset.csv` and run:

```bash
python scripts/train_model.py
```

For GitHub/deploy, use the included compact model or:

```bash
python scripts/train_model.py --csv data/sample_dataset.csv --trees 50 --max-depth 20
```
