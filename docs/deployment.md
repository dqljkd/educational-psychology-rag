# 部署说明

## 推荐部署方案

如果你的目标是“让老师可以直接在线打开、体验和检查项目”，推荐优先使用：

### 方案 A：Streamlit Community Cloud
- 最适合课程作业、演示和老师评审
- 部署流程简单
- 不需要自己配服务器
- 只要连接 GitHub 仓库并填写 Secrets 即可

如果你后续需要更灵活的公网服务，再考虑 Docker + Render / Railway / 云服务器。

## 本地部署

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
```

### 3. 启动 Streamlit
```bash
streamlit run app.py
```

### 4. 启动 FastAPI
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

## 云端部署建议

### 方案 A：Streamlit Community Cloud
- 将项目推送到 GitHub
- 选择 `RAG_Knowledge_Base_System/app.py` 作为入口
- 在 Streamlit Cloud 后台配置 Secrets
- 系统启动时会自动检查 `data/processed/` 中的结构化知识文件，并在索引为空时自动导入

推荐配置的 Secrets：

```toml
OPENAI_API_KEY="your_api_key"
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_CHAT_MODEL="gpt-4o-mini"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
RAG_COLLECTION_NAME="knowledge_base"
RAG_CHUNK_SIZE="800"
RAG_CHUNK_OVERLAP="120"
RAG_TOP_K="4"
```

适合：
- 课程项目展示
- 老师在线评审
- 轻量演示

### 方案 B：单机部署
- Nginx
- Streamlit
- FastAPI
- Chroma 本地持久化

适合 PoC、小团队、内部知识库。

### 方案 C：容器化部署
- Docker 打包前端与后端
- 向量库存储挂载持久卷
- 环境变量通过 Secret 管理

适合测试环境与轻量生产环境。

### 方案 D：生产增强版
- 独立前端
- 独立 API 服务
- 独立向量库服务
- 鉴权与审计
- 日志监控
- 异常告警

适合企业内网或多部门共享场景。

## Streamlit Community Cloud 部署步骤

### 1. 推送代码到 GitHub
建议将整个 `RAG_Knowledge_Base_System` 目录作为仓库根目录，或者作为主仓库中的一个子目录进行管理。

### 2. 登录 Streamlit Community Cloud
打开 Streamlit Community Cloud，选择：
- New app
- 绑定你的 GitHub 仓库
- Main file path 填写 `app.py`

如果项目不是仓库根目录，而是在子目录中，则选择对应子目录。

### 3. 配置 Secrets
在 App 设置中添加前述 OpenAI 相关环境变量。

### 4. 部署并验证
首次部署后，系统会：
- 读取 `data/processed/*.jsonl`
- 若当前索引为空，则自动建立向量索引
- 启动教育心理学问答页面

### 5. 交付给老师
建议把以下内容一起提供给老师：
- 公网访问链接
- GitHub 仓库地址
- `docs/system_documentation.md`
- `docs/evaluation_report.md`
- 一页简短演示说明

## Docker 部署

项目已提供：
- `Dockerfile`
- `.dockerignore`

本地构建命令：

```bash
docker build -t educational-psych-rag .
docker run -p 8501:8501 --env-file .env educational-psych-rag
```

如果部署到 Render、Railway 或云服务器，可以直接基于该 Dockerfile 上线。

## 生产环境注意事项
- API Key 不要写入代码
- 向量库存储要持久化
- 上传文件要限制类型与大小
- 对外服务需要鉴权
- 建议增加请求日志和响应延迟监控
- 建议记录召回片段与最终答案用于审计
