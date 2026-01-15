// Camera angle toggle
const angleButtons = document.querySelectorAll(".angle-btn");

angleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    angleButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

const uploadBtn = document.getElementById("uploadBtn");
const statusText = document.getElementById("statusText");
const resultBox = document.getElementById("resultBox");

uploadBtn.addEventListener("click", () => {
  const videoInput = document.getElementById("videoInput");

  if (!videoInput.files.length) {
    alert("Please select a video first");
    return;
  }

  // Get player names from inputs
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
      console.log("Analysis result:", data);
      
      statusText.innerText = data.message || "Analysis complete";
      
      // Display JSON result
      if (data.analysis) {
        resultBox.innerText = JSON.stringify(data.analysis, null, 2);
      }
      
      // Show uploaded video
      if (data.video) {
        const videoPlayer = document.getElementById("videoPlayer");
        const placeholder = document.getElementById("videoPlaceholder");

        videoPlayer.src = `http://localhost:5000/uploads/${data.video}`;
        videoPlayer.style.display = "block";
        placeholder.style.display = "none";
      }
      
      // Update dashboard with real data and player names
      if (data.analysis && data.analysis.analysis) {
        updateDashboard(data.analysis.analysis, player1Name, player2Name);
      }
      
      // Scroll to dashboard
      document.getElementById("dashboard").scrollIntoView({ behavior: 'smooth' });
    })
    .catch(err => {
      console.error(err);
      statusText.innerText = "Upload or analysis failed";
      resultBox.innerText = "Error: " + err.message;
    })
    .finally(() => {
      uploadBtn.disabled = false;
    });
});

// Function to update dashboard with analysis results
function updateDashboard(analysis, player1Name, player2Name) {
  // Update player names
  document.getElementById("p1Name").innerText = player1Name;
  document.getElementById("p2Name").innerText = player2Name;
  
  // Update scores
  document.getElementById("p1Score").innerText = analysis.player1?.score || 0;
  document.getElementById("p2Score").innerText = analysis.player2?.score || 0;
  document.getElementById("maxBreak").innerText = analysis.break || 0;
  document.getElementById("totalShots").innerText = analysis.total_shots || 0;
  
  console.log("Dashboard updated with:", analysis);
}

console.log("Snooker Video Analyst loaded");