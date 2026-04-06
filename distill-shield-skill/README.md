<div align="center">

# 防蒸馏.skill

### Distill Shield · 在要交出去的资料里，加一点「别被随便拿去蒸馏」的手段。

### 英文目录：`distill-shield-skill`，和上面说的是同一套东西。

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![执行入口](https://img.shields.io/badge/执行入口-SKILL.md-orange.svg)](SKILL.md)
[![FOR_AI](https://img.shields.io/badge/FOR_AI-第三节-blue.svg)](../FOR_AI.md)

</div>

<div align="center">

**交出去之前，给自己留一条能查的线。**

**Canary 是线索，不是保险箱；别指望靠这个挡掉全世界。**

</div>

---

<div align="center">

[防蒸馏是啥](#防蒸馏是啥) · [用得上的时候](#你可能用得上的时候) · [包里有什么](#仓库里和防蒸馏相关的东西) · [怎么用](#怎么用在仓库根目录执行) · [别和啥混](#和别的东西别混) · [给 AI](#给-ai的一句话复制)

</div>

---

## 防蒸馏是啥

「蒸馏」在咱们这个项目里，指的是：把聊天记录、文档、笔记里的说话方式抽出来，做成 AI 能用的数字分身。**防蒸馏**不是反对技术本身，而是针对一种情况——**你的材料已经要给别人了**（离职交接、给家人、给律师、合作方），你担心对方或下游把整包东西**直接丢进自动化流程里抽人格、训模型**，你又没法全程盯着。

这个 Skill 帮你做的事很具体：

1. **生成 Canary（金丝雀字符串）**：一长串唯一标记，塞进资料包里。以后若在不该出现的地方搜到这串字，至少说明**内容可能从你这包流出去的**，方便你对质或取证（不是法庭铁证，是线索）。
2. **可选**：在文档里加一些**对机器不友好、对人可读性影响可控**的段落（怎么加、加多重，看 [`SKILL.md`](SKILL.md) 里的 Phase，别瞎搞）。

**做不到的事**：加密到别人完全打不开、或者保证「全世界没有任何模型能学你」——做不到，也不吹这个牛。**只对「你有权处置」的材料用**；拿这个去祸害别人的数据，不在讨论范围内。

---

## 你可能用得上的时候

- 离职前整理硬盘，要交给公司的文件夹，你想留一手「别当免费语料」。
- 给家人的数字遗产包，你希望继承人**当文档读**，而不是被某个 App 一键「蒸」了。
- 已经和 **[蒸馏协议](../distill-protocol-skill/README.md)** 写清楚规矩了，还想在文件层面**多一层技术标记**。

---

## 仓库里和防蒸馏相关的东西

| 文件 | 干什么 |
|------|--------|
| [`SKILL.md`](SKILL.md) | 给 AI 用的完整流程：先想清楚威胁模型，再生成、再自检。 |
| [`kit/shield_gen.py`](kit/shield_gen.py) | 命令行生成 `CANARY.txt` 和 `SHIELD-MANIFEST.json`，Python 标准库就够。 |
| [`recipes/shield-flow.md`](recipes/shield-flow.md) | 给人看的步骤摘要。 |

---

## 怎么用（在仓库根目录执行）

先 `cd` 到克隆下来的 **`immortal-skill` 根目录**，再跑：

```bash
python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "移交包说明"
```

生成的文件在 `./handover-bundle/` 里，你再按 [`SKILL.md`](SKILL.md) 合并进真正要交付的目录。更省事的一键说明见 **[`FOR_AI.md`](../FOR_AI.md)** 第三节。

---

## 和别的东西别混

- **防蒸馏**只管「这包材料交出去之前怎么加固」。
- **蒸馏**（根目录 [`SKILL.md`](../SKILL.md)、[蒸笼](../steamer-skill/README.md)）是「怎么从材料里蒸出分身」——两码事。
- **蒸馏协议**是「规矩写在纸上」；防蒸馏是「包里塞标记」——经常一起用，但不是同一个文件。

---

## 给 AI 的一句话（复制）

```
工作目录在 immortal-skill 仓库根。请严格按 distill-shield-skill/SKILL.md 执行；需要生成 Canary 时运行：python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "我的移交包"
```

---

更多见 **[永生.skill 主 README](../README.md)**。
