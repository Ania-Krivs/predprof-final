function commonOptions(title) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: title
      },
      legend: {
        display: true
      },
      zoom: {
        pan: {
          enabled: true,
          mode: "xy"
        },
        zoom: {
          wheel: {
            enabled: true
          },
          pinch: {
            enabled: true
          },
          mode: "xy"
        }
      }
    }
  };
}

export function createLineChart(ctx, labels, data, title, label = "Value") {
  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label,
        data,
        borderColor: "#0d5ea6",
        backgroundColor: "rgba(13, 94, 166, 0.2)",
        fill: true,
        tension: 0.2
      }]
    },
    options: commonOptions(title)
  });
}

export function createBarChart(ctx, labels, data, title, label = "Count") {
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: [
          "#0d5ea6",
          "#1f8b4c",
          "#e67e22",
          "#8e44ad",
          "#c0392b",
          "#16a085",
          "#2c3e50"
        ]
      }]
    },
    options: commonOptions(title)
  });
}

export function bindResetZoom(buttonSelector, chart) {
  const button = document.querySelector(buttonSelector);
  if (!button) {
    return;
  }
  button.addEventListener("click", () => chart.resetZoom());
}
