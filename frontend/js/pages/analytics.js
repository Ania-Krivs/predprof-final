import { getAnalyticsSummary } from "../api.js";
import { requireAuth, bindLogout } from "../guards.js";
import { setActiveNav, setStatus } from "../ui.js";
import { analyticsMock } from "../mocks.js";
import { createLineChart, createBarChart, bindResetZoom } from "../charts.js";

if (requireAuth()) {
  bindLogout();
  setActiveNav("analytics.html");
}

const statusEl = document.querySelector("#status");

function renderAnalytics(data) {
  const chart1 = createLineChart(
    document.querySelector("#accuracyEpochsChart"),
    data.epochs_accuracy.map((x) => x.epoch),
    data.epochs_accuracy.map((x) => x.accuracy),
    "Точность на валидации по эпохам",
    "Accuracy"
  );

  const trainLabels = Object.keys(data.train_class_distribution);
  const trainValues = Object.values(data.train_class_distribution);
  const chart2 = createBarChart(
    document.querySelector("#trainDistributionChart"),
    trainLabels,
    trainValues,
    "Распределение train по классам",
    "Count"
  );

  const chart3 = createBarChart(
    document.querySelector("#testAccuracyChart"),
    data.test_record_accuracy.map((x) => `#${x.record}`),
    data.test_record_accuracy.map((x) => x.accuracy),
    "Точность по каждой записи теста",
    "Accuracy"
  );

  const topLabels = Object.keys(data.valid_top_5_classes);
  const topValues = Object.values(data.valid_top_5_classes);
  const chart4 = createBarChart(
    document.querySelector("#topClassesChart"),
    topLabels,
    topValues,
    "Top-5 классов в валидации",
    "Count"
  );

  bindResetZoom("#resetZoom1", chart1);
  bindResetZoom("#resetZoom2", chart2);
  bindResetZoom("#resetZoom3", chart3);
  bindResetZoom("#resetZoom4", chart4);
}

(async function init() {
  try {
    const data = await getAnalyticsSummary();
    renderAnalytics(data);
    setStatus(statusEl, "Данные загружены из backend API.", "success");
  } catch {
    renderAnalytics(analyticsMock);
    setStatus(statusEl, "Используются mock-данные (endpoint /api/analytics/summary недоступен).", "error");
  }
})();
