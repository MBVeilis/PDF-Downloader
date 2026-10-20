# PDF Downloader

A desktop application for downloading annual reports as PDF files from links stored in an Excel spreadsheet.

The application automates the download process, organises PDF files in a single folder, keeps track of previous downloads, and generates an Excel report containing the results.

It includes a graphical user interface (GUI), allowing users to download and manage reports without needing to work directly with the command line.

## Table of Contents

* [Features](#features)
* [How It Works](#how-it-works)
* [Requirements](#requirements)
* [Installation](#installation)
* [Starting the Application](#starting-the-application)
* [Using the Application](#using-the-application)
* [Downloading Reports Again](#downloading-reports-again)
* [Where Are My Files Saved?](#where-are-my-files-saved)
* [Understanding the Excel Report](#understanding-the-excel-report)
* [Understanding Download History](#understanding-download-history)
* [Troubleshooting](#troubleshooting)
* [Project Structure](#project-structure)
* [Running Tests](#running-tests)
* [Important Notes](#important-notes)

## Features

* **Automatic PDF downloads:** Downloads reports using links provided in an Excel spreadsheet.
* **Backup links:** Attempts to download a report from an alternative URL if the primary URL fails.
* **BR-number identification:** Includes the report's BR number in the downloaded PDF filename.
* **Centralised storage:** Keeps downloaded PDF files together in one folder.
* **Download history:** Remembers previous downloads to avoid unnecessary downloads.
* **Download everything again:** Resets the download history and attempts to download all reports again.
* **Excel summary:** Generates a spreadsheet showing the status and details of each report.
* **Progress tracking:** Displays progress and the number of downloaded, skipped, and failed reports.
* **Concurrent downloads:** Processes multiple reports concurrently to improve performance.
* **Error handling:** Records individual download failures without necessarily stopping the entire process.
* **Automated tests:** Includes tests for Excel handling, download history, and PDF processing.

## How It Works

The application follows a straightforward process:

1. Reads the list of reports from the input Excel spreadsheet.
2. Checks whether each report has already been downloaded and whether its existing PDF can be reused.
3. Downloads reports that need processing.
4. Tries the backup link if the primary link fails.
5. Saves successfully downloaded PDF files in the output folder.
6. Updates the download history.
7. Generates an Excel summary containing the results.

The application handles these steps automatically. Users mainly need to choose whether to start a normal download or download everything again.

## Requirements

The following are required to run the application:

* Windows is the primary target platform.
* Python must be installed.
* The project files must be available on the computer.
* The required Python packages must be installed.
* The input Excel spreadsheet must exist in the expected location.
* An internet connection is required to download reports.

The application uses Python libraries such as:

* `aiohttp` for asynchronous HTTP requests.
* `openpyxl` for reading and writing Excel files.
* `pytest` for automated testing.

Tkinter is used to provide the graphical user interface.

## Installation

### 1. Obtain the project

Download or clone the project repository and place it in a folder on your computer.

For example:

```text
C:\Users\YourName\source\repos\PDF-downloader
```

### 2. Open the project folder

Make sure the project contains the necessary Python files, including:

* `main.py`
* `gui.py`
* `pdf_downloader.py`
* `excel_service.py`
* `excel_reader.py`
* `report_processor.py`
* `history_service.py`

The project should also contain the `tests/` and `xlsx-file/` folders.

### 3. Create a virtual environment

If the project already has a working `.venv` folder, you can use the existing environment.

Otherwise, open PowerShell in the project directory and run:

```powershell
python -m venv .venv
```

A virtual environment keeps the project's Python packages separate from other Python projects on your computer.

### 4. Activate the virtual environment

Run:

```powershell
.\.venv\Scripts\Activate.ps1
```

When activation succeeds, the terminal will normally show `(.venv)` at the beginning of the command prompt.

If PowerShell prevents activation, follow your organisation's approved Python setup instructions or use the supplied batch file if it handles environment activation automatically.

### 5. Install dependencies

If the project contains a `requirements.txt` file, install the required packages with:

```powershell
python -m pip install -r requirements.txt
```

If the dependencies have already been installed in the existing virtual environment, this step may not be necessary.

## Starting the Application

The recommended way to start the application is to use the supplied Windows batch file (`.bat`).

1. Open the project folder in File Explorer.
2. Locate the application's batch file.
3. Double-click the file.
4. Wait for the application window to appear.

The batch file should start the application using the project's Python environment, provided it has been configured accordingly.

### Starting the application manually

You can also start the application through PowerShell.

First, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python main.py
```

The graphical user interface should open.

## Using the Application

The application window contains download controls, progress information, a results summary, and an activity log.

### Start download

Click **Start download** to process the input spreadsheet.

During a normal run, the application:

* Reads the report list.
* Checks the download history.
* Skips reports whose existing PDF files are valid and can be reused.
* Downloads reports that need processing.
* Attempts backup links when necessary.
* Updates the download history and Excel summary.

This is the recommended button for everyday use.

### Download everything again

Click **Download everything again** when you want to reset the download history and attempt every report again.

The application asks for confirmation before continuing.

See [Downloading Reports Again](#downloading-reports-again) for details.

### Monitor progress

The interface displays the current progress and the results of the download process.

**Downloaded**

The number of reports successfully downloaded during the current run.

**Skipped**

The number of reports that did not need to be downloaded again.

**Failed**

The number of reports that could not be downloaded successfully.

**Progress**

The number of processed reports compared with the total number of reports, including the overall percentage.

The activity log also shows individual report results using their BR numbers.

### Open PDF-folder

Click **Open PDF-folder** to open the folder containing the downloaded PDF files.

### Open Excel-report

Click **Open Excel-report** to open the Excel summary generated by the application.

If the Excel summary has not yet been created, the application displays a warning.

## Downloading Reports Again

The **Download everything again** button provides a convenient way to retry all reports.

This is useful when:

* A previous download failed.
* A website was temporarily unavailable.
* A report link has been updated.
* You want to refresh existing downloads.
* You want to retry the entire report list.

### What happens when you click the button?

1. The application asks for confirmation.
2. The existing download history is reset.
3. All reports in the input spreadsheet are attempted again.
4. Successful downloads are saved in the PDF output folder.
5. The history is updated as the reports are processed.
6. The Excel summary is regenerated.

### Are existing PDF files deleted?

No. Resetting the history does not automatically delete existing PDF files.

If a report is downloaded successfully and has the same filename as an existing PDF, the existing file may be overwritten.

If the new download fails, an existing PDF is not automatically deleted simply because the new attempt failed.

**Important:** Downloading everything again resets the history, not the PDF folder itself.

## Where Are My Files Saved?

The application uses the project directory and its configured output paths to store files.

The default input spreadsheet is:

```text
xlsx-file/GRI_2017_2025.xlsx
```

The output folder is:

```text
pdf_files/
```

The Excel summary is saved as:

```text
pdf_files/downloaded_reports.xlsx
```

The download history is stored separately in the project root:

```text
download_history.json
```

### PDF files

Downloaded PDF files are stored together in `pdf_files/`.

Filenames include the corresponding BR number where the filename-generation logic supports it.

For example:

```text
123_report.pdf
456_report.pdf
789_report.pdf
```

These are illustrative filenames. Actual filenames depend on the source URLs and the application's filename-generation rules.

### Excel summary

The file `downloaded_reports.xlsx` contains the results of the most recent processing run.

It can be opened using Microsoft Excel or another compatible spreadsheet application.

### Download history

The file `download_history.json` is stored in the project's root directory, alongside the main Python files.

It helps the application remember previous download results and determine whether an existing PDF can be reused.

## Understanding the Excel Report

The Excel summary provides an overview of the reports processed by the application.

The spreadsheet contains the following columns:

| Column           | Description                                   |
| ---------------- | --------------------------------------------- |
| `br_id`          | The BR number identifying the report.         |
| `pdf_link`       | The primary download URL.                     |
| `backup_link`    | The alternative download URL, if available.   |
| `successful_url` | The URL that successfully supplied the PDF.   |
| `pdf_filename`   | The filename of the downloaded PDF.           |
| `pdf_path`       | The location of the PDF file on the computer. |
| `status`         | The processing result for the report.         |
| `error`          | An error description, if an error occurred.   |

### Understanding report statuses

**Downloaded**

The report was downloaded successfully during the current run.

**Skipped**

The report was already downloaded, and the application determined that the existing file could be reused.

**Failed**

The application could not complete the download successfully.

The `error` column can help explain why the download failed.

A failed download does not necessarily mean the report does not exist. The website may be unavailable, the URL may have changed, or access may be restricted.

## Understanding Download History

The application stores download history in `download_history.json` in the project root directory.

This file is separate from both the PDF output folder and the Excel summary.

The history allows the application to determine whether a report has already been downloaded and whether the existing PDF can be reused.

During a normal run, a report may be skipped when:

* A matching history entry exists.
* The expected PDF file exists.
* The existing file satisfies the application's validation checks.
* The stored source information still matches the report being processed.

If the PDF is missing, invalid, or associated with a changed source link, the application can attempt the download again.

### Resetting the history

When **Download everything again** is selected, the application resets the history before processing the reports.

The history is then rebuilt as new results are recorded.

Existing PDF files are not automatically deleted.

The history and the Excel summary serve different purposes:

* **Download history:** Helps the application decide whether to download a report.
* **Excel summary:** Shows the results of the latest processing run.

Avoid manually editing or deleting the history file unless you understand the consequences.

## Troubleshooting

### The application does not start

Check that Python is installed and that the virtual environment and required packages are available.

Try starting the application manually:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

If an error appears in PowerShell, read the message carefully. It may identify a missing package, a configuration problem, or a missing file.

### The input Excel file cannot be found

The default input file is:

```text
xlsx-file/GRI_2017_2025.xlsx
```

Check that:

* The `xlsx-file` folder exists.
* The spreadsheet is present.
* The filename is correct.
* The file has not been moved or renamed.

### Some reports fail to download

Open `pdf_files/downloaded_reports.xlsx` and inspect the `error` column.

Possible causes include:

* The website is temporarily unavailable.
* The download URL is incorrect or outdated.
* The website blocks automated requests.
* The server redirects to a page that does not provide a PDF.
* Access requires authentication or other permissions.
* The internet connection is unavailable.

If appropriate, open the primary or backup URL in a web browser to check whether the report is accessible.

You can then use **Download everything again** to retry the reports.

### Reports are skipped instead of downloaded

This is normally expected behaviour.

The application skips reports when the download history and existing PDF indicate that the report can be reused.

If you want to retry every report, click **Download everything again** and confirm the operation.

### The Excel report cannot be saved

If the application cannot save `downloaded_reports.xlsx`, check whether the file is currently open in Microsoft Excel.

On Windows, Excel may lock the file and prevent the application from replacing it.

Close the spreadsheet and retry the operation.

Also check that:

* The output folder is writable.
* The disk has sufficient free space.
* The file is not locked by another application.

### One report fails, but the others continue

The application is designed to handle individual report errors without necessarily stopping the entire run.

Check the activity log and the corresponding row in the Excel summary to identify the failed BR number.

If the error appears temporary, retry the report by using **Download everything again**.

### The history does not appear to reset

Confirm that you used **Download everything again**, rather than **Start download**.

The first button resets the download history before processing. The normal download button uses the existing history to determine which reports can be skipped.

## Project Structure

The project is divided into separate Python modules, test files, configuration files, and data folders.

The following tree illustrates the expected structure:

```text
PDF-downloader/
├── main.py
├── gui.py
├── pdf_downloader.py
├── excel_service.py
├── excel_reader.py
├── report_processor.py
├── history_service.py
├── download_history.json
├── pytest.ini
├── requirements.txt
├── .venv/
├── xlsx-file/
│   └── GRI_2017_2025.xlsx
├── pdf_files/
│   ├── downloaded_reports.xlsx
│   └── BR-number_report.pdf
└── tests/
    ├── test_excel_service.py
    ├── test_history_service.py
    └── test_report_processor.py
```

The PDF filename in this example is illustrative. The actual output folder may contain many PDF files, depending on the reports processed.

### Main application files

| File                  | Purpose                                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `main.py`             | Entry point for starting the application.                                                                                     |
| `gui.py`              | Creates the graphical user interface, handles button actions, displays progress, and presents the results.                    |
| `pdf_downloader.py`   | Contains the downloader-related functionality defined by this module. Its exact responsibility depends on its implementation. |
| `excel_service.py`    | Coordinates report processing, asynchronous downloads, history checks, and Excel report generation.                           |
| `excel_reader.py`     | Reads report numbers and download links from the input spreadsheet.                                                           |
| `report_processor.py` | Processes individual reports, attempts primary and backup URLs, and handles PDF download results.                             |
| `history_service.py`  | Loads, saves, and resets the download history and checks whether existing reports can be reused.                              |

### Data and output files

| File or folder            | Purpose                                                                         |
| ------------------------- | ------------------------------------------------------------------------------- |
| `download_history.json`   | Stores download history in the project root directory.                          |
| `xlsx-file/`              | Contains the source Excel spreadsheet.                                          |
| `pdf_files/`              | Stores downloaded PDFs and the generated Excel summary.                         |
| `downloaded_reports.xlsx` | Summarises the processed reports, including links, paths, statuses, and errors. |

### Test files

The `tests/` directory contains automated tests for the application's main functionality.

| Test file                  | Purpose                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `test_excel_service.py`    | Tests Excel report generation and the report-processing workflow, including forced downloads and preservation of existing PDFs.                        |
| `test_history_service.py`  | Tests loading, saving, and resetting the history, as well as the conditions for skipping existing downloads.                                           |
| `test_report_processor.py` | Tests PDF filename generation, successful downloads, backup-link handling, failed downloads, and preservation of existing files when a download fails. |

### Configuration files

| File or folder     | Purpose                                                                    |
| ------------------ | -------------------------------------------------------------------------- |
| `requirements.txt` | Lists the Python packages required by the project.                         |
| `pytest.ini`       | Configures the pytest testing framework.                                   |
| `.venv/`           | Contains the project's isolated Python environment and installed packages. |

## Running Tests

The project includes automated tests to check important functionality.

Tests help verify that changes to the application do not unintentionally break existing behaviour.

### Run the full test suite

Open PowerShell in the project directory and activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run all tests:

```powershell
python -m pytest tests/ -v
```

The `-v` option displays each test individually, including whether it passed or failed.

### Test coverage

The test suite is divided into three modules.

#### `test_excel_service.py`

Tests functionality related to Excel processing and report orchestration, including:

* Saving report information to Excel.
* Resetting the history when forced downloading is requested.
* Preserving existing PDF files when a new download fails.

#### `test_history_service.py`

Tests download history functionality, including:

* Handling a missing history file.
* Saving and loading history.
* Reporting invalid JSON clearly.
* Validating the history structure.
* Resetting history without deleting PDF files.
* Skipping valid existing downloads.
* Retrying reports when PDFs are missing or source links change.

#### `test_report_processor.py`

Tests individual report-processing functionality, including:

* Generating PDF filenames.
* Handling URLs with and without PDF filenames.
* Handling uppercase PDF extensions.
* Downloading a report successfully.
* Using a backup URL when the primary URL fails.
* Handling failures when both URLs fail.
* Preserving an existing PDF if a new download cannot be saved.

### Understanding the test results

A successful test displays `PASSED`.

If a test fails, pytest displays the test name and an error traceback that can help identify the problem.

For example, a summary such as:

```text
19 passed
```

means that all 19 collected tests passed.

The exact number of tests may change as the project evolves.

## Important Notes

* Keep backups of important PDF files and the input spreadsheet.
* Do not delete `download_history.json` unless you intend to change how previous downloads are handled.
* Use **Download everything again** to reset the history and retry all reports.
* Existing PDF files are not automatically deleted when the history is reset.
* A successful download does not guarantee that the source document is the correct report. Verify important documents when necessary.
* External websites can change their URLs, become unavailable, or block automated requests.
* The Excel summary reflects the latest processing run and is not a permanent archive of every historical download attempt.
* If an Excel file cannot be overwritten, close it in Excel and try again.

## Summary

PDF Downloader simplifies the collection of annual reports from an Excel list.

For everyday use:

1. Start the application using the supplied batch file.
2. Click **Start download**.
3. Monitor the progress and review the results.
4. Open the PDF folder to access downloaded reports.
5. Open the Excel report to review successful, skipped, and failed downloads.

If you want to retry all reports, click **Download everything again** and confirm the operation.

The application handles the downloading, file organisation, history management, and Excel reporting automatically.