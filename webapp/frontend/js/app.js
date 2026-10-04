const selected = new Set();
let allSymptoms = [];
let charts = {};
let lastConsultationId = null;
let lastReportPayload = null;

const CHART_COLORS = [
  "rgba(45, 212, 191, 0.9)",
  "rgba(56, 189, 248, 0.9)",
  "rgba(167, 139, 250, 0.9)",
  "rgba(251, 191, 36, 0.9)",
  "rgba(251, 113, 133, 0.9)",
  "rgba(74, 222, 128, 0.9)",
  "rgba(251, 146, 60, 0.9)",
  "rgba(96, 165, 250, 0.9)",
];

const chartDefaults = {
  color: "#8ba3b8",
  borderColor: "rgba(148, 163, 184, 0.2)",
};

async function api(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(", ")
      : data.detail;
    throw new Error(detail || res.statusText);
  }
  return data;
}

function truncateLabel(label, max = 22) {
  return label.length > max ? `${label.slice(0, max)}…` : label;
}

function sortEntries(obj) {
  return Object.entries(obj || {}).sort((a, b) => b[1] - a[1]);
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

function upsertChart(id, type, labels, values, label, indexAxis) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  if (charts[id]) charts[id].destroy();

  const safeLabels = labels.map((l) => truncateLabel(String(l)));
  const total = values.reduce((a, b) => a + b, 0);
  const hasData = total > 0;

  charts[id] = new Chart(ctx, {
    type,
    data: {
      labels: hasData ? safeLabels : ["Waiting for data"],
      datasets: [
        {
          label,
          data: hasData ? values : [1],
          backgroundColor: hasData ? CHART_COLORS : ["rgba(100, 116, 139, 0.35)"],
          borderRadius: 6,
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: indexAxis || "x",
      plugins: {
        legend: {
          display: type === "doughnut" && hasData,
          position: "bottom",
          labels: { color: chartDefaults.color, font: { size: 11 }, boxWidth: 12 },
        },
        tooltip: {
          enabled: hasData,
          callbacks: {
            title: (items) => labels[items[0].dataIndex] || items[0].label,
          },
        },
      },
      scales:
        type === "bar" && hasData
          ? {
              x: {
                ticks: { color: chartDefaults.color, maxRotation: 45, minRotation: 0, font: { size: 9 } },
                grid: { color: chartDefaults.borderColor },
              },
              y: {
                beginAtZero: true,
                ticks: { color: chartDefaults.color, precision: 0 },
                grid: { color: chartDefaults.borderColor },
              },
            }
          : {},
    },
  });
}

function normalizeSymptomTrends(full) {
  if ((full.symptom_trends || []).length > 0) {
    return full.symptom_trends;
  }
  const top = full.dataset_top_symptoms;
  if (top && typeof top === "object" && !Array.isArray(top)) {
    return sortEntries(top)
      .map(([symptom, count]) => ({ symptom, count }))
      .slice(0, 12);
  }
  return [];
}

async function loadAnalytics() {
  const full = await api("/api/analytics/full");
  const sessionCount = full.total_consultations ?? 0;
  const symTrends = normalizeSymptomTrends(full);
  const useSessionDisease = Object.keys(full.disease_counts || {}).length > 0;

  document.getElementById("kpiTotal").textContent = sessionCount;
  const avgSev = full.average_severity ?? 0;
  document.getElementById("kpiSeverity").textContent =
    sessionCount > 0 ? `${Number(avgSev).toFixed(1)}` : "—";
  document.getElementById("kpiDiseases").textContent = useSessionDisease
    ? Object.keys(full.disease_counts).length
    : Object.keys(full.dataset_disease_stats || {}).length;
  document.getElementById("kpiSymptoms").textContent =
    symTrends.reduce((a, b) => a + (b.count || 0), 0) || 0;

  const hint = document.getElementById("analyticsHint");
  hint.textContent =
    sessionCount === 0
      ? "Baseline dataset statistics (run an analysis to add live session data)."
      : "Live analytics from your consultations on this server.";

  const diseaseSource = useSessionDisease ? full.disease_counts : full.dataset_disease_stats || {};
  const dEntries = sortEntries(diseaseSource).slice(0, 8);
  upsertChart(
    "diseaseChart",
    "bar",
    dEntries.map(([k]) => k),
    dEntries.map(([, v]) => v),
    useSessionDisease ? "Session diseases" : "Dataset diseases",
    "x"
  );

  const risk = full.risk_distribution || {};
  const rLabels = ["Low", "Medium", "High", "Critical"];
  const rValues = rLabels.map((k) => risk[k] || 0);
  upsertChart("riskChart", "doughnut", rLabels, rValues, "Risk levels");

  const sLabels = symTrends.map((x) => x.symptom).slice(0, 10);
  const sValues = symTrends.map((x) => x.count).slice(0, 10);
  upsertChart(
    "symptomChart",
    "bar",
    sLabels.length ? sLabels : ["—"],
    sValues.length ? sValues : [0],
    "Symptom frequency",
    "y"
  );
}

function setSeverityScore(score) {
  const val = Number(score);
  const el = document.getElementById("predSeverity");
  const fill = document.getElementById("severityFill");
  if (Number.isNaN(val)) {
    el.textContent = "—";
    fill.style.width = "0%";
    return;
  }
  el.textContent = `${val.toFixed(1)} / 100`;
  fill.style.width = `${Math.min(100, Math.max(0, val))}%`;
}

function setRiskBadge(level) {
  const el = document.getElementById("predRisk");
  el.textContent = level;
  el.className = "risk-pill";
  const map = {
    Low: "risk-low",
    Medium: "risk-medium",
    High: "risk-high",
    Critical: "risk-critical",
  };
  el.classList.add(map[level] || "risk-medium");
}

async function saveBlobResponse(res, filename, expectedPrefix) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Download failed (${res.status})`);
  }
  const buffer = await res.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  if (expectedPrefix === "pdf") {
    const head = String.fromCharCode(...bytes.slice(0, 4));
    if (head !== "%PDF") {
      throw new Error("Server did not return a valid PDF. Run analysis again, then download.");
    }
  }
  const blob = new Blob([buffer], {
    type: expectedPrefix === "pdf" ? "application/pdf" : res.headers.get("content-type") || "application/octet-stream",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 500);
}

async function downloadPdfReport() {
  if (!lastReportPayload) {
    throw new Error("Run an analysis first.");
  }
  const res = await fetch("/api/reports/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lastReportPayload),
  });
  const cid = lastReportPayload.consultation_id || "report";
  await saveBlobResponse(res, `MedAssist_report_${cid}.pdf`, "pdf");
}

async function downloadFile(url, filename, expectedPrefix) {
  const res = await fetch(url);
  await saveBlobResponse(res, filename, expectedPrefix);
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
    const btn = document.getElementById("predictBtn");
    btn.disabled = true;
    btn.textContent = "Analyzing…";
    const ageVal = document.getElementById("patientAge").value;
    const body = {
      patient_name: document.getElementById("patientName").value.trim(),
      age: ageVal ? Number(ageVal) : null,
      symptoms: [...selected],
    };
    try {
      const result = await api("/api/predict", { method: "POST", body: JSON.stringify(body) });
      lastConsultationId = result.consultation_id;
      lastReportPayload = {
        patient_name: body.patient_name,
        age: body.age,
        consultation_id: result.consultation_id,
        predicted_disease: result.predicted_disease,
        confidence: result.confidence,
        risk_level: result.risk_level,
        severity_score: result.severity_score,
        symptoms: body.symptoms,
        recommendations: result.recommendations,
      };
      document.getElementById("resultsCard").hidden = false;
      document.getElementById("resultsCard").scrollIntoView({ behavior: "smooth", block: "start" });
      document.getElementById("predDisease").textContent = result.predicted_disease;
      document.getElementById("predConf").textContent = `${(result.confidence * 100).toFixed(1)}%`;
      setRiskBadge(result.risk_level);
      setSeverityScore(result.severity_score);
      document.getElementById("topList").innerHTML = result.top_predictions
        .map((t) => `<li>${t.disease} (${(t.confidence * 100).toFixed(1)}%)</li>`)
        .join("");
      const fill = (id, items) => {
        const el = document.getElementById(id);
        el.innerHTML = (items && items.length)
          ? items.map((i) => `<li>${i}</li>`).join("")
          : "<li>No recommendations — please retry.</li>";
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
      await loadAnalytics();
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.textContent = "Run analysis";
    }
  });

  document.getElementById("pdfBtn").addEventListener("click", async () => {
    if (!lastReportPayload) {
      alert("Run an analysis first to generate a report.");
      return;
    }
    const btn = document.getElementById("pdfBtn");
    btn.disabled = true;
    btn.textContent = "Preparing PDF…";
    try {
      await downloadPdfReport();
    } catch (e) {
      alert(`PDF download failed: ${e.message}`);
    } finally {
      btn.disabled = false;
      btn.textContent = "⬇ Download PDF";
    }
  });

  document.getElementById("excelBtn").addEventListener("click", async () => {
    if (!lastConsultationId) {
      alert("Run an analysis first to generate a report.");
      return;
    }
    const btn = document.getElementById("excelBtn");
    btn.disabled = true;
    try {
      await downloadFile(
        `/api/reports/${lastConsultationId}/excel`,
        `MedAssist_report_${lastConsultationId}.xlsx`,
        "xlsx"
      );
    } catch (e) {
      alert(`Excel download failed: ${e.message}`);
    } finally {
      btn.disabled = false;
    }
  });

  try {
    await loadAnalytics();
  } catch (e) {
    console.warn("Analytics load:", e);
    document.getElementById("analyticsHint").textContent =
      "Could not load analytics. Refresh the page or check the server.";
  }
}

init();
