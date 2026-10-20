import hashlib
import json

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "download_history.json"


def load_history(file_path: str | Path = HISTORY_FILE) -> dict[str, Any]:
    """Load download history, creating an empty history if necessary."""

    file_path = Path(file_path)

    if not file_path.exists():
        return {}

    try:
        with file_path.open("r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, dict):
            raise ValueError("History must be a JSON object.")

        return history

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        raise ValueError (
            f"Could not read download history: {file_path}. "
            "Back up the file and repair or reset it before continuing."
        ) from error


def save_history(history: dict[str, Any], file_path: str | Path = HISTORY_FILE) -> None:
    """Save history atomically to reduce the risk of a corrupt JSON file."""

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
            file.flush()

        temporary_file.replace(file_path)

    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def file_sha256(file_path: str | Path) -> str:
    """Calculate a file's SHA-256 checksum."""

    digest = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def is_valid_pdf(file_path: str | Path) -> bool:
    """Check that a file exists and contains a PDF header."""

    file_path = Path(file_path)

    try:
        if not file_path.is_file() or file_path.stat().st_size == 0:
            return False

        with file_path.open("rb") as file:
            header = file.read(1024)

        return b"%PDF-" in header

    except OSError:
        return False


def is_report_downloaded(report: dict[str, Any], history: dict[str, Any], output_dir: str | Path) -> bool:
    """Return True only if the previous download is still trustworthy."""

    br_id = str(report["br_id"])
    entry = history.get(br_id)

    if not isinstance(entry, dict):
        return False

    if entry.get("status") != "downloaded":
        return False

    # If the source links changed, try the report again.
    if entry.get("pdf_link") != report.get("pdf_link"):
        return False

    if entry.get("backup_link") != report.get("backup_link"):
        return False

    filename = entry.get("pdf_filename")

    if not isinstance(filename, str) or Path(filename).name != filename:
        return False

    pdf_path = Path(output_dir) / filename

    if not is_valid_pdf(pdf_path):
        return False

    try:
        return file_sha256(pdf_path) == entry.get("sha256")
    except OSError:
        return False


def record_report(report: dict[str, Any], history: dict[str, Any], file_path: str | Path = HISTORY_FILE) -> None:
    """Record the latest result for a report and presist it immediately."""

    br_id = str(report["br_id"])
    pdf_path = report.get("pdf_path")
    checksum = None

    if report.get("status") == "downloaded" and pdf_path:
        try:
            checksum = file_sha256(pdf_path)
        except OSError:
            report["status"] = "failed"
            report["error"] = "Could not verify the saved PDF."
            report["pdf_path"] = None
            report["pdf_filename"] = None

    history[br_id] = {
        "br_id": br_id,
        "pdf_link": report.get("pdf_link"),
        "backup_link": report.get("backup_link"),
        "successful_url": report.get("successful_url"),
        "pdf_filename": report.get("pdf_filename"),
        "pdf_path": report.get("pdf_path"),
        "status": report.get("status"),
        "sha256": checksum,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "error": report.get("error")
    }

    save_history(history, file_path)


def reset_history(file_path: str | Path = HISTORY_FILE) -> None:
    """Delete download history without deleting any PDF files."""

    file_path = Path(file_path)

    if file_path.exists():
        file_path.unlink()