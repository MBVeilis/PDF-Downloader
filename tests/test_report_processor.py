import report_processor

# -------------------------------
# TESTS get_pdf_filename FUNCTION
# -------------------------------

def test_get_pdf_filename_uses_path_name_when_url_has_pdf_filename():
    url = (
        "https://www.novonordisk.com/content/dam/nncorp/global/en/investors/irmaterial/annual_report/2025/novo-nordisk-annual-report-2024.pdf"
    )

    result = report_processor.get_pdf_filename(url, br_id=1)

    assert result == "novo-nordisk-annual-report-2024.pdf"

def test_get_pdf_filename_uses_domain_when_url_has_no_pdf_filename():
    url = (
        "https://investor.maersk.com/static-files/31bf05a1-6f0c-4fbd-a3c7-3f58e044f798"
    )
    
    result = report_processor.get_pdf_filename(url, br_id=6)

    assert result == "investor.maersk.com.pdf"

def test_get_pdf_filename_when_url_does_not_exist():
    
    result = report_processor.get_pdf_filename(None, br_id=5)

    assert result == "5.pdf"

def test_get_pdf_filename_handles_uppercase_pdf_extension():
    url = "https://example.com/reports/ANNUAL-REPORT.PDF"

    result = report_processor.get_pdf_filename(url, br_id=10)

    assert result == "ANNUAL-REPORT.PDF"

def test_get_pdf_filename_uses_br_id_when_url_has_no_domain():
    url = "/some/path"

    result = report_processor.get_pdf_filename(url, br_id=11)

    assert result == "11.pdf"

# ------------------------------------------------------
# TESTS process_report FUNCTION
# USES monkeypatch FOR MOCKING AND TO SIMULATE DOWNLOADS
# ------------------------------------------------------

def test_process_report_download_success(monkeypatch, tmp_path):
    report = {
        "br_id": 1,
        "pdf_link": "https://example.com/report.pdf",
        "backup_link": None,
        "successful_url": None,
        "pdf_filename": None,
        "pdf_path": None,
        "status": "Pending"
    }

    pdf_content = b"%PDF-text-content"

    def fake_download_pdf(url):
        return pdf_content

    monkeypatch.setattr(
        report_processor,
        "download_pdf",
        fake_download_pdf
    )
    monkeypatch.setattr(report_processor, "OUTPUT_DIR", tmp_path)

    report_processor.process_report(report)

    assert report["status"] == "downloaded"
    assert report["successful_url"] == report["pdf_link"]
    assert report["pdf_filename"] == "1_report.pdf"
    assert (tmp_path / "1_report.pdf").read_bytes() == pdf_content
    

def test_process_report_uses_backup_url_when_primary_fails(monkeypatch, tmp_path):
    report = {
        "br_id": 2,
        "pdf_link": "https://example.com/broken.pdf",
        "backup_link": "https://backup.example.com/report.pdf",
        "successful_url": None,
        "pdf_filename": None,
        "pdf_path": None,
        "status": "Pending"
    }

    def fake_download_pdf(url):
        if url == report["pdf_link"]:
            return None
        return b"%PDF-backup-content"

    monkeypatch.setattr(
        report_processor,
        "download_pdf",
        fake_download_pdf
    )
    monkeypatch.setattr(report_processor, "OUTPUT_DIR", tmp_path)

    report_processor.process_report(report)

    assert report["status"] == "downloaded"
    assert report["successful_url"] == report["backup_link"]
    assert (tmp_path / "2_report.pdf").read_bytes() == b"%PDF-backup-content"

def test_process_report_fails_when_both_urls_fail(monkeypatch, tmp_path):
    report = {
        "br_id": 3,
        "pdf_link": "https://example.com/broken.pdf",
        "backup_link": "https://backup.example.com/broken.pdf",
        "successful_url": None,
        "pdf_filename": None,
        "pdf_path": None,
        "status": "Pending"
    }

    def fake_download_pdf(url):
        return None

    monkeypatch.setattr(
        report_processor,
        "download_pdf",
        fake_download_pdf
    )
    monkeypatch.setattr(report_processor, "OUTPUT_DIR", tmp_path)

    report_processor.process_report(report)

    assert report["status"] == "failed"
    assert report["successful_url"] is None
    assert report["pdf_filename"] is None
    assert report["pdf_path"] is None
    assert list(tmp_path.iterdir()) == []

def test_process_report_fails_when_saving_pdf_raises_oserror(monkeypatch, tmp_path):
    report = {
        "br_id": 4,
        "pdf_link": "https://example.com/report.pdf",
        "backup_link": None,
        "successful_url": None,
        "pdf_filename": None,
        "pdf_path": None,
        "status": "Pending"
    }

    def fake_download_pdf(url):
        return b"%PDF-test-content"

    def fake_write_bytes(self, content):
        raise OSError("Simulated file write error")

    monkeypatch.setattr(
        report_processor,
        "download_pdf",
        fake_download_pdf
    )
    monkeypatch.setattr(report_processor, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(
        report_processor.Path,
        "write_bytes",
        fake_write_bytes
    )

    report_processor.process_report(report)

    assert report["status"] == "failed"