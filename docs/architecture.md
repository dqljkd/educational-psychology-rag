# 架构说明

## 目标
构建一个可在线访问的 RAG 知识库系统，用于：
- 导入企业或项目知识文档
- 基于语义检索召回相关内容
- 使用大模型在证据约束下回答问题
- 输出可追溯引用

## 系统组成

### 1. Web 层
- `app.py`
- 基于 Streamlit 提供在线访问页面
- 用于文档上传、索引构建、语义检索、问答与结果展示

### 2. API 层
- `backend/api.py`
- 基于 FastAPI 提供标准接口
- 方便后续接入前端、内部系统或第三方平台

### 3. RAG 服务层
- `backend/rag_service.py`
- 负责文档解析、切片、向量化、召回和答案生成

### 4. 存储层
- `data/documents/`
  原始文档存储
- `data/vector_store/`
  Chroma 持久化向量索引
- `data/eval/`
  评测集与评估模板

## 处理流程
1. 上传文档
2. 解析文本
3. 按固定规则切片
4. 生成 embedding
5. 写入向量数据库
6. 用户提问
7. 检索 Top-K 片段
8. 拼接上下文
9. 生成带引用答案

## 当前设计选择
- 向量库：Chroma
- LLM 接口：OpenAI Compatible API
- 前端：Streamlit
- API：FastAPI

## 后续可扩展方向
- 多知识库隔离
- 用户权限控制
- 文档版本管理
- OCR 与表格解析
- Reranker
- 多跳检索
- 引用高亮
- 反馈学习闭环
