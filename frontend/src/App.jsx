import { useEffect, useState } from "react";
import SearchBar from "./components/SearchBar";
import ErrorBanner from "./components/ErrorBanner";
import CurrentWeatherCard from "./components/CurrentWeatherCard";
import ForecastStrip from "./components/ForecastStrip";
import ForecastChart from "./components/ForecastChart";
import RecommendationsList from "./components/RecommendationsList";
import AiInsightCard from "./components/AiInsightCard";
import ThemeToggle from "./components/ThemeToggle";
import CompareLocations from "./components/CompareLocations";
import SaveToLogForm from "./components/SaveToLogForm";
import LogbookSection from "./components/LogbookSection";
import Footer from "./components/Footer";
import { api, ApiError } from "./lib/api";
import { getCurrentPosition } from "./lib/geolocation";

function getInitialTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);
  const [lookup, setLookup] = useState(null); // current WeatherLookupResponse
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  const [records, setRecords] = useState([]);
  const [recordsLoading, setRecordsLoading] = useState(true);

  const [showSaveForm, setShowSaveForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    refreshRecords();
  }, []);

  async function refreshRecords() {
    setRecordsLoading(true);
    try {
      const data = await api.listRecords();
      setRecords(data);
    } catch (err) {
      setError(messageFor(err));
    } finally {
      setRecordsLoading(false);
    }
  }

  async function handleSearch(location) {
    setSearching(true);
    setError(null);
    try {
      const data = await api.lookupWeather(location);
      setLookup(data);
    } catch (err) {
      setLookup(null);
      setError(messageFor(err));
    } finally {
      setSearching(false);
    }
  }

  async function handleUseLocation() {
    setSearching(true);
    setError(null);
    try {
      const pos = await getCurrentPosition();
      const data = await api.lookupByCoordinates(pos.coords.latitude, pos.coords.longitude);
      setLookup(data);
    } catch (err) {
      setError(err.message || messageFor(err));
    } finally {
      setSearching(false);
    }
  }

  async function handleSaveRecord(payload) {
    setSaving(true);
    setSaveError(null);
    try {
      await api.createRecord(payload);
      setShowSaveForm(false);
      await refreshRecords();
    } catch (err) {
      setSaveError(messageFor(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateRecord(id, payload) {
    try {
      await api.updateRecord(id, payload);
      await refreshRecords();
    } catch (err) {
      setError(messageFor(err));
    }
  }

  async function handleDeleteRecord(id) {
    try {
      await api.deleteRecord(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(messageFor(err));
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Weather Station</p>
          <h1>Know before you go</h1>
        </div>
        <ThemeToggle theme={theme} onToggle={() => setTheme((t) => (t === "dark" ? "light" : "dark"))} />
      </header>

      <main className="app-main">
        <SearchBar onSearch={handleSearch} onUseLocation={handleUseLocation} loading={searching} />

        <ErrorBanner message={error} onDismiss={() => setError(null)} />

        <CompareLocations />

        {lookup && (
          <>
            <CurrentWeatherCard
              location={lookup.resolved_location.display_name}
              current={lookup.current}
              airQuality={lookup.air_quality}
              onSaveClick={() => {
                setSaveError(null);
                setShowSaveForm(true);
              }}
            />
            <ForecastStrip days={lookup.forecast} />
            <ForecastChart days={lookup.forecast} />
            <RecommendationsList tips={lookup.recommendations} />
            <AiInsightCard insight={lookup.ai_insight} />
          </>
        )}

        {showSaveForm && (
          <div className="modal-overlay" onClick={() => setShowSaveForm(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <SaveToLogForm
                defaultLocation={lookup?.resolved_location?.display_name}
                onSave={handleSaveRecord}
                onCancel={() => setShowSaveForm(false)}
                saving={saving}
                error={saveError}
              />
            </div>
          </div>
        )}

        <LogbookSection
          records={records}
          loading={recordsLoading}
          onUpdate={handleUpdateRecord}
          onDelete={handleDeleteRecord}
        />
      </main>

      <Footer />
    </div>
  );
}

function messageFor(err) {
  if (err instanceof ApiError) return err.message;
  return "Something went wrong. Please try again.";
}
