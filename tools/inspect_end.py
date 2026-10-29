# -*- coding: utf-8 -*-
import win32com.client

SRC = r"D:\陈汭-实验4-1seata.docx"
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(SRC)
lines = []
try:
    total = doc.Paragraphs.Count
    lines.append(f"paragraphs {total} tables {doc.Tables.Count}")
    start = max(1, total - 15)
    for i in range(start, total + 1):
        p = doc.Paragraphs(i)
        raw = p.Range.Text.replace("\r", "\\r").replace("\x07", "\\a").replace("\x0c", "\\f")
        page = p.Range.Information(3)
        pf = p.Range.ParagraphFormat
        lines.append(
            f"{i} page={page} keep={pf.KeepTogether} before={pf.SpaceBefore} after={pf.SpaceAfter} "
            f"rule={pf.LineSpacingRule} line={pf.LineSpacing} size={p.Range.Font.Size} "
            f"tables={p.Range.Tables.Count} text={raw[:60]!r}"
        )
    if doc.Tables.Count:
        table = doc.Tables(doc.Tables.Count)
        lines.append(f"last table rows={table.Rows.Count} cols={table.Columns.Count}")
        cell = table.Cell(table.Rows.Count, 1)
        lines.append(f"last cell paras={cell.Range.Paragraphs.Count} page={cell.Range.Information(3)}")
finally:
    open(r"D:\seata\end.txt", "w", encoding="utf-8").write("\n".join(lines))
    doc.Close(False)
    try:
        word.Quit()
    except Exception:
        pass
