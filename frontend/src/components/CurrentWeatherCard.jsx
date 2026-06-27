import WeatherIcon from "./WeatherIcon";
import AirQualityBadge from "./AirQualityBadge";

const SCALE_MIN = -10;
const SCALE_MAX = 45;

export default function CurrentWeatherCard({ location, current, airQuality, onSaveClick }) {
  const temp = current.temperature_c;
  const pct = clampPct(((temp - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100);

  return (
    <section className="readout-card">
      <div className="readout-top">
        <div>
          <p className="readout-location">{location}</p>
          <p className="readout-desc">{current.description}</p>
        </div>
        <WeatherIcon code={current.weather_code} isDay={current.is_day ?? true} size={52} />
      </div>

      <div className="readout-temp">
        <span className="readout-temp-value">{formatTemp(temp)}</span>
        <span className="readout-temp-unit">°C</span>
      </div>

      {/* Signature element: a thermometer-style tick scale showing where
          the current reading sits between -10°C and 45°C. */}
      <div className="tick-scale" aria-hidden="true">
        <div className="tick-scale-track">
          <div className="tick-scale-marker" style={{ left: `${pct}%` }} />
        </div>
        <div className="tick-scale-labels">
          <span>{SCALE_MIN}°</span>
          <span>{Math.round((SCALE_MIN + SCALE_MAX) / 2)}°</span>
          <span>{SCALE_MAX}°</span>
        </div>
      </div>

      <div className="readout-stats">
        <Stat label="Feels like" value={formatTemp(current.feels_like_c) + "°"} />
        <Stat label="Humidity" value={current.humidity_pct != null ? `${current.humidity_pct}%` : "—"} />
        <Stat label="Wind" value={current.wind_speed_kmh != null ? `${current.wind_speed_kmh} km/h` : "—"} />
      </div>

      {airQuality && <AirQualityBadge airQuality={airQuality} />}

      {onSaveClick && (
        <button className="btn btn-secondary readout-save" onClick={onSaveClick}>
          Save this location to my logbook
        </button>
      )}
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function formatTemp(t) {
  if (t == null) return "—";
  return Math.round(t);
}

function clampPct(p) {
  return Math.max(2, Math.min(98, p));
}
