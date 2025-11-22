# 🚀 Ultimate AI Voice Assistant

A powerful AI-based voice assistant that uses **Gemini AI**, **Flask**, and **automation tools** to execute system-level actions, search the web, open apps, control files, and handle chat responses.

---

## 📌 Features

* 🎙️ Voice-to-command processing
* 🧠 Gemini-powered AI command understanding
* ⚙️ Executes PC actions (open apps, browser, music, system control)
* 🖱️ Mouse & keyboard automation (pyautogui)
* 📂 File searching & opening
* 🔋 System status (battery, CPU)
* 🌐 Web automation (YouTube, Google, WhatsApp Web)
* 🛠️ Cross-platform server (Render-compatible)

---

## 📂 Project Structure

```
project/
│
├── server.py          # Flask server with AI + command execution
├── gui.html           # Frontend UI
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

---

## ⚙️ Installation

### Step 1 — Clone Project

```
git clone <repo-url>
cd project
```

### Step 2 — Install Dependencies

```
pip install -r requirements.txt
```

### Step 3 — Add Environment Variables

Create `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

Or on Render dashboard → Environment Variables add:

```
GOOGLE_API_KEY
```

### Step 4 — Run Server Locally

```
python server.py
```

Server will start at:

```
http://localhost:5000
```

---

## 🚀 Deployment (Render.com)

1. Create new **Web Service**
2. Connect GitHub repo
3. Select **Python** environment
4. Build command:

```
pip install -r requirements.txt
```

5. Start command:

```
gunicorn server:app
```

6. Add environment variable:

```
GOOGLE_API_KEY=your_key
```

7. Deploy 🎉

---

## 🧠 AI Flow (Command Processing)

```
User Command → Gemini AI → Server Logic
→ If ACTION → Execute pyautogui / system
→ If CHAT → Simple text reply
```

---

## 🛑 Common Issues

### ❌ API Key Not Working

Cause: `GOOGLE_API_KEY` not set on Render.
Fix: Add key in **Environment → Variables**.

### ❌ Windows Apps Not Opening on Render

Render = Linux → Cannot run Windows commands.
Use Windows client for automation.

---

## 🎯 Future Enhancements

* Desktop client for Windows automation
* WebSocket real-time control
* Authentication
* Offline mode

---

## ❤️ Creator

Made by **Yash Sharma** — AI/ML  Developer.

---

If you want further documentation or diagrams, just tell me! 🚀
