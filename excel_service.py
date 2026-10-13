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

		headers = [
			str(cell.value).strip() if cell.value is not None else f"column_{index + 1}"
			for index, cell in enumerate(header_cells)
		]
		reports = []
		for row in rows:
			if all(cell.value is None and cell.hyperlink is None for cell in row):
				continue

			reports.append(
				{
					headers[index]: (
						cell.hyperlink.target if cell.hyperlink else cell.value
					)
					for index, cell in enumerate(row)
				}
			)
		return reports
	finally:
		workbook.close()