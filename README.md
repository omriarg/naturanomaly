
# 🧠 NaturaAnomaly Detection System

This project combines real-time YOLO object detection with LLM-based reasoning (via Ollama) to enable natural language querying of surveillance data. Users can ask complex questions like:

> "What happened in this region yesterday?"  
> "Why is this object unusual?"  
> "Show me all detected trucks this week"

## 🗂 Project Structure

```
code/
├── backend/              # Django-based API with Ollama, ChromaDB, and pandas
├── frontend/
│   └── naturalAnomaly/   # React frontend for user interaction & table/heatmap display
```

---

## ⚙️ Backend Setup (Python + Django)

1. Open a terminal and navigate to the backend directory:

   ```bash
   cd code/backend
   ```

2. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Django development server:

   ```bash
   python manage.py runserver
   ```

This will start the API at: `http://127.0.0.1:8000/`

---

## 🌐 Frontend Setup (React JS + Vite)

1. Open a new terminal tab and go to the frontend directory:

   ```bash
   cd code/frontend/naturalAnomaly
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Run the development server:

   ```bash
   npm run dev
   ```

This will start the frontend (usually at `http://localhost:3000`) which will connect to your backend API.

---

## ✅ Features

- 🔎 Ask natural questions, get structured SQL-backed answers  
- 📊 Dynamic tables rendered from pandas DataFrames  
- 🧠 LLM Tool Calls (SQL, image, and explanation) via Ollama  
- 📍 ROI heatmap anomaly detection  
- 🎥 YOLO-based video object tracking & event logs

---

## 🧪 Requirements

- Python 3.9+  
- Node.js 18+  
- Ollama installed with LLaMA 3 (e.g., `ollama run llama3`)  
- ChromeDB / pandas / Django REST Framework
