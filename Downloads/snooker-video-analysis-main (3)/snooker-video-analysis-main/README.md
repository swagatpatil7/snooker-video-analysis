## 📌 Frontend – Snooker Video Analysis

### 📖 Overview

This folder contains the **frontend (UI/UX)** of the *Snooker Video Analysis* web application.
The frontend is responsible for presenting the user interface, handling user interactions, and communicating with the backend APIs.

---

### 🎯 Purpose

* Provide a clean and interactive interface for users
* Allow users to view snooker match analysis visually
* Display analytics such as shots, scores, and timelines

---

### 🛠️ Technologies Used

* **HTML5** – Page structure
* **CSS3** – Styling and layout
* **JavaScript** – Client-side logic and interactivity

---

### 📂 Folder Structure

```
snooker-video-analysis/
├── backend/
│   ├── server.js              # Node.js + Express backend API
│   ├── package.json           # Backend dependencies
│   ├── package-lock.json
│   ├── uploads/               # Uploaded snooker videos (ignored in git)
│   └── python/
│       └── analyze_video.py   # Python OpenCV analysis script
│
├── frontend/
│   ├── index.html             # Main UI page
│   ├── style.css              # UI styling
│   ├── main.js                # Frontend logic (upload, results)
│   └── snooker_image.jpg      # UI image asset
│
├── .gitignore                 # Ignore node_modules, uploads, env files
└── README.md                  # Project documentation

```

---

### 🖥️ Pages / Features

* Landing page with project introduction
* Visual layout inspired by Figma UI prototype
* Responsive and user-friendly design
* Placeholder sections for analytics and video output

---

### 🔗 Backend Integration (Planned)

* Frontend will communicate with a **Python Flask backend**
* APIs will be used to:

  * Upload snooker videos
  * Fetch analysis results
  * Display statistics and insights

---

### 🚧 Current Status

* ✅ UI structure completed
* ✅ Styling and layout implemented
* 🔄 Backend integration in progress

---

### 👨‍💻 Developed By

Snooker Video Analysis – Group 'L' Project

---
