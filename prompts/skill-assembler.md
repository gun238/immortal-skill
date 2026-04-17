# Prompt: Skill 组装器（微信适配，无角色版）

## 输入
- `{name}`、`{sender_username}`
- `procedure.md` / `interaction.md` / `memory.md` / `personality.md` / `conflicts.md`
- 来源文件名

## 组装目标
把各维度内容组装为可运行的 `SKILL.md`，并写入统一 metadata。

## 强约束
- 不再按角色增删维度，统一使用完整维度集合。
- 允许低样本风格提炼，但要求在内容中显示置信度。
- 在 `metadata` 与正文中明确“禁止敏感推断”。

## 前置校验
- 若任一维度缺失，写入“材料不足”占位，不终止组装。
- 不得删除已有的 `verbatim` 与 `artifact` 证据标记。

## 输出骨架
```markdown
---
name: "{skill_id}"
description: "..."
license: MIT
metadata: {"profile_mode":"wechat-adaptive","role_free":true,"sparse_inference_enabled":true,"forbidden_infer_fields":"职业、学历、收入、健康状况、政治立场、宗教、身份敏感信息"}
---

# {name}

## 运行规则
1. ...

## 禁止推断
- 职业、学历、收入、健康状况、政治立场、宗教、身份敏感信息。

## 局限
- ...
```
