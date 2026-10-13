from openpyxl import Workbook

from excel_service import EXCEL_FILE, load_reports


def test_load_reports_keeps_br_id_and_reads_primary_and_backup_links(tmp_path):
    file_path = tmp_path / "reports.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["id", "url", "alt url"])
    worksheet.append([472, "https://example.com/report.pdf", "Open backup"])
    worksheet["C2"].hyperlink = "https://backup.example.com/report.pdf"
    workbook.save(file_path)

    assert load_reports(file_path) == [
        {
            "br_id": 472,
            "pdf_link": "https://example.com/report.pdf",
            "backup_link": "https://backup.example.com/report.pdf",
        }
    ]


def test_default_excel_file_exists_and_loads():
    assert EXCEL_FILE.is_file()
    assert isinstance(load_reports(), list)