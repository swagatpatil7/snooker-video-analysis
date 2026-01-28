// ================= CAMERA ANGLE TOGGLE =================
const angleButtons = document.querySelectorAll(".angle-btn");

angleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    angleButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

// ================= UPLOAD & ANALYSIS =================
const uploadBtn = document.getElementById("uploadBtn");
const statusText = document.getElementById("statusText");
const resultBox = document.getElementById("resultBox");

uploadBtn.addEventListener("click", () => {
  const videoInput = document.getElementById("videoInput");

  if (!videoInput.files.length) {
    alert("Please select a video first");
    return;
  }

  const player1Name = document.getElementById("player1Name").value.trim() || "Player 1";
  const player2Name = document.getElementById("player2Name").value.trim() || "Player 2";

  uploadBtn.disabled = true;
  statusText.innerText = "Uploading & analyzing video...";
  resultBox.innerText = "";

  const formData = new FormData();
  formData.append("video", videoInput.files[0]);

  fetch("http://localhost:5000/api/upload", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      statusText.innerText = data.message || "Analysis complete";

      if (data.analysis) {
        resultBox.innerText = JSON.stringify(data.analysis, null, 2);
      }

      if (data.video) {
        const videoPlayer = document.getElementById("videoPlayer");
        const placeholder = document.getElementById("videoPlaceholder");

        videoPlayer.src = `http://localhost:5000/uploads/${data.video}`;
        videoPlayer.style.display = "block";
        placeholder.style.display = "none";
      }

      if (data.analysis && data.analysis.analysis) {
        updateDashboard(data.analysis.analysis, player1Name, player2Name);
        prepareChartData(data.analysis.analysis, player1Name, player2Name);
      }

      document.getElementById("dashboard").scrollIntoView({ behavior: "smooth" });
    })
    .catch(err => {
      statusText.innerText = "Upload or analysis failed";
      resultBox.innerText = "Error: " + err.message;
    })
    .finally(() => {
      uploadBtn.disabled = false;
    });
});

// ================= DASHBOARD UPDATE =================
function updateDashboard(analysis, player1Name, player2Name) {
  document.getElementById("p1Name").innerText = player1Name;
  document.getElementById("p2Name").innerText = player2Name;

  document.getElementById("p1Score").innerText = analysis.player1?.score || 0;
  document.getElementById("p2Score").innerText = analysis.player2?.score || 0;
  document.getElementById("maxBreak").innerText = analysis.break || 0;
  document.getElementById("totalShots").innerText = analysis.total_shots || 0;
}

// ================= PERFORMANCE CHART LOGIC =================
let performanceChart = null;
let chartLabels = [];
let p1ChartData = [];
let p2ChartData = [];
let p1Label = "Player One";
let p2Label = "Player Two";

function prepareChartData(analysis, player1Name, player2Name) {
  p1Label = player1Name;
  p2Label = player2Name;

  // ✅ X-axis labels: ONLY numbers 1–10
  chartLabels = [1,2,3,4,5,6,7,8,9,10];

  // Dummy accuracy data (replace later with backend values)
  p1ChartData = [20, 28, 35, 42, 50, 58, 65, 72, 78, 84];
  p2ChartData = [15, 22, 30, 38, 45, 52, 60, 66, 72, 78];
}

function renderChart(datasets) {
  const ctx = document.getElementById("performanceChart").getContext("2d");

  if (performanceChart) {
    performanceChart.destroy();
  }

  performanceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: chartLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#f5f5f0" }
        }
      },
      scales: {
        x: {
          ticks: { color: "#c7c7b5" },
          title: {
            display: true,
            text: "Frames",
            color: "#f5f5f0",
            padding: { top: 10 }
          }
        },
        y: {
          min: 20,
          max: 90,
          ticks: { color: "#c7c7b5" },
          beginAtZero: true
        }
      }
    }
  });
}

// ================= CARD CLICK EVENTS =================
document.getElementById("player1Card").addEventListener("click", () => {
  renderChart([
    {
      label: p1Label + " Accuracy %",
      data: p1ChartData,
      borderColor: "#c9a24d",
      tension: 0.4
    }
  ]);
});

document.getElementById("player2Card").addEventListener("click", () => {
  renderChart([
    {
      label: p2Label + " Accuracy %",
      data: p2ChartData,
      borderColor: "#6bbf9c",
      tension: 0.4
    }
  ]);
});

document.getElementById("compareBtn").addEventListener("click", () => {
  renderChart([
    {
      label: p1Label,
      data: p1ChartData,
      borderColor: "#c9a24d",
      tension: 0.4
    },
    {
      label: p2Label,
      data: p2ChartData,
      borderColor: "#6bbf9c",
      tension: 0.4
    }
  ]);
});

console.log("Snooker Video Analyst loaded");