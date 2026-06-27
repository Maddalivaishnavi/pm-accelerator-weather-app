import { useState } from "react";

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}
function plusDaysStr(n) {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

export default function SaveToLogForm({ defaultLocation, onSave, onCancel, saving, error }) {
  const [location, setLocation] = useState(defaultLocation || "");
  const [startDate, setStartDate] = useState(todayStr());
  const [endDate, setEndDate] = useState(plusDaysStr(4));
  const [notes, setNotes] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onSave({ location, start_date: startDate, end_date: endDate, notes: notes || undefined });
  }

  return (
    <form className="modal-form" onSubmit={handleSubmit}>
      <h3>Save to logbook</h3>
      {error && <p className="modal-error">{error}</p>}
      <label>
        Location
        <input value={location} onChange={(e) => setLocation(e.target.value)} required />
      </label>
      <div className="field-row">
        <label>
          From
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
        </label>
        <label>
          To
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
        </label>
      </div>
      <label>
        Notes (optional)
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
      </label>
      <div className="modal-actions">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving…" : "Save"}
        </button>
      </div>
    </form>
  );
}
