// Maps WMO weather codes (same scheme the backend uses) to a small set of
// hand-drawn SVG icons. Kept dependency-free on purpose.
export default function WeatherIcon({ code, size = 40, isDay = true }) {
  const kind = classify(code, isDay);
  const props = { width: size, height: size, viewBox: "0 0 48 48", "aria-hidden": "true" };

  switch (kind) {
    case "clear-day":
      return (
        <svg {...props}>
          <circle cx="24" cy="24" r="10" fill="var(--accent)" />
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <line
              key={deg}
              x1="24" y1="6" x2="24" y2="11"
              stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round"
              transform={`rotate(${deg} 24 24)`}
            />
          ))}
        </svg>
      );
    case "clear-night":
      return (
        <svg {...props}>
          <path
            d="M30 8a16 16 0 1 0 10 26 13 13 0 0 1-10-26z"
            fill="var(--ink-soft)"
          />
        </svg>
      );
    case "partly-cloudy":
      return (
        <svg {...props}>
          <circle cx="18" cy="20" r="8" fill="var(--accent)" />
          <path
            d="M14 32a8 8 0 0 1 1-16 11 11 0 0 1 21 4 7 7 0 0 1-2 12z"
            fill="var(--surface)" stroke="var(--border)" strokeWidth="1.5"
          />
        </svg>
      );
    case "cloudy":
      return (
        <svg {...props}>
          <path
            d="M12 32a8 8 0 0 1 1-16 11 11 0 0 1 21 4 7 7 0 0 1-2 12z"
            fill="var(--surface)" stroke="var(--border)" strokeWidth="1.5"
          />
        </svg>
      );
    case "fog":
      return (
        <svg {...props}>
          {[14, 22, 30].map((y) => (
            <line key={y} x1="8" y1={y} x2="40" y2={y} stroke="var(--muted)" strokeWidth="3" strokeLinecap="round" />
          ))}
        </svg>
      );
    case "rain":
      return (
        <svg {...props}>
          <path
            d="M12 26a8 8 0 0 1 1-16 11 11 0 0 1 21 4 7 7 0 0 1-2 12z"
            fill="var(--surface)" stroke="var(--border)" strokeWidth="1.5"
          />
          {[16, 24, 32].map((x) => (
            <line key={x} x1={x} y1="30" x2={x - 3} y2="40" stroke="var(--ink-soft)" strokeWidth="2.5" strokeLinecap="round" />
          ))}
        </svg>
      );
    case "snow":
      return (
        <svg {...props}>
          <path
            d="M12 24a8 8 0 0 1 1-16 11 11 0 0 1 21 4 7 7 0 0 1-2 12z"
            fill="var(--surface)" stroke="var(--border)" strokeWidth="1.5"
          />
          {[16, 24, 32].map((x) => (
            <circle key={x} cx={x} cy="38" r="2" fill="var(--muted)" />
          ))}
        </svg>
      );
    case "storm":
      return (
        <svg {...props}>
          <path
            d="M12 22a8 8 0 0 1 1-16 11 11 0 0 1 21 4 7 7 0 0 1-2 12z"
            fill="var(--ink-soft)"
          />
          <path d="M24 26l-6 10h5l-3 8 10-12h-5z" fill="var(--accent)" />
        </svg>
      );
    default:
      return (
        <svg {...props}>
          <circle cx="24" cy="24" r="14" fill="none" stroke="var(--muted)" strokeWidth="2" />
        </svg>
      );
  }
}

function classify(code, isDay) {
  if (code === 0 || code === 1) return isDay ? "clear-day" : "clear-night";
  if (code === 2) return "partly-cloudy";
  if (code === 3) return "cloudy";
  if (code === 45 || code === 48) return "fog";
  if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].includes(code)) return "rain";
  if ([71, 73, 75, 77, 85, 86].includes(code)) return "snow";
  if ([95, 96, 99].includes(code)) return "storm";
  return "unknown";
}
