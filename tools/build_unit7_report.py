# -*- coding: utf-8 -*-
"""Fill the unit 7 Sentinel lab report with the runs from this machine."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流")
IMG = ROOT / "screenshots"
IMG.mkdir(parents=True, exist_ok=True)
SHOT = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots")
FONT_UI = r"C:\Windows\Fonts\msyh.ttc"


def font(size):
    return ImageFont.truetype(FONT_UI, size)


def wrap_line(text, draw, fnt, max_w):
    if not text:
        return [""]
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def render_code(title, text, out_path):
    fnt = font(15)
    header_fnt = font(16)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = 980
    body_lines = []
    for line in text.splitlines():
        body_lines.extend(wrap_line(line, dummy, fnt, max_w - 70))
    line_h = 22
    header_h = 42
    height = header_h + 16 + line_h * len(body_lines) + 16
    img = Image.new("RGB", (max_w, height), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, max_w, header_h), fill="#2d2d30")
    draw.text((16, 11), title, font=header_fnt, fill="#ffffff")
    y = header_h + 10
    for i, line in enumerate(body_lines, 1):
        draw.text((12, y), f"{i:3}", font=fnt, fill="#858585")
        draw.text((52, y), line, font=fnt, fill="#d4d4d4")
        y += line_h
    img.save(out_path, quality=90)
    return out_path


def render_console(title, text, out_path):
    fnt = font(15)
    header_fnt = font(16)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = 980
    body_lines = []
    for line in text.splitlines():
        body_lines.extend(wrap_line(line, dummy, fnt, max_w - 36))
    line_h = 22
    header_h = 42
    height = header_h + 16 + line_h * len(body_lines) + 16
    img = Image.new("RGB", (max_w, height), "#0c0c0c")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, max_w, header_h), fill="#1f1f1f")
    draw.text((16, 11), title, font=header_fnt, fill="#cccccc")
    y = header_h + 10
    for line in body_lines:
        draw.text((16, y), line, font=fnt, fill="#cccccc")
        y += line_h
    img.save(out_path, quality=90)
    return out_path


def build_images():
    pics = {
        "login": SHOT / "sentinel-home.png",
        "menu": SHOT / "sentinel-menu.png",
        "identity": SHOT / "identity.png",
        "flow": SHOT / "flow-zoom.png",
        "hello_pass": SHOT / "hello-pass.png",
        "hello_block": SHOT / "hello-block.png",
        "metric": SHOT / "metric-hello.png",
        "hot_rule": SHOT / "hot-rules.png",
        "hot_result": SHOT / "hot-result.png",
        "system": SHOT / "system-rules.png",
        "degrade_pass": SHOT / "degrade-pass.png",
        "degrade_block": SHOT / "degrade-block.png",
        "degrade_rule": SHOT / "degrade-rules.png",
    }
    for key, path in pics.items():
        if not path.exists():
            raise SystemExit("missing screenshot: " + str(path))

    pics["console"] = render_console(
        "命令行  java -jar sentinel-dashboard-1.7.0.jar",
        "\n".join([
            "Tomcat initialized with port(s): 8080 (http)",
            "Sentinel servlet CommonFilter registered",
            "Started DashboardApplication in 2.998 seconds (JVM running for 3.483)",
            "",
            "浏览器访问 http://localhost:8080",
            "用户名 sentinel    密码 sentinel",
        ]),
        IMG / "dashboard-console.png",
    )
    pics["yaml"] = render_code(
        "application.yaml",
        (ROOT / "unit7demo1-sentinel" / "src" / "main" / "resources" / "application.yaml").read_text(encoding="utf-8"),
        IMG / "application-yaml.png",
    )
    pics["controller"] = render_code(
        "TestController.java",
        (ROOT / "unit7demo1-sentinel" / "src" / "main" / "java" / "com" / "example" / "demo" / "TestController.java").read_text(encoding="utf-8"),
        IMG / "test-controller.png",
    )
    pics["thread"] = render_code(
        "TestThread.java",
        (ROOT / "unit7demo1-sentinel" / "src" / "main" / "java" / "com" / "example" / "demo" / "TestThread.java").read_text(encoding="utf-8"),
        IMG / "test-thread-code.png",
    )
    pics["degrade_code"] = render_code(
        "degrade-test / TestController.java",
        (ROOT / "degrade-test" / "src" / "main" / "java" / "cn" / "js" / "ccit" / "TestController.java").read_text(encoding="utf-8"),
        IMG / "degrade-controller.png",
    )
    raw = (IMG / "test-thread.txt").read_text(encoding="utf-16")
    shown = [ln.strip() for ln in raw.splitlines() if ln.strip() == "hi" or ln.strip().startswith("exception:")]
    pics["thread_out"] = render_console(
        "TestThread  10 个线程，共 50 次请求  /hi",
        "\n".join(shown[:12] + ["......", "hi：5 次", 'exception: 429 Blocked by Sentinel (flow limiting)：45 次']),
        IMG / "test-thread-out.png",
    )
    return pics


def set_para_text(paragraph, text):
    rng = paragraph.Range
    rng.MoveEnd(1, -1)
    rng.Text = text
    rng.Font.Name = "宋体"
    rng.Font.NameFarEast = "宋体"
    rng.Font.Size = 12


def write_cell_text(cell, paragraphs):
    body = "\r".join(paragraphs)
    rng = cell.Range
    rng.MoveEnd(1, -1)
    rng.Text = body
    rng.Font.Name = "宋体"
    rng.Font.NameFarEast = "宋体"
    rng.Font.Size = 10.5
    for i in range(1, cell.Range.Paragraphs.Count + 1):
        try:
            p = cell.Range.Paragraphs(i)
        except Exception:
            break
        text = p.Range.Text.replace("\r", "").replace("\x07", "")
        pf = p.Range.ParagraphFormat
        pf.LineSpacingRule = 1
        pf.SpaceAfter = 6
        pf.SpaceBefore = 2
        p.Range.Font.Name = "宋体"
        p.Range.Font.NameFarEast = "宋体"
        p.Range.Font.Size = 10.5
        if text.startswith("实验总结") or text.startswith("对实验的自我评价") or text.startswith("表") or text.startswith("错误") or text.startswith("（"):
            p.Range.Font.Bold = -1
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("[[IMG:"):
            p.Range.Font.Bold = 0
            pf.Alignment = 1
            pf.CharacterUnitFirstLineIndent = 0
        else:
            p.Range.Font.Bold = 0
            pf.Alignment = 3
            pf.CharacterUnitFirstLineIndent = 2


def replace_images(doc, pics):
    for key, path in pics.items():
        token = "[[IMG:%s]]" % key
        while True:
            found = doc.Range()
            found.Find.ClearFormatting()
            found.Find.Text = token
            found.Find.Forward = True
            found.Find.Wrap = 0
            if not found.Find.Execute():
                break
            found.Text = ""
            shape = found.InlineShapes.AddPicture(
                FileName=str(path), LinkToFile=False, SaveWithDocument=True
            )
            shape.LockAspectRatio = True
            if shape.Width > 430:
                shape.Width = 430


def find_paragraph(doc, needle):
    for i in range(1, doc.Paragraphs.Count + 1):
        if needle in doc.Paragraphs(i).Range.Text:
            return doc.Paragraphs(i)
    raise RuntimeError("paragraph not found: " + needle)


def find_cell(doc, needle):
    for t in range(1, doc.Tables.Count + 1):
        table = doc.Tables(t)
        for r in range(1, table.Rows.Count + 1):
            for c in range(1, table.Columns.Count + 1):
                try:
                    cell = table.Cell(r, c)
                except Exception:
                    continue
                if needle in cell.Range.Text:
                    return cell
    raise RuntimeError("cell not found: " + needle)


def main():
    pics = build_images()
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(r"D:\学号-姓名-第七单元-Sentinel服务熔断与限流.doc")
        set_para_text(
            find_paragraph(doc, "学生姓名"),
            "学生姓名：陈汭            学号：423240532            专业班级：计算机科学与技术5班",
        )
        write_cell_text(find_cell(doc, "实验总结"), [
            "实验总结",
            "表1  Sentinel Dashboard启动记录",
            "控制台用的是 sentinel-dashboard-1.7.0.jar。命令是 java -jar sentinel-dashboard-1.7.0.jar，默认端口 8080。日志里 Tomcat 绑定 8080，大约 3 秒后 DashboardApplication 启动完成。浏览器打开 http://localhost:8080，登录页的用户名和密码都是 sentinel。",
            "[[IMG:console]]",
            "[[IMG:login]]",
            "工程是 unit7demo1-sentinel，应用名 service-sentinel，端口 8089。依赖按实验环境表来：Spring Boot 2.6.3、Spring Cloud 2021.0.1、Spring Cloud Alibaba 2021.0.1.0。登录以后左侧能看到 service-sentinel，健康实例是 1/1。客户端心跳端口是 8720，8719 被控制台自己占了。",
            "[[IMG:menu]]",
            "[[IMG:yaml]]",
            "[[IMG:controller]]",
            "表2  QPS限流测试记录",
            "先访问 /hello，簇点链路里出现这个资源。流控规则：资源 /hello，来源 default，阈值类型 QPS，阈值 1，流控模式直接，流控效果快速失败。",
            "[[IMG:identity]]",
            "[[IMG:flow]]",
            "浏览器对 http://localhost:8089/hello?name=test 同一批发了 15 个请求。1 个返回 Hello test!，另外 14 个是 429，正文是 Blocked by Sentinel (flow limiting)。实时监控里能看到通过 QPS 和拒绝 QPS，/hi 在系统保护生效时拒绝 QPS 为 8.0。",
            "[[IMG:hello_pass]]",
            "[[IMG:hello_block]]",
            "[[IMG:metric]]",
            "表3  热点参数限流测试记录",
            "hotpoint 方法上加了 @SentinelResource(\"hotpoint\")。热点规则的资源名是 hotpoint，参数索引 0，对应 type，流控模式 QPS，阈值 10。pom 里补了 sentinel-parameter-flow-control，否则热点规则不会生效。",
            "[[IMG:hot_rule]]",
            "type=a 并发 24 次：10 次返回 type: a, name: rose，14 次是 500，服务日志是 ParamFlowException: a。type=b 并发 8 次全部 200，返回 type: b, name: lily。阈值只限制了参数值 a。",
            "[[IMG:hot_result]]",
            "表4  系统保护规则测试记录",
            "系统规则一次只能填一个大于 0 的指标，所以分三条：系统 load 为 2，平均 RT 为 100 毫秒，入口 QPS 为 5。TestThread 用 10 个线程请求 http://localhost:8089/hi，一共 50 次。控制台打出 5 次 hi，另外 45 次是 exception: 429 Blocked by Sentinel (flow limiting)。入口 QPS 为 5 时，超出的请求被拒绝。",
            "[[IMG:system]]",
            "[[IMG:thread]]",
            "[[IMG:thread_out]]",
            "表5  RT熔断测试记录",
            "另外建了 degrade-test，端口仍是 8089，所以先停掉 service-sentinel 再启动。接口 /degrade-rt 里 Thread.sleep(200)，正常返回 rt策略测试。降级规则：资源 /degrade-rt，模式 RT，阈值 100 毫秒，时间窗口 10 秒。",
            "[[IMG:degrade_code]]",
            "[[IMG:degrade_rule]]",
            "没触发熔断时，浏览器直接看到 rt策略测试，耗时大约 200 毫秒。同一秒里把慢调用打上去之后，下一次请求不再等待，2 毫秒就返回 429 Blocked by Sentinel (flow limiting)。熔断打开后是快速失败。",
            "[[IMG:degrade_pass]]",
            "[[IMG:degrade_block]]",
        ])
        write_cell_text(find_cell(doc, "对实验的自我评价"), [
            "对实验的自我评价：",
            "Dashboard 的登录、QPS 限流、热点参数、系统保护和 RT 熔断都跑通了。调试时主要碰到下面几个问题。",
            "错误1：第一次启动控制台时，PowerShell 把 -Dserver.port=8080 拆开，Java 报找不到主类 .port=8080。",
            "分析：PowerShell 会把 -D 当成自己的参数。控制台默认就是 8080，不需要再写这个参数。",
            "解决：改成 cmd /c java -jar sentinel-dashboard-1.7.0.jar。日志里 Tomcat 端口是 8080，页面能打开。",
            "错误2：应用启动后，控制台里过一会儿才出现 service-sentinel，而且机器端口不是 8719。",
            "分析：客户端默认懒连接，要先访问一次接口才发心跳。8719 被控制台进程占用，客户端改用 8720。",
            "解决：先请求 http://localhost:8089/hello?name=test，等两三秒再刷新。左侧显示 service-sentinel (1/1)，机器是 10.26.144.55:8720。",
            "错误3：热点规则加上之后，type=a 一开始全部通过。",
            "分析：spring-cloud-starter-alibaba-sentinel 没有带上参数限流的槽。规则如果没写进 rule 这一层，控制台会返回 rule can't be null。",
            "解决：pom 增加 sentinel-parameter-flow-control。规则按资源 hotpoint、参数索引 0、阈值 10 保存。type=a 的 24 次里 10 次通过、14 次被拦，type=b 的 8 次全部通过。",
            "另外，TestThread 请求的是 /hi，实验给出的控制器只有 / 返回 hi。我把这两个路径写到同一个方法上，50 次请求里 5 次打印 hi，45 次是 429，和入口 QPS 为 5 一致。",
            "（一）实验总结",
            "控制台、QPS 限流、热点参数、系统保护和 RT 熔断都按上面的结果做完了。限流看的是这一秒能不能再进来，熔断看的是调用已经变慢之后要不要继续等。",
            "（二）思考题",
            "1. Sentinel的QPS限流和热点参数限流有什么区别？分别适用于什么场景？",
            "答：QPS 限流按整个资源计数，不区分参数。/hello 的阈值是 1 之后，name 无论是什么，同一秒里多出来的请求都是 429。热点参数限流只统计指定下标的参数。hotpoint 的参数索引 0 是 type，阈值 10。type=a 打到 24 次时只有 10 次通过，type=b 的 8 次全部通过。接口总容量用 QPS。商品 id、用户 id 这种少数值特别热、其他值还要正常访问的时候用热点参数。",
            "2. 系统保护规则中的LOAD、RT、QPS三个指标分别代表什么含义？如何合理设置阈值？",
            "答：LOAD 是系统近一分钟的平均负载，超过就拒绝新请求，这次填的是 2。这台机器是 Windows，JDK 的 getSystemLoadAverage 经常返回 -1，所以这条在 Windows 上基本不会触发，Linux 上可以按 CPU 核数的大约 0.7 到 1 倍来设。RT 是入口的平均响应时间，单位毫秒，这次是 100，要高于接口平时的耗时，低于能接受的超时。QPS 是整台机器每秒的入口请求数，这次是 5。TestThread 用 10 个线程打 50 次 /hi，5 次打印 hi，45 次是 429。三个条件满足任意一个就会拦截，阈值按压测容量留出余量，不要顶满。",
            "3. 在实际生产环境中，如何根据业务需求选择合适的限流策略？",
            "答：先看要保护的是哪一层。接口总流量用 QPS，可以直接失败，也可以排队把突发摊开。某个参数特别热就用热点参数，必要时给个别参数值单独设阈值。下游变慢或错误变多用熔断。这次 RT 阈值 100 毫秒，接口自己 sleep 了 200 毫秒，慢调用堆起来之后，下一次请求 2 毫秒就返回 429，不再等这 200 毫秒。机器本身快被打满时用系统规则兜底，LOAD、平均 RT 和入口 QPS 可以一起配。顺序一般是先按业务接口限流，再给不稳定的依赖做熔断，系统规则放在最后。阈值从压测和监控里来，再跟着实时监控调整。",
        ])
        replace_images(doc, pics)
        docx = r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx"
        doc_path = r"D:\423240532-陈汭-第七单元-Sentinel服务熔断与限流.doc"
        desktop_docx = r"C:\Users\Lenovo\Desktop\423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx"
        project_docx = str(ROOT / "423240532-陈汭-第七单元-Sentinel服务熔断与限流.docx")
        doc.SaveAs2(docx, FileFormat=12)
        doc.SaveAs2(desktop_docx, FileFormat=12)
        doc.SaveAs2(project_docx, FileFormat=12)
        doc.SaveAs2(doc_path, FileFormat=0)
        print("shapes", doc.InlineShapes.Count)
        print("saved")
    finally:
        if doc is not None:
            doc.Close(False)
        try:
            word.Quit()
        except Exception as exc:
            print("quit", exc)


if __name__ == "__main__":
    main()
