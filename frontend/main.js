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
      statusText.innerText = data.message || "Analysis complete";
  // Show uploaded video
      if (data.analysis && data.analysis.video) {
        const videoPlayer = document.getElementById("videoPlayer");
        const placeholder = document.getElementById("videoPlaceholder");

        videoPlayer.src = `http://localhost:5000/uploads/${data.analysis.video}`;
        videoPlayer.style.display = "block";
        placeholder.style.display = "none";
      }
    })
    .catch(err => {
      console.error(err);
      statusText.innerText = "Upload or analysis failed";
    })
    .finally(() => {
      uploadBtn.disabled = false;
    });
});

console.log("Snooker Video Analyst loaded");
