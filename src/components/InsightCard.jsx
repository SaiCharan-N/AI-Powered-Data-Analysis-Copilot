import { Activity, Sparkles } from "lucide-react";

export default function InsightCard({ insights, mlInsights }) {
  const anomaly = mlInsights?.anomaly_detection;
  const clustering = mlInsights?.clustering;
  const forecasting = mlInsights?.forecasting;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-950">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
          <Sparkles size={17} />
        </span>
        <h2 className="text-sm font-semibold text-slate-950 dark:text-white">AI insights</h2>
      </div>
      <p className="rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-700 dark:bg-slate-900/70 dark:text-slate-200">
        {insights || "Run a query to generate insights."}
      </p>
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Metric label="Outliers" value={anomaly?.enabled ? anomaly.outlier_count : "Off"} />
        <Metric label="Clusters" value={clustering?.enabled ? clustering.cluster_count : "Off"} />
        <Metric label="Forecast" value={forecasting?.enabled ? `${forecasting.horizon} periods` : "Off"} />
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-white px-3 py-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Activity size={13} />
        {label}
      </p>
      <p className="mt-1 text-lg font-semibold text-slate-950 dark:text-white">{value}</p>
    </div>
  );
}
