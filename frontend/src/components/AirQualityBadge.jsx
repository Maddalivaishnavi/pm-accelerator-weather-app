const AQI_LEVELS = [
  { max: 50, label: "Good", color: "var(--good)" },
  { max: 100, label: "Moderate", color: "var(--accent-deep)" },
  { max: 150, label: "Unhealthy for sensitive groups", color: "#d97706" },
  { max: 200, label: "Unhealthy", color: "#dc2626" },
  { max: 300, label: "Very unhealthy", color: "#9333ea" },
  { max: Infinity, label: "Hazardous", color: "#7f1d1d" },
];

export default function AirQualityBadge({ airQuality }) {
  if (airQuality?.us_aqi == null) return null;
  const level = AQI_LEVELS.find((l) => airQuality.us_aqi <= l.max);

  return (
    <div className="aqi-badge" style={{ "--aqi-color": level.color }}>
      <span className="aqi-dot" />
      <span>
        Air quality: <strong>{Math.round(airQuality.us_aqi)} US AQI</strong> · {level.label}
      </span>
    </div>
  );
}
