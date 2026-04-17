# Codex Adaptation

This project now supports Codex-driven distillation for WeChat records.

## What changed

- Role-free extraction (no self/friend/partner template gating in the batch pipeline).
- Four dimensions are always produced:
  - `procedure.md`
  - `interaction.md`
  - `memory.md`
  - `personality.md`
- Sensitive identity inference is explicitly forbidden.

## Engines

- `--engine rules`: local heuristic extraction.
- `--engine codex`: call Codex command for extraction.
- `--engine hybrid`: try Codex, fallback to rules.

Actual engine used for each subject is recorded in:
- `distill_manifest.csv` (`engine_used` column)
- `distill_manifest.json` (`engine_used` field)

## Codex command integration

The script accepts:

- `--codex-command "codex ..."`: stdin mode (prompt piped through stdin)
- `--codex-command "my_wrapper {prompt_file}"`: file mode (placeholder replaced by temp prompt file)

You can also set:

- `IMMORTAL_CODEX_COMMAND`

## Example

```bash
python kit/batch_distill_wechat_top.py \
  --top-n 35 \
  --engine codex \
  --codex-command "codex"
```

If Codex cannot run in current environment and `--codex-strict` is not set, the script falls back to `rules`.
