from openpyxl import Workbook

from excel_service import EXCEL_FILE, load_reports


def test_load_reports_keeps_br_id_and_reads_primary_and_backup_links(tmp_path, monkeypatch):
    file_path = tmp_path / "reports.xlsx"
    
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["id", "url", "alt url"])
    worksheet.append([1, "https://example.com/report.pdf", "Open backup"])
    worksheet["C2"].hyperlink = "https://backup.example.com/report.pdf"
    workbook.save(file_path)
    workbook.close()

    # Avoid real downloads and output-file creation in this test.
    # lambda is a nameless function and report is the functions parameter
    monkeypatch.setattr("excel_service.process_report", lambda report: None)
    monkeypatch.setattr(
        "excel_service.save_reports_to_excel",
        lambda reports: None
    )

    reports = load_reports(file_path)

    assert reports == [
        {
            "br_id": 1,
            "pdf_link": "https://example.com/report.pdf",
            "backup_link": "https://backup.example.com/report.pdf",
            "pdf_path": None,
            "pdf_filename": None,
            "successful_url": None,
            "status": "Pending"
        }
    ]

def test_default_excel_file_exists_and_loads(monkeypatch):
    assert EXCEL_FILE.is_file()

    # Avoid real downloads and output-file creation.
    monkeypatch.setattr("excel_service.process_report", lambda report: None)
    monkeypatch.setattr(
        "excel_service.save_reports_to_excel",
        lambda reports: None,
    )

    reports = load_reports()

    assert isinstance(reports, list)