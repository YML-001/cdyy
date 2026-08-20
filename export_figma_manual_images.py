#!/usr/bin/env python3
"""从 Figma 设计稿导出操作手册配图，替换 manual-screenshots 下的原型截图。"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

FILE_KEY = "b8gXB6N0or3WPKD3NwxtO3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "manual-screenshots")

# 手册图片文件名 -> Figma 节点 ID
MAPPING = {
    # 管理后台
    "admin-01-dashboard.png": "1:14113",
    "admin-02-venue-list.png": "1:13095",
    "admin-04-venue-detail.png": "1:17973",
    "admin-05-venue-add-basic.png": "1:15219",
    "admin-06-timeslot.png": "1:15285",
    "admin-07-form.png": "1:15339",
    "admin-08-approval.png": "1:15643",
    "admin-09-permission.png": "1:15793",
    "admin-17-template-list.png": "1:13787",
    "admin-20-booking-list.png": "1:14813",
    # 预约端 PC
    "user-pc-01-list.png": "1:22003",
    "user-pc-02-detail.png": "1:21876",
    "user-pc-04-form.png": "1:20583",
    "user-pc-07-slot-hour.png": "1:24629",
    "user-pc-07-slot-90min.png": "1:23586",
    "user-pc-07-slot-2hour.png": "1:23350",
    "user-pc-07-slot-mixed.png": "1:24911",
    "user-pc-08-slot-period.png": "1:24339",
    "user-pc-07-slot-halfday.png": "1:24074",
    "user-pc-07-slot-free.png": "1:23828",
    "user-pc-09-confirm.png": "1:21384",
    "user-pc-09-agreement.png": "1:20692",
    "user-pc-10-success.png": "1:21597",
    "user-pc-11-mybookings.png": "1:23125",
    # 预约端移动（设计稿暂无独立移动端，复用对应业务帧）
    "user-mb-01-list.png": "1:22003",
    "user-mb-02-detail.png": "1:21876",
    "user-mb-04-form.png": "1:20583",
    "user-mb-06-slot.png": "1:24629",
    "user-mb-06-slot-90min.png": "1:23586",
    "user-mb-06-slot-2hour.png": "1:23350",
    "user-mb-06-slot-mixed.png": "1:24911",
    "user-mb-06-slot-period.png": "1:24339",
    "user-mb-06-slot-halfday.png": "1:24074",
    "user-mb-06-slot-free.png": "1:23828",
    "user-mb-07-confirm.png": "1:21384",
    # 审批端
    "approval-pc-01-list.png": "1:14813",
    "approval-pc-02-detail.png": "1:21743",
    "approval-mb-01-list.png": "1:14813",
    "approval-mb-02-detail.png": "1:21645",
}


def api_get(url, token):
    req = urllib.request.Request(url, headers={"X-Figma-Token": token})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url, path):
    with urllib.request.urlopen(url, timeout=120) as resp:
        data = resp.read()
    with open(path, "wb") as f:
        f.write(data)


def export_images(token, scale=1):
    os.makedirs(OUT_DIR, exist_ok=True)
    unique_ids = sorted(set(MAPPING.values()))
    id_to_urls = {}

    for idx, node_id in enumerate(unique_ids, 1):
        ids_param = urllib.parse.quote(node_id, safe="")
        url = (
            f"https://api.figma.com/v1/images/{FILE_KEY}"
            f"?ids={ids_param}&format=png&scale={scale}"
        )
        for attempt in range(3):
            try:
                data = api_get(url, token)
                if data.get("err"):
                    raise RuntimeError(data["err"])
                id_to_urls.update(data.get("images", {}))
                print(f"导出节点 {idx}/{len(unique_ids)}: {node_id}")
                break
            except Exception as exc:
                if attempt == 2:
                    print(f"WARN 节点导出失败 {node_id}: {exc}")
                else:
                    time.sleep(2)
        time.sleep(1)

    ok, fail = 0, 0
    for filename, node_id in MAPPING.items():
        img_url = id_to_urls.get(node_id)
        out_path = os.path.join(OUT_DIR, filename)
        if not img_url:
            print(f"FAIL 无导出URL: {filename} ({node_id})")
            fail += 1
            continue
        try:
            download(img_url, out_path)
            size_kb = os.path.getsize(out_path) // 1024
            print(f"OK   {filename} <- {node_id} ({size_kb} KB)")
            ok += 1
        except Exception as exc:
            print(f"FAIL {filename}: {exc}")
            fail += 1

    print(f"\n完成: 成功 {ok}, 失败 {fail}, 输出目录 {OUT_DIR}")
    return fail == 0


if __name__ == "__main__":
    token = os.environ.get("FIGMA_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not token:
        print("请设置环境变量 FIGMA_TOKEN 或传入 token 参数", file=sys.stderr)
        sys.exit(1)
    success = export_images(token)
    sys.exit(0 if success else 1)
