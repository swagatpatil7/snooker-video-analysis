const express = require("express");
const multer = require("multer");
const cors = require("cors");
const { execFile } = require("child_process");
const path = require("path");

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// Multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname);
  }
});

const upload = multer({ storage });

// Upload API
app.post("/api/upload", upload.single("video"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "No video uploaded" });
  }

  const videoPath = path.join(__dirname, "uploads", req.file.filename);
  const pythonScript = path.join(__dirname, "python", "analyze_video.py");

  execFile("python", [pythonScript, videoPath], (error, stdout, stderr) => {
    if (error) {
      console.error("Python error:", error);
      return res.status(500).json({ error: "Python processing failed" });
    }

    try {
      const result = JSON.parse(stdout);
      res.json({
        message: "Video uploaded & analyzed successfully",
        analysis: {
            video: req.file.filename,
            total_frames: result.total_frames
        }
    });
    } catch (err) {
      console.error("JSON parse error:", err);
      res.status(500).json({ error: "Invalid Python output" });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});

app.use("/uploads", express.static("uploads"));
