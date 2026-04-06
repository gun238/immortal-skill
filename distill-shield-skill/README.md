# Distill Shield · 资料加固

在**你有权处置的资料包**里加入 **Canary（金丝雀）**、可选 **策略段落**，提高未授权自动化蒸馏的成本，并在泄露时留下可检测痕迹。

**不是**绝对防御，也**不是**鼓励对他人的恶意投毒。详见 [`SKILL.md`](SKILL.md)。

**从仓库根运行**（推荐，与 [`FOR_AI.md`](../FOR_AI.md) 一致）：

```bash
python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "我的移交包"
```

## 给 AI 的一句话

```
工作目录在仓库根。请读 distill-shield-skill/SKILL.md；生成 Canary 时执行：python3 distill-shield-skill/kit/shield_gen.py --output ./handover-bundle --label "我的移交包"
```
