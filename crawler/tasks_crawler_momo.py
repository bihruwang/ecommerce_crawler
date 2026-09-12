import os

from crawler.crawler_momo import crawler_momo as fetch_momo
from crawler.worker import app

SAVE_DIR = "data"


@app.task()
def crawler_momo_print(category_name: str):
    df = fetch_momo(category_name)
    print(df.head())

    os.makedirs(SAVE_DIR, exist_ok=True)
    today = df["抓取日期"].iloc[0]
    path = os.path.join(SAVE_DIR, f"{today}_{category_name}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print("已存檔:", path)

    return len(df)