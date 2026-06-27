import { useState } from "react";
import { api } from "../lib/api";

const EXPORT_FORMATS = [
  { value: "json", label: "JSON" },
  { value: "csv", label: "CSV" },
  { value: "xml", label: "XML" },
  { value: "markdown", label: "Markdown" },
  { value: "pdf", label: "PDF" },
];

export default function LogbookRecord({ record, onUpdate, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    location: record.query_location,
    start_date: record.start_date,
    end_date: record.end_date,
    notes: record.notes || "",
  });
  const [saving, setSaving] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  async function handleSaveEdit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await onUpdate(record.id, {
        location: form.location,
        start_date: form.start_date,
        end_date: form.end_date,
        notes: form.notes,
      });
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className="log-record">
      <div className="log-record-main">
        <button
          className="log-record-expand"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? "▾" : "▸"}
        </button>

        {editing ? (
          <form className="log-edit-form" onSubmit={handleSaveEdit}>
            <input
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              required
            />
            <input
              type="date"
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
              required
            />
            <input
              type="date"
              value={form.end_date}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })}
              required
            />
            <input
              placeholder="Notes"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
            <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </form>
        ) : (
          <div className="log-record-info">
            <strong>{record.resolved_name}</strong>
            <span className="log-record-dates">
              {record.start_date} → {record.end_date}
            </span>
            {record.notes && <span className="log-record-notes">{record.notes}</span>}
          </div>
        )}

        {!editing && (
          <div className="log-record-actions">
            <ExportMenu recordId={record.id} />
            <button className="icon-btn" onClick={() => setEditing(true)} aria-label="Edit">
              Edit
            </button>
            {confirmingDelete ? (
              <span className="confirm-delete">
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => onDelete(record.id)}
                >
                  Confirm
                </button>
                <button className="btn btn-ghost btn-sm" onClick={() => setConfirmingDelete(false)}>
                  Cancel
                </button>
              </span>
            ) : (
              <button className="icon-btn icon-btn-danger" onClick={() => setConfirmingDelete(true)} aria-label="Delete">
                Delete
              </button>
            )}
          </div>
        )}
      </div>

      {expanded && (
        <table className="daily-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Max °C</th>
              <th>Min °C</th>
              <th>Precip (mm)</th>
            </tr>
          </thead>
          <tbody>
            {record.daily_temperatures.length === 0 ? (
              <tr>
                <td colSpan={4} className="empty-row">No daily data for this range.</td>
              </tr>
            ) : (
              record.daily_temperatures.map((d) => (
                <tr key={d.date}>
                  <td>{d.date}</td>
                  <td>{fmt(d.temp_max_c)}</td>
                  <td>{fmt(d.temp_min_c)}</td>
                  <td>{fmt(d.precipitation_mm)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
    </li>
  );
}

function ExportMenu({ recordId }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="export-menu">
      <button className="icon-btn" onClick={() => setOpen((v) => !v)} aria-haspopup="true">
        Export ▾
      </button>
      {open && (
        <ul className="export-menu-list" onMouseLeave={() => setOpen(false)}>
          {EXPORT_FORMATS.map((f) => (
            <li key={f.value}>
              <a href={api.exportRecordUrl(recordId, f.value)} download>
                {f.label}
              </a>
            </li>
          ))}
        </ul>
      )}
    </span>
  );
}

function fmt(v) {
  return v == null ? "—" : v;
}
