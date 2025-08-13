# LabAcc Copilot

**基于 LangGraph React Agent 的 AI 智能实验室助手，用于分析实验数据、诊断问题并提供优化建议。**

## 🎯 当前状态：v2.1 - 简化的 React Agent

✅ **已简化**：单一 React Agent 配合工具（LangGraph）  
✅ **自然语言**：LLM 自然理解任何语言的意图  
✅ **易维护**：代码量减少 70%，易于扩展  
✅ **经过验证**：使用 LangGraph 经过实战检验的 React 模式  
🚧 **下一步**：后台处理和主动洞察功能

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- uv（Python 包管理器）

### 安装步骤
```bash
# 克隆仓库
git clone <repo-url>
cd Labacc_copilot

# 安装 Python 依赖
uv sync

# 安装前端依赖
cd frontend && npm install && cd ..

# 设置 API 密钥（深度研究功能需要）
export TAVILY_API_KEY="your-tavily-key"      # 用于文献搜索
export LANGFUSE_SECRET_KEY="your-langfuse-key"  # 可选：LLM 追踪
```

### 启动开发环境
```bash
# 终端 1：后端 API + React Agent
uv run uvicorn src.api.app:app --port 8002 --reload

# 终端 2：React 前端
cd frontend && npm run dev

# 访问应用：http://localhost:5173
```

## 🤖 React Agent 系统（v2.1）

### 简洁架构
```
用户查询 → LangGraph React Agent → 选择合适的工具
                 │
                 ├─→ 📁 scan_project：列出所有实验
                 ├─→ 🔬 analyze_experiment：分析特定文件夹
                 ├─→ 📚 research_literature：搜索论文（Tavily）
                 ├─→ ⚡ optimize_protocol：优化建议
                 └─→ 💾 manage_files：文件操作
```

### 工作原理

**无需手动意图检测！** LangGraph React Agent 使用 LLM 的自然语言理解能力：
1. 理解任何语言的用户意图
2. 决定使用哪些工具
3. 执行相应的工具
4. 返回自然的响应

### 可用工具

#### 📁 **scan_project（扫描项目）**
- 列出项目中的所有实验
- 显示文件数量和创建日期
- 提供实验摘要

#### 🔬 **analyze_experiment（分析实验）**
- 分析特定实验文件夹
- 审查协议和数据文件
- 基于实验类型提供洞察

#### 📚 **research_literature（文献研究）**
- 通过 Tavily API 搜索科学文献
- 快速或深度研究模式
- 返回相关论文和方法

#### ⚡ **optimize_protocol（优化协议）**
- 提供优化建议
- 故障排除特定问题
- 提供协议改进方案

#### 💾 **manage_files（管理文件）**
- 创建实验文件夹
- 组织文件
- 列出文件夹内容

### 示例命令

**快速响应（即时）：**
```
"你好"                      → 欢迎消息和功能介绍
"扫描我的项目"              → 所有实验概览
"优化我的协议"              → 策略建议
"我接下来该做什么？"        → 下一步指导
```

**深度研究（10-30 秒）：**
```
"深度研究 PCR 优化"         → 文献搜索 + 报告
"研究 GC 富集模板方法"      → 科学论文分析
"凝胶电泳的文献"            → 方法验证
```

## 🏗️ 系统架构

### 简化的响应流程

1. **用户发送消息**（任何语言）
2. **React Agent 自然理解**意图
3. **Agent 自动选择工具**
4. **工具执行**并返回结果
5. **Agent 自然格式化响应**

**响应时间：**
- 简单查询：2-3 秒
- 分析任务：3-5 秒
- 文献搜索：10-30 秒（Tavily API）

### 基于文件的记忆系统
```
data/alice_projects/
├── .labacc/                    # Copilot 元数据
│   ├── project_knowledge.md   # 跨实验洞察
│   └── agent_state.json       # 持久化 agent 记忆
├── exp_001_pcr_optimization/
│   ├── README.md              # 实验文档
│   └── [数据文件...]
└── [更多实验...]
```

## 📊 主要功能

### 当前能力（v2.1）
- ✅ **React Agent**：单一 agent 配合多个工具
- ✅ **自然语言**：支持任何语言
- ✅ **深度研究**：Tavily 驱动的文献搜索
- ✅ **项目扫描**：自动实验发现
- ✅ **智能工具**：上下文感知分析
- ✅ **文件管理**：集成实验浏览器
- ✅ **简单易维护**：比 v2.0 减少 70% 代码

### 即将推出（v2.2）
- 🚧 **后台处理**：主动实验监控
- 🚧 **模式识别**：跨实验分析
- 🚧 **预测建模**：成功概率计算
- 🚧 **多模态分析**：高级图像处理
- 🚧 **更多工具**：易于添加新功能

## 🔧 开发

### 项目结构
```
├── frontend/                 # React 应用
│   └── src/components/      # UI 组件
├── src/
│   ├── agents/              
│   │   └── react_agent.py  # 单一 React Agent 配合工具
│   ├── api/                 # FastAPI 端点
│   │   ├── app.py          # 主 API
│   │   └── react_bridge.py # 连接 React Agent 的桥接
│   ├── tools/               # 实用工具
│   │   └── deep_research/  # Tavily 集成
│   └── components/          # 核心组件
├── data/
│   └── alice_projects/      # 实验存储
└── CLAUDE.md               # 开发指南
```

### 运行测试
```bash
# 测试 React Agent
uv run python src/agents/react_agent.py

# 测试 API 服务器
uv run uvicorn src.api.app:app --port 8002 --reload
# 然后：curl -X POST http://localhost:8002/api/chat/message ...

# 测试深度研究（需要 Tavily API 密钥）
uv run python test_deep_research.py
```

### 配置

**环境变量：**
```bash
# 深度研究必需
export TAVILY_API_KEY="tvly-xxxxx"

# 可选 LLM 配置
export LANGFUSE_SECRET_KEY="sk-lf-xxxxx"
export LANGFUSE_PUBLIC_KEY="pk-lf-xxxxx"

# 自定义项目根目录（默认：data/alice_projects）
export LABACC_PROJECT_ROOT="/path/to/projects"
```

**深度研究设置**（为测试而优化）：
- 查询扇出：3 个查询（从 10 个减少）
- 研究循环：1 次（从 2 次减少）
- 超时：30 秒
- 成本：每次研究查询约 $0.01-0.03

## 📈 性能指标

- **简单查询**：2-3 秒（工具选择 + 执行）
- **分析任务**：3-5 秒（数据处理）
- **深度研究**：10-30 秒（Tavily API）
- **项目扫描**：100 个实验少于 2 秒
- **文件操作**：少于 1 秒

## 🔒 安全与隐私

- 所有数据本地存储在 `data/alice_projects/`
- 无自动云上传
- API 密钥存储为环境变量
- 文件路径验证防止遍历
- 人类可读的基于文件的记忆（无黑箱嵌入）

## 🤝 贡献

请参阅 [CLAUDE.md](CLAUDE.md) 了解开发指南和架构决策。

## 📝 许可证

[许可信息]

## 🔗 资源

- **文档**：查看 `/dev_plan/` 了解详细计划
- **状态**：查看 `STATUS.md` 了解当前能力
- **愿景**：阅读 `dev_plan/v2_copilot_vision.md` 了解路线图

---

## 🎯 添加新功能（超简单！）

使用 v2.1 的简化架构，添加新功能非常容易：

```python
# 1. 打开 src/agents/react_agent.py
# 2. 添加你的工具：
from langchain_core.tools import tool

@tool
def 你的新工具(参数: str) -> str:
    """工具描述 - LLM 会读取这个来理解何时使用它。"""
    # 实现
    return "结果"

# 3. 添加到工具列表
tools = [...现有工具, 你的新工具]

# 4. 完成！Agent 会在合适的时候自动使用它
```

---

**版本**：2.1.0  
**最后更新**：2025-01-12  
**状态**：简化的 React Agent 已运行