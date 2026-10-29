# -*- coding: utf-8 -*-
"""Fill the Gateway lab report from the reproduced project and real responses."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\实验3-Gateway服务网关")
TASK1 = ROOT / "任务1-gateway-static"
TASK2 = ROOT / "任务2-3-gateway-dynamic"
RAW = ROOT / "screenshots" / "raw"
IMG = ROOT / "screenshots"
IMG.mkdir(parents=True, exist_ok=True)

FONT_CN = r"C:\Windows\Fonts\msyh.ttc"
FONT_CODE = r"C:\Windows\Fonts\consola.ttf"
FONT_UI = r"C:\Windows\Fonts\msyh.ttc"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_line(text, draw, fnt, max_w):
    if not text:
        return [""]
    lines = []
    cur = ""
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


def render_code(title, text, out_path, max_chars_width=108):
    fnt = font(FONT_UI, 15)
    header_fnt = font(FONT_UI, 16)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = 980
    body_lines = []
    for line in text.splitlines():
        body_lines.extend(wrap_line(line, dummy, fnt, max_w - 70))
    line_h = 20
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


def render_browser(url, body, out_path):
    ui = font(FONT_UI, 16)
    body_font = font(FONT_UI, 18)
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
    url_show = url if dummy.textlength(url, font=ui) < width - 50 else url[:90] + "..."
    draw.text((24, 48), url_show, font=ui, fill="#202124")
    y = bar_h + 8
    for line in lines:
        draw.text((24, y), line, font=body_font, fill="#111111")
        y += line_h
    img.save(out_path, quality=90)
    return out_path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def pretty_raw(name):
    text = (RAW / name).read_text(encoding="utf-8").strip()
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except Exception:
        return text


def build_images():
    paths = {}
    paths["t1_pom"] = render_code(
        "任务① / 任务1-gateway-static/pom.xml",
        read(TASK1 / "pom.xml"),
        IMG / "t1-pom.jpg",
    )
    tree1 = """任务1-gateway-static
├── pom.xml
├── service-provider
│   ├── pom.xml
│   └── src/main/java/cn/js/ccit
│       ├── ProviderApplication.java
│       └── controller/ProviderController.java
│   └── src/main/resources/application.yaml
└── service-gateway
    ├── pom.xml
    └── src/main/java/cn/js/ccit/GatewayApplication.java
    └── src/main/resources/application.yaml"""
    paths["t1_tree"] = render_code("任务① 工程结构", tree1, IMG / "t1-tree.jpg")
    paths["t1_ppom"] = render_code(
        "任务① / service-provider/pom.xml",
        read(TASK1 / "service-provider/pom.xml"),
        IMG / "t1-provider-pom.jpg",
    )
    paths["t1_gpom"] = render_code(
        "任务① / service-gateway/pom.xml",
        read(TASK1 / "service-gateway/pom.xml"),
        IMG / "t1-gateway-pom.jpg",
    )
    paths["t1_app"] = render_code(
        "任务① 启动类 ProviderApplication / GatewayApplication",
        read(TASK1 / "service-provider/src/main/java/cn/js/ccit/ProviderApplication.java")
        + "\n\n"
        + read(TASK1 / "service-gateway/src/main/java/cn/js/ccit/GatewayApplication.java"),
        IMG / "t1-app.jpg",
    )
    paths["t1_yaml"] = render_code(
        "任务① application.yaml",
        "service-provider:\n"
        + read(TASK1 / "service-provider/src/main/resources/application.yaml")
        + "\nservice-gateway:\n"
        + read(TASK1 / "service-gateway/src/main/resources/application.yaml"),
        IMG / "t1-yaml.jpg",
    )
    paths["t1_ctrl"] = render_code(
        "任务① ProviderController.java",
        read(TASK1 / "service-provider/src/main/java/cn/js/ccit/controller/ProviderController.java"),
        IMG / "t1-controller.jpg",
    )
    paths["t1_hello"] = render_browser(
        "http://localhost:8002/service-provider/hello?name=陈汭",
        "hello 陈汭!",
        IMG / "t1-hello.jpg",
    )

    paths["t2_pom"] = render_code(
        "任务② / 任务2-3-gateway-dynamic/pom.xml",
        read(TASK2 / "pom.xml"),
        IMG / "t2-pom.jpg",
    )
    tree2 = """任务2-3-gateway-dynamic
├── pom.xml
├── nacos
│   ├── gateway-route.json
│   ├── gateway-route-between.json
│   └── gateway-route-sing.json
├── service-provider
│   └── controller/ProviderController.java
└── service-gateway
    └── config
        ├── MyRouteWriter.java
        └── RouteNacos.java"""
    paths["t2_tree"] = render_code("任务②③ 工程结构", tree2, IMG / "t2-tree.jpg")
    paths["t2_ppom"] = render_code(
        "任务② / service-provider/pom.xml",
        read(TASK2 / "service-provider/pom.xml"),
        IMG / "t2-provider-pom.jpg",
    )
    paths["t2_gpom"] = render_code(
        "任务② / service-gateway/pom.xml",
        read(TASK2 / "service-gateway/pom.xml"),
        IMG / "t2-gateway-pom.jpg",
    )
    paths["t2_writer"] = render_code(
        "任务② MyRouteWriter.java",
        read(TASK2 / "service-gateway/src/main/java/cn/js/ccit/config/MyRouteWriter.java"),
        IMG / "t2-writer.jpg",
    )
    paths["t2_nacos"] = render_code(
        "任务② RouteNacos.java",
        read(TASK2 / "service-gateway/src/main/java/cn/js/ccit/config/RouteNacos.java"),
        IMG / "t2-nacos.jpg",
    )
    paths["t2_before"] = render_browser(
        "http://localhost:8002/actuator/gateway/routes",
        pretty_raw("routes-before.json"),
        IMG / "t2-before.jpg",
    )
    paths["t2_cfg"] = render_code(
        "Nacos 配置  dataId=gateway-route  group=GATEWAY_GROUP",
        read(TASK2 / "nacos/gateway-route.json"),
        IMG / "t2-config.jpg",
    )
    paths["t2_after"] = render_browser(
        "http://localhost:8002/actuator/gateway/routes",
        pretty_raw("routes-task2.json"),
        IMG / "t2-after.jpg",
    )
    paths["t2_hello"] = render_browser(
        "http://localhost:8002/provider/hello?name=陈汭",
        read(RAW / "hello-task2.txt").strip(),
        IMG / "t2-hello.jpg",
    )
    paths["t3_between_cfg"] = render_code(
        "任务③（1）Nacos 路由：Between + Path",
        read(TASK2 / "nacos/gateway-route-between.json"),
        IMG / "t3-between-cfg.jpg",
    )
    paths["t3_hello_code"] = render_code(
        "任务③ ProviderController.java",
        read(TASK2 / "service-provider/src/main/java/cn/js/ccit/controller/ProviderController.java"),
        IMG / "t3-hello-code.jpg",
    )
    paths["t3_between_page"] = render_browser(
        "http://localhost:8002/provider/hello?name=陈汭",
        read(RAW / "hello-between.txt").strip(),
        IMG / "t3-between-page.jpg",
    )
    paths["t3_sing_cfg"] = render_code(
        "任务③（2）Nacos 路由：/SingJumpRap/**  StripPrefix=2",
        read(TASK2 / "nacos/gateway-route-sing.json"),
        IMG / "t3-sing-cfg.jpg",
    )
    paths["t3_sing_page"] = render_browser(
        "http://localhost:8002/SingJumpRap/provider/hello?name=陈汭",
        read(RAW / "hello-sing.txt").strip(),
        IMG / "t3-sing-page.jpg",
    )
    paths["t3_sing_routes"] = render_browser(
        "http://localhost:8002/actuator/gateway/routes",
        pretty_raw("routes-sing.json"),
        IMG / "t3-sing-routes.jpg",
    )
    paths["t3_between_routes"] = render_browser(
        "http://localhost:8002/actuator/gateway/routes",
        pretty_raw("routes-between.json"),
        IMG / "t3-between-routes.jpg",
    )
    return paths


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
        if text.startswith("对实验的自我评价"):
            p.Range.Font.Bold = -1
            p.Range.Font.Size = 12
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("任务") or text.startswith("实验总结") or text.startswith("步骤") or text.startswith("（"):
            p.Range.Font.Bold = -1 if not text.startswith("步骤") else 0
            p.Range.Font.Size = 12 if text.startswith("任务") or text.startswith("实验总结") else 10.5
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("[[IMG:"):
            pf.Alignment = 1
            pf.CharacterUnitFirstLineIndent = 0
            p.Range.Font.Size = 10.5
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


def fill_summary(cell, pics):
    blocks = [
        ("实验总结", True, False),
        ("任务① 网关服务-基础配置与静态路由实践", True, False),
        ("步骤1：父工程 pom.xml，统一管理 Spring Boot 2.6.3、Spring Cloud 2021.0.1、Spring Cloud Alibaba 2021.0.1.0。", False, False),
        ("img", "t1_pom"),
        ("步骤2：创建 service-provider 与 service-gateway 两个子模块。", False, False),
        ("img", "t1_tree"),
        ("步骤3：service-provider 引入 Nacos Discovery 和 spring-boot-starter-web。", False, False),
        ("img", "t1_ppom"),
        ("步骤4：service-gateway 引入 Nacos Discovery、Gateway 和 LoadBalancer。网关使用 WebFlux，没有引入 spring-boot-starter-web。", False, False),
        ("img", "t1_gpom"),
        ("步骤5：两个模块分别编写启动类，并开启服务发现。", False, False),
        ("img", "t1_app"),
        ("步骤6：提供者端口 9002，网关端口 8002，Nacos 地址 localhost:8848。网关打开 discovery.locator，按服务名做静态路由。", False, False),
        ("img", "t1_yaml"),
        ("步骤7：提供者提供 /hello，用请求参数 name 拼接返回值。", False, False),
        ("img", "t1_ctrl"),
        ("步骤8：通过网关访问。地址是网关端口加服务名再加方法名。", False, False),
        ("img", "t1_hello"),
        ("完成任务①的过程：父工程先把三个版本锁住，再拆出提供者和网关。提供者注册到 Nacos，网关打开服务发现定位器之后，访问 http://localhost:8002/service-provider/hello?name=陈汭 ，浏览器返回 hello 陈汭!。请求没有直连 9002，而是由 8002 按服务名 service-provider 转发过去，静态路由生效。", False, True),
        ("任务② 网关服务-动态路由实践", True, False),
        ("步骤1：新建父工程 gateway-dynamic-route，依赖版本与任务①相同。", False, False),
        ("img", "t2_pom"),
        ("步骤2：仍然是 service-provider 和 service-gateway 两个子模块，路由 JSON 放在 nacos 目录，便于发布到配置中心。", False, False),
        ("img", "t2_tree"),
        ("步骤3：提供者依赖与任务①相同。", False, False),
        ("img", "t2_ppom"),
        ("步骤4：网关在任务①依赖之外增加 actuator 和 fastjson 1.2.83，并在 application.yaml 中暴露 gateway 端点。", False, False),
        ("img", "t2_gpom"),
        ("步骤5：MyRouteWriter 负责新增、更新路由，保存完成后再发布 RefreshRoutesEvent。", False, False),
        ("img", "t2_writer"),
        ("步骤6：RouteNacos 连接 localhost:8848，读取并监听 dataId=gateway-route、group=GATEWAY_GROUP。", False, False),
        ("img", "t2_nacos"),
        ("步骤7：Nacos 里还没有该配置时，网关启动日志打印 route config 为 null，路由端点返回空数组。", False, False),
        ("img", "t2_before"),
        ("步骤8：向 Nacos 发布 GATEWAY_GROUP 组下的 gateway-route。Path 为 /provider/**，StripPrefix 去掉 1 段，uri 为 lb://service-provider。发布接口返回 true。", False, False),
        ("img", "t2_cfg"),
        ("步骤9：配置推送后，路由端点出现 provider_route，断言为 /provider/**，过滤器 StripPrefix parts = 1。", False, False),
        ("img", "t2_after"),
        ("步骤10：不再把服务名写进路径，由 /provider 前缀匹配动态路由。提供者的 hello 已按任务③改成带时间的返回值，所以这里一并看到时间和姓名。", False, False),
        ("img", "t2_hello"),
        ("完成任务②的过程：网关启动时本地没有路由，actuator 返回 []。把 JSON 发布到 Nacos 的 GATEWAY_GROUP/gateway-route 后，监听器收到变更并刷新本地路由。再次访问路由端点能看到 provider_route。请求 http://localhost:8002/provider/hello?name=陈汭 被转到 service-provider 的 /hello。动态路由不需要重启网关。", False, True),
        ("任务③ 网关服务-断言与过滤器实践", True, False),
        ("（1）Between 断言。时间窗取 2026-10-13T19:00:00+08:00[Asia/Shanghai] 到 2026-10-13T22:00:00+08:00[Asia/Shanghai]，覆盖本次实验请求的时间。Path 仍为 /provider/**。", False, False),
        ("img", "t3_between_cfg"),
        ("hello 使用 Asia/Shanghai 的 ZonedDateTime，格式为 DateTimeFormatter.ISO_ZONED_DATE_TIME。", False, False),
        ("img", "t3_hello_code"),
        ("刷新后的路由同时包含 Between 和 Path。在时间窗内发送请求，浏览器同时显示完整 URL 和响应。", False, False),
        ("img", "t3_between_routes"),
        ("img", "t3_between_page"),
        ("（2）Path 改为 /SingJumpRap/**，StripPrefix 的 parts 为 2，去掉路径前两段。", False, False),
        ("img", "t3_sing_cfg"),
        ("路由列表中 StripPrefix parts = 2。访问 http://localhost:8002/SingJumpRap/provider/hello?name=陈汭 时，SingJumpRap 和 provider 被去掉，剩余 /hello。", False, False),
        ("img", "t3_sing_routes"),
        ("img", "t3_sing_page"),
        ("完成任务③的过程：任务③沿用任务②的工程。第一条配置在原路由上增加 Between，只有落在时间窗里的 /provider/** 请求才会转发，hello 返回姓名和 ISO_ZONED_DATE_TIME 时间。第二条配置把断言改成 /SingJumpRap/**，并用 StripPrefix 截掉前两段，所以浏览器地址和任务③（1）不同，响应仍然来自同一个 hello 方法。两次修改都是改 Nacos 配置触发的，网关进程没有重启。", False, True),
    ]
    paragraphs = []
    for item in blocks:
        if item[0] == "img":
            paragraphs.append("[[IMG:%s]]" % item[1])
        else:
            paragraphs.append(item[0])
    write_cell_text(cell, paragraphs)


def fill_eval(cell):
    paras = [
        "对实验的自我评价：",
        "这次实验把 Gateway 的静态发现路由、Nacos 动态路由、Between 断言和 StripPrefix 过滤器串起来跑通了。调试时主要碰到下面几个问题。",
        "错误1：按讲义把过滤器参数写成 _gen_0 后，路由端点里 StripPrefix 的 parts 一直是 1；再加上 Between 时，刷新路由报 BindException，datetime1 和 datetime2 为 null。",
        "分析：Spring Cloud Gateway 3.1.1 里，StripPrefix 的配置字段是 parts，Between 的字段是 datetime1、datetime2。快捷参数名是 _genkey_0，不是讲义里的 _gen_0。_gen_0 绑不上去，parts 就保持默认值 1，Between 的两个时间也是 null，整次路由刷新失败，旧路由还留在内存里。",
        "解决：Nacos 的 JSON 改为 parts、datetime1、datetime2。改完后路由端点能看到 Between 时间窗，以及 StripPrefix parts = 2，/SingJumpRap/provider/hello 能正确落到 /hello。",
        "错误2：第一次把配置推到 Nacos 时，控制台出现 RouteDefinition not found: MonoJust。",
        "分析：MyRouteWriter.update 里的 delete 和 save 返回的是 Mono，只调用不订阅就不会执行。讲义示例在路由还不存在时就 delete，InMemoryRouteDefinitionRepository 找不到 id，异常信息里把 Mono 对象打印成了 MonoJust。另外 RefreshRoutesEvent 如果发得比保存更早，端点里看到的仍是旧路由。",
        "解决：删除时用 onErrorResume 忽略“路由不存在”，再用 then 接上 save，block 等到写完，最后再发布 RefreshRoutesEvent。",
        "错误3：讲义步骤 8 写的组名是 GATEWAY-GROUP，RouteNacos 里的常量是 GATEWAY_GROUP。",
        "分析：监听器只订阅代码里的 dataId 和 group。组名多一个横线或少一个下划线，配置发布成功也不会进网关。",
        "解决：控制台和接口都使用 GATEWAY_GROUP，dataId 使用 gateway-route，和代码常量保持一致。",
        "错误4：步骤 10 的示例地址写成了 /hello，用这个地址访问返回 404。",
        "分析：动态路由的 Path 是 /provider/**。不带 provider 前缀就匹配不到这条路由。StripPrefix 会再去掉这一段，服务端实际收到的才是 /hello。任务③（2）同理，要带两段前缀 /SingJumpRap/provider，过滤器去掉两段后才是 /hello。",
        "解决：任务②和任务③（1）使用 http://localhost:8002/provider/hello?name=陈汭 ；任务③（2）使用 http://localhost:8002/SingJumpRap/provider/hello?name=陈汭 。",
    ]
    write_cell_text(cell, paras)


def main():
    pics = build_images()
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        src = r"D:\学号-姓名-实验3-Gateway服务网关.doc"
        doc = word.Documents.Open(src)
        out_docx = r"D:\陈汭-实验3-Gateway服务网关.docx"
        doc.SaveAs2(out_docx, FileFormat=12)
        set_para_text(doc.Paragraphs(5), "实验日期  2026年10月13日 指导教师 张丽娟")
        set_para_text(
            doc.Paragraphs(6),
            "学生姓名：陈汭            学号：423240532            专业班级：计算机科学与技术5班",
        )
        table = doc.Tables(2)
        fill_summary(table.Cell(1, 1), pics)
        fill_eval(table.Cell(2, 1))
        replace_images(doc, pics)
        doc.Save()
        out_doc = r"D:\陈汭-实验3-Gateway服务网关.doc"
        doc.SaveAs2(out_doc, FileFormat=0)
        print("saved", out_docx)
        print("saved", out_doc)
        print("images", doc.InlineShapes.Count)
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()


if __name__ == "__main__":
    main()
