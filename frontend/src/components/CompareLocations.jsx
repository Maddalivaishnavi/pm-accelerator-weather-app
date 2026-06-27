import { useState } from "react";
import { api, ApiError } from "../lib/api";
import { getCurrentPosition } from "../lib/geolocation";
import MiniWeatherCard from "./MiniWeatherCard";
import ComparisonSummary from "./ComparisonSummary";

function emptySide() {
  return { input: "", lookup: null, loading: false, error: null };
}

function messageFor(err) {
  if (err instanceof ApiError) return err.message;
  return err?.message || "Something went wrong. Please try again.";
}

export default function CompareLocations() {
  const [open, setOpen] = useState(false);
  const [home, setHome] = useState(emptySide);
  const [dest, setDest] = useState(emptySide);

  async function search(setSide, location) {
    setSide((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await api.lookupWeather(location);
      setSide((s) => ({ ...s, lookup: data, loading: false }));
    } catch (err) {
      setSide((s) => ({ ...s, loading: false, error: messageFor(err), lookup: null }));
    }
  }

  async function handleUseMyLocation(setSide) {
    setSide((s) => ({ ...s, loading: true, error: null }));
    try {
      const pos = await getCurrentPosition();
      const data = await api.lookupByCoordinates(pos.coords.latitude, pos.coords.longitude);
      setSide((s) => ({ ...s, lookup: data, loading: false, input: data.resolved_location.display_name }));
    } catch (err) {
      setSide((s) => ({ ...s, loading: false, error: messageFor(err) }));
    }
  }

  return (
    <section className="compare-section">
      <button type="button" className="btn btn-ghost compare-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "Hide location comparison ▾" : "Compare with another location ▸"}
      </button>

      {open && (
        <div className="compare-body">
          <p className="compare-hint">
            Planning a trip? See how your destination compares to home before you go.
          </p>
          <div className="compare-grid">
            <CompareColumn
              label="Home"
              side={home}
              setSide={setHome}
              onSearch={(loc) => search(setHome, loc)}
              onUseLocation={() => handleUseMyLocation(setHome)}
            />
            <CompareColumn
              label="Destination"
              side={dest}
              setSide={setDest}
              onSearch={(loc) => search(setDest, loc)}
            />
          </div>

          {home.lookup && dest.lookup && (
            <ComparisonSummary home={home.lookup} dest={dest.lookup} homeName="Home" destName="Destination" />
          )}
        </div>
      )}
    </section>
  );
}

function CompareColumn({ label, side, setSide, onSearch, onUseLocation }) {
  function handleSubmit(e) {
    e.preventDefault();
    if (side.input.trim()) onSearch(side.input.trim());
  }

  return (
    <div className="compare-column">
      <p className="compare-column-label">{label}</p>
      <form onSubmit={handleSubmit} className="compare-form">
        <input
          value={side.input}
          onChange={(e) => setSide((s) => ({ ...s, input: e.target.value }))}
          placeholder={`${label} location…`}
          aria-label={`${label} location`}
        />
        <button type="submit" className="btn btn-primary btn-sm" disabled={side.loading}>
          {side.loading ? "…" : "Go"}
        </button>
        {onUseLocation && (
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={onUseLocation}
            disabled={side.loading}
          >
            Use mine
          </button>
        )}
      </form>
      {side.error && <p className="compare-error">{side.error}</p>}
      {side.lookup && <MiniWeatherCard lookup={side.lookup} />}
    </div>
  );
}
