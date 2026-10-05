from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from crawler.crawler_momo import CATEGORIES
from crawler.tasks_crawler_momo import crawler_momo_print

# 一天發三次。因為 task 有防重，重複跑只會留一份，
# 所以某一次因為斷網或關機沒跑到，後面還有機會補上。
RUN_HOURS = (9, 13, 21)


def send_momo_tasks():
    logger.info("發送 momo 爬蟲任務")
    for category_name in CATEGORIES:
        crawler_momo_print.s(category_name).apply_async()
        logger.info(f"已發送：{category_name}")


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Taipei")

    for hour in RUN_HOURS:
        scheduler.add_job(
            send_momo_tasks,
            trigger=CronTrigger(hour=hour, minute=0),
            id=f"momo-{hour}",
            name=f"momo 每日爬蟲 {hour}:00",
        )

    logger.info(f"排程啟動，每天 {RUN_HOURS} 點各發送一次")
    scheduler.start()
