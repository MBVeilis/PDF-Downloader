from typing import Any

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