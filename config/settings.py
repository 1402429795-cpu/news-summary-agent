import os

# 飞书配置（通过环境变量传入，不要硬编码密钥）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_aaa0886f06b89cd8")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_BASE_TOKEN = os.getenv("FEISHU_BASE_TOKEN", "Ry9NbpQtfaDzgBso0MecLxzIn6d")
FEISHU_TABLE_ID = os.getenv("FEISHU_TABLE_ID", "tblkmixN7c6X2qIf")
FEISHU_CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_ab8b6e880efe7a4c468396cd48535fd4")

# 抓取配置
MAX_ARTICLES_PER_SOURCE = 10
