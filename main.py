from excel_service import load_reports

def main():
    try:
        reports = load_reports()

        downloaded = sum(
            report.get("status") == "downloaded"
            for report in reports
        )
        failed = sum(
            report.get("status") == "failed"
            for report in reports
        )
        skipped = sum(
            report.get("status") == "skipped"
            for report in reports
        )

        print("\nDownload completed.")
        print(f"Reports processed: {len(reports)}")
        print(f"PDFs downloaded: {downloaded}")
        print(f"PDFs skipped: {skipped}")
        print(f"PDFs failed: {failed}")
        print("PDF folder: pdf_files/")
        print("Excel report: pdf_files/downloaded_reports.xlsx")

    except Exception as error:
        print(f"\nThe downloader could not complete: {error}")

    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()