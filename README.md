# Ning_Prompt (提示词工坊)

Ning_Prompt 是一个基于 Flet 开发的桌面端提示词（Prompt）优化与实验工具。旨在帮助用户通过 AI 的辅助，对原始提示词进行多维度的调整，以获得更符合预期的生成结果。

## ✨ 主要功能 (v1.2.0-beta)

本工具提供四种核心的提示词处理模式以及自定义模板功能：

1.  **语义增强 (Enhance)**
    *   **作用**: 丰富原始提示词的细节。
    *   **效果**: 添加描述性形容词、风格修饰词、光影氛围描述。适用于从简单的想法生成高质量、细节丰富的图像或文本。

2.  **语义泛化 (Generalize)** (原“语义弱化”)
    *   **作用**: 概括和抽象化提示词。
    *   **效果**: 移除具体的细节指令，保留核心概念。适用于希望 AI 发挥更多自由想象力，或需要生成更具艺术感、概念性结果的场景。

3.  **语义修复 (Repair)**
    *   **作用**: 填补逻辑漏洞和消除歧义。
    *   **效果**: 修正语法错误，补充缺失的上下文，确保提示词的逻辑连贯性。适用于原始想法比较碎片化或表述不清的情况。

4.  **语义剪枝 (Pruning)** (原“语义破坏”)
    *   **作用**: 精简指令，保留核心。
    *   **效果**: 移除冗余、重复或无关紧要的修饰，保留最核心、最有效的指令。即“奥卡姆剃刀”式的处理。

5.  **自定义模板 (Custom Template)**
    *   **作用**: 加载用户自定义的 `.md` 提示词模板。
    *   **使用**: 选择此模式后，系统将扫描并列出 `core/prompts/` 文件夹下所有 `.md` 文件供您选择。您可以修改这些预设模板，或创建新的模板文件（例如 `my_custom_template.md`），将其放置在 `core/prompts/` 文件夹中。这些文件将被自动识别，并在下拉列表中显示。

    **定制提示词示例**:
    打开 `core/prompts/enhance.md` 文件，其内容大致如下：
    ```markdown
    You are an expert prompt engineer specializing in **Semantic Enhancement**.

    **Objective**:
    Expand the 'Original Prompt' by adding descriptive details, stylistic modifiers, atmospheric elements, and technical parameters to increase the quality and richness of the generated output.

    **Instructions**:
    1.  **Analyze**: Understand the core subject and intent of the Original Prompt.
    2.  **Expand**: Add relevant details (lighting, texture, composition, mood) that align with the core subject.
    3.  **Refine**: Use precise and evocative vocabulary.
    4.  {{format_instruction}}
    5.  {{language_instruction}}

    **Original Prompt**:
    {{original_prompt}}
    ```
    您可以在此基础上修改指令、添加新的占位符（需要在 `PromptLoader` 中处理），以完全控制 AI 的行为。

## 🔧 技术架构与目录结构

从 v1.2.0-beta 开始，核心处理逻辑采用了 **Model Context Protocol (MCP)** 的标准设计模式。这不仅规范了内部的数据流转，也为将来作为 Agent 工具或微服务集成奠定了基础。

*   **MCPRequest**: 标准化的请求对象，封装了模式、提示词、温度、上下文等参数。
*   **MCPResponse**: 标准化的响应对象，包含结果、元数据及错误信息。

项目主要目录结构如下：
```
Ning_Prompt/
├── core/
│   ├── config_manager.py       # 配置管理
│   ├── llm_client.py           # LLM API 客户端
│   ├── mcp/                    # Model Context Protocol 定义
│   │   └── protocol.py         # MCP 数据结构
│   ├── prompt_loader.py        # 提示词模板加载器
│   ├── prompt_processor.py     # 提示词处理核心逻辑
│   └── prompts/                # 预设和自定义提示词模板 (.md 文件)
│       ├── enhance.md
│       ├── generalize.md
│       ├── repair.md
│       └── pruning.md
├── ui/                         # 用户界面相关文件
│   ├── components.py
│   └── main_window.py          # 主窗口 UI 逻辑
├── config.json                 # 用户配置文件 (Git 忽略)
├── config.example.json         # 配置文件示例
├── main.py                     # 应用入口
├── requirements.txt            # 项目依赖
└── README.md                   # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8+。

### 2. 安装依赖

在项目根目录下运行以下命令安装所需的 Python 库：

```bash
pip install -r requirements.txt
```

### 3. 配置文件设置

项目默认不包含 `config.json` 文件。您需要从示例文件创建一个：

1.  找到项目根目录下的 `config.example.json` 文件。
2.  将其复制并重命名为 `config.json`。
3.  编辑 `config.json`，填入您的 API 信息：

```json
{
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "api_key": "YOUR_ACTUAL_API_KEY",
    "model": "deepseek-chat",
    "language": "zh",
    "theme_mode": "dark"
}
```

### 4. 运行应用

```bash
python main.py
```

## ⚙️ 设置与参数说明

在应用界面的右上角点击“设置”图标，可以进行以下配置：

*   **API 配置**:
    *   **API URL**: 接口地址。
    *   **API Key**: 鉴权密钥。
    *   **模型名称**: 指定调用的 AI 模型（如 `deepseek-chat`）。
*   **通用设置**:
    *   **界面语言**: 切换界面语言（支持中文/English）。
    *   **回答语言偏好**: 设置 AI 输出的语言（跟随原 Prompt、强制英文、强制中文）。
    *   **输出格式**: 选择 Markdown（结构清晰）或 Plain Text（纯文本）。
    *   **深色模式**: 切换应用的明暗主题。
*   **主界面参数**:
    *   **温度 (Temperature)**: 控制生成的随机性与创造性 (0.0 - 1.0)。值越高越发散，值越低越严谨。

## 📜 版本更新日志

### v1.2.0-beta (2025-12-15)
- **新增功能**:
    - **自定义模板模式**: 用户现在可以加载本地 `core/prompts/` 文件夹中的 `.md` 文件作为自定义提示词模板。
    - **输出结果一键复制**: 输出区域新增复制按钮，优化用户体验。
- **架构改进**:
    - 引入 **Model Context Protocol (MCP)**，统一 Agent 交互接口，提升可扩展性。
- **提示词模式重构**:
    - "语义弱化"更名为 **"语义泛化" (Generalize)**。
    - "语义破坏"更名为 **"语义剪枝" (Pruning)**。
    - 明确了语义修复和语义增强的区分。
- **参数化配置**:
    - 引入 **温度 (Temperature)** 参数，替代模糊的“处理强度”。
    - 增加了回答语言偏好和纯文本/Markdown 输出格式选项。
- **代码优化**: 模块化设计和架构分离，提升可维护性。

### v1.1.0-beta (2025-12-11)
- 初始版本发布，包含语义增强、语义弱化、语义修复、语义破坏四种模式。
- 支持 API URL, API Key, 模型名称, 界面语言, 主题模式配置。
- 打包为 Windows 可执行文件。
- 完善了项目 `README.md`, `config.example.json`, `LICENSE` 等文件。
- 修复了 `ModuleNotFoundError: No module named 'flet'` 和 `IndentationError` 等问题。

## 🤝 贡献指南

我们欢迎并鼓励对 Ning_Prompt 项目的贡献！如果您有兴趣贡献代码、提出功能建议或报告 Bug，请遵循以下指南：

1.  **Fork 项目**: 将本仓库 Fork 到您自己的 GitHub 账户。
2.  **Clone 仓库**: 将 Fork 后的仓库克隆到本地。
3.  **创建分支**: 为您的功能或 Bug 修复创建一个新的分支 (e.g., `feat/add-new-feature` 或 `fix/bug-description`)。
4.  **编码**: 在您的分支上进行开发。请确保代码符合项目已有的风格和规范。
5.  **测试**: 在提交之前，请确保所有更改都经过了充分的测试。
6.  **提交**: 使用约定式提交（Conventional Commits）规范编写提交信息。
    *   `feat`: 新功能
    *   `fix`: Bug 修复
    *   `docs`: 文档变更
    *   `style`: 代码风格修改 (不影响代码运行的变动)
    *   `refactor`: 重构 (非功能性修改)
    *   `perf`: 性能优化
    *   `test`: 添加或修改测试
    *   `build`: 影响构建系统或外部依赖的更改
    *   `ci`: CI 配置或脚本的更改
    *   `chore`: 其他不属于以上类型的日常任务
7.  **推送**: 将您的分支推送到 Fork 后的仓库。
8.  **提交 Pull Request**: 向原仓库提交 Pull Request，详细描述您的更改、解决的问题以及引入的新功能。

---
Enjoy your prompting!