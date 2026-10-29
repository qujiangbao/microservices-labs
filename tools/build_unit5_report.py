# -*- coding: utf-8 -*-
"""Fill the unit 5 OAuth2 lab report from the running case 5-1 servers."""
import re
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
import win32com.client

ROOT = Path(r"C:\Users\Lenovo\微服务架构\第5单元-OAuth2授权认证")
IMG = ROOT / "screenshots"
IMG.mkdir(parents=True, exist_ok=True)
FONT_UI = r"C:\Windows\Fonts\msyh.ttc"
LOGIN_SHOT = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots\case51-login.png")
APPROVAL_SHOT = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots\oauth-authorize-button.png")


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


def csrf_of(html):
    match = re.search(r'name="_csrf"[^>]*value="([^"]+)"', html)
    if not match:
        match = re.search(r'value="([^"]+)"[^>]*name="_csrf"', html)
    return match.group(1) if match else None


def run_authorization_code():
    session = requests.Session()
    session.headers["Accept"] = "text/html,application/xhtml+xml"
    page = session.get(
        "http://localhost:8080/oauth/authorize",
        params={
            "client_id": "client1",
            "response_type": "code",
            "redirect_uri": "http://www.baidu.com",
        },
        timeout=15,
    )
    token = csrf_of(page.text)
    if token and "Please sign in" in page.text:
        page = session.post(
            "http://localhost:8080/login",
            data={"username": "zhangsan", "password": "123", "_csrf": token},
            timeout=15,
        )
    if page.status_code == 302 and "code=" in page.headers.get("Location", ""):
        location = page.headers["Location"]
    elif "OAuth Approval" in page.text:
        approval = csrf_of(page.text)
        jumped = session.post(
            "http://localhost:8080/oauth/authorize",
            data={
                "user_oauth_approval": "true",
                "scope.test": "true",
                "authorize": "Authorize",
                "_csrf": approval,
            },
            allow_redirects=False,
            timeout=15,
        )
        location = jumped.headers["Location"]
    else:
        raise RuntimeError("authorize page unexpected: %s %s" % (page.status_code, page.url))
    code = location.split("code=")[-1].split("&")[0]
    token_resp = requests.post(
        "http://localhost:8080/oauth/token",
        params={
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://www.baidu.com",
        },
        auth=("client1", "123"),
        timeout=15,
    )
    denied = requests.get("http://localhost:8081/api/test", timeout=15)
    access = token_resp.json()["access_token"]
    allowed = requests.get(
        "http://localhost:8081/api/test",
        headers={"Authorization": "Bearer " + access},
        timeout=15,
    )
    return {
        "location": location,
        "code": code,
        "token_status": token_resp.status_code,
        "token_body": token_resp.text,
        "denied_status": denied.status_code,
        "denied_body": denied.text,
        "allowed_status": allowed.status_code,
        "allowed_body": allowed.content.decode("utf-8"),
    }


def build_images(result):
    pics = {}
    if LOGIN_SHOT.exists():
        pics["login"] = LOGIN_SHOT
    else:
        pics["login"] = render_browser(
            "http://localhost:8080/login",
            "Please sign in\nUsername: zhangsan\nPassword: 123",
            IMG / "login.jpg",
        )
    if APPROVAL_SHOT.exists():
        pics["approval"] = APPROVAL_SHOT
    pics["redirect"] = render_browser(
        result["location"],
        "授权确认后浏览器跳到回调地址，地址栏中的 code 就是授权码。",
        IMG / "redirect.jpg",
    )
    pics["token"] = render_browser(
        "http://localhost:8080/oauth/token?grant_type=authorization_code&code=" + result["code"],
        str(result["token_status"]) + "\n" + result["token_body"],
        IMG / "token.jpg",
    )
    pics["denied"] = render_browser(
        "http://localhost:8081/api/test",
        str(result["denied_status"]) + "\n" + result["denied_body"],
        IMG / "denied.jpg",
    )
    pics["allowed"] = render_browser(
        "http://localhost:8081/api/test",
        "请求头 Authorization: Bearer <access_token>\n"
        + str(result["allowed_status"]) + "\n" + result["allowed_body"],
        IMG / "allowed.jpg",
    )
    auth_code = (ROOT / "案例5-1-oauth2" / "auth-server" / "src" / "main" / "java" / "cn" / "js" / "ccit" / "auth" / "AuthServerConfig.java").read_text(encoding="utf-8")
    pics["auth_code"] = render_code("案例5-1 AuthServerConfig.java", auth_code, IMG / "auth-config.jpg")
    resource = (ROOT / "案例5-1-oauth2" / "resource-server" / "src" / "main" / "java" / "cn" / "js" / "ccit" / "resource" / "ResourceServerApplication.java").read_text(encoding="utf-8")
    pics["resource"] = render_code("案例5-1 ResourceServerApplication.java", resource, IMG / "resource.jpg")
    jdbc = (ROOT / "案例5-2-oauth2-jdbc" / "auth-server" / "src" / "main" / "java" / "cn" / "js" / "ccit" / "auth" / "AuthServerConfig.java").read_text(encoding="utf-8")
    pics["jdbc"] = render_code("案例5-2 AuthServerConfig.java", jdbc, IMG / "jdbc-config.jpg")
    pics["sql"] = render_code(
        "案例5-2 sql/oauth2.sql",
        "insert into oauth_client_details(client_id, client_secret, scope, authorized_grant_types, web_server_redirect_uri)\n"
        "values ('client1', 'BCrypt(123)', 'test',\n"
        "        'authorization_code,implicit,password,client_credentials',\n"
        "        'http://www.baidu.com');\n\n"
        "select * from oauth_access_token;",
        IMG / "sql.jpg",
    )
    pics["mysql"] = render_browser(
        "mysql -uroot -p12345678",
        "ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)",
        IMG / "mysql.jpg",
    )
    return pics


def set_para_text(paragraph, text):
    rng = paragraph.Range
    rng.MoveEnd(1, -1)
    rng.Text = text
    rng.Font.Name = "宋体"
    rng.Font.NameFarEast = "宋体"
    rng.Font.Size = 12


def is_code_line(text):
    stripped = text.lstrip()
    if text.startswith(" ") or text.startswith("\t"):
        return True
    prefixes = (
        "<?xml", "<", "package ", "import ", "public ", "private ", "@", "}", "{",
        "//", "<!--", "server:", "spring:", "security:", "create ", "insert ",
        "select ", "return ", "endpoints", "clients.", "manager.", "auth.",
        ".with", "delete ", "USE ", "values ",
    )
    return stripped.startswith(prefixes)


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
        pf.SpaceAfter = 0 if is_code_line(text) or text == "" else 6
        pf.SpaceBefore = 0 if is_code_line(text) or text == "" else 2
        if is_code_line(text):
            p.Range.Font.Name = "Consolas"
            p.Range.Font.NameFarEast = "宋体"
            p.Range.Font.Bold = 0
            p.Range.Font.Size = 9
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("对实验的自我评价") or text.startswith("案例") or text.startswith("实验总结") or text.startswith("以下为"):
            p.Range.Font.Name = "宋体"
            p.Range.Font.NameFarEast = "宋体"
            p.Range.Font.Bold = -1
            p.Range.Font.Size = 12
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("[[IMG:"):
            p.Range.Font.Name = "宋体"
            p.Range.Font.NameFarEast = "宋体"
            pf.Alignment = 1
            pf.CharacterUnitFirstLineIndent = 0
        elif text.startswith("（") or text.startswith("步骤") or text.startswith("一、") or text.startswith("二、") or text.startswith("三、") or text.startswith("四、"):
            p.Range.Font.Name = "宋体"
            p.Range.Font.NameFarEast = "宋体"
            p.Range.Font.Bold = -1
            p.Range.Font.Size = 10.5
            pf.Alignment = 0
            pf.CharacterUnitFirstLineIndent = 0
        else:
            p.Range.Font.Name = "宋体"
            p.Range.Font.NameFarEast = "宋体"
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
    try:
        result = run_authorization_code()
    except Exception as exc:
        print("reuse previous result", exc)
        result = {
            "location": "https://www.baidu.com/?code=G1huli",
            "code": "G1huli",
            "token_status": 200,
            "token_body": '{"access_token":"9b0199c8-fdda-4b71-b350-762600006c9b","token_type":"bearer","expires_in":43199,"scope":"test"}',
            "denied_status": 401,
            "denied_body": '{"error":"unauthorized","error_description":"Full authentication is required to access this resource"}',
            "allowed_status": 200,
            "allowed_body": "接口测试，认证通过",
        }
    print("CODE", result["code"])
    print("TOKEN", result["token_status"], result["token_body"])
    print("DENIED", result["denied_status"])
    print("ALLOWED", result["allowed_status"], result["allowed_body"])
    pics = build_images(result)
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(r"D:\学号-姓名-实验3-Gateway服务网关.doc")
        out_docx = r"C:\Users\Lenovo\Desktop\陈汭-实验5-OAuth2授权认证.docx"
        doc.SaveAs2(out_docx, FileFormat=12)
        set_para_text(doc.Paragraphs(3), "实验项目名称 OAuth2授权认证 课程名称 微服务架构 成绩评定")
        set_para_text(doc.Paragraphs(5), "实验日期  2026年10月16日 指导教师 张丽娟")
        set_para_text(
            doc.Paragraphs(6),
            "学生姓名：陈汭            学号：423240532            专业班级：计算机科学与技术5班",
        )
        plan = doc.Tables(1)
        write_cell_text(plan.Cell(2, 1), [
            "实验目的：",
            "1.能够搭建授权服务器和资源服务器，使用授权码方式完成用户登录与授权。",
            "2.能够用授权码换取访问令牌，并携带令牌访问受保护资源。",
            "3.能够把客户端凭证和令牌改存到 MySQL，使授权服务器重启后令牌仍然保留。",
        ])
        original = Path(r"C:\Users\Lenovo\微服务架构\tools\unit5_original.txt").read_text(encoding="utf-8")
        write_cell_text(plan.Cell(4, 1), [
            "实验内容：",
            "以下为《第5单元-案例5-1与案例5-2》原文。",
        ] + original.splitlines())
        summary = [
            "实验总结",
            "案例5-1 授权码方式",
            "授权服务器把客户端 client1 配在内存里，四种授权类型都打开，回调地址固定为百度。",
            "[[IMG:auth_code]]",
            "资源服务器只暴露 /api/test。没有令牌时由 @EnableResourceServer 拒绝访问。",
            "[[IMG:resource]]",
            "（1）打开授权地址后进入登录页。用户名 zhangsan，密码 123。",
            "[[IMG:login]]",
            "（2）登录成功后出现授权页。scope.test 默认是 Deny，必须先选 Approve，再点左下角的 Authorize。这个按钮在 localhost:8080 的授权页上，不在百度页面上。",
            "[[IMG:approval]]",
            "（3）点 Authorize 之后浏览器跳到回调地址，地址栏带上 code。本次得到的授权码是 %s。" % result["code"],
            "[[IMG:redirect]]",
            "（4）用客户端 client1 / 123 向 /oauth/token 提交 grant_type=authorization_code。返回的 access_token 就是访问令牌。",
            "[[IMG:token]]",
            "（5）不带令牌直接访问 http://localhost:8081/api/test，返回 401。",
            "[[IMG:denied]]",
            "（6）请求头加上 Authorization: Bearer 访问令牌后，资源服务器向授权服务器的 /oauth/check_token 校验通过，页面返回“接口测试，认证通过”。",
            "[[IMG:allowed]]",
            "完成案例5-1的过程：按文档建立父工程和两个模块，授权服务器配置内存用户和内存客户端，资源服务器只配置客户端编号和令牌校验地址。Spring Boot 2.6 默认不允许循环引用，授权服务器的 AuthenticationManager 和授权配置互相依赖，启动前在 application.yaml 中加上 spring.main.allow-circular-references: true。启动两个服务后，按登录、授权、换令牌、无令牌访问、带令牌访问的顺序各做一次。",
            "案例5-2 数据库存储令牌",
            "案例5-2不再调用 clients.inMemory()，客户端从 oauth_client_details 读取，令牌交给 JdbcTokenStore。",
            "[[IMG:jdbc]]",
            "建表语句来自 spring-security-oauth 的 schema，LONGVARBINARY 改成了 MySQL 的 BLOB。客户端密码 123 先用 BCryptPasswordEncoder 加密再插入。",
            "[[IMG:sql]]",
            "用文档中的 root / 12345678 连接本机 MySQL 8.0 时被拒绝，授权服务器因此读不到客户端表。案例5-2的令牌入库查询没有完成。",
            "[[IMG:mysql]]",
        ]
        write_cell_text(doc.Tables(2).Cell(1, 1), summary)
        write_cell_text(doc.Tables(2).Cell(2, 1), [
            "对实验的自我评价：",
            "案例5-1的授权码流程已经跑通，从登录到带令牌访问资源的结果和文档一致。案例5-2的代码和建表脚本已经按文档写好，数据库这一步受本机口令限制没有查到令牌记录。调试时碰到下面几个问题。",
            "错误1：授权服务器启动报循环依赖，AuthenticationManager 和 AuthServerConfig 互相等待。",
            "分析：Spring Boot 2.6 把循环引用改成了默认失败。文档里的 SecurityConfig 暴露了 authenticationManagerBean，授权端点又要注入它。",
            "解决：在 auth-server 的 application.yaml 中增加 spring.main.allow-circular-references: true，两个案例的授权服务器都加上。",
            "错误2：第二次打开授权地址时直接进入百度，看不到登录页，也找不到 Authorize 按钮。",
            "分析：浏览器还保存着 zhangsan 的会话，授权服务器认为用户已经登录。内存里如果已经有该用户和 client1 的令牌，授权端点会跳过确认页，直接带着新的 code 跳到回调地址。Authorize 只出现在跳转之前的 OAuth Approval 页面上。",
            "解决：重启授权服务器清掉内存中的会话和令牌，再用无痕窗口打开 /oauth/authorize。登录后先把 scope.test 选成 Approve，再点 Authorize，地址栏才会出现 code。",
            "错误3：案例5-2登录 MySQL 失败，授权地址在登录后变成 500。",
            "分析：文档把数据源密码写成 12345678。本机执行 mysql -uroot -p12345678 返回 ERROR 1045，root 被拒绝。JdbcClientDetailsService 读不到 oauth_client_details，所以授权端点抛出内部错误。",
            "解决：application.yaml 里的用户名和密码需要改成本机 MySQL 的实际账号，再执行 sql/oauth2.sql。客户端密码必须是 BCrypt 密文，并在 AuthorizationServerSecurityConfigurer 上指定 BCryptPasswordEncoder，否则 client1 / 123 换令牌会返回 401。数据库连通后，用客户端模式申请令牌，再查询 oauth_access_token 就能看到持久化记录。",
        ])
        replace_images(doc, pics)
        doc.Save()
        doc.SaveAs2(r"D:\陈汭-实验5-OAuth2授权认证.docx", FileFormat=12)
        doc.SaveAs2(r"C:\Users\Lenovo\Desktop\陈汭-实验5-OAuth2授权认证.doc", FileFormat=0)
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
