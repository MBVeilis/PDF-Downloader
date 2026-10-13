from excel_service import load_reports

def main():
    reports = load_reports()
    print(f"Loaded {len(reports)} reports from Excel.")

if __name__ == "__main__":
    main()