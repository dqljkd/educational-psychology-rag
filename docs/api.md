# API 文档

## 健康检查

### `GET /health`
返回系统状态、向量集合名称、模型信息。

示例响应：
```json
{
  "status": "ok",
  "collection_name": "knowledge_base",
  "chat_model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small",
  "message": null
}
```

## 导入文档

### `POST /ingest`
表单上传多个文件，支持 `txt`、`md`、`pdf`。

示例响应：
```json
{
  "documents": 2,
  "chunks": 36,
  "files": ["guide.md", "faq.pdf"],
  "collection_name": "knowledge_base"
}
```

## 检索

### `POST /search`
请求体：
```json
{
  "query": "系统支持哪些部署方式？",
  "top_k": 4
}
```

## 问答

### `POST /ask`
请求体：
```json
{
  "question": "系统如何部署到线上？",
  "top_k": 4
}
```

返回：
- `answer`
- `contexts`

每个 context 包含：
- `source`
- `content`
- `score`
- `chunk_id`
