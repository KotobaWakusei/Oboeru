# Oboeru - 智能背单词系统

一个功能完善的 Python Tkinter GUI 背单词软件，支持 AI 例句生成、自定义词库、收藏管理和学习统计。

## 功能特点

### 核心功能
- 📚 支持自定义词库，灵活管理单词学习内容
- 📝 可调节的每日背诵单词数量（1-100）
- 🎯 先背诵后测试的两阶段学习模式
- 🔄 错误单词自动加入复习列表
- ⭐ 收藏不熟悉的单词，支持排序和备份

### AI 例句生成
- 🤖 多种 AI 提供商支持（讯飞星火、OpenAI、DeepSeek、Moonshot、智谱等）
- 🎓 6 级例句难度（小学、初中、高中、四级、六级、高级）
- ⚙️ 支持自定义 OpenAI 兼容 API
- 💡 根据难度自动调整例句复杂度和词汇水平

### 个性化设置
- 🎨 主题模式切换
- 🔤 可调节字体大小（12-24号）
- 🔀 随机顺序学习选项
- 📊 显示/隐藏进度条
- 💾 自动保存配置

### 学习统计
- 📈 今日学习数量统计
- 📊 总学习次数记录
- ⏱️ 学习时长追踪
- 📋 最近学习记录

### 交互优化
- ⌨️ 键盘快捷键支持
- ✨ 双击单词进入答题模式
- 🔊 TTS 语音朗读（支持 edge-tts 高质量语音、gtts、espeak）
- 📐 自适应窗口大小
- 🎯 响应式导航栏（窗口变小时自动调整为图标模式）
- 📝 背诵阶段显示最近单词回顾（鼠标悬停/点击查看意思）

## 项目结构

```
oboeru/
├── app.py                 # 应用入口
├── start.sh               # 启动脚本
├── data/
│   └── config.json        # 配置文件
├── modules/
│   ├── ai_manager.py      # AI 例句管理
│   ├── config_manager.py  # 配置管理
│   ├── favorites_manager.py # 收藏管理
│   ├── progress_manager.py # 进度管理
│   ├── tts_manager.py     # TTS 语音管理
│   ├── vocabulary_manager.py # 词库管理
│   └── utils/
│       ├── constants.py   # 常量定义
│       └── file_utils.py  # 文件工具
├── ui/
│   ├── core/
│   │   ├── application.py # 应用核心
│   │   ├── page_manager.py # 页面管理
│   │   └── style_manager.py # 样式管理
│   ├── components/        # UI 组件
│   └── pages/             # 页面模块
│       ├── home_page.py
│       ├── learning_page.py
│       ├── favorites_page.py
│       ├── settings_page.py
│       └── statistics_page.py
├── logs/
│   └── app.log            # 日志文件
└── backups/               # 备份目录
```

## 词库语法规则

词库文件采用文本格式（.txt），每行代表一个单词，使用制表符（Tab）分隔不同字段。

### 基本格式

```
单词	词性	中文意思	[可选：错误选项提示]
```

### 示例

```
# 这是一个注释行
apple	n.	苹果
banana	n.	香蕉
cat	n.	猫	cart,cut,cap
dog	n.	狗
good	adj.	好的	god,food,wood
```

## AI 配置

### 支持的 API 提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| 讯飞星火 Lite | lite | 免费版，适合日常使用 |
| 讯飞星火 Pro | generalv3 | 专业版，效果更好 |
| OpenAI | gpt-3.5-turbo | OpenAI GPT 模型 |
| DeepSeek | deepseek-chat | DeepSeek 大模型 |
| Moonshot | moonshot-v1-8k | 月之暗面 Kimi |
| 智谱 AI | glm-4-flash | 智谱 GLM 模型 |
| 自定义 | - | 任意 OpenAI 兼容 API |

### 例句难度等级

| 等级 | 最大词数 | 说明 |
|------|----------|------|
| 小学 | 10 | 简单词汇，短句，基础语法 |
| 初中 | 15 | 常用词汇，中等长度句子 |
| 高中 | 20 | 较复杂词汇，长句，多种句型 |
| 四级 | 25 | 四级词汇，复杂句型，学术表达 |
| 六级 | 30 | 六级词汇，高级表达，学术写作风格 |
| 高级 | 35 | 高级词汇，复杂句式，地道表达 |

### 配置示例

在设置页面配置：
1. 选择 API 提供商
2. 输入 API Key
3. 选择例句难度
4. 保存设置

## 配置文件说明

```json
{
  "daily_words": 20,
  "vocab_file": "data/vocabulary.txt",
  "theme": "default",
  "font_size": 14,
  "shuffle_words": true,
  "show_progress_bar": true,
  "ai_enabled": true,
  "ai_api_key": "your-api-key",
  "ai_provider": "xunfei_lite",
  "ai_difficulty": "junior",
  "ai_custom_url": "",
  "ai_custom_model": ""
}
```

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| daily_words | 每日单词量 | 20 |
| ai_enabled | 启用 AI 例句 | false |
| ai_provider | API 提供商 | xunfei_lite |
| ai_difficulty | 例句难度 | junior |
| ai_custom_url | 自定义 API URL | - |
| ai_custom_model | 自定义模型名称 | - |

## 安装与运行

### 环境要求

- Python 3.8 及以上版本
- 支持GUI的Python环境

### 运行方法

```bash
# 直接运行
python3 app.py

# 或使用启动脚本
./start.sh
```

### 依赖说明

本项目主要使用 Python 标准库：
- `tkinter` - GUI 界面
- `json` - 配置文件
- `threading` - 异步处理
- `urllib` - HTTP 请求

**可选依赖（用于增强功能）：**
- `Pillow` - 窗口图标生成
- `edge-tts` - 高质量TTS语音朗读（推荐）
- `gtts` - TTS语音朗读（备选）
- `espeak` - TTS语音朗读（基础，系统级安装）

如果 Tkinter 未安装：
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter
```

安装可选依赖：
```bash
pip install Pillow edge-tts gtts
```

## 学习流程

### 1. 准备阶段
1. 打开软件，进入设置界面
2. 调整每日单词数量
3. 选择词库文件
4. 配置 AI 功能（可选）
5. 点击「保存设置」

### 2. 开始学习
1. 点击「开始学习」
2. 背诵阶段：记忆单词和意思
3. 可收藏不熟悉的单词
4. 可查看 AI 生成的例句

### 3. 测试阶段
1. 双击或按 Enter 进入答题
2. 从四个选项中选择答案
3. 答错自动加入复习列表
4. 完成后显示学习结果

### 4. 复习与管理
- 查看收藏的单词
- 查看学习统计
- 导出学习数据

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Enter | 进入答题模式 |
| ← 左箭头 | 上一个单词 |
| → 右箭头 | 下一个单词 |

## 更新日志

### v3.0
- ✨ AI 例句生成功能
- 🎓 6级例句难度支持
- 🔌 多种 AI API 提供商
- ⚙️ 自定义 API 支持
- 📊 学习统计功能
- 🔊 TTS 语音朗读
- 🏗️ 模块化重构

### v2.0
- ✨ 全新设置界面
- ✨ 输入验证功能
- ✨ 三种主题模式
- ✨ 键盘快捷键支持
- ✨ 收藏功能增强

## 许可证

MIT License