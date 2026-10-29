# -*- coding: utf-8 -*-
"""Insert the captured screenshots into the step-by-step placeholders."""
from pathlib import Path

import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流\screenshots")
SHOT = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots")
SRC = Path(r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流 (1).docx")

PLACES = [
    ("[截图：Sentinel Dashboard启动成功的命令行界面]", [ROOT / "dashboard-console.png"]),
    ("[截图：application.yaml配置文件内容]", [ROOT / "application-yaml.png"]),
    ("[截图：TestController.java代码]", [ROOT / "test-controller.png"]),
    ("[截图：Sentinel Dashboard中显示已注册的应用列表]", [SHOT / "sentinel-apps.png"]),
    ("[截图：配置QPS限流规则的界面]", [SHOT / "flow-zoom.png"]),
    ("[截图：限流测试的浏览器界面和Dashboard监控数据]", [SHOT / "hello-pass.png", SHOT / "hello-block.png"]),
    ("[截图：Sentinel Dashboard的实时监控界面]", [SHOT / "metric-hello.png"]),
    ("[截图：修改后的TestController.java代码]", [ROOT / "test-controller.png"]),
    ("[截图：热点参数限流配置界面]", [SHOT / "hot-rules.png"]),
    ("[截图：热点参数限流测试结果]", [SHOT / "hot-result.png"]),
    ("[截图：添加系统保护测试接口后的Controller代码]", [ROOT / "test-controller.png"]),
    ("[截图：系统保护规则配置界面]", [SHOT / "system-rules.png"]),
]


def insert(doc, needle, paths):
    found = doc.Range()
    found.Find.ClearFormatting()
    found.Find.Text = needle
    found.Find.Forward = True
    found.Find.Wrap = 0
    if not found.Find.Execute():
        raise RuntimeError("placeholder not found: " + needle)
    found.Text = ""
    for path in paths:
        shape = found.InlineShapes.AddPicture(
            FileName=str(path), LinkToFile=False, SaveWithDocument=True
        )
        shape.LockAspectRatio = True
        if shape.Width > 430:
            shape.Width = 430
        found.Collapse(0)


def main():
    for _, paths in PLACES:
        for path in paths:
            if not path.exists():
                raise SystemExit("missing " + str(path))
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(SRC))
        for needle, paths in PLACES:
            insert(doc, needle, paths)
        left = doc.Content.Text.count("[截图")
        targets = [
            r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
            r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流 (1).docx",
            r"C:\Users\Lenovo\Desktop\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
            r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
        ]
        doc.SaveAs2(targets[0], FileFormat=12)
        for path in targets[1:]:
            doc.SaveAs2(path, FileFormat=12)
        doc.SaveAs2(r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.doc", FileFormat=0)
        print("shapes", doc.InlineShapes.Count, "placeholders_left", left)
    finally:
        if doc is not None:
            doc.Close(False)
        try:
            word.Quit()
        except Exception as exc:
            print("quit", exc)


if __name__ == "__main__":
    main()
