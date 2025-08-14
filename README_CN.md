# LabAcc Copilot

实验数据分析和优化的 AI 实验室助手。

## 🎯 当前状态：v2.2.1 - 生产就绪

✅ **记忆系统**：每个实验都有基于 README 的持久记忆  
✅ **实时可见性**：实时显示正在运行的工具  
✅ **多语言支持**：自然支持中文、英文、西班牙语等  
✅ **上下文感知**：预加载相关上下文以减少工具调用  
✅ **生产就绪**：所有主要问题已解决

## 🚀 快速开始

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆并设置
git clone <repo-url>
cd Labacc_copilot
uv sync
cd frontend && npm install && cd ..

# 设置 API 密钥
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# 启动
./start-dev.sh
# 打开 http://localhost:5173
```

## 💡 功能特性

- **多语言支持**：支持中文、英文、西班牙语等
- **记忆系统**：每个实验都有持久的 README 记忆
- **实时工具可见性**：实时查看正在运行的工具
- **文献搜索**：集成 Tavily API 搜索研究论文
- **智能上下文**：预加载相关数据以减少工具调用

## 📝 使用示例

```
"列出我的实验"               → 列出所有实验
"分析 exp_001 数据"         → 分析特定实验
"PCR 优化建议"              → 提供优化建议
"研究 CRISPR 方法"          → 搜索科学文献
"创建新实验文件夹"           → 创建新实验文件夹
```

## ⚙️ 配置

```bash
export TAVILY_API_KEY="tvly-..."     # 文献搜索
export OPENROUTER_API_KEY="sk-..."   # LLM 提供商
```

## 🔧 故障排除

- **端口已被占用**：终止现有进程或使用不同端口
- **API 密钥错误**：确保环境变量设置正确
- **前端无法加载**：检查后端是否在端口 8002 运行
- **工具未找到**：代码更改后重启后端

## 📚 文档

- `STATUS.md` - 当前系统状态和更新日志
- `CLAUDE.md` - 开发指南（开发者用）
- `/spec/` - 技术规范
- `/dev_plan/` - 开发路线图

## 📄 许可证

MIT 许可证 - 详见 LICENSE 文件

---

**版本**：2.2.1  
**最后更新**：2025-01-14  
**状态**：生产就绪