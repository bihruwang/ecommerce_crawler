import json
import re
import urllib.request as req

GOODS_CODE = "11703779"

url = f"https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code={GOODS_CODE}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
}

html = req.urlopen(req.Request(url, headers=headers)).read().decode("utf-8")

block = re.search(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
).group(1)
data = json.loads(block)
graph = data["@graph"]

product = next(i for i in graph if i.get("@type") in ("ProductGroup", "Product"))
props = product.get("additionalProperty", [])

print(f"===== 共 {len(props)} 個規格欄位 =====")
for p in props:
    print(f"{p['name']} = {p['value']}")

print("\n===== 商品其他欄位 =====")
for key, value in product.items():
    if key != "additionalProperty":
        print(f"{key} = {str(value)[:100]}")

print("\n===== 分類路徑 =====")
crumb = next(i for i in graph if i.get("@type") == "BreadcrumbList")
print(" > ".join(x["name"] for x in crumb["itemListElement"]))

# 完整資料存成檔案，避免畫面截斷
with open("detail_sample.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("\n完整內容已存到 detail_sample.json")