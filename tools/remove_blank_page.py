# -*- coding: utf-8 -*-
import shutil

import win32com.client

SRC = r"D:\陈汭-实验4-1seata.docx"
DESKTOP = r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.docx"

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(SRC)
try:
    # Drop the empty line inside the last table cell so the page has room.
    total = doc.Paragraphs.Count
    for i in range(total, 0, -1):
        p = doc.Paragraphs(i)
        raw = p.Range.Text
        if raw in ("\r", "\r\x07") and p.Range.Information(3) >= 26 and p.Range.Tables.Count:
            if raw == "\r":
                p.Range.Delete()
                break

    last = doc.Paragraphs.Last
    last.Range.Font.Size = 1
    pf = last.Range.ParagraphFormat
    pf.SpaceBefore = 0
    pf.SpaceAfter = 0
    pf.LineSpacingRule = 4
    pf.LineSpacing = 1
    pf.KeepTogether = False
    pf.PageBreakBefore = False

    doc.Repaginate()
    pages = doc.ComputeStatistics(2)
    tail = doc.Paragraphs.Last.Range.Information(3)
    open(r"D:\seata\end.txt", "w", encoding="utf-8").write(f"pages {pages}\nlast paragraph page {tail}\n")
    doc.Save()
    doc.SaveAs2(r"D:\陈汭-实验4-1seata.doc", FileFormat=0)
    doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.doc", FileFormat=0)
finally:
    try:
        doc.Close(False)
    except Exception:
        pass
    try:
        word.Quit()
    except Exception:
        pass

shutil.copyfile(SRC, DESKTOP)
