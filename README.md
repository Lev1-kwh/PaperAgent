# PaperAgent

基于 RAG（检索增强生成）的论文智能问答系统。上传 PDF 论文后，系统完成解析、切分、向量化和存储；随后可针对指定论文提问，系统检索相关内容并调用大模型生成回答，同时返回可追溯的论文来源（页码 + 相似度距离）。

## 架构

```
用户请求
   │
   ▼
FastAPI Router（app/routers）           ← 参数校验、HTTP 语义（400/404/500）
   │
   ▼
Service 层（app/services）
   ├── text_service      PDF 文本清洗 + 段落切分
   ├── chunk_service     段落 → 1000 字符 chunk（超长段落强切，短段落合并）
   ├── embedding_service all-MiniLM-L6-v2 句向量（384 维）
   ├── vector_service    ChromaDB 写入 / 删除 / 按 paper_id 隔离检索
   ├── rag_service       RAG 主流程：向量化问题 → 检索 → 组装 prompt → 调用 LLM
   ├── llm_service       DeepSeek API 封装
   └── paper_service     论文元数据 CRUD（SQLAlchemy + SQLite）
   │
   ▼
存储层
   ├── SQLite（app/database.db）  论文元数据
   └── ChromaDB（chroma_db/）     420+ chunk 向量与原文
```

## 技术栈

Python 3.13 · FastAPI · SQLAlchemy 2.x · SQLite · ChromaDB · PyMuPDF · Sentence Transformers (all-MiniLM-L6-v2) · DeepSeek API · Pydantic v2 · pytest

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/papers/upload` | 上传 PDF：解析→切分→向量化→存储。失败时补偿删除已写入的 Chroma 向量与文件（201） |
| GET | `/papers` | 论文列表 |
| GET | `/papers/{paper_id}` | 论文详情（404：不存在） |
| DELETE | `/papers/{paper_id}` | 删除论文及其向量（404：不存在） |
| POST | `/papers/ask` | 指定论文提问，返回回答 + 来源列表（400：空问题；404：论文不存在；500：RAG 服务异常） |

## 运行

```bash
# 1. 克隆后创建虚拟环境并安装依赖（12 个直接依赖，见 requirements.txt）
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

# 2. 配置环境变量（项目根目录创建 .env）
#    DEEPSEEK_API_KEY=你的密钥

# 3. 启动（任意目录均可，数据路径已锚定项目根，不依赖启动目录）
uvicorn app.main:app --reload

# 4. 运行测试（20 个用例，覆盖 5 个端点 + service 层异常分支）
#    Windows PowerShell 建议先设离线模式，避免模型加载时联网校验挂起：
$env:HF_HUB_OFFLINE = '1'
pytest tests/ -v
```

> 首次启动会自动下载 all-MiniLM-L6-v2 模型（约 90MB，国内可设置 `HF_ENDPOINT=https://hf-mirror.com` 加速）。

## 数据一致性设计

**上传（写入）**：文件落盘 → Chroma 写入 → SQLite 提交。SQLite 提交失败时，补偿删除已写入的 Chroma 向量和 PDF 文件（`test_upload_commit_failure` 验证）；Chroma 写入失败时清理文件（`test_upload_chroma_failure` 验证）。

**删除**：先删 Chroma 向量，再删 SQLite 记录。已知限制见下。

## 测试

20 个 pytest 用例，FastAPI TestClient + unittest.mock：

- 5 个端点的正常路径与主要错误路径（400/404/500）
- Service 层事务边界（commit 失败 → rollback + 资源释放）
- 上传失败补偿逻辑（Chroma 补偿删除、文件清理）
- Session 释放断言（所有异常路径 `close()` 恰好调用一次）

## 已知限制（V1.0 有意不处理）

1. **删除流程一致性窗口**：先删 Chroma 后删 SQLite。若 SQLite 提交失败，rollback 恢复记录但向量已删，留下"幽灵论文"（列表可见、提问检索为空）。曾评估改为先删 SQLite 后删 Chroma（失败残留变为不可达的孤儿向量，用户无感知），但两种顺序各有失效模式，真正的修复需要后台对账任务或 outbox 模式，超出 V1.0 复杂度预算。取舍：记录而非过度工程。
2. **删除不清理 uploads 文件**：DELETE 只删向量与元数据，PDF 文件保留在 `uploads/`。
3. **500 响应包含内部异常细节**（如 DeepSeek 报错原文）：生产环境应替换为通用消息 + 服务端日志。
4. **LLM 调用无超时**：DeepSeek 长时间无响应时请求会一直挂起。
5. **Chroma 距离度量**：默认 L2，与 sentence-transformers 生态惯用的 cosine 数值不可直接比较（排序近似可用）。
6. **空白 PDF / 无文本 PDF**：chunks 为空会使 Chroma add 报错，返回 500。
7. **上传无文件大小限制**。
8. **依赖版本弃用警告** 2 条（starlette/anyio BlockingPortal、Pydantic class-based Config），不影响功能，升级留待后续版本。

## 后续计划

RAG 检索质量优化（相似度阈值、Top-K 调优、检索评估）、简单任务路由（总结/方法提取/实验分析三类 prompt 流程）——按学习路线安排在后续阶段，V1.0 到此收口。
