import pytest

from history_service import (
    is_report_downloaded,
    load_history,
    record_report,
    reset_history,
    save_history,
)


def test_load_history_returns_empty_dict_when_missing(tmp_path):
    path = tmp_path / "history.json"

    assert load_history(path) == {}


def test_save_and_load_history(tmp_path):
    path = tmp_path / "history.json"
    history = {"123": {"status": "downloaded"}}

    save_history(history, path)

    assert load_history(path) == history


def test_invalid_json_raises_clear_error(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not read download history"):
        load_history(path)


def test_history_must_be_json_object(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError):
        load_history(path)


def test_reset_history_does_not_delete_pdf_files(tmp_path):
    history_path = tmp_path / "history.json"
    pdf_path = tmp_path / "123_report.pdf"

    save_history({"123": {"status": "downloaded"}}, history_path)
    pdf_path.write_bytes(b"%PDF-1.4 test")

    reset_history(history_path)

    assert not history_path.exists()
    assert pdf_path.exists()


def test_downloaded_report_is_skipped_when_file_is_valid(tmp_path):
    pdf_path = tmp_path / "123_report.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test content")

    report = {
        "br_id": 123,
        "pdf_link": "https://example.com/report.pdf",
        "backup_link": None,
        "successful_url": "https://example.com/report.pdf",
        "pdf_filename": pdf_path.name,
        "pdf_path": str(pdf_path),
        "status": "downloaded",
    }

    history = {}
    history_path = tmp_path / "history.json"
    record_report(report, history, history_path)

    assert is_report_downloaded(report, history, tmp_path)


def test_deleted_pdf_is_not_skipped(tmp_path):
    report = {
        "br_id": 123,
        "pdf_link": "https://example.com/report.pdf",
        "backup_link": None,
    }

    history = {
        "123": {
            "status": "downloaded",
            "pdf_link": report["pdf_link"],
            "backup_link": None,
            "pdf_filename": "123_report.pdf",
            "sha256": "some-old-checksum",
        }
    }

    assert not is_report_downloaded(report, history, tmp_path)


def test_changed_source_link_is_not_skipped(tmp_path):
    pdf_path = tmp_path / "123_report.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    report = {
        "br_id": 123,
        "pdf_link": "https://example.com/new-report.pdf",
        "backup_link": None,
    }

    history = {
        "123": {
            "status": "downloaded",
            "pdf_link": "https://example.com/old-report.pdf",
            "backup_link": None,
            "pdf_filename": pdf_path.name,
        }
    }

    assert not is_report_downloaded(report, history, tmp_path)