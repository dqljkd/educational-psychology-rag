# RAG Knowledge Base System

一个面向教育心理学与学校心理支持场景的可在线访问 RAG 系统，包含：
- 教育心理学专用 Web 界面
- FastAPI 接口
- 文档导入与向量索引
- 检索增强问答
- 完整架构与部署文档
- 评估标准与评测模板
- 原始资料结构化清洗脚本

## 目录结构
```text
RAG_Knowledge_Base_System/
├── app.py
├── backend/
│   ├── api.py
│   ├── config.py
│   ├── models.py
│   └── rag_service.py
├── data/
│   ├── documents/
│   ├── eval/
│   └── vector_store/
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── deployment.md
│   └── evaluation.md
├── requirements.txt
├── .env.example
└── README.md
```

## 功能
- 上传 `txt / md / pdf` 文档
- 建立向量索引
- 支持语义检索
- 支持基于检索结果的答案生成
- 返回引用上下文
- 提供 API 与 Streamlit 页面两种访问方式

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
```

将 `.env` 中的模型配置改为你自己的服务：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

如果你使用兼容 OpenAI API 的模型服务，也可以只替换 `OPENAI_BASE_URL` 和模型名。

### 3. 清洗并结构化原始知识库
```bash
python scripts/prepare_educational_psychology_kb.py \
  --structured-txt '/Users/niuwenjie/Desktop/教育心理学_学校心理支持_RAG知识库升级包_txt分块版.txt' \
  --pdf '/Users/niuwenjie/Downloads/1389703959379.pdf' \
  --pdf '/Users/niuwenjie/Downloads/094197-01.pdf'
```

清洗结果会写入：
- `data/raw_sources/`
- `data/processed/`
- `data/reports/cleaning_report.md`

### 4. 启动 Web 页面
```bash
streamlit run app.py
```

### 5. 启动 API 服务
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

## 核心流程
1. 清洗原始教育心理学资料为结构化 `jsonl`
2. 将结构化知识与原始文档导入系统
3. 向量化并写入 `data/vector_store/`
4. 查询时先召回 Top-K 片段
5. 将片段与问题一起交给 LLM 生成答案
6. 返回答案和引用证据，并对高风险问题给出转介提醒

## 评估与验收
完整评估标准见：
- [docs/evaluation.md](/Users/niuwenjie/Library/Mobile%20Documents/com~apple~CloudDocs/python%E2%80%94nwj/RAG_Knowledge_Base_System/docs/evaluation.md)
- [docs/domain_knowledge.md](/Users/niuwenjie/Library/Mobile%20Documents/com~apple~CloudDocs/python%E2%80%94nwj/RAG_Knowledge_Base_System/docs/domain_knowledge.md)
- [docs/system_documentation.md](/Users/niuwenjie/Library/Mobile%20Documents/com~apple~CloudDocs/python%E2%80%94nwj/RAG_Knowledge_Base_System/docs/system_documentation.md)
- [docs/evaluation_report.md](/Users/niuwenjie/Library/Mobile%20Documents/com~apple~CloudDocs/python%E2%80%94nwj/RAG_Knowledge_Base_System/docs/evaluation_report.md)

## 在线部署建议

如果你希望给老师直接在线查看，推荐优先使用：
- Streamlit Community Cloud

原因：
- 和当前项目技术栈完全匹配
- 不需要自己维护服务器
- 支持 Secrets 配置 OpenAI Key
- 本项目已经支持启动时自动从 `data/processed/` 初始化知识库

详细步骤见：
- [docs/deployment.md](/Users/niuwenjie/Library/Mobile%20Documents/com~apple~CloudDocs/python%E2%80%94nwj/RAG_Knowledge_Base_System/docs/deployment.md)

建议至少覆盖：
- 检索准确率
- 上下文覆盖率
- 答案忠实度
- 引用准确率
- 响应时延
- 失败率

## 推荐的下一步
- 接入真实业务文档
- 增加用户鉴权
- 增加重排器和多路召回
- 加入离线评测脚本
- 增加反馈闭环与人工标注集
