# 桩基础谜案 - AI DM

一款基于大语言模型的剧本杀 AI DM（主持人）应用程序。

## 项目特性

- 🎭 五人硬核工程推理剧本
- 🤖 AI驱动的游戏主持人
- 🕵️ 搜证、诡计、质证、复盘四个阶段
- 📱 支持语音输入
- 🔍 线索收集与管理系统

## 快速开始

### 本地运行

```bash
# 克隆项目
git clone <repository-url>
cd aidm

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
echo "LLM_API_KEY=your-api-key" > .env
echo "BASE_URL=https://api.deepseek.com/v1" >> .env
echo "MODEL_NAME=deepseek-chat" >> .env

# 启动应用
streamlit run app.py
```

### Streamlit Cloud 部署

1. **创建 GitHub 仓库**
   - 将项目代码上传到 GitHub

2. **配置 Secrets**
   在 Streamlit Cloud 的 Secrets 中添加：
   ```toml
   LLM_API_KEY = "your-deepseek-api-key"
   BASE_URL = "https://api.deepseek.com/v1"
   MODEL_NAME = "deepseek-chat"
   ```

3. **部署应用**
   - 访问 https://share.streamlit.io/
   - 连接您的 GitHub 仓库
   - 设置主文件为 `app.py`
   - 点击 Deploy

## 项目结构

```
aidm/
├── app.py              # 主应用入口
├── logic.py            # 游戏逻辑
├── voice_input.py      # 语音输入模块
├── requirements.txt    # 依赖列表
├── start.sh            # 启动脚本
└── data/               # 知识库
    ├── roles.json      # 角色信息
    ├── clue.json       # 线索数据
    ├── truth.txt       # 真相复盘
    ├── system_prompt.txt  # 系统提示
    └── stage_openings.json # 阶段开场台词
```

## 游戏玩法

1. **选择角色**：从五个角色中选择一个
2. **搜证阶段**：搜索现场线索，消耗AP点数
3. **诡计阶段**：分析物理诡计
4. **质证阶段**：对峙嫌疑人
5. **复盘阶段**：揭示真相

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| LLM_API_KEY | DeepSeek API 密钥 | 空 |
| BASE_URL | API 地址 | https://api.deepseek.com/v1 |
| MODEL_NAME | 模型名称 | deepseek-chat |

## 技术栈

- Streamlit - 前端框架
- OpenAI API - 大语言模型调用
- DeepSeek - AI模型提供商
- Python - 后端语言

## 许可证

MIT License
