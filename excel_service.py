from pathlib import Path
from typing import Any

from openpyxl import load_workbook


EXCEL_FILE = (
	Path(__file__).resolve().parent / "xlsx-file" / "GRI_2017_2025.xlsx"
)


def load_reports(file_path: str | Path = EXCEL_FILE) -> list[dict[str, Any]]:
	workbook = load_workbook(file_path, data_only=True)
	try:
		worksheet = workbook.active
		rows = worksheet.iter_rows()
		header_cells = next(rows, None)
		if header_cells is None:
			return []

		reports = []
		for row in rows:
			id_cell = row[0] if row else None
			primary_cell = row[1] if len(row) > 1 else None
			backup_cell = row[2] if len(row) > 2 else None
			if all(
				cell is None or (cell.value is None and cell.hyperlink is None)
				for cell in (id_cell, primary_cell, backup_cell)
			):
				continue

			reports.append(
				{
					"br_id": id_cell.value if id_cell else None,
					"pdf_link": (
						primary_cell.hyperlink.target
						if primary_cell and primary_cell.hyperlink
						else primary_cell.value if primary_cell else None
					),
					"backup_link": (
						backup_cell.hyperlink.target
						if backup_cell and backup_cell.hyperlink
						else backup_cell.value if backup_cell else None
					),
				}
			)
		return reports
	finally:
		workbook.close()