"""Probe: versiunea Microsoft Excel instalată și suportul pentru funcții dinamice."""

from __future__ import annotations

import pythoncom
import win32com.client

FORMULAS = [
    "=FILTER({1;2;3},{1;0;1})",
    "=LARGE({1,2,3},1)",
    "=SUMPRODUCT({1,2},{3,4})",
    '=TEXTJOIN(",",TRUE,{1,2})',
    "=LET(a,1,a)",
    "=XLOOKUP(2,{1;2;3},{10;20;30})",
]


def main() -> None:
    pythoncom.CoInitialize()
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    print("Version:", excel.Version)
    print("Build:", excel.Build)
    wb = excel.Workbooks.Add()
    ws = wb.Worksheets(1)
    for formula in FORMULAS:
        try:
            ws.Range("A1").Formula = formula
            print(f"{formula} -> {ws.Range('A1').Text}")
        except Exception as exc:  # noqa: BLE001
            print(f"{formula} -> EXCEPTIE {exc}")
    wb.Close(False)
    excel.Quit()
    pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
