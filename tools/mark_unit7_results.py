# -*- coding: utf-8 -*-
"""Put a visible result line, and the missing task-5 shots, under each task."""
import win32com.client

ROOT = r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流\screenshots"
SHOT = r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots"

RESULTS = [
    ("任务2  配置QPS限流规则",
     "任务1完成结果：Dashboard 已在 8080 端口启动，登录账号 sentinel。应用 service-sentinel 注册成功，健康实例 1/1，客户端端口 8720。"),
    ("任务3  配置热点参数限流",
     "任务2完成结果：/hello 的 QPS 阈值设为 1。同一批 15 次请求里，1 次返回 Hello test!，14 次返回 429 Blocked by Sentinel (flow limiting)。"),
    ("任务4  配置系统保护规则",
     "任务3完成结果：hotpoint 参数索引 0、QPS 阈值 10。type=a 并发 24 次，10 次通过、14 次被拦；type=b 并发 8 次，全部返回 200。"),
    ("任务5  熔断降级任务",
     "任务4完成结果：系统规则入口 QPS 为 5。TestThread 用 10 个线程请求 /hi 共 50 次，控制台 5 次打印 hi，45 次是 429。"),
]


def insert_before(doc, anchor, text):
    rng = doc.Content
    rng.Find.ClearFormatting()
    rng.Find.Text = anchor
    rng.Find.Forward = True
    rng.Find.Wrap = 0
    if not rng.Find.Execute():
        raise RuntimeError("not found: " + anchor)
    rng.Collapse(1)
    rng.InsertBefore(text + "\r")
    para = rng.Paragraphs(1)
    para.Range.Font.Bold = True
    para.Range.Font.Name = "宋体"
    para.Range.Font.Size = 12
    para.Range.Font.Color = 0xC00000


def add_picture(rng, path):
    shape = rng.InlineShapes.AddPicture(FileName=path, LinkToFile=False, SaveWithDocument=True)
    shape.LockAspectRatio = True
    if shape.Width > 430:
        shape.Width = 430
    rng.Collapse(0)
    rng.InsertAfter("\r")
    rng.Collapse(0)


def main():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx")
        for anchor, text in RESULTS:
            insert_before(doc, anchor, text)
        rng = doc.Content
        rng.Find.ClearFormatting()
        rng.Find.Text = "任务4完成结果："
        rng.Find.Forward = True
        rng.Find.Wrap = 0
        if not rng.Find.Execute():
            raise RuntimeError("task4 result not found")
        rng.Collapse(0)
        rng.InsertAfter("\r")
        rng.Collapse(0)
        add_picture(rng, ROOT + r"\test-thread-out.png")
        rng = doc.Content
        rng.Find.ClearFormatting()
        rng.Find.Text = "至此实现基于RT策略的熔断降级"
        rng.Find.Forward = True
        rng.Find.Wrap = 0
        if not rng.Find.Execute():
            raise RuntimeError("task5 ending not found")
        rng.Collapse(0)
        rng.InsertAfter("\r")
        rng.Collapse(0)
        for path in (
            ROOT + r"\degrade-controller.png",
            SHOT + r"\degrade-rules.png",
            SHOT + r"\degrade-pass.png",
            SHOT + r"\degrade-block.png",
        ):
            add_picture(rng, path)
        done = "任务5完成结果：未加规则时 /degrade-rt 返回 rt策略测试，耗时约 200 毫秒。RT 阈值 100 毫秒、时间窗口 10 秒。慢调用触发后，下一次请求 2 毫秒返回 429，熔断已打开。"
        rng.InsertAfter(done + "\r")
        para = rng.Paragraphs(1)
        para.Range.Font.Bold = True
        para.Range.Font.Name = "宋体"
        para.Range.Font.Size = 12
        para.Range.Font.Color = 0xC00000
        targets = [
            r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
            r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流 (1).docx",
            r"C:\Users\Lenovo\Desktop\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
            r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx",
        ]
        for path in targets:
            doc.SaveAs2(path, FileFormat=12)
        doc.SaveAs2(r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.doc", FileFormat=0)
        print("shapes", doc.InlineShapes.Count)
    finally:
        if doc is not None:
            doc.Close(False)
        try:
            word.Quit()
        except Exception as exc:
            print("quit", exc)


if __name__ == "__main__":
    main()
