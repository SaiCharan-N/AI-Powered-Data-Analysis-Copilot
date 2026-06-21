import { formatNumber } from "../utils/formatters.js";

export default function DataTable({ rows, columns }) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const safeColumns = Array.isArray(columns) ? columns : [];

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-950">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Data table</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Showing up to 250 rows for fast browsing.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-900 dark:text-slate-300">
          {safeRows.length} rows
        </span>
      </div>

      {safeRows.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-400">
          <div className="mx-auto mb-3 h-12 w-12 rounded-full bg-white shadow-sm dark:bg-slate-950" />
          No rows to display yet.
        </div>
      ) : (
        <div className="max-h-[460px] overflow-auto rounded-lg border border-slate-200 dark:border-slate-800">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm dark:divide-slate-800">
            <thead className="sticky top-0 bg-slate-50 dark:bg-slate-900">
              <tr>
                {safeColumns.map((column) => (
                  <th
                    className="whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400"
                    key={column}
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-900">
              {safeRows.slice(0, 250).map((row, rowIndex) => (
                <tr className="transition hover:bg-teal-50/50 dark:hover:bg-teal-950/20" key={rowIndex}>
                  {safeColumns.map((column) => (
                    <td
                      className="max-w-64 whitespace-nowrap px-4 py-3 text-slate-700 dark:text-slate-200"
                      key={`${rowIndex}-${column}`}
                      title={String(row[column] ?? "")}
                    >
                      <span className="block overflow-hidden text-ellipsis">
                        {formatNumber(row[column]) ?? "-"}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
