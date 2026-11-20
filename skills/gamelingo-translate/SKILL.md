---
name: gamelingo-translate
description: Translate an extracted game string table into any target language with context awareness - consistent glossary, preserved placeholders and control codes, character voice, UI length limits. Use after extraction, or whenever the user wants to translate game text, dialogue, quest text, item names, menus or subtitles into Arabic, Persian, Turkish, Spanish, French, Japanese, Chinese or any other language.
---

# GameLingo · Translate

Fill the `target` field of every record in `strings.jsonl`.

## Before translating

1. **Understand the game**: genre, tone, setting, characters (read a sample of 30–50 strings across files). Decide register (formal / casual / archaic) and, for Arabic, the variety (default: clear Modern Standard Arabic, natural not stilted; keep colloquial only if the user asks).
2. **Build the glossary.** Copy `references/glossary-template.json` from the `gamelingo` skill to the workspace; fill recurring names, places, skills, items, UI terms, and a `do_not_translate` list (brand names, button icons, stat abbreviations the game keeps). Ask the user to confirm the key terms. Reuse the glossary on every batch.
3. **Plan batches**: ~40–80 strings per batch, grouped by file so context stays coherent. Translate dialogue in conversation order.

## Rules while translating

- Translate **meaning and tone**, not word-for-word. Keep jokes, puns and character voice where possible; add no content, remove none.
- Preserve every placeholder and control code **exactly**: `{0}`, `{player}`, `%s`, `%1$d`, `<b>…</b>`, `[color=red]`, `\C[2]`, `\N[1]`, `\n`, `${x}`. Do not reorder variables in ways that break grammar unless the source order is required by the engine (positional `%1$s` can be reordered; plain `%s` cannot).
- Keep line breaks in place; keep strings about the same length when they are UI labels (buttons, menus: aim ≤ 130% of source length). For long dialogue the engine usually wraps.
- Numbers, currency symbols and stat abbreviations: follow the glossary. For Arabic use the numeral style the user prefers (Western digits 0–9 are safest in games).
- Gendered languages: infer speaker/addressee gender from context; when unknown use neutral phrasing and flag it.
- Never leave a string in the source language unless it is in `do_not_translate`.
- If a string is ambiguous (single word, no context), translate for the most likely UI meaning and add a `"note"` field in the record.

## Output handling

- Write translations back into the JSONL (same `id`/`file`, fill `target`). If the model struggles with tokens, run `python ../gamelingo/scripts/placeholders.py protect` first and `restore` afterwards (see script `--help`).
- After each batch run `python ../gamelingo/scripts/qa_check.py strings.jsonl --glossary glossary.json --expect-script <script>` and fix errors before continuing.
- Keep a running translation memory: identical source strings get identical translations.

Hand off to `gamelingo-rtl` for right-to-left languages, otherwise to `gamelingo-qa`.
