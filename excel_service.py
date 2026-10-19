from pathlib import Path
from typing import Any
from openpyxl import load_workbook, Workbook

from excel_reader import read_reports_from_excel
from report_processor import process_report


BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE = BASE_DIR / "xlsx-file" / "GRI_2017_2025.xlsx"

OUTPUT_DIR = BASE_DIR / "pdf_files"
OUTPUT_EXCEL_FILE = OUTPUT_DIR / "downloaded_reports.xlsx"


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