# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

import win32com.client

SRC = Path(r"D:\陈汭-实验4-1seata.docx")


def tune(cell, keep):
    cell.Range.NoProofing = True
    cell.Range.LanguageID = 2052
    cell.Range.LanguageIDFarEast = 2052
    count = cell.Range.Paragraphs.Count
    for i in range(1, count + 1):
        try:
            paragraph = cell.Range.Paragraphs(i)
        except Exception:
            break
        text = paragraph.Range.Text.replace("\r", "").replace("\x07", "").strip()
        paragraph.Range.NoProofing = True
        paragraph.Range.LanguageID = 2052
        paragraph.Range.LanguageIDFarEast = 2052
        if keep and text and paragraph.Range.InlineShapes.Count == 0:
            paragraph.Range.ParagraphFormat.KeepTogether = True
            paragraph.Range.ParagraphFormat.WidowControl = True


def patch_docx(path):
    xml_name = "word/document.xml"
    settings_name = "word/settings.xml"
    with zipfile.ZipFile(path, "r") as zin:
        xml = zin.read(xml_name).decode("utf-8")
        settings = zin.read(settings_name).decode("utf-8")
        others = {item.filename: zin.read(item.filename) for item in zin.infolist()}
    before = xml.count("noProof")
    xml = xml.replace("<w:rPr>", "<w:rPr><w:noProof/>")
    xml = xml.replace(
        '<w:lang w:eastAsia="zh-CN"/>',
        '<w:lang w:val="zh-CN" w:eastAsia="zh-CN"/>',
    )
    if "<w:hideSpellingErrors" not in settings:
        settings = settings.replace(
            "</w:settings>",
            "<w:hideSpellingErrors/><w:hideGrammaticalErrors/></w:settings>",
        )
    others[xml_name] = xml.encode("utf-8")
    others[settings_name] = settings.encode("utf-8")
    tmp = path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in others.items():
            zout.writestr(name, data)
    tmp.replace(path)
    print("noproof", before, "->", xml.count("noProof"))
    print("keepLines", xml.count("<w:keepLines/>") + xml.count('<w:keepLines w:val="1"/>') + xml.count("<w:keepLines "))


def main():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(SRC))
    doc.ShowSpellingErrors = False
    doc.ShowGrammaticalErrors = False
    try:
        for t in range(1, doc.Tables.Count + 1):
            table = doc.Tables(t)
            seen = set()
            for r in range(1, table.Rows.Count + 1):
                for c in range(1, table.Columns.Count + 1):
                    try:
                        cell = table.Cell(r, c)
                    except Exception:
                        continue
                    if cell.Range.Start in seen:
                        continue
                    seen.add(cell.Range.Start)
                    body = cell.Range.Text
                    if "对实验的自我评价" in body:
                        tune(cell, True)
                    elif "实验总结" in body[:30]:
                        tune(cell, False)
        doc.Save()
        doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.docx", FileFormat=12)
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
    patch_docx(SRC)
    import shutil
    shutil.copyfile(SRC, r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.docx")
    print("saved")


if __name__ == "__main__":
    main()
