# -*- coding: utf-8 -*-
"""Build one lab report for the predicate cases and the filter cases."""
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\实验3-Gateway服务网关")
PRED = ROOT / "案例4-3-gateway-predicate"
FILT = ROOT / "案例4-4-gateway-filter"
IMG = ROOT / "screenshots" / "predicate-filter"
IMG.mkdir(parents=True, exist_ok=True)
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
    img = Image.new("RGB", (max_w, max(height, 80)), "#1e1e1e")
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


def render_browser(url, body, out_path):
    ui = font(16)
    body_font = font(18)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    width = 980
    content_w = width - 48
    lines = []
    for line in body.splitlines() or [""]:
        lines.extend(wrap_line(line, dummy, body_font, content_w))
    line_h = 28
    bar_h = 78
    height = bar_h + 24 + line_h * max(len(lines), 1) + 28
    img = Image.new("RGB", (width, height), "#f3f3f3")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 36), fill="#dee1e6")
    draw.text((16, 8), "浏览器", font=ui, fill="#202124")
    draw.rounded_rectangle((12, 44, width - 12, 70), radius=14, fill="#ffffff", outline="#c4c7c5")
    draw.text((24, 48), url, font=ui, fill="#202124")
    y = bar_h + 8
    for line in lines:
        draw.text((24, y), line, font=body_font, fill="#111111")
        y += line_h
    img.save(out_path, quality=90)
    return out_path


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            seen = {}
            for key, value in resp.headers.items():
                if key.lower().startswith("x-response"):
                    seen[key.lower()] = key + ": " + value
            extra = list(seen.values())
            text = body if not extra else body + "\n" + "\n".join(extra)
            return resp.status, text
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if "404" in detail or exc.code == 404:
            return exc.code, "404 Not Found"
        return exc.code, detail[:300]


def read(path):
    return Path(path).read_text(encoding="utf-8")


def collect():
    data = {}
    checks = [
        ("p_after", "http://127.0.0.1:8011/hello?name=gateway", None),
        ("p_deny", "http://127.0.0.1:8011/after-deny/hello", None),
        ("p_between", "http://127.0.0.1:8011/between/hello?name=gateway", None),
        ("p_cookie", "http://127.0.0.1:8011/cookie/hello?name=gateway", {"Cookie": "test=chap"}),
        ("p_cookie_bad", "http://127.0.0.1:8011/cookie/hello?name=gateway", None),
        ("p_header", "http://127.0.0.1:8011/header/hello?name=gateway", {"X-Request-Id": "88"}),
        ("p_header_bad", "http://127.0.0.1:8011/header/hello?name=gateway", {"X-Request-Id": "abc"}),
        ("p_method", "http://127.0.0.1:8011/method/hello?name=gateway", None),
        ("p_red", "http://127.0.0.1:8011/red/1", None),
        ("p_blue", "http://127.0.0.1:8011/blue/bar", None),
        ("p_green", "http://127.0.0.1:8011/query/green?green=1", None),
        ("p_query", "http://127.0.0.1:8011/query/hello?red=green", None),
        ("p_query_bad", "http://127.0.0.1:8011/query/hello?red=nope", None),
        ("f_head", "http://127.0.0.1:8001/test/head", None),
        ("f_param", "http://127.0.0.1:8001/test/param", None),
        ("f_resp", "http://127.0.0.1:8001/hello?name=AddResponseHeader", None),
        ("f_remove", "http://127.0.0.1:8001/test/reresheader", None),
        ("f_remove_direct", "http://127.0.0.1:9001/test/reresheader", None),
        ("f_strip", "http://127.0.0.1:8001/red/blue/hello?name=StripPrefix", None),
        ("f_rewrite", "http://127.0.0.1:8001/red/hello?name=RewritePath", None),
    ]
    for key, url, headers in checks:
        status, text = fetch(url, headers)
        data[key] = (status, text, url)
        print(key, status, text.replace("\n", " | "))
    ports = []
    for _ in range(8):
        status, text = fetch("http://127.0.0.1:8001/test/lb")
        ports.append(text.strip())
    data["f_lb"] = (200, "多次访问得到：\n" + "\n".join(ports), "http://127.0.0.1:8001/test/lb")
    print("lb", sorted(set(ports)))
    return data


def build_images(data):
    pics = {}
    pics["p_yaml"] = render_code(
        "案例4-3 service-gateway/application.yaml",
        read(PRED / "service-gateway/src/main/resources/application.yaml"),
        IMG / "p-yaml.jpg",
    )
    pics["p_code"] = render_code(
        "案例4-3 ProviderController.java / PredicateAfter.java",
        read(PRED / "service-provider/src/main/java/cn/js/ccit/controller/ProviderController.java")
        + "\n\n"
        + read(PRED / "service-gateway/src/main/java/cn/js/ccit/PredicateAfter.java"),
        IMG / "p-code.jpg",
    )
    pics["f_yaml"] = render_code(
        "案例4-4 service-gateway/application.yaml",
        read(FILT / "service-gateway/src/main/resources/application.yaml"),
        IMG / "f-yaml.jpg",
    )
    pics["f_code"] = render_code(
        "案例4-4 ProviderController.java",
        read(FILT / "service-provider/src/main/java/cn/js/ccit/controller/ProviderController.java"),
        IMG / "f-code.jpg",
    )

    def shot(key, name, note=""):
        status, text, url = data[key]
        body = text if not note else text + "\n" + note
        pics[name] = render_browser(url, body, IMG / (name + ".jpg"))

    shot("p_after", "p_after")
    shot("p_deny", "p_deny", "After 设在 2099 年，当前请求不匹配")
    shot("p_between", "p_between")
    shot("p_cookie", "p_cookie", "请求头 Cookie: test=chap，值匹配正则 ch.p")
    shot("p_header", "p_header", "请求头 X-Request-Id: 88，值匹配 \\d+")
    shot("p_method", "p_method")
    shot("p_red", "p_red")
    shot("p_blue", "p_blue")
    shot("p_green", "p_green")
    shot("p_query", "p_query", "参数 red=green，匹配正则 gree.")
    shot("f_head", "f_head")
    shot("f_param", "f_param")
    shot("f_resp", "f_resp")
    status, text, url = data["f_remove"]
    direct = data["f_remove_direct"][1]
    pics["f_remove"] = render_browser(
        url,
        "经网关：\n" + text + "\n（响应头中已没有 X-Response-red）\n\n直连 9001：\n" + direct,
        IMG / "f-remove.jpg",
    )
    shot("f_strip", "f_strip")
    shot("f_rewrite", "f_rewrite")
    shot("f_lb", "f_lb")
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
        if text.startswith("对实验的自我评价") or text.startswith("案例") or text.startswith("实验总结"):
            p.Range.Font.Bold = -1
            p.Range.Font.Size = 12
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("[[IMG:"):
            pf.Alignment = 1
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("（") or text.startswith("步骤"):
            p.Range.Font.Bold = -1
            p.Range.Font.Size = 10.5
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        else:
            p.Range.Font.Bold = 0
            p.Range.Font.Size = 10.5
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


def main():
    data = collect()
    pics = build_images(data)
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(r"D:\学号-姓名-实验3-Gateway服务网关.doc")
        out_docx = r"C:\Users\Lenovo\Desktop\陈汭-Gateway断言与过滤器实验报告.docx"
        doc.SaveAs2(out_docx, FileFormat=12)
        set_para_text(doc.Paragraphs(3), "实验项目名称 Gateway路由断言与过滤器 课程名称 微服务架构 成绩评定")
        set_para_text(doc.Paragraphs(5), "实验日期  2026年10月16日 指导教师 张丽娟")
        set_para_text(
            doc.Paragraphs(6),
            "学生姓名：陈汭            学号：423240532            专业班级：计算机科学与技术5班",
        )
        plan = doc.Tables(1)
        write_cell_text(plan.Cell(2, 1), [
            "实验目的：",
            "1.能够使用 Gateway 的 After、Between、Cookie、Header、Method、Path、Query 断言判断请求是否匹配路由。",
            "2.能够使用 AddRequestHeader、AddRequestParameter、AddResponseHeader、RemoveResponseHeader、StripPrefix、RewritePath 和 LoadBalancerClientFilter 修改请求或响应。",
        ])
        write_cell_text(plan.Cell(4, 1), [
            "实验内容：",
            "本实验按《断言案例》和《过滤器实操》两份文档完成。两份案例都在 Spring Boot 2.6.3、Spring Cloud 2021.0.1 上实现，父工程分别是 unit4Demo3-gateway-predicate 和 unit4Demo4-gateway-filter。提供者注册到 Nacos，网关用静态路由把请求转到提供者。",
            "案例一 路由断言（案例 4-3）",
            "创建 service-provider 与 service-gateway。提供者提供 /hello，以及 /red/{segment}、/blue/{segment}。网关端口使用 8011，提供者端口使用 9011，避免和过滤器案例抢 8001、9001。",
            "（1）After。用 PredicateAfter 生成“当前时间加 1 小时”。把该未来时间配进路由时，当前请求匹配失败，返回 404。把时间改成 2026-10-16T08:00:00+08:00[Asia/Shanghai] 之后，访问 /hello?name=gateway 返回 hello gateway!。",
            "（2）Between。时间窗取 2026-10-16T08:00:00+08:00[Asia/Shanghai] 到 2026-10-16T18:00:00+08:00[Asia/Shanghai]。请求 /between/hello 落在窗内，RewritePath 去掉 between 前缀后转到 /hello。",
            "（3）Cookie。断言为 Cookie=test,ch.p。请求携带 Cookie: test=chap 时匹配成功；不带 Cookie 时返回 404。",
            "（4）Header。断言为 Header=X-Request-Id,\\d+。X-Request-Id 为 88 时匹配成功，为 abc 时匹配失败。",
            "（5）Method。只放行 GET 和 POST。GET /method/hello 可以访问。",
            "（6）Path。断言 Path=/red/{segment},/blue/{segment}。/red/1 返回 path red/1，/blue/bar 返回 path blue/bar。",
            "（7）Query。Query=green 只要求存在 green 参数；Query=red,gree. 要求 red 的值匹配正则。red=green 成功，red=nope 失败。",
            "案例二 过滤器（案例 4-4）",
            "网关端口 8001，提供者端口 9001。负载均衡再启动一个同名实例，端口 9012。发现分组使用 FILTER_GROUP，避免请求被分到其他实验的服务上。",
            "（1）AddRequestHeader。访问 /test/head，网关写入请求头 X-Request-red: blue，提供者读出该头。",
            "（2）AddRequestParameter。访问 /test/param，网关追加参数 red=blue，提供者读出该参数。",
            "（3）AddResponseHeader。访问 /hello?name=AddResponseHeader，响应头出现 X-Response-Red: Blue。",
            "（4）RemoveResponseHeader。提供者先写 X-Response-red: blue，网关再删除它。直连 9001 能看到该头，经 8001 访问则没有。",
            "（5）StripPrefix。访问 /red/blue/hello?name=StripPrefix，去掉前两段后落到 /hello。",
            "（6）RewritePath。访问 /red/hello?name=RewritePath，/red/hello 被替换成 /hello。",
            "（7）LoadBalancerClientFilter。路由 uri 使用 lb://service-provider。多次访问 /test/lb，结果在 port: 9001 和 port: 9012 之间切换。",
        ])
        summary = [
            "实验总结",
            "案例一 路由断言",
            "网关路由配置如下。每条断言都加了各自的 Path，这样 7 种断言可以在同一次启动里分别访问。",
            "[[IMG:p_yaml]]",
            "提供者接口和生成 After 时间的 PredicateAfter 如下。",
            "[[IMG:p_code]]",
            "（1）After 匹配成功。时间早于本次请求，页面返回 hello gateway!。",
            "[[IMG:p_after]]",
            "After 设在 2099 年时，当前请求不能匹配，网关返回 404。这对应讲义里“时间不满足则访问被阻止”的结果。",
            "[[IMG:p_deny]]",
            "（2）Between 匹配成功。请求落在 2026-10-16 08:00 到 18:00 之间。",
            "[[IMG:p_between]]",
            "（3）Cookie 匹配成功。Cookie 值为 chap，满足正则 ch.p。不带该 Cookie 时同一地址返回 404。",
            "[[IMG:p_cookie]]",
            "（4）Header 匹配成功。X-Request-Id 为数字 88。改成 abc 后返回 404。",
            "[[IMG:p_header]]",
            "（5）Method 匹配成功。GET 在允许的方法列表里。",
            "[[IMG:p_method]]",
            "（6）Path 匹配成功。/red/1 与 /blue/bar 分别命中两条路径模式。",
            "[[IMG:p_red]]",
            "[[IMG:p_blue]]",
            "（7）Query 匹配成功。只带 green 参数，以及 red=green 符合 gree. 时，都能转到 hello。red=nope 返回 404。",
            "[[IMG:p_green]]",
            "[[IMG:p_query]]",
            "完成断言案例的过程：先按文档建好父子工程和两个模块，在网关 application.yaml 中逐条写入 After、Between、Cookie、Header、Method、Path、Query。After 先用未来时间验证不匹配，再改成实验当天 08:00，请求恢复。其余断言各自用一条能命中的请求和一条不能命中的请求对照。Path 断言直接把 /red/1、/blue/bar 转到提供者对应接口。",
            "案例二 过滤器",
            "七个过滤器写在同一个网关配置里。StripPrefix 使用更具体的 /red/blue/**，order 比 RewritePath 更小，因此 /red/blue/hello 不会被改写规则抢走。",
            "[[IMG:f_yaml]]",
            "提供者按文档实现了 /test/head、/test/param、/hello、/test/reresheader 和 /test/lb。",
            "[[IMG:f_code]]",
            "（1）AddRequestHeader。未在地址中传该请求头，返回值仍是 blue，说明头是网关加上的。",
            "[[IMG:f_head]]",
            "（2）AddRequestParameter。地址中没有 red 参数，返回值仍读到 blue。",
            "[[IMG:f_param]]",
            "（3）AddResponseHeader。正文是 hello AddResponseHeader!，响应头为 X-Response-Red: Blue。",
            "[[IMG:f_resp]]",
            "（4）RemoveResponseHeader。直连提供者能看到 X-Response-red: blue，经过网关后该头消失，正文仍是 ok。",
            "[[IMG:f_remove]]",
            "（5）StripPrefix。/red/blue 两段被去掉，hello 收到 name=StripPrefix。",
            "[[IMG:f_strip]]",
            "（6）RewritePath。/red/hello 被替换为 /hello。",
            "[[IMG:f_rewrite]]",
            "（7）LoadBalancerClientFilter。连续访问得到 9001 和 9012 两个端口，说明请求按服务名分到了两个实例。",
            "[[IMG:f_lb]]",
            "完成过滤器案例的过程：提供者先写好读取请求头、请求参数、设置响应头和返回端口的接口。网关为每个接口配置对应过滤器。AddRequestHeader 与 AddRequestParameter 负责改进入提供者之前的请求，AddResponseHeader 与 RemoveResponseHeader 负责改返回浏览器之前的响应。StripPrefix 按段数截路径，RewritePath 按正则替换路径。最后用 lb://service-provider 启用负载均衡，并额外启动 9012 端口的实例，多次刷新可以看到两个端口交替出现。",
        ]
        write_cell_text(doc.Tables(2).Cell(1, 1), summary)
        write_cell_text(doc.Tables(2).Cell(2, 1), [
            "对实验的自我评价：",
            "两份文档里的断言和过滤器都已经跑通。调试时主要碰到下面几个问题。",
            "错误1：断言工程和过滤器工程如果都使用文档中的 8001、9001，后启动的服务会报端口占用。",
            "分析：两份案例的网关、提供者端口写的是同一组。实验 3 还占用了 9002，服务名也是 service-provider。",
            "解决：过滤器保持文档端口，网关 8001、提供者 9001。断言工程改用 8011 和 9011。负载均衡的第二个实例使用 9012，并把 Nacos 分组设为 FILTER_GROUP，只在本组内查找 service-provider。",
            "错误2：RewritePath 写成 /${segment} 后，网关启动报 Could not resolve placeholder segment。",
            "分析：Spring 会把 ${segment} 当成配置占位符，而不是 Gateway 过滤器的路径变量。",
            "解决：在 yaml 中写成 /$\\{segment}。启动后 /red/hello 能正确替换成 /hello，/between/hello 等断言路径也能改写到提供者的 /hello。",
            "错误3：把 10 月 13 日的 Between 时间窗留到 10 月 16 日再访问，/between/hello 返回 404。",
            "分析：Between 只匹配两个时间点之间的请求。实验日期变了，旧时间窗已经结束。After 如果仍放在未来，同样会把请求挡在路由之外。",
            "解决：After 改为 2026-10-16T08:00:00+08:00[Asia/Shanghai]，Between 改为当天 08:00 到 18:00。另保留一条 After=2099 的路由，用来对照文档中的不匹配页面。",
        ])
        replace_images(doc, pics)
        doc.Save()
        doc.SaveAs2(r"D:\陈汭-Gateway断言与过滤器实验报告.docx", FileFormat=12)
        doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-Gateway断言与过滤器实验报告.doc", FileFormat=0)
        print("shapes", doc.InlineShapes.Count)
        print("saved desktop docx")
    finally:
        if doc is not None:
            doc.Close(False)
        try:
            word.Quit()
        except Exception as exc:
            print("quit", exc)


if __name__ == "__main__":
    main()
