<div align="center">

# Distill Protocol · 蒸馏协议

### 你的数字碎片，也值得有一份「使用说明书」。

### 开源项目有 LICENSE，你的记忆和文档也可以有。

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![执行入口](https://img.shields.io/badge/执行入口-SKILL.md-orange.svg)](SKILL.md)
[![FOR_AI](https://img.shields.io/badge/FOR_AI-第四节-blue.svg)](../FOR_AI.md)

</div>

<div align="center">

**戏称「牛马保护法」——梗，带引号，不是真立法。**

**正式名还是：蒸馏协议。**

</div>

---

<div align="center">

[为啥要协议](#为啥要蒸馏协议) · [牛马保护法是啥](#牛马保护法是个啥) · [档位一览](#档位一览) · [产出啥文件](#产出啥文件) · [怎么跑](#从仓库根运行) · [和谁搭](#和四件套里谁搭) · [给 AI](#给-ai的一句话)

</div>

---

## 为啥要蒸馏协议？

法律对「个人数据被拿去训模型、被蒸馏成假的我」还在慢慢长——**但你可以先表态**。

**Distill Protocol** 帮你生成两样东西：

1. **人类能读的** `LICENSE-DISTILL.md`：写清楚「允许怎么用、禁止怎么用、要不要署名」。
2. **机器能读的** `manifest.json`：给以后的工具、爬虫策略、你自己的脚本一个 **结构化信号**。

形态上像 **开源协议 + 个人数据贴纸**：**不是**替律师出庭，**是**把 **意愿写清楚、留痕、可引用**——以后真扯皮，至少你说过不。

---

## 「牛马保护法」是个啥？

圈里自嘲的一句梗：**带引号**，表示「我也想给自己的数字劳动留点尊严」——**没有立法效力，没有执法机关**，别当真成「法」。

正式称呼永远是：**蒸馏协议 / Distill Protocol**。  
[`SKILL.md`](SKILL.md) 里该严肃的地方（免责声明、非法律意见）一句不会少。

---

## 档位一览

运行 `protocol_gen.py` 时用 `--tier` 选择（详见 [`SKILL.md`](SKILL.md) 完整表）：

| 档位 | 人话 |
|------|------|
| `human_only` | **只给人看**，别拿我的包去训模型、别自动化蒸馏人格 |
| `no_commercial_distill` | 个人学习可以，**别拿蒸馏结果赚钱** |
| `research_ok` | **研究向**可以，商用不行；希望署名 |

以后可加自定义档；复杂授权 **请咨询律师**，本生成器只做 **模板级** 表达。

---

## 产出啥文件？

在输出目录（如 `./my-protocol/`）里 typically：

| 文件 | 干啥 |
|------|------|
| `LICENSE-DISTILL.md` | 给人看的条款 + 声明 |
| `manifest.json` | `allow_distillation`、`tier`、`owner` 等字段，给程序读 |

另附 [`templates/robots-snippet.txt`](templates/robots-snippet.txt) 思路：若你有**个人网站**，可把「别爬去训模型」写进 `robots.txt` / `llms.txt`——与协议 **互相引用**效果最好。

---

## 从仓库根运行

```bash
python3 distill-protocol-skill/kit/protocol_gen.py --owner "你的名字" --tier human_only --output ./my-protocol
```

`--tier`：`human_only` | `no_commercial_distill` | `research_ok`

生成后请 **人工读一遍** 条款；涉及 **合同、雇佣、遗产**，务必 **真人律师**过目。

---

## 和四件套里谁搭？

| 搭子 | 咋配合 |
|------|--------|
| **[Distill Shield](../distill-shield-skill/README.md)** | 协议写 **规矩**，Shield 给 **Canary / 技术附录**——「又立字据又挂锁」 |
| **[蒸笼 / 主蒸馏](../README.md)** | 协议管 **数据边界**，蒸馏管 **怎么从材料里长 Skill**——先想清楚再放料 |

推荐阅读顺序：**先 Protocol（立规矩）→ 再蒸馏 → 要交包再 Shield**。

---

## 给 AI 的一句话

```
工作目录在仓库根。请读 distill-protocol-skill/SKILL.md；生成协议时执行：python3 distill-protocol-skill/kit/protocol_gen.py --owner "你的名字" --tier human_only --output ./my-protocol
```

---

**迷路了？** 回 **[永生.skill 主 README](../README.md)** 或 **[FOR_AI.md](../FOR_AI.md)**。
