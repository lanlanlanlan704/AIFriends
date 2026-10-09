# AIFriends大模型应用开发

> 一个支持文本、语音双模态交互的 AI 角色聊天系统。用户可以创建自定义角色，与角色自然对话，角色具备多轮记忆与知识库检索增强（RAG），并能主动发起消息互动。

## 功能特性

- **角色对话**：创建自定义角色（人设、音色、形象），与角色进行自然对话
- **语音交互**：语音输入（ASR）+ 语音回复（TTS），全链路流式输出
- **多轮记忆**：短期记忆（滑动窗口）+ 长期记忆（记忆总结 Agent 压缩）结合
- **知识库 RAG**：基于 LanceDB 的语义向量检索增强，回答角色预设知识
- **主动消息**：AI 可主动发起对话，实现"AI 找用户"的陪伴体验
- **角色广场**：浏览、搜索、创建角色，建立好友关系

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 · Pinia · Vite · Tailwind CSS |
| 后端 | Django 6 · DRF · Channels(ASGI) · JWT |
| AI 编排 | LangChain · LangGraph · 阿里云百炼(LLM/Embedding/ASR/TTS) |
| 检索 | LanceDB(向量检索) |
| 数据 | SQLite(开发) / PostgreSQL(部署) |

## 架构

```
前端 Vue3 SPA
   │ HTTP / WebSocket / SSE
后端 Django + Channels(ASGI)
   ├─ Agent 层：LangGraph 状态图（agent → tools → agent，ReAct 循环）
   │    工具：查询时间、检索知识库
   ├─ RAG 层：LanceDB 向量检索 + 语义相似度
   ├─ 多模态：实时语音 ASR、流式文本 SSE、语音合成 TTS
   └─ 记忆层：短期窗口 + 长期记忆总结
   │
数据：SQLite / PostgreSQL   ·   向量：LanceDB   ·   AI：阿里云百炼
```

## 快速开始

### 后端

```bash
# 1. 进入项目根目录，安装依赖（requirements.txt 在根目录）
pip install -r requirements.txt

# 2. 配置环境变量（复制模板并填入密钥）
cp .env.example .env

# 3. 迁移数据库
cd backend
python manage.py migrate

# 4. 启动后端
python manage.py runserver
```

### 前端

需要后端已启动，另开一个终端：

```bash
cd frontend
npm install
npm run dev   # 访问 http://localhost:5173
```

### 生产构建（可选）

```bash
cd frontend
npm run build   # 产物输出到 backend/static/frontend/
```

背起 Daphne + Nginx + PostgreSQL 可部署上线（详见配置）。

## 项目结构

```
AIFriends/
├── backend/            Django 后端（含 WebSocket）
│   ├── backend/        项目配置（settings / asgi / urls）
│   └── web/            业务应用
│       ├── views/      视图与 AI 编排（chat / asr / memory / proactive）
│       ├── documents/  RAG 知识库（插入、检索、嵌入）
│       └── models.py   数据模型
├── frontend/           Vue3 前端
│   └── src/            组件、页面、状态、路由
├── requirements.txt    后端依赖
└── docker-compose.yml  本地 PostgreSQL
```

## 核心设计

- **Agent 编排**：LangGraph 状态图 + 条件路由，模型通过工具调用自主决定是否检索知识库（ReAct 循环）
- **记忆机制**：短期记忆拼接最近对话保障连贯；长期记忆由独立 Agent 压缩为结构化摘要，失败时保留旧记忆
- **多模态链路**：前端 VAD 检测 + 实时 ASR（WebSocket）、流式文本（SSE）、语音合成（TTS），全链路流式输出
- **主动消息**：哨兵机制定时判断，AI 可主动发起对话（单好友单哨兵，防重复）

## License

个人项目，未经许可请勿商用。