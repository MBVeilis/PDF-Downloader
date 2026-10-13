from excel_service import load_reports

def main():
    reports = load_reports()
    print(f"Indlæste {len(reports)} rapporter fra Excel.")

if __name__ == "__main__":
    main()