import { useMemo, useState } from "react";
import { Clock3, DatabaseZap, LineChart, Sparkles } from "lucide-react";

import ChartRenderer from "./components/ChartRenderer.jsx";
import DataTable from "./components/DataTable.jsx";
import InsightCard from "./components/InsightCard.jsx";
import QueryInput from "./components/QueryInput.jsx";
import Sidebar from "./components/Sidebar.jsx";
import SqlCard from "./components/SqlCard.jsx";
import UploadPanel from "./components/UploadPanel.jsx";
import { runQuery, uploadCsv } from "./api/client.js";
import { getErrorMessage } from "./utils/formatters.js";

function formatTimestamp(date = new Date()) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short",
  }).format(date);
}

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [question, setQuestion] = useState("");
  const [queryState, setQueryState] = useState({ loading: false, error: "", result: null });
  const [uploadState, setUploadState] = useState({ loading: false, error: "", dataset: null });
  const [history, setHistory] = useState([]);

  const appClassName = darkMode ? "dark" : "";
  const result = queryState.result;

  const stats = useMemo(() => {
    if (!result) {
      return [
        ["Rows", "0", "Records returned"],
        ["Columns", "0", "Fields available"],
        ["Chart", "None", "Recommended visual"],
      ];
    }

    return [
      ["Rows", result.row_count, "Records returned"],
      ["Columns", result.columns?.length || 0, "Fields available"],
      ["Chart", result.visualization?.chart_type || "table", "Recommended visual"],
    ];
  }, [result]);

  async function handleUpload(file) {
    setUploadState({ loading: true, error: "", dataset: null });
    try {
      const dataset = await uploadCsv(file);
      setUploadState({ loading: false, error: "", dataset });
    } catch (error) {
      setUploadState({ loading: false, error: getErrorMessage(error), dataset: null });
    }
  }

  async function handleQuerySubmit(event) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      return;
    }

    setQueryState((state) => ({ ...state, loading: true, error: "" }));
    try {
      const data = await runQuery(trimmedQuestion);
      const executedAt = formatTimestamp();
      setQueryState({ loading: false, error: "", result: { ...data, executedAt } });
      setHistory((items) => [
        {
          id: `${Date.now()}`,
          question: trimmedQuestion,
          rowCount: data.row_count,
          executedAt,
        },
        ...items.slice(0, 7),
      ]);
    } catch (error) {
      setQueryState((state) => ({
        ...state,
        loading: false,
        error: getErrorMessage(error),
      }));
    }
  }

  return (
    <div className={appClassName}>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dffaf3,transparent_34%),linear-gradient(180deg,#f8fafc,#eef2f7)] text-slate-950 transition-colors duration-300 dark:bg-[radial-gradient(circle_at_top_left,rgba(20,184,166,0.14),transparent_32%),linear-gradient(180deg,#020617,#0f172a)] dark:text-white">
        <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[280px_1fr]">
          <div className="hidden lg:block">
            <Sidebar
              activeResult={result}
              darkMode={darkMode}
              history={history}
              onToggleDarkMode={() => setDarkMode((value) => !value)}
            />
          </div>

          <main className="min-w-0 px-4 py-5 sm:px-6 lg:px-8">
            <header className="mb-6 rounded-lg border border-white/70 bg-white/80 p-5 shadow-soft backdrop-blur dark:border-slate-800/80 dark:bg-slate-950/80">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex items-start gap-4">
                  <div className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-slate-950 text-white shadow-lg dark:bg-teal-400 dark:text-slate-950">
                    <Sparkles size={22} />
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-teal-700 dark:text-teal-300">
                      AI Data Analysis Copilot
                    </p>
                    <h1 className="mt-2 text-2xl font-semibold tracking-normal text-slate-950 dark:text-white sm:text-3xl">
                      Ask questions, inspect results, act on insights.
                    </h1>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">
                      Upload CSV data, generate SQL, review charts, and surface ML-backed business observations from one focused workspace.
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    Backend connected
                  </span>
                  {result?.executedAt && (
                    <span className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600 dark:bg-slate-900 dark:text-slate-300">
                      <Clock3 size={13} />
                      Last run {result.executedAt}
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-4 flex justify-end lg:hidden">
                <button
                  className="inline-flex w-fit items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
                  onClick={() => setDarkMode((value) => !value)}
                  type="button"
                >
                  {darkMode ? "Light mode" : "Dark mode"}
                </button>
              </div>
            </header>

            <section className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
              {stats.map(([label, value, caption]) => (
                <div
                  className="rounded-lg border border-white/80 bg-white/85 p-4 shadow-soft backdrop-blur transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-950/85"
                  key={label}
                >
                  <p className="text-xs text-slate-500 dark:text-slate-400">{caption}</p>
                  <p className="mt-2 text-2xl font-semibold capitalize text-slate-950 dark:text-white">
                    {value}
                  </p>
                  <p className="mt-1 text-xs font-medium text-teal-700 dark:text-teal-300">{label}</p>
                </div>
              ))}
            </section>

            <div className="grid grid-cols-1 gap-5 xl:grid-cols-[360px_1fr]">
              <div className="space-y-5">
                <UploadPanel onUpload={handleUpload} uploadState={uploadState} />
                <DatasetMetadataCard dataset={uploadState.dataset} />
                <div className="lg:hidden">
                  <Sidebar
                    activeResult={result}
                    darkMode={darkMode}
                    history={history}
                    onToggleDarkMode={() => setDarkMode((value) => !value)}
                  />
                </div>
              </div>

              <div className="min-w-0 space-y-5">
                <QueryInput
                  loading={queryState.loading}
                  onChange={setQuestion}
                  onSubmit={handleQuerySubmit}
                  value={question}
                />

                {queryState.error && (
                  <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-200">
                    {queryState.error}
                  </div>
                )}

                {!result ? (
                  <EmptyDashboard />
                ) : (
                  <>
                    <div className="grid grid-cols-1 gap-5 2xl:grid-cols-2">
                      <InsightCard insights={result.insights} mlInsights={result.ml_insights} />
                      <SqlCard darkMode={darkMode} sql={result.sql} />
                    </div>
                    <ChartRenderer
                      mlInsights={result.ml_insights}
                      rows={result.rows}
                      visualization={result.visualization}
                    />
                    <DataTable columns={result.columns} rows={result.rows} />
                  </>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

function DatasetMetadataCard({ dataset }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
          <DatabaseZap size={18} />
        </span>
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Dataset metadata</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {dataset ? "Latest uploaded dataset" : "Upload a CSV to activate"}
          </p>
        </div>
      </div>
      <div className="mt-4 space-y-2 text-sm">
        <MetadataRow label="File" value={dataset?.original_filename || "No dataset uploaded"} />
        <MetadataRow label="Rows" value={dataset?.rows ?? "-"} />
        <MetadataRow label="Columns" value={dataset?.columns ?? "-"} />
        <MetadataRow label="Table" value={dataset?.table_name || "-"} />
      </div>
    </section>
  );
}

function MetadataRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-900/70">
      <span className="text-xs text-slate-500 dark:text-slate-400">{label}</span>
      <span className="max-w-44 truncate text-right text-xs font-semibold text-slate-800 dark:text-slate-100">
        {value}
      </span>
    </div>
  );
}

function EmptyDashboard() {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white/85 p-8 text-center shadow-soft backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
      <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
        <LineChart size={28} />
      </div>
      <h2 className="mt-4 text-lg font-semibold text-slate-950 dark:text-white">
        Your analysis dashboard is ready.
      </h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500 dark:text-slate-400">
        Upload a dataset and ask a natural-language question. Generated SQL, charts, ML insights, and rows will appear here.
      </p>
    </div>
  );
}
