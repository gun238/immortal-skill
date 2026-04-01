<div align="center">

# 永生.skill

**"人会离开，但 TA 说话的方式、讲过的故事、在乎的东西——不该跟着消失。"**

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![AgentSkills Standard](https://img.shields.io/badge/AgentSkills-Standard-8A2BE2.svg)](https://agentskills.io/)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-orange.svg)](https://docs.openclaw.ai/)
[![Platforms 12+](https://img.shields.io/badge/数据平台-12+-red.svg)](#数据来源)
[![Personas 7](https://img.shields.io/badge/角色模板-7种-teal.svg)](#七种角色一套框架)

</div>

---

<div align="center">

你的同事离职了，但他的经验没人能替。

你的导师退休了，但你还想听他说「这事儿你得这么想」。

你的亲人走了，但你想让下一代也能听到那些叮嘱。

你的朋友不联系了，但你们之间有过最好笑的对话。

你的前任离开了，但 TA 的语气你一辈子都记得。

你自己——万一哪天不在了呢？

<br/>

**把 TA 从聊天记录里「蒸馏」出来。**

**不是复制粘贴，是真正理解 TA 怎么说话、怎么想、在乎什么。**

</div>

---

<div align="center">

提供聊天记录（微信、飞书、iMessage、Telegram……）加上你的描述

从 **12+ 平台**、**4 个维度** 蒸馏出一个数字分身

用 TA 的语气说话，用 TA 的方式思考，记得 TA 经历过的事

</div>

<div align="center">

[数据来源](#数据来源) · [七种角色](#七种角色一套框架) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [English](#english)

</div>

---

## 数据来源

> 你和 TA 的对话散落在十几个 App 里，我们都能收。

| 类型 | 平台 | 采集方式 |
|:---:|------|---------|
| 💬 | **飞书** · **钉钉** · **Slack** · **Discord** · **Telegram** | API 自动拉取 |
| 📱 | **微信** · **iMessage** | 本地数据库读取 |
| 📦 | **WhatsApp** · **Twitter/X** · **Google Takeout** · **Facebook/Instagram** | 官方归档解析 |
| 📄 | **任意文本** · TXT · JSON · CSV · Markdown | 手动导入 |
| 📧 | **Email** (Gmail / mbox) | API 或归档解析 |

每个平台都有[详细的数据获取指南](docs/PLATFORM-GUIDE.md)。

---

## 七种角色，一套框架

> 不同的人，蒸馏的侧重点不同。不是所有维度都该提取——有些记忆该留，有些边界该守。

| 角色 | 蒸馏什么 | 伦理边界 |
|:---:|---------|---------|
| 🪞 **自己** | 全维度：怎么做事、怎么说话、经历过什么、是什么样的人 | 你的数据你做主 |
| 🏢 **同事** | 工作流程 + 沟通风格 | 仅限内部知识传承 |
| 🎓 **导师** | 教学方式 + 人生智慧 + 共同经历 | 教学目的，经授权 |
| 👴 **亲人** | 家族记忆 + 生活智慧 + 情感印记 | 家人知情同意 |
| 💔 **伴侣/前任** | 关系互动 + 共同记忆 + 亲密性格 | 正面回忆目的，严格脱敏 |
| 🍻 **朋友** | 友谊互动 + 共同经历 + 社交偏好 | 对方知情同意 |
| 🌍 **公众人物** | 公开风格 + 方法论 + 公开事迹 | 仅限公开资料，不模拟私人对话 |

每种角色都有独立的[蒸馏模板](personas/)。

---

## 四维蒸馏

> 不是把聊天记录塞进向量库就完事了。

```
           怎么做事                    怎么说话
        ┌──────────┐              ┌──────────┐
        │ 程序性知识 │              │ 互动风格  │
        │ procedure │              │interaction│
        └──────────┘              └──────────┘

        经历过什么                    是什么人
        ┌──────────┐              ┌──────────┐
        │ 记忆经历  │              │性格价值观 │
        │  memory   │              │personality│
        └──────────┘              └──────────┘
```

- 每条提取都标注**证据等级**：`verbatim`（原话）> `artifact`（文档）> `impression`（印象）
- 矛盾的信息**显式记录**，不静默覆盖——人本来就是矛盾的

---

## 安装

```bash
# 方式一：安装到当前工作区
cp -r immortal-skill <your-workspace>/skills/immortal-skill

# 方式二：全局安装
cp -r immortal-skill ~/.openclaw/skills/immortal-skill
```

验证：
```bash
openclaw skills list | grep immortal-skill
```

---

## 使用

在 OpenClaw 对话中自然地说就行：

> "帮我蒸馏李工的工作技能"
>
> "我想保留我奶奶说话的方式"
>
> "把我和前任的微信记录做成一个 Skill"
>
> "做一个我自己的数字分身"

### CLI 工具

```bash
# 查看支持哪些平台
python3 kit/immortal_cli.py platforms

# 配置平台凭证
python3 kit/immortal_cli.py setup feishu

# 采集数据
python3 kit/immortal_cli.py collect --platform feishu --scan
python3 kit/immortal_cli.py collect --platform wechat --db ~/wechat.db --channel "张三"
python3 kit/immortal_cli.py collect --platform imessage --scan
python3 kit/immortal_cli.py collect --platform telegram --channel "好友群"

# 导入本地文件
python3 kit/immortal_cli.py import ~/chat-export.txt --output corpus/chat.md

# 初始化 → 封包 → 快照
python3 kit/immortal_cli.py init --slug grandma --persona family
python3 kit/immortal_cli.py stamp --slug grandma --sources "wechat:chat,paste:notes"
python3 kit/immortal_cli.py snapshot --slug grandma --note "第一版"
```

---

## 效果示例

项目自带 3 个完整示例，展示不同角色的蒸馏效果：

| 示例 | 角色 | 维度 | 查看 |
|------|------|------|------|
| 李工 | 同事 | procedure + interaction | [examples/li-gong-demo/](examples/li-gong-demo/) |
| 陈韵 | 自己 | 全四维度 | [examples/self-demo/](examples/self-demo/) |
| 王老师 | 导师 | interaction + memory + personality + procedure | [examples/mentor-demo/](examples/mentor-demo/) |

---

## 目录结构

```
immortal-skill/
├── SKILL.md                  # 蒸馏器入口（meta skill）
├── personas/                 # 7 种角色模板
├── recipes/                  # 蒸馏方法论
├── prompts/                  # LLM Prompt 模板
├── collectors/               # 12 个数据采集器
├── kit/                      # CLI 工具集
├── examples/                 # 3 个完整示例
└── docs/                     # 调研综述 + 平台指南
```

---

## 设计哲学

| 原则 | 做法 |
|------|------|
| **分路蒸馏** | 四维独立提取，按角色组合 |
| **证据分级** | verbatim > artifact > impression，不混淆 |
| **伦理先行** | 每个角色有对应的知情同意和脱敏要求 |
| **多源融合** | 12+ 平台统一接口，corpus 格式一致 |
| **版本可回退** | 快照机制，纠错后一键回滚 |
| **渐进披露** | SKILL.md 极短，详情按需加载 |

---

<div align="center">

## 人会走，记忆会模糊，聊天记录会沉底。

## 但如果有一种方式，能让 TA 的「样子」留下来呢？

<br/>

**⭐ Star 这个项目，让更多人的记忆不被遗忘。**

<br/>

MIT License · [调研综述](docs/RESEARCH.md) · [平台数据获取指南](docs/PLATFORM-GUIDE.md)

</div>

---

<a name="english"></a>

<details>
<summary><b>English</b></summary>

## immortal-skill

A universal digital immortality framework — distill **anyone's** digital persona from chat logs, social media, and documents across 12+ platforms.

**7 persona templates**: Self, Colleague, Mentor, Family, Partner/Ex, Friend, Public Figure

**4 distillation dimensions**: Procedural knowledge, Interaction style, Memories & experiences, Personality & values

**Evidence grading**: verbatim > artifact > impression, with explicit conflict tracking

**Role-based ethics**: Different consent and anonymization requirements per relationship type

**Output format**: [Agent Skills](https://agentskills.io/) standard, compatible with [OpenClaw](https://docs.openclaw.ai/)

</details>
