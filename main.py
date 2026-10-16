from excel_service import load_reports

def main():
    reports = load_reports()

    downloaded = sum(
        report["status"] == "downloaded"
        for report in reports
    )

    failed = sum(
        report["status"] == "failed"
        for report in reports
    )

    print(f"Processed {len(reports)} reports.")
    print(f"PDFs downloaded: {downloaded}")
    print(f"PDFs failed: {failed}")
    print(f"Results saved to pdf_files/downloaded_reports.xlsx")

if __name__ == "__main__":
    main()