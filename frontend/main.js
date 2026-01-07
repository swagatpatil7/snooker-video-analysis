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
      
      // Update dashboard with real data
      if (data.analysis && data.analysis.analysis) {
        updateDashboard(data.analysis.analysis);
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
function updateDashboard(analysis) {
  const stats = document.querySelectorAll(".stat");
  
  if (stats.length >= 4) {
    // Update Player 1 score
    stats[0].innerHTML = `Player 1<br><b>Score: ${analysis.player1?.score || 0}</b>`;
    
    // Update Player 2 score
    stats[1].innerHTML = `Player 2<br><b>Score: ${analysis.player2?.score || 0}</b>`;
    
    // Update Break
    stats[2].innerHTML = `Break<br><b>${analysis.break || 0}</b>`;
    
    // Update Fouls
    stats[3].innerHTML = `Fouls<br><b>${analysis.fouls || 0}</b>`;
  }
  
  console.log("Dashboard updated with:", analysis);
}

console.log("Snooker Video Analyst loaded");