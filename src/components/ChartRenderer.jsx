import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#0f766e", "#2563eb", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#65a30d", "#c2410c"];

export default function ChartRenderer({ rows, visualization, mlInsights }) {
  const chartType = visualization?.chart_type || "table";
  const xAxis = visualization?.x_axis;
  const yAxis = visualization?.y_axis;
  const hasAxes = Boolean(xAxis && yAxis);
  const data = Array.isArray(rows) ? rows : [];
  const forecast = mlInsights?.forecasting;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft transition-all duration-200 dark:border-slate-800 dark:bg-slate-950">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Results chart</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {hasAxes ? `${xAxis} by ${yAxis}` : "Visualization metadata will appear after analysis"}
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium capitalize text-slate-600 dark:bg-slate-900 dark:text-slate-300">
          {chartType}
        </span>
      </div>

      <div className="h-[360px] min-h-[360px] rounded-lg bg-slate-50 p-3 dark:bg-slate-900/60">
        {data.length === 0 || !hasAxes || chartType === "table" ? (
          <EmptyChart />
        ) : (
          <ResponsiveContainer height="100%" width="100%">
            {renderChart(chartType, data, xAxis, yAxis, forecast)}
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}

function renderChart(chartType, data, xAxis, yAxis, forecast) {
  if (chartType === "line") {
    const chartData = mergeForecastRows(data, forecast, xAxis, yAxis);
    return (
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
        <XAxis dataKey={xAxis} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Line dataKey={yAxis} dot={false} stroke="#0f766e" strokeWidth={3} type="monotone" />
        {forecast?.enabled && (
          <Line
            dataKey="forecast_value"
            dot={false}
            stroke="#f59e0b"
            strokeDasharray="6 4"
            strokeWidth={3}
            type="monotone"
          />
        )}
      </LineChart>
    );
  }

  if (chartType === "bar") {
    return (
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
        <XAxis dataKey={xAxis} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Bar dataKey={yAxis} fill="#2563eb" radius={[4, 4, 0, 0]} />
      </BarChart>
    );
  }

  if (chartType === "scatter") {
    return (
      <ScatterChart>
        <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
        <XAxis dataKey={xAxis} name={xAxis} tick={{ fontSize: 12 }} type="number" />
        <YAxis dataKey={yAxis} name={yAxis} tick={{ fontSize: 12 }} type="number" />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        <Legend />
        <Scatter data={data} fill="#0f766e" name={`${xAxis} vs ${yAxis}`} />
      </ScatterChart>
    );
  }

  if (chartType === "pie") {
    return (
      <PieChart>
        <Tooltip />
        <Legend />
        <Pie
          cx="50%"
          cy="50%"
          data={data}
          dataKey={yAxis}
          innerRadius={56}
          nameKey={xAxis}
          outerRadius={104}
          paddingAngle={2}
        >
          {data.map((entry, index) => (
            <Cell fill={COLORS[index % COLORS.length]} key={`${entry[xAxis]}-${index}`} />
          ))}
        </Pie>
      </PieChart>
    );
  }

  return <EmptyChart />;
}

function mergeForecastRows(data, forecast, xAxis, yAxis) {
  if (!forecast?.enabled || !Array.isArray(forecast.rows)) {
    return data;
  }

  const actualRows = data.map((row) => ({
    ...row,
    forecast_value: null,
  }));
  const forecastRows = forecast.rows.map((row) => ({
    [xAxis]: row[xAxis],
    [yAxis]: null,
    forecast_value: row[yAxis],
  }));

  return [...actualRows, ...forecastRows];
}

function EmptyChart() {
  return (
    <div className="grid h-full place-items-center rounded-lg border border-dashed border-slate-200 bg-white text-center text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
      <div>
        <div className="mx-auto mb-3 h-14 w-14 rounded-full bg-slate-100 dark:bg-slate-900" />
        Chart appears after a visual result is available.
      </div>
    </div>
  );
}
