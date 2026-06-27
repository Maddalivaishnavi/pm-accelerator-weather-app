import { useState } from "react";

export default function SearchBar({ onSearch, onUseLocation, loading }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim());
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="City, zip/postal code, landmark…"
        aria-label="Location"
      />
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Searching…" : "Check weather"}
      </button>
      <button
        type="button"
        className="btn btn-ghost"
        onClick={onUseLocation}
        disabled={loading}
      >
        Use my location
      </button>
    </form>
  );
}
