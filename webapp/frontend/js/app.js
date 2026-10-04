const selected = new Set();
let allSymptoms = [];
let charts = {};

async function api(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

function renderSymptoms(filter = "") {
  const list = document.getElementById("symptomList");
  const q = filter.trim().toLowerCase();
  list.innerHTML = "";
  allSymptoms
    .filter((s) => !q || s.toLowerCase().includes(q))
    .slice(0, 80)
    .forEach((symptom) => {
      const id = `sym-${symptom.replace(/\W/g, "_")}`;
      const wrap = document.createElement("label");
      wrap.innerHTML = `<input type="checkbox" id="${id}" ${
        selected.has(symptom) ? "checked" : ""
      } /> ${symptom}`;
      wrap.querySelector("input").addEventListener("change", (e) => {
        if (e.target.checked) selected.add(symptom);
        else selected.delete(symptom);
        document.getElementById("selectedCount").textContent = selected.size;
      });
      list.appendChild(wrap);
    });
}

function upsertChart(id, type, labels, values, label) {
  const ctx = document.getElementById(id);
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx, {
    type,
    data: {
      labels,
      datasets: [
        {
          label,
          data: values,
          backgroundColor: [
            "#38bdf8",
            "#34d399",
            "#a78bfa",
            "#fbbf24",
            "#f87171",
            "#fb923c",
            "#4ade80",
            "#60a5fa",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: type === "doughnut" } },
      scales: type === "bar" ? { y: { beginAtZero: true } } : {},
    },
  });
}

async function loadAnalytics() {
  const full = await api("/api/analytics/full");
  const diseaseSource =
    Object.keys(full.disease_counts || {}).length > 0
      ? full.disease_counts
      : full.dataset_disease_stats || {};
  const dLabels = Object.keys(diseaseSource).slice(0, 10);
  const dValues = dLabels.map((k) => diseaseSource[k]);
  upsertChart("diseaseChart", "bar", dLabels, dValues, "Disease count");

  const risk = full.risk_distribution || {};
  const rLabels = Object.keys(risk);
  const rValues = rLabels.map((k) => risk[k]);
  upsertChart("riskChart", "doughnut", rLabels.length ? rLabels : ["No data"], rValues.length ? rValues : [1], "Risk");

  const symptoms =
    (full.symptom_trends || []).length > 0
      ? full.symptom_trends
      : (full.dataset_top_symptoms || []).map(([symptom, count]) => ({ symptom, count }));
  if (Array.isArray(full.dataset_top_symptoms) && full.dataset_top_symptoms.length && !symptoms.length) {
    /* legacy */
  }
  let sLabels, sValues;
  if (symptoms.length && symptoms[0].symptom) {
    sLabels = symptoms.map((x) => x.symptom).slice(0, 12);
    sValues = symptoms.map((x) => x.count).slice(0, 12);
  } else if (full.dataset_top_symptoms && !Array.isArray(full.dataset_top_symptoms)) {
    sLabels = Object.keys(full.dataset_top_symptoms).slice(0, 12);
    sValues = sLabels.map((k) => full.dataset_top_symptoms[k]);
  } else {
    sLabels = ["—"];
    sValues = [0];
  }
  upsertChart("symptomChart", "bar", sLabels, sValues, "Symptom trends");
}

async function init() {
  const status = document.getElementById("modelStatus");
  try {
    const health = await api("/api/health");
    if (health.model_ready) {
      status.textContent = "Model ready";
      status.className = "badge badge-ok";
      const { symptoms } = await api("/api/symptoms");
      allSymptoms = symptoms;
      renderSymptoms();
    } else {
      status.textContent = "Train model first";
      status.className = "badge badge-warn";
      document.getElementById("predictBtn").disabled = true;
    }
  } catch {
    status.textContent = "API offline";
    status.className = "badge badge-warn";
  }

  document.getElementById("symptomSearch").addEventListener("input", (e) => {
    renderSymptoms(e.target.value);
  });

  document.getElementById("predictBtn").addEventListener("click", async () => {
    const err = document.getElementById("predictError");
    err.hidden = true;
    if (selected.size === 0) {
      err.textContent = "Select at least one symptom.";
      err.hidden = false;
      return;
    }
    const ageVal = document.getElementById("patientAge").value;
    const body = {
      patient_name: document.getElementById("patientName").value.trim(),
      age: ageVal ? Number(ageVal) : null,
      symptoms: [...selected],
    };
    try {
      const result = await api("/api/predict", { method: "POST", body: JSON.stringify(body) });
      document.getElementById("resultsCard").hidden = false;
      document.getElementById("predDisease").textContent = result.predicted_disease;
      document.getElementById("predConf").textContent = `${(result.confidence * 100).toFixed(1)}%`;
      document.getElementById("predRisk").textContent = result.risk_level;
      document.getElementById("topList").innerHTML = result.top_predictions
        .map((t) => `<li>${t.disease} (${(t.confidence * 100).toFixed(1)}%)</li>`)
        .join("");
      const fill = (id, items) => {
        document.getElementById(id).innerHTML = items.map((i) => `<li>${i}</li>`).join("");
      };
      fill("recPrevent", result.recommendations.preventive_care);
      fill("recLife", result.recommendations.lifestyle_advice);
      fill("recFollow", result.recommendations.follow_up_guidance);
      const llm = document.getElementById("llmSummary");
      if (result.recommendations.llm_summary) {
        llm.textContent = result.recommendations.llm_summary;
        llm.hidden = false;
      } else {
        llm.hidden = true;
      }
      const id = result.consultation_id;
      document.getElementById("pdfLink").href = `/api/reports/${id}/pdf`;
      document.getElementById("excelLink").href = `/api/reports/${id}/excel`;
      await loadAnalytics();
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    }
  });

  try {
    await loadAnalytics();
  } catch {
    /* dashboard optional before first predict */
  }
}

init();
