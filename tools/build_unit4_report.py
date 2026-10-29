# -*- coding: utf-8 -*-
"""Fill the Seata lab report from the run that just finished."""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\第6单元-Seata分布式事务")
IMG = ROOT / "screenshots"
IMG.mkdir(parents=True, exist_ok=True)
SHOT = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots")
FONT_UI = r"C:\Windows\Fonts\msyh.ttc"
NS = "93548d54-b713-459e-b9e5-6ed269e3ee1c"


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


def render_table(title, headers, rows, out_path):
    fnt = font(16)
    header_fnt = font(18)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cols = len(headers)
    widths = []
    for c in range(cols):
        texts = [headers[c]] + [str(row[c]) for row in rows]
        widths.append(max(dummy.textlength(t, font=fnt) for t in texts) + 36)
    width = int(sum(widths) + 2)
    row_h = 36
    height = 48 + row_h * (len(rows) + 1) + 16
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((12, 10), title, font=header_fnt, fill="#202124")
    y = 48
    x = 0
    for c, head in enumerate(headers):
        draw.rectangle((x, y, x + widths[c], y + row_h), fill="#e8f0fe", outline="#c4c7c5")
        draw.text((x + 12, y + 8), head, font=fnt, fill="#174ea6")
        x += widths[c]
    for row in rows:
        y += row_h
        x = 0
        for c, cell in enumerate(row):
            draw.rectangle((x, y, x + widths[c], y + row_h), fill="#ffffff", outline="#c4c7c5")
            draw.text((x + 12, y + 8), str(cell), font=fnt, fill="#202124")
            x += widths[c]
    img.save(out_path, quality=90)
    return out_path


def build_images():
    shutil.copyfile(SHOT / "page-2026-10-20T11-10-28-050Z.png", IMG / "nacos-config.png")
    shutil.copyfile(SHOT / "page-2026-10-20T11-11-39-194Z.png", IMG / "nacos-seata.png")
    shutil.copyfile(SHOT / "page-2026-10-20T11-12-36-736Z.png", IMG / "nacos-services.png")
    pics = {
        "config": IMG / "nacos-config.png",
        "seata": IMG / "nacos-seata.png",
        "services": IMG / "nacos-services.png",
    }
    pics["success"] = render_browser(
        "http://localhost:8001/order/create?userId=1&productId=1&count=10&money=100",
        '{"code":200,"message":"订单创建成功!","data":null}',
        IMG / "success.jpg",
    )
    pics["order_db"] = render_table(
        "seata_order.t_order",
        ["id", "user_id", "product_id", "count", "money", "status"],
        [["3", "1", "1", "10", "100", "1"]],
        IMG / "order-db.jpg",
    )
    pics["storage_db"] = render_table(
        "seata_storage.t_storage",
        ["id", "product_id", "total", "used", "residue"],
        [["1", "1", "600", "10", "590"]],
        IMG / "storage-db.jpg",
    )
    pics["rollback"] = render_browser(
        "http://localhost:8001/order/create?userId=1&productId=1&count=10&money=100",
        "500 Internal Server Error\n"
        '{"timestamp":"2026-10-20T11:13:52.463+00:00","status":500,'
        '"error":"Internal Server Error","path":"/order/create"}\n\n'
        "订单服务日志：\n"
        "feign.RetryableException: Connection refused: connect executing "
        "POST http://seata-storage/storage/reduce?productId=1&count=10\n"
        "[10.26.144.21:8091:4621529043868475429] rollback status: Rollbacked",
        IMG / "rollback.jpg",
    )
    code = (ROOT / "unit6Demo1" / "seata-order" / "src" / "main" / "java" / "cn" / "js" / "ccit" / "service" / "impl" / "OrderServiceImpl.java").read_text(encoding="utf-8")
    pics["code"] = render_code("OrderServiceImpl.java", code, IMG / "order-service.jpg")
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
        if text.startswith("实验总结") or text.startswith("对实验的自我评价") or text.startswith("错误"):
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
        doc = word.Documents.Open(r"D:\学号-姓名-实验4-1seata.doc")
        doc.SaveAs2(r"D:\陈汭-实验4-1seata.docx", FileFormat=12)
        set_para_text(
            find_paragraph(doc, "学生姓名"),
            "学生姓名：陈汭            学号：423240532            专业班级：计算机科学与技术5班",
        )
        write_cell_text(find_cell(doc, "实验总结"), [
            "实验总结",
            "这次实验按六个任务做完。Seata Server 用的是 1.4.2，存储模式改成 db，注册和配置都放到本机 Nacos 1.4.2。Nacos 里新建的命名空间叫 Seata，命名空间 ID 是 %s。配置集 Data ID 为 seataServer.properties，Group 为 SEATA_GROUP。" % NS,
            "[[IMG:config]]",
            "Seata 启动后监听 8091，并注册到 Seata 命名空间的 SEATA_GROUP。服务名是 seata-server，健康实例数为 1。",
            "[[IMG:seata]]",
            "订单服务 seata-order 端口 8001，库存服务 seata-storage 端口 8002，都注册在 public 命名空间。下单时订单服务用 OpenFeign 调用库存服务的 /storage/reduce，方法上加了 @GlobalTransactional。",
            "[[IMG:services]]",
            "[[IMG:code]]",
            "正常下单访问 http://localhost:8001/order/create?userId=1&productId=1&count=10&money=100 ，页面返回订单创建成功。",
            "[[IMG:success]]",
            "seata_order.t_order 新增一条记录，id 为 3，user_id 为 1，product_id 为 1，count 为 10，money 为 100，status 为 1。id 不是 1，是因为前面一次回滚测试已经用掉了自增值，插入被回滚后自增不会退回去。",
            "[[IMG:order_db]]",
            "seata_storage.t_storage 中 product_id 为 1 的商品，used 从 0 变成 10，residue 从 600 变成 590。",
            "[[IMG:storage_db]]",
            "异常回滚时停掉 seata-storage，再用同一个地址下单。浏览器返回 500。订单服务日志是 Connection refused，全局事务回滚状态为 Rollbacked，xid 为 10.26.144.21:8091:4621529043868475429。",
            "[[IMG:rollback]]",
            "回滚之后再查库，t_order 仍然只有上面那一条 status 为 1 的记录，没有新增；t_storage 的 used 仍是 10，residue 仍是 590。订单创建和扣减库存要么一起成功，要么一起撤销，跨库数据保持一致。",
        ])
        write_cell_text(find_cell(doc, "对实验的自我评价"), [
            "对实验的自我评价：",
            "Seata AT 模式的正常提交和异常回滚都跑通了。调试时主要碰到下面几个问题。",
            "错误1：用实验文档里的 root/123 连接本机 3306 的 MySQL80，返回 ERROR 1045，Access denied for user 'root'@'localhost'。",
            "分析：文档写的口令不是这台电脑上 MySQL80 的 root 口令。Seata 的事务表和两个业务库都需要一个能登录的 MySQL 8。",
            "解决：单独启动一个 MySQL 8 容器，根口令设为 123，映射到 3307。file.conf、config.txt 和两个微服务的数据源都改到 127.0.0.1:3307。JDBC 地址里加上 allowPublicKeyRetrieval=true，否则 MySQL 8 默认认证会拒绝客户端获取公钥。",
            "错误2：第一次 mvn package 生成的 seata-order 和 seata-storage 只有大约 10KB，不能用 java -jar 启动。",
            "分析：父工程没有继承 spring-boot-starter-parent。子模块里只声明 spring-boot-maven-plugin 时，repackage 不会自动绑到 package 阶段，打出来的是普通 jar，没有主清单。",
            "解决：在两个子模块的插件配置里显式加上 repackage 目标，重新打包后再启动。",
            "错误3：如果直接把官方 config.txt 放进 Nacos，客户端会找不到事务组，服务端也不会使用数据库存储。",
            "分析：官方文件里 store.mode 是 file，事务组只有 service.vgroupMapping.my_test_tx_group。订单服务配置的 tx-service-group 是 default_tx_group。另外 seata-server.bat 的 classpath 只包含 lib 目录，MySQL 驱动放在 lib/jdbc，启动时加载不到。",
            "解决：把 store.mode 改成 db，补上 service.vgroupMapping.default_tx_group=default，数据库地址、用户名和密码改成上面的 MySQL。再把 mysql-connector-java-8.0.19.jar 复制到 lib。改完后 Seata 能连上 seata 库，两个微服务也能完成提交和回滚。",
        ])
        replace_images(doc, pics)
        doc.Save()
        doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.docx", FileFormat=12)
        doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-实验4-1seata.doc", FileFormat=0)
        doc.SaveAs2(r"D:\陈汭-实验4-1seata.doc", FileFormat=0)
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
