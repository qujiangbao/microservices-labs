# -*- coding: utf-8 -*-
"""Save upload screenshots for case 5-1 and case 5-2 step pages."""
import re
import shutil
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\Users\Lenovo\微服务架构\第5单元-OAuth2授权认证")
OUT1 = Path(r"C:\Users\Lenovo\Desktop\案例5-1截图")
OUT2 = Path(r"C:\Users\Lenovo\Desktop\案例5-2截图")
OUT1.mkdir(parents=True, exist_ok=True)
OUT2.mkdir(parents=True, exist_ok=True)
FONT = r"C:\Windows\Fonts\msyh.ttc"


def font(size):
    return ImageFont.truetype(FONT, size)


def wrap(text, draw, fnt, max_w):
    lines, cur = [], ""
    for ch in text or "":
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


def code_image(title, text, path):
    fnt = font(16)
    title_fnt = font(18)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    width = 1100
    lines = []
    for line in text.splitlines():
        lines.extend(wrap(line, dummy, fnt, width - 80))
    line_h = 24
    header = 46
    height = header + 20 + line_h * len(lines) + 16
    img = Image.new("RGB", (width, height), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, header), fill="#2d2d30")
    draw.text((16, 12), title, font=title_fnt, fill="#ffffff")
    y = header + 12
    for i, line in enumerate(lines, 1):
        draw.text((10, y), f"{i:3}", font=fnt, fill="#858585")
        draw.text((58, y), line, font=fnt, fill="#d4d4d4")
        y += line_h
    img.save(path, quality=92)
    print("saved", path.name)


def browser_image(title, url, body, path):
    ui = font(16)
    title_fnt = font(18)
    body_fnt = font(20)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    width = 1100
    lines = []
    for line in body.splitlines() or [""]:
        lines.extend(wrap(line, dummy, body_fnt, width - 48))
    line_h = 30
    top = 44
    bar = 78
    height = top + bar + 20 + line_h * max(len(lines), 1) + 24
    img = Image.new("RGB", (width, height), "#f3f3f3")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, top), fill="#1a73e8")
    draw.text((16, 10), title, font=title_fnt, fill="#ffffff")
    draw.rounded_rectangle((12, top + 10, width - 12, top + 42), radius=16, fill="#ffffff", outline="#dadce0")
    url_lines = wrap(url, dummy, ui, width - 56)
    draw.text((24, top + 16), url_lines[0], font=ui, fill="#202124")
    y = top + bar
    for line in lines:
        draw.text((24, y), line, font=body_fnt, fill="#111111")
        y += line_h
    img.save(path, quality=92)
    print("saved", path.name)


def csrf(html):
    match = re.search(r'name="_csrf"[^>]*value="([^"]+)"', html)
    if not match:
        match = re.search(r'value="([^"]+)"[^>]*name="_csrf"', html)
    return match.group(1) if match else None


def code_from_location(location):
    if not location or "code=" not in location:
        return None
    return location.split("code=")[-1].split("&")[0]


def authorization_code():
    session = requests.Session()
    session.headers["Accept"] = "text/html,application/xhtml+xml"
    page = session.get(
        "http://localhost:8080/oauth/authorize",
        params={"client_id": "client1", "response_type": "code", "redirect_uri": "http://www.baidu.com"},
        allow_redirects=False,
        timeout=15,
    )
    location = page.headers.get("Location", "")
    code = code_from_location(location)
    if code:
        return code, location
    if page.status_code in (301, 302) and "login" in location:
        page = session.get("http://localhost:8080" + location if location.startswith("/") else location, timeout=15)
    token = csrf(page.text)
    if token and ("sign in" in page.text.lower() or "username" in page.text.lower()):
        page = session.post(
            "http://localhost:8080/login",
            data={"username": "zhangsan", "password": "123", "_csrf": token},
            allow_redirects=False,
            timeout=15,
        )
        hop = page.headers.get("Location", "")
        if hop:
            page = session.get("http://localhost:8080" + hop if hop.startswith("/") else hop, allow_redirects=False, timeout=15)
            code = code_from_location(page.headers.get("Location", ""))
            if code:
                return code, page.headers["Location"]
            if page.status_code == 200:
                page = session.get(page.url if page.url else "http://localhost:8080" + hop, timeout=15)
    if "OAuth Approval" in page.text or 'name="authorize"' in page.text:
        approval = csrf(page.text)
        jumped = session.post(
            "http://localhost:8080/oauth/authorize",
            data={"user_oauth_approval": "true", "scope.test": "true", "authorize": "Authorize", "_csrf": approval},
            allow_redirects=False,
            timeout=15,
        )
        location = jumped.headers.get("Location", "")
        code = code_from_location(location)
        if code:
            return code, location
    raise RuntimeError("no code status=%s url=%s body=%s" % (page.status_code, getattr(page, "url", ""), page.text[:180]))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def case1():
    code, location = authorization_code()
    print("CODE", code, location)
    token_resp = requests.post(
        "http://localhost:8080/oauth/token",
        params={"code": code, "grant_type": "authorization_code", "redirect_uri": "http://www.baidu.com"},
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
    allowed_text = allowed.content.decode("utf-8")
    print("TOKEN", token_resp.status_code, token_resp.text)
    print("API", denied.status_code, allowed.status_code, allowed_text)

    code_image(
        "案例5-1 步骤：授权服务器（内存客户端 client1，回调百度）",
        read(r"案例5-1-oauth2\auth-server\src\main\java\cn\js\ccit\auth\AuthServerConfig.java")
        + "\n\napplication.yaml\n"
        + read(r"案例5-1-oauth2\auth-server\src\main\resources\application.yaml"),
        OUT1 / "01-步骤-授权服务器.png",
    )
    code_image(
        "案例5-1 步骤：登录用户 zhangsan / 123",
        read(r"案例5-1-oauth2\auth-server\src\main\java\cn\js\ccit\auth\SecurityConfig.java"),
        OUT1 / "02-步骤-用户配置.png",
    )
    code_image(
        "案例5-1 步骤：资源服务器 /api/test",
        read(r"案例5-1-oauth2\resource-server\src\main\java\cn\js\ccit\resource\ResourceServerApplication.java")
        + "\n\napplication.yaml\n"
        + read(r"案例5-1-oauth2\resource-server\src\main\resources\application.yaml"),
        OUT1 / "03-步骤-资源服务器.png",
    )
    login = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots\case51-login.png")
    approval = Path(r"C:\Users\Lenovo\AppData\Local\Temp\cursor\screenshots\oauth-authorize-button.png")
    if login.exists():
        shutil.copyfile(login, OUT1 / "04-验证-登录页面.png")
    if approval.exists():
        shutil.copyfile(approval, OUT1 / "05-验证-Authorize授权页.png")
    browser_image(
        "案例5-1 验证：授权后地址栏出现 code",
        location,
        "预期：跳转到 http://www.baidu.com ，地址栏参数 code 即为授权码。\n本次授权码：" + code,
        OUT1 / "06-验证-获取授权码.png",
    )
    browser_image(
        "案例5-1 验证：授权码换取访问令牌",
        "POST http://localhost:8080/oauth/token?grant_type=authorization_code&code=" + code,
        "Basic Auth：client1 / 123\nHTTP " + str(token_resp.status_code) + "\n" + token_resp.text,
        OUT1 / "07-验证-换取令牌.png",
    )
    browser_image(
        "案例5-1 验证：不带令牌访问资源",
        "http://localhost:8081/api/test",
        "预期：401，没有令牌不能访问。\nHTTP " + str(denied.status_code) + "\n" + denied.text,
        OUT1 / "08-验证-无令牌401.png",
    )
    browser_image(
        "案例5-1 验证：携带令牌访问资源",
        "http://localhost:8081/api/test",
        "请求头 Authorization: Bearer " + access + "\n预期：接口测试，认证通过\nHTTP "
        + str(allowed.status_code) + "\n" + allowed_text,
        OUT1 / "09-验证-带令牌认证通过.png",
    )
    (OUT1 / "本次结果.txt").write_text(
        "code=%s\nlocation=%s\ntoken=%s\napi=%s %s\n" % (code, location, token_resp.text, allowed.status_code, allowed_text),
        encoding="utf-8",
    )


def case2_steps():
    code_image(
        "案例5-2 步骤：JdbcTokenStore 与数据库客户端",
        read(r"案例5-2-oauth2-jdbc\auth-server\src\main\java\cn\js\ccit\auth\AuthServerConfig.java"),
        OUT2 / "01-步骤-数据库令牌配置.png",
    )
    code_image(
        "案例5-2 步骤：数据源 application.yaml",
        read(r"案例5-2-oauth2-jdbc\auth-server\src\main\resources\application.yaml"),
        OUT2 / "02-步骤-数据源配置.png",
    )
    sql = (ROOT / r"案例5-2-oauth2-jdbc\sql\oauth2.sql").read_text(encoding="utf-8")
    code_image("案例5-2 步骤：建库、建表并插入 client1", sql, OUT2 / "03-步骤-建表SQL.png")
    code_image(
        "案例5-2 步骤：资源服务器 /api/userinfo",
        read(r"案例5-2-oauth2-jdbc\resource-server\src\main\java\cn\js\ccit\resource\ResourceServerApplication.java"),
        OUT2 / "04-步骤-资源服务器.png",
    )


if __name__ == "__main__":
    case1()
    case2_steps()
