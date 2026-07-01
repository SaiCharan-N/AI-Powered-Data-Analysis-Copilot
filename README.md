# AI-Powered Data Analysis Copilot using LLMs

A full-stack AI data analysis copilot that lets users upload CSV datasets, ask questions in natural language, and receive generated SQL, safe query results, charts, ML enrichment, forecasts, and concise business insights.

## What This Project Does

- Uploads CSV files and stores them automatically in SQLite
- Reads database schema, column types, sample values, and relationships
- Converts natural language questions into SQLite SQL using LangChain + Groq Llama 3
- Executes only safe read-only SQL queries
- Returns result rows as JSON
- Recommends charts automatically
- Adds ML enrichment:
  - anomaly detection
  - clustering
  - lightweight forecasting
- Generates concise AI insight narration
- Displays everything in a modern React dashboard

## Tech Stack

Backend:
- FastAPI
- SQLite
- SQLAlchemy
- pandas
- scikit-learn
- LangChain
- Groq Llama 3

Frontend:
- React
- Vite
- Tailwind CSS
- Axios
- Recharts
- Monaco Editor

## Folder Structure

```text
New project/
├── app/                         # FastAPI backend
│   ├── api/
│   │   └── routes/              # API endpoints
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic request/response models
│   ├── services/                # Business logic services
│   ├── utils/                   # Shared backend utilities
│   ├── config.py                # Environment-backed settings
│   └── main.py                  # FastAPI app entrypoint
├── src/                         # React frontend
│   ├── api/                     # Axios API client
│   ├── components/              # Dashboard UI components
│   ├── styles/                  # Tailwind CSS entry
│   ├── utils/                   # Frontend helpers
│   ├── App.jsx                  # Main dashboard app
│   └── main.jsx                 # React entrypoint
├── docs/                        # Project notes and source brief
├── data/                        # Local SQLite database, ignored by Git
├── uploads/                     # Uploaded CSV files, ignored by Git
├── .vscode/                     # VS Code tasks/debug config
├── requirements.txt             # Backend dependencies
├── package.json                 # Frontend dependencies/scripts
├── vite.config.js               # Vite config
├── tailwind.config.js           # Tailwind config
├── .env.example                 # Environment variable template
└── README.md
```

## Environment Setup

Create `.env` from the example:

```powershell
copy .env.example .env
```

Then edit `.env` and add your Groq key:

```env
GROQ_API_KEY="your_groq_api_key_here"
```

The frontend also reads this from the same `.env` file:

```env
VITE_API_BASE_URL="http://127.0.0.1:8000"
```

## Run In VS Code

Open the folder in VS Code:

```powershell
cd "C:\Users\HP\Documents\New project"
code .
```

Create and activate the Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
npm install
```

Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in a second terminal:

```powershell
npm run dev -- --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## VS Code Tasks

You can also run these from VS Code:

1. Press `Ctrl + Shift + P`
2. Search `Tasks: Run Task`
3. Choose:
   - `Backend: install dependencies`
   - `Backend: run FastAPI`
   - `Frontend: install dependencies`
   - `Frontend: run Vite`
   - `Build: frontend`

## Main API Endpoints

```text
GET  /api/v1/health
POST /api/v1/csv/upload
GET  /api/v1/schema
POST /api/v1/query/generate
POST /api/v1/query/run
```

## Production Notes

- `.env`, `.venv`, `node_modules`, `dist`, `data`, and `uploads` are ignored by Git.
- Keep secrets out of GitHub.
- For deployment, use a managed database instead of local SQLite if multiple users need access.
- The current forecasting layer is MVP-friendly and uses scikit-learn. Prophet can be added later behind the same response shape.
