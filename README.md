# immortal-skill

通用数字永生框架——从聊天记录、社交媒体、文档等多平台数据中蒸馏**任何人**的数字分身，生成符合 [Agent Skills](https://agentskills.io/) 规范的技能包，开箱即用于 [OpenClaw](https://docs.openclaw.ai/)。

## 为什么做这个

2026 年，「被蒸馏成 Token」已从段子变成现实。但现有的数字永生/蒸馏方案存在明显问题：

- 只面向职场同事，无法覆盖亲人、伴侣、导师等场景
- 数据源单一，不支持跨平台采集
- 缺乏伦理框架——辅助回忆 vs 冒充真人的边界模糊
- 粗放向量化，无法区分事实与印象、处理冲突

`immortal-skill` 解决这些问题。

## 核心特性

### 7 种角色模板

| 角色 | 核心维度 | 适用场景 |
|------|---------|---------|
| 自己 | 全维度（procedure + interaction + memory + personality） | 数字分身、个人备份 |
| 同事 | procedure + interaction | 团队知识传承 |
| 导师 | interaction + memory + personality + procedure | 教学智慧延续 |
| 亲人 | memory + personality + interaction | 家族记忆、数字留念 |
| 伴侣/前任 | interaction + memory + personality | 关系记忆 |
| 朋友 | interaction + memory + personality | 友谊互动 |
| 公众人物 | personality + interaction + procedure + memory | 公开风格学习 |

### 12+ 数据平台

| 类型 | 平台 |
|------|------|
| API 实时拉取 | 飞书、钉钉、Slack、Discord、Telegram、Email (Gmail) |
| 本地数据库 | 微信（SQLite）、iMessage（macOS chat.db） |
| 归档文件 | WhatsApp、Twitter/X、Google Takeout、Facebook |
| 手动导入 | 粘贴、TXT、JSON、CSV、Markdown |

### 4 维蒸馏

- **程序性知识**（procedure）：怎么做事
- **互动风格**（interaction）：怎么说话、怎么回应
- **记忆与经历**（memory）：经历过什么、记得什么故事
- **性格与价值观**（personality）：是什么样的人、在乎什么

### 证据分级 + 冲突处理

- `verbatim`（原话）> `artifact`（文档）> `impression`（印象）
- 矛盾项显式记录，不静默覆盖

### 按角色的伦理框架

- 同事/导师：限定内部培训用途
- 亲人（已故）：家人知情确认
- 伴侣/前任：正面回忆目的确认、严格脱敏
- 公众人物：仅限公开资料

## 安装（OpenClaw）

```bash
# 安装到当前工作区
cp -r immortal-skill <工作区>/skills/immortal-skill

# 或安装到全局
cp -r immortal-skill ~/.openclaw/skills/immortal-skill
```

重启 session 后验证：
```bash
openclaw skills list | grep immortal-skill
```

## 使用方式

在 OpenClaw 对话中说「蒸馏某人」「做数字分身」「保留 XX 的方式」即可触发。

### CLI 辅助

```bash
# 查看支持的平台
python3 kit/immortal_cli.py platforms

# 配置平台凭证
python3 kit/immortal_cli.py setup feishu
python3 kit/immortal_cli.py setup dingtalk
python3 kit/immortal_cli.py setup telegram

# 采集数据
python3 kit/immortal_cli.py collect --platform feishu --scan --keyword "项目组"
python3 kit/immortal_cli.py collect --platform feishu --channel oc_xxx --output corpus/msg.md
python3 kit/immortal_cli.py collect --platform wechat --db ~/wechat.db --channel "张三" --output corpus/wechat.md
python3 kit/immortal_cli.py collect --platform imessage --scan
python3 kit/immortal_cli.py collect --platform telegram --channel "好友群" --output corpus/tg.md

# 导入本地文件
python3 kit/immortal_cli.py import ~/Downloads/chat-export.txt --output corpus/import.md

# 初始化 skill 目录
python3 kit/immortal_cli.py init --slug wang-wu --persona colleague
python3 kit/immortal_cli.py init --slug my-clone --persona self

# 封包登记
python3 kit/immortal_cli.py stamp --slug wang-wu --sources "feishu:chat,paste:notes"

# 版本管理
python3 kit/immortal_cli.py snapshot --slug wang-wu --note "v1"
python3 kit/immortal_cli.py list-snapshots --slug wang-wu
python3 kit/immortal_cli.py rollback --slug wang-wu --tag v1
```

## 目录结构

```
immortal-skill/
├── SKILL.md                    # 蒸馏器入口（meta skill）
├── personas/                   # 7 种角色模板
│   ├── _base.md               #   通用基座维度
│   ├── self.md                #   自己
│   ├── colleague.md           #   同事
│   ├── mentor.md              #   导师
│   ├── family.md              #   亲人
│   ├── partner.md             #   伴侣/前任
│   ├── friend.md              #   朋友
│   └── public-figure.md       #   公众人物
├── recipes/                    # 方法论配方
│   ├── intake-protocol.md     #   多平台数据源路由
│   ├── procedural-mining.md   #   程序性知识挖掘
│   ├── interaction-mining.md  #   互动风格挖掘
│   ├── memory-mining.md       #   记忆经历挖掘
│   ├── personality-mining.md  #   性格价值观挖掘
│   ├── merge-policy.md        #   合并与冲突策略
│   └── output-contract.md     #   生成物目录约定
├── prompts/                    # Prompt 模板
│   ├── procedural-extractor.md
│   ├── interaction-extractor.md
│   ├── memory-extractor.md
│   ├── personality-extractor.md
│   ├── skill-assembler.md
│   └── correction-handler.md
├── collectors/                 # 12 个数据采集器
│   ├── base.py                #   统一接口基类
│   ├── feishu.py / dingtalk.py / wechat.py
│   ├── imessage.py / telegram.py / whatsapp.py
│   ├── slack.py / discord.py / email_collector.py
│   ├── twitter.py / social_archive.py / manual.py
│   └── __init__.py
├── kit/                        # CLI 工具
│   ├── immortal_cli.py        #   统一入口
│   ├── manifest_tool.py       #   目录初始化与指纹
│   └── version_tool.py        #   快照与回滚
├── examples/                   # 完整示例
│   ├── li-gong-demo/          #   同事（colleague）
│   ├── self-demo/             #   自己（self）—— 全维度
│   └── mentor-demo/           #   导师（mentor）
├── docs/
│   ├── RESEARCH.md            #   调研综述
│   └── PLATFORM-GUIDE.md      #   各平台数据获取指南
├── generated/                  # 输出目录（gitignore）
├── LICENSE
└── .gitignore
```

## 设计原则

1. **分路蒸馏**：按维度独立提取，按需组合
2. **证据分级**：`verbatim` > `artifact` > `impression`，三级分离
3. **渐进式披露**：SKILL.md 极短，详情按需加载
4. **角色适配**：不同关系类型有不同的维度组合与伦理要求
5. **多源融合**：12+ 平台统一接口，corpus 格式一致
6. **资产可溯**：manifest.json 记录来源、时间、指纹
7. **版本可回退**：快照机制支持纠正后回滚
8. **伦理先行**：每个角色有对应的伦理声明与脱敏要求

## 许可

MIT，见 [LICENSE](LICENSE)。
