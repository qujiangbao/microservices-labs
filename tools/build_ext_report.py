# -*- coding: utf-8 -*-
"""Write the extension lab report from the runs on this machine."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\拓展-Sentinel网关与Dubbo")
IMG = ROOT / "screenshots"
IMG.mkdir(parents=True, exist_ok=True)
FONT = r"C:\Windows\Fonts\msyh.ttc"


def font(size):
    return ImageFont.truetype(FONT, size)


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


def render_block(title, text, out_path, bg="#0c0c0c", fg="#d4d4d4"):
    fnt = font(16)
    header = font(18)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = 1100
    body = []
    for line in text.splitlines():
        body.extend(wrap_line(line, dummy, fnt, max_w - 40))
    line_h = 26
    header_h = 46
    height = header_h + 20 + line_h * len(body) + 18
    img = Image.new("RGB", (max_w, height), bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, max_w, header_h), fill="#1f1f1f")
    draw.text((16, 12), title, font=header, fill="#ffffff")
    y = header_h + 12
    for line in body:
        draw.text((16, y), line, font=fnt, fill=fg)
        y += line_h
    img.save(out_path, quality=92)
    return str(out_path)


def add_text(doc, text, size=12, bold=False, center=False, space_after=6):
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    rng.Text = text + "\r"
    rng.Font.NameFarEast = "宋体"
    rng.Font.Name = "宋体"
    rng.Font.Size = size
    rng.Font.Bold = bold
    rng.Font.Color = 0
    rng.ParagraphFormat.Alignment = 1 if center else 0
    rng.ParagraphFormat.SpaceAfter = space_after
    rng.ParagraphFormat.SpaceBefore = 0
    rng.ParagraphFormat.LineSpacing = 18


def add_picture(doc, path):
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    shape = rng.InlineShapes.AddPicture(FileName=path, LinkToFile=False, SaveWithDocument=True)
    shape.LockAspectRatio = True
    if shape.Width > 450:
        shape.Width = 450
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    rng.InsertAfter("\r")


def main():
    pics = {
        "gw_log": render_block(
            "网关启动日志",
            "[Sentinel-Gateway] 已加载网关流控规则: "
            "[GatewayFlowRule{resource='product', resourceMode=0, grade=1, count=5.0, intervalSec=1}]\n"
            "Netty started on port 9000\n"
            "Started GatewayApplication in 14.187 seconds",
            IMG / "gw-log.png",
        ),
        "pass": render_block(
            "单次访问 GET http://127.0.0.1:9000/product/products",
            "HTTP 200\n"
            '{"code":200,"success":true,"data":[{"name":"玫瑰花束","price":100},{"name":"百合花束","price":80}]}',
            IMG / "product-pass.png",
            bg="#102117",
            fg="#d7f5df",
        ),
        "block": render_block(
            "同一秒并发 20 次",
            "状态码统计：200 共 5 次，429 共 15 次\n"
            "429 响应体：\n"
            '{"path":"/product/products","code":429,"success":false,\n'
            ' "message":"当前访问人数过多，请稍后再试（Sentinel 网关限流）"}',
            IMG / "product-block.png",
            bg="#2a1414",
            fg="#ffd0d0",
        ),
        "dubbo_log": render_block(
            "order / goldCoin 启动与压测日志",
            "[Sentinel-Dubbo] 已加载流控规则: count=2.0\n"
            "resource=cn.js.ccit.common.dubbo.GoldCoinService:updateGoldCoin(java.lang.String,java.lang.Integer,java.lang.String)\n"
            "[Sentinel-Dubbo] 已加载熔断降级规则: 异常比例 0.5，最小请求数 5，统计窗口 10 秒，熔断时长 10 秒\n"
            "[Sentinel-Dubbo-Provider] 已加载提供方流控规则: count=5.0\n"
            "[goldCoin] 发放金币 user=zhangsan, coin=10, orderNo=NO28746725284300\n"
            "[goldCoin] 发放金币 user=zhangsan, coin=10, orderNo=NO28746936034700\n"
            "[Sentinel-Dubbo] 下单发金币被拦截(限流/熔断): method=updateGoldCoin, rule=FlowRule{count=2.0}\n"
            "以上拦截日志共 9 条。下单接口 11 次调用全部 HTTP 200，正文 ok。",
            IMG / "dubbo-log.png",
        ),
    }

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Add()
    try:
        add_text(doc, "广州华商学院实验报告", 18, True, True, 8)
        add_text(doc, "拓展：Sentinel 网关限流与 Dubbo 熔断降级", 16, True, True, 10)
        add_text(doc, "课程名称：微服务架构          实验日期：2026年10月27日          指导教师：张丽娟", 12, False, False, 2)
        add_text(doc, "学生姓名：陈汭          学号：423240532          专业班级：23本计算机科学与技术5班", 12, False, False, 10)

        add_text(doc, "一、实验目的", 14, True, False, 4)
        add_text(doc, "1. 用 Sentinel 对鲜花商城商品查询路由做网关限流。路由 id 为 product，QPS 阈值为 5，超过后返回自定义 429 JSON。", 12)
        add_text(doc, "2. 用 Sentinel 对下单发金币的 Dubbo 调用做流控、异常比例熔断和 fallback。消费端 QPS 为 2，提供端 QPS 为 5。被拦截时下单接口仍返回成功。", 12)

        add_text(doc, "二、实验环境", 14, True, False, 4)
        add_text(doc, "Windows 11，JDK 11.0.31，Maven 3.9.9，Spring Boot 2.6.3，Spring Cloud 2021.0.1，Spring Cloud Alibaba 2021.0.1.0，Sentinel 1.8.3，Dubbo 2.7.15。", 12)
        add_text(doc, "本机没有 flowersmall 全量工程，也没有导入 mall_product、mall_order 数据库。案例要求的两条 Sentinel 规则用四个可运行服务复现：product 端口 8001，order 端口 8002，goldCoin 端口 8003、Dubbo 20880，gateway 端口 9000。网关路由 id 手写为 product 和 order，转发到本机服务。Dubbo 使用直连 dubbo://127.0.0.1:20880，没有经过 Nacos。规则都在代码里用 @PostConstruct 加载。", 12)

        add_text(doc, "三、案例一：商品查询网关限流", 14, True, False, 4)
        add_text(doc, "网关把 /product/** 转到 product 服务，并去掉前缀。SentinelGatewayConfig 在启动时加载路由规则：资源名 product，资源模式为路由 id，QPS 阈值 5，统计间隔 1 秒。限流后的响应由 GatewayCallbackManager 返回 429，正文包含 code、success、message、path。", 12)
        add_text(doc, "步骤文档里的三个 import 在 Sentinel 1.8.3 中不存在。GatewayFlowRule 和 GatewayRuleManager 的实际包名是 com.alibaba.csp.sentinel.adapter.gateway.common.rule，路由模式常量在 SentinelGatewayConstants 里。按实际包名修改后才能编译。spring-cloud-alibaba-sentinel-gateway 会自动注册 SentinelGatewayFilter，配置类里没有再声明这两个 Bean。", 12)
        add_picture(doc, pics["gw_log"])
        add_text(doc, "图1  网关已加载 product 路由的 QPS=5 规则，并在 9000 端口启动", 10.5, False, False, 8)
        add_text(doc, "先单独访问一次，商品列表正常返回。再在同一秒内并发 20 次。阈值是 5，所以 5 次为 200，另外 15 次为 429。", 12)
        add_picture(doc, pics["pass"])
        add_text(doc, "图2  未触发限流时返回玫瑰花束和百合花束", 10.5, False, False, 6)
        add_picture(doc, pics["block"])
        add_text(doc, "图3  超过 5 QPS 后返回案例要求的自定义 429 JSON", 10.5, False, False, 8)

        add_text(doc, "四、案例二：下单发金币的 Dubbo 流控与降级", 14, True, False, 4)
        add_text(doc, "资源名按接口全限定名、方法名和参数类型写成：cn.js.ccit.common.dubbo.GoldCoinService:updateGoldCoin(java.lang.String,java.lang.Integer,java.lang.String)。order 加载两条规则：QPS 阈值 2；异常比例熔断，阈值 0.5，10 秒内至少 5 次请求，熔断打开 10 秒。goldCoin 再加载提供方 QPS 阈值 5。两边的 fallback 都返回 null，不把异常抛回下单接口。", 12)
        add_text(doc, "sentinel-apache-dubbo-adapter 的版本写成 1.8.3。步骤文档把 CircuitBreakerStrategy 写在 degrade 包下，1.8.3 里这个类在 degrade.circuitbreaker 包，import 改到这个包后编译通过。", 12)
        add_text(doc, "order 比 goldCoin 更早完成启动，日志里有一次 Connection refused: 20880。消费端 check 为 false，进程没有退出。goldCoin 监听 20880 之后，下单调用可以连上。", 12)
        add_text(doc, "验证时先发 1 次下单，再并发 10 次，一共 11 次。接口全部返回 HTTP 200，正文是 ok。goldCoin 日志只有 2 条发放记录，order 日志有 9 条“下单发金币被拦截”，规则是消费端 QPS=2 的 FlowRule。被拦住的调用没有进入发放逻辑。这次提供方没有抛异常，异常比例熔断规则已加载，但没有被这次压测打开。", 12)
        add_picture(doc, pics["dubbo_log"])
        add_text(doc, "图4  消费端 QPS=2 生效：11 次下单里 2 次发出金币，9 次被 fallback 接住，下单接口仍返回 ok", 10.5, False, False, 8)

        add_text(doc, "五、实验总结", 14, True, False, 4)
        add_text(doc, "网关限流保护的是进入 product 路由的全部请求，不区分参数。QPS 设为 5 时，同一秒 20 次访问里只有 5 次拿到商品数据，其余 15 次立刻返回 429，后端 product 不会被这 15 次打到。", 12)
        add_text(doc, "Dubbo 限流保护的是 updateGoldCoin 这一次远程调用，不是整个下单接口。消费端 QPS 为 2 时，多出来的发金币调用被 fallback 变成空结果，下单主流程继续返回 ok。这样演示的是“订单可以成功，超出阈值的金币不再发放”。提供方 QPS 为 5，阈值高于消费端，所以这次先被消费端拦住。", 12)
        add_text(doc, "如果要求没发出金币就必须让订单失败，fallback 应改为把异常抛回去，让上层事务回滚。本次按案例要求使用返回 null 的优雅降级。", 12)
    finally:
        targets = [
            r"D:\423240532-陈汭-拓展-Sentinel网关限流与Dubbo熔断.docx",
            r"C:\Users\Lenovo\Desktop\423240532-陈汭-拓展-Sentinel网关限流与Dubbo熔断.docx",
            str(ROOT / "423240532-陈汭-拓展-Sentinel网关限流与Dubbo熔断.docx"),
        ]
        for path in targets:
            doc.SaveAs2(path, FileFormat=12)
        print("saved", doc.InlineShapes.Count)
        doc.Close(False)
        try:
            word.Quit()
        except Exception as exc:
            print("quit", exc)


if __name__ == "__main__":
    main()
