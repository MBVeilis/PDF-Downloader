from openpyxl import Workbook

from excel_service import EXCEL_FILE, load_reports


def test_load_reports_reads_primary_and_backup_links_from_columns_a_and_b(tmp_path):
    file_path = tmp_path / "reports.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Primary PDF", "Backup PDF"])
    worksheet.append(["https://example.com/report.pdf", "Open backup"])
    worksheet["B2"].hyperlink = "https://backup.example.com/report.pdf"
    workbook.save(file_path)

    assert load_reports(file_path) == [
        {
            "pdf_link": "https://example.com/report.pdf",
            "backup_link": "https://backup.example.com/report.pdf",
        }
    ]


def test_default_excel_file_exists_and_loads():
    assert EXCEL_FILE.is_file()
    assert isinstance(load_reports(), list)