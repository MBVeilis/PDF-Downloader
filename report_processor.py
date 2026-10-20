import asyncio
import re
import aiohttp

from typing import Any
from pathlib import Path
from urllib.parse import urlparse, unquote
from pdf_downloader import download_pdf
from history_service import record_report


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "pdf_files"


def get_pdf_filename(url: str | None, br_id: Any) -> str:
	"""Get the filename from the URL and build it containing the report's BR identifier."""

	if url:
		parsed_url = urlparse(url)
		filename = unquote(Path(parsed_url.path).name)

		if filename and filename.lower().endswith(".pdf"):
			pass
		elif parsed_url.netloc:
			filename = f"{parsed_url.netloc}.pdf"
		else:
			# Some PDF URLs have no filename or .pdf extension.
			filename = f"{br_id}.pdf"
	else:
		filename = f"{br_id}.pdf"

	# Prevent path traversal and invalid Windows filenmae characters.
	filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
	filename = filename.strip(" .")

	return filename or f"{br_id}.pdf"
        

async def process_report(
		report: dict[str, Any],
		session: aiohttp.ClientSession,
		history: dict[str, Any],
		history_file: str | Path,
		semaphore: asyncio.Semaphore,
		output_dir: str | Path = OUTPUT_DIR
) -> dict[str, Any]:
	"""Download and save one report, updating its metadata and using the backup URL when necessary."""

	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	br_id = report["br_id"]
	report["error"] = None

	print(f"Checking report ID: {br_id}")

	try:
		async with semaphore:
			pdf_content = await download_pdf(
				report.get("pdf_link"), session
			)
			successful_url = (
				report.get("pdf_link")
				if pdf_content is not None
				else None
			)

			if pdf_content is None and report.get("backup_link"):
				pdf_content = await download_pdf(
					report["backup_link"], session
				)

				if pdf_content is not None:
					successful_url = report["backup_link"]

		if pdf_content is None:
			report.update(
				status="failed",
				successful_url=None,
				pdf_filename=None,
				pdf_path=None,
				error="Both the primary and backup URLs failed."
			)
		else:
			# Keep get_pdf_filename() compatible with the existing tests.
			filename = f"{br_id}_{get_pdf_filename(successful_url, br_id)}"
			pdf_path = output_dir / filename
			temporary_path = pdf_path.with_name(pdf_path.name + ".part")

			try:
				# Write the new PDF first, preserving an existing PDF if
				# the write fails before the replacement.
				temporary_path.write_bytes(pdf_content)

				if b"%PDF-" not in temporary_path.read_bytes()[:1024]:
					raise ValueError("Downloaded content is not a valid PDF.")

				temporary_path.replace(pdf_path)

			finally:
				if temporary_path.exists():
					temporary_path.unlink()

			report.update(
				successful_url=successful_url,
				pdf_filename=filename,
				pdf_path=str(pdf_path),
				status="downloaded",
				error=None
			)

			print(f"Downloaded report ID: {br_id}")

	except (OSError, ValueError) as error:
		report.update(
			status="failed",
			error=str(error)
		)
		print(f"Could not save report ID {br_id}: {error}")

	# Save each result immediatly so completed work is remembered
	record_report(report, history, history_file)

	return report