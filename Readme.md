# Infosys Springboard Internship — AI Medical Symptom Analysis

## Week 1 (notebook)

Colab notebook: `AI_Medical_Symptom_Analysis_&_Disease_Prediction_System.ipynb`

- Data loading & EDA on `Diseases_and_Symptoms_dataset.csv`
- Random Forest classifier (~87% accuracy on 100 diseases)

## Week 2 (web application)

Full stack under **`webapp/`**:

- **Day 6** — Treatment recommendations (preventive / lifestyle / follow-up) from disease + risk
- **Day 7** — Patient health reports (PDF & Excel download)
- **Day 8** — Analytics dashboard (Chart.js: symptoms, diseases, risk)
- **Day 9–10** — Integrated API + UI, Docker, deployment notes

See **[docs/WEEK2.md](docs/WEEK2.md)** for setup, LLM API keys, Docker, and demo flow.

### Quick start

```bash
cd webapp
pip install -r requirements.txt
# Place CSV in webapp/data/Diseases_and_Symptoms_dataset.csv
python scripts/train_model.py
set PYTHONPATH=.
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000

### Live deployment (public URL)

See **[docs/DEPLOY.md](docs/DEPLOY.md)** — push to GitHub, then deploy on **Render** for a free live link (e.g. `https://your-app.onrender.com`).
