import { BarChart3, Database, History, Moon, Sparkles, Sun } from "lucide-react";

export default function Sidebar({ darkMode, onToggleDarkMode, history, activeResult }) {
  return (
    <aside className="flex h-full flex-col border-r border-slate-200 bg-white px-4 py-5 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-lg bg-teal-700 text-white shadow-lg shadow-teal-900/10">
          <BarChart3 size={20} />
        </div>
        <div>
          <p className="text-sm font-bold text-slate-950 dark:text-white">Data Copilot</p>
          <p className="text-xs text-slate-500 dark:text-slate-400">AI analytics console</p>
        </div>
      </div>

      <nav className="mt-8 space-y-2">
        <a className="flex items-center gap-3 rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-200 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800">
          <Database size={17} />
          Workspace
        </a>
        <a className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white">
          <History size={17} />
          History
        </a>
      </nav>

      <section className="mt-8 min-h-0 flex-1">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Recent queries
        </p>
        <div className="max-h-[44vh] space-y-2 overflow-y-auto pr-1">
          {history.length === 0 ? (
            <p className="rounded-lg border border-dashed border-slate-200 px-3 py-4 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
              No queries yet.
            </p>
          ) : (
            history.map((item) => (
              <div
                className="rounded-lg border border-slate-200 px-3 py-2 transition hover:-translate-y-0.5 hover:border-teal-200 hover:bg-teal-50/50 dark:border-slate-800 dark:hover:border-teal-900 dark:hover:bg-teal-950/20"
                key={item.id}
              >
                <p className="line-clamp-2 text-xs font-medium text-slate-800 dark:text-slate-100">
                  {item.question}
                </p>
                <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                  {item.rowCount} rows · {item.executedAt}
                </p>
              </div>
            ))
          )}
        </div>
      </section>

      <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-900/70">
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Sparkles size={14} />
          Active result
        </div>
        <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">
          {activeResult ? `${activeResult.row_count} rows` : "None"}
        </p>
      </div>

      <button
        className="mt-4 flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 dark:border-slate-800 dark:text-slate-200 dark:hover:bg-slate-900"
        onClick={onToggleDarkMode}
        type="button"
      >
        {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        {darkMode ? "Light mode" : "Dark mode"}
      </button>
    </aside>
  );
}
