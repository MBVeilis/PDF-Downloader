from typing import Any
from pathlib import Path
from urllib.parse import urlparse, unquote

from pdf_downloader import download_pdf

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "pdf_files"

def get_pdf_filename(url: str | None, br_id: Any) -> str:
	"""Get the filename from the URL, or use the domain name as fallback."""

	if url:
		parsed_url = urlparse(url)
		filename = unquote(Path(urlparse(url).path).name)

		if filename and filename.lower().endswith(".pdf"):
			return filename

		domain = parsed_url.netloc

		if domain:
			return f"{domain}.pdf"

	# Some PDF URLs have no filename or .pdf extension.
	return f"{br_id}.pdf"
        

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