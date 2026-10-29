# -*- coding: utf-8 -*-
"""Drive the Sentinel lab: register resources, push rules, record results."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

OUT = Path(r"C:\Users\Lenovo\微服务架构\第7单元-Sentinel服务熔断与限流\screenshots")
OUT.mkdir(parents=True, exist_ok=True)
RESULT = Path(r"C:\Users\Lenovo\微服务架构\tools\unit7_results.json")
BASE = "http://localhost:8089"
DASH = "http://localhost:8080"


def hit(url):
    started = time.time()
    try:
        response = requests.get(url, timeout=8)
        return {
            "url": url,
            "status": response.status_code,
            "body": response.text[:300],
            "ms": int((time.time() - started) * 1000),
        }
    except Exception as exc:
        return {"url": url, "status": 0, "body": str(exc), "ms": int((time.time() - started) * 1000)}


def burst(url, count, workers=20):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda u: hit(u), [url] * count))


def summarize(rows):
    passed, blocked, other = [], [], []
    for row in rows:
        body = row["body"]
        if row["status"] == 200 and "Blocked" not in body and "exception" not in body.lower():
            passed.append(row)
        elif "Blocked" in body or row["status"] == 429:
            blocked.append(row)
        else:
            other.append(row)
    sample = {
        "pass": passed[0]["body"] if passed else "",
        "block": blocked[0]["body"] if blocked else "",
        "other": other[0]["body"] if other else "",
    }
    return {
        "total": len(rows),
        "pass": len(passed),
        "blocked": len(blocked),
        "other": len(other),
        "sample": sample,
    }


def main():
    data = {}
    warmup_urls = [
        BASE + "/",
        BASE + "/hello?name=test",
        BASE + "/hotpoint?type=a&name=rose",
        BASE + "/hotpoint?type=b&name=lily",
        BASE + "/test-sys-qps1",
        BASE + "/test-sys-qps2",
        BASE + "/test-sys-qps3",
        BASE + "/hi",
    ]
    data["warmup"] = [hit(url) for url in warmup_urls]
    time.sleep(3)

    session = requests.Session()
    login = session.post(
        DASH + "/auth/login",
        data={"username": "sentinel", "password": "sentinel"},
        timeout=10,
    )
    data["login"] = {"status": login.status_code, "body": login.text[:500]}
    apps = session.get(DASH + "/app/briefinfos.json", timeout=10)
    data["apps"] = apps.json()
    machines = session.get(DASH + "/app/service-sentinel/machines.json", timeout=10)
    data["machines"] = machines.json()
    machine_list = data["machines"].get("data") or []
    if not machine_list:
        raise SystemExit("service-sentinel is not registered in Sentinel Dashboard")
    machine = machine_list[0]
    ip, port = machine["ip"], machine["port"]
    data["machine"] = {"ip": ip, "port": port}
    resources = session.get(
        DASH + "/resource/machineResource.json",
        params={"ip": ip, "port": port, "type": "cluster"},
        timeout=10,
    )
    data["resources_before"] = resources.json()

    flow = session.post(
        DASH + "/v1/flow/rule",
        json={
            "app": "service-sentinel",
            "ip": ip,
            "port": port,
            "resource": "/hello",
            "limitApp": "default",
            "grade": 1,
            "count": 1,
            "strategy": 0,
            "controlBehavior": 0,
            "clusterMode": False,
        },
        timeout=10,
    )
    data["flow_add"] = flow.json()
    time.sleep(1)
    data["qps_burst"] = summarize(burst(BASE + "/hello?name=test", 20, 20))

    hot = session.post(
        DASH + "/paramFlow/rule",
        json={
            "app": "service-sentinel",
            "ip": ip,
            "port": port,
            "resource": "hotpoint",
            "grade": 1,
            "paramIdx": 0,
            "count": 10,
            "controlBehavior": 0,
            "durationInSec": 1,
            "burstCount": 0,
            "maxQueueingTimeMs": 0,
        },
        timeout=10,
    )
    data["hot_add"] = hot.json()
    time.sleep(1)
    data["hot_a"] = summarize(burst(BASE + "/hotpoint?type=a&name=rose", 30, 30))
    time.sleep(1.2)
    data["hot_b"] = summarize(burst(BASE + "/hotpoint?type=b&name=lily", 8, 8))

    system = session.get(
        DASH + "/system/new.json",
        params={
            "app": "service-sentinel",
            "ip": ip,
            "port": port,
            "highestSystemLoad": -1,
            "highestCpuUsage": -1,
            "avgRt": 100,
            "maxThread": -1,
            "qps": 5,
        },
        timeout=10,
    )
    data["system_add"] = system.json()
    time.sleep(1)
    data["system_burst"] = summarize(burst(BASE + "/hi", 50, 10))

    now = int(time.time() * 1000)
    metric = session.get(
        DASH + "/metric/queryTopResourceMetric.json",
        params={
            "app": "service-sentinel",
            "pageIndex": 1,
            "pageSize": 20,
            "desc": True,
            "startTime": now - 60_000,
            "endTime": now,
            "searchKey": "",
        },
        timeout=10,
    )
    data["metric"] = metric.json()
    rules = session.get(
        DASH + "/v1/flow/rules",
        params={"app": "service-sentinel", "ip": ip, "port": port},
        timeout=10,
    )
    data["flow_rules"] = rules.json()
    RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "login": data["login"]["status"],
        "apps": [item.get("app") for item in (data["apps"].get("data") or [])],
        "machine": data["machine"],
        "resources": [item.get("resource") for item in (data["resources_before"].get("data") or [])],
        "flow_add": data["flow_add"].get("success"),
        "qps": data["qps_burst"],
        "hot_add": data["hot_add"].get("success"),
        "hot_a": data["hot_a"],
        "hot_b": data["hot_b"],
        "system_add": data["system_add"].get("success"),
        "system": data["system_burst"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
