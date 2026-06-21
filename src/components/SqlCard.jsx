import { Code2 } from "lucide-react";
import Editor from "@monaco-editor/react";

export default function SqlCard({ sql, darkMode = false }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-950">
      <div className="mb-3 flex items-center gap-2">
        <Code2 size={18} className="text-blue-700 dark:text-blue-300" />
        <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Generated SQL</h2>
      </div>
      <div className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-800">
        <Editor
          height="220px"
          language="sql"
          options={{
            readOnly: true,
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            wordWrap: "on",
            padding: { top: 14, bottom: 14 },
          }}
          theme={darkMode ? "vs-dark" : "light"}
          value={sql || "-- No SQL generated yet."}
        />
      </div>
    </section>
  );
}
