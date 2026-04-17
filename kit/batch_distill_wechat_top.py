#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch distill top senders from WeChat CSV into immortal-skill packages.

Workflow:
1) init skill folder via immortal_cli.py
2) write interaction/memory/personality/conflicts/SKILL.md
3) stamp manifest via immortal_cli.py
4) optional rename folder to WeChat nickname
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
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
CLI_PATH = SCRIPT_DIR / "immortal_cli.py"

CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
TOKEN_RE = re.compile(r"[\u4e00-\u9fffA-Za-z0-9_@#]{2,}")
SLUG_SAFE_RE = re.compile(r"[^a-z0-9]+")
INVALID_FILE_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
NOISE_PATTERNS = (
    "发起了群收款",
    "请点击升级至最新版",
    "如需收钱，请点击升级至最新版",
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
}


def run_cmd(cmd: List[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = CTRL_RE.sub("", text).strip()
    if not text:
        return ""
    for pattern in NOISE_PATTERNS:
        if pattern in text:
            return ""
    return text


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_top_senders(stats_csv: Path, top_n: int) -> List[Dict[str, str]]:
    rows = read_csv_rows(stats_csv)
    return rows[:top_n]


def load_dataset_map(path: Path) -> Dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sender_rows(dataset_csv: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for row in read_csv_rows(dataset_csv):
        row["text"] = clean_text(row.get("text", ""))
        if row["text"]:
            rows.append(row)
    rows.sort(key=lambda r: r.get("datetime", ""))
    return rows


def parse_dt(v: str) -> dt.datetime | None:
    if not v:
        return None
    try:
        return dt.datetime.fromisoformat(v)
    except Exception:
        return None


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
    candidate = f"{base}_{i}"
    used.add(candidate)
    return candidate


def top_tokens(rows: List[Dict[str, str]], n: int = 12) -> List[Tuple[str, int]]:
    counter = Counter()
    for row in rows:
        for token in TOKEN_RE.findall(row["text"]):
            if token.isdigit() or token in STOPWORDS or len(token) == 1 or len(token) > 24:
                continue
            counter[token] += 1
    return counter.most_common(n)


def top_endings(rows: List[Dict[str, str]], n: int = 8) -> List[Tuple[str, int]]:
    counter = Counter()
    for row in rows:
        text = row["text"]
        for k in (2, 3, 4):
            if len(text) >= k:
                counter[text[-k:]] += 1
    return counter.most_common(n)


def choose_quotes(rows: List[Dict[str, str]], n: int = 8) -> List[Dict[str, str]]:
    seen = set()
    picked: List[Dict[str, str]] = []
    for row in rows:
        text = row["text"].replace("\n", " ").strip()
        if len(text) < 3 or len(text) > 80:
            continue
        if text in seen:
            continue
        seen.add(text)
        picked.append(row)
        if len(picked) >= n:
            break
    return picked


def session_top(rows: List[Dict[str, str]], n: int = 6) -> List[Tuple[str, int]]:
    counter = Counter()
    for row in rows:
        session = (row.get("session_display_name") or "").strip() or (row.get("session_username") or "").strip()
        counter[session] += 1
    return counter.most_common(n)


def hour_top(rows: List[Dict[str, str]], n: int = 3) -> List[Tuple[int, int]]:
    counter = Counter()
    for row in rows:
        d = parse_dt(row.get("datetime", ""))
        if d:
            counter[d.hour] += 1
    return counter.most_common(n)


def mk_interaction_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    lengths = [len(r["text"]) for r in rows]
    avg_len = round(sum(lengths) / len(lengths), 2) if lengths else 0
    med_len = int(statistics.median(lengths)) if lengths else 0
    short_ratio = round(sum(1 for x in lengths if x <= 10) * 100.0 / len(lengths), 2) if lengths else 0
    token_rows = top_tokens(rows)
    ending_rows = top_endings(rows)
    session_rows = session_top(rows)
    hour_rows = hour_top(rows)
    quotes = choose_quotes(rows)

    lines = [
        f"# 互动与语气：{display_name}",
        "",
        "## 沟通节奏",
        f"- 平均句长约 {avg_len} 字，中位数 {med_len} 字（`artifact`）",
        f"- 短句（<=10字）占比约 {short_ratio}%（`artifact`）",
    ]
    if hour_rows:
        lines.append("- 高频时段：" + "、".join([f"{h}:00({c})" for h, c in hour_rows]) + "（`artifact`）")
    lines.extend(["", "## 高频表达"])
    if token_rows:
        lines.append("- 高频词：" + "、".join([f"{t}({c})" for t, c in token_rows]) + "（`artifact`）")
    if ending_rows:
        lines.append("- 常见句尾：" + "、".join([f"{t}({c})" for t, c in ending_rows]) + "（`artifact`）")
    if session_rows:
        lines.append("- 高频会话：" + "、".join([f"{s}({c})" for s, c in session_rows]) + "（`artifact`）")
    lines.extend(["", "## 代表性原话"])
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
    session_rows = session_top(rows)

    lines = [
        f"# 记忆线索：{display_name}",
        "",
        f"- 语料覆盖区间：{first} ~ {last}（`artifact`）",
    ]
    if top_months:
        lines.append("- 活跃月份：" + "、".join([f"{m}({c})" for m, c in top_months]) + "（`artifact`）")
    if session_rows:
        lines.append("- 主要出现会话：" + "、".join([f"{s}({c})" for s, c in session_rows]) + "（`artifact`）")
    lines.extend(
        [
            "",
            "## 使用建议",
            "- 仅作为风格与记忆线索，不用于事实背书。",
            "- 涉及关键事实时需二次核验原始来源。",
        ]
    )
    return "\n".join(lines) + "\n"


def mk_personality_md(display_name: str, rows: List[Dict[str, str]]) -> str:
    token_rows = top_tokens(rows, 20)
    ending_rows = top_endings(rows, 12)
    quotes = choose_quotes(rows, 10)

    lines = [
        f"# 性格与表达偏好：{display_name}",
        "",
        "## 可观察到的表达偏好",
        "- 以原话与统计特征为主，不引入主观画像。",
    ]
    if token_rows:
        lines.append("- 常用词：" + "、".join([f"{t}({c})" for t, c in token_rows]) + "（`artifact`）")
    if ending_rows:
        lines.append("- 句尾倾向：" + "、".join([f"{t}({c})" for t, c in ending_rows]) + "（`artifact`）")
    lines.extend(["", "## 语气样本（原话）"])
    for row in quotes:
        lines.append(f"- “{row['text'].replace('`', '')}”（`verbatim`）")
    return "\n".join(lines) + "\n"


def mk_conflicts_md() -> str:
    return (
        "# 待决冲突\n\n"
        "- 当前自动蒸馏未检测到可稳定复现的显著冲突条目。\n"
        "- 如后续补充长文本、语音转写、邮件等跨渠道语料，建议重新执行冲突扫描。\n"
    )


def count_tag(text: str, tag: str) -> int:
    return text.count(f"`{tag}`")


def mk_skill_md(
    skill_id: str,
    display_name: str,
    sender_username: str,
    persona: str,
    interaction_md: str,
    memory_md: str,
    personality_md: str,
    dataset_csv: Path,
) -> str:
    iv = count_tag(interaction_md, "verbatim")
    ia = count_tag(interaction_md, "artifact")
    mv = count_tag(memory_md, "verbatim")
    ma = count_tag(memory_md, "artifact")
    pv = count_tag(personality_md, "verbatim")
    pa = count_tag(personality_md, "artifact")
    evidence = f"interaction={iv}v+{ia}a; memory={mv}v+{ma}a; personality={pv}v+{pa}a"
    metadata = {
        "ethics_note": "personal-memorial",
        "kit": "immortal-skill",
        "persona": persona,
        "evidence": evidence,
        "platforms": ["wechat"],
        "sender_username": sender_username,
        "dataset": str(dataset_csv),
    }
    meta_line = json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
    desc = f"基于微信聊天语料蒸馏 {display_name} 的互动风格、记忆线索与表达偏好。仅用于辅助理解与风格对齐，不用于冒充。"

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
        "1. 先读 `personality.md`，确定语气边界。\n"
        "2. 再读 `interaction.md`，对齐句长、词汇和节奏。\n"
        "3. 需要上下文时读 `memory.md`。\n"
        "4. 遇到冲突或不确定，读 `conflicts.md` 并显式说明不确定性。\n"
        "5. 不得伪造可归因于真人的承诺、身份或经历。\n\n"
        "## 局限\n\n"
        "- 语料主要为微信文本，缺少语音和线下语境。\n"
        "- 当前仅使用 `verbatim` 与 `artifact` 证据，不引入 `impression`。\n"
        "- 若要提高拟合度，建议补充跨场景材料后重跑蒸馏。\n"
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
    parser.add_argument("--min-messages", type=int, default=50, help="Skip sender if valid message count is below this")
    parser.add_argument(
        "--persona",
        default="friend",
        choices=["self", "colleague", "mentor", "family", "partner", "friend", "public-figure"],
    )
    parser.add_argument("--out-base", default=str(PROJECT_DIR / "skills" / "immortals"))
    parser.add_argument("--report-base", default=str(PROJECT_DIR / "distill_outputs"))
    parser.add_argument(
        "--dir-name-mode",
        default="nickname",
        choices=["slug", "nickname"],
        help="Folder naming mode for final output folders",
    )
    parser.add_argument("--note", default="batch_distill_wechat_top")
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
            "--persona",
            args.persona,
        ]
        if args.force:
            init_cmd.append("--force")
        run_cmd(init_cmd, PROJECT_DIR)

        skill_dir = out_base / skill_id
        interaction_md = mk_interaction_md(display_name, rows)
        memory_md = mk_memory_md(display_name, rows)
        personality_md = mk_personality_md(display_name, rows)
        conflicts_md = mk_conflicts_md()
        skill_md = mk_skill_md(
            skill_id=skill_id,
            display_name=display_name,
            sender_username=sender,
            persona=args.persona,
            interaction_md=interaction_md,
            memory_md=memory_md,
            personality_md=personality_md,
            dataset_csv=dataset_csv,
        )

        write_text(skill_dir / "interaction.md", interaction_md)
        write_text(skill_dir / "memory.md", memory_md)
        write_text(skill_dir / "personality.md", personality_md)
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
                if args.force:
                    raise RuntimeError(
                        f"Target directory exists for nickname mode: {target}. "
                        "Please remove it first or choose another out-base."
                    )
                raise RuntimeError(
                    f"Target directory exists: {target}. "
                    "Use --force with a clean output folder, or switch dir naming mode."
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
            ["rank", "skill_id", "dir_name", "sender_username", "sender_display_name", "message_count", "dataset_csv", "skill_dir"]
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
