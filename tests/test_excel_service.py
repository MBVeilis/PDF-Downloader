from openpyxl import Workbook

from excel_service import EXCEL_FILE, load_reports


def test_load_reports_reads_values_and_hyperlinks(tmp_path):
    file_path = tmp_path / "reports.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Company", "Report link"])
    worksheet.append(["Example Ltd", "Open report"])
    worksheet["B2"].hyperlink = "https://example.com/report.pdf"
    workbook.save(file_path)

    assert load_reports(file_path) == [
        {
            "Company": "Example Ltd",
            "Report link": "https://example.com/report.pdf",
        }
    ]


def test_default_excel_file_exists_and_loads():
    assert EXCEL_FILE.is_file()
    assert isinstance(load_reports(), list)