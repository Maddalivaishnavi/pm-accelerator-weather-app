import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer,
} from "recharts";

export default function ForecastChart({ days }) {
  if (!days?.length) return null;

  const data = days.map((d) => ({
    day: weekday(d.date),
    High: round(d.temp_max_c),
    Low: round(d.temp_min_c),
    "Rain chance": d.precipitation_probability != null ? round(d.precipitation_probability) : 0,
  }));

  return (
    <section className="forecast-chart" aria-label="5-day forecast trend">
      <h3 className="forecast-chart-title">5-day trend</h3>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="day" stroke="var(--muted)" fontSize={12} tickLine={false} />
          <YAxis
            yAxisId="temp" stroke="var(--muted)" fontSize={12}
            tickLine={false} axisLine={false} unit="°"
          />
          <YAxis
            yAxisId="precip" orientation="right" stroke="var(--muted)" fontSize={12}
            tickLine={false} axisLine={false} unit="%" domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface)", border: "1px solid var(--border)",
              borderRadius: 8, fontSize: 13,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar
            yAxisId="precip" dataKey="Rain chance" fill="var(--accent)"
            fillOpacity={0.35} radius={[4, 4, 0, 0]} barSize={18}
          />
          <Line
            yAxisId="temp" type="monotone" dataKey="High" stroke="var(--sky-deep)"
            strokeWidth={2.5} dot={{ r: 3 }}
          />
          <Line
            yAxisId="temp" type="monotone" dataKey="Low" stroke="var(--accent-deep)"
            strokeWidth={2.5} dot={{ r: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </section>
  );
}

function weekday(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString(undefined, { weekday: "short" });
}

function round(v) {
  return v == null ? null : Math.round(v);
}
