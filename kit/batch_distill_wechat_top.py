#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch distill top WeChat senders into immortal-skill packages.

Wechat-adaptive principles:
1) No role/persona restrictions.
2) Even with sparse chat material, infer style/tone dimensions with confidence marks.
3) Never infer occupation/education/income/health/political stance from chat style.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
CLI_PATH = SCRIPT_DIR / "immortal_cli.py"

CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
TOKEN_RE = re.compile(r"[\u4e00-\u9fffA-Za-z0-9_@#]{2,}")
SLUG_SAFE_RE = re.compile(r"[^a-z0-9]+")
INVALID_FILE_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF]")

NOISE_PATTERNS = (
    "发起了群收款",
    "请点击升级至最新版",
    "如需收钱，请点击升级至最新版",
    "濡傞渶鏀堕挶锛岃鐐瑰嚮鍗囩骇鑷虫渶鏂扮増",
    "璇风偣鍑诲崌绾ц嚦鏈€鏂扮増",
    "鍙戣捣浜嗙兢鏀舵",
)

STOPWORDS = {
    "这个",
    "那个",
    "我们",
    "你们",
    "他们",
    "真的",
    "现在",
    "可以",
    "还是",
    "但是",
    "然后",
    "已经",
    "一个",
    "没有",
    "不是",
    "谢谢",
    "好的",
    "哈哈",
    "然后",
    "就是",
}

AFFIRM_WORDS = ("好", "好的", "行", "可以", "收到", "明白", "ok", "OK", "没问题", "安排")
CAUTIOUS_WORDS = ("可能", "也许", "大概", "先看看", "再说", "不确定", "先试试")
BOUNDARY_WORDS = ("不想", "算了", "别", "不要", "不方便", "先这样", "晚点", "改天", "不聊", "不说")
ACTION_WORDS = ("我来", "我先", "我去", "我弄", "我处理", "我看看", "安排", "推进", "回头", "跟进")
POLITE_WORDS = ("谢谢", "麻烦", "辛苦", "请", "拜托")
POS_WORDS = ("开心", "高兴", "哈哈", "笑死", "赞", "棒", "好耶", "太好了")
NEG_WORDS = ("烦", "无语", "崩溃", "生气", "难受", "算了", "服了", "累")

FORBIDDEN_INFER_FIELDS = "职业、学历、收入、健康状况、政治立场、宗教、身份敏感信息"


def run_cmd(cmd: List[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def clean_text(text: str) -> str:
    if not text:
        return ""
    t = CTRL_RE.sub("", text).strip()
    if not t:
        return ""
    for pattern in NOISE_PATTERNS:
        if pattern in t:
            return ""
    return t


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_top_senders(stats_csv: Path, top_n: int) -> List[Dict[str, str]]:
    return read_csv_rows(stats_csv)[:top_n]


def load_dataset_map(path: Path) -> Dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_dt(v: str) -> dt.datetime | None:
    if not v:
        return None
    try:
        return dt.datetime.fromisoformat(v)
    except Exception:
        return None


def read_sender_rows(dataset_csv: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for row in read_csv_rows(dataset_csv):
        row["text"] = clean_text(row.get("text", ""))
        if row["text"]:
            rows.append(row)
    rows.sort(key=lambda r: r.get("datetime", ""))
    return rows


def slug_from_sender(sender: str, used: set[str]) -> str:
    base = sender.lower().strip()
    base = SLUG_SAFE_RE.sub("-", base).strip("-")
    if not base:
        base = "unknown"
    slug = f"wx-{base}"
    if slug not in used:
        used.add(slug)
        return slug
    i = 2
    while f"{slug}-{i}" in used:
        i += 1
    slug = f"{slug}-{i}"
    used.add(slug)
    return slug


def sanitize_dir_name(name: str) -> str:
    n = INVALID_FILE_CHARS_RE.sub("_", (name or "").strip())
    n = n.rstrip(". ").strip()
    return n or "未命名"


def unique_name(base: str, used: set[str]) -> str:
    if base not in used:
        used.add(base)
        return base
    i = 2
    while f"{base}_{i}" in used:
        i += 1
    out = f"{base}_{i}"
    used.add(out)
    return out


def contains_any(text: str, words: Iterable[str]) -> bool:
    return any(w in text for w in words)


def ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count * 100.0 / total, 2)


def top_tokens(rows: List[Dict[str, str]], n: int = 15) -> List[Tuple[str, int]]:
    c = Counter()
    for row in rows:
        for tok in TOKEN_RE.findall(row["text"]):
            if tok.isdigit() or tok in STOPWORDS:
                continue
            if len(tok) == 1 or len(tok) > 24:
                continue
            c[tok] += 1
    return c.most_common(n)


def top_endings(rows: List[Dict[str, str]], n: int = 10) -> List[Tuple[str, int]]:
    c = Counter()
    for row in rows:
        t = row["text"]
        for k in (2, 3, 4):
            if len(t) >= k:
                c[t[-k:]] += 1
    return c.most_common(n)


def choose_quotes(rows: List[Dict[str, str]], n: int = 10) -> List[Dict[str, str]]:
    picked: List[Dict[str, str]] = []
    seen = set()
    for row in rows:
        t = row["text"].replace("\n", " ").strip()
        if len(t) < 3 or len(t) > 100:
            continue
        if t in seen:
            continue
        seen.add(t)
        picked.append(row)
        if len(picked) >= n:
            break
    return picked


def session_top(rows: List[Dict[str, str]], n: int = 8) -> List[Tuple[str, int]]:
    c = Counter()
    for row in rows:
        s = (row.get("session_display_name") or "").strip() or (row.get("session_username") or "").strip()
        c[s] += 1
    return c.most_common(n)


def hour_top(rows: List[Dict[str, str]], n: int = 4) -> List[Tuple[int, int]]:
    c = Counter()
    for row in rows:
        d = parse_dt(row.get("datetime", ""))
        if d:
            c[d.hour] += 1
    return c.most_common(n)


def confidence_level(msg_count: int) -> str:
    if msg_count >= 400:
        return "高"
    if msg_count >= 120:
        return "中"
    if msg_count >= 30:
        return "低"
    return "很低"


def style_signals(rows: List[Dict[str, str]]) -> Dict[str, float]:
    texts = [r["text"] for r in rows]
    total = len(texts)
    lengths = [len(t) for t in texts]
    q_count = sum(1 for t in texts if "?" in t or "？" in t or contains_any(t, ("吗", "么", "呢", "怎么", "为何", "为什么")))
    e_count = sum(1 for t in texts if "!" in t or "！" in t)
    emoji_count = sum(1 for t in texts if EMOJI_RE.search(t))
    ellipsis_count = sum(1 for t in texts if "..." in t or "…" in t)
    affirm_count = sum(1 for t in texts if contains_any(t, AFFIRM_WORDS))
    cautious_count = sum(1 for t in texts if contains_any(t, CAUTIOUS_WORDS))
    boundary_count = sum(1 for t in texts if contains_any(t, BOUNDARY_WORDS))
    action_count = sum(1 for t in texts if contains_any(t, ACTION_WORDS))
    polite_count = sum(1 for t in texts if contains_any(t, POLITE_WORDS))
    pos_count = sum(1 for t in texts if contains_any(t, POS_WORDS))
    neg_count = sum(1 for t in texts if contains_any(t, NEG_WORDS))
    self_ref_count = sum(1 for t in texts if "我" in t)
    other_ref_count = sum(1 for t in texts if "你" in t or "您" in t)
    short_count = sum(1 for x in lengths if x <= 10)

    return {
        "message_count": total,
        "avg_len": round(sum(lengths) / total, 2) if total else 0.0,
        "median_len": int(statistics.median(lengths)) if lengths else 0.0,
        "short_ratio": ratio(short_count, total),
        "question_ratio": ratio(q_count, total),
        "exclaim_ratio": ratio(e_count, total),
        "emoji_ratio": ratio(emoji_count, total),
        "ellipsis_ratio": ratio(ellipsis_count, total),
        "affirm_ratio": ratio(affirm_count, total),
        "cautious_ratio": ratio(cautious_count, total),
        "boundary_ratio": ratio(boundary_count, total),
        "action_ratio": ratio(action_count, total),
        "polite_ratio": ratio(polite_count, total),
        "pos_ratio": ratio(pos_count, total),
        "neg_ratio": ratio(neg_count, total),
        "self_ref_ratio": ratio(self_ref_count, total),
        "other_ref_ratio": ratio(other_ref_count, total),
    }


def infer_style_bullets(signals: Dict[str, float], cfd: str) -> List[str]:
    bullets: List[str] = []
    avg_len = signals["avg_len"]
    short_ratio = signals["short_ratio"]
    q_ratio = signals["question_ratio"]
    exclaim_ratio = signals["exclaim_ratio"]
    emoji_ratio = signals["emoji_ratio"]
    affirm_ratio = signals["affirm_ratio"]
    cautious_ratio = signals["cautious_ratio"]
    action_ratio = signals["action_ratio"]
    boundary_ratio = signals["boundary_ratio"]
    polite_ratio = signals["polite_ratio"]
    pos_ratio = signals["pos_ratio"]
    neg_ratio = signals["neg_ratio"]

    # 对话推进方式
    if short_ratio >= 65:
        bullets.append(f"- 对话推进偏向短句与快节奏确认（置信:{cfd}，`artifact`）")
    elif avg_len >= 26:
        bullets.append(f"- 对话推进偏向完整句解释与上下文补充（置信:{cfd}，`artifact`）")
    else:
        bullets.append(f"- 对话推进在短确认与简述之间切换（置信:{cfd}，`artifact`）")

    if q_ratio >= 35:
        bullets.append(f"- 提问密度高，常通过追问推进信息澄清（置信:{cfd}，`artifact`）")
    elif q_ratio <= 10:
        bullets.append(f"- 提问密度较低，更常直接给出判断/结论（置信:{cfd}，`artifact`）")
    else:
        bullets.append(f"- 提问与陈述较平衡，既会确认也会直接表达（置信:{cfd}，`artifact`）")

    # 情绪与语气
    if exclaim_ratio >= 22 or emoji_ratio >= 20:
        bullets.append(f"- 情绪外显度偏高，常用感叹号或表情强化语气（置信:{cfd}，`artifact`）")
    else:
        bullets.append(f"- 情绪外显度偏克制，更多用文本语义而非强符号表达（置信:{cfd}，`artifact`）")

    if pos_ratio >= neg_ratio + 8:
        bullets.append(f"- 积极反馈信号明显多于负向表达（置信:{cfd}，`artifact`）")
    elif neg_ratio >= pos_ratio + 8:
        bullets.append(f"- 负向情绪词出现更频繁，压力/不满表达更直接（置信:{cfd}，`artifact`）")
    else:
        bullets.append(f"- 正负情绪表达相对均衡，语气受语境影响较大（置信:{cfd}，`artifact`）")

    # 行动/决策倾向
    if action_ratio >= cautious_ratio + 8:
        bullets.append(f"- 更偏“先处理再反馈”的行动型表达（置信:{cfd}，`artifact`）")
    elif cautious_ratio >= action_ratio + 8:
        bullets.append(f"- 更偏“先评估再行动”的谨慎型表达（置信:{cfd}，`artifact`）")
    else:
        bullets.append(f"- 行动推进与谨慎评估并存（置信:{cfd}，`artifact`）")

    if affirm_ratio >= 28:
        bullets.append(f"- 高频确认词显示出较强的协作回应倾向（置信:{cfd}，`artifact`）")

    # 社交边界
    if boundary_ratio >= 10:
        bullets.append(f"- 边界提示语出现较多，存在明确“停止/延后”策略（置信:{cfd}，`artifact`）")
    if polite_ratio >= 12:
        bullets.append(f"- 礼貌缓冲词使用较多，倾向降低对话摩擦（置信:{cfd}，`artifact`）")
    elif polite_ratio <= 3:
        bullets.append(f"- 礼貌缓冲词较少，表达更直接（置信:{cfd}，`artifact`）")

    return bullets


def mk_interaction_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    signals = style_signals(rows)
    tokens = top_tokens(rows, 12)
    endings = top_endings(rows, 10)
    sessions = session_top(rows, 6)
    hours = hour_top(rows, 4)
    quotes = choose_quotes(rows, 10)
    cfd = confidence_level(len(rows))

    lines = [
        f"# 互动与语气：{display_name}",
        "",
        "## 统计轮廓",
        f"- 消息样本：{int(signals['message_count'])} 条（总体置信:{cfd}，`artifact`）",
        f"- 平均句长：{signals['avg_len']} 字，中位数：{signals['median_len']} 字（`artifact`）",
        f"- 短句占比：{signals['short_ratio']}%，提问占比：{signals['question_ratio']}%（`artifact`）",
        f"- 感叹占比：{signals['exclaim_ratio']}%，表情占比：{signals['emoji_ratio']}%（`artifact`）",
    ]
    if hours:
        lines.append("- 活跃时段：" + "、".join([f"{h}:00({c})" for h, c in hours]) + "（`artifact`）")
    if sessions:
        lines.append("- 高频会话：" + "、".join([f"{s}({c})" for s, c in sessions]) + "（`artifact`）")

    lines.extend(["", "## 风格归纳（微信适配）"])
    lines.extend(infer_style_bullets(signals, cfd))

    lines.extend(["", "## 高频表达"])
    if tokens:
        lines.append("- 高频词：" + "、".join([f"{t}({c})" for t, c in tokens]) + "（`artifact`）")
    if endings:
        lines.append("- 常见句尾：" + "、".join([f"{t}({c})" for t, c in endings]) + "（`artifact`）")

    lines.extend(["", "## 代表性原话"])
    if not quotes:
        lines.append("- 材料不足，暂无可引用原话。")
    for row in quotes:
        text = row["text"].replace("`", "")
        timestamp = row.get("datetime", "")
        session = (row.get("session_display_name") or row.get("session_username") or "").strip()
        lines.append(f"- “{text}” —— {timestamp} / {session}（`verbatim`）")

    return "\n".join(lines) + "\n"


def mk_memory_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    first = rows[0].get("datetime", "") if rows else ""
    last = rows[-1].get("datetime", "") if rows else ""
    month_counter = Counter()
    for row in rows:
        d = parse_dt(row.get("datetime", ""))
        if d:
            month_counter[d.strftime("%Y-%m")] += 1
    top_months = month_counter.most_common(6)
    sessions = session_top(rows, 8)
    tokens = top_tokens(rows, 10)
    cfd = confidence_level(len(rows))

    lines = [
        f"# 记忆线索：{display_name}",
        "",
        "## 时间与场景",
        f"- 语料覆盖区间：{first or '未知'} ~ {last or '未知'}（`artifact`）",
        f"- 样本量：{len(rows)}（总体置信:{cfd}，`artifact`）",
    ]
    if top_months:
        lines.append("- 活跃月份：" + "、".join([f"{m}({c})" for m, c in top_months]) + "（`artifact`）")
    if sessions:
        lines.append("- 主要会话场景：" + "、".join([f"{s}({c})" for s, c in sessions]) + "（`artifact`）")

    lines.extend(["", "## 可复用记忆锚点"])
    if tokens:
        lines.append("- 重复提及词：" + "、".join([f"{t}({c})" for t, c in tokens]) + "（`artifact`）")
    else:
        lines.append("- 材料不足，仅保留基础时间线索（`artifact`）。")

    lines.extend(
        [
            "",
            "## 低样本处理说明",
            "- 当样本偏少时，优先保留可观察线索，不补写不可验证事实。",
            f"- 禁止从当前语料推断：{FORBIDDEN_INFER_FIELDS}。",
        ]
    )
    return "\n".join(lines) + "\n"


def mk_personality_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    signals = style_signals(rows)
    tokens = top_tokens(rows, 18)
    endings = top_endings(rows, 12)
    quotes = choose_quotes(rows, 10)
    cfd = confidence_level(len(rows))

    lines = [
        f"# 性格与表达倾向：{display_name}",
        "",
        "## 稳定表达偏好（从语气反推）",
        f"- 确认表达占比：{signals['affirm_ratio']}%，谨慎表达占比：{signals['cautious_ratio']}%（`artifact`）",
        f"- 边界提示占比：{signals['boundary_ratio']}%，礼貌缓冲占比：{signals['polite_ratio']}%（`artifact`）",
        f"- 自指占比：{signals['self_ref_ratio']}%，对他者指向占比：{signals['other_ref_ratio']}%（`artifact`）",
    ]

    lines.extend(["", "## 维度提炼（可低样本推断，附置信）"])
    lines.extend(infer_style_bullets(signals, cfd))

    lines.extend(["", "## 语言标识"])
    if tokens:
        lines.append("- 高频词：" + "、".join([f"{t}({c})" for t, c in tokens]) + "（`artifact`）")
    if endings:
        lines.append("- 句尾偏好：" + "、".join([f"{t}({c})" for t, c in endings]) + "（`artifact`）")

    lines.extend(
        [
            "",
            "## 安全边界",
            f"- 本画像禁止推断：{FORBIDDEN_INFER_FIELDS}。",
            "- 仅从聊天语气/措辞/互动节奏提炼行为倾向，不作为现实身份认定。",
        ]
    )

    lines.extend(["", "## 原话样本"])
    if not quotes:
        lines.append("- 材料不足，暂无可引用原话。")
    for row in quotes:
        lines.append(f"- “{row['text'].replace('`', '')}”（`verbatim`）")
    return "\n".join(lines) + "\n"


def mk_procedure_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    signals = style_signals(rows)
    cfd = confidence_level(len(rows))
    lines = [
        f"# 程序性知识：{display_name}",
        "",
        "## 沟通执行流程（微信语料推断）",
    ]

    if signals["question_ratio"] >= 25:
        lines.append(f"- 步骤1：先提问澄清边界与上下文（置信:{cfd}，`artifact`）")
    else:
        lines.append(f"- 步骤1：先给出简要结论/态度，再补充细节（置信:{cfd}，`artifact`）")

    if signals["action_ratio"] >= signals["cautious_ratio"]:
        lines.append(f"- 步骤2：快速推进可执行项，后续补反馈（置信:{cfd}，`artifact`）")
    else:
        lines.append(f"- 步骤2：先评估风险与可行性，再进入执行（置信:{cfd}，`artifact`）")

    if signals["boundary_ratio"] >= 8:
        lines.append(f"- 步骤3：通过“延后/拒绝/改天”维持节奏边界（置信:{cfd}，`artifact`）")
    else:
        lines.append(f"- 步骤3：通过确认词收束任务闭环（置信:{cfd}，`artifact`）")

    lines.extend(
        [
            "",
            "## 使用提醒",
            "- 这是基于聊天行为的轻量流程画像，不等同于真实工作 SOP。",
            f"- 禁止从该流程画像推断：{FORBIDDEN_INFER_FIELDS}。",
        ]
    )
    return "\n".join(lines) + "\n"


def mk_conflicts_md(rows: List[Dict[str, str]]) -> str:
    signals = style_signals(rows)
    lines = ["# 待决冲突", ""]
    if signals["affirm_ratio"] >= 25 and signals["boundary_ratio"] >= 10:
        lines.append("- 观察到“高确认 + 高边界”并存：既愿意配合，也会在特定场景快速设限。")
        lines.append("- 解释优先级：视具体会话情境判定，不做单向人格标签化。")
    else:
        lines.append("- 当前样本未发现可稳定复现的显著冲突条目。")
    lines.append("- 建议后续引入跨平台语料后重新扫描冲突。")
    return "\n".join(lines) + "\n"


def count_tag(text: str, tag: str) -> int:
    return text.count(f"`{tag}`")


def mk_skill_md(
    skill_id: str,
    display_name: str,
    sender_username: str,
    interaction_md: str,
    memory_md: str,
    personality_md: str,
    procedure_md: str,
    dataset_csv: Path,
) -> str:
    iv = count_tag(interaction_md, "verbatim")
    ia = count_tag(interaction_md, "artifact")
    mv = count_tag(memory_md, "verbatim")
    ma = count_tag(memory_md, "artifact")
    pv = count_tag(personality_md, "verbatim")
    pa = count_tag(personality_md, "artifact")
    pr_v = count_tag(procedure_md, "verbatim")
    pr_a = count_tag(procedure_md, "artifact")
    evidence = f"interaction={iv}v+{ia}a; memory={mv}v+{ma}a; personality={pv}v+{pa}a; procedure={pr_v}v+{pr_a}a"
    metadata = {
        "ethics_note": "personal-memorial",
        "kit": "immortal-skill",
        "profile_mode": "wechat-adaptive",
        "role_free": True,
        "sparse_inference_enabled": True,
        "forbidden_infer_fields": FORBIDDEN_INFER_FIELDS,
        "evidence": evidence,
        "platforms": ["wechat"],
        "sender_username": sender_username,
        "dataset": str(dataset_csv),
    }
    meta_line = json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
    desc = f"基于微信聊天语料蒸馏 {display_name} 的互动风格、记忆线索与行为倾向。支持低样本风格提炼，不用于冒充。"

    return (
        "---\n"
        f'name: "{skill_id}"\n'
        f'description: "{desc}"\n'
        "license: MIT\n"
        f"metadata: {meta_line}\n"
        "---\n\n"
        f"# {display_name}\n\n"
        f"目标对象：`{sender_username}`\n\n"
        "## 运行规则\n\n"
        "1. 先读 `personality.md`，明确语气边界和禁推断项。\n"
        "2. 再读 `interaction.md`，对齐句长、节奏、提问方式与情绪外显度。\n"
        "3. 需要上下文时读 `memory.md`；需要流程偏好时读 `procedure.md`。\n"
        "4. 允许低样本下的风格提炼，但每条归纳须附“置信度”。\n"
        "5. 不得伪造可归因于真人的承诺、身份与经历。\n\n"
        "## 禁止推断\n\n"
        f"- 禁止根据当前语料推断：{FORBIDDEN_INFER_FIELDS}。\n"
        "- 禁止把语气特征直接等同为心理诊断或现实身份结论。\n\n"
        "## 局限\n\n"
        "- 语料以微信文本为主，缺少语音、线下语境与长期行为数据。\n"
        "- 低样本结论只能用于风格对齐，不可当作事实判断依据。\n"
    )


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def resolve_input_paths(args: argparse.Namespace) -> Tuple[Path, Path]:
    if args.stats_csv and args.dataset_map:
        return Path(args.stats_csv), Path(args.dataset_map)

    if args.summary_dir:
        summary_dir = Path(args.summary_dir)
        return summary_dir / "sender_stats.csv", summary_dir / "sender_dataset_map.json"

    candidates = [
        PROJECT_DIR / "distill_inputs" / "summary",
        PROJECT_DIR.parent / "fork-WeChatMsg" / "exports" / "weixin4" / "trainset" / "summary",
    ]
    for summary_dir in candidates:
        stats = summary_dir / "sender_stats.csv"
        dataset_map = summary_dir / "sender_dataset_map.json"
        if stats.exists() and dataset_map.exists():
            return stats, dataset_map

    raise FileNotFoundError(
        "Cannot locate sender_stats.csv and sender_dataset_map.json. "
        "Please pass --summary-dir, or both --stats-csv and --dataset-map."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch distill top WeChat senders into immortal-skill packages")
    parser.add_argument("--stats-csv", help="Path to sender_stats.csv")
    parser.add_argument("--dataset-map", help="Path to sender_dataset_map.json")
    parser.add_argument("--summary-dir", help="Directory containing sender_stats.csv and sender_dataset_map.json")
    parser.add_argument("--top-n", type=int, default=35, help="How many top senders to distill")
    parser.add_argument(
        "--min-messages",
        type=int,
        default=1,
        help="Skip sender if valid message count is below this (default 1: low-sample still allowed)",
    )
    parser.add_argument("--out-base", default=str(PROJECT_DIR / "skills" / "immortals"))
    parser.add_argument("--report-base", default=str(PROJECT_DIR / "distill_outputs"))
    parser.add_argument(
        "--dir-name-mode",
        default="nickname",
        choices=["slug", "nickname"],
        help="Final folder naming mode",
    )
    parser.add_argument("--note", default="batch_distill_wechat_top_wechat_adaptive")
    parser.add_argument("--force", action="store_true", help="Re-init existing skill folder when slug collides")
    parser.add_argument("--dry-run", action="store_true", help="Only print resolved input and planned output")
    args = parser.parse_args()

    stats_csv, dataset_map_path = resolve_input_paths(args)
    if not stats_csv.exists():
        raise FileNotFoundError(f"stats csv not found: {stats_csv}")
    if not dataset_map_path.exists():
        raise FileNotFoundError(f"dataset map not found: {dataset_map_path}")

    out_base = Path(args.out_base)
    out_base.mkdir(parents=True, exist_ok=True)

    top_rows = load_top_senders(stats_csv, args.top_n)
    dataset_map = load_dataset_map(dataset_map_path)

    used_skill_ids: set[str] = set()
    used_dir_names: set[str] = {p.name for p in out_base.iterdir() if p.is_dir()}
    distill_result = []
    rename_map = []

    for idx, row in enumerate(top_rows, start=1):
        sender = (row.get("sender_username") or "").strip()
        display_name = (row.get("sender_display_name") or "").strip() or sender
        dataset = dataset_map.get(sender)
        if not sender or not dataset:
            continue

        dataset_csv = Path(dataset)
        if not dataset_csv.is_absolute():
            dataset_csv = (dataset_map_path.parent / dataset_csv).resolve()
        if not dataset_csv.exists():
            continue

        rows = read_sender_rows(dataset_csv)
        if len(rows) < args.min_messages:
            continue

        skill_id = slug_from_sender(sender, used_skill_ids)
        final_dir_name = skill_id
        if args.dir_name_mode == "nickname":
            final_dir_name = unique_name(sanitize_dir_name(display_name), used_dir_names)
        else:
            used_dir_names.add(final_dir_name)

        if args.dry_run:
            distill_result.append(
                {
                    "rank": idx,
                    "skill_id": skill_id,
                    "dir_name": final_dir_name,
                    "sender_username": sender,
                    "sender_display_name": display_name,
                    "message_count": len(rows),
                    "confidence": confidence_level(len(rows)),
                    "dataset_csv": str(dataset_csv),
                    "skill_dir": str(out_base / final_dir_name),
                    "dry_run": True,
                }
            )
            continue

        init_cmd = [
            sys.executable,
            str(CLI_PATH),
            "init",
            "--slug",
            skill_id,
            "--base",
            str(out_base),
        ]
        if args.force:
            init_cmd.append("--force")
        run_cmd(init_cmd, PROJECT_DIR)

        skill_dir = out_base / skill_id
        interaction_md = mk_interaction_md(display_name, rows)
        memory_md = mk_memory_md(display_name, rows)
        personality_md = mk_personality_md(display_name, rows)
        procedure_md = mk_procedure_md(display_name, rows)
        conflicts_md = mk_conflicts_md(rows)
        skill_md = mk_skill_md(
            skill_id=skill_id,
            display_name=display_name,
            sender_username=sender,
            interaction_md=interaction_md,
            memory_md=memory_md,
            personality_md=personality_md,
            procedure_md=procedure_md,
            dataset_csv=dataset_csv,
        )

        write_text(skill_dir / "interaction.md", interaction_md)
        write_text(skill_dir / "memory.md", memory_md)
        write_text(skill_dir / "personality.md", personality_md)
        write_text(skill_dir / "procedure.md", procedure_md)
        write_text(skill_dir / "conflicts.md", conflicts_md)
        write_text(skill_dir / "SKILL.md", skill_md)

        stamp_cmd = [
            sys.executable,
            str(CLI_PATH),
            "stamp",
            "--slug",
            skill_id,
            "--base",
            str(out_base),
            "--sources",
            f"wechat:{dataset_csv.name}",
            "--note",
            args.note,
        ]
        run_cmd(stamp_cmd, PROJECT_DIR)

        final_skill_dir = skill_dir
        if final_dir_name != skill_id:
            target = out_base / final_dir_name
            if target.exists():
                raise RuntimeError(
                    f"Target directory exists: {target}. "
                    "Please remove it first, or switch --dir-name-mode slug."
                )
            skill_dir.rename(target)
            final_skill_dir = target
            rename_map.append({"skill_id": skill_id, "dir_name": final_dir_name, "display_name": display_name})

        distill_result.append(
            {
                "rank": idx,
                "skill_id": skill_id,
                "dir_name": final_dir_name,
                "sender_username": sender,
                "sender_display_name": display_name,
                "message_count": len(rows),
                "confidence": confidence_level(len(rows)),
                "dataset_csv": str(dataset_csv),
                "skill_dir": str(final_skill_dir),
            }
        )

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(args.report_base) / f"wechat_top{args.top_n}_{ts}"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_json = report_dir / "distill_manifest.json"
    report_csv = report_dir / "distill_manifest.csv"
    report_json.write_text(json.dumps(distill_result, ensure_ascii=False, indent=2), encoding="utf-8")

    with report_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "skill_id",
                "dir_name",
                "sender_username",
                "sender_display_name",
                "message_count",
                "confidence",
                "dataset_csv",
                "skill_dir",
            ]
        )
        for row in distill_result:
            writer.writerow(
                [
                    row["rank"],
                    row["skill_id"],
                    row["dir_name"],
                    row["sender_username"],
                    row["sender_display_name"],
                    row["message_count"],
                    row["confidence"],
                    row["dataset_csv"],
                    row["skill_dir"],
                ]
            )

    if rename_map:
        rename_map_csv = report_dir / "nickname_dir_map.csv"
        with rename_map_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["skill_id", "dir_name", "display_name"])
            for row in rename_map:
                writer.writerow([row["skill_id"], row["dir_name"], row["display_name"]])

    print(f"distilled_count={len(distill_result)}")
    print(f"stats_csv={stats_csv}")
    print(f"dataset_map={dataset_map_path}")
    print(f"out_base={out_base}")
    print(f"dir_name_mode={args.dir_name_mode}")
    print(f"report_json={report_json}")
    print(f"report_csv={report_csv}")


if __name__ == "__main__":
    main()
