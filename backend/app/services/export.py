"""
Export service — satisfies requirement 2.3 (Data Export).
Supports JSON, CSV, XML, Markdown, and PDF, for either a single record
or the full list of records.

Each function returns (bytes, media_type, filename_suffix).
"""
import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import List

from fpdf import FPDF

from app.models import WeatherRecord


def _record_to_dict(r: WeatherRecord) -> dict:
    return {
        "id": r.id,
        "query_location": r.query_location,
        "resolved_name": r.resolved_name,
        "country": r.country,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat(),
        "notes": r.notes,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "daily_temperatures": [
            {
                "date": d.date.isoformat(),
                "temp_max_c": d.temp_max_c,
                "temp_min_c": d.temp_min_c,
                "precipitation_mm": d.precipitation_mm,
                "weather_code": d.weather_code,
            }
            for d in r.daily_temperatures
        ],
    }


def to_json(records: List[WeatherRecord]) -> bytes:
    payload = [_record_to_dict(r) for r in records]
    return json.dumps(payload, indent=2).encode("utf-8")


def to_csv(records: List[WeatherRecord]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["record_id", "location", "country", "latitude", "longitude",
         "date", "temp_max_c", "temp_min_c", "precipitation_mm", "notes"]
    )
    for r in records:
        if not r.daily_temperatures:
            writer.writerow([r.id, r.resolved_name, r.country, r.latitude,
                              r.longitude, "", "", "", "", r.notes or ""])
        for d in r.daily_temperatures:
            writer.writerow([
                r.id, r.resolved_name, r.country, r.latitude, r.longitude,
                d.date.isoformat(), d.temp_max_c, d.temp_min_c,
                d.precipitation_mm, r.notes or "",
            ])
    return buf.getvalue().encode("utf-8")


def to_xml(records: List[WeatherRecord]) -> bytes:
    root = ET.Element("weather_records")
    for r in records:
        rec_el = ET.SubElement(root, "record", id=str(r.id))
        for field in ["query_location", "resolved_name", "country",
                      "latitude", "longitude", "start_date", "end_date", "notes"]:
            value = getattr(r, field)
            child = ET.SubElement(rec_el, field)
            child.text = str(value) if value is not None else ""
        daily_el = ET.SubElement(rec_el, "daily_temperatures")
        for d in r.daily_temperatures:
            day_el = ET.SubElement(daily_el, "day", date=d.date.isoformat())
            ET.SubElement(day_el, "temp_max_c").text = str(d.temp_max_c)
            ET.SubElement(day_el, "temp_min_c").text = str(d.temp_min_c)
            ET.SubElement(day_el, "precipitation_mm").text = str(d.precipitation_mm)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def to_markdown(records: List[WeatherRecord]) -> bytes:
    lines = ["# Weather Records Export", ""]
    for r in records:
        lines.append(f"## {r.resolved_name} ({r.start_date} to {r.end_date})")
        lines.append(f"- Query: `{r.query_location}`")
        lines.append(f"- Coordinates: {r.latitude}, {r.longitude}")
        if r.notes:
            lines.append(f"- Notes: {r.notes}")
        lines.append("")
        if r.daily_temperatures:
            lines.append("| Date | Max °C | Min °C | Precip (mm) |")
            lines.append("|------|--------|--------|-------------|")
            for d in r.daily_temperatures:
                lines.append(
                    f"| {d.date} | {d.temp_max_c} | {d.temp_min_c} | {d.precipitation_mm} |"
                )
        lines.append("")
    return "\n".join(lines).encode("utf-8")


def to_pdf(records: List[WeatherRecord]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Weather Records Export", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)

    for r in records:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, f"{r.resolved_name} ({r.start_date} to {r.end_date})",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Query: {r.query_location}  |  Coordinates: {r.latitude}, {r.longitude}",
                 new_x="LMARGIN", new_y="NEXT")
        if r.notes:
            pdf.multi_cell(0, 6, f"Notes: {r.notes}")

        if r.daily_temperatures:
            pdf.set_x(pdf.l_margin)  # multi_cell() above doesn't reset X — without
            pdf.set_font("Helvetica", "B", 10)  # this, the header row renders off-page
            pdf.cell(40, 6, "Date", border=1)
            pdf.cell(30, 6, "Max C", border=1)
            pdf.cell(30, 6, "Min C", border=1)
            pdf.cell(40, 6, "Precip (mm)", border=1, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for d in r.daily_temperatures:
                pdf.set_x(pdf.l_margin)
                pdf.cell(40, 6, str(d.date), border=1)
                pdf.cell(30, 6, str(d.temp_max_c), border=1)
                pdf.cell(30, 6, str(d.temp_min_c), border=1)
                pdf.cell(40, 6, str(d.precipitation_mm), border=1,
                         new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


EXPORTERS = {
    "json": (to_json, "application/json", "json"),
    "csv": (to_csv, "text/csv", "csv"),
    "xml": (to_xml, "application/xml", "xml"),
    "markdown": (to_markdown, "text/markdown", "md"),
    "pdf": (to_pdf, "application/pdf", "pdf"),
}


def export_records(records: List[WeatherRecord], fmt: str):
    fmt = fmt.lower()
    if fmt not in EXPORTERS:
        raise ValueError(f"Unsupported export format: {fmt}")
    func, media_type, ext = EXPORTERS[fmt]
    return func(records), media_type, ext
