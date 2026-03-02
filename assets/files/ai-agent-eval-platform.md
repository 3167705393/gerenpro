# 企业级 AI Agent 自动化评估与 LLMOps 管理平台

## 1. 项目背景与设计理念 (Background & Philosophy)

随着大模型应用从"玩具 Demo"向"企业级生产环境"迈进，传统的软件测试方法已无法适应 AI Agent 非确定性、易产生"幻觉"的特性。在缺乏科学评测工具的情况下，团队往往只能依靠低效的人工抽测来判断 Prompt 或 RAG 知识库的优化效果，导致 Agent 上线周期长、稳定性难以保证。

**设计理念：**

本项目旨在打造一条**专属于 AI Agent 的 CI/CD（持续集成与交付）流水线**。通过构建全异步的高并发调度底座，结合 **LLM-as-a-Judge（大模型裁判）** 机制，将 Agent 的能力评测从"人工玄学的盲测"彻底转化为"可视化、可追溯的量化科学"，为研发团队提供稳定、高效的大模型应用度量衡。

---

## 2. 核心系统架构 (Core Architecture)

系统采用经典的**前后端分离 + 异步任务调度**的微服务架构，基于 Docker Compose 实现一键容器化部署。

### 2.1 技术栈概览

| 层级 | 技术选型 | 职责 |
|------|----------|------|
| **前端交互层 (Frontend)** | `Vue 3` + `Vite` + `TypeScript` | 动态数据可视化展示、测试任务的细粒度生命周期管理、二进制流（Blob）测试报告下载 |
| **业务网关层 (Backend)** | `FastAPI` + `Python` | 极速响应前端请求，管理 PostgreSQL 异步连接池，下发调度任务 |
| **异步调度层 (Task Queue)** | `Celery` + `Redis` | 充当"缓冲池"与"苦力"，剥离耗时极长的大模型推理任务 |
| **数据持久层 (Storage)** | `PostgreSQL 15` + `MinIO` | 结构化数据（测试用例、评价规则、跑分）+ 非结构化数据（对话日志、大型文件） |

---

## 3. 核心运行机理：平台是如何流转的？

当用户在前端发起一次针对 Agent 的批量测试时，系统内部将经历以下 4 个标准化的业务阶段：

### 阶段一：环境与资产配置 (Configuration)

1. **被测端点接入 (Agent Endpoint)**：在系统中配置待测目标（如 Dify 应用的 API URL 与 Bearer Token），支持多环境隔离。
2. **评价策略配置 (Evaluator Config)**：动态挂载"裁判模型"（如 GPT-4o / Qwen-Max），并设定评分的 Prompt 规则体系（如："请依据准确度、相关性、是否幻觉进行 1-10 分评级"）。

### 阶段二：测试用例构建 (Test Suite)

用户可通过界面手动录入或 Excel 批量导入包含 `[用户 Query]` 与 `[预期参考答案]` 的海量测试用例，并将其打包为特定的测试套件（Test Suite）。

### 阶段三：异步并发执行 (Automated Batch Execution)

1. **任务下发**：前端调用 `/test-jobs` 接口，FastAPI 接收请求并在 PostgreSQL 中创建状态为 `PENDING` 的任务记录。
2. **平滑排队**：FastAPI 将任务 ID 抛入 Redis 消息队列，系统立刻给前端返回受理成功响应，避免浏览器阻塞。
3. **高并发调度**：后台 Celery Worker 监听 Redis，按设定的并发上限（Concurrent Limit）拉取任务。Worker 从数据库提取测试用例，向被测 Dify 端点发起并发请求。此机制完美规避了大模型 API 的 Rate Limit（限流）问题。

### 阶段四：LLM-as-a-Judge 自动断言与归档 (Evaluation)

1. **智能判卷**：Celery 拿到 Dify 的真实回答后，将其与"预期答案"封装进评价 Prompt 中，发送给"裁判大模型"进行自动化打分。
2. **状态机控制与导出**：测试过程中，前端可通过操作 Redis 状态位，随时对长耗时任务进行**暂停 (Pause) / 恢复 (Resume) / 终止 (Cancel)**。测试结束后，后端利用 Pandas 将 PostgreSQL 中的跑分数据与 MinIO 中的过程日志汇聚，通过 HTTP 流式响应（StreamingResponse）推送给前端，实现 Excel 报告的一键下载。

---

## 4. 项目的宏观意义与业务价值

### 4.1 建立大模型时代的"度量衡"

将非结构化的自然语言回答转化为确切的**通过率 (Pass Rate)** 与 **得分矩阵**。让研发团队每次微调 Prompt 或优化 RAG 文档切分策略时，都能拥有"用数据说话"的底气，彻底消除 AI 研发过程中的盲盒效应。

### 4.2 突破工程死穴，保障系统高可用

大模型 API 调用耗时长、易超时。本项目通过坚固的 FastAPI + Celery 异步底座，成功实现了流量的"削峰填谷"。不仅保护了被测 Agent 端点不被海量并发打崩，更实现了单次支撑成千上万条用例长效回归测试的工程奇迹。

### 4.3 赋能 LLMOps，极致降本增效

将原本需要测试团队花费数天时间进行的人工对话回归测试，压缩至"喝杯咖啡的时间"。完全自动化的批处理流水线，让 AI Agent 从"实验室"走向"生产环境"的周期缩短了数倍，极大节省了企业级 AI 应用的落地成本。

---

## 5. 研发模式实践：AI 驱动式工程 (AI-Driven Development)

本项目的落地深度实践了前沿的**基于大模型的敏捷工程（AI 辅助编程）**模式：

- **架构师思维主导**：由开发者全盘把控系统的顶层架构设计（如引入 Redis 解决异步解耦、设计 PostgreSQL 库表关联模型）。
- **AI 赋能提效**：利用大模型高效完成 CRUD 代码生成、Vue 3 页面骨架搭建及底层接口联调，将基础编码耗时压缩 80% 以上。
- **工程兜底与深度 Review**：针对核心难点（如 Celery 任务的细粒度中断机制、大文件 Blob 流式传输的内存管理），由开发者进行严密的逻辑重构与代码审查，确保 AI 生成代码在企业级生产环境下的绝对安全与稳定。

---

## 6. 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户交互层                                      │
│                     Vue 3 + Vite + TypeScript                            │
│              (数据可视化 / 任务管理 / 报告下载)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           业务网关层                                      │
│                        FastAPI + Python                                  │
│            (请求路由 / 异步连接池 / 任务下发 / 状态查询)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │   Redis      │ │ PostgreSQL   │ │    MinIO     │
           │  消息队列     │ │   数据持久   │ │  对象存储    │
           └──────────────┘ └──────────────┘ └──────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        异步任务调度层                                     │
│                      Celery Worker Pool                                  │
│         (并发控制 / 任务执行 / LLM调用 / 状态机管理)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
           ┌──────────────┐               ┌──────────────┐
           │  被测 Agent   │               │  裁判模型    │
           │  (Dify/自研)  │               │ (GPT-4o等)  │
           └──────────────┘               └──────────────┘
```

---

## 7. 核心技术亮点

### 7.1 异步任务生命周期管理

```
PENDING → RUNNING → PAUSED → RUNNING → COMPLETED
                   ↘ CANCELLED
```

- 支持任务的**暂停/恢复/取消**操作
- 基于 Redis 状态位实现轻量级控制
- 任务状态实时同步至前端

### 7.2 流量削峰填谷机制

```
前端请求 ──▶ FastAPI ──▶ Redis Queue ──▶ Celery Worker
    │            │                              │
    │     立即返回任务ID          按并发上限消费任务
    │                                        │
    └──────────── 轮询状态 ──────────────────┘
```

### 7.3 LLM-as-a-Judge 评价体系

```python
# 评价 Prompt 模板示例
evaluation_prompt = """
你是一个专业的 AI 回答质量评估专家。

【用户问题】{query}
【预期答案】{expected_answer}
【实际回答】{actual_answer}

请从以下维度进行评分（1-10分）：
1. 准确度：回答是否准确无误
2. 相关性：回答是否紧扣问题
3. 完整性：回答是否覆盖所有要点
4. 幻觉检测：是否存在虚构信息

输出格式：JSON { "accuracy": X, "relevance": X, "completeness": X, "hallucination": X, "total": X, "comment": "..." }
"""
```

---

## 8. 部署指南

### 8.1 Docker Compose 一键部署

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/eval
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  worker:
    build: ./backend
    command: celery -A worker worker --concurrency=4
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/eval
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=eval

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  redisdata:
  miniodata:
```

### 8.2 快速启动

```bash
# 克隆项目
git clone <repo-url>
cd ai-agent-eval-platform

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 访问前端
open http://localhost
```

---

## 9. 未来规划

- [ ] 支持更多裁判模型（Claude、Gemini、国产大模型）
- [ ] 集成 RAG 知识库评测模块
- [ ] 添加 A/B Testing 对比评测功能
- [ ] 支持自定义评价维度与权重
- [ ] 对接 Prometheus + Grafana 监控大盘
- [ ] 支持多租户与权限管理

---

*文档生成时间：2026-02-27*