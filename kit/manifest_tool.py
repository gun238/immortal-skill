#!/usr/bin/env python3
"""Lightweight toolkit for creating skill folders and stamping manifest fingerprints.

Wechat-adaptive mode:
- No role/persona-specific folder templates.
- Always creates a full set of dimensions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BASE_FILES = ("procedure.md", "interaction.md", "memory.md", "personality.md", "conflicts.md")

FILE_HINTS = {
    "procedure.md": (
        "# 程序性知识\n\n"
        "- 记录对方在聊天中展现的做事流程、推进顺序、复盘方式。\n"
        "- 如材料不足，可从其表达习惯中抽象出轻量流程偏好，并标注低置信。\n"
    ),
    "interaction.md": (
        "# 互动与语气\n\n"
        "- 聚焦句长、节奏、常用词、提问方式、情绪表达、边界感。\n"
        "- 允许在低样本下进行风格归纳，并在条目后标注置信度。\n"
    ),
    "memory.md": (
        "# 记忆与经历\n\n"
        "- 记录聊天中出现的事件线索、重复话题、情绪锚点、关系上下文。\n"
        "- 材料不足时，保留可观察线索，不强行补全事实细节。\n"
    ),
    "personality.md": (
        "# 性格与价值观\n\n"
        "- 基于可观察表达与互动行为提炼稳定倾向。\n"
        "- 禁止推断职业、学历、收入、疾病等高风险属性。\n"
    ),
    "conflicts.md": (
        "# 待决冲突\n\n"
        "- 记录同一对象在不同时期/场景下的矛盾表达。\n"
        "- 暂无冲突时明确写“未发现稳定冲突”。\n"
    ),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_slug(slug: str) -> None:
    if not SLUG_PATTERN.fullmatch(slug):
        print(
            "Error: slug must contain lowercase letters, digits, and hyphens only.",
            file=sys.stderr,
        )
        sys.exit(2)


def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.base).expanduser().resolve()
    slug = args.slug
    validate_slug(slug)
    root = base / slug

    if root.exists() and not args.force:
        print(f"Error: {root} already exists. Use --force to overwrite files.", file=sys.stderr)
        sys.exit(1)

    root.mkdir(parents=True, exist_ok=True)

    for name in BASE_FILES:
        p = root / name
        if args.force or not p.exists():
            p.write_text(FILE_HINTS[name], encoding="utf-8")

    manifest = {
        "slug": slug,
        "profile_mode": "wechat-adaptive",
        "built_at": None,
        "sources_summarized": [],
        "platforms": [],
        "kit": "immortal-skill",
        "dimensions": [f.replace(".md", "") for f in BASE_FILES if f != "conflicts.md"],
        "fingerprints": {},
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Initialized: {root}")


def cmd_stamp(args: argparse.Namespace) -> None:
    base = Path(args.base).expanduser().resolve()
    slug = args.slug
    validate_slug(slug)
    root = base / slug

    if not root.is_dir():
        print(f"Error: skill dir not found: {root}", file=sys.stderr)
        sys.exit(1)

    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        print("Error: manifest.json not found. Run init first.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["built_at"] = utc_now_iso()
    if args.sources:
        data["sources_summarized"] = [s.strip() for s in args.sources.split(",") if s.strip()]
    if args.note:
        data["note"] = args.note

    fps: dict[str, str] = {}
    for f in root.iterdir():
        if f.suffix in (".md", ".json") and f.name != "manifest.json":
            fps[f.name] = file_sha256(f)
    data["fingerprints"] = fps

    manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Stamped manifest: {manifest_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="immortal-skill manifest tool")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create <slug>/ skeleton")
    p_init.add_argument("--slug", required=True)
    p_init.add_argument("--base", default="./skills/immortals", help="Output root folder")
    # Backward compatibility only: accepted but ignored.
    p_init.add_argument("--persona", default=None, help="Deprecated and ignored.")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_stamp = sub.add_parser("stamp", help="Write built_at, fingerprints and source metadata")
    p_stamp.add_argument("--slug", required=True)
    p_stamp.add_argument("--base", default="./skills/immortals")
    p_stamp.add_argument("--sources", help="Comma-separated source hints")
    p_stamp.add_argument("--note", help="Optional note")
    p_stamp.set_defaults(func=cmd_stamp)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
