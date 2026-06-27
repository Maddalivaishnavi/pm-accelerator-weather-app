import LogbookRecord from "./LogbookRecord";
import { api } from "../lib/api";

const EXPORT_FORMATS = [
  { value: "json", label: "JSON" },
  { value: "csv", label: "CSV" },
  { value: "xml", label: "XML" },
  { value: "markdown", label: "Markdown" },
  { value: "pdf", label: "PDF" },
];

export default function LogbookSection({ records, loading, onUpdate, onDelete }) {
  return (
    <section className="logbook">
      <div className="logbook-header">
        <div>
          <h2>Logbook</h2>
          <p className="logbook-sub">
            Every location and date range you've saved, with the temperatures fetched for it.
          </p>
        </div>
        {records.length > 0 && (
          <div className="export-menu">
            <BulkExport />
          </div>
        )}
      </div>

      {loading && <p className="muted">Loading saved records…</p>}

      {!loading && records.length === 0 && (
        <p className="empty-state">
          Nothing saved yet. Look up a location above, then save it to start your logbook.
        </p>
      )}

      {records.length > 0 && (
        <ul className="log-list">
          {records.map((r) => (
            <LogbookRecord key={r.id} record={r} onUpdate={onUpdate} onDelete={onDelete} />
          ))}
        </ul>
      )}
    </section>
  );
}

function BulkExport() {
  return (
    <details className="bulk-export">
      <summary className="btn btn-ghost btn-sm">Export all ▾</summary>
      <ul className="export-menu-list export-menu-list-static">
        {EXPORT_FORMATS.map((f) => (
          <li key={f.value}>
            <a href={api.exportAllUrl(f.value)} download>
              {f.label}
            </a>
          </li>
        ))}
      </ul>
    </details>
  );
}
