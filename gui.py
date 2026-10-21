import asyncio
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk

from pathlib import Path
from tkinter import ttk, messagebox

from excel_service import (
    EXCEL_FILE,
    OUTPUT_DIR,
    OUTPUT_EXCEL_FILE,
    load_reports_async,
)


BASE_DIR = Path(__file__).resolve().parent


class PDFDownloaderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF Downloader")
        self.root.geometry("760x560")
        self.root.minsize(650, 480)

        self.events = queue.Queue()
        self.running = False
        self.reports = []

        self._build_ui()
        self.root.after(100, self._process_events)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="PDF Downloader",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="Download and manage annual reports",
        ).pack(anchor="w", pady=(2, 18))

        input_frame = ttk.LabelFrame(
            main,
            text="Input",
            padding=10,
        )
        input_frame.pack(fill="x", pady=(0, 14))

        ttk.Label(
            input_frame,
            text=f"Excel-file: {EXCEL_FILE}",
            wraplength=680,
        ).pack(anchor="w")

        self.status_var = tk.StringVar(
            value="Ready to start."
        )
        ttk.Label(
            main,
            textvariable=self.status_var,
        ).pack(anchor="w", pady=(0, 8))

        self.progress = ttk.Progressbar(
            main,
            mode="determinate",
            maximum=100,
        )
        self.progress.pack(fill="x", pady=(0, 8))

        self.progress_var = tk.StringVar(value="0 / 0 reports")
        ttk.Label(
            main,
            textvariable=self.progress_var,
        ).pack(anchor="w", pady=(0, 14))

        stats = ttk.LabelFrame(
            main,
            text="Results",
            padding=12,
        )
        stats.pack(fill="x", pady=(0, 14))

        self.downloaded_var = tk.StringVar(value="Downloaded: 0")
        self.skipped_var = tk.StringVar(value="Skipped: 0")
        self.failed_var = tk.StringVar(value="Failed: 0")

        for variable in (
            self.downloaded_var,
            self.skipped_var,
            self.failed_var,
        ):
            ttk.Label(
                stats,
                textvariable=variable,
            ).pack(anchor="w", pady=2)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(0, 12))

        self.start_button = ttk.Button(
            buttons,
            text="Start download",
            command=lambda: self._start_download(False),
        )
        self.start_button.pack(
            side="left", padx=(0, 8), pady=4
        )

        self.force_button = ttk.Button(
            buttons,
            text="Download everything again",
            command=self._confirm_full_download,
        )
        self.force_button.pack(
            side="left", padx=(0, 8), pady=4
        )

        ttk.Button(
            buttons,
            text="Open PDF-folder",
            command=self._open_output_folder,
        ).pack(side="left", padx=(0, 8), pady=4)

        ttk.Button(
            buttons,
            text="Open Excel-report",
            command=self._open_excel_report,
        ).pack(side="left", pady=4)

        log_frame = ttk.LabelFrame(
            main,
            text="Activity",
            padding=8,
        )
        log_frame.pack(fill="both", expand=True)

        self.log = tk.Text(
            log_frame,
            height=8,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.log.pack(fill="both", expand=True)

    def _log(self, message: str):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _confirm_full_download(self):
        if self.running:
            return

        confirmed = messagebox.askyesno(
            "Download all reports again",
            "The download history will be reset, and all reports "
            "will be attempted to be fetched again.\n\n"
            "Existing PDF files are not automatically deleted, "
            "but files with the same name may be overwritten.\n\n"
            "Do you want to continue?",
            parent=self.root,
        )

        if confirmed:
            self._start_download(True)

    def _start_download(self, force_download: bool):
        if self.running:
            return

        if not EXCEL_FILE.is_file():
            messagebox.showerror(
                "Excel-file missing",
                f"Inputfile was not found:\n{EXCEL_FILE}",
                parent=self.root,
            )
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.force_button.configure(state="disabled")

        self.progress["value"] = 0
        self.progress_var.set("0 / 0 reports")
        self.downloaded_var.set("Downloaded: 0")
        self.skipped_var.set("Skipped: 0")
        self.failed_var.set("Failed: 0")

        mode = (
            "Full download started."
            if force_download
            else "Download started."
        )
        self.status_var.set(mode)
        self._log(mode)

        worker = threading.Thread(
            target=self._download_worker,
            args=(force_download,),
            daemon=True,
        )
        worker.start()

    def _download_worker(self, force_download: bool):
        def report_progress(progress: dict):
            self.events.put(("progress", progress))

        try:
            reports = asyncio.run(
                load_reports_async(
                    EXCEL_FILE,
                    force_download=force_download,
                    progress_callback=report_progress,
                )
            )

            self.events.put(("finished", reports))

        except Exception as error:
            self.events.put((
                "error",
                f"{type(error).__name__}: {error}",
            ))

    def _process_events(self):
        try:
            while True:
                event, data = self.events.get_nowait()

                if event == "progress":
                    self._update_progress(data)

                elif event == "finished":
                    self.reports = data
                    self._finish_download()

                elif event == "error":
                    self._finish_error(data)

        except queue.Empty:
            pass

        self.root.after(100, self._process_events)

    def _update_progress(self, data: dict):
        completed = data["completed"]
        total = data["total"]

        percent = (
            completed / total * 100
            if total
            else 100
        )

        self.progress["value"] = percent
        self.progress_var.set(
            f"{completed} / {total} reports ({percent:.1f} %)"
        )

        self.downloaded_var.set(
            f"Downloaded: {data['downloaded']}"
        )
        self.skipped_var.set(
            f"Skipped: {data['skipped']}"
        )
        self.failed_var.set(
            f"Failed: {data['failed']}"
        )

        report = data.get("report", {})
        self.status_var.set(
            f"processing report {completed} of {total}"
        )

        self._log(
            f"BR {report.get('br_id', '?')}: "
            f"{report.get('status', 'unknown')}"
        )

    def _finish_download(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.force_button.configure(state="normal")

        downloaded = sum(
            r.get("status") == "downloaded"
            for r in self.reports
        )
        skipped = sum(
            r.get("status") == "skipped"
            for r in self.reports
        )
        failed = sum(
            r.get("status") == "failed"
            for r in self.reports
        )

        self.status_var.set("Download ended.")
        self._log(
            f"Done: {downloaded} downloaded, "
            f"{skipped} skipped, {failed} failed."
        )

        if self.reports:
            self.progress["value"] = 100
            self.progress_var.set(
                f"{len(self.reports)} / {len(self.reports)} reports"
            )

        messagebox.showinfo(
            "Download ended",
            f"Downloaded: {downloaded}\n"
            f"Skipped: {skipped}\n"
            f"Failed: {failed}\n\n"
            f"Excel-report:\n{OUTPUT_EXCEL_FILE}",
            parent=self.root,
        )

    def _finish_error(self, error: str):
        self.running = False
        self.start_button.configure(state="normal")
        self.force_button.configure(state="normal")

        self.status_var.set("Download stopped due to an error.")
        self._log(f"ERROR: {error}")

        messagebox.showerror(
            "Download error",
            error,
            parent=self.root,
        )

    def _open_output_folder(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])

    def _open_excel_report(self):
        if not OUTPUT_EXCEL_FILE.is_file():
            messagebox.showwarning(
                "No report yet",
                "The excel-report is not created yet. "
                "Start download first.",
                parent=self.root,
            )
            return

        if sys.platform == "win32":
            os.startfile(str(OUTPUT_EXCEL_FILE))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_EXCEL_FILE)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_EXCEL_FILE)])


def main():
    root = tk.Tk()
    PDFDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()