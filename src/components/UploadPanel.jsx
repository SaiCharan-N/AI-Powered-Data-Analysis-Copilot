import { CheckCircle2, FileSpreadsheet, UploadCloud } from "lucide-react";

import LoadingSpinner from "./LoadingSpinner.jsx";

export default function UploadPanel({ uploadState, onUpload }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Dataset upload</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">CSV files are stored in SQLite.</p>
        </div>
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
          <UploadCloud size={19} />
        </span>
      </div>

      <label className="mt-4 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50/70 px-4 py-7 text-center transition-all duration-200 hover:border-teal-600 hover:bg-teal-50 dark:border-slate-700 dark:bg-slate-900/60 dark:hover:border-teal-400 dark:hover:bg-teal-950/40">
        <input
          accept=".csv,text/csv"
          className="sr-only"
          disabled={uploadState.loading}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              onUpload(file);
              event.target.value = "";
            }
          }}
          type="file"
        />
        <FileSpreadsheet className="mb-2 text-slate-400 dark:text-slate-500" size={24} />
        <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">Choose CSV</span>
        <span className="mt-1 text-xs text-slate-500 dark:text-slate-400">Upload and index automatically</span>
      </label>

      <div className="mt-4 min-h-6">
        {uploadState.loading && <LoadingSpinner label="Uploading CSV" />}
        {uploadState.error && (
          <p className="text-sm text-red-600 dark:text-red-300">{uploadState.error}</p>
        )}
        {uploadState.dataset && (
          <div className="rounded-lg border border-teal-100 bg-teal-50/70 p-3 text-xs text-slate-600 dark:border-teal-900/60 dark:bg-teal-950/30 dark:text-slate-300">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="text-teal-700 dark:text-teal-300" size={16} />
              <p className="font-semibold text-slate-900 dark:text-white">
                {uploadState.dataset.original_filename}
              </p>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <MetadataPill label="Rows" value={uploadState.dataset.rows} />
              <MetadataPill label="Columns" value={uploadState.dataset.columns} />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function MetadataPill({ label, value }) {
  return (
    <div className="rounded-md bg-white px-3 py-2 dark:bg-slate-900">
      <p className="text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-950 dark:text-white">{value}</p>
    </div>
  );
}
