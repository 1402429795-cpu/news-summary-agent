import schedule
import time
from pipeline import run

# 每天早上 8:30 执行
schedule.every().day.at("08:30").do(run)

if __name__ == "__main__":
    print("[scheduler] 启动，每天 08:30 执行资讯抓取...")
    run()  # 启动时立即执行一次
    while True:
        schedule.run_pending()
        time.sleep(60)
