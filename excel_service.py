from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote
from pdf_downloader import download_pdf
from openpyxl import load_workbook, Workbook


BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE = BASE_DIR / "xlsx-file" / "GRI_2017_2025.xlsx"

OUTPUT_DIR = BASE_DIR / "pdf_files"
OUTPUT_EXCEL_FILE = OUTPUT_DIR / "downloaded_reports.xlsx"


def get_pdf_filename(url: str | None, br_id: Any) -> str:
	"""Get the filename from the URL, or use the report ID."""

	if url:
		filename = unquote(Path(urlparse(url).path).name)

		if filename and filename.lower().endswith(".pdf"):
			return filename

	# Some PDF URLs have no filename or .pdf extension.
	return f"{br_id}.pdf"

def save_reports_to_excel(reports: list[dict[str, Any]], file_path: str | Path = OUTPUT_EXCEL_FILE) -> None:
	"""Save report metadata and download status to Excel."""

	file_path = Path(file_path)
	file_path.parent.mkdir(parents=True, exist_ok=True)

	workbook = Workbook()
	worksheet = workbook.active
	worksheet.title = "Downloaded Reports"

	worksheet.append([
		"br_id",
		"pdf_link",
		"backup_link",
		"successful_url",
		"pdf_filename",
		"pdf_path",
		"status"
	])

	for report in reports:
		worksheet.append([
			report["br_id"],
			report["pdf_link"],
			report["backup_link"],
			report.get("successful_url"),
			report.get("pdf_filename"),
			report.get("pdf_path"),
			report["status"]
		])

	workbook.save(file_path)
	workbook.close()

def read_reports_from_excel(worksheet) -> list[dict[str, Any]]:
	"""Read report metadata from an Excel worksheet."""

	rows = worksheet.iter_rows()
	
	# Skip the header row.
	header_cells = next(rows, None)
	if header_cells is None:
		return []

	# Read all report metadata before downloading.
	reports: list[dict[str, Any]] = []

	for row in rows:
		id_cell = row[0] if len(row) > 0 else None
		primary_cell = row[1] if len(row) > 1 else None
		backup_cell = row[2] if len(row) > 2 else None

		# Skips all empty cells
		if all(
			cell is None or (
				cell.value is None and cell.hyperlink is None
			)
			for cell in (id_cell, primary_cell, backup_cell)
		):
			continue

		# Get the report ID and the two URLs
		br_id = id_cell.value if id_cell else None

		primary_url = (
			primary_cell.hyperlink.target
			if primary_cell and primary_cell.hyperlink
			else primary_cell.value if primary_cell else None
		)

		backup_url = (
			backup_cell.hyperlink.target
			if backup_cell and backup_cell.hyperlink
			else backup_cell.value if backup_cell else None
		)

		reports.append(
			{
				"br_id": br_id,
				"pdf_link": primary_url,
				"backup_link": backup_url,
				"pdf_path": None,
				"pdf_filename": None,
				"successful_url": None,
				"status": "Pending"
			}
		)

	return reports

def process_report(report: dict[str, Any]) -> None:
	"""Download and save one report, updating its metadata."""

	br_id = report["br_id"]
	primary_url = report["pdf_link"]
	backup_url = report["backup_link"]

	print(f"Checking report ID: {br_id}")

	pdf_content = download_pdf(primary_url)
	successful_url = primary_url if pdf_content is not None else None

	if pdf_content is None and backup_url:
		print(
			f"Primary URL failed. "
			f"Trying backup for ID: {br_id}"
		)

		pdf_content = download_pdf(backup_url)

		if pdf_content is not None:
			successful_url = backup_url

	if pdf_content is not None:
		filename = get_pdf_filename(successful_url, br_id)

		# Prefix the ID to prevent filename collision
		filename = f"{br_id}_{filename}"
		pdf_path = OUTPUT_DIR / filename

		try:
			pdf_path.write_bytes(pdf_content)

			report["successful_url"] = successful_url
			report["pdf_filename"] = filename
			report["pdf_path"] = str(pdf_path)
			report["status"] = "downloaded"

			print(
				f"Valid PDF saved for ID: {br_id} "
				f"using {successful_url}"
			)

		except OSError as error:
			report["status"] = "failed"
			print(
				f"Could not save PDF for ID {br_id}: {error}"
			)
	else:
		report["status"] = "failed"
		print(f"No valid PDF found for ID: {br_id}")


def load_reports(file_path: str | Path = EXCEL_FILE) -> list[dict[str, Any]]:
	"""Read reports, download each one once, and save the results."""

	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

	workbook = load_workbook(file_path, data_only=True)

	try:
		worksheet = workbook.active

		# Read all report metadata
		reports = read_reports_from_excel(worksheet)
		
		# Create the Excel file before downloading anything and save the initial report list
		save_reports_to_excel(reports)

		# Try each URL and record which one actually works.
		for report in reports:
			process_report(report)

			# Save progress after each report.
			save_reports_to_excel(reports)

		return reports
	
	finally:
		workbook.close()