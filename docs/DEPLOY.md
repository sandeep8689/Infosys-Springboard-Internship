# Deploy live (public URL in Chrome)

Use this guide to host the app on the internet (not only `localhost`). Anyone can open your **https://…onrender.com** link in Chrome.

---

## What goes to GitHub vs what stays private

| In GitHub | Not in GitHub (keep local / Render only) |
|-----------|------------------------------------------|
| Code, notebook, `webapp/`, **compact model** (~24 MB) | `webapp/.env` (Groq key) |
| `sample_dataset.csv` | Full `Diseases_and_Symptoms_dataset.csv` (~46 MB) |

Repo: **https://github.com/sandeep8689/Infosys-Springboard-Internship**

---

## 1. Push latest code to GitHub

From the project folder (where `.git` lives):

```powershell
git add .
git commit -m "Update deploy files"
git push origin main
```

If Git asks you to sign in, use your GitHub account in the browser or a **Personal Access Token** — never share your password in chat.

---

## 2. Deploy on Render (recommended, free tier)

### Option A — Blueprint (uses `render.yaml` at repo root)

1. Go to [render.com](https://render.com) → sign in with **GitHub**.
2. **New → Blueprint**.
3. Connect repo **`Infosys-Springboard-Internship`**.
4. Render reads **`render.yaml`** in the **repo root** (not inside `webapp/`).
5. When prompted, set **`GROQ_API_KEY`** (paste your Groq key).
6. **Apply** and wait for the build (several minutes).

### Option B — Web Service (what you used if Blueprint failed)

1. **New → Web Service** → connect the same GitHub repo.
2. Settings:

| Setting | Value |
|---------|--------|
| **Language / Runtime** | **Docker** |
| **Root Directory** | *(leave empty — repo root)* |
| **Dockerfile Path** | `Dockerfile` |
| **Branch** | `main` |

3. **Environment** → add:

| Key | Value |
|-----|--------|
| `PYTHONPATH` | `/app` |
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | your Groq key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |

4. **Create Web Service** → wait for **Live**.

Your public URL will look like:

`https://infosys-springboard-internship-1.onrender.com`

Open that in **Chrome** on any phone or laptop.

---

## 3. Fix: “open Dockerfile: no such file or directory”

This is the error in your failed deploy screenshot.

**Cause:** Render looked for `Dockerfile` in the **repo root**, but the app used to only have `webapp/Dockerfile`.

**Fix (pick one):**

1. **Pull latest from GitHub** — the repo now includes a **root `Dockerfile`** that builds the web app. On Render: **Manual Deploy → Deploy latest commit**.
2. **Or** in Render → **Settings** → set **Dockerfile Path** to `webapp/Dockerfile` and **Docker context** / root directory so the build context is the `webapp` folder (advanced).

After a successful build, logs should show `pip install` and `uvicorn`, not “no such file or directory”.

---

## 4. After deploy — verify in Chrome

1. Open your `https://….onrender.com` URL.
2. Top badge should say **Model ready** (green).
3. Select symptoms → **Run analysis**.
4. Try **Download PDF** and check the **Analytics** charts.

**Cold start:** On the free plan, the app sleeps when idle. The first visit can take **30–60 seconds**; then it runs normally.

---

## 5. Local vs live

| | Local | Live (Render) |
|---|--------|----------------|
| URL | http://localhost:8000 | https://your-service.onrender.com |
| Groq key | `webapp/.env` | Render → **Environment** |
| Start server | `uvicorn backend.main:app --port 8000` (from `webapp/`) | Render runs Docker automatically |

---

## 6. Re-train model locally (optional)

Full CSV (not on GitHub):

```powershell
cd webapp
python scripts/train_model.py
```

Smaller model for experiments:

```powershell
cd webapp
python scripts/train_model.py --csv data/sample_dataset.csv
```

---

## 7. Troubleshooting

| Problem | What to do |
|---------|------------|
| Build fails: no Dockerfile | Push latest `main` (root `Dockerfile`) and redeploy |
| **Model not ready** on live site | Check build logs; ensure `webapp/artifacts/model.joblib` is in Git |
| 502 / very slow first load | Free tier waking up — wait and refresh |
| LLM notes missing | Set `GROQ_API_KEY` + `LLM_PROVIDER=groq` in Render Environment, redeploy |
| Port error locally | Something else uses port 8000 — stop other terminal or use `--port 8001` |

For internship **Day 10 demo**, use the **live Render URL** in Chrome and keep GitHub as your code + documentation link.
