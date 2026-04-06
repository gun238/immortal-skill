<div align="center">

# 蒸馏协议.skill

### 开源项目有 LICENSE，你的记忆和文档凭什么没有？

### 戏称「牛马保护法」——梗，带引号，不是真立法。

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![执行入口](https://img.shields.io/badge/执行入口-SKILL.md-orange.svg)](SKILL.md)
[![FOR_AI](https://img.shields.io/badge/FOR_AI-第四节-blue.svg)](../FOR_AI.md)

</div>

<div align="center">

**法律还没管到这儿，不代表你不能先表态。**

**写清楚「我的东西能怎么用」，比事后扯皮强一百倍。**

</div>

---

<div align="center">

[为啥要这个](#为啥要蒸馏协议) · [「牛马保护法」](#牛马保护法是个啥) · [能选什么档位](#能选什么档位) · [怎么用](#怎么用) · [生成什么文件](#生成什么文件) · [和谁搭配](#和谁搭配) · [给 AI](#给-ai-的一句话)

</div>

---

## 为啥要蒸馏协议

你在互联网上留下了多少东西？

聊天记录、朋友圈、博客、笔记、代码注释、邮件、语音转文字——**这些全是你的数字碎片**。

2026 年了，这些碎片正在被各种管线吃进去：训练、微调、蒸馏、RAG——**你的说话方式可能已经在某个模型里了，你不知道而已。**

法律在追，但追得慢。GDPR 管欧洲的，美国还在打官司，国内更是灰色地带。

**等法律追上来之前，你至少可以先做一件事：把自己的态度写清楚。**

蒸馏协议帮你生成的东西很简单：

1. **一份人能读的声明**（`LICENSE-DISTILL.md`）：写清楚你的材料**能怎么用、不能怎么用**——能不能蒸馏、能不能训练、能不能商用、要不要署名。
2. **一份机器能读的清单**（`manifest.json`）：结构化字段，给以后的工具、爬虫策略、自动化流程一个信号。

**它不是律师函**，不保证全世界都听你的。但它是你的**意愿表达**——白纸黑字写过、文件带哈希记过、以后真扯皮了你说过「不」。有这个和没这个，差很远。

---

## 「牛马保护法」是个啥

圈里自嘲的一句话：我们这些给互联网贡献数据的人，是不是也该有点「保护法」？

**带引号**，表示这是梗、是态度、是自嘲——**不是真的立法，没有执法机关，没有法庭效力**。

正式名称始终是：**蒸馏协议 / Distill Protocol**。

[`SKILL.md`](SKILL.md) 里该写的免责声明一句不少。

---

## 能选什么档位

运行生成器时用 `--tier` 选：

| 档位 | 人话 |
|------|------|
| `human_only` | **只给人看**。别拿我的东西训模型，别自动化蒸馏人格。 |
| `no_commercial_distill` | 个人学习可以，**别拿蒸馏结果赚钱**。 |
| `research_ok` | 学术研究可以引用，**商用不行**，希望署名。 |

以后会加自定义档。复杂的授权场景——涉及合同、雇佣、遗产——**请找真人律师**，这个工具只做模板级表达。

---

## 怎么用

在仓库根目录执行：

```bash
python3 distill-protocol-skill/kit/protocol_gen.py --owner "你的名字" --tier human_only --output ./my-protocol
```

`--tier` 可选：`human_only` | `no_commercial_distill` | `research_ok`

跑完后请**人工读一遍**生成的条款。生成器帮你写初稿，但签字的是你。

---

## 生成什么文件

| 文件 | 干啥 |
|------|------|
| `LICENSE-DISTILL.md` | 人能读的协议：所有者、档位、条款、免责声明 |
| `manifest.json` | 机器能读的结构化数据：`allow_distillation`、`tier`、`commercial`… |

**建议**：把这两个文件和你的资料包放在**同一个目录**里。有网站的话，还可以参考 [`templates/robots-snippet.txt`](templates/robots-snippet.txt) 的思路在 `robots.txt` 里拒绝 AI 爬虫——和协议**互相引用**效果最好。

---

## 和谁搭配

| 搭子 | 怎么配合 |
|------|----------|
| **[防蒸馏](../distill-shield-skill/README.md)** | 协议是**规矩写在纸上**，Shield 是**包里塞技术标记**——又立字据又挂锁 |
| **[蒸笼 / 永生蒸馏器](../README.md)** | 蒸馏管「怎么产出分身」，协议管「我的材料能不能被拿去产出」——先想清楚再放料 |

**推荐顺序**：先 **蒸馏协议**（立规矩）→ 再决定要不要 **[蒸馏](../README.md)** 别人或被蒸 → 交包之前加 **[防蒸馏](../distill-shield-skill/README.md)** 标记。

---

<div align="center">

## 最后说句正经的。

你在网上说的每一句话、写的每一段字——

都是你的。

法律还没完全保护到，不代表你不能先**说清楚**。

<br/>

**⭐ Star 一下。下次有人拿你的数据去蒸馏的时候，至少你说过「不」。**

<br/>

回 **[永生.skill 主页](../README.md)** · **[给 AI 的一键入口](../FOR_AI.md)**

</div>

---

## 给 AI 的一句话

```
工作目录在 immortal-skill 仓库根。请读 distill-protocol-skill/SKILL.md 并按 Phase 执行；生成协议时运行：python3 distill-protocol-skill/kit/protocol_gen.py --owner "你的名字" --tier human_only --output ./my-protocol
```
