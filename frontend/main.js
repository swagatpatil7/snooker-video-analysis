// Camera angle toggle
const angleButtons = document.querySelectorAll(".angle-btn");

angleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    angleButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

// Placeholder for future backend integration
console.log("Snooker Video Analyst loaded");
