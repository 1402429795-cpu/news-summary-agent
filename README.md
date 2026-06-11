# news-summary-agent

每日科技资讯自动摘要工具。定时抓取科技资讯网站内容，通过 AI 生成摘要，存入飞书多维表格，并推送每日汇总消息到飞书群。

## 功能特性

- 每天自动抓取科技资讯（基于 RSS 源）
- 使用 DeepSeek AI 提炼文章摘要和关键词
- 将结果存入飞书多维表格（Bitable）
- 在飞书群发送每日资讯汇总消息

## 技术架构

```
news-summary-agent/
├── config/
│   └── settings.py       # 配置：飞书参数、抓取目标
├── scrapers/
│   ├── base.py           # Article 数据类
│   ├── kr36.py           # 资讯源 1（IT之家 RSS）
│   └── huxiu.py          # 资讯源 2（IT之家 RSS 第二批）
├── ai/
│   └── summarizer.py     # DeepSeek API 生成摘要 + 关键词
├── feishu/
│   ├── bitable.py        # 写入飞书多维表格
│   └── messenger.py      # 发送飞书群消息
├── pipeline.py           # 主流程：抓取 → 摘要 → 存储 → 推送
├── scheduler.py          # 定时任务（每天 08:30 触发）
└── requirements.txt
```

### 数据流

```
定时触发（08:30）
    ↓
scrapers/ 通过 RSS 抓取最新科技资讯
    ↓
ai/summarizer 调用 DeepSeek API 逐条生成摘要 + 关键词
    ↓
feishu/bitable 写入多维表格（标题/来源/链接/摘要/关键词/日期）
    ↓
feishu/messenger 汇总当日内容，发送飞书群消息
```

### 技术选型

| 模块 | 技术 |
|------|------|
| 资讯抓取 | `feedparser`（RSS 解析） |
| AI 摘要 | DeepSeek API（`openai` SDK 兼容调用） |
| 飞书集成 | `lark-cli`（飞书开放平台 CLI 工具） |
| 定时调度 | `schedule` 库 |

## 环境要求

- Python 3.10+
- Node.js（用于 lark-cli）
- lark-cli v1.0+

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
npm install -g @larksuite/cli
```

### 2. 配置飞书 CLI

```bash
echo "YOUR_APP_SECRET" | lark-cli config init \
  --app-id YOUR_APP_ID \
  --app-secret-stdin \
  --brand feishu
```

### 3. 设置环境变量

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

### 4. 运行

**单次执行：**
```bash
python pipeline.py
```

**启动定时任务（每天 08:30 自动执行）：**
```bash
python scheduler.py
```

## 飞书多维表格字段

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 文本 | 文章原标题 |
| 来源 | 单选 | 36氪 / 虎嗅 |
| 原文链接 | 文本 | 文章 URL |
| 摘要 | 文本 | AI 生成的 2-3 句摘要 |
| 关键词 | 文本 | AI 提取的关键词，以 " / " 分隔 |
| 抓取日期 | 日期时间 | 入库时间 |

## 开发过程中遇到的问题与解决方案

### 1. 目标站点 DNS 被污染

**问题：** 36氪（36kr.com）和虎嗅（huxiu.com）的 DNS 被当前网络解析到保留地址段（198.18.0.x），导致 TLS 握手失败，连 `verify=False` 也无法绕过。

**解决方案：** 改用网络可访问的 IT之家 RSS 源（`https://www.ithome.com/rss/`），通过 `feedparser` 解析 RSS，比直接爬 HTML 更稳定、更轻量。

### 2. 飞书权限需逐条申请

**问题：** 飞书开放平台的 API 权限粒度极细（`base:app:create`、`base:table:create`、`base:table:read` 等独立权限），每次调用 API 才能发现缺少哪个权限，导致反复报错。

**解决方案：** 在飞书开放平台权限管理页面搜索关键词 `bitable`、`base`、`im:message`，将搜索结果全部勾选后统一发布版本，一次性解决权限问题。

### 3. lark-cli 批量写入参数格式

**问题：** `+record-batch-create` 命令的数据格式与预期不同，不接受 `--records` 参数，而是用 `--json` 传入 `{"fields": [...], "rows": [[...]]}` 的列表格式。

**解决方案：** 阅读 `lark-cli base +record-batch-create --help` 输出，按实际格式重写写入逻辑，并将 `关键词` 字段从单选改为文本类型以支持动态写入。

### 4. bot 身份创建的飞书资源用户不可见

**问题：** 用 bot 身份调用 API 创建的多维表格，飞书用户账号默认没有访问权限。

**解决方案：** 通过飞书开放平台返回的直链（`base_token` 对应的 URL）直接访问表格，或在飞书中手动将用户添加为表格管理员。

### 5. 飞书机器人无法主动发消息

**问题：** 应用未开启「机器人」能力，飞书客户端中无法找到对话入口。

**解决方案：** 在飞书开放平台 → 应用能力 → 添加「机器人」，发布新版本后，在飞书中创建群组并将机器人拉入群，通过群 `chat_id` 发送消息。

## 配置说明

主要配置项位于 `config/settings.py`：

| 配置项 | 说明 |
|--------|------|
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret |
| `FEISHU_BASE_TOKEN` | 多维表格 token |
| `FEISHU_TABLE_ID` | 数据表 ID |
| `FEISHU_CHAT_ID` | 目标群 chat_id |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（环境变量） |
| `MAX_ARTICLES_PER_SOURCE` | 每个来源每日最多抓取条数（默认 10） |
