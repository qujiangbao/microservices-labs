# -*- coding: utf-8 -*-
import win32com.client

SRC = r"D:\陈汭-实验4-1seata.docx"
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(SRC)
try:
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)
    lines = [f"pages {pages}"]
    for n in range(1, pages + 1):
        start = doc.GoTo(1, 1, n).Start
        end = doc.Content.End if n == pages else doc.GoTo(1, 1, n + 1).Start
        rng = doc.Range(start, end)
        text = rng.Text.replace("\r", " ").replace("\x07", " ").replace("\x0c", "[PB]").replace("\x0b", " ")
        text = " ".join(text.split())
        pics = rng.InlineShapes.Count
        lines.append(f"P{n} chars={len(text)} pics={pics} :: {text[:120]}")
    lines.append("--- breaks ---")
    finder = doc.Content.Find
    finder.ClearFormatting()
    finder.Text = "^m"
    finder.Forward = True
    finder.Wrap = 0
    hits = 0
    while finder.Execute():
        hits += 1
        if hits > 20:
            break
    lines.append(f"section breaks found {hits}")
    open(r"D:\seata\pages.txt", "w", encoding="utf-8").write("\n".join(lines))
finally:
    doc.Close(False)
    try:
        word.Quit()
    except Exception:
        pass
