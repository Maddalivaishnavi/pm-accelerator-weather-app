import WeatherIcon from "./WeatherIcon";

export default function MiniWeatherCard({ lookup }) {
  const { resolved_location, current, forecast } = lookup;
  const todayRain = forecast?.[0]?.precipitation_probability;

  return (
    <div className="mini-weather-card">
      <div className="mini-top">
        <WeatherIcon code={current.weather_code} isDay={current.is_day ?? true} size={28} />
        <span className="mini-temp">
          {current.temperature_c != null ? Math.round(current.temperature_c) : "—"}°C
        </span>
      </div>
      <p className="mini-location">{resolved_location.display_name}</p>
      <p className="mini-desc">{current.description}</p>
      <div className="mini-stats">
        <span>Feels {current.feels_like_c != null ? Math.round(current.feels_like_c) : "—"}°</span>
        <span>Humidity {current.humidity_pct ?? "—"}%</span>
        {todayRain != null && <span>Rain {Math.round(todayRain)}%</span>}
      </div>
    </div>
  );
}
