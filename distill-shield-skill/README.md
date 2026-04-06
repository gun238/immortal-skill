<div align="center">

# Distill Shield · 蒸馏盾

### 资料要交出去之前，先给自己加一层壳。

### 不是魔法盾，是「对方乱蒸你时得多付点成本」。

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![执行入口](https://img.shields.io/badge/执行入口-SKILL.md-orange.svg)](SKILL.md)
[![FOR_AI](https://img.shields.io/badge/FOR_AI-第三节-blue.svg)](../FOR_AI.md)

</div>

<div align="center">

**Canary 一埋，复制粘贴现形。**

**伦理红线一划，别拿毒包害人。**

</div>

---

<div align="center">

[为啥要盾](#为啥要这层盾) · [能防啥不能防啥](#能防啥不能防啥) · [里面有什么](#里面有什么) · [谁该用](#谁该用) · [怎么跑](#从仓库根运行) · [给 AI](#给-ai的一句话)

</div>

---

## 为啥要这层盾？

你要把 **聊天记录、笔记、作品集** 交给：**公司交接、律师、家人、合伙人**——只要对方可能用 **自动化管线**（上传即蒸馏、RAG 一塞就抽人格）处理你的东西，你就该多想一步：

- **你**还希望对方**当人看**；
- **机器**可能只想**当语料吃**。

**Distill Shield** 做的是：在**你有权处置**的资料包里，加入 **Canary（金丝雀）** 和可选 **策略段落**，让：

1. **未授权的批量蒸馏**更麻烦、更容易出垃圾结果；
2. 若内容被原样泄露到别处，你至少能 **搜 Canary 字符串** 做 **溯源线索**（不是铁证，是线索）。

**它不是**国家安全级加密，**不是**鼓励你对别人的硬盘下毒——**只服务「自己的包、自己签字交出去」的场景。详见 [`SKILL.md`](SKILL.md) 伦理红线。

---

## 能防啥不能防啥

| | 能帮你 | 别指望 |
|---|--------|--------|
| **态度** | 提高胡搞成本、留下检测线索 | 挡住决心极大的人工抄写 |
| **技术** | Canary、清单、可选干扰段落 | 数学上「绝对不可蒸馏」 |
| **法律** | 配合你的协议与证据意识 | 替代律师函 |

诚实讲：**军备竞赛永远存在**；盾的价值是 **意愿表达 + 成本 + 可追溯性**，不是玄学。

---

## 里面有什么

| 组件 | 干啥 |
|------|------|
| **[`SKILL.md`](SKILL.md)** | Agent 完整 Phase：威胁模型 → 盘点 → 选策略 → 生成 → 自检 |
| **`kit/shield_gen.py`** | 生成 `CANARY.txt` + `SHIELD-MANIFEST.json`（标准库，无额外依赖） |
| **[`recipes/shield-flow.md`](recipes/shield-flow.md)** | 人类可读的流程摘要 |

生成物里 **Canary** 是一串唯一标识：出现在奇怪的地方时，提醒你「这坨可能从我这儿流出去的」。

---

## 谁该用

- **要离职交接**的你：盘里一文件夹，想标明「别喂模型」。
- **立遗嘱式数字遗产**：给继承人一份带技术附录的包。
- **创作者**：作品 zip 外再挂一层「别蒸馏」的声明 + Canary（和 **Distill Protocol** 一起用更完整）。

**不该用**：对**别人的**数据搞恶意投毒——本仓库 **不教、不支持**。

---

## 从仓库根运行

与 **[`FOR_AI.md`](../FOR_AI.md)** 第三节一致（**推荐**，路径最不容易错）：

```bash
python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "我的移交包"
```

会在 `./handover-bundle/` 下生成 `CANARY.txt` 与 `SHIELD-MANIFEST.json`。再把它们**合并进你真正要交的目录**，并按 [`SKILL.md`](SKILL.md) 做自检。

---

## 和四件套里谁搭？

| 搭子 | 咋配合 |
|------|--------|
| **[Distill Protocol](../distill-protocol-skill/README.md)** | 先 **立规矩**（能不能蒸、能不能商用），再 **Shield** 做技术附录 |
| **[蒸笼 / 主蒸馏](../README.md)** | 盾管 **交出**，蒸馏管 **生成**——别混成一件事 |

---

## 给 AI 的一句话

```
工作目录在仓库根。请读 distill-shield-skill/SKILL.md；生成 Canary 时执行：python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "我的移交包"
```

---

**迷路了？** 回 **[永生.skill 主 README](../README.md)** 或 **[FOR_AI.md](../FOR_AI.md)**。
