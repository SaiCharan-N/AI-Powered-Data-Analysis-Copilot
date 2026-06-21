# LLM-Powered Data Analysis Copilot

This project is a full-stack AI data analysis copilot. Users upload CSV files, ask questions in natural language, and receive generated SQL, safely executed query results, charts, ML enrichment, forecasts, and concise AI insights.

## Core Features

- FastAPI backend with modular routes, services, schemas, and utilities
- SQLite database storage through SQLAlchemy
- CSV upload and automatic CSV-to-table ingestion
- Schema introspection with table names, columns, datatypes, sample values, and foreign keys
- Natural-language-to-SQL with LangChain and Groq Llama 3
- SQL self-correction retry loop
- Read-only SQL execution with row limits and timeout protection
- pandas-based query result processing
- ML enrichment with anomaly detection, clustering, and lightweight forecasting
- Chart recommendation and Recharts visualization
- AI insight narration
- React + Vite + Tailwind dashboard frontend

## Main Flow

1. Upload a CSV from the frontend.
2. Backend stores the CSV and writes it into SQLite.
3. Ask a question in natural language.
4. Backend introspects the schema and sends schema context to the LLM.
5. LLM generates SQLite SQL.
6. SQL is validated and executed safely.
7. Results are enriched with ML metadata and forecast data when possible.
8. Chart metadata and AI insights are generated.
9. Frontend renders SQL, insights, chart, ML metadata, and table rows.

## Main Endpoints

- `GET /api/v1/health`
- `POST /api/v1/csv/upload`
- `GET /api/v1/schema`
- `POST /api/v1/query/generate`
- `POST /api/v1/query/run`
