import WeatherIcon from "./WeatherIcon";

export default function ForecastStrip({ days }) {
  if (!days?.length) return null;

  return (
    <section className="forecast-strip" aria-label="5-day forecast">
      {days.map((d) => (
        <div className="forecast-day" key={d.date}>
          <span className="forecast-weekday">{weekday(d.date)}</span>
          <WeatherIcon code={d.weather_code} size={32} />
          <span className="forecast-temps">
            <strong>{round(d.temp_max_c)}°</strong>
            <span className="forecast-min"> {round(d.temp_min_c)}°</span>
          </span>
          {d.precipitation_probability != null && (
            <span className="forecast-precip">{Math.round(d.precipitation_probability)}% rain</span>
          )}
        </div>
      ))}
    </section>
  );
}

function weekday(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString(undefined, { weekday: "short" });
}

function round(v) {
  return v == null ? "—" : Math.round(v);
}
