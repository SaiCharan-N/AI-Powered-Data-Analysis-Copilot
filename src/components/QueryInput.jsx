import { MessageSquareText, SendHorizontal } from "lucide-react";

import LoadingSpinner from "./LoadingSpinner.jsx";

export default function QueryInput({ value, onChange, onSubmit, loading }) {
  return (
    <section className="sticky top-4 z-20 rounded-lg border border-slate-200/80 bg-white/90 p-4 shadow-soft backdrop-blur transition-all duration-300 dark:border-slate-800/80 dark:bg-slate-950/90">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-950 dark:text-white">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
          <MessageSquareText size={17} />
        </span>
        Ask your data
      </div>
      <form className="flex flex-col gap-3 sm:flex-row" onSubmit={onSubmit}>
        <textarea
          className="min-h-24 flex-1 resize-none rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-950 outline-none transition-all duration-200 placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:shadow-[0_0_0_4px_rgba(15,118,110,0.10)] dark:border-slate-800 dark:bg-slate-900 dark:text-white dark:focus:border-teal-400"
          disabled={loading}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Ask about your dataset..."
          value={value}
        />
        <button
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-teal-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-teal-800 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-teal-500 dark:text-slate-950 dark:hover:bg-teal-400"
          disabled={loading || !value.trim()}
          type="submit"
        >
          <SendHorizontal size={17} />
          Ask
        </button>
      </form>
      <div className="mt-3 min-h-6">
        {loading && <LoadingSpinner label="Generating SQL, running analysis, and preparing insights" />}
      </div>
    </section>
  );
}
