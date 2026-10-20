import report_processor
import asyncio
import pytest


def make_report(br_id=1, backup=None):
    return {
        "br_id": br_id,
        "pdf_link": "https://example.com/report.pdf",
        "backup_link": backup,
        "successful_url": None,
        "pdf_filename": None,
        "pdf_path": None,
        "status": "Pending",
    }


# -------------------------------
# TESTS get_pdf_filename FUNCTION
# -------------------------------

def test_get_pdf_filename_uses_pdf_path_name():
    url = "https://example.com/reports/annual-report-2025.pdf"

    assert report_processor.get_pdf_filename(url, 1) == (
        "annual-report-2025.pdf"
    )


def test_get_pdf_filename_uses_domain_without_pdf_filename():
    url = "https://investor.example.com/static/12345"

    assert report_processor.get_pdf_filename(url, 2) == (
        "investor.example.com.pdf"
    )


def test_get_pdf_filename_without_url():
    assert report_processor.get_pdf_filename(None, 5) == "5.pdf"


def test_get_pdf_filename_handles_uppercase_extension():
    url = "https://example.com/ANNUAL-REPORT.PDF"

    assert report_processor.get_pdf_filename(url, 10) == (
        "ANNUAL-REPORT.PDF"
    )


def test_get_pdf_filename_without_domain():
    assert report_processor.get_pdf_filename("/some/path", 11) == "11.pdf"

# ------------------------------------------------------
# TESTS process_report FUNCTION
# USES monkeypatch FOR MOCKING AND TO SIMULATE DOWNLOADS
# ------------------------------------------------------

@pytest.mark.asyncio
async def test_process_report_download_success(monkeypatch, tmp_path):
    report = make_report()
    history = {}
    history_file = tmp_path / "history.json"
    content = b"%PDF-1.4 test content"

    async def fake_download(url, session):
        return content

    def fake_record(report, history, file_path):
        history[str(report["br_id"])] = {
            "status": report["status"],
            "pdf_filename": report["pdf_filename"],
        }

    monkeypatch.setattr(report_processor, "download_pdf", fake_download)
    monkeypatch.setattr(report_processor, "record_report", fake_record)

    result = await report_processor.process_report(
        report, None, history, history_file,
        asyncio.Semaphore(1), tmp_path,
    )

    assert result["status"] == "downloaded"
    assert result["successful_url"] == report["pdf_link"]
    assert result["pdf_filename"] == "1_report.pdf"
    assert (tmp_path / "1_report.pdf").read_bytes() == content
    assert history["1"]["status"] == "downloaded"


@pytest.mark.asyncio
async def test_process_report_uses_backup_when_primary_fails(
    monkeypatch, tmp_path
):
    report = make_report(2, "https://backup.example.com/report.pdf")
    history = {}

    async def fake_download(url, session):
        if url == report["pdf_link"]:
            return None
        return b"%PDF-1.4 backup content"

    monkeypatch.setattr(report_processor, "download_pdf", fake_download)
    monkeypatch.setattr(
        report_processor,
        "record_report",
        lambda report, history, file_path: None,
    )

    result = await report_processor.process_report(
        report, None, history, tmp_path / "history.json",
        asyncio.Semaphore(1), tmp_path,
    )

    assert result["status"] == "downloaded"
    assert result["successful_url"] == report["backup_link"]
    assert (tmp_path / "2_report.pdf").is_file()


@pytest.mark.asyncio
async def test_process_report_fails_when_both_urls_fail(
    monkeypatch, tmp_path
):
    report = make_report(3, "https://backup.example.com/broken.pdf")
    history = {}
    recorded = []

    async def fake_download(url, session):
        return None

    def fake_record(report, history, file_path):
        recorded.append(report["status"])

    monkeypatch.setattr(report_processor, "download_pdf", fake_download)
    monkeypatch.setattr(report_processor, "record_report", fake_record)

    result = await report_processor.process_report(
        report, None, history, tmp_path / "history.json",
        asyncio.Semaphore(1), tmp_path,
    )

    assert result["status"] == "failed"
    assert result["successful_url"] is None
    assert recorded == ["failed"]
    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_process_report_preserves_existing_pdf_on_write_failure(
    monkeypatch, tmp_path
):
    report = make_report(4)
    existing = tmp_path / "4_report.pdf"
    existing.write_bytes(b"%PDF-1.4 old content")

    async def fake_download(url, session):
        return b"%PDF-1.4 new content"

    monkeypatch.setattr(report_processor, "download_pdf", fake_download)
    monkeypatch.setattr(
        report_processor,
        "record_report",
        lambda report, history, file_path: None,
    )

    original_write_bytes = report_processor.Path.write_bytes

    def fake_write_bytes(self, content):
        if self.name.endswith(".part"):
            raise OSError("Simulated write failure")
        return original_write_bytes(self, content)

    monkeypatch.setattr(
        report_processor.Path, "write_bytes", fake_write_bytes
    )

    result = await report_processor.process_report(
        report, None, {}, tmp_path / "history.json",
        asyncio.Semaphore(1), tmp_path,
    )

    assert result["status"] == "failed"
    assert existing.read_bytes() == b"%PDF-1.4 old content"