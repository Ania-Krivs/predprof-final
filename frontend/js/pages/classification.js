import { classifyCivilization } from "../api.js";
import { mapClassificationResponse } from "../mappers.js";
import { requireAuth, bindLogout } from "../guards.js";
import { setStatus, toggleLoading, formatPercent, setActiveNav } from "../ui.js";
import { createBarChart, bindResetZoom } from "../charts.js";

if (requireAuth()) {
  bindLogout();
  setActiveNav("classification.html");
}

const form = document.querySelector("#classificationForm");
const statusEl = document.querySelector("#status");
const submitBtn = document.querySelector("#submitBtn");
const tableBody = document.querySelector("#predictionsBody");
const resultBox = document.querySelector("#resultBox");
const chartCanvas = document.querySelector("#predictionsChart");

let predictionsChart;

function renderResult(mapped) {
  document.querySelector("#civilization").textContent = mapped.civilization;
  document.querySelector("#confidence").textContent = formatPercent(mapped.confidence);
  document.querySelector("#classId").textContent = String(mapped.classId);

  tableBody.innerHTML = "";
  mapped.predictions.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.label}</td><td>${formatPercent(item.confidence)}</td>`;
    tableBody.appendChild(row);
  });

  if (predictionsChart) {
    predictionsChart.destroy();
  }

  predictionsChart = createBarChart(
    chartCanvas,
    mapped.predictions.map((item) => item.label),
    mapped.predictions.map((item) => item.confidence),
    "Вероятности по всем классам",
    "Confidence"
  );

  bindResetZoom("#resetZoomBtn", predictionsChart);
  resultBox.hidden = false;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const fileInput = document.querySelector("#audio");
  const file = fileInput.files[0];

  if (!file) {
    setStatus(statusEl, "Выберите mp3 файл.", "error");
    return;
  }

  if (!file.name.toLowerCase().endsWith(".mp3")) {
    setStatus(statusEl, "Допустим только формат .mp3", "error");
    return;
  }

  toggleLoading(submitBtn, "Классификация...", "Запустить классификацию", true);
  setStatus(statusEl, "", "");

  try {
    const response = await classifyCivilization(file);
    const mapped = mapClassificationResponse(response);
    renderResult(mapped);
    setStatus(statusEl, "Классификация выполнена успешно.", "success");
  } catch (error) {
    setStatus(statusEl, error.message, "error");
  } finally {
    toggleLoading(submitBtn, "Классификация...", "Запустить классификацию", false);
  }
});
