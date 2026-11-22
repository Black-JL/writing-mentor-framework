#!/usr/bin/env python3
"""
Render XLSX workbooks (including their charts) to PDF and PNG using Microsoft Excel.

macOS: drives Excel through AppleScript.
Windows: drives Excel through PowerShell (Excel's COM interface).
Both need Excel installed and poppler (pdftoppm) for the PNG step.
"""
import os
from pathlib import Path

from _tools import IS_MAC, IS_WINDOWS, pdf_to_pngs, run, utf8_console

# Paths go in through environment variables so spaces and quotes are safe.
WINDOWS_SCRIPT = r'''
$ErrorActionPreference = 'Stop'
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
try {
    $wb = $xl.Workbooks.Open($env:WMF_XLSX_IN, 0, $true)
    try { $wb.ExportAsFixedFormat(0, $env:WMF_PDF_OUT) }
    finally { $wb.Close($false) }
}
finally {
    $xl.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
}
'''


def _export_mac(path, pdf_path):
    # Remember whether Excel was already open, and quit it afterwards if it wasn't.
    script = f'''
    set wasRunning to application "Microsoft Excel" is running
    tell application "Microsoft Excel"
        set display alerts to false
        try
            set wb to open workbook workbook file name (POSIX file "{path}" as text)
        on error errMsg number errNum
            if not wasRunning then quit saving no
            error errMsg number errNum
        end try
        set pdfPath to POSIX file "{pdf_path}"
        try
            save workbook as wb filename pdfPath file format PDF file format
        on error errMsg number errNum
            close wb saving no
            if not wasRunning then quit saving no
            error errMsg number errNum
        end try
        close wb saving no
        if not wasRunning then quit saving no
    end tell
    '''
    return run(['osascript', '-e', script], check=False)


def _export_windows(path, pdf_path):
    env = os.environ.copy()
    env['WMF_XLSX_IN'] = str(path.resolve())
    env['WMF_PDF_OUT'] = str(pdf_path.resolve())
    return run(
        ['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
         '-Command', WINDOWS_SCRIPT],
        check=False, env=env,
    )


def render_xlsx(path, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{path.stem}.pdf"
    if IS_MAC:
        result = _export_mac(path, pdf_path)
    elif IS_WINDOWS:
        result = _export_windows(path, pdf_path)
    else:
        raise RuntimeError("Excel rendering works only on macOS and Windows. Use render_xlsx.py (LibreOffice).")

    if result.returncode != 0:
        raise RuntimeError(f"Excel render failed: {result.stderr.strip()} {result.stdout.strip()}")
    if not pdf_path.exists():
        raise RuntimeError(f"Excel did not create PDF for {path.name}")

    pdf_to_pngs(pdf_path, out_dir / path.stem)


if __name__ == '__main__':
    # Older review folders call this script directly; hand off to render_charts.py,
    # which picks the best tool installed (same --input/--out options).
    import sys as _sys
    from render_charts import main as _main
    _sys.exit(_main())
