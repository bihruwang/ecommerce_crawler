import json
import re
import urllib.request as req

from crawler.crawler_momo import HEADERS

DETAIL_URL = "https://www.momoshop.com.tw/product/{}"

PUSH = re.compile(r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\s*\]\)', re.S)
CHUNK = re.compile(r"([0-9a-f]{1,4}):T([0-9a-f]+),")

def fetch_flight(goods_code: str) -> str:
    """抓商品頁，把切成好幾十段的資料拼回一整串"""
    url = DETAIL_URL.format(goods_code)
    html = req.urlopen(req.Request(url, headers=HEADERS)).read().decode("utf-8")
    return "".join(json.loads(m.group(1)) for m in PUSH.finditer(html))


def build_chunks(flight: str) -> dict:
    chunks = {}
    pos = 0
    while True:
        m = CHUNK.search(flight, pos)
        if not m:
            break

        nbytes = int(m.group(2), 16)          # 標籤說的是「位元組」數
        start = m.end()

        # 先轉成位元組、切出這一包、再轉回文字
        raw = flight[start:].encode("utf-8")[:nbytes]
        text = raw.decode("utf-8", errors="ignore")

        chunks[m.group(1)] = text
        pos = start + len(text)               # 用實際字數往前推進
    return chunks


def extract_object(flight: str, key: str):
    """從一大串文字裡，挖出 "key":{...} 這個完整物件"""
    idx = flight.find(f'"{key}":')
    if idx < 0:
        return None

    start = flight.index("{", idx)
    depth, in_str, esc = 0, False, False

    for i in range(start, len(flight)):
        c = flight[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(flight[start : i + 1])
    return None


if __name__ == "__main__":
    flight = fetch_flight("11703779")
    chunks = build_chunks(flight)
    data = extract_object(flight, "goodsDetailData")

    print("拼回來的長度:", len(flight))
    print("文字區塊:", list(chunks.keys()))
    print("\n===== goodsDetailData 有這些欄位 =====")
    for k in data:
        print(" ", k)

    print("\n===== normDescription =====")
    for item in data["normDescription"]:
        for k, v in item.items():
            text = str(v)
            # 遇到 $1a 這種代號就換成實際內容
            if text.startswith("$") and text[1:] in chunks:
                text = chunks[text[1:]]
            print(f"[{k}] {text[:300]}")
            print()