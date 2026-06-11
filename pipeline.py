from datetime import date
from config.settings import MAX_ARTICLES_PER_SOURCE
from scrapers import kr36, huxiu
from ai.summarizer import summarize
from feishu.bitable import save_articles
from feishu.messenger import send_daily_summary
from analysis.analyzer import analyze
from analysis.report import send_analysis_card


def run():
    today = date.today().strftime("%Y-%m-%d")
    print(f"[pipeline] 开始执行，日期：{today}")

    # 1. 抓取
    articles = []
    for fetcher, name in [(kr36.fetch, "36氪"), (huxiu.fetch, "虎嗅")]:
        try:
            batch = fetcher(max_articles=MAX_ARTICLES_PER_SOURCE)
            print(f"[pipeline] {name} 抓取 {len(batch)} 条")
            articles.extend(batch)
        except Exception as e:
            print(f"[pipeline] {name} 抓取失败: {e}")

    if not articles:
        print("[pipeline] 无数据，退出")
        return

    # 2. AI 摘要 + 分类
    print(f"[pipeline] 开始生成摘要，共 {len(articles)} 条...")
    articles = summarize(articles)

    # 3. 写入多维表格
    saved = save_articles(articles)
    print(f"[pipeline] 写入多维表格 {saved}/{len(articles)} 条")

    # 4. 发送每日资讯卡片
    send_daily_summary(articles, today)

    # 5. 从多维表格读取数据 → 分析 → 发送分析报告
    print("[pipeline] 开始分析...")
    result = analyze(today)
    send_analysis_card(result)

    print("[pipeline] 完成")


if __name__ == "__main__":
    run()
